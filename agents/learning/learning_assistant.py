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
from db.session import get_session_db

# ============================================================================
# Setup
# ============================================================================
agent_db = get_session_db()

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
    enable_agentic_memory=True,  # Enables learning via memory tools
    enable_user_memories=True,  # Auto-manage user memories
    add_datetime_to_context=True,
    add_history_to_context=True,
    num_history_runs=10,
    markdown=True,
)

if __name__ == "__main__":
    learning_assistant.cli_app(stream=True)
