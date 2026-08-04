-- 05_seed_data.sql
-- Sample documents for testing. These have no embeddings.
-- For real embeddings, run: uv run python src/seed.py
--
-- Note: rows without embeddings will not appear in vector results. They can
-- still appear in full-text results and the full-text branch of hybrid search.

INSERT INTO documents (content, metadata) VALUES
(
    'pgvector is a PostgreSQL extension that adds support for vector similarity search. It allows you to store embeddings as a native column type and query them using distance operators like cosine distance, inner product, and L2 distance.',
    '{"source": "pgvector-docs", "topic": "overview"}'
),
(
    'HNSW (Hierarchical Navigable Small World) is an approximate nearest neighbor algorithm. In pgvector, you create an HNSW index with CREATE INDEX USING hnsw. Its query behavior depends on the data, index settings, and available resources.',
    '{"source": "pgvector-docs", "topic": "indexing"}'
),
(
    'Cosine distance measures the angle between two vectors, ignoring magnitude. In PostgreSQL with pgvector, the cosine distance operator is <=>. A cosine distance of 0 means identical direction, while 2 means opposite direction.',
    '{"source": "pgvector-docs", "topic": "distance-metrics"}'
),
(
    'RAG (Retrieval-Augmented Generation) is a technique where you retrieve relevant documents from a database and pass them as context to a large language model. This grounds the LLM response in your actual data instead of relying solely on its training data.',
    '{"source": "ai-engineering", "topic": "rag"}'
),
(
    'Full-text search in PostgreSQL uses tsvector for indexed document representations and tsquery for search queries. The @@ operator matches a tsquery against a tsvector. Combined with GIN indexes, full-text search is fast even on large tables.',
    '{"source": "postgresql-docs", "topic": "full-text-search"}'
),
(
    'Hybrid search combines vector similarity search with keyword-based full-text search. Reciprocal Rank Fusion (RRF) merges ranked results from both methods. Documents that appear in both lists receive a score contribution from each rank.',
    '{"source": "ai-engineering", "topic": "hybrid-search"}'
),
(
    'The text-embedding-3-small model from OpenAI produces 1536-dimensional vectors. These embeddings capture semantic meaning, so similar concepts have similar vector representations regardless of the exact words used.',
    '{"source": "openai-docs", "topic": "embeddings"}'
),
(
    'PostgreSQL supports ACID transactions, JSONB for semi-structured data, and full-text search. The pgvector extension adds dense vector storage and similarity operators to the same database.',
    '{"source": "postgresql-docs", "topic": "overview"}'
),
(
    'IVFFlat is another pgvector index type. It partitions vectors into lists and needs data in the table before the index is created. Compare its build time, memory use, query latency, and recall with HNSW on your own workload.',
    '{"source": "pgvector-docs", "topic": "indexing"}'
),
(
    'Some managed PostgreSQL services support the pgvector extension. Check the provider version, extension policy, index support, limits, and migration process before choosing one.',
    '{"source": "managed-postgresql", "topic": "vector-search"}'
);
