# Getting Started with Pi

This is the supporting material for the video: Getting Started with Pi.

## Install

```bash
npm install -g @mariozechner/pi-coding-agent
```

## Authentication

Pi supports API keys and OAuth subscriptions.

### API Keys (pay per use)

Set environment variables for the providers you want:

```bash
# In your .zshrc or .bashrc
export ANTHROPIC_API_KEY=sk-ant-...
export OPENAI_API_KEY=sk-...
export GEMINI_API_KEY=...
```

### Subscriptions (use your existing plan)

Pi supports OAuth login for Claude Pro/Max, ChatGPT Plus/Pro, GitHub Copilot, and Gemini CLI. Start Pi and run:

```
/login
```

Select your provider and follow the browser flow.

## First Run

```bash
# Start interactive session
pi

# Start with a specific model
pi --model claude-sonnet-4-20250514

# One-shot mode (no interactive session)
pi -p "What files are in this directory?"
```

## Essential Commands

| Command | What it does |
|---------|-------------|
| `/help` | Show all commands |
| `/model` | Show current model |
| `/session` | Session info |
| `/tree` | Navigate session history (branch, fold, search) |
| `/fork` | Branch the conversation |
| `/compact` | Compress context to free up tokens |
| `/reload` | Hot-reload extensions, skills, themes |
| `/new` | Start a fresh session |
| `/login` | Authenticate with a subscription provider |

## Keyboard Shortcuts

| Shortcut | Action |
|----------|--------|
| Ctrl+P / Shift+Ctrl+P | Cycle through models |
| Shift+Tab | Cycle thinking level (off/low/medium/high/xhigh) |
| Shift+Enter | Multi-line input |
| Ctrl+V | Paste image |
| `!command` | Run bash command, pipe output to model |
| `@` | Fuzzy file reference |
| Escape | Abort current generation |
| Enter (while agent works) | Queue a steering message |
| Alt+Enter (while agent works) | Queue a follow-up message |

## Context Files

Pi loads context files automatically, just like Claude Code loads CLAUDE.md:

```
~/.pi/agent/AGENTS.md     # Global context (loaded everywhere)
./AGENTS.md                # Project context (loaded in this directory)
./.pi/AGENTS.md            # Alternative project context location
```

Pi also reads `CLAUDE.md` if no `AGENTS.md` exists. So if you already have Claude Code set up, Pi picks up your existing instructions.

## Directory Structure

Pi stores everything under `~/.pi/agent/`:

```
~/.pi/agent/
├── extensions/     # Global extensions (auto-loaded)
├── skills/         # Global skills
├── prompts/        # Prompt templates
├── themes/         # Custom themes
├── sessions/       # Session history (JSONL)
├── models.json     # Custom provider config
├── settings.json   # Settings
└── SYSTEM.md       # Custom system prompt
```

## Go Deeper

To go deeper on AI engineering, join my AI engineering community: [aiengineer.co](https://aiengineer.co).
