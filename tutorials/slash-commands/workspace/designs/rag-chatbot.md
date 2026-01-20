# Design: RAG Chatbot

## Overview

A RAG (Retrieval-Augmented Generation) chatbot that allows users to upload documents to a knowledge base and ask questions that are answered using relevant context from those documents. Built with FastAPI, PostgreSQL/pgvector, OpenAI embeddings, and Claude for responses.

## Context

This example demonstrates the slash commands workflow (`/design` -> `/plan` -> `/task`) in a realistic production scenario. Users need to:
- Build knowledge bases from their documents
- Ask questions and get accurate answers grounded in their data
- See which sources informed each response

## Goals and Non-Goals

**Goals:**
- Upload text documents to build a knowledge base
- Embed documents using OpenAI embeddings and store vectors in pgvector
- Retrieve relevant chunks for user queries
- Generate answers using Claude with retrieved context
- Clean, modern UI with document management and chat

**Non-Goals:**
- User authentication (would complicate the demo)
- Multi-tenant document isolation
- Advanced chunking strategies (recursive, semantic)
- Hybrid search (keyword + vector)
- PDF/DOCX parsing (text files only)

## Proposed Solution

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│   index.html    │────▶│   FastAPI       │────▶│  PostgreSQL     │
│   (Tailwind)    │     │   Backend       │     │  + pgvector     │
└─────────────────┘     └────────┬────────┘     └─────────────────┘
                                 │
                    ┌────────────┼────────────┐
                    ▼            ▼            ▼
              ┌─────────┐  ┌─────────┐  ┌─────────┐
              │ OpenAI  │  │ Claude  │  │ Upload  │
              │ Embed   │  │ Chat    │  │ Process │
              └─────────┘  └─────────┘  └─────────┘
```

User uploads document → Backend chunks text → OpenAI embeds chunks → pgvector stores vectors.

User asks question → Backend embeds query → pgvector finds similar chunks → Claude generates answer with context.

## Technical Design

**Data Model:**

```
Document
├── id: UUID (PK)
├── filename: String
├── content: Text (original text)
├── created_at: Timestamp
└── updated_at: Timestamp

Chunk
├── id: UUID (PK)
├── document_id: UUID (FK -> Document)
├── content: Text (chunk text)
├── embedding: vector(1536) (OpenAI ada-002 dimensions)
├── chunk_index: Integer
└── created_at: Timestamp
```

**API Endpoints:**

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/` | GET | Serve chat UI |
| `/api/documents` | GET | List all documents |
| `/api/documents` | POST | Upload new document |
| `/api/documents/{id}` | DELETE | Remove document and chunks |
| `/api/chat` | POST | RAG chat endpoint |
| `/health` | GET | Health check |

**Key Components:**

1. **Document Processor** - Extract text, chunk into segments (500 chars, 50 overlap)
2. **Embedding Service** - Generate OpenAI embeddings (text-embedding-ada-002)
3. **Vector Store** - pgvector operations (store, cosine similarity search)
4. **RAG Engine** - Orchestrate retrieval and generation
5. **Chat Service** - Claude API integration (claude-sonnet-4-20250514)

**Chunking Strategy:**

Fixed-size chunking with overlap:
- Chunk size: 500 characters
- Overlap: 50 characters
- Split on sentence boundaries when possible

## Alternatives Considered

| Decision | Options | Choice | Rationale |
|----------|---------|--------|-----------|
| Vector DB | pgvector, Pinecone, ChromaDB | pgvector | PostgreSQL native, no extra service |
| Embeddings | OpenAI, Cohere, local | OpenAI | Best quality, simple API |
| LLM | OpenAI GPT-4, Claude | Claude | Better instruction following |
| Chunking | Fixed-size, recursive, semantic | Fixed-size | Simple, predictable |
| Frontend | React, Vue, plain HTML | Plain HTML + Tailwind | Single file, no build step |

## Dependencies and Risks

**Dependencies:**
- `fastapi` - Web framework
- `uvicorn` - ASGI server
- `anthropic` - Claude API client
- `openai` - Embeddings API
- `asyncpg` - Async PostgreSQL driver
- `pgvector` - Vector extension bindings
- `python-multipart` - File uploads

**Risks:**
- PostgreSQL requires pgvector extension installed
- Two API keys needed (OpenAI + Anthropic)
- Large documents may hit rate limits

**Mitigations:**
- Provide clear setup instructions for pgvector
- Document required environment variables
- Implement chunking to stay within limits

## Acceptance Criteria

- [ ] User can upload a document and see it in the list
- [ ] Uploaded documents are chunked and embedded
- [ ] Chat queries retrieve relevant chunks
- [ ] Claude generates coherent answers using context
- [ ] Response shows which sources were used
- [ ] UI is clean and responsive
- [ ] All endpoints have proper error handling
