# nano-harness

This is the supporting material for the video: nano-harness.

A teaching-scale coding agent harness in a single Python file (~250 lines).

Claude Code, Codex, Cursor, and Pi are all elaborate versions of the same loop.
This file is that loop, stripped to the smallest version that still teaches the
real shape.

## Run it

```bash
echo "ANTHROPIC_API_KEY=sk-..." > .env
uv run nano-harness.py
```

`uv` reads the PEP 723 header at the top of the script, sets up an ephemeral
venv with `anthropic` and `python-dotenv`, and runs it. No `pip install`, no
`requirements.txt`.

## The core idea

> A coding agent = a model + a harness.
>
> The model decides what to do next.
> The harness actually does it, then feeds the result back.

That's it. Everything else is elaboration on those two sentences.

## Concepts

The file is organized into labeled sections (`── Section ──`). Read top to
bottom - each section is one concept.

### 1. System prompt

The single highest-leverage thing in the harness. Without it the model has no
identity, no environment, no idea what its tools mean. With 20 lines of
context - cwd, OS, tool guidance - behavior changes dramatically.

Real harnesses assemble this dynamically per turn: cwd, git status, open files,
project conventions (`CLAUDE.md`), recently edited files. nano-harness keeps it
static and minimal so you can see the *shape*.

### 2. Tools

Three tools: `bash`, `read_file`, `edit_file`.

Bash alone is Turing-complete - the model could do everything by composing
shell commands. But structured `read_file` (with line numbers) and `edit_file`
(exact-match replacement) give the model better signal and give the harness
something reviewable to show in the approval gate. Real harnesses add Grep,
Glob, Write, and dynamically-loaded MCP tools.

Tool definitions are JSON schemas. The model never executes them - the harness
does, in `run_tool()`. The model just *requests* a call.

### 3. Events (and hooks)

The harness emits events at lifecycle points (`model_text`, `pre_tool`,
`post_tool`, `turn_end`). Anything can subscribe: loggers, telemetry, UIs,
guardrails.

Hooks - callbacks that **gate** an action rather than just observe it - are
one consumer pattern on top of events. The convention here: a listener on a
`pre_*` event returning `False` cancels the action. That's how `approve()` is
implemented - it's an ordinary listener that happens to return a bool.

Why bother with events at this size? Two reasons:
- **Separation.** The loop doesn't know about your UI or logger. You can swap
  listeners to run the same loop under a CLI, a web UI, or a test harness.
- **It's the pattern real harnesses converge on.** Claude Code's hook system
  is this same idea, scaled up.

### 4. Spinner (not streaming)

We deliberately don't stream tokens. Claude Code uses the same trick: show a
spinner while the model thinks, then print the response in one go. Cleaner
terminal, no half-rendered output, no cursor jitter.

### 5. Prompt caching

A one-line change for ~90% cost reduction on multi-turn sessions.

`cache_control: {type: "ephemeral"}` marks a *boundary* in the request:
everything up to and including that marker is cached for ~5 minutes. nano-harness
marks two boundaries:

- the end of the system prompt
- the end of the tools array

From turn 2 onward, system + tools are served from cache. Real harnesses also
cache stable message prefixes (early turns, loaded files) for big wins on
long sessions.

### 6. The agent loop

The whole harness, in eight lines of control flow:

1. Ask the model what to do.
2. If it's done talking (`end_turn`), return.
3. For each tool call the model requested:
   - emit `pre_tool` (listeners may veto)
   - run the tool
   - emit `post_tool`
4. Send tool results back as a user message. Repeat.

That's the loop every coding agent runs. Everything else - context management,
sub-agents, streaming, permissions models - is layered around it.

### 7. REPL

`input()` in a loop, with persistent message history across turns so the agent
remembers what it just did. Ctrl-C to exit.

## What nano-harness deliberately doesn't do

Real coding harnesses add a lot around the same bones. The honest list:

- **Context management.** The message list grows unboundedly here. Real
  harnesses compact / summarize old turns when approaching the context window.
- **Permissions model.** y/n on every call is unusable past five minutes. Real
  harnesses have allow rules, deny rules, session approvals, sandboxing.
- **Sub-agents.** Spawning isolated child loops with their own context and
  tool subset (e.g. for "go explore this codebase" without polluting the main
  thread).
- **Streaming, retries, rate-limit handling, token accounting.**
- **Session persistence.** Resume where you left off.
- **Multi-provider abstraction.** Swap Anthropic / OpenAI / local models behind
  one interface.

The skeleton - loop, tools, events, system prompt, approval gate, caching - is
the real shape. The above are all things you *grow into*, not things you start
with.

## File layout

```
code/
├── nano-harness.py    # the whole thing
├── .env               # ANTHROPIC_API_KEY=...
├── .gitignore
└── README.md
```

## Go Deeper

To go deeper on AI engineering, join my AI engineering community: [aiengineer.co](https://aiengineer.co).
