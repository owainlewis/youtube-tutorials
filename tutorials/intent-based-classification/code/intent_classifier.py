"""
Intent Classification for RAG Systems

Classifies user queries by intent using Pydantic and OpenAI structured output.
Each intent maps to a different retrieval strategy.
"""

from enum import Enum

from openai import OpenAI
from pydantic import BaseModel, Field


class Intent(str, Enum):
    """The different types of queries a user might ask."""

    CONCEPTUAL = "conceptual"  # "What is X?" — needs broad context
    PROCEDURAL = "procedural"  # "How do I X?" — needs specific steps
    FACTUAL = "factual"  # "What was X?" — needs data lookup
    COMPARATIVE = "comparative"  # "X vs Y?" — needs multi-source synthesis
    OUT_OF_SCOPE = "out_of_scope"  # Off-topic or unsafe


class QueryClassification(BaseModel):
    """The result of classifying a user query."""

    intent: Intent
    confidence: float = Field(
        ge=0,
        le=1,
        description="How confident the classification is, from 0 to 1",
    )
    reasoning: str = Field(
        description="Brief explanation of why this classification was chosen",
    )


CLASSIFICATION_PROMPT = """You are a query classifier for a software documentation system.

Classify the user's query into exactly ONE category:

CONCEPTUAL - Questions about what something is, why it exists, or how it works at a high level.
The user wants to UNDERSTAND, not DO.
Examples: "What is a JWT?", "Why do we use microservices?", "Explain OAuth"

PROCEDURAL - Questions about how to do something specific. Step-by-step instructions.
The user wants to DO something.
Examples: "How do I reset my API key?", "How do I deploy to production?", "Show me how to configure logging"

FACTUAL - Questions asking for specific data, numbers, or lookups from structured data.
The user wants a SPECIFIC ANSWER, not an explanation.
Examples: "What was our Q3 revenue?", "How many users signed up last month?", "What's the current API rate limit?"

COMPARATIVE - Questions comparing two or more options or asking for a recommendation.
The user is CHOOSING between alternatives.
Examples: "Should I use Postgres or MongoDB?", "What's the difference between REST and GraphQL?"

OUT_OF_SCOPE - Questions unrelated to our software documentation, or inappropriate queries.
Examples: "What's the weather?", "Who should I vote for?", "Tell me a joke"

User query: {query}"""


def classify_query(query: str, client: OpenAI | None = None) -> QueryClassification:
    """
    Classify a user query into one of the predefined intents.

    Uses OpenAI structured output to guarantee the response
    matches our Pydantic model. No JSON parsing needed.
    """
    if client is None:
        client = OpenAI()

    response = client.responses.parse(
        model="gpt-4o-mini",
        input=CLASSIFICATION_PROMPT.format(query=query),
        text_format=QueryClassification,
    )

    return response.output_parsed
