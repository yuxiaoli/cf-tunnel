# Repository Guidelines

## Project Structure & Module Organization

This is a Python 3.11+ project using a `src/` layout. Application code lives in `src/cftui/`: `cli.py` defines Typer commands, `config.py` loads `.env` settings, `cloudflared.py` manages the subprocess lifecycle, `cloudflare_api.py` scaffolds managed tunnel API work, and `tui/` contains Textual UI components. Tests live in `tests/`. Keep reference material in `refs/`, design notes in `docs/`, automation in `scripts/`, and temporary output in `temp/`.

## Build, Test, and Development Commands

Use `uv` when possible:

```powershell
uv sync --extra dev
uv run cftui version
uv run cftui share --port 3000
uv run pytest
uv run ruff check .
uv run ruff format .
```

`pytest` runs the unit suite. `ruff check` reports lint issues, and `ruff format` applies formatting.

## Coding Style & Naming Conventions

Use 4-space indentation, type hints for public functions, and small modules with explicit responsibilities. Prefer `snake_case` for functions, variables, and module names; use `PascalCase` for classes and enums. Keep asynchronous tunnel process code in `cloudflared.py` and UI-specific behavior in `tui/`.

## Testing Guidelines

Tests use `pytest` and should be named `test_*.py`. Add parser tests for cloudflared log handling and config tests for environment behavior. Avoid starting real tunnels in unit tests; mock subprocess behavior for future runner tests.

## Commit & Pull Request Guidelines

The current history uses conventional-style messages such as `chore: initial commit for branch setup`. Continue with short imperative subjects like `feat: add quick tunnel runner` or `fix: handle missing cloudflared`. Pull requests should include a concise description, test results, linked issues when relevant, and terminal screenshots or recordings for TUI changes.

## Security & Configuration Tips

Never commit `.env`; document settings in `.env.example` only. Quick Tunnel mode must not require Cloudflare credentials. Managed tunnel operations must validate `CLOUDFLARE_API_TOKEN` and `CLOUDFLARE_ACCOUNT_ID`, and logs must not print raw tokens.
