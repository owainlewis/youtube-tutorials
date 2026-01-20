---
task: 2
title: Document and chunk models
depends_on: [1]
files: [examples/rag-chatbot/src/models/__init__.py, examples/rag-chatbot/src/models/document.py, examples/rag-chatbot/src/models/chunk.py]
---

## Context

We're building a RAG chatbot that stores documents and their embedded chunks. This task creates the Pydantic models for serialization and validation.

The data model:
- Documents have id, filename, content, and timestamps
- Chunks belong to a document and have content, embedding vector, and index
- Embeddings are 1536-dimensional vectors (OpenAI ada-002)

## Requirements

### Document Model

Create models in `document.py`:

```python
# Database representation
Document:
    id: UUID
    filename: str
    content: str
    created_at: datetime
    updated_at: datetime

# API request
DocumentCreate:
    filename: str
    content: str

# API response
DocumentResponse:
    id: UUID
    filename: str
    created_at: datetime
    chunk_count: int  # number of chunks for this doc
```

### Chunk Model

Create models in `chunk.py`:

```python
# Database representation
Chunk:
    id: UUID
    document_id: UUID
    content: str
    embedding: list[float]  # 1536 dimensions
    chunk_index: int
    created_at: datetime

# For creating chunks
ChunkCreate:
    document_id: UUID
    content: str
    embedding: list[float]
    chunk_index: int

# API response (for showing sources)
ChunkResponse:
    id: UUID
    content: str
    chunk_index: int
    similarity: float  # populated during search
```

### Helper Methods

Add class methods for converting database rows:
- `from_row(row: asyncpg.Record) -> Model`
- Timestamps should use UTC

## Technical Notes

- Use `pydantic.BaseModel` for all models
- Use `uuid.UUID` type for IDs
- Embedding is `list[float]` in Python, `vector(1536)` in Postgres
- All models should be immutable (`frozen=True` or `model_config`)
- Export all public models from `__init__.py`

## Acceptance Criteria

- [ ] Document model with all required fields
- [ ] DocumentCreate for upload requests
- [ ] DocumentResponse for API responses
- [ ] Chunk model with embedding field
- [ ] ChunkCreate for internal use
- [ ] ChunkResponse for search results
- [ ] `from_row` methods work with asyncpg Records
- [ ] Models export from `src/models/__init__.py`
