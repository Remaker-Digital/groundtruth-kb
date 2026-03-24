# © 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""Audit log sanitizer — SPEC-1843 / WI-1615.

Ensures audit log payloads never contain PII or tenant business data.
Two layers of protection:

1. **Allowlist gate**: Only explicitly allowed fields pass through.
   Any field not on the allowlist is silently dropped.

2. **PII regex scrub**: All string values in allowed fields are scrubbed
   for known PII patterns (emails, API keys, Stripe keys, Shopify tokens).

The sanitizer is integrated into AuditLogRepository.log_event() (WI-1616)
so ALL audit writes pass through it automatically.
"""
from __future__ import annotations

import re
from typing import Any

# ── Allowlisted payload fields ──────────────────────────────────────────
# Only these fields may appear in audit log payloads.  Any field not in
# this set is stripped before persistence.
ALLOWED_PAYLOAD_FIELDS: frozenset[str] = frozenset({
    "action",
    "resource_type",
    "resource_id",
    "result",
    "reason",
    "old_value_hash",
    "new_value_hash",
    "count",
    "duration_ms",
    "status_code",
})

# ── PII regex patterns ─────────────────────────────────────────────────
# Each tuple: (compiled regex, replacement string).
# Order matters — more specific patterns first to avoid partial matches.
_PII_PATTERNS: list[tuple[re.Pattern[str], str]] = [
    # Shopify access tokens: shpat_ followed by hex/alphanumeric
    (re.compile(r"shpat_[A-Za-z0-9_-]+"), "[SHOPIFY_TOKEN]"),
    # Stripe secret/publishable keys: sk_live_, sk_test_, pk_live_, pk_test_
    (re.compile(r"[sp]k_(live|test)_[A-Za-z0-9]+"), "[STRIPE_KEY]"),
    # Agent Red API keys: ar_live_, ar_spa_, ar_user_, ar_tenant_
    (re.compile(r"ar_(live|spa|user|tenant)_[A-Za-z0-9_-]+"), "[API_KEY]"),
    # Email addresses (RFC 5322 simplified)
    (re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}"), "[EMAIL]"),
]


def _scrub_pii(value: str) -> str:
    """Replace PII patterns in a string with safe placeholders."""
    for pattern, replacement in _PII_PATTERNS:
        value = pattern.sub(replacement, value)
    return value


def sanitize_audit_payload(payload: dict[str, Any]) -> dict[str, Any]:
    """Sanitize an audit event payload before persistence.

    1. Drop any field not in ALLOWED_PAYLOAD_FIELDS.
    2. Scrub remaining string values for PII patterns.

    Args:
        payload: Raw audit event payload dict.

    Returns:
        Sanitized payload with only allowed fields and scrubbed strings.
    """
    sanitized: dict[str, Any] = {}
    for key, value in payload.items():
        if key not in ALLOWED_PAYLOAD_FIELDS:
            continue
        if isinstance(value, str):
            sanitized[key] = _scrub_pii(value)
        else:
            sanitized[key] = value
    return sanitized


# ── SPA query projection (WI-1617) ─────────────────────────────────────
# SPA (cross-partition) audit queries return ONLY these top-level event
# fields.  The full payload is NEVER returned to SPA consumers.

_SPA_SAFE_EVENT_FIELDS: frozenset[str] = frozenset({
    "event_type",
    "timestamp",
    "tenant_id",
})


def sanitize_for_spa_query(event: dict[str, Any]) -> dict[str, Any]:
    """Project an audit event to SPA-safe fields only.

    SPA (Provider Console) queries must never see the payload or
    conversation details.  Only event_type, timestamp, tenant_id,
    and action (extracted from payload) are returned.

    Args:
        event: Full audit event document from Cosmos.

    Returns:
        Projected event with only SPA-safe fields + action.
    """
    result: dict[str, Any] = {}
    for key in _SPA_SAFE_EVENT_FIELDS:
        if key in event:
            result[key] = event[key]
    # Extract action from payload if present (safe metadata)
    payload = event.get("payload")
    result["action"] = payload.get("action") if isinstance(payload, dict) else None
    return result
