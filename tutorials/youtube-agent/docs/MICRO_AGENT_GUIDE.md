# Micro-Agent Pattern Guide

A micro-agent is a portable folder that any AI coding assistant can use. No platform, no deployment, no Docker.

## Philosophy

Traditional AI agent frameworks require:
- Platform lock-in (OpenAI Assistants, LangChain, etc.)
- Complex deployment
- Custom SDKs and protocols

Micro-agents require:
- A folder with scripts
- An AGENTS.md manifest
- That's it

## The Key Insight

**Separate the thinking from the doing.**

- AI handles reasoning, planning, and orchestration
- Scripts handle deterministic execution
- AGENTS.md bridges the gap by describing what's available

## Anatomy of a Micro-Agent

```
your-agent/
├── AGENTS.md              # Tool manifest for AI agents
├── scripts/               # CLI tools with JSON output
│   └── tool.py
├── docs/                  # Templates, guides, examples
│   └── template.yaml
├── .env                   # Secrets (gitignored)
└── README.md              # Human documentation
```

## AGENTS.md vs README.md

| README.md | AGENTS.md |
|-----------|-----------|
| For humans | For AI agents |
| Explains what/why | Explains how to use |
| Conceptual overview | Executable commands |
| Installation steps | Tool discovery |

## Design Principles

### 1. JSON Output
Always support `--json` for programmatic processing:
```bash
uv run script.py command --json
```

### 2. Standalone Execution
Scripts must work without AI:
```bash
# Should work fine
uv run script.py command arg1 arg2
```

### 3. Clear Error Messages
Return structured errors:
```json
{"error": "Channel not found: @nonexistent"}
```

### 4. Minimal Secrets
Use environment variables, not config files:
```bash
export MY_API_KEY=xxx
```

## The agents.md Standard

This pattern follows the [agents.md](https://agents.md) open standard backed by the [Agentic AI Foundation](https://aaif.io/).

The standard defines how AI agents discover and use tools through a simple markdown manifest.

## Example Workflow

1. User asks agent to "analyze top performing videos"
2. Agent reads AGENTS.md, discovers `get_channel_videos` command
3. Agent runs: `uv run youtube.py get_channel_videos @handle --json`
4. Agent parses JSON response
5. Agent reasons about the data and responds to user

## Compatibility

Tested with:
- Claude Code
- Cursor
- Goose
- Aider
- Windsurf
- Any agent that reads markdown

## Building Your Own

1. Create a `scripts/` folder with your CLI tool
2. Add `--json` output support
3. Write an AGENTS.md describing your commands
4. Add any templates to `docs/`
5. Done. Any AI can now use your tool.
