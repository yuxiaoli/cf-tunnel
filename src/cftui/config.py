from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv
from pydantic import BaseModel, ConfigDict, Field


class ManagedConfigError(ValueError):
    """Raised when managed tunnel mode is missing required configuration."""


class Settings(BaseModel):
    cloudflare_api_token: str | None = Field(default=None)
    cloudflare_account_id: str | None = Field(default=None)
    cloudflare_zone_id: str | None = Field(default=None)
    cloudflare_default_domain: str | None = Field(default=None)
    cloudflared_bin: str = Field(default="cloudflared")
    log_level: str = Field(default="INFO")

    model_config = ConfigDict(frozen=True)

    def validate_managed_mode(self) -> None:
        missing = []
        if not self.cloudflare_api_token:
            missing.append("CLOUDFLARE_API_TOKEN")
        if not self.cloudflare_account_id:
            missing.append("CLOUDFLARE_ACCOUNT_ID")
        if missing:
            joined = ", ".join(missing)
            raise ManagedConfigError(f"Managed tunnel mode requires: {joined}")


def _env(name: str, default: str | None = None) -> str | None:
    value = os.getenv(name, default)
    if value is None:
        return None
    value = value.strip()
    return value or None


def load_settings(env_file: str | Path | None = ".env", *, override: bool = False) -> Settings:
    if env_file is None:
        load_dotenv(override=override)
    else:
        load_dotenv(dotenv_path=env_file, override=override)

    return Settings(
        cloudflare_api_token=_env("CLOUDFLARE_API_TOKEN"),
        cloudflare_account_id=_env("CLOUDFLARE_ACCOUNT_ID"),
        cloudflare_zone_id=_env("CLOUDFLARE_ZONE_ID"),
        cloudflare_default_domain=_env("CLOUDFLARE_DEFAULT_DOMAIN"),
        cloudflared_bin=_env("CLOUDFLARED_BIN", "cloudflared") or "cloudflared",
        log_level=(_env("LOG_LEVEL", "INFO") or "INFO").upper(),
    )
