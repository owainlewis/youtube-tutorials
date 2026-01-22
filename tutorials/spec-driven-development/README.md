# Spec-Driven Development for AI Agents

A practical guide to writing specifications that help AI coding agents build what you actually want.

---

## What is Spec-Driven Development?

Spec-driven development (SDD) is writing a specification (plan) before writing code. The spec becomes the source of truth that guides implementation.

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
**Tests:** Write test first, then implement
**Verify:** `command to run` or manual check

### T2: [Title]
**What:** ...
**Files:** ...
**Tests:** ...
**Verify:** ...
```

---

## Template Sections Explained

### Why
The problem you're solving. Keeps you (and the agent) focused on outcomes, not just outputs. Helps make tradeoff decisions.

Bad: "We need authentication"
Good: "Users currently share one account. We need individual accounts so we can track usage per user and bill accordingly."

### What
The concrete deliverable. Should be verifiable — you know when it's done.

Bad: "Add user management"
Good: "Users can register, log in, and reset password. JWT auth with 1hr access tokens and 7d refresh tokens."

### Constraints
Boundaries that prevent the agent from going off-track. This section is the secret weapon.

- **Must:** Tech choices, patterns to follow, performance requirements
- **Must Not:** Things to avoid — don't add dependencies, don't refactor unrelated code
- **Out of Scope:** Adjacent features that are explicitly not part of this work

Without constraints, agents over-engineer, add unwanted libraries, and "improve" code you didn't ask them to touch.

### Current State
What exists now. Saves the agent from exploring your codebase (costs tokens, risks hallucination).

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
# JWT Authentication

## Why

Users currently share a single demo account. We need individual accounts to track usage per user for billing and to enable personal settings.

## What

Users can register, log in, and refresh tokens. JWT-based auth with 1hr access tokens and 7d refresh tokens. Protected routes return 401 without valid token.

- POST /auth/register — create account, return tokens
- POST /auth/login — validate credentials, return tokens
- POST /auth/refresh — exchange refresh token for new access token
- GET /auth/me — return current user (protected)

## Constraints

### Must
- Use existing Express app structure in `src/server.ts`
- Use jsonwebtoken library (already in package.json)
- Store users in existing Postgres via Prisma
- Follow error handling pattern in `src/lib/errors.ts`

### Must Not
- Add new dependencies
- Modify existing user-facing routes
- Store tokens in database (stateless JWT)

### Out of Scope
- Password reset flow
- Email verification
- OAuth / social login

## Current State

- Server: Express in `src/server.ts`
- Routes: `src/routes/index.ts` exports router, individual routes in `src/routes/*.ts`
- DB: Prisma with schema in `prisma/schema.prisma`
- Errors: Pattern in `src/lib/errors.ts` (throw AppError, caught by error middleware)
- Auth: None yet

## Tasks

### T1: Add User model
**What:** Add User model to Prisma schema with id, email, passwordHash, createdAt. Run migration.
**Files:** `prisma/schema.prisma`
**Tests:** None
**Verify:** `npx prisma migrate dev` succeeds, User table exists

### T2: Create auth utilities
**What:** Create JWT sign/verify functions. signAccessToken (1hr), signRefreshToken (7d), verifyToken.
**Files:** `src/lib/jwt.ts`, `src/lib/jwt.test.ts`
**Tests:** Test sign and verify for valid tokens, expired tokens, invalid tokens
**Verify:** `npm test` passes

### T3: Create register endpoint
**What:** POST /auth/register accepts email/password, hashes password, creates user, returns tokens.
**Files:** `src/routes/auth.ts` (create), `src/routes/index.ts` (add auth routes)
**Tests:** `src/routes/auth.test.ts` — successful registration, duplicate email, invalid input
**Verify:** `npm test` passes, `curl` returns 201 with tokens

### T4: Create login endpoint
**What:** POST /auth/login accepts email/password, validates credentials, returns tokens.
**Files:** `src/routes/auth.ts`
**Tests:** `src/routes/auth.test.ts` — successful login, wrong password, nonexistent user
**Verify:** `npm test` passes, `curl` returns 200 with tokens or 401

### T5: Create refresh endpoint
**What:** POST /auth/refresh accepts refresh token, returns new access token.
**Files:** `src/routes/auth.ts`
**Tests:** `src/routes/auth.test.ts` — valid refresh, expired refresh, invalid refresh
**Verify:** `npm test` passes

### T6: Create auth middleware
**What:** Middleware that validates access token from Authorization header, attaches user to request.
**Files:** `src/middleware/auth.ts` (create), `src/types/index.ts` (extend Request type)
**Tests:** `src/middleware/auth.test.ts` — valid token, missing token, expired token, malformed token
**Verify:** `npm test` passes

### T7: Protect test route
**What:** Add GET /auth/me that requires auth and returns current user.
**Files:** `src/routes/auth.ts`
**Tests:** `src/routes/auth.test.ts` — with valid token returns user, without token returns 401
**Verify:** Full flow works: register → login → access /me with token
```

---

## Slash Commands

### /spec — Generate a new spec

```
/spec [description]
```

Generates a spec file at `.ai/specs/<feature-slug>.md` with:
- Why, What, Constraints, Current State, Tasks
- Asks clarifying questions before generating if anything is ambiguous

Usage:
```
/spec user authentication with JWT and refresh tokens
```

### /task — Execute a single task

```
/task .ai/specs/<spec>.md T<number>
```

Executes a specific task from a spec file:
1. Reads the spec for context (Why, What, Constraints, Current State)
2. Implements exactly what the task describes
3. Runs the Verify step
4. Reports what was done and any issues

Usage:
```
/task .ai/specs/auth.md T3
```

### /tasks — Show task status

```
/tasks .ai/specs/<spec>.md
```

Shows progress on a spec:
- Lists all tasks with completion status
- Shows next actionable task

Usage:
```
/tasks .ai/specs/auth.md
```

---

## Workflow

### Starting a project

1. Describe what you want to build
2. Use `/spec` to generate initial spec
3. Review and refine — especially Constraints and Current State
4. Spec is saved to `.ai/specs/<feature>.md`

### Working through tasks

For each task:
1. Start fresh chat/session
2. Use `/task .ai/specs/<feature>.md T1` to execute
3. Agent reads spec, implements task, runs verification
4. Review the work
5. Commit with message "T1: [name]"
6. Continue with next task: `/task .ai/specs/<feature>.md T2`

### Resuming later

1. Start fresh chat
2. Use `/tasks .ai/specs/<feature>.md` to see progress
3. Continue with the next incomplete task

### Key habits

| Moment | Action |
|--------|--------|
| Start of session | Agent reads full spec |
| During task | Follow constraints strictly |
| End of task | Run verification step |
| Before commit | Verify step passes |
| After commit | Move to next task |

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
# Feature Name
## Why (problem)
## What (deliverable)
## Constraints (Must / Must Not / Out of Scope)
## Current State (what exists)
## Tasks (T1, T2, T3...)
```

### Task structure
```
### T1: Title
**What:** Action to take
**Files:** Paths to create or modify
**Tests:** Tests to write
**Verify:** How to confirm it works
```

### Commands
```
/spec [description]           — Generate new spec
/task .ai/specs/X.md T1       — Execute single task
/tasks .ai/specs/X.md         — Check progress
```

### Principles
1. Fresh context per task
2. Small tasks (30 min max, 1-3 files)
3. Explicit verification
4. Explicit file paths
5. Tests included in task
