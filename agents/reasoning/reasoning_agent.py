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
