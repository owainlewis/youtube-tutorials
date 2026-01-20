from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


class Document(BaseModel):
    """Database representation of a document."""

    id: UUID
    filename: str
    content: str
    created_at: datetime
    updated_at: datetime

    model_config = {"frozen": True}

    @classmethod
    def from_row(cls, row) -> "Document":
        return cls(
            id=row["id"],
            filename=row["filename"],
            content=row["content"],
            created_at=row["created_at"],
            updated_at=row["updated_at"],
        )


class DocumentCreate(BaseModel):
    """Request model for creating a document."""

    filename: str
    content: str


class DocumentResponse(BaseModel):
    """API response for a document."""

    id: UUID
    filename: str
    created_at: datetime
    chunk_count: int

    model_config = {"frozen": True}
