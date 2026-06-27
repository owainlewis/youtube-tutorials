# Before vs After: Testing Library Functions vs Testing Your Decisions

## Before: implementation-focused prompt

> "Cover: password hashing + verification, session token generation, session expiry checking."

This told the AI which **functions** to test, so it wrote a test for each function. Most tests just proved that well-known libraries work as documented.

## After: risk-focused prompt

> "Think about what could actually go wrong. Don't test library functions. Test YOUR logic and YOUR decisions."

This told the AI what could **go wrong**, so it wrote tests that prove spec requirements and catch real bugs.

## Comparison

| What's tested | Before (7 tests) | After (6 tests) | Why it matters |
|---|---|---|---|
| bcrypt produces a hash | Yes | No | bcrypt has been tested for 25 years. This can never fail in your code. |
| bcrypt verifies correct password | Yes | No | Same. You're testing the library, not your logic. |
| bcrypt rejects wrong password | Yes | As part of a bigger test | Before: tested in isolation. After: tested alongside empty string and trailing space. Actual edge cases. |
| secrets.token_hex returns hex | Yes | No | Testing the Python standard library. Will never fail. |
| 100 tokens are unique | Yes | No | secrets is cryptographically random by definition. |
| Session not expired before expiry | Yes | Yes | Same in both. Documents the boundary condition. |
| Session expired after expiry | Yes | Yes | Same in both. |
| Default session duration is 2 hours | **No** | Yes | Spec says "default: 2 hours". Before missed this entirely. A bug here would go unnoticed. |
| Custom duration override works | **No** | Yes | Spec says "configurable period". Before never tested it. Someone could hardcode 2 hours and break configurability. |
| Same user gets different tokens | **No** | Yes | Spec says "not derivable from user data". Before tested that any two tokens differ. After proves the same user ID still produces different tokens. The actual security requirement. |
| Empty password is rejected | **No** | Yes | An empty string matching a hash would be a critical auth bypass. Before never checked. |
| Trailing space in password fails | **No** | Yes | Silent whitespace trimming could let "password " match "password". Before never checked. |

## The takeaway

**Before:** 7 tests, mostly proving libraries work. A senior engineer would say "these are fine but they don't catch bugs."

**After:** 6 tests, all proving spec requirements or catching real risks. Every test either documents a decision (2-hour default, configurable duration) or guards against a security risk (empty passwords, token predictability).

**Fewer tests, more value. The prompt made the difference.**
