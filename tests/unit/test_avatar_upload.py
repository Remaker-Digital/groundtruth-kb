"""
Tests for avatar upload endpoint — D22 capability.

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

from __future__ import annotations

import base64
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient

from src.multi_tenant.avatar_upload import router, configure_avatar_service

# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


def _make_app() -> FastAPI:
    app = FastAPI()
    app.include_router(router)
    return app


def _make_mock_processor(success: bool = True):
    proc = MagicMock()
    result = MagicMock()
    result.success = success
    proc.update_config = AsyncMock(return_value=result)
    return proc


def _make_png_bytes(size: int = 100) -> bytes:
    """Create minimal PNG-like bytes."""
    return b"\x89PNG\r\n\x1a\n" + b"\x00" * (size - 8)


def _make_jpeg_bytes(size: int = 100) -> bytes:
    """Create minimal JPEG-like bytes."""
    return b"\xff\xd8\xff\xe0" + b"\x00" * (size - 4)


@pytest.fixture
def mock_ctx():
    ctx = MagicMock()
    ctx.tenant_id = "test-tenant-001"
    ctx.tier = "professional"
    ctx.user_id = "admin-user"
    ctx.shop_domain = None
    return ctx


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------


class TestAvatarUpload:
    """Tests for POST /api/admin/avatar/upload."""

    @pytest.mark.asyncio
    async def test_upload_png_success(self, mock_ctx):
        proc = _make_mock_processor()
        configure_avatar_service(proc)
        app = _make_app()

        with patch("src.multi_tenant.avatar_upload.get_tenant_context", return_value=mock_ctx):
            app.dependency_overrides[
                __import__("src.multi_tenant.middleware", fromlist=["get_tenant_context"]).get_tenant_context
            ] = lambda: mock_ctx
            transport = ASGITransport(app=app)
            async with AsyncClient(transport=transport, base_url="http://test") as client:
                png_data = _make_png_bytes(200)
                resp = await client.post(
                    "/api/admin/avatar/upload",
                    files={"file": ("avatar.png", png_data, "image/png")},
                )

        assert resp.status_code == 200
        body = resp.json()
        assert body["success"] is True
        assert body["avatar_url"].startswith("data:image/png;base64,")
        assert body["size_bytes"] == 200

    @pytest.mark.asyncio
    async def test_upload_jpeg_success(self, mock_ctx):
        proc = _make_mock_processor()
        configure_avatar_service(proc)
        app = _make_app()

        with patch("src.multi_tenant.avatar_upload.get_tenant_context", return_value=mock_ctx):
            app.dependency_overrides[
                __import__("src.multi_tenant.middleware", fromlist=["get_tenant_context"]).get_tenant_context
            ] = lambda: mock_ctx
            transport = ASGITransport(app=app)
            async with AsyncClient(transport=transport, base_url="http://test") as client:
                jpeg_data = _make_jpeg_bytes(300)
                resp = await client.post(
                    "/api/admin/avatar/upload",
                    files={"file": ("photo.jpg", jpeg_data, "image/jpeg")},
                )

        assert resp.status_code == 200
        body = resp.json()
        assert body["success"] is True
        assert "image/jpeg" in body["avatar_url"]

    @pytest.mark.asyncio
    async def test_upload_rejects_invalid_type(self, mock_ctx):
        proc = _make_mock_processor()
        configure_avatar_service(proc)
        app = _make_app()

        with patch("src.multi_tenant.avatar_upload.get_tenant_context", return_value=mock_ctx):
            app.dependency_overrides[
                __import__("src.multi_tenant.middleware", fromlist=["get_tenant_context"]).get_tenant_context
            ] = lambda: mock_ctx
            transport = ASGITransport(app=app)
            async with AsyncClient(transport=transport, base_url="http://test") as client:
                resp = await client.post(
                    "/api/admin/avatar/upload",
                    files={"file": ("file.gif", b"GIF89a" + b"\x00" * 50, "image/gif")},
                )

        assert resp.status_code == 400
        assert "Invalid file type" in resp.json()["detail"]

    @pytest.mark.asyncio
    async def test_upload_rejects_oversized_file(self, mock_ctx):
        proc = _make_mock_processor()
        configure_avatar_service(proc)
        app = _make_app()

        with patch("src.multi_tenant.avatar_upload.get_tenant_context", return_value=mock_ctx):
            app.dependency_overrides[
                __import__("src.multi_tenant.middleware", fromlist=["get_tenant_context"]).get_tenant_context
            ] = lambda: mock_ctx
            transport = ASGITransport(app=app)
            async with AsyncClient(transport=transport, base_url="http://test") as client:
                big_data = _make_png_bytes(8) + b"\x00" * (256 * 1024 + 1)
                resp = await client.post(
                    "/api/admin/avatar/upload",
                    files={"file": ("big.png", big_data, "image/png")},
                )

        assert resp.status_code == 400
        assert "too large" in resp.json()["detail"]

    @pytest.mark.asyncio
    async def test_upload_stores_data_uri_in_config(self, mock_ctx):
        proc = _make_mock_processor()
        configure_avatar_service(proc)
        app = _make_app()

        with patch("src.multi_tenant.avatar_upload.get_tenant_context", return_value=mock_ctx):
            app.dependency_overrides[
                __import__("src.multi_tenant.middleware", fromlist=["get_tenant_context"]).get_tenant_context
            ] = lambda: mock_ctx
            transport = ASGITransport(app=app)
            async with AsyncClient(transport=transport, base_url="http://test") as client:
                png_data = _make_png_bytes(64)
                await client.post(
                    "/api/admin/avatar/upload",
                    files={"file": ("a.png", png_data, "image/png")},
                )

        # Verify update_config was called with data URI
        proc.update_config.assert_called_once()
        call_kwargs = proc.update_config.call_args
        updates = call_kwargs.kwargs.get("updates") or call_kwargs[1].get("updates")
        assert "widget_agent_avatar_url" in updates
        assert updates["widget_agent_avatar_url"].startswith("data:image/png;base64,")


class TestAvatarDelete:
    """Tests for DELETE /api/admin/avatar."""

    @pytest.mark.asyncio
    async def test_delete_success(self, mock_ctx):
        proc = _make_mock_processor()
        configure_avatar_service(proc)
        app = _make_app()

        with patch("src.multi_tenant.avatar_upload.get_tenant_context", return_value=mock_ctx):
            app.dependency_overrides[
                __import__("src.multi_tenant.middleware", fromlist=["get_tenant_context"]).get_tenant_context
            ] = lambda: mock_ctx
            transport = ASGITransport(app=app)
            async with AsyncClient(transport=transport, base_url="http://test") as client:
                resp = await client.delete("/api/admin/avatar")

        assert resp.status_code == 200
        body = resp.json()
        assert body["success"] is True
        assert "removed" in body["message"].lower() or "default" in body["message"].lower()

    @pytest.mark.asyncio
    async def test_delete_sets_avatar_to_none(self, mock_ctx):
        proc = _make_mock_processor()
        configure_avatar_service(proc)
        app = _make_app()

        with patch("src.multi_tenant.avatar_upload.get_tenant_context", return_value=mock_ctx):
            app.dependency_overrides[
                __import__("src.multi_tenant.middleware", fromlist=["get_tenant_context"]).get_tenant_context
            ] = lambda: mock_ctx
            transport = ASGITransport(app=app)
            async with AsyncClient(transport=transport, base_url="http://test") as client:
                await client.delete("/api/admin/avatar")

        call_kwargs = proc.update_config.call_args
        updates = call_kwargs.kwargs.get("updates") or call_kwargs[1].get("updates")
        assert updates["widget_agent_avatar_url"] is None
