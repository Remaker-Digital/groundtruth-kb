"""Unit tests for widget OTP email verification (AUTH-3).

Tests the OTP send and verify endpoints in
src/multi_tenant/widget_otp_verification.py.

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

from __future__ import annotations

import json
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient

from src.multi_tenant.widget_otp_verification import (
    _OTP_TOKEN_TYPE,
    _SMS_OTP_TOKEN_TYPE,
    _generate_otp,
    decode_customer_token,
    router,
)

# ---------------------------------------------------------------------------
# Test app
# ---------------------------------------------------------------------------


def _build_app() -> FastAPI:
    """Create a minimal FastAPI app with the OTP router."""
    app = FastAPI()
    app.include_router(router)
    return app


def _mock_tenant_context(tenant_id: str = "test-tenant-001"):
    """Create a mock TenantContext for dependency injection."""
    ctx = MagicMock()
    ctx.tenant_id = tenant_id
    ctx.tier = "starter"
    ctx.status = "active"
    return ctx


# ---------------------------------------------------------------------------
# OTP generation tests
# ---------------------------------------------------------------------------


class TestOtpGeneration:
    """Test the OTP code generation function."""

    def test_otp_is_six_digits(self):
        code = _generate_otp()
        assert len(code) == 6
        assert code.isdigit()

    def test_otp_is_zero_padded(self):
        """Ensure codes like 000123 are zero-padded."""
        # Run many times to increase probability of small numbers
        for _ in range(100):
            code = _generate_otp()
            assert len(code) == 6

    def test_otp_is_random(self):
        """Codes should vary (probabilistic test)."""
        codes = {_generate_otp() for _ in range(20)}
        # With 10^6 possible values and 20 draws, collisions are very unlikely
        assert len(codes) >= 15


# ---------------------------------------------------------------------------
# Customer token tests
# ---------------------------------------------------------------------------


class TestCustomerToken:
    """Test customer token generation and validation."""

    def test_valid_token_decodes(self):
        from src.multi_tenant.widget_otp_verification import _generate_customer_token

        token = _generate_customer_token(
            tenant_id="test-tenant",
            email="alice@example.com",
            name="Alice",
        )
        payload = decode_customer_token(token)
        assert payload is not None
        assert payload["tenant_id"] == "test-tenant"
        assert payload["email"] == "alice@example.com"
        assert payload["name"] == "Alice"
        assert "exp" in payload

    def test_expired_token_returns_none(self):
        import base64
        import hashlib
        import hmac
        import os
        import time

        # Manually create an expired token
        payload = json.dumps(
            {
                "tenant_id": "t",
                "email": "a@b.com",
                "name": "",
                "exp": int(time.time()) - 100,  # Expired 100s ago
            },
            separators=(",", ":"),
            sort_keys=True,
        )
        secret = os.environ.get("CUSTOMER_TOKEN_SECRET", "agentred-customer-token-default")
        sig = hmac.new(secret.encode(), payload.encode(), hashlib.sha256).hexdigest()[:32]
        encoded = base64.urlsafe_b64encode(payload.encode()).decode()
        token = f"{encoded}.{sig}"

        assert decode_customer_token(token) is None

    def test_tampered_token_returns_none(self):
        from src.multi_tenant.widget_otp_verification import _generate_customer_token

        token = _generate_customer_token(
            tenant_id="test-tenant",
            email="alice@example.com",
            name="Alice",
        )
        # Flip a character in the signature
        parts = token.split(".")
        tampered_sig = parts[1][:-1] + ("a" if parts[1][-1] != "a" else "b")
        tampered = f"{parts[0]}.{tampered_sig}"
        assert decode_customer_token(tampered) is None

    def test_garbage_token_returns_none(self):
        assert decode_customer_token("not-a-token") is None
        assert decode_customer_token("") is None
        assert decode_customer_token("a.b.c") is None


# ---------------------------------------------------------------------------
# Endpoint tests
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
class TestSendOtpEndpoint:
    """Test POST /api/chat/otp/send."""

    async def test_send_otp_success(self):
        app = _build_app()
        ctx = _mock_tenant_context()

        mock_token_repo = MagicMock()
        mock_token_repo.delete_token = AsyncMock(return_value=True)
        mock_token_repo.create_token = AsyncMock(return_value={"id": "otp:test-tenant-001:alice@example.com"})

        mock_container = MagicMock()
        mock_container.patch_item = AsyncMock(return_value={})

        mock_cosmos = MagicMock()
        mock_cosmos.get_container = MagicMock(return_value=mock_container)

        with (
            patch("src.multi_tenant.widget_otp_verification.get_tenant_context", return_value=ctx),
            patch(
                "src.multi_tenant.widget_otp_verification._get_verification_mode",
                new_callable=AsyncMock,
                return_value="required",
            ),
            patch("src.multi_tenant.repositories.VerificationTokenRepository", return_value=mock_token_repo),
            patch("src.multi_tenant.cosmos_client.get_cosmos_manager", return_value=mock_cosmos),
            patch(
                "src.multi_tenant.widget_otp_verification._send_otp_email", new_callable=AsyncMock, return_value=True
            ),
        ):
            app.dependency_overrides = {}
            from src.multi_tenant.middleware import get_tenant_context

            app.dependency_overrides[get_tenant_context] = lambda: ctx

            async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
                resp = await client.post(
                    "/api/chat/otp/send",
                    json={
                        "email": "alice@example.com",
                        "name": "Alice",
                    },
                )

            assert resp.status_code == 200
            data = resp.json()
            assert data["sent"] is True

    async def test_send_otp_when_disabled(self):
        app = _build_app()
        ctx = _mock_tenant_context()

        with (
            patch(
                "src.multi_tenant.widget_otp_verification._get_verification_mode",
                new_callable=AsyncMock,
                return_value="disabled",
            ),
        ):
            from src.multi_tenant.middleware import get_tenant_context

            app.dependency_overrides[get_tenant_context] = lambda: ctx

            async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
                resp = await client.post(
                    "/api/chat/otp/send",
                    json={
                        "email": "alice@example.com",
                    },
                )

            assert resp.status_code == 200
            data = resp.json()
            assert "not required" in data["message"].lower()


@pytest.mark.asyncio
class TestVerifyOtpEndpoint:
    """Test POST /api/chat/otp/verify."""

    async def test_verify_otp_success(self):
        app = _build_app()
        ctx = _mock_tenant_context()

        mock_container = MagicMock()
        mock_container.read_item = AsyncMock(
            return_value={
                "id": "otp:test-tenant-001:alice@example.com",
                "otp_code": "123456",
                "used": False,
                "customer_name": "Alice",
            }
        )

        mock_cosmos = MagicMock()
        mock_cosmos.get_container = MagicMock(return_value=mock_container)

        mock_token_repo = MagicMock()
        mock_token_repo.consume_token = AsyncMock(return_value={"id": "otp:test-tenant-001:alice@example.com"})

        with (
            patch("src.multi_tenant.cosmos_client.get_cosmos_manager", return_value=mock_cosmos),
            patch("src.multi_tenant.repositories.VerificationTokenRepository", return_value=mock_token_repo),
        ):
            from src.multi_tenant.middleware import get_tenant_context

            app.dependency_overrides[get_tenant_context] = lambda: ctx

            async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
                resp = await client.post(
                    "/api/chat/otp/verify",
                    json={
                        "email": "alice@example.com",
                        "code": "123456",
                    },
                )

            assert resp.status_code == 200
            data = resp.json()
            assert data["verified"] is True
            assert data["customer_token"] is not None

    async def test_verify_otp_wrong_code(self):
        app = _build_app()
        ctx = _mock_tenant_context()

        mock_container = MagicMock()
        mock_container.read_item = AsyncMock(
            return_value={
                "id": "otp:test-tenant-001:alice@example.com",
                "otp_code": "123456",
                "used": False,
            }
        )

        mock_cosmos = MagicMock()
        mock_cosmos.get_container = MagicMock(return_value=mock_container)

        with (
            patch("src.multi_tenant.cosmos_client.get_cosmos_manager", return_value=mock_cosmos),
        ):
            from src.multi_tenant.middleware import get_tenant_context

            app.dependency_overrides[get_tenant_context] = lambda: ctx

            async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
                resp = await client.post(
                    "/api/chat/otp/verify",
                    json={
                        "email": "alice@example.com",
                        "code": "999999",
                    },
                )

            assert resp.status_code == 200
            data = resp.json()
            assert data["verified"] is False
            assert data["customer_token"] is None

    async def test_verify_otp_already_used(self):
        app = _build_app()
        ctx = _mock_tenant_context()

        mock_container = MagicMock()
        mock_container.read_item = AsyncMock(
            return_value={
                "id": "otp:test-tenant-001:alice@example.com",
                "otp_code": "123456",
                "used": True,  # Already used
            }
        )

        mock_cosmos = MagicMock()
        mock_cosmos.get_container = MagicMock(return_value=mock_container)

        with (
            patch("src.multi_tenant.cosmos_client.get_cosmos_manager", return_value=mock_cosmos),
        ):
            from src.multi_tenant.middleware import get_tenant_context

            app.dependency_overrides[get_tenant_context] = lambda: ctx

            async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
                resp = await client.post(
                    "/api/chat/otp/verify",
                    json={
                        "email": "alice@example.com",
                        "code": "123456",
                    },
                )

            assert resp.status_code == 200
            data = resp.json()
            assert data["verified"] is False

    async def test_verify_otp_expired_not_found(self):
        """OTP expired (Cosmos DB TTL deleted it)."""
        app = _build_app()
        ctx = _mock_tenant_context()

        mock_container = MagicMock()
        mock_container.read_item = AsyncMock(side_effect=Exception("NotFound"))

        mock_cosmos = MagicMock()
        mock_cosmos.get_container = MagicMock(return_value=mock_container)

        with (
            patch("src.multi_tenant.cosmos_client.get_cosmos_manager", return_value=mock_cosmos),
        ):
            from src.multi_tenant.middleware import get_tenant_context

            app.dependency_overrides[get_tenant_context] = lambda: ctx

            async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
                resp = await client.post(
                    "/api/chat/otp/verify",
                    json={
                        "email": "alice@example.com",
                        "code": "123456",
                    },
                )

            assert resp.status_code == 200
            data = resp.json()
            assert data["verified"] is False

    async def test_verify_otp_wrong_code_increments_attempt_counter(self):
        app = _build_app()
        ctx = _mock_tenant_context()

        mock_container = MagicMock()
        mock_container.read_item = AsyncMock(
            return_value={
                "id": "otp:test-tenant-001:alice@example.com",
                "otp_code": "123456",
                "used": False,
                "verify_attempts": 2,
            }
        )
        mock_container.patch_item = AsyncMock(return_value={})

        mock_cosmos = MagicMock()
        mock_cosmos.get_container = MagicMock(return_value=mock_container)

        with (
            patch("src.multi_tenant.cosmos_client.get_cosmos_manager", return_value=mock_cosmos),
        ):
            from src.multi_tenant.middleware import get_tenant_context

            app.dependency_overrides[get_tenant_context] = lambda: ctx

            async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
                resp = await client.post(
                    "/api/chat/otp/verify",
                    json={
                        "email": "alice@example.com",
                        "code": "999999",
                    },
                )

            assert resp.status_code == 200
            data = resp.json()
            assert data["verified"] is False
            mock_container.patch_item.assert_awaited_once_with(
                item="otp:test-tenant-001:alice@example.com",
                partition_key=_OTP_TOKEN_TYPE,
                patch_operations=[
                    {"op": "incr", "path": "/verify_attempts", "value": 1},
                ],
            )

    async def test_verify_otp_returns_false_when_locked_after_max_attempts(self):
        app = _build_app()
        ctx = _mock_tenant_context()

        mock_container = MagicMock()
        mock_container.read_item = AsyncMock(
            return_value={
                "id": "otp:test-tenant-001:alice@example.com",
                "otp_code": "123456",
                "used": False,
                "verify_attempts": 5,
            }
        )
        mock_container.patch_item = AsyncMock(return_value={})

        mock_cosmos = MagicMock()
        mock_cosmos.get_container = MagicMock(return_value=mock_container)

        with (
            patch("src.multi_tenant.cosmos_client.get_cosmos_manager", return_value=mock_cosmos),
        ):
            from src.multi_tenant.middleware import get_tenant_context

            app.dependency_overrides[get_tenant_context] = lambda: ctx

            async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
                resp = await client.post(
                    "/api/chat/otp/verify",
                    json={
                        "email": "alice@example.com",
                        "code": "123456",
                    },
                )

            assert resp.status_code == 200
            data = resp.json()
            assert data["verified"] is False
            mock_container.patch_item.assert_not_awaited()


@pytest.mark.asyncio
class TestSmsOtpEndpoints:
    """Test POST /api/chat/otp/send-sms and /api/chat/otp/verify-sms."""

    async def test_send_sms_returns_transport_failure_response(self):
        app = _build_app()
        ctx = _mock_tenant_context()

        mock_token_repo = MagicMock()
        mock_token_repo.delete_token = AsyncMock(return_value=True)
        mock_token_repo.create_token = AsyncMock(return_value={"id": "otp:test-tenant-001:+12125550100"})

        mock_container = MagicMock()
        mock_container.patch_item = AsyncMock(return_value={})

        mock_cosmos = MagicMock()
        mock_cosmos.get_container = MagicMock(return_value=mock_container)

        with (
            patch(
                "src.multi_tenant.widget_otp_verification._check_tier_gate", new_callable=AsyncMock, return_value=True
            ),
            patch("src.multi_tenant.repositories.VerificationTokenRepository", return_value=mock_token_repo),
            patch("src.multi_tenant.cosmos_client.get_cosmos_manager", return_value=mock_cosmos),
            patch(
                "src.multi_tenant.sms_verification._send_sms",
                new_callable=AsyncMock,
                side_effect=RuntimeError("ACS down"),
            ),
        ):
            from src.multi_tenant.middleware import get_tenant_context

            app.dependency_overrides[get_tenant_context] = lambda: ctx

            async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
                resp = await client.post(
                    "/api/chat/otp/send-sms",
                    json={
                        "phone": "+12125550100",
                        "name": "Alice",
                    },
                )

            assert resp.status_code == 200
            data = resp.json()
            assert data["sent"] is False
            assert "Unable to send verification code" in data["message"]

    async def test_send_sms_returns_failure_when_send_sms_returns_false(self):
        """_send_sms returning False (not raising) must produce sent=False response (WI-3038).

        Fixture pattern (per bridge `agent-red-sms-otp-hardening-002` NO-GO): patch
        `_is_rate_limited` to False so prior-test state in the in-memory rate-limiter
        cannot interfere. This test is not about rate limiting; isolating that
        dependency ensures the _send_sms branch is what drives the outcome.
        """
        app = _build_app()
        ctx = _mock_tenant_context()

        mock_token_repo = MagicMock()
        mock_token_repo.delete_token = AsyncMock(return_value=True)
        mock_token_repo.create_token = AsyncMock(return_value={"id": "otp:test-tenant-001:+12125550100"})

        mock_container = MagicMock()
        mock_container.patch_item = AsyncMock(return_value={})

        mock_cosmos = MagicMock()
        mock_cosmos.get_container = MagicMock(return_value=mock_container)

        mock_send_sms = AsyncMock(return_value=False)

        with (
            patch(
                "src.multi_tenant.widget_otp_verification._check_tier_gate", new_callable=AsyncMock, return_value=True
            ),
            patch("src.multi_tenant.widget_otp_verification._is_rate_limited", return_value=False),
            patch("src.multi_tenant.repositories.VerificationTokenRepository", return_value=mock_token_repo),
            patch("src.multi_tenant.cosmos_client.get_cosmos_manager", return_value=mock_cosmos),
            patch("src.multi_tenant.sms_verification._send_sms", mock_send_sms),
        ):
            from src.multi_tenant.middleware import get_tenant_context

            app.dependency_overrides[get_tenant_context] = lambda: ctx

            async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
                resp = await client.post(
                    "/api/chat/otp/send-sms",
                    json={
                        "phone": "+12125550100",
                        "name": "Alice",
                    },
                )

            assert resp.status_code == 200
            data = resp.json()
            assert data["sent"] is False
            assert "Unable to send verification code" in data["message"]
            # Per -002 NO-GO condition 3: assert _send_sms was awaited so the test
            # cannot pass by returning False from an earlier broad-exception path.
            mock_send_sms.assert_awaited_once()

    async def test_verify_sms_wrong_code_increments_attempt_counter(self):
        app = _build_app()
        ctx = _mock_tenant_context()

        mock_container = MagicMock()
        mock_container.read_item = AsyncMock(
            return_value={
                "id": "otp:test-tenant-001:+12125550100",
                "otp_code_hash": "hash:123456",
                "used": False,
                "verify_attempts": 1,
            }
        )
        mock_container.patch_item = AsyncMock(return_value={})

        mock_cosmos = MagicMock()
        mock_cosmos.get_container = MagicMock(return_value=mock_container)

        with (
            patch("src.multi_tenant.cosmos_client.get_cosmos_manager", return_value=mock_cosmos),
            patch("src.multi_tenant.sms_verification.hash_code", side_effect=lambda code: f"hash:{code}"),
        ):
            from src.multi_tenant.middleware import get_tenant_context

            app.dependency_overrides[get_tenant_context] = lambda: ctx

            async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
                resp = await client.post(
                    "/api/chat/otp/verify-sms",
                    json={
                        "phone": "+12125550100",
                        "code": "999999",
                    },
                )

            assert resp.status_code == 200
            data = resp.json()
            assert data["verified"] is False
            mock_container.patch_item.assert_awaited_once_with(
                item="otp:test-tenant-001:+12125550100",
                partition_key=_SMS_OTP_TOKEN_TYPE,
                patch_operations=[
                    {"op": "incr", "path": "/verify_attempts", "value": 1},
                ],
            )
