from __future__ import annotations

import importlib.util
import tempfile
import unittest
from pathlib import Path


SCRIPT_PATH = Path(__file__).resolve().parents[1] / "repository_checks.py"
SPEC = importlib.util.spec_from_file_location("repository_checks", SCRIPT_PATH)
assert SPEC and SPEC.loader
repository_checks = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(repository_checks)


class RepositoryChecksTest(unittest.TestCase):
    def test_layout_uses_tracked_file_inventory(self) -> None:
        files = [
            Path("tutorials/alpha/README.md"),
            Path("tutorials/alpha/LESSON.md"),
            Path("tutorials/alpha/code/.gitkeep"),
            Path("tutorials/alpha/resources/.gitkeep"),
            Path("tutorials/alpha/resources/slides/.gitkeep"),
        ]

        self.assertEqual(repository_checks.check_layout(files, ["alpha"]), [])

    def test_layout_reports_tutorial_and_missing_directory(self) -> None:
        files = [
            Path("tutorials/alpha/README.md"),
            Path("tutorials/alpha/LESSON.md"),
            Path("tutorials/alpha/resources/.gitkeep"),
            Path("tutorials/alpha/resources/slides/.gitkeep"),
        ]

        self.assertEqual(
            repository_checks.check_layout(files, ["alpha"]),
            ["tutorials/alpha: missing tracked code directory"],
        )

    def test_markdown_links_ignore_examples_in_fenced_blocks(self) -> None:
        markdown = """A [real](./real.md) link.

```markdown
[example](./not-real.md)
```
"""

        self.assertEqual(
            repository_checks.local_markdown_links(markdown), [(1, "./real.md")]
        )

    def test_markdown_links_report_missing_target_with_line(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "README.md").write_text("See [missing](./missing.md).\n")
            (root / "missing.md").write_text("local but untracked\n")

            errors = repository_checks.check_markdown_links(
                root, [Path("README.md")]
            )

        self.assertEqual(
            errors, ["README.md:1: missing local link target './missing.md'"]
        )

    def test_markdown_links_reject_target_outside_repository(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory) / "repo"
            root.mkdir()
            (root / "README.md").write_text("See [outside](../outside.md).\n")
            (root.parent / "outside.md").write_text("outside\n")

            errors = repository_checks.check_markdown_links(
                root, [Path("README.md")]
            )

        self.assertEqual(
            errors, ["README.md:1: missing local link target '../outside.md'"]
        )

    def test_verification_manifest_requires_every_code_tutorial(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            manifest = root / "verification.json"
            manifest.write_text('{"tutorials": {}}')

            errors = repository_checks.check_verification_manifest(
                root,
                [Path("tutorials/alpha/code/main.py")],
                manifest,
            )

        self.assertEqual(
            errors,
            ["verification manifest missing code-bearing tutorials: ['alpha']"],
        )


if __name__ == "__main__":
    unittest.main()
