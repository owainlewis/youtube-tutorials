# Herdr Setup Checklist

## Install

- Install Herdr.
- Run `herdr --version`.
- Start Herdr from a real project folder with `herdr`.
- Confirm you can detach with `ctrl+b q`.
- Confirm you can reattach with `herdr`.

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
