from __future__ import annotations

from cftui.cloudflared import mask_sensitive_values, parse_public_url


def test_parse_public_url_from_cloudflared_log_line():
    line = "INF +------------------------------------------------------------+ https://demo.trycloudflare.com"

    assert parse_public_url(line) == "https://demo.trycloudflare.com"


def test_parse_public_url_returns_none_without_trycloudflare_url():
    assert parse_public_url("INF Starting tunnel") is None


def test_mask_sensitive_values_masks_long_values():
    text = "Authorization: Bearer abcdefghijkl"

    assert mask_sensitive_values(text, ["abcdefghijkl"]) == "Authorization: Bearer abc...kl"
