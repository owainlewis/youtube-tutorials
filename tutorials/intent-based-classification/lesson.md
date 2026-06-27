# Intent-Based Query Routing for RAG

Most RAG systems send every query through the same pipeline. That's wasteful - different queries need different retrieval strategies. A conceptual question needs broad semantic search. A factual question needs a database lookup. An off-topic question shouldn't search at all.

This course builds a classification and routing layer that sits in front of your RAG pipeline and sends each query to the right place.

## What you'll learn

- Why naive RAG fails on different query types
- How to define a taxonomy of query intents
- Building a classifier with Pydantic and OpenAI structured output
- Routing queries to specialized retrieval strategies
- Testing and evaluating classification accuracy

## Setup

```bash
git clone https://github.com/owainlewis/youtube-tutorials.git
cd youtube-tutorials/tutorials/intent-based-classification
uv sync
```

Set your OpenAI API key:

```bash
export OPENAI_API_KEY=sk-your-key-here
```

Run the demo:

```bash
uv run python example.py
```

Or classify a specific query:

```bash
uv run python example.py "How do I reset my API key?"
```

## Chapters

1. [The Problem](docs/01-the-problem.md) - Why sending every query through the same pipeline breaks
2. [Query Types](docs/02-query-types.md) - A taxonomy of user intents and what each needs
3. [The Classifier](docs/03-the-classifier.md) - Pydantic models + OpenAI structured output
4. [The Router](docs/04-the-router.md) - Sending queries to the right retrieval strategy
5. [Evaluation](docs/05-evaluation.md) - Testing that it actually works
6. [Summary](docs/06-summary.md) - Recap and next steps

## Files

| File | What it does |
|------|-------------|
| `intent_classifier.py` | Classification with Pydantic + structured output |
| `retrieval.py` | Mock retrieval strategies for each intent |
| `router.py` | Orchestration: classify -> route -> retrieve -> generate |
| `example.py` | Runnable demo script |

## Prerequisites

- Python 3.11+
- Familiarity with Pydantic basics
- An OpenAI API key

## The architecture

```
User query
  │
  ▼
┌─────────────┐
│  Classifier  │  <- gpt-4o-mini, ~100ms, ~$0.0001
└──────┬──────┘
       │
  ┌────┴────────────────────────────────┐
  │         │          │         │      │
  ▼         ▼          ▼         ▼      ▼
Semantic  Hybrid   Database  Multi-   Early
Search    Search   Lookup    Source   Exit
  │         │          │         │      │
  └────┬────┘          │         │      │
       ▼               ▼         ▼      ▼
   Generate         Generate  Generate  Return
    Answer           Answer    Answer   refusal
```
