from __future__ import annotations

import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

from agent import Agent, NoMemory, SessionSearchMemory, StaticFileMemory, bullet_list, search_terms


class AgentTest(unittest.TestCase):
    def test_search_terms_ignores_short_words(self) -> None:
        self.assertEqual(
            search_terms("How do we run python commands with uv?"),
            ["python", "commands", "with"],
        )

    def test_bullet_list_handles_empty_items(self) -> None:
        self.assertEqual(bullet_list("Memory", []), "Memory\n(none)")

    def test_search_sessions_finds_recent_matching_message(self) -> None:
        memory = SessionSearchMemory(db_path=Path(":memory:"))
        memory.save("We chose SQLite for the memory demo.", "Good choice.")

        self.assertEqual(
            memory.search("Which database did we choose for memory?"),
            ["user: We chose SQLite for the memory demo."],
        )

        memory.close()

    def test_static_memory_loads_markdown_files_at_startup(self) -> None:
        with TemporaryDirectory() as directory:
            memory_dir = Path(directory)
            (memory_dir / "AGENTS.md").write_text("Use `uv run`.", encoding="utf-8")

            memory = StaticFileMemory(memory_dir=memory_dir)

            self.assertIn("AGENTS.md\nUse `uv run`.", memory.startup())

    def test_agent_run_tracks_short_term_history(self) -> None:
        agent = Agent(memory=NoMemory())
        agent.call_model = lambda instructions, messages: "done"  # type: ignore[method-assign]

        self.assertEqual(agent.run("hello"), "done")
        self.assertEqual(
            [message.role for message in agent.messages],
            ["user", "assistant"],
        )


if __name__ == "__main__":
    unittest.main()
