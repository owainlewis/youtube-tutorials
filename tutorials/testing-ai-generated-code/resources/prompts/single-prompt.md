# Single-Prompt Approach

For smaller tasks where separating "what to test" from "make it pass" is overkill.

## Template

```
Implement [feature description].

Use red-green TDD. Only write tests for:
- Business logic and validation rules
- Edge cases (empty input, nulls, boundary values)
- Security boundaries (auth, permissions, data isolation)

Do NOT write tests for:
- Framework routing or boilerplate
- Database connection setup
- Library functions
- Simple CRUD with no custom logic

Run tests with: uv run pytest tests/ -x
After implementation, run the full test suite to check for regressions.
```

## When to use this

- Quick features with straightforward logic
- Bug fixes where the test is obvious
- Adding a new endpoint that has some validation but nothing complex

## When NOT to use this

- Features with complex business rules (use the two-prompt approach)
- Security-sensitive code (you should decide what to test, not the agent)
- Any time you've found yourself saying "the agent tested the wrong things"
