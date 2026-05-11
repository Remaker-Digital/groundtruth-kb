"""Production startup configuration guard tests."""

from __future__ import annotations

import pytest


def _set_valid_deployed_env(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("ENVIRONMENT", "production")
    monkeypatch.setenv("ADMIN_PREVIEW_PASSWORD", "admin-password-123")
    monkeypatch.setenv("ADMIN_SESSION_SECRET", "s" * 32)
    monkeypatch.setenv("MAGIC_LINK_JWT_SECRET", "m" * 32)
    monkeypatch.setenv("MFA_JWT_SECRET", "f" * 32)
    monkeypatch.setenv("CUSTOMER_TOKEN_SECRET", "c" * 32)
    monkeypatch.setenv("APP_BASE_URL", "https://agent-red.example.com")
    monkeypatch.setenv("APP_CORS_ORIGINS", "https://merchant.myshopify.com")


@pytest.mark.asyncio
async def test_deployed_config_guard_allows_complete_production_env(monkeypatch: pytest.MonkeyPatch) -> None:
    from src.app.lifecycle import _startup_required_deployed_config

    _set_valid_deployed_env(monkeypatch)

    await _startup_required_deployed_config()


@pytest.mark.asyncio
async def test_deployed_config_guard_rejects_missing_signing_secret(monkeypatch: pytest.MonkeyPatch) -> None:
    from src.app.lifecycle import _startup_required_deployed_config

    _set_valid_deployed_env(monkeypatch)
    monkeypatch.delenv("MFA_JWT_SECRET")

    with pytest.raises(RuntimeError, match="MFA_JWT_SECRET"):
        await _startup_required_deployed_config()


@pytest.mark.asyncio
async def test_deployed_config_guard_rejects_localhost_base_url(monkeypatch: pytest.MonkeyPatch) -> None:
    from src.app.lifecycle import _startup_required_deployed_config

    _set_valid_deployed_env(monkeypatch)
    monkeypatch.setenv("APP_BASE_URL", "http://localhost:8080")

    with pytest.raises(RuntimeError, match="localhost"):
        await _startup_required_deployed_config()


@pytest.mark.asyncio
async def test_deployed_config_guard_skips_development(monkeypatch: pytest.MonkeyPatch) -> None:
    from src.app.lifecycle import _startup_required_deployed_config

    monkeypatch.setenv("ENVIRONMENT", "development")
    for name in (
        "ADMIN_PREVIEW_PASSWORD",
        "ADMIN_SESSION_SECRET",
        "MAGIC_LINK_JWT_SECRET",
        "MFA_JWT_SECRET",
        "CUSTOMER_TOKEN_SECRET",
        "APP_BASE_URL",
        "APP_CORS_ORIGINS",
    ):
        monkeypatch.delenv(name, raising=False)

    await _startup_required_deployed_config()
