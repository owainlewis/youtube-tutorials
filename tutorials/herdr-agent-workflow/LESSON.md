# Herdr: The Agent Multiplexer AI Developers Need

Free resources included: my Herdr setup files, reference configs, prompts, and setup script.

Herdr is a terminal workspace manager built for AI coding agents.

The practical reason to care is simple: once you run more than one coding agent, the hard part is not starting agents. The hard part is knowing which agent is working, which one is blocked, which one is done, and which terminal still has the server, tests, or logs you need.

Herdr gives you tmux-style persistence, mouse-native panes, agent state, integrations, and a CLI/socket API that agents can use from inside the terminal.

My honest opinion is that the Codex UI is still the easiest place for my day-to-day development work when I need to manage multiple projects and agents. It gives me a clean view of the work, and that matters.

But I keep coming back to Herdr because it solves a slightly different problem. I have tried tmux and cmux, and both were interesting, but neither quite felt right for my workflow. Herdr feels different. I enjoy using it, and it helps me stay organised when agent sessions run for hours.

## Title Options

Recommended title: Herdr: The Agent Multiplexer AI Developers Need

Giveaway line: My Herdr setup files, configs, prompts, and setup script are linked for free below.

1. Herdr: The Agent Multiplexer AI Developers Need
2. Herdr Complete Guide for AI Coding Agents
3. How to Run Multiple Coding Agents Without Losing Control
4. My Herdr Workflow for Claude Code, Codex, Tests, and Logs
5. Stop Losing Track of Your AI Coding Agents
6. Herdr vs tmux for AI Developers
7. The Terminal Runtime for AI Coding Agents
8. Herdr: My Setup for Running Multiple Coding Agents

## Opening Script

This is a complete guide to Herdr for AI coding agents.

By the end of the video, you'll know everything you need to know to use Herdr as a practical workspace for agents, projects, tabs, panes, servers, tests, logs, and long-running development sessions.

The reason this matters is that normal terminals were not really designed for this level of agentic development. We are no longer just running one shell and one server. We are managing many agents, many projects, test runners, logs, and sessions that can last for hours.

For my normal day-to-day development work, I still love the Codex UI because it makes it easy to manage multiple projects and multiple agents. But I have also tried tmux and cmux, and for my workflow something did not quite feel right. Herdr feels different. It is mouse-first, it is pleasant to use, and it helps me stay organised when I have many agents running at the same time.

In this video, we'll cover how to install Herdr, how the UI works, how to create projects, tabs, and panes, how to run coding agents, how to use AI to manage your Herdr configuration, and the advanced worker orchestrator pattern, where an agent opens new terminals, runs checks, waits for output, and reports back.

All of the config files, prompts, and setup scripts are linked for free in the description below.

So, let's get into it.

## What Herdr Is

Herdr is a terminal multiplexer for coding agents.

The closest mental model is tmux:

- A background server owns the terminal processes.
- A client attaches to show the UI.
- You can detach and reattach later.
- Your panes keep running while the client is gone.

Herdr adds the pieces tmux does not know about:

- Workspaces for projects or investigations.
- Tabs for layouts inside a workspace.
- Panes that run real terminal processes.
- Agent state in the sidebar.
- Integrations for agent session restore and state reporting.
- A CLI and socket API that scripts and agents can drive.

The important shift is this:

```text
tmux manages terminals.
Herdr manages terminals plus agent state.
```

That matters because coding agents are not just commands you run once. They are long-running workers that pause for permission, need review, run tools, and often sit beside servers, test runners, logs, and other agents.

## Why AI Developers Should Care

Running one coding agent is easy.

Running several is where the workflow starts to break:

- One agent is waiting for permission.
- One agent is still editing files.
- One agent says it is done, but you have not reviewed it.
- A dev server is running in another pane.
- Tests failed somewhere else.
- You closed the terminal and now you do not know what survived.

This gets worse because agent sessions often last for hours.

You might start one agent on a feature, another on a review, another on docs, and a fourth terminal with the dev server. At the start, it feels productive. An hour later, it is easy to lose track of what needs your attention.

That is the real reason I care about Herdr.

It is not just a prettier terminal multiplexer. It gives you one visible control surface for long-running agent work.

```mermaid
flowchart LR
  Dev["Developer"] --> Herdr["Herdr workspace"]
  Herdr --> AgentA["Claude Code\nblocked"]
  Herdr --> AgentB["Codex\nworking"]
  Herdr --> Tests["Tests\nrunning"]
  Herdr --> Logs["Logs\nwatching"]
  AgentA --> Review["Human decision"]
  AgentB --> Evidence["Diff and tests"]
```

The lesson is not "run as many agents as possible."

The lesson is "give each agent a clear job, keep the work visible, and make review easy."

## Install Herdr

On Linux or macOS, the direct install path is:

```bash
curl -fsSL https://herdr.dev/install.sh | sh
herdr
```

On Windows preview beta:

```powershell
powershell -ExecutionPolicy Bypass -c "irm https://herdr.dev/install.ps1 | iex"
herdr
```

If you already use Homebrew:

```bash
brew install herdr
```

If you already use mise:

```bash
mise use -g herdr
```

If you use Nix, Herdr provides a flake:

```bash
nix run github:ogulcancelik/herdr
```

Check the install:

```bash
herdr --version
herdr
```

If your shell cannot find `herdr`, restart the terminal or check that the install directory is on your `PATH`.

For direct installs, Herdr can update itself:

```bash
herdr update
```

Homebrew, mise, and Nix installs update through those package managers.

## The Basic Model

Teach Herdr in this order:

| Concept | What it means | When to use it |
| --- | --- | --- |
| Session | A persistent background Herdr server namespace. | Use the default session first. Use named sessions for fully separate contexts. |
| Workspace | A project-level container. | One repo, task, or investigation. |
| Tab | A layout inside a workspace. | Separate `agents`, `server`, `logs`, and `review`. |
| Pane | A real terminal process. | Run agents, shells, servers, tests, and logs. |
| Agent | A recognized coding agent process. | Claude Code, Codex, Pi, OpenCode, Cursor Agent, and others. |

Start Herdr from a project:

```bash
cd ~/Code/my-project
herdr
```

Run an agent inside the first pane:

```bash
claude
```

Or:

```bash
codex
```

Herdr detects supported agents and shows their state in the sidebar:

| State | Meaning |
| --- | --- |
| `working` | The agent is actively running. |
| `blocked` | The agent needs input, permission, or a decision. |
| `done` | The agent finished and you have not looked at it yet. |
| `idle` | The agent is ready or has been seen. |
| `unknown` | Herdr cannot classify it confidently. |

## The Video Walkthrough

Use this order in the video:

1. Install Herdr.
2. Start Herdr from a real project.
3. Explain the prefix key: `ctrl+b`.
4. Use an agent to change the theme and basic config.
5. Create and manage projects with workspaces.
6. Create and manage tabs inside a project.
7. Create and manage panes inside a tab.
8. Run Claude Code, Codex, or another agent.
9. Install agent integrations and the Herdr skill.
10. Use AI to manage the boring parts, including Herdr config.
11. Show the worker orchestrator pattern: ask one agent to open helper panes and run work.
12. Detach with `ctrl+b q`, reattach with `herdr`, and show that everything is still running.

That order keeps the video practical. Basics first, then the part that makes Herdr feel different.

## The First Workspace To Build

For the video demo, use one repo and four panes:

```text
workspace: project-name
  tab: agents
    pane 1: claude or codex
    pane 2: second agent or shell
  tab: dev
    pane 1: dev server
    pane 2: test runner
  tab: logs
    pane 1: logs or git diff
```

You can create most of this with the mouse:

- Click panes, tabs, workspaces, and agents.
- Drag split borders.
- Right-click for context menus.
- Drag-select text to copy.

The keyboard basics are:

| Action | Key |
| --- | --- |
| Prefix key | `ctrl+b` |
| Toggle sidebar | `ctrl+b`, then `b` |
| New tab | `ctrl+b`, then `c` |
| Split right | `ctrl+b`, then `v` |
| Split down | `ctrl+b`, then `minus` |
| Workspace picker | `ctrl+b`, then `w` |
| Detach | `ctrl+b`, then `q` |
| Show all bindings | `ctrl+b`, then `?` |

## Create And Manage Projects

In Herdr, a project is usually a workspace.

Start in a project directory:

```bash
cd ~/Code/my-project
herdr
```

Create a new workspace from inside Herdr with the mouse, or use the prefix:

```text
ctrl+b, then shift+n
```

From the CLI:

```bash
herdr workspace list
herdr workspace create --cwd ~/Code/my-project --label "my-project"
herdr workspace rename w1 "api"
herdr workspace close w1
```

Use one workspace per repo, task, or investigation. This is what keeps agent state readable when several projects are running.

## Create And Manage Tabs

Tabs are layouts inside a workspace.

Good tab names for coding-agent work:

- `agents`
- `dev`
- `tests`
- `logs`
- `review`

Create a tab with the keyboard:

```text
ctrl+b, then c
```

From the CLI:

```bash
herdr tab list --workspace w1
herdr tab create --workspace w1 --label "tests"
herdr tab rename w1:t2 "review"
herdr tab focus w1:t2
herdr tab close w1:t2
```

Tabs are useful when a project has several modes of work. For example, keep the agent conversation in `agents`, the server and tests in `dev`, and the final diff review in `review`.

## Create And Manage Panes

Panes are real terminals inside a tab.

Create a pane with the keyboard:

```text
ctrl+b, then v      # split right
ctrl+b, then minus  # split down
```

From the CLI:

```bash
herdr pane list
herdr pane split w1:p1 --direction right --no-focus
herdr pane split w1:p1 --direction down --no-focus
herdr pane rename w1:p2 "tests"
herdr pane run w1:p2 "npm test"
herdr pane read w1:p2 --source recent --lines 80
herdr pane close w1:p2
```

Use panes for processes that should keep running:

- an agent
- a dev server
- tests
- logs
- a shell for git and file inspection

The important habit is naming and separation. Do not let every pane become "random terminal number four."

## Useful Keyboard Shortcuts

The prefix key is:

```text
ctrl+b
```

Press it, release it, then press the action key.

Useful shortcuts to cover in the video:

| Action | Config key | Shortcut |
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

You do not need to memorize all of them. For the video, the high-value ones are sidebar, new tab, split panes, zoom, detach, and help.

The important demo moment is detach and reattach:

```bash
# inside Herdr
ctrl+b, then q

# back in your shell
herdr
```

The panes are still there because the Herdr server kept them alive.

To stop the session and terminate panes:

```bash
herdr server stop
```

## How To Work With Herdr

This is worth walking through slowly in the video.

Herdr has a simple model:

```text
Run Herdr where the work lives.
Attach from wherever you are.
```

The everyday local path is:

```bash
cd ~/Code/my-project
herdr
```

Run your agents, tests, servers, and logs inside panes. Then detach:

```text
ctrl+b, then q
```

Your terminal client closes, but the Herdr server keeps the panes running.

Reattach later:

```bash
herdr
```

That is the part to show on camera:

1. Start a dev server in one pane.
2. Start Claude Code or Codex in another pane.
3. Detach with `ctrl+b q`.
4. Return to the shell.
5. Run `herdr`.
6. Show that the server and agent are still there.

There are three useful remote patterns:

| Pattern | Command | Use it when |
| --- | --- | --- |
| Local work | `herdr` | The code and agents are on your machine. |
| Normal SSH | `ssh you@server`, then `herdr` | You already work inside a remote shell, or you are using a phone SSH client. |
| Remote thin client | `herdr --remote workbox` | You want the remote session to feel local and keep local terminal features. |

For phone access, there is no Herdr mobile app to install. Use an SSH client, connect to the machine where the work is running, and run:

```bash
herdr
```

The same persistent session opens in the phone terminal.

The key distinction:

```text
Detach keeps live processes running.
Stopping the server ends the running panes.
```

Use this command only when you want to stop the session and terminate the panes:

```bash
herdr server stop
```

## Install Agent Integrations

Herdr detects supported agents automatically, but integrations make the workflow better.

Install the integrations for the agents you use:

```bash
herdr integration install claude
herdr integration install codex
herdr integration install pi
herdr integration install opencode
herdr integration status
```

For Claude Code and Codex, integrations report native session identity so Herdr can restore agent sessions after a server restart when possible. Their state still comes from Herdr's screen detection.

For agents such as Pi, Kimi, OpenCode, Kilo, and Hermes, integrations can provide stronger lifecycle state.

The honest version is this: Herdr is good at state, but agent state is still a moving target. Agent terminal UIs change. Hooks differ. Detection can be wrong. Use the sidebar as a visibility layer, not as a reason to skip review.

When state looks wrong:

```bash
herdr agent list
herdr agent explain <target> --json
herdr pane read <pane-id> --source recent --lines 50
```

## Add Herdr To Your Agent Instructions

There are two different files to understand.

First, Herdr has an agent skill. This teaches an agent how to control Herdr from inside a Herdr pane.

Install it globally for supported agents:

```bash
npx skills add ogulcancelik/herdr --skill herdr -g
```

The skill tells the agent to check `HERDR_ENV=1` before controlling Herdr. If the agent is not running inside Herdr, it should stop instead of trying to inspect a session it does not own.

Second, Herdr has a human onboarding guide for agents:

```text
https://herdr.dev/agent-guide.md
```

Use that when you want an agent to help you understand, set up, or troubleshoot Herdr. The guide explains the concepts, setup path, configuration, and diagnosis recipes.

Copy this into your repo's agent instructions when Herdr is part of the workflow:

```md
## Herdr

If you are running inside Herdr, `HERDR_ENV=1` will be set.

When `HERDR_ENV=1` is set:

- Use `herdr pane list` to inspect available panes.
- Use `herdr pane read <pane-id> --source recent --lines 80` before assuming what another pane is doing.
- Use `herdr wait output` for servers and tests.
- Use `herdr wait agent-status` for coding agents.
- Use `--no-focus` when creating helper panes so you do not steal the user's active pane.
- Do not close panes, stop servers, or send input to another agent unless the user asked or the task clearly requires it.

When helping a human set up Herdr, read:

https://herdr.dev/agent-guide.md
```

This repo includes a fuller example at `resources/example-AGENTS.md`.

## The Agent-Controlled Workflow

The most interesting Herdr feature is not the UI.

It is that an agent can control the Herdr workspace it is running inside.

That is the demo to lean into.

Inside a Herdr-managed agent, say:

```text
Can you open a Herdr pane for me, run the test suite inside it, wait for the result, and then tell me what happened?

Do not steal focus.
Do not modify files.
Do not close the pane when you are done.
```

If the Herdr skill is installed and `HERDR_ENV=1` is set, the agent can inspect the current panes, create a sibling pane, run the command, wait for output, read the result, and report back.

That changes the feel of the workflow.

You are no longer manually creating every terminal, copying output between panes, and telling the agent what happened. The agent can use the terminal workspace as part of its own working environment.

From inside Herdr, an agent can:

- list panes
- split panes
- start commands
- wait for output
- read output
- wait for another agent
- spawn helper agents

The core loop looks like this:

```mermaid
flowchart LR
  Human["Human asks agent"] --> Agent["Agent inside Herdr"]
  Agent --> Inspect["Inspect panes"]
  Inspect --> Split["Open helper pane"]
  Split --> Run["Run command"]
  Run --> Wait["Wait for output"]
  Wait --> Read["Read result"]
  Read --> Report["Report back"]
```

Underneath, the agent is using commands like these:

```bash
herdr pane list
herdr workspace list
herdr pane read w1:p1 --source recent --lines 80
```

Run a test in a new pane without stealing focus:

```bash
NEW_PANE=$(herdr pane split w1:p1 --direction right --no-focus | python3 -c 'import sys,json; print(json.load(sys.stdin)["result"]["pane"]["pane_id"])')
herdr pane run "$NEW_PANE" "npm test"
herdr wait output "$NEW_PANE" --match "test" --timeout 60000
herdr pane read "$NEW_PANE" --source recent --lines 80
```

Wait for another agent:

```bash
herdr wait agent-status w1:p2 --status done --timeout 120000
herdr pane read w1:p2 --source recent --lines 100
```

The strongest version of this demo is not "look, Herdr has panes."

It is:

```text
I ask one agent to create the environment it needs to verify its own work.
```

Use this carefully. An agent that can control panes is useful, but it should still have boundaries.

Good jobs:

- start a dev server and wait for readiness
- run tests beside the main agent
- read logs after a failure
- check what a helper agent reported
- create a clean workspace for a narrow task

Risky jobs:

- sending instructions to another agent without asking
- closing panes with active work
- making several agents edit the same files
- treating `done` as reviewed

## Worker Orchestrator Pattern

This is the killer demo.

The pattern is:

```text
One main agent coordinates helper panes.
Each helper pane does one narrow job.
The main agent waits, reads the result, and reports back.
```

Use a project where the work is visible. A good demo project is a small JavaScript or TypeScript app with:

- `npm run dev`
- `npm test`
- `npm run lint`
- a small bug or README change
- a visible passing or failing test result

The main agent should not make a huge change. The point is to show the workflow, not to ship a complex feature.

Use this prompt inside Claude Code or Codex running inside Herdr:

```text
Can you act as a worker orchestrator inside Herdr?

Open three Herdr panes without stealing focus:

1. A test pane that runs `npm test`.
2. A lint pane that runs `npm run lint`.
3. A git pane that runs `git diff --stat` and then waits.

Wait for the test and lint output.
Read the output from each pane.
Then report:

1. Which panes you created.
2. Which commands passed or failed.
3. The most important output.
4. Whether there is enough evidence to continue.

Do not modify files.
Do not close panes.
Do not send input to another agent.
```

If you want the demo to feel more agent-native, make the helper panes agent panes:

```text
Can you open two Herdr panes without stealing focus?

In the first pane, launch Claude Code and ask it to review the test coverage.
In the second pane, launch Claude Code and ask it to inspect the README and docs for drift.

Wait until each helper agent reaches done or idle.
Read the recent output from both panes.
Then summarize the findings and tell me what still needs human review.

Do not let the helper agents modify files.
Do not close panes.
```

The reason this is powerful is that Herdr gives the main agent a workspace it can operate. The agent is not just reading your prompt. It can create terminals, run checks, wait, inspect, and report.

## Customize The Style And Feel

Herdr works without a config file. Add one when you want custom keys, themes, sidebar behavior, notifications, or session behavior.

The config file is:

```text
~/.config/herdr/config.toml
```

Print the default config:

```bash
herdr --default-config
```

Create a starting config:

```bash
mkdir -p ~/.config/herdr
herdr --default-config > ~/.config/herdr/config.toml
```

After edits, reload the running server:

```bash
herdr server reload-config
```

And because we are building with agents, do not make this feel more manual than it needs to be.

The practical move is to ask your agent to inspect the config docs, update the config, validate the TOML, and reload Herdr:

```text
Read the Herdr configuration docs.

Update my Herdr config at `~/.config/herdr/config.toml` to use the `rose-pine` theme, keep the prefix key as `ctrl+b`, make the sidebar useful for managing coding agents, and disable sound notifications for recording.

Validate that the TOML parses.
Then reload Herdr with `herdr server reload-config`.

Do not change unrelated settings.
```

That is a good on-camera point: agentic developers should not be hand-editing every config file. The human decides the taste and the constraints. The agent makes the boring edit, validates it, and reports what changed.

The most useful style settings for recording:

```toml
onboarding = false

[theme]
name = "rose-pine"
auto_switch = true
light_name = "rose-pine-dawn"
dark_name = "rose-pine"

[theme.custom]
accent = "#c4a7e7"
green = "#9ccfd8"
blue = "#31748f"
red = "#eb6f92"
yellow = "#f6c177"

[keys]
prefix = "ctrl+b"
toggle_sidebar = "prefix+b"
new_workspace = "prefix+shift+n"
workspace_picker = "prefix+w"
new_tab = "prefix+c"
split_vertical = "prefix+v"
split_horizontal = "prefix+minus"
zoom = "prefix+z"
detach = "prefix+q"

[ui]
sidebar_width = 34
sidebar_min_width = 22
sidebar_max_width = 44
pane_borders = true
pane_gaps = true
show_agent_labels_on_pane_borders = true
agent_panel_sort = "priority"
accent = "#7aa89f"

[ui.toast]
delivery = "herdr"
delay_seconds = 1

[ui.toast.herdr]
position = "bottom-right"

[ui.sound]
enabled = false
```

This makes the sidebar more useful on camera, sorts agents by attention priority, shows agent labels on pane borders, and uses in-app notifications without sound.

The giveaway configs are in `resources/configs/`.

## A Practical Demo Flow

Use this flow for the video.

1. Show the problem.

Start two agents in separate panes or tabs. Ask one to inspect the repo and one to make a small README change. Show that the real issue is tracking state.

2. Install and start.

```bash
curl -fsSL https://herdr.dev/install.sh | sh
herdr --version
herdr
```

3. Explain the prefix key.

Show that the prefix is `ctrl+b`.

Open the help panel:

```text
ctrl+b, then ?
```

Toggle the sidebar:

```text
ctrl+b, then b
```

4. Change the theme and basic config.

Ask the agent to update `~/.config/herdr/config.toml`, show the theme, sidebar, notifications, and keybindings, then reload:

```bash
herdr server reload-config
```

5. Create and manage a project.

Create a workspace with the mouse or keyboard. Explain that a workspace is the project container.

6. Create and manage tabs.

Create `agents`, `dev`, `tests`, and `review` tabs.

7. Create and manage panes.

Create a right split, a down split, rename a pane, run a command, and read output.

8. Add integrations.

```bash
herdr integration install claude
herdr integration install codex
herdr integration status
```

9. Install the agent skill.

```bash
npx skills add ogulcancelik/herdr --skill herdr -g
```

10. Show the worker orchestrator pattern.

Use the worker orchestrator prompt from `resources/prompts.md`. The main moment is the agent opening helper panes, running checks, waiting, reading output, and reporting back.

11. Show persistence.

Detach with `ctrl+b q`, reattach with `herdr`, and show that the agents and server are still running. Make this a clear demo beat, because it explains why Herdr is useful for sessions that last for hours.

12. Show the CLI layer.

```bash
herdr pane list
herdr agent list
herdr pane read <pane-id> --source recent --lines 50
```

13. Show the config giveaway.

Copy one reference config:

```bash
cp resources/configs/agent-dashboard.toml ~/.config/herdr/config.toml
herdr server reload-config
```

14. Close with the limitation.

Herdr makes agent work visible and persistent. It does not replace specs, tests, code review, or human judgment.

## Tradeoffs

Where Herdr is strong:

- running multiple terminal agents
- seeing blocked, working, done, and idle state
- keeping work alive after detach
- remote SSH work
- agent and script coordination through CLI commands
- a lighter alternative to desktop agent managers

Where to be careful:

- too many agents can create review debt
- state detection can lag behind agent UI changes
- server restart is different from detach
- pane screen history can store sensitive output if enabled
- custom plugins run as normal code on your machine
- Windows support is still beta

The best workflow is still boring:

1. Give the agent a small job.
2. Keep the workspace visible.
3. Run tests.
4. Review the diff.
5. Decide what to merge.

## References

- Herdr docs: https://herdr.dev/docs/
- Install docs: https://herdr.dev/docs/install/
- How to work with Herdr: https://herdr.dev/docs/how-to-work/
- Agent guide for humans using agents: https://herdr.dev/agent-guide.md
- Agent skill docs: https://herdr.dev/docs/agent-skill/
- Configuration docs: https://herdr.dev/docs/configuration/
- CLI reference: https://herdr.dev/docs/cli-reference/
- Socket API: https://herdr.dev/docs/socket-api/
- Herdr GitHub repo: https://github.com/ogulcancelik/herdr
- Prompts: `resources/prompts.md`
- Setup helper: `code/setup-herdr.sh`
- Reference configs: `resources/configs/`

## Summary

- The one thing to remember: Herdr is useful because it treats coding agents as visible, persistent terminal workers.
- The honest limitation: it helps you supervise agent work, but it does not make parallel agent work safe by itself.
- What to try next: install Herdr, add the integrations for your agents, install the agent skill, and run one small project with an agent pane, a test pane, and a log pane.
