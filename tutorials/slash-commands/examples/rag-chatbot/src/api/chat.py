from fastapi import APIRouter, Request
from pydantic import BaseModel

from src.services.rag import RAGResponse

router = APIRouter(prefix="/api", tags=["chat"])


class ChatRequest(BaseModel):
    message: str


@router.post("/chat", response_model=RAGResponse)
async def chat(request: Request, body: ChatRequest) -> RAGResponse:
    """Send a message and get a RAG-powered response."""
    return await request.app.state.rag_service.answer(body.message)
