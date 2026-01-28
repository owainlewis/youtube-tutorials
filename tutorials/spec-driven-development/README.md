# Spec-Driven Development

> Plan your work before you write code. But rather than writing plans for humans, we're writing plans and tasks for agents.

What is spec driven development? 

> Instead of prompting first and figuring it out as you go, you start with a spec. It's a short document that defines what you're building, the constraints, and the key decisions—a contract for how your code should behave. The spec becomes the source of truth the agent uses to generate code. Less guesswork. Fewer surprises.

---

## The Problem

You tell an AI agent "add authentication." A minute later, you've got code.

But it's not what you wanted.

- Wrong approach (OAuth when you needed email/password)
- Wrong libraries (ones you've never heard of)
- Files in weird places
- Features you didn't ask for (password reset, email verification)

So you fix it. Something else breaks. An hour later you're still untangling **decisions you never made**.

That's what happens when the AI is guessing at what you wanted.

---

## What is Spec-Driven Development?

Instead of telling the AI "add authentication," you write a **spec** first—a short document that defines:

- What you're building
- The constraints
- The key decisions

So the AI doesn't have to guess.

### Before (Vague Prompt)

```
Add authentication to the app
```

### After (Spec)

```
Email and password auth using the existing user table.
JWT tokens stored in httpOnly cookies.
Login and signup pages only.
No password reset for v1.
Don't add OAuth.
Don't install new dependencies.
```

Now the AI knows exactly what to build—and what **not** to build.

---

## Why Specs Matter

When you build something yourself, you don't need to write this down. The decisions are in your head. But the AI can't read your head.

**You have to externalize your thinking.**

Specs also help with longer work. Real features take hours, sometimes days. You want to:

- Pause mid-feature to review
- Have someone code review the work mid-flow
- Commit each task independently

This is how software engineering typically works. We break features into tasks and commit each one independently.

**It's easier to review in small chunks than to rewrite everything at the end.**

---

## This Isn't a PRD

Different documents serve different audiences:

```
┌─────────────────┬─────────────────────────┬─────────────────────────────────┐
│ Document        │ Audience                │ Purpose                         │
├─────────────────┼─────────────────────────┼─────────────────────────────────┤
│ PRD             │ PMs / Stakeholders      │ Define the business value       │
│ Design Doc      │ Engineers               │ Define the architecture         │
│ AI Spec         │ Agents                  │ Define exact boundaries & tasks │
└─────────────────┴─────────────────────────┴─────────────────────────────────┘
```

The spec includes *some* why and how—just enough context for the agent to make good decisions. But it's not a debate. **It's an action plan.**

If you're writing a "PRD" for an AI agent, you're probably writing a spec. Just call it a spec.

---

## The Workflow

```
┌──────────────────────────────────────────────────────────────────────────────┐
│                                                                              │
│    ┌─────────┐     ┌─────────┐     ┌─────────┐     ┌─────────┐              │
│    │         │     │         │     │         │     │         │              │
│    │ Generate│────▶│ Review  │────▶│  Task   │────▶│ Commit  │───┐         │
│    │  Spec   │     │ & Refine│     │   N     │     │         │   │         │
│    │         │     │         │     │         │     │         │   │         │
│    └─────────┘     └─────────┘     └─────────┘     └─────────┘   │         │
│         │                               ▲                         │         │
│         │                               │                         │         │
│         │                               └─────────────────────────┘         │
│         │                                    Repeat for each task           │
│         ▼                                                                    │
│    ┌─────────────────────────────────────────────────────────────┐          │
│    │                         SPEC FILE                           │          │
│    │  • Why: Problem being solved                                │          │
│    │  • What: Concrete deliverable                               │          │
│    │  • Constraints: Must / Must Not / Out of Scope              │          │
│    │  • Current State: Existing code & patterns                  │          │
│    │  • Tasks: Small, verifiable implementation steps            │          │
│    └─────────────────────────────────────────────────────────────┘          │
│                                                                              │
└──────────────────────────────────────────────────────────────────────────────┘
```

### The 5 Steps

1. **Use AI to generate an initial spec from a template** (metaprompting)
2. **Review it. Refine it.** Make sure the decisions are yours.
3. **The spec breaks the work into small tasks.** Pick the first one.
4. **Run that task in a fresh session.** Review. Iterate. Commit.
5. **Repeat for each task until done.**

**Spec → Task → Review → Commit. Clean context every session.**

---

## The Template

```markdown
# Feature Name

## Why

[1-2 sentences: What problem this solves. Why it matters now.]

## What

[Concrete deliverable. Specific enough to verify when done.]

## Constraints

### Must
- [Required patterns, libraries, conventions]

### Must Not
- [No new dependencies unless specified]
- [Don't modify unrelated code]

### Out of Scope
- [Adjacent features we're explicitly not building]

## Current State

[What exists now. Saves agent from exploring.]

- Relevant files: `path/to/file.ts`
- Existing patterns to follow

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

## Task Design Principles

### Fresh Context Per Task

Each task runs in a new session. This avoids **context rot**—where the conversation gets so long the AI starts losing focus.

### Small Tasks Stay on Track

If it touches more than 3 files or takes more than 30 minutes, break it down further.

### Verification is Mandatory

Every task needs a way to confirm it worked:

- A command to run
- A test to pass
- Something concrete

Without this, you get slop.

---

## Example Spec

```markdown
# JWT Authentication

## Why

Users currently share a demo account. We need individual accounts for billing.

## What

Register, login, and refresh token endpoints with JWT authentication.

## Constraints

### Must
- Use existing Express structure
- Use jsonwebtoken library
- Store tokens in httpOnly cookies

### Must Not
- Don't add new dependencies
- Don't modify existing routes
- Don't add OAuth

### Out of Scope
- Password reset
- Email verification
- Social login

## Current State

- Express app in `src/server/`
- User model exists in `src/models/user.ts`
- Using existing middleware pattern in `src/middleware/`

## Tasks

### T1: Create auth middleware
**What:** JWT verification middleware
**Files:** `src/middleware/auth.ts`, `src/middleware/auth.test.ts`
**Verify:** `npm test -- auth.test.ts`

### T2: Create register endpoint
**What:** POST /api/auth/register - create user, return JWT
**Files:** `src/routes/auth.ts`, `src/routes/auth.test.ts`
**Verify:** `npm test -- auth.test.ts`

### T3: Create login endpoint
**What:** POST /api/auth/login - verify credentials, return JWT
**Files:** `src/routes/auth.ts`
**Verify:** `npm test -- auth.test.ts`

### T4: Create refresh endpoint
**What:** POST /api/auth/refresh - refresh JWT token
**Files:** `src/routes/auth.ts`
**Verify:** `npm test -- auth.test.ts`

### T5: Add auth to existing routes
**What:** Protect /api/projects/* with auth middleware
**Files:** `src/routes/projects.ts`
**Verify:** `curl` without token returns 401

### T6: Update API documentation
**What:** Add auth endpoints to OpenAPI spec
**Files:** `docs/api.yaml`
**Verify:** Manual review

### T7: Integration test
**What:** Full auth flow test
**Files:** `src/tests/auth.integration.test.ts`
**Verify:** `npm test -- auth.integration`

## Validation

- All tests pass: `npm test`
- Manual: Register → Login → Access protected route → Refresh token
```

---

## SDLC Comparison

Traditional software development has always followed this pattern:

```
┌────────────────────────────────────────────────────────────────────────────┐
│                     TRADITIONAL SDLC                                       │
├────────────────────────────────────────────────────────────────────────────┤
│                                                                            │
│   Requirements ──▶ Design ──▶ Tasks ──▶ Implement ──▶ Review ──▶ Merge    │
│       │              │          │           │            │          │      │
│       ▼              ▼          ▼           ▼            ▼          ▼      │
│      PRD        Design Doc   Tickets      Code          PR       Main     │
│                                                                            │
│   (for humans)  (for humans) (for humans) (by humans)                      │
│                                                                            │
└────────────────────────────────────────────────────────────────────────────┘

┌────────────────────────────────────────────────────────────────────────────┐
│                     SPEC-DRIVEN DEVELOPMENT                                │
├────────────────────────────────────────────────────────────────────────────┤
│                                                                            │
│   Spec (Why/What/Constraints) ──▶ Tasks ──▶ Execute ──▶ Review ──▶ Commit │
│              │                       │          │          │          │    │
│              ▼                       ▼          ▼          ▼          ▼    │
│         spec.md                   T1, T2...   Agent     Human      Git    │
│                                                                            │
│        (for agents)              (for agents) (agent)  (human)             │
│                                                                            │
└────────────────────────────────────────────────────────────────────────────┘
```

The process is the same. The audience is different.

---

## FAQs

### "Claude Code already has planning mode. Why do I need files?"

Planning mode is great for thinking through a problem. But that plan lives inside your conversation session.

Yes, you can resume sessions. But sessions get long. Context rots. And if you want to share the plan with a teammate, or reference it six months later, you're digging through conversation history.

A spec file is:

- **Separate** — not tied to one session
- **Clean** — no conversation noise
- **Versionable** — lives in your repo
- **Shareable** — hand it to any agent in any tool

**Use planning mode to think. Use spec files to execute.**

### "This sounds like waterfall."

No. Waterfall is months of planning before you write any code.

This is **five minutes**. Maybe fifteen lines. Just enough to give the AI direction.

Think of it as a **sketch, not a blueprint**.

---

## When You Need More

Tools like OpenSpec, SpecKit, and Kiro exist. They add:

- **Spec deltas** — tracking what changed when requirements evolve
- **Compliance** — traceability for regulated industries
- **Multi-tool workflows** — teams switching between Cursor, Claude Code, and Copilot

My honest take: for most use cases, they're overkill. A markdown file in your repo does the job.

That said, they do standardise things, which is good. Worth checking out for yourself.

**Start with a file. Add complexity when you hit a wall—not before.**

---

## Quick Start

### 1. Create a spec template

Save this as `.ai/templates/spec.md` in your repo:

```markdown
# Feature Name

## Why
[Problem being solved]

## What
[Concrete deliverable]

## Constraints
### Must
- 
### Must Not
- 
### Out of Scope
- 

## Current State
- Relevant files:
- Existing patterns:

## Tasks
### T1: [Title]
**What:** 
**Files:** 
**Verify:** 
```

### 2. Generate a spec

```
Read .ai/templates/spec.md and generate a spec for: [describe your feature]
Save it to .ai/specs/[feature-name].md
```

### 3. Review and refine

Open the generated spec. Make sure the decisions are yours.

### 4. Execute tasks

```
Read .ai/specs/[feature-name].md and implement T1
```

### 5. Review, iterate, commit

Check the code. Fix any issues. Commit when it's right.

### 6. Repeat

Start a fresh session for T2. Clean context every time.

---

## Summary

Spec-driven development is simpler than people make it sound.

1. Write a spec
2. Run each task with a fresh agent
3. Review and commit as you go

**One file. That's the whole system.**

---

## Resources

- [Example specs repository](#)
- [Spec template](#)
- [Video walkthrough](#)

---

## License

MIT
