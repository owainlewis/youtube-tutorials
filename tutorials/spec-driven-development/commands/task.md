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

## After Completion

Update spec:
- Mark task `- [x]`
- Update status count

Report:
- What was implemented
- Verification result
- Blockers for next task (if any)

Suggest next: `/task path/to/spec.md TN+1`
