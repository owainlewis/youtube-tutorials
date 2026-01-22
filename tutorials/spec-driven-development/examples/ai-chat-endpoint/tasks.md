# Tasks: AI Chat Endpoint

## Configuration
- [ ] Add `anthropic` to pyproject.toml dependencies
- [ ] Add settings to config.py: ANTHROPIC_API_KEY, MODEL, SYSTEM_PROMPT
- [ ] MODEL defaults to "claude-sonnet-4-20250514"
- [ ] Validate API key on startup

## Data Layer
- [ ] Create Pydantic schemas in `schemas/chat.py`
- [ ] ChatMessage: `{ role: "user" | "assistant", content: str }`
- [ ] ChatRequest: `{ messages: list[ChatMessage], stream?: bool }`
- [ ] ChatResponse: `{ message: ChatMessage, usage: { input_tokens, output_tokens } }`

## Service Layer
- [ ] Create `chat.py` service
- [ ] Implement `chat_completion(messages, stream=False)` - returns full response
- [ ] Implement `chat_completion_stream(messages)` - yields tokens
- [ ] Handle Anthropic API errors gracefully
- [ ] Add retry logic with exponential backoff

## API Layer
- [ ] Create POST `/chat` endpoint
- [ ] Non-streaming: return ChatResponse as JSON
- [ ] Streaming: return SSE with `data: {token}` events
- [ ] Final SSE event: `data: [DONE]`
- [ ] Add request validation and error responses

## Verification
- [ ] Non-streaming request returns complete response
- [ ] Streaming request delivers tokens in real-time
- [ ] Invalid API key returns 401
- [ ] Malformed request returns 422 with details
- [ ] Conversation history is respected (multi-turn works)
