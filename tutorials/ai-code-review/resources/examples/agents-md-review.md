# Code Review Guidelines (for agents.md or AGENTS.md)

Add this section to your agents.md file to steer Codex and other agents during code review.

```markdown
## Code Review

When reviewing pull requests:

- Focus on correctness, security, and maintainability. Skip style nitpicks.
- Flag only actionable issues introduced by the PR. Don't comment on pre-existing code.
- Prioritize severe issues. A review with 2 real findings beats one with 15 nitpicks.
- Check that new code follows existing patterns in the codebase.
- Verify error handling is correct, not just present.
- Look for unintended side effects in changed functions.
- If the PR modifies a public API, check that callers are updated.
- Cite specific file and line numbers for every finding.
```
