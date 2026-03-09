"""SMS Verification Service (SPEC-1686).

Provides email/SMS choice for verification when a verified phone exists.

Key behaviors:
    1. 6-digit code via ACS toll-free, 15-min TTL, single-use.
    2. Phone superadmin-managed (SPEC-1681).
    3. SMS failure falls back to email automatically.
    4. Email primary, SMS supplementary.
    5. Integrates with both login and email change flows.
    6. Emits communication events via SPEC-1687.

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

from __future__ import annotations

import hashlib
import logging
import os
import secrets
from typing import Any

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

_VERIFICATION_TOKEN_TYPE = "sms_verification"
_CODE_DIGITS = 6
_CODE_TTL = 900  # 15 minutes (SPEC-1686 requirement)

# ACS phone number for sending SMS -- disabled when absent
_ACS_SMS_FROM = os.environ.get("ACS_SMS_FROM", "")
_ACS_CONNECTION_STRING = os.environ.get("AZURE_COMM_CONNECTION_STRING", "")


# ---------------------------------------------------------------------------
# Public helpers
# ---------------------------------------------------------------------------


def is_sms_configured() -> bool:
    """Return True if ACS SMS sending is available."""
    return bool(_ACS_SMS_FROM and _ACS_CONNECTION_STRING)


def generate_verification_code() -> str:
    """Generate a cryptographically random 6-digit verification code."""
    return "".join(str(secrets.randbelow(10)) for _ in range(_CODE_DIGITS))


def hash_code(code: str) -> str:
    """SHA-256 hash a verification code for storage."""
    return hashlib.sha256(code.encode()).hexdigest()


# ---------------------------------------------------------------------------
# SMS sending
# ---------------------------------------------------------------------------


async def _send_sms(phone_number: str, code: str) -> bool:
    """Send an SMS verification code via ACS.

    Returns True on success, False on failure. Never raises.
    """
    if not is_sms_configured():
        logger.warning("SMS not configured (ACS_SMS_FROM missing)")
        return False

    try:
        import asyncio

        from azure.communication.sms import SmsClient

        def _send() -> None:
            sms_client = SmsClient.from_connection_string(_ACS_CONNECTION_STRING)
            sms_client.send(
                from_=_ACS_SMS_FROM,
                to=phone_number,
                message=f"Your Agent Red verification code is: {code}",
            )

        await asyncio.to_thread(_send)
        logger.info(
            "SMS verification sent: phone=%s***",
            phone_number[:6],
        )
        return True
    except Exception:
        logger.exception("Failed to send SMS verification code")
        return False

# -----------------------------------------------------------------------
# Service class
# -----------------------------------------------------------------------


class SmsVerificationService:
    """Orchestrates verification code delivery via SMS or email.

    Usage::

        svc = SmsVerificationService()
        result = await svc.send_code(
            email="user@example.com",
            phone="+15550123456",
            prefer_sms=True,
        )
        # result == {"channel": "sms", "code_hash": "...", "ttl": 900}

        ok = await svc.verify_code(
            code="123456",
            expected_hash=result["code_hash"],
        )
    """

    async def send_code(
        self,
        *,
        email: str,
        phone: str = "",
        prefer_sms: bool = False,
        purpose: str = "verification",
        metadata: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Generate and deliver a verification code.

        Tries SMS first if `prefer_sms=True` and a phone is
        provided and ACS is configured.  Falls back to email
        on any SMS failure.

        Returns
        -------
        dict with keys:
            channel: "sms" | "email"
            code_hash: SHA-256 of the code
            ttl: seconds until expiry
        """
        code = generate_verification_code()
        code_hashed = hash_code(code)

        channel = "email"  # default

        # -- Try SMS first if preferred ------------------------------
        if prefer_sms and phone and is_sms_configured():
            sms_ok = await _send_sms(phone, code)
            if sms_ok:
                channel = "sms"
                await self._emit_event(
                    event_type=f"{purpose}_sms_code",
                    recipient=phone,
                    channel="sms",
                    code=code,
                    metadata=metadata,
                )
            else:
                logger.warning(
                    "SMS failed for %s, falling back to email",
                    phone[:6],
                )

        # -- Email fallback (or primary) -----------------------------
        if channel == "email":
            await self._send_email(email, code, purpose)
            await self._emit_event(
                event_type=f"{purpose}_email_code",
                recipient=email,
                channel="email",
                code=code,
                subject=f"Your Agent Red {purpose} code",
                metadata=metadata,
            )

        return {
            "channel": channel,
            "code_hash": code_hashed,
            "ttl": _CODE_TTL,
        }

    async def verify_code(
        self,
        *,
        code: str,
        expected_hash: str,
    ) -> bool:
        """Verify a user-supplied code against the stored hash.

        Single-use: the caller must invalidate the hash after
        a successful verification.
        """
        if not code or not expected_hash:
            return False
        return hash_code(code) == expected_hash

    # -----------------------------------------------------------------
    # Internal helpers
    # -----------------------------------------------------------------

    async def _send_email(
        self,
        email: str,
        code: str,
        purpose: str,
    ) -> None:
        """Send a verification code via email (SMTP primary, ACS fallback)."""
        import asyncio

        subject = f"Your Agent Red {purpose} code"
        body = (
            "<html><body>"
            f"<p>Your verification code is: <strong>{code}</strong></p>"
            f"<p>This code expires in {_CODE_TTL // 60} minutes.</p>"
            "<p>If you did not request this, please ignore this email.</p>"
            "</body></html>"
        )

        try:
            from src.multi_tenant.email_sender import EmailSender

            sender = EmailSender()
            await asyncio.to_thread(
                sender.send_email,
                to_email=email,
                subject=subject,
                html_body=body,
            )
            logger.info("Email verification sent: email=%s", email)
        except Exception:
            logger.exception("Failed to send verification email")

    async def _emit_event(
        self,
        *,
        event_type: str,
        recipient: str,
        channel: str,
        code: str = "",
        subject: str = "",
        metadata: dict[str, Any] | None = None,
    ) -> None:
        """Emit a communication event via SPEC-1687."""
        try:
            from src.multi_tenant.communication_capture import (
                emit_communication_event,
            )

            emit_communication_event(
                event_type=event_type,
                recipient=recipient,
                channel=channel,
                subject=subject,
                token=code,
                ttl_minutes=_CODE_TTL // 60,
                metadata=metadata or {},
            )
        except Exception:
            logger.exception("Failed to emit communication event")
