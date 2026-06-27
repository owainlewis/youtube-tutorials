# Cleanup

Clean up local branches and stale references.

## Instructions

1. Fetch and prune remote references: `git fetch --prune`
2. List all local branches: `git branch`
3. Identify branches that have been merged into main
4. Show the list and confirm before deleting anything
5. Delete confirmed branches: `git branch -d <branch>`

## Rules

- Only delete branches that have been fully merged
- Use `-d` (safe delete), never `-D` (force delete) unless explicitly asked
- Never delete `main` or `develop`
- Show the full list of branches to delete and get confirmation first
- Report how many branches were cleaned up

## Also check

- `git stash list` — remind the user if they have stashed work
- Any branches with unpushed commits — warn before suggesting deletion
