Read the Linear issue $ARGUMENTS using the Linear MCP tool.

If the issue has a parent issue, read that too for full context.
If the description references a spec file (e.g. `Spec: specs/feature.md`), read it.

Then follow this workflow:

## 1. Start

- Set the issue status to **In Progress**.
- Create a branch following the convention in CLAUDE.md.

## 2. Implement

- Implement the change described in the ticket.
- Run `bun run build` and confirm it passes.
- Commit with the issue ID: `<summary> (<ISSUE-ID>)`

## 3. Self-Review

Before pushing, launch a sub-agent with this task:

```
Review the diff between this branch and main (`git diff main`).

Check for:
- Bugs, logic errors, or edge cases
- Unused imports, dead code, or references to things that don't exist
- Empty catch blocks or swallowed errors
- Security issues (exposed secrets, unsanitized input)
- Over-engineering or unnecessary abstractions
- Missing error handling

For each issue found, classify it as:
- 🔴 Critical — must fix before pushing
- 🟡 Warning — should fix, use judgment
- 🟢 Nit — optional improvement

If no issues found, say "LGTM".
```

Fix all 🔴 Critical issues. Re-run `bun run build` after any fixes.

## 4. Ship

- Push and create a PR with `gh pr create`.
  - PR body: summary, verification section, link to Linear issue.
- Set the issue status to **In Review**.
- Add a comment on the Linear issue with the PR URL.

If anything fails at any step, stop and report the error.
