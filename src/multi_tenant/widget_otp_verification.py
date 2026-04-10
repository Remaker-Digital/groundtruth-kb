# © 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""Widget OTP verification — customer-facing 6-digit code flow (email + SMS).

Provides endpoints for the chat widget to send and verify OTP codes
before starting a conversation. Uses the existing verification_tokens
Cosmos DB collection with TTL-based auto-expiry.

Endpoints:
    POST /api/chat/otp/send        — Send a 6-digit OTP to customer email
    POST /api/chat/otp/verify      — Verify the email OTP code
    POST /api/chat/otp/send-sms    — Send a 6-digit OTP via SMS (SPEC-1879)
    POST /api/chat/otp/verify-sms  — Verify the SMS OTP code (SPEC-1879)

Authentication:
    Widget key (X-Widget-Key: pk_live_...) — same as all /api/chat/* endpoints.

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

from __future__ import annotations

import logging
import os
import secrets
from typing import Any

from fastapi import APIRouter, Depends, Request
from pydantic import BaseModel, Field

from src.multi_tenant.auth import TenantContext
from src.multi_tenant.middleware import get_tenant_context

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/chat/otp", tags=["Widget OTP"])

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

_OTP_TTL = 10 * 60  # 10 minutes
_OTP_LENGTH = 6  # 6-digit numeric code
_OTP_TOKEN_TYPE = "widget_otp"
_SMS_OTP_TOKEN_TYPE = "widget_otp_sms"  # SPEC-1879
_MAX_VERIFY_ATTEMPTS = 5  # Lock token after 5 failed attempts

# E.164 phone validation
import re  # noqa: E402

_E164_PATTERN = re.compile(r"^\+[1-9]\d{1,14}$")

# ---------------------------------------------------------------------------
# Rate limiting (in-memory, per-instance)
# ---------------------------------------------------------------------------

_RATE_WINDOW = 300.0  # 5 minutes
_RATE_MAX = 3  # max 3 OTP requests per window per IP


def _is_rate_limited(client_ip: str) -> bool:
    """Check if IP has exceeded OTP request rate limit (SPEC-1694)."""
    from src.multi_tenant.security_hardening import get_rate_limit_backend
    return get_rate_limit_backend().is_limited(
        f"widget_otp:{client_ip}", max_requests=_RATE_MAX, window_seconds=_RATE_WINDOW,
    )


def _generate_otp() -> str:
    """Generate a cryptographically random 6-digit numeric OTP."""
    # Use secrets.randbelow for uniform distribution across 000000-999999
    return str(secrets.randbelow(10**_OTP_LENGTH)).zfill(_OTP_LENGTH)


# ---------------------------------------------------------------------------
# Request / response models
# ---------------------------------------------------------------------------


class OtpSendRequest(BaseModel):
    """Request body for sending an OTP to a customer email."""

    email: str = Field(description="Customer email address", max_length=254)
    name: str = Field(default="", description="Customer name (optional)", max_length=200)


class OtpSendResponse(BaseModel):
    """Response after OTP send attempt — uniform to prevent enumeration."""

    sent: bool = Field(
        default=True,
        description="Always true — never reveals whether the email was valid",
    )
    message: str = Field(default="Enter the code we sent to your email.")


class OtpVerifyRequest(BaseModel):
    """Request body for verifying an OTP code."""

    email: str = Field(description="Customer email address", max_length=254)
    code: str = Field(description="6-digit OTP code", max_length=6)


class OtpVerifyResponse(BaseModel):
    """Response after OTP verification attempt."""

    verified: bool = Field(description="Whether the code was valid")
    customer_token: str | None = Field(
        default=None,
        description="Short-lived session token for verified customers",
    )


# ---------------------------------------------------------------------------
# OTP email template
# ---------------------------------------------------------------------------

_OTP_EMAIL_BODY = """
<h2 style="margin:0 0 16px;color:#111827;font-size:20px">Your Verification Code</h2>
<p style="color:#374151;font-size:14px;line-height:1.6;margin:0 0 24px">
  Enter this code in the chat widget to verify your email address.
</p>
<div style="text-align:center;margin:24px 0">
  <div style="display:inline-block;padding:16px 40px;background:#f8f9fa;
       border:2px solid #e5e7eb;border-radius:8px;font-size:32px;
       font-family:'SF Mono',SFMono-Regular,ui-monospace,monospace;
       font-weight:700;letter-spacing:8px;color:#111827">
    {code}
  </div>
</div>
<p style="color:#9ca3af;font-size:12px;line-height:1.5;margin:16px 0 0">
  This code expires in 10 minutes. If you didn't request this, ignore this email.
</p>
"""


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------


@router.post(
    "/send",
    response_model=OtpSendResponse,
    summary="Send OTP code to customer email",
    description="Sends a 6-digit verification code to the customer's email. "
    "Rate-limited to 3 requests per 5 minutes per IP. "
    "Requires widget key authentication.",
)
async def send_otp(
    body: OtpSendRequest,
    request: Request,
    ctx: TenantContext = Depends(get_tenant_context),
) -> OtpSendResponse:
    """Send a 6-digit OTP to the customer's email address.

    This endpoint is widget-authenticated (X-Widget-Key).
    Always returns the same response to prevent email enumeration.
    """
    client_ip = request.client.host if request.client else "unknown"

    if _is_rate_limited(client_ip):
        logger.warning(
            "Widget OTP rate limit exceeded: ip=%s tenant=%s",
            client_ip, ctx.tenant_id,
        )
        # Still return success to prevent timing attacks
        return OtpSendResponse()

    try:
        # Check if OTP verification is enabled for this tenant
        verification_mode = await _get_verification_mode(ctx.tenant_id)
        if verification_mode == "disabled":
            return OtpSendResponse(
                sent=True,
                message="Verification is not required.",
            )

        from src.multi_tenant.repositories import VerificationTokenRepository

        token_repo = VerificationTokenRepository()

        # Generate OTP code
        otp_code = _generate_otp()

        # Store OTP in verification_tokens with TTL
        # Use email+tenant as the token ID for easy lookup during verify
        token_id = f"otp:{ctx.tenant_id}:{body.email}"

        # Delete any existing OTP for this email (replace, not stack)
        try:
            await token_repo.delete_token(token_id, _OTP_TOKEN_TYPE)
        except Exception:
            pass  # Fine if it doesn't exist

        await token_repo.create_token(
            token_id=token_id,
            token_type=_OTP_TOKEN_TYPE,
            tenant_id=ctx.tenant_id,
            email=body.email,
            ttl=_OTP_TTL,
        )

        # Store the OTP code as an additional field via patch
        from src.multi_tenant.cosmos_client import get_cosmos_manager
        from src.multi_tenant.cosmos_schema import COLLECTION_VERIFICATION_TOKENS

        container = get_cosmos_manager().get_container(
            COLLECTION_VERIFICATION_TOKENS,
        )
        await container.patch_item(
            item=token_id,
            partition_key=_OTP_TOKEN_TYPE,
            patch_operations=[
                {"op": "add", "path": "/otp_code", "value": otp_code},
                {"op": "add", "path": "/customer_name", "value": body.name},
            ],
        )

        # Send the OTP email
        await _send_otp_email(body.email, otp_code, ctx.tenant_id)

        logger.info(
            "Widget OTP sent: tenant=%s email=%s",
            ctx.tenant_id, body.email,
        )

    except Exception:
        logger.exception("Error sending widget OTP")

    return OtpSendResponse()


@router.post(
    "/verify",
    response_model=OtpVerifyResponse,
    summary="Verify OTP code",
    description="Verifies the 6-digit code entered by the customer. "
    "Returns a short-lived customer session token on success.",
)
async def verify_otp(
    body: OtpVerifyRequest,
    ctx: TenantContext = Depends(get_tenant_context),
) -> OtpVerifyResponse:
    """Verify a 6-digit OTP code submitted by the customer.

    On success, returns a short-lived customer_token that the widget
    includes in subsequent chat requests to prove identity.
    """
    try:
        from src.multi_tenant.repositories import VerificationTokenRepository

        token_repo = VerificationTokenRepository()
        token_id = f"otp:{ctx.tenant_id}:{body.email}"

        # Read the token document (don't consume yet — need to check code)
        from src.multi_tenant.cosmos_client import get_cosmos_manager
        from src.multi_tenant.cosmos_schema import COLLECTION_VERIFICATION_TOKENS

        container = get_cosmos_manager().get_container(
            COLLECTION_VERIFICATION_TOKENS,
        )

        try:
            doc = await container.read_item(
                item=token_id,
                partition_key=_OTP_TOKEN_TYPE,
            )
        except Exception:
            return OtpVerifyResponse(verified=False)

        if doc.get("used"):
            return OtpVerifyResponse(verified=False)

        # Attempt throttle: lock token after _MAX_VERIFY_ATTEMPTS failures
        attempts = doc.get("verify_attempts", 0)
        if attempts >= _MAX_VERIFY_ATTEMPTS:
            logger.warning(
                "Widget OTP locked (max attempts): tenant=%s email=%s attempts=%d",
                ctx.tenant_id, body.email, attempts,
            )
            return OtpVerifyResponse(verified=False)

        # Compare OTP codes (constant-time comparison)
        stored_code = doc.get("otp_code", "")
        if not secrets.compare_digest(body.code.strip(), stored_code):
            # Increment attempt counter
            try:
                await container.patch_item(
                    item=token_id,
                    partition_key=_OTP_TOKEN_TYPE,
                    patch_operations=[
                        {"op": "incr", "path": "/verify_attempts", "value": 1},
                    ],
                )
            except Exception:
                logger.warning(
                    "Widget OTP: failed to increment verify_attempts for %s — throttle may not reflect this attempt",
                    token_id,
                )
            logger.info(
                "Widget OTP mismatch: tenant=%s email=%s attempt=%d",
                ctx.tenant_id, body.email, attempts + 1,
            )
            return OtpVerifyResponse(verified=False)

        # Mark token as consumed
        await token_repo.consume_token(token_id, _OTP_TOKEN_TYPE)

        # Generate a short-lived customer session token
        customer_token = _generate_customer_token(
            tenant_id=ctx.tenant_id,
            email=body.email,
            name=doc.get("customer_name", ""),
        )

        logger.info(
            "Widget OTP verified: tenant=%s email=%s",
            ctx.tenant_id, body.email,
        )

        return OtpVerifyResponse(
            verified=True,
            customer_token=customer_token,
        )

    except Exception:
        logger.exception("Error verifying widget OTP")
        return OtpVerifyResponse(verified=False)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


async def _get_verification_mode(tenant_id: str) -> str:
    """Load the customer_email_verification config value for a tenant.

    Returns "required" (default), "optional", or "disabled".
    """
    try:
        from src.multi_tenant.repository import PreferencesRepository

        prefs_repo = PreferencesRepository()
        prefs = await prefs_repo.get_current(tenant_id)
        if prefs:
            return prefs.get("customer_email_verification", "required")
    except Exception:
        logger.debug(
            "Failed to load verification mode for %s — defaulting to required",
            tenant_id,
        )
    return "required"


def _generate_customer_token(
    *,
    tenant_id: str,
    email: str,
    name: str,
) -> str:
    """Generate a JWT-style customer session token.

    This token proves the customer verified their email. The chat
    endpoints accept it via X-Customer-Token header to link the
    conversation to the verified identity.

    Token lifetime: 2 hours.
    """
    import hashlib
    import hmac
    import json
    import time

    secret = os.environ.get("CUSTOMER_TOKEN_SECRET", "agentred-customer-token-default")
    expires_at = int(time.time()) + (2 * 60 * 60)  # 2 hours

    payload = json.dumps({
        "tenant_id": tenant_id,
        "email": email,
        "name": name,
        "exp": expires_at,
    }, separators=(",", ":"), sort_keys=True)

    # HMAC-SHA256 signature
    sig = hmac.new(
        secret.encode(),
        payload.encode(),
        hashlib.sha256,
    ).hexdigest()[:32]

    import base64

    encoded_payload = base64.urlsafe_b64encode(payload.encode()).decode()

    return f"{encoded_payload}.{sig}"


def decode_customer_token(token: str) -> dict[str, Any] | None:
    """Decode and validate a customer session token.

    Returns the payload dict if valid and not expired, or None.
    """
    import base64
    import hashlib
    import hmac
    import json
    import time

    try:
        parts = token.split(".", 1)
        if len(parts) != 2:
            return None

        encoded_payload, sig = parts
        payload_bytes = base64.urlsafe_b64decode(encoded_payload)
        payload_str = payload_bytes.decode()

        # Verify signature
        secret = os.environ.get(
            "CUSTOMER_TOKEN_SECRET", "agentred-customer-token-default",
        )
        expected_sig = hmac.new(
            secret.encode(),
            payload_bytes,
            hashlib.sha256,
        ).hexdigest()[:32]

        if not secrets.compare_digest(sig, expected_sig):
            return None

        payload = json.loads(payload_str)

        # Check expiry
        if payload.get("exp", 0) < time.time():
            return None

        return payload

    except Exception:
        return None


async def _send_otp_email(
    to_email: str,
    otp_code: str,
    tenant_id: str,
) -> bool:
    """Send an OTP email using SMTP or ACS.

    Provider selection: SMTP (Titan) > ACS > skip.
    """
    from src.multi_tenant.alert_delivery import format_branded_email

    html_body = _OTP_EMAIL_BODY.format(code=otp_code)
    full_html = format_branded_email(html_body)
    subject = "Your verification code"

    # --- Provider 1: SMTP (Titan or other SMTP provider) ---
    smtp_host = os.environ.get("SMTP_HOST", "")
    if smtp_host:
        import asyncio
        import smtplib
        from email.mime.multipart import MIMEMultipart
        from email.mime.text import MIMEText

        smtp_port = int(os.environ.get("SMTP_PORT", "587"))
        smtp_user = os.environ.get("SMTP_USERNAME", "")
        smtp_pass = os.environ.get("SMTP_PASSWORD", "")
        smtp_from = os.environ.get("SMTP_FROM", smtp_user)

        def _smtp_send() -> None:
            msg = MIMEMultipart("alternative")
            msg["From"] = f"Agent Red <{smtp_from}>"
            msg["To"] = to_email
            msg["Subject"] = subject
            msg.attach(MIMEText(full_html, "html"))
            if smtp_port == 465:
                with smtplib.SMTP_SSL(smtp_host, smtp_port, timeout=10) as server:
                    if smtp_user and smtp_pass:
                        server.login(smtp_user, smtp_pass)
                    server.send_message(msg)
            else:
                with smtplib.SMTP(smtp_host, smtp_port, timeout=10) as server:
                    server.ehlo()
                    if smtp_port != 25:
                        server.starttls()
                    if smtp_user and smtp_pass:
                        server.login(smtp_user, smtp_pass)
                    server.send_message(msg)

        try:
            await asyncio.to_thread(_smtp_send)  # SPEC-1622: non-blocking SMTP
            return True
        except Exception:
            logger.exception("SMTP email send failed for widget OTP — trying ACS fallback")
            # Fall through to ACS provider

    # --- Provider 2: Azure Communication Services (fallback) ---
    conn_str = os.environ.get("AZURE_COMM_CONNECTION_STRING", "")
    if conn_str:
        try:
            from src.multi_tenant.alert_delivery import send_acs_email

            status = await send_acs_email(conn_str, to_email, subject, full_html)
            return status == "Succeeded"
        except Exception:
            logger.exception("ACS email send failed for widget OTP")
            return False

    logger.warning("No email provider configured for widget OTP")
    return False


# ---------------------------------------------------------------------------
# SMS OTP — SPEC-1879: Phone Identity Channel
# ---------------------------------------------------------------------------


def normalize_e164(raw_phone: str) -> str | None:
    """Normalize a phone number to E.164 format.

    Strips spaces, dashes, parentheses, and dots. Returns the normalized
    string if valid, or None if the result doesn't match E.164.
    """
    cleaned = raw_phone.strip()
    for ch in " -().":
        cleaned = cleaned.replace(ch, "")
    if _E164_PATTERN.match(cleaned):
        return cleaned
    return None


class SmsSendRequest(BaseModel):
    """Request body for sending an SMS OTP (SPEC-1879)."""

    phone: str = Field(description="Customer phone number (E.164 format)", max_length=16)
    name: str = Field(default="", description="Customer name (optional)", max_length=200)


class SmsSendResponse(BaseModel):
    """Response after SMS OTP send — uniform to prevent enumeration."""

    sent: bool = Field(
        default=True,
        description="Always true — never reveals whether the phone was valid",
    )
    message: str = Field(default="Enter the code we sent to your phone.")
    reason: str | None = Field(
        default=None,
        description="Structured reason code for programmatic branching (e.g., 'tier_blocked')",
    )


class SmsVerifyRequest(BaseModel):
    """Request body for verifying an SMS OTP code (SPEC-1879)."""

    phone: str = Field(description="Customer phone number (E.164 format)", max_length=16)
    code: str = Field(description="6-digit OTP code", max_length=6)


class SmsVerifyResponse(BaseModel):
    """Response after SMS OTP verification.

    Phase 1 constraint: does NOT return a customer_token. The verified phone
    is confirmed but no chat-usable token is minted until a phone-aware
    session/endpoint path is reviewed in a later phase (Codex P1-2 blocker).
    """

    verified: bool = Field(description="Whether the code was valid")
    phone: str | None = Field(
        default=None,
        description="Verified phone number (E.164) — returned only on success",
    )


async def _check_tier_gate(tenant_id: str) -> bool:
    """Return True if tenant is professional+ (SPEC-1879 tier gate).

    Delegates to shared utility; kept as local wrapper for backward compat.
    """
    from src.multi_tenant.tier_utils import check_tier_gate

    return await check_tier_gate(tenant_id)


@router.post(
    "/send-sms",
    response_model=SmsSendResponse,
    summary="Send OTP code via SMS (SPEC-1879)",
    description="Sends a 6-digit verification code to the customer's phone via SMS. "
    "Requires professional+ tier. Rate-limited to 3 requests per 5 minutes per IP. "
    "Requires widget key authentication.",
)
async def send_sms_otp(
    body: SmsSendRequest,
    request: Request,
    ctx: TenantContext = Depends(get_tenant_context),
) -> SmsSendResponse:
    """Send a 6-digit OTP to the customer's phone number via ACS SMS.

    This endpoint is widget-authenticated (X-Widget-Key).
    Always returns the same response to prevent phone enumeration.
    """
    client_ip = request.client.host if request.client else "unknown"

    if _is_rate_limited(client_ip):
        logger.warning(
            "SMS OTP rate limit exceeded: ip=%s tenant=%s",
            client_ip, ctx.tenant_id,
        )
        return SmsSendResponse()

    try:
        # Tier gate: professional+ only
        if not await _check_tier_gate(ctx.tenant_id):
            logger.info(
                "SMS OTP blocked by tier gate: tenant=%s", ctx.tenant_id,
            )
            return SmsSendResponse(
                sent=True,
                message="SMS verification is not available for your plan.",
                reason="tier_blocked",
            )

        # Validate and normalize E.164
        phone = normalize_e164(body.phone)
        if not phone:
            return SmsSendResponse()

        from src.multi_tenant.repositories import VerificationTokenRepository
        from src.multi_tenant.sms_verification import hash_code

        token_repo = VerificationTokenRepository()

        otp_code = _generate_otp()
        hashed_code = hash_code(otp_code)

        # Store hashed OTP in verification_tokens with TTL
        token_id = f"otp:{ctx.tenant_id}:{phone}"

        try:
            await token_repo.delete_token(token_id, _SMS_OTP_TOKEN_TYPE)
        except Exception:
            pass

        await token_repo.create_token(
            token_id=token_id,
            token_type=_SMS_OTP_TOKEN_TYPE,
            tenant_id=ctx.tenant_id,
            email=phone,  # Reuse email field for phone (token schema)
            ttl=_OTP_TTL,
        )

        # Patch to store hashed code (NOT plaintext — Codex requirement)
        from src.multi_tenant.cosmos_client import get_cosmos_manager
        from src.multi_tenant.cosmos_schema import COLLECTION_VERIFICATION_TOKENS

        container = get_cosmos_manager().get_container(
            COLLECTION_VERIFICATION_TOKENS,
        )
        await container.patch_item(
            item=token_id,
            partition_key=_SMS_OTP_TOKEN_TYPE,
            patch_operations=[
                {"op": "add", "path": "/otp_code_hash", "value": hashed_code},
                {"op": "add", "path": "/customer_name", "value": body.name},
            ],
        )

        # Send SMS via ACS
        from src.multi_tenant.sms_verification import _send_sms

        await _send_sms(phone, otp_code)

        logger.info(
            "SMS OTP sent: tenant=%s phone=%s***",
            ctx.tenant_id, phone[:6],
        )

    except Exception:
        logger.exception("Error sending SMS OTP")
        return SmsSendResponse(sent=False, message="Unable to send verification code. Please try again.")

    return SmsSendResponse()


@router.post(
    "/verify-sms",
    response_model=SmsVerifyResponse,
    summary="Verify SMS OTP code (SPEC-1879)",
    description="Verifies the 6-digit SMS code entered by the customer. "
    "Returns verified status and phone on success. "
    "Phase 1: no customer_token, no ContactAttribute linkage.",
)
async def verify_sms_otp(
    body: SmsVerifyRequest,
    ctx: TenantContext = Depends(get_tenant_context),
) -> SmsVerifyResponse:
    """Verify a 6-digit SMS OTP code submitted by the customer.

    On success, returns verified=True and the normalized phone number.
    Phase 1 constraint: does NOT mint a customer_token or link
    ContactAttribute(PHONE). Token issuance deferred to a later phase
    with a reviewed phone-aware session/endpoint path.
    """
    try:
        phone = normalize_e164(body.phone)
        if not phone:
            return SmsVerifyResponse(verified=False)

        from src.multi_tenant.cosmos_client import get_cosmos_manager
        from src.multi_tenant.cosmos_schema import COLLECTION_VERIFICATION_TOKENS
        from src.multi_tenant.repositories import VerificationTokenRepository
        from src.multi_tenant.sms_verification import hash_code

        token_repo = VerificationTokenRepository()
        token_id = f"otp:{ctx.tenant_id}:{phone}"

        container = get_cosmos_manager().get_container(
            COLLECTION_VERIFICATION_TOKENS,
        )

        try:
            doc = await container.read_item(
                item=token_id,
                partition_key=_SMS_OTP_TOKEN_TYPE,
            )
        except Exception:
            return SmsVerifyResponse(verified=False)

        if doc.get("used"):
            return SmsVerifyResponse(verified=False)

        # Attempt throttle: lock token after _MAX_VERIFY_ATTEMPTS failures
        attempts = doc.get("verify_attempts", 0)
        if attempts >= _MAX_VERIFY_ATTEMPTS:
            logger.warning(
                "SMS OTP locked (max attempts): tenant=%s phone=%s*** attempts=%d",
                ctx.tenant_id, phone[:6], attempts,
            )
            return SmsVerifyResponse(verified=False)

        # Constant-time hash comparison (Codex security requirement)
        stored_hash = doc.get("otp_code_hash", "")
        submitted_hash = hash_code(body.code.strip())
        if not secrets.compare_digest(submitted_hash, stored_hash):
            # Increment attempt counter
            try:
                await container.patch_item(
                    item=token_id,
                    partition_key=_SMS_OTP_TOKEN_TYPE,
                    patch_operations=[
                        {"op": "incr", "path": "/verify_attempts", "value": 1},
                    ],
                )
            except Exception:
                logger.warning(
                    "SMS OTP: failed to increment verify_attempts for %s — throttle may not reflect this attempt",
                    token_id,
                )
            logger.info(
                "SMS OTP mismatch: tenant=%s phone=%s*** attempt=%d",
                ctx.tenant_id, phone[:6], attempts + 1,
            )
            return SmsVerifyResponse(verified=False)

        # Mark token as consumed (single-use)
        await token_repo.consume_token(token_id, _SMS_OTP_TOKEN_TYPE)

        # Phase 1: return verified status + phone only.
        # No customer_token minted — current chat runtime treats any valid
        # customer_token as customer_verified=True which would skip identity
        # collection (Codex P1-2 blocker). Token issuance deferred to a
        # later phase with a reviewed phone-aware session path.

        logger.info(
            "SMS OTP verified: tenant=%s phone=%s***",
            ctx.tenant_id, phone[:6],
        )

        return SmsVerifyResponse(
            verified=True,
            phone=phone,
        )

    except Exception:
        logger.exception("Error verifying SMS OTP")
        return SmsVerifyResponse(verified=False)


