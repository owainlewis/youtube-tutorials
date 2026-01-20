---
task: 4
title: Document service with chunking
depends_on: [2, 3]
files: [examples/rag-chatbot/src/services/documents.py]
---

## Context

We're building a RAG chatbot that chunks documents and stores their embeddings. This task creates the document service that handles the upload pipeline: save document, chunk text, embed chunks, store vectors.

Chunking strategy:
- Fixed-size chunks of 500 characters
- 50 character overlap between chunks
- Split on sentence boundaries when possible

## Requirements

### Document Service

Create `documents.py` with:

```python
class DocumentService:
    def __init__(
        self,
        pool: asyncpg.Pool,
        embedding_service: EmbeddingService,
        vector_store: VectorStore
    ):
        # Store dependencies

    async def create(self, filename: str, content: str) -> DocumentResponse:
        # 1. Insert document into database
        # 2. Chunk the content
        # 3. Embed all chunks
        # 4. Store chunks with embeddings
        # 5. Return document with chunk count
        # Use transaction for atomicity

    async def list_all(self) -> list[DocumentResponse]:
        # Return all documents with chunk counts
        # Order by created_at descending

    async def delete(self, document_id: UUID) -> bool:
        # 1. Delete all chunks for document
        # 2. Delete document
        # Return True if deleted, False if not found

    async def get(self, document_id: UUID) -> Document | None:
        # Get single document by ID
```

### Chunking Function

Create a helper function:

```python
def chunk_text(text: str, chunk_size: int = 500, overlap: int = 50) -> list[str]:
    # Split text into overlapping chunks
    # Try to break on sentence boundaries (. ! ?)
    # Return list of chunk strings
```

## Technical Notes

- Use database transaction for create (document + chunks atomic)
- Chunk count comes from JOIN or subquery
- Handle empty documents gracefully
- Strip whitespace from chunks
- Skip empty chunks after splitting
- Sentence boundary detection: look for `. `, `! `, `? ` within overlap window

Example chunking:
```
Text: "Hello world. This is a test. Another sentence here."
Chunk 1: "Hello world. This is a test."
Chunk 2: "This is a test. Another sentence here."
         ^-- overlap starts here
```

## Acceptance Criteria

- [ ] `chunk_text` splits text into ~500 char chunks
- [ ] Chunks have ~50 char overlap
- [ ] Sentence boundaries preferred for splits
- [ ] `create` saves document and chunks atomically
- [ ] `create` returns document with chunk count
- [ ] `list_all` returns documents ordered by date
- [ ] `delete` removes document and all chunks
- [ ] Empty documents handled gracefully
