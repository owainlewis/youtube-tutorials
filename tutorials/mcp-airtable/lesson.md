# Give Your AI Agents a Database (Airtable MCP)

Companion guide for the video. Connect Claude Code to Airtable through MCP so your AI agents can read and write persistent data.

## The Problem

AI coding agents like Claude Code don't have persistent memory. Every session starts fresh. That makes it hard to use them for day-to-day tasks like project management - tracking ideas, updating statuses, knowing what you're working on.

The fix: connect Claude Code to an external database through MCP. Your agents can read from it, write to it, and build on previous work across sessions.

## What You'll Set Up

1. An Airtable personal access token with the right scopes
2. The official Airtable MCP server connected to Claude Code
3. A working workflow where Claude queries, filters, and updates your data

## Prerequisites

- [Claude Code](https://docs.anthropic.com/en/docs/claude-code) installed (v2.17+)
- An [Airtable](https://airtable.com) account (free tier works)
- An Airtable base with at least one table you want Claude to interact with

## Step 1: Create a Personal Access Token

1. Go to [airtable.com/create/tokens/new](https://airtable.com/create/tokens/new)
2. Give the token a name (e.g. "Claude Code")
3. Add these scopes:
   - `schema.bases:read` - lets Claude see your table structure
   - `data.records:read` - lets Claude query records
   - `data.records:write` - lets Claude create and update records
4. Under **Access**, select the specific base(s) you want Claude to reach. Don't give it access to everything.
5. Copy the token. You'll only see it once.

## Step 2: Connect the MCP Server

Run this in your terminal:

```bash
claude mcp add --scope user --transport http airtable \
  https://mcp.airtable.com/mcp \
  --header "Authorization: Bearer YOUR_TOKEN_HERE"
```

Replace `YOUR_TOKEN_HERE` with the token from Step 1.

This connects to Airtable's official hosted MCP server. Nothing to install locally - no npm, no npx, no Node.js required.

### Verify the connection

Start a new Claude Code session and run:

```
/mcp
```

You should see the Airtable server listed with its tools.

Then try:

```
> List all my Airtable bases
```

If you see your bases, the connection is working.

## Step 3: Use It

Once connected, you can talk to your Airtable data naturally:

```
> Show me all records in my [table name]
> Which items have status "In Progress"?
> Update the status of [record] to "Done"
> Add a new record with title "My New Idea" and status "Idea"
```

Claude discovers the table schema automatically and maps your natural language to the right MCP tool calls.

## Context Management

If you've tried MCP servers before and noticed they slowed things down, that's been fixed.

Claude Code v2.17+ uses **on-demand tool loading**. MCP tool definitions are no longer preloaded into your context window. Instead, Claude searches for the right tool when it needs one.

Check it with:

```
/context
```

MCP tools show as "deferred" - available but not loaded until actually needed. This means you can connect multiple MCP servers without burning context.

## Limitations

Be honest about what this can and can't do:

- **Cannot create bases.** You create the base in Airtable.
- **Cannot create tables or fields.** You design the schema yourself - field types, relationships, views. Claude works within that structure.
- **Primarily reads and writes records.** Think of it as a data layer, not a database builder.
- **Permission prompts on every write.** By default, Claude asks for approval on each MCP tool call. You can add tools to `allowedTools` in your project settings to skip this.

For most workflows, these limitations are fine. Set up the table once, and let Claude handle the data.

## Example: Content Pipeline Skill

You can pair MCP with a Claude Code skill to automate a specific workflow. Here's an example that researches video ideas and writes them to Airtable.

Create `.claude/skills/research/SKILL.md`:

```markdown
---
name: research
description: "Research video ideas for a topic and add them to the Airtable content pipeline."
---

# Research Skill

Generate video ideas for a given topic and push them into Airtable.

## Airtable Configuration

- Base: [Your Base Name] ([your-base-id])
- Table: [Your Table Name] ([your-table-id])

## Process

1. Research the given topic using web search
2. Generate 10 video ideas with concise, YouTube-optimized titles
3. Assign each idea to a content category
4. Use the Airtable MCP to create records in the table
5. Return a summary of what was added
```

Then trigger it:

```
> Research 10 video ideas about building AI agents and add them to my content pipeline
```

Claude reads the skill, generates ideas, calls the Airtable MCP, and writes the records. One command, full pipeline.

## Other Use Cases

This pattern - MCP for the connection, a skill for the workflow - works for any structured data:

| Use Case | What Claude Does |
|----------|-----------------|
| Content pipeline | Research ideas, track status, manage publishing |
| Client tracker | Log interactions, update project status |
| Research database | Store competitor analysis, tool evaluations |
| Knowledge base | Save reusable configs, decision logs, prompts |

## Project Structure

```
your-project/
  .claude/
    skills/
      research/
        SKILL.md            # Defines what Claude does with the data
    settings.local.json     # MCP config (auto-generated by claude mcp add)
```

## Links

- [Airtable MCP Server docs](https://support.airtable.com/docs/using-the-airtable-mcp-server)
- [Claude Code MCP docs](https://docs.anthropic.com/en/docs/claude-code/mcp)
- [Create Airtable API tokens](https://airtable.com/create/tokens)
