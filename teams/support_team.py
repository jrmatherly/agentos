"""
Support Team
============

Intelligent routing team that classifies queries and delegates to specialists.

Run:
    python -m teams.support_team
"""

from agno.agent import Agent
from agno.knowledge import Knowledge
from agno.knowledge.embedder.openai import OpenAIEmbedder
from agno.models.litellm import LiteLLM
from agno.team import Team
from agno.vectordb.pgvector import PgVector, SearchType

from app.config import get_litellm_config, get_model_id
from db.session import db_url, get_postgres_db, get_session_db

# ============================================================================
# Setup
# ============================================================================
team_db = get_session_db()

# Knowledge base for documentation agent
knowledge = Knowledge(
    name="Support Knowledge Base",
    vector_db=PgVector(
        db_url=db_url,
        table_name="support_team_docs",
        search_type=SearchType.hybrid,
        embedder=OpenAIEmbedder(id="text-embedding-3-small"),
    ),
    max_results=5,
    contents_db=get_postgres_db(),
)

# ============================================================================
# Team Members
# ============================================================================
doc_agent = Agent(
    id="doc-agent",
    name="Documentation Agent",
    role="Answer questions using the knowledge base",
    knowledge=knowledge,
    search_knowledge=True,
    instructions="""\
You search the knowledge base to answer user questions.
- Provide accurate information based on documentation
- Include relevant quotes and references
- If information isn't found, say so clearly
- Suggest related topics when helpful
""",
)

escalation_agent = Agent(
    id="escalation-agent",
    name="Escalation Agent",
    role="Handle bug reports and issues requiring human attention",
    instructions="""\
You handle bug reports and escalations.
- Gather all relevant details about the issue
- Categorize the severity (critical, high, medium, low)
- Document reproduction steps if provided
- Acknowledge the report and set expectations
- Log the issue for the support team
""",
)

feedback_agent = Agent(
    id="feedback-agent",
    name="Feedback Agent",
    role="Collect and acknowledge user feedback and feature requests",
    instructions="""\
You collect user feedback and feature requests.
- Thank users for their input
- Clarify and document the feedback clearly
- Categorize as: bug, feature request, improvement, praise
- Acknowledge without promising specific timelines
- Note any context that helps prioritize
""",
)

# ============================================================================
# Create Team
# ============================================================================
support_team = Team(
    id="support-team",
    name="Support Team",
    model=LiteLLM(id=get_model_id("Support Team"), **get_litellm_config()),
    db=team_db,
    members=[doc_agent, escalation_agent, feedback_agent],
    instructions="""\
You are the support team leader responsible for routing customer inquiries.

CLASSIFICATION
--------------
Analyze each message and classify as:
- QUESTION: Product questions, how-to inquiries -> Documentation Agent
- BUG: Error reports, broken features, issues -> Escalation Agent
- FEEDBACK: Feature requests, suggestions, praise -> Feedback Agent

WORKFLOW
--------
1. Read and understand the inquiry
2. Classify the inquiry type
3. Route to the appropriate agent with context
4. Ensure the user gets a helpful response

GUIDELINES
----------
- Be empathetic and professional
- When unclear, ask for clarification
- Ensure smooth handoffs between agents
- Follow up if the first response doesn't fully address the inquiry
""",
    show_members_responses=True,
    enable_agentic_memory=True,
    markdown=True,
)

if __name__ == "__main__":
    support_team.cli_app(stream=True)
