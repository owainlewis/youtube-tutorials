from __future__ import annotations

import importlib.util
import json
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

    def test_verification_manifest_requires_runnable_documentation(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            code = root / "tutorials/alpha/code"
            code.mkdir(parents=True)
            (code / "main.py").write_text("print('ok')\n")
            manifest = root / "verification.json"
            manifest.write_text(
                """{
  "tutorials": {
    "alpha": {
      "classification": "runnable",
      "kind": "offline",
      "commands": [{"cwd": "tutorials/alpha/code", "run": ["python", "main.py"]}]
    }
  }
}
"""
            )

            errors = repository_checks.check_verification_manifest(
                root,
                [Path("tutorials/alpha/code/main.py")],
                manifest,
            )

        self.assertEqual(
            errors,
            [
                "alpha: runnable tutorials need install, run, test, and reset documentation"
            ],
        )

    def test_verification_manifest_validates_documentation_headings(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            tutorial = root / "tutorials/alpha"
            code = tutorial / "code"
            code.mkdir(parents=True)
            (code / "main.py").write_text("print('ok')\n")
            (tutorial / "LESSON.md").write_text(
                "# Alpha\n\n## Install\n\n## Run\n\n## Test\n\n## Reset\n\n"
                "```markdown\n## Missing Test Heading\n```\n"
            )
            manifest = root / "verification.json"
            references = {
                action: {
                    "path": "tutorials/alpha/LESSON.md",
                    "heading": heading,
                }
                for action, heading in {
                    "install": "Install",
                    "run": "Run",
                    "test": "Missing Test Heading",
                    "reset": "Reset",
                }.items()
            }
            manifest.write_text(
                json.dumps(
                    {
                        "tutorials": {
                            "alpha": {
                                "classification": "runnable",
                                "kind": "offline",
                                "documentation": references,
                                "commands": [
                                    {
                                        "cwd": "tutorials/alpha/code",
                                        "run": ["python", "main.py"],
                                    }
                                ],
                            }
                        }
                    }
                )
            )

            errors = repository_checks.check_verification_manifest(
                root,
                [
                    Path("tutorials/alpha/LESSON.md"),
                    Path("tutorials/alpha/code/main.py"),
                ],
                manifest,
            )

        self.assertEqual(
            errors,
            [
                "alpha: test documentation heading 'Missing Test Heading' not found in tutorials/alpha/LESSON.md"
            ],
        )

    def test_verification_manifest_requires_static_infrastructure_checks(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            code = root / "tutorials/alpha/code"
            code.mkdir(parents=True)
            (code / "main.tf").write_text("terraform {}\n")
            manifest = root / "verification.json"
            manifest.write_text(
                """{
  "tutorials": {
    "alpha": {
      "classification": "infrastructure-only",
      "reason": "Terraform example.",
      "kind": "offline",
      "commands": [{"cwd": "tutorials/alpha/code", "run": ["terraform", "fmt", "-check"]}]
    }
  }
}
"""
            )

            errors = repository_checks.check_verification_manifest(
                root,
                [Path("tutorials/alpha/code/main.tf")],
                manifest,
            )

        self.assertEqual(
            errors,
            ["alpha: infrastructure-only tutorials need static verification"],
        )

    def test_verification_manifest_rejects_cross_tutorial_references(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            alpha = root / "tutorials/alpha"
            beta = root / "tutorials/beta"
            (alpha / "code").mkdir(parents=True)
            (beta / "code").mkdir(parents=True)
            (alpha / "code/main.py").write_text("print('alpha')\n")
            (beta / "code/main.py").write_text("print('beta')\n")
            lesson = "# Lesson\n\n## Install\n\n## Run\n\n## Test\n\n## Reset\n"
            (alpha / "LESSON.md").write_text(lesson)
            (beta / "LESSON.md").write_text(lesson)
            documentation = {
                action: {
                    "path": "tutorials/alpha/LESSON.md",
                    "heading": heading,
                }
                for action, heading in {
                    "install": "Install",
                    "run": "Run",
                    "test": "Test",
                    "reset": "Reset",
                }.items()
            }
            documentation["test"]["path"] = "tutorials/beta/LESSON.md"
            manifest = root / "verification.json"
            manifest.write_text(
                json.dumps(
                    {
                        "tutorials": {
                            "alpha": {
                                "classification": "runnable",
                                "kind": "offline",
                                "documentation": documentation,
                                "commands": [
                                    {
                                        "cwd": "tutorials/beta/code",
                                        "run": ["python", "main.py"],
                                    }
                                ],
                            },
                            "beta": {
                                "classification": "snippet-only",
                                "reason": "Fixture.",
                                "kind": "offline",
                                "commands": [
                                    {
                                        "cwd": "tutorials/beta/code",
                                        "run": ["python", "main.py"],
                                    }
                                ],
                            },
                        }
                    }
                )
            )

            errors = repository_checks.check_verification_manifest(
                root,
                [
                    Path("tutorials/alpha/LESSON.md"),
                    Path("tutorials/alpha/code/main.py"),
                    Path("tutorials/beta/LESSON.md"),
                    Path("tutorials/beta/code/main.py"),
                ],
                manifest,
            )

        self.assertEqual(
            errors,
            [
                "alpha: test documentation must stay inside tutorials/alpha",
                "alpha: command 1 cwd must stay inside tutorials/alpha",
            ],
        )

    def test_junk_check_rejects_common_lockfiles(self) -> None:
        files = [
            Path("tutorials/python/uv.lock"),
            Path("tutorials/node/package-lock.json"),
            Path("tutorials/rust/Cargo.lock"),
        ]

        self.assertEqual(
            repository_checks.check_junk(files),
            [
                "tutorials/python/uv.lock: tracked junk",
                "tutorials/node/package-lock.json: tracked junk",
                "tutorials/rust/Cargo.lock: tracked junk",
            ],
        )

    def test_junk_check_rejects_generated_data_and_secret_files(self) -> None:
        files = [
            Path("tutorials/python/results.sqlite3"),
            Path("tutorials/python/.env.production"),
            Path("tutorials/python/service-account.json"),
            Path("tutorials/python/.env.example"),
        ]

        self.assertEqual(
            repository_checks.check_junk(files),
            [
                "tutorials/python/results.sqlite3: tracked junk",
                "tutorials/python/.env.production: tracked junk",
                "tutorials/python/service-account.json: tracked junk",
            ],
        )

    def test_junk_check_rejects_redundant_gitkeep(self) -> None:
        files = [
            Path("tutorials/alpha/code/.gitkeep"),
            Path("tutorials/alpha/code/main.py"),
            Path("tutorials/alpha/resources/slides/.gitkeep"),
        ]

        self.assertEqual(
            repository_checks.check_junk(files),
            [
                "tutorials/alpha/code/.gitkeep: redundant .gitkeep beside tracked content"
            ],
        )

    def test_junk_check_rejects_nested_repositories(self) -> None:
        self.assertEqual(
            repository_checks.check_nested_repositories(
                [Path("tutorials/example/code/vendor-repository")]
            ),
            [
                "tutorials/example/code/vendor-repository: tracked nested repository"
            ],
        )

    def test_empty_resource_links_reject_placeholder_only_directory(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            readme = root / "tutorials/alpha/README.md"
            readme.parent.mkdir(parents=True)
            readme.write_text("Browse [code](./code/).\n")

            errors = repository_checks.check_empty_resource_links(
                root,
                [
                    Path("tutorials/alpha/README.md"),
                    Path("tutorials/alpha/code/.gitkeep"),
                ],
            )

        self.assertEqual(
            errors,
            [
                "tutorials/alpha/README.md:1: link target './code/' contains only placeholders"
            ],
        )

    def test_empty_resource_links_allow_directory_with_real_content(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            readme = root / "tutorials/alpha/README.md"
            readme.parent.mkdir(parents=True)
            readme.write_text("Browse [code](./code/).\n")

            errors = repository_checks.check_empty_resource_links(
                root,
                [
                    Path("tutorials/alpha/README.md"),
                    Path("tutorials/alpha/code/.gitkeep"),
                    Path("tutorials/alpha/code/main.py"),
                ],
            )

        self.assertEqual(errors, [])


if __name__ == "__main__":
    unittest.main()
