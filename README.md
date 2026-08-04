# YouTube Tutorials

Code and examples from my YouTube channel tutorials.

## Tutorials

Each tutorial uses the same public shape:

- `README.md` - what the tutorial is and where to start.
- `LESSON.md` - the main teaching document.
- `code/` - runnable code, sample apps, fixtures, or setup files.
- `resources/` - prompts, slides, configs, references, images, and other loose assets.

<!-- tutorial-catalog:start -->
31 published tutorials:

- [6 Types of RAG, Clearly Explained](./tutorials/6-types-of-rag/)
- [Agent Goals and Loops Explained Simply](./tutorials/agent-goals-and-loops/)
- [Claude Code Agent Teams](./tutorials/agent-teams/)
- [AI Agent Memory Explained Simply](./tutorials/ai-agent-memory/)
- [How I Review AI-Generated Code](./tutorials/ai-code-review/)
- [AI Git Workflow](./tutorials/ai-git-workflow/)
- [My Autonomous AI Coding Workflow](./tutorials/autonomous-ai-coding-workflow/)
- [Background Agent Workers: A Pull-Based Architecture](./tutorials/background-agents/)
- [Codex Scheduled Tasks: Bug Scan and Bug Fix](./tutorials/codex-automations/)
- [OpenAI Codex For Developers](./tutorials/codex-for-developers/)
- [7 Codex Skills I Use As An AI Engineer](./tutorials/codex-skills-i-use/)
- [Deploy AI Systems on Google Cloud With OpenAI Codex](./tutorials/deploy-ai-on-gcp/)
- [Docker Sandboxes for Developers](./tutorials/docker-sandboxes-for-developers/)
- [GitHub AI Workflow](./tutorials/github-ai-workflow/)
- [Herdr: The Agent Multiplexer AI Developers Need](./tutorials/herdr-agent-workflow/)
- [How I'd Learn Software Engineering (When AI Writes the Code)](./tutorials/how-id-learn-software-engineering/)
- [Intent-Based Query Routing for RAG](./tutorials/intent-based-classification/)
- [Linear as Your Agent's Control Plane](./tutorials/linear-workflow/)
- [Loop Engineering: A Practical Example](./tutorials/loop-engineering/)
- [Give Your AI Agents a Database (Airtable MCP)](./tutorials/mcp-airtable/)
- [Micro Agents Demo](./tutorials/micro-agents-demo/)
- [Micro Neo](./tutorials/micro-neo/)
- [Multica Turns Claude Code Into a Remote Teammate](./tutorials/multi-agent-teams/)
- [Nano Agent](./tutorials/nano-agent/)
- [Nested subagents in Claude Code: one agent, one concern](./tutorials/nested-subagents-claude-code/)
- [Harness Engineering: Building a Custom Pi Agent Workflow](./tutorials/pi-agent-workflow/)
- [Pi Coding Agent (Full Course)](./tutorials/pi-coding-agent-guide/)
- [PostgreSQL for RAG](./tutorials/postgresql-only-database-ai/)
- [Spec-Driven Development](./tutorials/spec-driven-development/)
- [Stop Vibe Coding - How to Build Software With AI Like a Senior Engineer](./tutorials/stop-vibe-coding/)
- [How I Test AI-Generated Code](./tutorials/testing-ai-generated-code/)
<!-- tutorial-catalog:end -->

## Tutorial Standard

Use [tutorials/TUTORIAL-STANDARD.md](./tutorials/TUTORIAL-STANDARD.md) when turning video material into consistent public lessons and code samples.

Use [tutorials/_templates](./tutorials/_templates/) for reusable lesson and slide templates.

Create a new tutorial with:

```bash
just new-tutorial my-topic "My Tutorial Title"
```

Run repository checks with:

```bash
just check
```

The root tutorial list is generated from
[`tutorials/catalog.json`](./tutorials/catalog.json). After changing catalog
metadata, update the list with:

```bash
just update-tutorial-catalog
```

## About

These tutorials demonstrate practical AI automation patterns. Each one is a complete, working example you can use and adapt.

## License

This repository is licensed under the [MIT License](./LICENSE).

## Go Deeper

To go deeper on AI engineering, join my AI engineering community: [aiengineer.co](https://aiengineer.co).
