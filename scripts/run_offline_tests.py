#!/usr/bin/env python3
"""Run the repository's tutorial verification matrix."""

from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


MANIFEST_PATH = ROOT / "scripts" / "tutorial_verification.json"
DEFAULT_KINDS = frozenset({"offline", "static"})


def selected_entries(
    entries: dict[str, dict[str, object]], requested_kind: str
) -> list[tuple[str, dict[str, object]]]:
    """Return stable manifest entries for a requested verification group."""
    kinds = DEFAULT_KINDS if requested_kind == "offline" else {requested_kind}
    return [
        (slug, entry)
        for slug, entry in sorted(entries.items())
        if entry["kind"] in kinds
    ]


def run(kind: str) -> int:
    entries = json.loads(MANIFEST_PATH.read_text())["tutorials"]
    selected = selected_entries(entries, kind)
    if not selected:
        print(f"No {kind} tutorial checks are configured.")
        return 0
    for tutorial, entry in selected:
        for item in entry["commands"]:
            command = list(item["run"])
            if command[0] == "python":
                command[0] = sys.executable
            executable = command[0]
            directory = ROOT / item["cwd"]
            environment = os.environ.copy()
            environment.setdefault("PYTHONDONTWRITEBYTECODE", "1")
            environment.setdefault("PYTEST_ADDOPTS", "-p no:cacheprovider")
            environment.update(item.get("env", {}))
            printable = " ".join(command)
            if not shutil.which(executable):
                print(f"[{tutorial}] missing command: {executable}", file=sys.stderr)
                return 1
            print(f"\n[{tutorial}] {printable}", flush=True)
            result = subprocess.run(command, cwd=directory, env=environment)
            if result.returncode:
                print(
                    f"[{tutorial}] failed with exit code {result.returncode}: {printable}",
                    file=sys.stderr,
                )
                return result.returncode
    print(f"\nAll {kind} tutorial tests passed.")
    return 0


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--kind", choices=["offline", "network"], default="offline")
    raise SystemExit(run(parser.parse_args().kind))
