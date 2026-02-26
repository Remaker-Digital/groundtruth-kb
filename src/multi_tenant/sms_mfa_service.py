"""
SMS MFA service — 6-digit OTP codes via Azure Communication Services.

Generates random 6-digit codes, stores SHA-256 hashes in the
verification_tokens collection (token_type="sms_otp", 10-min TTL),
and sends codes via ACS SmsClient. Gracefully degrades to unavailable
when ACS_SMS_FROM is not configured.

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

_SMS_TOKEN_TYPE = "sms_otp"
_SMS_CODE_DIGITS = 6
_SMS_CODE_TTL = 600  # 10 minutes

# ACS phone number for sending SMS — disabled when absent
_ACS_SMS_FROM = os.environ.get("ACS_SMS_FROM", "")
_ACS_CONNECTION_STRING = os.environ.get("AZURE_COMM_CONNECTION_STRING", "")


def is_sms_available() -> bool:
    """Return True if SMS sending is configured."""
    return bool(_ACS_SMS_FROM and _ACS_CONNECTION_STRING)


def _generate_otp() -> str:
    """Generate a cryptographically random 6-digit OTP code."""
    return "".join(str(secrets.randbelow(10)) for _ in range(_SMS_CODE_DIGITS))


def _hash_otp(code: str) -> str:
    """SHA-256 hash an OTP code for storage."""
    return hashlib.sha256(code.encode()).hexdigest()


# ---------------------------------------------------------------------------
# SMS MFA service
# ---------------------------------------------------------------------------


class SmsMfaService:
    """Orchestrates SMS OTP generation, delivery, and verification.

    Uses VerificationTokenRepository for token storage (same collection
    as magic link tokens, different token_type). Sends SMS via ACS.
    """

    def __init__(
        self,
        token_repo: Any | None = None,
    ) -> None:
        self._token_repo = token_repo

    async def send_code(
        self,
        tenant_id: str,
        member_id: str,
        phone_number: str,
    ) -> bool:
        """Generate and send a 6-digit SMS OTP code.

        Args:
            tenant_id: Tenant partition key.
            member_id: Team member document ID (used as token_id prefix).
            phone_number: E.164 phone number to send to.

        Returns:
            True if the code was sent successfully.
        """
        if not is_sms_available():
            logger.warning("SMS MFA not available (ACS_SMS_FROM not configured)")
            return False

        if not self._token_repo:
            logger.error("SmsMfaService: token_repo not configured")
            return False

        code = _generate_otp()
        code_hash = _hash_otp(code)

        # Use member_id as part of token_id so we can have one active
        # code per member (new code overwrites by consuming any existing)
        token_id = f"sms_otp_{member_id}"

        try:
            await self._token_repo.create_token(
                token_id=token_id,
                token_type=_SMS_TOKEN_TYPE,
                tenant_id=tenant_id,
                email=code_hash,  # Reuse email field for code hash
                ttl=_SMS_CODE_TTL,
                member_id=member_id,
            )
        except Exception:
            # Token already exists (race condition) — try to consume and recreate
            try:
                await self._token_repo.consume_token(token_id, _SMS_TOKEN_TYPE)
                await self._token_repo.create_token(
                    token_id=token_id,
                    token_type=_SMS_TOKEN_TYPE,
                    tenant_id=tenant_id,
                    email=code_hash,
                    ttl=_SMS_CODE_TTL,
                    member_id=member_id,
                )
            except Exception:
                logger.exception("Failed to create SMS OTP token")
                return False

        # Send the code via ACS SMS
        try:
            from azure.communication.sms import SmsClient

            sms_client = SmsClient.from_connection_string(_ACS_CONNECTION_STRING)
            sms_client.send(
                from_=_ACS_SMS_FROM,
                to=phone_number,
                message=f"Your Agent Red verification code is: {code}",
            )
            logger.info(
                "SMS OTP sent: member=%s phone=%s***",
                member_id, phone_number[:6],
            )
            return True
        except Exception:
            logger.exception("Failed to send SMS OTP")
            return False

    async def verify_code(
        self,
        member_id: str,
        code: str,
    ) -> bool:
        """Verify a 6-digit SMS OTP code.

        Consumes the token on successful verification (single-use).

        Args:
            member_id: Team member document ID.
            code: 6-digit code entered by the user.

        Returns:
            True if the code is valid.
        """
        if not self._token_repo:
            return False

        token_id = f"sms_otp_{member_id}"
        doc = await self._token_repo.consume_token(token_id, _SMS_TOKEN_TYPE)

        if not doc:
            return False

        stored_hash = doc.get("email", "")  # Hash stored in email field
        return stored_hash == _hash_otp(code)
