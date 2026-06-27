# Project Context

## What This Is

A web application built with Python (FastAPI) and PostgreSQL. The frontend is Next.js with TypeScript.

## Structure

```
backend/          Python FastAPI application
frontend/         Next.js application
```

## Conventions

- All API routes under /api/v1/
- Async throughout the backend
- Pydantic schemas for all request/response models
- One service file per domain (users, orders, etc.)
- Tests mirror the source structure (tests/test_users.py for services/users.py)

## Commands

```bash
# Backend
cd backend && uv run pytest           # Run tests
cd backend && uv run uvicorn app.main:app --reload  # Dev server

# Frontend
cd frontend && bun run dev            # Dev server
cd frontend && bun test               # Run tests
```

## Rules

- Never store secrets in code. Use environment variables.
- Always validate user input at the API boundary.
- Write tests for business logic. Don't test framework boilerplate.
- Keep functions under 30 lines. Extract when they grow.
- Use meaningful names. No single-letter variables outside loops.
