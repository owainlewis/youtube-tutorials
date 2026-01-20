from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


class Chunk(BaseModel):
    """Database representation of a chunk."""

    id: UUID
    document_id: UUID
    content: str
    embedding: list[float]
    chunk_index: int
    created_at: datetime

    model_config = {"frozen": True}

    @classmethod
    def from_row(cls, row) -> "Chunk":
        return cls(
            id=row["id"],
            document_id=row["document_id"],
            content=row["content"],
            embedding=list(row["embedding"]),
            chunk_index=row["chunk_index"],
            created_at=row["created_at"],
        )


class ChunkCreate(BaseModel):
    """Model for creating a chunk."""

    document_id: UUID
    content: str
    embedding: list[float]
    chunk_index: int


class ChunkResponse(BaseModel):
    """API response for a chunk (used in search results)."""

    id: UUID
    content: str
    chunk_index: int
    similarity: float

    model_config = {"frozen": True}
