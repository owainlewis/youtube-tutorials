# RAG Chatbot

A retrieval-augmented generation chatbot that answers questions using your uploaded documents.

## Features

- Upload text documents to build a knowledge base
- Automatic chunking and embedding with OpenAI
- Vector similarity search with PostgreSQL/pgvector
- AI responses powered by Claude
- Clean, modern UI with Tailwind CSS

## Prerequisites

- Python 3.11+
- PostgreSQL with pgvector extension
- OpenAI API key
- Anthropic API key

## Setup

### 1. Install PostgreSQL with pgvector

```bash
# macOS with Homebrew
brew install postgresql@16
brew install pgvector

# Or use Docker
docker run -d --name postgres \
  -e POSTGRES_PASSWORD=password \
  -p 5432:5432 \
  ankane/pgvector
```

### 2. Create the database

```bash
createdb ragchat
psql ragchat < scripts/init_db.sql
```

### 3. Configure environment

```bash
cp .env.example .env
# Edit .env with your API keys and database URL
```

### 4. Install dependencies

```bash
uv sync
```

### 5. Run the application

```bash
uv run uvicorn main:app --reload
```

Open http://localhost:8000 in your browser.

## Usage

1. Upload a text document using the sidebar
2. Ask questions about the document content
3. View AI responses with source citations

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | Chat UI |
| `/api/documents` | GET | List documents |
| `/api/documents` | POST | Upload document |
| `/api/documents/{id}` | DELETE | Delete document |
| `/api/chat` | POST | Send message |
| `/health` | GET | Health check |

## Project Structure

```
├── main.py              # FastAPI application
├── src/
│   ├── config.py        # Settings
│   ├── database.py      # DB connection
│   ├── models/          # Pydantic models
│   ├── services/        # Business logic
│   └── api/             # API endpoints
├── static/              # Frontend files
├── scripts/             # Database scripts
└── tests/               # Test files
```

## How It Works

1. **Upload**: Documents are chunked into ~500 character segments with overlap
2. **Embed**: Each chunk is embedded using OpenAI's text-embedding-ada-002
3. **Store**: Embeddings are stored in PostgreSQL with pgvector
4. **Query**: User questions are embedded and matched against stored chunks
5. **Generate**: Claude generates responses using the top matching chunks as context
