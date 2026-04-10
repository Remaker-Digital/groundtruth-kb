# © 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""In-conversation identity preprocessor (P0-AUTH-FIX).

Intercepts customer messages before they reach the AI pipeline to detect
and handle identity-related inputs:

1. **Email detection** -- when the message contains an email address
   (standalone or embedded in a short sentence like "my email is x@y.com"),
   sends an OTP verification code and returns a system response.
2. **OTP verification** -- when an OTP has been sent and the message is
   a 6-digit code, validates it and marks the conversation as verified.
3. **Skip/guest** -- when the customer says "skip" or "continue as guest"
   during an OTP-pending state, acknowledges and proceeds anonymously.

This keeps OTP mechanics deterministic (Python code) while the AI handles
the conversational UX (asking for email, warning about limitations).

The preprocessor reads/writes ConversationDocument fields:
- identity_email: str | None
- identity_otp_sent_at: str | None
- identity_otp_attempts: int
- customer_verified: bool (email/Shopify — NOT set by phone OTP)
- identity_phone: str | None (SPEC-1879)
- identity_sms_sent_at: str | None (SPEC-1879)
- identity_sms_attempts: int (SPEC-1879)
- phone_verified: bool (SPEC-1879 Phase 2A — weaker assurance than customer_verified)

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

from __future__ import annotations

import logging
import re
import secrets
from dataclasses import dataclass
from datetime import UTC, datetime
from typing import Literal

logger = logging.getLogger(__name__)

# E.164 phone: strict match (starts with +, 2-15 digits)
_PHONE_STRICT_PATTERN = re.compile(r"^\+[1-9]\d{1,14}$")
# Flexible: phone embedded in a short message like "my phone is +15551234567"
# Uses word-char lookarounds to reject trailing alpha, embedded words, overlong digits.
_PHONE_EXTRACT_PATTERN = re.compile(r"(?<![+\w])(\+[1-9]\d{1,14})(?!\w)")

# Strict email regex: entire message is a single email address
_EMAIL_STRICT_PATTERN = re.compile(r"^[^\s@]+@[^\s@]+\.[^\s@]+$")

# Flexible email regex: extract an email embedded in a sentence
_EMAIL_EXTRACT_PATTERN = re.compile(r"\b([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})\b")

# Don't try to extract email from long messages (likely not an email submission)
_MAX_EMAIL_MSG_LENGTH = 200

# OTP: exactly 6 digits, nothing else
_OTP_PATTERN = re.compile(r"^\d{6}$")

# Skip phrases (case-insensitive, exact match)
_SKIP_PHRASES = {"skip", "continue as guest", "guest", "no thanks"}

# Rate limit: max OTP verification attempts per conversation
_MAX_OTP_ATTEMPTS = 3

# OTP token type and TTL (same as widget_otp_verification.py)
_OTP_TOKEN_TYPE = "widget_otp"
_OTP_TTL = 600  # 10 minutes
_OTP_LENGTH = 6


@dataclass
class IdentityAction:
    """Result of preprocessing a customer message for identity signals."""

    action: Literal[
        "none",
        "email_received",
        "otp_received",
        "otp_invalid",
        "otp_rate_limited",
        "skip_verification",
        "phone_received",
        "sms_otp_received",
        "sms_otp_invalid",
        "sms_otp_rate_limited",
    ]
    email: str | None = None
    phone: str | None = None
    system_message: str | None = None


# ---------------------------------------------------------------------------
# Internal OTP helpers (reuse Cosmos patterns from widget_otp_verification)
# ---------------------------------------------------------------------------


async def _send_otp_for_conversation(email: str, tenant_id: str) -> bool:
    """Generate and send an OTP code for in-conversation verification.

    Reuses the same Cosmos DB ``verification_tokens`` collection and
    email sending logic as widget_otp_verification.py.

    Returns True if OTP was sent successfully, False otherwise.
    """
    try:
        from src.multi_tenant.cosmos_client import get_cosmos_manager
        from src.multi_tenant.cosmos_schema import COLLECTION_VERIFICATION_TOKENS
        from src.multi_tenant.repositories import VerificationTokenRepository
        from src.multi_tenant.widget_otp_verification import _send_otp_email

        # Generate 6-digit code
        otp_code = str(secrets.randbelow(10**_OTP_LENGTH)).zfill(_OTP_LENGTH)

        token_repo = VerificationTokenRepository()
        token_id = f"otp:{tenant_id}:{email}"

        # Delete existing OTP (replace, not stack)
        try:
            await token_repo.delete_token(token_id, _OTP_TOKEN_TYPE)
        except Exception:
            pass

        # Create token document
        await token_repo.create_token(
            token_id=token_id,
            token_type=_OTP_TOKEN_TYPE,
            tenant_id=tenant_id,
            email=email,
            ttl=_OTP_TTL,
        )

        # Store OTP code via patch
        container = get_cosmos_manager().get_container(COLLECTION_VERIFICATION_TOKENS)
        await container.patch_item(
            item=token_id,
            partition_key=_OTP_TOKEN_TYPE,
            patch_operations=[
                {"op": "add", "path": "/otp_code", "value": otp_code},
                {"op": "add", "path": "/customer_name", "value": ""},
            ],
        )

        # Send the email
        await _send_otp_email(email, otp_code, tenant_id)

        logger.info("In-conversation OTP sent: tenant=%s email=%s", tenant_id[:8], email)
        return True

    except Exception as exc:
        logger.error("Failed to send in-conversation OTP: %s", exc)
        return False


async def _verify_otp_for_conversation(email: str, code: str, tenant_id: str) -> bool:
    """Verify a 6-digit OTP code for in-conversation verification.

    Returns True if the code is valid and consumed, False otherwise.
    """
    try:
        from src.multi_tenant.cosmos_client import get_cosmos_manager
        from src.multi_tenant.cosmos_schema import COLLECTION_VERIFICATION_TOKENS
        from src.multi_tenant.repositories import VerificationTokenRepository

        token_id = f"otp:{tenant_id}:{email}"
        container = get_cosmos_manager().get_container(COLLECTION_VERIFICATION_TOKENS)

        # Read the token document
        try:
            doc = await container.read_item(
                item=token_id,
                partition_key=_OTP_TOKEN_TYPE,
            )
        except Exception:
            return False

        if doc.get("used"):
            return False

        # Constant-time comparison
        stored_code = doc.get("otp_code", "")
        if not secrets.compare_digest(code.strip(), stored_code):
            return False

        # Mark token as consumed
        token_repo = VerificationTokenRepository()
        await token_repo.consume_token(token_id, _OTP_TOKEN_TYPE)

        logger.info("In-conversation OTP verified: tenant=%s email=%s", tenant_id[:8], email)
        return True

    except Exception as exc:
        logger.error("In-conversation OTP verification error: %s", exc)
        return False


# ---------------------------------------------------------------------------
# Email extraction
# ---------------------------------------------------------------------------


def _extract_email(content: str) -> str | None:
    """Extract an email address from a customer message.

    Uses a two-tier strategy:
    1. **Strict match** — entire message is a single email (highest confidence).
    2. **Flexible extraction** — email embedded in a short sentence like
       "my email is alice@example.com" (only if message < 200 chars and
       exactly one email found).

    Returns the lowercase email if exactly one is found, or None.
    """
    stripped = content.strip()

    # Tier 1: strict — entire message is email
    if _EMAIL_STRICT_PATTERN.match(stripped):
        return stripped.lower()

    # Tier 2: flexible — extract from sentence (short messages only)
    if len(stripped) > _MAX_EMAIL_MSG_LENGTH:
        return None

    matches = _EMAIL_EXTRACT_PATTERN.findall(stripped)
    if len(matches) == 1:
        return matches[0].lower()

    return None  # Zero or multiple emails — ambiguous


# ---------------------------------------------------------------------------
# Phone extraction (SPEC-1879 Phase 2A)
# ---------------------------------------------------------------------------


def _extract_phone(content: str) -> str | None:
    """Extract an E.164 phone number from a customer message.

    Uses a two-tier strategy mirroring _extract_email:
    1. **Strict match** — entire message is a single E.164 phone number.
    2. **Flexible extraction** — phone embedded in a short sentence like
       "my phone is +15551234567" (only if message < 200 chars and
       exactly one phone found).

    Returns the phone string if exactly one is found, or None.
    """
    stripped = content.strip()

    # Tier 1: strict — entire message is E.164 phone
    if _PHONE_STRICT_PATTERN.match(stripped):
        return stripped

    # Tier 2: flexible — extract from sentence (short messages only)
    if len(stripped) > _MAX_EMAIL_MSG_LENGTH:
        return None

    matches = _PHONE_EXTRACT_PATTERN.findall(stripped)
    if len(matches) == 1:
        # Defense-in-depth: verify candidate passes strict E.164 fullmatch
        candidate = matches[0]
        if _PHONE_STRICT_PATTERN.match(candidate):
            return candidate

    return None  # Zero, multiple, or invalid phones


# ---------------------------------------------------------------------------
# SMS OTP helpers (SPEC-1879 Phase 2A — reuses Phase 1 infrastructure)
# ---------------------------------------------------------------------------


_SMS_OTP_TOKEN_TYPE = "widget_otp_sms"
_SMS_OTP_TTL = 600  # 10 minutes
_MAX_SMS_OTP_ATTEMPTS = 3


async def _send_sms_otp_for_conversation(phone: str, tenant_id: str) -> bool:
    """Generate and send an SMS OTP code for in-conversation phone verification.

    Reuses the same Cosmos DB verification_tokens collection and SMS sending
    logic as widget_otp_verification.py Phase 1 endpoints.

    Returns True if SMS OTP was sent successfully, False otherwise.
    """
    try:
        from src.multi_tenant.cosmos_client import get_cosmos_manager
        from src.multi_tenant.cosmos_schema import COLLECTION_VERIFICATION_TOKENS
        from src.multi_tenant.repositories import VerificationTokenRepository
        from src.multi_tenant.sms_verification import _send_sms, hash_code

        # Generate 6-digit code
        otp_code = str(secrets.randbelow(10**_OTP_LENGTH)).zfill(_OTP_LENGTH)

        token_repo = VerificationTokenRepository()
        token_id = f"otp:{tenant_id}:{phone}"

        # Delete existing token (replace, not stack)
        try:
            await token_repo.delete_token(token_id, _SMS_OTP_TOKEN_TYPE)
        except Exception:
            pass

        # Create token document
        await token_repo.create_token(
            token_id=token_id,
            token_type=_SMS_OTP_TOKEN_TYPE,
            tenant_id=tenant_id,
            email=phone,  # Reuse email field for phone (token schema)
            ttl=_SMS_OTP_TTL,
        )

        # Store hashed OTP code
        container = get_cosmos_manager().get_container(COLLECTION_VERIFICATION_TOKENS)
        await container.patch_item(
            item=token_id,
            partition_key=_SMS_OTP_TOKEN_TYPE,
            patch_operations=[
                {"op": "add", "path": "/otp_code_hash", "value": hash_code(otp_code)},
                {"op": "add", "path": "/customer_name", "value": ""},
            ],
        )

        # Send the SMS
        await _send_sms(phone, otp_code)

        logger.info("In-conversation SMS OTP sent: tenant=%s phone=%s***", tenant_id[:8], phone[:6])
        return True

    except Exception as exc:
        logger.error("Failed to send in-conversation SMS OTP: %s", exc)
        return False


async def _verify_sms_otp_for_conversation(phone: str, code: str, tenant_id: str) -> bool:
    """Verify a 6-digit SMS OTP code for in-conversation phone verification.

    Uses SHA-256 hash comparison (constant-time) matching Phase 1 security.
    Returns True if the code is valid and consumed, False otherwise.
    """
    try:
        from src.multi_tenant.cosmos_client import get_cosmos_manager
        from src.multi_tenant.cosmos_schema import COLLECTION_VERIFICATION_TOKENS
        from src.multi_tenant.repositories import VerificationTokenRepository
        from src.multi_tenant.sms_verification import hash_code

        token_id = f"otp:{tenant_id}:{phone}"
        container = get_cosmos_manager().get_container(COLLECTION_VERIFICATION_TOKENS)

        try:
            doc = await container.read_item(
                item=token_id,
                partition_key=_SMS_OTP_TOKEN_TYPE,
            )
        except Exception:
            return False

        if doc.get("used"):
            return False

        # Constant-time hash comparison (Codex security requirement)
        stored_hash = doc.get("otp_code_hash", "")
        submitted_hash = hash_code(code.strip())
        if not secrets.compare_digest(submitted_hash, stored_hash):
            return False

        # Mark token as consumed
        token_repo = VerificationTokenRepository()
        await token_repo.consume_token(token_id, _SMS_OTP_TOKEN_TYPE)

        logger.info("In-conversation SMS OTP verified: tenant=%s phone=%s***", tenant_id[:8], phone[:6])
        return True

    except Exception as exc:
        logger.error("In-conversation SMS OTP verification error: %s", exc)
        return False


# ---------------------------------------------------------------------------
# Main preprocessor
# ---------------------------------------------------------------------------


async def preprocess_identity(
    conversation_id: str,
    tenant_id: str,
    content: str,
) -> IdentityAction:
    """Preprocess a customer message for identity signals.

    Args:
        conversation_id: The active conversation ID.
        tenant_id: The tenant partition key.
        content: The raw customer message content.

    Returns:
        IdentityAction describing what happened. If action is ``"none"``,
        the message should pass through to the AI pipeline normally.
    """
    content_stripped = content.strip()

    # Load conversation document
    try:
        from src.multi_tenant.repository import ConversationRepository

        conv_repo = ConversationRepository()
        conv_doc = await conv_repo.read(tenant_id, conversation_id)
    except Exception as exc:
        logger.warning(
            "Identity preprocessor: failed to read conversation %s: %s",
            conversation_id,
            exc,
        )
        return IdentityAction(action="none")

    if conv_doc is None:
        return IdentityAction(action="none")

    # If already verified, pass through -- no identity collection needed
    if conv_doc.get("customer_verified", False):
        return IdentityAction(action="none")

    otp_sent_at = conv_doc.get("identity_otp_sent_at")
    otp_attempts = conv_doc.get("identity_otp_attempts", 0)
    identity_email = conv_doc.get("identity_email")

    # -- State: OTP has been sent, awaiting code ----------------------------

    if otp_sent_at:
        # Check for skip phrases
        if content_stripped.lower() in _SKIP_PHRASES:
            return IdentityAction(
                action="skip_verification",
                system_message=(
                    "No problem! Just so you know, without verification "
                    "I won't be able to access order details, account info, "
                    "or loyalty rewards. I can still help with general questions."
                ),
            )

        # Check for 6-digit OTP code
        if _OTP_PATTERN.match(content_stripped):
            # Rate limit check
            if otp_attempts >= _MAX_OTP_ATTEMPTS:
                return IdentityAction(
                    action="otp_rate_limited",
                    system_message=(
                        "You've reached the maximum number of verification "
                        "attempts. Please start a new conversation to try again."
                    ),
                )

            # Increment attempt counter
            try:
                await conv_repo.patch(
                    tenant_id,
                    conversation_id,
                    operations=[
                        {"op": "set", "path": "/identity_otp_attempts", "value": otp_attempts + 1},
                        {"op": "set", "path": "/updated_at", "value": datetime.now(UTC).isoformat()},
                    ],
                )
            except Exception as exc:
                logger.warning("Failed to increment OTP attempts: %s", exc)

            # Validate OTP
            is_valid = await _verify_otp_for_conversation(
                email=identity_email or "",
                code=content_stripped,
                tenant_id=tenant_id,
            )

            if is_valid:
                # Mark conversation as verified
                try:
                    now_iso = datetime.now(UTC).isoformat()
                    await conv_repo.patch(
                        tenant_id,
                        conversation_id,
                        operations=[
                            {"op": "set", "path": "/customer_verified", "value": True},
                            {"op": "set", "path": "/updated_at", "value": now_iso},
                        ],
                    )
                except Exception as exc:
                    logger.error("Failed to mark conversation verified: %s", exc)

                return IdentityAction(
                    action="otp_received",
                    email=identity_email,
                    system_message=(
                        "Email verified! I can now access your account information. How can I help you today?"
                    ),
                )
            else:
                return IdentityAction(
                    action="otp_invalid",
                    system_message=(
                        "That code doesn't look right. Please check your email "
                        "and try again, or say 'skip' to continue as a guest."
                    ),
                )

        # Not a code or skip phrase — check for phone before passing through.
        # Dual-state: email OTP pending, but customer may also provide phone.
        if not conv_doc.get("identity_sms_sent_at"):
            phone = _extract_phone(content_stripped)
            if phone:
                from src.multi_tenant.tier_utils import check_tier_gate

                if await check_tier_gate(tenant_id):
                    sent = await _send_sms_otp_for_conversation(phone=phone, tenant_id=tenant_id)
                    if sent:
                        try:
                            now_iso = datetime.now(UTC).isoformat()
                            await conv_repo.patch(
                                tenant_id,
                                conversation_id,
                                operations=[
                                    {"op": "set", "path": "/identity_phone", "value": phone},
                                    {"op": "set", "path": "/identity_sms_sent_at", "value": now_iso},
                                    {"op": "set", "path": "/identity_sms_attempts", "value": 0},
                                    {"op": "set", "path": "/updated_at", "value": now_iso},
                                ],
                            )
                        except Exception as exc:
                            logger.warning("Failed to update conversation with phone: %s", exc)

                        masked_phone = phone[:3] + "***" + phone[-3:] if len(phone) > 6 else phone
                        return IdentityAction(
                            action="phone_received",
                            phone=phone,
                            system_message=(
                                f"I've also sent an SMS code to {masked_phone}. "
                                f"You can verify with either the email or SMS code."
                            ),
                        )

        return IdentityAction(action="none")

    # -- State: SMS OTP pending (SPEC-1879 Phase 2A) -------------------------
    # Only enters SMS state machine if email OTP is NOT pending (email takes
    # precedence per dual-state design).

    sms_sent_at = conv_doc.get("identity_sms_sent_at")
    sms_attempts = conv_doc.get("identity_sms_attempts", 0)
    identity_phone = conv_doc.get("identity_phone")

    if sms_sent_at and not otp_sent_at:
        # Skip phrases
        if content_stripped.lower() in _SKIP_PHRASES:
            return IdentityAction(
                action="skip_verification",
                system_message=(
                    "No problem! Just so you know, without verification "
                    "I won't be able to access order details, account info, "
                    "or loyalty rewards. I can still help with general questions."
                ),
            )

        # Check for 6-digit SMS OTP code
        if _OTP_PATTERN.match(content_stripped):
            # Rate limit check (per-conversation SMS throttling)
            if sms_attempts >= _MAX_SMS_OTP_ATTEMPTS:
                return IdentityAction(
                    action="sms_otp_rate_limited",
                    system_message=(
                        "You've reached the maximum number of SMS verification "
                        "attempts. Please start a new conversation to try again."
                    ),
                )

            # Increment attempt counter
            try:
                await conv_repo.patch(
                    tenant_id,
                    conversation_id,
                    operations=[
                        {"op": "set", "path": "/identity_sms_attempts", "value": sms_attempts + 1},
                        {"op": "set", "path": "/updated_at", "value": datetime.now(UTC).isoformat()},
                    ],
                )
            except Exception as exc:
                logger.warning("Failed to increment SMS OTP attempts: %s", exc)

            # Validate SMS OTP
            is_valid = await _verify_sms_otp_for_conversation(
                phone=identity_phone or "",
                code=content_stripped,
                tenant_id=tenant_id,
            )

            if is_valid:
                # Mark phone as verified (phone_verified, NOT customer_verified)
                try:
                    now_iso = datetime.now(UTC).isoformat()
                    await conv_repo.patch(
                        tenant_id,
                        conversation_id,
                        operations=[
                            {"op": "set", "path": "/phone_verified", "value": True},
                            {"op": "set", "path": "/updated_at", "value": now_iso},
                        ],
                    )
                except Exception as exc:
                    logger.error("Failed to mark phone verified: %s", exc)

                # Mask phone for display (show country code + last 3 digits)
                masked_phone = (
                    identity_phone[:3] + "***" + identity_phone[-3:]
                    if identity_phone and len(identity_phone) > 6
                    else identity_phone or ""
                )

                return IdentityAction(
                    action="sms_otp_received",
                    phone=identity_phone,
                    system_message=(f"Phone {masked_phone} verified! Thanks for confirming your phone number."),
                )
            else:
                return IdentityAction(
                    action="sms_otp_invalid",
                    system_message=(
                        "That code doesn't look right. Please check your SMS "
                        "and try again, or say 'skip' to continue as a guest."
                    ),
                )

        # Not a code or skip phrase — check for email before passing through.
        # Dual-state: SMS OTP pending, but customer may also provide email.
        # Email takes precedence per spec — if email found, start email OTP too.
        if not conv_doc.get("identity_otp_sent_at"):
            email = _extract_email(content_stripped)
            if email:
                sent = await _send_otp_for_conversation(email=email, tenant_id=tenant_id)
                if sent:
                    try:
                        now_iso = datetime.now(UTC).isoformat()
                        await conv_repo.patch(
                            tenant_id,
                            conversation_id,
                            operations=[
                                {"op": "set", "path": "/identity_email", "value": email},
                                {"op": "set", "path": "/identity_otp_sent_at", "value": now_iso},
                                {"op": "set", "path": "/identity_otp_attempts", "value": 0},
                                {"op": "set", "path": "/updated_at", "value": now_iso},
                            ],
                        )
                    except Exception as exc:
                        logger.warning("Failed to update conversation with email: %s", exc)

                    parts = email.split("@")
                    masked = parts[0][:2] + "***@" + parts[1] if len(parts) == 2 else email
                    return IdentityAction(
                        action="email_received",
                        email=email,
                        system_message=(
                            f"I've also sent a verification code to {masked}. "
                            f"You can verify with either the email or SMS code."
                        ),
                    )

        return IdentityAction(action="none")

    # -- State: No OTP sent yet -- check for email address ------------------

    email = _extract_email(content_stripped)
    if email:
        # Send OTP
        sent = await _send_otp_for_conversation(email=email, tenant_id=tenant_id)
        if not sent:
            return IdentityAction(
                action="none",
                system_message=(
                    "I wasn't able to send a verification code right now. "
                    "Let me help you with what I can in the meantime."
                ),
            )

        # Update conversation with email + OTP timestamp
        try:
            now_iso = datetime.now(UTC).isoformat()
            await conv_repo.patch(
                tenant_id,
                conversation_id,
                operations=[
                    {"op": "set", "path": "/identity_email", "value": email},
                    {"op": "set", "path": "/identity_otp_sent_at", "value": now_iso},
                    {"op": "set", "path": "/identity_otp_attempts", "value": 0},
                    {"op": "set", "path": "/updated_at", "value": now_iso},
                ],
            )
        except Exception as exc:
            logger.warning("Failed to update conversation with identity email: %s", exc)

        # Mask email for display (show first 2 chars + domain)
        parts = email.split("@")
        masked = parts[0][:2] + "***@" + parts[1] if len(parts) == 2 else email

        return IdentityAction(
            action="email_received",
            email=email,
            system_message=(
                f"I've sent a verification code to {masked}. "
                f"Please enter the 6-digit code when you receive it, "
                f"or say 'skip' to continue as a guest."
            ),
        )

    # -- State: No email found -- check for phone (SPEC-1879 Phase 2A) -----
    # Phone detection only runs if no email collected AND no OTP pending

    if not identity_email and not otp_sent_at and not sms_sent_at:
        phone = _extract_phone(content_stripped)
        if phone:
            # Professional+ tier gate — starter tenants cannot use SMS OTP
            from src.multi_tenant.tier_utils import check_tier_gate

            if not await check_tier_gate(tenant_id):
                logger.info(
                    "SMS OTP blocked by tier gate: tenant=%s", tenant_id,
                )
                return IdentityAction(action="none")

            # Send SMS OTP
            sent = await _send_sms_otp_for_conversation(phone=phone, tenant_id=tenant_id)
            if not sent:
                return IdentityAction(
                    action="none",
                    system_message=(
                        "I wasn't able to send a verification code right now. "
                        "Let me help you with what I can in the meantime."
                    ),
                )

            # Update conversation with phone + SMS OTP timestamp
            try:
                now_iso = datetime.now(UTC).isoformat()
                await conv_repo.patch(
                    tenant_id,
                    conversation_id,
                    operations=[
                        {"op": "set", "path": "/identity_phone", "value": phone},
                        {"op": "set", "path": "/identity_sms_sent_at", "value": now_iso},
                        {"op": "set", "path": "/identity_sms_attempts", "value": 0},
                        {"op": "set", "path": "/updated_at", "value": now_iso},
                    ],
                )
            except Exception as exc:
                logger.warning("Failed to update conversation with identity phone: %s", exc)

            # Mask phone for display
            masked_phone = phone[:3] + "***" + phone[-3:] if len(phone) > 6 else phone

            return IdentityAction(
                action="phone_received",
                phone=phone,
                system_message=(
                    f"I've sent a verification code to {masked_phone}. "
                    f"Please enter the 6-digit code when you receive it, "
                    f"or say 'skip' to continue as a guest."
                ),
            )

    # -- Default: not an identity-related message ---------------------------

    return IdentityAction(action="none")
