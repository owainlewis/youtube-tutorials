# Branch

Create a new branch for a feature, fix, or chore.

## What are we working on?

$ARGUMENTS

## Instructions

1. Pull the latest main: `git pull origin main`
2. Create and switch to a new branch following the naming convention
3. Confirm the branch was created

## Naming convention

```
<type>/<short-description>
```

### Types

- `feature/` — new functionality
- `fix/` — bug fix
- `chore/` — maintenance, config, deps
- `docs/` — documentation

### Rules

- Lowercase kebab-case
- 2-4 words max
- Include ticket number if one exists: `feature/AUTH-123-password-reset`

## Examples

```
feature/contact-form
fix/session-timeout
chore/update-dependencies
docs/api-reference
feature/PROJ-42-dark-mode
```
