"""
Intent-Based Router

Classify a query, route it to the right retrieval strategy, generate an answer.
"""

import os
from dataclasses import dataclass

from openai import OpenAI

from intent_classifier import QueryClassification, classify_query
from intents import Intent
from retrieval import RetrievalResult
from routing import route_to_retrieval


@dataclass
class RoutedResponse:
    """Complete response including classification, retrieval, and answer."""

    query: str
    classification: QueryClassification
    retrieval_result: RetrievalResult
    answer: str


def route_query(query: str, client: OpenAI | None = None) -> RoutedResponse:
    """
    The complete pipeline: classify → route → retrieve → generate.
    """
    if client is None:
        client = OpenAI()

    # Step 1: Classify
    classification = classify_query(query, client)

    # Step 2: Route to retrieval strategy
    retrieval_result = route_to_retrieval(classification.intent, query)

    # Step 3: Generate answer (or return early for out-of-scope)
    if classification.intent == Intent.OUT_OF_SCOPE:
        answer = retrieval_result.chunks[0]
    else:
        answer = generate_answer(query, retrieval_result.chunks, client)

    return RoutedResponse(
        query=query,
        classification=classification,
        retrieval_result=retrieval_result,
        answer=answer,
    )


def generate_answer(query: str, context_chunks: list[str], client: OpenAI) -> str:
    """Generate an answer using retrieved context."""
    context = "\n\n---\n\n".join(context_chunks)

    response = client.responses.create(
        model=os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
        input=f"""Answer the user's question based on the provided context.
Be concise and direct. If the context doesn't contain the answer, say so.

Context:
{context}

Question: {query}""",
    )

    return response.output_text
