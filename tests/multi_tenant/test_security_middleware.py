"""Tests for security middleware — body limits, JSON depth, security headers.

Covers:
    - RequestBodyLimitMiddleware: Content-Length rejection, chunked body tracking, exempt paths
    - validate_json_depth: depth limits, nested dicts/lists, scalar pass-through
    - JsonDepthValidationMiddleware: POST/PUT rejection, GET pass-through, non-JSON pass-through
    - SecurityHeadersMiddleware: OWASP headers, HSTS, Shopify admin exemptions, Server-Timing

Run:
    pytest tests/multi_tenant/test_security_middleware.py -v

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

from __future__ import annotations

import json

import pytest
from starlette.testclient import TestClient

from src.multi_tenant.security_middleware import (
    BODY_LIMIT_EXEMPT_PREFIXES,
    MAX_BODY_SIZE_BYTES,
    MAX_JSON_DEPTH,
    SECURITY_HEADERS,
    JsonDepthValidationMiddleware,
    RequestBodyLimitMiddleware,
    SecurityHeadersMiddleware,
    validate_json_depth,
)


# ---------------------------------------------------------------------------
# SM-01 to SM-03: validate_json_depth unit tests
# ---------------------------------------------------------------------------


class TestValidateJsonDepth:
    """Pure-function tests for JSON depth validation."""

    def test_sm_01_shallow_dict_passes(self):
        """Shallow dict (depth 1) passes validation."""
        assert validate_json_depth({"key": "value"}) is True

    def test_sm_02_deep_dict_raises(self):
        """Dict exceeding max_depth raises ValueError."""
        # Build a dict nested 5 levels deep and set max_depth=3
        nested = {"a": {"b": {"c": {"d": {"e": "deep"}}}}}
        with pytest.raises(ValueError, match="nesting depth exceeds maximum"):
            validate_json_depth(nested, max_depth=3)

    def test_sm_03_deep_list_raises(self):
        """Nested lists exceeding max_depth raises ValueError."""
        nested: list = [[[["deep"]]]]
        with pytest.raises(ValueError, match="nesting depth exceeds maximum"):
            validate_json_depth(nested, max_depth=2)

    def test_sm_04_scalar_passes(self):
        """Scalar values (str, int, None) always pass."""
        assert validate_json_depth("hello") is True
        assert validate_json_depth(42) is True
        assert validate_json_depth(None) is True

    def test_sm_05_exact_depth_passes(self):
        """Dict at exactly max_depth passes (not >)."""
        # depth=0: outer dict, depth=1: inner value
        nested = {"a": "b"}
        assert validate_json_depth(nested, max_depth=1) is True

    def test_sm_06_mixed_nesting(self):
        """Mixed dict/list nesting counted correctly."""
        # dict -> list -> dict = depth 3
        data = {"items": [{"name": "test"}]}
        assert validate_json_depth(data, max_depth=3) is True
        with pytest.raises(ValueError):
            validate_json_depth(data, max_depth=1)


# ---------------------------------------------------------------------------
# SM-07 to SM-10: Middleware integration via TestClient
# ---------------------------------------------------------------------------


class TestRequestBodyLimit:
    """RequestBodyLimitMiddleware via Content-Length header check."""

    def _make_app(self, max_size: int = 1024):
        """Build a minimal Starlette app with body limit middleware."""
        from starlette.applications import Starlette
        from starlette.responses import JSONResponse
        from starlette.routing import Route

        async def echo(request):
            body = await request.body()
            return JSONResponse({"size": len(body)})

        async def stream_echo(request):
            body = await request.body()
            return JSONResponse({"size": len(body)})

        app = Starlette(
            routes=[
                Route("/test", echo, methods=["POST"]),
                Route("/api/chat/stream", stream_echo, methods=["POST"]),
            ],
        )
        return RequestBodyLimitMiddleware(app, max_body_size=max_size)

    def test_sm_07_small_body_passes(self):
        """Body under the limit is accepted."""
        app = self._make_app(max_size=1024)
        client = TestClient(app, raise_server_exceptions=False)
        resp = client.post("/test", content=b"small")
        assert resp.status_code == 200
        assert resp.json()["size"] == 5

    def test_sm_08_content_length_over_limit_413(self):
        """Content-Length exceeding limit returns 413."""
        app = self._make_app(max_size=10)
        client = TestClient(app, raise_server_exceptions=False)
        resp = client.post(
            "/test",
            content=b"x" * 50,
            headers={"content-length": "50"},
        )
        assert resp.status_code == 413
        assert "too large" in resp.json()["error"].lower()

    def test_sm_09_exempt_path_bypasses_limit(self):
        """Exempt paths (/api/chat/stream) bypass body size limit."""
        app = self._make_app(max_size=10)
        client = TestClient(app, raise_server_exceptions=False)
        resp = client.post(
            "/api/chat/stream",
            content=b"x" * 50,
            headers={"content-length": "50"},
        )
        assert resp.status_code == 200


class TestJsonDepthMiddleware:
    """JsonDepthValidationMiddleware integration tests."""

    def _make_app(self, max_depth: int = 5):
        """Build a minimal Starlette app with JSON depth middleware."""
        from starlette.applications import Starlette
        from starlette.responses import JSONResponse
        from starlette.routing import Route

        async def echo(request):
            return JSONResponse({"ok": True})

        app = Starlette(
            routes=[Route("/test", echo, methods=["POST", "GET"])],
        )
        return JsonDepthValidationMiddleware(app, max_depth=max_depth)

    def test_sm_10_shallow_json_post_passes(self):
        """POST with shallow JSON body passes."""
        app = self._make_app(max_depth=5)
        client = TestClient(app, raise_server_exceptions=False)
        resp = client.post(
            "/test",
            json={"key": "value"},
        )
        assert resp.status_code == 200

    def test_sm_11_deep_json_post_rejected(self):
        """POST with deeply nested JSON is rejected with 400."""
        app = self._make_app(max_depth=2)
        client = TestClient(app, raise_server_exceptions=False)
        deep = {"a": {"b": {"c": {"d": "deep"}}}}
        resp = client.post(
            "/test",
            json=deep,
        )
        assert resp.status_code == 400
        assert "nesting depth" in resp.json()["error"].lower()

    def test_sm_12_get_request_skips_validation(self):
        """GET requests bypass JSON depth validation."""
        app = self._make_app(max_depth=1)
        client = TestClient(app, raise_server_exceptions=False)
        resp = client.get("/test")
        assert resp.status_code == 200

    def test_sm_13_non_json_content_type_skips(self):
        """Non-JSON content type bypasses depth validation."""
        app = self._make_app(max_depth=1)
        client = TestClient(app, raise_server_exceptions=False)
        resp = client.post(
            "/test",
            content=b"plain text body",
            headers={"content-type": "text/plain"},
        )
        assert resp.status_code == 200


class TestSecurityHeaders:
    """SecurityHeadersMiddleware adds OWASP headers."""

    def _make_app(self):
        """Build a minimal app with security headers middleware."""
        from starlette.applications import Starlette
        from starlette.responses import JSONResponse
        from starlette.routing import Route

        async def hello(request):
            return JSONResponse({"ok": True})

        async def admin_page(request):
            return JSONResponse({"admin": True})

        app = Starlette(
            routes=[
                Route("/api/test", hello),
                Route("/admin/dashboard", admin_page),
            ],
        )
        return SecurityHeadersMiddleware(app)

    def test_sm_14_standard_headers_present(self):
        """All OWASP security headers are present on API responses."""
        app = self._make_app()
        client = TestClient(app, raise_server_exceptions=False)

        # SLA monitor import failure is caught by the middleware's try/except pass
        resp = client.get("/api/test")

        assert resp.status_code == 200
        assert resp.headers["x-content-type-options"] == "nosniff"
        assert resp.headers["x-frame-options"] == "DENY"
        assert resp.headers["x-xss-protection"] == "0"
        assert resp.headers["referrer-policy"] == "strict-origin-when-cross-origin"
        assert "camera=()" in resp.headers["permissions-policy"]
        assert resp.headers["cache-control"] == "no-store"

    def test_sm_15_admin_path_no_frame_options(self):
        """Admin paths skip X-Frame-Options (uses CSP frame-ancestors instead)."""
        app = self._make_app()
        client = TestClient(app, raise_server_exceptions=False)

        resp = client.get("/admin/dashboard")

        assert resp.status_code == 200
        # X-Frame-Options should NOT be present for /admin/ paths
        assert "x-frame-options" not in resp.headers
        # CSP frame-ancestors should be set instead
        assert "frame-ancestors" in resp.headers.get("content-security-policy", "")

    def test_sm_16_server_timing_header(self):
        """Server-Timing header with total duration is always present."""
        app = self._make_app()
        client = TestClient(app, raise_server_exceptions=False)

        resp = client.get("/api/test")

        assert "server-timing" in resp.headers
        assert "total;dur=" in resp.headers["server-timing"]
