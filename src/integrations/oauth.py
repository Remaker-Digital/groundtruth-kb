"""Multi-Tenant OAuth Manager (SPEC-1764).

Manages OAuth2 authorization code flows for external integrations.
Each (tenant, integration) pair gets isolated token storage with
automatic refresh and CSRF protection via signed JWT state.

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

from __future__ import annotations

import asyncio
import hashlib
import hmac
import json
import logging
import secrets
import time
from typing import Any
from urllib.parse import urlencode

from src.integrations.manifest import AuthConfig, AuthType
from src.integrations.models import AuthenticationError, IntegrationError

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

STATE_EXPIRY_SECONDS = 600  # 10 minutes
TOKEN_REFRESH_BUFFER_SECONDS = 300  # Refresh 5 min before expiry


# ---------------------------------------------------------------------------
# State token (CSRF protection)
# ---------------------------------------------------------------------------


def create_state_token(
    tenant_id: str,
    integration_id: str,
    signing_secret: str,
    *,
    nonce: str | None = None,
    expiry_seconds: int = STATE_EXPIRY_SECONDS,
) -> str:
    """Create a signed state token for OAuth CSRF protection.

    The token is a base64url-encoded JSON payload with HMAC-SHA256 signature.
    Contains: tenant_id, integration_id, nonce, exp (expiry timestamp).
    """
    if nonce is None:
        nonce = secrets.token_urlsafe(16)

    payload = {
        "tid": tenant_id,
        "iid": integration_id,
        "nonce": nonce,
        "exp": int(time.time()) + expiry_seconds,
    }
    payload_json = json.dumps(payload, separators=(",", ":"), sort_keys=True)

    signature = hmac.new(
        signing_secret.encode(),
        payload_json.encode(),
        hashlib.sha256,
    ).hexdigest()

    # Combine as payload.signature
    import base64

    encoded_payload = base64.urlsafe_b64encode(payload_json.encode()).decode().rstrip("=")
    return f"{encoded_payload}.{signature}"


def verify_state_token(
    state: str,
    signing_secret: str,
) -> dict[str, Any]:
    """Verify and decode a state token.

    Returns the payload dict if valid.
    Raises AuthenticationError if invalid or expired.
    """
    import base64

    parts = state.rsplit(".", 1)
    if len(parts) != 2:
        raise AuthenticationError("Invalid state token format")

    encoded_payload, provided_sig = parts

    # Restore base64 padding
    padded = encoded_payload + "=" * (4 - len(encoded_payload) % 4)
    try:
        payload_json = base64.urlsafe_b64decode(padded).decode()
    except Exception:
        raise AuthenticationError("Invalid state token encoding")

    # Verify signature
    expected_sig = hmac.new(
        signing_secret.encode(),
        payload_json.encode(),
        hashlib.sha256,
    ).hexdigest()

    if not hmac.compare_digest(provided_sig, expected_sig):
        raise AuthenticationError("Invalid state token signature")

    payload = json.loads(payload_json)

    # Check expiry
    if payload.get("exp", 0) < time.time():
        raise AuthenticationError("State token expired")

    return payload


# ---------------------------------------------------------------------------
# Token storage interface
# ---------------------------------------------------------------------------


class TokenData:
    """OAuth token data container."""

    __slots__ = (
        "access_token",
        "refresh_token",
        "token_type",
        "expires_at",
        "scopes",
        "raw",
    )

    def __init__(
        self,
        access_token: str,
        refresh_token: str = "",
        token_type: str = "Bearer",
        expires_at: float = 0.0,
        scopes: list[str] | None = None,
        raw: dict[str, Any] | None = None,
    ):
        self.access_token = access_token
        self.refresh_token = refresh_token
        self.token_type = token_type
        self.expires_at = expires_at
        self.scopes = scopes or []
        self.raw = raw or {}

    @property
    def is_expired(self) -> bool:
        """Check if the token is expired (with buffer)."""
        if self.expires_at <= 0:
            return False  # No expiry set
        return time.time() >= (self.expires_at - TOKEN_REFRESH_BUFFER_SECONDS)

    def to_dict(self) -> dict[str, Any]:
        return {
            "access_token": self.access_token,
            "refresh_token": self.refresh_token,
            "token_type": self.token_type,
            "expires_at": self.expires_at,
            "scopes": self.scopes,
        }


# ---------------------------------------------------------------------------
# OAuth Manager
# ---------------------------------------------------------------------------


class OAuthManager:
    """Multi-tenant OAuth2 flow manager.

    Handles authorization URL generation, callback processing, token
    storage/refresh, and revocation.  Uses an in-memory token store
    by default (production uses CredentialVault via SPEC-1765).
    """

    def __init__(
        self,
        signing_secret: str = "",
        token_store: dict[tuple[str, str], TokenData] | None = None,
    ):
        self._signing_secret = signing_secret or secrets.token_urlsafe(32)
        self._token_store: dict[tuple[str, str], TokenData] = (
            token_store if token_store is not None else {}
        )
        # Per-(tenant, integration) lock to prevent concurrent refresh races
        self._refresh_locks: dict[tuple[str, str], asyncio.Lock] = {}

    def _get_lock(self, tenant_id: str, integration_id: str) -> asyncio.Lock:
        key = (tenant_id, integration_id)
        if key not in self._refresh_locks:
            self._refresh_locks[key] = asyncio.Lock()
        return self._refresh_locks[key]

    # -- Authorization URL --------------------------------------------------

    def get_authorization_url(
        self,
        tenant_id: str,
        integration_id: str,
        auth_config: AuthConfig,
        *,
        redirect_uri: str,
        extra_params: dict[str, str] | None = None,
    ) -> str:
        """Generate an OAuth2 authorization URL with CSRF state.

        Args:
            tenant_id: Tenant requesting authorization.
            integration_id: Integration being connected.
            auth_config: Auth configuration from manifest.
            redirect_uri: OAuth callback URL.
            extra_params: Additional query parameters.

        Returns:
            Full authorization URL with state parameter.
        """
        state = create_state_token(
            tenant_id, integration_id, self._signing_secret
        )

        params = {
            "client_id": auth_config.client_id_env,
            "redirect_uri": redirect_uri,
            "response_type": "code",
            "state": state,
        }
        if auth_config.scopes:
            params["scope"] = " ".join(auth_config.scopes)
        if extra_params:
            params.update(extra_params)

        return f"{auth_config.authorize_url}?{urlencode(params)}"

    # -- Callback -----------------------------------------------------------

    async def handle_callback(
        self,
        state: str,
        code: str,
        auth_config: AuthConfig,
        *,
        redirect_uri: str,
    ) -> TokenData:
        """Handle OAuth2 callback: validate state, exchange code for tokens.

        Args:
            state: State parameter from callback.
            code: Authorization code from callback.
            auth_config: Auth configuration from manifest.
            redirect_uri: Same redirect_uri used in authorization.

        Returns:
            TokenData with access and refresh tokens.
        """
        # Verify CSRF state
        payload = verify_state_token(state, self._signing_secret)
        tenant_id = payload["tid"]
        integration_id = payload["iid"]

        # Exchange code for tokens (placeholder — production uses httpx)
        token_data = await self._exchange_code(
            code, auth_config, redirect_uri=redirect_uri
        )

        # Store tokens
        key = (tenant_id, integration_id)
        self._token_store[key] = token_data

        logger.info(
            "OAuth tokens stored: tenant=%s integration=%s scopes=%s",
            tenant_id,
            integration_id,
            token_data.scopes,
        )
        return token_data

    async def _exchange_code(
        self,
        code: str,
        auth_config: AuthConfig,
        *,
        redirect_uri: str,
    ) -> TokenData:
        """Exchange authorization code for tokens.

        In production, this calls the token endpoint via httpx.
        For testing, returns a mock token.
        """
        # Placeholder — real implementation uses httpx POST to auth_config.token_url
        return TokenData(
            access_token=f"access_{code[:8]}",
            refresh_token=f"refresh_{code[:8]}",
            token_type="Bearer",
            expires_at=time.time() + 3600,
            scopes=auth_config.scopes,
        )

    # -- Token Access -------------------------------------------------------

    async def get_valid_token(
        self,
        tenant_id: str,
        integration_id: str,
        auth_config: AuthConfig,
    ) -> TokenData:
        """Get a valid access token, refreshing if necessary.

        Uses per-(tenant, integration) locking to prevent concurrent
        refresh races.
        """
        key = (tenant_id, integration_id)
        token = self._token_store.get(key)

        if token is None:
            raise AuthenticationError(
                f"No OAuth token for tenant={tenant_id} integration={integration_id}",
                integration_id=integration_id,
            )

        if not token.is_expired:
            return token

        # Token expired — refresh with lock
        lock = self._get_lock(tenant_id, integration_id)
        async with lock:
            # Double-check after acquiring lock
            token = self._token_store.get(key)
            if token and not token.is_expired:
                return token

            if not token or not token.refresh_token:
                raise AuthenticationError(
                    "Token expired and no refresh token available",
                    integration_id=integration_id,
                )

            refreshed = await self._refresh_token(token, auth_config)
            self._token_store[key] = refreshed
            logger.info(
                "Token refreshed: tenant=%s integration=%s",
                tenant_id,
                integration_id,
            )
            return refreshed

    async def _refresh_token(
        self,
        token: TokenData,
        auth_config: AuthConfig,
    ) -> TokenData:
        """Refresh an expired token.

        In production, calls the token endpoint with grant_type=refresh_token.
        """
        # Placeholder — real implementation uses httpx POST
        return TokenData(
            access_token=f"refreshed_{token.access_token[-8:]}",
            refresh_token=token.refresh_token,
            token_type=token.token_type,
            expires_at=time.time() + 3600,
            scopes=token.scopes,
        )

    # -- Revocation ---------------------------------------------------------

    async def revoke_token(
        self,
        tenant_id: str,
        integration_id: str,
        auth_config: AuthConfig,
    ) -> bool:
        """Revoke tokens for a tenant's integration.

        Removes from local store and calls revocation endpoint if available.
        """
        key = (tenant_id, integration_id)
        token = self._token_store.pop(key, None)
        self._refresh_locks.pop(key, None)

        if token and auth_config.revoke_url:
            # Placeholder — real implementation calls revoke endpoint
            logger.info(
                "Token revoked: tenant=%s integration=%s",
                tenant_id,
                integration_id,
            )

        return token is not None

    # -- Status -------------------------------------------------------------

    def has_token(self, tenant_id: str, integration_id: str) -> bool:
        """Check if a token exists for a tenant's integration."""
        return (tenant_id, integration_id) in self._token_store

    def token_count(self) -> int:
        """Total stored tokens."""
        return len(self._token_store)
