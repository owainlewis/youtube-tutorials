# /commit

Prepare a git commit for the current changes.

## Process

1. Run `git status` to see what's changed
2. Run `git diff` to understand the changes
3. Analyze what changed and **why**
4. Write a commit message
5. Show the commit for approval before executing

## Commit Message Format

Use [Conventional Commits](https://www.conventionalcommits.org/):

```
type(scope): short description

- Bullet point explaining a key change
- Another key change
- Reference task file if applicable

[optional footer]
```

### Types
- `feat` — New feature
- `fix` — Bug fix
- `refactor` — Code change that neither fixes a bug nor adds a feature
- `test` — Adding or updating tests
- `docs` — Documentation only
- `chore` — Maintenance tasks, dependencies, config
- `perf` — Performance improvement

### Scope
The area of the codebase (e.g., `auth`, `api`, `ui`, `db`).

### Description
- Use imperative mood ("add" not "added")
- Don't capitalize first letter
- No period at the end
- Keep under 50 characters

## Guidelines

1. **Stage intentionally** — Only stage files related to this change. Don't commit unrelated changes.

2. **Atomic commits** — One logical change per commit. If you're tempted to use "and" in the message, consider splitting.

3. **Explain the why** — The diff shows what changed. The message should explain why.

4. **Reference context** — If this implements a task file, reference it.

## Example

```
feat(auth): add JWT token validation middleware

- Validate token signature and expiration
- Return 401 for invalid/expired tokens
- Add user context to request object
- Implements task-3 from auth feature
```

## Before Committing

Show me the proposed commit message and staged files. I'll confirm before executing `git commit`.
