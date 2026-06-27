# Evaluation

You've built a classifier and a router. How do you know it works?

## Why evaluation matters

The classifier feels like it works when you test it with five hand-picked examples. But in production, users ask ambiguous questions, use slang, make typos, and combine multiple intents in a single message.

Without systematic testing, you won't know your classifier misroutes 15% of procedural queries until users start complaining about bad answers.

## Building a test set

Start with a set of queries where you know the correct intent. This is your ground truth:

```python
TEST_CASES = [
    # (query, expected_intent)

    # Conceptual
    ("What is OAuth?", "conceptual"),
    ("Explain how JWTs work", "conceptual"),
    ("Why do we use microservices?", "conceptual"),
    ("What's the difference between authentication and authorization?", "conceptual"),

    # Procedural
    ("How do I reset my API key?", "procedural"),
    ("Steps to deploy to production", "procedural"),
    ("How do I configure logging?", "procedural"),
    ("Show me how to set up a webhook", "procedural"),

    # Factual
    ("What was our Q3 revenue?", "factual"),
    ("How many users signed up last month?", "factual"),
    ("What's the current API rate limit?", "factual"),
    ("How many active users do we have?", "factual"),

    # Comparative
    ("Should I use Postgres or MongoDB?", "comparative"),
    ("REST vs GraphQL?", "comparative"),
    ("What's the difference between Redis and Memcached?", "comparative"),
    ("Which deployment method is better, Docker or bare metal?", "comparative"),

    # Out of scope
    ("What's the weather?", "out_of_scope"),
    ("Tell me a joke", "out_of_scope"),
    ("Who won the game last night?", "out_of_scope"),
    ("What should I have for lunch?", "out_of_scope"),
]
```

## Running the evaluation

```python
from openai import OpenAI
from intent_classifier import classify_query


def evaluate(test_cases: list[tuple[str, str]], client: OpenAI) -> dict:
    """Run the classifier against a test set and report accuracy."""
    correct = 0
    total = len(test_cases)
    errors = []

    for query, expected in test_cases:
        result = classify_query(query, client)
        actual = result.intent.value

        if actual == expected:
            correct += 1
        else:
            errors.append({
                "query": query,
                "expected": expected,
                "actual": actual,
                "confidence": result.confidence,
                "reasoning": result.reasoning,
            })

    accuracy = correct / total

    return {
        "accuracy": accuracy,
        "correct": correct,
        "total": total,
        "errors": errors,
    }


# Run it
client = OpenAI()
results = evaluate(TEST_CASES, client)

print(f"Accuracy: {results['accuracy']:.0%} ({results['correct']}/{results['total']})")

if results["errors"]:
    print(f"\nMisclassified queries:")
    for error in results["errors"]:
        print(f"  Query: {error['query']}")
        print(f"  Expected: {error['expected']}, Got: {error['actual']}")
        print(f"  Confidence: {error['confidence']}, Reasoning: {error['reasoning']}")
        print()
```

## What to look for

### Overall accuracy

For 5 categories, you should aim for **90%+ accuracy** on your test set. Below that, either your categories overlap too much or your prompt needs work.

### Confusion patterns

Look at which categories get confused with each other. Common confusions:

- **Conceptual vs Procedural**: "How does OAuth work?" — is this asking for an explanation (conceptual) or steps (procedural)?
- **Conceptual vs Comparative**: "What's the difference between REST and GraphQL?" — explanation or comparison?
- **Factual vs Procedural**: "What's the command to restart the server?" — data lookup or how-to?

If two categories are constantly confused, either:
1. Make the classification prompt more specific about the boundary
2. Merge them into one category (maybe they should use the same retrieval strategy anyway)

### Confidence distribution

Plot the confidence scores:

```python
def analyze_confidence(test_cases: list[tuple[str, str]], client: OpenAI):
    """Analyze confidence score distribution."""
    results = []

    for query, expected in test_cases:
        result = classify_query(query, client)
        results.append({
            "query": query,
            "expected": expected,
            "actual": result.intent.value,
            "confidence": result.confidence,
            "correct": result.intent.value == expected,
        })

    # Check if misclassified queries have lower confidence
    correct_conf = [r["confidence"] for r in results if r["correct"]]
    wrong_conf = [r["confidence"] for r in results if not r["correct"]]

    print(f"Avg confidence (correct): {sum(correct_conf) / len(correct_conf):.2f}")
    if wrong_conf:
        print(f"Avg confidence (wrong):   {sum(wrong_conf) / len(wrong_conf):.2f}")
    else:
        print("No misclassifications!")
```

Ideally, misclassified queries have lower confidence than correctly classified ones. This means you can use a confidence threshold to catch errors.

## Improving the classifier

When accuracy isn't good enough, you have three options:

### 1. Improve the prompt

Add more examples, especially for the categories that get confused:

```python
# Before: vague boundary
"CONCEPTUAL - Questions about what something is"

# After: explicit boundary
"""CONCEPTUAL - Questions about what something is, why it exists, or how it works
at a high level. The user wants to UNDERSTAND, not DO.
Examples: "What is a JWT?", "Why do we use microservices?"
NOT conceptual: "How do I create a JWT?" (that's procedural)"""
```

### 2. Add few-shot examples

Include example classifications in the prompt:

```python
PROMPT = """...

Examples:
Query: "What is a load balancer?" → conceptual
Query: "How do I set up Nginx?" → procedural
Query: "What was last month's uptime?" → factual
Query: "Nginx vs Apache?" → comparative
Query: "What's the best pizza place?" → out_of_scope

Now classify this query: {query}"""
```

### 3. Use a better model

If `gpt-4o-mini` isn't accurate enough, try `gpt-4o`. It costs more per classification but might save money overall by routing more queries correctly (better answers = fewer follow-up queries).

## Testing with edge cases

The easy queries are easy. Test the hard ones:

```python
EDGE_CASES = [
    # Ambiguous intent
    ("How does OAuth work?", "conceptual"),  # could be procedural
    ("What's the best way to deploy?", "procedural"),  # could be comparative

    # Compound queries
    ("What is OAuth and how do I implement it?", "procedural"),  # two intents

    # Casual phrasing
    ("yo how do i fix my api key", "procedural"),  # informal
    ("tell me about jwt stuff", "conceptual"),  # vague

    # Nearly in-scope
    ("What programming language should I learn?", "out_of_scope"),  # related but off-topic
]
```

Edge cases reveal where your category boundaries need sharpening.

## Cost of evaluation

Each evaluation run costs a few cents (20 test cases × ~$0.0001 per classification = ~$0.002). Run it often. Run it after every prompt change. It's cheap insurance.

## What's next

You now have a complete system: classifier, router, and evaluation framework. Let's wrap up with how this fits into a production RAG pipeline.

[Next: Summary →](06-summary.md)
