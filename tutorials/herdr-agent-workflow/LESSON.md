# Herdr: The Agent Multiplexer AI Developers Need

Free resource included: my `/ticket` slash command for orchestrating GitHub issue work inside Herdr.

This is a simple recording guide for the video.

The goal is not to explain every Herdr feature. The goal is to help people understand Herdr in plain English, then see enough of the workflow to try it themselves.

The video should feel like this:

1. Why normal terminals get messy with many agents.
2. What Herdr is.
3. How to install and open it.
4. How workspaces, tabs, and panes fit together.
5. How to run coding agents inside it.
6. How to customize it with AI.
7. How agents can control Herdr itself with a real `/ticket` slash command.

## Title Options

Recommended title: Herdr: The Agent Multiplexer AI Developers Need

Giveaway line: My Herdr `/ticket` slash command is linked for free below.

1. Herdr: The Agent Multiplexer AI Developers Need
2. Herdr Complete Guide for AI Coding Agents
3. How to Run Multiple Coding Agents Without Losing Control
4. My Herdr Workflow for Claude Code, Codex, Tests, and Logs
5. Stop Losing Track of Your AI Coding Agents
6. Herdr vs tmux for AI Developers
7. The Terminal Runtime for AI Coding Agents
8. Herdr: My Setup for Running Multiple Coding Agents

## Opening Script

This is a complete guide to Herdr for AI developers.

The reason this matters is that normal terminals were not really designed for the way many of us work now. We are running multiple coding agents, servers, test runners, logs, and project sessions that can last for hours.

I have tried tmux and cmux, and both are interesting, but Herdr is the one that has felt best to me for this kind of work. It is mouse-first, it is easy to look around, and it helps me stay organised when I have multiple agents running at the same time.

In this video, I will show you what Herdr is, how to install it, how the UI works, how to create workspaces, tabs, and panes, and how to run coding agents inside it.

Then at the end, I will show you the really interesting part: using an AI agent to control Herdr itself with a `/ticket` slash command that creates a worktree, opens a tab, starts an agent, and hands it a GitHub issue.

The slash command is linked for free in the description below.

So, let's get into it.

## What Herdr Is

Herdr is a terminal workspace manager.

The simple version is:

```text
Herdr keeps your terminal work visible, persistent, and organised.
```

If you know tmux, the basic idea will feel familiar. A Herdr server keeps processes running in the background, and the Herdr client shows the UI.

The important difference is that Herdr is designed around coding agents.

It gives you:

- workspaces for projects or tasks
- tabs for different modes of work
- panes for real terminal processes
- a sidebar that shows agent state
- mouse-first controls
- integrations for agents like Claude Code and Codex
- a CLI that agents can use to control the workspace

Do not overcomplicate this section.

The viewer only needs one mental model:

```text
Workspace = project or task
Tab = layout inside that project
Pane = terminal inside that layout
Agent = coding agent running in a pane
```

## Why AI Developers Should Care

Running one agent is easy.

Running several agents is where the workflow starts to break.

You end up with:

- one agent editing files
- one agent waiting for permission
- one server running somewhere
- one test runner failing somewhere else
- one log pane you forgot about
- one completed agent that still needs review

That is the real problem Herdr solves.

It gives you one place to see what is running, what is blocked, what is done, and what still needs your attention.

The lesson is not "run as many agents as possible."

The lesson is:

```text
Give each agent a clear job.
Keep the work visible.
Make review easier.
```

## Install Herdr

Keep this part short.

Show the main install path:

```bash
curl -fsSL https://herdr.dev/install.sh | sh
herdr --version
```

Then open Herdr from a real project:

```bash
cd ~/Code/my-project
herdr
```

Mention that there are other install paths:

```bash
brew install herdr
mise use -g herdr
nix run github:ogulcancelik/herdr
```

For the video, do not spend too long here. The install is not the interesting part. The interesting part is seeing how the workspace fits together.

## Open Herdr And Explain The UI

Start Herdr from a project folder:

```bash
cd ~/Code/my-project
herdr
```

Then pause and explain the screen.

Show these four ideas in order:

| Element | Plain English Meaning | What To Show |
| --- | --- | --- |
| Workspace | A project, task, or investigation. | The current project Herdr opened into. |
| Tab | A layout inside the workspace. | A tab for `agents`, `dev`, `logs`, or `review`. |
| Pane | A real terminal process. | A shell, agent, server, test runner, or log stream. |
| Sidebar | The place where agent state is visible. | Working, blocked, done, idle. |

Say this simply:

```text
Herdr is not difficult once you understand the pieces.
A workspace contains tabs.
A tab contains panes.
An agent runs inside a pane.
The sidebar helps you see agent state.
```

Also mention the mouse-first point:

```text
One thing I like about Herdr is that you can click around.
You can click panes, tabs, workspaces, and agents.
That makes it feel much more approachable than a pure keyboard-only terminal setup.
```

## Create Two Workspaces

This is the first real demo.

Show that Herdr can manage more than one project or task.

Create two workspaces:

1. One for the main app.
2. One for docs, review, or a second repo.

Useful commands:

```bash
herdr workspace list
herdr workspace create --cwd ~/Code/my-project --label "app"
herdr workspace create --cwd ~/Code/my-docs --label "docs"
```

What to say:

```text
I like to think of a workspace as one unit of work.
That might be a repo, a bug, a feature, or an investigation.
The point is that I can keep separate jobs separate without losing the running processes.
```

What to show:

- switch between workspaces
- rename a workspace if useful
- explain that long-running agents can live inside a workspace
- show that this is how you avoid mixing projects together

## Create Tabs

Tabs are layouts inside a workspace.

Do not make this abstract. Use a practical layout:

```text
workspace: app
  tab: agents
  tab: dev
  tab: logs
  tab: review
```

Create a tab:

```text
ctrl+b, then c
```

Useful commands:

```bash
herdr tab list --workspace w1
herdr tab create --workspace w1 --label "agents"
herdr tab create --workspace w1 --label "dev"
herdr tab create --workspace w1 --label "logs"
```

What to say:

```text
Tabs are useful because each project has different modes of work.
I usually want one place for agents, one for the dev server and tests, one for logs, and one for final review.
```

## Split Panes

Panes are the real terminals.

This is where you run:

- coding agents
- dev servers
- tests
- logs
- git commands
- background checks

Show the two basic splits:

```text
ctrl+b, then v      # split right
ctrl+b, then minus  # split down
```

Then create a simple layout:

```text
tab: agents
  pane 1: Claude Code or Codex
  pane 2: shell or second agent

tab: dev
  pane 1: dev server
  pane 2: test runner

tab: logs
  pane 1: logs or git diff
```

What to say:

```text
The important habit is separation.
Do not let every pane become a random terminal.
Give each pane a job.
```

## Run Agents

Now run a coding agent inside a pane:

```bash
claude
```

Or:

```bash
codex
```

Herdr can show supported agents in the sidebar.

Explain the states in plain English:

| State | Meaning |
| --- | --- |
| `working` | The agent is doing work. |
| `blocked` | The agent needs input, permission, or a decision. |
| `done` | The agent has finished and needs review. |
| `idle` | The agent is ready or not currently doing much. |

What to say:

```text
This is the part I really care about.
I do not just want terminals.
I want to know which agent needs attention.
```

## Detach And Reattach

This is a good practical tip.

Detach the client:

```text
ctrl+b, then q
```

Then reattach:

```bash
herdr
```

What to say:

```text
This is the difference between closing the UI and stopping the work.
When I detach, the panes keep running.
That means the agents, servers, tests, and logs can keep going while I step away.
```

Important distinction:

```text
Detach keeps panes running.
Stopping the server ends the session.
```

Stop the server only when you want to terminate the running panes:

```bash
herdr server stop
```

## Customize Herdr With AI

This is a key point for the video.

We are agentic developers, so we should not be hand-editing every config file.

Use AI to manage the config.

Prompt:

```text
Read the Herdr configuration docs:
https://herdr.dev/docs/configuration/

Update my Herdr config at `~/.config/herdr/config.toml` to:

1. Use the `rose-pine` theme.
2. Keep the prefix key as `ctrl+b`.
3. Make the sidebar useful for managing coding agents.
4. Show agent labels on pane borders.
5. Disable sound notifications for recording.
6. Validate the TOML.
7. Reload Herdr with `herdr server reload-config`.

Before changing anything, show me the current config and the planned diff.
```

Useful config shape:

```toml
[theme]
name = "rose-pine"

[bindings]
prefix = "ctrl+b"
toggle_sidebar = "prefix+b"
help = "prefix+?"
new_workspace = "prefix+shift+n"
workspace_picker = "prefix+w"
new_tab = "prefix+c"
split_vertical = "prefix+v"
split_horizontal = "prefix+minus"
zoom = "prefix+z"
detach = "prefix+q"

[ui]
pane_borders = true
pane_gaps = true
show_agent_labels_on_pane_borders = true
agent_panel_sort = "priority"
prompt_new_tab_name = true

[notifications]
sound = false
```

What to say:

```text
The human decides the taste and constraints.
The agent makes the boring edit, validates it, and reports what changed.
```

For this tutorial, the main resource is not a big config pack. It is the real slash command used in the final demo.

## Install Agent Integrations

Herdr can integrate with supported coding agents.

Show this as setup, not as a long technical section.

```bash
herdr integration install claude
herdr integration install codex
herdr integration install pi
herdr integration install opencode
```

Then install the Herdr skill for agents:

```bash
npx skills add https://herdr.dev/skills/herdr/SKILL.md
```

Also mention the agent guide:

```text
https://herdr.dev/agent-guide.md
```

What to say:

```text
This gives the agent better instructions for understanding Herdr.
It means the agent can inspect panes, create helper panes, run commands, and read output without me manually copying everything around.
```

## The Killer Demo: Agents Control Herdr

This is the payoff at the end.

Tease this in the intro:

```text
Stick around to the end, because I will show you how an AI agent can control Herdr itself and use it to orchestrate more complex workflows.
```

Then show it for real.

Start with the simplest version:

```text
Can you open a Herdr pane for me, run the project's test suite inside it, wait for the result, and then tell me what happened?

Create the pane without stealing focus.
Do not close the pane when you are done.
```

Then show the real slash command:

```md
---
description: Take a GitHub issue end to end - worktree, implement, test, PR - running in its own Herdr tab.
argument-hint: <github issue number or URL>
---

Issue: $ARGUMENTS

Do this yourself, you already know how - worktrees, testing, and PRs aren't new to you. Steps are here only to pin down the Herdr wiring, not to teach you the engineering. This works in any repo's current workspace:

1. `gh issue view $ARGUMENTS` to pull the issue.
2. Create a worktree + branch for it, always based off the repo's main branch.
3. Find your current workspace: `herdr pane current` -> workspace_id.
4. Create a new tab for this ticket with `herdr tab create`.
5. Start an agent in that tab with `herdr agent start`.
6. Hand it the task with `herdr agent send`.
7. Tell me the tab label and branch name.
```

The full command is in:

```text
resources/commands/ticket.md
```

What this proves:

```text
Herdr is not only a workspace for humans.
It can become part of the agent's working environment.
```

That is the moment where the viewer should understand why Herdr is interesting.

## Useful Keyboard Shortcuts

The prefix key is:

```text
ctrl+b
```

The useful shortcuts to cover are:

| Action | Config Key | Shortcut |
| --- | --- | --- |
| Toggle sidebar | `toggle_sidebar` | `prefix+b` |
| Show help | `help` | `prefix+?` |
| New workspace | `new_workspace` | `prefix+shift+n` |
| Workspace picker | `workspace_picker` | `prefix+w` |
| New tab | `new_tab` | `prefix+c` |
| Previous tab | `previous_tab` | `prefix+p` |
| Next tab | `next_tab` | `prefix+n` |
| Split right | `split_vertical` | `prefix+v` |
| Split down | `split_horizontal` | `prefix+minus` |
| Zoom pane | `zoom` | `prefix+z` |
| Close pane | `close_pane` | `prefix+x` |
| Detach | `detach` | `prefix+q` |

Do not make the viewer memorize everything.

For the video, focus on:

- sidebar
- new workspace
- new tab
- split panes
- zoom
- detach
- help

## Simple Demo Flow

Use this order when recording:

1. Say the opening script.
2. Install Herdr.
3. Open Herdr in a real project.
4. Explain workspace, tab, pane, sidebar.
5. Create two workspaces.
6. Create the `agents`, `dev`, `logs`, and `review` tabs.
7. Split panes inside the `dev` tab.
8. Run an agent in the `agents` tab.
9. Show agent state in the sidebar.
10. Detach with `ctrl+b q`.
11. Reattach with `herdr`.
12. Ask AI to update the config.
13. Show the rose-pine theme and useful bindings.
14. Install the agent integrations and Herdr skill.
15. Run the simple AI-controlled pane demo.
16. Run the `/ticket` slash command demo.
17. Show the free slash command file.
18. Close with the practical takeaway.

This should feel like a guided walkthrough, not a complete encyclopedia.

## What To Give Away

Link these in the description:

- slash command: `resources/commands/ticket.md`
- Herdr install docs: https://herdr.dev/docs/install/
- Herdr work docs: https://herdr.dev/docs/how-to-work/
- Herdr config docs: https://herdr.dev/docs/configuration/
- Herdr agent guide: https://herdr.dev/agent-guide.md

## Outro

Herdr is useful because it gives AI developers one place to manage long-running agent work.

You can start simple:

```text
one project
one agent pane
one test pane
one log pane
```

Then, once that makes sense, you can move to the advanced pattern where agents control Herdr directly.

The `/ticket` slash command is linked below.

If you are building serious projects with AI coding agents, this is the kind of workflow that helps you stay organised without slowing down.
