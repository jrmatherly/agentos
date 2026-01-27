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
