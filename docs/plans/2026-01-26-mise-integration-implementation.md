# Mise Integration Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Integrate Mise-En-Place as the central development workflow tool for automatic Python/venv activation, unified task running, and structured environment management.

**Architecture:** Mise configuration in `mise.toml` defines Python 3.12 + uv as tools, auto-creates/activates `.venv`, manages environment variables with layered config (base + local secrets), and wraps existing shell scripts as tasks. Lockfile ensures reproducible tool versions.

**Tech Stack:** Mise, Python 3.12, uv, existing shell scripts

---

## Task 1: Add mise.local.toml to .gitignore

**Files:**
- Modify: `.gitignore:211-214`

**Step 1: Add mise.local.toml to gitignore**

Add after the existing Claude section at the end of `.gitignore`:

```gitignore
# Mise
mise.local.toml
```

**Step 2: Verify the change**

Run: `grep -n "mise.local.toml" .gitignore`
Expected: Line showing `mise.local.toml`

**Step 3: Commit**

```bash
git add .gitignore
git commit -m "chore: add mise.local.toml to gitignore"
```

---

## Task 2: Create mise.toml configuration

**Files:**
- Create: `mise.toml`

**Step 1: Create the mise.toml file**

```toml
# mise.toml - AgentOS Development Configuration
min_version = "2024.0.0"

[settings]
lockfile = true
experimental = true
python_venv_auto_create = true

[tools]
python = "3.12"
uv = "latest"

[env]
# Virtual environment - auto-create and activate
_.python.venv = { path = ".venv", create = true }

# Backward compatibility - load .env if it exists
_.file = [".env"]

# Database defaults (match compose.yaml)
DB_HOST = "localhost"
DB_PORT = "5432"
DB_USER = "ai"
DB_PASS = "ai"
DB_DATABASE = "ai"

# LiteLLM defaults
LITELLM_DEFAULT_MODEL = "gpt-5-mini"

# Required - mise validates this exists
LITELLM_API_KEY = { required = "Set LITELLM_API_KEY in mise.local.toml or .env" }

[tasks.setup]
description = "Install dependencies and setup development environment"
run = """
uv pip install -r requirements.txt
uv pip install -e .[dev]
"""

[tasks.format]
description = "Format code with ruff"
run = "./scripts/format.sh"
alias = "f"

[tasks.validate]
description = "Run linting and type checking"
run = "./scripts/validate.sh"
alias = "check"

[tasks.generate-requirements]
description = "Regenerate requirements.txt from pyproject.toml"
run = "./scripts/generate_requirements.sh"

[tasks."generate-requirements:upgrade"]
description = "Regenerate requirements.txt with upgrades"
run = "./scripts/generate_requirements.sh upgrade"

[tasks.build]
description = "Build Docker image"
run = "./scripts/build_image.sh"

[tasks.dev]
description = "Run development server"
run = "python -m app.main"

[tasks.load-knowledge]
description = "Load knowledge base documents"
run = "python -m agents.knowledge_agent"
```

**Step 2: Verify syntax**

Run: `mise config`
Expected: Shows loaded configuration without errors

**Step 3: Commit**

```bash
git add mise.toml
git commit -m "feat: add mise.toml for development workflow management"
```

---

## Task 3: Create mise.local.toml.example template

**Files:**
- Create: `mise.local.toml.example`

**Step 1: Create the example template**

```toml
# mise.local.toml - Local secrets and overrides
# Copy to mise.local.toml and fill in your values:
#   cp mise.local.toml.example mise.local.toml

[env]
# Required - your LiteLLM API key
LITELLM_API_KEY = "sk-your-api-key"

# Optional overrides - uncomment as needed
# LITELLM_API_BASE = "https://your-proxy.example.com"
# LITELLM_DEFAULT_MODEL = "gpt-4"
# KNOWLEDGE_AGENT_MODEL = "gpt-4"
# MCP_AGENT_MODEL = "claude-3-opus"
# REDIS_URL = "redis://localhost:6379"
```

**Step 2: Verify file exists**

Run: `cat mise.local.toml.example`
Expected: Shows the template content

**Step 3: Commit**

```bash
git add mise.local.toml.example
git commit -m "docs: add mise.local.toml.example template for secrets"
```

---

## Task 4: Generate mise.lock

**Files:**
- Create: `mise.lock` (auto-generated)

**Step 1: Install tools and generate lockfile**

Run: `mise install`
Expected: Downloads Python 3.12 and uv, creates `mise.lock`

**Step 2: Verify lockfile created**

Run: `cat mise.lock | head -20`
Expected: Shows TOML with `[tools.python]` section and version info

**Step 3: Commit**

```bash
git add mise.lock
git commit -m "chore: add mise.lock for reproducible tool versions"
```

---

## Task 5: Test mise environment activation

**Files:**
- None (verification only)

**Step 1: Leave and re-enter directory**

Run: `cd .. && cd agentos-docker`
Expected: Mise activates Python 3.12 and creates `.venv` if missing

**Step 2: Verify Python version**

Run: `python --version`
Expected: `Python 3.12.x`

**Step 3: Verify venv is active**

Run: `echo $VIRTUAL_ENV`
Expected: Path ending in `.venv`

**Step 4: Verify environment variables**

Run: `echo $DB_HOST`
Expected: `localhost`

---

## Task 6: Test mise setup task

**Files:**
- None (verification only)

**Step 1: Create mise.local.toml with test key**

Run: `cp mise.local.toml.example mise.local.toml`
Then edit `mise.local.toml` to add your actual API key.

**Step 2: Run setup task**

Run: `mise run setup`
Expected: Installs dependencies from requirements.txt and dev dependencies

**Step 3: Verify installation**

Run: `python -c "import agno; print(agno.__version__)"`
Expected: Shows agno version (e.g., `2.4.0`)

---

## Task 7: Test all mise tasks

**Files:**
- None (verification only)

**Step 1: List available tasks**

Run: `mise tasks`
Expected: Shows all 8 tasks with descriptions

**Step 2: Test format task**

Run: `mise run format`
Expected: Runs ruff format successfully

**Step 3: Test validate task**

Run: `mise run validate`
Expected: Runs ruff check and mypy successfully

**Step 4: Test dev task**

Run: `mise run dev` (then Ctrl+C to stop)
Expected: Starts uvicorn server on port 8000

---

## Task 8: Update CLAUDE.md with mise commands

**Files:**
- Modify: `CLAUDE.md:9-69`

**Step 1: Update the Commands section**

Replace the entire `## Commands` section with:

```markdown
## Commands

### Development (with mise)

```bash
# First-time setup (after mise is installed)
mise run setup

# Run development server
mise run dev

# Format code
mise run format

# Validate (lint + type check)
mise run validate

# Regenerate requirements.txt
mise run generate-requirements
mise run generate-requirements:upgrade  # with upgrades
```

### Development (without mise)

```bash
# Setup local environment
./scripts/venv_setup.sh && source .venv/bin/activate

# Run locally (requires DB)
python -m app.main

# Start database only
docker compose up -d agentos-db

# Start with Redis
docker compose --profile redis up -d agentos-db agentos-redis
```

### Docker

```bash
# Start all services
docker compose up -d --build

# Start with Redis profile
docker compose --profile redis up -d --build

# View logs
docker compose logs -f

# Load knowledge base
docker exec -it agentos-api python -m agents.knowledge_agent
```

### Code Quality

```bash
# With mise
mise run format      # Format code
mise run validate    # Lint + type check

# Without mise
./scripts/format.sh
./scripts/validate.sh
ruff format .
ruff check .
mypy . --config-file pyproject.toml
```

### Dependencies

```bash
# With mise
mise run generate-requirements
mise run generate-requirements:upgrade

# Without mise
./scripts/generate_requirements.sh
./scripts/generate_requirements.sh upgrade
```
```

**Step 2: Verify the update**

Run: `grep -A 5 "mise run setup" CLAUDE.md`
Expected: Shows the mise setup command

**Step 3: Commit**

```bash
git add CLAUDE.md
git commit -m "docs: update CLAUDE.md with mise commands"
```

---

## Task 9: Update README.md Local Development section

**Files:**
- Modify: `README.md:91-121`

**Step 1: Update Local Development section**

Replace the `## Local Development` section with:

```markdown
## Local Development

For development without Docker:

### Option A: With mise (recommended)

```sh
# Install mise (one-time)
curl https://mise.run | sh
echo 'eval "$(mise activate zsh)"' >> ~/.zshrc  # or ~/.bashrc
source ~/.zshrc

# Enter project - Python 3.12 + venv auto-activated
cd agentos-docker

# Configure secrets
cp mise.local.toml.example mise.local.toml
# Edit mise.local.toml with your LITELLM_API_KEY

# Install dependencies
mise run setup

# Start development server
mise run dev
```

### Option B: Manual setup

```sh
# Install uv
curl -LsSf https://astral.sh/uv/install.sh | sh

# Setup environment
./scripts/venv_setup.sh
source .venv/bin/activate

# Configure secrets
cp example.env .env
# Edit .env with your LITELLM_API_KEY

# Run server
python -m app.main
```

### Add dependencies

1. Edit `pyproject.toml`
2. Regenerate requirements:

```sh
mise run generate-requirements  # or ./scripts/generate_requirements.sh
```

3. Rebuild:

```sh
docker compose up -d --build
```
```

**Step 2: Verify the update**

Run: `grep -A 3 "mise run setup" README.md`
Expected: Shows mise setup instructions

**Step 3: Commit**

```bash
git add README.md
git commit -m "docs: update README with mise development workflow"
```

---

## Task 10: Update DEVELOPER_GUIDE.md

**Files:**
- Modify: `docs/guides/DEVELOPER_GUIDE.md:1-50`

**Step 1: Add mise section after Prerequisites**

Insert after the `### Prerequisites` section (around line 18):

```markdown
### Setup with mise (recommended)

[mise](https://mise.jdx.dev/) provides automatic Python version management and virtual environment activation.

```bash
# Install mise (one-time)
curl https://mise.run | sh
echo 'eval "$(mise activate zsh)"' >> ~/.zshrc  # or bash
source ~/.zshrc

# Clone and enter project
git clone https://github.com/agno-agi/agentos-docker-template.git
cd agentos-docker
# → Python 3.12 + venv auto-activated

# Configure secrets
cp mise.local.toml.example mise.local.toml
# Edit mise.local.toml with your LITELLM_API_KEY

# Install dependencies
mise run setup
```

Available tasks: `mise tasks`

| Command | Description |
|---------|-------------|
| `mise run setup` | Install all dependencies |
| `mise run dev` | Start development server |
| `mise run format` | Format code with ruff |
| `mise run validate` | Run linting + type checking |
| `mise run generate-requirements` | Regenerate requirements.txt |

### Setup without mise
```

**Step 2: Rename existing "Install uv" section**

Change `### Install uv` to be under the new `### Setup without mise` heading.

**Step 3: Commit**

```bash
git add docs/guides/DEVELOPER_GUIDE.md
git commit -m "docs: add mise setup instructions to DEVELOPER_GUIDE"
```

---

## Task 11: Final verification and summary commit

**Files:**
- None (verification only)

**Step 1: Verify all files exist**

Run: `ls -la mise.toml mise.local.toml.example mise.lock`
Expected: All three files exist

**Step 2: Verify mise tasks work**

Run: `mise tasks`
Expected: Lists all 8 tasks

**Step 3: Verify environment**

Run: `mise doctor`
Expected: No errors

**Step 4: Check git status**

Run: `git status`
Expected: Clean working tree (nothing to commit)

**Step 5: View commit history**

Run: `git log --oneline -10`
Expected: Shows all mise-related commits

---

## Task 12: Update Serena memory - suggested_commands

**Files:**
- Modify: `.serena/memories/suggested_commands.md`

**Step 1: Add mise section at the top of Development section**

Insert after `## Development (Without Docker)` header, add new section before it:

```markdown
## Development (With mise - Recommended)

### First-Time Setup
```sh
# Install mise (one-time)
curl https://mise.run | sh
echo 'eval "$(mise activate zsh)"' >> ~/.zshrc  # or bash
source ~/.zshrc

# Enter project (auto-activates Python + venv)
cd agentos-docker

# Configure secrets
cp mise.local.toml.example mise.local.toml
# Edit mise.local.toml with your LITELLM_API_KEY

# Install dependencies
mise run setup
```

### Common Tasks
```sh
mise tasks                          # List all available tasks
mise run dev                        # Start development server
mise run format                     # Format code
mise run validate                   # Lint + type check
mise run generate-requirements      # Regenerate requirements.txt
mise run generate-requirements:upgrade  # Upgrade dependencies
mise run build                      # Build Docker image
mise run load-knowledge             # Load knowledge base
```

## Development (Without mise)
```

**Step 2: Commit**

```bash
git add .serena/memories/suggested_commands.md
git commit -m "docs: add mise commands to Serena suggested_commands memory"
```

---

## Task 13: Update Serena memory - project_overview

**Files:**
- Modify: `.serena/memories/project_overview.md`

**Step 1: Add mise to Tech Stack table**

In the Tech Stack table, add a row for mise:

```markdown
| Dev Tools | mise | Development workflow management |
```

**Step 2: Add mise.toml to File Structure**

In the File Structure section, add:

```markdown
├── mise.toml             # Development workflow config
├── mise.local.toml.example  # Secrets template
├── mise.lock             # Locked tool versions
```

**Step 3: Commit**

```bash
git add .serena/memories/project_overview.md
git commit -m "docs: add mise to Serena project_overview memory"
```

---

## Task 14: Update docs/guides/GETTING_STARTED.md

**Files:**
- Modify: `docs/guides/GETTING_STARTED.md`

**Step 1: Add mise quick start option after "Quick Start (5 minutes)" header**

Insert after line 14 (after the "Quick Start" section header):

```markdown
> **Tip:** For local development, we recommend using [mise](https://mise.jdx.dev/) for automatic Python/venv management. See [Developer Guide](./DEVELOPER_GUIDE.md) for mise setup.
```

**Step 2: Update Common Commands table**

Add mise equivalents to the table at line ~192:

```markdown
| Format code | `mise run format` |
| Validate code | `mise run validate` |
| Run dev server (local) | `mise run dev` |
```

**Step 3: Commit**

```bash
git add docs/guides/GETTING_STARTED.md
git commit -m "docs: add mise references to GETTING_STARTED guide"
```

---

## Task 15: Update docs/guides/CREATING_AGENTS.md

**Files:**
- Modify: `docs/guides/CREATING_AGENTS.md`

**Step 1: Update restart command**

At line 65, change:

```bash
docker compose restart
```

To:

```bash
# With Docker
docker compose restart

# Local development (with mise)
# Server auto-reloads on file changes
```

**Step 2: Update CLI testing command**

At line 391, add mise alternative:

```bash
# With Docker
docker exec -it agentos-api python -m agents.my_agent

# Local development (with mise)
python -m agents.my_agent
```

**Step 3: Commit**

```bash
git add docs/guides/CREATING_AGENTS.md
git commit -m "docs: add mise alternatives to CREATING_AGENTS guide"
```

---

## Task 16: Update docs/architecture/ARCHITECTURE.md

**Files:**
- Modify: `docs/architecture/ARCHITECTURE.md`

**Step 1: Add mise to Technology Stack table**

In the Technology Stack table (around line 330), add:

```markdown
| Dev Workflow | mise | Python/venv/task management |
```

**Step 2: Commit**

```bash
git add docs/architecture/ARCHITECTURE.md
git commit -m "docs: add mise to ARCHITECTURE technology stack"
```

---

## Task 17: Final verification and summary commit

**Files:**
- None (verification only)

**Step 1: Verify all files exist**

Run: `ls -la mise.toml mise.local.toml.example mise.lock`
Expected: All three files exist

**Step 2: Verify mise tasks work**

Run: `mise tasks`
Expected: Lists all 8 tasks

**Step 3: Verify environment**

Run: `mise doctor`
Expected: No errors

**Step 4: Check git status**

Run: `git status`
Expected: Clean working tree (nothing to commit)

**Step 5: View commit history**

Run: `git log --oneline -15`
Expected: Shows all mise-related commits

---

## Summary

After completing all tasks, the project will have:

| File | Purpose |
|------|---------|
| `mise.toml` | Main configuration (tools, env, tasks) |
| `mise.local.toml.example` | Template for secrets |
| `mise.lock` | Locked tool versions |
| Updated `.gitignore` | Ignores `mise.local.toml` |
| Updated `CLAUDE.md` | Mise commands documented |
| Updated `README.md` | Mise quickstart added |
| Updated `docs/guides/DEVELOPER_GUIDE.md` | Full mise setup guide |
| Updated `docs/guides/GETTING_STARTED.md` | Mise tip and commands |
| Updated `docs/guides/CREATING_AGENTS.md` | Mise alternatives for testing |
| Updated `docs/architecture/ARCHITECTURE.md` | Mise in tech stack |
| Updated `.serena/memories/suggested_commands.md` | Mise commands for AI assistants |
| Updated `.serena/memories/project_overview.md` | Mise in project overview |

Developer workflow becomes:
1. Install mise (one-time)
2. `cd agentos-docker` → auto Python + venv
3. `cp mise.local.toml.example mise.local.toml` + add API key
4. `mise run setup` → dependencies installed
5. `mise run dev` → server running
