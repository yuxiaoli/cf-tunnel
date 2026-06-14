from __future__ import annotations

import asyncio

import pyperclip
from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.widgets import Footer, Header, RichLog

from cftui.cloudflared import CloudflaredNotFoundError, CloudflaredRunner
from cftui.models import TunnelEventType
from cftui.tui.widgets import SummaryPanel


class TunnelApp(App[None]):
    CSS = """
    Screen {
        layout: vertical;
    }

    #summary {
        height: 5;
        padding: 0 1;
        border: solid $primary;
    }

    #logs {
        height: 1fr;
        border: solid $accent;
    }
    """

    BINDINGS = [
        Binding("q", "quit", "Quit"),
        Binding("r", "restart", "Restart"),
        Binding("c", "copy_url", "Copy URL"),
        Binding("s", "stop", "Stop"),
    ]

    def __init__(self, runner: CloudflaredRunner) -> None:
        super().__init__()
        self.runner = runner
        self._event_task: asyncio.Task[None] | None = None

    def compose(self) -> ComposeResult:
        yield Header()
        yield SummaryPanel(id="summary")
        yield RichLog(id="logs", wrap=True, highlight=True, markup=False)
        yield Footer()

    async def on_mount(self) -> None:
        self.title = "cftui"
        self._refresh_summary()
        self._write_log("Quick Tunnel URLs are public. Do not expose sensitive services.")
        self._event_task = asyncio.create_task(self._consume_events())
        await self._start_tunnel()

    async def on_unmount(self) -> None:
        if self._event_task:
            self._event_task.cancel()
        await self.runner.stop()

    async def action_stop(self) -> None:
        await self.runner.stop()
        self._refresh_summary()

    async def action_restart(self) -> None:
        self._write_log("Restarting tunnel...")
        await self._start_tunnel(restart=True)

    def action_copy_url(self) -> None:
        if not self.runner.public_url:
            self.notify("No public URL is available yet.", severity="warning")
            return

        try:
            if hasattr(self, "copy_to_clipboard"):
                self.copy_to_clipboard(self.runner.public_url)
            else:
                pyperclip.copy(self.runner.public_url)
        except Exception as exc:
            self.notify(f"Could not copy URL: {exc}", severity="error")
            return
        self.notify("Public URL copied.")

    async def _start_tunnel(self, *, restart: bool = False) -> None:
        try:
            if restart:
                await self.runner.restart()
            else:
                await self.runner.start()
        except CloudflaredNotFoundError as exc:
            self._write_log(str(exc))
            self.notify(str(exc), severity="error")
        self._refresh_summary()

    async def _consume_events(self) -> None:
        while True:
            event = await self.runner.events.get()
            if event.type is TunnelEventType.LOG:
                self._write_log(event.message)
            elif event.type is TunnelEventType.URL:
                self._write_log(f"Public URL detected: {event.message}")
                self.notify("Public URL detected.")
            elif event.type is TunnelEventType.ERROR:
                self._write_log(event.message)
                self.notify(event.message, severity="error")
            elif event.type is TunnelEventType.STATUS:
                self._write_log(event.message)
            self._refresh_summary()

    def _refresh_summary(self) -> None:
        summary = self.query_one("#summary", SummaryPanel)
        summary.update_summary(
            local_url=self.runner.local_url,
            public_url=self.runner.public_url,
            status=self.runner.status.value,
        )

    def _write_log(self, message: str) -> None:
        logs = self.query_one("#logs", RichLog)
        logs.write(message)
