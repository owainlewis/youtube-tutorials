from openai import AsyncOpenAI


class EmbeddingService:
    """Service for generating text embeddings using OpenAI."""

    MODEL = "text-embedding-ada-002"
    DIMENSIONS = 1536

    def __init__(self, api_key: str):
        self.client = AsyncOpenAI(api_key=api_key)

    async def embed_text(self, text: str) -> list[float]:
        """Embed a single text string."""
        response = await self.client.embeddings.create(
            model=self.MODEL,
            input=text,
        )
        return response.data[0].embedding

    async def embed_batch(self, texts: list[str]) -> list[list[float]]:
        """Embed multiple texts in a single API call."""
        if not texts:
            return []

        response = await self.client.embeddings.create(
            model=self.MODEL,
            input=texts,
        )
        return [item.embedding for item in response.data]
