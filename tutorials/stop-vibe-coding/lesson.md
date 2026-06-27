# Stop Vibe Coding - How to Build Software With AI Like a Senior Engineer

> The tools are free. The judgement isn't.

Most people using AI coding agents are only using them for one thing: generating code. That's like buying a Swiss Army knife and only using the bottle opener.

This tutorial walks through the full software development lifecycle and shows where AI fits at every stage - not just the build step.

---

## The 7 Stages

Every piece of software ever built went through some version of this lifecycle. AI doesn't replace it. It accelerates every step.

### 1. Requirements - What are we building?

Before you write a single line of code, get clear on what you're building, why, and what's out of scope.

Produce a short requirements doc (PRD):

```
What: User authentication system
Why: Users need accounts to save preferences
Who: End users of the web app
In scope: Email/password login, signup page
Out of scope: OAuth, password reset (v1), admin roles
```

AI can help you draft this, challenge your assumptions, and even prototype quickly to test ideas before committing.

**Key insight:** Prototyping is now fast enough to be a planning tool. Build throwaway versions to learn, not to ship.

### 2. Technical Design - How are we building it?

Requirements are what and why. Technical design is how.

Decide upfront:
- Database choice and data model
- Architecture (monolith, microservices, serverless)
- Auth strategy
- Key constraints and tradeoffs

These decisions are hard to undo. Don't let an agent make them unchecked. Use AI to think through tradeoffs, but own the decisions yourself.

### 3. Task Breakdown - Plan the work

Break the project into small, clear, bounded tasks. This is project management - and it maps directly onto how you should work with coding agents.

**Don't:** Hand an agent your entire application and say "build this."

**Do:** Give it one specific task with all the context it needs.

```
Task: Create the login API endpoint
Context: We're using FastAPI with SQLAlchemy async.
Auth is JWT tokens in httpOnly cookies.
User model is already defined in app/models/user.py.
Follow the existing pattern in app/routers/health.py.
```

The difference in output quality is dramatic.

**Example prompt for breaking down a spec:**

```
Read the spec in .ai/specs/auth.md.

Break it down into independent work items that can be completed
one at a time. Each work item should have a clear title, a short
description of what needs to be done, and any dependencies on
other work items.

Once you have the list, push each work item to Linear as a new task.
```

### 4. Build - Write the code

Brief the agent properly. Give it:
- Background on what you're building
- Your technical design decisions
- The specific task
- Constraints and preferences

An LLM makes hundreds of small decisions as it writes code. Context makes those decisions well-informed. Without it, the agent guesses.

### 5. Review - The most important step

This is the step most people skip. Don't.

**Self-review:** Ask the agent to review its own code. Generation and review are different cognitive tasks. Almost every time, the agent finds issues it missed on the first pass.

```
Look at the code you just wrote. Find any bugs, edge cases,
security issues, or potential problems.
```

Common things caught on review:
- Edge cases and error handling
- Security vulnerabilities
- Missing input validation
- Performance issues

**Human review:** You don't need to read every line, but understand what was built. Does it match your design? Are there obvious issues?

**Automated review:** Layer in CI/CD checks, static analysis, and AI-powered PR review tools.

### 6. Deploy - Ship it

Get your code to production. AI can help you set up deployment pipelines, CI/CD, and infrastructure if you're not familiar with them.

**Example prompt:**

```
Commit and save these changes with a clear commit message.
Then push the latest version to GCP Cloud Run.
```

### 7. Monitor - Know when things break

Set up monitoring before your users tell you something is broken.

Minimum monitoring stack:
- **Error tracking** (e.g. Sentry) - real-time errors with stack traces
- **Uptime monitoring** - know when your app goes down
- **Alerts** - get notified immediately
- **Logs** - understand what happened and why

---

## The Presentation

The `presentation.html` file is the slide deck used in the video. Open it in any browser - it's a self-contained HTML file with keyboard navigation.

**Controls:**
- Arrow keys or click to navigate between slides
- Works in any modern browser
- No dependencies or build step required

---

## Key Takeaways

1. **AI accelerates the entire lifecycle, not just coding.** Use it for planning, design, task breakdown, review, deployment, and monitoring.

2. **Never accept the first output.** Ask the agent to self-review. Nine times out of ten, it finds real issues.

3. **Small tasks beat big prompts.** One task per session with clear context produces dramatically better code than "build me an app."

4. **The framework doesn't matter.** Claude Code, Cursor, Codex - they all send text to a language model. The quality of your thinking before the prompt is what matters.

5. **Vibe coding isn't the enemy. Skipping the thinking is.** A senior engineer who has done the design work can move fast within that structure. Skipping it produces a mess, no matter how good the tools are.

---

## Watch the Video

📺 [Watch on YouTube](https://youtube.com/@owainlewis)
