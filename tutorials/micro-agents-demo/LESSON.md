# Micro Agents Demo

A YouTube research agent built with the [Micro Agent](resources/docs/spec.md) pattern.

## What is a Micro Agent?

Two files. That's it.

```
my-agent/
├── AGENTS.md     # Instructions for the agent
└── tools/        # Scripts it can run
```

No framework. No dependencies. Just files an LLM can read and execute.

## This Demo

This repo contains a working YouTube research agent that can:

- Search YouTube for videos on any topic
- Analyze channels to find outlier content (2+ std devs above average)
- Download transcripts for study
- Help write scripts and titles
- Upload videos (with OAuth)

## Quick Start

1. **Set up environment**

```bash
cd code
cp .env.example .env
# Add your YOUTUBE_API_KEY
```

2. **Install dependencies**

```bash
uv sync
```

3. **Point your agent at the folder**

Open this folder in Claude Code, Goose, or any terminal agent:

```
Read resources/AGENTS.md and help me research AI agent videos.
```

The agent reads the instructions, discovers the tools, and gets to work.

## Structure

```
micro-agents-demo/
├── resources/
│   ├── AGENTS.md             # Agent identity and instructions
│   ├── context/              # Script, title, and metadata guidance
│   └── docs/
│       └── spec.md           # The micro agent specification
├── code/
│   ├── .env.example          # Credentials template
│   ├── pyproject.toml        # Python project
│   ├── workspace/            # Projects, research, transcripts
│   └── tools/
│       └── youtube.py        # YouTube API wrapper
```

## Tools

### search_videos

```bash
cd code
uv run tools/youtube.py search_videos "AI agents" --max 10 --json
```

### get_channel_videos

```bash
cd code
uv run tools/youtube.py get_channel_videos @daveebbelaar --days 365 --json
```

### get_transcript

```bash
cd code
uv run tools/youtube.py get_transcript VIDEO_ID
```

### upload

```bash
cd code
uv run tools/youtube.py upload video.mp4 --metadata metadata.md
```

## The Pattern

Read [resources/docs/spec.md](resources/docs/spec.md) for the full micro agent specification.

The key insight: if it runs from a terminal, it's a tool. No wrappers. No schemas. 50 years of Unix tools work out of the box.

## License

Licensed under the [MIT License](../../LICENSE).
