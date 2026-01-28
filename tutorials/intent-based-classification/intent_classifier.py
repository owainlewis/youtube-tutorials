"""
Intent Classification for RAG Systems

This module demonstrates how to classify user queries by intent
before routing them to the appropriate retrieval strategy.
"""

from enum import Enum
from pydantic import BaseModel
from openai import OpenAI


class Intent(str, Enum):
    """The different types of queries a user might ask."""

    CONCEPTUAL = "conceptual"    # "What is X?" - needs broad context
    PROCEDURAL = "procedural"    # "How do I X?" - needs specific steps
    FACTUAL = "factual"          # "What was X?" - needs data lookup
    COMPARATIVE = "comparative"  # "X vs Y?" - needs multi-source synthesis
    OUT_OF_SCOPE = "out_of_scope"  # Off-topic or unsafe


class ClassificationResult(BaseModel):
    """The result of classifying a user query."""

    intent: Intent
    confidence: str  # "high", "medium", "low"
    reasoning: str


# The classification prompt - this is the core of intent identification
CLASSIFICATION_PROMPT = """You are a query classifier for a software documentation system.

Your job is to classify the user's query into exactly ONE category:

CONCEPTUAL - Questions about what something is, why it exists, or how it works at a high level.
Examples: "What is a JWT?", "Why do we use microservices?", "Explain OAuth"

PROCEDURAL - Questions about how to do something specific, step-by-step instructions.
Examples: "How do I reset my API key?", "How do I deploy to production?", "Show me how to configure logging"

FACTUAL - Questions asking for specific data, numbers, or lookups from structured data.
Examples: "What was our Q3 revenue?", "How many users signed up last month?", "What's the current API rate limit?"

COMPARATIVE - Questions comparing two or more options or asking for recommendations.
Examples: "Should I use Postgres or MongoDB?", "What's the difference between REST and GraphQL?"

OUT_OF_SCOPE - Questions unrelated to our software/documentation, or inappropriate queries.
Examples: "What's the weather?", "Who should I vote for?", "Tell me a joke"

Respond with a JSON object containing:
- intent: one of [conceptual, procedural, factual, comparative, out_of_scope]
- confidence: one of [high, medium, low]
- reasoning: a brief explanation of why you chose this classification

User query: {query}"""


def classify_intent(query: str, client: OpenAI | None = None) -> ClassificationResult:
    """
    Classify a user query into one of the predefined intents.

    This is the "router" step that happens BEFORE any retrieval.
    Uses a fast, cheap LLM call to determine the query type.

    Args:
        query: The user's question
        client: OpenAI client (creates one if not provided)

    Returns:
        ClassificationResult with intent, confidence, and reasoning
    """
    if client is None:
        client = OpenAI()

    response = client.responses.create(
        model="gpt-4o-mini",  # Fast and cheap for classification
        input=CLASSIFICATION_PROMPT.format(query=query),
    )

    # Parse the response
    import json
    content = response.output_text

    # Handle potential JSON in markdown code blocks
    if "```json" in content:
        content = content.split("```json")[1].split("```")[0]
    elif "```" in content:
        content = content.split("```")[1].split("```")[0]

    data = json.loads(content.strip())

    return ClassificationResult(
        intent=Intent(data["intent"]),
        confidence=data["confidence"],
        reasoning=data["reasoning"]
    )


def classify_intent_simple(query: str, client: OpenAI | None = None) -> Intent:
    """
    Simplified classification that just returns the intent.

    This is the minimal version - one LLM call, one category back.
    Use this when you don't need confidence scores or reasoning.
    """
    if client is None:
        client = OpenAI()

    simple_prompt = """Classify this query into exactly ONE category.

Categories:
- CONCEPTUAL (what is X, explain X)
- PROCEDURAL (how do I X, steps to X)
- FACTUAL (data lookup, specific numbers)
- COMPARATIVE (X vs Y, which should I use)
- OUT_OF_SCOPE (off-topic, inappropriate)

Respond with ONLY the category name in uppercase. Nothing else.

Query: {query}"""

    response = client.responses.create(
        model="gpt-4o-mini",
        input=simple_prompt.format(query=query),
    )

    intent_str = response.output_text.strip().lower()
    return Intent(intent_str)
