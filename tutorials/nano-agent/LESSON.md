# Nano Agent

A working AI coding agent that runs in the terminal like Claude Code etc.

This was built as part of a YouTube tutorial and is for educational purposes only.

# How Coding Agents Work

A coding agent is a loop. Strip away the frameworks and abstractions and you're left with this:

1. Send a task to an LLM
2. The LLM responds with text (done) or tool calls (keep going)
3. Execute the tools, send results back
4. Go to step 2

```
         ┌──────────────┐
         │  User Task   │
         └──────┬───────┘
                │
         ┌──────▼───────┐
    ┌───►│   Call LLM    │
    │    └──────┬───────┘
    │           │
    │    ┌──────▼───────┐
    │    │  stop_reason  │
    │    └──┬────────┬──┘
    │       │        │
    │  tool_use   end_turn
    │       │        │
    │  ┌────▼────┐   │
    │  │Execute  │   │
    │  │tools    │   │
    │  └────┬────┘   │
    │       │        │
    └───────┘   ┌────▼────┐
                │  Done   │
                └─────────┘
```

The entire agent is built from three pieces: a message list, a set of tools, and a stop reason check.

---

## The Message List

The message list is the agent's memory. Every user message, assistant response, tool call, and tool result gets appended here. The LLM sees the full history on every call.

LLMs are stateless. If you don't pass the conversation history, the model has no memory of previous turns. So the message list grows over time. In long sessions this becomes a problem because the context window fills up with old tool results and irrelevant context, and agent performance degrades.

Production agents like Claude Code use intelligent context compression strategies. A naive approach is to keep only the latest N messages. We skip compression in nano-agent to keep things simple.

A conversation with tool use looks like this:

```python
messages = [
    # User's task
    {"role": "user", "content": "Create a hello.py file"},

    # Assistant responds with a tool call
    {"role": "assistant", "content": [
        {"type": "text", "text": "I'll create that file for you."},
        {"type": "tool_use", "id": "toolu_01ABC", "name": "write_file",
         "input": {"file_path": "hello.py", "content": "print('hello')"}}
    ]},

    # Tool result goes back as a user message
    {"role": "user", "content": [
        {"type": "tool_result", "tool_use_id": "toolu_01ABC",
         "content": "Wrote 15 bytes to hello.py"}
    ]},

    # Assistant sees the result and continues
    {"role": "assistant", "content": [
        {"type": "text", "text": "Done. Created hello.py."}
    ]}
]
```

Key rules: every `tool_result` must reference the matching `tool_use_id`. Tool results use the `user` role because they're new information from the outside world. The assistant's response can contain multiple blocks (text, tool_use, thinking).

---

## Tools

Tools are how the agent interacts with the world. Each tool has a JSON schema the LLM sees and a Python function that runs. The LLM never sees the implementation.

We use a decorator to keep schema and implementation together:

```python
TOOL_REGISTRY: dict[str, tuple[dict, Callable]] = {}

def tool(name: str, description: str, parameters: dict):
    def decorator(fn):
        schema = {
            "name": name,
            "description": description,
            "input_schema": {
                "type": "object",
                "properties": parameters,
                "required": list(parameters.keys()),
            },
        }
        TOOL_REGISTRY[name] = (schema, fn)
        return fn
    return decorator
```

nano-agent ships with five tools:

| Tool | Purpose |
|------|---------|
| bash | Run shell commands |
| read_file | Read file contents |
| write_file | Create or modify files |
| grep | Search for patterns |
| list_directory | Navigate the filesystem |

These five are enough for real coding tasks. Claude Code has more, but the pattern is identical.

Tool descriptions matter. The LLM picks tools based entirely on the description and parameter names. A vague description leads to wrong tool choices.

Errors are returned as strings, not raised. The LLM needs to see what went wrong so it can try a different approach.

---

## The Agent Loop

The core loop is about 50 lines. Here's the logic:

```python
async def run(task, config, emit=None, is_subagent=False):
    messages = [{"role": "user", "content": task}]
    tools = get_tool_schemas(include_subagents=not is_subagent)

    for turn in range(config.get("max_turns", 20)):
        response = call_llm(messages, tools, config)

        if response.stop_reason == "end_turn":
            text = next((b.text for b in response.content if b.type == "text"), "")
            return text

        if response.stop_reason == "tool_use":
            messages.append({"role": "assistant", "content": response.content})
            tool_results = []

            for block in response.content:
                if block.type == "tool_use":
                    result = await execute_tool(block.name, block.input)
                    tool_results.append({
                        "type": "tool_result",
                        "tool_use_id": block.id,
                        "content": result,
                    })

            messages.append({"role": "user", "content": tool_results})

    return "Max turns reached."
```

Two exit conditions: Claude returns `end_turn` (task complete), or we hit `max_turns` (safety valve). There's no planning step, no reflection step. Claude decides what to do, does it, sees the result, and decides again.

The loop calls `call_llm()` from a provider module that wraps the Anthropic API. Swapping models means changing one file.

---

## Events

Without events, adding features like logging, approval gates, or UI means embedding logic directly into the loop. Events keep the loop clean.

The loop emits typed events. Listeners subscribe and respond:

```python
@dataclass
class ToolCall:
    name: str
    input: dict
    tool_use_id: str

@dataclass
class ToolResult:
    name: str
    output: str
    tool_use_id: str
```

The emit function is simple:

```python
def make_emit(*listeners):
    def emit(event):
        for listener in listeners:
            listener(event)
    return emit
```

Want to log every tool call? Write a listener. Want to block dangerous commands? Write a listener that raises `PermissionError`. The loop never changes.

This is the same pattern Claude Code uses for hooks:

| nano-agent | Claude Code |
|-----------|------------|
| ToolCall event | PreToolUse hook |
| ToolResult event | PostToolUse hook |
| listener function | hook shell command |
| raise PermissionError | exit code 2 (deny) |

---

## Approval Gate

The approval gate is a listener that intercepts tool calls and asks the user for permission:

```python
def approval_listener(auto_approve: list[str]):
    def listener(event):
        if not isinstance(event, ToolCall):
            return
        if event.name in auto_approve:
            return
        answer = input(f"Allow {event.name}? [y/n] ").strip().lower()
        if answer != "y":
            raise PermissionError(f"User denied {event.name}")
    return listener
```

Read-only tools (read_file, grep, list_directory) auto-approve. Write operations (bash, write_file) prompt. When denied, the loop sends "Tool call denied by user" back to Claude as a tool result. Claude sees the denial and adapts.

---

## Sub-Agents

Sub-agents run independent tasks in parallel. They're recursive calls to the same loop:

```python
async def _run_subagents(tasks, config, emit=None):
    results = await asyncio.gather(
        *[run(t["task"], config, emit=emit, is_subagent=True) for t in tasks],
        return_exceptions=True,
    )
```

The LLM decides when to delegate via a `run_subagents` tool. Sub-agents don't get access to this tool themselves, which prevents infinite recursion. Each sub-agent gets its own message list and runs independently.

---

## Extended Thinking

One API parameter makes Claude's reasoning visible:

```python
if thinking_enabled:
    kwargs["thinking"] = {
        "type": "enabled",
        "budget_tokens": 10000,
    }
```

The response includes `thinking` blocks alongside `text` and `tool_use`. The loop emits these as events and the UI renders them.

---

## What's Deliberately Left Out

nano-agent is a teaching tool. Things we skipped:

- **Streaming** - synchronous calls keep the message structure visible
- **Context compaction** - no summarizing or trimming the message list
- **Session persistence** - each run starts fresh
- **MCP** - no external tool servers
- **Retry logic** - one API failure stops the agent
- **Cost tracking** - no token counting or budget limits

The core loop stays the same when you add these. They're good follow-up projects.
