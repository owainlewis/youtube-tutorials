# Intent-Based Classification for RAG

The pattern that separates demo RAG from production RAG.

## The Problem

Naive RAG treats every query the same:

```
Query → Embed → Vector Search → Stuff into Prompt → Generate
```

But different queries need different approaches:

| Query | What it needs | Naive RAG does |
|-------|--------------|----------------|
| "What was Q3 revenue?" | Database lookup | Searches 50k document chunks |
| "How do I reset my API key?" | Exact steps | Returns vague conceptual text |
| "Postgres vs MongoDB?" | Info on BOTH | Retrieves one side only |

## The Solution

Add ONE step before retrieval: **classify the intent**.

```
Query → CLASSIFY → Route to Strategy → Retrieve → Generate
```

## The Categories

| Intent | Example Query | Retrieval Strategy |
|--------|---------------|-------------------|
| CONCEPTUAL | "What is OAuth?" | Semantic search, larger chunks |
| PROCEDURAL | "How do I deploy?" | Hybrid search (keywords matter) |
| FACTUAL | "Q3 revenue?" | SQL/database query (skip vectors) |
| COMPARATIVE | "X vs Y?" | Multi-source, then synthesize |
| OUT_OF_SCOPE | "Weather?" | Early exit (don't search) |

## Quick Start

```bash
# Install dependencies
uv sync

# Run the demo
uv run python example.py

# Or with a specific query
uv run python example.py "How do I reset my API key?"
```

## Files

- `intent_classifier.py` - Classification logic and prompts
- `retrieval.py` - Mock retrieval strategies for each intent
- `router.py` - Orchestration layer tying it together
- `example.py` - Runnable demo script
- `01_intent_classification.ipynb` - Step-by-step notebook

## The Classification Prompt

The core is just a specialized prompt:

```python
PROMPT = """Classify this query into ONE category:

- CONCEPTUAL (what is X, explain X)
- PROCEDURAL (how do I X, steps to X)
- FACTUAL (data lookup, specific numbers)
- COMPARATIVE (X vs Y, which should I use)
- OUT_OF_SCOPE (off-topic)

Respond with ONLY the category name.

Query: {query}"""
```

One LLM call. ~50ms. Costs almost nothing.

## Why This Makes Your System FASTER

Counter-intuitive: adding classification often reduces latency.

**Without routing:** Every query runs the full expensive pipeline.

**With routing:**
- Factual → SQL query (skip embedding, skip vectors)
- Out of scope → Cached response (skip everything)
- Procedural → Targeted hybrid search (skip reranking)

You're not adding latency. You're adding a cheap check that skips expensive operations.

## Requirements

- Python 3.11+
- OpenAI API key (set `OPENAI_API_KEY` environment variable)
