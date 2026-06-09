# My Autonomous AI Coding Workflow

Companion resources for the YouTube video:

**My Autonomous AI Coding Workflow (Codex + Claude Code)**

The workflow has two loops:

1. **Outer loop:** manage the backlog, classify work, and create a safe queue.
2. **Inner loop:** pick one safe issue, implement it, verify it, and open a draft PR.

The point is not to let agents do everything. The point is to automate the parts of the development workflow that are clear, repeated, low-risk, and easy to review.

## Skills

Install the public skills:

```bash
npx skills@latest add owainlewis/agent-skills
```

The video uses:

| Skill | Job |
|---|---|
| `backlog-manager` | Reviews GitHub Issues or Linear, applies risk/type/agent labels, creates evidence-backed maintenance tickets, and keeps the backlog tidy. |
| `codex-run-loop` | Coordinates Codex worker threads or worktrees that turn one or more issues into draft PRs. |

## Labels

The backlog manager uses a small fixed label set.

Risk:

- `risk:low`
- `risk:medium`
- `risk:high`

Type:

- `type:bug`
- `type:feature`
- `type:docs`
- `type:test`
- `type:refactor`
- `type:chore`

Agent routing:

- `agent:ready`
- `agent:blocked`
- `agent:complete`

Human routing:

- `needs:human`

The execution loop should usually only pick issues with:

```text
risk:low
agent:ready
```

It should skip anything with:

```text
needs:human
agent:blocked
```

## Demo Flow

### 1. Run the outer loop

Use the backlog manager in dry-run mode first:

```text
$backlog-manager dry-run GitHub backlog for owner/repo
```

Then apply changes when the dry run looks safe:

```text
$backlog-manager apply GitHub backlog for owner/repo
```

The backlog manager should:

- inspect open issues
- inspect linked pull requests
- inspect the project board when available
- create missing labels
- classify risk and type
- add Agent Assessment comments
- create new issues only when there is clear evidence of a real problem
- mark unclear work with `needs:human`

### 2. Run the inner loop

Use the Codex run loop to pick one safe issue and open a draft PR:

```text
$codex-run-loop

Find one open GitHub issue in owner/repo with both labels:
- risk:low
- agent:ready

Skip issues with:
- needs:human
- agent:blocked

For the selected issue:
1. Write a short implementation plan.
2. Create a branch or worktree.
3. Make the smallest complete fix.
4. Run the relevant checks.
5. Run a reviewer sub-agent if available.
6. Fix valid review findings.
7. Open a draft PR.
8. Link the issue in the PR body.
9. Move the issue to review if the tracker supports status updates.
10. Stop before merge.
```

## Automation Shape

You can run the two loops manually while developing the workflow.

Once the workflow is proven, put each loop on a schedule.

Example schedule:

| Automation | Cadence | Job |
|---|---:|---|
| Backlog manager | Every 12 hours | Tidy labels, classify tickets, create evidence-backed issues. |
| Issue to PR loop | Daily | Pick one safe issue and open one draft PR. |

## Codex And Claude Code

The same workflow can be implemented in either tool.

| Workflow piece | Codex | Claude Code |
|---|---|---|
| Scheduled run | Codex Automations, cron, or GitHub Actions | Schedules, hooks, cron, or GitHub Actions |
| Reusable instructions | Skills | Skills, commands, or agents |
| Backlog access | GitHub CLI, GitHub connector, Linear connector | GitHub CLI, MCP, Linear MCP |
| Isolation | Threads, branches, worktrees | `git worktree`, worktree sessions, subagents |
| Review | Reviewer sub-agent, tests, checks | `/code-review`, subagents, tests, checks |
| Output | Draft PR | Draft PR |

## Safety Rules

Good candidates for automation:

- documentation fixes
- broken links
- stale setup commands
- small tests
- lint fixes
- formatting
- repo chores
- patch dependency upgrades
- simple CI drift

Bad candidates for unattended automation:

- auth
- billing
- permissions
- security policy
- data migrations
- production deployment changes
- broad architecture changes
- vague feature requests

The human should make the final merge decision.

## Resources

- [Backlog manager prompt](./resources/backlog-manager.md)
- [Issue to PR loop prompt](./resources/issue-to-pr-loop.md)
- [Cron wiring example](./resources/cron-wiring.md)

