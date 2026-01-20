from uuid import UUID

from fastapi import APIRouter, HTTPException, Request, UploadFile, status

from src.models import DocumentResponse

router = APIRouter(prefix="/api/documents", tags=["documents"])


@router.get("", response_model=list[DocumentResponse])
async def list_documents(request: Request) -> list[DocumentResponse]:
    """List all documents."""
    return await request.app.state.document_service.list_all()


@router.post("", response_model=DocumentResponse, status_code=status.HTTP_201_CREATED)
async def upload_document(request: Request, file: UploadFile) -> DocumentResponse:
    """Upload a new document."""
    if not file.filename:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File must have a filename",
        )

    content = await file.read()
    try:
        text = content.decode("utf-8")
    except UnicodeDecodeError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File must be valid UTF-8 text",
        )

    if not text.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File is empty",
        )

    return await request.app.state.document_service.create(file.filename, text)


@router.delete("/{document_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_document(request: Request, document_id: UUID) -> None:
    """Delete a document and its chunks."""
    deleted = await request.app.state.document_service.delete(document_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found",
        )
