# AI Agent Memory Demo

This folder contains four small Python demos.

Each demo adds one memory idea.

The shared agent abstraction lives in `agent.py`.

Each script keeps the same shape:

```python
agent = Agent(memory=StaticFileMemory())
agent.run("How should I run Python commands here?")
```

## Setup

Use Python 3.11 or newer.

For real model calls, set an OpenAI API key:

```bash
export OPENAI_API_KEY="your-openai-api-key"
```

For a no-cost local smoke test, use fake-model mode:

```bash
export AI_MEMORY_DEMO_FAKE_MODEL=1
```

Fake-model mode only proves the memory plumbing.
Use a real API key for the actual lesson.

## Run

From this folder:

```bash
uv run 01_no_memory.py
uv run 02_static_memory.py
uv run 03_session_search.py
```

The Mem0 example needs a Mem0 API key and the optional dependency:

```bash
export MEM0_API_KEY="your-mem0-api-key"
uv run --extra mem0 04_mem0_memory.py
```

## Reset

The session-search demo writes `sessions.sqlite3`.

Reset it with:

```bash
uv run reset_demo.py
```

## Test

```bash
python3 -m unittest discover -s tests
python3 -m compileall .
```

## The Ladder

```text
01 no memory
02 static file memory
03 session search
04 external memory with Mem0
```
