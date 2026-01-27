# Creating Custom Agents

This guide explains how to create new AI agents in AgentOS, covering knowledge-based agents, tool-using agents, and advanced configurations.

## Agent Basics

An agent in AgentOS is an AI assistant with:

- A **model** (the LLM that powers it)
- **Instructions** (system prompt defining behavior)
- **Tools** or **Knowledge** (capabilities)
- **Memory** (session and long-term context)

## Quick Start: Minimal Agent

Create a new file `agents/my_agent.py`:

```python
"""
My Agent
========

A simple agent that answers questions.
"""

from agno.agent import Agent
from agno.models.litellm import LiteLLM

from app.config import get_litellm_config, get_model_id
from db.session import get_session_db

# Database for memory storage (PostgreSQL or Redis based on REDIS_URL)
agent_db = get_session_db()

# Create the agent
my_agent = Agent(
    name="My Agent",
    model=LiteLLM(id=get_model_id("My Agent"), **get_litellm_config()),
    db=agent_db,
    instructions="You are a helpful assistant.",
    markdown=True,
)
```

**Configuration helpers**:

- `get_model_id("My Agent")`: Returns `MY_AGENT_MODEL` env var, or `LITELLM_DEFAULT_MODEL`, or `gpt-5-mini`
- `get_litellm_config()`: Returns `api_key` and optionally `api_base` for proxy mode
- `get_session_db()`: Returns Redis if `REDIS_URL` is set, otherwise PostgreSQL

Register it in `app/main.py`:

```python
from agents.my_agent import my_agent

agent_os = AgentOS(
    name="AgentOS",
    agents=[knowledge_agent, mcp_agent, my_agent],  # Add here
    config=str(Path(__file__).parent / "config.yaml"),
)
```

Restart to apply:

```bash
# With Docker
docker compose restart

# Local development (with mise)
# Server auto-reloads on file changes
```

## Agent Types

### 1. Knowledge Agent (RAG)

Uses vector search to answer questions from documents.

```python
from agno.agent import Agent
from agno.knowledge import Knowledge
from agno.knowledge.embedder.openai import OpenAIEmbedder
from agno.models.litellm import LiteLLM
from agno.vectordb.pgvector import PgVector, SearchType

from app.config import get_litellm_config, get_model_id
from db.session import db_url, get_postgres_db, get_session_db

# Session storage (PostgreSQL or Redis)
agent_db = get_session_db()

# Configure knowledge base (always PostgreSQL for vector search)
knowledge = Knowledge(
    name="Product Documentation",
    vector_db=PgVector(
        db_url=db_url,
        table_name="product_docs",  # Unique table name
        search_type=SearchType.hybrid,  # semantic + keyword
        embedder=OpenAIEmbedder(id="text-embedding-3-small"),
    ),
    max_results=10,
    contents_db=get_postgres_db(),  # Knowledge always uses PostgreSQL
)

product_agent = Agent(
    name="Product Agent",
    model=LiteLLM(id=get_model_id("Product Agent"), **get_litellm_config()),
    db=agent_db,
    knowledge=knowledge,
    instructions="""You are a product documentation assistant.

Answer questions using the knowledge base. If information isn't available,
say so clearly. Always cite your sources.""",
    enable_agentic_memory=True,
    markdown=True,
)
```

**Loading knowledge:**

```python
if __name__ == "__main__":
    # From URLs
    knowledge.insert(name="User Guide", url="https://docs.example.com/guide.md")

    # From local files
    knowledge.insert(name="FAQ", path="./docs/faq.md")

    # From text
    knowledge.insert(name="Quick Tips", content="Tip 1: ...")
```

### 2. Tool Agent (MCP)

Uses external tools via Model Context Protocol.

```python
from agno.agent import Agent
from agno.models.litellm import LiteLLM
from agno.tools.mcp import MCPTools

from app.config import get_litellm_config, get_model_id
from db.session import get_session_db

agent_db = get_session_db()

tool_agent = Agent(
    name="Tool Agent",
    model=LiteLLM(id=get_model_id("Tool Agent"), **get_litellm_config()),
    db=agent_db,
    tools=[
        MCPTools(url="https://api.example.com/mcp"),
    ],
    instructions="""You are an assistant with access to external tools.

Use the available tools to help users with their requests.
Explain what you're doing when using tools.""",
    enable_agentic_memory=True,
    markdown=True,
)
```

### 3. Custom Tools Agent

Create your own tools using the `@tool` decorator.

```python
from agno.agent import Agent
from agno.models.litellm import LiteLLM
from agno.tools import tool

from app.config import get_litellm_config, get_model_id
from db.session import get_session_db

agent_db = get_session_db()

@tool
def get_weather(city: str) -> str:
    """Get current weather for a city.

    Args:
        city: The city name (e.g., "San Francisco")

    Returns:
        Weather description
    """
    # Replace with actual weather API
    return f"The weather in {city} is sunny, 72°F"

@tool
def search_database(query: str, limit: int = 10) -> list:
    """Search the internal database.

    Args:
        query: Search query
        limit: Maximum results to return

    Returns:
        List of matching records
    """
    # Your search logic here
    return [{"id": 1, "title": "Result 1"}]

custom_agent = Agent(
    name="Custom Tools Agent",
    model=LiteLLM(id=get_model_id("Custom Tools Agent"), **get_litellm_config()),
    db=agent_db,
    tools=[get_weather, search_database],
    instructions="You can check weather and search our database.",
    markdown=True,
)
```

### 4. Hybrid Agent

Combines knowledge base with tools.

```python
hybrid_agent = Agent(
    name="Hybrid Agent",
    model=LiteLLM(id=get_model_id("Hybrid Agent"), **get_litellm_config()),
    db=agent_db,
    knowledge=knowledge,
    tools=[get_weather, MCPTools(url="https://api.example.com/mcp")],
    instructions="""You are a versatile assistant with access to:
- A knowledge base for documentation
- Weather information
- External tools

Choose the appropriate resource based on the user's question.""",
    enable_agentic_memory=True,
    markdown=True,
)
```

## Agent Configuration

### Model Options

```python
# LiteLLM (standard)
from agno.models.litellm import LiteLLM
model = LiteLLM(id="gpt-5-mini")

# LiteLLM Responses (streaming optimized)
from agno.models.litellm import LiteLLM
model = LiteLLM(id="gpt-5-mini")

# OpenAI Direct
from agno.models.openai import OpenAI
model = OpenAI(id="gpt-4-turbo")

# Anthropic Direct
from agno.models.anthropic import Claude
model = Claude(id="claude-3-opus")
```

### Memory Settings

```python
agent = Agent(
    name="Memory Demo",
    model=model,
    db=agent_db,

    # Enable long-term memory across sessions
    enable_agentic_memory=True,

    # Include conversation history
    add_history_to_context=True,
    num_history_runs=5,  # Last 5 exchanges

    # Add current timestamp
    add_datetime_to_context=True,
)
```

### Search Types

```python
from agno.vectordb.pgvector import SearchType

# Semantic only (embedding similarity)
search_type=SearchType.semantic

# Keyword only (full-text search)
search_type=SearchType.keyword

# Hybrid (best of both)
search_type=SearchType.hybrid
```

### Embedding Models

```python
from agno.knowledge.embedder.openai import OpenAIEmbedder

# OpenAI embeddings
embedder = OpenAIEmbedder(id="text-embedding-3-small")  # 1536 dims
embedder = OpenAIEmbedder(id="text-embedding-3-large")  # 3072 dims

# Cohere embeddings (requires CohereEmbedder)
from agno.knowledge.embedder.cohere import CohereEmbedder
embedder = CohereEmbedder(id="embed-english-v3.0")
```

## Instructions Best Practices

### Structure Your Prompts

```python
instructions = """\
You are [ROLE DESCRIPTION].

## CAPABILITIES
- Capability 1
- Capability 2

## WORKFLOW
1. First, understand the user's request
2. Then, [action]
3. Finally, [response format]

## GUIDELINES
- Be concise and direct
- Always cite sources
- Ask for clarification when needed

## LIMITATIONS
- You cannot [limitation]
- If asked about [topic], redirect to [resource]
"""
```

### Example: Customer Support Agent

```python
instructions = """\
You are a customer support agent for TechCorp.

## YOUR ROLE
Help customers with product questions, troubleshooting, and account issues.

## WORKFLOW
1. Greet the customer warmly
2. Identify their issue category
3. Search the knowledge base for solutions
4. Provide step-by-step guidance
5. Confirm the issue is resolved

## GUIDELINES
- Use simple, non-technical language
- Empathize with frustrated customers
- Escalate billing issues to human support
- Never share customer data

## RESPONSE FORMAT
- Use bullet points for steps
- Include relevant article links
- End with "Is there anything else I can help with?"
"""
```

## Adding Quick Prompts

Update `app/config.yaml`:

```yaml
chat:
  quick_prompts:
    my-agent:
      - "What can you help me with?"
      - "Show me an example"
      - "Explain how this works"

    product-agent:
      - "How do I get started?"
      - "What are the pricing plans?"
      - "Show me the API documentation"
```

## Testing Your Agent

### CLI Testing

Add a `__main__` block for CLI interaction:

```python
if __name__ == "__main__":
    my_agent.cli_app(stream=True)
```

Run it:

```bash
# With Docker
docker exec -it agentos-api python -m agents.my_agent

# Local development (with mise)
python -m agents.my_agent
```

### API Testing

```python
import requests

# Test chat
response = requests.post(
    "http://localhost:8000/v1/chat/my-agent",
    json={"message": "Hello!"}
)
print(response.json())
```

### Unit Testing

```python
import pytest
from agents.my_agent import my_agent

def test_agent_responds():
    response = my_agent.run("What is 2+2?")
    assert response.content is not None
    assert len(response.content) > 0

def test_agent_uses_knowledge():
    response = my_agent.run("What is our refund policy?")
    assert "refund" in response.content.lower()
```

## Complete Example

Here's a complete agent file:

```python
"""
Support Agent
=============

Customer support agent with knowledge base and tools.

Run:
    python -m agents.support_agent
"""

from agno.agent import Agent
from agno.knowledge import Knowledge
from agno.knowledge.embedder.openai import OpenAIEmbedder
from agno.models.litellm import LiteLLM
from agno.tools import tool
from agno.vectordb.pgvector import PgVector, SearchType

from app.config import get_litellm_config, get_model_id
from db.session import db_url, get_postgres_db, get_session_db

# ============================================================================
# Setup
# ============================================================================
agent_db = get_session_db()  # PostgreSQL or Redis based on REDIS_URL

knowledge = Knowledge(
    name="Support Knowledge Base",
    vector_db=PgVector(
        db_url=db_url,
        table_name="support_docs",
        search_type=SearchType.hybrid,
        embedder=OpenAIEmbedder(id="text-embedding-3-small"),
    ),
    max_results=5,
    contents_db=get_postgres_db(),  # Knowledge always uses PostgreSQL
)

# ============================================================================
# Tools
# ============================================================================
@tool
def create_ticket(subject: str, description: str, priority: str = "medium") -> dict:
    """Create a support ticket.

    Args:
        subject: Ticket subject
        description: Detailed description
        priority: low, medium, or high

    Returns:
        Ticket information
    """
    # Integration with ticketing system
    return {
        "ticket_id": "TKT-12345",
        "status": "created",
        "priority": priority
    }

@tool
def check_order_status(order_id: str) -> dict:
    """Check the status of an order.

    Args:
        order_id: The order ID to check

    Returns:
        Order status information
    """
    # Integration with order system
    return {
        "order_id": order_id,
        "status": "shipped",
        "tracking": "1Z999AA10123456784"
    }

# ============================================================================
# Instructions
# ============================================================================
instructions = """\
You are a customer support agent for TechCorp.

## CAPABILITIES
- Answer product questions using the knowledge base
- Check order status
- Create support tickets for complex issues

## WORKFLOW
1. Greet the customer
2. Identify their need
3. Use appropriate tools or knowledge
4. Provide clear, helpful response
5. Offer additional assistance

## GUIDELINES
- Be friendly and professional
- Use simple language
- Escalate billing issues to human support
- Create tickets for unresolved issues
"""

# ============================================================================
# Create Agent
# ============================================================================
support_agent = Agent(
    name="Support Agent",
    model=LiteLLM(id=get_model_id("Support Agent"), **get_litellm_config()),
    db=agent_db,
    knowledge=knowledge,
    tools=[create_ticket, check_order_status],
    instructions=instructions,
    enable_agentic_memory=True,
    add_datetime_to_context=True,
    add_history_to_context=True,
    num_history_runs=10,
    markdown=True,
)

if __name__ == "__main__":
    # Load knowledge base
    print("Loading knowledge base...")
    knowledge.insert(name="FAQ", url="https://docs.techcorp.com/faq.md")
    knowledge.insert(name="Returns Policy", url="https://docs.techcorp.com/returns.md")
    print("Knowledge loaded!")

    # Start CLI
    support_agent.cli_app(stream=True)
```

## Creating Teams

Teams are groups of agents that collaborate on complex tasks. Each member has a specific role.

```python
"""
Research Team
=============

A team of specialized agents that collaborate on research tasks.
"""

from agno.agent import Agent
from agno.models.litellm import LiteLLM
from agno.team import Team
from agno.tools.duckduckgo import DuckDuckGoTools
from agno.tools.hackernews import HackerNewsTools

from app.config import get_litellm_config, get_model_id
from db.session import get_session_db

team_db = get_session_db()

# Team Members
web_researcher = Agent(
    id="web-researcher",
    name="Web Researcher",
    role="Search the web for current information and news",
    tools=[DuckDuckGoTools()],
    instructions="You search the web to find relevant, current information. Cite your sources.",
)

tech_researcher = Agent(
    id="tech-researcher",
    name="Tech Researcher",
    role="Find trending technology news and discussions from HackerNews",
    tools=[HackerNewsTools()],
    instructions="You search HackerNews for tech trends, discussions, and news.",
)

synthesizer = Agent(
    id="synthesizer",
    name="Synthesizer",
    role="Combine research from team members into coherent summaries",
    instructions="You take research from other team members and create clear summaries.",
)

# Create Team
research_team = Team(
    id="research-team",
    name="Research Team",
    model=LiteLLM(id=get_model_id("Research Team"), **get_litellm_config()),
    db=team_db,
    members=[web_researcher, tech_researcher, synthesizer],
    instructions="You are a research team leader coordinating specialized researchers.",
    enable_agentic_memory=True,
    markdown=True,
)
```

Register in `app/main.py`:

```python
from agents.research_team import research_team

agent_os = AgentOS(
    name="AgentOS",
    agents=[knowledge_agent, mcp_agent],
    teams=[research_team],  # Add teams here
    config=str(Path(__file__).parent / "config.yaml"),
)
```

## Creating Workflows

Workflows chain multiple agents as sequential steps, passing output from one to the next.

```python
"""
Content Workflow
================

A workflow that researches a topic and generates content.
"""

from agno.agent import Agent
from agno.models.litellm import LiteLLM
from agno.tools.duckduckgo import DuckDuckGoTools
from agno.workflow.step import Step
from agno.workflow.workflow import Workflow

from app.config import get_litellm_config, get_model_id
from db.session import get_session_db

workflow_db = get_session_db()
model = LiteLLM(id=get_model_id("Content Workflow"), **get_litellm_config())

# Workflow Agents
researcher = Agent(
    name="Content Researcher",
    model=model,
    tools=[DuckDuckGoTools()],
    instructions="Research the topic and gather key facts with sources.",
)

writer = Agent(
    name="Content Writer",
    model=model,
    instructions="Write a clear, engaging article from the research.",
)

editor = Agent(
    name="Content Editor",
    model=model,
    instructions="Edit and polish the content for clarity and flow.",
)

# Workflow Steps
research_step = Step(name="research", description="Research the topic", agent=researcher)
write_step = Step(name="write", description="Write content", agent=writer)
edit_step = Step(name="edit", description="Edit content", agent=editor)

# Create Workflow
content_workflow = Workflow(
    name="content-workflow",
    description="Research, write, and edit content on any topic",
    db=workflow_db,
    steps=[research_step, write_step, edit_step],
)
```

Register in `app/main.py`:

```python
from agents.content_workflow import content_workflow

agent_os = AgentOS(
    name="AgentOS",
    agents=[knowledge_agent, mcp_agent],
    teams=[research_team],
    workflows=[content_workflow],  # Add workflows here
    config=str(Path(__file__).parent / "config.yaml"),
)
```

## Adding Guardrails

Guardrails protect agents by validating input/output. Use `pre_hooks` for input validation.

```python
from agno.agent import Agent
from agno.guardrails import PIIDetectionGuardrail
from agno.models.litellm import LiteLLM

from app.config import get_litellm_config, get_model_id
from db.session import get_session_db

agent_db = get_session_db()

# Agent with PII detection guardrail
protected_agent = Agent(
    name="Protected Agent",
    model=LiteLLM(id=get_model_id("Protected Agent"), **get_litellm_config()),
    db=agent_db,
    instructions="You are a helpful assistant.",
    pre_hooks=[PIIDetectionGuardrail(mask_pii=True)],  # Mask PII in input
    markdown=True,
)
```

**Guardrail options**:

- `PIIDetectionGuardrail()` - Block requests containing PII
- `PIIDetectionGuardrail(mask_pii=True)` - Mask PII instead of blocking

## Next Steps

- [Architecture Overview](../architecture/ARCHITECTURE.md) - Understand the system design
- [API Reference](../api/openapi.yaml) - Complete API documentation
- [Developer Guide](./DEVELOPER_GUIDE.md) - Local development setup
