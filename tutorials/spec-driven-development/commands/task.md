# Implement Task

Implement a specific task from a feature's tasks.md file.

## Task

$ARGUMENTS

## Instructions

1. Read CLAUDE.md for project patterns
2. Read the feature's `plan.md` for context
3. Read the feature's `tasks.md` for the full task list
4. Implement the specified task
5. Mark the task as complete in tasks.md: `- [ ]` → `- [x]`

## Guidelines

- Focus on just this task — don't scope creep into other tasks
- Follow patterns established in plan.md and CLAUDE.md
- If the task is ambiguous, ask for clarification
- Run any verification commands if specified
- Keep changes minimal and focused

## Example Usage

```
/task .ai/features/note-deletion "Add deleteNote function"
```

This will:
1. Read the note-deletion plan and tasks
2. Implement the deleteNote function
3. Mark that task complete in tasks.md

## Output

After implementation:
- Show what was changed
- Show the updated tasks.md with checkbox marked
- Note any follow-up tasks that are now unblocked
