#!/usr/bin/env python3
"""Deterministic checks for tracked repository content."""

from __future__ import annotations

import argparse
import ast
import json
import re
import shutil
import subprocess
import sys
import tomllib
from pathlib import Path
from urllib.parse import unquote


ROOT = Path(__file__).resolve().parents[1]
CATALOG_PATH = ROOT / "tutorials" / "catalog.json"
VERIFICATION_PATH = ROOT / "scripts" / "tutorial_verification.json"
ALLOWED_TUTORIAL_ROOT_ITEMS = {"README.md", "LESSON.md", "code", "resources"}
REQUIRED_TUTORIAL_FILES = {"README.md", "LESSON.md"}
REQUIRED_TUTORIAL_PREFIXES = {"code/", "resources/", "resources/slides/"}
JUNK_PATTERN = re.compile(
    r"(^|/)(\.venv|venv|__pycache__|\.pytest_cache|\.ruff_cache|\.mypy_cache|"
    r"\.DS_Store|\.git/|node_modules|dist/|build/|\.lsp|\.clj-kondo|"
    r"\.ipynb_checkpoints|uv\.lock$|package-lock\.json$|pnpm-lock\.yaml$|"
    r"yarn\.lock$|bun\.lockb?$|Pipfile\.lock$|poetry\.lock$|Cargo\.lock$|"
    r".*\.log$|\.env$|\.env\.local$)"
)
MARKDOWN_LINK_PATTERN = re.compile(r"!?\[[^\]]*\]\(([^)\n]+)\)")
FENCED_BLOCK_PATTERN = re.compile(r"(^|\n)(```|~~~).*?\n\2", re.DOTALL)


def tracked_files(root: Path = ROOT) -> list[Path]:
    result = subprocess.run(
        ["git", "ls-files", "-z"],
        cwd=root,
        check=True,
        capture_output=True,
        text=True,
    )
    return [Path(filename) for filename in result.stdout.split("\0") if filename]


def catalog_slugs(path: Path = CATALOG_PATH) -> list[str]:
    payload = json.loads(path.read_text())
    return [tutorial["slug"] for tutorial in payload["tutorials"]]


def check_layout(files: list[Path], slugs: list[str]) -> list[str]:
    filenames = {path.as_posix() for path in files}
    errors: list[str] = []
    for slug in slugs:
        prefix = f"tutorials/{slug}/"
        tutorial_files = {
            filename.removeprefix(prefix)
            for filename in filenames
            if filename.startswith(prefix)
        }
        for required in sorted(REQUIRED_TUTORIAL_FILES):
            if required not in tutorial_files:
                errors.append(f"tutorials/{slug}: missing tracked {required}")
        for required_prefix in sorted(REQUIRED_TUTORIAL_PREFIXES):
            if not any(filename.startswith(required_prefix) for filename in tutorial_files):
                errors.append(
                    f"tutorials/{slug}: missing tracked {required_prefix.rstrip('/')} directory"
                )

        root_items = {Path(filename).parts[0] for filename in tutorial_files}
        extra = sorted(root_items - ALLOWED_TUTORIAL_ROOT_ITEMS)
        if extra:
            errors.append(f"tutorials/{slug}: unsupported root items {extra}")
    return errors


def check_root_docs(files: list[Path], slugs: list[str]) -> list[str]:
    known_slugs = set(slugs)
    errors: list[str] = []
    for path in files:
        parts = path.parts
        if (
            len(parts) == 3
            and parts[0] == "tutorials"
            and parts[1] in known_slugs
            and path.suffix == ".md"
            and parts[2] not in REQUIRED_TUTORIAL_FILES
        ):
            errors.append(f"{path}: move tutorial root reference docs into resources/")
    return errors


def check_junk(files: list[Path]) -> list[str]:
    return [
        f"{path}: tracked junk"
        for path in files
        if JUNK_PATTERN.search(path.as_posix())
    ]


def without_fenced_blocks(markdown: str) -> str:
    return FENCED_BLOCK_PATTERN.sub(
        lambda match: "\n" * match.group(0).count("\n"), markdown
    )


def local_markdown_links(markdown: str) -> list[tuple[int, str]]:
    text = without_fenced_blocks(markdown)
    links: list[tuple[int, str]] = []
    for match in MARKDOWN_LINK_PATTERN.finditer(text):
        raw_target = match.group(1).strip()
        if raw_target.startswith("<") and ">" in raw_target:
            target = raw_target[1 : raw_target.index(">")]
        else:
            target = raw_target.split(maxsplit=1)[0]
        if not target or target.startswith(
            ("#", "http://", "https://", "mailto:", "tel:")
        ):
            continue
        target = unquote(target.split("#", 1)[0])
        if not target:
            continue
        line = text.count("\n", 0, match.start()) + 1
        links.append((line, target))
    return links


def tracked_target_exists(target: Path, root: Path, tracked: set[str]) -> bool:
    try:
        relative = target.resolve().relative_to(root.resolve()).as_posix()
    except ValueError:
        return False
    if relative in {"", "."}:
        return True
    return relative in tracked or any(
        filename.startswith(relative.rstrip("/") + "/") for filename in tracked
    )


def check_markdown_links(root: Path, files: list[Path]) -> list[str]:
    errors: list[str] = []
    tracked = {path.as_posix() for path in files}
    for path in files:
        if path.suffix.lower() != ".md":
            continue
        full_path = root / path
        markdown = full_path.read_text(errors="replace")
        for line, target in local_markdown_links(markdown):
            resolved = full_path.parent / target
            if not tracked_target_exists(resolved, root, tracked):
                errors.append(f"{path}:{line}: missing local link target {target!r}")
    return errors


def check_verification_manifest(
    root: Path, files: list[Path], path: Path = VERIFICATION_PATH
) -> list[str]:
    payload = json.loads(path.read_text())
    entries = payload.get("tutorials")
    if not isinstance(entries, dict):
        return [f"{path.relative_to(root)}: expected a tutorials object"]

    code_bearing = {
        parts[1]
        for file in files
        if len(parts := file.parts) >= 4
        and parts[0] == "tutorials"
        and parts[2] == "code"
        and file.name != ".gitkeep"
    }
    manifest_slugs = set(entries)
    errors: list[str] = []
    if missing := sorted(code_bearing - manifest_slugs):
        errors.append(f"verification manifest missing code-bearing tutorials: {missing}")
    if extra := sorted(manifest_slugs - code_bearing):
        errors.append(f"verification manifest has tutorials without code: {extra}")

    valid_kinds = {"offline", "network", "static", "integration-only"}
    for slug, entry in sorted(entries.items()):
        if not isinstance(entry, dict):
            errors.append(f"{slug}: verification entry must be an object")
            continue
        kind = entry.get("kind")
        if kind not in valid_kinds:
            errors.append(f"{slug}: unsupported verification kind {kind!r}")
        if kind == "integration-only":
            if not str(entry.get("reason", "")).strip():
                errors.append(f"{slug}: integration-only entries need a reason")
        elif not isinstance(entry.get("commands"), list) or not entry["commands"]:
            errors.append(f"{slug}: {kind} entries need at least one command")
    return errors


def check_python_syntax(root: Path, files: list[Path]) -> list[str]:
    errors: list[str] = []
    for path in files:
        if path.suffix != ".py":
            continue
        try:
            ast.parse((root / path).read_text(), filename=str(path))
        except (SyntaxError, UnicodeDecodeError) as error:
            errors.append(f"{path}: {error}")
    return errors


def check_shell_syntax(root: Path, files: list[Path]) -> list[str]:
    errors: list[str] = []
    for path in files:
        if path.suffix != ".sh":
            continue
        result = subprocess.run(
            ["bash", "-n", str(path)], cwd=root, capture_output=True, text=True
        )
        if result.returncode:
            detail = result.stderr.strip() or "bash -n failed"
            errors.append(f"{path}: {detail}")
    return errors


def check_data_files(root: Path, files: list[Path]) -> list[str]:
    errors: list[str] = []
    for path in files:
        try:
            if path.suffix in {".json", ".ipynb"}:
                json.loads((root / path).read_text())
            elif path.suffix == ".toml":
                with (root / path).open("rb") as handle:
                    tomllib.load(handle)
        except (
            OSError,
            UnicodeDecodeError,
            json.JSONDecodeError,
            tomllib.TOMLDecodeError,
        ) as error:
            errors.append(f"{path}: {error}")
    return errors


def check_terraform_format(root: Path, files: list[Path]) -> list[str]:
    terraform_files = [path for path in files if path.suffix == ".tf"]
    if not terraform_files:
        return []
    if not shutil.which("terraform"):
        return ["terraform: command not found; install Terraform to check .tf formatting"]
    directories = sorted({str(path.parent) for path in terraform_files})
    errors: list[str] = []
    for directory in directories:
        result = subprocess.run(
            ["terraform", "fmt", "-check", "-diff"],
            cwd=root / directory,
            capture_output=True,
            text=True,
        )
        if result.returncode:
            detail = (result.stdout + result.stderr).strip()
            errors.append(f"{directory}: terraform fmt -check failed\n{detail}")
    return errors


def run_check(
    name: str, root: Path, files: list[Path], slugs: list[str]
) -> list[str]:
    checks = {
        "layout": lambda: check_layout(files, slugs),
        "root-docs": lambda: check_root_docs(files, slugs),
        "junk": lambda: check_junk(files),
        "markdown-links": lambda: check_markdown_links(root, files),
        "verification": lambda: check_verification_manifest(root, files),
        "syntax": lambda: check_python_syntax(root, files)
        + check_shell_syntax(root, files),
        "data": lambda: check_data_files(root, files),
        "terraform": lambda: check_terraform_format(root, files),
    }
    errors = checks[name]()
    if errors:
        return [f"[{name}] {error}" for error in errors]
    print(f"[{name}] OK")
    return []


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "check",
        choices=[
            "all",
            "layout",
            "root-docs",
            "junk",
            "markdown-links",
            "verification",
            "syntax",
            "data",
            "terraform",
        ],
    )
    args = parser.parse_args()
    files = tracked_files()
    slugs = catalog_slugs()
    names = (
        [
            "layout",
            "root-docs",
            "junk",
            "markdown-links",
            "verification",
            "syntax",
            "data",
            "terraform",
        ]
        if args.check == "all"
        else [args.check]
    )
    errors: list[str] = []
    for name in names:
        errors.extend(run_check(name, ROOT, files, slugs))
    if errors:
        print("\n".join(errors), file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
