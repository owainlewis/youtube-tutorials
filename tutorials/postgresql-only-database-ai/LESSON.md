# PostgreSQL for RAG

This tutorial builds a small RAG application with PostgreSQL, pgvector, FastAPI, and OpenAI.

The useful idea is not that PostgreSQL should be the only database in every AI system. It is that PostgreSQL can own relational data, full-text search, and vector retrieval in one place when that fits the workload. You still need application code for model calls, request handling, retrieval policy, evaluation, and operations.

## Opening Script

This is a practical guide to building RAG with PostgreSQL and pgvector. A lot of RAG examples start by adding a separate vector database before they have proved that they need one. In this tutorial, we will build the retrieval layer with PostgreSQL, combine vector and full-text search, and connect it to a small FastAPI application. I will also show you what PostgreSQL handles, what stays in the application, and where this design stops being a sensible default. All of the code and verification commands are included in the repository. So, let's get into it.

## What You Will Build

The sample answers questions over a small set of fictitious support documents.

```mermaid
sequenceDiagram
    participant Browser
    participant App as FastAPI application
    participant Model as OpenAI API
    participant DB as PostgreSQL and pgvector

    Browser->>App: POST /chat with a question
    App->>Model: Create a query embedding
    Model-->>App: 1536-value vector
    App->>DB: hybrid_search(question, vector, 5)
    DB-->>App: Ranked documents
    App->>Model: Question plus retrieved context
    Model-->>App: Streamed answer
    App-->>Browser: Streamed text
```

There are two external systems at runtime:

- PostgreSQL stores documents and performs retrieval.
- OpenAI creates embeddings and generates the answer.

The browser and FastAPI code connect those systems. This is a teaching sample, not a complete production service.

## Start With The Boundary

Calling this a PostgreSQL RAG system does not mean PostgreSQL does every job.

| Responsibility | PostgreSQL | Application |
| --- | --- | --- |
| Store document text and metadata | Yes | Chooses what to ingest |
| Store embedding vectors | Yes, through pgvector | Creates the embeddings |
| Full-text search | Yes | Chooses the query and result count |
| Vector search | Yes | Supplies a compatible query vector |
| Merge ranked results | Yes, in this sample's SQL function | Chooses whether RRF is appropriate |
| Call an embedding or chat model | No | Yes |
| Build prompts and stream responses | No | Yes |
| Authentication, authorization, rate limits, and abuse controls | No | Yes |
| Evaluate retrieval and answer quality | No | Yes |
| Backups, monitoring, capacity planning, and recovery | Needs operating | Needs operating |

This boundary is the main architectural decision. Keeping retrieval in PostgreSQL removes a data synchronization path. It does not remove the need to operate the database or test the application.

## Project Map

Run all commands in this lesson from `tutorials/postgresql-only-database-ai/code` unless a command says otherwise.

```text
code/
├── .env.example
├── docker-compose.yml
├── pyproject.toml
├── start.sh
├── verify_database.sh
├── verify_offline.py
├── sql/
│   ├── 01_setup.sql
│   ├── 02_vector_search.sql
│   ├── 03_full_text_search.sql
│   ├── 04_hybrid_search.sql
│   └── 05_seed_data.sql
└── src/
    ├── main.py
    ├── seed.py
    └── static/index.html
```

The SQL files have distinct roles:

| File | Role | Runs during first Docker initialization |
| --- | --- | --- |
| `sql/01_setup.sql` | Enable pgvector, create the table and indexes | Yes |
| `sql/02_vector_search.sql` | Commented reference query | Yes, but contains comments only |
| `sql/03_full_text_search.sql` | Commented reference query | Yes, but contains comments only |
| `sql/04_hybrid_search.sql` | Create the hybrid search function | Yes |
| `sql/05_seed_data.sql` | Insert text-only rows for database inspection | Yes |

Docker's PostgreSQL entrypoint reads these files in filename order when it creates an empty data volume. It does not run them again on every container start.

## Prerequisites

You need:

- Python 3.12 or newer
- [uv](https://docs.astral.sh/uv/)
- Docker with Docker Compose
- an OpenAI API key for seeding embeddings and using chat

The offline verifier needs only Python. The database verifier needs Docker, but it does not need an API key.

## 1. Configure The Application

From the repository root:

```bash
cd tutorials/postgresql-only-database-ai/code
cp .env.example .env
```

Edit `.env` and replace the placeholder key:

```dotenv
OPENAI_API_KEY=replace-with-your-key
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/postgres
OPENAI_EMBEDDING_MODEL=text-embedding-3-small
OPENAI_CHAT_MODEL=gpt-4o
```

The schema uses `vector(1536)`, so the embedding model must return 1536 values. If you change the embedding model or its dimensions, update `sql/01_setup.sql` and recreate the database before seeding.

Install the Python dependencies:

```bash
uv sync
```

This repo does not commit generated lockfiles. `uv` may create a local ignored `uv.lock` while resolving the environment.

## 2. Create The Database And Apply The SQL

Start the database and wait for its health check:

```bash
docker compose up -d --wait db
```

On a fresh volume, Docker applies the files under `code/sql/` in order. This is the migration path for this small sample.

Inspect the extension, table, indexes, function, and initial rows:

```bash
docker compose exec -T db psql -U postgres -d postgres -c "SELECT extname FROM pg_extension WHERE extname = 'vector';"
docker compose exec -T db psql -U postgres -d postgres -c "\d documents"
docker compose exec -T db psql -U postgres -d postgres -c "\df hybrid_search"
docker compose exec -T db psql -U postgres -d postgres -c "SELECT id, metadata->>'topic' AS topic FROM documents ORDER BY id LIMIT 5;"
```

Expected evidence:

- the extension query returns `vector`
- the table contains `content`, `metadata`, `embedding`, and generated `fts` columns
- the table has HNSW and GIN indexes
- PostgreSQL lists a `hybrid_search` function
- the final query returns the text-only inspection rows from `sql/05_seed_data.sql`

The database verifier performs these structural checks for you:

```bash
./verify_database.sh
```

## 3. Understand The Schema

The source of truth is `code/sql/01_setup.sql`:

```sql
CREATE EXTENSION IF NOT EXISTS vector;

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

Each part has one job:

- `content` stores the text passed to retrieval and generation.
- `metadata` stores fields you may later use for filtering or authorization.
- `embedding` stores one 1536-value vector per embedded document.
- `fts` is generated from `content` for PostgreSQL full-text search.
- the HNSW index supports approximate cosine-distance search.
- the GIN index supports full-text matching.

The schema leaves `embedding` nullable so `sql/05_seed_data.sql` can create rows without calling an external API. Those rows are useful for inspecting full-text search. `src/seed.py` replaces them with embedded rows before the full application runs.

## 4. Understand The Three Retrieval Steps

### Vector search

`code/sql/02_vector_search.sql` documents the query used for semantic similarity:

```sql
SELECT id, content, 1 - (embedding <=> query_vector) AS similarity
FROM documents
ORDER BY embedding <=> query_vector
LIMIT 5;
```

The `<=>` operator returns cosine distance. The application must create the query vector with the same embedding model and dimensions used for the documents.

### Full-text search

`code/sql/03_full_text_search.sql` documents the keyword path:

```sql
SELECT id, content
FROM documents
WHERE fts @@ websearch_to_tsquery('english', 'search terms')
ORDER BY ts_rank(fts, websearch_to_tsquery('english', 'search terms')) DESC
LIMIT 5;
```

This path helps when exact words, identifiers, product names, or error codes matter.

### Hybrid search

`code/sql/04_hybrid_search.sql` creates one SQL function that ranks vector results and full-text results, then combines their ranks with Reciprocal Rank Fusion.

```text
rrf_score = 1 / (rrf_k + vector_rank)
          + 1 / (rrf_k + text_rank)
```

The function returns documents ordered by the combined score. RRF is one simple fusion policy, not a guarantee of better retrieval. Evaluate its result against vector-only and text-only baselines using representative questions from your application.

## 5. Seed Embeddings

The initial SQL seed rows do not contain embeddings. Replace them with the twenty sample documents and OpenAI embeddings:

```bash
uv run python src/seed.py
```

Expected output ends with:

```text
Seeded 20 documents with embeddings.
```

Confirm the result:

```bash
docker compose exec -T db psql -U postgres -d postgres -c "SELECT count(*) AS documents, count(embedding) AS embeddings FROM documents;"
```

Both counts should be `20`.

`src/seed.py` deletes the current rows before inserting the sample set. Do not reuse that behavior for a production ingestion pipeline. A real pipeline needs stable document identifiers, chunk versioning, retries, and deliberate update and deletion rules.

## 6. Run And Inspect The App

Start FastAPI:

```bash
uv run fastapi dev src/main.py
```

Open [http://localhost:8000](http://localhost:8000) and ask a question represented by the sample documents, such as:

```text
How do I cancel my subscription?
```

Watch the server terminal for request failures. Inspect database rows separately with:

```bash
docker compose exec -T db psql -U postgres -d postgres -c "SELECT id, metadata, left(content, 80) AS preview FROM documents ORDER BY id;"
```

The application flow in `code/src/main.py` is deliberately small:

1. Validate the incoming message.
2. Ask OpenAI for a query embedding.
3. Call PostgreSQL's `hybrid_search` function.
4. Put the returned document text into the system message.
5. Stream the model response to the browser.

This proves the wiring. It does not prove that every answer is correct or safe.

## 7. Verify Without Credentials

Run the static verifier from `code/`:

```bash
python3 verify_offline.py
```

It checks:

- Python syntax
- the expected SQL and application files
- schema columns and vector dimensions
- the HNSW and GIN index definitions
- the hybrid search function and its two ranked inputs
- Docker's SQL mount and PostgreSQL health check
- consistency between documented model settings and source code

This check does not parse SQL with PostgreSQL and cannot prove model behavior. Run `./verify_database.sh` when Docker is available, then use the app manually when an API key is available.

From the repository root, the same offline check is included in:

```bash
just test-offline
just check
```

## Reset And Repeat

Stop the app with `Ctrl+C`. To stop PostgreSQL without deleting data:

```bash
docker compose down
```

To remove the tutorial database volume and reapply all SQL files from a clean state:

```bash
docker compose down -v
docker compose up -d --wait db
```

The `-v` command deletes this Compose project's database volume. Use it only when you want to discard the tutorial data.

To remove the local Python environment and ignored resolution files:

```bash
rm -rf .venv uv.lock
```

Run that command only from `tutorials/postgresql-only-database-ai/code`.

## Where This Design Fits

PostgreSQL with pgvector is worth evaluating when:

- the application already uses PostgreSQL
- vector data belongs in the same transactions as relational records
- metadata filters and full-text search are important
- one operational data store is simpler for the current team
- measured retrieval quality and latency meet the product's requirements

Evaluate another retrieval service when:

- your measured scale, latency, throughput, or availability targets do not fit the PostgreSQL deployment you can operate
- a required index, filtering mode, replication model, or managed service feature is missing
- retrieval needs independent scaling or isolation from transactional traffic
- the team has evidence that a specialized system performs better for the real workload

There is no useful universal row-count threshold. Vector dimensions, index settings, filters, hardware, concurrency, data distribution, and recall targets all affect the result. Benchmark representative data and queries before making a production decision.

## Production Work Still Missing

Before using this shape in a real product, add at least:

- authentication and authorization before retrieval
- tenant and document access filters in SQL
- ingestion with stable IDs, chunking rules, retries, and deletions
- prompt-injection handling for retrieved content
- retrieval and answer evaluations
- timeouts, retry limits, logging, metrics, and tracing
- connection pool and query load tests
- backups, restore tests, schema migrations, and deployment controls
- rate limits, cost limits, and user-facing error handling
- source citations if users need to verify answers

The sample also sends retrieved text to an external model provider. Review privacy, retention, and data-processing requirements before using sensitive data.

## Summary

- The one thing to remember: PostgreSQL can keep relational, full-text, and vector retrieval together, while the application still owns the AI workflow.
- The honest limitation: this sample proves the architecture and commands, not production performance or answer quality.
- What to try next: run the offline verifier, inspect a clean database, then evaluate retrieval with questions that represent your product.

## References

- [pgvector](https://github.com/pgvector/pgvector)
- [PostgreSQL full-text search](https://www.postgresql.org/docs/current/textsearch.html)
- [Psycopg connection pools](https://www.psycopg.org/psycopg3/docs/advanced/pool.html)
- [FastAPI streaming responses](https://fastapi.tiangolo.com/advanced/custom-response/)

## License

Licensed under the [MIT License](../../LICENSE).
