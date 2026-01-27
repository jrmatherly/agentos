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
