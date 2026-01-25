# Spec-Driven Development for AI Agents

A practical guide to writing specifications that help AI coding agents build what you actually want.

---

## The Simple Truth

Spec-driven development sounds complicated. PRDs, design docs, RFCs, Gherkin scenarios, OpenSpec, SpecKit — what should be a simple topic has been overcomplicated.

Here's the truth: **it's a plan and a checklist.** That's it.

This is the same workflow Big Tech has used for decades. Problem → Plan → Tasks → Code. No engineer at Google just opens their editor and starts coding. They write a design doc first.

AI doesn't replace this workflow. **AI accelerates the execution step.**

---

## Why Specs Matter for AI

AI agents fail in predictable ways when you skip the spec:

**Agents need clarity.** When you say "add authentication," the agent has to guess everything. Passwords or OAuth? JWT or sessions? What library? Where do files go? A spec answers these questions upfront.

**Context windows get polluted.** Long conversations accumulate noise — old errors, dead ends, abandoned approaches. The agent loses focus. Fresh context per task means cleaner execution.

**No constraints means chaos.** Without boundaries, agents over-engineer. They add libraries you didn't ask for. They "improve" code you didn't want touched.

Without a spec, you're vibe coding — describing something vaguely and hoping the agent figures it out.

---

## The Key Insight: Specs for Agents, Not Humans

Most spec frameworks were designed for humans, not agents.

- User stories? That's for stakeholder alignment.
- Phased implementation plans? That's for team coordination.
- Gherkin scenarios? That's for QA communication.

Agents don't need that scaffolding. They need something different:

| Humans Need | Agents Need |
|-------------|-------------|
| User stories | Clear deliverables |
| Phased plans | Ordered tasks |
| Context (they assume) | Explicit constraints |
| Flexibility | File paths |

You're writing for an agent, not a product manager. Skip the user stories. Add the constraints.

---

## The Template

One file. That's what you need.

```markdown
# Feature Name

## Why

[1-2 sentences: What problem this solves. Why it matters now.]

## What

[Concrete deliverable. Specific enough to verify when done.]

- Bullet list of what will be added/modified
- Each item should be observable or testable

## Constraints

### Must
- [Required patterns, libraries, conventions]
- [Use existing X from Y]

### Must Not
- [No new dependencies unless specified]
- [Don't modify unrelated code]

### Out of Scope
- [Adjacent features we're explicitly not building]
- [Future enhancements to ignore]

## Current State

[What exists now. Saves agent from exploring.]

- Relevant files: `path/to/file.ts`
- Existing patterns to follow
- Related code locations

## Tasks

### T1: [Title]
**What:** [What to build]
**Files:** `path/to/file`, `path/to/test`
**Verify:** `command to run` or manual check

### T2: [Title]
**What:** ...
**Files:** ...
**Verify:** ...

## Validation

[End-to-end verification after all tasks complete]

- `command to verify entire feature works`
- `npm test` or equivalent
- Manual check: [what to verify in UI/API]
```

---

## Template Sections Explained

### Why
The problem you're solving. Keeps you (and the agent) focused on outcomes, not just outputs.

Bad: "We need authentication"
Good: "Users currently share one account. We need individual accounts to track usage per user."

### What
The concrete deliverable. Should be verifiable — you know when it's done.

Bad: "Add user management"
Good: "Users can register, log in, and reset password. JWT auth with 1hr access tokens."

### Constraints
Boundaries that prevent the agent from going off-track. **This is your secret weapon.**

- **Must:** Tech choices, patterns to follow
- **Must Not:** Don't add dependencies, don't refactor unrelated code
- **Out of Scope:** Adjacent features explicitly not part of this work

Without constraints, agents over-engineer.

### Current State
What exists now. Saves the agent from exploring your codebase (costs tokens, risks hallucination).

Include:
- Relevant file paths
- Patterns to follow
- Tech already in use

### Tasks
The implementation breakdown. Each task should be:

- **Small:** One concern per task
- **Scoped:** 1-3 files maximum
- **Verifiable:** Clear way to confirm it works

Task structure:

| Field | Purpose |
|-------|---------|
| What | Action to take, no ambiguity |
| Files | Exact paths to create/modify |
| Verify | How to confirm it works |

### Validation
End-to-end verification that the entire feature works. Run this after all tasks complete.

---

## The Workflow

### 1. Create the spec

```bash
/spec user authentication with JWT
```

Or write it manually. The spec is saved to `.ai/specs/feature-name.md`.

### 2. Start fresh, execute task

Start a **fresh Claude session**. Clean context.

```
Read .ai/specs/auth.md and implement T1
```

The agent reads the full spec (gets context), then executes just that task.

### 3. Commit and continue

```bash
git commit -m "T1: Add User model"
```

Fresh session. Same spec. Next task.

```
Read .ai/specs/auth.md and implement T2
```

### 4. Validate

After all tasks complete, run the Validation commands to verify the entire feature works end-to-end.

---

## Task Design Principles

### Fresh context per task
Each task runs in a new session. Context windows get polluted with old errors and dead ends. Fresh start = cleaner execution.

This means every task must be self-contained. The agent can't rely on "what we just discussed."

### Small tasks stay on track
If a task touches more than 3 files, break it down.

Signs a task is too big:
- Contains "and" (that's two tasks)
- No single verification step
- Requires decisions mid-execution

### Verification is mandatory
Every task needs a way to confirm it worked. Otherwise the agent decides when it's "done."

Good verifications:
- `npm test` passes
- `curl` returns expected response
- File exists with specific content

### Files are explicit
Don't make the agent guess where code goes. List exact paths.

Bad: "Add auth middleware"
Good: "Files: `src/middleware/auth.ts` (create), `src/types/request.ts` (extend)"

---

## Common Objections

### "Claude Code has planning mode. Why do I need files?"

Planning mode is ephemeral. When your session ends, that plan disappears.

A spec file persists. It lives in your repo. You can version it, share it, review it. Six months from now, someone can read the spec and understand why the feature exists.

Planning mode is thinking out loud. A spec file is documentation.

### "This sounds like waterfall."

No. Waterfall is months of planning. This is five minutes.

The spec is 15-30 lines. The tasks are checkboxes. You're not writing a 50-page PRD.

Think of it as a sketch, not a blueprint. You can change it. You probably will. But starting with a sketch beats starting with nothing.

---

## When You Need More

Tools like OpenSpec and SpecKit solve real problems:

**Spec deltas** — tracking what changed. Important for teams, for compliance.

**Formal requirements** — Gherkin, audit trails. Healthcare, finance, government need this.

**Multi-tool workflows** — cross-tool compatibility when your team uses different AI tools.

### When to graduate

| Pain | Solution |
|------|----------|
| Team needs coordination | Add shared tooling |
| Compliance requires audit trails | Add formal process |
| Context exceeds token limits | Split strategically |
| 20 people writing specs differently | Enforce framework |

Start simple. Graduate when you feel pain.

---

## Slash Commands

Copy the files in `/commands` to your project's `.claude/commands/` folder.

### /spec — Generate a new spec

```
/spec user authentication with JWT and refresh tokens
```

Generates `.ai/specs/<feature-slug>.md` with Why, What, Constraints, Current State, Tasks, Validation.

### /task — Execute a single task

```
/task .ai/specs/auth.md T1
```

Reads the spec for context, implements exactly what the task describes, runs verification.

### /tasks — Show task status

```
/tasks .ai/specs/auth.md
```

Lists all tasks with completion status, shows next actionable task.

---

## Quick Reference

### Spec structure
```
# Feature Name
## Why (problem)
## What (deliverable)
## Constraints (Must / Must Not / Out of Scope)
## Current State (what exists)
## Tasks (T1, T2, T3...)
## Validation (end-to-end check)
```

### Task structure
```
### T1: Title
**What:** Action to take
**Files:** Paths to create or modify
**Verify:** How to confirm it works
```

### Workflow
```
1. /spec [description]                           — Generate spec
2. Fresh session: "Read spec and implement T1"   — Execute task
3. git commit -m "T1: [name]"                    — Commit
4. Repeat for T2, T3...                          — Continue
5. Run Validation commands                       — Verify feature
```

### Principles
1. Fresh context per task
2. Small tasks (1-3 files max)
3. Explicit file paths
4. Verification per task
5. Constraints prevent chaos
