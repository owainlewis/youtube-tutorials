# Spec-Driven Development for AI Agents

A practical guide to writing specifications that help AI coding agents build what you actually want.

---

## What is Spec-Driven Development?

Spec-driven development (SDD) is writing a specification before writing code. The spec becomes the source of truth that guides implementation.

With AI agents, this matters more than ever. Without a spec, you're "vibe coding" — describing something vaguely and hoping the agent figures it out. Sometimes it works. Often it doesn't.

A spec gives the agent:
- Clear goals (what to build)
- Boundaries (what not to build)
- Context (what already exists)
- Verification (how to know it's done)

The agent stops guessing. You stop correcting.

---

## Why We Need It

AI agents fail in predictable ways:

| Failure Mode | Cause | Spec Solution |
|--------------|-------|---------------|
| Builds wrong thing | Ambiguous requirements | Clear "What" section |
| Over-engineers | No constraints | "Must not" boundaries |
| Refactors unrelated code | No scope limits | "Out of scope" list |
| Gets lost mid-task | Task too big | Small, verifiable tasks |
| Makes inconsistent choices | No project context | "Current state" section |
| Hallucinates file paths | Doesn't know codebase | Explicit file lists |
| Can't self-verify | No success criteria | "Verify" per task |

A good spec prevents all of these.

---

## When to Use It

Use a spec when:
- Feature takes more than one session
- Multiple files or components involved
- You need to pause and resume later
- Anyone else might continue your work
- You want an audit trail of decisions

Skip the spec when:
- Quick one-off question
- Single-file change you can verify by eye
- Exploratory prototyping (write spec after you know what works)

---

## Velocity vs Control

Choosing an approach depends on what you're optimizing for:

- Velocity: Ship fast, iterate, minimal process
- Control: Audit trails, compliance, team coordination

Most solo developers and small teams should optimize for velocity. Frameworks optimize for control.

---

## Why Frameworks Feel Like Overkill (The "Ceremony Tax")

Frameworks introduce process overhead that costs time:

**File fragmentation**: Frameworks split data across multiple files (proposals, specs, tasks, designs). For AI agents, this is fatal. You constantly remind the agent to "read file X and Y." A single file is context-ready.

**Maintenance burden**: Rigorous frameworks mean more time managing process than writing code. If changing a variable requires updating three documentation files, you just won't do it. The spec goes stale.

**Tooling fatigue**: Requiring CLI installation just to write a to-do list creates friction. The best process is usually a text file.

If you're solo or a team of two, strict frameworks solve problems you don't have yet (like audit trails and compliance).

---

## When Frameworks Are Not Overkill

Frameworks exist to manage entropy as complexity scales. You need them when:

**Context exceeds memory**: If your spec.md is 50,000 words, an AI agent can't read it all. You must split it structurally and feed the AI only what it needs.

**Async collaboration**: If Developer A writes the spec and Developer B implements it next week, rigid structure ensures nothing is lost in translation.

**Standardization**: In a team of 20, you can't have 20 different styles. Frameworks enforce a common language.

**Compliance requirements**: Regulated industries need audit trails. Frameworks provide them.

---

## The AI-Specific Nuance

AI agents thrive on context density.

Frameworks dilute context by splitting information across folders. A simple spec keeps Goal, Constraints, and Current State physically close in the text. This helps the agent reason better — it doesn't have to retrieve information from distant sources.

For AI coding: A dense, well-structured single file is superior because it fits neatly into the context window and reduces hallucination.

For human teams: Frameworks become necessary once communication overhead is your biggest bottleneck.

---

## Comparison: Popular Solutions vs Simple Spec

### GitHub SpecKit

Four-phase workflow: Constitution → Specify → Plan → Tasks → Implement

Pros:
- Structured process
- Slash commands built in
- Works with multiple AI tools

Cons:
- Requires CLI installation
- Multiple files to manage
- Can be overkill for small features
- "Sledgehammer for a nail" on simple tasks

Best for: Teams wanting enforced process, enterprise environments.

### OpenSpec

Separates proposals, specs, designs, and tasks into different files with formal change workflow.

Pros:
- Audit trail for changes
- Good for multi-session planning
- Team collaboration features

Cons:
- Context fragmented across files
- Agents must load multiple documents
- Higher maintenance overhead
- Ceremony over substance for small teams

Best for: Larger teams, compliance requirements, long-running projects.

### Simple Single-File Spec (This Guide)

One markdown file with everything the agent needs.

Pros:
- Zero tooling required
- Full context in one file
- Agent reads once, executes
- You'll actually maintain it
- Works with any AI tool

Cons:
- No enforced process
- Manual updates required
- Less formal audit trail

Best for: Solo developers, small teams, shipping fast.

### When to Graduate

Start simple. Move to frameworks when you feel specific pain:

| Pain | Solution |
|------|----------|
| Team needs coordination | Add shared tooling |
| Compliance requires audit trails | Add formal process |
| Context exceeds token limits | Split strategically |
| 20 people writing specs differently | Enforce framework |

Don't add complexity before you need it. The frameworks will still be there.

---

## The Spec Template

```markdown
# Feature: [Name]
Status: [Not started | In progress | Done]

## Why
[Problem. Who has it. What happens if unsolved. 1-2 sentences.]

## What
[Concrete deliverable. Specific enough to know when it's done.]

## Constraints
- Must: [Non-negotiables — tech, patterns, performance]
- Must not: [Forbidden approaches — no new deps, don't touch X]
- Out of scope: [Adjacent things explicitly excluded]

## Current state
[What exists. Key files. Patterns to follow. Entry points.]

## Tasks

### Task 1: [Name]
What: [Action to take]
Files: [Paths to create or modify]
Tests: [Tests to write or update]
Verify: [Command or check to confirm it works]
Context: [Relevant info from previous tasks]

### Task 2: [Name]
What: [Action to take]
Files: [Paths to create or modify]
Tests: [Tests to write or update]
Verify: [Command or check to confirm it works]
Context: [Relevant info from previous tasks]

## Decisions
- [Date] [Choice]: [Rationale]

## Notes
[Open questions, links, failed attempts]
```

---

## Template Sections Explained

### Status
Quick reference for where things stand. Update as you progress.

### Why
The problem you're solving. Keeps you (and the agent) focused on outcomes, not just outputs. Helps make tradeoff decisions.

Bad: "We need authentication"
Good: "Users currently share one account. We need individual accounts so we can track usage per user and bill accordingly."

### What
The concrete deliverable. Should be verifiable — you know when it's done.

Bad: "Add user management"
Good: "Users can register, log in, and reset password. JWT auth with 1hr access tokens and 7d refresh tokens."

### Constraints
Boundaries that prevent the agent from going off-track.

- Must: Tech choices, patterns to follow, performance requirements
- Must not: Things to avoid — don't add dependencies, don't refactor unrelated code
- Out of scope: Adjacent features that are explicitly not part of this work

This section is the secret weapon. Without it, agents over-engineer, add unwanted libraries, and "improve" code you didn't ask them to touch.

### Current state
What exists now. Key files, existing patterns, entry points. Saves the agent from exploring your codebase (costs tokens, risks hallucination).

Include:
- Relevant file paths
- Patterns to follow ("see /lib/errors.ts for error handling")
- Tech already in use
- Database state

### Tasks
The implementation breakdown. Each task should be:

- Small: 30 minutes of agent work max
- Scoped: 1-3 files
- Verifiable: Clear test or check
- Independent: Can run in fresh context

Task structure:

| Field | Purpose |
|-------|---------|
| What | Action to take, no ambiguity |
| Files | Exact paths to create/modify |
| Tests | Tests to write or update |
| Verify | How to confirm it works |
| Context | Info from previous tasks needed here |

The Context field matters because each task should run in a fresh context window. Previous conversation doesn't carry over, so anything the agent needs to know must be stated explicitly.

### Decisions
Log choices as you make them. Date, what you decided, why.

Prevents re-litigating. Your future self (and teammates) will thank you.

### Notes
Everything else: open questions, links, approaches that didn't work.

---

## Task Design Principles

### Principle 1: Fresh context per task
Each task runs in a new session. Context windows get polluted with old errors, debug tangents, abandoned approaches. Fresh start = cleaner execution.

This means every task must be self-contained. Agent can't rely on "what we just discussed."

### Principle 2: Small tasks stay on track
If a task touches more than 3 files or takes more than 30 minutes, break it down.

Signs a task is too big:
- Contains "and" (that's two tasks)
- No single verification step
- Requires decisions mid-execution

### Principle 3: Verification is mandatory
Every task needs a way to confirm it worked. Otherwise the agent decides when it's "done."

Good verifications:
- `npm test` passes
- `curl` returns expected response
- File exists with specific content
- UI shows expected state

### Principle 4: Files are explicit
Don't make the agent guess where code goes. List exact paths.

Bad: "Add auth middleware"
Good: "Files: src/middleware/auth.ts (create), src/types/request.ts (extend Request type)"

### Principle 5: Tests are part of the task
Include test expectations in the task, either:
- Per-task: Tests field specifies what to test
- Project-wide: Constraint says "always write tests"

---

## Example Spec

```markdown
# Feature: JWT Authentication
Status: In progress

## Why
Users currently share a single demo account. We need individual accounts to track usage per user for billing and to enable personal settings.

## What
Users can register, log in, and refresh tokens. JWT-based auth with 1hr access tokens and 7d refresh tokens. Protected routes return 401 without valid token.

## Constraints
- Must: Use existing Express app structure
- Must: Use jsonwebtoken library (already in package.json)
- Must: Store users in existing Postgres via Prisma
- Must: Follow error handling pattern in src/lib/errors.ts
- Must not: Add new dependencies
- Must not: Modify existing user-facing routes
- Out of scope: Password reset, email verification, OAuth

## Current state
- Server: Express in src/server.ts
- Routes: src/routes/index.ts exports router, individual routes in src/routes/*.ts
- DB: Prisma with schema in prisma/schema.prisma
- Errors: Pattern in src/lib/errors.ts (throw AppError, caught by error middleware)
- Auth: None yet

## Tasks

### Task 1: Add User model
What: Add User model to Prisma schema with id, email, passwordHash, createdAt. Run migration.
Files: prisma/schema.prisma (modify)
Tests: None
Verify: npx prisma migrate dev succeeds, User table exists
Context: None

### Task 2: Create auth utilities
What: Create JWT sign/verify functions. signAccessToken (1hr), signRefreshToken (7d), verifyToken.
Files: src/lib/jwt.ts (create)
Tests: src/lib/jwt.test.ts — test sign and verify for valid tokens, expired tokens, invalid tokens
Verify: npm test passes
Context: Use jsonwebtoken library

### Task 3: Create register endpoint
What: POST /auth/register accepts email/password, hashes password, creates user, returns tokens
Files: src/routes/auth.ts (create), src/routes/index.ts (add auth routes)
Tests: src/routes/auth.test.ts — test successful registration, duplicate email, invalid input
Verify: npm test passes, curl test returns 201 with tokens
Context: Use bcrypt for password hashing (already in package.json), jwt utils from Task 2

### Task 4: Create login endpoint
What: POST /auth/login accepts email/password, validates credentials, returns tokens
Files: src/routes/auth.ts (modify)
Tests: src/routes/auth.test.ts — test successful login, wrong password, nonexistent user
Verify: npm test passes, curl test returns 200 with tokens or 401
Context: Uses same file as Task 3, jwt utils from Task 2

### Task 5: Create refresh endpoint
What: POST /auth/refresh accepts refresh token, returns new access token
Files: src/routes/auth.ts (modify)
Tests: src/routes/auth.test.ts — test valid refresh, expired refresh, invalid refresh
Verify: npm test passes, curl test works
Context: jwt utils from Task 2

### Task 6: Create auth middleware
What: Middleware that validates access token from Authorization header, attaches user to request
Files: src/middleware/auth.ts (create), src/types/index.ts (extend Request type)
Tests: src/middleware/auth.test.ts — test valid token, missing token, expired token, malformed token
Verify: npm test passes
Context: jwt utils from Task 2

### Task 7: Protect a test route
What: Add GET /auth/me that requires auth and returns current user
Files: src/routes/auth.ts (modify)
Tests: src/routes/auth.test.ts — test with valid token returns user, without token returns 401
Verify: npm test passes, full flow works: register → login → access /me with token
Context: Uses middleware from Task 6

## Decisions
- 2024-01-15 JWT over sessions: Stateless, simpler for API, no session store needed
- 2024-01-15 1hr/7d token expiry: Balance security (short access) with UX (long refresh)

## Notes
- Consider rate limiting on auth endpoints (future task)
- Password reset will be separate feature
```

---

## Slash Commands

### /spec — Generate a new spec

```
/spec [description]

Read my description and create a spec using this structure:

# Feature: [Name]
Status: Not started

## Why
[Problem, who has it, what if unsolved]

## What
[Concrete deliverable, verifiable]

## Constraints
- Must: [X]
- Must not: [Y]
- Out of scope: [Z]

## Current state
[Leave blank for me to fill, or ask]

## Tasks

### Task 1: [Name]
What: [Action]
Files: [Paths]
Tests: [Tests to write]
Verify: [How to confirm]
Context: [Prior task info if needed]

## Decisions
[Empty]

## Notes
[Empty]

Before generating, ask 2-3 clarifying questions about scope, constraints, or current state.
```

Usage:
```
/spec user authentication with JWT and refresh tokens
```

### /task — Execute a single task

```
/task [number]

Read spec.md and execute Task [number].

Follow these steps:
1. Read the task's What, Files, Tests, Verify, and Context
2. Implement the change
3. Write the tests specified
4. Run verification to confirm it works
5. Report what was done and any issues

Do not modify files outside those listed.
Do not move to other tasks.
```

Usage:
```
/task 3
```

### /status — Get current status

```
/status

Read spec.md and report:
1. Current status
2. Completed tasks (checked)
3. Next task to execute
4. Any blockers or open questions from Notes

Keep it brief.
```

### /update — Update spec after work

```
/update

Based on our session, propose updates to spec.md:
1. Check off completed tasks
2. Add any decisions we made with rationale
3. Update current state if it changed
4. Add any new notes or discovered tasks

Show the changes, don't apply them yet.
```

---

## Workflow

### Starting a project

1. Write description of what you want to build
2. Use /spec to generate initial spec
3. Review and refine — especially Constraints and Current state
4. Save to spec.md in your repo

### Working through tasks

For each task:
1. Start fresh chat/session
2. Paste spec.md (or have agent read it)
3. Use /task N to execute
4. Review the work
5. Commit with message "Task N: [name]"
6. Use /update to get spec changes
7. Apply updates to spec.md
8. Repeat with next task

### Resuming later

1. Start fresh chat
2. Use /status to orient
3. Continue with /task N

### Key habits

| Moment | Action |
|--------|--------|
| Start of session | Agent reads full spec |
| During task | Reference constraints when making decisions |
| End of task | Agent proposes spec updates |
| Before commit | Verify step passes |
| After commit | Update spec.md, check off task |

---

## Tips

### Keep the spec updated
A stale spec is worse than no spec. Update after every task.

### Be specific in Constraints
Agents are eager. They'll add libraries, refactor code, and "improve" things you didn't ask for. Explicit constraints prevent this.

### Write verification you can actually run
"Works correctly" is not a verification. "npm test passes" is.

### Use Context field to bridge tasks
Since each task runs in fresh context, anything the agent needs to know from previous work must be in the Context field.

### Don't over-engineer the spec
A spec is a tool, not a deliverable. Keep it lean enough that you'll maintain it.

### Graduate complexity only when needed
Start with single file. Add tooling when you feel the pain of not having it.

---

## Quick Reference

### Spec structure
```
Feature name + Status
Why (problem)
What (deliverable)
Constraints (must/must not/out of scope)
Current state (what exists)
Tasks (what/files/tests/verify/context)
Decisions (choice + rationale)
Notes (questions, links, failures)
```

### Task structure
```
What: Action to take
Files: Paths to create or modify
Tests: Tests to write
Verify: How to confirm it works
Context: Info from previous tasks
```

### Commands
```
/spec [description] — Generate new spec
/task [number] — Execute single task
/status — Check progress
/update — Propose spec updates
```

### Principles
1. Fresh context per task
2. Small tasks (30 min max, 1-3 files)
3. Explicit verification
4. Explicit file paths
5. Tests included in task
