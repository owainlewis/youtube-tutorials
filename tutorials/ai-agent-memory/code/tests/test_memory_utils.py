from __future__ import annotations

import sqlite3
import unittest

from memory_utils import bullet_list, save_message, search_sessions, search_terms


class MemoryUtilsTest(unittest.TestCase):
    def test_search_terms_ignores_short_words(self) -> None:
        self.assertEqual(
            search_terms("How do we run python commands with uv?"),
            ["python", "commands", "with"],
        )

    def test_bullet_list_handles_empty_items(self) -> None:
        self.assertEqual(bullet_list("Memory", []), "Memory\n(none)")

    def test_search_sessions_finds_recent_matching_message(self) -> None:
        db = sqlite3.connect(":memory:")
        db.execute(
            """
            CREATE TABLE messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                role TEXT NOT NULL,
                content TEXT NOT NULL
            )
            """
        )

        save_message(db, "user", "We chose SQLite for the memory demo.")
        save_message(db, "assistant", "Good choice.")

        self.assertEqual(
            search_sessions(db, "Which database did we choose for memory?"),
            ["user: We chose SQLite for the memory demo."],
        )


if __name__ == "__main__":
    unittest.main()
