"""Shared runtime configuration for every RAG example."""

from functools import cache
import os

try:
    from dotenv import load_dotenv
except ImportError:  # The credential-free tests use only the standard library.
    load_dotenv = None

if load_dotenv is not None:
    load_dotenv()


CHAT_MODEL = os.getenv("OPENAI_CHAT_MODEL", "gpt-5")
EMBEDDING_MODEL = os.getenv("OPENAI_EMBEDDING_MODEL", "text-embedding-3-small")
DATABASE_URL = os.getenv(
    "DATABASE_URL", "postgresql://raguser:ragpass@localhost:5432/ecommerce"
)


@cache
def get_client():
    """Create the OpenAI client only when a live example needs it."""
    from openai import OpenAI

    return OpenAI()


def connect():
    """Create a PostgreSQL connection only when a live example needs it."""
    import psycopg

    return psycopg.connect(DATABASE_URL)
