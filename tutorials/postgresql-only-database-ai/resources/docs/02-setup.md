# Chapter 2: Setup -- Docker, pgvector, and the Documents Table

Get PostgreSQL running with pgvector and create a vector-ready documents table in three steps.

## The Problem

You want to store and search embeddings, but setting up a vector database feels like a project in itself. SDKs to learn, APIs to authenticate, data to migrate. You already have PostgreSQL. You just need to enable vector support.

## Core Concept

A few SQL statements get you from zero to a working vector database with full-text search:

```sql
CREATE EXTENSION vector;

CREATE TABLE documents (
    id          BIGSERIAL PRIMARY KEY,
    content     TEXT NOT NULL,
    metadata    JSONB,
    embedding   vector(1536),
    fts         tsvector GENERATED ALWAYS AS (to_tsvector('english', content)) STORED
);

CREATE INDEX ON documents
USING hnsw (embedding vector_cosine_ops)
WITH (m = 16, ef_construction = 64);

CREATE INDEX ON documents USING gin(fts);
```

One extension. One table. Two indexes. That is the entire setup.

## How It Works

- `CREATE EXTENSION vector` activates pgvector. The `pgvector/pgvector:pg18` Docker image ships with it pre-installed -- you just need to enable it.
- `vector(1536)` is a native column type. The number 1536 matches the dimensionality of OpenAI's `text-embedding-3-small` model. If you use a different embedding model, change the number to match.
- `HNSW` (Hierarchical Navigable Small World) is an approximate nearest neighbor index. It builds a multi-layer graph of vectors so queries only visit a small fraction of the data. The result: fast lookups with high recall.
- `vector_cosine_ops` tells the index to optimize for cosine distance queries. This is the standard choice for text embeddings.
- `m = 16` controls how many connections each node has in the graph. Higher values improve recall but use more memory. 16 is a solid default.
- `ef_construction = 64` controls how many candidates the algorithm considers when building the index. Higher values produce a better index but take longer to build. 64 works well for most datasets.
- At query time, `hnsw.ef_search` controls the recall/latency tradeoff. The default is 40. For higher recall, increase it before querying: `SET hnsw.ef_search = 100;`. This is the most important tuning knob for production workloads.

## Progressive Examples

### Step 1: Start PostgreSQL with pgvector

Use Docker Compose to start PostgreSQL. The SQL files in the `sql/` directory run automatically on first boot:

```bash
docker compose up -d
```

The `docker-compose.yml` mounts `./sql` into `/docker-entrypoint-initdb.d`, so PostgreSQL executes the setup SQL on startup.

If you prefer to run PostgreSQL without Docker Compose:

```bash
docker run -d \
  --name pgvector-demo \
  -e POSTGRES_PASSWORD=postgres \
  -p 5432:5432 \
  pgvector/pgvector:pg18
```

### Step 2: Connect and enable pgvector

```bash
psql -h localhost -U postgres
```

```sql
CREATE EXTENSION vector;
```

### Step 3: Create the documents table

```sql
CREATE TABLE documents (
    id          BIGSERIAL PRIMARY KEY,
    content     TEXT NOT NULL,
    metadata    JSONB,
    embedding   vector(1536),
    fts         tsvector GENERATED ALWAYS AS (to_tsvector('english', content)) STORED
);
```

Five columns. `id` is an auto-incrementing primary key. `content` holds the document text. `metadata` stores structured attributes as JSONB (source, topic, date -- whatever you need). `embedding` holds the 1536-dimensional vector. `fts` is a generated column that PostgreSQL maintains automatically for full-text search -- it updates whenever `content` changes.

### Step 4: Create the HNSW index

```sql
CREATE INDEX ON documents
USING hnsw (embedding vector_cosine_ops)
WITH (m = 16, ef_construction = 64);
```

Without this index, every query scans every row. With HNSW, queries return in milliseconds even on large tables.

## Real-World Example

After running `docker compose up -d`, the full setup SQL runs automatically. You can verify it:

```bash
psql -h localhost -U postgres -c "\d documents"
```

Expected output:

```
                                      Table "public.documents"
  Column   |     Type      | Collation | Nullable |               Default
-----------+---------------+-----------+----------+--------------------------------------
 id        | bigint        |           | not null | nextval('documents_id_seq'::regclass)
 content   | text          |           | not null |
 metadata  | jsonb         |           |          |
 embedding | vector(1536)  |           |          |
 fts       | tsvector      |           |          | generated always as stored
Indexes:
    "documents_pkey" PRIMARY KEY, btree (id)
    "documents_embedding_idx" hnsw (embedding vector_cosine_ops)
    "documents_fts_idx" gin (fts)
```

## Common Mistakes

**Using the wrong vector dimensions.** If your embedding model produces 768-dimensional vectors but your column is `vector(1536)`, inserts will fail. Always match the column dimension to your model.

**Forgetting the index.** Without HNSW, vector queries do a sequential scan. This is fine for a few thousand rows but becomes unusable as your table grows. Always create the index.

**Using IVFFlat instead of HNSW.** IVFFlat is an older index type in pgvector. It uses k-means clustering at index build time, which means data must already exist in the table before you create the index. It generally provides lower recall than HNSW. Use HNSW unless you have a specific reason not to.

**Creating the HNSW index before bulk loading data.** For large datasets, it is faster to load the data first and then create the index. Each insert into a table with an existing HNSW index must update the graph structure. For the small dataset in this tutorial it does not matter, but for production bulk loads, always load first, index second.

## Key Takeaways

- `pgvector/pgvector:pg18` gives you PostgreSQL with pgvector pre-installed.
- `CREATE EXTENSION vector` is the only setup step.
- `vector(1536)` is a native column type -- it works with standard SQL.
- HNSW indexes make vector queries fast. Use `m = 16, ef_construction = 64` as defaults.
- The `docker-compose.yml` in this repo runs the setup SQL automatically on first boot.

## Learn More

- [pgvector: Creating an HNSW index](https://github.com/pgvector/pgvector#hnsw)
- [PostgreSQL JSONB documentation](https://www.postgresql.org/docs/current/datatype-json.html)
- [pgvector Docker images](https://hub.docker.com/r/pgvector/pgvector)

## What's Next

With the table and index in place, you are ready to run vector similarity queries. The next chapter covers the cosine distance operator and how to search by semantic similarity.
