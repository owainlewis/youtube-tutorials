"""
Intent-Based Classification Demo

Run with example queries:
    uv run python example.py

Or with a specific query:
    uv run python example.py "How do I reset my API key?"
"""

import sys

from openai import OpenAI

from intent_classifier import classify_query
from router import route_query


def demo_classify(query: str, client: OpenAI):
    """Show classification results for a single query."""
    print(f"\n{'=' * 60}")
    print(f"  {query}")
    print(f"{'=' * 60}")

    result = classify_query(query, client)

    print(f"  Intent:     {result.intent.value}")
    print(f"  Confidence: {result.confidence}")
    print(f"  Reasoning:  {result.reasoning}")


def demo_route(query: str, client: OpenAI):
    """Show the full pipeline for a single query."""
    print(f"\n{'=' * 60}")
    print(f"  {query}")
    print(f"{'=' * 60}")

    result = route_query(query, client)

    print(f"  Intent:     {result.classification.intent.value}")
    print(f"  Confidence: {result.classification.confidence}")
    print(f"  Strategy:   {result.retrieval_result.strategy_used}")
    print(f"  Answer:     {result.answer[:200]}")


def main():
    client = OpenAI()

    if len(sys.argv) > 1:
        query = " ".join(sys.argv[1:])
        demo_route(query, client)
        return

    # Demo queries — one for each intent
    queries = [
        "What is a JWT?",
        "How do I reset my API key?",
        "What was our Q3 revenue?",
        "Should I use Postgres or MongoDB?",
        "What's the weather like today?",
    ]

    print("\n  INTENT-BASED CLASSIFICATION DEMO")
    print("  Each query gets classified and routed to a different strategy.\n")

    for query in queries:
        demo_classify(query, client)

    print()


if __name__ == "__main__":
    main()
