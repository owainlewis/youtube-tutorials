# Example AGENTS.md Herdr Section

Copy this into a project-level `AGENTS.md` when Herdr is part of the coding-agent workflow.

```md
## Herdr

Herdr is the terminal workspace for this project when `HERDR_ENV=1` is set.

When running inside Herdr:

- Use `herdr pane list` to inspect panes before assuming what is running.
- Use `herdr agent list` to inspect known coding agents.
- Use `herdr pane read <pane-id> --source recent --lines 80` to read sibling pane output.
- Use `herdr wait output` for servers, tests, and logs.
- Use `herdr wait agent-status` for coding agents.
- Use `--no-focus` when creating helper panes.
- Prefer running tests and servers in sibling panes instead of interrupting the user's active pane.
- Do not close panes, stop servers, or send input to another agent unless the user asked or the task clearly requires it.

When helping a human set up or troubleshoot Herdr, read this first:

https://herdr.dev/agent-guide.md

Do not invent Herdr commands, config keys, or keybindings. Use the official docs when unsure:

https://herdr.dev/docs/
```

The key rule is simple: Herdr can make agents more capable, but the agent still needs boundaries.
