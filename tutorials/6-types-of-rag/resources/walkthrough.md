# 6 Types of RAG, Clearly Explained

## What is RAG?

RAG means fetching data and adding it to the prompt.

```python
from openai import OpenAI

client = OpenAI()

def rag_response(user_query: str, context: str) -> str:
    response = client.responses.create(
        model="gpt-5.4",
        instructions="Answer questions using the provided context.",
        input=f"Context:\n{context}\n\nQuestion: {user_query}"
    )
    return response.output_text
```

That's it. The interesting part is **how you get the context**.

---

## The RAG Spectrum

```
Simple ←──────────────────────────────────────→ Smart
Document    Full-Text    Vector    Hybrid    SQL    Agentic
Loading     Search       Search    Search    RAG    RAG
```

Left side: simple, fast, no infrastructure.
Right side: more powerful, more moving parts.

**Start as simple as you can. Move right only when simple breaks.**

---

## Our Demo Setup

An e-commerce shoe store with:

| Data Type | Storage | Example |
|-----------|---------|---------|
| Products (structured) | PostgreSQL table | Name, brand, price, rating, description |
| FAQ (unstructured) | Markdown file | Shipping times, payment methods |
| Refund Policy (unstructured) | Markdown file | Return windows, refund process |

Documents are parsed and chunked using **Docling**, which handles the full pipeline: parse the format, understand the structure, chunk intelligently.

```python
from docling.document_converter import DocumentConverter
from docling.chunking import HybridChunker

converter = DocumentConverter()
result = converter.convert("refund-policy.md")

chunker = HybridChunker(tokenizer="BAAI/bge-small-en-v1.5", max_tokens=512)
chunks = list(chunker.chunk(result.document))
```

Same data, six different retrieval approaches.

---

## Type 1: Document Loading

**Load entire files into the prompt. No database needed.**

```python
def load_documents() -> str:
    docs = []
    for filepath in sorted(DATA_DIR.glob("*.md")):
        content = filepath.read_text()
        docs.append(f"--- {filepath.name} ---\n{content}")
    return "\n\n".join(docs)
```

When to use:
- Small document sets (FAQs, policies, runbooks)
- When you need the FULL document (step-by-step guides, checklists)
- Documents fit within the context window

Demo: "What's your return policy for opened items?"

---

## Type 2: Full-Text Search

**Keyword matching using PostgreSQL tsvector/tsquery.**

```sql
SELECT name, brand, price, description
FROM products
WHERE description_tsv @@ websearch_to_tsquery('english', 'blue running shoes')
ORDER BY ts_rank(description_tsv, websearch_to_tsquery('english', 'blue running shoes')) DESC
```

Works: "blue running shoes" finds products with those exact words.
Breaks: "comfortable shoes for long runs" misses "cushioned" and "supportive".

Keywords match words, not meaning.

---

## Type 3: Vector Search

**Semantic matching using OpenAI embeddings + pgvector.**

```python
response = client.embeddings.create(model="text-embedding-3-small", input=[query])
query_embedding = response.data[0].embedding

cur.execute("""
    SELECT name, brand, price, description,
           1 - (embedding <=> %s::vector) AS similarity
    FROM products
    ORDER BY embedding <=> %s::vector
    LIMIT 5
""", (str(query_embedding), str(query_embedding)))
```

Works: "comfortable shoes for long runs" finds "cushioned midsole", "marathon-ready".
Breaks: "Nike shoes under $100" returns wrong prices and wrong brands.

Vectors match meaning, not exact values.

---

## Type 4: Hybrid Search

**Full-text + vector search combined with Reciprocal Rank Fusion.**

```sql
WITH fts AS (
    SELECT id, ROW_NUMBER() OVER (ORDER BY ts_rank(...) DESC) AS rank_fts
    FROM products WHERE description_tsv @@ websearch_to_tsquery(...)
),
vec AS (
    SELECT id, ROW_NUMBER() OVER (ORDER BY embedding <=> ...) AS rank_vec
    FROM products
)
SELECT *,
    1.0/(60 + rank_fts) + 1.0/(60 + rank_vec) AS rrf_score
FROM fts FULL OUTER JOIN vec ON fts.id = vec.id
ORDER BY rrf_score DESC
```

"Nike running shoes comfortable for long distance"
- Keyword locks in "Nike"
- Vector finds "cushioned", "marathon-ready"
- Combined: Nike shoes that are also comfortable for distance

**This is the production default for most RAG systems.**

Still can't handle: "shoes under $100 with 4+ stars"

---

## Type 5: SQL RAG

**The LLM generates SQL from natural language.**

```python
def generate_sql(question: str) -> str:
    response = client.responses.create(
        model="gpt-5.4",
        instructions=f"Generate a PostgreSQL SELECT query. Schema: {SCHEMA}",
        input=question
    )
    return response.output_text.strip()
```

"Running shoes under $100 with 4+ stars, sorted by price"

```sql
SELECT * FROM products
WHERE category = 'running' AND price < 100 AND rating >= 4
ORDER BY price
```

Precise. No fuzzy matching. Exact filters on exact fields.
Breaks: "Find me something for trail running in wet conditions" (no "wetness" column).

---

## Type 6: Agentic RAG

**The agent has all five tools and picks the right one.**

```python
TOOLS = [
    {"name": "load_document", ...},    # For policy/FAQ questions
    {"name": "full_text_search", ...}, # For keyword queries
    {"name": "vector_search", ...},    # For semantic queries
    {"name": "sql_query", ...},        # For structured filters
]
```

"I want running shoes under $150 but what's your return policy if they don't fit?"

The agent:
1. Calls `sql_query` for "running shoes under $150" (structured data)
2. Calls `load_document` for the return policy (full document needed)
3. Combines both into one answer

**The agent chooses the right retrieval strategy for each part of the question.**

---

## When to Use What

| Type | Best For | Skip If |
|------|----------|---------|
| Document Loading | Small doc sets, full-context needed | Too many/large docs |
| Full-Text Search | Exact keyword matching | Natural language queries |
| Vector Search | Semantic similarity | Exact filters needed |
| Hybrid Search | General purpose (production default) | Simple use case |
| SQL RAG | Structured data, exact filters | Unstructured text only |
| Agentic RAG | Complex multi-part questions | Simple single-source queries |

---

## Key Takeaways

1. RAG is just fetching data and adding it to the prompt. How you fetch is the whole game.
2. Start simple. Document loading works more often than you think.
3. Hybrid search is the safe production default.
4. SQL RAG is underrated. If your data has columns, query it. Don't embed it.
5. Postgres handles full-text search, vector search, and SQL in one database.
6. Agentic RAG ties it all together, but learn the building blocks first.
