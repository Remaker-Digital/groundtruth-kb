"""Widget OTP email verification — customer-facing 6-digit code flow.

Provides endpoints for the chat widget to send and verify OTP codes
before starting a conversation. Uses the existing verification_tokens
Cosmos DB collection with TTL-based auto-expiry.

Endpoints:
    POST /api/chat/otp/send    — Send a 6-digit OTP to customer email
    POST /api/chat/otp/verify  — Verify the OTP code

Authentication:
    Widget key (X-Widget-Key: pk_live_...) — same as all /api/chat/* endpoints.

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

from __future__ import annotations

import logging
import os
import secrets
import time
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Request
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

# ---------------------------------------------------------------------------
# Rate limiting (in-memory, per-instance)
# ---------------------------------------------------------------------------

_RATE_WINDOW = 300.0  # 5 minutes
_RATE_MAX = 3  # max 3 OTP requests per window per IP

_rate_limit: dict[str, list[float]] = {}


def _is_rate_limited(client_ip: str) -> bool:
    """Check if IP has exceeded OTP request rate limit."""
    now = time.time()
    window_start = now - _RATE_WINDOW
    if client_ip in _rate_limit:
        _rate_limit[client_ip] = [
            ts for ts in _rate_limit[client_ip] if ts > window_start
        ]
    requests = _rate_limit.get(client_ip, [])
    if len(requests) >= _RATE_MAX:
        return True
    _rate_limit.setdefault(client_ip, []).append(now)
    return False


def _generate_otp() -> str:
    """Generate a cryptographically random 6-digit numeric OTP."""
    # Use secrets.randbelow for uniform distribution across 000000-999999
    return str(secrets.randbelow(10**_OTP_LENGTH)).zfill(_OTP_LENGTH)


# ---------------------------------------------------------------------------
# Request / response models
# ---------------------------------------------------------------------------


class OtpSendRequest(BaseModel):
    """Request body for sending an OTP to a customer email."""

    email: str = Field(description="Customer email address")
    name: str = Field(default="", description="Customer name (optional)")


class OtpSendResponse(BaseModel):
    """Response after OTP send attempt — uniform to prevent enumeration."""

    sent: bool = Field(
        default=True,
        description="Always true — never reveals whether the email was valid",
    )
    message: str = Field(default="Enter the code we sent to your email.")


class OtpVerifyRequest(BaseModel):
    """Request body for verifying an OTP code."""

    email: str = Field(description="Customer email address")
    code: str = Field(description="6-digit OTP code")


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

        # Compare OTP codes (constant-time comparison)
        stored_code = doc.get("otp_code", "")
        if not secrets.compare_digest(body.code.strip(), stored_code):
            logger.info(
                "Widget OTP mismatch: tenant=%s email=%s",
                ctx.tenant_id, body.email,
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
    from src.multi_tenant.alert_delivery import _EMAIL_WRAPPER

    html_body = _OTP_EMAIL_BODY.format(code=otp_code)
    full_html = _EMAIL_WRAPPER.format(body=html_body)
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
