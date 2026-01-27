"""
Database Session
================

Database connection and session management.
Supports PostgreSQL (default) and Redis for session storage.
"""

from __future__ import annotations

from os import getenv
from typing import TYPE_CHECKING, Generator

if TYPE_CHECKING:
    from agno.db.redis import RedisDb

from agno.db.postgres import PostgresDb
from sqlalchemy.engine import Engine, create_engine
from sqlalchemy.orm import Session, sessionmaker

from db.url import get_db_url

# =============================================================================
# PostgreSQL Setup (always available for vector search)
# =============================================================================
db_url: str = get_db_url()
db_engine: Engine = create_engine(db_url, pool_pre_ping=True)
SessionLocal: sessionmaker[Session] = sessionmaker(autocommit=False, autoflush=False, bind=db_engine)


# =============================================================================
# Session Storage Backend
# =============================================================================
def get_session_db() -> PostgresDb | RedisDb:
    """Get the configured session storage backend.

    Returns Redis if REDIS_URL is set, otherwise PostgreSQL.
    """
    redis_url = getenv("REDIS_URL")

    if redis_url:
        from agno.db.redis import RedisDb

        return RedisDb(db_url=redis_url)

    return PostgresDb(db_url=db_url)


def get_postgres_db() -> PostgresDb:
    """Get PostgreSQL for vector search / knowledge base."""
    return PostgresDb(db_url=db_url)


def get_tracing_db() -> PostgresDb:
    """Get a dedicated PostgreSQL instance for tracing.

    Uses a separate database ID to isolate traces from agent data.
    """
    return PostgresDb(db_url=db_url, id="tracing_db")


def get_db() -> Generator[Session, None, None]:
    """Dependency to get a database session."""
    db: Session = SessionLocal()
    try:
        yield db
    finally:
        db.close()
