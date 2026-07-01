# Where Scheduled Agents Run

If an agent is scheduled, the main question is simple:

Does the scheduler run locally, or does it run in the cloud?

## Options

| Option | Where It Runs | Needs Your Machine On? | API Keys And Tools | Notes |
| --- | --- | --- | --- | --- |
| Claude Code `/loop` | Local Claude Code session | Yes | Uses your current session environment and local tools | Best for short polling while you are working |
| Claude Code Desktop scheduled task | Your machine | Yes | Uses local env, local config, and local tools | Best when the task needs files or tools only on your laptop |
| Claude Code Routine via `/schedule` | Anthropic cloud | No | Add environment variables and setup scripts to the cloud environment | Best for durable scheduled work |
| Claude Code GitHub Action | GitHub Actions runner | No | Use GitHub Secrets and install tools in the workflow | Good for PR, issue, CI, and cron-triggered repo work |
| Codex app automation | Your machine running Codex | Yes | Uses your Codex app environment and local tools | Best for recurring work against a local project or worktree |
| Codex cloud task | OpenAI cloud container | No | Configure the cloud environment | Best for cloud coding work from a repo checkout |
| Codex GitHub Action | GitHub Actions runner | No | Use GitHub Secrets and install tools in the workflow | Good for Codex tasks in CI or scheduled workflows |

## Simple Rule

Local scheduler means your machine needs to be on.

Cloud Routine, cloud Codex task, or GitHub Actions means your laptop can be off.

## Important Notes

- Claude Code `/loop` is session-scoped. It is useful for checking back every few minutes while you are working.
- Claude Code `/schedule` creates a cloud Routine. It does not need your laptop to stay on.
- Claude cloud Routines can use environment variables for API keys and setup scripts for CLI tools.
- Claude docs say cloud environments do not yet have a dedicated secrets store. Environment variables and setup scripts are visible to anyone who can edit that environment.
- GitHub Actions can run either Claude Code or Codex on a schedule using cron.
- GitHub Actions scheduled workflows run from the default branch. The shortest schedule interval is 5 minutes.

## Reply To A Viewer

```text
It depends which scheduler you use.

If you use a local loop, like Claude Code /loop, your machine and session need to be available. Claude Code Desktop scheduled tasks are also local, so your computer needs to be awake.

If you use Claude Code /schedule, that creates a cloud Routine, so it can run while your laptop is off. GitHub Actions also runs on GitHub's runners, so your machine does not need to be on.

For Codex, app automations are local and need the machine running Codex to be on. Codex can also run in cloud tasks, and Codex can run from GitHub Actions.
```

## References

- Claude Code scheduled tasks and `/loop`: <https://code.claude.com/docs/en/scheduled-tasks>
- Claude Code Routines: <https://code.claude.com/docs/en/routines>
- Claude Code Desktop scheduled tasks: <https://code.claude.com/docs/en/desktop-scheduled-tasks>
- Claude Code GitHub Actions: <https://code.claude.com/docs/en/github-actions>
- Codex automations: <https://developers.openai.com/codex/app/automations>
- Codex cloud environments: <https://developers.openai.com/codex/cloud/environments>
- Codex GitHub Action: <https://developers.openai.com/codex/github-action>
- GitHub Actions schedule event: <https://docs.github.com/en/actions/reference/workflows-and-actions/events-that-trigger-workflows#schedule>
