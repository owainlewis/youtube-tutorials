# Code Review Instructions

When reviewing changes, check the following.

## Correctness

- Does the code do what the ticket, plan, or spec asked for?
- Does it handle edge cases (empty input, null values, missing keys)?
- Are there any obvious bugs or off-by-one errors?

## Tests

- Does the change include tests?
- Do the tests actually cover the new behavior, or do they just assert the happy path?
- Do all existing tests still pass?

## Conventions

- Does the code follow the patterns already in this project?
- Are new files placed in the right directories?
- Is naming consistent with the existing codebase?

## Dependencies

- Were any new dependencies added?
- If so, are they necessary, or does the stdlib cover the use case?

## What to ignore

- Style differences that do not affect readability
- Micro-optimizations that do not matter at this scale
- Anything outside the scope of the ticket, plan, or spec

## How to use this file

Reference this from `AGENTS.md` so Codex applies it consistently:

```markdown
## Review instructions
See `code_review.md` for how to review changes before committing.
```

You can also invoke it directly with `/review` in a Codex session.
