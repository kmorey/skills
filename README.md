# Skills

Personal agent skills maintained by Kevin Morey.

## Development

Install [`uv`](https://docs.astral.sh/uv/), then run the repository checks from
the project root:

```bash
uv sync --locked
uv run --locked ruff check .
uv run --locked ruff format --check .
uv run --locked pytest
```

`pyproject.toml` defines the supported Python versions, test discovery, and
development tools. `uv.lock` pins the complete tool environment used locally
and in CI.
