# Commit

Generate a commit message for staged changes.

## Instructions

1. Run `git diff --staged` to see changes
2. Write a commit message that explains WHY, not just WHAT

## Format

<type>(<scope>): <subject>

<body>

### Types
- feat: New feature
- fix: Bug fix
- refactor: Code change (not fix or feature)
- test: Tests
- docs: Documentation
- chore: Maintenance

### Rules
- Subject: max 50 chars, imperative mood
- Body: explain WHY this change was needed
- Reference issues if applicable

## Example

feat(auth): add password reset flow

Users were locked out permanently if they forgot their password.
This adds a reset flow using email verification tokens.

Closes #234

## Guidelines

- Future you will search git blame at 2am
- A good commit message is a gift to yourself
- If you can't summarize it, the change might be too big
