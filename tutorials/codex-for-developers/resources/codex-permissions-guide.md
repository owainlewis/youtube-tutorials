# Codex Permissions Guide

This is the simple version.

If you only remember one thing, remember this:

> Sandbox is where Codex can act. Network is whether commands can go online. Approval is whether Codex asks first.

---

## The 3 Settings

| Setting | What it controls | Best default |
|---|---|---|
| `sandbox_mode` | Where Codex can read/write and what it can run safely | `workspace-write` |
| `network_access` | Whether shell commands can use the internet | Only on when needed |
| `approval_policy` | Whether Codex asks before crossing a boundary | `on-request` |

---

## The Simple Matrix

This is the easiest way to explain it:

| Situation | Sandbox | Network | Approval |
|---|---|---|---|
| Review only | `read-only` | Off | `on-request` |
| Normal coding | `workspace-write` | Off or on if needed | `on-request` |
| Installing packages or calling APIs | `workspace-write` | On | `on-request` |
| Fully hands-off in a trusted environment | `workspace-write` or `danger-full-access` | On if needed | `never` |

---

## What The Sandbox Modes Mean

| Mode | Plain English | Use it when |
|---|---|---|
| `read-only` | Codex can inspect, but not really change things | Review, explain, analyze |
| `workspace-write` | Codex can edit inside the project | Normal day-to-day coding |
| `danger-full-access` | Codex can do anything your user account can do | Only in a trusted disposable environment |

Good default:

```toml
sandbox_mode = "workspace-write"
approval_policy = "on-request"
```

---

## What Approval Actually Means

| Codex approval policy | Behavior | Claude equivalent |
|---|---|---|
| `untrusted` | Always ask before actions | Normal safe mode |
| `on-request` | Ask only when escalation is needed | Partial guardrails (default) |
| `on-failure` | Ask only if something breaks | No direct equivalent |
| `never` | Never ask, just execute | `--dangerously-skip-permissions` |

Important:

> Approval does not create permission. It only decides whether Codex asks before trying.

Setting `approval_policy = "never"` is YOLO mode. Commands run immediately, file edits happen without confirmation, no "are you sure?" checkpoints. The agent decides and executes in one loop.

---

## Common Examples

| Action | Result in normal setup |
|---|---|
| Edit a file in the repo | Usually allowed |
| Run tests in the repo | Usually allowed |
| Edit a file on the Desktop | Usually asks or needs escalation |
| Run `npm install` | Needs network access |
| Run `curl ...` | Needs network access |
| Ask Codex to search the web | Separate from shell network access |

---

## The One Confusing Bit

There are two different internet paths:

| Thing | Controlled by |
|---|---|
| `npm install`, `uv sync`, `curl`, scripts calling APIs | command `network_access` |
| Codex using built-in web search/fetch tools | web/search settings inside Codex |

That is why shell `curl` can be blocked while Codex can still look something up with its own web tools.

---

## Good Defaults

### Safe everyday coding

```toml
sandbox_mode = "workspace-write"
approval_policy = "on-request"
```

Turn network on only if you actually need installs or API calls.

### Review only

```toml
sandbox_mode = "read-only"
approval_policy = "on-request"
```

### Trusted automation

Use `never` only when you understand the tradeoff.

Do not jump to full access unless you really need it.

---

## One Good Rule

If Codex needs another directory, do this:

```bash
codex --add-dir /path/to/other/folder
```

Do not jump straight to:

```bash
codex --dangerously-bypass-approvals-and-sandbox
```

---

## Matching Claude Code's "Dangerously Skip Permissions"

If you already use Claude Code, you may know the `--dangerously-skip-permissions` flag. It bypasses safety confirmations so the agent proceeds with all actions without asking. Here is the Codex equivalent.

| | Claude Code | Codex |
|---|---|---|
| One-off flag | `claude --dangerously-skip-permissions` | `codex --dangerously-bypass-approvals-and-sandbox` |
| Config equivalent | Flag only, not configurable | `sandbox_mode = "danger-full-access"` + `approval_policy = "never"` |
| Scope | Full system access as current user | Full system access as current user |

The config equivalent in Codex:

```toml
sandbox_mode = "danger-full-access"
approval_policy = "never"
```

Or as a named profile you can switch to without changing the default:

```toml
[profiles.yolo]
sandbox_mode = "danger-full-access"
approval_policy = "never"
```

Activate with:

```bash
codex --profile yolo
```

**Key differences.**

- Claude's mode is a flag you type each time and cannot be set as a default in config. Codex lets you bake it into a named profile — more convenient for scripts and automation, but easier to leave on by accident.
- Codex with `never` is still constrained by sandbox mode and environment permissions. Claude's `--dangerously-skip-permissions` more explicitly disables all permission prompts with fewer guardrails underneath.
- For day-to-day use they are functionally equivalent: the agent decides and executes without asking.

Use either only in a trusted, disposable environment — a Docker container, a CI sandbox, a VM you can discard. Not on your main machine where the agent can touch anything your user account can touch.

---

## 20-Second Explanation

If you need a quick way to say it in the video:

1. `workspace-write` is the normal default.
2. `on-request` is the normal approval mode.
3. Turn network on only when you actually need it.
4. Use `read-only` for review.
5. Avoid full access unless the environment is already safe.
