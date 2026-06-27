# Plugins

This is the supporting material for the video: Plugins.

Plugins give Codex access to external tools. Instead of context-switching to another app,
you describe the task in natural language and Codex handles the tool interaction.

## Installing plugins

In the Codex desktop app: Settings > Plugins > Browse.

## The Linear plugin

Linear is a project management tool. The Linear plugin lets Codex read and update issues
directly from a Codex session. No browser tab required.

### What it enables

- "Show me all open bugs in the Current Sprint"
- "Create an issue for the auth bug we just found"
- "Mark issue ENG-142 as in progress"
- "What issues are assigned to me?"
- Start a plan or spec directly from a Linear issue: "Fix the bug in ENG-142"

### Installing the Linear plugin

In the desktop app: Settings > Plugins > search "Linear" > Install.

Authenticate with your Linear account when prompted.

### Workflow: issue to plan

1. Ask Codex to fetch the issue: "Show me ENG-142"
2. Codex returns the issue title, description, and acceptance criteria from Linear
3. Use that as the foundation for your plan or lightweight spec
4. When done: "Mark ENG-142 as done and leave a comment with a summary of the changes"

This replaces the manual copy-paste loop between your issue tracker and your coding session.

## Other useful plugins

| Plugin | What it does |
|--------|-------------|
| GitHub | Read PRs, issues, and comments without leaving the session |
| Sentry | Fetch error details and stack traces by ID |
| Notion | Read and write docs from a Codex session |

Install only what you actually use. Each plugin adds context overhead to every session.

## Go Deeper

To go deeper on AI engineering, join my AI engineering community: [aiengineer.co](https://aiengineer.co).
