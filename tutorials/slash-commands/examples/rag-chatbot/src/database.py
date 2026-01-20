import asyncpg
from pgvector.asyncpg import register_vector

from src.config import settings


async def create_pool() -> asyncpg.Pool:
    """Create and configure the database connection pool."""
    pool = await asyncpg.create_pool(
        settings.database_url,
        min_size=2,
        max_size=10,
        init=_init_connection,
    )
    return pool


async def _init_connection(conn: asyncpg.Connection) -> None:
    """Initialize each connection with pgvector support."""
    await register_vector(conn)
