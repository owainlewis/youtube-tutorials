"""RAG chatbot using PostgreSQL with pgvector for hybrid search."""

import os
from contextlib import asynccontextmanager
from pathlib import Path

import psycopg_pool
from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.responses import HTMLResponse, StreamingResponse
from openai import AsyncOpenAI
from pydantic import BaseModel, Field

load_dotenv()

DATABASE_URL = os.getenv(
    "DATABASE_URL", "postgresql://postgres:postgres@localhost:5432/postgres"
)
EMBEDDING_MODEL = os.getenv("OPENAI_EMBEDDING_MODEL", "text-embedding-3-small")
CHAT_MODEL = os.getenv("OPENAI_CHAT_MODEL", "gpt-4o")

client = AsyncOpenAI()
pool: psycopg_pool.AsyncConnectionPool | None = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Open and close the connection pool with the application lifecycle."""
    global pool
    pool = psycopg_pool.AsyncConnectionPool(
        DATABASE_URL, min_size=2, max_size=10, open=False
    )
    await pool.open()
    yield
    await pool.close()


app = FastAPI(lifespan=lifespan)


async def get_embedding(text: str) -> list[float]:
    """Generate an embedding vector for the given text."""
    response = await client.embeddings.create(model=EMBEDDING_MODEL, input=text)
    return response.data[0].embedding


async def hybrid_search(
    conn, query: str, embedding: list[float], limit: int = 5
) -> list[dict]:
    """Search documents using hybrid search (vector + full-text with RRF)."""
    async with conn.cursor() as cur:
        await cur.execute(
            "SELECT id, content, rrf_score FROM hybrid_search(%s, %s::vector, %s)",
            (query, str(embedding), limit),
        )
        rows = await cur.fetchall()
        return [
            {"id": row[0], "content": row[1], "score": row[2]}
            for row in rows
        ]


class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=2000)


@app.get("/", response_class=HTMLResponse)
async def index():
    """Serve the chat UI."""
    html_path = Path(__file__).parent / "static" / "index.html"
    return html_path.read_text()


@app.post("/chat")
async def chat(request: ChatRequest):
    """Retrieve relevant documents and stream an LLM response."""
    embedding = await get_embedding(request.message)

    if pool is None:
        raise RuntimeError("Database connection pool is not available")
    async with pool.connection() as conn:
        results = await hybrid_search(conn, request.message, embedding)

    context = "\n\n".join(
        f"[Document {r['id']}]: {r['content']}" for r in results
    )

    async def generate():
        stream = await client.chat.completions.create(
            model=CHAT_MODEL,
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are a customer support agent for Nimbus Cloud, "
                        "a cloud storage and collaboration platform. Answer "
                        "the customer's question based only on the following "
                        "support documents. If the documents don't contain "
                        "the answer, say you'll escalate to a specialist.\n\n"
                        f"Documents:\n{context}"
                    ),
                },
                {"role": "user", "content": request.message},
            ],
            stream=True,
        )
        async for chunk in stream:
            if chunk.choices[0].delta.content:
                yield chunk.choices[0].delta.content

    return StreamingResponse(generate(), media_type="text/plain")
