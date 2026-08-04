# Testing Prompts

Adapt the paths and commands to your project. These prompts keep requirements separate from implementation and ask the agent for verification evidence.

## Prompt 1: Write One Failing Test

```text
Read the requirement at [path].

Before writing code, identify the highest-risk observable behavior in this change.
Explain the bug that a test for this behavior would catch.

Write one test for that behavior. Do not change production code.
Run it with: [focused test command]
Confirm that it fails for the expected reason.
```

The failure is evidence that the test can detect the missing behavior. If the test passes before implementation, explain why before continuing.

## Prompt 2: Make the Test Pass

```text
Run the failing test with: [focused test command]

Implement the smallest correct change that satisfies the requirement.
Do not delete or weaken the test.

Run the focused test again.
Then run the full suite with: [full suite command]
Report both results and any behavior that remains untested.
```

If the test is genuinely wrong, stop and explain the mismatch instead of silently changing it.

## Single-Prompt Version

Use this for a small change with an obvious boundary:

```text
Implement [feature or fix].

Requirements:
- [observable behavior]
- [boundary or failure behavior]

Use a red-green-refactor loop:
1. Write one focused test.
2. Run it and confirm the expected failure.
3. Implement the change.
4. Run the focused test.
5. Run the full suite.

Commands:
- Focused test: [command]
- Full suite: [command]

Do not test framework or library behavior unless our integration with it is the risk.
State what the tests prove and what they do not prove.
```

## Project Instruction Block

Add a concrete version of this block to your repository instructions:

```markdown
## Testing

- Focused test command: `[command]`
- Full suite command: `[command]`
- Write tests from requirements and risk boundaries.
- Confirm a new test fails for the expected reason before implementation.
- Do not delete or weaken tests just to make a change pass.
- Run the focused test, then the full suite and repository checks.
- Report what remains outside the tested boundary.
```
