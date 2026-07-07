# Herdr Setup Checklist

## Install

- Install Herdr.
- Run `herdr --version`.
- Start Herdr from a real project folder with `herdr`.
- Confirm you can detach with `ctrl+b q`.
- Confirm you can reattach with `herdr`.
- Confirm a running pane survives detach and reattach.
- Know the difference between detaching the client and stopping the server.

## Working Modes

- Use `herdr` for local work.
- Use `ssh you@server`, then `herdr`, when the code and agents live on a remote machine.
- Use `herdr --remote <host>` when you want a local thin client for a remote Herdr server.
- Use a phone SSH client plus `herdr` to inspect long-running sessions from your phone.
- Use `herdr server stop` only when you want to stop the session and terminate panes.

## Agent Setup

- Install integrations for the agents you use.
- Run `herdr integration status`.
- Install the Herdr skill with `npx skills add ogulcancelik/herdr --skill herdr -g`.
- Add the Herdr section from `resources/example-AGENTS.md` to any repo where agents should use Herdr.

## Workspace

- Use one workspace per repo, task, or investigation.
- Use tabs for `agents`, `dev`, `logs`, and `review`.
- Use panes for agents, servers, tests, logs, and shells.
- Rename important agents or panes when the sidebar gets noisy.
- Show how to create, rename, focus, and close a workspace.
- Show how to create, rename, focus, and close a tab.
- Show how to split, rename, run a command in, read, and close a pane.

## Keyboard

- Explain that the prefix key is `ctrl+b`.
- Show `prefix+?` for help.
- Show `prefix+b` for sidebar toggle.
- Show `prefix+c` for new tab.
- Show `prefix+v` and `prefix+minus` for panes.
- Show `prefix+z` for zoom.
- Show `prefix+q` for detach.

## Worker Orchestrator Demo

- Use the prompt from `resources/prompts.md`.
- Ask the main agent to open helper panes without stealing focus.
- Run tests in one pane.
- Run lint or another check in another pane.
- Read the outputs.
- Report what passed, failed, and still needs review.

## Config

- Create `~/.config/herdr/config.toml`.
- Choose a built-in theme.
- Set `agent_panel_sort = "priority"` if you care most about blocked and done agents.
- Turn on `show_agent_labels_on_pane_borders = true` for recording.
- Choose notification delivery.
- Disable sound on shared machines or recordings.

## Safety

- Do not run many agents against the same files.
- Do not treat `done` as reviewed.
- Do not enable pane screen history if pane output may contain secrets.
- Review plugin manifests before installing third-party plugins.
- Use `herdr agent explain <target> --json` when state detection looks wrong.
