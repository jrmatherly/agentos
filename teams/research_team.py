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
