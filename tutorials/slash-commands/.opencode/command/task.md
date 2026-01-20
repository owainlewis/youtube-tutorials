# /task

Execute the task defined in: $ARGUMENTS

## Rules

1. **Read only the task file.** It contains all the context you need.

2. **Implement exactly what's specified.** Nothing more, nothing less.

3. **Follow existing patterns.** Match the code style and patterns already in the codebase.

4. **Write tests if specified.** Check the acceptance criteria.

5. **Don't refactor unrelated code.** Stay focused on this task only.

6. **Don't add features.** If you think something is missing, note it as a blocker—don't implement it.

## Process

1. Read the task file completely
2. Review the files listed in the frontmatter
3. Implement the requirements
4. Verify each acceptance criterion
5. Mark criteria as complete in the task file

## When Done

Update the task file:
- Mark acceptance criteria as `[x]`
- Add any notes about blockers or issues for subsequent tasks
- Note any deviations from the plan (and why)

## Important

This command is designed to run in a **clean context**. If you're in the middle of a long conversation, consider:
- Running `/clear` first
- Or spawning a sub-agent to execute this task

The task file should be the only context needed.
