-- 05_seed_data.sql
-- Sample documents for testing. These have no embeddings.
-- For real embeddings, run: uv run src/seed.py
--
-- Note: rows without embeddings will appear in full-text search results
-- but not in vector or hybrid search results.

INSERT INTO documents (content, metadata) VALUES
(
    'pgvector is a PostgreSQL extension that adds support for vector similarity search. It allows you to store embeddings as a native column type and query them using distance operators like cosine distance, inner product, and L2 distance.',
    '{"source": "pgvector-docs", "topic": "overview"}'
),
(
    'HNSW (Hierarchical Navigable Small World) is an approximate nearest neighbor algorithm. In pgvector, you create an HNSW index with CREATE INDEX USING hnsw. It provides fast query times with high recall, making it suitable for production workloads.',
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
    'Hybrid search combines vector similarity search with keyword-based full-text search. Reciprocal Rank Fusion (RRF) merges ranked results from both methods. Documents scoring well in both lists rise to the top, improving retrieval quality over either method alone.',
    '{"source": "ai-engineering", "topic": "hybrid-search"}'
),
(
    'The text-embedding-3-small model from OpenAI produces 1536-dimensional vectors. These embeddings capture semantic meaning, so similar concepts have similar vector representations regardless of the exact words used.',
    '{"source": "openai-docs", "topic": "embeddings"}'
),
(
    'PostgreSQL has been in production for over 35 years. It supports ACID transactions, JSONB for semi-structured data, full-text search, and with pgvector, dense vector embeddings. This makes it a unified data platform for AI applications.',
    '{"source": "postgresql-docs", "topic": "overview"}'
),
(
    'IVFFlat is an older indexing method in pgvector that partitions vectors into lists using k-means clustering at index build time. While it uses less memory than HNSW, data must exist in the table before the index is created, and it generally provides lower recall. HNSW is recommended for most production use cases.',
    '{"source": "pgvector-docs", "topic": "indexing"}'
),
(
    'Supabase provides hosted PostgreSQL with pgvector pre-installed. All standard pgvector SQL works on Supabase without modification. This gives you a managed vector database without running your own infrastructure.',
    '{"source": "supabase-docs", "topic": "vector-search"}'
);
