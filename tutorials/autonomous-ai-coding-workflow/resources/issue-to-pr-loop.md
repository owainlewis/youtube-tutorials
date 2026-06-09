# Issue To PR Loop Prompt

Use this prompt with the `codex-run-loop` skill.

Replace:

- `owner/repo` with your GitHub repository.
- `REPO_PATH` with the local repository path.
- `BASE_BRANCH` with your default branch, usually `main` or `master`.

## One Issue To Draft PR

```text
$codex-run-loop

Repository: owner/repo
Repository path: REPO_PATH
Base branch: BASE_BRANCH

Find one open GitHub issue with both labels:
- risk:low
- agent:ready

Skip issues with any of these labels:
- needs:human
- agent:blocked
- risk:medium
- risk:high

Select the oldest eligible issue unless there is a clear reason to choose another.

For the selected issue:
1. Read the issue body and comments.
2. Write a short implementation plan before editing code.
3. Create a traceable branch or worktree from BASE_BRANCH.
4. Make the smallest complete change that satisfies the issue.
5. Run the relevant tests, lint, typecheck, or build commands.
6. Run a reviewer sub-agent if available.
7. Fix valid review findings that are in scope.
8. Open a draft PR.
9. Link the issue in the PR body.
10. Include the plan, acceptance criteria, verification, and reviewer result in the PR body.
11. Move the issue to review if the tracker supports status updates.
12. Stop before merge.

If the issue is unclear, unsafe, too broad, or cannot be verified, do not code.
Comment on the issue with the blocker, add agent:blocked, and report what human input is needed.
```

## Parallel Variant

Use this only after the linear loop works.

```text
$codex-run-loop

Repository: owner/repo
Repository path: REPO_PATH
Base branch: BASE_BRANCH

Find up to three open GitHub issues with both labels:
- risk:low
- agent:ready

Skip anything with:
- needs:human
- agent:blocked
- risk:medium
- risk:high

Only run issues in parallel when they are independent, reviewable, mergeable, and revertible on their own.

Create one worktree and branch per issue.
Open one draft PR per issue.
Stop before merge.
```

