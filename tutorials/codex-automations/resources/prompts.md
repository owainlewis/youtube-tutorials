# Scheduled Task Prompt Examples

These prompts are optional starting points for the supported Scheduled task
workflow described in [the lesson](../LESSON.md). They are not a documented
Codex configuration or import format.

Replace each value in angle brackets before testing a prompt in a normal Codex
chat. Schedule it only after the manual run produces a useful result.

## Bug scan

Use this as a standalone scheduled task when you want each scan to produce a
separate report.

```text
Review <repository or project> for one critical or high-impact bug introduced
since <comparison point, such as the last release tag>.

Scope:
- Inspect only <directories or components>.
- Ignore style, naming, and speculative improvements.
- Report a bug only when you can explain the failing path and its impact.
- Do not modify code.

For each confirmed bug:
1. Search the connected GitHub repository for an open issue with the same file,
   behavior, and cause.
2. If a matching issue exists, link it and do not create a duplicate.
3. Otherwise, create a GitHub issue only if the GitHub tool is available. Give
   it a clear title, evidence, reproduction steps when practical, impact, and
   the affected file or component.

Return:
- Bugs confirmed
- Existing issues found
- Issues created
- Checks performed
- Missing access or blockers

If you cannot establish a real bug, say that no confirmed bug was found. Do not
create an issue to fill the report.
```

## Bug fix

Use a dedicated worktree for this task so a run does not edit your active
checkout.

```text
In <repository or project>, find the oldest open GitHub issue with the label
<automation label> that has enough information for a focused fix.

Before editing:
1. Read the repository instructions.
2. Confirm that the issue is still open and not already covered by an open pull
   request.
3. State the intended change, acceptance criteria, and verification command.
4. Stop if the issue is ambiguous, destructive, requires unavailable secrets,
   or needs a product decision.

Then:
1. Make only the change required by that issue.
2. Run the smallest relevant tests and repository checks.
3. Review the diff for unrelated changes.
4. Commit and push a branch named <branch prefix><short issue slug>.
5. Open a pull request that links the issue. Do not merge it.

Return:
- Issue selected
- Change made
- Tests and checks run
- Pull request URL
- Anything that still needs human review

If no suitable issue exists, report that and make no changes.
```

## Make the prompt durable

A scheduled prompt should define:

- the exact job and scope
- the source of truth, such as a repository and issue label
- what the task may change
- when it must stop
- the checks that prove the result
- the output you want after each run

Keep project-specific rules in the repository's `AGENTS.md` or in a reusable
skill. Keep the schedule and run-specific job in the Scheduled task.
