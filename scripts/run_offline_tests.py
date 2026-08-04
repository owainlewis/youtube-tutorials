#!/usr/bin/env python3
"""Run credential-free tests already provided by tutorial samples."""

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


def run(kind: str) -> int:
    entries = json.loads(MANIFEST_PATH.read_text())["tutorials"]
    selected = [
        (slug, entry)
        for slug, entry in sorted(entries.items())
        if entry["kind"] == kind
    ]
    for tutorial, entry in selected:
        for item in entry["commands"]:
            command = list(item["run"])
            if command[0] == "python":
                command[0] = sys.executable
            executable = command[0]
            directory = ROOT / item["cwd"]
            environment = os.environ.copy()
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
