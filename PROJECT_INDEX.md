# Project Index: agentos-docker

Generated: 2026-01-27 | Version: 1.0.0 | **Token-efficient reference (~3KB)**

## 📁 Structure

```tree
├── app/
│   ├── main.py             # AgentOS entry point
│   ├── config.py           # LiteLLM configuration
│   ├── auth.py             # JWT RBAC config
│   └── config.yaml         # Quick prompts
├── agents/
│   ├── knowledge_agent.py  # Vector search Q&A
│   ├── mcp_agent.py        # MCP tools
│   ├── reasoning/          # CoT agents (3)
│   ├── tools/              # Finance, web, research (3)
│   ├── learning/           # Adaptive assistant
│   └── hitl/               # Human-in-the-loop
├── teams/                  # Multi-agent teams (3)
├── workflows/              # Sequential pipelines (2)
├── db/                     # Database utilities
└── scripts/                # Bash utilities
```

## 🚀 Entry Points

| File | Purpose |
|------|---------|
| `app/main.py` | AgentOS + FastAPI app |
| `app/config.py` | `get_litellm_config()`, `get_model_id()` |
| `db/session.py` | `get_session_db()`, `get_postgres_db()` |

## 🤖 Agents

| Agent | File | Features |
|-------|------|----------|
| knowledge | `knowledge_agent.py` | Hybrid search, pgvector, PII guardrail |
| mcp | `mcp_agent.py` | MCP tools, agentic memory |
| reasoning | `reasoning/*.py` | CoT (3 variants) |
| finance | `tools/finance_agent.py` | YFinance |
| web_scraper | `tools/web_scraper_agent.py` | DuckDuckGo, Newspaper4k |
| research | `tools/research_agent.py` | Multi-source reports |
| learning | `learning/learning_assistant.py` | User memories |
| confirmation | `hitl/confirmation_agent.py` | HITL patterns |

## 👥 Teams

| Team | Members | Purpose |
|------|---------|---------|
| research_team | web_researcher, tech_researcher, synthesizer | Collaborative research |
| support_team | doc_agent, escalation_agent, feedback_agent | Query routing |
| reasoning_team | web_agent, finance_agent + ReasoningTools | Transparent reasoning |

## ⚡ Workflows

| Workflow | Steps | Purpose |
|----------|-------|---------|
| content_workflow | researcher → writer → editor | Content creation |
| blog_generator | research → write | Async blog posts |

## 🔌 API Endpoints

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/v1/agents` | GET | List agents |
| `/v1/chat/{agent}` | POST | Chat (SSE) |
| `/v1/teams` | GET | List teams |
| `/health` | GET | Health check |
| `/docs` | GET | Swagger UI |
| `/mcp` | * | MCP server |

## 🔧 Configuration

| File | Purpose |
|------|---------|
| `mise.toml` | Dev tasks |
| `compose.yaml` | Docker stack |
| `pyproject.toml` | Dependencies |

## 🔑 Environment Variables

```bash
# Required
LITELLM_API_KEY=         # LLM provider

# Database (defaults work with compose)
DB_HOST=localhost
DB_PORT=5432
DB_USER=ai
DB_PASS=ai
DB_DATABASE=ai

# Optional
LITELLM_API_BASE=        # Proxy URL
LITELLM_DEFAULT_MODEL=   # Default: gpt-5-mini
{AGENT}_MODEL=           # Per-agent override
REDIS_URL=               # Enable Redis sessions
JWT_VERIFICATION_KEY=    # JWT RBAC
```

## 📝 Quick Start

```bash
# Docker (recommended)
docker compose up -d --build
# API: http://localhost:8000/docs

# Local dev
mise run setup
mise run dev
```

## 🔗 Key Dependencies

| Package | Version | Purpose |
|---------|---------|---------|
| agno | >=2.4.3 | Agent framework |
| fastapi | latest | API framework |
| litellm | >=1.81.3 | LLM gateway |
| pgvector | latest | Vector search |
| sqlalchemy | latest | ORM |
| redis | latest | Session cache |

## 📚 Documentation

- `docs/guides/GETTING_STARTED.md` - Quick start
- `docs/guides/CREATING_AGENTS.md` - Agent development
- `docs/guides/JWT_RBAC.md` - Authentication
- `docs/CODE_REFERENCE.md` - API docs
- `CLAUDE.md` - AI assistant guide
