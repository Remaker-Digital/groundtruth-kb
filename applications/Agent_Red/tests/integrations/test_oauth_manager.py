"""Tests for Multi-Tenant OAuth Manager (SPEC-1764).

Tests cover: state token CSRF, authorization URL generation, callback
handling, token refresh with locking, and revocation.

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

from __future__ import annotations

import time

import pytest

from src.integrations.manifest import AuthConfig
from src.integrations.models import AuthenticationError
from src.integrations.oauth import (
    OAuthManager,
    TokenData,
    create_state_token,
    verify_state_token,
)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

SIGNING_SECRET = "test-secret-key-for-oauth-tests"


@pytest.fixture
def auth_config() -> AuthConfig:
    return AuthConfig(
        scopes=["read", "write"],
        authorize_url="https://vendor.example.com/oauth/authorize",
        token_url="https://vendor.example.com/oauth/token",
        revoke_url="https://vendor.example.com/oauth/revoke",
        client_id_env="test-client-id",
        client_secret_env="test-client-secret",
    )


@pytest.fixture
def oauth_manager() -> OAuthManager:
    return OAuthManager(signing_secret=SIGNING_SECRET)


# ===================================================================
# State Token (CSRF)
# ===================================================================


class TestStateToken:
    """SPEC-1764: Signed JWT state for CSRF protection."""

    def test_create_and_verify(self) -> None:
        """Create a state token and verify it successfully."""
        token = create_state_token("t-1", "zendesk", SIGNING_SECRET)
        payload = verify_state_token(token, SIGNING_SECRET)
        assert payload["tid"] == "t-1"
        assert payload["iid"] == "zendesk"
        assert "nonce" in payload
        assert "exp" in payload

    def test_tampered_token_rejected(self) -> None:
        """Tampered token fails signature verification."""
        token = create_state_token("t-1", "zendesk", SIGNING_SECRET)
        # Tamper with the signature
        tampered = token[:-4] + "xxxx"
        with pytest.raises(AuthenticationError, match="signature"):
            verify_state_token(tampered, SIGNING_SECRET)

    def test_wrong_secret_rejected(self) -> None:
        """Token verified with wrong secret fails."""
        token = create_state_token("t-1", "zendesk", SIGNING_SECRET)
        with pytest.raises(AuthenticationError, match="signature"):
            verify_state_token(token, "wrong-secret")

    def test_expired_token_rejected(self) -> None:
        """Expired state token is rejected."""
        token = create_state_token(
            "t-1", "zendesk", SIGNING_SECRET, expiry_seconds=-1
        )
        with pytest.raises(AuthenticationError, match="expired"):
            verify_state_token(token, SIGNING_SECRET)

    def test_invalid_format_rejected(self) -> None:
        """Malformed token is rejected."""
        with pytest.raises(AuthenticationError):
            verify_state_token("not-a-valid-token", SIGNING_SECRET)

    def test_custom_nonce(self) -> None:
        """Custom nonce is included in the token."""
        token = create_state_token(
            "t-1", "zendesk", SIGNING_SECRET, nonce="my-nonce"
        )
        payload = verify_state_token(token, SIGNING_SECRET)
        assert payload["nonce"] == "my-nonce"


# ===================================================================
# Authorization URL
# ===================================================================


class TestAuthorizationURL:
    """SPEC-1764: Authorization URL generation."""

    def test_generates_valid_url(
        self, oauth_manager: OAuthManager, auth_config: AuthConfig
    ) -> None:
        """URL contains all required OAuth2 parameters."""
        url = oauth_manager.get_authorization_url(
            "t-1",
            "zendesk",
            auth_config,
            redirect_uri="https://app.example.com/callback",
        )
        assert "vendor.example.com/oauth/authorize" in url
        assert "client_id=test-client-id" in url
        assert "response_type=code" in url
        assert "state=" in url
        assert "scope=read+write" in url
        assert "redirect_uri=" in url

    def test_extra_params_included(
        self, oauth_manager: OAuthManager, auth_config: AuthConfig
    ) -> None:
        """Extra parameters are appended to the URL."""
        url = oauth_manager.get_authorization_url(
            "t-1",
            "zendesk",
            auth_config,
            redirect_uri="https://app.example.com/callback",
            extra_params={"access_type": "offline"},
        )
        assert "access_type=offline" in url


# ===================================================================
# Callback Handling
# ===================================================================


class TestCallback:
    """SPEC-1764: OAuth callback handling."""

    @pytest.mark.asyncio
    async def test_callback_exchanges_code(
        self, oauth_manager: OAuthManager, auth_config: AuthConfig
    ) -> None:
        """Callback verifies state and exchanges code for tokens."""
        state = create_state_token("t-1", "zendesk", SIGNING_SECRET)
        token = await oauth_manager.handle_callback(
            state=state,
            code="auth-code-12345",
            auth_config=auth_config,
            redirect_uri="https://app.example.com/callback",
        )
        assert token.access_token.startswith("access_")
        assert token.refresh_token.startswith("refresh_")
        assert oauth_manager.has_token("t-1", "zendesk")

    @pytest.mark.asyncio
    async def test_callback_invalid_state_rejected(
        self, oauth_manager: OAuthManager, auth_config: AuthConfig
    ) -> None:
        """Callback with invalid state raises AuthenticationError."""
        with pytest.raises(AuthenticationError):
            await oauth_manager.handle_callback(
                state="invalid.state",
                code="auth-code",
                auth_config=auth_config,
                redirect_uri="https://app.example.com/callback",
            )


# ===================================================================
# Token Access & Refresh
# ===================================================================


class TestTokenAccess:
    """SPEC-1764: Token access with auto-refresh."""

    @pytest.mark.asyncio
    async def test_get_valid_token(
        self, oauth_manager: OAuthManager, auth_config: AuthConfig
    ) -> None:
        """get_valid_token returns stored token when not expired."""
        # Store a token first
        state = create_state_token("t-1", "zendesk", SIGNING_SECRET)
        await oauth_manager.handle_callback(
            state=state, code="code", auth_config=auth_config,
            redirect_uri="https://cb.example.com",
        )

        token = await oauth_manager.get_valid_token("t-1", "zendesk", auth_config)
        assert token.access_token.startswith("access_")

    @pytest.mark.asyncio
    async def test_missing_token_raises(
        self, oauth_manager: OAuthManager, auth_config: AuthConfig
    ) -> None:
        """get_valid_token raises when no token exists."""
        with pytest.raises(AuthenticationError, match="No OAuth token"):
            await oauth_manager.get_valid_token("t-1", "zendesk", auth_config)

    @pytest.mark.asyncio
    async def test_expired_token_refreshed(
        self, oauth_manager: OAuthManager, auth_config: AuthConfig
    ) -> None:
        """Expired token is automatically refreshed."""
        # Store an expired token
        expired = TokenData(
            access_token="old_access",
            refresh_token="old_refresh",
            expires_at=time.time() - 100,  # Already expired
        )
        oauth_manager._token_store[("t-1", "zendesk")] = expired

        token = await oauth_manager.get_valid_token("t-1", "zendesk", auth_config)
        assert token.access_token.startswith("refreshed_")

    @pytest.mark.asyncio
    async def test_expired_no_refresh_token_raises(
        self, oauth_manager: OAuthManager, auth_config: AuthConfig
    ) -> None:
        """Expired token without refresh_token raises."""
        expired = TokenData(
            access_token="old_access",
            refresh_token="",  # No refresh token
            expires_at=time.time() - 100,
        )
        oauth_manager._token_store[("t-1", "zendesk")] = expired

        with pytest.raises(AuthenticationError, match="no refresh token"):
            await oauth_manager.get_valid_token("t-1", "zendesk", auth_config)


# ===================================================================
# Token Data
# ===================================================================


class TestTokenData:
    """SPEC-1764: TokenData model."""

    def test_is_expired_within_buffer(self) -> None:
        """Token within refresh buffer is considered expired."""
        token = TokenData(
            access_token="test",
            expires_at=time.time() + 60,  # 1 min from now (within 5min buffer)
        )
        assert token.is_expired is True

    def test_is_not_expired(self) -> None:
        """Token well within validity is not expired."""
        token = TokenData(
            access_token="test",
            expires_at=time.time() + 3600,  # 1 hour from now
        )
        assert token.is_expired is False

    def test_no_expiry_not_expired(self) -> None:
        """Token without expiry is never considered expired."""
        token = TokenData(access_token="test", expires_at=0)
        assert token.is_expired is False

    def test_to_dict(self) -> None:
        """TokenData serializes to dict."""
        token = TokenData(
            access_token="a", refresh_token="r", scopes=["read"]
        )
        d = token.to_dict()
        assert d["access_token"] == "a"
        assert d["refresh_token"] == "r"
        assert d["scopes"] == ["read"]


# ===================================================================
# Revocation
# ===================================================================


class TestRevocation:
    """SPEC-1764: Token revocation."""

    @pytest.mark.asyncio
    async def test_revoke_removes_token(
        self, oauth_manager: OAuthManager, auth_config: AuthConfig
    ) -> None:
        """Revocation removes token from store."""
        oauth_manager._token_store[("t-1", "zendesk")] = TokenData(
            access_token="test"
        )
        assert oauth_manager.has_token("t-1", "zendesk")

        result = await oauth_manager.revoke_token("t-1", "zendesk", auth_config)
        assert result is True
        assert not oauth_manager.has_token("t-1", "zendesk")

    @pytest.mark.asyncio
    async def test_revoke_nonexistent_returns_false(
        self, oauth_manager: OAuthManager, auth_config: AuthConfig
    ) -> None:
        """Revoking a nonexistent token returns False."""
        result = await oauth_manager.revoke_token("t-1", "nonexistent", auth_config)
        assert result is False
