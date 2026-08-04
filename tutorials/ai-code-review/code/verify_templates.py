#!/usr/bin/env python3
"""Verify the AI code review templates without changing a real project."""

from __future__ import annotations

import json
import os
import shutil
import stat
import subprocess
import tempfile
from pathlib import Path


TUTORIAL_ROOT = Path(__file__).resolve().parents[1]
RESOURCES = TUTORIAL_ROOT / "resources"


def run(
    *args: str,
    cwd: Path | None = None,
    check: bool = True,
    env: dict[str, str] | None = None,
) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        args,
        cwd=cwd,
        check=check,
        capture_output=True,
        text=True,
        env=env,
    )


def load_json(path: Path) -> dict[str, object]:
    with path.open(encoding="utf-8") as handle:
        value = json.load(handle)
    if not isinstance(value, dict):
        raise ValueError(f"{path} must contain a JSON object")
    return value


def verify_source_templates() -> None:
    settings_path = RESOURCES / "hooks" / "settings.json"
    stop_hook_path = RESOURCES / "hooks" / "stop-hook.json"
    script_path = RESOURCES / "hooks" / "stop-checks.sh"

    settings = load_json(settings_path)
    stop_hook = load_json(stop_hook_path)

    stop_command = settings["hooks"]["Stop"][0]["hooks"][0]["command"]  # type: ignore[index]
    if stop_command != ".claude/hooks/stop-checks.sh":
        raise ValueError("settings.json does not point to the documented stop hook destination")

    agent_prompt = stop_hook["hooks"]["Stop"][0]["hooks"][0]["prompt"]  # type: ignore[index]
    if "$ARGUMENTS" not in agent_prompt or '"ok": false' not in agent_prompt:
        raise ValueError("stop-hook.json must include the hook input and blocking response format")

    if not script_path.stat().st_mode & stat.S_IXUSR:
        raise ValueError("stop-checks.sh must be executable")

    run("bash", "-n", str(script_path))


def verify_installed_templates() -> None:
    with tempfile.TemporaryDirectory(prefix="ai-code-review-") as temporary_directory:
        project = Path(temporary_directory)
        hooks_directory = project / ".claude" / "hooks"
        hooks_directory.mkdir(parents=True)

        shutil.copy2(
            RESOURCES / "hooks" / "settings.json",
            project / ".claude" / "settings.local.json",
        )
        installed_hook = shutil.copy2(
            RESOURCES / "hooks" / "stop-checks.sh",
            hooks_directory / "stop-checks.sh",
        )
        shutil.copy2(RESOURCES / "examples" / "REVIEW.md", project / "REVIEW.md")

        run("git", "init", "--quiet", cwd=project)
        example = project / "example.py"
        example.write_text("value = 1\n", encoding="utf-8")
        run("git", "add", "example.py", cwd=project)
        run(
            "git",
            "-c",
            "user.name=Template Verifier",
            "-c",
            "user.email=verifier@example.invalid",
            "commit",
            "--quiet",
            "-m",
            "fixture",
            cwd=project,
        )
        example.write_text("value = 2\n", encoding="utf-8")

        fake_bin = project / "fake-bin"
        fake_bin.mkdir()
        fake_ruff = fake_bin / "ruff"
        fake_ruff.write_text("#!/bin/sh\nexit 0\n", encoding="utf-8")
        fake_ruff.chmod(fake_ruff.stat().st_mode | stat.S_IXUSR)
        environment = os.environ.copy()
        environment["PATH"] = f"{fake_bin}{os.pathsep}{environment['PATH']}"

        passing_result = run(
            "bash", str(installed_hook), cwd=project, check=False, env=environment
        )
        if passing_result.returncode != 0:
            raise ValueError("installed stop hook did not allow a passing Ruff result")

        fake_ruff.write_text("#!/bin/sh\nexit 1\n", encoding="utf-8")
        blocking_result = run(
            "bash", str(installed_hook), cwd=project, check=False, env=environment
        )
        if blocking_result.returncode != 2 or "Ruff failures" not in blocking_result.stdout:
            raise ValueError("installed stop hook did not block a failing Ruff result")


def main() -> None:
    verify_source_templates()
    verify_installed_templates()
    print("Template verification passed.")


if __name__ == "__main__":
    main()
