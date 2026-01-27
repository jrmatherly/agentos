# Mise Integration Design

Integrate Mise-En-Place as the central development workflow tool for AgentOS.

## Goals

1. **Developer Experience** - Automatic Python/venv activation when entering the project
2. **Task Standardization** - Unified task runner (`mise run <task>`)
3. **Environment Management** - Structured env var handling with secrets separation

## Configuration Files

```
agentos-docker/
├── mise.toml             # Main config (committed)
├── mise.local.toml       # Local secrets (gitignored)
├── mise.lock             # Tool version lockfile (committed)
├── mise.local.toml.example  # Template for secrets
└── .mise/
    └── tasks/            # Future: standalone task files
```

### mise.toml (Complete Configuration)

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
# Virtual environment
_.python.venv = { path = ".venv", create = true }
_.file = [".env"]  # Backward compatibility

# Database defaults
DB_HOST = "localhost"
DB_PORT = "5432"
DB_USER = "ai"
DB_PASS = "ai"
DB_DATABASE = "ai"

# LiteLLM defaults
LITELLM_DEFAULT_MODEL = "gpt-5-mini"
LITELLM_API_KEY = { required = "Set LITELLM_API_KEY in mise.local.toml" }

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
description = "Regenerate requirements.txt"
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

### mise.local.toml.example

```toml
# mise.local.toml - Local secrets and overrides
# Copy to mise.local.toml and fill in your values

[env]
LITELLM_API_KEY = "sk-your-api-key"

# Optional overrides
# LITELLM_API_BASE = "https://your-proxy.example.com"
# LITELLM_DEFAULT_MODEL = "gpt-4"
# KNOWLEDGE_AGENT_MODEL = "gpt-4"
# MCP_AGENT_MODEL = "claude-3-opus"
# REDIS_URL = "redis://localhost:6379"
```

## How It Works

### Python Environment

1. Developer runs `cd agentos-docker`
2. Mise activates automatically (requires shell integration)
3. Python 3.12 installed if missing
4. `.venv` created if missing
5. Venv activated (PATH prepended, VIRTUAL_ENV set)

### Environment Variables

- **mise.toml**: Non-sensitive defaults (committed)
- **mise.local.toml**: Secrets and overrides (gitignored)
- **Layered**: Local values override base values
- **Validation**: Required variables fail fast with helpful messages
- **Backward compatible**: `.env` files still loaded during transition

### Tasks

| Command | Description |
|---------|-------------|
| `mise run setup` | Install dependencies |
| `mise run format` | Format code with ruff |
| `mise run validate` | Run linting + type checking |
| `mise run dev` | Start development server |
| `mise run build` | Build Docker image |
| `mise run load-knowledge` | Load knowledge base |
| `mise run generate-requirements` | Regenerate requirements.txt |
| `mise run generate-requirements:upgrade` | Upgrade all dependencies |

### Lockfile

- `mise.lock` pins exact tool versions with checksums
- Commit to repo for reproducible environments
- Regenerated on `mise install` when tools change

## MCP Server Integration

Mise exposes an MCP server for AI assistant integration.

**Claude Code configuration** (`~/.config/claude/claude_desktop_config.json`):

```json
{
  "mcpServers": {
    "mise": {
      "command": "mise",
      "args": ["mcp"],
      "env": {
        "MISE_EXPERIMENTAL": "1"
      }
    }
  }
}
```

**Available resources:**
- `mise://tasks` - List available tasks
- `mise://tools` - Installed tools and versions
- `mise://env` - Environment variables

## Migration Plan

### New Files

| File | Purpose |
|------|---------|
| `mise.toml` | Main configuration |
| `mise.local.toml.example` | Template for secrets |

### Modified Files

| File | Change |
|------|--------|
| `.gitignore` | Add `mise.local.toml` |
| `CLAUDE.md` | Update commands with mise equivalents |
| `README.md` | Update quickstart |
| `docs/guides/DEVELOPER_GUIDE.md` | Add mise setup instructions |

### Unchanged (During Transition)

| File | Reason |
|------|--------|
| `scripts/*.sh` | Tasks reference them; migrate later |
| `example.env` | Documentation + backward compatibility |

## Developer Onboarding

```bash
# 1. Install mise (one-time)
curl https://mise.run | sh
echo 'eval "$(mise activate zsh)"' >> ~/.zshrc
source ~/.zshrc

# 2. Clone and enter project
git clone <repo> && cd agentos-docker
# → Python 3.12 + venv auto-activated

# 3. Configure secrets
cp mise.local.toml.example mise.local.toml
# Edit mise.local.toml with your API key

# 4. Install dependencies
mise run setup

# 5. Start developing
mise run dev
```

## Future Migration Path

Once mise is established, consider:

1. **Move script logic into tasks** - Replace `run = "./scripts/format.sh"` with inline commands
2. **Remove scripts/ directory** - After all logic migrated
3. **Add file-based tasks** - Complex tasks in `.mise/tasks/` with shebangs
4. **Add hooks** - `enter` hook for welcome message or dependency check
5. **Environment profiles** - `mise.staging.toml` if staging environment needed
