# The Problem with Naive RAG

Most RAG tutorials end with the same architecture:

```
User query → Embed → Vector search → Stuff into prompt → Generate
```

It works great for the demo. Then you deploy it and users start typing real messages.

## Where it breaks

Here's what a typical day looks like for a RAG system handling support queries for a developer platform:

```
"What is OAuth?"                          → needs a broad explanation
"How do I reset my API key?"              → needs specific step-by-step instructions
"What was our Q3 revenue?"                → needs a database lookup, not document search
"Should I use Postgres or MongoDB?"       → needs info on BOTH, then a comparison
"What's the weather?"                     → should refuse, not search your docs for weather info
```

Five queries. Each one needs a fundamentally different approach. But naive RAG treats them all the same: embed the query, search the vector database, stuff results into a prompt.

## What goes wrong

Let's look at each failure:

**Conceptual queries get fragmented answers.** "What is OAuth?" needs a broad explanation pulling from multiple sections. Vector search returns the three most similar chunks, which might be three unrelated paragraphs that each mention OAuth once.

**Procedural queries miss keywords.** "How do I reset my API key?" has specific technical terms that matter — "reset", "API key". Pure semantic search might return conceptually similar results about authentication that don't contain the actual steps.

**Factual queries waste time on vectors.** "What was Q3 revenue?" has a precise answer sitting in a database. Embedding it and searching 50,000 document chunks is pointless when a SQL query would return the answer in milliseconds.

**Comparative queries only get one side.** "Postgres vs MongoDB?" retrieves the three chunks most similar to the query. Those chunks probably all discuss the same database. You need to deliberately retrieve information about both.

**Off-topic queries hallucinate.** "What's the weather?" has no answer in your documents. But vector search always returns something — the three least irrelevant chunks. The LLM then does its best to answer a weather question using your API documentation.

## The cost

This isn't just about answer quality. It's about real money and latency:

```python
# What most RAG systems do — every single query
def handle_query(query: str) -> str:
    embedding = embed(query)                    # ~100ms, ~$0.0001
    chunks = vector_db.search(embedding, k=5)   # ~200ms
    prompt = build_prompt(query, chunks)         # ~500 tokens of context
    answer = llm.generate(prompt)                # ~2s, ~$0.01
    return answer
```

Every query runs the full pipeline. The factual query that could have been a database lookup takes 2.3 seconds and costs a cent. The off-topic query that should have been rejected immediately still burns the same tokens.

When you're handling thousands of queries a day, this adds up.

## The fix

Add one step before retrieval: **classify the intent.**

```
User query → Classify intent → Route to strategy → Retrieve → Generate
```

```python
# What a routed system does
def handle_query(query: str) -> str:
    intent = classify(query)                     # ~100ms, ~$0.0001

    match intent:
        case "conceptual":
            chunks = semantic_search(query, chunk_size="large")
        case "procedural":
            chunks = hybrid_search(query)  # keywords + semantic
        case "factual":
            chunks = database_lookup(query)  # skip vectors entirely
        case "comparative":
            chunks = multi_source_search(query)  # search both sides
        case "out_of_scope":
            return "I can only help with questions about our platform."

    return generate_answer(query, chunks)
```

One cheap LLM call (~100ms, fraction of a cent) to classify the query. Then each query type gets a retrieval strategy optimized for it. The factual query skips vectors entirely. The off-topic query returns instantly. The comparative query deliberately searches both sides.

Counter-intuitive: adding a classification step often makes the system **faster**, because it lets you skip expensive operations for queries that don't need them.

## What you'll build

In this course, we'll build a complete intent classification and routing system:

1. Define the query types your system handles
2. Build a classifier using Pydantic and OpenAI's structured output
3. Create retrieval strategies optimized for each type
4. Wire it together into a router
5. Test and evaluate the classifier

By the end, you'll have a working system you can drop into any RAG pipeline.

## What's next

Before we build the classifier, we need to define what we're classifying into. Next, we'll look at the taxonomy of query types.

[Next: Query Types →](02-query-types.md)
