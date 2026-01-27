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
