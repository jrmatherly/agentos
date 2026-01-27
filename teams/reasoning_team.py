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
    tools=[YFinanceTools()],
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
