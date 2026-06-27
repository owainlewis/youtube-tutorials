# History

Explore git history to understand what changed and why.

## What to look for

$ARGUMENTS — e.g. "what changed in the last 3 commits", "who last changed this function", "what happened to auth.ts"

## Tools

### Recent commits
```
git log --oneline -N
```

### Changes in a specific commit
```
git show <hash>
```

### Who changed a specific file or line
```
git log --follow -p <file>
git blame <file>
```

### Search commit messages
```
git log --grep="keyword"
```

### Find when a line was introduced
```
git log -S "search string" --oneline
```

## Instructions

1. Understand what the user is looking for
2. Use the appropriate git command to find it
3. Summarize the findings in plain language — don't just dump raw output
4. If looking at blame, explain the context of each change

## Rules

- Translate git output into human-readable summaries
- When showing blame, include the commit message context — not just the hash
- For large histories, summarize the key changes rather than listing everything
