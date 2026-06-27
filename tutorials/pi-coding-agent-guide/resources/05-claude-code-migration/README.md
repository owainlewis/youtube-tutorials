# Coming from Claude Code?

This is the supporting material for the video: Coming from Claude Code?.

If you're a Claude Code user, this is the guide you want. Pi does things differently, but most of what you rely on has an equivalent.

## Feature Mapping

| Claude Code | Pi Equivalent | Notes |
|---|---|---|
| CLAUDE.md | AGENTS.md (or CLAUDE.md) | Pi reads both. Same concept, same behavior. |
| Permission modes | None by default | Use the [permission-gate extension](../03-extensions/permission-gate.ts) |
| MCP servers | No built-in MCP | Use extensions or the community [pi-mcp-adapter](https://github.com/nicobailon/pi-mcp-adapter) |
| /compact | /compact | Same |
| Sub-agents | None by default | Build via extension. Pi has an [example](https://github.com/badlogic/pi-mono/tree/main/packages/coding-agent/examples/extensions/subagent) |
| Plan mode | None by default | Build via extension. Pi has an [example](https://github.com/badlogic/pi-mono/tree/main/packages/coding-agent/examples/extensions/plan-mode) |
| Hooks (pre/post commands) | `pi.on("tool_call", ...)` | Extensions are more flexible than hooks |
| TodoWrite / task tracking | File-based | Create a TODO.md. The agent reads and updates it. |
| Model selection | Ctrl+P | Cycle through configured models mid-session |
| Thinking budget | Shift+Tab | Cycle: off/low/medium/high/xhigh |
| Session resume | /continue or start Pi | Same concept. Sessions persist as JSONL. |
| `!command` | `!command` | Same. Runs bash and pipes output to context. |
| `@file` | `@file` | Same. Fuzzy file reference. |
| Image paste | Ctrl+V | Same. |

## What You Gain

**More context window.** Claude Code's system prompt is ~14K tokens. Pi's is under 1K. That's 13K more tokens for your actual work.

**Provider freedom.** Switch between Claude, GPT, Gemini, Groq, and 15+ others mid-session. Use the best model for each task.

**Full control.** Extensions can intercept and modify everything: tool calls, system prompts, messages before they hit the LLM, even the compaction algorithm.

**Open source.** MIT licensed. Read the source. Fork it. Understand exactly what your agent does.

## What You Lose

**Out-of-the-box polish.** Claude Code works great immediately. Pi requires setup.

**Safety rails.** No permission system by default. You need to add your own if you want one.

**MCP support.** No built-in MCP protocol. You use extensions instead, or the community adapter.

**Anthropic-specific features.** Things like Claude Code's tight integration with claude.ai, usage dashboard, and managed billing.

## Migration Checklist

1. Install Pi: `npm install -g @mariozechner/pi-coding-agent`
2. Set your API key: `export ANTHROPIC_API_KEY=sk-ant-...`
3. Copy your CLAUDE.md files. Pi reads them as-is.
4. Install the [permission-gate extension](../03-extensions/permission-gate.ts) if you want safety prompts
5. Configure additional providers in [models.json](../02-configuration/models.json) if you want multi-provider support
6. Try it on a real project. Run `pi` in your project directory.

## Tips for Claude Code Users

- **Don't fight the minimalism.** Pi intentionally leaves things out. If you miss a feature, check the [60+ example extensions](https://github.com/badlogic/pi-mono/tree/main/packages/coding-agent/examples/extensions) before building your own.
- **Use both tools.** Pi and Claude Code are not mutually exclusive. Use Claude Code for quick tasks where you want zero setup. Use Pi when you want control.
- **Start with the defaults.** Pi works fine with just an API key and no extensions. Add complexity only when you need it.

## Go Deeper

To go deeper on AI engineering, join my AI engineering community: [aiengineer.co](https://aiengineer.co).
