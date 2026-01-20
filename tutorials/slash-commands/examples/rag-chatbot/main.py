from contextlib import asynccontextmanager
from pathlib import Path

import anthropic
from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from src.config import settings
from src.database import create_pool
from src.services import DocumentService, EmbeddingService, RAGService, VectorStore
from src.api import chat_router, documents_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage application lifecycle."""
    # Startup
    app.state.pool = await create_pool()

    # Initialize services
    embedding_service = EmbeddingService(settings.openai_api_key)
    vector_store = VectorStore(app.state.pool)
    anthropic_client = anthropic.AsyncAnthropic(api_key=settings.anthropic_api_key)

    app.state.document_service = DocumentService(
        app.state.pool,
        embedding_service,
        vector_store,
    )
    app.state.rag_service = RAGService(
        embedding_service,
        vector_store,
        anthropic_client,
    )

    yield

    # Shutdown
    await app.state.pool.close()


app = FastAPI(
    title="RAG Chatbot",
    description="A chatbot with document upload and retrieval-augmented generation",
    version="0.1.0",
    lifespan=lifespan,
)

# Mount API routers
app.include_router(documents_router)
app.include_router(chat_router)

# Mount static files
static_dir = Path(__file__).parent / "static"
app.mount("/static", StaticFiles(directory=static_dir), name="static")


@app.get("/")
async def index():
    """Serve the chat UI."""
    return FileResponse(static_dir / "index.html")


@app.get("/health")
async def health():
    """Health check endpoint."""
    return {"status": "ok"}
