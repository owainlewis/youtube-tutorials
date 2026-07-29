# Micro Neo

Micro Neo is a minimal coding agent written in one Go file. It uses OpenRouter,
three tools, a serial agent loop, and a small event-driven terminal interface.

## Start Here

- Read the lesson: [LESSON.md](./LESSON.md)
- Run the agent: [code/](./code/)
- Follow the live-build prompts: [resources/prompts.md](./resources/prompts.md)
- Browse slides: [resources/slides/](./resources/slides/)

## Quick Start

```bash
cd code
export OPENROUTER_API_KEY="your-key"
go run main.go --workspace testdata/demo
```

Then enter a task at the prompt:

```text
› Find and fix the failing test. Run the tests when you are done.
```

The lesson includes model selection, tests, security limits, and the exact demo
reset command.

## Go Deeper

To go deeper on AI engineering, join my AI engineering community: [aiengineer.co](https://aiengineer.co).
