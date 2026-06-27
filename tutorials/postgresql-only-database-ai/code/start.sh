#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")"

# --- .env ---
if [ ! -f .env ]; then
  echo "Creating .env from .env-sample..."
  cp .env-sample .env
  echo "Edit .env and add your OPENAI_API_KEY, then re-run this script."
  exit 1
fi

source .env

if [ -z "${OPENAI_API_KEY:-}" ] || [ "$OPENAI_API_KEY" = "sk-your-openai-api-key-here" ]; then
  echo "Error: Set a valid OPENAI_API_KEY in .env"
  exit 1
fi

# --- Dependencies ---
echo "Installing Python dependencies..."
uv sync --quiet

# --- PostgreSQL ---
echo "Starting PostgreSQL..."
docker compose up -d

echo "Waiting for PostgreSQL to be ready..."
until docker compose exec -T db pg_isready -U postgres > /dev/null 2>&1; do
  sleep 1
done
echo "PostgreSQL is ready."

# --- Seed data ---
echo "Seeding database..."
uv run src/seed.py

# --- Start app ---
echo "Starting FastAPI server..."
echo "Open http://localhost:8000"
uv run fastapi dev src/main.py
