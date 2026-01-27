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
    tools=[YFinanceTools()],
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
