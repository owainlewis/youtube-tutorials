# Advanced Usage

This is the supporting material for the video: Advanced Usage.

Power-user features for when you're past the basics.

## Modes

Pi runs in four modes beyond the interactive terminal.

### Print Mode (one-shot)

Run Pi as a single command. Great for scripts:

```bash
# Simple question
pi -p "What files are in this directory?"

# Pipe input
cat error.log | pi -p "What's wrong here?"

# Use in a shell script
SUMMARY=$(pi -p "Summarize the changes in the last 5 commits")
```

### JSON Mode (structured output)

Outputs all agent events as JSON lines. Useful for building your own tools:

```bash
pi --mode json "Fix the bug in auth.ts"
```

Events include: `agent_start`, `turn_start`, `message_start`, `message_update`, `message_end`, `tool_call`, `tool_result`, `turn_end`, `agent_end`.

### RPC Mode (remote control)

Control Pi from another process via stdin/stdout using JSON-RPC:

```bash
pi --mode rpc --no-session
```

Send prompts and abort messages via stdin. Receive all events via stdout. This is how you'd build a custom IDE integration or chat client.

### SDK (embed in your apps)

Use Pi as a library in your own TypeScript applications:

```typescript
import { createAgentSession, SessionManager, ModelRegistry } from "@mariozechner/pi-coding-agent";

const session = await createAgentSession({
  model: "claude-sonnet-4-20250514",
  systemPrompt: "You are a helpful assistant.",
  tools: ["read", "write", "edit", "bash"],
});

await session.send("Fix the failing tests");
```

This is how OpenClaw was built. The entire OpenClaw ecosystem runs on Pi's SDK.

## Config Syncing Across Machines

If you work on multiple machines, sync your Pi config via cloud storage:

```json
// settings.json
{
  "extensionPaths": ["~/Dropbox/pi-config/extensions"],
  "skillPaths": ["~/Dropbox/pi-config/skills"],
  "themePaths": ["~/Dropbox/pi-config/themes"]
}
```

Or use a Git repo:

```bash
# Set up once
cd ~/.pi/agent
git init
git remote add origin git@github.com:you/pi-config.git

# Sync
git pull  # on new machine
git push  # after changes
```

## Ephemeral Sessions

Run Pi without saving the session:

```bash
pi --no-session
```

Useful for quick questions or when working with sensitive data.

## Custom CLI Flags from Extensions

Extensions can register their own CLI flags:

```typescript
pi.registerFlag("strict", {
  type: "boolean",
  default: false,
  description: "Enable strict review mode"
});
```

Then use them: `pi --strict`

## Self-Awareness

Pi's system prompt includes information about its own architecture. If you ask Pi about its own capabilities, it reads its source from `node_modules` to give grounded answers. This is why Pi can write its own extensions. It has access to its own documentation and source code.

## Go Deeper

To go deeper on AI engineering, join my AI engineering community: [aiengineer.co](https://aiengineer.co).
