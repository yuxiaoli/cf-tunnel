from __future__ import annotations

import pytest

from cftui.config import ManagedConfigError, load_settings

ENV_KEYS = [
    "CLOUDFLARE_API_TOKEN",
    "CLOUDFLARE_ACCOUNT_ID",
    "CLOUDFLARE_ZONE_ID",
    "CLOUDFLARE_DEFAULT_DOMAIN",
    "CLOUDFLARED_BIN",
    "LOG_LEVEL",
]


def test_load_settings_from_env_file(tmp_path, monkeypatch):
    for key in ENV_KEYS:
        monkeypatch.delenv(key, raising=False)
    env_file = tmp_path / ".env"
    env_file.write_text(
        "\n".join(
            [
                "CLOUDFLARE_ACCOUNT_ID=account-123",
                "CLOUDFLARED_BIN=/opt/bin/cloudflared",
                "LOG_LEVEL=debug",
            ]
        ),
        encoding="utf-8",
    )

    settings = load_settings(env_file, override=True)

    assert settings.cloudflare_account_id == "account-123"
    assert settings.cloudflare_api_token is None
    assert settings.cloudflared_bin == "/opt/bin/cloudflared"
    assert settings.log_level == "DEBUG"


def test_managed_mode_requires_token_and_account(tmp_path, monkeypatch):
    for key in ENV_KEYS:
        monkeypatch.delenv(key, raising=False)
    env_file = tmp_path / ".env"
    env_file.write_text("", encoding="utf-8")

    settings = load_settings(env_file, override=True)

    with pytest.raises(ManagedConfigError, match="CLOUDFLARE_API_TOKEN"):
        settings.validate_managed_mode()


def test_managed_mode_accepts_required_credentials(tmp_path, monkeypatch):
    for key in ENV_KEYS:
        monkeypatch.delenv(key, raising=False)
    env_file = tmp_path / ".env"
    env_file.write_text(
        "CLOUDFLARE_API_TOKEN=secret-token\nCLOUDFLARE_ACCOUNT_ID=account-123\n",
        encoding="utf-8",
    )

    settings = load_settings(env_file, override=True)

    settings.validate_managed_mode()
