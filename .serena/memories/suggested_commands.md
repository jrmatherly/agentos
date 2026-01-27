# Suggested Commands

## Docker Operations (Primary)

### Start Stack
```sh
docker compose up -d --build
```

### Start Stack with Redis (Optional)
```sh
docker compose --profile redis up -d --build
```

### Stop Stack
```sh
docker compose down
```

### View Logs
```sh
docker compose logs -f
docker compose logs -f agentos-api    # API only
docker compose logs -f agentos-db     # DB only
docker compose logs -f agentos-redis  # Redis only (if started with --profile redis)
```

### Restart After Code Changes
```sh
docker compose restart
```

### Rebuild After Dependency Changes
```sh
docker compose up -d --build
```

### Load Knowledge Base
```sh
docker exec -it agentos-api python -m agents.knowledge_agent
```

### Run MCP Agent CLI
```sh
docker exec -it agentos-api python -m agents.mcp_agent
```

### Database Shell
```sh
docker exec -it agentos-db psql -U ai -d ai
```

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

### Release & Publishing
```sh
mise run release                    # Interactive release (prompts for version)
mise run release:patch              # Auto-increment patch (v0.1.0 → v0.1.1)
mise run release:minor              # Auto-increment minor (v0.1.0 → v0.2.0)
mise run release:major              # Auto-increment major (v0.1.0 → v1.0.0)
gh release list                     # View releases
gh run list --workflow=docker-images.yml  # Check workflow status
```

## Development (Without mise)

### Setup Virtual Environment
```sh
./scripts/venv_setup.sh
source .venv/bin/activate
```

### Format Code
```sh
./scripts/format.sh
# Or manually:
ruff format .
ruff check --select I --fix .
```

### Validate Code
```sh
./scripts/validate.sh
# Or manually:
ruff check .
mypy . --config-file pyproject.toml
```

### Add Dependencies
```sh
# 1. Edit pyproject.toml
# 2. Regenerate requirements:
./scripts/generate_requirements.sh
# 3. Rebuild container:
docker compose up -d --build
```

### Run Locally (requires local PostgreSQL)
```sh
cp example.env .env
# Edit .env with your settings
python -m app.main
```

## CI/CD

### Manual Image Build
```sh
./scripts/build_image.sh
```

### Trigger Release Build
Create a GitHub release to trigger `docker-images.yml` workflow.

## Troubleshooting

### Reset Database
```sh
docker compose down -v
docker compose up -d --build
```

### Check Container Status
```sh
docker compose ps
```

### Enter Container Shell
```sh
docker exec -it agentos-api bash
```
