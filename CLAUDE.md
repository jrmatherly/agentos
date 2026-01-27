# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

AgentOS MatherlyNet is a production-ready API template for running AI agents, teams, and workflows. Built on the [Agno](https://docs.agno.com) framework with FastAPI, PostgreSQL/pgvector, and optional Redis session storage.

## Commands

### Development (with mise)

```bash
# First-time setup (after mise is installed)
mise run setup

# Run development server
mise run dev

# Format code
mise run format

# Validate (lint + type check)
mise run validate

# Regenerate requirements.txt
mise run generate-requirements
mise run generate-requirements:upgrade  # with upgrades
```

### Development (without mise)

```bash
# Setup local environment
./scripts/venv_setup.sh && source .venv/bin/activate

# Run locally (requires DB)
python -m app.main

# Start database only
docker compose up -d agentos-db

# Start with Redis
docker compose --profile redis up -d agentos-db agentos-redis
```

### Docker

```bash
# Start all services
docker compose up -d --build

# Start with Redis profile
docker compose --profile redis up -d --build

# View logs
docker compose logs -f

# Load knowledge base
docker exec -it agentos-api python -m agents.knowledge_agent
```

### Code Quality

```bash
# With mise
mise run format      # Format code
mise run validate    # Lint + type check

# Without mise
./scripts/format.sh
./scripts/validate.sh
ruff format .
ruff check .
mypy . --config-file pyproject.toml
```

### Dependencies

```bash
# With mise
mise run generate-requirements
mise run generate-requirements:upgrade

# Without mise
./scripts/generate_requirements.sh
./scripts/generate_requirements.sh upgrade
```

### Checking for Outdated Packages (UV)

```bash
# Check outdated packages (pip-style)
uv pip list --outdated

# Show dependency tree with outdated markers
uv tree --outdated

# Upgrade all packages in uv.lock
uv lock --upgrade

# Upgrade specific package only
uv lock --upgrade-package <package-name>

# Generate requirements.txt from uv.lock
uv export --format requirements.txt -o requirements.txt

# Compile requirements with upgrades (pip-compile style)
uv pip compile pyproject.toml --upgrade -o requirements.txt
```

**Upgrade Workflow:**

1. Check what's outdated: `uv pip list --outdated` or `uv tree --outdated`
2. Upgrade lock file: `uv lock --upgrade` (all) or `uv lock --upgrade-package <name>` (specific)
3. Regenerate requirements: `mise run generate-requirements` or `uv export --format requirements.txt -o requirements.txt`
4. Test the application
5. Commit `uv.lock` and `requirements.txt`

### Releases

```bash
# Interactive release (prompts for version)
mise run release

# Auto-increment versions
mise run release:patch    # v0.1.0 → v0.1.1
mise run release:minor    # v0.1.0 → v0.2.0
mise run release:major    # v0.1.0 → v1.0.0

# Check release status
gh release list
gh run list --workflow=docker-images.yml
```

## Architecture

### Request Flow

```markdown
HTTP Request → FastAPI (app.main) → AgentOS → Agent → LiteLLM → Model Provider
                                       ↓
                                   PostgresDb/RedisDb (session storage)
                                   PgVector (knowledge base)
```

### Core Components

**Entry Point** (`app/main.py`): Creates `AgentOS` instance, registers agents, exposes FastAPI app.

**Configuration** (`app/config.py`):

- `get_litellm_config()`: Builds LiteLLM config with optional proxy support
- `get_model_id(agent_name)`: Returns model ID with priority: per-agent env var → default env var → fallback

**Session Storage** (`db/session.py`):

- `get_session_db()`: Returns `RedisDb` if `REDIS_URL` set, otherwise `PostgresDb`
- `get_postgres_db()`: Always returns PostgresDb (for vector search)
- Exports `db_url`, `db_engine`, `SessionLocal` for direct SQLAlchemy access

### AgentOS Features

The `AgentOS` instance in `app/main.py` is configured with:

- `tracing=True`: OpenTelemetry tracing stored in PostgreSQL
- `enable_mcp_server=True`: Exposes agents as MCP server at `/mcp` endpoint
- `authorization=True` + `JWT_VERIFICATION_KEY`: Scope-based endpoint authorization (optional)
- `teams=[...]`: Registered team instances
- `workflows=[...]`: Registered workflow instances

### Agents (`agents/`)

| Agent | Purpose | Features |
|-------|---------|----------|
| `knowledge_agent` | Vector search Q&A | Hybrid search, agentic memory, PII guardrail |
| `mcp_agent` | Tool-based Q&A | MCP tools, agentic memory, PII guardrail |
| `reasoning/reasoning_model_agent` | Native reasoning | Chain-of-thought, agentic memory |
| `reasoning/reasoning_tools_agent` | Explicit reasoning | ReasoningTools, think/analyze |
| `reasoning/reasoning_agent` | Structured CoT | reasoning=True flag |
| `tools/finance_agent` | Financial analysis | YFinance tools |
| `tools/web_scraper_agent` | Web extraction | DuckDuckGo, Newspaper4k |
| `tools/research_agent` | Deep research | Multi-source reports, expected_output |
| `learning/learning_assistant` | Adaptive assistant | Agentic memory, user memories |
| `hitl/confirmation_agent` | HITL patterns | User confirmation flows |

### Teams (`teams/`)

| Team | Purpose | Members |
|------|---------|---------|
| `research_team` | Collaborative research | web_researcher, tech_researcher, synthesizer |
| `support_team` | Query routing | doc_agent, escalation_agent, feedback_agent |
| `reasoning_team` | Transparent reasoning | web_agent, finance_agent + ReasoningTools |

### Workflows (`workflows/`)

| Workflow | Purpose | Features |
|----------|---------|----------|
| `content_workflow` | Content creation | researcher → writer → editor (Step-based) |
| `blog_generator` | Blog posts with caching | Async, Pydantic schemas, caching |

### Agent Pattern

Agents follow a consistent structure in `agents/`:

1. Import db helpers and config functions
2. Initialize database connection via `get_session_db()`
3. Define knowledge base if needed (with `PgVector` + `OpenAIEmbedder`)
4. Write instructions as multiline string with WORKFLOW and GUIDELINES sections
5. Create `Agent` instance with standard options
6. Add guardrails via `pre_hooks` if needed

Key agent options used:

- `enable_agentic_memory=True`
- `add_datetime_to_context=True`
- `add_history_to_context=True`
- `num_history_runs=5`
- `markdown=True`
- `pre_hooks=[PIIDetectionGuardrail(mask_pii=True)]` (optional)

### Teams

Teams are groups of agents that collaborate. See `teams/research_team.py`:

```python
from agno.team import Team

my_team = Team(
    id="my-team",
    name="My Team",
    model=LiteLLM(id=get_model_id("My Team"), **get_litellm_config()),
    db=get_session_db(),
    members=[agent1, agent2],  # Agents with specific roles
    enable_agentic_memory=True,
    markdown=True,
)
```

Register in `app/main.py`: `teams=[my_team]`

### Workflows

Workflows chain agents as sequential steps. See `workflows/content_workflow.py`:

```python
from agno.workflow.step import Step
from agno.workflow.workflow import Workflow

step1 = Step(name="research", description="Research topic", agent=researcher)
step2 = Step(name="write", description="Write content", agent=writer)

my_workflow = Workflow(
    name="my-workflow",
    description="Research and write",
    db=get_session_db(),
    steps=[step1, step2],
)
```

Register in `app/main.py`: `workflows=[my_workflow]`

### Guardrails

Use `pre_hooks` to validate input before processing:

```python
from agno.guardrails import PIIDetectionGuardrail

agent = Agent(
    pre_hooks=[PIIDetectionGuardrail(mask_pii=True)],
    ...
)
```

### Model Configuration

Models are configured via environment variables:

1. Per-agent: `{AGENT_NAME}_MODEL` (e.g., `KNOWLEDGE_AGENT_MODEL`)
2. Default: `LITELLM_DEFAULT_MODEL`
3. Fallback: `gpt-5-mini`

Agent names are uppercased with spaces replaced by underscores for env var lookup.

**Note**: `app/main.py` sets `litellm.drop_params = True` to prevent `UnsupportedParamsError` when models don't support certain parameters (e.g., `top_p`).

## Code Style

- **Line length**: 120 characters
- **Type hints**: Required on all functions
- **Docstrings**: Google-style
- **Section dividers**: Use `# ===...` comment blocks for logical sections
- **Module docstrings**: Include module name, description, and `Run:` command

### File Structure

```python
"""
Module Name
===========

Brief description.

Run:
    python -m module.name
"""

# Standard library
# Third-party
# Local imports

# ============================================================================
# Section Name
# ============================================================================
```

## Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `LITELLM_API_KEY` | Yes | LiteLLM API key |
| `LITELLM_API_BASE` | No | Proxy URL (enables proxy mode) |
| `LITELLM_DEFAULT_MODEL` | No | Default model (fallback: gpt-5-mini) |
| `{AGENT}_MODEL` | No | Per-agent model override |
| `DB_HOST/PORT/USER/PASS/DATABASE` | No | PostgreSQL connection (defaults work with compose) |
| `REDIS_URL` | No | Enables Redis session storage |

### JWT RBAC Authentication

| Variable | Required | Description |
|----------|----------|-------------|
| `JWT_VERIFICATION_KEY` | No | RSA public key for JWT verification |
| `JWT_JWKS_FILE` | No | Path to JWKS file (alternative to inline key) |
| `JWT_ALGORITHM` | No | JWT signing algorithm (default: RS256) |
| `JWT_VERIFY_AUDIENCE` | No | Enable audience verification (default: false) |

See [JWT RBAC Guide](docs/guides/JWT_RBAC.md) for detailed configuration.
