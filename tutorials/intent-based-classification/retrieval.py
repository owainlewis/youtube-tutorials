"""
Mock Retrieval Strategies

These are simplified mock implementations showing how different
retrieval strategies work for different query types.

In a real system, these would connect to:
- Vector databases (Pinecone, Weaviate, Qdrant)
- SQL databases (Postgres, MySQL)
- Hybrid search systems (Elasticsearch, OpenSearch)
"""

from dataclasses import dataclass


@dataclass
class RetrievalResult:
    """The result of a retrieval operation."""

    chunks: list[str]
    strategy_used: str
    metadata: dict


# =============================================================================
# Mock Data - Simulating different data sources
# =============================================================================

# Conceptual content - longer explanations, broader context
CONCEPTUAL_DOCS = {
    "jwt": """
    JSON Web Tokens (JWT) are a compact, URL-safe means of representing claims
    between two parties. They're commonly used for authentication and information
    exchange. A JWT consists of three parts: a header (algorithm and type),
    a payload (claims/data), and a signature (verification).

    JWTs are stateless - the server doesn't need to store session data.
    The token itself contains all the information needed to verify the user.
    This makes them ideal for distributed systems and microservices.
    """,
    "microservices": """
    Microservices architecture structures an application as a collection of
    loosely coupled, independently deployable services. Each service runs
    its own process and communicates via lightweight protocols (usually HTTP/REST).

    Benefits include: independent scaling, technology flexibility, fault isolation,
    and easier maintenance. Challenges include: distributed system complexity,
    data consistency, and operational overhead.
    """,
    "oauth": """
    OAuth 2.0 is an authorization framework that enables third-party applications
    to obtain limited access to a web service. It works by delegating user
    authentication to the service that hosts the user account.

    Key concepts: Authorization Server, Resource Server, Client, Access Token,
    Refresh Token, Scopes. OAuth separates the role of the client from the
    resource owner, allowing more secure and flexible access control.
    """
}

# Procedural content - step-by-step instructions, specific commands
PROCEDURAL_DOCS = {
    "reset_api_key": """
    To reset your API key:

    1. Log into the developer dashboard at https://dashboard.example.com
    2. Navigate to Settings → API Keys
    3. Click "Regenerate" next to your current key
    4. Confirm the action (note: this invalidates your old key immediately)
    5. Copy the new key and update your environment variables

    Command line alternative:
    ```
    example-cli auth reset-key --confirm
    ```
    """,
    "deploy_production": """
    To deploy to production:

    1. Ensure all tests pass: `uv run pytest`
    2. Build the container: `docker build -t myapp:latest .`
    3. Push to registry: `docker push registry.example.com/myapp:latest`
    4. Deploy: `kubectl apply -f k8s/production.yaml`
    5. Verify: `kubectl get pods -n production`

    Rollback if needed: `kubectl rollout undo deployment/myapp -n production`
    """,
    "configure_logging": """
    To configure logging:

    1. Install the logging library: `uv add structlog`
    2. Create a logging config file at `config/logging.py`
    3. Set log level via environment variable: `LOG_LEVEL=INFO`
    4. Initialize in your main.py:
       ```python
       import structlog
       structlog.configure(
           processors=[structlog.dev.ConsoleRenderer()],
           wrapper_class=structlog.make_filtering_bound_logger(log_level),
       )
       ```
    """
}

# Factual data - structured information, numbers, lookups
FACTUAL_DATA = {
    "q3_revenue": {"value": "$2.4M", "period": "Q3 2024", "growth": "+12% YoY"},
    "monthly_signups": {"january": 1250, "february": 1340, "march": 1520},
    "api_rate_limit": {"standard": "1000 req/min", "premium": "10000 req/min"},
    "user_count": {"total": 45000, "active_monthly": 28000},
}

# Comparative content - pros/cons, decision frameworks
COMPARATIVE_DOCS = {
    "postgres_vs_mongodb": {
        "postgres": {
            "type": "Relational (SQL)",
            "best_for": "Complex queries, transactions, data integrity",
            "scaling": "Vertical primarily, read replicas",
            "schema": "Strict, migrations required"
        },
        "mongodb": {
            "type": "Document (NoSQL)",
            "best_for": "Flexible schemas, rapid iteration, unstructured data",
            "scaling": "Horizontal (sharding)",
            "schema": "Flexible, schema-less"
        },
        "recommendation": "Use Postgres for transactional data with complex relationships. Use MongoDB for rapid prototyping or document-centric data."
    },
    "rest_vs_graphql": {
        "rest": {
            "type": "Resource-based API",
            "best_for": "Simple CRUD, caching, public APIs",
            "learning_curve": "Lower",
            "overfetching": "Common problem"
        },
        "graphql": {
            "type": "Query language for APIs",
            "best_for": "Complex data requirements, mobile apps, multiple clients",
            "learning_curve": "Higher",
            "overfetching": "Solved by design"
        },
        "recommendation": "Start with REST for simplicity. Consider GraphQL when you have multiple clients with different data needs."
    }
}


# =============================================================================
# Retrieval Functions - Different strategies for different intents
# =============================================================================

def semantic_search(query: str, top_k: int = 3) -> RetrievalResult:
    """
    Semantic/Vector search - best for CONCEPTUAL queries.

    In production, this would:
    1. Embed the query using an embedding model
    2. Search a vector database for similar chunks
    3. Return chunks ranked by semantic similarity

    Good for: "What is X?", "Explain Y", "Why do we use Z?"
    """
    # Mock: Find conceptual docs that might match
    chunks = []
    query_lower = query.lower()

    for topic, content in CONCEPTUAL_DOCS.items():
        if topic in query_lower or any(word in query_lower for word in topic.split("_")):
            chunks.append(content.strip())

    # Fallback if no direct match
    if not chunks:
        chunks = [list(CONCEPTUAL_DOCS.values())[0]]

    return RetrievalResult(
        chunks=chunks[:top_k],
        strategy_used="semantic_search",
        metadata={"embedding_model": "text-embedding-3-small", "top_k": top_k}
    )


def hybrid_search(query: str, alpha: float = 0.5) -> RetrievalResult:
    """
    Hybrid search (vector + keyword) - best for PROCEDURAL queries.

    In production, this would:
    1. Run semantic search for contextual matches
    2. Run keyword/BM25 search for exact term matches
    3. Combine scores with alpha weighting

    Good for: "How do I X?", technical terms, CLI commands
    Alpha controls balance: 0 = all keywords, 1 = all semantic
    """
    chunks = []
    query_lower = query.lower()

    # Keyword matching for procedural docs
    for topic, content in PROCEDURAL_DOCS.items():
        # Check for keyword matches (important for technical queries)
        topic_words = topic.replace("_", " ").split()
        if any(word in query_lower for word in topic_words):
            chunks.append(content.strip())

    # Fallback
    if not chunks:
        chunks = [list(PROCEDURAL_DOCS.values())[0]]

    return RetrievalResult(
        chunks=chunks,
        strategy_used="hybrid_search",
        metadata={"alpha": alpha, "keyword_weight": 1 - alpha, "semantic_weight": alpha}
    )


def structured_query(query: str) -> RetrievalResult:
    """
    Structured data query - best for FACTUAL queries.

    In production, this would:
    1. Parse the query to identify what data is needed
    2. Generate SQL or query structured data directly
    3. Return formatted results

    Good for: "What was revenue?", "How many users?", "What's the limit?"
    NOTE: This skips vector search entirely - the answer is in a database.
    """
    query_lower = query.lower()

    # Simple keyword matching to find relevant data
    result_data = None

    if "revenue" in query_lower or "q3" in query_lower or "q4" in query_lower:
        result_data = FACTUAL_DATA["q3_revenue"]
    elif "signup" in query_lower or "user" in query_lower and "month" in query_lower:
        result_data = FACTUAL_DATA["monthly_signups"]
    elif "rate limit" in query_lower or "limit" in query_lower:
        result_data = FACTUAL_DATA["api_rate_limit"]
    elif "user" in query_lower and "count" in query_lower:
        result_data = FACTUAL_DATA["user_count"]

    if result_data:
        chunks = [f"Data retrieved: {result_data}"]
    else:
        chunks = ["No matching data found in structured sources."]

    return RetrievalResult(
        chunks=chunks,
        strategy_used="structured_query",
        metadata={"source": "database", "query_type": "direct_lookup"}
    )


def multi_source_retrieval(query: str) -> RetrievalResult:
    """
    Multi-source retrieval - best for COMPARATIVE queries.

    In production, this would:
    1. Parse the query to identify the items being compared
    2. Retrieve information about each item separately
    3. Combine for synthesis

    Good for: "X vs Y?", "Should I use A or B?", "Compare X and Y"
    """
    query_lower = query.lower()
    chunks = []

    # Find comparison data
    for comparison_key, data in COMPARATIVE_DOCS.items():
        items = comparison_key.split("_vs_")
        if any(item in query_lower for item in items):
            # Format comparison data nicely
            for item in items:
                if item in data:
                    chunks.append(f"{item.upper()}: {data[item]}")
            if "recommendation" in data:
                chunks.append(f"RECOMMENDATION: {data['recommendation']}")
            break

    if not chunks:
        chunks = ["No comparison data found for the specified items."]

    return RetrievalResult(
        chunks=chunks,
        strategy_used="multi_source_retrieval",
        metadata={"sources_queried": 2, "synthesis_required": True}
    )


def early_exit(query: str) -> RetrievalResult:
    """
    Early exit - for OUT_OF_SCOPE queries.

    Don't search anything. Return a canned response immediately.
    Saves tokens, reduces latency, avoids liability.
    """
    return RetrievalResult(
        chunks=["I can only answer questions about our software and documentation. "
                "For other topics, please consult appropriate resources."],
        strategy_used="early_exit",
        metadata={"reason": "out_of_scope", "search_performed": False}
    )
