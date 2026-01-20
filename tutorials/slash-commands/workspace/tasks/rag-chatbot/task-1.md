---
task: 1
title: Project setup and database schema
depends_on: []
files: [examples/rag-chatbot/pyproject.toml, examples/rag-chatbot/.env.example, examples/rag-chatbot/.gitignore, examples/rag-chatbot/scripts/init_db.sql, examples/rag-chatbot/src/config.py, examples/rag-chatbot/src/database.py]
---

## Context

We're building a RAG chatbot that stores document embeddings in PostgreSQL with pgvector. This task sets up the project foundation: UV package management, database schema, and configuration.

The application uses:
- Python 3.11+ with UV for package management
- FastAPI for the web framework
- PostgreSQL with pgvector extension for vector storage
- OpenAI for embeddings, Anthropic for chat

## Requirements

### Project Setup

Create a UV project with these dependencies:
- `fastapi` - Web framework
- `uvicorn[standard]` - ASGI server
- `anthropic` - Claude API client
- `openai` - Embeddings API
- `asyncpg` - Async PostgreSQL driver
- `pgvector` - Vector extension bindings
- `python-multipart` - File upload support
- `pydantic-settings` - Environment config

Dev dependencies:
- `pytest`
- `ipykernel`

### Database Schema

Create SQL script that:
1. Enables pgvector extension
2. Creates `documents` table with id, filename, content, timestamps
3. Creates `chunks` table with id, document_id, content, embedding, chunk_index
4. Adds foreign key constraint from chunks to documents
5. Creates HNSW index on embedding column for fast similarity search

### Configuration

Create Pydantic settings class that loads:
- `DATABASE_URL` - PostgreSQL connection string
- `OPENAI_API_KEY` - For embeddings
- `ANTHROPIC_API_KEY` - For chat

### Database Connection

Create async database module with:
- Connection pool using asyncpg
- Startup/shutdown lifecycle functions
- Helper for getting connections from pool

## Technical Notes

- Use UUID for primary keys (postgres `gen_random_uuid()`)
- Embedding dimension is 1536 (OpenAI ada-002)
- HNSW index uses cosine distance operator
- Connection pool size: 5-10 connections
- All database operations should be async

## Acceptance Criteria

- [ ] `uv sync` installs all dependencies without errors
- [ ] `pyproject.toml` has correct project metadata
- [ ] `.env.example` documents all required variables
- [ ] `init_db.sql` creates tables with correct schema
- [ ] Config loads environment variables with validation
- [ ] Database pool can connect to PostgreSQL
- [ ] Pool properly closes on shutdown
