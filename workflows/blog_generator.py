"""
Blog Generator Workflow
=======================

Advanced async workflow with caching and Pydantic output schemas.

Run:
    python -m workflows.blog_generator
"""

import asyncio
import json
from textwrap import dedent
from typing import Optional

from agno.agent import Agent
from agno.models.litellm import LiteLLM
from agno.tools.duckduckgo import DuckDuckGoTools
from agno.tools.newspaper4k import Newspaper4kTools
from agno.workflow.workflow import Workflow
from pydantic import BaseModel, Field

from app.config import get_litellm_config, get_model_id
from db.session import get_session_db

# ============================================================================
# Response Schemas
# ============================================================================


class NewsArticle(BaseModel):
    title: str = Field(description="Title of the article")
    url: str = Field(description="URL of the article")
    summary: Optional[str] = Field(default=None, description="Brief summary if available")


class SearchResults(BaseModel):
    articles: list[NewsArticle] = Field(description="List of found articles")


class ScrapedArticle(BaseModel):
    title: str = Field(description="Article title")
    url: str = Field(description="Article URL")
    content: Optional[str] = Field(default=None, description="Full article content in markdown")


# ============================================================================
# Setup
# ============================================================================
workflow_db = get_session_db()
model = LiteLLM(id=get_model_id("Blog Generator"), **get_litellm_config())

# ============================================================================
# Workflow Agents
# ============================================================================
research_agent = Agent(
    name="Blog Research Agent",
    model=model,
    tools=[DuckDuckGoTools()],
    output_schema=SearchResults,
    instructions=dedent("""\
        You find high-quality sources for blog content.
        - Search for 5-7 authoritative, recent sources
        - Evaluate credibility and relevance
        - Return structured results with titles, URLs, and summaries
    """),
)

scraper_agent = Agent(
    name="Content Scraper Agent",
    model=model,
    tools=[Newspaper4kTools()],
    output_schema=ScrapedArticle,
    instructions=dedent("""\
        You extract article content from URLs.
        - Extract the full article text
        - Preserve important quotes and statistics
        - Format content in clean markdown
    """),
)

writer_agent = Agent(
    name="Blog Writer Agent",
    model=model,
    instructions=dedent("""\
        You write engaging, well-researched blog posts.

        STRUCTURE
        ---------
        # {Viral-Worthy Headline}

        ## Introduction
        {Engaging hook and context}

        ## {Main Section 1}
        {Key insights with evidence}

        ## {Main Section 2}
        {Deeper exploration}

        ## Key Takeaways
        - {Takeaway 1}
        - {Takeaway 2}
        - {Takeaway 3}

        ## Sources
        {Attributed sources with links}

        GUIDELINES
        ----------
        - Write in a professional but approachable tone
        - Include statistics and quotes from sources
        - Optimize for readability and SEO
        - Always cite sources
    """),
    markdown=True,
)


# ============================================================================
# Caching Helpers
# ============================================================================
def get_cached(session_state: dict, key: str, topic: str):
    """Get cached value from session state."""
    return session_state.get(key, {}).get(topic)


def set_cached(session_state: dict, key: str, topic: str, value):
    """Set cached value in session state."""
    if key not in session_state:
        session_state[key] = {}
    session_state[key][topic] = value


# ============================================================================
# Workflow Execution
# ============================================================================
async def blog_generation(
    session_state: dict,
    topic: str,
    use_cache: bool = True,
) -> str:
    """
    Generate a blog post through research, scraping, and writing phases.

    Args:
        session_state: Shared state for caching
        topic: The blog topic to write about
        use_cache: Whether to use cached results
    """
    print(f"Generating blog post about: {topic}")
    print("=" * 60)

    # Check for cached blog post
    if use_cache:
        cached_blog = get_cached(session_state, "blog_posts", topic)
        if cached_blog:
            print("Found cached blog post!")
            return cached_blog

    # Phase 1: Research
    print("\nPHASE 1: RESEARCH")
    print("-" * 40)

    cached_search = get_cached(session_state, "search_results", topic) if use_cache else None
    if cached_search:
        print("Using cached search results")
        search_results = SearchResults.model_validate(cached_search)
    else:
        print(f"Searching for articles about: {topic}")
        response = await research_agent.arun(f"Find articles about: {topic}")
        if not response or not response.content:
            return f"Could not find articles about: {topic}"
        search_results = response.content
        set_cached(session_state, "search_results", topic, search_results.model_dump())

    print(f"Found {len(search_results.articles)} articles")

    # Phase 2: Scrape articles (parallel)
    print("\nPHASE 2: CONTENT EXTRACTION")
    print("-" * 40)

    cached_articles = get_cached(session_state, "scraped_articles", topic) if use_cache else None
    if cached_articles:
        print("Using cached scraped articles")
        scraped_articles = [ScrapedArticle.model_validate(a) for a in cached_articles]
    else:
        print(f"Scraping {len(search_results.articles)} articles...")
        tasks = [scraper_agent.arun(article.url) for article in search_results.articles]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        scraped_articles = []
        for result in results:
            if isinstance(result, BaseException):
                continue
            if result and result.content:
                scraped_articles.append(result.content)

        set_cached(
            session_state,
            "scraped_articles",
            topic,
            [a.model_dump() for a in scraped_articles],
        )

    print(f"Successfully scraped {len(scraped_articles)} articles")

    if not scraped_articles:
        return f"Could not extract content for: {topic}"

    # Phase 3: Write blog post
    print("\nPHASE 3: WRITING")
    print("-" * 40)

    writer_input = {
        "topic": topic,
        "articles": [a.model_dump() for a in scraped_articles],
    }

    print("Writing blog post...")
    response = await writer_agent.arun(json.dumps(writer_input, indent=2))

    if not response or not response.content:
        return f"Could not generate blog post for: {topic}"

    blog_post = response.content
    set_cached(session_state, "blog_posts", topic, blog_post)

    print("Blog post generated successfully!")
    return blog_post


# ============================================================================
# Create Workflow
# ============================================================================
blog_workflow = Workflow(
    name="Blog Generator",
    description="Research, scrape, and write blog posts with caching",
    db=workflow_db,
)

if __name__ == "__main__":

    async def main():
        topic = "The future of AI agents in enterprise software"
        session_state: dict = {}
        result = await blog_generation(session_state, topic=topic, use_cache=True)
        print("\n" + "=" * 60)
        print("GENERATED BLOG POST")
        print("=" * 60)
        print(result)

    asyncio.run(main())
