# Agent Goals and Loops Explained Simply

Agent workflows get confusing because people use the same words for different things.

A prompt, a goal, a loop, a schedule, and an automation are related, but they are not the same primitive.

This page explains the model, then gives compact examples you can copy into Codex or Claude Code.

One important naming note: `loop` is mostly a Claude Code feature name here.

The more general idea is simpler: run the agent on an interval.

## The Model

| Primitive | Meaning | Use It For |
| --- | --- | --- |
| Prompt | Ask once. | One answer or one action. |
| Goal | Keep working until done. | Longer work with a finish condition. |
| Interval run | Run the agent every few minutes. | Polling CI, PR comments, logs, deploy state. |
| Fixed schedule | Run the agent at a fixed time. | Daily or weekly maintenance. |
| System | Combine the pieces. | Reliable workflows with boundaries. |

The short version:

- Prompt asks once.
- Goal defines done.
- Interval run polls by running the agent again.
- Fixed schedule starts the agent at a set time.
- System combines the pieces into useful work.

## Tool Map

| Primitive | Codex | Claude Code |
| --- | --- | --- |
| Prompt | Prompt | Prompt |
| Goal | `/goal` | `/goal` |
| Interval run | Automation | `/loop` |
| Fixed schedule | Automation | `/schedule` |
| Boundary | Sandbox and approvals | Permissions and hooks |

Codex has `/goal`.

For repeated or later work in Codex, create an automation.

Claude Code has `/goal` for outcome-driven work.

Claude Code has `/loop` for interval polling.

Claude Code has `/schedule` for fixed scheduled tasks.

In Codex, use automations for interval runs and fixed schedules.

## Why Goals Matter

A prompt says, "Do this next thing."

A goal says, "Keep working until this outcome is true."

That matters because real work is rarely one step.

The agent may need to inspect the repo, run tests, fix errors, read review comments,
rebase a branch, check a live app, and report evidence.

With a goal, the agent keeps going until the finish condition is true or a stop rule is hit.

## Good Goal Shape

| Part | Question | Example |
| --- | --- | --- |
| Outcome | What should be true? | All safe PRs are merged. |
| Evidence | How do we know? | CI, PR state, live site, labels, logs. |
| Boundary | What can it touch? | One repo, one branch, docs only, one deploy. |
| Risk | What is forbidden? | Auth, billing, secrets, IAM, data deletion. |
| Retry rule | What happens after failure? | Fix the smallest confirmed cause. |
| Stop rule | When does it ask for help? | Missing secret, unclear policy, repeated failure. |

Simple audit test:

If a reviewer cannot tell whether the goal succeeded, rewrite the goal.

## Cost Control

The common objection is fair: a vague goal can burn tokens while the agent wanders.

Good goals control cost with visible limits.

| Control | Example |
| --- | --- |
| Done condition | `Live site loads and smoke test passes.` |
| Attempt limit | `Stop after 3 failed deploy attempts.` |
| Scope limit | `Only work on open PRs in this repo.` |
| Risk limit | `Do not change secrets, IAM, billing, or data deletion.` |
| Evidence | `Report CI, logs, PRs, labels, and live URL.` |

The value is not unlimited autonomy.

The value is bounded follow-through.

## Goal Examples

These are goal shapes I use frequently.

The full copyable prompts are in [resources/prompts.md](./resources/prompts.md).

### Merge Open PRs

Use when open PRs need conflicts fixed, CI shepherded, or review feedback addressed.

- Prompt: `/goal Merge all open PRs that are safe to merge.`
- Done: every open PR is merged, closed, updated, or blocked with evidence.
- Checks: CI, branch protection, review comments, merge conflicts.
- Stop: unclear merge authority, conflicting feedback, risky code area.

This is useful because the agent shepherds work through review.

It is not just writing code.

### Triage GitHub Issues

Use when GitHub Issues has drifted away from reality.

- Prompt: `/goal Triage all open GitHub issues.`
- Done: every open issue has correct labels, is closed with evidence, or is blocked on a clear question.
- Checks: labels, linked PRs, current codebase, duplicate issues.
- Stop: product judgement, maintainer context, speculative closure.

This is useful because the backlog becomes trustworthy again.

### Deploy To Production On GCP

Use when the deploy path is known and the repo deploys from `master` through Cloud Build.

- Prompt: `/goal Deploy this app to production on GCP.`
- Done: deploy is on `master`, Cloud Build succeeds, live site works, logs show no new errors.
- Checks: Cloud Build, live URL, smoke test path, production logs.
- Stop: missing GCP access, failed build twice, secrets, IAM, billing, DNS, rollback needed.

This is useful because deployment is follow-through work.

The agent can push, wait, inspect Cloud Build, open the site, check logs, and report evidence.

### Documentation Drift

Use when docs need to match the repo.

- Prompt: `/goal Review the codebase and update stale documentation.`
- Done: docs match implementation, checked commands still work, docs-only PR is opened or ready.
- Checks: README, docs, package scripts, examples, relevant tests.
- Stop: unclear behavior, product judgement, missing secrets.

This is useful because it is low risk and easy to review.

### Long Running Ticket Build

Use when the work spans several selected tickets.

- Prompt: `/goal Build the selected tickets end to end.`
- Done: each ticket is implemented, checks pass, UI changes are verified, final report links tickets and PR.
- Checks: tests, browser verification, ticket acceptance criteria.
- Stop: conflicting acceptance criteria, expanding scope, product decision needed.

This is useful when the next action depends on what the agent just learned.

## Interval And Schedule Examples

Use an interval when the useful action is polling.

Use a fixed schedule when the useful action should start at a known time.

| Pattern | Use When | Example |
| --- | --- | --- |
| Interval run | CI finishes later. | `/loop every 5 minutes check CI for PR #123.` |
| Interval run | Review feedback arrives later. | `/loop every 20 minutes check PR #123.` |
| Interval run | Production state changes after release. | Check Cloud Build, live site, and logs. |
| Fixed schedule | Backlogs drift over time. | Run every Monday at 9am. |
| Fixed schedule | Code changes make docs stale. | Run every weekday morning. |

### Weekly Issue Triage

Codex:

```text
Create a Codex automation that runs every Monday morning.

Review the GitHub issue backlog.
Ensure every ticket has correct labels.
Close duplicate or already completed issues with a comment.
Update tickets in the wrong state.
Report anything needing human judgement.
```

Claude Code:

```text
/schedule every Monday morning, triage the GitHub issue backlog.
Fix labels, close duplicates with comments, correct stale states, and report
anything that needs maintainer judgement.
```

### Daily Documentation Drift

Codex:

```text
Create a daily Codex automation that checks for documentation drift.

If docs and code are out of sync, open a docs-only PR.
If docs contain errors, fix them in the same PR.
Stop if the correct behavior is unclear.
```

Claude Code:

```text
/schedule every day, check for documentation drift.
Open a docs-only PR for safe fixes. Stop if the correct behavior is unclear.
```

### PR Babysitter

```text
/loop every 20 minutes check PR #123.

Stop when:
- CI is green
- there are no unresolved requested changes

Stop early if:
- the same failure appears twice
- a review comment needs product judgement
- 60 minutes pass
```

## Combining Goals With Intervals And Schedules

Useful systems usually have three parts:

1. A schedule or event starts the work.
2. A goal defines the finish line.
3. An interval run repeats a check until the goal is done or blocked.

```mermaid
flowchart LR
  A["Schedule or event"] --> B["Goal"]
  B --> C["Agent work"]
  C --> D["Evidence"]
  D -->|"done"| E["PR, merge, deploy, or report"]
  D -->|"not done"| C
  D -->|"blocked"| F["Ask human"]
```

| System | Schedule Or Event | Goal | Done |
| --- | --- | --- | --- |
| Backlog cleanup | Monday morning | Triage GitHub issues | Every issue is labelled, closed, or blocked. |
| Docs maintenance | Every weekday | Fix docs drift | Docs PR exists or no safe fix is possible. |
| Deploy verifier | Deploy starts | Deploy to GCP | Live site works and logs are clean. |
| PR queue cleanup | Manual start or daily | Merge safe PRs | Every PR is merged, closed, updated, or blocked. |

## What To Avoid

| Bad Instruction | Problem |
| --- | --- |
| `/goal Improve my repo.` | No finish line. |
| `/goal Fix everything you find.` | Unsafe scope. |
| `/loop Keep trying until it works.` | No budget. |
| `Every night, make the code better.` | No proof. |
| `Merge when done.` | Removes review boundaries. |

Better:

- `/goal Fix one confirmed bug from issue #123 and open a PR with tests.`
- `/loop every 3 minutes check CI for PR #123. Stop after 30 minutes or when CI is green.`
- `Create a Codex automation that checks docs daily and opens docs-only PRs.`

## References

- Prompt pack: [resources/prompts.md](./resources/prompts.md)
- Codex goals cookbook: <https://developers.openai.com/cookbook/examples/codex/using_goals_in_codex>
- Claude Code goals: <https://code.claude.com/docs/en/goal>
- Claude Code scheduled tasks and `/loop`: <https://code.claude.com/docs/en/scheduled-tasks>

## Summary

- The one thing to remember: goals define done.
- The honest limitation: autonomy needs boundaries, evidence, and stop rules.
- What to try next: run the issue triage goal or docs drift automation on one repo.
