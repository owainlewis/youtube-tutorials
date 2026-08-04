# Optional Pi Extensions

Extensions are TypeScript modules that run inside Pi. They can register tools,
commands, event handlers, and user-interface elements.

Pi loads extension files from `~/.pi/agent/extensions/` or `.pi/extensions/`.
For a one-off test, pass a path with `--extension`:

```bash
cd /path/to/youtube-tutorials/tutorials/pi-coding-agent-guide
pi --extension resources/03-extensions/permission-gate.ts
```

## Examples

| File | What it demonstrates |
| --- | --- |
| [`permission-gate.ts`](./permission-gate.ts) | Inspect and block selected `bash` tool calls. |
| [`slash-command.ts`](./slash-command.ts) | Register `/review` and `/explain` commands. |

Every extension exports a factory:

```typescript
import type { ExtensionAPI } from "@earendil-works/pi-coding-agent";

export default function (pi: ExtensionAPI) {
  pi.on("session_start", async (_event, ctx) => {
    if (ctx.hasUI) ctx.ui.notify("Extension loaded", "info");
  });
}
```

The current event API uses `event.toolName` and `event.input` for tool-call
handlers. Use the upstream [extension reference](https://github.com/earendil-works/pi/blob/main/packages/coding-agent/docs/extensions.md)
when adding another event or tool.

## Security Boundary

Extensions run with the same operating system permissions as Pi. They can read
files, make network requests, and start processes. A permission-gate extension
can improve the interface, but regular expressions cannot recognise every
dangerous shell command. Use operating system isolation when enforcement matters.
