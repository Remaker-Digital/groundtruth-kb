"""Tests for forgot-password / reset-password flow.

Validates HMAC-signed tokens work across replicas (no shared in-memory state),
rate limiting, single-use nonce tracking, and email enumeration resistance.

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

import time
from unittest.mock import patch

import pytest


# ---------------------------------------------------------------------------
# Unit tests for HMAC token generation / validation
# ---------------------------------------------------------------------------

@pytest.fixture(autouse=True)
def _ensure_password_hash():
    """Ensure _admin_password_hash and _ADMIN_HMAC_KEY are set for HMAC token tests."""
    import src.app.standalone_auth as m
    original_hash = m._admin_password_hash
    original_hmac_key = m._ADMIN_HMAC_KEY
    if not original_hash:
        h = m.hashlib.sha256(b"agentred-admin:testpw").hexdigest()
        m._admin_password_hash = h
        m._ADMIN_HMAC_KEY = h
    elif not original_hmac_key:
        m._ADMIN_HMAC_KEY = original_hash
    yield
    m._admin_password_hash = original_hash
    m._ADMIN_HMAC_KEY = original_hmac_key
    m._admin_used_reset_nonces.clear()


class TestHMACTokenGeneration:
    """Test _generate_reset_token and _validate_reset_token."""

    def test_generate_token_format(self):
        """Token has three dot-separated parts: nonce.expiry.hmac."""
        from src.main import _generate_reset_token
        token = _generate_reset_token(ttl=60)
        parts = token.split(".")
        assert len(parts) == 3, f"Expected 3 parts, got {len(parts)}"
        nonce, expiry, sig = parts
        assert len(nonce) > 0
        assert int(expiry) > time.time()
        assert len(sig) == 64  # SHA-256 hex digest

    def test_validate_valid_token(self):
        """A freshly generated token is valid."""
        from src.main import _generate_reset_token, _validate_reset_token
        token = _generate_reset_token(ttl=60)
        assert _validate_reset_token(token) is True

    def test_validate_expired_token(self):
        """An expired token is rejected."""
        from src.main import _generate_reset_token, _validate_reset_token
        token = _generate_reset_token(ttl=1)
        # Fast-forward past expiry
        with patch("src.app.standalone_auth._time.time", return_value=time.time() + 10):
            assert _validate_reset_token(token) is False

    def test_validate_tampered_signature(self):
        """A token with a modified signature is rejected."""
        from src.main import _generate_reset_token, _validate_reset_token
        token = _generate_reset_token(ttl=60)
        parts = token.split(".")
        parts[2] = "a" * 64  # bogus sig
        tampered = ".".join(parts)
        assert _validate_reset_token(tampered) is False

    def test_validate_tampered_expiry(self):
        """Extending the expiry invalidates the HMAC."""
        from src.main import _generate_reset_token, _validate_reset_token
        token = _generate_reset_token(ttl=60)
        parts = token.split(".")
        parts[1] = str(int(time.time()) + 999999)  # extend expiry
        tampered = ".".join(parts)
        assert _validate_reset_token(tampered) is False

    def test_validate_empty_token(self):
        from src.main import _validate_reset_token
        assert _validate_reset_token("") is False

    def test_validate_garbage_token(self):
        from src.main import _validate_reset_token
        assert _validate_reset_token("not-a-valid-token") is False

    def test_validate_wrong_part_count(self):
        from src.main import _validate_reset_token
        assert _validate_reset_token("a.b") is False
        assert _validate_reset_token("a.b.c.d") is False

    def test_single_use_nonce(self):
        """After marking a nonce as used, the same token is rejected."""
        from src.main import (
            _generate_reset_token,
            _validate_reset_token,
            _admin_used_reset_nonces,
        )
        token = _generate_reset_token(ttl=60)
        nonce = token.split(".")[0]
        assert _validate_reset_token(token) is True
        # Mark as used
        _admin_used_reset_nonces.add(nonce)
        assert _validate_reset_token(token) is False

    def test_different_tokens_unique(self):
        """Each call generates a unique token."""
        from src.main import _generate_reset_token
        tokens = {_generate_reset_token(ttl=60) for _ in range(10)}
        assert len(tokens) == 10


# ---------------------------------------------------------------------------
# Integration tests for forgot-password endpoints
# ---------------------------------------------------------------------------

@pytest.fixture()
def standalone_client():
    """Create a test client with admin password configured."""
    import src.main as main_mod
    import src.app.standalone_auth as auth_mod

    # Ensure admin password is set for testing — mutate on the auth module
    # where the route handlers actually read mutable state.
    original_pw = auth_mod._ADMIN_INITIAL_PASSWORD
    original_hash = auth_mod._admin_password_hash
    original_hmac_key = auth_mod._ADMIN_HMAC_KEY
    original_email = auth_mod._ADMIN_RESET_EMAIL

    test_hash = auth_mod.hashlib.sha256(
        b"agentred-admin:testpassword",
    ).hexdigest()
    auth_mod._ADMIN_INITIAL_PASSWORD = "testpassword"
    auth_mod._admin_password_hash = auth_mod._hash_password("testpassword")
    auth_mod._ADMIN_HMAC_KEY = test_hash
    auth_mod._ADMIN_RESET_EMAIL = "admin@test.com"

    from fastapi.testclient import TestClient
    with TestClient(main_mod.app) as client:
        yield client

    # Restore
    auth_mod._ADMIN_INITIAL_PASSWORD = original_pw
    auth_mod._admin_password_hash = original_hash
    auth_mod._ADMIN_HMAC_KEY = original_hmac_key
    auth_mod._ADMIN_RESET_EMAIL = original_email
    auth_mod._admin_used_reset_nonces.clear()
    # Rate limit state now in shared backend (SPEC-1691)
    from src.multi_tenant.security_hardening import get_rate_limit_backend
    backend = get_rate_limit_backend()
    if hasattr(backend, "_windows"):
        backend._windows.clear()


def _get_csrf(client, url):
    """GET a page to obtain CSRF cookie."""
    resp = client.get(url)
    return resp.cookies.get("agentred_csrf", "")


class TestForgotPasswordEndpoints:
    """Integration tests for the forgot/reset password flow."""

    def test_get_forgot_password_form(self, standalone_client):
        """GET forgot-password returns the form."""
        resp = standalone_client.get("/admin/standalone/_forgot-password")
        assert resp.status_code == 200
        assert "email" in resp.text.lower()

    def test_post_forgot_password_valid_email(self, standalone_client):
        """POST with matching email returns success page (no email enumeration)."""
        csrf = _get_csrf(standalone_client, "/admin/standalone/_forgot-password")
        with patch("src.app.standalone_auth._send_admin_reset_email", return_value=True) as mock_send:
            resp = standalone_client.post(
                "/admin/standalone/_forgot-password",
                data={"email": "admin@test.com", "csrf_token": csrf},
                cookies={"agentred_csrf": csrf},
            )
        assert resp.status_code == 200
        assert mock_send.called
        # Verify reset URL contains HMAC token format
        call_args = mock_send.call_args
        reset_url = call_args[0][1]
        token = reset_url.split("token=")[1]
        assert len(token.split(".")) == 3  # nonce.expiry.hmac

    def test_post_forgot_password_wrong_email(self, standalone_client):
        """POST with non-matching email still returns success (anti-enumeration)."""
        csrf = _get_csrf(standalone_client, "/admin/standalone/_forgot-password")
        with patch("src.app.standalone_auth._send_admin_reset_email") as mock_send:
            resp = standalone_client.post(
                "/admin/standalone/_forgot-password",
                data={"email": "wrong@example.com", "csrf_token": csrf},
                cookies={"agentred_csrf": csrf},
            )
        assert resp.status_code == 200
        assert not mock_send.called

    def test_post_forgot_password_invalid_email(self, standalone_client):
        """POST with invalid email returns error."""
        csrf = _get_csrf(standalone_client, "/admin/standalone/_forgot-password")
        resp = standalone_client.post(
            "/admin/standalone/_forgot-password",
            data={"email": "not-an-email", "csrf_token": csrf},
            cookies={"agentred_csrf": csrf},
        )
        assert resp.status_code == 400

    def test_rate_limit_forgot_password(self, standalone_client):
        """Fourth request within 5 minutes returns 429."""
        from src.multi_tenant.security_hardening import get_rate_limit_backend
        backend = get_rate_limit_backend()
        if hasattr(backend, "_windows"):
            backend._windows.clear()

        with patch("src.app.standalone_auth._send_admin_reset_email", return_value=True):
            for _ in range(3):
                csrf = _get_csrf(standalone_client, "/admin/standalone/_forgot-password")
                resp = standalone_client.post(
                    "/admin/standalone/_forgot-password",
                    data={"email": "admin@test.com", "csrf_token": csrf},
                    cookies={"agentred_csrf": csrf},
                )
                assert resp.status_code == 200

            # Fourth should be rate-limited
            csrf = _get_csrf(standalone_client, "/admin/standalone/_forgot-password")
            resp = standalone_client.post(
                "/admin/standalone/_forgot-password",
                data={"email": "admin@test.com", "csrf_token": csrf},
                cookies={"agentred_csrf": csrf},
            )
            assert resp.status_code == 429

    def test_reset_password_with_valid_token(self, standalone_client):
        """Full flow: generate token, GET form, POST new password -> auto-login."""
        from src.main import _generate_reset_token
        token = _generate_reset_token(ttl=60)

        # GET the reset form (also sets CSRF cookie)
        resp = standalone_client.get(
            f"/admin/standalone/_reset-password?token={token}",
        )
        assert resp.status_code == 200
        assert token in resp.text or "new_password" in resp.text.lower()
        csrf = resp.cookies.get("agentred_csrf", "")

        # POST the new password -> auto-login redirect with cookie
        resp = standalone_client.post(
            "/admin/standalone/_reset-password",
            data={"token": token, "new_password": "newpassword123", "confirm_password": "newpassword123", "csrf_token": csrf},
            cookies={"agentred_csrf": csrf},
            follow_redirects=False,
        )
        assert resp.status_code == 303
        assert resp.headers.get("location") == "/admin/standalone/"
        assert "agentred_admin=" in resp.headers.get("set-cookie", "")

    def test_reset_password_with_invalid_token(self, standalone_client):
        """Reset with invalid token returns 400."""
        resp = standalone_client.get(
            "/admin/standalone/_reset-password?token=bad.token.value",
        )
        assert resp.status_code == 400

    def test_reset_password_mismatch(self, standalone_client):
        """Mismatched passwords return 400."""
        from src.main import _generate_reset_token
        token = _generate_reset_token(ttl=60)

        csrf = _get_csrf(standalone_client, f"/admin/standalone/_reset-password?token={token}")
        resp = standalone_client.post(
            "/admin/standalone/_reset-password",
            data={"token": token, "new_password": "newpassword123", "confirm_password": "newpassword456", "csrf_token": csrf},
            cookies={"agentred_csrf": csrf},
        )
        assert resp.status_code == 400

    def test_reset_password_too_short(self, standalone_client):
        """Password under 12 chars returns 400 (SPEC-1691)."""
        from src.main import _generate_reset_token
        token = _generate_reset_token(ttl=60)

        csrf = _get_csrf(standalone_client, f"/admin/standalone/_reset-password?token={token}")
        resp = standalone_client.post(
            "/admin/standalone/_reset-password",
            data={"token": token, "new_password": "short12345", "confirm_password": "short12345", "csrf_token": csrf},
            cookies={"agentred_csrf": csrf},
        )
        assert resp.status_code == 400

    def test_token_single_use(self, standalone_client):
        """After successful reset, the same token cannot be reused."""
        from src.main import _generate_reset_token
        token = _generate_reset_token(ttl=60)

        # First use succeeds (303 redirect = auto-login)
        csrf = _get_csrf(standalone_client, f"/admin/standalone/_reset-password?token={token}")
        resp = standalone_client.post(
            "/admin/standalone/_reset-password",
            data={"token": token, "new_password": "newpassword123", "confirm_password": "newpassword123", "csrf_token": csrf},
            cookies={"agentred_csrf": csrf},
            follow_redirects=False,
        )
        assert resp.status_code == 303

        # Second use fails (nonce tracked)
        resp = standalone_client.post(
            "/admin/standalone/_reset-password",
            data={"token": token, "new_password": "anotherpass123", "confirm_password": "anotherpass123", "csrf_token": csrf},
            cookies={"agentred_csrf": csrf},
        )
        assert resp.status_code == 400
