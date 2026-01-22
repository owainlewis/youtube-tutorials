---
description: Generate a conventional commit message from staged changes
---

You are a developer writing a clear, conventional commit message.

## Task

Analyze the staged changes and generate an appropriate commit message following conventional commit format.

## Process

1. Run `git diff --staged` to see what's being committed
2. Understand the purpose and scope of the changes
3. Generate a commit message

## Commit Format

```
<type>(<scope>): <subject>

<body>
```

### Types
- **feat**: New feature
- **fix**: Bug fix
- **docs**: Documentation changes
- **style**: Formatting, no code change
- **refactor**: Code restructuring, no behavior change
- **test**: Adding or updating tests
- **chore**: Maintenance, dependencies, config

### Rules
- Subject line: max 50 characters, imperative mood ("add" not "added")
- Body: wrap at 72 characters, explain what and why (not how)
- Scope: optional, indicates area affected (api, auth, db)

## Output Format

Provide the commit message ready to use:

```
feat(api): add todo creation endpoint

Implement POST /todos endpoint that accepts title and optional
description. Returns 201 with the created todo including generated ID.
```

## Guidelines

- Focus on WHY the change was made, not just what
- Keep subject line concise and specific
- Use body for context that isn't obvious from the diff
- Don't describe implementation details in message
- If changes are unrelated, suggest splitting into multiple commits
