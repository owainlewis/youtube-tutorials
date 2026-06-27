# Query Types

Before you can classify anything, you need to know what you're classifying into.

## Choosing your categories

The categories depend on your domain. A customer support bot has different intents than a code documentation system. But most RAG systems share a common set of query patterns.

Here are five that cover the majority of cases:

| Intent | What the user wants | Example |
|--------|-------------------|---------|
| **Conceptual** | Understand a concept | "What is OAuth?" |
| **Procedural** | Step-by-step instructions | "How do I reset my API key?" |
| **Factual** | A specific data point | "What was Q3 revenue?" |
| **Comparative** | Compare options | "Postgres vs MongoDB?" |
| **Out of scope** | Something you can't help with | "What's the weather?" |

## Why these five

Each one needs a fundamentally different retrieval strategy. That's the whole point — if two intents would be handled the same way, they should be the same category.

### Conceptual

The user wants to understand something. "What is X?", "Explain Y", "Why do we use Z?"

These queries need **broad context**. The answer isn't in one chunk — it's spread across multiple sections. You want semantic search with larger chunks so the LLM gets enough context to synthesize an explanation.

```python
# Conceptual queries need broad context
def handle_conceptual(query: str) -> list[str]:
    return semantic_search(query, top_k=5, chunk_size="large")
```

### Procedural

The user wants to do something. "How do I X?", "Steps to Y", "Configure Z".

These queries need **keyword precision**. The specific technical terms matter — "reset", "API key", "deploy", "configure". Pure semantic search might return conceptually related results that don't contain the actual commands or steps.

Hybrid search (combining semantic similarity with keyword matching) works best here.

```python
# Procedural queries need keyword precision
def handle_procedural(query: str) -> list[str]:
    return hybrid_search(query, alpha=0.5)  # 50% semantic, 50% keyword
```

### Factual

The user wants a specific data point. "How many users?", "What was revenue?", "What's the rate limit?"

These queries often have answers in **structured data** — databases, spreadsheets, config files. Searching a vector database for "Q3 revenue" is wasteful when the answer is a single row in a table.

```python
# Factual queries should skip vectors entirely
def handle_factual(query: str) -> list[str]:
    return database_query(query)  # SQL, not embeddings
```

### Comparative

The user wants to compare options. "X vs Y?", "Should I use A or B?", "What's the difference?"

These queries need **information from multiple sources**. If you search for "Postgres vs MongoDB", most retrieval systems return chunks about whichever one is more prominent in your docs. You need to deliberately fetch information about both options.

```python
# Comparative queries need both sides
def handle_comparative(query: str) -> list[str]:
    items = extract_comparison_items(query)
    results = []
    for item in items:
        results.extend(semantic_search(item, top_k=2))
    return results
```

### Out of scope

The user asked something your system can't or shouldn't answer. Off-topic, inappropriate, or outside your domain.

The best strategy is **no retrieval at all**. Return a polite refusal immediately. This saves tokens, reduces latency, and avoids hallucination.

```python
# Out of scope — don't search, don't generate
def handle_out_of_scope(query: str) -> str:
    return "I can only answer questions about our platform."
```

## Modelling this in Python

We can represent these intents using Python's Enum:

```python
from enum import Enum

class Intent(str, Enum):
    CONCEPTUAL = "conceptual"
    PROCEDURAL = "procedural"
    FACTUAL = "factual"
    COMPARATIVE = "comparative"
    OUT_OF_SCOPE = "out_of_scope"
```

Using `str, Enum` makes the values JSON-serializable. This matters when we use structured output from an LLM — the model returns a string, and we need it to match our enum values.

## How many categories?

Keep it between 3 and 7. Fewer than 3 and you're not routing meaningfully. More than 7 and the classifier starts making mistakes — the boundaries between categories get blurry.

If you find yourself needing more categories, you probably need a two-stage classifier:

```
Stage 1: Is this in-scope? (yes/no)
Stage 2: If yes, what type? (conceptual/procedural/factual/comparative)
```

This is a common production pattern. The first stage is a cheap filter, the second is more nuanced.

## Customizing for your domain

The five categories above are a starting point. Your system might need different ones. A few examples:

**E-commerce support bot:**
- Product inquiry → search product catalog
- Order status → query order database
- Return/refund → route to policy docs
- Complaint → escalate to human
- Off-topic → polite refusal

**Internal knowledge base:**
- Policy question → search policy documents
- Technical how-to → search runbooks
- People/org question → query HR system
- Data request → route to analytics
- Off-topic → redirect

The principle is the same: each category maps to a different retrieval strategy or action.

## What's next

We know what we're classifying into. Now let's build the classifier itself using Pydantic and OpenAI's structured output.

[Next: Building the Classifier →](03-the-classifier.md)
