# Harness Engineering: Building a Custom Pi Agent Workflow

Companion resources for the YouTube video.

This tutorial walks through what harness engineering is, builds a minimal
coding harness from scratch, and demonstrates a custom workflow built on top
of Pi that takes a GitHub issue and ships a pull request end-to-end.

## Layout

```
pi-agent-workflow/
├── README.md
├── docs/
│   └── harness-engineering-reference.md   Full technical reference (~6,500 words)
├── slides/
│   └── index.html                          Section 2 slide deck
└── code/
    └── minimal-harness.py                  ~50-line agent harness in Python
```

## The Pi extension (PBE)

The Pi extension demonstrated in the video - branch -> plan -> build -> eval ->
retry -> PR - lives in the Pi extensions repo:

-> https://github.com/owainlewis/pi-extensions (`extensions/pbe-harness`)

## Running the slides

Open `slides/index.html` directly in a browser, or serve it locally:

```bash
cd slides
python3 -m http.server 3030
```

Navigate with arrow keys or spacebar. Press `F` for fullscreen.

## Running the minimal harness

```bash
cd code
export ANTHROPIC_API_KEY=...
uv run minimal-harness.py
```

The default task asks the agent to look at files in the current directory and
describe what's there. Edit the `agent("...")` call in `__main__` to give it a
different goal.

## Reference doc

`docs/harness-engineering-reference.md` is the long-form companion to the
video. ~6,500 words covering:

- What an agent harness is, and how it differs from a framework
- The agent loop
- The six configuration surfaces (AGENTS.md, MCP, skills, sub-agents,
  hooks, back-pressure)
- Working backward from behavior - how each harness component earns its place
- Common failure modes
- A worked case study (the Pi extension)
- Running a harness in practice (session protocol, state, git, sprint contracts)

## Related tutorials

- [pi-coding-agent-guide](../pi-coding-agent-guide) - full guide to Pi as a
  coding agent.

## License

MIT.
