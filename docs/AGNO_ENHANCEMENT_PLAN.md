# AgentOS Enhancement Plan

> Research-based implementation plan for enhancing AgentOS with Agno framework features.

## Executive Summary

After comprehensive analysis of the Agno documentation (1,847 docs) and cross-referencing with the current AgentOS implementation, this document outlines prioritized enhancement opportunities organized by impact, complexity, and strategic value.

## Current Implementation Status

### Implemented Features

| Feature | Status | Files |
|---------|--------|-------|
| Agents | 10 agents | `agents/` |
| Teams | 3 teams | `teams/` |
| Workflows | 2 workflows | `workflows/` |
| Knowledge (RAG) | Hybrid search | `agents/knowledge_agent.py` |
| Memory | Agentic memory | All agents |
| Guardrails | PII detection | `knowledge_agent.py`, `mcp_agent.py` |
| Tracing | OpenTelemetry | `app/main.py` |
| MCP Server | `/mcp` endpoint | `app/main.py` |
| HITL | Tool confirmation | `agents/hitl/confirmation_agent.py` |
| JWT RBAC | Authorization | `app/auth.py` |
| Session Storage | PostgreSQL + Redis | `db/session.py` |

### Feature Gaps Identified

| Feature | Agno Docs | Current Status |
|---------|-----------|----------------|
| Context Compression | `/compression/overview.mdx` | Not implemented |
| Skills | `/skills/overview.mdx` | Not implemented |
| Evals | `/evals/overview.mdx` | Not implemented |
| Post-hooks | `/hooks/overview.mdx` | Only pre-hooks used |
| Background Hooks | `/agent-os/background-tasks/overview.mdx` | Not enabled |
| Learning Stores | `/learning/stores/intro.mdx` | Basic memory only |
| State Management | `/state/overview.mdx` | Not implemented |
| Dependencies | `/dependencies/overview.mdx` | Not implemented |
| Structured Output | `/input-output/` | Not implemented |
| Run Cancellation | `/run-cancellation/overview.mdx` | Not implemented |
| Additional Guardrails | `/guardrails/included/` | PII only |
| Multimodal | `/multimodal/overview.mdx` | Not implemented |

---

## Enhancement Recommendations

### Priority 1: High Impact, Low Effort

#### 1.1 Context Compression

**Impact:** Cost reduction, extended context windows
**Effort:** Low (configuration change)

Add context compression to tool-heavy agents to reduce token costs and stay within context limits.

```python
# agents/tools/research_agent.py
research_agent = Agent(
    name="Research Agent",
    # ... existing config ...
    compress_tool_results=True,  # Add this
)

# For custom control:
from agno.compression.manager import CompressionManager

compression_manager = CompressionManager(
    model=LiteLLM(id="gpt-4o-mini", **get_litellm_config()),  # Fast, cheap model
    compress_tool_results_limit=3,
)

research_agent = Agent(
    name="Research Agent",
    compression_manager=compression_manager,
    # ...
)
```

**Files to modify:**

- `agents/tools/research_agent.py`
- `agents/tools/web_scraper_agent.py`
- `teams/research_team.py`

---

#### 1.2 Additional Guardrails

**Impact:** Enhanced security
**Effort:** Low (add imports and hooks)

Add prompt injection defense and OpenAI moderation to sensitive agents.

```python
# agents/mcp_agent.py
from agno.guardrails import PIIDetectionGuardrail, PromptInjectionGuardrail

mcp_agent = Agent(
    name="MCP Agent",
    # ... existing config ...
    pre_hooks=[
        PIIDetectionGuardrail(mask_pii=True),
        PromptInjectionGuardrail(),  # Add this
    ],
)
```

**Files to modify:**

- `agents/mcp_agent.py`
- `agents/knowledge_agent.py`
- Any agent exposed to untrusted input

---

#### 1.3 Background Hooks

**Impact:** Faster API responses, non-blocking analytics
**Effort:** Low (configuration change)

Enable background hooks for logging/analytics without blocking responses.

```python
# app/main.py
agent_os = AgentOS(
    name="AgentOS",
    # ... existing config ...
    run_hooks_in_background=True,  # Add this
)
```

Or for specific hooks:

```python
from agno.hooks import hook

@hook(run_in_background=True)
async def log_response_metrics(run_output, agent):
    """Log metrics without blocking response."""
    await send_to_analytics(run_output)
```

**Files to modify:**

- `app/main.py`

---

#### 1.4 Post-hooks for Output Validation

**Impact:** Quality assurance, compliance
**Effort:** Low

Add post-hooks to validate and transform agent outputs.

```python
# agents/tools/research_agent.py
from agno.exceptions import CheckTrigger, OutputCheckError

def validate_source_citations(run_output):
    """Ensure research output includes source citations."""
    if "sources" not in run_output.content.lower():
        raise OutputCheckError(
            "Response missing source citations",
            check_trigger=CheckTrigger.OUTPUT_NOT_ALLOWED,
        )

research_agent = Agent(
    name="Research Agent",
    # ... existing config ...
    post_hooks=[validate_source_citations],
)
```

---

### Priority 2: Medium Impact, Medium Effort

#### 2.1 State Management

**Impact:** Persistent user data, shopping lists, preferences
**Effort:** Medium

Implement session_state for agents that need to maintain data across runs.

```python
# agents/learning/learning_assistant.py
from agno.run import RunContext

def update_preferences(run_context: RunContext, category: str, value: str) -> str:
    """Update user preferences in session state."""
    run_context.session_state["preferences"][category] = value
    return f"Updated {category} preference to {value}"

learning_assistant = Agent(
    name="Learning Assistant",
    db=agent_db,
    session_state={
        "preferences": {},
        "todo_items": [],
        "conversation_summary": "",
    },
    tools=[update_preferences],
    instructions="User preferences: {preferences}",
    # ...
)
```

**New file:** `agents/stateful/preferences_agent.py`

---

#### 2.2 Structured Output

**Impact:** Type-safe responses, easier parsing
**Effort:** Medium

Add Pydantic output schemas for agents that produce structured data.

```python
# agents/tools/finance_agent.py
from pydantic import BaseModel, Field

class StockAnalysis(BaseModel):
    symbol: str = Field(description="Stock ticker symbol")
    current_price: float = Field(description="Current stock price")
    recommendation: str = Field(description="Buy, hold, or sell")
    reasoning: str = Field(description="Analysis reasoning")
    risk_level: str = Field(description="Low, medium, or high")

finance_agent = Agent(
    name="Finance Agent",
    output_schema=StockAnalysis,
    # ...
)

# Usage
result = finance_agent.run("Analyze AAPL stock")
analysis: StockAnalysis = result.parsed_content  # Type-safe!
```

**Files to modify:**

- `agents/tools/finance_agent.py`
- `agents/tools/research_agent.py`

---

#### 2.3 Dependencies Injection

**Impact:** Dynamic context, personalization
**Effort:** Medium

Inject dynamic context into agent instructions at runtime.

```python
# agents/learning/learning_assistant.py
def get_user_context(user_id: str) -> dict:
    """Fetch user context from database."""
    return {
        "name": "Jason",
        "preferences": {"language": "en", "detail_level": "concise"},
        "recent_topics": ["AI agents", "Python"],
    }

learning_assistant = Agent(
    name="Learning Assistant",
    dependencies={
        "user_context": get_user_context,
        "current_time": lambda: datetime.now().isoformat(),
    },
    instructions="User: {user_context[name]}. Preferences: {user_context[preferences]}",
    add_dependencies_to_context=True,
    # ...
)
```

---

#### 2.4 Evals Framework

**Impact:** Quality assurance, regression testing
**Effort:** Medium

Create an evaluation suite for agents.

```python
# tests/evals/test_knowledge_agent.py
from agno.eval.accuracy import AccuracyEval

def test_knowledge_agent_accuracy():
    evaluation = AccuracyEval(
        model=OpenAIResponses(id="gpt-4o"),
        agent=knowledge_agent,
        input="What is Agno?",
        expected_output="Agno is an AI agent framework",
        additional_guidelines="Response should be factual and cite documentation.",
    )
    result = evaluation.run()
    assert result.passed

# tests/evals/test_research_agent.py
from agno.eval.reliability import ReliabilityEval

def test_research_agent_tool_calls():
    evaluation = ReliabilityEval(
        agent=research_agent,
        input="Research AI trends",
        expected_tool_calls=["duckduckgo_search"],
    )
    result = evaluation.run()
    assert result.passed
```

**New directory:** `tests/evals/`

---

### Priority 3: High Impact, High Effort

#### 3.1 Learning Machine with Learning Stores

**Impact:** Personalization, continuous improvement
**Effort:** High

Implement the full Learning Machine pattern with multiple knowledge stores.

```python
# agents/learning/advanced_learning_assistant.py
from agno.agent import Agent
from agno.learn import LearningMachine, UserProfileConfig
from agno.models.litellm import LiteLLM

from app.config import get_litellm_config, get_model_id
from db.session import get_session_db

agent_db = get_session_db()

# Simple boolean-based configuration
advanced_assistant = Agent(
    name="Advanced Learning Assistant",
    model=LiteLLM(id=get_model_id("Learning Assistant"), **get_litellm_config()),
    db=agent_db,
    learning=LearningMachine(
        user_profile=True,       # Structured fields (name, preferences)
        user_memory=True,        # Unstructured observations & facts
        session_context=True,    # Goals, plans, active state
        entity_memory=True,      # Facts about business entities
        learned_knowledge=False, # Reusable insights (requires Knowledge base)
    ),
    markdown=True,
)

# Or with custom profile schema
from dataclasses import dataclass, field
from typing import Optional
from agno.learn.schemas import UserProfile

@dataclass
class CustomerProfile(UserProfile):
    """Extended profile for personalization."""
    company: Optional[str] = field(default=None, metadata={"description": "Company name"})
    role: Optional[str] = field(default=None, metadata={"description": "Job title"})
    expertise_level: Optional[str] = field(default=None, metadata={"description": "beginner|intermediate|expert"})

custom_assistant = Agent(
    name="Custom Learning Assistant",
    model=LiteLLM(id=get_model_id("Learning Assistant"), **get_litellm_config()),
    db=agent_db,
    learning=LearningMachine(
        user_profile=UserProfileConfig(schema=CustomerProfile),
        user_memory=True,
        session_context=True,
    ),
    markdown=True,
)
```

**New file:** `agents/learning/advanced_learning_assistant.py`

---

#### 3.2 Skills Integration

**Impact:** Modular expertise, reduced context usage
**Effort:** High

Implement Anthropic's Agent Skills specification for domain-specific knowledge.

```tree
skills/
├── code-review/
│   ├── SKILL.md
│   ├── scripts/
│   │   └── review_pr.py
│   └── references/
│       └── guidelines.md
├── research/
│   ├── SKILL.md
│   └── references/
│       └── methodology.md
└── writing/
    ├── SKILL.md
    └── references/
        └── style_guide.md
```

```python
# agents/skills_agent.py
from agno.skills import Skills, LocalSkills

skills_agent = Agent(
    name="Skills Agent",
    model=LiteLLM(id=get_model_id("Skills Agent"), **get_litellm_config()),
    skills=Skills(loaders=[LocalSkills("./skills")]),
    # Agent now has: get_skill_instructions(), get_skill_reference(), get_skill_script()
)
```

**New directory:** `skills/`
**New file:** `agents/skills_agent.py`

---

#### 3.3 Multimodal Agent

**Impact:** Image/audio/video processing
**Effort:** High

Create a multimodal agent for processing images and files.

```python
# agents/multimodal/vision_agent.py
from agno.agent import Agent
from agno.models.litellm import LiteLLM
from agno.media import Image

vision_agent = Agent(
    name="Vision Agent",
    model=LiteLLM(id="gpt-4o", **get_litellm_config()),  # Multimodal model
    instructions="Analyze images and provide detailed descriptions.",
    # ...
)

# Usage
response = vision_agent.run(
    "Describe this image",
    images=[Image(url="https://example.com/image.png")],
)
```

**New directory:** `agents/multimodal/`

---

#### 3.4 Run Cancellation Support

**Impact:** User experience, resource management
**Effort:** Medium

Enable cancellation of long-running agent operations.

```python
# In API handler
from agno.run import cancel_run

@app.post("/agents/{agent_id}/runs/{run_id}/cancel")
async def cancel_agent_run(agent_id: str, run_id: str):
    await cancel_run(run_id)
    return {"status": "cancelled"}
```

---

### Priority 4: Tooling Expansion

#### 4.1 Additional Tool Integrations

Current tools: DuckDuckGo, HackerNews, YFinance, Newspaper4k

Recommended additions based on Agno toolkit documentation:

| Category | Tool | Use Case |
|----------|------|----------|
| Search | Tavily | Better web search with extraction |
| Search | Exa | Semantic search |
| Database | Pandas | Data analysis |
| Database | SQL | Database queries |
| Scraping | Firecrawl | Production web scraping |
| Models | OpenAI | Image generation |
| Others | GitHub | Repository integration |
| Others | Notion | Documentation integration |
| Others | Google Calendar | Scheduling |

```python
# agents/tools/data_analyst_agent.py
from agno.tools.pandas_tools import PandasTools
from agno.tools.sql import SqlTools

data_analyst = Agent(
    name="Data Analyst",
    tools=[PandasTools(), SqlTools(db_url=db_url)],
    # ...
)
```

---

## Implementation Roadmap

### Phase 1: Quick Wins (1-2 days)

- [ ] Add context compression to research/web agents
- [ ] Add prompt injection guardrail to exposed agents
- [ ] Enable background hooks in AgentOS
- [ ] Add post-hooks for output validation

### Phase 2: Core Enhancements (1 week)

- [ ] Implement state management for learning assistant
- [ ] Add structured output schemas to finance/research agents
- [ ] Implement dependencies injection
- [ ] Create basic eval test suite

### Phase 3: Advanced Features (2-3 weeks)

- [ ] Implement Learning Machine with stores
- [ ] Create skills directory structure
- [ ] Build skills-enabled agent
- [ ] Add multimodal agent

### Phase 4: Production Polish (ongoing)

- [ ] Expand tool integrations
- [ ] Add comprehensive evals
- [ ] Performance optimization
- [ ] Documentation updates

---

## Files to Create

| File | Purpose |
|------|---------|
| `agents/stateful/preferences_agent.py` | State management demo |
| `agents/multimodal/vision_agent.py` | Image processing |
| `agents/skills_agent.py` | Skills-enabled agent |
| `agents/learning/advanced_learning_assistant.py` | Full learning machine |
| `tests/evals/test_knowledge_agent.py` | Accuracy evals |
| `tests/evals/test_research_agent.py` | Reliability evals |
| `skills/code-review/SKILL.md` | Code review skill |
| `skills/research/SKILL.md` | Research skill |
| `docs/COMPRESSION_GUIDE.md` | Context compression guide |

## Files to Modify

| File | Changes |
|------|---------|
| `app/main.py` | Add `run_hooks_in_background=True` |
| `agents/knowledge_agent.py` | Add prompt injection guardrail |
| `agents/mcp_agent.py` | Add prompt injection guardrail |
| `agents/tools/research_agent.py` | Add compression, structured output, post-hooks |
| `agents/tools/finance_agent.py` | Add structured output schema |
| `agents/learning/learning_assistant.py` | Add state management, dependencies |
| `teams/research_team.py` | Add compression |

---

## Success Metrics

| Metric | Current | Target |
|--------|---------|--------|
| Token cost per research query | ~10k tokens | ~5k tokens (compression) |
| Security guardrails | 1 (PII) | 3 (PII, Prompt Injection, Moderation) |
| Eval test coverage | 0% | 80% |
| Agent features per agent | ~5 | ~8 |
| Tool integrations | 4 | 10+ |

---

## References

- Agno Documentation: `.docs/agno-docs/`
- Context Compression: `/compression/overview.mdx`
- Guardrails: `/guardrails/overview.mdx`
- Hooks: `/hooks/overview.mdx`
- Evals: `/evals/overview.mdx`
- Skills: `/skills/overview.mdx`
- Learning Machine: `/learning/overview.mdx`
- State Management: `/state/overview.mdx`
- Dependencies: `/dependencies/overview.mdx`
- Multimodal: `/multimodal/overview.mdx`

---

*Generated: 2026-01-28*
*Based on Agno documentation analysis (1,847 files)*
