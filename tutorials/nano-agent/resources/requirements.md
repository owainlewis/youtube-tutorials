# Nano Agent Requirements and Boundaries

## Purpose

Nano Agent is a readable Python reference for developers learning how terminal coding agents work. Simplicity and inspectable behavior matter more than feature coverage.

## Implemented behavior

- Run as the `nano-agent` terminal command.
- Keep conversation history in memory for one process.
- Use the Anthropic Messages API through a small provider interface.
- Configure adaptive, manual, or disabled thinking.
- Register seven tools in an explicit dictionary: `read_file`, `edit_file`, `write_file`, `find_files`, `list_directory`, `run_bash`, and `spawn_agent`.
- Ask for approval before every parent tool call.
- Run approved child agents concurrently when the model requests several in one response.
- Prevent child agents from spawning more children.
- Stop each parent or child request after a configurable number of model calls.
- Emit typed lifecycle events for UI, approval, and logging listeners.
- Exit cleanly on Ctrl+C or EOF.

## Quality requirements

- Python 3.12 or newer.
- One `uv` setup path.
- Credential-free tests with a mocked Anthropic client.
- Clear provider and tool errors instead of silent failures.
- No UI or logging imports in the core loop.
- Config values that affect safety or API validity are validated before the REPL starts.

## Deliberate limits

- No saved sessions.
- No streaming.
- No context compaction.
- No retry policy.
- No command sandbox or resource isolation.
- No network isolation.
- No diff-based patch tool.
- No model cost tracking.
- No plugins or MCP support.

This project is educational. A turn limit bounds model calls but does not bound what an approved shell command can do. A parent approval for `spawn_agent` also authorizes that child to use its normal tools without further prompts.

## Verification

From [`../code/`](../code/):

```bash
uv run pytest
```

The tests cover all implemented requirements without an API key.
