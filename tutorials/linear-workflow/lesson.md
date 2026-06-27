# Linear as Your Agent's Control Plane

> Use Linear MCP to give Claude Code direct access to your project management. The agent reads tickets, updates status, creates sub-issues, and follows your workflow - without you copy-pasting descriptions.

---

## The Problem

You have a Linear board with 20 tickets. You want an AI agent to work on one.

Today, you copy the ticket description, paste it into the agent, and tell it what to do. When it's done, you go back to Linear and update the status manually.

That's fine for one ticket. It breaks down at scale:

- Context gets lost between copy-paste
- You forget to update status
- The agent doesn't know about parent issues, blocking relationships, or specs
- Nothing connects the PR back to the ticket automatically

Linear MCP fixes this. The agent reads tickets directly, updates status as it works, and follows your workflow end-to-end.

---

## What is Linear MCP?

MCP (Model Context Protocol) is a standard for connecting AI tools to external services. The Linear MCP server gives Claude Code direct API access to your Linear workspace.

The agent can:
- **Read** issues, parent issues, projects, comments
- **Update** issue status, assignee, labels
- **Create** new issues, sub-issues, comments
- **Search** across your workspace

It turns Linear from a to-do list you manage into a control plane the agent participates in.

---

## Setup

### 1. Get a Linear API Key

Go to **Linear Settings -> API -> Personal API keys** and create one.

### 2. Configure Claude Code

Add the Linear MCP server to your Claude Code settings. Open your settings file:

```bash
# Global (all projects)
~/.claude/settings.json

# Or per-project
.claude/settings.json
```

Add the MCP server configuration:

```json
{
  "mcpServers": {
    "linear": {
      "type": "npm",
      "package": "@anthropic-ai/linear-mcp-server",
      "env": {
        "LINEAR_API_KEY": "lin_api_xxxxxxxxxxxxx"
      }
    }
  }
}
```

### 3. Verify It Works

Start Claude Code and ask:

```
List my Linear teams
```

If it returns your team names, you're connected.

---

## The Workflow

Once connected, the agent can follow a full ticket lifecycle:

```
1. Read the ticket          ->  Understands what to build
2. Read parent issue        ->  Gets full context (why, constraints)
3. Read referenced spec     ->  Gets implementation details
4. Set status: In Progress  ->  Board reflects reality
5. Create branch            ->  Named after the ticket
6. Implement                ->  Guided by ticket + spec
7. Build & verify           ->  Catches errors before commit
8. Commit with ticket ID    ->  Links code to ticket
9. Push & open PR           ->  PR references the ticket
10. Set status: In Review   ->  Board updates automatically
```

The key insight: **the agent updates Linear as part of its work**, not as an afterthought. Your board always reflects what's actually happening.

---

## Where to Put What: CLAUDE.md vs /implement

CLAUDE.md is loaded into every session. Every line costs tokens whether you're implementing a ticket or just asking "where's the auth logic?" So it should contain **rules and conventions** - things the agent needs all the time.

`/implement` is loaded only when you invoke it. So it should contain the **procedural workflow** - the step-by-step sequence you only need when picking up a ticket.

```
┌─────────────────────────────────────────────────────────────────┐
│                        CLAUDE.md                                │
│                   (loaded every session)                        │
│                                                                 │
│  • Branching format                                             │
│  • Commit message format                                        │
│  • "Never force push"                                           │
│  • "Never commit code that doesn't build"                       │
│  • "Always read parent issues"                                  │
│  • Build / dev / test commands                                  │
│                                                                 │
│  Rules the agent should always know.                            │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│                  /implement PROJ-42                              │
│               (loaded only when invoked)                        │
│                                                                 │
│  1. Read the ticket and parent issue                            │
│  2. Set status to In Progress                                   │
│  3. Create branch (following CLAUDE.md convention)              │
│  4. Implement the change                                        │
│  5. Build and verify                                            │
│  6. Self-review (sub-agent reviews git diff)                    │
│  7. Fix critical issues                                         │
│  8. Push and create PR                                          │
│  9. Set status to In Review                                     │
│                                                                 │
│  Procedure you run on demand.                                   │
└─────────────────────────────────────────────────────────────────┘
```

The slash command references CLAUDE.md for conventions ("create branch following the convention in CLAUDE.md") but owns the procedure. **CLAUDE.md sets the rules. `/implement` runs the playbook.**

### Example CLAUDE.md

```markdown
# CLAUDE.md

## Project

- Runtime: Bun
- Build: `bun run build`

## Linear

- Fetch issues using the Linear MCP tool.
- Always read the parent issue (if one exists) for full context.
- If a description references a spec file, read it before implementing.
- Issue lifecycle: Backlog -> Todo -> In Progress -> In Review -> Done
  (Done happens after merge, not by you).

## Branching

Branch format: `<prefix>/<issue-id-lowercase>-<slug>`

Prefix by label:
- `feature/` - `feature` (or no label)
- `fix/` - `bug`
- `cleanup/` - `cleanup` or `tech-debt`
- `docs/` - `docs`

## Commits

- Format: `<summary> (<ISSUE-ID>)` - e.g. `Add auth middleware (PROJ-12)`
- Never amend. Never force push.
- Never commit code that doesn't build.

## Pull Requests

Create with `gh pr create`. Body must include: summary,
verification (`bun run build` result), Linear issue link.

## Error Handling

If anything fails - build, push, PR creation - stop and report.
No silent workarounds.
```

This is ~25 lines. Lean enough that it doesn't waste tokens, complete enough that the agent always knows your conventions.

---

## Common Commands

Once Linear MCP is configured, you can talk to your board naturally:

### Reading tickets

```
Show me issue PROJ-42
```

```
What are my open issues?
```

```
List issues in the "Authentication" project
```

```
Show me the parent issue for PROJ-42
```

### Working on tickets

```
Pick up PROJ-42. Read the ticket and any referenced spec,
create a branch, and implement it.
```

```
Read PROJ-42 and its parent issue, then implement it following
the workflow in CLAUDE.md.
```

### Updating status

```
Set PROJ-42 to In Progress
```

```
Mark PROJ-42 as In Review and add a comment with the PR link
```

### Creating tickets

```
Create a sub-issue under PROJ-40 titled "Add input validation"
with priority Normal and label "feature"
```

```
Read specs/auth.md and create Linear tickets for each task
under the Auth project
```

### Searching

```
Find all issues labeled "bug" with priority Urgent
```

```
Show me issues updated in the last 24 hours
```

---

## Slash Commands

Encode the full workflow into a slash command so picking up a ticket is a single action.

Create `.claude/commands/implement.md`:

```markdown
Read the Linear issue $ARGUMENTS using the Linear MCP tool.

If the issue has a parent issue, read that too for full context.
If the description references a spec file, read it.

Then follow this workflow:

## 1. Start
- Set the issue status to **In Progress**.
- Create a branch following the convention in CLAUDE.md.

## 2. Implement
- Implement the change described in the ticket.
- Run `bun run build` and confirm it passes.
- Commit with the issue ID: `<summary> (<ISSUE-ID>)`

## 3. Self-Review
Before pushing, launch a sub-agent with this task:

    Review the diff between this branch and main (`git diff main`).
    Check for: bugs, unused imports, dead code, empty catch blocks,
    security issues, over-engineering, missing error handling.
    Classify as: 🔴 Critical, 🟡 Warning, 🟢 Nit.
    If no issues, say "LGTM".

Fix all 🔴 Critical issues. Re-run build after fixes.

## 4. Ship
- Push and create a PR with `gh pr create`.
- Set the issue status to **In Review**.
- Add a comment on the Linear issue with the PR URL.

If anything fails at any step, stop and report the error.
```

Now you can run:

```
/implement PROJ-42
```

And the agent handles the entire lifecycle - including self-review before pushing.

Notice that the self-review prompt lives here, not in CLAUDE.md. It's ~100 tokens that only get loaded when you're actually implementing. If it were in CLAUDE.md, you'd pay for it every session.

---

## Spec-Driven Workflow with Linear

For larger features, combine specs with Linear tickets:

### 1. Write the spec

```
Read my spec template and generate a spec for: user authentication
with JWT tokens. Save it to specs/auth.md
```

### 2. Create tickets from the spec

```
Read specs/auth.md and create a parent Linear issue titled
"JWT Authentication" in the Auth project, team Engineering.

Then create one sub-issue per task from the spec, linked to the parent.
Each sub-issue should reference the spec: "Spec: specs/auth.md"
```

### 3. Work on tickets

```
/implement PROJ-43
```

The agent reads the ticket, finds the spec reference, reads the spec, and implements with full context.

### 4. Track progress

Your Linear board now shows:
- Parent issue with progress bar (auto-calculated from sub-issues)
- Each sub-issue moving through: Todo -> In Progress -> In Review -> Done
- Comments with PR links on each ticket

You get visibility without doing any project management manually.

---

## Tips

### Keep CLAUDE.md lean

Every line costs tokens in every session. Put stable rules here (conventions, commands, workflow). Don't put things the agent can discover by reading files.

### Use parent issues for context

A sub-issue description can be short ("Add JWT verification middleware"). The parent issue carries the why, the constraints, and the full picture. Teaching the agent to always read the parent is the single highest-value instruction.

### Spec references beat long descriptions

Instead of writing a 500-word ticket description, write a spec file and reference it: `Spec: specs/auth.md`. The agent reads the file. The ticket stays clean. The spec is version-controlled.

### Status updates are cheap signals

Having the agent set "In Progress" and "In Review" costs almost nothing but gives you real-time visibility into what's happening - especially when running multiple agents.

### Check for file overlaps before parallel work

If two tickets touch the same files, they'll produce merge conflicts. Check this at planning time, not merge time. Either sequence them (one `blockedBy` the other) or merge them into one ticket.

---

## Available Linear MCP Tools

| Tool | What it does |
|------|-------------|
| `list_teams` | List teams in workspace |
| `get_team` | Get team details |
| `list_issues` | Search/filter issues |
| `get_issue` | Get full issue details + relations |
| `create_issue` | Create new issue |
| `update_issue` | Update status, assignee, labels, etc. |
| `list_comments` | Read comments on an issue |
| `create_comment` | Add a comment to an issue |
| `list_projects` | List projects |
| `get_project` | Get project details |
| `list_cycles` | Get team cycles |
| `list_issue_statuses` | Get available statuses for a team |
| `list_issue_labels` | Get available labels |
| `list_users` | List workspace members |

---

## License

MIT
