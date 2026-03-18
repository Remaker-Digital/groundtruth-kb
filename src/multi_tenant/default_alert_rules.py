"""Default alert rules — ship operational monitoring out of the box (SPEC-1831).

Seeds 8 default alert rules into Cosmos ``platform_config`` on application
startup if no alert_rules documents exist. Rules are fully editable and
deletable by platform admins via the SPA Control Plane.

Called from application startup (lifespan). Safe to call repeatedly — skips
seeding when rules already exist.

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""
from __future__ import annotations

import logging
from datetime import datetime, timezone
from typing import Any

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Config type used in Cosmos platform_config
# ---------------------------------------------------------------------------

ALERT_RULES_CONFIG_TYPE = "alert_rules"

# ---------------------------------------------------------------------------
# Default alert rule definitions (SPEC-1831)
# ---------------------------------------------------------------------------

DEFAULT_ALERT_RULES: list[dict[str, Any]] = [
    {
        "rule_id": "circuit_breaker_open",
        "name": "Circuit Breaker Open",
        "description": "Alert when any service circuit breaker enters OPEN state.",
        "severity": "critical",
        "cooldown_minutes": 5,
        "enabled": True,
        "condition": {
            "metric": "circuit_breaker_state",
            "operator": "eq",
            "value": "open",
        },
    },
    {
        "rule_id": "error_rate_spike",
        "name": "Error Rate Spike",
        "description": "Alert when tenant error rate exceeds 10% over 5-minute window.",
        "severity": "critical",
        "cooldown_minutes": 5,
        "enabled": True,
        "condition": {
            "metric": "error_rate_pct",
            "operator": "gt",
            "value": 10,
            "window_minutes": 5,
        },
    },
    {
        "rule_id": "sla_breach_approaching",
        "name": "SLA Breach Approaching",
        "description": "Alert when error budget remaining drops below 20%.",
        "severity": "warning",
        "cooldown_minutes": 15,
        "enabled": True,
        "condition": {
            "metric": "error_budget_remaining_pct",
            "operator": "lt",
            "value": 20,
        },
    },
    {
        "rule_id": "high_latency",
        "name": "High Latency",
        "description": "Alert when P95 latency exceeds 3000ms for any tier.",
        "severity": "warning",
        "cooldown_minutes": 15,
        "enabled": True,
        "condition": {
            "metric": "p95_latency_ms",
            "operator": "gt",
            "value": 3000,
        },
    },
    {
        "rule_id": "rate_limit_saturation",
        "name": "Rate Limit Saturation",
        "description": "Alert when any tenant exceeds 80% of rate limit allocation.",
        "severity": "warning",
        "cooldown_minutes": 15,
        "enabled": True,
        "condition": {
            "metric": "rate_limit_usage_pct",
            "operator": "gt",
            "value": 80,
        },
    },
    {
        "rule_id": "secret_expiry",
        "name": "Secret Expiry Warning",
        "description": "Alert when any tenant secret expires within 7 days.",
        "severity": "info",
        "cooldown_minutes": 60,
        "enabled": True,
        "condition": {
            "metric": "secret_days_until_expiry",
            "operator": "lt",
            "value": 7,
        },
    },
    {
        "rule_id": "audit_log_size",
        "name": "Audit Log Size",
        "description": "Alert when audit log collection exceeds 1GB per tenant.",
        "severity": "info",
        "cooldown_minutes": 60,
        "enabled": True,
        "condition": {
            "metric": "audit_log_size_bytes",
            "operator": "gt",
            "value": 1_073_741_824,  # 1 GB
        },
    },
    {
        "rule_id": "scaling_ceiling",
        "name": "Scaling Ceiling",
        "description": "Alert when active replicas equal max_replicas for 10+ minutes.",
        "severity": "critical",
        "cooldown_minutes": 5,
        "enabled": True,
        "condition": {
            "metric": "replicas_at_max",
            "operator": "eq",
            "value": True,
            "duration_minutes": 10,
        },
    },
]


# ---------------------------------------------------------------------------
# Seed function (called from app startup)
# ---------------------------------------------------------------------------


async def seed_default_alert_rules() -> int:
    """Seed default alert rules into platform_config if none exist.

    Returns the number of rules seeded (0 if rules already exist).
    Safe to call repeatedly — checks for existing rules first.
    """
    try:
        from src.multi_tenant.repositories.platform import PlatformConfigRepository
        repo = PlatformConfigRepository()
    except Exception:
        logger.debug("Cannot seed alert rules: PlatformConfigRepository not available")
        return 0

    # Check if any alert rules already exist
    try:
        from src.multi_tenant.cosmos_schema import PlatformConfigDocument
        existing = await repo.get_config(ALERT_RULES_CONFIG_TYPE, "all_rules")
        if existing is not None:
            logger.debug("Alert rules already exist — skipping seed")
            return 0
    except Exception:
        logger.debug("Alert rules check failed — skipping seed", exc_info=True)
        return 0

    # Seed the default rules
    now = datetime.now(timezone.utc).isoformat()
    rules_by_id = {rule["rule_id"]: rule for rule in DEFAULT_ALERT_RULES}

    doc = PlatformConfigDocument(
        id=f"{ALERT_RULES_CONFIG_TYPE}:all_rules",
        config_type=ALERT_RULES_CONFIG_TYPE,
        config_key="all_rules",
        value=rules_by_id,
        version=1,
        updated_at=now,
        updated_by="default_alert_rules.seed",
    )

    try:
        await repo.set_config(doc)
        logger.info("Seeded %d default alert rules", len(DEFAULT_ALERT_RULES))
        return len(DEFAULT_ALERT_RULES)
    except Exception:
        logger.warning("Failed to seed default alert rules", exc_info=True)
        return 0


def get_default_alert_rules() -> list[dict[str, Any]]:
    """Return the default alert rule definitions (for testing/reference)."""
    return list(DEFAULT_ALERT_RULES)
