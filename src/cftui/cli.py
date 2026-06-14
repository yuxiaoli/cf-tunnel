from __future__ import annotations

from typing import Annotated

import typer
from rich.console import Console

from . import __version__
from .cloudflared import CloudflaredRunner
from .config import ManagedConfigError, load_settings
from .models import ManagedTunnelRequest
from .tui.app import TunnelApp

app = typer.Typer(help="Cloudflare Tunnel manager with a Textual TUI.")
console = Console()


def _local_url(port: int | None, url: str | None) -> str:
    if port is None and url is None:
        raise typer.BadParameter("Provide either --port or --url.")
    if port is not None and url is not None:
        raise typer.BadParameter("Use either --port or --url, not both.")
    return url or f"http://localhost:{port}"


@app.command()
def share(
    port: Annotated[
        int | None,
        typer.Option("--port", "-p", min=1, max=65535, help="Local HTTP port to expose."),
    ] = None,
    url: Annotated[
        str | None,
        typer.Option("--url", "-u", help="Full local origin URL to expose."),
    ] = None,
) -> None:
    """Expose a local service through a Cloudflare Quick Tunnel."""
    settings = load_settings()
    local_url = _local_url(port, url)
    console.print("[yellow]Quick Tunnel URLs are public. Do not expose sensitive services.[/]")
    runner = CloudflaredRunner(
        local_url,
        cloudflared_bin=settings.cloudflared_bin,
        log_level=settings.log_level,
        sensitive_values=[settings.cloudflare_api_token],
    )
    TunnelApp(runner).run()


@app.command()
def publish(
    name: Annotated[str, typer.Option("--name", "-n", help="Cloudflare tunnel name.")],
    hostname: Annotated[
        str,
        typer.Option("--hostname", "-h", help="Public hostname to route to the local service."),
    ],
    port: Annotated[
        int,
        typer.Option("--port", "-p", min=1, max=65535, help="Local HTTP port to expose."),
    ],
) -> None:
    """Scaffold a future Cloudflare-managed persistent tunnel flow."""
    settings = load_settings()
    try:
        settings.validate_managed_mode()
    except ManagedConfigError as exc:
        console.print(f"[red]{exc}[/]")
        raise typer.Exit(2) from exc

    request = ManagedTunnelRequest(
        name=name,
        hostname=hostname,
        local_url=f"http://localhost:{port}",
    )
    console.print(
        "[yellow]Managed publish is scaffolded for this MVP.[/]\n"
        f"Would configure tunnel [bold]{request.name}[/] at [bold]{request.hostname}[/] "
        f"for [bold]{request.local_url}[/]."
    )


@app.command("version")
def version_command() -> None:
    """Print the cftui version."""
    console.print(__version__)
