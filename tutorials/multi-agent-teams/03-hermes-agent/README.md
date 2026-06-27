# 03 - Install Hermes Agent on the VPS

This is the supporting material for the video: 03 - Install Hermes Agent on the VPS.

Hermes Agent is a general-purpose AI agent for personal automations and knowledge work. Where Claude Code is optimized for coding, Hermes is the better fit for research, repurposing, drafting, and general task automation.

We install both on the same VPS so Multica can delegate to whichever agent fits a given ticket.

## Install

> Confirm the exact install command from the [Hermes Agent docs](https://hermes.dev/) at the time you set this up. The pattern below is the expected shape; replace with the current command.

Expected (placeholder):

```bash
# Likely install pattern; verify with current docs
curl -fsSL https://hermes-agent.dev/install.sh | bash
# OR via npm
sudo npm install -g @hermes-agent/cli
```

Verify:

```bash
hermes --version
```

## Set the API key

```bash
echo 'export HERMES_API_KEY="..."' >> ~/.bashrc
source ~/.bashrc
```

## First run (one time, interactive)

```bash
hermes
```

Same reasoning as Claude Code: validates the key, caches any OAuth tokens for downstream services Hermes connects to. Same [headless OAuth dance](../02-claude-code/#the-headless-oauth-dance-the-gotcha) applies if Hermes integrates with services that use OAuth.

## Test headless invocation

```bash
# Confirm Hermes' equivalent of `claude -p`
echo "Summarize today's top AI news in 5 bullets" | hermes -p
```

## Use Hermes purely as a runner

Hermes ships with its own Kanban feature. We're deliberately ignoring it - we want Multica's vendor-neutral abstraction layer instead. Configure Hermes only as a runner that Multica delegates to.

If Hermes has tool/integration setup it needs for the use cases in the video (e.g., access to specific MCPs or APIs), configure those before moving on. Document any tool/integration setup as you go.

## Common issues

- **Auth conflicts with Claude Code** - they should be independent. Check token storage paths don't collide.
- **Rate limits** - Hermes' free tier has limits. Consider a paid plan if you'll run many parallel agents.
- **MCP sandboxing** - Hermes restricts MCP server processes more aggressively than Claude Code. OAuth-based MCPs (Notion, Gmail, Google Drive) often won't complete their flow inside Hermes. If you need Notion or similar, route those tasks to Claude Code instead, or use the GitHub gist pattern below for output.

## Recommended output pattern: GitHub gists

For agent outputs (research briefs, drafts, reports) the simplest universal pattern is a private GitHub gist:

```bash
echo "{markdown content}" | gh gist create --filename "research.md" --desc "Topic: ..."
```

This returns a URL the agent can hand back to Multica as the task result. Why this works for both runners:

- Both Hermes and Claude Code have `gh` CLI access
- No MCP dependency, so Hermes' sandbox doesn't block it
- Returns a clean URL for Multica's ticket
- Private by default, easy to share or revoke
- No repo clutter

If you need rich formatting or dashboards (Notion, Airtable), do the agent's work into a gist, then have a separate downstream step (a Multica scheduled job, or a webhook on PR merge) sync to the dashboard tool.

## Next

[04 - Install Multica](../04-multica/)

## Go Deeper

To go deeper on AI engineering, join my AI engineering community: [aiengineer.co](https://aiengineer.co).
