"""
Intent-Based Classification Example

Run this script to see intent classification in action:
    uv run python example.py

Or run with a specific query:
    uv run python example.py "How do I reset my API key?"
"""

import sys
import anthropic

from intent_classifier import classify_intent, classify_intent_simple, Intent
from retrieval import (
    semantic_search,
    hybrid_search,
    structured_query,
    multi_source_retrieval,
    early_exit,
)


def route_and_retrieve(intent: Intent, query: str):
    """Route to the appropriate retrieval strategy."""
    match intent:
        case Intent.CONCEPTUAL:
            return semantic_search(query)
        case Intent.PROCEDURAL:
            return hybrid_search(query)
        case Intent.FACTUAL:
            return structured_query(query)
        case Intent.COMPARATIVE:
            return multi_source_retrieval(query)
        case Intent.OUT_OF_SCOPE:
            return early_exit(query)


def process_query(query: str, client: anthropic.Anthropic):
    """Complete pipeline: classify → route → retrieve."""
    print(f"\n{'='*60}")
    print(f"QUERY: {query}")
    print(f"{'='*60}\n")

    # Step 1: Classify
    print("Step 1: Classifying intent...")
    result = classify_intent(query, client)
    print(f"  Intent: {result.intent.value.upper()}")
    print(f"  Confidence: {result.confidence}")
    print(f"  Reasoning: {result.reasoning}")

    # Step 2: Route and retrieve
    print(f"\nStep 2: Routing to retrieval strategy...")
    retrieval_result = route_and_retrieve(result.intent, query)
    print(f"  Strategy: {retrieval_result.strategy_used}")
    print(f"  Metadata: {retrieval_result.metadata}")

    # Step 3: Show retrieved content
    print(f"\nStep 3: Retrieved content:")
    for i, chunk in enumerate(retrieval_result.chunks, 1):
        preview = chunk[:200] + "..." if len(chunk) > 200 else chunk
        print(f"  [{i}] {preview}")

    return result.intent, retrieval_result


def main():
    client = anthropic.Anthropic()

    if len(sys.argv) > 1:
        # Process command-line query
        query = " ".join(sys.argv[1:])
        process_query(query, client)
    else:
        # Run demo with example queries
        demo_queries = [
            "What is a JWT?",                        # CONCEPTUAL
            "How do I reset my API key?",            # PROCEDURAL
            "What was our Q3 revenue?",              # FACTUAL
            "Should I use Postgres or MongoDB?",     # COMPARATIVE
            "What's the weather like today?",        # OUT_OF_SCOPE
        ]

        print("\n" + "="*60)
        print("INTENT-BASED CLASSIFICATION DEMO")
        print("="*60)
        print("\nThis demo shows how different queries get routed to")
        print("different retrieval strategies based on their intent.\n")

        for query in demo_queries:
            process_query(query, client)
            print()


if __name__ == "__main__":
    main()
