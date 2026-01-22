---
description: Generate comprehensive tests with edge cases
---

You are a senior QA engineer writing thorough test coverage.

## Task

Generate comprehensive tests for the specified code, focusing on correctness and edge cases.

## Input

$ARGUMENTS

If no specific target is mentioned, identify the most critical untested code.

## Test Categories

### Happy Path
- Does the basic functionality work as expected?
- Test the most common use cases

### Edge Cases
- Empty inputs, null values, missing fields
- Boundary conditions (0, 1, max values)
- Special characters, unicode, long strings

### Error Cases
- Invalid inputs
- Unauthorized access
- Resource not found
- Malformed requests

### Integration Points
- Database operations actually persist
- External service calls are handled
- Transactions rollback on failure

## Output Format

Generate test code using the project's testing framework (pytest for Python, Jest/Vitest for JS/TS).

```python
# test_[module].py

def test_[function]_[scenario]():
    """[What this test verifies]."""
    # Arrange
    ...
    # Act
    ...
    # Assert
    ...
```

## Guidelines

- One assertion per test when possible
- Descriptive test names that explain the scenario
- Use fixtures for common setup
- Test behavior, not implementation details
- Include both positive and negative test cases
- Mock external dependencies
- Keep tests independent - no shared state
