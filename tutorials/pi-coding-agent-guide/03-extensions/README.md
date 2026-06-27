# Writing Pi Extensions

This is the supporting material for the video: Writing Pi Extensions.

Extensions are TypeScript files that extend Pi's behavior. No build step required. Drop a `.ts` file in `~/.pi/agent/extensions/` and it auto-loads.

## How Extensions Work

Every extension exports a default function that receives the `ExtensionAPI`:

```typescript
import type { ExtensionAPI } from "@mariozechner/pi-coding-agent";

export default function (pi: ExtensionAPI) {
  // Register tools, commands, events, shortcuts here
}
```

Pi discovers extensions from:
- `~/.pi/agent/extensions/*.ts` (global)
- `.pi/extensions/*.ts` (project-local)
- Subdirectories with `index.ts`
- Paths listed in `settings.json`
- CLI flag: `pi -e ./my-extension.ts`

Hot-reload with `/reload`. No restart needed.

## Extension Examples in This Repo

| File | What it does | Complexity |
|------|-------------|------------|
| [permission-gate.ts](./permission-gate.ts) | Block dangerous bash commands | Beginner |
| [git-checkpoint.ts](./git-checkpoint.ts) | Auto-stash before each agent turn | Beginner |
| [cost-tracker.ts](./cost-tracker.ts) | Track token spend per session | Intermediate |
| [slash-command.ts](./slash-command.ts) | Register a custom slash command | Beginner |

## The Extension API

### Register a Tool

Tools are functions the LLM can call:

```typescript
import { Type } from "@mariozechner/pi-ai";
import { defineTool, type ExtensionAPI } from "@mariozechner/pi-coding-agent";

const myTool = defineTool({
  name: "search_docs",
  label: "Search Docs",
  description: "Search project documentation",
  parameters: Type.Object({
    query: Type.String({ description: "Search query" }),
  }),
  async execute(toolCallId, params, signal, onUpdate, ctx) {
    // Do the work
    const results = `Found results for: ${params.query}`;
    return {
      content: [{ type: "text", text: results }],
      details: { query: params.query },
    };
  },
});

export default function (pi: ExtensionAPI) {
  pi.registerTool(myTool);
}
```

### Register a Command

Commands are slash commands the user invokes:

```typescript
export default function (pi: ExtensionAPI) {
  pi.registerCommand("stats", {
    description: "Show session statistics",
    handler: async (args, ctx) => {
      const usage = ctx.getContextUsage();
      ctx.ui.notify(`Tokens used: ${usage}`, "info");
    },
  });
}
```

### Listen to Events

React to anything that happens in the agent lifecycle:

```typescript
export default function (pi: ExtensionAPI) {
  // Run code when a session starts
  pi.on("session_start", async (event, ctx) => {
    ctx.ui.notify("Session started", "info");
  });

  // Intercept tool calls (can block or modify them)
  pi.on("tool_call", async (event, ctx) => {
    if (event.tool === "bash" && event.input.command.includes("rm -rf")) {
      return { block: true, reason: "Blocked dangerous command" };
    }
  });

  // React to tool results
  pi.on("tool_result", async (event, ctx) => {
    // Log, modify, or react to results
  });

  // Modify messages before they hit the LLM
  pi.on("context", async (event, ctx) => {
    return { messages: event.messages };
  });

  // Modify the system prompt
  pi.on("before_agent_start", async (event, ctx) => {
    return {
      systemPrompt: event.systemPrompt + "\nAlways be concise.",
    };
  });
}
```

### Key Events

| Event | When it fires | Can modify? |
|-------|--------------|-------------|
| `session_start` | Session begins or reloads | No |
| `before_agent_start` | Before LLM call | System prompt |
| `tool_call` | Before a tool executes | Block or mutate input |
| `tool_result` | After a tool returns | Modify result |
| `context` | Before messages sent to LLM | Filter/modify messages |
| `turn_start` / `turn_end` | Agent turn boundaries | No |
| `input` | User submits text | Transform input |
| `session_shutdown` | Session ending | No |

### UI Interactions

Extensions can interact with the user:

```typescript
pi.on("session_start", async (event, ctx) => {
  // Ask a yes/no question
  const confirmed = await ctx.ui.confirm("Enable strict mode?");

  // Show a selection menu
  const choice = await ctx.ui.select("Pick a framework:", [
    { label: "React", value: "react" },
    { label: "Vue", value: "vue" },
  ]);

  // Show a notification
  ctx.ui.notify("Extension loaded", "info");

  // Set a persistent status line
  ctx.ui.setStatus("my-ext", "Active");
});
```

## Gotchas

1. **Don't call action methods at the top level.** `pi.sendMessage()`, `pi.getActiveTools()`, etc. only work inside event handlers, not in the factory function body.

2. **Always check `ctx.hasUI`** before calling `ctx.ui.select()` etc. In print/RPC mode, UI calls silently return undefined.

3. **Throw errors, don't return them.** The framework catches thrown errors and reports them to the LLM properly.

4. **State is lost on `/reload`.** Use `pi.appendEntry()` to persist state across reloads.

5. **Extensions run with full system access.** There is no sandbox. Only install extensions you trust.

## Go Deeper

To go deeper on AI engineering, join my AI engineering community: [aiengineer.co](https://aiengineer.co).
