# Testing Library Functions vs Testing Your Decisions

These are copyable teaching examples, not a runnable suite. Run the complete session-policy example under [`../../code/`](../../code/) instead.

## Implementation-focused prompt

> Cover password hashing and verification, session token generation, and session expiry checking.

This names functions rather than requirements. It invites one test per function, including assertions that mostly repeat library behavior.

## Risk-focused prompt

> The default session duration is 120 minutes, callers can choose a positive custom duration, and a session expires at its exact boundary. Write tests that prove these requirements.

This names observable decisions in the application.

## Comparison

| Test shape | What it tells us | Better question |
| --- | --- | --- |
| A hash differs from the plain password | The chosen hashing function transforms input. | Can invalid credentials ever grant access? |
| A generated token is a string | The token library returned its documented type. | Where is token ownership checked? |
| A mock method was called | Our code reached one internal interaction. | What externally visible outcome should occur? |
| Default expiry is 120 minutes | Our application applies its documented default. | Which wider boundary still needs an integration test? |
| Zero duration is rejected | Our application enforces a policy boundary. | How should the API expose that error? |
| A session expires at its boundary | The comparison uses the agreed inclusive boundary. | Are production clocks and stored values compatible? |

## The takeaway

A useful test has a clear requirement, a failure it can detect, and an honest boundary. Test counts and line coverage do not supply that meaning by themselves.
