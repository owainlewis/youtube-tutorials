# OpenAI Codex For Developers

A practical guide to using OpenAI Codex as a professional developer. Covers the CLI, desktop app, Linear workflow, automations, and the system layer that makes it all work well.

---

## Contents

- [Three Ways to Use Codex](#three-ways-to-use-codex)
- [CLI](#cli)
- [VS Code Extension](#vs-code-extension)
- [Desktop App](#desktop-app)
- [Live Demo: Linear Workflow](#live-demo-linear-workflow)
- [Automations](#automations)
- [Plugins](#plugins)
- [Skills](#skills)
- [Pricing](#pricing)
- [Quick Tips](#quick-tips)
- [Codex vs Claude Code](#codex-vs-claude-code)

---

## Three Ways to Use Codex

1. **The CLI** - if you like working in the terminal
2. **The desktop app** - designed for parallel work across multiple projects
3. **The VS Code extension** - if you want to stay inside your editor

---

## CLI

### Install

```bash
npm install -g @openai/codex
# or
brew install codex
```

Worth knowing: it is a Rust binary under the hood. npm is just the installer.

### Open it

```bash
codex
```

Clean, minimal TUI. Type `/` to see built-in slash commands.

### Useful slash commands

| Command | What it does |
|---|---|
| `/init` | Generate an AGENTS.md for this project - do this first in any new repo |
| `/diff` | See what changed during a task |
| `/fork` | Copy the session before trying something risky |
| `/compact` | Summarise earlier context when the session gets long |

### Non-interactive mode

```bash
codex exec "add input validation to src/api/users.py"
```

No TUI, just output. This is where Codex becomes developer tooling rather than just an app. Composes with the shell, justfiles, Git, and CI.

Pipe something in:

```bash
cat error.log | codex exec "Explain this error and suggest a fix"
```

### Sessions persist

```bash
codex resume       # opens a picker
codex resume --last
```

Sessions are saved. You can always come back to where you left off.

---

## VS Code Extension

Available from the VS Code extensions panel - search for Codex and install. Useful if you prefer to stay inside your editor. The desktop app and CLI cover everything in this guide.

---

## Desktop App

### Two modes that matter

| Mode | Use it for |
|---|---|
| Local | Small supervised tasks in your current checkout |
| Worktree | Isolated parallel work without touching your main branch |

### Local mode

Local works directly in the project directory you have open. Use it for small focused tasks: explain a module, add one test, make one small fix.

Start from a clean Git state, write the task, let Codex work, then check `/diff` before accepting anything.

### Worktree mode

Git worktrees give you multiple checkouts of the same repo on disk at the same time. Each Codex task gets its own directory and working state. Tasks do not block each other.

The practical workflow: fire two or three tasks in parallel, get on with something else, come back and review the diffs. Your main checkout stays clean throughout.

### What is actually in the app

Beyond the task input box:

- **Open in VS Code** - when working in a worktree, open it directly in VS Code. Useful for browsing changes while Codex is still running.
- **Integrated terminal** - run commands in the worktree without switching windows
- **Git diff view** - staged changes, commit from inside the app
- **Line comments on diffs** - leave a comment on a specific line rather than accepting or rejecting the whole diff. Keeps review conversational.
- **Keyboard shortcuts** - `Cmd+Enter` submit, `Cmd+K` command palette, `Escape` stop

---

## Live Demo: Linear Workflow

This is the workflow I use on real client projects. Before touching Codex, two things need to be in place: `AGENTS.md` and the Linear plugin. Together they are what make this feel like a professional workflow rather than a chat session.

### Step 1 - AGENTS.md: the project briefing

`AGENTS.md` lives in the root of the repo. Codex reads it before every task. Think of it as the briefing you would give a new engineer joining the team - what the product does, how the workflow runs, what conventions to follow.

Two principles to keep in mind when writing AGENTS.md:

**Reference, don't repeat.** Only write down what the agent cannot discover itself.

| Put this in AGENTS.md | Defer to the source |
|---|---|
| Commit conventions | Commands -> `justfile` or `Makefile` |
| Linear / Git workflow | Project layout -> agent reads the tree |
| Product context, non-obvious constraints | Dependencies -> `pyproject.toml` / `package.json` |

If your commands are already in a `justfile`, point there. The moment you copy a command into AGENTS.md you have two sources of truth and one will go stale.

**Context compression.** Every word you give an agent costs attention. Write instructions in as few words as possible, with maximum clarity and no overlapping or conflicting rules. A bloated AGENTS.md is not just wasteful - vague or contradictory instructions actively degrade output quality. Say one thing clearly rather than three things loosely.

A good AGENTS.md for most projects is short:

```md
# Project Name

One sentence on what this product does and who it is for.

See `docs/product-spec.md` for product direction, scope, phases, or workflow.

## Commands

See `justfile` for all available commands. Run `just` to list them.

## Workflow

Linear project `Project Name` is the source of truth for current work. Agents have Linear MCP access.

- Pick up tickets from Linear. Move to `In Progress` on start, `Done` when verified.
- Keep work scoped to the active ticket unless asked otherwise.
- Commit messages include the Linear ID when the work maps to a ticket (e.g. `GRA-141 Add minimal Postgres persistence`).
```

Run `/init` to generate a starting point, then trim aggressively.

See: [`01-setup/AGENTS.md`](01-setup/AGENTS.md)

### Step 2 - Linear plugin: no context switching

Install from the desktop app: Settings > Plugins > Browse > Linear > Install.

Without the plugin, working from a ticket means: open Linear, read the ticket, copy the description, paste it into Codex, do the work, go back to Linear, update the status manually. Every step is a context switch.

With the plugin, the full loop stays in one place. Codex reads the ticket, implements the work, and closes the ticket - all from a single session.

### Step 3 - Pull the ticket

```
Show me the details for [ticket ID]
```

Codex reads the title, description, and acceptance criteria directly from Linear. It already has the project context from AGENTS.md. That is everything it needs.

### Step 4 - Run the task

Fire the task. While it is running, fire a second smaller ticket in Worktree. You do not need to sit and watch - that is the point of the parallel workflow.

### Step 5 - Review the diff

When the task completes, review the diff the same way you would review a PR from a junior engineer:

- Did it meet the goal in the ticket?
- Did it stay in scope?
- Are the tests meaningful?
- Did it touch anything it should not have?

Accept what looks right. Flag anything that needs a tweak. Iterate on specific lines, not the whole diff.

### Step 6 - Close the loop in Linear

```
Mark [ticket ID] as done and add a comment summarising what was built
```

Ticket in Linear, built with Codex, diff reviewed, ticket closed. No manual status updates.

---

## Automations

The desktop app can run recurring tasks on a schedule. Useful for maintenance work that is easy to forget.

### Example: check for stale dependencies

Create a new automation with a prompt like:

```
Check this project for stale or outdated dependencies. List anything that is significantly behind with a short note on whether it is worth updating.
```

Set it to run weekly. You get a dependency health check without having to remember it.

Other useful examples:

- **Weekly summary** - `Summarise what changed in this repo this week`
- **Branch check-in** - `Check if there are any open branches older than two weeks`

---

## Plugins

### What they are

Plugins connect Codex to external tools - issue trackers, error monitoring, documentation platforms. Instead of switching between apps and copy-pasting context, you describe what you want in natural language and Codex handles the interaction.

Install from the desktop app: Settings > Plugins > Browse.

### Why use them

Without plugins, working from a Linear ticket means: open Linear, read the ticket, copy the description, paste it into Codex, do the work, go back to Linear, update the status manually. Every step is a context switch.

With the Linear plugin, the full loop stays in one place. Codex reads the ticket, implements the work, and closes the ticket - all from a single session.

### Examples

| Plugin | What it does |
|---|---|
| **Linear** | Read, create, and update tickets. Pull acceptance criteria directly into a task. Close tickets when work is done. |
| **GitHub** | Read PRs, issues, and comments without leaving the session |
| **Sentry** | Fetch error details and stack traces by ID. Feed them directly into a debugging task. |
| **Notion** | Read and write documentation from inside a Codex session |

### Best practices

- Install only what you actually use. Every plugin adds context overhead to every session.
- The Linear plugin is the most useful one for day-to-day development work. Start there.
- Plugins work best when combined with a good AGENTS.md - the plugin provides the ticket, AGENTS.md provides the standing rules.

See: [`05-plugins/README.md`](05-plugins/README.md)

---

## Skills

### What they are

A skill is a reusable workflow stored as a `SKILL.md` file. When you invoke a skill by name, Codex reads the file and follows the instructions inside it.

Type `$` in Codex to see available skills, or reference one directly:

```
Use the $plan skill to write an implementation plan for this ticket
```

Store personal skills in `~/.agents/skills/` and they are available across every project.

### Why use them

Without skills, you re-explain the same task type every session. Code review: "Review this for correctness, check the tests are meaningful, flag anything risky." Planning: "Turn this ticket into a short implementation plan with goal, scope, steps, and verification." You write that prompt from scratch every time.

A skill writes it once. The instructions live in a file, they are version-controlled, and they get better over time as you refine them.

### Examples

| Skill | What it does |
|---|---|
| `$plan` | Turns a ticket or feature request into a short implementation plan before coding |
| `$review` | Reviews a diff for correctness, test quality, scope creep, and anything risky |
| `$commit` | Writes a well-structured commit message based on the current diff |
| `$release-notes` | Summarises changes since the last tag into a readable release note |

### Best practices

- Keep each skill focused on one kind of task. A skill that tries to do everything will do nothing well.
- Write skills in plain English. They are instructions for the agent, not code.
- Refine them over time. A skill is a living document - update it when you find a better way to do the task.
- The `$plan` skill is a good first one to write. Planning is the highest-leverage thing to get right before coding.

See: [`04-skills/plan-skill/SKILL.md`](04-skills/plan-skill/SKILL.md)

---

## Pricing

Everything covered in this guide is available on the standard $20 a month ChatGPT Plus plan. Not a pro plan, not an API-only setup - full access to the desktop app, the CLI, and the full model.

Rate limits are better than most people expect. For focused supervised work, the $20 plan goes a long way. Heavy parallel worktree use will burn through it faster.

---

## Quick Tips

- **Fork** - `/fork` copies the current session into a new thread. Use it before trying something risky so you keep your progress and can explore a different direction.
- **Fast mode** - `/fast` runs tasks quicker but costs more credits. Good for low-stakes work like formatting or docstrings.
- **Mention files** - `/mention path/to/file` when you want Codex to look at a specific file rather than guessing.
- **Subagents** - ask explicitly: `Spawn one agent to check for security issues, one for test gaps, one for anything brittle. Summarise the findings.`

---

## Codex vs Claude Code

They are not competing for the same use case.

| Codex | Claude Code |
|---|---|
| Delegation | Conversation |
| Parallel tasks | Interactive debugging |
| Ticket-shaped work | Exploratory work |
| Reviewable diffs | Back-and-forth reasoning |
| Full autonomy via `danger-full-access` + `approval_policy = "never"` (configurable, nameable profile) | Full autonomy via `--dangerously-skip-permissions` (flag only, not configurable) |

If you can write a clear plan or spec, reach for Codex. If you are still figuring out the problem, reach for Claude Code.

For a full breakdown of how Codex permissions map to Claude's dangerous mode, see [`codex-permissions-guide.md`](codex-permissions-guide.md).

---

## Resources in this repo

| File | What it is |
|---|---|
| [`01-setup/AGENTS.md`](01-setup/AGENTS.md) | AGENTS.md example |
| [`config.toml.example`](config.toml.example) | Safe default config |
| [`codex-permissions-guide.md`](codex-permissions-guide.md) | Permissions reference |
| [`02-plans-and-specs/template.md`](02-plans-and-specs/template.md) | Task brief template |
| [`02-plans-and-specs/good-example.md`](02-plans-and-specs/good-example.md) | Good task brief example |
| [`04-skills/plan-skill/SKILL.md`](04-skills/plan-skill/SKILL.md) | Example skill file |
| [`05-plugins/README.md`](05-plugins/README.md) | Plugins guide |
| [`06-automation/justfile`](06-automation/justfile) | justfile targets |
| [`resources/live-demo-workflow.md`](resources/live-demo-workflow.md) | Live demo workflow |
| [`resources/plan-template.md`](resources/plan-template.md) | Short plan template |

---

If you want to go deeper on building with AI tools professionally, I run [AI Engineer](https://aiengineer.co) - a community for engineers doing serious work with these tools.
