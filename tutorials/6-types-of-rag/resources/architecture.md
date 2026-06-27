# Architecture: 6 Types of RAG

## The Domain: ShopMax E-Commerce Store

```
┌─────────────────────────────────────────────────────────┐
│                     ShopMax Data                         │
├────────────────────────┬────────────────────────────────┤
│   Structured (SQL)     │   Unstructured (Documents)     │
│                        │                                │
│   products table       │   faq.md                       │
│   ├── name             │   ├── Shipping                 │
│   ├── brand            │   ├── Orders                   │
│   ├── category         │   └── Products                 │
│   ├── price            │                                │
│   ├── rating           │   refund-policy.md             │
│   ├── color            │   ├── Return Window            │
│   ├── description      │   ├── Opened Items             │
│   ├── description_tsv  │   ├── Refund Process           │
│   └── embedding        │   ├── Exchanges                │
│                        │   ├── Sale Items               │
│   12 products          │   └── Defective Items          │
│   5 brands             │                                │
│   4 categories         │   ~2 pages total               │
└────────────────────────┴────────────────────────────────┘
```

## The Spectrum

```
Simple ←───────────────────────────────────────────────→ Smart

  1              2              3            4           5          6
Document     Full-Text      Vector       Hybrid       SQL      Agentic
Loading       Search        Search       Search       RAG        RAG

No DB        Postgres       pgvector     FTS +       LLM →     Agent
needed       tsvector      embeddings    vector       SQL      picks
                                          RRF                  tools
```

---

## Type 1: Document Loading

```
┌──────────┐     ┌──────────────┐     ┌─────────┐     ┌──────────┐
│   User   │────→│  Load Files  │────→│  Prompt  │────→│   LLM    │
│ Question │     │  from disk   │     │ Context  │     │ (GPT-5.4) │
└──────────┘     └──────────────┘     │ + Query  │     └────┬─────┘
                                      └──────────┘          │
                  faq.md ─────────────────┘                  │
                  refund-policy.md ───────┘                  │
                                                             ▼
                                                        ┌──────────┐
                                                        │  Answer  │
                                                        └──────────┘
```

**Flow:** Read files from disk -> stuff into prompt -> ask LLM
**Infrastructure:** None. Just files and an API key.
**Best query:** "What's your return policy for opened items?"

---

## Type 2: Full-Text Search

```
┌──────────┐     ┌──────────────────┐     ┌─────────┐     ┌──────────┐
│   User   │────→│    PostgreSQL    │────→│  Prompt  │────→│   LLM    │
│ Question │     │                  │     │ Results  │     │ (GPT-5.4) │
└──────────┘     │  websearch_to_  │     │ + Query  │     └────┬─────┘
                 │  tsquery(query)  │     └──────────┘          │
                 │                  │                            │
                 │  Matches exact   │                            ▼
                 │  words in        │                       ┌──────────┐
                 │  description_tsv │                       │  Answer  │
                 └──────────────────┘                       └──────────┘
```

**Flow:** Convert query to tsquery -> match against tsvector index -> rank by ts_rank
**Infrastructure:** PostgreSQL (built-in, no extensions)
**Best query:** "blue running shoes"
**Breaks on:** "comfortable shoes for long runs" (no literal match for "comfortable")

---

## Type 3: Vector Search

```
┌──────────┐     ┌──────────────┐     ┌──────────────────┐     ┌─────────┐     ┌──────────┐
│   User   │────→│    OpenAI    │────→│    PostgreSQL     │────→│  Prompt  │────→│   LLM    │
│ Question │     │  Embeddings  │     │     pgvector      │     │ Results  │     │ (GPT-5.4) │
└──────────┘     │              │     │                   │     │ + Query  │     └────┬─────┘
                 │  text-embed  │     │  Cosine distance  │     └──────────┘          │
                 │  -3-small    │     │  embedding <=>    │                            │
                 │              │     │  query_vector     │                            ▼
                 │  Query → Vec │     │                   │                       ┌──────────┐
                 └──────────────┘     │  Ranked by        │                       │  Answer  │
                                      │  similarity       │                       └──────────┘
                                      └──────────────────┘
```

**Flow:** Embed query -> cosine similarity search in pgvector -> rank by distance
**Infrastructure:** PostgreSQL + pgvector extension, OpenAI embeddings API
**Best query:** "comfortable shoes for long distance running"
**Breaks on:** "Nike shoes under $100" (vectors don't understand price filters)

---

## Type 4: Hybrid Search (RRF)

```
┌──────────┐
│   User   │
│ Question │
└────┬─────┘
     │
     ├───────────────────────────────────┐
     │                                   │
     ▼                                   ▼
┌────────────────┐              ┌────────────────┐
│  Full-Text     │              │    Vector       │
│  Search        │              │    Search       │
│                │              │                 │
│  rank_fts = 1  │              │  rank_vec = 1   │
│  rank_fts = 2  │              │  rank_vec = 2   │
│  rank_fts = 3  │              │  rank_vec = 3   │
└───────┬────────┘              └───────┬─────────┘
        │                               │
        └───────────┬───────────────────┘
                    │
                    ▼
        ┌───────────────────────┐
        │  Reciprocal Rank      │
        │  Fusion (RRF)         │
        │                       │
        │  score = 1/(60+rank_  │
        │  fts) + 1/(60+rank_   │     ┌─────────┐     ┌──────────┐
        │  vec)                 │────→│  Prompt  │────→│   LLM    │
        │                       │     │ + Query  │     │ (GPT-5.4) │
        │  Merged & re-ranked   │     └──────────┘     └──────────┘
        └───────────────────────┘
```

**Flow:** Run both FTS and vector search -> merge with RRF scoring -> rank combined results
**Infrastructure:** PostgreSQL + pgvector (same DB, one query)
**Best query:** "Nike running shoes comfortable for long distance"
**Breaks on:** "shoes under $100 with 4+ stars" (structured filters)

---

## Type 5: SQL RAG

```
┌──────────┐     ┌──────────────┐     ┌──────────────────┐     ┌─────────┐     ┌──────────┐
│   User   │────→│     LLM      │────→│    PostgreSQL     │────→│  Prompt  │────→│   LLM    │
│ Question │     │  (generate   │     │                   │     │ Results  │     │ (answer) │
└──────────┘     │   SQL)       │     │  SELECT * FROM    │     │ + Query  │     └────┬─────┘
                 │              │     │  products WHERE   │     └──────────┘          │
                 │  + schema    │     │  price < 100      │                            │
                 │              │     │  AND rating >= 4  │                            ▼
                 │  "Natural    │     │  ORDER BY price   │                       ┌──────────┐
                 │   language   │     │                   │                       │  Answer  │
                 │   → SQL"     │     └──────────────────┘                       └──────────┘
                 └──────────────┘
```

**Flow:** LLM generates SQL from question + schema -> execute query -> LLM answers from results
**Infrastructure:** PostgreSQL (no embeddings needed)
**Two LLM calls:** One to generate SQL, one to answer with results.
**Best query:** "Running shoes under $100 with at least 4 stars, sorted by price"
**Breaks on:** "something good for trail running in wet conditions" (no "wetness" column)

---

## Type 6: Agentic RAG

```
┌──────────┐     ┌────────────────────────────────────────────────┐
│   User   │────→│                   Agent (LLM)                  │
│ Question │     │                                                │
└──────────┘     │  "I want running shoes under $150 but what's   │
                 │   your return policy if they don't fit?"        │
                 │                                                │
                 │  Thinks: This has two parts...                  │
                 │                                                │
                 │  ┌─────────────┐  ┌─────────────────────────┐  │
                 │  │ Tool Call 1 │  │ Tool Call 2             │  │
                 │  │ sql_query   │  │ load_document           │  │
                 │  │ "SELECT ..  │  │ "refund-policy.md"      │  │
                 │  │  WHERE      │  │                         │  │
                 │  │  price<150" │  │                         │  │
                 │  └──────┬──────┘  └────────────┬────────────┘  │
                 │         │                      │               │
                 │         ▼                      ▼               │
                 │  ┌─────────────┐  ┌─────────────────────────┐  │
                 │  │ Products:   │  │ Full refund policy      │  │
                 │  │ TrailBlazer │  │ document loaded         │  │
                 │  │ SprintForce │  │                         │  │
                 │  │ EnduroRun   │  │                         │  │
                 │  └─────────────┘  └─────────────────────────┘  │
                 │                                                │
                 │  Combines both into one coherent answer        │
                 └───────────────────────┬────────────────────────┘
                                         │
                                         ▼
                                    ┌──────────┐
                                    │  Answer  │
                                    └──────────┘

Available tools:
┌──────────────────┬──────────────────┬──────────────────┬──────────────────┐
│  load_document   │ full_text_search │  vector_search   │    sql_query     │
│                  │                  │                  │                  │
│  Load full docs  │  Keyword match   │  Semantic match  │  Structured      │
│  (FAQ, policies) │  (brand, color)  │  (natural lang)  │  filters         │
└──────────────────┴──────────────────┴──────────────────┴──────────────────┘
```

**Flow:** Agent receives question -> decides which tools to call -> executes tools -> synthesizes answer
**Infrastructure:** All of the above + tool definitions
**Best query:** Multi-part questions spanning structured and unstructured data
**The payoff:** The agent chooses the right retrieval strategy. You built the tools. It picks the right one.

---

## Summary: When to Use What

```
┌─────────────────────────────────────────────────────────────────┐
│                                                                 │
│  "Do I need search at all?"                                     │
│       │                                                         │
│       ├── No, docs fit in context ──→ Type 1: Document Loading  │
│       │                                                         │
│       └── Yes ──→ "Is the data structured?"                     │
│                       │                                         │
│                       ├── Yes (columns, filters) ──→ Type 5: SQL│
│                       │                                         │
│                       └── No (text, descriptions)               │
│                               │                                 │
│                               ├── Exact terms? ──→ Type 2: FTS  │
│                               │                                 │
│                               ├── Meaning? ──→ Type 3: Vector   │
│                               │                                 │
│                               ├── Both? ──→ Type 4: Hybrid      │
│                               │                                 │
│                               └── Complex/multi-part?           │
│                                       └──→ Type 6: Agentic      │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

## Tech Stack

| Component | Tool | Why |
|-----------|------|-----|
| LLM | OpenAI GPT-5.4 | One provider for chat + embeddings |
| Embeddings | text-embedding-3-small (1536 dims) | Same API key, good quality |
| Database | PostgreSQL 17 + pgvector | FTS + vectors + SQL in one DB |
| Document parsing | Docling | Handles real document formats |
| Language | Python 3.12+ | uv for package management |
| Infrastructure | Docker Compose | One command: `docker compose up -d` |
