# AI Git Workflow

> Stop memorizing git commands. Codify your conventions once, let AI agents handle the rest.

---

## What's In This Repo

Two things you can copy straight into your project:

1. **`resources/CLAUDE.md`** - A config file that defines your git conventions (branch naming, commit format, PR template, safety rules). Copy it into your project root as `CLAUDE.md`.

2. **`resources/commands/`** - Slash commands for the common git operations. Copy these into `.claude/commands/` in your project and use them as `/commit`, `/branch`, `/pr`, etc.

```
ai-git-workflow/
├── resources/
│   ├── CLAUDE.md             # Git conventions config
│   └── commands/
│       ├── commit.md         # /commit - stage and commit with a good message
│       ├── branch.md         # /branch - create a branch following conventions
│       ├── pr.md             # /pr - push and open a pull request
│       ├── squash.md         # /squash - squash commits into one
│       ├── undo.md           # /undo - safely undo a git mistake
│       ├── cleanup.md        # /cleanup - delete merged branches
│       └── history.md        # /history - explore what changed and why
└── README.md
```

---

## Setup

1. Copy `resources/CLAUDE.md` into the root of your project as `CLAUDE.md`
2. Copy the `resources/commands/` folder into `.claude/commands/` in your project
3. Adjust the conventions in `CLAUDE.md` to match your team's style
4. Open Claude Code - the config loads automatically, and commands are available as `/command-name`

---

## The Commands

### `/commit`

Reads the full diff, matches your repo's existing commit style, and writes a conventional commit with a body that explains WHY. Separates unrelated changes into multiple commits automatically.

```
/commit
```

### `/branch`

Creates a branch following your naming convention. No `git checkout -b`, no thinking about prefixes.

```
/branch password reset flow
/branch PROJ-42 dark mode toggle
```

### `/pr`

Pushes the branch and opens a pull request with a title, summary, and testing checklist - all generated from the actual diff and commit history.

```
/pr
```

### `/squash`

Combines recent commits into a single clean commit. Writes a new coherent message instead of concatenating the old ones.

```
/squash 4
/squash the three login-related commits
```

### `/undo`

Safely undoes git mistakes. Describes what it's going to do before running anything destructive.

```
/undo last commit
/undo I accidentally committed to main
/undo wrong files got committed
```

### `/cleanup`

Prunes stale remote references and deletes local branches that have been merged. Shows the list and confirms before deleting.

```
/cleanup
```

### `/history`

Explores git history and summarizes it in plain language instead of raw output.

```
/history what changed in the last 5 commits
/history who last changed the auth module and why
/history when was the payment logic introduced
```

---

## The Config

The `CLAUDE.md` covers:

- **Branch naming** - `feature/`, `fix/`, `chore/` with kebab-case
- **Commit messages** - conventional commits, body explains WHY not WHAT
- **Atomic commits** - one logical change per commit
- **Safety checks** - no secrets, no debug statements, no commented-out code
- **PR template** - What / Why / How to test
- **Hard rules** - never commit to main, never force push, squash and merge

It's ~30 lines. You're not teaching the agent how git works - you're telling it which conventions to follow.

---

## Natural Language Prompts

Beyond the slash commands, you can just talk to the agent. These work because of the conventions in `CLAUDE.md`:

```
merge feature-branch into main and resolve any conflicts
```

```
rebase this branch onto the latest main
```

```
cherry-pick just the auth fix from feature-branch and apply it here
```

```
what's the CI status on this PR? squash and merge if it's passing
```

The commands handle the common workflows. Natural language handles everything else.

---

## Adapt It

These are starting points. Change whatever doesn't fit:

- Different commit format? Edit `resources/CLAUDE.md` and `commands/commit.md`
- Trunk-based instead of feature branches? Edit `commands/branch.md`
- Different PR template? Edit `commands/pr.md`
- Need a release command? Add `commands/release.md`

The patterns are general. The specifics are yours.

---

## License

Licensed under the [MIT License](../../LICENSE).
