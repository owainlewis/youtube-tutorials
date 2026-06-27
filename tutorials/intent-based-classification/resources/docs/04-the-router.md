# The Router

The classifier tells us _what_ the query is. The router decides _what to do about it_.

## The pattern

A router is a function that takes a classified query and sends it to the right retrieval strategy:

```python
def route_query(query: str, intent: Intent) -> list[str]:
    match intent:
        case Intent.CONCEPTUAL:
            return semantic_search(query, top_k=5, chunk_size="large")
        case Intent.PROCEDURAL:
            return hybrid_search(query, alpha=0.5)
        case Intent.FACTUAL:
            return database_lookup(query)
        case Intent.COMPARATIVE:
            return multi_source_search(query)
        case Intent.OUT_OF_SCOPE:
            return []  # Don't retrieve anything
```

That's the core idea. A match statement. Each intent gets its own strategy.

## Building each strategy

In a production system, these strategies connect to real data sources. For this course, we'll use mock implementations that demonstrate the different approaches.

### Semantic search (conceptual queries)

Vector search optimized for broad understanding:

```python
from dataclasses import dataclass


@dataclass
class RetrievalResult:
    """The result of a retrieval operation."""
    chunks: list[str]
    strategy: str
    metadata: dict


def semantic_search(query: str, top_k: int = 3) -> RetrievalResult:
    """
    Semantic search — best for conceptual queries.

    In production, this would:
    1. Embed the query using an embedding model
    2. Search a vector database (Pinecone, Weaviate, Qdrant)
    3. Return chunks ranked by semantic similarity

    We use larger chunks and higher top_k for conceptual queries
    because the answer is often spread across multiple sections.
    """
    # In production: vector_db.search(embed(query), top_k=top_k)
    return RetrievalResult(
        chunks=["[semantic search results would go here]"],
        strategy="semantic_search",
        metadata={"top_k": top_k, "embedding_model": "text-embedding-3-small"},
    )
```

### Hybrid search (procedural queries)

Combines semantic similarity with keyword matching:

```python
def hybrid_search(query: str, alpha: float = 0.5) -> RetrievalResult:
    """
    Hybrid search — best for procedural queries.

    Combines two search approaches:
    1. Semantic search (understands meaning)
    2. Keyword/BM25 search (matches exact terms)

    Alpha controls the balance:
    - alpha=0.0: pure keyword search
    - alpha=0.5: equal weight
    - alpha=1.0: pure semantic search

    For procedural queries, keywords matter. "reset API key" should
    match documents containing those exact terms, not just documents
    about authentication in general.
    """
    return RetrievalResult(
        chunks=["[hybrid search results would go here]"],
        strategy="hybrid_search",
        metadata={"alpha": alpha},
    )
```

### Database lookup (factual queries)

Skip vectors entirely — query structured data directly:

```python
def database_lookup(query: str) -> RetrievalResult:
    """
    Structured data query — best for factual queries.

    In production, this would:
    1. Parse the query to identify what data is needed
    2. Generate a SQL query or call an API
    3. Return formatted results

    This is the big win of routing. Factual queries get answered
    in milliseconds from a database instead of seconds from a
    vector search + LLM pipeline.
    """
    return RetrievalResult(
        chunks=["[database query results would go here]"],
        strategy="database_lookup",
        metadata={"source": "database", "skip_vectors": True},
    )
```

### Multi-source search (comparative queries)

Deliberately fetch information about each item being compared:

```python
def multi_source_search(query: str) -> RetrievalResult:
    """
    Multi-source retrieval — best for comparative queries.

    The key insight: if you search for "Postgres vs MongoDB",
    standard retrieval returns chunks that mention both.
    That's usually one-sided — whichever is more prominent
    in your docs dominates the results.

    Instead, search for each item separately and combine:
    1. Search for "Postgres" → get Postgres-specific chunks
    2. Search for "MongoDB" → get MongoDB-specific chunks
    3. Combine for the LLM to synthesize
    """
    return RetrievalResult(
        chunks=["[results for item A]", "[results for item B]"],
        strategy="multi_source_search",
        metadata={"sources_queried": 2},
    )
```

### Early exit (out of scope)

Don't search. Don't generate. Return immediately:

```python
def early_exit(query: str) -> RetrievalResult:
    """
    Early exit — for out-of-scope queries.

    No retrieval. No LLM generation. Just a canned response.
    This saves tokens, reduces latency, and avoids hallucination.
    """
    return RetrievalResult(
        chunks=["I can only answer questions about our platform."],
        strategy="early_exit",
        metadata={"search_performed": False},
    )
```

## Putting it together

The complete router combines classification and retrieval into a single pipeline:

```python
from openai import OpenAI
from intent_classifier import Intent, QueryClassification, classify_query


def route_query(query: str, client: OpenAI) -> RetrievalResult:
    """Classify a query and route it to the right retrieval strategy."""
    classification = classify_query(query, client)

    match classification.intent:
        case Intent.CONCEPTUAL:
            return semantic_search(query)
        case Intent.PROCEDURAL:
            return hybrid_search(query)
        case Intent.FACTUAL:
            return database_lookup(query)
        case Intent.COMPARATIVE:
            return multi_source_search(query)
        case Intent.OUT_OF_SCOPE:
            return early_exit(query)


def generate_answer(query: str, context: list[str], client: OpenAI) -> str:
    """Generate a final answer from the retrieved context."""
    context_text = "\n\n---\n\n".join(context)

    response = client.responses.create(
        model="gpt-4o-mini",
        input=f"""Answer the user's question based on the provided context.
Be concise and direct. If the context doesn't contain the answer, say so.

Context:
{context_text}

Question: {query}""",
    )

    return response.output_text


def handle_query(query: str, client: OpenAI) -> str:
    """The complete pipeline: classify → route → retrieve → generate."""
    # Step 1: Classify and route
    result = route_query(query, client)

    # Step 2: Early exit for out-of-scope queries
    if result.strategy == "early_exit":
        return result.chunks[0]

    # Step 3: Generate answer from retrieved context
    return generate_answer(query, result.chunks, client)
```

## The match statement

Python 3.10 introduced structural pattern matching (`match`/`case`). It's the cleanest way to route on an enum:

```python
match classification.intent:
    case Intent.CONCEPTUAL:
        return semantic_search(query)
    case Intent.PROCEDURAL:
        return hybrid_search(query)
```

If you're on Python 3.9 or earlier, use `if`/`elif`:

```python
intent = classification.intent
if intent == Intent.CONCEPTUAL:
    return semantic_search(query)
elif intent == Intent.PROCEDURAL:
    return hybrid_search(query)
```

## Strategy parameters

Each strategy has knobs you can tune:

| Strategy | Key parameter | What it controls |
|----------|--------------|-----------------|
| Semantic search | `top_k` | How many chunks to retrieve |
| Hybrid search | `alpha` | Balance between keyword and semantic |
| Database lookup | — | Depends on your schema |
| Multi-source | items | What to search for separately |

In production, these become part of your configuration. You might find that procedural queries work better with `alpha=0.3` (more keyword weight) while conceptual queries need `top_k=7` for enough context.

## What's next

We have a working classifier and router. But how do we know it actually works? Next, we'll build an evaluation framework to test our system.

[Next: Evaluation →](05-evaluation.md)
