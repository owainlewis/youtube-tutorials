# Task

Execute a single task from a spec file.

## Input

$ARGUMENTS should be: `path/to/spec.md TN`

Examples:
- `/task .ai/specs/auth.md T1`
- `/task .ai/specs/rate-limiting.md T3`

## Process

1. Read the spec file
2. Find the specified task (T1, T2, etc.)
3. Read the Why, What, and Constraints sections for context
4. Read the Current State section to understand existing code
5. Implement EXACTLY what the task describes—nothing more
6. Run the Verify step to confirm it worked

## Rules

- Implement only this task—ignore other tasks in the spec
- Follow constraints strictly—they exist to prevent over-engineering
- Write tests if specified in the task
- Do NOT refactor unrelated code
- Do NOT add features not in the task
- Touch only the files listed in the task

## After Completion

Report:
- What was implemented
- Verification result (pass/fail)
- Any issues or blockers for next task

Suggest: `/task path/to/spec.md TN+1` for the next task
