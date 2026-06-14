# cftui

`cftui` is a developer-focused Cloudflare Tunnel manager with a Textual TUI. It exposes local HTTP services through `cloudflared`, shows the generated public URL, streams logs in real time, and provides start, stop, restart, and copy actions from the terminal.

The MVP fully supports Cloudflare Quick Tunnel mode. Managed persistent tunnels with custom hostnames are scaffolded for future Cloudflare API integration.

## Requirements

- Python 3.11+
- `uv` recommended for dependency management
- `cloudflared` installed and available on `PATH`

Install `cloudflared` from Cloudflare's package instructions, or use a platform package manager such as:

```powershell
winget install Cloudflare.cloudflared
```

## Installation

```powershell
uv sync --extra dev
```

If you are not using `uv`, install the project in editable mode:

```powershell
python -m pip install -e ".[dev]"
```

## Configuration

Copy `.env.example` to `.env` and adjust local values:

```env
CLOUDFLARE_API_TOKEN=
CLOUDFLARE_ACCOUNT_ID=
CLOUDFLARE_ZONE_ID=
CLOUDFLARE_DEFAULT_DOMAIN=
CLOUDFLARED_BIN=cloudflared
LOG_LEVEL=INFO
```

Quick Tunnel mode does not require Cloudflare API credentials. Managed mode requires `CLOUDFLARE_API_TOKEN` and `CLOUDFLARE_ACCOUNT_ID`.

## Quick Tunnel Usage

Expose a local port:

```powershell
cftui share --port 3000
```

Or expose a full local URL:

```powershell
cftui share --url http://localhost:3000
```

The TUI shows:

```text
Local URL:  http://localhost:3000
Public URL: https://example.trycloudflare.com
Status:     running

q quit | r restart | c copy URL | s stop
```

Quick Tunnel URLs are public. Do not expose admin panels, private data, or unauthenticated internal services.

## Managed Tunnel Roadmap

The `publish` command validates managed-mode configuration and captures the intended interface:

```powershell
cftui publish --name my-api --hostname api.example.com --port 3000
```

Future work will create or reuse named tunnels, configure public hostnames, update DNS routes, run token-based tunnels, and support Cloudflare Access protection.

## Development

```powershell
uv sync --extra dev
uv run pytest
uv run ruff check .
uv run ruff format .
uv run cftui version
```

## Security Notes

Never commit `.env` or API tokens. The application masks configured sensitive values in streamed logs and does not require credentials for Quick Tunnel mode.
