# Architecture

## Overview
Nano Agent follows an **event-driven agent loop** pattern: read user input, send to LLM with tools, emit lifecycle events, execute approved tool calls, return results, repeat. The system is a single-process CLI application with no server, no database, and no background workers (per FR-01, FR-02, FR-19).

The agent loop is deliberately kept pure - it contains **zero** UI, approval, or logging logic. All side effects are handled by **event listeners** registered on an event bus (FR-14-18). This keeps the core loop clean and makes behaviors like approval, rendering, and logging pluggable without modifying the agent.

The architecture separates the agent loop from the LLM provider and tool implementations behind simple interfaces, enabling future provider extensibility (FR-20) without touching core logic.

The agent supports **sub-agent spawning** (FR-11-13): the parent agent can delegate subtasks to independent child agents that each run their own agent loop with their own event bus. Multiple sub-agents run concurrently via `asyncio.gather()`. The entire agent loop is async to support this.

## System Design

```
┌─────────────────────────────────────────────────┐
│                    CLI (main.py)                 │
│         asyncio.run(), REPL input loop           │
└─────────────────┬───────────────────────────────┘
                  │ registers listeners, calls agent.run()
                  ▼
┌─────────────────────────────────────────────────┐
│              Agent Loop (agent.py)               │
│  conversation history, tool dispatch             │
│  emits events ── no UI, no approval logic        │
└──┬──────────┬───────────────────┬───────────────┘
   │          │                   │
   │    ┌─────▼──────────┐  ┌────▼────────────────┐
   │    │  Event Bus       │  │  Tools              │
   │    │  (events.py)     │  │  (tools/)           │
   │    │                  │  │  read_file           │
   │    │  PreToolUse      │  │  write_file          │
   │    │  PostToolUse     │  │  find_files          │
   │    │  Stop            │  │  list_directory      │
   │    │  SubagentStart   │  │  run_bash            │
   │    │  SubagentStop    │  │  spawn_agent ──┐    │
   │    └───────┬──────────┘  └───────────────┼────┘
   │            │                             │
   │    ┌───────▼──────────────────┐  ┌───────▼───────────┐
   │    │  Listeners               │  │  Sub-Agent(s)      │
   │    │                          │  │  (async, parallel)  │
   │    │  UIListener (ui.py)      │  │  own history,      │
   │    │  ApprovalListener        │  │  own listeners      │
   │    │  [LoggingListener, ...]  │  └───────────────────┘
   │    └──────────────────────────┘
   ▼
┌───────────────────┐
│  Provider          │
│  (providers/)      │
│  AnthropicProvider │
└───────────────────┘
```

## Components
<components>

### CLI (`main.py`)
- **Purpose**: Entry point. Wires up the agent with listeners and runs the REPL.
- **Responsibilities**:
  - Parse CLI arguments (model selection, etc.)
  - Create the `Agent` instance and register event listeners (UI, approval, etc.)
  - Run the async REPL input loop via `asyncio.run()`
  - Handle Ctrl+C / EOF for clean exit
- **Interface**: Creates `Agent`, registers listeners, calls `await agent.run(user_input)` in a loop
- **Requirements satisfied**: FR-01, FR-02, NFR-05

### Agent (`agent.py`)
- **Purpose**: Core agent loop. Manages conversation history, tool dispatch, and event emission. Contains **zero** UI or approval logic.
- **Responsibilities**:
  - Maintain conversation history (list of messages) in memory
  - Send messages to the provider and process the response
  - Detect tool_use blocks in responses and dispatch to the correct tool
  - **Emit lifecycle events** at each stage (`PreToolUse`, `PostToolUse`, `Stop`, `SubagentStart`, `SubagentStop`)
  - For `PreToolUse` events: await the listener response to determine approve/deny
  - Feed tool results back to the provider for continued reasoning
  - Loop until the model produces a final text response (no more tool calls)
  - Spawn sub-agents when the `spawn_agent` tool is called
- **Interface**: `async Agent.run(user_input) -> str` (final text response). Side effects happen via events.
- **Requirements satisfied**: FR-03, FR-04, FR-11, FR-12, FR-13, FR-14

### Event Bus (`events.py`)
- **Purpose**: Simple event system that the agent emits to and listeners subscribe to.
- **Responsibilities**:
  - Define event types as dataclasses: `PreToolUse`, `PostToolUse`, `Stop`, `SubagentStart`, `SubagentStop`
  - `PreToolUse` is special: it is an **approval gate** - the listener returns `True` (approve) or `False` (deny)
  - Maintain a list of registered listeners per event type
  - Dispatch events to listeners in registration order
- **Interface**:
  - `event_bus.on(event_type, async_callback)` - register a listener
  - `await event_bus.emit(event)` - emit an event to all registered listeners
  - `await event_bus.emit_approval(pre_tool_use_event) -> bool` - emit and collect approve/deny
- **Requirements satisfied**: FR-14, FR-15, FR-16

### Provider Interface (`providers/base.py`)
- **Purpose**: Abstract interface for LLM providers.
- **Responsibilities**:
  - Define the contract: `async send(messages, tools, system_prompt) -> ProviderResponse`
  - `ProviderResponse` contains: thinking text, content blocks (text or tool_use)
- **Interface**: Abstract base class with a single `send` method
- **Requirements satisfied**: FR-18

### Anthropic Provider (`providers/anthropic.py`)
- **Purpose**: Anthropic API implementation of the provider interface.
- **Responsibilities**:
  - Construct API requests with extended thinking enabled
  - Map Anthropic response format to `ProviderResponse`
  - Handle API errors (rate limits, auth failures, network errors)
- **Interface**: Implements `async Provider.send()` using `AsyncAnthropic` client
- **Requirements satisfied**: FR-04, FR-05, FR-18, NFR-04

### Tools (`tools/`)
- **Purpose**: Individual tool implementations that the agent can invoke.
- **Responsibilities**:
  - Each tool is a function that takes typed parameters and returns a string result
  - Tools are registered in a tool registry (a dict mapping name → function + schema)
  - Tool schemas are defined in Anthropic's tool format for the API
- **Interface**: `async execute(name, params) -> str`
- **Requirements satisfied**: FR-06, FR-07, FR-08, FR-09, FR-10, FR-11

### UI Listener (`listeners/ui.py`)
- **Purpose**: Rich-based rendering, implemented as event listeners. The agent loop never calls UI code directly.
- **Responsibilities**:
  - Listen for `PreToolUse` → render tool name and parameters in a highlighted panel
  - Listen for `PostToolUse` → render result (truncated if exceeding max length)
  - Listen for `Stop` → render final text as Rich markdown
  - Listen for `SubagentStart` → render sub-agent task description
  - Listen for `SubagentStop` → render sub-agent completion summary
- **Interface**: A function `register_ui_listeners(event_bus)` that hooks all handlers onto the bus
- **Requirements satisfied**: FR-05, FR-17

### Approval Listener (`listeners/approval.py`)
- **Purpose**: Tool call approval gate, implemented as an event listener on `PreToolUse`.
- **Responsibilities**:
  - Listen for `PreToolUse` → prompt user with y/n via Rich-styled input
  - Return `True` (approve) or `False` (deny)
  - For sub-agents: a no-op auto-approve listener is used instead
- **Interface**: A function `register_approval_listener(event_bus)` that hooks the handler onto the bus
- **Requirements satisfied**: FR-16, FR-18

### Sub-Agent Spawner (`tools/spawn_agent.py`)
- **Purpose**: Tool that creates and runs independent child agent instances for parallel subtask execution.
- **Responsibilities**:
  - Accept a task description (and optional parameters like model override)
  - Create a new `Agent` instance with its own conversation history
  - Run the sub-agent's loop to completion (sub-agents auto-approve tool calls - they don't prompt the user)
  - Return the sub-agent's final text response as the tool result
  - When multiple sub-agents are spawned in a single turn, run them concurrently via `asyncio.gather()`
- **Interface**: `async spawn_agent(task: str) -> str`
- **Requirements satisfied**: FR-11, FR-12, FR-13

</components>

## Data Flow

### Startup (once)

1. **main.py** creates an `EventBus`, an `Agent(provider, event_bus)`, and registers listeners:
   - `register_ui_listeners(event_bus)` - Rich rendering
   - `register_approval_listener(event_bus)` - y/n tool approval
   - (optional: `register_logging_listener(event_bus)` - file logging, etc.)
2. **main.py** enters the async REPL loop.

### Per-turn flow

1. **User types input** → `main.py` captures it via Rich `Prompt.ask()`
2. **main.py** calls `await agent.run(user_input)`
3. **Agent** appends `{"role": "user", "content": user_input}` to conversation history
4. **Agent** calls `await provider.send(messages, tools, system_prompt)`
5. **Provider** returns a `ProviderResponse` with thinking text and content blocks
6. **Agent** checks content blocks for `tool_use` blocks:
   - If **tool_use found**:
     a. Emits `PreToolUse(name, params)` → UI listener renders the tool call panel, Approval listener prompts user
     b. Calls `await event_bus.emit_approval(pre_tool_use)` → returns `True`/`False`
     c. If **approved**: executes tool via `await tools.execute(name, params)`
     d. Emits `PostToolUse(name, result)` → UI listener renders the result
     e. If **denied**: uses "tool call denied by user" as the result
     f. **Special case - `spawn_agent`**: Emits `SubagentStart(task)`, runs sub-agent(s) concurrently via `asyncio.gather()`, emits `SubagentStop(task, result)` for each. Sub-agents get their own `EventBus` with an auto-approve listener (no user prompts).
     g. Appends assistant response and tool results to conversation history
     h. **Loops back to step 4**
   - If **text only** (no tool calls):
     a. Emits `Stop(text)` → UI listener renders the response
     b. Appends assistant response to conversation history
     c. Returns the final text to `main.py`
7. **main.py** loops back to step 1

## Key Technical Decisions
<decisions>

- **Event-driven agent loop (FR-14-18)**: The agent loop emits lifecycle events instead of directly calling UI or approval code. This keeps the agent loop pure - it only manages conversation history, provider calls, and tool dispatch. All side effects (rendering, approval prompts, logging) are handled by listeners registered externally. This is the central architectural decision and teaches an important pattern for building extensible agents. Alternative considered: direct function calls from agent to UI - rejected because it couples the agent to its presentation and makes adding new behaviors (logging, metrics, custom approval) require modifying the agent loop.

- **Simple event bus, not a framework (FR-14)**: The event bus is a single file (~50 lines) with `on()`, `emit()`, and `emit_approval()`. Events are dataclasses. No third-party event library. This keeps it readable and avoids hiding behavior behind framework magic.

- **Approval as a listener, not built into the loop (FR-16, FR-18)**: Tool call approval is an event listener on `PreToolUse` that returns approve/deny. For the parent agent, this prompts the user. For sub-agents, a no-op auto-approve listener is registered instead. This cleanly solves the "sub-agents shouldn't prompt" problem without any conditional logic in the agent loop.

- **No streaming (FR-19)**: Wait for the full API response before rendering. Simplifies the codebase significantly - no async generators, no partial rendering, no buffering. The tradeoff is slower perceived response time, but this is acceptable for a teaching tool.

- **Provider abstraction via ABC (FR-20)**: A simple abstract base class with one method (`send`). No dependency injection framework, no plugin system. Adding a new provider means creating one file with one class. Over-abstracting would contradict NFR-01.

- **Tools as a flat registry (FR-06-11)**: Tools are async functions registered in a dictionary. No class hierarchy, no decorator magic. Each tool file exports an async function and a schema dict. This is the simplest pattern that works and is easy to read.

- **Sub-agents auto-approve tool calls (FR-11)**: Sub-agents run autonomously without user approval prompts. Achieved by registering an auto-approve listener on the sub-agent's event bus. The parent agent's approval of the `spawn_agent` call serves as the authorization gate. Sub-agents do NOT have access to the `spawn_agent` tool themselves (no recursive spawning) to keep complexity bounded.

- **Async execution with asyncio (FR-11, FR-12)**: The agent loop is async to support concurrent sub-agent execution via `asyncio.gather()`. The Anthropic SDK's `AsyncAnthropic` client is used. The REPL entry point uses `asyncio.run()`. This adds some complexity but is essential for parallel sub-agents and teaches an important real-world pattern.

- **Rich for terminal UI (FR-17)**: Rich provides panels, syntax highlighting, markdown rendering, and styled text out of the box. Implemented as event listeners, not called from the agent loop. Alternative considered: plain print statements - rejected because the thinking/tool call display would be hard to visually distinguish.

- **Tool output truncation**: Tool results (file contents, bash output) are truncated to 10,000 characters before being sent back to the model and displayed. This prevents context window exhaustion and keeps the terminal readable.

- **System prompt**: The agent uses a minimal system prompt that describes its role as a coding assistant and instructs it to use tools to interact with the filesystem. The system prompt is defined as a constant in the agent module.

</decisions>

## External Dependencies

| Dependency | Purpose | Version Constraint |
|---|---|---|
| `anthropic` | Anthropic API client (extended thinking, tool use) | `>=0.40.0` |
| `rich` | Terminal UI rendering (panels, markdown, syntax) | `>=13.0` |
| `pytest` | Testing framework (dev dependency) | `>=8.0` |
| `ipykernel` | Jupyter support (dev dependency, per project standards) | any |

## File & Folder Structure

```
nano-agent/
├── README.md
├── LESSON.md
├── code/
│   ├── pyproject.toml              # Project config, dependencies, entry point
│   ├── nano-agent.example.yml      # Example runtime config
│   ├── src/
│   │   └── nano_agent/
│   │       ├── __init__.py         # Package init, version
│   │       ├── main.py             # CLI entry point, REPL loop, listener wiring
│   │       ├── agent.py            # Agent loop, conversation history, tool dispatch
│   │       ├── events.py           # EventBus and event dataclasses
│   │       ├── system_prompt.py    # System prompt constant
│   │       ├── listeners/
│   │       │   ├── ui.py           # Rich-based UI event listeners
│   │       │   └── approval.py     # Tool call approval listener
│   │       ├── providers/
│   │       │   ├── base.py         # Provider interface
│   │       │   └── anthropic.py    # Anthropic API implementation
│   │       └── tools/
│   │           ├── read_file.py
│   │           ├── write_file.py
│   │           ├── find_files.py
│   │           ├── list_directory.py
│   │           ├── run_bash.py
│   │           └── spawn_agent.py
│   └── tests/
│       ├── test_agent.py
│       ├── test_events.py
│       ├── test_tools.py
│       └── test_providers.py
└── resources/
    ├── architecture.md
    ├── requirements.md
    ├── tasks.md
    ├── plan.md
    ├── todo.md
    └── claude-settings.example.json
```

## Configuration

| Setting | Source | Default |
|---|---|---|
| `ANTHROPIC_API_KEY` | Environment variable | (required, no default) |
| `--model` / `NANO_AGENT_MODEL` | CLI flag or env var | `claude-sonnet-4-20250514` |
| `--max-tokens` | CLI flag | `16000` |
| `--max-tool-output` | CLI flag | `10000` (characters) |
| `nano-agent.yml` | Optional config file copied from `code/nano-agent.example.yml` | none |

Run the project from `code/` so `pyproject.toml`, `src/`, `tests/`, and the optional `nano-agent.yml` config file stay together.

## Error Handling Strategy

- **API errors** (rate limits, auth, network): Caught in the agent loop. Raised to `main.py` which renders the error via Rich. The REPL continues - the user can retry.
- **Tool execution errors** (file not found, permission denied, bash failures): Caught in each tool function. The error message is returned as the tool result string so the model can see what went wrong and adjust.
- **Invalid input** (empty input, very long input): Handled in `main.py` before sending to the agent.
- **Keyboard interrupt**: Caught in the REPL loop. Prints a clean goodbye message and exits with code 0.
- **No exception propagation to the user**: All exceptions are caught at component boundaries. The user never sees a Python traceback.

## Observability

The event-driven architecture makes observability trivially extensible:

- **Default (UI listener)**: Thinking traces, tool calls, tool results, responses, and errors are all rendered to the terminal via Rich panels by the UI event listener.
- **File logging**: Can be added by registering a logging listener on the event bus - e.g., `register_logging_listener(event_bus, log_path)` - without modifying the agent loop. Not included in MVP but the architecture supports it with zero changes to existing code.
- **No structured logging or metrics in MVP**: This matches the simplicity goal (NFR-01). The event bus is the extension point for adding these later.

## Security Considerations

- **API key**: Read from environment variable only. Never logged or displayed.
- **Bash execution (FR-10)**: Fully unrestricted per requirements. The user approval step (FR-12) is the only safeguard. This is acceptable because the target user is a developer running the tool locally on their own machine.
- **File write (FR-07)**: Can overwrite any file the process has permission to write. Again, gated by user approval.
- **No network access beyond the Anthropic API**: The tool set does not include any HTTP/network tools, limiting the attack surface.
- **Sub-agents (FR-11)**: Sub-agents auto-approve tool calls, which means a single user approval of `spawn_agent` grants the sub-agent full tool access. This is acceptable for the target use case (local dev tool). Sub-agents cannot spawn further sub-agents (no recursion).
- **Input validation**: Tool parameters are validated by type (the Anthropic API enforces the JSON schema). Path traversal is not blocked - the user is trusted.

## Testing Strategy

- **Unit tests for tools** (`test_tools.py`): Each tool function is tested with valid inputs, edge cases (missing files, empty dirs), and error cases. Uses `tmp_path` pytest fixture for filesystem tests.
- **Unit tests for agent loop** (`test_agent.py`): Mock the provider to return scripted responses (text-only, single tool call, multi-step tool chain). Register a test listener that auto-approves and collects emitted events. Verify conversation history is built correctly, tool dispatch works, correct events are emitted, and the loop terminates.
- **Unit tests for event bus** (`test_events.py`): Test listener registration, event dispatch, approval gate returns, and multiple listeners per event type.
- **Unit tests for provider** (`test_providers.py`): Mock the `anthropic.Anthropic` client. Verify request construction (extended thinking enabled, tools passed correctly) and response mapping.
- **No e2e tests**: Would require a real API key and incur cost. Manual testing covers this.
- **No UI tests**: Rich output is tested visually during development.

## Assumptions
- [ASSUMED] CLI entry point is `nano-agent` (configured in pyproject.toml `[project.scripts]`).
- [ASSUMED] The system prompt is a short, static string - not templated or user-configurable.
- [ASSUMED] Conversation history is unbounded within a session. If context window is exceeded, the Anthropic API will return an error, which is displayed to the user.
- [ASSUMED] Tool approval prompt uses Python's built-in `input()` wrapped with Rich styling - no complex key handling needed.

## Open Questions
- [TBD] Should the agent support a `--yes` flag to auto-approve all tool calls for power users? - Would be trivial to add but changes the safety model.
