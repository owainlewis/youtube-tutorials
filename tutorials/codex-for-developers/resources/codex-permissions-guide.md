# Codex Permissions Guide

Last verified against the official OpenAI documentation: 2026-08-04.

If you remember one thing, remember this:

> The sandbox controls what Codex can do. The approval policy controls when Codex pauses to ask.

## The Main Settings

| Setting | What it controls | Normal starting point |
| --- | --- | --- |
| `sandbox_mode` | Filesystem and command boundaries. | `workspace-write` in a trusted Git repository. |
| `approval_policy` | When Codex pauses for approval. | `on-request` for interactive work. |
| `sandbox_workspace_write.network_access` | Whether commands in the workspace-write sandbox can reach the network. | `false` unless the task needs it. |

OpenAI calls workspace write with on-request approvals the Auto combination:

```toml
sandbox_mode = "workspace-write"
approval_policy = "on-request"
```

## Sandbox Modes

| Mode | Plain meaning | Useful for |
| --- | --- | --- |
| `read-only` | Inspect without making normal workspace edits. | Explanation, audit, and review. |
| `workspace-write` | Read and edit inside the active workspace. | Normal repository work. |
| `danger-full-access` | Run without the local sandbox boundary. | A controlled environment that already provides isolation. |

Use `/permissions` to inspect or change the active mode. Use `/status` to inspect the workspace roots and current configuration.

## Approval Policies

| Policy | Behavior |
| --- | --- |
| `untrusted` | Ask before commands that are not classified as known-safe reads. |
| `on-request` | Work inside the sandbox and ask when an action needs a wider boundary. |
| `never` | Never show an approval prompt. The sandbox still limits the run. |

`on-failure` is deprecated. Use `on-request` for interactive work or `never` for non-interactive runs.

Approval does not grant access by itself. For example, `never` with `read-only` remains read-only.

## Network Access

Command network access is off by default in the workspace-write sandbox. Enable it only when the task needs package installation or an external API:

```toml
[sandbox_workspace_write]
network_access = true
```

This setting controls programs launched by commands, such as `curl`, package managers, and test code that calls external services. Codex web search has separate controls.

## Useful Combinations

### Normal coding

```toml
sandbox_mode = "workspace-write"
approval_policy = "on-request"
```

### Review only

```toml
sandbox_mode = "read-only"
approval_policy = "on-request"
```

### Read-only automation

```toml
sandbox_mode = "read-only"
approval_policy = "never"
```

Only use full access when the surrounding machine, container, or VM already provides the boundary you need. The one-off full-access flag is deliberately named:

```bash
codex --dangerously-bypass-approvals-and-sandbox
```

Do not use it as a shortcut around a configuration problem.

## Add One Extra Directory

If the task needs another directory, grant that directory instead of removing the whole sandbox:

```bash
codex --add-dir /path/to/other/folder
```

## References

- [Agent approvals and security](https://developers.openai.com/codex/agent-approvals-security)
- [Configuration reference](https://developers.openai.com/codex/config-reference)

## Short Explanation

1. Start with workspace write and on-request approvals for normal repository work.
2. Use read-only for explanation and review.
3. Keep command network access off until a task needs it.
4. Expand one boundary at a time.
5. Use full access only inside an environment you already trust for that level of access.
