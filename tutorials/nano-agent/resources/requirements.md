# Requirements

## Overview
Nano Agent is a terminal-based minimal coding agent built in Python using the Anthropic API. It serves as a teaching tool for developers who want to learn how to build coding agents from scratch. The codebase prioritizes simplicity and readability over feature completeness.

## Problem Statement
Developers who want to build their own coding agents have no simple, readable reference implementation to learn from. Existing tools (Claude Code, Cursor, etc.) are production systems with complex internals. Nano Agent provides a minimal, understandable implementation of the core agent loop with tool use, thinking traces, and a polished terminal UI.

## Users
- **Primary:** Developers learning how to build coding agents from scratch. They will read the source code, run the agent, and use it as a reference for their own implementations.

## Functional Requirements
<requirements>
- FR-01: The agent runs as a CLI application started from the terminal.
- FR-02: The agent accepts natural language input from the user in a REPL-style loop.
- FR-03: The agent maintains conversation history across turns within a single session (no persistent sessions across restarts).
- FR-04: The agent uses the Anthropic API with extended thinking (reasoning) enabled.
- FR-05: The agent's thinking/reasoning trace is displayed in the terminal as it processes a request.
- FR-06: The agent can read file contents (tool: read_file).
- FR-07: The agent can write/create files (tool: write_file).
- FR-08: The agent can search for files by name/pattern (tool: find_files).
- FR-09: The agent can list directory contents (tool: list_directory).
- FR-10: The agent can execute arbitrary bash commands (tool: run_bash).
- FR-11: The agent can spawn sub-agents to handle subtasks (tool: spawn_agent). Each sub-agent runs its own agent loop with its own conversation history.
- FR-12: The agent can spawn multiple sub-agents concurrently. Sub-agents run in parallel using asyncio.
- FR-13: Sub-agent results are collected and returned to the parent agent as tool results.
- FR-14: The agent loop emits lifecycle events at each stage: `PreToolUse`, `PostToolUse`, `Stop`, `SubagentStart`, `SubagentStop`.
- FR-15: Event listeners can be registered on the agent to respond to lifecycle events. Listeners are async callables that receive the event.
- FR-16: A listener can control flow by returning a value - e.g., a `PreToolUse` listener returns approve/deny to gate tool execution.
- FR-17: The terminal UI (Rich) is implemented as a set of event listeners, not called directly by the agent loop.
- FR-18: Tool call approval is implemented as an event listener on `PreToolUse`, keeping the approval logic outside the agent loop.
- FR-19: The agent does not use streaming; it waits for the full API response before displaying output.
- FR-20: The provider implementation is abstracted behind an interface so that additional LLM providers can be added later without changing the agent loop.
</requirements>

## Non-Functional Requirements
<nfr>
- NFR-01: The codebase is structured for readability - simple modules, clear naming, minimal abstraction. A developer unfamiliar with the project can understand the full agent loop by reading the code.
- NFR-02: The project is installable and runnable via `uv` (no pip/poetry).
- NFR-03: The project uses `pytest` for testing.
- NFR-04: The agent handles API errors (rate limits, network failures) with clear error messages displayed to the user - no silent failures.
- NFR-05: The agent exits cleanly on Ctrl+C / EOF without traceback.
</nfr>

## Out of Scope
- Persistent sessions or conversation history across restarts.
- Streaming responses from the API.
- Multi-provider support in MVP (architecture supports it, but only Anthropic is implemented).
- File editing with diff-based patching (write_file overwrites; no surgical edits).
- Autonomous mode (all tool calls require user approval in MVP).
- Web search, URL fetching, or any network tools beyond the LLM API.
- Configuration files or settings management.
- Plugin or extension system.

## Success Metrics
- A developer can clone the repo, run `uv run nano-agent`, and interact with a working coding agent within 2 minutes.
- A developer can read and understand the entire agent loop (prompt → API call → tool execution → response) in under 30 minutes.
- All 6 tools (read_file, write_file, find_files, list_directory, run_bash, spawn_agent) execute correctly and display their results in the terminal.
- The agent loop contains zero UI or approval logic - all side effects are handled by event listeners.
- The thinking trace and tool call display are visually distinct and easy to follow in the terminal.

## Assumptions
- [ASSUMED] Python 3.12+ is the minimum supported version (per project standards).
- [ASSUMED] The default Anthropic model is Claude Sonnet (latest) - configurable via environment variable or CLI flag.
- [ASSUMED] The Anthropic API key is provided via the `ANTHROPIC_API_KEY` environment variable.
- [ASSUMED] Tool call approval is a simple y/n prompt per tool call (no batch approval or "approve all" mode).
- [ASSUMED] No authentication, permissions, or sandboxing for bash command execution.
- [ASSUMED] The Rich library is used for terminal UI rendering.

## Open Questions
- [TBD] Should tool results (e.g., file contents, command output) be truncated after a certain length to keep the terminal readable? - Affects UX for large files/outputs. (YES)
- [TBD] Should the agent have a system prompt that defines its persona and capabilities, or is the tool list sufficient? - Affects response quality. (YES we need a basic agent system prompt)
- [TBD] What is the CLI entry point name? (`nano-agent`, `na`, something else?) - Affects packaging and pyproject.toml config.
