# Micro Agent Specification

**Version**: 1.0.0
**License**: [MIT](../../../../LICENSE)

---

## Minimum Shape

A Micro Agent is a folder with two things:

1. **AGENTS.md:** Instructions for the agent
2. **tools/:** Scripts it can run

```
my-agent/
├── AGENTS.md     # "You are X. You can use these tools..."
└── tools/        # Any executable
```

Point a terminal agent at the folder. Done.

The pattern does not require an agent framework or a separate orchestration service. The Markdown defines the local instructions. The scripts provide the capabilities. Each script may still need its own configuration and dependencies.

---

## Any Executable Is a Tool

This is the core idea. If it runs from a terminal, it's a tool.

### Python

```bash
python tools/analyze.py --input data.csv
```

### Bash

```bash
bash tools/deploy.sh production
```

### Node

```bash
node tools/scrape.js https://example.com
```

### Go, Rust, Any Binary

```bash
./tools/crawler --url https://example.com --depth 3
```

### Docker

```bash
docker run --rm -v $(pwd):/data myimage:latest /data/input.csv
```

### Existing CLIs You Already Have

```bash
ffmpeg -i input.mp4 -vf scale=1280:720 output.mp4
```

```bash
yt-dlp --extract-audio "https://youtube.com/watch?v=xxx"
```

```bash
curl -s "https://api.example.com/data" | jq '.items'
```

```bash
rg "TODO" --type py
```

```bash
gh issue list --repo owner/repo --json title,url
```

### The Pattern

If it:
- Accepts arguments
- Outputs to stdout
- Returns an exit code

It's a tool. No wrappers. No schemas. No function registration. Just executables.

Existing command-line tools can use the same interface when the terminal agent is allowed to run them.

---

## Why This Works

**Reviewable instructions.** The important local instructions live in a file that a developer can inspect and change.

**Loose coupling.** The files are not tied to one model API, but each terminal agent may interpret instructions and permissions differently.

**Inspect the boundary.** Instruction problems can be reviewed in Markdown. Tool failures still need normal logs, errors, and debugging.

**Durable workspace.** Files written to the workspace remain available between agent sessions unless another process changes them.

---

## Full Structure

The minimum is `AGENTS.md` + `tools/`. For real work, add context and workspace:

```
agent-name/
├── AGENTS.md          # Required: Identity and instructions
├── tools/            # Required: Executables
├── context/          # Optional: SOPs, guides, templates
├── workspace/        # Optional: Agent's working files
└── .env.example      # Optional: Credentials template
```

| Directory | Purpose | Agent Access |
|-----------|---------|--------------|
| `tools/` | Scripts and executables | Run |
| `context/` | Reference docs, SOPs | Read |
| `workspace/` | Files the agent creates | Read/Write |

---

## AGENTS.md Format

Plain markdown. Follows [AGENTS.md](https://agents.md) conventions.

```markdown
# Agent Name

You are a [role]. You help [do what].

You can use the following tools:

## Tools

### tool_name

What it does.

    command --with args

## Workspace

Save files to `workspace/`:

- `workspace/output/`: Generated files
- `workspace/data/`: Downloaded data

## Workflows

### Task Name

1. Read `context/guide.md`
2. Run `tool_name`
3. Save to `workspace/`

## Environment

    export API_KEY=your_key
```

---

## Tool Conventions

Tools don't need to follow any protocol. But good tools:

- Accept `--help` for self-documentation
- Output JSON with `--json` flag when useful
- Write errors to stderr
- Return non-zero on failure

That's it. No schemas. No registration. Just good CLI hygiene.

---

## Compatible Agents

Any terminal agent that reads files and runs commands:

- [Claude Code](https://docs.anthropic.com/en/docs/claude-code)
- [Goose](https://github.com/block/goose)
- [Codex CLI](https://github.com/openai/codex)
- [Aider](https://aider.chat)
- [OpenCode](https://opencode.ai)

Or any chat with code execution. The folder is portable.

---

## Example: YouTube Agent

```markdown
# YouTube Agent

You are a YouTube research agent. You analyze channels and write scripts.

You can use the following tools:

## Tools

### search_videos

Search YouTube.

    .venv/bin/python tools/youtube.py search_videos "QUERY" --max 25 --json

### get_channel_videos

Get channel videos with outlier analysis.

    .venv/bin/python tools/youtube.py get_channel_videos @HANDLE --days 30 --json

### get_transcript

Get video transcript.

    .venv/bin/python tools/youtube.py get_transcript VIDEO_ID

### download_audio

Download audio from a video.

    yt-dlp -x --audio-format mp3 "https://youtube.com/watch?v=VIDEO_ID"

## Workspace

- `workspace/projects/`: Video projects
- `workspace/research/`: Analysis
- `workspace/transcripts/`: Transcripts

## Workflows

### Research a Topic

1. Search with `search_videos`
2. Find outliers with `get_channel_videos`
3. Get transcripts of top performers
4. Save to `workspace/research/`

### Write a Script

1. Read `context/script-guide.md`
2. Write to `workspace/projects/<n>/script.md`

## Environment

    export YOUTUBE_API_KEY=your_key
```

---

## The Tradeoffs

**Manual overhead.** You trigger the agent. You review output. Not fully autonomous.

**Latency.** Read-plan-act is slower than stream-of-consciousness.

For personal use, these are features. You stay in the loop. The overhead is control.

---

## Summary

Two files minimum:

- **AGENTS.md**: Who the agent is and what tools it has
- **tools/**: Executable commands the terminal agent may run

The pattern can be adapted to terminal agents that can read the instructions and run the declared commands. Compatibility and permission behavior still depend on the agent.

The value is a small, inspectable interface between instructions and tools.
