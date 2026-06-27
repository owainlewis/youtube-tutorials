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
EMBEDDING_MODEL = "text-embedding-3-small"

client = AsyncOpenAI()
pool = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Open and close the connection pool with the application lifecycle."""
    global pool
    pool = psycopg_pool.ConnectionPool(DATABASE_URL, min_size=2, max_size=10)
    yield
    pool.close()


app = FastAPI(lifespan=lifespan)


async def get_embedding(text: str) -> list[float]:
    """Generate an embedding vector for the given text."""
    response = await client.embeddings.create(model=EMBEDDING_MODEL, input=text)
    return response.data[0].embedding


def hybrid_search(conn, query: str, embedding: list[float], limit: int = 5) -> list[dict]:
    """Search documents using hybrid search (vector + full-text with RRF)."""
    with conn.cursor() as cur:
        cur.execute(
            "SELECT id, content, rrf_score FROM hybrid_search(%s, %s::vector, %s)",
            (query, str(embedding), limit),
        )
        return [
            {"id": row[0], "content": row[1], "score": row[2]}
            for row in cur.fetchall()
        ]


class ChatRequest(BaseModel):
    message: str = Field(..., max_length=2000)


@app.get("/", response_class=HTMLResponse)
async def index():
    """Serve the chat UI."""
    html_path = Path(__file__).parent / "static" / "index.html"
    return html_path.read_text()


@app.post("/chat")
async def chat(request: ChatRequest):
    """Retrieve relevant documents and stream an LLM response."""
    embedding = await get_embedding(request.message)

    conn = pool.getconn()
    try:
        results = hybrid_search(conn, request.message, embedding)
    finally:
        pool.putconn(conn)

    context = "\n\n".join(
        f"[Document {r['id']}]: {r['content']}" for r in results
    )

    async def generate():
        stream = await client.chat.completions.create(
            model="gpt-4o",
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
