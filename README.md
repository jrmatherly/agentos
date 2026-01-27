# AgentOS MatherlyNet Template

Run agents, teams, and workflows as a production-ready API. Deploy anywhere Docker runs.

## Quickstart

### Prerequisites

- [Docker Desktop](https://www.docker.com/products/docker-desktop) installed and running
- [LiteLLM API key](https://example.litellm.com/)

### Clone and configure

```sh
git clone https://github.com/agno-agi/agentos-docker-template.git agentos-docker
cd agentos-docker

cp example.env .env
# Add LITELLM_API_KEY to .env
# Optional: Set LITELLM_API_BASE for proxy mode
# Optional: Set per-agent models (e.g., KNOWLEDGE_AGENT_MODEL)
```

> Agno works with any model provider. Update the agents in `/agents` and add dependencies to `pyproject.toml`.

### Start AgentOS

```sh
docker compose up -d --build
```

This starts:

- **AgentOS** (FastAPI server) on http://localhost:8000
- **PostgreSQL** with pgvector on localhost:5432

**Optional**: Start with Redis for session storage:

```sh
docker compose --profile redis up -d --build
```

Open http://localhost:8000/docs to see the API.

### Connect to the control plane

1. Open [os.agno.com](https://os.agno.com)
2. Click "Add OS" and select "Local"
3. Enter `http://localhost:8000`

### Stop AgentOS

```sh
docker compose down
```

## Project Structure

```tree
agentos-docker/
├── agents/              # Your agents
├── app/                 # AgentOS entry point + config helpers
├── db/                  # Database + session management
├── scripts/             # Helper scripts
├── compose.yaml         # Docker Compose configuration
├── Dockerfile           # Container build
├── example.env          # Example environment variables
└── pyproject.toml       # Python dependencies
```

## Common Tasks

### Load a knowledge base

```sh
docker exec -it agentos-api python -m agents.knowledge_agent
```

### View logs

```sh
docker compose logs -f
```

### Restart after code changes

```sh
docker compose restart
```

## Local Development

For development without Docker:

### Option A: With mise (recommended)

```sh
# Install mise (one-time)
curl https://mise.run | sh
echo 'eval "$(mise activate zsh)"' >> ~/.zshrc  # or ~/.bashrc
source ~/.zshrc

# Enter project - Python 3.12 + venv auto-activated
cd agentos-docker

# Configure secrets
cp mise.local.toml.example mise.local.toml
# Edit mise.local.toml with your LITELLM_API_KEY

# Install dependencies
mise run setup

# Start development server
mise run dev
```

### Option B: Manual setup

```sh
# Install uv
curl -LsSf https://astral.sh/uv/install.sh | sh

# Setup environment
./scripts/venv_setup.sh
source .venv/bin/activate

# Configure secrets
cp example.env .env
# Edit .env with your LITELLM_API_KEY

# Run server
python -m app.main
```

### Add dependencies

1. Edit `pyproject.toml`
2. Regenerate requirements:

```sh
mise run generate-requirements  # or ./scripts/generate_requirements.sh
```

3. Rebuild:

```sh
docker compose up -d --build
```

## Learn More

- [Agno Documentation](https://docs.agno.com)
- [AgentOS Documentation](https://docs.agno.com/agent-os)
- [Discord Community](https://agno.link/discord)
