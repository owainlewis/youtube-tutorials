# YouTube Agent

A micro-agent for YouTube research and publishing. Works with Claude Code, Cursor, Goose, and any AI coding assistant that reads markdown.

## What This Is

A portable folder with CLI tools that any AI can use to:
- Analyze YouTube channels and find outlier videos
- Search for top-performing content
- Extract video transcripts
- Upload videos with metadata

No platform lock-in. No deployment. Just scripts + AGENTS.md.

## Quick Start

```bash
# Install dependencies
uv sync

# Set your API key
export YOUTUBE_API_KEY=your_api_key

# Test it
uv run scripts/youtube.py search_videos "AI agents" --max 5
```

## Usage

### With AI Assistants

Drop this folder into your project. The AI reads `AGENTS.md` and discovers the available tools automatically.

```
User: "Find the top performing videos about AI agents"
AI: [reads AGENTS.md, runs search_videos, returns analysis]
```

### Standalone

```bash
# Analyze a channel
uv run scripts/youtube.py get_channel_videos @mkbhd --days 30

# Search videos
uv run scripts/youtube.py search_videos "Claude AI tutorial" --order view_count

# Get transcript
uv run scripts/youtube.py get_transcript dQw4w9WgXcQ
```

## The Micro-Agent Pattern

This project demonstrates the micro-agent pattern:

1. **AGENTS.md** - Describes tools for AI agents (not humans)
2. **scripts/** - CLI tools with `--json` output
3. **docs/** - Templates and guides

The AI handles reasoning. The scripts handle execution. AGENTS.md bridges the gap.

See `docs/MICRO_AGENT_GUIDE.md` for the full pattern explanation.

## Requirements

- Python 3.12+
- [uv](https://docs.astral.sh/uv/) package manager
- YouTube Data API key ([get one here](https://console.cloud.google.com/apis/credentials))

## Files

| File | Purpose |
|------|---------|
| `AGENTS.md` | Tool manifest for AI agents |
| `scripts/youtube.py` | Main CLI tool |
| `docs/description_template.md` | Video description template |
| `docs/description_guide.md` | Best practices for descriptions |
| `docs/MICRO_AGENT_GUIDE.md` | Explains the micro-agent pattern |

## License

MIT
