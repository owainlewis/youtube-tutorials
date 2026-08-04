# Recording Walkthrough: 6 Types of RAG

This is an optional demo sequence. The complete teaching lives in [`../LESSON.md`](../LESSON.md).

## Before Recording

From `tutorials/6-types-of-rag/code`:

```bash
python3 -m unittest discover -s tests -v
uv venv
uv pip install --python .venv/bin/python -e .
cp .env.example .env
docker compose up -d
.venv/bin/python src/seed.py
```

Add a real OpenAI API key to `.env` before seeding.

## Show the Data First

Open:

- `code/data/faq.md`
- `code/data/refund-policy.md`
- `code/sql/schema.sql`
- `code/src/config.py`

Point out that the same small dataset supports every example. The retrieval method changes because the question shape changes.

## Type 1: Complete Documents

Run:

```bash
.venv/bin/python src/01_document_loading.py
```

Notice the difference between loading all documents and selecting one document from the index. The likely failure point is context growth as documents become larger or more numerous.

## Type 2: Full-Text Search

Run:

```bash
.venv/bin/python src/02_full_text_search.py
```

Show `websearch_to_tsquery`, the GIN index in `schema.sql`, and the parameter tuple passed to the database. Exact terms are the strength. Different wording is the failure point.

## Type 3: Vector Search

Run:

```bash
.venv/bin/python src/03_vector_search.py
```

Show the embedding request and `<=>` cosine-distance operator. Similar descriptions are the strength. Price and brand constraints are the failure point.

## Type 4: Hybrid Search

Run:

```bash
.venv/bin/python src/04_hybrid_search.py
```

Open the three SQL common table expressions. Show the keyword rank, vector rank, and RRF merge. Explain that fusion should earn its complexity on an evaluation set.

## Type 5: SQL RAG

Run both variants:

```bash
.venv/bin/python src/05a_sql_rag_parameterized.py
.venv/bin/python src/05b_sql_rag_dynamic.py
```

Compare application-built parameterized SQL with model-generated SQL. The first is bounded and predictable. The second needs real database permissions and query-policy controls before production use.

## Type 6: Agentic RAG

Run:

```bash
.venv/bin/python src/06_agentic_rag.py
```

Show the tool definitions and the loop that feeds tool results back to the model. Watch which tool handles each part of a compound question. The failure point is routing or arguments, not only the final answer.

## Finish With the Tests

Open `code/tests/test_strategies.py`. The tests replace OpenAI and PostgreSQL with deterministic fakes. They prove the application wiring without credentials, while the live demo proves the integrations in the configured environment.

## Reset

```bash
docker compose down --volumes
rm -rf .venv
rm -f .env
```
