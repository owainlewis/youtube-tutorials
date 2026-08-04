from __future__ import annotations

import importlib.util
import subprocess
import tempfile
import unittest
from pathlib import Path


SCRIPT_PATH = Path(__file__).resolve().parents[1] / "scaffold_tutorial.py"
ROOT = SCRIPT_PATH.parents[1]
SPEC = importlib.util.spec_from_file_location("scaffold_tutorial", SCRIPT_PATH)
assert SPEC and SPEC.loader
scaffold_tutorial = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(scaffold_tutorial)


class ScaffoldTutorialTest(unittest.TestCase):
    def test_scaffold_creates_standard_shape_without_empty_resource_links(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            tutorial = scaffold_tutorial.scaffold(root, "example-agent", "Example Agent")

            files = {
                path.relative_to(tutorial).as_posix()
                for path in tutorial.rglob("*")
                if path.is_file()
            }
            readme = (tutorial / "README.md").read_text()

        self.assertEqual(
            files,
            {
                "LESSON.md",
                "README.md",
                "code/.gitkeep",
                "resources/prompts.md",
                "resources/slides/.gitkeep",
            },
        )
        self.assertIn("[LESSON.md](./LESSON.md)", readme)
        self.assertNotIn("(./code/)", readme)
        self.assertNotIn("(./resources/)", readme)
        self.assertNotIn("(./resources/slides/)", readme)

    def test_scaffold_replaces_lesson_title(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            tutorial = scaffold_tutorial.scaffold(
                Path(directory), "example-agent", "Example Agent"
            )

            lesson = (tutorial / "LESSON.md").read_text()

        self.assertTrue(lesson.startswith("# Example Agent\n"))
        self.assertNotIn("# Lesson Title", lesson)

    def test_scaffold_rejects_invalid_slug(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            with self.assertRaisesRegex(ValueError, "lowercase"):
                scaffold_tutorial.scaffold(Path(directory), "Bad Slug", "Title")

    def test_scaffold_does_not_overwrite_existing_tutorial(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            scaffold_tutorial.scaffold(root, "example-agent", "Example Agent")

            with self.assertRaises(FileExistsError):
                scaffold_tutorial.scaffold(root, "example-agent", "Replacement")

    def test_just_recipe_shell_quotes_title(self) -> None:
        title = 'Title "$(touch should-not-run)" and O\'Brien'
        result = subprocess.run(
            [
                "just",
                "--dry-run",
                "--no-highlight",
                "new-tutorial",
                "safe-slug",
                title,
            ],
            cwd=ROOT,
            check=True,
            capture_output=True,
            text=True,
        )

        self.assertEqual(
            result.stderr,
            "python3 scripts/scaffold_tutorial.py 'safe-slug' "
            "'Title \"$(touch should-not-run)\" and O'\\''Brien'\n",
        )


if __name__ == "__main__":
    unittest.main()
