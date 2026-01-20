from uuid import UUID

import asyncpg
import numpy as np

from src.models import ChunkCreate, ChunkResponse


class VectorStore:
    """Service for storing and searching vector embeddings using pgvector."""

    def __init__(self, pool: asyncpg.Pool):
        self.pool = pool

    async def insert_chunks(self, chunks: list[ChunkCreate]) -> list[UUID]:
        """Insert chunks with embeddings and return their IDs."""
        if not chunks:
            return []

        async with self.pool.acquire() as conn:
            ids = []
            for chunk in chunks:
                row = await conn.fetchrow(
                    """
                    INSERT INTO chunks (document_id, content, embedding, chunk_index)
                    VALUES ($1, $2, $3, $4)
                    RETURNING id
                    """,
                    chunk.document_id,
                    chunk.content,
                    np.array(chunk.embedding),
                    chunk.chunk_index,
                )
                ids.append(row["id"])
            return ids

    async def search(
        self,
        query_embedding: list[float],
        limit: int = 5,
    ) -> list[ChunkResponse]:
        """Find most similar chunks using cosine distance."""
        async with self.pool.acquire() as conn:
            rows = await conn.fetch(
                """
                SELECT id, content, chunk_index,
                       1 - (embedding <=> $1) as similarity
                FROM chunks
                ORDER BY embedding <=> $1
                LIMIT $2
                """,
                np.array(query_embedding),
                limit,
            )
            return [
                ChunkResponse(
                    id=row["id"],
                    content=row["content"],
                    chunk_index=row["chunk_index"],
                    similarity=float(row["similarity"]),
                )
                for row in rows
            ]

    async def delete_by_document(self, document_id: UUID) -> int:
        """Delete all chunks for a document and return count."""
        async with self.pool.acquire() as conn:
            result = await conn.execute(
                "DELETE FROM chunks WHERE document_id = $1",
                document_id,
            )
            return int(result.split()[-1])
