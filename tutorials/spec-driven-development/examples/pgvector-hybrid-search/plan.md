# PGVector Hybrid Search

## Why

We need semantic search for our knowledge base. Pure keyword search misses relevant results when users phrase things differently. Hybrid search combines vector similarity (semantic) with full-text search (keyword) for better recall.

## What Changes

- Add pgvector extension to PostgreSQL
- Create embeddings table with vector column
- Add full-text search index for keyword matching
- Implement hybrid search that combines both approaches
- Create embedding generation utility using OpenAI

## How

- Use pgvector extension (1536 dimensions for text-embedding-3-small)
- Store documents with: id, content, embedding, metadata
- Full-text search via PostgreSQL `tsvector` and `ts_rank`
- Hybrid scoring: `0.7 * vector_score + 0.3 * text_score` (tunable)
- RRF (Reciprocal Rank Fusion) for combining results

## Files Affected

- `docker-compose.yml` - add pgvector image
- `src/db/schema.sql` - documents table with vector + tsvector columns
- `src/db/migrations/001_add_pgvector.sql` - enable extension
- `src/services/embeddings.py` - generate embeddings via OpenAI
- `src/services/search.py` - hybrid search implementation
- `src/api/routes/search.py` - /search endpoint
