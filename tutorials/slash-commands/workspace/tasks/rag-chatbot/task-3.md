---
task: 3
title: Embedding and vector store services
depends_on: [1, 2]
files: [examples/rag-chatbot/src/services/__init__.py, examples/rag-chatbot/src/services/embeddings.py, examples/rag-chatbot/src/services/vector_store.py]
---

## Context

We're building a RAG chatbot that uses OpenAI embeddings and pgvector for similarity search. This task creates the services that handle embedding generation and vector operations.

The application:
- Uses OpenAI text-embedding-ada-002 (1536 dimensions)
- Stores vectors in PostgreSQL with pgvector extension
- Performs cosine similarity search to find relevant chunks

## Requirements

### Embedding Service

Create `embeddings.py` with:

```python
class EmbeddingService:
    def __init__(self, api_key: str):
        # Initialize async OpenAI client

    async def embed_text(self, text: str) -> list[float]:
        # Embed single text, return 1536-dim vector

    async def embed_batch(self, texts: list[str]) -> list[list[float]]:
        # Embed multiple texts efficiently
        # OpenAI supports up to 2048 texts per batch
```

Use model `text-embedding-ada-002`.

### Vector Store Service

Create `vector_store.py` with:

```python
class VectorStore:
    def __init__(self, pool: asyncpg.Pool):
        # Store connection pool reference

    async def insert_chunks(self, chunks: list[ChunkCreate]) -> list[UUID]:
        # Insert chunks with embeddings
        # Return list of created chunk IDs

    async def search(
        self,
        query_embedding: list[float],
        limit: int = 5
    ) -> list[ChunkResponse]:
        # Find most similar chunks using cosine distance
        # Return chunks with similarity scores

    async def delete_by_document(self, document_id: UUID) -> int:
        # Delete all chunks for a document
        # Return count of deleted chunks
```

## Technical Notes

- Use async OpenAI client (`openai.AsyncOpenAI`)
- pgvector cosine distance operator is `<=>`
- Convert Python list to pgvector with `::vector` cast
- Similarity = 1 - distance (for cosine)
- Use parameterized queries to prevent SQL injection
- Batch inserts with `executemany` for performance

Example pgvector search query:
```sql
SELECT id, content, chunk_index,
       1 - (embedding <=> $1::vector) as similarity
FROM chunks
ORDER BY embedding <=> $1::vector
LIMIT $2
```

## Acceptance Criteria

- [ ] EmbeddingService initializes with API key
- [ ] `embed_text` returns 1536-dimension vector
- [ ] `embed_batch` handles multiple texts
- [ ] VectorStore connects to database pool
- [ ] `insert_chunks` stores chunks with embeddings
- [ ] `search` returns chunks ordered by similarity
- [ ] `delete_by_document` removes all document chunks
- [ ] Services export from `src/services/__init__.py`
