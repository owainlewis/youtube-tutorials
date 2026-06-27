# Review Standards

Project-specific review rules. Any reviewer (human, AI agent, or CI tool) should check against these.

## Must Check

- All database queries use parameterized statements (no string interpolation)
- API routes validate input with Pydantic schemas before processing
- No secrets, API keys, or credentials in code (use environment variables)
- Error responses never expose stack traces, internal paths, or database details
- New public API endpoints require authentication middleware

## Skip

- Generated files under /gen/ (auto-generated, don't review)
- Migration files (reviewed separately in migration PRs)
- Lock files (package-lock.json, uv.lock)

## Project Patterns

- We use the repository pattern for data access. Direct database queries in route handlers are a red flag.
- All async functions must handle cancellation. Check for proper cleanup in finally blocks.
- New API routes need at least one integration test. Flag if missing.
- Use structured logging (not print statements). Log context, not messages.
- Configuration values come from environment variables via pydantic-settings, not hardcoded.

## Common AI Mistakes to Watch For

- Adding unnecessary abstraction layers (wrapper classes, factory patterns for single implementations)
- Silently changing existing function behavior while "fixing" something adjacent
- Making previously required parameters optional without updating callers
- Adding dependencies that duplicate functionality already in the project
- Over-engineering error handling (catching and re-raising without adding value)
