# Streaming Chat Endpoint

## Why

We need a `/chat` API endpoint that streams responses from Claude. The frontend needs real-time token streaming for good UX. Currently there's no AI integration in the backend.

## What

A chat endpoint with Server-Sent Events (SSE) for real-time token streaming.

- POST /chat — accepts messages, returns streaming response
- Non-streaming mode for simple requests
- Conversation history support (stateless, client passes history)
- Configurable system prompt

## Constraints

### Must
- Use Anthropic Python SDK with streaming
- Use SSE for real-time token delivery
- Use Claude 3.5 Sonnet as default model
- Follow existing FastAPI patterns

### Must Not
- Store conversation history server-side
- Add rate limiting (separate feature)
- Add authentication (separate feature)

### Out of Scope
- Tool use / function calling
- Multi-modal (images)
- Conversation persistence

## Current State

- Server: FastAPI in `src/main.py`
- Config: Pydantic settings in `src/config.py`
- No AI integration exists yet

## Tasks

### T1: Add Anthropic dependency
**What:** Add anthropic to pyproject.toml, add config settings for API key and model.
**Files:** `pyproject.toml`, `src/config.py`
**Tests:** None
**Verify:** `uv sync` succeeds, config loads API key from environment

### T2: Create chat schemas
**What:** Pydantic schemas for ChatMessage, ChatRequest, ChatResponse.
**Files:** `src/api/schemas/chat.py`
**Tests:** None
**Verify:** Schemas validate correctly

### T3: Create chat service (non-streaming)
**What:** Implement chat_completion(messages) that returns full response.
**Files:** `src/services/chat.py`, `src/services/chat_test.py`
**Tests:** Test successful completion, test API error handling
**Verify:** `uv run pytest src/services/chat_test.py` passes

### T4: Add streaming support
**What:** Implement chat_completion_stream(messages) that yields tokens.
**Files:** `src/services/chat.py`
**Tests:** `src/services/chat_test.py` — test streaming yields tokens
**Verify:** `uv run pytest` passes

### T5: Create chat endpoint
**What:** POST /chat with SSE streaming. Non-streaming returns JSON, streaming returns SSE events.
**Files:** `src/api/routes/chat.py`, `src/main.py` (register router)
**Tests:** `src/api/routes/chat_test.py` — test both modes
**Verify:** `curl` receives streaming tokens, final event is `[DONE]`

### T6: Add error handling
**What:** Handle Anthropic API errors gracefully, add retry with exponential backoff.
**Files:** `src/services/chat.py`
**Tests:** `src/services/chat_test.py` — test retry behavior, test error responses
**Verify:** Invalid API key returns 401, rate limit triggers retry

## Validation

After all tasks complete, verify the full chat flow:

- `uv run pytest` — all tests pass
- Manual flow test:
  1. Non-streaming: `curl -X POST localhost:8000/chat -d '{"messages":[{"role":"user","content":"Say hello"}],"stream":false}' -H "Content-Type: application/json"` — returns complete JSON response
  2. Streaming: `curl -N -X POST localhost:8000/chat -d '{"messages":[{"role":"user","content":"Count to 5"}],"stream":true}' -H "Content-Type: application/json"` — returns SSE events with tokens, ends with `[DONE]`
  3. Verify conversation history works by passing multiple messages
  4. Verify error handling with invalid API key returns 401
