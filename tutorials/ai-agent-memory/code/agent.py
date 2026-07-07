from __future__ import annotations

import os
import re
import sqlite3
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Protocol


ROOT = Path(__file__).resolve().parent
MEMORY_DIR = ROOT / "memory"
DB_PATH = ROOT / "sessions.sqlite3"
DEFAULT_MODEL = os.environ.get("OPENAI_MODEL", "gpt-4.1-mini")
USER_ID = os.environ.get("DEMO_USER_ID", "demo-user")


@dataclass(frozen=True)
class Message:
    role: str
    content: str


class Memory(Protocol):
    def startup(self) -> str:
        """Return small stable context loaded when the agent starts."""

    def search(self, user_message: str) -> list[str]:
        """Return relevant context loaded before this model turn."""

    def save(self, user_message: str, assistant_reply: str) -> None:
        """Save anything useful after this model turn."""


class NoMemory:
    def startup(self) -> str:
        return ""

    def search(self, user_message: str) -> list[str]:
        return []

    def save(self, user_message: str, assistant_reply: str) -> None:
        return None


class StaticFileMemory(NoMemory):
    def __init__(self, memory_dir: Path = MEMORY_DIR) -> None:
        self.memory_dir = memory_dir

    def startup(self) -> str:
        parts: list[str] = []
        for path in sorted(self.memory_dir.glob("*.md")):
            text = path.read_text(encoding="utf-8").strip()
            parts.append(f"{path.name}\n{text}")
        return "\n\n".join(parts)


class SessionSearchMemory(StaticFileMemory):
    def __init__(
        self,
        db_path: Path = DB_PATH,
        memory_dir: Path = MEMORY_DIR,
        max_results: int = 5,
    ) -> None:
        super().__init__(memory_dir)
        self.db_path = db_path
        self.max_results = max_results
        self.db = sqlite3.connect(db_path)
        self.db.execute(
            """
            CREATE TABLE IF NOT EXISTS messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                role TEXT NOT NULL,
                content TEXT NOT NULL
            )
            """
        )

    def search(self, user_message: str) -> list[str]:
        terms = search_terms(user_message)
        if not terms:
            return []

        matches: list[str] = []
        rows = self.db.execute(
            "SELECT role, content FROM messages ORDER BY id DESC LIMIT 50"
        ).fetchall()

        for role, content in rows:
            text = content.lower()
            if any(term in text for term in terms):
                matches.append(f"{role}: {content}")
            if len(matches) == self.max_results:
                break

        return matches

    def save(self, user_message: str, assistant_reply: str) -> None:
        self._save_message("user", user_message)
        self._save_message("assistant", assistant_reply)

    def close(self) -> None:
        self.db.close()

    def _save_message(self, role: str, content: str) -> None:
        self.db.execute(
            "INSERT INTO messages(role, content) VALUES (?, ?)",
            (role, content),
        )
        self.db.commit()


class Mem0Memory(StaticFileMemory):
    def __init__(self, user_id: str = USER_ID, memory_dir: Path = MEMORY_DIR) -> None:
        super().__init__(memory_dir)

        api_key = os.environ.get("MEM0_API_KEY")
        if not api_key:
            raise SystemExit("Set MEM0_API_KEY before running this example.")

        try:
            from mem0 import MemoryClient
        except ImportError as exc:
            raise SystemExit(
                "Install the Mem0 extra with: uv run --extra mem0 04_mem0_memory.py"
            ) from exc

        self.client = MemoryClient(api_key=api_key)
        self.user_id = user_id

    def search(self, user_message: str) -> list[str]:
        response = self.client.search(user_message, filters={"user_id": self.user_id})
        return [memory_text(item) for item in result_items(response)]

    def save(self, user_message: str, assistant_reply: str) -> None:
        self.client.add(
            messages=[
                {"role": "user", "content": user_message},
                {"role": "assistant", "content": assistant_reply},
            ],
            user_id=self.user_id,
        )


class Agent:
    def __init__(self, memory: Memory | None = None, model: str = DEFAULT_MODEL) -> None:
        self.memory = memory or NoMemory()
        self.model = model
        self.startup_memory = self.memory.startup()
        self.messages: list[Message] = []

    def run(self, user_message: str) -> str:
        retrieved_memory = self.memory.search(user_message)
        instructions = self.instructions(retrieved_memory)

        self.messages.append(Message(role="user", content=user_message))
        reply = self.call_model(instructions, self.messages)
        self.messages.append(Message(role="assistant", content=reply))

        self.memory.save(user_message, reply)
        return reply

    def instructions(self, retrieved_memory: list[str]) -> str:
        sections = [
            "You are a helpful coding assistant.",
            "Be direct, practical, and concise.",
        ]

        if self.startup_memory:
            sections.append("Static memory loaded at startup:\n" + self.startup_memory)

        if retrieved_memory:
            sections.append(bullet_list("Retrieved memory for this turn", retrieved_memory))

        return "\n\n".join(sections)

    def call_model(self, instructions: str, messages: list[Message]) -> str:
        if os.environ.get("AI_MEMORY_DEMO_FAKE_MODEL") == "1":
            return fake_model_response(instructions, messages)

        if not os.environ.get("OPENAI_API_KEY"):
            raise SystemExit(
                "Set OPENAI_API_KEY for real model calls, or set "
                "AI_MEMORY_DEMO_FAKE_MODEL=1 for a local smoke test."
            )

        from openai import OpenAI

        response = OpenAI().responses.create(
            model=self.model,
            instructions=instructions,
            input=[
                {"role": message.role, "content": message.content}
                for message in messages
            ],
        )
        return response.output_text.strip()


def run_repl(agent: Agent, title: str) -> None:
    print(f"{title}. Type 'exit' to quit.\n")
    while True:
        user_message = input("you> ").strip()
        if user_message.lower() in {"exit", "quit"}:
            break

        reply = agent.run(user_message)
        print(f"\nagent> {reply}\n")


def bullet_list(title: str, items: list[str]) -> str:
    if not items:
        return f"{title}\n(none)"
    return title + "\n" + "\n".join(f"- {item}" for item in items)


def search_terms(query: str) -> list[str]:
    return re.findall(r"[a-zA-Z0-9_]{4,}", query.lower())[:6]


def fake_model_response(instructions: str, messages: list[Message]) -> str:
    visible_context = []

    if "Use `uv run` for Python commands" in instructions:
        visible_context.append("I can see the static memory saying to use `uv run`.")

    if "Retrieved memory for this turn\n-" in instructions:
        visible_context.append("I can see retrieved session or external memory.")

    if not visible_context:
        visible_context.append("I only have the current prompt and conversation.")

    user_messages = [message.content for message in messages if message.role == "user"]
    latest_user_message = user_messages[-1] if user_messages else ""
    return " ".join(visible_context) + f" You asked: {latest_user_message}"


def memory_text(item: Any) -> str:
    if isinstance(item, dict):
        return str(item.get("memory") or item.get("content") or item)
    return str(item)


def result_items(response: Any) -> list[Any]:
    if isinstance(response, dict):
        results = response.get("results", [])
        return results if isinstance(results, list) else []
    return response if isinstance(response, list) else []
