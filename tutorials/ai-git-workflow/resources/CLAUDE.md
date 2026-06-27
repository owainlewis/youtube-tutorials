# Git

## Branches

- `feature/<description>`, `fix/<description>`, `chore/<description>`, `docs/<description>`
- Lowercase kebab-case, 2-4 words
- Include ticket number if one exists: `feature/AUTH-123-password-reset`

## Commits

- Conventional commits: `type(scope): description`
- Types: feat, fix, refactor, chore, docs, test, perf
- Subject line under 72 characters, imperative mood
- Body explains WHY, not WHAT — the diff shows what changed
- One logical change per commit. Separate unrelated changes into multiple commits.
- Do NOT include Co-Authored-By lines

## Pull Requests

Title follows commit format. Body structure:

```
## What
1-2 sentences.

## Why
The problem this solves.

## How to test
Steps to verify.
```

## Rules

- Never commit directly to `main`
- Never force push to `main`
- Stage files individually — no `git add .` unless every change belongs together
- Before committing: no `.env` files, no secrets, no `console.log` / debug statements, no commented-out code
- Squash and merge when closing PRs
- Delete branch after merge
