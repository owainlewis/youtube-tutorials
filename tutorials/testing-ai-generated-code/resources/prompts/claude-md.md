# CLAUDE.md Testing Config

Add this to your project's `CLAUDE.md` file to set the testing baseline for every agent session.

## For Python (FastAPI + pytest)

```markdown
## Testing

- Run tests with: `uv run pytest tests/ -x`
- Use red-green TDD for new features with business logic
- Write tests for: business logic, complex conditionals, data transformations, edge cases
- Do NOT write tests for: framework boilerplate, library behavior, simple CRUD
- After implementation, run the full test suite to check for regressions
- If tests fail, fix the code, not the tests (unless the test is genuinely wrong)
- Do not delete or weaken existing tests to make new code pass
```

## For TypeScript (Bun)

```markdown
## Testing

- Run tests with: `bun test`
- Use red-green TDD for new features with business logic
- Write tests for: business logic, complex conditionals, data transformations, edge cases
- Do NOT write tests for: framework routing, library behavior, simple CRUD
- After implementation, run the full test suite to check for regressions
- If tests fail, fix the code, not the tests (unless the test is genuinely wrong)
- Do not delete or weaken existing tests to make new code pass
```

## For Ruby (Rails + RSpec)

```markdown
## Testing

- Run tests with: `bundle exec rspec`
- Use red-green TDD for new features with business logic
- Write tests for: models, services, business logic, edge cases, permissions
- Do NOT write tests for: Rails framework behavior, simple validations Rails already tests
- After implementation, run the full test suite to check for regressions
- If tests fail, fix the code, not the tests (unless the test is genuinely wrong)
- Do not delete or weaken existing tests to make new code pass
```
