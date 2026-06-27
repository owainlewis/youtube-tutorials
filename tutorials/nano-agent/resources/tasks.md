# Implementation Plan

## Summary
- Total phases: 4
- Total tasks: 16
- Estimated complexity: Medium

---

## Phase 1: Working Conversational Agent with UI
**Goal**: `uv run nano-agent` starts with a polished Rich UI, sends user input to the Anthropic API with extended thinking, displays the thinking trace and response with proper styling. No tools yet - just a beautiful conversational agent loop.
**Requirements covered**: FR-01, FR-02, FR-03, FR-04, FR-05, FR-14, FR-15, FR-16, FR-17, FR-18, FR-19, FR-20, NFR-02, NFR-04, NFR-05

<task id="1.1">
  <title>Initialize project with uv and configure pyproject.toml</title>
  <context>
    This is a Python project managed with `uv`. The package lives under `src/nano_agent/`.
    The CLI entry point is `nano-agent` mapped to `nano_agent.main:main`.
    Runtime dependencies: `anthropic>=0.40.0`, `rich>=13.0`.
    Dev dependencies: `pytest`, `ipykernel`.
  </context>
  <files>
    pyproject.toml
    src/nano_agent/__init__.py
  </files>
  <action>
    Create `pyproject.toml` with:
    - `[project]` name="nano-agent", requires-python=">=3.12"
    - `[project.scripts]` nano-agent = "nano_agent.main:main"
    - dependencies: anthropic>=0.40.0, rich>=13.0
    - `[dependency-groups]` dev = ["pytest", "ipykernel"]
    - `[build-system]` using hatchling with `src` layout
    Create `src/nano_agent/__init__.py` with `__version__ = "0.1.0"`.
  </action>
  <verify>
    Run `uv sync` - exits without error, `.venv` is created.
  </verify>
  <depends_on></depends_on>
</task>

<task id="1.2">
  <title>Implement event bus with lifecycle events</title>
  <context>
    The event bus is a single-file module (~50 lines). Events are dataclasses. The bus has three methods:
    `on(event_type, async_callback)` - register a listener.
    `emit(event)` - call all registered listeners for that event type.
    `emit_approval(event) -> bool` - special method for `PreToolUse` that returns True if approved.
    Event types: `PreToolUse(tool_name, tool_params)`, `PostToolUse(tool_name, result)`,
    `Stop(text)`, `SubagentStart(task)`, `SubagentStop(task, result)`.
    All listeners are async callables. Listeners are called in registration order.
    For `emit_approval`, if any listener returns False, return False. Default True if no listeners.
  </context>
  <files>
    src/nano_agent/events.py
  </files>
  <action>
    Create `events.py` with:
    - Dataclasses for each event type: `PreToolUse`, `PostToolUse`, `Stop`, `SubagentStart`, `SubagentStop`.
    - `PreToolUse` has fields: `tool_name: str`, `tool_params: dict`.
    - `PostToolUse` has fields: `tool_name: str`, `result: str`.
    - `Stop` has field: `text: str`.
    - `SubagentStart` has field: `task: str`.
    - `SubagentStop` has fields: `task: str`, `result: str`.
    - Class `EventBus` with:
      - `self._listeners: dict[type, list[Callable]]` initialized as defaultdict(list).
      - `on(event_type, callback)` - appends callback to the list for that type.
      - `async emit(event)` - iterates `self._listeners[type(event)]` and awaits each callback with the event.
      - `async emit_approval(event: PreToolUse) -> bool` - calls each listener; if any returns False, return False. Default True.
  </action>
  <verify>
    Run `uv run pytest tests/test_events.py` - write a quick test that registers a listener, emits an event, and asserts the listener was called. Test approval gate returns True by default and False when a listener denies.
  </verify>
  <depends_on>1.1</depends_on>
</task>

<task id="1.3">
  <title>Implement provider interface and Anthropic provider</title>
  <context>
    The provider is an abstract base class with one method: `async send(messages, tools, system_prompt) -> ProviderResponse`.
    `ProviderResponse` is a dataclass with fields: `thinking: str | None`, `content: list[ContentBlock]`.
    `ContentBlock` is a dataclass with `type: str` ("text" or "tool_use") and relevant fields.
    The Anthropic provider uses `AsyncAnthropic` client with extended thinking enabled (`thinking={"type": "enabled", "budget_tokens": N}`).
    It maps the Anthropic response format to `ProviderResponse`.
    API errors are caught and re-raised as a simple `ProviderError` exception.
  </context>
  <files>
    src/nano_agent/providers/__init__.py
    src/nano_agent/providers/base.py
    src/nano_agent/providers/anthropic.py
  </files>
  <action>
    Create `providers/base.py` with:
    - Dataclasses: `TextBlock(type="text", text: str)`, `ToolUseBlock(type="tool_use", id: str, name: str, input: dict)`.
    - `ContentBlock = TextBlock | ToolUseBlock` (type alias).
    - Dataclass `ProviderResponse(thinking: str | None, content: list[ContentBlock])`.
    - `class ProviderError(Exception): pass`
    - Abstract class `Provider(ABC)` with `async def send(self, messages: list[dict], tools: list[dict], system_prompt: str) -> ProviderResponse`.

    Create `providers/anthropic.py` with:
    - Class `AnthropicProvider(Provider)` initialized with `model: str`, `max_tokens: int`, `api_key: str | None = None`.
    - Creates `AsyncAnthropic(api_key=api_key)` client in `__init__`.
    - `async send()`: calls `self.client.messages.create(...)` with extended thinking enabled. Maps response content blocks to `TextBlock` / `ToolUseBlock`. Extracts thinking from thinking blocks. Wraps API exceptions in `ProviderError`.

    Create `providers/__init__.py` that re-exports `Provider`, `AnthropicProvider`, `ProviderResponse`.
  </action>
  <verify>
    Run `uv run python -c "from nano_agent.providers import AnthropicProvider; print('OK')"` - no import errors.
  </verify>
  <depends_on>1.1</depends_on>
</task>

<task id="1.4">
  <title>Implement the core agent loop</title>
  <context>
    The agent loop manages conversation history, calls the provider, emits events, and dispatches tools.
    It contains ZERO UI or approval logic - all side effects go through the event bus.
    The loop: append user message -> call provider -> if tool_use blocks, emit PreToolUse, await approval,
    execute tool (or deny), emit PostToolUse, loop back to provider -> if text only, emit Stop, return text.
    Conversation history is a list of message dicts kept in memory (FR-03).
    The agent is initialized with a Provider, EventBus, tool registry (dict), and system prompt string.
    A system prompt constant is defined in `system_prompt.py`.
    For this task, the tools dict will be empty - just get the text-only conversational loop working.
  </context>
  <files>
    src/nano_agent/agent.py
    src/nano_agent/system_prompt.py
  </files>
  <action>
    Create `system_prompt.py` with a `SYSTEM_PROMPT` string constant - short text describing the agent as a coding assistant that uses tools to interact with the filesystem.

    Create `agent.py` with:
    - Class `Agent` initialized with `provider: Provider`, `event_bus: EventBus`, `tools: dict`, `system_prompt: str = SYSTEM_PROMPT`.
    - `self.history: list[dict] = []` for conversation history.
    - `async def run(self, user_input: str) -> str`:
      1. Append `{"role": "user", "content": user_input}` to history.
      2. Build tools list from `self.tools` (extract schemas).
      3. Enter loop:
         a. Call `await self.provider.send(self.history, tool_schemas, self.system_prompt)`.
         b. Process response: find text blocks and tool_use blocks.
         c. If tool_use blocks present:
            - Build the assistant message content (include all blocks from the response).
            - Append assistant message to history.
            - For each tool_use block:
              - Emit `PreToolUse(tool_name, tool_params)` via `event_bus.emit_approval()`.
              - If approved: call the tool function from `self.tools[name]["function"]` with params.
              - If denied: result = "Tool call denied by user".
              - Emit `PostToolUse(tool_name, result)`.
            - Append tool result messages to history (role="user", tool_result content blocks).
            - Continue loop.
         d. If text only (no tool_use):
            - Extract text from text blocks.
            - Append assistant message to history.
            - Emit `Stop(text)`.
            - Return text.
  </action>
  <verify>
    Write `tests/test_agent.py` with a mock provider that returns a text-only response. Create an Agent with the mock provider and an EventBus. Call `await agent.run("hello")`. Assert the response text is returned and a `Stop` event was emitted.
    Run `uv run pytest tests/test_agent.py`.
  </verify>
  <depends_on>1.2, 1.3</depends_on>
</task>

<task id="1.5">
  <title>Implement Rich UI and approval event listeners</title>
  <context>
    The UI listener uses Rich to render events. The agent loop never calls UI code directly.
    The approval listener prompts the user with y/n on `PreToolUse` events.
    UI rendering: `PreToolUse` -> panel showing tool name + params. `PostToolUse` -> panel showing result (truncated to 10000 chars). `Stop` -> Rich markdown rendering. `SubagentStart`/`SubagentStop` -> brief status lines.
    Approval: prompts via `Console.input("[y/n]")`, returns True for "y", False otherwise.
    Each listener module exports a `register_*_listeners(event_bus)` function.
    The UI should look polished from the start - this is what users see first.
  </context>
  <files>
    src/nano_agent/listeners/__init__.py
    src/nano_agent/listeners/ui.py
    src/nano_agent/listeners/approval.py
  </files>
  <action>
    Create `listeners/ui.py` with:
    - A Rich `Console` instance.
    - `async def on_pre_tool_use(event: PreToolUse)` - print a Rich Panel with title=tool_name, body=JSON-formatted params.
    - `async def on_post_tool_use(event: PostToolUse)` - print result text (truncated to 10000 chars) in a dim panel.
    - `async def on_stop(event: Stop)` - print event.text as Rich Markdown.
    - `async def on_subagent_start(event: SubagentStart)` - print a status line like "Sub-agent started: {task}".
    - `async def on_subagent_stop(event: SubagentStop)` - print "Sub-agent done: {task}".
    - `def register_ui_listeners(event_bus: EventBus)` - calls `event_bus.on()` for each handler.

    Create `listeners/approval.py` with:
    - `async def on_pre_tool_use(event: PreToolUse) -> bool` - uses Rich Console to prompt "Allow {tool_name}? [y/n]", returns True if input starts with "y".
    - `def register_approval_listener(event_bus: EventBus)` - registers the handler.

    Create `listeners/__init__.py` that re-exports both register functions.
  </action>
  <verify>
    Run `uv run python -c "from nano_agent.listeners import register_ui_listeners, register_approval_listener; print('OK')"` - no import errors.
  </verify>
  <depends_on>1.2</depends_on>
</task>

<task id="1.6">
  <title>Wire everything together in main.py - working conversational agent</title>
  <context>
    `main.py` is the CLI entry point. It creates the provider, event bus, agent, registers listeners, and runs the REPL.
    The provider is AnthropicProvider. API key comes from `ANTHROPIC_API_KEY` env var.
    Model is configurable via `--model` CLI flag or `NANO_AGENT_MODEL` env var, default `claude-sonnet-4-20250514`.
    Use `argparse` for CLI args (just `--model` and `--max-tokens`).
    No tools registered yet - the agent is conversational only but with full Rich UI.
    Error handling: catch `ProviderError` in the REPL loop, print the error via Rich, continue.
    Catches KeyboardInterrupt/EOFError for clean exit with code 0, no traceback.
    This is the milestone: run `uv run nano-agent`, have a conversation, see thinking traces and styled responses.
  </context>
  <files>
    src/nano_agent/main.py
  </files>
  <action>
    Create `main.py` with:
    - `import argparse, asyncio, os`
    - `from rich.console import Console`
    - Imports for Agent, EventBus, AnthropicProvider, ProviderError, listeners.
    - `async def run()`:
      1. Parse args: `--model` (default from env `NANO_AGENT_MODEL` or `claude-sonnet-4-20250514`), `--max-tokens` (default 16000).
      2. Create `AnthropicProvider(model=args.model, max_tokens=args.max_tokens)`.
      3. Create `EventBus()`.
      4. `register_ui_listeners(event_bus)`.
      5. `register_approval_listener(event_bus)`.
      6. Create `Agent(provider=provider, event_bus=event_bus, tools={})`.
      7. Print a welcome banner via Rich Console.
      8. REPL loop: read input via `console.input(">>> ")`, skip empty, call `await agent.run(input)`, catch `ProviderError` and print error in red.
    - `def main()`: wraps `asyncio.run(run())` in try/except for KeyboardInterrupt and EOFError, prints goodbye, exits 0.
  </action>
  <verify>
    Set `ANTHROPIC_API_KEY` env var. Run `uv run nano-agent`. See welcome banner. Type "What is 2+2?". See the thinking trace rendered in a styled panel, then the response rendered as Rich markdown. Type another question - conversation history is maintained. Press Ctrl+C - clean exit with no traceback.
  </verify>
  <depends_on>1.4, 1.5</depends_on>
</task>

---

## Phase 2: Tools
**Goal**: All 7 tools are implemented and registered. The agent can read/write/edit files, search, list directories, and run bash commands. Tool calls show in the Rich UI with approval prompts.
**Requirements covered**: FR-06, FR-07, FR-08, FR-09, FR-10

<task id="2.1">
  <title>Implement tool registry, read_file, and edit_file tools</title>
  <context>
    Tools are async functions registered in a dict: `{name: {"function": async_fn, "schema": dict}}`.
    The schema is in Anthropic's tool format: `{"name": str, "description": str, "input_schema": {json_schema}}`.
    `tools/__init__.py` exports a `get_tools() -> dict` function that returns the full registry.
    `read_file` reads a file path and returns its contents as a string. On error, returns the error message.
    `edit_file` does exact string replacement (old_string -> new_string). Requires old_string to appear exactly once.
    Tool output is truncated to 10000 characters.
  </context>
  <files>
    src/nano_agent/tools/__init__.py
    src/nano_agent/tools/read_file.py
    src/nano_agent/tools/edit_file.py
  </files>
  <action>
    Create `tools/__init__.py`:
    - `MAX_OUTPUT = 10000` constant.
    - `def get_tools() -> dict` - returns registry dict for all tools. Start with read_file and edit_file.

    Create `tools/read_file.py`:
    - `async def read_file(file_path: str) -> str`: read file at path, return contents. On FileNotFoundError or PermissionError, return error message string. Truncate output to 10000 chars with a "[truncated]" suffix.
    - `SCHEMA` dict in Anthropic tool format.

    Create `tools/edit_file.py`:
    - `async def edit_file(file_path: str, old_string: str, new_string: str) -> str`:
      1. Read the file. Return error if not found.
      2. Check that `old_string` appears exactly once. If zero: return "old_string not found in file". If multiple: return "old_string is not unique - provide more context".
      3. Replace and write back.
      4. Return f"Successfully edited {file_path}".
    - `SCHEMA` dict.
  </action>
  <verify>
    Run `uv run pytest tests/test_tools.py` - write tests: read_file reads a temp file correctly, returns error for missing file, truncates large output. edit_file replaces a unique string, fails on missing string, fails on ambiguous match.
  </verify>
  <depends_on>1.1</depends_on>
</task>

<task id="2.2">
  <title>Implement write_file, find_files, and list_directory tools</title>
  <context>
    Three file-system tools, each following the same pattern as read_file:
    async function + SCHEMA dict. Errors returned as strings, not raised.
    `write_file(file_path, content)` - writes content to file, creating parent dirs if needed. Returns confirmation.
    `find_files(pattern, path=".")` - uses `glob.glob(pattern, recursive=True)` relative to path. Returns newline-separated list of matches.
    `list_directory(path=".")` - uses `os.listdir`. Returns newline-separated list of entries with type indicators (/ for dirs).
  </context>
  <files>
    src/nano_agent/tools/write_file.py
    src/nano_agent/tools/find_files.py
    src/nano_agent/tools/list_directory.py
    src/nano_agent/tools/__init__.py
  </files>
  <action>
    Create `tools/write_file.py`:
    - `async def write_file(file_path: str, content: str) -> str`: create parent dirs with `os.makedirs(exist_ok=True)`, write content, return f"Successfully wrote {len(content)} characters to {file_path}".
    - Schema: file_path (required), content (required).

    Create `tools/find_files.py`:
    - `async def find_files(pattern: str, path: str = ".") -> str`: use `glob.glob(os.path.join(path, pattern), recursive=True)`, return matches joined by newlines. If no matches, return "No files found matching pattern: {pattern}".
    - Schema: pattern (required), path (optional, default ".").

    Create `tools/list_directory.py`:
    - `async def list_directory(path: str = ".") -> str`: list entries, append "/" to directories, return joined by newlines.
    - Schema: path (optional, default ".").

    Update `tools/__init__.py` to register all three new tools in `get_tools()`.
  </action>
  <verify>
    Run `uv run pytest tests/test_tools.py` - add tests for each: write_file creates a file and returns confirmation, find_files finds matching files, list_directory lists entries with "/" suffix for dirs.
  </verify>
  <depends_on>2.1</depends_on>
</task>

<task id="2.3">
  <title>Implement run_bash tool</title>
  <context>
    `run_bash` executes arbitrary bash commands via `asyncio.create_subprocess_shell`.
    No restrictions on what commands can be run - the user approval listener gates execution.
    Returns combined stdout + stderr. Truncated to 10000 characters.
    Has a default timeout of 30 seconds. On timeout, kills the process and returns a timeout message.
  </context>
  <files>
    src/nano_agent/tools/run_bash.py
    src/nano_agent/tools/__init__.py
  </files>
  <action>
    Create `tools/run_bash.py`:
    - `async def run_bash(command: str, timeout: int = 30) -> str`:
      1. Create subprocess with `asyncio.create_subprocess_shell(command, stdout=PIPE, stderr=PIPE)`.
      2. `await asyncio.wait_for(process.communicate(), timeout=timeout)`.
      3. Combine stdout and stderr (decoded as utf-8).
      4. Prepend exit code: f"Exit code: {process.returncode}\n{output}".
      5. Truncate to 10000 chars.
      6. On `asyncio.TimeoutError`: kill process, return "Command timed out after {timeout} seconds".
    - Schema: command (required), timeout (optional integer, default 30).

    Update `tools/__init__.py` to register run_bash.
  </action>
  <verify>
    Run `uv run pytest tests/test_tools.py` - test `run_bash("echo hello")` returns "Exit code: 0\nhello\n". Test a failing command returns non-zero exit code.
  </verify>
  <depends_on>2.1</depends_on>
</task>

<task id="2.4">
  <title>Register all tools in main.py</title>
  <context>
    `main.py` currently creates the Agent with an empty tools dict.
    Now that all tools are implemented, wire them in via `get_tools()`.
  </context>
  <files>
    src/nano_agent/main.py
  </files>
  <action>
    Update `main.py`:
    - Import `get_tools` from `nano_agent.tools`.
    - Replace `tools={}` with `tools=get_tools()` when creating the Agent.
  </action>
  <verify>
    Run `uv run nano-agent`. Ask "List the files in the current directory." See the PreToolUse panel with tool name and params. Approve with "y". See the directory listing in a result panel. See the agent's summary response rendered as markdown.
  </verify>
  <depends_on>1.6, 2.1, 2.2, 2.3</depends_on>
</task>

---

## Phase 3: Sub-Agents
**Goal**: The agent can spawn sub-agents for parallel subtask execution. Sub-agents run their own agent loops, auto-approve tool calls, and return results to the parent.
**Requirements covered**: FR-11, FR-12, FR-13

<task id="3.1">
  <title>Implement spawn_agent tool with parallel execution</title>
  <context>
    `spawn_agent` creates a new Agent instance with its own EventBus and conversation history.
    The sub-agent gets the SAME provider and tools as the parent (minus spawn_agent itself - no recursion).
    The sub-agent's EventBus gets an auto-approve listener (returns True for all PreToolUse events).
    When the parent agent encounters multiple spawn_agent tool_use blocks in a single turn,
    it runs them concurrently via `asyncio.gather()`. This logic lives in the agent loop, not in the tool itself.
    SubagentStart and SubagentStop events are emitted on the PARENT event bus.
  </context>
  <files>
    src/nano_agent/tools/spawn_agent.py
    src/nano_agent/agent.py
    src/nano_agent/tools/__init__.py
  </files>
  <action>
    Create `tools/spawn_agent.py`:
    - `SCHEMA` with: name="spawn_agent", description="Spawn a sub-agent to handle a subtask independently", input_schema with `task` (required string).
    - No function export needed - the agent loop handles sub-agent creation directly.

    Update `agent.py` to handle `spawn_agent` specially in the tool dispatch:
    - When processing tool_use blocks, collect all `spawn_agent` calls into a list.
    - For each, create a new Agent with: same provider, new EventBus (with auto-approve listener), tools dict WITHOUT spawn_agent.
    - Emit `SubagentStart(task)` on the PARENT event bus.
    - Run all sub-agents concurrently: `results = await asyncio.gather(*[sub.run(task) for sub, task in sub_agents])`.
    - Emit `SubagentStop(task, result)` for each on the PARENT event bus.
    - Use results as the tool results.

    Update `tools/__init__.py` to include spawn_agent schema (but no function - agent handles it).
  </action>
  <verify>
    Write `tests/test_agent.py` test: mock provider returns two spawn_agent tool_use blocks, then a text response. Mock sub-agent provider returns text immediately. Assert both SubagentStart and SubagentStop events are emitted, and results are fed back to the parent.
    Run `uv run pytest tests/test_agent.py`.
  </verify>
  <depends_on>1.4, 2.1</depends_on>
</task>

---

## Phase 4: Tests and Polish
**Goal**: Comprehensive test coverage across all components. The codebase is clean, well-tested, and ready for developers to learn from.
**Requirements covered**: NFR-01, NFR-03

<task id="4.1">
  <title>Comprehensive event bus tests</title>
  <context>
    The event bus is the architectural centerpiece. Tests should cover: listener registration,
    event dispatch to multiple listeners, approval gate (True/False), emission order,
    and behavior with no listeners registered (emit is a no-op, approval defaults to True).
  </context>
  <files>
    tests/test_events.py
  </files>
  <action>
    Write tests in `tests/test_events.py`:
    - test_emit_calls_listener: register a listener, emit event, assert called with correct event.
    - test_emit_multiple_listeners: register two listeners, emit, assert both called in order.
    - test_emit_no_listeners: emit with no listeners registered - no error.
    - test_approval_default_true: emit_approval with no listeners returns True.
    - test_approval_approved: register listener returning True, assert emit_approval returns True.
    - test_approval_denied: register listener returning False, assert emit_approval returns False.
    - test_approval_multiple_listeners_one_denies: register two listeners (True, False), assert False.
  </action>
  <verify>
    Run `uv run pytest tests/test_events.py -v` - all tests pass.
  </verify>
  <depends_on>1.2</depends_on>
</task>

<task id="4.2">
  <title>Comprehensive agent loop tests</title>
  <context>
    Test the agent loop with a mock provider and test event listeners.
    The mock provider returns scripted ProviderResponse sequences.
    A test listener collects all emitted events for assertion.
    Cover: text-only response, single tool call, multi-step tool chain (tool -> provider -> tool -> text),
    denied tool call, and conversation history accumulation.
  </context>
  <files>
    tests/test_agent.py
  </files>
  <action>
    Write tests in `tests/test_agent.py`:
    - Create a `MockProvider` that returns responses from a list (pops from front on each call).
    - Create a `CollectorListener` that appends events to a list.
    - test_text_response: provider returns text only -> agent returns text, Stop event emitted.
    - test_tool_call_approved: provider returns tool_use then text -> tool executed, PostToolUse emitted, Stop emitted.
    - test_tool_call_denied: register deny listener -> tool not executed, "denied" result in PostToolUse.
    - test_multi_step: provider returns tool_use, then another tool_use, then text -> two tool calls, correct history.
    - test_conversation_history: call agent.run() twice -> history contains both exchanges.
  </action>
  <verify>
    Run `uv run pytest tests/test_agent.py -v` - all tests pass.
  </verify>
  <depends_on>1.4</depends_on>
</task>

<task id="4.3">
  <title>Comprehensive tool tests</title>
  <context>
    Each tool function should be tested with valid inputs, edge cases, and error cases.
    Use pytest `tmp_path` fixture for all filesystem operations.
    All tool functions are async - use `pytest-asyncio` or `asyncio.run()` in tests.
  </context>
  <files>
    tests/test_tools.py
  </files>
  <action>
    Write tests in `tests/test_tools.py`:
    - read_file: reads existing file, returns error for missing file, truncates large files.
    - write_file: creates file with content, creates parent directories, overwrites existing file.
    - edit_file: replaces a unique string, fails on missing string, fails on ambiguous match.
    - find_files: finds files matching pattern, returns "No files found" for no matches.
    - list_directory: lists entries, shows "/" for directories, handles missing directory.
    - run_bash: runs echo command, handles failing command (non-zero exit), handles timeout.
  </action>
  <verify>
    Run `uv run pytest tests/test_tools.py -v` - all tests pass.
  </verify>
  <depends_on>2.1, 2.2, 2.3</depends_on>
</task>

<task id="4.4">
  <title>Provider tests with mocked API</title>
  <context>
    Test the AnthropicProvider with a mocked AsyncAnthropic client.
    Verify: extended thinking is enabled in requests, response is correctly mapped to ProviderResponse,
    API errors are wrapped in ProviderError.
  </context>
  <files>
    tests/test_providers.py
  </files>
  <action>
    Write tests in `tests/test_providers.py`:
    - Mock `anthropic.AsyncAnthropic` and its `messages.create` method.
    - test_send_constructs_correct_request: verify model, messages, tools, system, and thinking params are passed.
    - test_send_maps_text_response: mock response with text block -> ProviderResponse has TextBlock.
    - test_send_maps_tool_use_response: mock response with tool_use block -> ProviderResponse has ToolUseBlock.
    - test_send_maps_thinking: mock response with thinking block -> ProviderResponse.thinking is set.
    - test_send_wraps_api_error: mock raises `anthropic.APIError` -> ProviderError raised.
  </action>
  <verify>
    Run `uv run pytest tests/test_providers.py -v` - all tests pass.
  </verify>
  <depends_on>1.3</depends_on>
</task>

---

## Parallelism Notes

Tasks that can run in parallel within their phase:
- **Phase 1**: Tasks 1.2, 1.3, 1.5 have no dependencies on each other (all depend only on 1.1).
- **Phase 2**: Tasks 2.2 and 2.3 can run in parallel (both depend only on 2.1).
- **Phase 4**: All tasks (4.1, 4.2, 4.3, 4.4) can run in parallel.

## Requirements Coverage

| Requirement | Covered by |
|---|---|
| FR-01 | 1.6 |
| FR-02 | 1.6 |
| FR-03 | 1.4 |
| FR-04 | 1.3, 1.4 |
| FR-05 | 1.5 |
| FR-06 | 2.1 |
| FR-07 | 2.2 |
| FR-08 | 2.2 |
| FR-09 | 2.2 |
| FR-10 | 2.3 |
| FR-11 | 3.1 |
| FR-12 | 3.1 |
| FR-13 | 3.1 |
| FR-14 | 1.2 |
| FR-15 | 1.2 |
| FR-16 | 1.2, 1.5 |
| FR-17 | 1.5 |
| FR-18 | 1.5 |
| FR-19 | 1.3 |
| FR-20 | 1.3 |
| NFR-01 | all (structural) |
| NFR-02 | 1.1 |
| NFR-03 | 4.1-4.4 |
| NFR-04 | 1.3, 1.6 |
| NFR-05 | 1.6 |
