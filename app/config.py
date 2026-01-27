"""
Application Configuration
=========================

Centralized configuration from environment variables.
"""

from os import getenv


def get_litellm_config() -> dict:
    """Build LiteLLM configuration from environment."""
    config = {
        "api_key": getenv("LITELLM_API_KEY"),
    }

    api_base = getenv("LITELLM_API_BASE")
    if api_base:
        config["api_base"] = api_base

    return config


def get_model_id(agent_name: str) -> str:
    """Get model ID for an agent.

    Priority:
    1. Agent-specific env var (e.g., KNOWLEDGE_AGENT_MODEL)
    2. Default model env var (LITELLM_DEFAULT_MODEL)
    3. Hardcoded fallback
    """
    env_key = agent_name.upper().replace(" ", "_") + "_MODEL"

    return getenv(env_key, getenv("LITELLM_DEFAULT_MODEL", "gpt-5-mini"))
