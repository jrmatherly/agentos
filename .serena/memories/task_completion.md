# Task Completion Checklist

When completing a coding task, run these checks:

## 1. Format Code
```sh
./scripts/format.sh
```
Or manually:
```sh
ruff format .
ruff check --select I --fix .
```

## 2. Validate Code
```sh
./scripts/validate.sh
```
Or manually:
```sh
ruff check .
mypy . --config-file pyproject.toml
```

## 3. Test Changes (if Docker is running)
```sh
docker compose restart
# Check logs for errors
docker compose logs -f
```

## 4. If Dependencies Changed
1. Update `pyproject.toml`
2. Run: `./scripts/generate_requirements.sh`
3. Rebuild: `docker compose up -d --build`

## Pre-commit Checklist
- [ ] Code formatted (`./scripts/format.sh`)
- [ ] No linting errors (`ruff check .`)
- [ ] No type errors (`mypy . --config-file pyproject.toml`)
- [ ] App starts without errors (if testable)
- [ ] Dependencies updated if needed
