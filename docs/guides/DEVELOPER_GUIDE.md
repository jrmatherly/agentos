# Developer Guide

This guide covers local development setup, code style, testing, and contribution workflows for AgentOS.

## Local Development Setup

### Prerequisites

- Python 3.12 or later
- Docker (for PostgreSQL)
- Git

### Setup with mise (recommended)

[mise](https://mise.jdx.dev/) provides automatic Python version management and virtual environment activation.

```bash
# Install mise (one-time)
curl https://mise.run | sh
echo 'eval "$(mise activate zsh)"' >> ~/.zshrc  # or bash
source ~/.zshrc

# Clone and enter project
git clone https://github.com/agno-agi/agentos-docker-template.git
cd agentos-docker
# → Python 3.12 + venv auto-activated

# Configure secrets
cp mise.local.toml.example mise.local.toml
# Edit mise.local.toml with your LITELLM_API_KEY

# Install dependencies
mise run setup
```

Available tasks: `mise tasks`

| Command | Description |
|---------|-------------|
| `mise run setup` | Install all dependencies |
| `mise run dev` | Start development server |
| `mise run format` | Format code with ruff |
| `mise run validate` | Run linting + type checking |
| `mise run generate-requirements` | Regenerate requirements.txt |

### Setup without mise

#### Install uv

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

#### Setup Virtual Environment

```bash
# Clone the repository
git clone https://github.com/agno-agi/agentos-docker-template.git
cd agentos-docker

# Run the setup script
./scripts/venv_setup.sh

# Activate the environment
source .venv/bin/activate
```

The setup script:

1. Creates a Python 3.12 virtual environment
2. Installs production dependencies
3. Installs dev dependencies (mypy, ruff)
4. Installs the project in editable mode

### Start Database Only

For local development, start just the database:

```bash
docker compose up -d agentos-db
```

**Optional**: Start with Redis for session storage:

```bash
docker compose --profile redis up -d agentos-db agentos-redis
```

### Configure Environment

```bash
cp example.env .env
```

Edit `.env`:

```env
# Required
LITELLM_API_KEY=sk-your-key

# Database
DB_HOST=localhost
DB_PORT=5432

# Optional: LiteLLM proxy mode
# LITELLM_API_BASE=https://your-proxy.example.com

# Optional: Default model for all agents
# LITELLM_DEFAULT_MODEL=gpt-4-turbo

# Optional: Per-agent model overrides
# KNOWLEDGE_AGENT_MODEL=claude-3-opus
# MCP_AGENT_MODEL=gpt-4-turbo

# Optional: Redis for session storage
# REDIS_URL=redis://localhost:6379
```

### Run the Application

```bash
# Development server with auto-reload
python -m app.main

# Or with uvicorn directly
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

## Code Style

### Tools

| Tool | Purpose | Config |
|------|---------|--------|
| ruff | Linting & formatting | `pyproject.toml` |
| mypy | Type checking | `pyproject.toml` |

### Formatting

```bash
# Format code
./scripts/format.sh

# Or manually
ruff format .
ruff check --select I --fix .  # Sort imports
```

### Linting

```bash
# Check for issues
ruff check .

# Auto-fix issues
ruff check --fix .
```

### Type Checking

```bash
mypy . --config-file pyproject.toml
```

### Pre-commit Checklist

Before committing, run:

```bash
./scripts/format.sh && ./scripts/validate.sh
```

This ensures:

- Code is formatted
- Imports are sorted
- No linting errors
- No type errors

## Project Structure

```tree
agentos-docker/
├── app/                    # Application entry point
│   ├── main.py            # AgentOS initialization
│   ├── config.py          # Environment configuration helpers
│   ├── config.yaml        # UI configuration
│   └── __init__.py
├── agents/                 # Agent definitions
│   ├── knowledge_agent.py
│   ├── mcp_agent.py
│   └── __init__.py
├── db/                     # Database layer
│   ├── url.py             # URL builder
│   ├── session.py         # Session management (PostgreSQL + Redis)
│   └── __init__.py
├── scripts/                # Dev scripts
├── docs/                   # Documentation
├── .github/workflows/      # CI/CD
├── compose.yaml           # Docker Compose (with Redis profile)
├── Dockerfile
├── pyproject.toml         # Project config
└── requirements.txt       # Locked deps
```

## Coding Conventions

### Module Structure

```python
"""
Module Name
===========

Brief description of what this module does.

Run:
    python -m module.name
"""

# Standard library imports
from pathlib import Path
from typing import Generator

# Third-party imports
from agno.agent import Agent
from sqlalchemy.orm import Session

# Local imports
from db.session import get_postgres_db

# ============================================================================
# Section Name
# ============================================================================

# Code here...
```

### Type Hints

Always use type hints:

```python
def get_db_url() -> str:
    """Build database URL from environment."""
    ...

def process_items(items: list[str], limit: int = 10) -> dict[str, int]:
    """Process a list of items."""
    ...
```

### Docstrings

Use Google-style docstrings:

```python
def create_agent(name: str, model: str, tools: list | None = None) -> Agent:
    """Create a new agent with the specified configuration.

    Args:
        name: Display name for the agent.
        model: LLM model identifier (e.g., "gpt-5-mini").
        tools: Optional list of tools to enable.

    Returns:
        Configured Agent instance.

    Raises:
        ValueError: If name is empty.

    Example:
        >>> agent = create_agent("Helper", "gpt-5-mini")
        >>> response = agent.run("Hello")
    """
    ...
```

## Dependency Management

### Adding Dependencies

1. Edit `pyproject.toml`:

```toml
dependencies = [
    "agno==2.4.0",
    "new-package>=1.0.0",  # Add here
]
```

2. Regenerate lockfile:

```bash
./scripts/generate_requirements.sh
```

3. Rebuild container:

```bash
docker compose up -d --build
```

### Upgrading Dependencies

```bash
./scripts/generate_requirements.sh upgrade
```

### Dev Dependencies

```toml
[project.optional-dependencies]
dev = ["mypy", "ruff", "pytest"]
```

Install: `pip install -e ".[dev]"`

### Key Dependencies

| Package | Purpose |
|---------|---------|
| agno | Agent framework |
| agno-infra | Infrastructure utilities |
| fastapi | Web framework |
| litellm | Multi-provider LLM gateway |
| pgvector | Vector embeddings |
| sqlalchemy | ORM |
| redis | Redis client (for optional session storage) |
| mcp | Model Context Protocol |

## Testing

### Running Tests

```bash
# All tests
pytest

# With coverage
pytest --cov=app --cov=agents --cov=db

# Specific test file
pytest tests/test_agents.py

# Verbose output
pytest -v
```

### Writing Tests

```python
# tests/test_knowledge_agent.py
import pytest
from agents.knowledge_agent import knowledge_agent

def test_agent_has_name():
    assert knowledge_agent.name == "Knowledge Agent"

def test_agent_responds_to_greeting():
    response = knowledge_agent.run("Hello")
    assert response.content is not None

@pytest.mark.asyncio
async def test_async_response():
    async for chunk in knowledge_agent.arun_stream("Hello"):
        assert chunk is not None
```

### Test Database

For tests that need a database:

```python
import pytest
from db.session import SessionLocal

@pytest.fixture
def db_session():
    session = SessionLocal()
    yield session
    session.rollback()
    session.close()

def test_with_database(db_session):
    # Use db_session here
    pass
```

## Debugging

### VS Code Configuration

`.vscode/launch.json`:

```json
{
    "version": "0.2.0",
    "configurations": [
        {
            "name": "Python: FastAPI",
            "type": "python",
            "request": "launch",
            "module": "uvicorn",
            "args": ["app.main:app", "--reload"],
            "jinja": true,
            "env": {
                "PYTHONPATH": "${workspaceFolder}"
            }
        },
        {
            "name": "Python: Agent CLI",
            "type": "python",
            "request": "launch",
            "module": "agents.knowledge_agent",
            "console": "integratedTerminal"
        }
    ]
}
```

### Logging

```python
import logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

logger.debug("Debug message")
logger.info("Info message")
logger.error("Error message", exc_info=True)
```

### Docker Debugging

```bash
# View logs
docker compose logs -f agentos-api

# Enter container
docker exec -it agentos-api bash

# Check database
docker exec -it agentos-db psql -U ai -d ai
```

## CI/CD

### GitHub Actions

**Validation** (`.github/workflows/validate.yml`):

- Runs on pull requests
- Checks formatting
- Runs linting
- Runs type checking

**Docker Build** (`.github/workflows/docker-images.yml`):

- Runs on release
- Builds multi-arch images
- Pushes to Docker Hub

### Running CI Locally

```bash
# Same checks as CI
./scripts/format.sh
./scripts/validate.sh
```

### Creating Releases

Use mise to create releases, which triggers the Docker build workflow:

```bash
# Interactive release (prompts for version type)
mise run release

# Auto-increment versions
mise run release:patch    # v0.1.0 → v0.1.1
mise run release:minor    # v0.1.0 → v0.2.0
mise run release:major    # v0.1.0 → v1.0.0

# Check release status
gh release list
gh run list --workflow=docker-images.yml
```

The release script:

1. Auto-detects the latest tag
2. Suggests the next version (with override option)
3. Generates release notes from commits
4. Creates and pushes the git tag
5. Creates a GitHub release (triggers Docker build)

## Contributing

### Workflow

1. Fork the repository
2. Create a feature branch:

   ```bash
   git checkout -b feature/amazing-feature
   ```

3. Make changes
4. Format and validate:

   ```bash
   ./scripts/format.sh && ./scripts/validate.sh
   ```

5. Commit changes:

   ```bash
   git commit -m "Add amazing feature"
   ```

6. Push to your fork:

   ```bash
   git push origin feature/amazing-feature
   ```

7. Open a Pull Request

### Commit Messages

Use conventional commits:

```markdown
feat: add new knowledge search endpoint
fix: resolve database connection timeout
docs: update API documentation
refactor: simplify agent initialization
test: add tests for MCP agent
chore: update dependencies
```

### Pull Request Guidelines

- Keep PRs focused on a single change
- Include tests for new features
- Update documentation as needed
- Ensure CI passes
- Request review from maintainers

## Troubleshooting

### Common Issues

**Import errors**:

```bash
# Ensure PYTHONPATH includes project root
export PYTHONPATH="${PYTHONPATH}:$(pwd)"
```

**Database connection failed**:

```bash
# Check if PostgreSQL is running
docker compose ps agentos-db

# Check connection settings
echo $DB_HOST $DB_PORT
```

**Type errors in IDE**:

```bash
# Regenerate stubs
mypy --install-types
```

### Getting Help

- Check existing [GitHub Issues](https://github.com/agno-agi/agentos-docker-template/issues)
- Join the [Discord Community](https://agno.link/discord)
- Read the [Agno Documentation](https://docs.agno.com)
