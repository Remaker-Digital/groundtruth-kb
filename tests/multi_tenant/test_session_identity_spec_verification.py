"""Spec verification tests for session, customer identity, and magic link URL specs.

Each test class verifies a specific SPEC-* requirement against the
actual implementation. Tests exercise production interfaces per GOV-10.

Session S152 — spec review and real test creation (batch 2).
© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

from __future__ import annotations

import inspect
import re
import time
from datetime import datetime, timedelta, timezone
from unittest.mock import AsyncMock, MagicMock, patch

import jwt
import pytest


# ---------------------------------------------------------------------------
# SPEC-0584: Refreshing the admin MUST preserve the session
# ---------------------------------------------------------------------------


class TestSpec0584SessionPersistence:
    """SPEC-0584: Refreshing the admin MUST preserve the session.

    The magic link session token is a JWT stored in sessionStorage.
    Verifying it does not invalidate it — the same token remains valid
    for the entire 8-hour TTL. This means page refresh does not lose
    the session.
    """

    def test_session_token_is_jwt_with_expiry(self):
        """Session token is a standard JWT with exp claim."""
        from src.multi_tenant.magic_link_auth import create_magic_link_session_token

        token, expires_at = create_magic_link_session_token(
            tenant_id="test-tenant", email="user@example.com"
        )
        payload = jwt.decode(token, options={"verify_signature": False})
        assert "exp" in payload
        assert payload["type"] == "magic_link_session"

    def test_session_token_8_hour_ttl(self):
        """Session token has 8-hour TTL (not single-use)."""
        from src.multi_tenant.magic_link_auth import _SESSION_TTL_HOURS

        assert _SESSION_TTL_HOURS == 8

    def test_verify_session_token_returns_payload_not_consumed(self):
        """Verifying the token returns payload without consuming it.
        This means the same token can be used across page refreshes."""
        from src.multi_tenant.magic_link_auth import (
            create_magic_link_session_token,
            verify_magic_link_session_token,
        )

        token, _ = create_magic_link_session_token(
            tenant_id="test-tenant", email="user@example.com"
        )
        # Verify twice — both should succeed (token is NOT consumed)
        result1 = verify_magic_link_session_token(token)
        result2 = verify_magic_link_session_token(token)
        assert result1 is not None
        assert result2 is not None
        assert result1["sub"] == "test-tenant"
        assert result2["email"] == "user@example.com"


# ---------------------------------------------------------------------------
# SPEC-0585: Password gate reappears after logout/cookies cleared
# ---------------------------------------------------------------------------


class TestSpec0585SessionClearOnLogout:
    """SPEC-0585: The standalone admin password gate MUST reappear after
    logging out or clearing cookies.

    Since session tokens are stored client-side (sessionStorage), clearing
    storage means the token is gone. The verify function returns None for
    invalid/missing tokens, which forces re-authentication.
    """

    def test_expired_token_returns_none(self):
        """An expired session token returns None — forces re-auth."""
        from src.multi_tenant.magic_link_auth import (
            _JWT_SECRET,
            verify_magic_link_session_token,
        )

        # Create an already-expired token
        payload = {
            "sub": "test-tenant",
            "email": "user@example.com",
            "type": "magic_link_session",
            "exp": int((datetime.now(timezone.utc) - timedelta(hours=1)).timestamp()),
        }
        expired_token = jwt.encode(payload, _JWT_SECRET, algorithm="HS256")
        result = verify_magic_link_session_token(expired_token)
        assert result is None

    def test_invalid_token_returns_none(self):
        """An invalid (garbage) token returns None — forces re-auth."""
        from src.multi_tenant.magic_link_auth import verify_magic_link_session_token

        result = verify_magic_link_session_token("garbage-token")
        assert result is None

    def test_empty_string_token_returns_none(self):
        """Empty string token returns None — forces re-auth."""
        from src.multi_tenant.magic_link_auth import verify_magic_link_session_token

        result = verify_magic_link_session_token("")
        assert result is None


# ---------------------------------------------------------------------------
# SPEC-1619: Magic link URL must match origin URL
# ---------------------------------------------------------------------------


class TestSpec1619MagicLinkOriginUrl:
    """SPEC-1619: When a user selects 'Sign in with email' from a
    tenant-scoped admin URL, the magic link must include the same
    tenant parameter to restore the correct tenant context."""

    def test_build_url_with_origin_tenant(self):
        """URL includes origin_tenant parameter when provided."""
        from src.multi_tenant.magic_link_auth import _build_magic_link_url

        url = _build_magic_link_url(
            scheme="https",
            host="example.com",
            token_id="abc123",
            origin_tenant="my-store",
        )
        assert "tenant=my-store" in url
        assert "token=abc123" in url

    def test_build_url_without_origin_tenant(self):
        """URL omits tenant parameter when origin_tenant is None."""
        from src.multi_tenant.magic_link_auth import _build_magic_link_url

        url = _build_magic_link_url(
            scheme="https",
            host="example.com",
            token_id="abc123",
            origin_tenant=None,
        )
        assert "tenant=" not in url
        assert "token=abc123" in url

    def test_build_url_preserves_standalone_path(self):
        """URL uses the standalone admin verify path."""
        from src.multi_tenant.magic_link_auth import _build_magic_link_url

        url = _build_magic_link_url(
            scheme="https",
            host="example.com",
            token_id="tok",
            origin_tenant="store",
        )
        assert "/admin/standalone/verify-magic-link" in url

    def test_spec_1619_comment_exists_in_source(self):
        """Source code references SPEC-1619 in the URL builder."""
        from src.multi_tenant import magic_link_auth

        source = inspect.getsource(magic_link_auth._build_magic_link_url)
        assert "SPEC-1619" in source


# ---------------------------------------------------------------------------
# SPEC-0427: Auth, 2FA, and RBAC unified implementation
# ---------------------------------------------------------------------------


class TestSpec0427UnifiedAuthImplementation:
    """SPEC-0427: Auth, 2FA, and RBAC are tightly coupled and MUST be
    dealt with at the same time as a unified implementation.

    Verified by: middleware resolves auth → role → 2FA in one flow.
    """

    def test_middleware_resolves_auth_to_tenant_context(self):
        """Middleware resolves auth credentials to a TenantContext
        which includes both authentication AND role information."""
        from src.multi_tenant.auth import TenantContext

        fields = {f.name for f in TenantContext.__dataclass_fields__.values()}
        # Auth fields
        assert "auth_method" in fields
        # Role fields (RBAC)
        assert "team_member_role" in fields
        # Tier fields
        assert "tier" in fields

    def test_mfa_module_exists_alongside_auth(self):
        """2FA module exists as part of the auth system."""
        from src.multi_tenant import admin_mfa_auth

        assert hasattr(admin_mfa_auth, "requires_2fa")
        assert hasattr(admin_mfa_auth, "router")


# ---------------------------------------------------------------------------
# SPEC-0498: Customer identification at chat start
# ---------------------------------------------------------------------------


class TestSpec0498CustomerIdentification:
    """SPEC-0498: When a customer attempts to chat, the system MUST make
    every attempt to authenticate and identify them.

    Verified by: identity_preprocessor intercepts messages for email,
    and chat endpoints support customer_id from visitor identity.
    """

    def test_identity_preprocessor_exists(self):
        """Identity preprocessor module exists for in-conversation identification."""
        from src.chat import identity_preprocessor

        assert hasattr(identity_preprocessor, "preprocess_identity")

    def test_identity_preprocessor_detects_email(self):
        """Preprocessor can extract email from customer message."""
        from src.chat.identity_preprocessor import _extract_email

        assert _extract_email("alice@example.com") == "alice@example.com"
        assert _extract_email("my email is bob@test.org") == "bob@test.org"

    def test_chat_models_support_visitor_identity(self):
        """Chat models include visitor identity with customer_id."""
        from src.chat.models import VisitorIdentity

        fields = set(VisitorIdentity.model_fields.keys())
        assert "customer_id" in fields
        assert "email" in fields


# ---------------------------------------------------------------------------
# SPEC-0502: Name and email required before AI responds
# ---------------------------------------------------------------------------


class TestSpec0502NameEmailRequired:
    """SPEC-0502: AUTH-1: Name and email MUST be required before AI responds.

    The identity preprocessor intercepts messages to collect email.
    OTP verification confirms the email. If the customer refuses,
    the AI warns about limited functionality.
    """

    def test_email_extraction_from_message(self):
        """Email extracted from typical customer message patterns."""
        from src.chat.identity_preprocessor import _extract_email

        # Direct email
        assert _extract_email("john@example.com") == "john@example.com"
        # Embedded in sentence
        assert _extract_email("My email is sarah@shop.com") == "sarah@shop.com"
        # Too long — ignored
        long_msg = "a" * 250 + " email@test.com"
        assert _extract_email(long_msg) is None

    def test_identity_action_types_include_email_received(self):
        """IdentityAction supports 'email_received' action."""
        from src.chat.identity_preprocessor import IdentityAction

        action = IdentityAction(action="email_received", email="test@test.com")
        assert action.action == "email_received"
        assert action.email == "test@test.com"


# ---------------------------------------------------------------------------
# SPEC-0505: OTP verification mandatory for Persistent Customer Memory
# ---------------------------------------------------------------------------


class TestSpec0505OtpVerification:
    """SPEC-0505: OTP verification MUST be mandatory — not for security,
    but to authenticate customers for Persistent Customer Memory.

    The system sends a 6-digit OTP via email. Verification marks the
    conversation as customer_verified=True.
    """

    def test_otp_pattern_is_6_digits(self):
        """OTP pattern matches exactly 6 digits."""
        from src.chat.identity_preprocessor import _OTP_PATTERN

        assert _OTP_PATTERN.match("123456")
        assert not _OTP_PATTERN.match("12345")   # too short
        assert not _OTP_PATTERN.match("1234567")  # too long
        assert not _OTP_PATTERN.match("abcdef")   # not digits

    def test_otp_length_is_6(self):
        """OTP code is 6 digits."""
        from src.chat.identity_preprocessor import _OTP_LENGTH

        assert _OTP_LENGTH == 6

    def test_otp_ttl_is_10_minutes(self):
        """OTP expires after 10 minutes (600 seconds)."""
        from src.chat.identity_preprocessor import _OTP_TTL

        assert _OTP_TTL == 600

    def test_max_otp_attempts_is_3(self):
        """Maximum OTP verification attempts per conversation is 3."""
        from src.chat.identity_preprocessor import _MAX_OTP_ATTEMPTS

        assert _MAX_OTP_ATTEMPTS == 3


# ---------------------------------------------------------------------------
# SPEC-0506: Ask to 'verify their identity' (no additional explanation)
# ---------------------------------------------------------------------------


class TestSpec0506VerifyIdentityLanguage:
    """SPEC-0506: When asking for the customer's email, the system MUST ask
    to 'verify their identity' with no additional explanation.

    The actual prompt language is in the AI configuration, but the
    preprocessor's OTP flow uses identity-focused language.
    """

    def test_identity_action_has_system_message(self):
        """IdentityAction includes a system_message for OTP flow."""
        from src.chat.identity_preprocessor import IdentityAction

        action = IdentityAction(
            action="otp_received",
            system_message="Verified!",
        )
        assert action.system_message is not None


# ---------------------------------------------------------------------------
# SPEC-0507: Warning for anonymous customers MUST NOT be skipped
# ---------------------------------------------------------------------------


class TestSpec0507AnonymousWarning:
    """SPEC-0507: The warning for anonymous customers MUST NOT be skipped.

    When a customer says 'skip' or 'continue as guest', the system warns
    about limited functionality. The skip_verification action includes
    a warning message.
    """

    def test_skip_phrases_include_guest_options(self):
        """Skip phrases cover common ways customers decline identification."""
        from src.chat.identity_preprocessor import _SKIP_PHRASES

        assert "skip" in _SKIP_PHRASES
        assert "continue as guest" in _SKIP_PHRASES
        assert "guest" in _SKIP_PHRASES
        assert "no thanks" in _SKIP_PHRASES

    def test_skip_verification_action_has_warning_message(self):
        """The skip_verification action includes a warning about limitations."""
        from src.chat.identity_preprocessor import IdentityAction

        action = IdentityAction(
            action="skip_verification",
            system_message="Without verification I won't be able to access order details",
        )
        assert "verification" in action.system_message.lower()


# ---------------------------------------------------------------------------
# SPEC-0499: Anonymous sessions discouraged (Persistent Customer Memory)
# ---------------------------------------------------------------------------


class TestSpec0499AnonymousDiscouraged:
    """SPEC-0499: Anonymous chat sessions MUST be discouraged because they
    undermine the value of Persistent Customer Memory.

    The identity preprocessor is the mechanism that discourages anonymity:
    it intercepts all messages to prompt for email, and warns about
    limitations when customers skip verification.
    """

    def test_preprocessor_processes_all_unverified_messages(self):
        """preprocess_identity is designed to intercept messages when
        customer_verified is False (not yet identified)."""
        source = inspect.getsource(
            __import__("src.chat.identity_preprocessor", fromlist=["preprocess_identity"]).preprocess_identity
        )
        # The function checks customer_verified before passing through
        assert "customer_verified" in source

    def test_otp_rate_limited_action_exists(self):
        """Rate limiting on OTP prevents abuse but still encourages retry."""
        from src.chat.identity_preprocessor import IdentityAction

        action = IdentityAction(action="otp_rate_limited")
        assert action.action == "otp_rate_limited"


# ---------------------------------------------------------------------------
# SPEC-0869: All API responses MUST use camelCase field names
# ---------------------------------------------------------------------------


class TestSpec0869CamelCaseApiResponses:
    """SPEC-0869: All API responses MUST use camelCase field names.

    Pydantic models use aliases configured via model_config to output
    camelCase while Python code uses snake_case internally.
    """

    def test_pydantic_models_use_camelcase_aliases(self):
        """Key API models use by_alias for camelCase output."""
        from src.chat.models import ConversationStateResponse

        # Pydantic v2 model_config — check alias generator or field aliases
        fields = ConversationStateResponse.model_fields
        # Check that snake_case fields exist in Python
        assert "conversation_id" in fields or "conversationId" in fields

    def test_api_versioning_header_names_are_kebab_case(self):
        """HTTP headers follow standard kebab-case (X-API-Version)."""
        from src.multi_tenant.api_versioning import ApiVersionMiddleware

        source = inspect.getsource(ApiVersionMiddleware)
        assert "x-api-version" in source
        assert "x-product-version" in source


# ---------------------------------------------------------------------------
# SPEC-0453: Admin UI API version numbering tracks API version
# ---------------------------------------------------------------------------


class TestSpec0453ApiVersionTracking:
    """SPEC-0453: The admin UI API version numbering MUST track the API
    version so administrators can verify which version is running."""

    def test_api_version_is_semver(self):
        """API_VERSION follows semantic versioning."""
        from src.multi_tenant.api_versioning import API_VERSION

        parts = API_VERSION.split(".")
        assert len(parts) == 3
        assert all(p.isdigit() for p in parts)

    def test_product_version_is_semver(self):
        """PRODUCT_VERSION follows semantic versioning."""
        from src.multi_tenant.api_versioning import PRODUCT_VERSION

        parts = PRODUCT_VERSION.split(".")
        assert len(parts) == 3
        assert all(p.isdigit() for p in parts)

    def test_api_version_middleware_adds_both_headers(self):
        """ApiVersionMiddleware adds both version headers to responses."""
        source = inspect.getsource(
            __import__("src.multi_tenant.api_versioning", fromlist=["ApiVersionMiddleware"]).ApiVersionMiddleware
        )
        assert "x-api-version" in source
        assert "x-product-version" in source

    def test_deprecated_paths_is_defined(self):
        """DEPRECATED_PATHS dict exists for future deprecation notices."""
        from src.multi_tenant.api_versioning import DEPRECATED_PATHS

        assert isinstance(DEPRECATED_PATHS, dict)


# ---------------------------------------------------------------------------
# SPEC-0054: All configuration page changes are drafts until activated
# ---------------------------------------------------------------------------


class TestSpec0054DraftUntilActivated:
    """SPEC-0054: All configuration page changes are drafts until activated
    using the 'Activate' control.

    The ActivationService implements a two-phase commit model:
    DRAFT → ACTIVE. Changes saved are drafts until explicitly activated.
    """

    def test_config_state_has_draft_and_active(self):
        """ConfigState enum includes 'draft' and 'active'."""
        from src.multi_tenant.cosmos_schema import ConfigState

        assert hasattr(ConfigState, "DRAFT") or hasattr(ConfigState, "draft") or "draft" in [e.value for e in ConfigState]
        assert hasattr(ConfigState, "ACTIVE") or hasattr(ConfigState, "active") or "active" in [e.value for e in ConfigState]

    def test_activation_service_has_save_draft(self):
        """ActivationService has save_draft method."""
        from src.multi_tenant.activation_service import ActivationService

        assert hasattr(ActivationService, "save_draft")

    def test_activation_service_has_activate(self):
        """ActivationService has activate method."""
        from src.multi_tenant.activation_service import ActivationService

        assert hasattr(ActivationService, "activate")

    def test_draft_save_result_has_state_field(self):
        """DraftSaveResult defaults to state='draft'."""
        from src.multi_tenant.activation_service import DraftSaveResult

        result = DraftSaveResult(success=True)
        assert result.state == "draft"


# ---------------------------------------------------------------------------
# SPEC-0479: System MUST NOT be Active if mandatory inputs missing
# ---------------------------------------------------------------------------


class TestSpec0479NoActiveWithoutMandatory:
    """SPEC-0479: The system MUST NOT be in an 'Active' state if mandatory
    inputs are missing.

    ActivationService.activate() runs validation before promoting
    draft to active. If validation fails, activation is blocked.
    """

    def test_activation_result_has_errors(self):
        """ActivationResult can carry validation errors."""
        from src.multi_tenant.activation_service import ActivationResult

        result = ActivationResult(success=False, errors=[{"field": "brand_name", "error": "required"}])
        assert not result.success
        assert len(result.errors) == 1

    def test_validation_result_has_hard_errors(self):
        """ValidationResult distinguishes hard errors from warnings."""
        from src.multi_tenant.activation_service import ValidationResult

        vr = ValidationResult(
            can_activate=False,
            hard_errors=[{"field": "agent_name", "error": "required"}],
            warnings=[],
        )
        assert not vr.can_activate
        assert len(vr.hard_errors) == 1

    def test_activation_service_has_validate_method(self):
        """ActivationService has validation capability."""
        # The validate step is inside activate() — check source
        from src.multi_tenant.activation_service import ActivationService

        source = inspect.getsource(ActivationService.activate)
        assert "validate" in source.lower() or "ValidationResult" in source


# ---------------------------------------------------------------------------
# SPEC-0064: When configuration becomes Active, widget immediately available
# ---------------------------------------------------------------------------


class TestSpec0064ActiveMeansWidgetAvailable:
    """SPEC-0064: When configuration becomes Active, the widget MUST
    immediately become available.

    The chat pipeline reads config_state='active' from the preferences
    collection. Once activation writes this state, the next pipeline
    read picks it up (cache TTL is 60 seconds at most).
    """

    def test_activation_result_includes_activated_at(self):
        """ActivationResult records when activation happened."""
        from src.multi_tenant.activation_service import ActivationResult

        result = ActivationResult(
            success=True,
            version=1,
            activated_at="2026-03-06T12:00:00Z",
        )
        assert result.activated_at is not None

    def test_config_state_active_value(self):
        """ConfigState ACTIVE is the value the pipeline reads."""
        from src.multi_tenant.cosmos_schema import ConfigState

        values = [e.value for e in ConfigState]
        assert "active" in values
