"""Credential-free routing policy for classified queries."""

from intents import Intent
from retrieval import (
    RetrievalResult,
    early_exit,
    hybrid_search,
    multi_source_retrieval,
    semantic_search,
    structured_query,
)


def route_to_retrieval(intent: Intent, query: str) -> RetrievalResult:
    """Send a classified query to its retrieval strategy."""
    match intent:
        case Intent.CONCEPTUAL:
            return semantic_search(query, top_k=5)
        case Intent.PROCEDURAL:
            return hybrid_search(query, alpha=0.5)
        case Intent.FACTUAL:
            return structured_query(query)
        case Intent.COMPARATIVE:
            return multi_source_retrieval(query)
        case Intent.OUT_OF_SCOPE:
            return early_exit(query)

    raise ValueError(f"Unsupported intent: {intent!r}")
