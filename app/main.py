"""
AgentOS
=======

The main entry point for AgentOS.

Run:
    python -m app.main
"""

from pathlib import Path

import litellm

# Drop unsupported params (e.g., top_p for some models) to avoid UnsupportedParamsError
# This must be set before importing agents that use LiteLLM
litellm.drop_params = True

from agno.os import AgentOS  # noqa: E402
from fastapi.staticfiles import StaticFiles  # noqa: E402

# HITL agent
from agents.hitl import confirmation_agent  # noqa: E402

# Existing agents
from agents.knowledge_agent import knowledge_agent  # noqa: E402

# Learning agent
from agents.learning import learning_assistant  # noqa: E402
from agents.mcp_agent import mcp_agent  # noqa: E402

# Reasoning agents
from agents.reasoning import (  # noqa: E402
    reasoning_agent,
    reasoning_model_agent,
    reasoning_tools_agent,
)

# Tool showcase agents
from agents.tools import finance_agent, research_agent, web_scraper_agent  # noqa: E402

# Auth configuration
from app.auth import get_authorization_config, is_auth_enabled  # noqa: E402
from db.session import get_postgres_db  # noqa: E402

# Teams
from teams import reasoning_team, research_team, support_team  # noqa: E402

# Workflows
from workflows import blog_workflow, content_workflow  # noqa: E402

# ============================================================================
# Create AgentOS with tracing and optional JWT RBAC
# ============================================================================
auth_config = get_authorization_config()

agent_os = AgentOS(
    name="AgentOS",
    agents=[
        # Existing
        knowledge_agent,
        mcp_agent,
        # Reasoning showcase
        reasoning_model_agent,
        reasoning_tools_agent,
        reasoning_agent,
        # Tools showcase
        finance_agent,
        web_scraper_agent,
        research_agent,
        # Learning
        learning_assistant,
        # HITL
        confirmation_agent,
    ],
    teams=[research_team, support_team, reasoning_team],
    workflows=[content_workflow, blog_workflow],
    config=str(Path(__file__).parent / "config.yaml"),
    db=get_postgres_db(),  # Dedicated DB for traces
    tracing=True,  # Enable OpenTelemetry tracing
    enable_mcp_server=True,  # Expose as MCP server at /mcp
    # JWT RBAC (enabled if JWT_VERIFICATION_KEY or JWT_JWKS_FILE is set)
    authorization=is_auth_enabled(),
    authorization_config=auth_config,
)

if is_auth_enabled():
    print("[Auth] JWT RBAC authentication enabled")
else:
    print("[Auth] Running without authentication (development mode)")

app = agent_os.get_app()

# Mount static files for favicon and other assets
static_dir = Path(__file__).parent / "static"
if static_dir.exists():
    app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")


# Serve favicon from static directory
@app.get("/favicon.ico", include_in_schema=False)
async def favicon():
    from fastapi.responses import FileResponse

    favicon_path = static_dir / "favicon.ico"
    if favicon_path.exists():
        return FileResponse(favicon_path)
    # Return empty response if no favicon exists
    from fastapi.responses import Response

    return Response(status_code=204)


if __name__ == "__main__":
    agent_os.serve(app="main:app", reload=True)
