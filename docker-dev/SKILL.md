---
name: docker-dev
description: Route all Python, testing, and development commands through local
  Docker infrastructure when a docker-compose.yml file exists in the project.
---

# Docker Development Environment

## Rule

When a `docker-compose.yml` or `docker-compose.yaml` file exists at the project root (or any parent directory up to the repo root), **all runtime commands MUST execute inside the appropriate Docker container**. This applies to:

- **Python**: `python`, `python3`, `pip`, `uv`, any Python script execution
- **Testing**: `pytest`, `unittest`, `tox`, `nox`, `coverage`
- **Django**: `manage.py` commands, `django-admin`
- **Linting/Formatting**: `ruff`, `black`, `isort`, `flake8`, `mypy`, `pylint`
- **Package management**: `pip install`, `uv add`, `uv sync`, `poetry install`
- **Database**: `psql`, migrations, seed scripts
- **Any other dev tooling** defined in the compose services

## How to Execute

1. **Check for compose file** before running any development command. Look for `docker-compose.yml`, `docker-compose.yaml`, or `compose.yml` in the working directory or repo root.

2. **Identify the correct service**. Read the compose file to determine which service runs the relevant tool. Common patterns:
   - A service named `app`, `web`, `backend`, `api`, or `django` for Python/Django commands
   - A service named `db`, `postgres`, `mysql` for database commands
   - If unclear, check which service mounts the source code or has Python installed

3. **Use `docker compose exec`** for commands when containers are running:
   ```bash
   docker compose exec <service> <command>
   ```

4. **Use `docker compose run --rm`** if the service is not already running:
   ```bash
   docker compose run --rm <service> <command>
   ```

5. **Preserve working directory context** when the compose file sets a `working_dir` or mounts code to a specific path. Use `-w` flag if needed:
   ```bash
   docker compose exec -w /app <service> pytest tests/
   ```

## Examples

```bash
# Instead of: pytest
docker compose exec app pytest

# Instead of: python manage.py migrate
docker compose exec app python manage.py migrate

# Instead of: ruff check .
docker compose exec app ruff check .

# Instead of: uv add requests
docker compose exec app uv add requests

# Instead of: python scripts/seed_data.py
docker compose exec app python scripts/seed_data.py
```

## Exceptions

Do **NOT** route through Docker:
- `git` commands — always run on host
- File editing/reading — use your tools directly
- `docker` and `docker compose` commands themselves — these manage the infrastructure
- Commands the user explicitly asks to run on the host
- Build steps like `docker compose build` or `docker compose up`

## When Containers Are Not Running

If `docker compose exec` fails because the container is not running:
1. Inform the user that the containers appear to be down
2. Ask if they want you to start them with `docker compose up -d`
3. Once confirmed and started, proceed with the original command
