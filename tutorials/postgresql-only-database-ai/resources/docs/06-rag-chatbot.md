# Chapter 6: Building the RAG Chatbot

Wire PostgreSQL hybrid search into a FastAPI backend with a streaming chat UI.

## The Problem

You have hybrid search working in SQL. Now you need an application around it: embed the user's question, call hybrid search, pass the results as context to an LLM, and stream the response back. Most RAG tutorials make this complicated with frameworks, abstractions, and dozens of files.

This chatbot is one Python file, one HTML file, and PostgreSQL.

## Core Concept

The architecture is three steps in sequence:

1. **Embed** the user's question with OpenAI
2. **Retrieve** relevant documents with `hybrid_search()`
3. **Generate** a response by passing those documents as context to GPT-4o

```python
results = hybrid_search(conn, request.message)
context = "\n\n".join(f"[Document {r['id']}]: {r['content']}" for r in results)
# Pass context + question to GPT-4o, stream the response
```

## How It Works

```mermaid
sequenceDiagram
    participant User as Browser
    participant API as FastAPI
    participant OAI as OpenAI API
    participant PG as PostgreSQL

    User->>API: POST /chat {"message": "..."}
    API->>OAI: Embed question
    OAI-->>API: Query vector
    API->>PG: SELECT * FROM hybrid_search(query, vector, 5)
    PG-->>API: Top 5 documents
    API->>OAI: Chat completion with documents as context
    OAI-->>API: Streamed response chunks
    API-->>User: Streamed text
```

The browser sends a question. FastAPI embeds it, searches PostgreSQL, and streams the LLM response back. No intermediate caching, no orchestration framework. The entire flow is visible in one file.

## Progressive Examples

### The FastAPI application (`src/main.py`)

The complete backend:

```python
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
    global pool
    pool = psycopg_pool.ConnectionPool(DATABASE_URL, min_size=2, max_size=10)
    yield
    pool.close()


app = FastAPI(lifespan=lifespan)


async def get_embedding(text: str) -> list[float]:
    response = await client.embeddings.create(model=EMBEDDING_MODEL, input=text)
    return response.data[0].embedding


def hybrid_search(conn, query: str, embedding: list[float], limit: int = 5) -> list[dict]:
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
    html_path = Path(__file__).parent / "static" / "index.html"
    return html_path.read_text()


@app.post("/chat")
async def chat(request: ChatRequest):
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
                        "You are a helpful assistant. Answer the user's question "
                        "based on the following documents. If the documents don't "
                        "contain relevant information, say so.\n\n"
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
```

Key details:

- **Connection pool** — `psycopg_pool.ConnectionPool` reuses database connections instead of opening a new one per request. The pool is created on startup and closed on shutdown via the lifespan context manager.
- **Async throughout** — `AsyncOpenAI` and `await` for embedding and chat calls. The `/chat` endpoint is async and never blocks the event loop, so the server can handle concurrent requests while streaming.
- **`get_embedding`** calls OpenAI's embeddings API with the same model used to embed the documents.
- **`hybrid_search`** takes a pre-computed embedding and calls the SQL function. The embedding is generated before the DB connection is checked out.
- **`/chat`** retrieves documents, builds a context string, and streams the GPT-4o response.
- **`/`** serves the static HTML file. No template engine, no build step.

### The seed script (`src/seed.py`)

Before the chatbot can answer questions, you need documents in the database with real embeddings:

```bash
uv run src/seed.py
```

This script embeds 10 sample documents about PostgreSQL, pgvector, and RAG using OpenAI's API, then inserts them with their embeddings. It uses batch embedding (one API call for all documents) to minimize latency and cost.

### The chat UI (`src/static/index.html`)

A single HTML file with inline CSS and JavaScript. It posts to `/chat` and reads the streamed response:

```javascript
const response = await fetch("/chat", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ message }),
});

const reader = response.body.getReader();
const decoder = new TextDecoder();

while (true) {
    const { done, value } = await reader.read();
    if (done) break;
    assistantEl.textContent += decoder.decode(value);
}
```

No React. No build tools. The browser's `ReadableStream` API handles streaming natively.

## Real-World Example

Running the complete system:

```bash
# 1. Start PostgreSQL with pgvector
docker compose up -d

# 2. Set up the Python environment
uv sync

# 3. Add your OpenAI API key
cp .env-sample .env
# Edit .env with your key

# 4. Seed the database with sample documents
uv run src/seed.py

# 5. Start the chatbot
uv run fastapi dev src/main.py
```

Open `http://localhost:8000` and ask a question:

- "How does vector search work in PostgreSQL?" -- retrieves documents about pgvector and cosine distance
- "What is HNSW?" -- keyword match on the acronym plus semantic match on indexing concepts
- "Should I use Supabase for vector search?" -- finds the Supabase document and related context

## Key Takeaways

- The entire backend is one Python file. The entire frontend is one HTML file.
- `hybrid_search()` handles retrieval in a single database call.
- Streaming responses use FastAPI's `StreamingResponse` and the OpenAI streaming API.
- The codebase is deliberately simple -- no frameworks, no abstractions, no unnecessary layers.
- Clone the repo, run three commands, and you have a working RAG chatbot.

## Learn More

- [FastAPI: StreamingResponse](https://fastapi.tiangolo.com/advanced/custom-response/#streamingresponse)
- [OpenAI: Chat Completions streaming](https://platform.openai.com/docs/guides/text-generation/streaming)
- [psycopg 3 documentation](https://www.psycopg.org/psycopg3/docs/)

## What's Next

The chatbot works. But PostgreSQL is not always the right choice. The next chapter covers when you should use a dedicated vector database instead.
