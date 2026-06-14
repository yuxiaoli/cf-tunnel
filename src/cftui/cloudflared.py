from __future__ import annotations

import asyncio
import re
from collections.abc import Sequence

from .models import TunnelEvent, TunnelEventType, TunnelStatus

TRYCLOUDFLARE_URL_RE = re.compile(r"https://[A-Za-z0-9-]+\.trycloudflare\.com\b")


class CloudflaredNotFoundError(RuntimeError):
    """Raised when the configured cloudflared executable cannot be found."""


def parse_public_url(line: str) -> str | None:
    match = TRYCLOUDFLARE_URL_RE.search(line)
    return match.group(0) if match else None


def mask_sensitive_values(text: str, values: Sequence[str | None]) -> str:
    masked = text
    for value in values:
        if value and len(value) >= 6:
            masked = masked.replace(value, f"{value[:3]}...{value[-2:]}")
    return masked


class CloudflaredRunner:
    def __init__(
        self,
        local_url: str,
        *,
        cloudflared_bin: str = "cloudflared",
        log_level: str = "INFO",
        sensitive_values: Sequence[str | None] = (),
    ) -> None:
        self.local_url = local_url
        self.cloudflared_bin = cloudflared_bin
        self.log_level = log_level.lower()
        self.sensitive_values = sensitive_values
        self.status = TunnelStatus.STOPPED
        self.public_url: str | None = None
        self.events: asyncio.Queue[TunnelEvent] = asyncio.Queue()
        self._process: asyncio.subprocess.Process | None = None
        self._tasks: set[asyncio.Task[None]] = set()
        self._stopping = False

    @property
    def is_running(self) -> bool:
        return self._process is not None and self._process.returncode is None

    async def start(self) -> None:
        if self.is_running:
            await self._emit(TunnelEventType.LOG, "Tunnel is already running.")
            return

        self.public_url = None
        self._stopping = False
        await self._set_status(TunnelStatus.STARTING, "Starting Cloudflare Quick Tunnel...")

        try:
            self._process = await asyncio.create_subprocess_exec(
                self.cloudflared_bin,
                "tunnel",
                "--loglevel",
                self.log_level,
                "--url",
                self.local_url,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )
        except FileNotFoundError as exc:
            message = (
                f"Could not find '{self.cloudflared_bin}'. Install cloudflared or set "
                "CLOUDFLARED_BIN in .env."
            )
            await self._set_status(TunnelStatus.ERROR, message)
            raise CloudflaredNotFoundError(message) from exc

        await self._set_status(TunnelStatus.RUNNING, "cloudflared process started.")
        self._tasks = {
            asyncio.create_task(self._read_stream(self._process.stdout, "stdout")),
            asyncio.create_task(self._read_stream(self._process.stderr, "stderr")),
            asyncio.create_task(self._watch_process()),
        }

    async def stop(self) -> None:
        if not self.is_running:
            await self._set_status(TunnelStatus.STOPPED, "Tunnel is stopped.")
            return

        self._stopping = True
        await self._set_status(TunnelStatus.STOPPING, "Stopping tunnel...")
        assert self._process is not None
        self._process.terminate()
        try:
            await asyncio.wait_for(self._process.wait(), timeout=8)
        except TimeoutError:
            self._process.kill()
            await self._process.wait()

        for task in self._tasks:
            task.cancel()
        self._tasks.clear()
        await self._set_status(TunnelStatus.STOPPED, "Tunnel stopped.")

    async def restart(self) -> None:
        await self.stop()
        await self.start()

    async def _read_stream(self, stream: asyncio.StreamReader | None, stream_name: str) -> None:
        if stream is None:
            return

        while True:
            raw = await stream.readline()
            if not raw:
                return
            text = raw.decode(errors="replace").rstrip()
            text = mask_sensitive_values(text, self.sensitive_values)
            await self._emit(TunnelEventType.LOG, f"[{stream_name}] {text}")
            public_url = parse_public_url(text)
            if public_url and public_url != self.public_url:
                self.public_url = public_url
                await self._emit(TunnelEventType.URL, public_url)

    async def _watch_process(self) -> None:
        if self._process is None:
            return
        code = await self._process.wait()
        if self._stopping:
            return
        if code == 0:
            await self._set_status(TunnelStatus.STOPPED, "cloudflared exited.")
        else:
            await self._set_status(TunnelStatus.ERROR, f"cloudflared exited with code {code}.")

    async def _set_status(self, status: TunnelStatus, message: str) -> None:
        self.status = status
        await self.events.put(TunnelEvent(TunnelEventType.STATUS, message, status))

    async def _emit(self, event_type: TunnelEventType, message: str) -> None:
        await self.events.put(TunnelEvent(event_type, message))
