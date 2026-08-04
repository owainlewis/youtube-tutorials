#!/usr/bin/env python3
"""Verify the PostgreSQL RAG sample without services or credentials."""

from __future__ import annotations

import ast
import sys
import tomllib
from pathlib import Path


ROOT = Path(__file__).resolve().parent


def require(text: str, fragment: str, label: str, errors: list[str]) -> None:
    """Record an error when a required source fragment is missing."""
    if fragment.lower() not in text.lower():
        errors.append(f"{label}: missing {fragment!r}")


def check_files(errors: list[str]) -> None:
    expected = [
        ".env.example",
        "docker-compose.yml",
        "pyproject.toml",
        "sql/01_setup.sql",
        "sql/02_vector_search.sql",
        "sql/03_full_text_search.sql",
        "sql/04_hybrid_search.sql",
        "sql/05_seed_data.sql",
        "src/main.py",
        "src/seed.py",
        "src/static/index.html",
    ]
    for relative in expected:
        if not (ROOT / relative).is_file():
            errors.append(f"missing required file: {relative}")


def check_python(errors: list[str]) -> None:
    for relative in ("src/main.py", "src/seed.py", "verify_offline.py"):
        path = ROOT / relative
        try:
            ast.parse(path.read_text(), filename=relative)
        except (OSError, SyntaxError, UnicodeDecodeError) as error:
            errors.append(f"{relative}: {error}")

    with (ROOT / "pyproject.toml").open("rb") as handle:
        project = tomllib.load(handle)["project"]
    dependencies = "\n".join(project["dependencies"])
    for dependency in ("fastapi", "psycopg", "psycopg-pool", "openai"):
        require(dependencies, dependency, "pyproject.toml", errors)


def check_schema(errors: list[str]) -> None:
    schema = (ROOT / "sql/01_setup.sql").read_text()
    for fragment in (
        "CREATE EXTENSION IF NOT EXISTS vector",
        "CREATE TABLE documents",
        "content     TEXT NOT NULL",
        "metadata    JSONB",
        "embedding   vector(1536)",
        "tsvector GENERATED ALWAYS AS",
        "USING hnsw (embedding vector_cosine_ops)",
        "USING gin(fts)",
    ):
        require(schema, fragment, "sql/01_setup.sql", errors)

    hybrid = (ROOT / "sql/04_hybrid_search.sql").read_text()
    for fragment in (
        "CREATE OR REPLACE FUNCTION hybrid_search",
        "query_embedding vector(1536)",
        "vector_results AS",
        "WHERE embedding IS NOT NULL",
        "fts_results AS",
        "ORDER BY ts_rank",
        "FULL OUTER JOIN",
        "ORDER BY c.rrf_score DESC",
    ):
        require(hybrid, fragment, "sql/04_hybrid_search.sql", errors)


def check_configuration(errors: list[str]) -> None:
    compose = (ROOT / "docker-compose.yml").read_text()
    for fragment in (
        "pgvector/pgvector:pg18",
        "./sql:/docker-entrypoint-initdb.d:ro",
        "pg_isready -U postgres",
    ):
        require(compose, fragment, "docker-compose.yml", errors)

    env = (ROOT / ".env.example").read_text()
    main = (ROOT / "src/main.py").read_text()
    seed = (ROOT / "src/seed.py").read_text()
    for name in (
        "OPENAI_API_KEY",
        "DATABASE_URL",
        "OPENAI_EMBEDDING_MODEL",
        "OPENAI_CHAT_MODEL",
    ):
        require(env, name, ".env.example", errors)
    require(main, 'os.getenv("OPENAI_EMBEDDING_MODEL"', "src/main.py", errors)
    require(main, 'os.getenv("OPENAI_CHAT_MODEL"', "src/main.py", errors)
    require(seed, 'os.getenv("OPENAI_EMBEDDING_MODEL"', "src/seed.py", errors)


def main() -> int:
    errors: list[str] = []
    check_files(errors)
    if not errors:
        check_python(errors)
        check_schema(errors)
        check_configuration(errors)
    if errors:
        print("Offline verification failed:", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        return 1
    print("Offline verification passed: Python, SQL, and configuration agree.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
