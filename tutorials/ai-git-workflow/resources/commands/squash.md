# Squash

Squash recent commits into a single clean commit.

## Input

$ARGUMENTS — number of commits to squash (e.g. "4") or a description of which commits

## Instructions

1. Run `git log --oneline -10` to show recent commits
2. Identify which commits to squash
3. Use `git reset --soft HEAD~N` to uncommit while keeping changes staged
4. Write a single coherent commit message that summarizes the combined work
5. Do NOT just concatenate the old messages — write a new one that captures the intent

## Rules

- Never squash commits that have already been pushed to a shared branch
- If commits are already pushed to a feature branch, warn before proceeding
- The new message should describe the overall change, not list individual steps
- Follow the same commit message format (type(scope): subject + body)

## Example

Before:
```
a1b2c3d fix typo in auth handler
d4e5f6g add error handling to login
g7h8i9j add login endpoint
```

After squash:
```
feat(auth): add login endpoint with error handling

Adds POST /api/auth/login with credential verification,
JWT token generation, and structured error responses.
```
