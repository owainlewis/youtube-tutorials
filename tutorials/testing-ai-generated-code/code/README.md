# Session Policy Example

This credential-free Python example shows how tests can prove application decisions without retesting a framework or network service.

## Requirements

- Python 3.11 or newer

There are no packages to install.

## Run the tests

From the repository root:

```bash
python3 -m unittest discover \
  -s tutorials/testing-ai-generated-code/code/tests \
  -v
```

Expected result:

```text
Ran 6 tests

OK
```

The tests do not create persistent files, so there is no reset step.

## Files

- `auth_service.py` contains the session-expiry policy.
- `tests/test_auth_service.py` tests the documented behavior with fixed times.

This is a focused unit example. It does not prove database persistence, HTTP behavior, token ownership, or production clock synchronization.
