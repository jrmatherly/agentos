"""
Content Workflow
================

A workflow that researches a topic and generates content.

Run:
    python -m agents.content_workflow
"""

from agno.agent import Agent
from agno.models.litellm import LiteLLM
from agno.tools.duckduckgo import DuckDuckGoTools
from agno.workflow.step import Step
from agno.workflow.workflow import Workflow

from app.config import get_litellm_config, get_model_id
from db.session import get_session_db

# ============================================================================
# Setup
# ============================================================================
workflow_db = get_session_db()
model = LiteLLM(id=get_model_id("Content Workflow"), **get_litellm_config())

# ============================================================================
# Workflow Agents
# ============================================================================
researcher = Agent(
    name="Content Researcher",
    model=model,
    tools=[DuckDuckGoTools()],
    instructions="""\
You are a research specialist. Your job is to:
1. Search for relevant information on the given topic
2. Gather key facts, statistics, and insights
3. Cite your sources

Output a structured research summary with:
- Key findings
- Important statistics
- Source URLs
""",
)

writer = Agent(
    name="Content Writer",
    model=model,
    instructions="""\
You are a content writer. Based on the research provided:
1. Write a clear, engaging article
2. Structure with introduction, body, and conclusion
3. Include relevant facts and statistics from the research
4. Keep paragraphs concise and readable

Write in a professional but approachable tone.
""",
)

editor = Agent(
    name="Content Editor",
    model=model,
    instructions="""\
You are an editor. Review the content and:
1. Check for clarity and flow
2. Ensure facts are properly cited
3. Polish the language and formatting
4. Add a compelling title if missing

Output the final, polished version.
""",
)

# ============================================================================
# Workflow Steps
# ============================================================================
research_step = Step(
    name="research",
    description="Research the topic and gather information",
    agent=researcher,
)

write_step = Step(
    name="write",
    description="Write content based on research",
    agent=writer,
)

edit_step = Step(
    name="edit",
    description="Edit and polish the final content",
    agent=editor,
)

# ============================================================================
# Create Workflow
# ============================================================================
content_workflow = Workflow(
    name="content-workflow",
    description="Research, write, and edit content on any topic",
    db=workflow_db,
    steps=[research_step, write_step, edit_step],
)

if __name__ == "__main__":
    content_workflow.print_response(
        input="Write an article about the future of AI agents",
        markdown=True,
    )
