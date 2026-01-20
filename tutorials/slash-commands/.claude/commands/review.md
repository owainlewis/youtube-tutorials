# /review

Review the recent changes in this codebase.

## What to Analyze

1. **Code Quality**
   - Readability and clarity
   - Naming conventions
   - Function/method size
   - Code duplication

2. **Correctness**
   - Logic errors
   - Edge cases not handled
   - Off-by-one errors
   - Null/undefined handling

3. **Security**
   - Input validation
   - Authentication/authorization
   - Sensitive data exposure
   - Injection vulnerabilities

4. **Performance**
   - Unnecessary loops or queries
   - Missing indexes (if DB changes)
   - Memory leaks
   - N+1 query problems

5. **Testing**
   - Test coverage gaps
   - Missing edge case tests
   - Test quality

6. **Consistency**
   - Matches existing patterns
   - Follows project conventions
   - Consistent error handling

## Output Format

For each issue found:

```
### [{severity}] {brief description}

**Location:** `{file}:{line}`

**Problem:** {what's wrong}

**Suggestion:** {how to fix it}
```

Severity levels:
- **critical** — Must fix before merge. Security issues, data loss risks, broken functionality.
- **high** — Should fix. Bugs, performance problems, missing error handling.
- **medium** — Consider fixing. Code quality, maintainability concerns.
- **low** — Nice to have. Style, minor improvements.

## Important

**Do NOT make changes.** Only report findings. Let the developer decide what to fix.

If no issues found, say so. Don't invent problems.
