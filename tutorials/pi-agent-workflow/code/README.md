# nano-harness

This is the supporting material for the video: nano-harness.

A teaching-scale coding agent harness in a single Python file (about 300 lines).

Claude Code, Codex, Cursor, and Pi are all elaborate versions of the same loop.
This file is that loop, stripped to the smallest version that still teaches the
real shape.

## Run it

```bash
cp .env.example .env
# Edit .env and replace the placeholder API key.
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

The system prompt gives the model an identity, environment, and tool guidance.
Add focused context such as the working directory, operating system, and tool
rules so it can make grounded decisions.

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

`cache_control: {type: "ephemeral"}` marks a *boundary* in the request.
Stable content up to that boundary can be reused according to the provider's
cache policy. nano-harness marks two boundaries:

- the end of the system prompt
- the end of the tools array

Later turns may reuse the system prompt and tool definitions. Real harnesses
can also cache stable message prefixes. Measure the result for the provider,
model, and request shape you use.

### 6. The agent loop

The whole harness can be described in eight steps:

1. Send the current messages to the model.
2. Store the assistant response.
3. Display any text blocks.
4. Return when the model reports `end_turn`.
5. Inspect each requested tool call.
6. Ask pre-tool listeners whether it is allowed.
7. Run the tool and record its result.
8. Add all tool results to the messages and repeat.

That's the loop every coding agent runs. Everything else - context management,
sub-agents, streaming, permissions models - is layered around it.

### 7. REPL

`input()` in a loop, with persistent message history across turns so the agent
remembers what it just did. Ctrl-C to exit.

## What nano-harness deliberately doesn't do

Real coding harnesses add a lot around the same bones. The honest list:

- **Context management.** The message list grows unboundedly here. Real
  harnesses compact / summarize old turns when approaching the context window.
- **Permissions model.** Repeated y/n approval quickly becomes noisy. Real
  harnesses have allow rules, deny rules, session approvals, and sandboxing.
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
├── .env.example       # configuration template
├── .gitignore
├── tests/
└── README.md
```

## Test it offline

The tests replace the model SDK with local stubs. They do not use an API key or
make a network request.

```bash
python3 -m unittest discover -s tests -v
```

## Go Deeper

To go deeper on AI engineering, join my AI engineering community: [aiengineer.co](https://aiengineer.co).
