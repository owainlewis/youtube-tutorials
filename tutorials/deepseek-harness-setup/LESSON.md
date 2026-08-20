# Set Up DeepSeek Harness

DeepSeek Harness is a local coding agent from DeepSeek. The useful difference is
its plugin model. Models, tools, storage, the agent loop, and browser interface
are all replaceable parts.

This tutorial gives you one setup path that you can reproduce. You will start
the web interface, configure a model, connect Linear through a read-only MCP
server, and use a coding agent to build the local Kanban plugin from the
included prompt.

The commands below pin DeepSeek Harness to `0.1.0-rc.8`. The project is still a
developer preview and warns that compatibility-breaking changes will happen.
Pinning the version keeps this tutorial consistent while the project changes.

## What You Need

Install a current version of Node.js with `npm` and make sure `npx` works:

```bash
node --version
npm --version
npx --version
```

You also need:

- a project directory that the agent can use as its workspace
- a DeepSeek API key for the model setup shown here
- a Linear account if you want to follow the MCP section
- Git and pnpm if you want to build the Kanban plugin inside a source checkout

Do not paste a real key into this repository or a prompt. Add secrets through
the harness settings interface or your shell environment.

## Start the Web Interface

Run the pinned release:

```bash
npx @deepseek-ai/dsh@0.1.0-rc.8 web
```

The command starts the web interface at
[http://127.0.0.1:3080](http://127.0.0.1:3080).

A fresh setup cannot send a message yet. It needs a workspace and a model.

First, click **Choose workspace**, add the project directory you want the agent
to use, and select it. The composer stays disabled until a workspace is active.

Next, open **Settings**, then **Models**. Add your DeepSeek API key, save it, and
select `deepseek-v4-flash`. Model changes apply to the next request without a
restart.

Send a small read-only task to prove the setup:

```text
Summarize this repository and identify its main packages. Do not change any files.
```

Open the Trajectory view after the response. You should see the model request,
tool calls, results, token use, and timing for the session.

## What the Setup Creates

DeepSeek Harness stores its local state under `~/.dsh` by default:

```text
~/.dsh/
  settings.yaml
  .credentials.yaml
  profiles/
    web/
      package.json
      cordis.patch.yml
  storages/
```

`settings.yaml` holds normal configuration. The credentials file holds saved
keys. The web profile contains the plugin dependencies and your local patch
layer.

Treat this directory as sensitive. Do not commit it.

## Connect Linear Through MCP

MCP stands for Model Context Protocol. An MCP server gives an agent a set of
external tools. In this example, Linear supplies tools for reading teams,
projects, and issues.

The rc.8 command already ships the DeepSeek Harness MCP client. Linear uses
OAuth 2.1, so this setup runs Linear's recommended `mcp-remote` bridge over
stdio. It uses Linear's read-only endpoint.

Stop DeepSeek Harness, then add this row to
`~/.dsh/profiles/web/cordis.patch.yml`:

```yaml
- id: mcp-linear
  name: '@deepseek-ai/dsh-mcp-client'
  config:
    serverName: linear
    transport: stdio
    command: npx
    args: ['-y', 'mcp-remote@0.1.38', 'https://mcp.linear.app/mcp/readonly']
```

Start the web interface again:

```bash
npx @deepseek-ai/dsh@0.1.0-rc.8 web
```

Complete the Linear OAuth flow. Wait for tools named
`mcp__linear__<tool>` to appear, then open a new session and test the
connection:

```text
List my Linear teams, then show five active issues. Do not create, update, or delete anything.
```

The `/mcp/readonly` endpoint only exposes read tools. Use
`https://mcp.linear.app/mcp` only when the workflow must create or update
Linear data.

This configuration matches the rc.8 client source and Linear's current
documentation. Rehearse the OAuth login and live tool discovery in your own
profile before recording or relying on it.

## Use the Complete Profile Patch

The accompanying
[profile patch](./resources/cordis.patch.yml) is the complete configuration
used for the demo. It mounts the Codex and Claude Code subagent providers, the
local Kanban browser plugin, and Linear MCP.

The shared patch uses Linear's read-write `/mcp` endpoint with a bearer-token
placeholder. It assumes the provider and plugin packages are already installed
in the web profile. Replace `XXX` only in your local copy, never in a tracked
file. Keep the `/mcp/readonly` setup above if the agent only needs to inspect
Linear.

## Build the Kanban Plugin

The Kanban plugin shows delegated work across projects. Each card groups a
coordinator session with its worker sessions, then surfaces blocked, running,
done, idle, and archived batches.

Build it in a source checkout so the coding agent can inspect the current plugin
interfaces and design tokens:

```bash
git clone --branch dsh-v0.1.0-rc.8 --depth 1 https://github.com/deepseek-ai/deepseek-harness.git
cd deepseek-harness
pnpm install
pnpm run build
pnpm dsh web
```

Select the checkout as the workspace and choose the **Creator** agent preset.
Copy the complete prompt from
[resources/prompts.md](./resources/prompts.md) into a new session.

The prompt specifies the package layout, host and browser entry points, session
data model, slot registration, design tokens, failure cases, and acceptance
checks. It also records several runtime details that are easy to guess wrong,
including the session ID field, subagent titles, activity timing, and injection
format.

When the agent finishes:

1. Read the complete diff.
2. Check every dependency and install script.
3. Check file, environment, network, and credential access.
4. Run every acceptance check from the prompt.
5. Restart the web profile and verify the board with real coordinator and worker
   sessions.
6. Disable the plugin and confirm the standard interface still works.

A host plugin runs with the permissions of the DeepSeek Harness process. A
browser plugin can observe the client services injected into it. Do not install
a community plugin on a machine with source code and credentials until you have
reviewed its source and pinned the version you reviewed.

The [community plugin directory](https://deepseek-code.com/plugins) is useful
for seeing what people are building. Treat it as a discovery page, not a trust
boundary.

## Common Problems

### The port is already in use

Start the web interface on another port:

```bash
npx @deepseek-ai/dsh@0.1.0-rc.8 web --port 8081
```

### The composer is disabled

Select a workspace and configure a usable model. Both are required on a fresh
profile.

### Linear tools do not appear

Confirm that the YAML row is in the web profile, restart the process, complete
the browser OAuth flow, and open a new session. A running session may not see a
plugin mounted after it started.

### A plugin breaks after an update

Run the pinned rc.8 command used by this tutorial. DeepSeek Harness is a
developer preview, so plugin APIs can change between release candidates.

## References

- [DeepSeek Harness repository](https://github.com/deepseek-ai/deepseek-harness)
- [DeepSeek Harness web interface guide](https://github.com/deepseek-ai/deepseek-harness/blob/master/docs/user/guide/index.md)
- [DeepSeek Harness architecture](https://github.com/deepseek-ai/deepseek-harness/blob/master/docs/architecture.md)
- [Community plugins](https://deepseek-code.com/plugins)
- [Linear MCP documentation](https://linear.app/docs/mcp)
- [Complete video guide and recording outline](https://docs.aiengineer.co/docs/YYsG6gYOSyYSWz29G5akuA)
- [Kanban build prompt](./resources/prompts.md)
- [Complete profile patch](./resources/cordis.patch.yml)

## Summary

- The one thing to remember: DeepSeek Harness is useful when you want to change
  the agent workflow or interface, not only the model.
- The honest limitation: it is a developer preview, and local plugins run with
  access to your machine.
- What to try next: start rc.8, run one read-only task, then connect Linear or
  build the Kanban plugin in a disposable checkout.
