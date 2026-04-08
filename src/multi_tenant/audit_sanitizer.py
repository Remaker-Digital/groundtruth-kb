# (c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""Audit log sanitizer — SPEC-1843 / WI-1615.

Ensures audit log payloads never contain PII or tenant business data.
Three layers of protection:

1. **PII denylist**: Fields known to carry PII are unconditionally stripped.
2. **Allowlist gate**: Only explicitly allowed operational fields pass through.
3. **PII regex scrub + content truncation**: All surviving string values are
   scrubbed for known PII patterns and long content is truncated.

The sanitizer is integrated into AuditLogRepository.log_event() (WI-1616)
so ALL audit writes pass through it automatically.
"""
from __future__ import annotations

import re
from typing import Any

from src.multi_tenant.superadmin_api._pii_mask import mask_domain, mask_email

# ── PII denylist — always stripped ─────────────────────────────────────
# Fields that carry PII / tenant business data.  Unconditionally removed
# before any allowlist check.
PII_DENYLIST: frozenset[str] = frozenset({
    "email",
    "customer_email",
    "new_email",
    "recovery_email",
    "team_member_email",
    "deactivated_email",
    "name",
    "display_name",
    "customer",
    "phone",
    "api_key",
    "widget_key",
    "totp_seed",
    "session_token",
    "shopify_domain",
    "messages",
    "content",
    "body",
    "message",
    "diff_summary",
    "new_keys",
    "old_keys",
    "changes",
    "metadata",
})

# ── Allowlisted payload fields ──────────────────────────────────────────
# Only these operational / metadata fields may appear in audit log payloads.
# Any field not in this set (and not in PII_DENYLIST) is silently dropped.
ALLOWED_PAYLOAD_FIELDS: frozenset[str] = frozenset({
    "action",
    "resource_type",
    "resource_id",
    "result",
    "reason",
    "change_reason",
    "old_value_hash",
    "new_value_hash",
    "count",
    "entry_count",
    "field_count",
    "change_count",
    "error_count",
    "flag_count",
    "duration_ms",
    "duration_s",
    "latency_ms",
    "status",
    "status_code",
    "new_status",
    "previous_status",
    "version",
    "new_version",
    "previous_version",
    "from_version",
    "to_version",
    "active_version",
    "draft_version",
    "previous_active_version",
    "source_version",
    "demoted_version",
    "restored_version",
    "revision_name",
    "role",
    "team_member_role",
    "tier",
    "enabled",
    "disabled",
    "forced",
    "dry_run",
    "partial",
    "is_active",
    "passed",
    "failed",
    "success",
    "sent",
    "rollback",
    "indefinite",
    "needs_review",
    "enrolled",
    "deploy_id",
    "run_id",
    "deletion_id",
    "export_id",
    "alert_id",
    "member_id",
    "config_key",
    "config_name",
    "config_type",
    "alert_type",
    "list_type",
    "export_type",
    "deletion_type",
    "suite",
    "environment",
    "image",
    "previous_image",
    "title",
    "steps",
    "flags",
    "severity",
    "auth_method",
    "key_suffix",
    "key_hash_prefix",
    "path",
    "method",
    "client_ip",
    "fields_changed",
    "block_reason",
    "scheduled_start",
    "scheduled_end",
    "billing_period",
    "included_allowance",
    "total_conversations",
    "usage_percent",
    "local_overage",
    "stripe_meter_total",
    "discrepancy",
    "discrepancy_percent",
    "circuit_breaker_state",
    "response_length",
    "backup_codes_remaining",
    "stores_deleted",
    "stores_exported",
    "expires_in",
    "appearance_name",
    "created_by",
    "activated_by",
    "deactivated_by",
    "deactivated_at",
    "regenerated_at",
})

_CONTENT_TRUNCATION_THRESHOLD = 100

# ── PII regex patterns ─────────────────────────────────────────────────
# Each tuple: (compiled regex, replacement string).
# Order matters — more specific patterns first to avoid partial matches.
_PII_PATTERNS: list[tuple[re.Pattern[str], str]] = [
    # TOTP seeds (base32-encoded, 16-32 chars)
    (re.compile(r"\b[A-Z2-7]{16,32}\b"), "[TOTP_SEED]"),
    # Shopify access tokens: shpat_ followed by hex/alphanumeric
    (re.compile(r"shpat_[A-Za-z0-9_-]+"), "[SHOPIFY_TOKEN]"),
    # Stripe secret/restricted/publishable keys
    (re.compile(r"[spr]k_(live|test)_[A-Za-z0-9]+"), "[STRIPE_KEY]"),
    # Agent Red API keys: ar_live_, ar_spa_, ar_user_, ar_tenant_
    (re.compile(r"ar_(live|spa|user|tenant)_[A-Za-z0-9_-]+"), "[API_KEY]"),
    # Phone numbers (international and US formats)
    (re.compile(r"\+?1?[-.\s]?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}\b"), "[PHONE]"),
    # Email addresses (RFC 5322 simplified)
    (re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}"), "[EMAIL]"),
]


def _scrub_pii(value: str) -> str:
    """Replace PII patterns in a string with safe placeholders."""
    for pattern, replacement in _PII_PATTERNS:
        value = pattern.sub(replacement, value)
    if len(value) > _CONTENT_TRUNCATION_THRESHOLD:
        value = f"[redacted: {len(value)} chars]"
    return value


def _scrub_value(value: Any) -> Any:
    """Recursively scrub PII from a value (string, list, or dict)."""
    if isinstance(value, str):
        return _scrub_pii(value)
    if isinstance(value, list):
        return [_scrub_value(v) for v in value]
    if isinstance(value, dict):
        return {k: _scrub_value(v) for k, v in value.items()
                if k not in PII_DENYLIST}
    return value


def sanitize_audit_payload(payload: dict[str, Any]) -> dict[str, Any]:
    """Sanitize an audit event payload before persistence.

    1. Strip any field in PII_DENYLIST unconditionally.
    2. Drop any remaining field not in ALLOWED_PAYLOAD_FIELDS.
    3. Scrub surviving values for PII patterns and truncate long content.

    Args:
        payload: Raw audit event payload dict.

    Returns:
        Sanitized payload with only allowed fields and scrubbed values.
    """
    sanitized: dict[str, Any] = {}
    for key, value in payload.items():
        if key in PII_DENYLIST:
            continue
        if key not in ALLOWED_PAYLOAD_FIELDS:
            continue
        sanitized[key] = _scrub_value(value)
    return sanitized


# ── SPA query projection (WI-1617) ─────────────────────────────────────
# SPA (cross-partition) audit queries return ONLY these top-level event
# fields.  The full payload is NEVER returned to SPA consumers.

_SPA_SAFE_EVENT_FIELDS: frozenset[str] = frozenset({
    "id",
    "event_type",
    "timestamp",
    "tenant_id",
    "actor",
    "actor_type",
})


def sanitize_for_spa_query(event: dict[str, Any]) -> dict[str, Any]:
    """Project an audit event to SPA-safe fields only.

    SPA (Provider Console) queries must never see the full payload or
    conversation details.  Only safe metadata fields and the action
    extracted from payload are returned.

    Args:
        event: Full audit event document from Cosmos.

    Returns:
        Projected event with only SPA-safe fields + action.
    """
    result: dict[str, Any] = {}
    for key in _SPA_SAFE_EVENT_FIELDS:
        if key in event:
            result[key] = event[key]
    payload = event.get("payload")
    result["action"] = payload.get("action") if isinstance(payload, dict) else None
    return result
