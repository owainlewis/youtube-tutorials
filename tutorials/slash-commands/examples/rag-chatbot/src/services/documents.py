import re
from uuid import UUID

import asyncpg

from src.models import ChunkCreate, DocumentResponse
from src.services.embeddings import EmbeddingService
from src.services.vector_store import VectorStore


def chunk_text(text: str, chunk_size: int = 500, overlap: int = 50) -> list[str]:
    """Split text into overlapping chunks, preferring sentence boundaries."""
    if not text or not text.strip():
        return []

    text = text.strip()
    chunks = []
    start = 0

    while start < len(text):
        end = start + chunk_size

        if end >= len(text):
            chunks.append(text[start:].strip())
            break

        # Look for sentence boundary in the overlap window
        window_start = max(end - overlap, start)
        window = text[window_start:end]

        # Find last sentence-ending punctuation in window
        match = None
        for m in re.finditer(r"[.!?]\s", window):
            match = m

        if match:
            # Split at the sentence boundary
            boundary = window_start + match.end()
            chunks.append(text[start:boundary].strip())
            start = boundary
        else:
            # No sentence boundary found, split at chunk_size
            chunks.append(text[start:end].strip())
            start = end - overlap

    return [c for c in chunks if c]


class DocumentService:
    """Service for managing documents and their chunks."""

    def __init__(
        self,
        pool: asyncpg.Pool,
        embedding_service: EmbeddingService,
        vector_store: VectorStore,
    ):
        self.pool = pool
        self.embedding_service = embedding_service
        self.vector_store = vector_store

    async def create(self, filename: str, content: str) -> DocumentResponse:
        """Create a document, chunk it, embed chunks, and store everything."""
        async with self.pool.acquire() as conn:
            async with conn.transaction():
                # Insert document
                row = await conn.fetchrow(
                    """
                    INSERT INTO documents (filename, content)
                    VALUES ($1, $2)
                    RETURNING id, created_at
                    """,
                    filename,
                    content,
                )
                doc_id = row["id"]
                created_at = row["created_at"]

                # Chunk the content
                chunks = chunk_text(content)

                if chunks:
                    # Embed all chunks
                    embeddings = await self.embedding_service.embed_batch(chunks)

                    # Create chunk records
                    chunk_creates = [
                        ChunkCreate(
                            document_id=doc_id,
                            content=chunk,
                            embedding=embedding,
                            chunk_index=i,
                        )
                        for i, (chunk, embedding) in enumerate(zip(chunks, embeddings))
                    ]

                    # Insert chunks
                    await self.vector_store.insert_chunks(chunk_creates)

                return DocumentResponse(
                    id=doc_id,
                    filename=filename,
                    created_at=created_at,
                    chunk_count=len(chunks),
                )

    async def list_all(self) -> list[DocumentResponse]:
        """List all documents with their chunk counts."""
        async with self.pool.acquire() as conn:
            rows = await conn.fetch(
                """
                SELECT d.id, d.filename, d.created_at,
                       COUNT(c.id) as chunk_count
                FROM documents d
                LEFT JOIN chunks c ON c.document_id = d.id
                GROUP BY d.id, d.filename, d.created_at
                ORDER BY d.created_at DESC
                """
            )
            return [
                DocumentResponse(
                    id=row["id"],
                    filename=row["filename"],
                    created_at=row["created_at"],
                    chunk_count=row["chunk_count"],
                )
                for row in rows
            ]

    async def delete(self, document_id: UUID) -> bool:
        """Delete a document and its chunks. Returns True if found."""
        async with self.pool.acquire() as conn:
            result = await conn.execute(
                "DELETE FROM documents WHERE id = $1",
                document_id,
            )
            return result == "DELETE 1"

    async def get(self, document_id: UUID):
        """Get a document by ID."""
        async with self.pool.acquire() as conn:
            row = await conn.fetchrow(
                "SELECT * FROM documents WHERE id = $1",
                document_id,
            )
            return row
