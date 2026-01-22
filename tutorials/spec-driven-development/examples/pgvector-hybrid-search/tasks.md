# Tasks: PGVector Hybrid Search

## Infrastructure
- [ ] Update docker-compose.yml to use `pgvector/pgvector:pg16` image
- [ ] Create migration to enable pgvector extension: `CREATE EXTENSION vector`
- [ ] Create documents table with columns: id, content, embedding (vector(1536)), metadata (jsonb)
- [ ] Add GIN index on tsvector column for full-text search
- [ ] Add HNSW index on embedding column for vector search

## Data Layer
- [ ] Create `embeddings.py` service
- [ ] Implement `generate_embedding(text)` using OpenAI text-embedding-3-small
- [ ] Batch embedding support for multiple documents
- [ ] Create `search.py` service
- [ ] Implement `vector_search(query_embedding, limit)` using cosine similarity
- [ ] Implement `keyword_search(query, limit)` using ts_rank
- [ ] Implement `hybrid_search(query, limit)` combining both with RRF

## API Layer
- [ ] Create `/search` POST endpoint
- [ ] Accept: `{ query: string, limit?: number, mode?: "hybrid" | "vector" | "keyword" }`
- [ ] Return: `{ results: [{ id, content, score, metadata }] }`
- [ ] Add `/documents` POST endpoint for ingestion
- [ ] Auto-generate embedding on document insert

## Verification
- [ ] Vector search returns semantically similar results
- [ ] Keyword search returns exact matches
- [ ] Hybrid search outperforms either alone on test queries
- [ ] Indexing 1000 documents completes in < 60 seconds
- [ ] Search latency < 100ms for typical queries
