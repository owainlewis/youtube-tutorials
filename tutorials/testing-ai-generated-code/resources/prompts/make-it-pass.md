# Prompt 2: Make It Pass

Use this after Prompt 1 has created a failing test. The agent's only job is to write the minimum code to make it green.

## Template

```
Run the failing tests. Implement the minimum code to make them pass.
Do not modify the tests. Do not add tests.
After all tests pass, run the full test suite to check for regressions.

Run tests with: uv run pytest tests/ -x
```

## Why "minimum code"?

This is the key constraint that makes TDD work with agents. Without it, the agent will over-engineer. It'll add error handling you didn't ask for, create abstractions you don't need, and refactor things that were fine.

"Minimum code to pass" keeps the agent focused. It writes exactly what's needed and nothing more.

## Why "do not modify the tests"?

Agents will sometimes try to delete or weaken a test to make the code pass. The test is the spec. The code conforms to the test, not the other way around.

If the agent genuinely can't make a test pass, it should tell you why, not silently change the test.

## Why "run the full test suite"?

The new code might pass the new test but break an existing one. Running the full suite after implementation catches regressions immediately.
