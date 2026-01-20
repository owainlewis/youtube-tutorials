---
task: 6
title: Document API endpoints and main app
depends_on: [4]
files: [examples/rag-chatbot/src/api/documents.py, examples/rag-chatbot/main.py, examples/rag-chatbot/src/__init__.py]
---

## Context

We're building a RAG chatbot with document upload functionality. This task creates the REST API endpoints for document management and wires everything together in the main FastAPI application.

The API needs:
- List documents
- Upload document (multipart form)
- Delete document
- Health check
- Serve static files for UI

## Requirements

### Document Endpoints

Create `documents.py` with:

```python
# GET /api/documents
# Returns list of all documents with metadata

# POST /api/documents
# Accepts multipart form with file upload
# Reads file content, creates document
# Returns created document

# DELETE /api/documents/{document_id}
# Deletes document and all chunks
# Returns 204 on success, 404 if not found
```

### Main Application

Create `main.py` with:

```python
# FastAPI app with lifespan for startup/shutdown

# On startup:
# - Create database pool
# - Initialize services
# - Register on app.state

# On shutdown:
# - Close database pool

# Routes:
# - Mount /api/documents router
# - Mount /api/chat router
# - GET /health - return {"status": "ok"}
# - GET / - serve static/index.html
# - Mount /static for CSS/JS files
```

### Error Handling

- 400 for invalid requests (empty file, bad format)
- 404 for document not found
- 500 for internal errors with generic message
- Log errors for debugging

## Technical Notes

- Use `UploadFile` for file upload handling
- Read file as text (UTF-8)
- Use dependency injection for services
- Store services on `app.state` for access in routes
- Use `APIRouter` for organizing endpoints
- Static files with `StaticFiles` mount

Example lifespan:
```python
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    app.state.pool = await create_pool()
    app.state.services = initialize_services(app.state.pool)
    yield
    # Shutdown
    await app.state.pool.close()
```

## Acceptance Criteria

- [ ] GET /api/documents returns document list
- [ ] POST /api/documents handles file upload
- [ ] DELETE /api/documents/{id} removes document
- [ ] 404 returned for missing documents
- [ ] GET /health returns status
- [ ] GET / serves index.html
- [ ] Static files accessible at /static/*
- [ ] App starts and connects to database
- [ ] App shuts down cleanly
