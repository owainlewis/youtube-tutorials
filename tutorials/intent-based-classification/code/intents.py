"""Intent categories shared by classification and routing."""

from enum import Enum


class Intent(str, Enum):
    """A user query category that maps to a retrieval strategy."""

    CONCEPTUAL = "conceptual"
    PROCEDURAL = "procedural"
    FACTUAL = "factual"
    COMPARATIVE = "comparative"
    OUT_OF_SCOPE = "out_of_scope"
