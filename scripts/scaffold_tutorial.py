#!/usr/bin/env python3
"""Create a tutorial from the repository templates."""

from __future__ import annotations

import argparse
import re
import shutil
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SLUG_PATTERN = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")


def readme(title: str) -> str:
    return f"""# {title}

This is the supporting material for the video: {title}.

## Start Here

- Read the lesson: [LESSON.md](./LESSON.md)

Supporting code, prompts, resources, and slides are linked here only when the
tutorial includes real material to use.

## Go Deeper

To go deeper on AI engineering, join my AI engineering community:
[aiengineer.co](https://aiengineer.co).
"""


def scaffold(root: Path, slug: str, title: str) -> Path:
    if not SLUG_PATTERN.fullmatch(slug):
        raise ValueError("Slug must use lowercase letters, numbers, and hyphens only.")
    if not title.strip():
        raise ValueError("Title cannot be empty.")

    tutorial = root / "tutorials" / slug
    if tutorial.exists():
        raise FileExistsError(f"{tutorial.relative_to(root)} already exists.")

    templates = ROOT / "tutorials" / "_templates"
    (tutorial / "code").mkdir(parents=True)
    (tutorial / "resources" / "slides").mkdir(parents=True)

    lesson = (templates / "LESSON.md").read_text().replace(
        "# Lesson Title", f"# {title}", 1
    )
    (tutorial / "README.md").write_text(readme(title))
    (tutorial / "LESSON.md").write_text(lesson)
    shutil.copyfile(
        templates / "resources" / "prompts.md",
        tutorial / "resources" / "prompts.md",
    )
    (tutorial / "code" / ".gitkeep").touch()
    (tutorial / "resources" / "slides" / ".gitkeep").touch()
    return tutorial


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("slug")
    parser.add_argument("title")
    args = parser.parse_args()
    try:
        tutorial = scaffold(ROOT, args.slug, args.title)
    except (ValueError, FileExistsError) as error:
        print(error, file=sys.stderr)
        return 1

    print(f"Created {tutorial.relative_to(ROOT)}")
    print("Next: write LESSON.md, add only real resource links, then update tutorials/catalog.json.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
