# Getting Started with AgentOS

This guide walks you through setting up AgentOS and creating your first AI agent interaction.

## Prerequisites

Before you begin, ensure you have:

- **Docker Desktop** installed and running ([Download](https://www.docker.com/products/docker-desktop))
- **LiteLLM API key** ([Get one here](https://example.litellm.com/))
- **Git** for cloning the repository

## Quick Start (5 minutes)

> **Tip:** For local development, we recommend using [mise](https://mise.jdx.dev/) for automatic Python/venv management. See [Developer Guide](./DEVELOPER_GUIDE.md) for mise setup.

### 1. Clone the Repository

```bash
git clone https://github.com/agno-agi/agentos-docker-template.git agentos-docker
cd agentos-docker
```

### 2. Configure Environment

```bash
# Copy the example environment file
cp example.env .env
```

Edit `.env` and configure:

```env
# Required
LITELLM_API_KEY=sk-your-api-key-here

# Optional: Use LiteLLM proxy instead of direct SDK
# LITELLM_API_BASE=https://your-proxy.example.com

# Optional: Override default model for all agents
# LITELLM_DEFAULT_MODEL=gpt-4-turbo

# Optional: Per-agent model overrides
# KNOWLEDGE_AGENT_MODEL=claude-3-opus
# MCP_AGENT_MODEL=gpt-4-turbo
```

### 3. Start AgentOS

```bash
docker compose up -d --build
```

This command:

- Builds the AgentOS container image
- Starts PostgreSQL with pgvector extension
- Starts the AgentOS API server
- Creates the necessary database tables

**Optional**: Start with Redis for session storage:

```bash
docker compose --profile redis up -d --build
```

This additionally starts Redis on localhost:6379 for improved session performance.

### 4. Verify Installation

Check that services are running:

```bash
docker compose ps
```

Expected output:

```bash
NAME            STATUS         PORTS
agentos-api     Up (healthy)   0.0.0.0:8000->8000/tcp
agentos-db      Up (healthy)   0.0.0.0:5432->5432/tcp
agentos-redis   Up (healthy)   0.0.0.0:6379->6379/tcp  # If started with --profile redis
```

### 5. Access the API

Open your browser to:

- **API Documentation**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health

## Your First Chat

### Using the API Docs

1. Open http://localhost:8000/docs
2. Find `POST /v1/chat/knowledge-agent`
3. Click "Try it out"
4. Enter a message:

   ```json
   {
     "message": "What can you help me with?"
   }
   ```

5. Click "Execute"

### Using cURL

```bash
curl -X POST http://localhost:8000/v1/chat/knowledge-agent \
  -H "Content-Type: application/json" \
  -d '{"message": "Hello, what can you do?"}'
```

### Using Python

```python
import requests

response = requests.post(
    "http://localhost:8000/v1/chat/knowledge-agent",
    json={"message": "What is Agno?"}
)

print(response.json()["message"])
```

## Load the Knowledge Base

The Knowledge Agent needs documents to answer questions effectively.

### Load Default Documentation

```bash
docker exec -it agentos-api python -m agents.knowledge_agent
```

This loads:

- Agno Introduction
- Agno Quickstart Guide

### Add Custom Knowledge

```python
import requests

# Add documentation from a URL
requests.post(
    "http://localhost:8000/v1/knowledge/knowledge-agent",
    json={
        "name": "My Documentation",
        "url": "https://example.com/docs/intro.md"
    }
)

# Add text content directly
requests.post(
    "http://localhost:8000/v1/knowledge/knowledge-agent",
    json={
        "name": "Company FAQ",
        "content": """
Q: What does our company do?
A: We build AI-powered solutions.

Q: How do I contact support?
A: Email support@example.com
        """
    }
)
```

## Connect to the Control Plane

For a richer experience, connect AgentOS to the Agno control plane:

1. Open [os.agno.com](https://os.agno.com)
2. Click **"Add OS"**
3. Select **"Local"**
4. Enter `http://localhost:8000`

The control plane provides:

- Visual chat interface
- Conversation history
- Knowledge base management
- Agent configuration

## Common Commands

| Task | Command |
|------|---------|
| Start AgentOS | `docker compose up -d --build` |
| Start with Redis | `docker compose --profile redis up -d --build` |
| Stop AgentOS | `docker compose down` |
| View logs | `docker compose logs -f` |
| Restart after code changes | `docker compose restart` |
| Reset database | `docker compose down -v && docker compose up -d --build` |
| Enter container shell | `docker exec -it agentos-api bash` |
| Format code | `mise run format` |
| Validate code | `mise run validate` |
| Run dev server (local) | `mise run dev` |

## Troubleshooting

### Container won't start

Check logs for errors:

```bash
docker compose logs agentos-api
```

Common issues:

- **Missing API key**: Ensure `LITELLM_API_KEY` is set in `.env`
- **Port conflict**: Another service using port 8000 or 5432

### Database connection failed

```bash
# Check if database is ready
docker compose logs agentos-db

# Restart the database
docker compose restart agentos-db
```

### API returns 500 errors

```bash
# Check application logs
docker compose logs -f agentos-api

# Common fixes:
# 1. Ensure database is fully started
docker compose restart

# 2. Reset and rebuild
docker compose down -v
docker compose up -d --build
```

## Next Steps

Now that AgentOS is running, explore these guides:

- [Creating Custom Agents](./CREATING_AGENTS.md) - Build your own AI agents
- [Developer Guide](./DEVELOPER_GUIDE.md) - Local development setup
- [API Reference](../api/openapi.yaml) - Complete API documentation
- [Architecture Overview](../architecture/ARCHITECTURE.md) - System design

## Getting Help

- **Documentation**: [docs.agno.com](https://docs.agno.com)
- **Discord Community**: [agno.link/discord](https://agno.link/discord)
- **GitHub Issues**: Report bugs or request features
