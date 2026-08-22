# DS Kanban

DS Kanban adds a board to DeepSeek Harness for viewing coordinator and worker
sessions across projects.

The plugin was built and tested with DeepSeek Harness `0.1.0-rc.8`.

## Install

Run these commands from the root of this repository:

```bash
PLUGIN_DIR="$(pwd)/tutorials/deepseek-harness-setup/code/dsh-client-ui-ds-kanban"
pnpm --dir "$HOME/.dsh/profiles/web" add "dsh-client-ui-ds-kanban@file:$PLUGIN_DIR"
```

Add the plugin to `~/.dsh/profiles/web/cordis.patch.yml`:

```yaml
- insert:
    - id: ds-kanban
      name: dsh-client-ui-ds-kanban
```

Restart the pinned web interface:

```bash
npx @deepseek-ai/dsh@0.1.0-rc.8 web
```

Open **DS Kanban** from the sidebar footer.

## Check the Package

```bash
node --check tutorials/deepseek-harness-setup/code/dsh-client-ui-ds-kanban/lib/index.js
node --check tutorials/deepseek-harness-setup/code/dsh-client-ui-ds-kanban/lib/client.js
```

## Remove

Remove the `ds-kanban` entry from `cordis.patch.yml`, then run:

```bash
pnpm --dir "$HOME/.dsh/profiles/web" remove dsh-client-ui-ds-kanban
```

Restart DeepSeek Harness.
