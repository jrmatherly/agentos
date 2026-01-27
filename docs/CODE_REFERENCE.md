# Code Reference

Complete API reference for all modules, classes, and functions in AgentOS.

## Module Index

| Module | Description |
|--------|-------------|
| [`app.main`](#appmain) | Application entry point and AgentOS initialization |
| [`app.config`](#appconfig) | Centralized configuration from environment variables |
| [`agents.knowledge_agent`](#agentsknowledge_agent) | Vector search Q&A agent |
| [`agents.mcp_agent`](#agentsmcp_agent) | MCP tools-based agent |
| [`agents.research_team`](#agentsresearch_team) | Collaborative research team |
| [`agents.content_workflow`](#agentscontent_workflow) | Content creation workflow |
| [`db.url`](#dburl) | Database URL construction |
| [`db.session`](#dbsession) | Database session management |

---

## app.main

**Path**: `app/main.py`

The main entry point for AgentOS. Creates and configures the FastAPI application with registered agents.

### Module Variables

#### `agent_os`

```python
agent_os: AgentOS
```

The AgentOS instance that orchestrates all agents.

**Configuration**:

- `name`: "AgentOS"
- `agents`: List containing `knowledge_agent` and `mcp_agent`
- `config`: Path to `app/config.yaml`

#### `app`

```python
app: FastAPI
```

The FastAPI application instance, obtained from `agent_os.get_app()`.

### Usage

**As a module**:

```python
from app.main import app, agent_os
```

**Running directly**:

```bash
python -m app.main
# Or with uvicorn:
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

### Example

```python
from app.main import agent_os

# Access registered agents
for agent in agent_os.agents:
    print(f"Agent: {agent.name}")

# Get the FastAPI app
app = agent_os.get_app()
```

---

## app.config

**Path**: `app/config.py`

Centralized configuration helpers for reading environment variables and building configuration objects.

### Functions

#### `get_litellm_config() -> dict`

Build LiteLLM configuration from environment variables.

**Returns**: Dictionary with LiteLLM configuration

**Behavior**:

- Always includes `api_key` from `LITELLM_API_KEY`
- If `LITELLM_API_BASE` is set, includes `api_base` (enables proxy mode)

**Example**:

```python
from app.config import get_litellm_config
from agno.models.litellm import LiteLLM

# SDK mode (default)
config = get_litellm_config()
# Returns: {"api_key": "sk-..."}

# Proxy mode (when LITELLM_API_BASE is set)
config = get_litellm_config()
# Returns: {"api_key": "sk-...", "api_base": "https://proxy.example.com"}

# Use with LiteLLM model
model = LiteLLM(id="gpt-5-mini", **get_litellm_config())
```

#### `get_model_id(agent_name: str) -> str`

Get the model ID for an agent with priority-based resolution.

**Parameters**:

- `agent_name`: The agent's display name (e.g., "Knowledge Agent")

**Returns**: Model ID string

**Priority Order**:

1. Agent-specific env var (e.g., `KNOWLEDGE_AGENT_MODEL`)
2. Default model env var (`LITELLM_DEFAULT_MODEL`)
3. Hardcoded fallback (`gpt-5-mini`)

**Example**:

```python
from app.config import get_model_id

# With KNOWLEDGE_AGENT_MODEL=claude-3-opus
model_id = get_model_id("Knowledge Agent")
# Returns: "claude-3-opus"

# Without agent-specific var, uses LITELLM_DEFAULT_MODEL
model_id = get_model_id("MCP Agent")
# Returns: value of LITELLM_DEFAULT_MODEL or "gpt-5-mini"
```

**Environment Variable Naming**:

The agent name is converted to an env var key:

- Spaces replaced with underscores
- Converted to uppercase
- `_MODEL` appended

| Agent Name | Env Var Key |
|------------|-------------|
| Knowledge Agent | `KNOWLEDGE_AGENT_MODEL` |
| MCP Agent | `MCP_AGENT_MODEL` |
| My Custom Agent | `MY_CUSTOM_AGENT_MODEL` |

---

## agents.knowledge_agent

**Path**: `agents/knowledge_agent.py`

An AI agent that answers questions using a vector-based knowledge base with hybrid search (semantic + keyword).

### Module Variables

#### `agent_db`

```python
agent_db: PostgresDb | RedisDb
```

Database connection for agent storage (sessions, memory). Configured via `get_session_db()`.

#### `knowledge`

```python
knowledge: Knowledge
```

Knowledge base configuration with pgvector storage.

**Configuration**:

| Property | Value |
|----------|-------|
| `name` | "Knowledge Base" |
| `table_name` | "knowledge_agent_docs" |
| `search_type` | `SearchType.hybrid` |
| `embedder` | `OpenAIEmbedder(id="text-embedding-3-small")` |
| `max_results` | 10 |
| `contents_db` | PostgreSQL (always, for vector search) |

#### `instructions`

```python
instructions: str
```

System prompt defining agent behavior:

- Search knowledge base for relevant information
- Provide clear, accurate answers
- Include sources when possible
- Ask clarifying questions if needed

#### `knowledge_agent`

```python
knowledge_agent: Agent
```

The configured Agent instance.

**Configuration**:

| Property | Value |
|----------|-------|
| `name` | "Knowledge Agent" |
| `model` | `LiteLLM(id=get_model_id("Knowledge Agent"), **get_litellm_config())` |
| `db` | `get_session_db()` (PostgreSQL or Redis) |
| `enable_agentic_memory` | `True` |
| `add_datetime_to_context` | `True` |
| `add_history_to_context` | `True` |
| `num_history_runs` | 5 |
| `markdown` | `True` |

### Usage

**Import and use**:

```python
from agents.knowledge_agent import knowledge_agent, knowledge

# Chat with the agent
response = knowledge_agent.run("What is Agno?")
print(response.content)
```

**Load knowledge base** (CLI):

```bash
python -m agents.knowledge_agent
```

This runs the `__main__` block which loads documentation:

```python
knowledge.insert(name="Agno Introduction", url="https://docs.agno.com/introduction.md")
knowledge.insert(name="Agno Quickstart", url="https://docs.agno.com/get-started/quickstart.md")
```

### Methods (via Agent class)

#### `run(message: str, session_id: str = None) -> RunResponse`

Send a message to the agent and get a response.

**Parameters**:

- `message`: The user's question or input
- `session_id`: Optional session ID for conversation continuity

**Returns**: `RunResponse` with `content`, `sources`, and metadata

**Example**:

```python
response = knowledge_agent.run(
    message="How do I create an agent?",
    session_id="user_123"
)
print(response.content)
for source in response.sources:
    print(f"- {source.name}: {source.url}")
```

#### `cli_app(stream: bool = True)`

Start an interactive CLI chat session.

**Parameters**:

- `stream`: Enable streaming output (default: True)

---

## agents.mcp_agent

**Path**: `agents/mcp_agent.py`

An AI agent that uses Model Context Protocol (MCP) tools to answer questions.

### Module Variables

#### `agent_db`

```python
agent_db: PostgresDb | RedisDb
```

Database connection for agent storage. Configured via `get_session_db()`.

#### `instructions`

```python
instructions: str
```

System prompt defining agent behavior for tool-based Q&A.

#### `mcp_agent`

```python
mcp_agent: Agent
```

The configured Agent instance.

**Configuration**:

| Property | Value |
|----------|-------|
| `name` | "MCP Agent" |
| `model` | `LiteLLM(id=get_model_id("MCP Agent"), **get_litellm_config())` |
| `db` | `get_session_db()` (PostgreSQL or Redis) |
| `tools` | `[MCPTools(url="https://docs.agno.com/mcp")]` |
| `enable_agentic_memory` | `True` |
| `add_datetime_to_context` | `True` |
| `add_history_to_context` | `True` |
| `num_history_runs` | 5 |
| `markdown` | `True` |

### Usage

**Import and use**:

```python
from agents.mcp_agent import mcp_agent

response = mcp_agent.run("What tools are available?")
print(response.content)
```

**Interactive CLI**:

```bash
python -m agents.mcp_agent
```

### Differences from Knowledge Agent

| Feature | Knowledge Agent | MCP Agent |
|---------|-----------------|-----------|
| Model class | `LiteLLM` | `LiteLLM` |
| Data source | Vector knowledge base | MCP tools |
| Search type | Hybrid (semantic + keyword) | Tool execution |
| Use case | Document Q&A | Dynamic tool use |

---

## agents.research_team

**Path**: `agents/research_team.py`

A team of specialized agents that collaborate on research tasks.

### Module Variables

#### `research_team`

```python
research_team: Team
```

The configured Team instance with three specialized members.

**Team Members**:

| Member | Role | Tools |
|--------|------|-------|
| `web_researcher` | Search the web for current information | `DuckDuckGoTools` |
| `tech_researcher` | Find trending tech news from HackerNews | `HackerNewsTools` |
| `synthesizer` | Combine research into coherent summaries | None |

**Configuration**:

| Property | Value |
|----------|-------|
| `id` | "research-team" |
| `name` | "Research Team" |
| `model` | `LiteLLM(id=get_model_id("Research Team"), **get_litellm_config())` |
| `db` | `get_session_db()` |
| `enable_agentic_memory` | `True` |
| `markdown` | `True` |

### Usage

```python
from agents.research_team import research_team

# Run a research task
response = research_team.run("Research the latest AI developments")
print(response.content)

# Interactive CLI
research_team.cli_app(stream=True)
```

---

## agents.content_workflow

**Path**: `agents/content_workflow.py`

A workflow that researches a topic and generates polished content through sequential steps.

### Module Variables

#### `content_workflow`

```python
content_workflow: Workflow
```

The configured Workflow instance with three sequential steps.

**Workflow Steps**:

| Step | Agent | Purpose |
|------|-------|---------|
| `research` | Content Researcher | Research topic, gather facts with sources |
| `write` | Content Writer | Write engaging article from research |
| `edit` | Content Editor | Polish content for clarity and flow |

**Configuration**:

| Property | Value |
|----------|-------|
| `name` | "content-workflow" |
| `description` | "Research, write, and edit content on any topic" |
| `db` | `get_session_db()` |

### Usage

```python
from agents.content_workflow import content_workflow

# Run the workflow
content_workflow.print_response(
    input="Write an article about AI agents",
    markdown=True,
)
```

---

## db.url

**Path**: `db/url.py`

Utility module for constructing database connection URLs from environment variables.

### Functions

#### `get_db_url() -> str`

Build a database URL from environment variables.

**Returns**: PostgreSQL connection string in SQLAlchemy format

**Environment Variables**:

| Variable | Default | Description |
|----------|---------|-------------|
| `DB_DRIVER` | `postgresql+psycopg` | SQLAlchemy driver |
| `DB_USER` | `ai` | Database username |
| `DB_PASS` | `ai` | Database password |
| `DB_HOST` | `localhost` | Database host |
| `DB_PORT` | `5432` | Database port |
| `DB_DATABASE` | `ai` | Database name |

**Returns Format**:

```bash
{driver}://{user}:{password}@{host}:{port}/{database}
```

**Example**:

```python
from db.url import get_db_url

url = get_db_url()
# Returns: "postgresql+psycopg://ai:ai@localhost:5432/ai"
```

**With custom environment**:

```bash
export DB_HOST=prod-db.example.com
export DB_PASS=secret123
```

```python
url = get_db_url()
# Returns: "postgresql+psycopg://ai:secret123@prod-db.example.com:5432/ai"
```

---

## db.session

**Path**: `db/session.py`

Database connection and session management. Supports PostgreSQL (default) and Redis for session storage.

### Module Variables

#### `db_url`

```python
db_url: str
```

The database URL, obtained from `get_db_url()`.

#### `db_engine`

```python
db_engine: Engine
```

SQLAlchemy engine with connection pooling.

**Configuration**:

- `pool_pre_ping=True`: Validates connections before use

#### `SessionLocal`

```python
SessionLocal: sessionmaker[Session]
```

Session factory for creating database sessions.

**Configuration**:

- `autocommit=False`
- `autoflush=False`
- `bind=db_engine`

### Functions

#### `get_session_db() -> PostgresDb | RedisDb`

Get the configured session storage backend.

**Returns**: `RedisDb` if `REDIS_URL` is set, otherwise `PostgresDb`

**Behavior**:

- Checks for `REDIS_URL` environment variable
- If set, returns a `RedisDb` instance connected to that URL
- If not set, returns a `PostgresDb` instance

**Example**:

```python
from db.session import get_session_db

# Default: PostgreSQL
agent_db = get_session_db()

# With REDIS_URL=redis://localhost:6379
agent_db = get_session_db()  # Returns RedisDb

# Use with an agent
agent = Agent(
    name="My Agent",
    db=agent_db,
    ...
)
```

#### `get_postgres_db() -> PostgresDb`

Get PostgreSQL for vector search and knowledge base storage.

**Returns**: `PostgresDb` instance configured with the database URL

**Note**: Always use this for knowledge base `contents_db`, as vector search requires PostgreSQL with pgvector.

**Example**:

```python
from db.session import get_postgres_db

# For knowledge base (always PostgreSQL)
knowledge = Knowledge(
    name="My Knowledge",
    contents_db=get_postgres_db(),
    ...
)
```

#### `get_db() -> Generator[Session, None, None]`

Dependency generator for FastAPI endpoints that need database access.

**Yields**: SQLAlchemy `Session` instance

**Usage** (FastAPI dependency):

```python
from fastapi import Depends
from db.session import get_db

@app.get("/users")
def get_users(db: Session = Depends(get_db)):
    return db.query(User).all()
```

**Usage** (context manager pattern):

```python
from db.session import SessionLocal

with SessionLocal() as db:
    users = db.query(User).all()
```

---

## Type Reference

### Agno Types

```python
from agno.agent import Agent
from agno.db.postgres import PostgresDb
from agno.db.redis import RedisDb
from agno.knowledge import Knowledge
from agno.knowledge.embedder.openai import OpenAIEmbedder
from agno.models.litellm import LiteLLM
from agno.os import AgentOS
from agno.tools.mcp import MCPTools
from agno.vectordb.pgvector import PgVector, SearchType
```

### SQLAlchemy Types

```python
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session, sessionmaker
```

---

## Configuration Reference

### app/config.yaml

Chat UI configuration for quick prompts.

```yaml
chat:
  quick_prompts:
    knowledge-agent:
      - "What is Agno?"
      - "What is AgentOS?"
      - "What can you do?"
    mcp-agent:
      - "What is Agno?"
      - "What is AgentOS?"
      - "What can you do?"
```

### Environment Variables

Complete list of environment variables:

#### LiteLLM Configuration

| Variable | Default | Required | Description |
|----------|---------|----------|-------------|
| `LITELLM_API_KEY` | - | Yes | LiteLLM API key |
| `LITELLM_API_BASE` | - | No | Proxy URL (enables proxy mode) |
| `LITELLM_DEFAULT_MODEL` | `gpt-5-mini` | No | Default model for all agents |
| `KNOWLEDGE_AGENT_MODEL` | - | No | Model override for Knowledge Agent |
| `MCP_AGENT_MODEL` | - | No | Model override for MCP Agent |

#### Database Configuration

| Variable | Default | Required | Description |
|----------|---------|----------|-------------|
| `DB_DRIVER` | `postgresql+psycopg` | No | Database driver |
| `DB_USER` | `ai` | No | Database username |
| `DB_PASS` | `ai` | No | Database password |
| `DB_HOST` | `localhost` | No | Database host |
| `DB_PORT` | `5432` | No | Database port |
| `DB_DATABASE` | `ai` | No | Database name |

#### Redis Configuration (Optional)

| Variable | Default | Required | Description |
|----------|---------|----------|-------------|
| `REDIS_URL` | - | No | Redis URL (enables Redis sessions) |

#### Runtime Configuration

| Variable | Default | Required | Description |
|----------|---------|----------|-------------|
| `WAIT_FOR_DB` | `False` | No | Wait for DB on startup |
| `PRINT_ENV_ON_LOAD` | `False` | No | Print env on startup |

#### Other LLM Providers (Optional)

| Variable | Default | Required | Description |
|----------|---------|----------|-------------|
| `OPENAI_API_KEY` | - | No | OpenAI API key |
| `ANTHROPIC_API_KEY` | - | No | Anthropic API key |
| `GOOGLE_API_KEY` | - | No | Google API key |
