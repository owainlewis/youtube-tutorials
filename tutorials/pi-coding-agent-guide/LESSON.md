# Pi Coding Agent (Full Course)

Companion repo for the video. Everything you need to go from zero to a fully configured Pi setup with custom extensions.

## What is Pi?

Pi is a minimal, open-source terminal coding agent by Mario Zechner (creator of libGDX). It ships with 4 tools (read, write, edit, bash), a system prompt under 1,000 tokens, and an extension system that lets you build everything else yourself.

- GitHub: https://github.com/badlogic/pi-mono
- Website: https://pi.dev

## What's in This Repo

```
00-pricing/             What it costs, which subscriptions work, which don't
01-getting-started/     Install, first run, basic commands, keyboard shortcuts
02-configuration/       Custom providers, system prompts, settings, templates
03-extensions/          Write your own tools and event handlers (4 working examples)
04-skills/              On-demand capability packages (code review skill included)
05-claude-code-migration/ Coming from Claude Code? Feature mapping + migration checklist
06-multi-provider/      Switch models mid-session, custom provider configs
07-advanced/            Print/JSON/RPC modes, SDK, config syncing, CLI flags
```

## Quick Start

```bash
# Install Pi
npm install -g @mariozechner/pi-coding-agent

# Set up a provider (pick one)
export ANTHROPIC_API_KEY=sk-ant-...   # API key (pay-as-you-go)
export OPENAI_API_KEY=sk-...
export GEMINI_API_KEY=...

# Or use a subscription (ChatGPT Plus, GitHub Copilot, Gemini CLI)
# Start Pi and run /login

# Run it
pi
```

Then clone this repo and copy the extensions you want:

```bash
git clone https://github.com/owainlewis/youtube-tutorials.git
cd youtube-tutorials/tutorials/pi-coding-agent-guide

# Copy extensions to your Pi config
cp 03-extensions/permission-gate.ts ~/.pi/agent/extensions/
cp 03-extensions/git-checkpoint.ts ~/.pi/agent/extensions/
cp 03-extensions/cost-tracker.ts ~/.pi/agent/extensions/

# Copy the multi-provider config
cp 06-multi-provider/models.json ~/.pi/agent/models.json

# Start Pi (extensions auto-load)
pi
```

## Pricing: The Short Version

Pi itself is free. You pay for the LLM.

| Provider | How it works in Pi |
|----------|-------------------|
| Anthropic Claude | API key or extra usage (both per token) |
| OpenAI ChatGPT | Subscription works for personal use |
| GitHub Copilot | Subscription works via OAuth |
| Google Gemini | Subscription works via OAuth |
| OpenRouter | API key (access all providers) |
| Ollama (local) | Free (your hardware) |

**Quick version:** Claude needs an API key. OpenAI works with your existing subscription. Switch models mid-session with `Ctrl+P`.

See [00-pricing/](./00-pricing/) for the full breakdown.

## Extensions Included

| Extension | What it does |
|-----------|-------------|
| [permission-gate.ts](./03-extensions/permission-gate.ts) | Block dangerous bash commands |
| [git-checkpoint.ts](./03-extensions/git-checkpoint.ts) | Auto-stash before each agent turn |
| [cost-tracker.ts](./03-extensions/cost-tracker.ts) | Track token spend + `/cost` command |
| [slash-command.ts](./03-extensions/slash-command.ts) | Custom `/review` and `/explain` commands |

## Coming from Claude Code?

See the [migration guide](./05-claude-code-migration/). Your CLAUDE.md files work as-is. Most features have equivalents. The main gaps are MCP (use extensions instead) and permission modes (use the permission-gate extension).

## Requirements

- Node.js >= 20.6.0
- At least one LLM provider API key or supported subscription

## Resources

- [Pi README](https://github.com/badlogic/pi-mono/tree/main/packages/coding-agent)
- [60+ example extensions](https://github.com/badlogic/pi-mono/tree/main/packages/coding-agent/examples/extensions)
- [Armin Ronacher's extensions](https://github.com/mitsuhiko/agent-stuff)
- [Armin's blog post on Pi](https://lucumr.pocoo.org/2026/1/31/pi/)
- [Blueprint Skills (SDLC)](https://github.com/owainlewis/blueprint)
