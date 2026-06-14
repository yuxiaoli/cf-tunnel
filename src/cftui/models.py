from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum


class TunnelStatus(StrEnum):
    STOPPED = "stopped"
    STARTING = "starting"
    RUNNING = "running"
    STOPPING = "stopping"
    ERROR = "error"


class TunnelEventType(StrEnum):
    LOG = "log"
    STATUS = "status"
    URL = "url"
    ERROR = "error"


@dataclass(frozen=True)
class TunnelEvent:
    type: TunnelEventType
    message: str
    status: TunnelStatus | None = None


@dataclass(frozen=True)
class ManagedTunnelRequest:
    name: str
    hostname: str
    local_url: str
