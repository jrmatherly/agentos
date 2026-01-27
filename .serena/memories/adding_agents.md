# Adding New Agents

## Quick Start

1. Create a new file in `agents/`:
```python
# agents/my_agent.py
"""
My Agent
========

Description of what this agent does.
"""

from agno.agent import Agent
from agno.models.litellm import LiteLLM

from app.config import get_litellm_config, get_model_id
from db.session import get_session_db

# ============================================================================
# Setup
# ============================================================================
agent_db = get_session_db()  # PostgreSQL or Redis based on REDIS_URL

# ============================================================================
# Instructions
# ============================================================================
instructions = """\
You are a helpful assistant that...

WORKFLOW
--------
1. First step
2. Second step

GUIDELINES
----------
- Guideline one
- Guideline two
"""

# ============================================================================
# Create Agent
# ============================================================================
my_agent = Agent(
    name="My Agent",
    model=LiteLLM(id=get_model_id("My Agent"), **get_litellm_config()),
    db=agent_db,
    instructions=instructions,
    enable_agentic_memory=True,
    add_datetime_to_context=True,
    add_history_to_context=True,
    num_history_runs=5,
    markdown=True,
)

if __name__ == "__main__":
    my_agent.cli_app(stream=True)
```

**Configuration helpers**:
- `get_model_id("My Agent")`: Returns `MY_AGENT_MODEL` env var → `LITELLM_DEFAULT_MODEL` → `gpt-5-mini`
- `get_litellm_config()`: Returns `api_key` and optionally `api_base` for proxy mode
- `get_session_db()`: Returns Redis if `REDIS_URL` is set, otherwise PostgreSQL

2. Register in `app/main.py`:
```python
from agents.my_agent import my_agent

agent_os = AgentOS(
    name="AgentOS",
    agents=[knowledge_agent, mcp_agent, my_agent],  # Add here
    config=str(Path(__file__).parent / "config.yaml"),
)
```

3. Add quick prompts in `app/config.yaml`:
```yaml
chat:
  quick_prompts:
    my-agent:
      - "What can you do?"
      - "Help me with..."
```

4. Restart: `docker compose restart`

## Agent Organization

Agents are organized by feature in subdirectories:
- `agents/reasoning/` - Reasoning agents (model, tools, flag)
- `agents/tools/` - Tool showcase agents (finance, scraper, research)
- `agents/learning/` - Learning agents
- `agents/hitl/` - Human-in-the-loop agents
- `teams/` - Team definitions
- `workflows/` - Workflow definitions

## Agent Types

### Knowledge Agent (Vector Search)
```python
from agno.knowledge import Knowledge
from agno.knowledge.embedder.openai import OpenAIEmbedder
from agno.vectordb.pgvector import PgVector, SearchType

from app.config import get_litellm_config, get_model_id
from db.session import db_url, get_postgres_db, get_session_db

agent_db = get_session_db()  # Sessions can use PostgreSQL or Redis

knowledge = Knowledge(
    name="My Knowledge Base",
    vector_db=PgVector(
        db_url=db_url,
        table_name="my_agent_docs",
        search_type=SearchType.hybrid,
        embedder=OpenAIEmbedder(id="text-embedding-3-small"),
    ),
    max_results=10,
    contents_db=get_postgres_db(),  # Knowledge ALWAYS uses PostgreSQL (pgvector)
)

my_agent = Agent(
    name="My Knowledge Agent",
    model=LiteLLM(id=get_model_id("My Knowledge Agent"), **get_litellm_config()),
    db=agent_db,
    knowledge=knowledge,
    ...
)
```

### Tool Agent (MCP Tools)
```python
from agno.models.litellm import LiteLLM
from agno.tools.mcp import MCPTools

from app.config import get_litellm_config, get_model_id
from db.session import get_session_db

agent_db = get_session_db()

my_agent = Agent(
    name="My Tool Agent",
    model=LiteLLM(id=get_model_id("My Tool Agent"), **get_litellm_config()),
    db=agent_db,
    tools=[MCPTools(url="https://example.com/mcp")],
    ...
)
```

### Custom Tools
```python
from agno.tools import tool

@tool
def my_tool(query: str) -> str:
    """Tool description."""
    return f"Result for: {query}"

my_agent = Agent(
    name="My Agent",
    tools=[my_tool],
    ...
)
```

### Reasoning Agent (reasoning=True flag)
```python
from agno.agent import Agent
from agno.models.litellm import LiteLLM

from app.config import get_litellm_config, get_model_id
from db.session import get_session_db

agent_db = get_session_db()

reasoning_agent = Agent(
    name="Reasoning Agent",
    model=LiteLLM(id=get_model_id("Reasoning Agent"), **get_litellm_config()),
    db=agent_db,
    reasoning=True,  # Enables structured chain-of-thought
    instructions="Think through problems step by step.",
    enable_agentic_memory=True,
    markdown=True,
)
```

### Reasoning Tools Agent (explicit think/analyze)
```python
from agno.agent import Agent
from agno.models.litellm import LiteLLM
from agno.tools.reasoning import ReasoningTools

from app.config import get_litellm_config, get_model_id
from db.session import get_session_db

agent_db = get_session_db()

reasoning_tools_agent = Agent(
    name="Reasoning Tools Agent",
    model=LiteLLM(id=get_model_id("Reasoning Tools Agent"), **get_litellm_config()),
    db=agent_db,
    tools=[ReasoningTools(add_instructions=True)],  # Adds think() and analyze()
    instructions="Use think() to plan and analyze() to evaluate.",
    enable_agentic_memory=True,
    markdown=True,
)
```

### HITL Agent (Human-in-the-Loop with confirmation)
```python
from agno.agent import Agent
from agno.models.litellm import LiteLLM
from agno.tools import tool

from app.config import get_litellm_config, get_model_id
from db.session import get_session_db

agent_db = get_session_db()

@tool(requires_confirmation=True)
def send_email(to: str, subject: str, body: str) -> str:
    """Send email. Requires user confirmation."""
    return f"Email sent to {to}"

@tool
def search_files(query: str) -> str:
    """Search files. No confirmation needed."""
    return f"Found files for: {query}"

hitl_agent = Agent(
    name="HITL Agent",
    model=LiteLLM(id=get_model_id("HITL Agent"), **get_litellm_config()),
    db=agent_db,
    tools=[send_email, search_files],
    instructions="Sensitive operations require confirmation.",
    markdown=True,
)

# Handle confirmations in runtime:
# run_response = hitl_agent.run("...")
# for req in run_response.active_requirements:
#     if req.needs_confirmation:
#         req.confirm() or req.reject()
# agent.continue_run(run_id=run_response.run_id, requirements=run_response.requirements)
```

### Learning Agent (agentic memory + user memories)
```python
from agno.agent import Agent
from agno.models.litellm import LiteLLM

from app.config import get_litellm_config, get_model_id
from db.session import get_session_db

agent_db = get_session_db()

learning_agent = Agent(
    name="Learning Agent",
    model=LiteLLM(id=get_model_id("Learning Agent"), **get_litellm_config()),
    db=agent_db,
    instructions="Learn from user preferences and remember them.",
    enable_agentic_memory=True,  # Agent can manage memories
    enable_user_memories=True,   # Auto-manage user memories
    add_history_to_context=True,
    num_history_runs=10,
    markdown=True,
)
```

## Model Options

```python
# LiteLLM (default, works with any provider via LiteLLM gateway)
from agno.models.litellm import LiteLLM
model = LiteLLM(id="gpt-5-mini")

# OpenAI Direct
from agno.models.openai import OpenAI
model = OpenAI(id="gpt-4")

# OpenAI Responses (streaming optimized)
from agno.models.openai import OpenAIResponses
model = OpenAIResponses(id="gpt-5.2")

# Anthropic Direct
from agno.models.anthropic import Claude
model = Claude(id="claude-3-opus")
```

## Common Agent Options

```python
Agent(
    name="Agent Name",           # Display name
    model=...,                    # LLM model
    db=agent_db,                 # PostgresDb for memory
    knowledge=...,               # Optional: Knowledge base
    tools=[...],                 # Optional: Tools list
    instructions="...",          # System prompt
    pre_hooks=[...],             # Optional: Input guardrails
    enable_agentic_memory=True,  # Remember across sessions
    add_datetime_to_context=True, # Include timestamp
    add_history_to_context=True,  # Include chat history
    num_history_runs=5,          # History messages to include
    markdown=True,               # Format output as markdown
)
```

## Creating Teams

Teams are groups of agents that collaborate on complex tasks:

```python
from agno.agent import Agent
from agno.models.litellm import LiteLLM
from agno.team import Team
from agno.tools.duckduckgo import DuckDuckGoTools

from app.config import get_litellm_config, get_model_id
from db.session import get_session_db

team_db = get_session_db()

# Team members (agents with specific roles)
web_researcher = Agent(
    id="web-researcher",
    name="Web Researcher",
    role="Search the web for information",
    tools=[DuckDuckGoTools()],
    instructions="Search and cite sources.",
)

synthesizer = Agent(
    id="synthesizer",
    name="Synthesizer",
    role="Combine research into summaries",
    instructions="Create clear summaries from research.",
)

# Create team
my_team = Team(
    id="my-team",
    name="My Team",
    model=LiteLLM(id=get_model_id("My Team"), **get_litellm_config()),
    db=team_db,
    members=[web_researcher, synthesizer],
    instructions="Coordinate team members to complete research tasks.",
    enable_agentic_memory=True,
    markdown=True,
)
```

Register in `app/main.py`:
```python
agent_os = AgentOS(
    agents=[...],
    teams=[my_team],  # Add teams here
)
```

## Creating Workflows

Workflows chain agents as sequential steps:

```python
from agno.agent import Agent
from agno.models.litellm import LiteLLM
from agno.workflow.step import Step
from agno.workflow.workflow import Workflow

from app.config import get_litellm_config, get_model_id
from db.session import get_session_db

workflow_db = get_session_db()
model = LiteLLM(id=get_model_id("My Workflow"), **get_litellm_config())

# Workflow agents
researcher = Agent(name="Researcher", model=model, instructions="Research the topic.")
writer = Agent(name="Writer", model=model, instructions="Write content from research.")

# Workflow steps
research_step = Step(name="research", description="Research topic", agent=researcher)
write_step = Step(name="write", description="Write content", agent=writer)

# Create workflow
my_workflow = Workflow(
    name="my-workflow",
    description="Research and write content",
    db=workflow_db,
    steps=[research_step, write_step],
)
```

Register in `app/main.py`:
```python
agent_os = AgentOS(
    agents=[...],
    teams=[...],
    workflows=[my_workflow],  # Add workflows here
)
```

## Adding Guardrails

Guardrails validate input/output. Use `pre_hooks` for input validation:

```python
from agno.agent import Agent
from agno.guardrails import PIIDetectionGuardrail
from agno.models.litellm import LiteLLM

from app.config import get_litellm_config, get_model_id
from db.session import get_session_db

agent_db = get_session_db()

protected_agent = Agent(
    name="Protected Agent",
    model=LiteLLM(id=get_model_id("Protected Agent"), **get_litellm_config()),
    db=agent_db,
    instructions="You are a helpful assistant.",
    pre_hooks=[PIIDetectionGuardrail(mask_pii=True)],  # Mask PII in input
    markdown=True,
)
```

**Options:**
- `PIIDetectionGuardrail()` - Block requests containing PII
- `PIIDetectionGuardrail(mask_pii=True)` - Mask PII instead of blocking
