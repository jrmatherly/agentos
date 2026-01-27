# API Reference

## AgentOS Endpoints

AgentOS exposes a FastAPI application at `http://localhost:8000`.

### OpenAPI Documentation
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **OpenAPI JSON**: http://localhost:8000/openapi.json

### Core Endpoints (via Agno)

#### Chat with Agent
```
POST /v1/chat/{agent_name}
```
Sends a message to the specified agent.

#### List Agents
```
GET /v1/agents
```
Returns available agents and their metadata.

#### Health Check
```
GET /health
```
Returns service health status.

## Agent Capabilities

### Knowledge Agent
- **Name**: `knowledge-agent`
- **Model**: Configurable via `KNOWLEDGE_AGENT_MODEL` or `LITELLM_DEFAULT_MODEL` (default: gpt-5-mini)
- **Capabilities**:
  - Hybrid vector search (semantic + keyword)
  - Knowledge base Q&A
  - Source citations
  - Agentic memory (remembers context)

### MCP Agent
- **Name**: `mcp-agent`
- **Model**: Configurable via `MCP_AGENT_MODEL` or `LITELLM_DEFAULT_MODEL` (default: gpt-5-mini)
- **Capabilities**:
  - MCP tool execution
  - External data retrieval
  - Agentic memory

## Database Schema

### Session Storage
- **Default**: PostgreSQL (`agent_sessions` table)
- **Optional**: Redis (when `REDIS_URL` is set)

### Knowledge Agent Tables
| Table | Purpose |
|-------|---------|
| `knowledge_agent_docs` | Vector embeddings for knowledge base (always PostgreSQL) |
| `agent_sessions` | Session/memory storage (PostgreSQL or Redis) |

## Configuration

### `app/config.yaml`
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

## Control Plane Integration

Connect to https://os.agno.com to:
- Monitor agent activity
- View conversation history
- Manage knowledge bases
- Configure agent settings
