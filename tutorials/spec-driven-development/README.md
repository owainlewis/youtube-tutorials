# Spec-Driven Development Made Simple

A simple workflow for AI-assisted development using Claude Code.

## Quick Start

### 1. Install the commands

```bash
cp -r commands/* ~/.claude/commands/
```

### 2. Create CLAUDE.md in your project

```markdown
# CLAUDE.md

## Patterns
- FastAPI for endpoints
- Pydantic for validation
- SQLAlchemy for database

## Rules
- Use uv for packages (not pip)
- Write tests first
- No print statements in production
```

### 3. Use the workflow

```bash
/spec Add user authentication    # Plan the feature
# Implement each task in a fresh chat
/review                          # Review the code
/commit                          # Commit with a good message
```

---

## The Workflow

### What Big Tech Actually Does

At Google, Amazon, and every serious engineering org, software gets built the same way:

1. Product Requirements — What are we building and why?
2. Technical Design — How will we build it?
3. Task Breakdown — What are the individual pieces?
4. Implementation — Build one piece at a time
5. Code Review — Is this good enough to ship?
6. Merge — Document and commit

This workflow adapts that process for AI agents.

### Why This Matters for AI Agents

AI agents have a fundamental constraint: context windows.

Long conversations accumulate noise. The agent loses track of what matters. Instructions from 50 messages ago get buried. Quality drifts.

The Big Tech process solves this naturally:

- Specs live in files, not chat history. The agent reads them fresh each time.
- Tasks are self-contained. Each one has everything needed to complete it.
- New chats start clean. No accumulated confusion.

### The Core Principle

One task = one chat = one commit.

Everything else—specs, commands, ceremonies—exists to support this principle.

---

## The Commands

### /spec

Creates a specification file that breaks a feature into tasks.

```
/spec Add user authentication with password reset
```

Creates `.ai/specs/user-auth.md`:

```markdown
# User Authentication

## Goal
Add email/password auth so users can create accounts and recover access.

## Tasks

### T1: Add User model with password hash
Files: `src/models/user.py`, `tests/models/test_user.py`
Do: Write test first, then create User model with email, password_hash fields
Verify: `uv run pytest tests/models/test_user.py`
Done: User can be created with hashed password, verification works

### T2: Add /register endpoint
Files: `src/routes/auth.py`, `tests/routes/test_auth.py`
Do: Write test first, then implement POST /register
Verify: `uv run pytest tests/routes/test_auth.py::test_register`
Done: Can register new user via API, returns valid token
```

### /review

Reviews code like a senior engineer would.

```
/review src/auth/middleware.py
```

Checks for:
- Simplicity: Is this over-engineered?
- Clarity: Are the names clear?
- Consistency: Does it match CLAUDE.md patterns?
- Correctness: Any bugs?

### /commit

Generates a commit message that explains WHY, not just WHAT.

```
/commit
```

Output:
```
feat(auth): add JWT authentication middleware

Users needed a way to authenticate API requests. This adds
middleware that validates JWT tokens from the Authorization
header and attaches the user to the request context.

Closes #234
```

---

## The Per-Task Loop

```
For each task:
1. Start a NEW chat (clean context)
2. "Read CLAUDE.md and .ai/specs/feature.md. Implement T1."
3. Agent implements the task
4. Run the Verify command
5. /review the changed files
6. /commit
7. Repeat for T2, T3...
```

---

## When Do You Need All This?

| Work | What You Need | Why |
|------|---------------|-----|
| Bug fix | Nothing | Just fix it |
| Small feature (1-2 files) | Mental model | You can hold it in your head |
| Medium feature (3-5 files) | One task file | Prevents scope creep |
| Large feature (5+ files) | Full spec + breakdown | Too complex to track mentally |

Rule of thumb: if you'd write a ticket for it, write a spec.

---

## Key Takeaways

1. It's the Big Tech process. PRD → Design → Tasks → Build → Review → Merge.

2. One task = one chat = one commit. This is the atomic unit.

3. The spec is the source of truth. Not chat history. Not AI memory. The file.

4. Scale ceremony to complexity. Bug fixes need nothing. Features need specs.

5. Context windows are the constraint. The process works with this limit instead of against it.
