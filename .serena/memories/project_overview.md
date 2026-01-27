# AgentOS MatherlyNet - Project Overview

## Purpose
Production-ready API template for running AI agents, teams, and workflows. Built on the [Agno](https://docs.agno.com) framework.

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                        AgentOS                              │
│  ┌─────────────────────────────────────────────────────┐   │
│  │                   FastAPI (app.main)                │   │
│  │  ┌─────────────────┐    ┌─────────────────┐        │   │
│  │  │ Knowledge Agent │    │    MCP Agent    │        │   │
│  │  │ (Vector Search) │    │  (MCP Tools)    │        │   │
│  │  └────────┬────────┘    └────────┬────────┘        │   │
│  │           │                      │                  │   │
│  │           └──────────┬───────────┘                  │   │
│  │                      │                              │   │
│  │    ┌─────────────────┼─────────────────┐            │   │
│  │    │                 │                 │            │   │
│  │    ▼                 ▼                 ▼            │   │
│  │ ┌───────────┐  ┌───────────┐  ┌───────────┐        │   │
│  │ │ PostgreSQL│  │  pgvector │  │   Redis   │        │   │
│  │ │ (sessions)│  │(knowledge)│  │ (optional)│        │   │
│  │ └───────────┘  └───────────┘  └───────────┘        │   │
│  └─────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
```

## Key Components

### Entry Point (`app/main.py`)
- Sets `litellm.drop_params = True` to avoid UnsupportedParamsError
- Creates `AgentOS` instance with registered agents, teams, and workflows
- Configures tracing (`tracing=True`) and MCP server (`enable_mcp_server=True`)
- Loads configuration from `app/config.yaml`
- Exposes FastAPI app on port 8000

### Configuration (`app/config.py`)
- `get_litellm_config()`: Build LiteLLM config with optional proxy support
- `get_model_id(agent_name)`: Get model ID with priority: per-agent > default > fallback

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

### Features
| Feature | Configuration |
|---------|---------------|
| **Tracing** | `tracing=True` in AgentOS - OpenTelemetry traces stored in PostgreSQL |
| **MCP Server** | `enable_mcp_server=True` - Exposes agents at `/mcp` endpoint |
| **Guardrails** | `PIIDetectionGuardrail(mask_pii=True)` on agents via `pre_hooks` |
| **JWT RBAC** | `authorization=True` + `JWT_VERIFICATION_KEY` env var - Scope-based endpoint authorization |

### Database (`db/`)
| Module | Purpose |
|--------|---------|
| `url.py` | Build DB URL from environment |
| `session.py` | SQLAlchemy engine + session factory + `get_session_db()` for PostgreSQL/Redis |

## File Structure
```
agentos-docker/
├── app/
│   ├── main.py           # AgentOS entry point
│   ├── config.py         # Environment configuration helpers
│   ├── config.yaml       # Chat UI configuration
│   └── __init__.py
├── agents/
│   ├── knowledge_agent.py  # Vector search agent
│   ├── mcp_agent.py        # MCP tools agent
│   ├── reasoning/          # Reasoning agents (model, tools, flag)
│   ├── tools/              # Tool showcase agents (finance, scraper, research)
│   ├── learning/           # Learning assistant
│   ├── hitl/               # Human-in-the-loop agents
│   └── __init__.py
├── teams/
│   ├── research_team.py    # Collaborative research team
│   ├── support_team.py     # Query routing team
│   ├── reasoning_team.py   # Transparent reasoning team
│   └── __init__.py
├── workflows/
│   ├── content_workflow.py # Step-based content workflow
│   ├── blog_generator.py   # Async blog generation workflow
│   └── __init__.py
├── db/
│   ├── url.py            # Database URL builder
│   ├── session.py        # Session management
│   └── __init__.py
├── scripts/
│   ├── entrypoint.sh     # Container entrypoint
│   ├── format.sh         # ruff format + import sort
│   ├── validate.sh       # ruff check + mypy
│   ├── venv_setup.sh     # Local dev setup
│   ├── generate_requirements.sh
│   └── build_image.sh
├── .github/workflows/
│   ├── docker-images.yml # Release builds
│   └── validate.yml      # CI validation
├── compose.yaml          # Docker Compose stack (with Redis profile)
├── Dockerfile            # Container build
├── mise.toml             # Development workflow config
├── mise.local.toml.example  # Secrets template
├── mise.lock             # Locked tool versions
├── pyproject.toml        # Dependencies + tools config
├── requirements.txt      # Locked dependencies
└── example.env           # Environment template
```

## Tech Stack
| Layer | Technology |
|-------|------------|
| Language | Python 3.12+ |
| Framework | Agno (FastAPI-based) |
| AI Models | LiteLLM (multi-provider) |
| Embeddings | text-embedding-3-small |
| Database | PostgreSQL 18 + pgvector |
| Container | Docker + Docker Compose |
| Dev Workflow | mise |
| Package Manager | uv |
| Linting | ruff |
| Type Checking | mypy |

## Environment Variables

### LiteLLM Configuration
| Variable | Default | Description |
|----------|---------|-------------|
| `LITELLM_API_KEY` | required | LiteLLM API key |
| `LITELLM_API_BASE` | - | Proxy URL (enables proxy mode) |
| `LITELLM_DEFAULT_MODEL` | gpt-5-mini | Default model for all agents |
| `KNOWLEDGE_AGENT_MODEL` | - | Model override for Knowledge Agent |
| `MCP_AGENT_MODEL` | - | Model override for MCP Agent |

### Database Configuration
| Variable | Default | Description |
|----------|---------|-------------|
| `DB_HOST` | localhost | Database host |
| `DB_PORT` | 5432 | Database port |
| `DB_USER` | ai | Database user |
| `DB_PASS` | ai | Database password |
| `DB_DATABASE` | ai | Database name |
| `DB_DRIVER` | postgresql+psycopg | SQLAlchemy driver |

### Redis (Optional)
| Variable | Default | Description |
|----------|---------|-------------|
| `REDIS_URL` | - | Redis URL (enables Redis sessions) |

### JWT RBAC Authentication
| Variable | Default | Description |
|----------|---------|-------------|
| `JWT_VERIFICATION_KEY` | - | RSA public key for JWT verification |
| `JWT_JWKS_FILE` | - | Path to JWKS file (alternative) |
| `JWT_ALGORITHM` | RS256 | JWT signing algorithm |

### Runtime
| Variable | Default | Description |
|----------|---------|-------------|
| `WAIT_FOR_DB` | False | Wait for DB on startup |
| `PRINT_ENV_ON_LOAD` | False | Print env on startup |

## URLs
- **API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs
- **Control Plane**: https://os.agno.com
