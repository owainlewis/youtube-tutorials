# Prompt 1: Write the Test

Use this prompt when you've decided what needs testing. The key insight: orient around **risk and behavior**, not functions.

## The Wrong Way

```
Write unit tests for the auth service. Cover:
- Password hashing and verification
- Session token generation
- Session expiry checking
```

This produces trivial tests. The agent tests that bcrypt hashes things and that `secrets` is random. You're testing the library, not your code.

## The Right Way

```
Read the spec at .ai/specs/auth.md

Before writing any tests, identify what could actually go wrong
with the auth logic in this application. Focus on:
- Behaviours where a bug would be a security vulnerability
- Edge cases where the logic could silently do the wrong thing
- Requirements from the spec that need proving

Don't test library functions (bcrypt, secrets). Test YOUR logic
and YOUR decisions. If a test would still pass with a completely
different implementation, it's probably not testing anything useful.

For each test, state which line of our code it would catch a bug in.
If the answer is "it tests that bcrypt/secrets works correctly," drop it.

Write the first test only. Do not implement anything.
Run it with: uv run pytest tests/ -x
Confirm it fails.
```

## Why This Works

- **"What could go wrong"** forces thinking about risk, not coverage
- **"Don't test library functions"** explicitly kills trivial tests
- **"If a test would still pass with a completely different implementation"** is the litmus test. If you swapped bcrypt for argon2 and the test still passes, it's testing the library choice, not your logic.

The prompt shapes the quality of the tests more than the AI does.

## The Litmus Test

Ask yourself: **"If I say 'test the password hashing function,' will I get a test that bcrypt works, or a test that proves a wrong password can never grant access?"**

The first is a library test. The second is a security test. Same topic. Completely different value.

## More Examples

### Testing behavior, not implementation

```
Write a test that proves a recruiter can never see another recruiter's candidates.
Create two recruiters with separate candidate lists.
Query the /candidates endpoint as recruiter A.
Assert that recruiter B's candidates are not in the response.

Only write the test. Do not implement anything.
Run it with: uv run pytest tests/ -x
Confirm it fails.
```

### Testing what could go wrong

```
We're adding a candidate scoring feature.
Before writing any code, what are the edge cases that could
produce a wrong score?
- Candidate with zero experience but perfect skill matches
- Job with no required skills listed
- Candidate with skills in a different case ("Python" vs "python")

Write a test for the first edge case only. Do not implement anything.
Run it with: uv run pytest tests/ -x
Confirm it fails.
```

### Testing a spec requirement

```
The spec says sessions expire after a configurable period (default 2 hours).
Write a test that:
1. Creates a session with the default expiry
2. Proves the default is 2 hours
3. Creates a session with a custom expiry of 30 minutes
4. Proves the custom expiry is respected

Don't test that datetime arithmetic works. Test that YOUR
configuration logic produces the right expiry times.
```
