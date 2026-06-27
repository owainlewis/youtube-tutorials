# Building the Classifier

This is the core of the system. One LLM call that takes a user query and returns a structured classification.

## The simplest version

Start with Pydantic and OpenAI's structured output:

```python
from enum import Enum
from pydantic import BaseModel
from openai import OpenAI

class Intent(str, Enum):
    CONCEPTUAL = "conceptual"
    PROCEDURAL = "procedural"
    FACTUAL = "factual"
    COMPARATIVE = "comparative"
    OUT_OF_SCOPE = "out_of_scope"

class QueryClassification(BaseModel):
    intent: Intent

client = OpenAI()

response = client.responses.parse(
    model="gpt-4o-mini",
    input="Classify this query: What is OAuth?",
    text_format=QueryClassification,
)

result = response.output_parsed
print(result.intent)  # Intent.CONCEPTUAL
```

That's it. The model returns a structured response that Pydantic validates. No JSON parsing, no regex, no hoping the model formatted things correctly.

## Why structured output matters

Without structured output, you'd write something like this:

```python
# The fragile way — don't do this
response = client.responses.create(
    model="gpt-4o-mini",
    input="Classify this query as one of: conceptual, procedural, factual, comparative, out_of_scope\n\nQuery: What is OAuth?",
)

raw_text = response.output_text.strip().lower()

# Hope the model returned just the category name...
# Maybe it returned "The query is conceptual."
# Maybe it returned "CONCEPTUAL"
# Maybe it returned "conceptual (explanation: the user is asking...)"

if "```json" in raw_text:
    raw_text = raw_text.split("```json")[1].split("```")[0]

import json
data = json.loads(raw_text)  # might crash
```

This is brittle. The model might wrap its answer in explanation, use different casing, or add markdown formatting. You end up writing parsing code that handles edge cases.

Structured output guarantees the response matches your Pydantic model. The model is constrained to return valid JSON that passes validation.

## Adding confidence and reasoning

The basic classifier tells you _what_ the intent is. In production, you also want to know _how sure_ the model is and _why_ it classified this way:

```python
from pydantic import BaseModel, Field
from enum import Enum

class Intent(str, Enum):
    CONCEPTUAL = "conceptual"
    PROCEDURAL = "procedural"
    FACTUAL = "factual"
    COMPARATIVE = "comparative"
    OUT_OF_SCOPE = "out_of_scope"

class QueryClassification(BaseModel):
    intent: Intent
    confidence: float = Field(
        ge=0,
        le=1,
        description="How confident the classification is, from 0 to 1"
    )
    reasoning: str = Field(
        description="Brief explanation of why this classification was chosen"
    )
```

The `description` fields matter. They become part of the JSON schema that the model sees, helping it understand what each field expects.

Now when you classify:

```python
response = client.responses.parse(
    model="gpt-4o-mini",
    input="Classify this user query: How do I reset my API key?",
    text_format=QueryClassification,
)

result = response.output_parsed
print(result.intent)      # Intent.PROCEDURAL
print(result.confidence)  # 0.95
print(result.reasoning)   # "User is asking for specific steps to perform an action"
```

## The classification prompt

The `input` parameter is doing a lot of work. A better prompt gives the model context about each category:

```python
CLASSIFICATION_PROMPT = """You are a query classifier for a software documentation system.

Classify the user's query into exactly ONE category:

CONCEPTUAL - Questions about what something is, why it exists, or how it works at a high level.
Examples: "What is a JWT?", "Why do we use microservices?", "Explain OAuth"

PROCEDURAL - Questions about how to do something specific. Step-by-step instructions.
Examples: "How do I reset my API key?", "How do I deploy to production?"

FACTUAL - Questions asking for specific data, numbers, or lookups from structured data.
Examples: "What was our Q3 revenue?", "How many users signed up last month?"

COMPARATIVE - Questions comparing two or more options or asking for a recommendation.
Examples: "Should I use Postgres or MongoDB?", "REST vs GraphQL?"

OUT_OF_SCOPE - Questions unrelated to our software documentation, or inappropriate queries.
Examples: "What's the weather?", "Tell me a joke"

User query: {query}"""
```

Giving examples for each category is important. The model needs concrete anchors, not just abstract definitions.

## Wrapping it in a function

```python
from openai import OpenAI
from pydantic import BaseModel, Field
from enum import Enum


class Intent(str, Enum):
    CONCEPTUAL = "conceptual"
    PROCEDURAL = "procedural"
    FACTUAL = "factual"
    COMPARATIVE = "comparative"
    OUT_OF_SCOPE = "out_of_scope"


class QueryClassification(BaseModel):
    intent: Intent
    confidence: float = Field(
        ge=0, le=1,
        description="How confident the classification is, from 0 to 1",
    )
    reasoning: str = Field(
        description="Brief explanation of why this classification was chosen",
    )


CLASSIFICATION_PROMPT = """You are a query classifier for a software documentation system.

Classify the user's query into exactly ONE category:

CONCEPTUAL - Questions about what something is, why it exists, or how it works at a high level.
Examples: "What is a JWT?", "Why do we use microservices?", "Explain OAuth"

PROCEDURAL - Questions about how to do something specific. Step-by-step instructions.
Examples: "How do I reset my API key?", "How do I deploy to production?"

FACTUAL - Questions asking for specific data, numbers, or lookups from structured data.
Examples: "What was our Q3 revenue?", "How many users signed up last month?"

COMPARATIVE - Questions comparing two or more options or asking for a recommendation.
Examples: "Should I use Postgres or MongoDB?", "REST vs GraphQL?"

OUT_OF_SCOPE - Questions unrelated to our software documentation, or inappropriate queries.
Examples: "What's the weather?", "Tell me a joke"

User query: {query}"""


def classify_query(query: str, client: OpenAI | None = None) -> QueryClassification:
    """Classify a user query into one of the predefined intents."""
    if client is None:
        client = OpenAI()

    response = client.responses.parse(
        model="gpt-4o-mini",
        input=CLASSIFICATION_PROMPT.format(query=query),
        text_format=QueryClassification,
    )

    return response.output_parsed
```

Usage:

```python
client = OpenAI()

result = classify_query("What is a JWT?", client)
print(result.intent)      # Intent.CONCEPTUAL
print(result.confidence)  # 0.92
print(result.reasoning)   # "User is asking for an explanation of a concept"

result = classify_query("What's the weather?", client)
print(result.intent)      # Intent.OUT_OF_SCOPE
print(result.confidence)  # 0.98
print(result.reasoning)   # "Question is unrelated to software documentation"
```

## Using gpt-4o-mini

We use `gpt-4o-mini` for classification. It's fast (~100ms) and cheap (~$0.0001 per classification). This is a simple decision — it doesn't need the reasoning power of a larger model.

Classification is a solved problem for modern LLMs. You don't need GPT-4o for "is this a how-to question or a what-is question?" Save the expensive model for the generation step.

## Handling edge cases

Some queries sit on the boundary between categories:

- "What is the best database for my project?" — conceptual or comparative?
- "How does OAuth work?" — conceptual or procedural?
- "Show me last month's error rates and explain what caused the spike" — factual or conceptual?

This is where the confidence score helps. If confidence is below a threshold (say 0.7), you can fall back to a default strategy:

```python
def classify_with_fallback(
    query: str,
    client: OpenAI,
    confidence_threshold: float = 0.7,
) -> QueryClassification:
    """Classify with a fallback for low-confidence results."""
    result = classify_query(query, client)

    if result.confidence < confidence_threshold:
        # Fall back to semantic search — works reasonably for any query type
        return QueryClassification(
            intent=Intent.CONCEPTUAL,
            confidence=result.confidence,
            reasoning=f"Low confidence ({result.confidence}), falling back to semantic search",
        )

    return result
```

## Learn more

- [OpenAI Structured Outputs](https://platform.openai.com/docs/guides/structured-outputs)
- [Pydantic Field documentation](https://docs.pydantic.dev/latest/concepts/fields/)

## What's next

We have a classifier that tells us what type of query we're looking at. Next, let's build the router that sends each type to the right retrieval strategy.

[Next: The Router →](04-the-router.md)
