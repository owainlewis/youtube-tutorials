# Review

Review code as a senior engineer would.

## Target

$ARGUMENTS

If no target specified, review all changed files.

## Instructions

Look at the code and ask:

### Simplicity
- Is this over-engineered?
- Could it be shorter without losing clarity?
- Are there unnecessary abstractions?

### Clarity
- Are names descriptive?
- Is the logic easy to follow?
- Would a new teammate understand this?

### Consistency
- Does it match patterns in CLAUDE.md?
- Is it idiomatic for the language?

### Correctness
- Are edge cases handled?
- Any obvious bugs?

## Output

If changes needed:
1. List specific issues with file and line
2. Provide the fixed code

If code is good:
- Say so briefly and move on

## Guidelines

- Be constructive, not nitpicky
- Focus on what matters: bugs, clarity, maintainability
- Don't suggest changes just to suggest changes
