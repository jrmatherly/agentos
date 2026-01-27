# AgentOS UI Integration & Enhancement Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Enable AgentOS Control Plane UI integration and add Teams, Workflows, Guardrails, and MCP Server capabilities.

**Architecture:** Phased approach starting with tracing/UI integration (Tier 1), then agent enhancement (Tier 2), then production features (Tier 3). Each tier builds on the previous.

**Tech Stack:** Agno 2.4.0, FastAPI, PostgreSQL/pgvector, OpenTelemetry, LiteLLM

---

## Phase 1: UI Integration & Tracing (Tier 1)

### Task 1: Add OpenTelemetry Dependencies

**Files:**

- Modify: `pyproject.toml`
- Modify: `requirements.txt` (regenerate)

**Step 1: Update pyproject.toml**

Add to dependencies list in `pyproject.toml`:

```python
  "opentelemetry-api",
  "opentelemetry-sdk",
  "openinference-instrumentation-agno",
```

**Step 2: Regenerate requirements.txt**

Run: `cd /Users/jason/dev/MCP/AgentOS/agentos-docker && ./scripts/generate_requirements.sh`

**Step 3: Rebuild Docker image**

Run: `docker compose down && docker compose build`

**Step 4: Commit**

```bash
git add pyproject.toml requirements.txt
git commit -m "feat: add OpenTelemetry dependencies for tracing"
```

---

### Task 2: Enable Tracing in AgentOS

**Files:**

- Modify: `app/main.py`
- Modify: `db/session.py`

**Step 1: Add tracing database helper to db/session.py**

Add after `get_postgres_db()` function:

```python
def get_tracing_db() -> PostgresDb:
    """Get a dedicated PostgreSQL instance for tracing.

    Uses a separate database ID to isolate traces from agent data.
    """
    return PostgresDb(db_url=db_url, id="tracing_db")
```

**Step 2: Update app/main.py to enable tracing**

Replace the AgentOS instantiation with:

```python
from db.session import get_postgres_db

# ============================================================================
# Create AgentOS with tracing enabled
# ============================================================================
agent_os = AgentOS(
    name="AgentOS",
    agents=[knowledge_agent, mcp_agent],
    config=str(Path(__file__).parent / "config.yaml"),
    db=get_postgres_db(),  # Dedicated DB for traces
    tracing=True,          # Enable OpenTelemetry tracing
)
```

**Step 3: Verify tracing is working**

Run: `docker compose up -d --build`
Run: `docker compose logs -f agentos-api`

Expected: No errors, API starts normally with tracing enabled

**Step 4: Commit**

```bash
git add app/main.py db/session.py
git commit -m "feat: enable OpenTelemetry tracing for AgentOS"
```

---

### Task 3: Expand config.yaml for UI

**Files:**

- Modify: `app/config.yaml`

**Step 1: Update config.yaml with full UI configuration**

Replace contents of `app/config.yaml` with:

```yaml
# AgentOS UI Configuration
# See: https://docs.agno.com/agent-os/config

chat:
  quick_prompts:
    knowledge-agent:
      - "What is Agno?"
      - "How do I create an agent?"
      - "What can you help me with?"
      - "Search for information about AgentOS"
    mcp-agent:
      - "What tools are available?"
      - "What is Agno?"
      - "Help me understand MCP"

memory:
  display_name: "Agent Memories"

session:
  display_name: "User Sessions"

knowledge:
  display_name: "Knowledge Bases"
```

**Step 2: Restart to apply**

Run: `docker compose restart agentos-api`

**Step 3: Commit**

```bash
git add app/config.yaml
git commit -m "feat: expand config.yaml for AgentOS UI integration"
```

---

### Task 4: Connect to Control Plane (Manual Step)

**This is a manual step - document for user:**

1. Open https://os.agno.com and sign in
2. Click "Add new OS"
3. Configure:
   - Environment: Local
   - Endpoint URL: `http://localhost:8000`
   - OS Name: "AgentOS Development"
   - Tags: `dev`, `local`
4. Click "CONNECT"
5. Verify: Status shows "Running", agents appear in chat interface

---

## Phase 2: Agent Enhancement (Tier 2)

### Task 5: Create Research Team

**Files:**

- Create: `agents/research_team.py`
- Modify: `app/main.py`
- Modify: `app/config.yaml`

**Step 1: Create research_team.py**

Create file `agents/research_team.py`:

```python
"""
Research Team
=============

A team of specialized agents that collaborate on research tasks.

Run:
    python -m agents.research_team
"""

from agno.agent import Agent
from agno.models.litellm import LiteLLM
from agno.team import Team
from agno.tools.duckduckgo import DuckDuckGoTools
from agno.tools.hackernews import HackerNewsTools

from app.config import get_litellm_config, get_model_id
from db.session import get_session_db

# ============================================================================
# Setup
# ============================================================================
team_db = get_session_db()

# ============================================================================
# Team Members
# ============================================================================
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
    instructions="You search HackerNews for tech trends, discussions, and news. Summarize key points.",
)

synthesizer = Agent(
    id="synthesizer",
    name="Synthesizer",
    role="Combine research from team members into coherent summaries",
    instructions="You take research from other team members and create clear, comprehensive summaries.",
)

# ============================================================================
# Create Team
# ============================================================================
research_team = Team(
    id="research-team",
    name="Research Team",
    model=LiteLLM(id=get_model_id("Research Team"), **get_litellm_config()),
    db=team_db,
    members=[web_researcher, tech_researcher, synthesizer],
    instructions="""\
You are a research team leader coordinating specialized researchers.

WORKFLOW
--------
1. Analyze the research request
2. Delegate to appropriate team members based on their roles
3. Have the Synthesizer combine findings into a coherent response

GUIDELINES
----------
- Web Researcher for general web searches and news
- Tech Researcher for technology and startup topics
- Synthesizer for combining and summarizing findings
- Always cite sources in the final response
""",
    enable_agentic_memory=True,
    markdown=True,
)

if __name__ == "__main__":
    research_team.cli_app(stream=True)
```

**Step 2: Add DuckDuckGo and HackerNews to dependencies**

Add to `pyproject.toml` dependencies:

```python
  "duckduckgo-search",
```

**Step 3: Regenerate requirements**

Run: `./scripts/generate_requirements.sh`

**Step 4: Update app/main.py to include team**

Add import and update AgentOS:

```python
from agents.research_team import research_team

agent_os = AgentOS(
    name="AgentOS",
    agents=[knowledge_agent, mcp_agent],
    teams=[research_team],  # Add teams
    config=str(Path(__file__).parent / "config.yaml"),
    db=get_postgres_db(),
    tracing=True,
)
```

**Step 5: Update config.yaml with team prompts**

Add to `app/config.yaml`:

```yaml
    research-team:
      - "Research the latest AI developments"
      - "What's trending on HackerNews?"
      - "Find information about cloud computing trends"
```

**Step 6: Rebuild and test**

Run: `docker compose down && docker compose up -d --build`
Run: `docker compose logs -f agentos-api`

Expected: No errors, team registered

**Step 7: Commit**

```bash
git add agents/research_team.py app/main.py app/config.yaml pyproject.toml requirements.txt
git commit -m "feat: add Research Team with web and tech researchers"
```

---

### Task 6: Create Content Workflow

**Files:**

- Create: `agents/content_workflow.py`
- Modify: `app/main.py`
- Modify: `app/config.yaml`

**Step 1: Create content_workflow.py**

Create file `agents/content_workflow.py`:

```python
"""
Content Workflow
================

A workflow that researches a topic and generates content.

Run:
    python -m agents.content_workflow
"""

from agno.agent import Agent
from agno.models.litellm import LiteLLM
from agno.tools.duckduckgo import DuckDuckGoTools
from agno.workflow import Workflow

from app.config import get_litellm_config, get_model_id
from db.session import get_session_db

# ============================================================================
# Setup
# ============================================================================
workflow_db = get_session_db()
model = LiteLLM(id=get_model_id("Content Workflow"), **get_litellm_config())

# ============================================================================
# Workflow Steps (Agents)
# ============================================================================
researcher = Agent(
    id="content-researcher",
    name="Content Researcher",
    model=model,
    tools=[DuckDuckGoTools()],
    instructions="""\
You are a research specialist. Your job is to:
1. Search for relevant information on the given topic
2. Gather key facts, statistics, and insights
3. Cite your sources

Output a structured research summary with:
- Key findings
- Important statistics
- Source URLs
""",
)

writer = Agent(
    id="content-writer",
    name="Content Writer",
    model=model,
    instructions="""\
You are a content writer. Based on the research provided:
1. Write a clear, engaging article
2. Structure with introduction, body, and conclusion
3. Include relevant facts and statistics from the research
4. Keep paragraphs concise and readable

Write in a professional but approachable tone.
""",
)

editor = Agent(
    id="content-editor",
    name="Content Editor",
    model=model,
    instructions="""\
You are an editor. Review the content and:
1. Check for clarity and flow
2. Ensure facts are properly cited
3. Polish the language and formatting
4. Add a compelling title if missing

Output the final, polished version.
""",
)

# ============================================================================
# Create Workflow
# ============================================================================
content_workflow = Workflow(
    id="content-workflow",
    name="Content Workflow",
    db=workflow_db,
    steps=[researcher, writer, editor],
    markdown=True,
)

if __name__ == "__main__":
    content_workflow.print_response(
        "Write an article about the future of AI agents",
        stream=True,
    )
```

**Step 2: Update app/main.py to include workflow**

Add import and update AgentOS:

```python
from agents.content_workflow import content_workflow

agent_os = AgentOS(
    name="AgentOS",
    agents=[knowledge_agent, mcp_agent],
    teams=[research_team],
    workflows=[content_workflow],  # Add workflows
    config=str(Path(__file__).parent / "config.yaml"),
    db=get_postgres_db(),
    tracing=True,
)
```

**Step 3: Update config.yaml with workflow prompts**

Add to `app/config.yaml`:

```yaml
    content-workflow:
      - "Write an article about AI agents"
      - "Create content about cloud computing"
      - "Generate a blog post about Python best practices"
```

**Step 4: Rebuild and test**

Run: `docker compose restart agentos-api`
Run: `docker compose logs -f agentos-api`

Expected: No errors, workflow registered

**Step 5: Commit**

```bash
git add agents/content_workflow.py app/main.py app/config.yaml
git commit -m "feat: add Content Workflow with research-write-edit pipeline"
```

---

### Task 7: Add Guardrails to Agents

**Files:**

- Modify: `agents/knowledge_agent.py`
- Modify: `agents/mcp_agent.py`

**Step 1: Add PII guardrail to knowledge_agent.py**

Add import at top:

```python
from agno.guardrails import PIIDetectionGuardrail
```

Update the Agent creation to include guardrails:

```python
knowledge_agent = Agent(
    name="Knowledge Agent",
    model=LiteLLM(
        id=get_model_id("Knowledge Agent"),
        **get_litellm_config(),
    ),
    db=agent_db,
    knowledge=knowledge,
    instructions=instructions,
    pre_hooks=[PIIDetectionGuardrail(mask_pii=True)],  # Add guardrail
    enable_agentic_memory=True,
    add_datetime_to_context=True,
    add_history_to_context=True,
    num_history_runs=5,
    markdown=True,
)
```

**Step 2: Add PII guardrail to mcp_agent.py**

Add import at top:

```python
from agno.guardrails import PIIDetectionGuardrail
```

Update the Agent creation:

```python
mcp_agent = Agent(
    name="MCP Agent",
    model=LiteLLM(
        id=get_model_id("MCP Agent"),
        **get_litellm_config(),
    ),
    db=agent_db,
    tools=[MCPTools(url="https://docs.agno.com/mcp")],
    instructions=instructions,
    pre_hooks=[PIIDetectionGuardrail(mask_pii=True)],  # Add guardrail
    enable_agentic_memory=True,
    add_datetime_to_context=True,
    add_history_to_context=True,
    num_history_runs=5,
    markdown=True,
)
```

**Step 3: Restart and test**

Run: `docker compose restart agentos-api`

Test PII masking by sending a message with an email address through the API.

**Step 4: Commit**

```bash
git add agents/knowledge_agent.py agents/mcp_agent.py
git commit -m "feat: add PII detection guardrails to agents"
```

---

## Phase 3: Production Features (Tier 3)

### Task 8: Enable MCP Server

**Files:**

- Modify: `app/main.py`

**Step 1: Enable MCP server in AgentOS**

Update AgentOS instantiation:

```python
agent_os = AgentOS(
    name="AgentOS",
    agents=[knowledge_agent, mcp_agent],
    teams=[research_team],
    workflows=[content_workflow],
    config=str(Path(__file__).parent / "config.yaml"),
    db=get_postgres_db(),
    tracing=True,
    enable_mcp_server=True,  # Expose as MCP server at /mcp
)
```

**Step 2: Restart and verify**

Run: `docker compose restart agentos-api`

Test MCP endpoint:
Run: `curl http://localhost:8000/mcp`

Expected: MCP server responds

**Step 3: Commit**

```bash
git add app/main.py
git commit -m "feat: enable MCP server endpoint at /mcp"
```

---

### Task 9: Update Documentation

**Files:**

- Modify: `docs/guides/CREATING_AGENTS.md`
- Modify: `docs/CODE_REFERENCE.md`
- Modify: `PROJECT_INDEX.json`

**Step 1: Update CREATING_AGENTS.md**

Add sections for Teams, Workflows, and Guardrails based on the implementations.

**Step 2: Update CODE_REFERENCE.md**

Add reference entries for:

- `agents.research_team`
- `agents.content_workflow`
- Guardrails configuration

**Step 3: Update PROJECT_INDEX.json**

Add entries for new modules:

```json
"teams": {
  "research_team": {
    "path": "agents/research_team.py",
    "members": ["web_researcher", "tech_researcher", "synthesizer"]
  }
},
"workflows": {
  "content_workflow": {
    "path": "agents/content_workflow.py",
    "steps": ["researcher", "writer", "editor"]
  }
}
```

**Step 4: Commit**

```bash
git add docs/ PROJECT_INDEX.json
git commit -m "docs: update documentation for teams, workflows, and guardrails"
```

---

### Task 10: Update Serena Memories

**Files:**

- Modify: `.serena/memories/project_overview.md`
- Modify: `.serena/memories/adding_agents.md`

**Step 1: Update project_overview.md**

Add sections for:

- Teams (research_team)
- Workflows (content_workflow)
- Tracing configuration
- MCP server endpoint

**Step 2: Update adding_agents.md**

Add examples for:

- Creating teams
- Creating workflows
- Adding guardrails

**Step 3: Commit**

```bash
git add .serena/memories/
git commit -m "docs: update Serena memories with teams, workflows, guardrails"
```

---

## Final Verification

### Task 11: Full Integration Test

**Step 1: Rebuild everything**

Run: `docker compose down && docker compose up -d --build`

**Step 2: Verify all components**

- [ ] API starts without errors: `docker compose logs agentos-api`
- [ ] Agents registered: `curl http://localhost:8000/config | jq '.agents'`
- [ ] Teams registered: `curl http://localhost:8000/config | jq '.teams'`
- [ ] Workflows registered: `curl http://localhost:8000/config | jq '.workflows'`
- [ ] MCP server active: `curl http://localhost:8000/mcp`
- [ ] Tracing enabled: Check AgentOS UI at os.agno.com/traces

**Step 3: Test in Control Plane**

1. Open https://os.agno.com
2. Select your connected OS
3. Test chat with Knowledge Agent
4. Test chat with Research Team
5. Run Content Workflow
6. View traces in Tracing tab

**Step 4: Final commit**

```bash
git add -A
git commit -m "feat: complete AgentOS UI integration and enhancement"
```

---

## Summary

| Phase | Tasks | Key Features |
|-------|-------|--------------|
| 1 | Tasks 1-4 | Tracing, UI config, Control Plane connection |
| 2 | Tasks 5-7 | Research Team, Content Workflow, Guardrails |
| 3 | Tasks 8-11 | MCP Server, Documentation, Integration test |

**Dependencies installed:**

- `opentelemetry-api`
- `opentelemetry-sdk`
- `openinference-instrumentation-agno`
- `duckduckgo-search`

**Endpoints added:**

- `/mcp` - MCP server for external tool access
- Tracing data at `/traces` (via AgentOS UI)

**UI Features enabled:**

- Chat with Agents, Teams, Workflows
- Tracing with tree and waterfall views
- Session tracking
- Memory management
- Knowledge base management
