-- 01_setup.sql
-- Enable pgvector, create the documents table with full-text search,
-- and add HNSW and GIN indexes.

CREATE EXTENSION IF NOT EXISTS vector;

CREATE TABLE documents (
    id          BIGSERIAL PRIMARY KEY,
    content     TEXT NOT NULL,
    metadata    JSONB,
    embedding   vector(1536),
    fts         tsvector GENERATED ALWAYS AS (to_tsvector('english', content)) STORED
);

-- HNSW index for fast approximate nearest neighbor search.
-- vector_cosine_ops tells PostgreSQL to use cosine distance.
CREATE INDEX ON documents
USING hnsw (embedding vector_cosine_ops)
WITH (m = 16, ef_construction = 64);

-- GIN index for fast full-text search.
CREATE INDEX ON documents USING gin(fts);
