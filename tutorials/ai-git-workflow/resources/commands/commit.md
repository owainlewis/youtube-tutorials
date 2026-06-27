# Commit

Stage and commit changes with a well-written message.

## Instructions

1. Run `git status` and `git diff` to understand all changes
2. Run `git log --oneline -5` to match the repo's existing commit style
3. Group related changes — if there are unrelated changes, separate them into multiple commits
4. Stage files individually (no `git add .` unless every change belongs together)
5. Write the commit message

## Before committing, check for

- No `.env` files or secrets
- No `console.log` / debug statements
- No commented-out code

## Message format

```
type(scope): subject

Body explains WHY this change was needed, not what changed.
The diff shows what changed.
```

### Types

- feat: New feature
- fix: Bug fix
- refactor: Code restructure (not a fix or feature)
- chore: Maintenance, deps, config
- docs: Documentation
- test: Adding or fixing tests
- perf: Performance improvement

### Rules

- Subject line: max 72 chars, imperative mood ("add", not "added")
- Body: explain the reasoning, not the mechanics
- One logical change per commit
- Reference issue numbers if applicable

## Example

```
feat(auth): add password reset via email verification

Users were permanently locked out if they forgot their password.
This adds a reset flow using time-limited email tokens.

Closes #234
```
