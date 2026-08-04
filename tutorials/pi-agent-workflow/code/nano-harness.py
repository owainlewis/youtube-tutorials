#!/usr/bin/env python3
# /// script
# requires-python = ">=3.12"
# dependencies = ["anthropic>=0.40.0", "python-dotenv>=1.0.0"]
# ///
"""
nano-harness — a teaching-scale coding agent harness.

A coding agent = a model + a harness.

    The model decides what to do next.
    The harness actually does it, then feeds the result back.

That's the whole idea. Everything below is a concrete version of those
two sentences. Claude Code, Codex, Cursor, and Pi are all elaborate
versions of this same loop.

Usage:
    cp .env.example .env
    uv run nano-harness.py
"""
import os
import platform
import subprocess
import sys
import threading
import time
from itertools import cycle
from pathlib import Path

from anthropic import Anthropic
from dotenv import load_dotenv

load_dotenv()
client = Anthropic()
MODEL = os.getenv("ANTHROPIC_MODEL", "claude-sonnet-4-6")


# ── System prompt ─────────────────────────────────────────────────────
# The system prompt gives the model an identity, environment, and tool
# guidance. Focused context helps it make grounded decisions.
#
# Real harnesses (Claude Code, Codex) assemble this dynamically per
# turn: cwd, git status, open files, project conventions (CLAUDE.md),
# recently edited files. Here we keep it static and minimal.

SYSTEM_PROMPT = f"""You are a coding agent running in a terminal harness.

Environment:
- Working directory: {os.getcwd()}
- Platform: {platform.platform()}
- Shell: bash

Tools available:
- bash: run shell commands. Prefer `rg` over `grep`, `fd` over `find`.
- read_file: read a file with line numbers. Read before you edit.
- edit_file: replace exact text in a file. The old_string must appear
  exactly once — include surrounding context to make it unique.

Be concise. Take actions yourself rather than asking the user."""


# ── Tools ─────────────────────────────────────────────────────────────
# Three tools. Bash is the universal solvent, but structured read/edit
# tools give the model better signal (line numbers, exact-match edits)
# and give the harness something reviewable to show in the approval
# gate. Real harnesses add Grep, Glob, Write, and MCP-loaded tools.
#
# The trailing `cache_control` marks the end of the cacheable tool
# block — see the "Prompt caching" section below.

TOOLS = [
    {
        "name": "bash",
        "description": "Run a bash command. Returns stdout and stderr.",
        "input_schema": {
            "type": "object",
            "properties": {"command": {"type": "string"}},
            "required": ["command"],
        },
    },
    {
        "name": "read_file",
        "description": "Read a file's contents with 1-indexed line numbers.",
        "input_schema": {
            "type": "object",
            "properties": {
                "path": {"type": "string"},
                "offset": {"type": "integer", "description": "Line to start from (0-indexed)."},
                "limit": {"type": "integer", "description": "Max lines to return."},
            },
            "required": ["path"],
        },
    },
    {
        "name": "edit_file",
        "description": (
            "Replace exact text in a file. `old_string` must appear "
            "exactly once — include surrounding context to make it unique."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "path": {"type": "string"},
                "old_string": {"type": "string"},
                "new_string": {"type": "string"},
            },
            "required": ["path", "old_string", "new_string"],
        },
        "cache_control": {"type": "ephemeral"},
    },
]


def run_bash(command: str) -> str:
    result = subprocess.run(
        command, shell=True, capture_output=True, text=True, timeout=60,
    )
    return (result.stdout + result.stderr).strip() or "(no output)"


def read_file(path: str, offset: int = 0, limit: int = 2000) -> str:
    lines = Path(path).read_text().splitlines()
    chunk = lines[offset : offset + limit]
    return "\n".join(f"{i + 1:6}\t{line}" for i, line in enumerate(chunk, start=offset))


def edit_file(path: str, old_string: str, new_string: str) -> str:
    p = Path(path)
    text = p.read_text()
    count = text.count(old_string)
    if count == 0:
        return f"Error: old_string not found in {path}"
    if count > 1:
        return f"Error: old_string matches {count} times in {path}; must be unique"
    p.write_text(text.replace(old_string, new_string))
    return f"Edited {path}"


def run_tool(name: str, args: dict) -> str:
    if name == "bash":
        return run_bash(args["command"])
    if name == "read_file":
        return read_file(args["path"], args.get("offset", 0), args.get("limit", 2000))
    if name == "edit_file":
        return edit_file(args["path"], args["old_string"], args["new_string"])
    return f"Unknown tool: {name}"


# ── Events ────────────────────────────────────────────────────────────
# The harness emits events at lifecycle points. Anything can subscribe:
# loggers, telemetry, UIs, guardrails. Hooks — user-defined callbacks
# that gate or react to specific events — are just one consumer pattern
# built on top. Claude Code's hook system is this idea, scaled up.
#
# Veto convention: a listener on a pre_* event returning False cancels
# the action. That's what turns a passive event bus into an active gate.

LISTENERS: dict[str, list] = {}

def on(event: str):
    def subscribe(fn):
        LISTENERS.setdefault(event, []).append(fn)
        return fn
    return subscribe

def emit(event: str, **payload) -> bool:
    """Notify every listener for `event`. Returns False if any vetoed."""
    for fn in LISTENERS.get(event, []):
        if fn(**payload) is False:
            return False
    return True


# ── Spinner ───────────────────────────────────────────────────────────
# Claude Code's UX trick: don't stream tokens, show a spinner while the
# model thinks. Cleaner terminal, no half-rendered output, no cursor
# jitter. The completed response is printed as one block.

class Spinner:
    def __init__(self, label: str = "thinking"):
        self.label, self._stop = label, threading.Event()
    def __enter__(self):
        self._t = threading.Thread(target=self._spin, daemon=True)
        self._t.start()
        return self
    def __exit__(self, *_):
        self._stop.set()
        self._t.join()
        sys.stdout.write("\r\033[K"); sys.stdout.flush()
    def _spin(self):
        for c in cycle("⠋⠙⠹⠸⠼⠴⠦⠧⠇⠏"):
            if self._stop.is_set(): return
            sys.stdout.write(f"\r\033[90m{c} {self.label}\033[0m"); sys.stdout.flush()
            time.sleep(0.08)


# ── Model call + prompt caching ───────────────────────────────────────
# `cache_control: {type: "ephemeral"}` marks a *boundary*: everything up
# to and including that marker can be reused according to the provider's
# cache policy. We mark:
#   • the end of the system prompt
#   • the end of the tools array (see TOOLS above)
# Later turns may reuse the eligible system and tool content, depending
# on the provider's cache policy.
#
# Real harnesses may also cache stable message prefixes such as early
# turns and loaded files.

def call_model(messages: list):
    with Spinner():
        return client.messages.create(
            model=MODEL,
            max_tokens=4096,
            system=[{
                "type": "text",
                "text": SYSTEM_PROMPT,
                "cache_control": {"type": "ephemeral"},
            }],
            tools=TOOLS,
            messages=messages,
        )


# ── The loop ──────────────────────────────────────────────────────────
# Read top to bottom:
#   1. Ask the model what to do.
#   2. If it's done talking, return.
#   3. For each tool call: emit pre_tool (may veto), run, emit post_tool.
#   4. Send results back. Repeat.

def agent(messages: list) -> None:
    while True:
        response = call_model(messages)
        messages.append({"role": "assistant", "content": response.content})

        for block in response.content:
            if block.type == "text" and block.text.strip():
                emit("model_text", text=block.text)

        if response.stop_reason == "end_turn":
            emit("turn_end")
            return

        tool_results = []
        for block in response.content:
            if block.type != "tool_use":
                continue
            if emit("pre_tool", tool=block.name, args=block.input):
                output = run_tool(block.name, block.input)
            else:
                output = "(denied by user)"
            emit("post_tool", tool=block.name, args=block.input, output=output)
            tool_results.append({
                "type": "tool_result",
                "tool_use_id": block.id,
                "content": output,
            })

        messages.append({"role": "user", "content": tool_results})


# ── Listeners ─────────────────────────────────────────────────────────
# Everything below subscribes to events emitted by the loop above. The
# loop doesn't know they exist — comment any of them out and it still
# runs. `approve` is a hook in the strict sense (gates an action via
# veto); the others are observers.

def _summarize(tool: str, args: dict) -> str:
    if tool == "bash":      return f"$ {args['command']}"
    if tool == "read_file": return f"read {args['path']}"
    if tool == "edit_file": return f"edit {args['path']}"
    return f"{tool}({args})"

@on("model_text")
def show_model_text(text: str) -> None:
    print(f"\n\033[36m{text}\033[0m")

@on("pre_tool")
def approve(tool: str, args: dict) -> bool:
    print(f"\n\033[33m?\033[0m {_summarize(tool, args)}")
    return input("\033[33m  approve [y/N]: \033[0m").strip().lower() == "y"

@on("post_tool")
def show_output(tool: str, args: dict, output: str) -> None:
    display = output if len(output) < 500 else f"{output[:500]}\n... ({len(output)} chars total)"
    print(f"\033[90m{display}\033[0m")


# ── REPL ──────────────────────────────────────────────────────────────
# Persistent message history across turns so the agent remembers what
# it just did. Ctrl-C to exit.

def main():
    print("\033[1mnano-harness\033[0m — Ctrl-C to exit.")
    messages = []
    while True:
        try:
            goal = input("\n\033[32m> \033[0m").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            return
        if goal:
            messages.append({"role": "user", "content": goal})
            agent(messages)


if __name__ == "__main__":
    main()
