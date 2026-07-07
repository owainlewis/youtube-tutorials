from __future__ import annotations

import os
import re
import sqlite3
from pathlib import Path


ROOT = Path(__file__).resolve().parent
MEMORY_DIR = ROOT / "memory"
DB_PATH = ROOT / "sessions.sqlite3"
MODEL = os.environ.get("OPENAI_MODEL", "gpt-4.1-mini")
USER_ID = os.environ.get("DEMO_USER_ID", "demo-user")


def load_static_memory() -> str:
    parts: list[str] = []
    for path in sorted(MEMORY_DIR.glob("*.md")):
        text = path.read_text(encoding="utf-8").strip()
        parts.append(f"{path.name}\n{text}")
    return "\n\n".join(parts)


def bullet_list(title: str, items: list[str]) -> str:
    if not items:
        return f"{title}\n(none)"
    return title + "\n" + "\n".join(f"- {item}" for item in items)


def search_terms(query: str) -> list[str]:
    return re.findall(r"[a-zA-Z0-9_]{4,}", query.lower())[:6]


def build_instructions(
    *,
    startup_memory: str = "",
    retrieved_memory: list[str] | None = None,
) -> str:
    sections = [
        "You are a helpful coding assistant.",
        "Be direct, practical, and concise.",
    ]

    if startup_memory:
        sections.append("Static memory loaded at startup:\n" + startup_memory)

    if retrieved_memory is not None:
        sections.append(bullet_list("Retrieved memory for this turn", retrieved_memory))

    return "\n\n".join(sections)


def ask_model(instructions: str, user_input: str) -> str:
    if os.environ.get("AI_MEMORY_DEMO_FAKE_MODEL") == "1":
        return fake_model_response(instructions, user_input)

    if not os.environ.get("OPENAI_API_KEY"):
        raise SystemExit(
            "Set OPENAI_API_KEY for real model calls, or set "
            "AI_MEMORY_DEMO_FAKE_MODEL=1 for a local smoke test."
        )

    from openai import OpenAI

    response = OpenAI().responses.create(
        model=MODEL,
        instructions=instructions,
        input=user_input,
    )
    return response.output_text.strip()


def fake_model_response(instructions: str, user_input: str) -> str:
    visible_context = []

    if "Use `uv run` for Python commands" in instructions:
        visible_context.append("I can see the static memory saying to use `uv run`.")

    if "Retrieved memory for this turn\n-" in instructions:
        visible_context.append("I can see retrieved session or external memory.")

    if not visible_context:
        visible_context.append("I only have the current prompt and conversation.")

    return " ".join(visible_context) + f" You asked: {user_input}"


def connect_sessions() -> sqlite3.Connection:
    db = sqlite3.connect(DB_PATH)
    db.execute(
        """
        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            role TEXT NOT NULL,
            content TEXT NOT NULL
        )
        """
    )
    return db


def save_message(db: sqlite3.Connection, role: str, content: str) -> None:
    db.execute(
        "INSERT INTO messages(role, content) VALUES (?, ?)",
        (role, content),
    )
    db.commit()


def search_sessions(db: sqlite3.Connection, query: str) -> list[str]:
    terms = search_terms(query)
    if not terms:
        return []

    matches: list[str] = []
    rows = db.execute(
        "SELECT role, content FROM messages ORDER BY id DESC LIMIT 50"
    ).fetchall()

    for role, content in rows:
        text = content.lower()
        if any(term in text for term in terms):
            matches.append(f"{role}: {content}")
        if len(matches) == 5:
            break

    return matches
