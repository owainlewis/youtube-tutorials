# 6 Types of RAG, Clearly Explained

Real code examples showing six retrieval strategies for RAG, from simple document loading to agentic search.

**Stack:** OpenAI (GPT-5.4 + text-embedding-3-small), PostgreSQL + pgvector, Docling

## Setup

### 1. Start PostgreSQL

```bash
docker compose up -d
```

### 2. Install dependencies

```bash
uv sync
```

### 3. Set environment variables

```bash
cp .env.example .env
# Edit .env with your API keys
```

### 4. Seed the database

```bash
uv run src/seed.py
```

## Run the examples

Each file is self-contained. Run them in order to follow the progression:

```bash
uv run src/01_document_loading.py   # Load full docs into prompt
uv run src/02_full_text_search.py   # PostgreSQL keyword search
uv run src/03_vector_search.py      # OpenAI embeddings + pgvector semantic search
uv run src/04_hybrid_search.py      # Combined FTS + vector with RRF
uv run src/05_sql_rag.py            # LLM generates SQL queries
uv run src/06_agentic_rag.py        # Agent picks the right strategy
```

## The Spectrum

```
Simple ---------> Smart
01  02  03  04  05  06
```

Start simple. Move right only when simple breaks.
