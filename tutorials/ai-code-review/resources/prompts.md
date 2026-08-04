# AI Code Review Prompts

These prompts are templates. Replace the angle-bracketed fields with facts from your change.

## Fresh Local Review

```text
Review the current diff without editing it.

Intent:
<what the change should do>

Acceptance criteria:
<the concrete conditions for success>

Verification already run:
<commands and results>

Focus on correctness, security, regressions, missing tests, and unintended scope.
Only report actionable findings introduced by this change.
Include a file and line for each finding.
```

## Review After Fixes

```text
Review the updated diff without editing it.

Check that the previous findings are fully addressed and look for any regressions caused by the fixes.
Use the stated acceptance criteria and verification evidence.
Only report remaining actionable findings introduced by this change.
```
