"""
Confirmation Agent
==================

Demonstrates Human-in-the-Loop patterns with user confirmation for
sensitive operations.

Run:
    python -m agents.hitl.confirmation_agent
"""

from agno.agent import Agent
from agno.models.litellm import LiteLLM
from agno.tools import tool

from app.config import get_litellm_config, get_model_id
from db.session import get_session_db

# ============================================================================
# Setup
# ============================================================================
agent_db = get_session_db()


# ============================================================================
# Tools with Confirmation Requirements
# ============================================================================
@tool(requires_confirmation=True)
def send_email(to: str, subject: str, body: str) -> str:
    """Send an email to the specified recipient. Requires user confirmation.

    Args:
        to: Email recipient address
        subject: Email subject line
        body: Email body content

    Returns:
        Confirmation message
    """
    # Simulated - in production, integrate with email service
    return f"Email sent successfully to {to} with subject: {subject}"


@tool(requires_confirmation=True)
def delete_file(filepath: str) -> str:
    """Delete a file from the system. Requires user confirmation.

    Args:
        filepath: Path to the file to delete

    Returns:
        Confirmation message
    """
    # Simulated - demonstrates dangerous operation pattern
    return f"File {filepath} has been deleted"


@tool(requires_confirmation=True)
def execute_command(command: str) -> str:
    """Execute a system command. Requires user confirmation.

    Args:
        command: The command to execute

    Returns:
        Command output
    """
    # Simulated - never execute arbitrary commands in production
    return f"Command executed: {command}"


@tool
def search_files(query: str) -> str:
    """Search for files matching the query. No confirmation needed.

    Args:
        query: Search query string

    Returns:
        List of matching files
    """
    # Safe operation - no confirmation required
    return f"Found 3 files matching '{query}': file1.txt, file2.txt, file3.txt"


@tool
def read_file(filepath: str) -> str:
    """Read contents of a file. No confirmation needed.

    Args:
        filepath: Path to the file to read

    Returns:
        File contents
    """
    # Safe read operation
    return f"Contents of {filepath}: [simulated file contents]"


# ============================================================================
# Agent Instructions
# ============================================================================
instructions = """\
You help users manage files and communications.

HITL GUIDELINES
---------------
- File searches and reads run automatically (safe operations)
- Emails, deletions, and commands require user approval (sensitive operations)
- Always explain what you're about to do before requesting confirmation
- If user rejects an action, acknowledge and ask for alternative instructions

WORKFLOW
--------
1. Understand the user's request
2. Identify which operations are needed
3. For sensitive operations, explain what will happen
4. Wait for confirmation before proceeding
5. Report results or handle rejections gracefully
"""

# ============================================================================
# Create Agent
# ============================================================================
confirmation_agent = Agent(
    name="Confirmation Agent",
    model=LiteLLM(
        id=get_model_id("Confirmation Agent"),
        **get_litellm_config(),
    ),
    db=agent_db,
    tools=[send_email, delete_file, execute_command, search_files, read_file],
    instructions=instructions,
    enable_agentic_memory=True,
    add_datetime_to_context=True,
    markdown=True,
)

if __name__ == "__main__":
    from rich.console import Console
    from rich.prompt import Prompt

    console = Console()

    print("HITL Confirmation Agent Demo")
    print("=" * 50)

    run_response = confirmation_agent.run(
        "Search for files containing 'report' and then send an email to bob@example.com with the list"
    )

    # Handle any pending confirmations
    for requirement in run_response.active_requirements:
        if requirement.needs_confirmation and requirement.tool_execution:
            console.print(
                f"\nTool [bold blue]{requirement.tool_execution.tool_name}"
                f"({requirement.tool_execution.tool_args})[/] requires confirmation."
            )
            message = Prompt.ask("Approve?", choices=["y", "n"], default="y").strip().lower()

            if message == "n":
                requirement.reject()
            else:
                requirement.confirm()

    # Continue execution after confirmations
    if run_response.active_requirements:
        final_response = confirmation_agent.continue_run(
            run_id=run_response.run_id,
            requirements=run_response.requirements,
        )
        print(f"\nFinal response: {final_response.content}")
    else:
        print(f"\nResponse: {run_response.content}")
