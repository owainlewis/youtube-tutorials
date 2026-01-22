# AI Chat Endpoint

## Why

We need a `/chat` API endpoint that streams responses from Claude. The frontend needs real-time token streaming for good UX. Currently there's no AI integration in the backend.

## What Changes

- Add Anthropic SDK dependency
- Create chat service with streaming support
- Create `/chat` endpoint with SSE (Server-Sent Events)
- Add conversation history support
- Implement system prompt configuration

## How

- Use Anthropic Python SDK with streaming
- SSE for real-time token delivery to frontend
- Store conversation in memory (stateless per request, history passed by client)
- System prompt from environment variable or config
- Claude 3.5 Sonnet as default model

## Files Affected

- `pyproject.toml` - add anthropic dependency
- `src/config.py` - add ANTHROPIC_API_KEY, MODEL, SYSTEM_PROMPT
- `src/services/chat.py` - chat completion with streaming
- `src/api/routes/chat.py` - /chat endpoint with SSE
- `src/api/schemas/chat.py` - request/response schemas
