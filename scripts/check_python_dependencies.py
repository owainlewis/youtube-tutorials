#!/usr/bin/env python3
"""Resolve every tracked Python tutorial manifest without writing lockfiles."""

from __future__ import annotations

import subprocess
import sys
import tempfile
import tomllib
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def tracked_pyprojects(root: Path = ROOT) -> list[Path]:
    result = subprocess.run(
        ["git", "ls-files", "-z"],
        cwd=root,
        check=True,
        capture_output=True,
        text=True,
    )
    paths = [Path(filename) for filename in result.stdout.split("\0") if filename]
    return sorted(
        path
        for path in paths
        if len(path.parts) == 4
        and path.parts[0] == "tutorials"
        and path.parts[2] == "code"
        and path.name == "pyproject.toml"
    )


def compile_command(pyproject: Path, output: Path) -> list[str]:
    with pyproject.open("rb") as handle:
        payload = tomllib.load(handle)
    command = [
        "uv",
        "pip",
        "compile",
        str(pyproject),
        "--all-extras",
        "--python-version",
        "3.12",
        "--output-file",
        str(output),
        "--quiet",
    ]
    for group in sorted(payload.get("dependency-groups", {})):
        command.extend(["--group", f"{pyproject}:{group}"])
    return command


def run() -> int:
    projects = tracked_pyprojects()
    with tempfile.TemporaryDirectory(prefix="tutorial-dependencies-") as directory:
        output_dir = Path(directory)
        for pyproject in projects:
            slug = pyproject.parts[1]
            command = compile_command(pyproject, output_dir / f"{slug}.txt")
            print(f"[{slug}] resolving current dependencies", flush=True)
            result = subprocess.run(command, cwd=ROOT, capture_output=True, text=True)
            if result.returncode:
                detail = (result.stdout + result.stderr).strip()
                print(f"[{slug}] dependency resolution failed\n{detail}", file=sys.stderr)
                return result.returncode
    print(f"Resolved {len(projects)} Python tutorial manifests without lockfiles.")
    return 0


if __name__ == "__main__":
    raise SystemExit(run())
