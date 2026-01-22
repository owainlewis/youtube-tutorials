# Tasks

Show task status for a spec file.

## Input

$ARGUMENTS should be: `path/to/spec.md`

Examples:
- `/tasks .ai/specs/auth.md`
- `/tasks .ai/specs/rate-limiting.md`

## Process

1. Read the spec file
2. List all tasks with their status
3. Show which tasks are complete, in progress, or pending

## Output Format

```
## auth.md

T1: Setup database schema     [x] complete
T2: Create auth middleware    [x] complete
T3: Add login endpoint        [ ] pending
T4: Add token refresh         [ ] pending

Progress: 2/4 tasks complete
Next: /task .ai/specs/auth.md T3
```

## Notes

- Mark tasks complete based on whether Verify step passes
- If a task file exists in .ai/tasks/, check for completion markers
- Show the next actionable task
