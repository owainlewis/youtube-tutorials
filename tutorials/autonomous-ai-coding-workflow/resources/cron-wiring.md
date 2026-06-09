# Cron Wiring Example

The exact scheduler does not matter as much as the workflow boundary.

Use whatever is easiest in your environment:

- Codex Automations
- Claude Code schedules
- GitHub Actions
- a cron job on a VPS
- a local cron job while testing

## Example Cadence

```text
Every 12 hours:
  Run backlog-manager apply

Every day:
  Run codex-run-loop for one risk:low + agent:ready issue
```

## Pseudocode

```bash
# 08:00 and 20:00
agent run "$BACKLOG_MANAGER_PROMPT"

# 09:00
agent run "$ISSUE_TO_PR_PROMPT"
```

## Production Notes

Run in dry-run mode before enabling apply mode.

Keep the execution loop linear at first:

- one issue
- one branch or worktree
- one draft PR
- one human review

Use parallel work only when the review process can handle it.

The automation should never merge code by default.

