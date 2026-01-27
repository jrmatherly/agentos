# Code Style Guide

## Tools
- **Formatter**: ruff (line length: 120)
- **Linter**: ruff
- **Type Checker**: mypy (strict mode)

## Formatting Rules
- Line length: 120 characters
- Run `./scripts/format.sh` before committing
- Import sorting: isort via `ruff check --select I --fix`

## Type Annotations
- All functions require type hints
- Use `from __future__ import annotations` for forward references
- mypy runs in strict mode (`check_untyped_defs`, `no_implicit_optional`)

## File Structure Patterns

### Module Docstrings
Every module starts with a docstring:
```python
"""
Module Name
===========

Brief description.

Run:
    python -m module.name
"""
```

### Section Comments
Use section dividers for logical groupings:
```python
# ============================================================================
# Section Name
# ============================================================================
```

### Agent Definition Pattern
```python
from agno.agent import Agent
from agno.models.litellm import LiteLLM
from db.session import get_postgres_db

# Setup
agent_db = get_postgres_db()

# Instructions (multiline string)
instructions = """\
You are...

WORKFLOW
--------
1. Step one
2. Step two

GUIDELINES
----------
- Guideline one
- Guideline two
"""

# Create Agent
my_agent = Agent(
    name="My Agent",
    model=LiteLLM(id="gpt-5-mini"),
    db=agent_db,
    instructions=instructions,
    enable_agentic_memory=True,
    add_datetime_to_context=True,
    add_history_to_context=True,
    num_history_runs=5,
    markdown=True,
)
```

### Database Pattern
```python
from db.session import db_url, get_postgres_db

# For agents
agent_db = get_postgres_db()

# For raw SQLAlchemy
from db.session import SessionLocal
with SessionLocal() as session:
    # use session
```

## Imports
- `__init__.py` files may have F401/F403 ignores for re-exports
- Group imports: stdlib, third-party, local
- Prefer explicit imports over star imports (except `__init__.py`)

## Naming Conventions
| Type | Convention | Example |
|------|------------|---------|
| Modules | snake_case | `knowledge_agent.py` |
| Classes | PascalCase | `PostgresDb` |
| Functions | snake_case | `get_db_url()` |
| Variables | snake_case | `agent_db` |
| Constants | UPPER_SNAKE | `DB_HOST` |
| Agents | snake_case suffix | `knowledge_agent` |

## Error Handling
- Use explicit exception types
- Don't silence exceptions without logging
- Use `contextlib.suppress()` for intentional ignores

## Validation Checklist
Before committing:
1. `./scripts/format.sh` - no changes needed
2. `ruff check .` - no errors
3. `mypy . --config-file pyproject.toml` - no errors
