-- 04_hybrid_search.sql
-- Hybrid search function combining vector search and full-text search
-- using Reciprocal Rank Fusion (RRF).

CREATE OR REPLACE FUNCTION hybrid_search(
    query_text    TEXT,
    query_embedding vector(1536),
    match_count   INT DEFAULT 10,
    rrf_k         INT DEFAULT 60
)
RETURNS TABLE (
    id        BIGINT,
    content   TEXT,
    rrf_score FLOAT
)
LANGUAGE sql
AS $$
    WITH vector_results AS (
        SELECT
            id,
            ROW_NUMBER() OVER (ORDER BY embedding <=> query_embedding) AS rank
        FROM documents
        ORDER BY embedding <=> query_embedding
        LIMIT match_count
    ),
    fts_results AS (
        SELECT
            id,
            ROW_NUMBER() OVER (
                ORDER BY ts_rank(fts, websearch_to_tsquery('english', query_text)) DESC
            ) AS rank
        FROM documents
        WHERE fts @@ websearch_to_tsquery('english', query_text)
        LIMIT match_count
    ),
    combined AS (
        SELECT
            COALESCE(v.id, f.id) AS id,
            COALESCE(1.0 / (rrf_k + v.rank), 0.0) +
            COALESCE(1.0 / (rrf_k + f.rank), 0.0) AS rrf_score
        FROM vector_results v
        FULL OUTER JOIN fts_results f ON v.id = f.id
    )
    SELECT
        c.id,
        d.content,
        c.rrf_score
    FROM combined c
    JOIN documents d ON c.id = d.id
    ORDER BY c.rrf_score DESC
    LIMIT match_count;
$$;

-- Example call (replace the vector literal with a real embedding):
-- SELECT * FROM hybrid_search(
--     'how does vector search work in PostgreSQL',
--     '[0.1, 0.2, ...]'::vector,
--     10
-- );
