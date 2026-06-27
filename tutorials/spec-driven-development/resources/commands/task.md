# Task

Execute a single task from a spec file.

## Input

$ARGUMENTS: `path/to/spec.md TN`

## Process

1. Read the spec file
2. Find the specified task
3. Review Why, What, Constraints, and Current State for context
4. Implement exactly what the task describes — nothing more
5. Run the Verify step

## Rules

- Only this task — ignore others in the spec
- Only files listed in the task
- No drive-by refactors or additions
- Follow constraints strictly
- Write tests if specified
- Do NOT add dependencies unless specified in Constraints

## After Completion

Report:
- What was implemented
- Files created or modified
- Verification result (pass/fail)
- Any issues or blockers

Suggest next step:
- If more tasks remain: `Read spec and implement TN+1`
- If all tasks complete: Run Validation section commands
