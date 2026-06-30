# Prompts

Copy these into Codex or Claude Code.

Use `/goal` when you need an outcome.

Use `/loop`, `/schedule`, or a Codex automation when the agent needs to check back later.

## Goal Template

```text
/goal <outcome>

Done means:
- <observable result>
- <verification passes>
- <artifact exists>

Boundaries:
- <allowed scope>
- <forbidden actions>
- <attempt or time limit>

Stop if:
- <ambiguity>
- <risky area>
- <repeated failure>
- <missing permission>

Output:
- <summary>
- <evidence>
- <links or files changed>
```

## Merge All Open PRs

Use when the repo has open PRs that need conflicts fixed, review feedback addressed, or CI shepherded.

```text
/goal Merge all open PRs that are safe to merge.

Source of truth:
- open GitHub PRs
- PR descriptions
- review comments
- CI status
- branch protection rules
- repo instructions

Done means:
- every open PR is merged, closed, updated, or blocked with evidence
- rebase conflicts are resolved where safe
- actionable human and automated review feedback is addressed
- CI is green before merge
- final report lists what happened to each PR

Boundaries:
- follow branch protection
- do not bypass required review
- do not force-push unless explicitly approved
- do not merge auth, billing, permissions, data deletion, security, or API changes
- do not close PRs without evidence

Stop if:
- merge authority is unclear
- review feedback conflicts
- CI needs unavailable secrets or services
- a PR needs product judgement
- a PR touches a risky area

Output:
- PRs merged
- PRs closed or proposed for closure
- PRs updated
- blocked PRs and why
```

## Triage All GitHub Issues

Use when the issue backlog is out of sync with reality.

```text
/goal Triage all open GitHub issues.

Source of truth:
- open GitHub issues
- current labels
- linked PRs
- current codebase
- repo instructions

Done means:
- every open issue has correct labels
- duplicate issues are closed with a comment
- already completed issues are closed with evidence
- stale states are corrected
- unclear issues are blocked with a specific question

Boundaries:
- do not merge PRs
- do not close issues without evidence
- do not make product, API, release, or security decisions
- do not create broad refactor work

Stop if:
- an issue needs product judgement
- the correct label depends on maintainer context
- closing the issue would be speculative
- a fix would touch auth, billing, permissions, or data deletion

Output:
- labels changed
- issues closed
- duplicates found
- questions for human review
```

## Deploy App To Production On GCP

Use only when the repo already deploys from `master` through Cloud Build.

```text
/goal Deploy this app to production on GCP.

Source of truth:
- repo deploy instructions
- Cloud Build status
- GCP logs
- live site URL
- smoke test path

Done means:
- the deploy change is merged to master
- Cloud Build completes successfully
- the live site is accessible
- the core flow works
- production logs show no new errors
- final report includes build link, live URL, checks, and any follow-up risk

Boundaries:
- do not change secrets
- do not change IAM
- do not change billing
- do not change DNS
- do not run destructive migrations without approval
- do not continue after a failed rollback

Stop if:
- Cloud Build fails twice for the same reason
- deploy needs manual approval
- required GCP access is missing
- the live app has errors that need rollback
- the deploy requires infrastructure decisions

Output:
- commit or PR deployed
- Cloud Build result
- live URL
- smoke checks
- logs checked
- blockers
```

## Documentation Drift Goal

Use when docs need to match the current implementation.

```text
/goal Review the codebase and update stale documentation.

Source of truth:
- current implementation
- README
- docs folder
- package scripts
- tests
- examples

Done means:
- stale documentation is updated
- docs match current implementation
- commands in docs are checked where practical
- relevant checks pass
- a docs-only PR is opened or ready

Boundaries:
- documentation-only changes
- one PR
- no application code changes
- no deploy
- no unrelated rewrites

Stop if:
- correct behavior is unclear
- verification needs missing secrets
- docs require a product decision

Output:
- stale docs found
- files changed
- checks run
- PR URL or diff summary
```

## Long Running Ticket Goal

Use when one goal spans several selected tickets.

```text
/goal Build the selected tickets end to end.

Source of truth:
- selected ticket links
- repo instructions
- existing tests
- current product behavior

Done means:
- each selected ticket is implemented
- relevant tests pass
- browser verification passes where UI changed
- each ticket is linked to the final PR or summary
- final report lists what changed and what remains

Boundaries:
- work only on selected tickets
- keep each change small
- do not start unrelated refactors
- do not change pricing, auth, billing, or data deletion

Stop if:
- a ticket needs a product decision
- acceptance criteria conflict
- a required secret or external service is missing
- the same blocker repeats 3 times
- work expands beyond the selected tickets

Output:
- tickets completed
- files changed
- tests run
- browser checks run
- blockers
- PR URL or final diff summary
```

## Factory Issue Queue Goal

Codex:

```text
/goal Work through all open issues in owainlewis/factory. Implement issues
labelled factory-ready one at a time, open PRs, run go test ./..., and merge
safe PRs when checks pass. For blocked issues, confirm the blocker is still
real and leave a short note. Close duplicate or already completed issues with
evidence. You are done when every issue is closed, merged, or clearly blocked.
Stop before risky changes, unclear product decisions, or failing tests you
cannot explain.
```

Claude Code:

```text
/goal Work through github.com/owainlewis/factory/issues. Start with
factory-ready issues. Implement one issue at a time, run go test ./..., open a
PR, address review feedback, and merge only when safe. Leave factory-blocked
issues open unless the blocker is gone. You are done when every issue is
closed, merged, or blocked with evidence.
```

## Production Error Audit Automation

Codex:

```text
Create a Codex automation that runs every Monday morning.

/goal Scan the last 7 days of production logs, CI failures, scheduled jobs, and
GitHub issues. If you find a confirmed repo-owned bug, reproduce it, fix it,
add tests, and open a draft PR. If there is no actionable bug, report what you
checked and do not open a PR.
```

## Passage Production Deploy Goal

Codex or Claude Code:

```text
/goal Deploy passage.md to production on GCP. Pushing to main should trigger
Cloud Build and deploy to Cloud Run. You are done when the live site works over
HTTPS, Cloud Build has passed, Cloud SQL is connected, secrets are not in the
repo, and there is a documented rollback path. Stop if GCP access, DNS, IAM,
billing, or secrets need human approval.
```

## Slate Phase 5 Goal

Codex or Claude Code:

```text
/goal Complete the phase:5-agents-cli issues in slate.do. Work through the
issues in order, keep each change scoped, open PRs, and run the relevant Go and
browser checks. You are done when the phase issues are merged, closed, or
blocked with evidence. Stop if auth design, token security, or product behavior
needs human judgement.
```

## Weekly Issue Triage Automation

Codex:

```text
Create a Codex automation that runs every Monday morning.

Automation prompt:
Review the GitHub issue backlog.
Ensure every ticket has correct labels.
Close duplicate issues with a comment.
Close already completed issues with evidence.
Update tickets in the wrong state.
Report anything needing human judgement.
```

Claude Code:

```text
/schedule every Monday morning, triage the GitHub issue backlog.
Fix labels, close duplicates with comments, correct stale states, and report
anything that needs maintainer judgement.
```

## Daily Documentation Drift Automation

Codex:

```text
Create a daily Codex automation that checks for documentation drift.

Automation prompt:
Compare docs against the current implementation.
If docs and code are out of sync, open a docs-only PR.
If docs contain errors, fix them in the same PR.
Stop if the correct behavior is unclear.
```

Claude Code:

```text
/schedule every day, check for documentation drift.
Open a docs-only PR for safe fixes.
Stop if the correct behavior is unclear.
```

## PR Babysitter Loop

Use when a PR is waiting on CI or review comments.

```text
/loop every 20 minutes check PR #123.

Check:
- CI status
- latest review comments
- merge conflict status

Stop when:
- CI is green
- there are no unresolved requested changes

Stop early if:
- the same failure appears twice
- a review comment needs product judgement
- 60 minutes pass

Output:
- current PR status
- blockers
- next recommended action
```

## Deploy Verification Loop

Use after a deploy starts.

```text
/loop every 5 minutes check the production deploy.

Check:
- Cloud Build status
- live site URL
- production logs
- smoke test path

Stop when:
- build is successful
- live site loads
- smoke test passes
- logs show no new errors

Stop early if:
- build fails twice for the same reason
- live app returns errors
- rollback is needed
- required GCP access is missing
```
