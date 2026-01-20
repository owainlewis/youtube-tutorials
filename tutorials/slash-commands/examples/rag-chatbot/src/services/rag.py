from pydantic import BaseModel
import anthropic

from src.models import ChunkResponse
from src.services.embeddings import EmbeddingService
from src.services.vector_store import VectorStore


class RAGResponse(BaseModel):
    """Response from the RAG service."""

    answer: str
    sources: list[ChunkResponse]


SYSTEM_PROMPT = """You are a helpful assistant that answers questions based on the provided context.
Use only the information in the context to answer. If the context doesn't contain
relevant information, say so clearly."""


class RAGService:
    """Service for retrieval-augmented generation."""

    def __init__(
        self,
        embedding_service: EmbeddingService,
        vector_store: VectorStore,
        anthropic_client: anthropic.AsyncAnthropic,
    ):
        self.embedding_service = embedding_service
        self.vector_store = vector_store
        self.anthropic = anthropic_client

    async def answer(self, question: str, top_k: int = 5) -> RAGResponse:
        """Answer a question using RAG."""
        # Embed the question
        query_embedding = await self.embedding_service.embed_text(question)

        # Search for relevant chunks
        chunks = await self.vector_store.search(query_embedding, limit=top_k)

        # Build context from chunks
        if chunks:
            context_parts = []
            for i, chunk in enumerate(chunks, 1):
                context_parts.append(f"[Source {i}]\n{chunk.content}")
            context = "\n\n---\n\n".join(context_parts)
        else:
            context = "No relevant documents found."

        # Build the prompt
        user_message = f"""Context:
{context}

Question: {question}

Answer based on the context above:"""

        # Call Claude
        response = await self.anthropic.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=1024,
            system=SYSTEM_PROMPT,
            messages=[{"role": "user", "content": user_message}],
        )

        answer = response.content[0].text

        return RAGResponse(answer=answer, sources=chunks)
