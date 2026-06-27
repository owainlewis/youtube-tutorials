# Chapter 4: Full-Text Search with tsvector

Add keyword search to your documents table with one column and one index.

## The Problem

Embeddings capture meaning, not exact terms. A user searches for "HNSW" -- a specific acronym. The embedding model might map this to something close to "approximate nearest neighbor," but there is no guarantee it will rank the exact HNSW documentation highest. A product code like "pg18" or a version number like "3.2.0" has the same problem.

Full-text search catches exact matches. You want both: semantic similarity for meaning, keyword matching for precision.

## Core Concept

```sql
ALTER TABLE documents
ADD COLUMN fts tsvector
    GENERATED ALWAYS AS (to_tsvector('english', content)) STORED;

CREATE INDEX ON documents USING gin(fts);
```

One new column. One new index. Full-text search is live on the same table that already holds your vectors.

## How It Works

- `tsvector` is PostgreSQL's full-text search data type. It stores a processed representation of the text -- words are normalized (stemmed), stop words are removed, and positions are tracked.
- `GENERATED ALWAYS AS ... STORED` means the column updates automatically whenever `content` changes. Zero application logic required.
- `to_tsvector('english', content)` applies English-language stemming. "running" and "runs" both match "run."
- `GIN` (Generalized Inverted Index) is the index type for full-text search. It maps each word stem to the rows that contain it, making lookups fast.
- `websearch_to_tsquery` converts natural language input into a search query. The user types "vector search PostgreSQL" and it becomes a proper tsquery.
- `@@` is the match operator -- it returns true when a tsvector matches a tsquery.
- `ts_rank` scores how well a document matches the query, so you can order results by relevance.

## Progressive Examples

### Step 1: The fts column and GIN index

The `fts` column and GIN index are created in `sql/01_setup.sql` alongside the documents table:

```sql
CREATE TABLE documents (
    id          BIGSERIAL PRIMARY KEY,
    content     TEXT NOT NULL,
    metadata    JSONB,
    embedding   vector(1536),
    fts         tsvector GENERATED ALWAYS AS (to_tsvector('english', content)) STORED
);

CREATE INDEX ON documents USING gin(fts);
```

The `GENERATED ALWAYS AS ... STORED` column updates automatically whenever `content` changes. Zero application logic required. The GIN index makes lookups fast even on large tables.

If you are adding full-text search to an existing table that does not have the `fts` column, run:

```sql
ALTER TABLE documents
ADD COLUMN fts tsvector
    GENERATED ALWAYS AS (to_tsvector('english', content)) STORED;

CREATE INDEX ON documents USING gin(fts);
```

### Step 2: Run a full-text search query

```sql
SELECT id, content
FROM documents
WHERE fts @@ websearch_to_tsquery('english', 'HNSW indexing')
ORDER BY ts_rank(fts, websearch_to_tsquery('english', 'HNSW indexing')) DESC
LIMIT 5;
```

`websearch_to_tsquery` handles natural language input. The user does not need to know PostgreSQL query syntax -- they just type words.

### Step 4: Combine with metadata filtering

```sql
SELECT id, content
FROM documents
WHERE fts @@ websearch_to_tsquery('english', 'cosine distance')
  AND metadata->>'topic' = 'distance-metrics'
ORDER BY ts_rank(fts, websearch_to_tsquery('english', 'cosine distance')) DESC
LIMIT 5;
```

Standard SQL WHERE clauses work alongside full-text search. Filter by metadata, date, user, or any other column.

## Real-World Example

A complete Python function for full-text search:

```python
import psycopg

def full_text_search(conn, query: str, limit: int = 5) -> list[dict]:
    """Find documents matching the search terms using full-text search."""
    with conn.cursor() as cur:
        cur.execute(
            """
            SELECT id, content,
                   ts_rank(fts, websearch_to_tsquery('english', %s)) AS rank
            FROM documents
            WHERE fts @@ websearch_to_tsquery('english', %s)
            ORDER BY rank DESC
            LIMIT %s
            """,
            (query, query, limit),
        )
        return [
            {"id": row[0], "content": row[1], "rank": row[2]}
            for row in cur.fetchall()
        ]
```

## Common Mistakes

**Using `plainto_tsquery` instead of `websearch_to_tsquery`.** `plainto_tsquery` treats all words as AND. `websearch_to_tsquery` handles natural phrases, OR operators, and quoted strings. Use `websearch_to_tsquery` for user-facing search.

**Forgetting the GIN index.** Without it, `@@` still works but does a sequential scan. On a table with millions of rows, this means seconds instead of milliseconds.

## Key Takeaways

- `tsvector` generated columns maintain themselves automatically -- no application code needed.
- GIN indexes make full-text search fast on large tables.
- `websearch_to_tsquery` handles natural language input from users.
- Full-text search lives on the same table as your vectors. No separate service.
- Adding full-text search to an existing table takes two SQL statements and changes nothing else.

## Learn More

- [PostgreSQL: Full-Text Search](https://www.postgresql.org/docs/current/textsearch.html)
- [PostgreSQL: Generated Columns](https://www.postgresql.org/docs/current/ddl-generated-columns.html)
- [PostgreSQL: GIN Indexes](https://www.postgresql.org/docs/current/gin.html)

## What's Next

You now have two search capabilities on the same table: vector search for meaning, full-text search for keywords. The next chapter combines them into hybrid search using Reciprocal Rank Fusion.
