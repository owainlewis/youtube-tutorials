---
description: Take a GitHub issue end to end - worktree, implement, test, PR - running in its own Herdr tab.
argument-hint: <github issue number or URL>
---

Issue: $ARGUMENTS

Do this yourself, you already know how - worktrees, testing, and PRs aren't new to you. Steps are here only to pin down the Herdr wiring, not to teach you the engineering. This works in any repo's current workspace:

1. `gh issue view $ARGUMENTS` to pull the issue.
2. Create a worktree + branch for it, always based off the repo's main branch (`main` or `master`, whichever exists) - never off whatever branch happens to be checked out. Fetch/update main first so the base is fresh, e.g. `git fetch origin main` then `git worktree add <path> -b <branch-name> origin/main`.
3. Find your current workspace: `herdr pane current` -> workspace_id.
4. Create a new tab for this ticket, labeled with the issue number: `herdr tab create --workspace <workspace_id> --cwd <worktree_path> --label "#<issue-number>" --no-focus`
5. Start an agent in that tab: `herdr agent start "#<issue-number>" --tab <new_tab_id> --cwd <worktree_path> -- claude`
6. Hand it the task with `herdr agent send "#<issue-number>" "<full task, including implement, self-review, run tests, then gh pr create>"`
7. Tell me the tab label and branch name. Don't babysit it here - I'll check the tab bar myself; `herdr tab list --workspace <workspace_id>` shows live status per ticket.
