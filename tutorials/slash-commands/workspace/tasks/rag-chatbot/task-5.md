---
task: 5
title: RAG service and chat endpoint
depends_on: [3, 4]
files: [examples/rag-chatbot/src/services/rag.py, examples/rag-chatbot/src/api/__init__.py, examples/rag-chatbot/src/api/chat.py]
---

## Context

We're building a RAG chatbot that retrieves relevant context and generates answers using Claude. This task creates the RAG orchestration service and the chat API endpoint.

RAG flow:
1. User sends question
2. Embed the question
3. Search for similar chunks
4. Build prompt with context
5. Generate answer with Claude
6. Return answer with sources

## Requirements

### RAG Service

Create `rag.py` with:

```python
class RAGService:
    def __init__(
        self,
        embedding_service: EmbeddingService,
        vector_store: VectorStore,
        anthropic_client: anthropic.AsyncAnthropic
    ):
        # Store dependencies

    async def answer(
        self,
        question: str,
        top_k: int = 5
    ) -> RAGResponse:
        # 1. Embed the question
        # 2. Search for top_k similar chunks
        # 3. Build prompt with context
        # 4. Call Claude API
        # 5. Return response with sources
```

### Response Model

```python
class RAGResponse:
    answer: str
    sources: list[ChunkResponse]  # chunks used as context
```

### Prompt Template

Build a prompt that clearly separates context from question:

```
You are a helpful assistant that answers questions based on the provided context.
Use only the information in the context to answer. If the context doesn't contain
relevant information, say so.

Context:
---
{chunk_1_content}
---
{chunk_2_content}
---
...

Question: {user_question}

Answer:
```

### Chat API Endpoint

Create `chat.py` with:

```python
# POST /api/chat
# Request: { "message": "user question" }
# Response: { "answer": "...", "sources": [...] }
```

## Technical Notes

- Use `claude-sonnet-4-20250514` model for good speed/quality balance
- Max tokens: 1024 for response
- Handle case where no documents exist (empty context)
- Handle case where no similar chunks found
- Include similarity score in source response
- Use async Anthropic client

## Acceptance Criteria

- [ ] RAGService embeds questions correctly
- [ ] Top-k chunks retrieved by similarity
- [ ] Prompt includes all context chunks
- [ ] Claude generates coherent response
- [ ] Response includes source chunks
- [ ] Chat endpoint accepts POST requests
- [ ] Endpoint returns structured JSON response
- [ ] Empty database handled gracefully
