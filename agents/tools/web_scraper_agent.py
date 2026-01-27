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
