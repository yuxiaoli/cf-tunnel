from __future__ import annotations

from typing import Any

import httpx

from .config import Settings
from .models import ManagedTunnelRequest


class CloudflareAPI:
    """Thin async client for future Cloudflare-managed tunnel operations."""

    base_url = "https://api.cloudflare.com/client/v4"

    def __init__(self, settings: Settings) -> None:
        settings.validate_managed_mode()
        self._settings = settings
        self._client = httpx.AsyncClient(
            base_url=self.base_url,
            headers={
                "Authorization": f"Bearer {settings.cloudflare_api_token}",
                "Content-Type": "application/json",
            },
            timeout=30.0,
        )

    async def close(self) -> None:
        await self._client.aclose()

    async def list_tunnels(self) -> dict[str, Any]:
        response = await self._client.get(
            f"/accounts/{self._settings.cloudflare_account_id}/tunnels"
        )
        response.raise_for_status()
        return response.json()

    async def publish(self, request: ManagedTunnelRequest) -> None:
        raise NotImplementedError(
            "Managed publish is scaffolded for the MVP. "
            f"Requested {request.hostname} -> {request.local_url}."
        )
