# Environment Configuration Enhancement

**Date:** 2026-01-26
**Status:** Approved
**Author:** Claude + Jason

## Overview

Enhance AgentOS environment configuration to support LiteLLM proxy mode and Redis session storage alongside PostgreSQL.

## Goals

1. Support external LiteLLM proxy with automatic SDK fallback
2. Add Redis as optional session storage backend
3. Enable per-agent model configuration via environment variables
4. Maintain backwards compatibility with existing setups

## Design

### LiteLLM Configuration

**Behavior:**

- Default: SDK mode using `LITELLM_API_KEY`
- If `LITELLM_API_BASE` is set: Proxy mode (connects to external LiteLLM proxy)

**Model Selection Priority:**

1. Per-agent env var (e.g., `KNOWLEDGE_AGENT_MODEL`)
2. Default model env var (`LITELLM_DEFAULT_MODEL`)
3. Hardcoded fallback (`gpt-5-mini`)

**Environment Variables:**

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `LITELLM_API_KEY` | Yes | - | API key for LiteLLM |
| `LITELLM_API_BASE` | No | - | Proxy URL (enables proxy mode) |
| `LITELLM_DEFAULT_MODEL` | No | `gpt-5-mini` | Default model for all agents |
| `KNOWLEDGE_AGENT_MODEL` | No | - | Model override for Knowledge Agent |
| `MCP_AGENT_MODEL` | No | - | Model override for MCP Agent |

### Session Storage

**Behavior:**

- Default: PostgreSQL for session storage
- If `REDIS_URL` is set: Redis for session storage
- PostgreSQL always used for vector search (pgvector requirement)

**Environment Variables:**

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `REDIS_URL` | No | - | Redis connection URL (enables Redis sessions) |

### PostgreSQL Configuration

No changes to existing variables:

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `DB_HOST` | No | `localhost` | Database host |
| `DB_PORT` | No | `5432` | Database port |
| `DB_USER` | No | `ai` | Database username |
| `DB_PASS` | No | `ai` | Database password |
| `DB_DATABASE` | No | `ai` | Database name |

## Implementation

### New File: `app/config.py`

Centralized configuration helpers:

```python
"""
Application Configuration
=========================

Centralized configuration from environment variables.
"""

from os import getenv


def get_litellm_config() -> dict:
    """Build LiteLLM configuration from environment."""
    config = {
        "api_key": getenv("LITELLM_API_KEY"),
    }

    api_base = getenv("LITELLM_API_BASE")
    if api_base:
        config["api_base"] = api_base

    return config


def get_model_id(agent_name: str) -> str:
    """Get model ID for an agent.

    Priority:
    1. Agent-specific env var (e.g., KNOWLEDGE_AGENT_MODEL)
    2. Default model env var (LITELLM_DEFAULT_MODEL)
    3. Hardcoded fallback
    """
    env_key = agent_name.upper().replace(" ", "_") + "_MODEL"

    return getenv(
        env_key,
        getenv("LITELLM_DEFAULT_MODEL", "gpt-5-mini")
    )
```

### Modified: `db/session.py`

Add Redis support:

```python
"""
Database Session
================

Database connection and session management.
Supports PostgreSQL (default) and Redis for session storage.
"""

from os import getenv
from typing import Generator

from agno.db.postgres import PostgresDb
from sqlalchemy.engine import Engine, create_engine
from sqlalchemy.orm import Session, sessionmaker

from db.url import get_db_url

# =============================================================================
# PostgreSQL Setup (always available for vector search)
# =============================================================================
db_url: str = get_db_url()
db_engine: Engine = create_engine(db_url, pool_pre_ping=True)
SessionLocal: sessionmaker[Session] = sessionmaker(
    autocommit=False, autoflush=False, bind=db_engine
)


# =============================================================================
# Session Storage Backend
# =============================================================================
def get_session_db() -> PostgresDb | "RedisDb":
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


def get_db() -> Generator[Session, None, None]:
    """Dependency to get a database session."""
    db: Session = SessionLocal()
    try:
        yield db
    finally:
        db.close()
```

### Modified: `agents/knowledge_agent.py`

Use config helpers:

```python
from agno.models.litellm import LiteLLM
from app.config import get_litellm_config, get_model_id
from db.session import get_session_db, get_postgres_db, db_url

agent_db = get_session_db()

knowledge = Knowledge(
    name="Knowledge Base",
    vector_db=PgVector(
        db_url=db_url,
        table_name="knowledge_agent_docs",
        search_type=SearchType.hybrid,
        embedder=LiteLLMEmbedder(id="text-embedding-3-small"),
    ),
    max_results=10,
    contents_db=get_postgres_db(),
)

knowledge_agent = Agent(
    name="Knowledge Agent",
    model=LiteLLM(
        id=get_model_id("Knowledge Agent"),
        **get_litellm_config(),
    ),
    db=agent_db,
    knowledge=knowledge,
    # ... rest unchanged
)
```

### Modified: `agents/mcp_agent.py`

Use config helpers:

```python
from agno.models.litellm import LiteLLMResponses
from app.config import get_litellm_config, get_model_id
from db.session import get_session_db

agent_db = get_session_db()

mcp_agent = Agent(
    name="MCP Agent",
    model=LiteLLMResponses(
        id=get_model_id("MCP Agent"),
        **get_litellm_config(),
    ),
    db=agent_db,
    # ... rest unchanged
)
```

### Modified: `compose.yaml`

Add optional Redis service:

```yaml
services:
  agentos-db:
    # ... unchanged

  agentos-redis:
    image: redis:7-alpine
    container_name: agentos-redis
    restart: unless-stopped
    ports:
      - "6379:6379"
    volumes:
      - redisdata:/data
    command: redis-server --appendonly yes
    networks:
      - agentos
    profiles:
      - redis

  agentos-api:
    # ... existing config
    environment:
      # LiteLLM
      LITELLM_API_KEY: ${LITELLM_API_KEY}
      LITELLM_API_BASE: ${LITELLM_API_BASE:-}
      LITELLM_DEFAULT_MODEL: ${LITELLM_DEFAULT_MODEL:-gpt-5-mini}
      KNOWLEDGE_AGENT_MODEL: ${KNOWLEDGE_AGENT_MODEL:-}
      MCP_AGENT_MODEL: ${MCP_AGENT_MODEL:-}
      # PostgreSQL
      DB_HOST: agentos-db
      DB_PORT: 5432
      DB_USER: ${DB_USER:-ai}
      DB_PASS: ${DB_PASS:-ai}
      DB_DATABASE: ${DB_DATABASE:-ai}
      # Redis (optional)
      REDIS_URL: ${REDIS_URL:-}
      # ... rest unchanged

volumes:
  pgdata:
  redisdata:
```

### Modified: `example.env`

```env
# =============================================================================
# LiteLLM Configuration
# =============================================================================

# API key for LiteLLM (required)
LITELLM_API_KEY=sk-***

# Proxy mode: Uncomment to use an external LiteLLM proxy instead of direct SDK
# LITELLM_API_BASE=https://your-litellm-proxy.example.com

# Default model for all agents
LITELLM_DEFAULT_MODEL=gpt-5-mini

# Per-agent model overrides (optional)
# KNOWLEDGE_AGENT_MODEL=gpt-4
# MCP_AGENT_MODEL=claude-3-opus

# =============================================================================
# PostgreSQL Database (required - used for vector search)
# =============================================================================

DB_HOST=localhost
DB_PORT=5432
DB_USER=ai
# Generate secure password: openssl rand -base64 24 | tr -d '/+=' | head -c 32
DB_PASS=ai
DB_DATABASE=ai

# =============================================================================
# Redis (optional - for session storage)
# =============================================================================

# Uncomment to use Redis for session storage instead of PostgreSQL
# When using docker compose --profile redis:
# REDIS_URL=redis://agentos-redis:6379
#
# For external Redis:
# REDIS_URL=redis://username:password@your-redis-host:6379

# =============================================================================
# Other LLM Providers (optional - for direct SDK access)
# =============================================================================

# OPENAI_API_KEY=sk-***
# ANTHROPIC_API_KEY=sk-ant-***
# GOOGLE_API_KEY=***
```

### Modified: `pyproject.toml`

Add Redis dependency:

```toml
dependencies = [
    # ... existing
    "redis",
]
```

## File Changes Summary

| File | Action |
|------|--------|
| `example.env` | Update with new variables |
| `app/config.py` | Create new file |
| `db/session.py` | Add `get_session_db()` |
| `agents/knowledge_agent.py` | Use config helpers |
| `agents/mcp_agent.py` | Use config helpers |
| `compose.yaml` | Add Redis service + new env vars |
| `pyproject.toml` | Add `redis` dependency |
| `requirements.txt` | Regenerate after pyproject.toml change |

## Usage

### Default (PostgreSQL only, SDK mode)

```bash
# .env
LITELLM_API_KEY=sk-...

# Start
docker compose up -d
```

### With Redis Sessions

```bash
# .env
LITELLM_API_KEY=sk-...
REDIS_URL=redis://agentos-redis:6379

# Start with Redis profile
docker compose --profile redis up -d
```

### With LiteLLM Proxy

```bash
# .env
LITELLM_API_KEY=sk-...
LITELLM_API_BASE=https://your-litellm-proxy.example.com

# Start
docker compose up -d
```

### Custom Models

```bash
# .env
LITELLM_API_KEY=sk-...
LITELLM_DEFAULT_MODEL=gpt-4
KNOWLEDGE_AGENT_MODEL=claude-3-opus
MCP_AGENT_MODEL=gpt-5-mini

# Start
docker compose up -d
```

## Backwards Compatibility

Existing `.env` files continue to work:

- `LITELLM_API_KEY` still required
- Missing new variables use sensible defaults
- PostgreSQL remains default session storage
- SDK mode remains default LiteLLM behavior
