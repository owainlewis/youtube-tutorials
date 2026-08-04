from __future__ import annotations

import importlib.util
import json
import tempfile
import unittest
from pathlib import Path


SCRIPT_PATH = Path(__file__).resolve().parents[1] / "tutorial_catalog.py"
SPEC = importlib.util.spec_from_file_location("tutorial_catalog", SCRIPT_PATH)
assert SPEC and SPEC.loader
tutorial_catalog = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(tutorial_catalog)


class TutorialCatalogTest(unittest.TestCase):
    def test_render_readme_block_lists_only_published_tutorials(self) -> None:
        tutorials = [
            {
                "slug": "alpha",
                "title": "Alpha",
                "status": "published",
                "video_url": "",
                "last_verified": "",
            },
            {
                "slug": "beta",
                "title": "Beta",
                "status": "draft",
                "video_url": "",
                "last_verified": "",
            },
        ]

        block = tutorial_catalog.render_readme_block(tutorials)

        self.assertIn("\n1 published tutorial:\n", block)
        self.assertIn("./tutorials/alpha/", block)
        self.assertNotIn("./tutorials/beta/", block)

    def test_validate_tracked_parity_reports_both_directions(self) -> None:
        tutorials = [
            {
                "slug": "catalog-only",
                "title": "Catalog only",
                "status": "draft",
                "video_url": "",
                "last_verified": "",
            }
        ]

        with self.assertRaises(tutorial_catalog.CatalogError) as raised:
            tutorial_catalog.validate_tracked_parity(tutorials, {"tracked-only"})
        self.assertIn("Missing from catalog", str(raised.exception))
        self.assertIn("Missing from Git", str(raised.exception))

    def test_replace_readme_block_rejects_missing_markers(self) -> None:
        with self.assertRaisesRegex(tutorial_catalog.CatalogError, "exactly one"):
            tutorial_catalog.replace_readme_block("# Tutorials\n", "generated")

    def test_replace_readme_block_rejects_duplicate_sections(self) -> None:
        section = (
            f"{tutorial_catalog.START_MARKER}\n"
            "stale\n"
            f"{tutorial_catalog.END_MARKER}"
        )
        with self.assertRaisesRegex(tutorial_catalog.CatalogError, "exactly one"):
            tutorial_catalog.replace_readme_block(f"{section}\n{section}", "generated")

    def test_replace_readme_block_rejects_inverted_markers(self) -> None:
        readme = (
            f"{tutorial_catalog.END_MARKER}\n"
            "stale\n"
            f"{tutorial_catalog.START_MARKER}"
        )
        with self.assertRaisesRegex(tutorial_catalog.CatalogError, "wrong order"):
            tutorial_catalog.replace_readme_block(readme, "generated")

    def test_load_catalog_requires_expanded_iso_date(self) -> None:
        payload = {
            "tutorials": [
                {
                    "slug": "alpha",
                    "title": "Alpha",
                    "status": "published",
                    "video_url": "",
                    "last_verified": "20260804",
                }
            ]
        }
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "catalog.json"
            path.write_text(json.dumps(payload))
            with self.assertRaisesRegex(tutorial_catalog.CatalogError, "YYYY-MM-DD"):
                tutorial_catalog.load_catalog(path)


if __name__ == "__main__":
    unittest.main()
