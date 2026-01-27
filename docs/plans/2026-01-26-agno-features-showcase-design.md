# Agno Features Showcase Design

**Date**: 2026-01-26
**Goal**: Comprehensive showcase of Agno capabilities for learning/reference purposes
**Scope**: 12 new files, 2 moved files, 5 `__init__.py` files, 2 new dependencies

## Overview

This design adds comprehensive examples across 6 Agno feature categories:

| Category | Files | Key Features |
|----------|-------|--------------|
| Reasoning | 3 agents | All 3 approaches: models, tools, `reasoning=True` |
| Tools | 3 agents | Finance (YFinance), Web scraping (Newspaper4k), Deep research |
| Learning | 1 agent | Learning Machine with agentic mode |
| HITL | 1 agent | User confirmation for sensitive operations |
| Teams | 2 new + 1 moved | Support routing, reasoning team with visible thinking |
| Workflows | 1 new + 1 moved | Async, caching, Pydantic schemas |

## Directory Structure

```tree
agents/
├── __init__.py                    # Updated exports
├── knowledge_agent.py             # Existing
├── mcp_agent.py                   # Existing
│
├── reasoning/                     # NEW: Reasoning showcase
│   ├── __init__.py
│   ├── reasoning_model_agent.py   # Native reasoning model
│   ├── reasoning_tools_agent.py   # ReasoningTools approach
│   └── reasoning_agent.py         # reasoning=True approach
│
├── tools/                         # NEW: Tool showcase
│   ├── __init__.py
│   ├── finance_agent.py           # YFinance tools
│   ├── web_scraper_agent.py       # Firecrawl/Newspaper4k
│   └── research_agent.py          # DuckDuckGo + deep research
│
├── learning/                      # NEW: Learning Machine
│   ├── __init__.py
│   └── learning_assistant.py      # Agent that improves over time
│
└── hitl/                          # NEW: Human-in-the-loop
    ├── __init__.py
    └── confirmation_agent.py      # User confirmation patterns

teams/                             # NEW: Team directory
├── __init__.py
├── research_team.py               # Moved from agents/
├── support_team.py                # NEW: Routing/classification
└── reasoning_team.py              # NEW: Visible thinking

workflows/                         # NEW: Workflow directory
├── __init__.py
├── content_workflow.py            # Moved from agents/
└── blog_generator.py              # NEW: Async + caching + Pydantic
```

---

## 1. Reasoning Showcase

Three agents demonstrating each reasoning approach.

### 1.1 `agents/reasoning/reasoning_model_agent.py`

Uses a native reasoning model that thinks internally before responding.

```python
"""
Reasoning Model Agent
=====================

Demonstrates using a native reasoning model (DeepSeek-R1, o3-mini) that
performs chain-of-thought internally.

Run:
    python -m agents.reasoning.reasoning_model_agent
"""

from agno.agent import Agent
from agno.models.litellm import LiteLLM

from app.config import get_litellm_config, get_model_id
from db.session import get_session_db

# ============================================================================
# Setup
# ============================================================================
agent_db = get_session_db()

# ============================================================================
# Agent Instructions
# ============================================================================
instructions = """\
You are an analytical problem solver that thinks through complex problems.

WORKFLOW
--------
1. Analyze the problem carefully
2. Break it into logical steps
3. Work through each step methodically
4. Verify your reasoning before concluding

BEST FOR
--------
- Math and logic problems
- Code analysis and debugging
- Complex decision making
- Scientific reasoning
"""

# ============================================================================
# Create Agent
# ============================================================================
reasoning_model_agent = Agent(
    name="Reasoning Model Agent",
    model=LiteLLM(
        id=get_model_id("Reasoning Model Agent"),
        **get_litellm_config(),
    ),
    db=agent_db,
    instructions=instructions,
    enable_agentic_memory=True,
    add_datetime_to_context=True,
    markdown=True,
)

if __name__ == "__main__":
    # Example: Problem that benefits from step-by-step reasoning
    reasoning_model_agent.print_response(
        "Which is larger: 9.11 or 9.9? Explain your reasoning.",
        stream=True,
        show_full_reasoning=True,
    )
```

### 1.2 `agents/reasoning/reasoning_tools_agent.py`

Adds explicit thinking tools to any model.

```python
"""
Reasoning Tools Agent
=====================

Demonstrates using ReasoningTools to add explicit think() and analyze()
capabilities to any model.

Run:
    python -m agents.reasoning.reasoning_tools_agent
"""

from agno.agent import Agent
from agno.models.litellm import LiteLLM
from agno.tools.reasoning import ReasoningTools

from app.config import get_litellm_config, get_model_id
from db.session import get_session_db

# ============================================================================
# Setup
# ============================================================================
agent_db = get_session_db()

# ============================================================================
# Agent Instructions
# ============================================================================
instructions = """\
You are a research analyst that thinks through problems systematically.

WORKFLOW
--------
1. Use the think() tool to plan your approach
2. Break complex problems into sub-questions
3. Use analyze() to evaluate information
4. Synthesize findings into clear conclusions

GUIDELINES
----------
- Always show your reasoning process
- Consider multiple perspectives
- Validate assumptions before concluding
- Use tables to organize comparisons
"""

# ============================================================================
# Create Agent
# ============================================================================
reasoning_tools_agent = Agent(
    name="Reasoning Tools Agent",
    model=LiteLLM(
        id=get_model_id("Reasoning Tools Agent"),
        **get_litellm_config(),
    ),
    db=agent_db,
    tools=[ReasoningTools(add_instructions=True)],
    instructions=instructions,
    enable_agentic_memory=True,
    add_datetime_to_context=True,
    markdown=True,
)

if __name__ == "__main__":
    reasoning_tools_agent.print_response(
        "Compare the pros and cons of microservices vs monolithic architecture for a startup.",
        stream=True,
        show_full_reasoning=True,
    )
```

### 1.3 `agents/reasoning/reasoning_agent.py`

Transforms any model into a reasoning system via `reasoning=True`.

```python
"""
Reasoning Agent
===============

Demonstrates the reasoning=True flag that transforms any model into
a reasoning system through structured chain-of-thought prompting.

Run:
    python -m agents.reasoning.reasoning_agent
"""

from agno.agent import Agent
from agno.models.litellm import LiteLLM

from app.config import get_litellm_config, get_model_id
from db.session import get_session_db

# ============================================================================
# Setup
# ============================================================================
agent_db = get_session_db()

# ============================================================================
# Agent Instructions
# ============================================================================
instructions = """\
You solve complex problems requiring multiple steps and tool calls.

WORKFLOW
--------
1. Understand the full problem scope
2. Plan the sequence of steps needed
3. Execute each step, validating results
4. Self-correct if you detect errors
5. Provide a comprehensive final answer

GUIDELINES
----------
- Think before acting
- Validate intermediate results
- Catch and fix your own mistakes
- Explain your reasoning clearly
"""

# ============================================================================
# Create Agent
# ============================================================================
reasoning_agent = Agent(
    name="Reasoning Agent",
    model=LiteLLM(
        id=get_model_id("Reasoning Agent"),
        **get_litellm_config(),
    ),
    db=agent_db,
    reasoning=True,  # Enables structured chain-of-thought
    instructions=instructions,
    enable_agentic_memory=True,
    add_datetime_to_context=True,
    markdown=True,
)

if __name__ == "__main__":
    reasoning_agent.print_response(
        "Plan a 3-day technical conference. Include sessions, speakers criteria, and logistics.",
        stream=True,
        show_full_reasoning=True,
    )
```

---

## 2. Tools Showcase

Three agents demonstrating different built-in tool categories.

### 2.1 `agents/tools/finance_agent.py`

```python
"""
Finance Agent
=============

Demonstrates YFinance tools for stock analysis and financial data.

Run:
    python -m agents.tools.finance_agent
"""

from agno.agent import Agent
from agno.models.litellm import LiteLLM
from agno.tools.yfinance import YFinanceTools

from app.config import get_litellm_config, get_model_id
from db.session import get_session_db

# ============================================================================
# Setup
# ============================================================================
agent_db = get_session_db()

# ============================================================================
# Agent Instructions
# ============================================================================
instructions = """\
You are a financial analyst assistant.

WORKFLOW
--------
1. Gather requested financial data using tools
2. Analyze trends and patterns
3. Present findings with data tables
4. Provide balanced insights (not financial advice)

GUIDELINES
----------
- Always cite data sources and timestamps
- Use tables for numerical comparisons
- Include relevant context for metrics
- Disclaimer: This is informational, not financial advice
"""

# ============================================================================
# Create Agent
# ============================================================================
finance_agent = Agent(
    name="Finance Agent",
    model=LiteLLM(
        id=get_model_id("Finance Agent"),
        **get_litellm_config(),
    ),
    db=agent_db,
    tools=[
        YFinanceTools(
            stock_price=True,
            analyst_recommendations=True,
            company_info=True,
            historical_prices=True,
        )
    ],
    instructions=instructions,
    enable_agentic_memory=True,
    add_datetime_to_context=True,
    markdown=True,
)

if __name__ == "__main__":
    finance_agent.print_response(
        "Analyze NVDA stock - current price, recent performance, and analyst recommendations.",
        stream=True,
    )
```

### 2.2 `agents/tools/web_scraper_agent.py`

```python
"""
Web Scraper Agent
=================

Demonstrates Newspaper4k tools for web content extraction.

Run:
    python -m agents.tools.web_scraper_agent
"""

from agno.agent import Agent
from agno.models.litellm import LiteLLM
from agno.tools.duckduckgo import DuckDuckGoTools
from agno.tools.newspaper4k import Newspaper4kTools

from app.config import get_litellm_config, get_model_id
from db.session import get_session_db

# ============================================================================
# Setup
# ============================================================================
agent_db = get_session_db()

# ============================================================================
# Agent Instructions
# ============================================================================
instructions = """\
You are a web research assistant that extracts and summarizes content.

WORKFLOW
--------
1. Search for relevant articles on the topic
2. Extract full content from promising URLs
3. Summarize key points and insights
4. Cite sources with URLs

GUIDELINES
----------
- Prioritize recent, authoritative sources
- Extract quotes and statistics when relevant
- Organize findings by theme or importance
- Always attribute information to sources
"""

# ============================================================================
# Create Agent
# ============================================================================
web_scraper_agent = Agent(
    name="Web Scraper Agent",
    model=LiteLLM(
        id=get_model_id("Web Scraper Agent"),
        **get_litellm_config(),
    ),
    db=agent_db,
    tools=[DuckDuckGoTools(), Newspaper4kTools()],
    instructions=instructions,
    enable_agentic_memory=True,
    add_datetime_to_context=True,
    markdown=True,
)

if __name__ == "__main__":
    web_scraper_agent.print_response(
        "Find and summarize the latest news about AI agents and autonomous systems.",
        stream=True,
    )
```

### 2.3 `agents/tools/research_agent.py`

```python
"""
Research Agent
==============

Deep research agent that searches multiple sources, cross-references facts,
and produces structured reports.

Run:
    python -m agents.tools.research_agent
"""

from textwrap import dedent

from agno.agent import Agent
from agno.models.litellm import LiteLLM
from agno.tools.duckduckgo import DuckDuckGoTools
from agno.tools.newspaper4k import Newspaper4kTools

from app.config import get_litellm_config, get_model_id
from db.session import get_session_db

# ============================================================================
# Setup
# ============================================================================
agent_db = get_session_db()

# ============================================================================
# Agent Instructions
# ============================================================================
instructions = """\
You are an elite investigative researcher producing comprehensive reports.

WORKFLOW
--------
1. Research Phase
   - Search for 10+ authoritative sources
   - Prioritize recent publications and expert opinions
   - Identify key stakeholders and perspectives

2. Analysis Phase
   - Extract and verify critical information
   - Cross-reference facts across multiple sources
   - Identify patterns and trends
   - Evaluate conflicting viewpoints

3. Writing Phase
   - Craft a compelling headline
   - Structure content professionally
   - Include relevant quotes and statistics
   - Maintain objectivity and balance

4. Quality Control
   - Verify all facts and attributions
   - Ensure narrative flow and readability
   - Add context where necessary
"""

expected_output = dedent("""\
# {Compelling Headline}

## Executive Summary
{Concise overview of key findings}

## Background & Context
{Historical context and current landscape}

## Key Findings
{Main discoveries with evidence}
{Expert insights and quotes}
{Statistical evidence}

## Impact Analysis
{Current implications}
{Stakeholder perspectives}

## Future Outlook
{Emerging trends}
{Expert predictions}

## Sources
{List of sources with URLs}
""")

# ============================================================================
# Create Agent
# ============================================================================
research_agent = Agent(
    name="Research Agent",
    model=LiteLLM(
        id=get_model_id("Research Agent"),
        **get_litellm_config(),
    ),
    db=agent_db,
    tools=[DuckDuckGoTools(), Newspaper4kTools()],
    instructions=instructions,
    expected_output=expected_output,
    enable_agentic_memory=True,
    add_datetime_to_context=True,
    markdown=True,
)

if __name__ == "__main__":
    research_agent.print_response(
        "Research the current state of AI regulation worldwide.",
        stream=True,
    )
```

---

## 3. Learning Machine

### 3.1 `agents/learning/learning_assistant.py`

```python
"""
Learning Assistant
==================

An agent that learns and improves over time using Learning Machine.

Run:
    python -m agents.learning.learning_assistant
"""

from agno.agent import Agent
from agno.models.litellm import LiteLLM

from app.config import get_litellm_config, get_model_id
from db.session import get_postgres_db, get_session_db

# ============================================================================
# Setup
# ============================================================================
agent_db = get_session_db()
postgres_db = get_postgres_db()

# ============================================================================
# Agent Instructions
# ============================================================================
instructions = """\
You are a personal assistant that learns and improves over time.

LEARNING GUIDELINES
-------------------
- Remember user preferences (communication style, topics of interest)
- Learn from corrections and feedback
- Build knowledge about recurring topics
- Adapt responses based on past interactions

WORKFLOW
--------
1. Check if you have relevant learned context
2. Apply learned preferences to your response
3. Note new information worth remembering
4. Explicitly mention when you've learned something new

GUIDELINES
----------
- Be helpful and adaptive
- Acknowledge when you remember something
- Ask clarifying questions to learn preferences
- Improve response quality over time
"""

# ============================================================================
# Create Agent
# ============================================================================
learning_assistant = Agent(
    name="Learning Assistant",
    model=LiteLLM(
        id=get_model_id("Learning Assistant"),
        **get_litellm_config(),
    ),
    db=agent_db,
    instructions=instructions,
    learning=True,
    learning_mode="agentic",  # Agent decides what to learn
    enable_agentic_memory=True,
    add_datetime_to_context=True,
    add_history_to_context=True,
    num_history_runs=10,
    markdown=True,
)

if __name__ == "__main__":
    learning_assistant.cli_app(stream=True)
```

---

## 4. Human-in-the-Loop

### 4.1 `agents/hitl/confirmation_agent.py`

```python
"""
Confirmation Agent
==================

Demonstrates Human-in-the-Loop patterns with user confirmation for
sensitive operations.

Run:
    python -m agents.hitl.confirmation_agent
"""

from agno.agent import Agent
from agno.models.litellm import LiteLLM
from agno.tools.base import tool

from app.config import get_litellm_config, get_model_id
from db.session import get_session_db

# ============================================================================
# Setup
# ============================================================================
agent_db = get_session_db()


# ============================================================================
# Tools with Confirmation
# ============================================================================
@tool(requires_confirmation=True)
def send_email(to: str, subject: str, body: str) -> str:
    """Send an email to the specified recipient. Requires user confirmation."""
    # Simulated - in production, integrate with email service
    return f"Email sent successfully to {to} with subject: {subject}"


@tool(requires_confirmation=True)
def delete_file(filepath: str) -> str:
    """Delete a file from the system. Requires user confirmation."""
    # Simulated - demonstrates dangerous operation pattern
    return f"File {filepath} has been deleted"


@tool(requires_confirmation=True)
def execute_command(command: str) -> str:
    """Execute a system command. Requires user confirmation."""
    # Simulated - never execute arbitrary commands in production
    return f"Command executed: {command}"


@tool
def search_files(query: str) -> str:
    """Search for files matching the query. No confirmation needed."""
    # Safe operation - no confirmation required
    return f"Found 3 files matching '{query}': file1.txt, file2.txt, file3.txt"


@tool
def read_file(filepath: str) -> str:
    """Read contents of a file. No confirmation needed."""
    # Safe read operation
    return f"Contents of {filepath}: [simulated file contents]"


# ============================================================================
# Agent Instructions
# ============================================================================
instructions = """\
You help users manage files and communications.

HITL GUIDELINES
---------------
- File searches and reads run automatically (safe operations)
- Emails, deletions, and commands require user approval (sensitive operations)
- Always explain what you're about to do before requesting confirmation
- If user rejects an action, acknowledge and ask for alternative instructions

WORKFLOW
--------
1. Understand the user's request
2. Identify which operations are needed
3. For sensitive operations, explain what will happen
4. Wait for confirmation before proceeding
5. Report results or handle rejections gracefully
"""

# ============================================================================
# Create Agent
# ============================================================================
confirmation_agent = Agent(
    name="Confirmation Agent",
    model=LiteLLM(
        id=get_model_id("Confirmation Agent"),
        **get_litellm_config(),
    ),
    db=agent_db,
    tools=[send_email, delete_file, execute_command, search_files, read_file],
    instructions=instructions,
    enable_agentic_memory=True,
    add_datetime_to_context=True,
    markdown=True,
)

if __name__ == "__main__":
    # Example usage with HITL flow
    print("HITL Confirmation Agent Demo")
    print("=" * 50)

    response = confirmation_agent.run(
        "Search for files containing 'report' and then send an email to bob@example.com with the list"
    )

    # Handle any pending confirmations
    for req in response.active_requirements:
        if req.needs_confirmation:
            print(f"\nPending confirmation for: {req.tool.tool_name}")
            print(f"Arguments: {req.tool.tool_args}")
            user_input = input("Approve? (y/n): ")
            if user_input.lower() == "y":
                req.confirm()
            else:
                req.reject()

    # Continue execution after confirmations
    if response.active_requirements:
        final_response = confirmation_agent.continue_run(run_response=response)
        print(f"\nFinal response: {final_response.content}")
    else:
        print(f"\nResponse: {response.content}")
```

---

## 5. Teams

### 5.1 `teams/research_team.py`

Moved from `agents/research_team.py` - no code changes, just relocated.

### 5.2 `teams/support_team.py`

```python
"""
Support Team
============

Intelligent routing team that classifies queries and delegates to specialists.

Run:
    python -m teams.support_team
"""

from agno.agent import Agent
from agno.knowledge import Knowledge
from agno.knowledge.embedder.openai import OpenAIEmbedder
from agno.models.litellm import LiteLLM
from agno.team import Team
from agno.vectordb.pgvector import PgVector, SearchType

from app.config import get_litellm_config, get_model_id
from db.session import db_url, get_postgres_db, get_session_db

# ============================================================================
# Setup
# ============================================================================
team_db = get_session_db()

# Knowledge base for documentation agent
knowledge = Knowledge(
    name="Support Knowledge Base",
    vector_db=PgVector(
        db_url=db_url,
        table_name="support_team_docs",
        search_type=SearchType.hybrid,
        embedder=OpenAIEmbedder(id="text-embedding-3-small"),
    ),
    max_results=5,
    contents_db=get_postgres_db(),
)

# ============================================================================
# Team Members
# ============================================================================
doc_agent = Agent(
    id="doc-agent",
    name="Documentation Agent",
    role="Answer questions using the knowledge base",
    knowledge=knowledge,
    search_knowledge=True,
    instructions="""\
You search the knowledge base to answer user questions.
- Provide accurate information based on documentation
- Include relevant quotes and references
- If information isn't found, say so clearly
- Suggest related topics when helpful
""",
)

escalation_agent = Agent(
    id="escalation-agent",
    name="Escalation Agent",
    role="Handle bug reports and issues requiring human attention",
    instructions="""\
You handle bug reports and escalations.
- Gather all relevant details about the issue
- Categorize the severity (critical, high, medium, low)
- Document reproduction steps if provided
- Acknowledge the report and set expectations
- Log the issue for the support team
""",
)

feedback_agent = Agent(
    id="feedback-agent",
    name="Feedback Agent",
    role="Collect and acknowledge user feedback and feature requests",
    instructions="""\
You collect user feedback and feature requests.
- Thank users for their input
- Clarify and document the feedback clearly
- Categorize as: bug, feature request, improvement, praise
- Acknowledge without promising specific timelines
- Note any context that helps prioritize
""",
)

# ============================================================================
# Create Team
# ============================================================================
support_team = Team(
    id="support-team",
    name="Support Team",
    model=LiteLLM(id=get_model_id("Support Team"), **get_litellm_config()),
    db=team_db,
    members=[doc_agent, escalation_agent, feedback_agent],
    instructions="""\
You are the support team leader responsible for routing customer inquiries.

CLASSIFICATION
--------------
Analyze each message and classify as:
- QUESTION: Product questions, how-to inquiries -> Documentation Agent
- BUG: Error reports, broken features, issues -> Escalation Agent
- FEEDBACK: Feature requests, suggestions, praise -> Feedback Agent

WORKFLOW
--------
1. Read and understand the inquiry
2. Classify the inquiry type
3. Route to the appropriate agent with context
4. Ensure the user gets a helpful response

GUIDELINES
----------
- Be empathetic and professional
- When unclear, ask for clarification
- Ensure smooth handoffs between agents
- Follow up if the first response doesn't fully address the inquiry
""",
    show_members_responses=True,
    enable_agentic_memory=True,
    markdown=True,
)

if __name__ == "__main__":
    support_team.cli_app(stream=True)
```

### 5.3 `teams/reasoning_team.py`

```python
"""
Reasoning Team
==============

Team with visible reasoning process using ReasoningTools.

Run:
    python -m teams.reasoning_team
"""

from agno.agent import Agent
from agno.models.litellm import LiteLLM
from agno.team import Team
from agno.tools.duckduckgo import DuckDuckGoTools
from agno.tools.reasoning import ReasoningTools
from agno.tools.yfinance import YFinanceTools

from app.config import get_litellm_config, get_model_id
from db.session import get_session_db

# ============================================================================
# Setup
# ============================================================================
team_db = get_session_db()

# ============================================================================
# Team Members
# ============================================================================
web_agent = Agent(
    id="web-agent",
    name="Web Search Agent",
    role="Search the web for current information",
    tools=[DuckDuckGoTools()],
    instructions="Search the web for relevant information. Always cite sources.",
)

finance_agent = Agent(
    id="finance-agent",
    name="Finance Agent",
    role="Retrieve and analyze financial data",
    tools=[
        YFinanceTools(
            stock_price=True,
            analyst_recommendations=True,
            company_info=True,
        )
    ],
    instructions="Retrieve financial data and present in tables. Include context for metrics.",
)

# ============================================================================
# Create Team
# ============================================================================
reasoning_team = Team(
    id="reasoning-team",
    name="Reasoning Team",
    model=LiteLLM(id=get_model_id("Reasoning Team"), **get_litellm_config()),
    db=team_db,
    members=[web_agent, finance_agent],
    tools=[ReasoningTools(add_instructions=True)],  # Team-level reasoning
    instructions="""\
You are a research team leader with transparent reasoning.

WORKFLOW
--------
1. Use think() to plan your approach to the query
2. Decide which team members to involve
3. Coordinate their work and synthesize findings
4. Use analyze() to evaluate the combined results
5. Present a comprehensive, well-reasoned response

GUIDELINES
----------
- Show your reasoning process transparently
- Delegate appropriately based on member expertise
- Cross-reference information from multiple sources
- Present findings with supporting evidence
""",
    show_members_responses=True,
    enable_agentic_memory=True,
    markdown=True,
)

if __name__ == "__main__":
    reasoning_team.print_response(
        "What are the top 3 AI companies by market cap and what's driving their growth?",
        stream=True,
        show_full_reasoning=True,
    )
```

---

## 6. Advanced Workflows

### 6.1 `workflows/content_workflow.py`

Moved from `agents/content_workflow.py` - no code changes, just relocated.

### 6.2 `workflows/blog_generator.py`

```python
"""
Blog Generator Workflow
=======================

Advanced async workflow with caching and Pydantic output schemas.

Run:
    python -m workflows.blog_generator
"""

import asyncio
import json
from textwrap import dedent
from typing import Optional

from agno.agent import Agent
from agno.models.litellm import LiteLLM
from agno.tools.duckduckgo import DuckDuckGoTools
from agno.tools.newspaper4k import Newspaper4kTools
from agno.workflow.workflow import Workflow
from pydantic import BaseModel, Field

from app.config import get_litellm_config, get_model_id
from db.session import get_session_db

# ============================================================================
# Response Schemas
# ============================================================================


class NewsArticle(BaseModel):
    title: str = Field(description="Title of the article")
    url: str = Field(description="URL of the article")
    summary: Optional[str] = Field(description="Brief summary if available")


class SearchResults(BaseModel):
    articles: list[NewsArticle] = Field(description="List of found articles")


class ScrapedArticle(BaseModel):
    title: str = Field(description="Article title")
    url: str = Field(description="Article URL")
    content: Optional[str] = Field(description="Full article content in markdown")


# ============================================================================
# Setup
# ============================================================================
workflow_db = get_session_db()
model = LiteLLM(id=get_model_id("Blog Generator"), **get_litellm_config())

# ============================================================================
# Workflow Agents
# ============================================================================
research_agent = Agent(
    name="Blog Research Agent",
    model=model,
    tools=[DuckDuckGoTools()],
    output_schema=SearchResults,
    instructions=dedent("""\
        You find high-quality sources for blog content.
        - Search for 5-7 authoritative, recent sources
        - Evaluate credibility and relevance
        - Return structured results with titles, URLs, and summaries
    """),
)

scraper_agent = Agent(
    name="Content Scraper Agent",
    model=model,
    tools=[Newspaper4kTools()],
    output_schema=ScrapedArticle,
    instructions=dedent("""\
        You extract article content from URLs.
        - Extract the full article text
        - Preserve important quotes and statistics
        - Format content in clean markdown
    """),
)

writer_agent = Agent(
    name="Blog Writer Agent",
    model=model,
    instructions=dedent("""\
        You write engaging, well-researched blog posts.

        STRUCTURE
        ---------
        # {Viral-Worthy Headline}

        ## Introduction
        {Engaging hook and context}

        ## {Main Section 1}
        {Key insights with evidence}

        ## {Main Section 2}
        {Deeper exploration}

        ## Key Takeaways
        - {Takeaway 1}
        - {Takeaway 2}
        - {Takeaway 3}

        ## Sources
        {Attributed sources with links}

        GUIDELINES
        ----------
        - Write in a professional but approachable tone
        - Include statistics and quotes from sources
        - Optimize for readability and SEO
        - Always cite sources
    """),
    markdown=True,
)


# ============================================================================
# Caching Helpers
# ============================================================================
def get_cached(session_state: dict, key: str, topic: str):
    """Get cached value from session state."""
    return session_state.get(key, {}).get(topic)


def set_cached(session_state: dict, key: str, topic: str, value):
    """Set cached value in session state."""
    if key not in session_state:
        session_state[key] = {}
    session_state[key][topic] = value


# ============================================================================
# Workflow Execution
# ============================================================================
async def blog_generation(
    session_state: dict,
    topic: str,
    use_cache: bool = True,
) -> str:
    """
    Generate a blog post through research, scraping, and writing phases.

    Args:
        session_state: Shared state for caching
        topic: The blog topic to write about
        use_cache: Whether to use cached results
    """
    print(f"Generating blog post about: {topic}")
    print("=" * 60)

    # Check for cached blog post
    if use_cache:
        cached_blog = get_cached(session_state, "blog_posts", topic)
        if cached_blog:
            print("Found cached blog post!")
            return cached_blog

    # Phase 1: Research
    print("\nPHASE 1: RESEARCH")
    print("-" * 40)

    cached_search = get_cached(session_state, "search_results", topic) if use_cache else None
    if cached_search:
        print("Using cached search results")
        search_results = SearchResults.model_validate(cached_search)
    else:
        print(f"Searching for articles about: {topic}")
        response = await research_agent.arun(f"Find articles about: {topic}")
        if not response or not response.content:
            return f"Could not find articles about: {topic}"
        search_results = response.content
        set_cached(session_state, "search_results", topic, search_results.model_dump())

    print(f"Found {len(search_results.articles)} articles")

    # Phase 2: Scrape articles (parallel)
    print("\nPHASE 2: CONTENT EXTRACTION")
    print("-" * 40)

    cached_articles = get_cached(session_state, "scraped_articles", topic) if use_cache else None
    if cached_articles:
        print("Using cached scraped articles")
        scraped_articles = [ScrapedArticle.model_validate(a) for a in cached_articles]
    else:
        print(f"Scraping {len(search_results.articles)} articles...")
        tasks = [scraper_agent.arun(article.url) for article in search_results.articles]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        scraped_articles = []
        for result in results:
            if not isinstance(result, Exception) and result and result.content:
                scraped_articles.append(result.content)

        set_cached(
            session_state,
            "scraped_articles",
            topic,
            [a.model_dump() for a in scraped_articles],
        )

    print(f"Successfully scraped {len(scraped_articles)} articles")

    if not scraped_articles:
        return f"Could not extract content for: {topic}"

    # Phase 3: Write blog post
    print("\nPHASE 3: WRITING")
    print("-" * 40)

    writer_input = {
        "topic": topic,
        "articles": [a.model_dump() for a in scraped_articles],
    }

    print("Writing blog post...")
    response = await writer_agent.arun(json.dumps(writer_input, indent=2))

    if not response or not response.content:
        return f"Could not generate blog post for: {topic}"

    blog_post = response.content
    set_cached(session_state, "blog_posts", topic, blog_post)

    print("Blog post generated successfully!")
    return blog_post


# ============================================================================
# Create Workflow
# ============================================================================
blog_workflow = Workflow(
    name="Blog Generator",
    description="Research, scrape, and write blog posts with caching",
    db=workflow_db,
    steps=blog_generation,
    session_state={},
)

if __name__ == "__main__":

    async def main():
        topic = "The future of AI agents in enterprise software"
        response = await blog_workflow.arun(topic=topic, use_cache=True)
        print("\n" + "=" * 60)
        print("GENERATED BLOG POST")
        print("=" * 60)
        print(response.content)

    asyncio.run(main())
```

---

## 7. Integration

### 7.1 `app/main.py` Updates

```python
import litellm
from agno.agent.os import AgentOS

# Existing agents
from agents.knowledge_agent import knowledge_agent
from agents.mcp_agent import mcp_agent

# Reasoning agents
from agents.reasoning import (
    reasoning_agent,
    reasoning_model_agent,
    reasoning_tools_agent,
)

# Tool showcase agents
from agents.tools import finance_agent, research_agent, web_scraper_agent

# Learning agent
from agents.learning import learning_assistant

# HITL agent
from agents.hitl import confirmation_agent

# Teams
from teams import reasoning_team, research_team, support_team

# Workflows
from workflows import blog_workflow, content_workflow

litellm.drop_params = True

app = AgentOS(
    agents=[
        # Existing
        knowledge_agent,
        mcp_agent,
        # Reasoning showcase
        reasoning_model_agent,
        reasoning_tools_agent,
        reasoning_agent,
        # Tools showcase
        finance_agent,
        web_scraper_agent,
        research_agent,
        # Learning
        learning_assistant,
        # HITL
        confirmation_agent,
    ],
    teams=[research_team, support_team, reasoning_team],
    workflows=[content_workflow, blog_workflow],
    tracing=True,
    enable_mcp_server=True,
)
```

### 7.2 Package `__init__.py` Files

Each new directory needs an `__init__.py` that exports its components:

```python
# agents/reasoning/__init__.py
from .reasoning_agent import reasoning_agent
from .reasoning_model_agent import reasoning_model_agent
from .reasoning_tools_agent import reasoning_tools_agent

__all__ = ["reasoning_model_agent", "reasoning_tools_agent", "reasoning_agent"]
```

Similar patterns for `agents/tools/`, `agents/learning/`, `agents/hitl/`, `teams/`, and `workflows/`.

### 7.3 Dependencies

Add to `pyproject.toml`:

```toml
[project]
dependencies = [
    # ... existing ...
    "yfinance>=0.2.0",
    "newspaper4k>=0.9.0",
    "lxml-html-clean>=0.1.0",
]
```

---

## 8. Implementation Order

Suggested sequence for implementation:

1. **Directory structure** - Create directories and `__init__.py` files
2. **Move existing files** - Relocate research_team.py and content_workflow.py
3. **Tools showcase** - finance_agent, web_scraper_agent, research_agent
4. **Reasoning showcase** - All 3 reasoning agents
5. **Teams** - support_team, reasoning_team
6. **Learning** - learning_assistant
7. **HITL** - confirmation_agent
8. **Workflows** - blog_generator
9. **Integration** - Update app/main.py and add dependencies
10. **Testing** - Verify all agents/teams/workflows work

---

## 9. Documentation Updates

After implementation, update:

- `CLAUDE.md` - Add new agents, teams, workflows to documentation
- `README.md` - Update features list and usage examples
- Serena memory `adding_agents.md` - Add patterns for each new category
