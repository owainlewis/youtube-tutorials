# GitHub AI Workflow Prompts

Use these prompts as starting points.

Adjust names, issue numbers, repo details, and verification commands for your project.

## Create Repo

```text
Create a new public GitHub repo called [repo-name].

Initialize it with a README and a Go module.
Add a standard Go .gitignore.

Set the description to:
"[description]"

Add these topics:
- cli
- golang
- github
- [topic]
```

## Create Project Board

```text
Create a GitHub Project board linked to this repo.

I want statuses for:
- Backlog
- In Progress
- In Review
- Done
```

## Write Spec

```text
Use the spec skill.

I want to build [tool description].

Write a complete spec covering:
- requirements
- command structure
- technical approach
- dependencies
- error handling
- tests

Save it to specs/initial-spec.md.
```

## Create Issues

```text
Use the plan skill.

Take specs/initial-spec.md and break it into GitHub issues.

Each issue needs:
- a clear title
- a short description
- acceptance criteria as a checklist
- labels

Create the issues with gh issue create.
Add them to the project board.
```

## Implement Issue

```text
Use the implement skill.

Take issue #[number].

Move it to In Progress.
Create a branch.
Implement the acceptance criteria.
Run tests.
Review the diff in a fresh context.
Fix valid findings.
Open a PR with a description that includes Closes #[number].
```

## Address Review

```text
Use the address PR feedback skill.

Fetch all PR comments and review threads.

For each comment, decide whether it is:
- valid and needs a code change
- valid but needs no code change
- not valid for this PR

Apply fixes where appropriate.
Push them.
Reply to each thread with what changed or why no change was made.
```

## Merge

```text
Squash and merge this PR.

Use a clean conventional commit message.
Reference the issue.
Delete the branch after merge.
```

## Release

```text
Set up a GitHub Actions release workflow for this Go CLI.

On tags like v0.1.0, build platform binaries, generate release notes, create a GitHub release, and attach the binaries.

Walk me through the plan before writing the workflow.
```

## Commit Message

```text
Write a commit message for the staged changes.

Rules:
- Use Conventional Commits format: type(scope): summary
- Use one of these types: feat, fix, docs, test, refactor, chore, ci
- Keep the summary under 72 characters
- Use imperative mood
- Add a body when it helps explain why the change was made
- Mention important tradeoffs or follow-up work
- Reference the issue number when one exists
- Do not describe unrelated changes

Before writing the message, inspect:
- git status
- git diff --staged
- recent commit style from git log --oneline -10

If the staged changes contain multiple unrelated changes, stop and suggest splitting them into separate commits.
```
