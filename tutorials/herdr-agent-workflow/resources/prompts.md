# Prompts

Use these prompts inside Herdr after you have installed the Herdr skill:

```bash
npx skills add ogulcancelik/herdr --skill herdr -g
```

## Agent Herdr Setup Prompt

Use this when you want an agent to help you set up or troubleshoot Herdr.

```text
Help me understand and set up Herdr.

Before you answer, read this guide:

https://herdr.dev/agent-guide.md

Then walk me through:

1. What Herdr is.
2. Whether I am already running inside Herdr.
3. How to install Herdr.
4. How to install integrations for Claude Code and Codex.
5. How to install the Herdr agent skill.
6. How to create a practical workspace for agents, tests, servers, and logs.
7. How to diagnose agent state if something looks wrong.

Do not invent commands. If you are unsure, point me to the official Herdr docs page.
```

## Agent Test Pane Prompt

Use this inside a Herdr-managed coding agent.

```text
Can you open a Herdr pane for me, run the project's test suite inside it, wait for the result, and then tell me what happened?

If you are running inside Herdr, use the Herdr skill.

Create the pane without stealing focus.
Do not modify files.
Do not close panes.

When you are done, tell me:

1. Which pane you created.
2. Which command you ran.
3. Whether the command passed or failed.
4. The most important output.
5. What I should inspect next.
```

## Agent Dev Server Prompt

Use this when you want the agent to create a long-running helper pane.

```text
Can you open a Herdr pane for me, start the dev server inside it, wait until it is ready, and then report the local URL or readiness message?

If you are running inside Herdr, use the Herdr skill.

Create the pane without stealing focus.
Do not stop the server after it starts.
Do not modify files.

When you are done, tell me:

1. Which pane contains the server.
2. The command you ran.
3. The readiness output you saw.
4. Any errors that appeared.
```

## Agent Scratch Investigation Prompt

Use this when you want an agent to open a pane for safe read-only exploration.

```text
Can you open a Herdr pane for a read-only investigation?

Use it to inspect the repository structure and identify the likely test command.
Do not modify files.
Do not close the pane.

Report:

1. Which pane you opened.
2. Which files or commands you inspected.
3. The likely test command.
4. What evidence supports that.
```

## Agent Log Reader Prompt

Use this when a server is running in another pane.

```text
If you are running inside Herdr, inspect the current panes.

Find the pane that appears to contain the dev server or logs.
Read the recent output.
Tell me:

1. Which pane you inspected.
2. Whether the server is running.
3. Any visible error.
4. The next command I should run.

Do not send input to the server pane unless I ask.
```

## Agent Coordination Prompt

Use this when one agent needs to wait for another agent.

```text
If you are running inside Herdr, list the agents and panes.

Wait for the target agent to reach `done` or `idle`.
Then read its recent output and summarize the result.

Do not assume a `done` state means the code is safe.
Tell me what evidence still needs review.
```

## Repo Instruction Prompt

Use this to ask an agent to add Herdr guidance to a repo instruction file.

```text
Add a small Herdr section to this repository's agent instructions.

The section should say:

- If `HERDR_ENV=1` is set, the agent is running inside Herdr.
- The agent may inspect panes, read output, run tests in sibling panes, and wait for agent status.
- The agent should use `--no-focus` when creating helper panes.
- The agent must not close panes, stop servers, or send input to another agent unless asked.
- When helping a human set up Herdr, read https://herdr.dev/agent-guide.md first.

Keep it short and practical.
```
