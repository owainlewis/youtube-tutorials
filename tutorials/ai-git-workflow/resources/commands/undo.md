# Undo

Undo a recent git mistake safely.

## What happened?

$ARGUMENTS — describe the mistake (e.g. "committed to main by accident", "undo last commit", "wrong files got committed")

## Common scenarios

### Undo last commit, keep the changes
```
git reset --soft HEAD~1
```
Changes go back to staging. Nothing lost.

### Undo last commit, unstage the changes
```
git reset HEAD~1
```
Changes stay in working directory but are unstaged.

### Accidentally committed to main
1. Create a new branch from current state
2. Switch back to main
3. Reset main to before the commit
4. Push the changes on the new branch instead

### Wrong files got committed
1. `git reset --soft HEAD~1` to undo the commit
2. Unstage the wrong files
3. Re-commit with only the correct files

### Need to recover something lost
1. Check `git reflog` to find the state you want
2. Explain each reflog entry in plain language
3. Ask before taking any action

## Rules

- Always explain what will happen before running destructive commands
- Prefer `--soft` over `--hard` to preserve work
- Never run `git reset --hard` without explicit confirmation
- If changes have been pushed, use `git revert` instead of `git reset`
- Check `git stash list` — the user might have stashed work they forgot about
