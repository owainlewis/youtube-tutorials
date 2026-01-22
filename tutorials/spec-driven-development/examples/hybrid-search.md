# Hybrid Search with pgvector

## Why

We need semantic search for our knowledge base. Pure keyword search misses relevant results when users phrase things differently. Hybrid search combines vector similarity with full-text search for better recall.

## What

A search endpoint that combines vector similarity (semantic) with full-text search (keyword) for better results.

- POST /search — hybrid search with configurable mode
- POST /documents — ingest documents with auto-generated embeddings
- Vector search using pgvector with cosine similarity
- Keyword search using PostgreSQL tsvector
- Hybrid scoring using Reciprocal Rank Fusion (RRF)

## Constraints

### Must
- Use pgvector extension (1536 dimensions for text-embedding-3-small)
- Use existing FastAPI app structure
- Follow async patterns throughout
- Use OpenAI for embeddings

### Must Not
- Add caching layer (future optimization)
- Add authentication (separate feature)
- Modify existing endpoints

### Out of Scope
- Document chunking strategies
- Multi-tenancy
- Real-time index updates

## Current State

- Server: FastAPI in `src/main.py`
- DB: PostgreSQL with SQLAlchemy async in `src/db/`
- Config: Pydantic settings in `src/config.py`
- No search functionality exists yet

## Tasks

### T1: Add pgvector extension
**What:** Update docker-compose to use pgvector image, create migration to enable extension.
**Files:** `docker-compose.yml`, `src/db/migrations/001_add_pgvector.sql`
**Tests:** None
**Verify:** `CREATE EXTENSION vector` succeeds in database

### T2: Create documents table
**What:** Create documents table with id, content, embedding (vector(1536)), metadata (jsonb), tsvector column.
**Files:** `src/db/schema.sql`, `src/db/models/document.py`
**Tests:** None
**Verify:** Table exists with correct columns and indexes

### T3: Create embedding service
**What:** Service to generate embeddings using OpenAI text-embedding-3-small.
**Files:** `src/services/embeddings.py`, `src/services/embeddings_test.py`
**Tests:** Test single embedding, test batch embedding
**Verify:** `uv run pytest src/services/embeddings_test.py` passes

### T4: Create vector search
**What:** Implement vector_search(query_embedding, limit) using cosine similarity.
**Files:** `src/services/search.py`
**Tests:** `src/services/search_test.py` — returns results ordered by similarity
**Verify:** `uv run pytest` passes

### T5: Create keyword search
**What:** Implement keyword_search(query, limit) using ts_rank on tsvector.
**Files:** `src/services/search.py`
**Tests:** `src/services/search_test.py` — returns exact keyword matches
**Verify:** `uv run pytest` passes

### T6: Create hybrid search
**What:** Implement hybrid_search combining both with RRF scoring.
**Files:** `src/services/search.py`
**Tests:** `src/services/search_test.py` — hybrid outperforms either alone
**Verify:** `uv run pytest` passes

### T7: Create API endpoints
**What:** POST /search and POST /documents endpoints.
**Files:** `src/api/routes/search.py`, `src/api/schemas/search.py`
**Tests:** `src/api/routes/search_test.py` — end-to-end tests
**Verify:** `curl` tests return expected results, latency < 100ms
