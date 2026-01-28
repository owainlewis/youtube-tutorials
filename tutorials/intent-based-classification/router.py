"""
Intent-Based Router

This is the orchestration layer that:
1. Classifies the user's query by intent
2. Routes to the appropriate retrieval strategy
3. Returns results optimized for that query type

This is the core pattern that separates demo RAG from production RAG.
"""

from dataclasses import dataclass
from openai import OpenAI

from intent_classifier import Intent, classify_intent, classify_intent_simple
from retrieval import (
    RetrievalResult,
    semantic_search,
    hybrid_search,
    structured_query,
    multi_source_retrieval,
    early_exit,
)


@dataclass
class RoutedResponse:
    """Complete response including classification and retrieval results."""

    query: str
    intent: Intent
    retrieval_result: RetrievalResult
    answer: str | None = None  # Optional: LLM-generated answer


def route_query(
    query: str,
    client: OpenAI | None = None,
    generate_answer: bool = False
) -> RoutedResponse:
    """
    The main routing function.

    1. Classify the query intent
    2. Route to the appropriate retrieval strategy
    3. Optionally generate an answer using the retrieved context

    Args:
        query: The user's question
        client: OpenAI client for classification (and answer generation)
        generate_answer: Whether to generate an LLM answer from retrieved context
    """
    if client is None:
        client = OpenAI()

    # Step 1: Classify intent
    intent = classify_intent_simple(query, client)

    # Step 2: Route to appropriate retrieval strategy
    retrieval_result = route_to_retrieval(intent, query)

    # Step 3: Optionally generate answer
    answer = None
    if generate_answer and intent != Intent.OUT_OF_SCOPE:
        answer = generate_rag_answer(query, retrieval_result.chunks, client)

    return RoutedResponse(
        query=query,
        intent=intent,
        retrieval_result=retrieval_result,
        answer=answer
    )


def route_to_retrieval(intent: Intent, query: str) -> RetrievalResult:
    """
    Route to the appropriate retrieval strategy based on intent.

    This is where the magic happens - each intent gets a different
    search strategy optimized for that type of query.
    """
    match intent:
        case Intent.CONCEPTUAL:
            # Broad understanding needed - use semantic search with larger chunks
            return semantic_search(query, top_k=3)

        case Intent.PROCEDURAL:
            # Specific steps needed - use hybrid search (keywords matter)
            return hybrid_search(query, alpha=0.5)

        case Intent.FACTUAL:
            # Data lookup - skip vectors, query structured data directly
            return structured_query(query)

        case Intent.COMPARATIVE:
            # Multiple sources needed - gather info on each item
            return multi_source_retrieval(query)

        case Intent.OUT_OF_SCOPE:
            # Don't search - return canned response immediately
            return early_exit(query)


def generate_rag_answer(
    query: str,
    context_chunks: list[str],
    client: OpenAI
) -> str:
    """
    Generate an answer using retrieved context.

    This is the final step - after routing and retrieval,
    we use the LLM to synthesize an answer from the context.
    """
    context = "\n\n---\n\n".join(context_chunks)

    response = client.responses.create(
        model="gpt-4o-mini",
        input=f"""Answer the user's question based on the provided context.
Be concise and direct. If the context doesn't contain the answer, say so.

CONTEXT:
{context}

QUESTION: {query}

ANSWER:""",
    )

    return response.output_text


# =============================================================================
# Convenience functions for demonstration
# =============================================================================

def explain_routing(query: str) -> dict:
    """
    Explain how a query would be routed (without making API calls).

    Useful for understanding the routing logic and for testing.
    """
    # Keywords that suggest different intents
    conceptual_keywords = ["what is", "explain", "why", "concept", "understand"]
    procedural_keywords = ["how do i", "how to", "steps", "configure", "setup", "reset"]
    factual_keywords = ["how many", "what was", "revenue", "count", "number", "rate"]
    comparative_keywords = ["vs", "versus", "compare", "difference", "should i use", "or"]

    query_lower = query.lower()

    suggested_intent = "unknown"
    reasoning = []

    if any(kw in query_lower for kw in procedural_keywords):
        suggested_intent = "PROCEDURAL"
        reasoning.append("Contains action-oriented keywords (how do I, steps, configure)")

    elif any(kw in query_lower for kw in factual_keywords):
        suggested_intent = "FACTUAL"
        reasoning.append("Asking for specific data or numbers")

    elif any(kw in query_lower for kw in comparative_keywords):
        suggested_intent = "COMPARATIVE"
        reasoning.append("Comparing options or asking for recommendations")

    elif any(kw in query_lower for kw in conceptual_keywords):
        suggested_intent = "CONCEPTUAL"
        reasoning.append("Asking about concepts, definitions, or explanations")

    # Map intent to retrieval strategy
    strategy_map = {
        "CONCEPTUAL": "semantic_search - Vector search with larger context chunks",
        "PROCEDURAL": "hybrid_search - Combined keyword + semantic for technical precision",
        "FACTUAL": "structured_query - Direct database/SQL lookup, skip vectors",
        "COMPARATIVE": "multi_source_retrieval - Gather info on each option, then synthesize",
        "OUT_OF_SCOPE": "early_exit - Return canned response, don't search",
        "unknown": "Would need LLM classification to determine"
    }

    return {
        "query": query,
        "suggested_intent": suggested_intent,
        "reasoning": reasoning,
        "retrieval_strategy": strategy_map.get(suggested_intent, "unknown"),
        "note": "This is a heuristic guess. Real classification uses an LLM."
    }
