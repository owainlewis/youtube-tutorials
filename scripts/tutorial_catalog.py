#!/usr/bin/env python3
"""Validate the tutorial catalog and keep the root README in sync."""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from datetime import date
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
CATALOG_PATH = ROOT / "tutorials" / "catalog.json"
README_PATH = ROOT / "README.md"
START_MARKER = "<!-- tutorial-catalog:start -->"
END_MARKER = "<!-- tutorial-catalog:end -->"
VALID_STATUSES = {"draft", "published"}
REQUIRED_FIELDS = {"slug", "title", "status", "video_url", "last_verified"}
SLUG_PATTERN = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")


class CatalogError(ValueError):
    """Raised when catalog data does not meet the repository contract."""


def load_catalog(path: Path = CATALOG_PATH) -> list[dict[str, str]]:
    try:
        payload: Any = json.loads(path.read_text())
    except (OSError, json.JSONDecodeError) as error:
        raise CatalogError(f"Cannot read {path}: {error}") from error

    if not isinstance(payload, dict) or not isinstance(payload.get("tutorials"), list):
        raise CatalogError("Catalog must contain a 'tutorials' list.")

    tutorials = payload["tutorials"]
    errors: list[str] = []
    slugs: list[str] = []

    for index, tutorial in enumerate(tutorials, start=1):
        prefix = f"tutorials[{index}]"
        if not isinstance(tutorial, dict):
            errors.append(f"{prefix} must be an object.")
            continue

        missing = REQUIRED_FIELDS - tutorial.keys()
        extra = tutorial.keys() - REQUIRED_FIELDS
        if missing:
            errors.append(f"{prefix} is missing fields: {sorted(missing)}")
        if extra:
            errors.append(f"{prefix} has unsupported fields: {sorted(extra)}")
        if missing:
            continue

        if any(not isinstance(tutorial[field], str) for field in REQUIRED_FIELDS):
            errors.append(f"{prefix} fields must all be strings.")
            continue

        slug = tutorial["slug"]
        slugs.append(slug)
        if not SLUG_PATTERN.fullmatch(slug):
            errors.append(f"{prefix}.slug is invalid: {slug!r}")
        if not tutorial["title"].strip():
            errors.append(f"{prefix}.title cannot be empty.")
        if tutorial["status"] not in VALID_STATUSES:
            errors.append(
                f"{prefix}.status must be one of {sorted(VALID_STATUSES)}."
            )
        if tutorial["video_url"] and not tutorial["video_url"].startswith("https://"):
            errors.append(f"{prefix}.video_url must be empty or use HTTPS.")
        if tutorial["last_verified"]:
            try:
                if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", tutorial["last_verified"]):
                    raise ValueError
                date.fromisoformat(tutorial["last_verified"])
            except ValueError:
                errors.append(f"{prefix}.last_verified must use YYYY-MM-DD.")

    duplicates = sorted({slug for slug in slugs if slugs.count(slug) > 1})
    if duplicates:
        errors.append(f"Duplicate tutorial slugs: {duplicates}")
    if slugs != sorted(slugs):
        errors.append("Tutorial entries must be sorted by slug.")

    if errors:
        raise CatalogError("\n".join(errors))

    return tutorials


def tracked_tutorial_slugs(root: Path = ROOT) -> set[str]:
    result = subprocess.run(
        ["git", "ls-files", "-z", "--", "tutorials"],
        cwd=root,
        check=True,
        capture_output=True,
        text=True,
    )
    slugs: set[str] = set()
    for filename in result.stdout.split("\0"):
        parts = Path(filename).parts
        if len(parts) >= 3 and parts[0] == "tutorials" and not parts[1].startswith("_"):
            slugs.add(parts[1])
    return slugs


def validate_tracked_parity(
    tutorials: list[dict[str, str]], tracked_slugs: set[str]
) -> None:
    catalog_slugs = {tutorial["slug"] for tutorial in tutorials}
    missing = sorted(tracked_slugs - catalog_slugs)
    extra = sorted(catalog_slugs - tracked_slugs)
    if missing or extra:
        lines = ["Catalog does not match tracked tutorial directories."]
        if missing:
            lines.append(f"Missing from catalog: {missing}")
        if extra:
            lines.append(f"Missing from Git: {extra}")
        raise CatalogError("\n".join(lines))


def render_readme_block(tutorials: list[dict[str, str]]) -> str:
    published = [tutorial for tutorial in tutorials if tutorial["status"] == "published"]
    noun = "tutorial" if len(published) == 1 else "tutorials"
    lines = [START_MARKER, f"{len(published)} published {noun}:", ""]
    lines.extend(
        f'- [{tutorial["title"]}](./tutorials/{tutorial["slug"]}/)'
        for tutorial in published
    )
    lines.append(END_MARKER)
    return "\n".join(lines)


def replace_readme_block(readme: str, expected_block: str) -> str:
    if readme.count(START_MARKER) != 1 or readme.count(END_MARKER) != 1:
        raise CatalogError(
            "README must contain exactly one tutorial catalog start marker and end marker."
        )
    pattern = re.compile(
        rf"{re.escape(START_MARKER)}.*?{re.escape(END_MARKER)}", re.DOTALL
    )
    if not pattern.search(readme):
        raise CatalogError("README tutorial catalog markers are in the wrong order.")
    return pattern.sub(expected_block, readme, count=1)


def run(write: bool) -> None:
    tutorials = load_catalog()
    validate_tracked_parity(tutorials, tracked_tutorial_slugs())
    expected_block = render_readme_block(tutorials)
    current_readme = README_PATH.read_text()
    updated_readme = replace_readme_block(current_readme, expected_block)

    if write:
        README_PATH.write_text(updated_readme)
        print(f"Updated {README_PATH.relative_to(ROOT)} from tutorials/catalog.json.")
        return

    if current_readme != updated_readme:
        raise CatalogError(
            "README tutorial list is out of date. Run 'just update-tutorial-catalog'."
        )
    print("Tutorial catalog and root README are in sync.")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--write", action="store_true", help="rewrite the generated README section"
    )
    args = parser.parse_args()
    try:
        run(write=args.write)
    except (CatalogError, subprocess.CalledProcessError) as error:
        print(error, file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
