# Summary

## What we built

A query classification and routing system for RAG:

```
User query → Classify intent → Route to strategy → Retrieve → Generate
```

One cheap LLM call classifies the query. Then each query type gets a retrieval strategy optimized for it.

## The key pieces

**Intent classification** (Chapter 3): A Pydantic model + OpenAI structured output that categorizes queries into conceptual, procedural, factual, comparative, or out-of-scope.

**Router** (Chapter 4): A match statement that sends each intent to a different retrieval strategy — semantic search, hybrid search, database lookup, multi-source retrieval, or early exit.

**Evaluation** (Chapter 5): A test set with known-correct labels, run against the classifier to measure accuracy and find confusion patterns.

## The code

```python
# The complete pipeline in ~20 lines
from openai import OpenAI
from intent_classifier import classify_query, Intent
from retrieval import (
    semantic_search, hybrid_search, database_lookup,
    multi_source_search, early_exit,
)

def handle_query(query: str) -> str:
    client = OpenAI()

    # Classify
    classification = classify_query(query, client)

    # Route
    match classification.intent:
        case Intent.CONCEPTUAL:   result = semantic_search(query)
        case Intent.PROCEDURAL:   result = hybrid_search(query)
        case Intent.FACTUAL:      result = database_lookup(query)
        case Intent.COMPARATIVE:  result = multi_source_search(query)
        case Intent.OUT_OF_SCOPE: return "I can only answer questions about our platform."

    # Generate
    return generate_answer(query, result.chunks, client)
```

## Why this matters

The pattern is simple. The impact is significant:

- **Better answers**: Each query type gets retrieval optimized for it
- **Lower cost**: Factual and out-of-scope queries skip expensive vector search
- **Lower latency**: Out-of-scope queries return instantly, factual queries hit a database
- **Less hallucination**: Off-topic queries get caught before they reach the LLM

## Taking it further

Things we didn't cover that you might explore:

**Two-stage classification**: First classify in-scope vs out-of-scope (cheap, fast), then classify intent for in-scope queries. Useful when most queries are in-scope and you want the fastest possible rejection for the rest.

**Dynamic strategies**: Adjust retrieval parameters based on confidence. Low confidence? Cast a wider net. High confidence? Be more targeted.

**Multi-intent queries**: "What is OAuth and how do I implement it?" has two intents. You could decompose the query, classify each part, and combine the results.

**Logging and monitoring**: Log every classification in production. Track accuracy over time. Flag low-confidence classifications for human review.

**Custom fine-tuning**: If you have thousands of classified queries, you can fine-tune a smaller model for even faster classification.

## Learn more

- [OpenAI Structured Outputs](https://platform.openai.com/docs/guides/structured-outputs)
- [Pydantic documentation](https://docs.pydantic.dev/latest/)
- [OpenAI Responses API](https://platform.openai.com/docs/api-reference/responses)
