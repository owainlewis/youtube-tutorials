# Micro Neo Live-Build Prompts

These prompts build the MVP in stages. Use the same `main.go` throughout.
Review and explain each change before moving to the next prompt.

## 1. Call OpenRouter

```text
Build the smallest useful Go CLI in main.go.

Requirements:
- Use only the Go standard library.
- Read OPENROUTER_API_KEY from the environment.
- Start an interactive read-eval-print loop.
- Read one message at a time from standard input.
- POST the task to OpenRouter's /api/v1/chat/completions endpoint.
- Use OPENROUTER_MODEL when set, with a sensible default.
- Print the model's text response, then show the prompt again.
- Exit cleanly when the user enters /exit.
- Keep all code in main.go.

Run gofmt, go test ./..., and go run main.go --help when finished.
```

Teaching point: before it is an agent, it is just a model call.

## 2. Add One Tool

```text
Extend the existing main.go with tool calling.

Add the smallest useful types for Message, ToolCall, ToolDefinition, and Tool.
Add one read_file tool with a JSON Schema containing a relative path.
Send that tool definition to OpenRouter and decode tool calls from the response.
Do not add the agent loop yet. If the model requests read_file, print the
requested tool name and arguments.

Keep everything in main.go and use only the standard library.
Run gofmt and go test ./... when finished.
```

Teaching point: the model requests a function. Your program owns execution.

## 3. Build the Agent Loop

```text
Turn the current program into a serial coding-agent loop.

For each turn:
1. Send the system prompt, transcript, and tool definitions to OpenRouter.
2. Append the assistant response to the transcript.
3. If there are no tool calls, print the final text and stop.
4. Otherwise execute each tool call.
5. Append one tool message with the matching tool_call_id for every call.
6. Send the expanded transcript back to the model.

After the model returns final text, wait for the next user message and keep the
transcript so follow-ups have the full conversation. Add a maximum of 50 model
turns per user message. Tool failures must become tool results so the model can
recover. Keep everything in main.go. Run gofmt and go test ./....
```

Teaching point: this loop is the core of the entire agent.

## 4. Make It a Coding Agent

```text
Extend main.go with two more tools:

- edit_file: replace exactly one occurrence of old_text with new_text.
- run_command: execute a shell command from the configured workspace.

All file paths must be relative and remain inside the workspace. Reject
ambiguous edits. Give every tool a clear description and strict JSON Schema.
Keep tool execution serial and keep all implementation in main.go.

Run gofmt and go test ./... when finished.
```

Teaching point: tools define what the agent can actually do.

## 5. Add an Event-Driven UI

```text
Refactor the existing main.go so the agent loop emits semantic events instead
of printing UI details directly.

Use a callback for:
- assistant_text
- tool_start
- tool_finish
- done
- error

Add a small terminal renderer that shows tool names, durations, failures, and
the final answer. Keep the transcript as the source of truth. Events are only
live notifications. Keep everything in main.go.

Run gofmt and go test ./... when finished.
```

Teaching point: events separate the core loop from the interface.

## 6. Harden the Boundaries

```text
Harden the single-file agent without adding product features.

Add:
- strict JSON argument decoding
- bounded file reads and command output
- basic command timeout and cancellation
- useful OpenRouter HTTP errors
- preservation of tool call IDs and provider reasoning fields
- a clear error when a model stops because of an output limit

Do not add streaming, sessions, approvals, subagents, or parallel tools.
Keep everything in main.go. Run gofmt, go test -race ./..., and go vet ./....
```

Teaching point: prompts express preferences. Code enforces guarantees.

## 7. Add the Safety Net

```text
Create one main_test.go for the finished single-file agent.

Test the agent loop with a fake provider, the transcript tool-call invariant,
turn limits, cancellation, the OpenRouter request boundary, workspace path
containment, exact edits, bounded output, and event rendering.

Tests must not call paid APIs. Keep all production code in main.go.
Run gofmt, go test -race ./..., and go vet ./....
```

The video can stop before this step or show it briefly at the end. The tests
are proof, not part of the core mental model.

# Demo Prompts

Run these from `tutorials/micro-neo/code/`.

## Main Demo

```bash
go run main.go --workspace testdata/demo
```

Then enter:

```text
› Find and fix the failing test. Run the tests when you are done.
```

Expected path:

1. Run `go test ./...` and observe the failure.
2. Read `calculator.go` and `calculator_test.go`.
3. Replace subtraction with addition.
4. Run `go test ./...` again.
5. Report that the test passes.

Reset the demo from the repository root:

```bash
git restore tutorials/micro-neo/code/testdata/demo/calculator.go
```

## Read-Only Exploration

```bash
go run main.go --workspace .
```

Then enter:

```text
› Explain how this coding agent works. Do not change any files.
```

## Failure Recovery

```bash
go run main.go --workspace testdata/demo
```

Then enter:

```text
› Read arithmetic.go, explain the Add function, and run its tests.
```

The file does not exist. The model can recover with `run_command`, inspect the
workspace, and continue.

## Try Another Model

```bash
go run main.go \
  --model openai/gpt-5.4 \
  --workspace testdata/demo
```

The selected OpenRouter model must support tool calling.
