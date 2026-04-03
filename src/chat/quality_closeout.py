"""Quality closeout helper — shared across all conversation-end paths.

Called by:
  - session.py:end_conversation()
  - session.py:escalate_conversation()
  - admin_conversation_api.py:resolve_conversation()
  - admin_conversation_api.py:escalate_conversation()
  - conversation_meter.py:scan_idle_conversations()

Computes quality_aggregate from per-turn scores and evaluates quality
regression alerts. Both operations must happen at every closeout path
so the dashboard read path (_quality.py:242) always has data.

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

from __future__ import annotations

import logging
from typing import Any

logger = logging.getLogger(__name__)


async def evaluate_quality_and_alert(
    tenant_id: str,
    conversation_id: str,
    repo: Any,
) -> None:
    """Compute quality aggregate and evaluate regression alert.

    Args:
        tenant_id: Tenant identifier.
        conversation_id: Conversation that just ended.
        repo: ConversationRepository instance (for reading messages and patching).
    """
    try:
        # Step 1: Read conversation and extract per-turn quality scores
        doc = await repo.get(tenant_id, conversation_id)
        messages = doc.get("messages", [])

        scores: list[float] = []
        for msg in messages:
            meta = msg.get("metadata") or {}
            qs = meta.get("quality_score")
            if qs and isinstance(qs, dict) and "overall" in qs:
                scores.append(float(qs["overall"]))

        if not scores:
            return  # No scored turns — nothing to aggregate

        # Step 2: Compute aggregate
        aggregate = {
            "mean": sum(scores) / len(scores),
            "min": min(scores),
            "max": max(scores),
            "count": len(scores),
        }

        # Step 3: Persist quality_aggregate via patch
        await repo.patch(tenant_id, conversation_id, [
            {"op": "set", "path": "/quality_aggregate", "value": aggregate},
        ])

        logger.debug(
            "Quality aggregate persisted: conv=%s mean=%.2f count=%d",
            conversation_id, aggregate["mean"], aggregate["count"],
        )

        # Step 4: Evaluate quality regression alert
        await _evaluate_regression(tenant_id, conversation_id, aggregate)

    except Exception:
        # Quality closeout is non-fatal — never block conversation end
        logger.warning(
            "Quality closeout failed (non-fatal): tenant=%s conv=%s",
            tenant_id, conversation_id, exc_info=True,
        )


async def _evaluate_regression(
    tenant_id: str,
    conversation_id: str,
    aggregate: dict[str, float],
) -> None:
    """Evaluate quality regression using the alert rule system.

    Uses AlertRuleRepository to find the quality_regression rule,
    checks tenant-scoped cooldown, detects regression, and delivers alert.
    """
    try:
        from src.multi_tenant.repositories.alerts import AlertRuleRepository, AlertHistoryRepository
        from src.multi_tenant.alert_delivery import get_alert_service

        rule_repo = AlertRuleRepository()
        history_repo = AlertHistoryRepository()

        # Find the quality_regression rule
        rules = await rule_repo.list_rules()
        quality_rule = None
        for rule in rules:
            rule_dict = rule if isinstance(rule, dict) else rule.model_dump()
            if rule_dict.get("rule_type") == "quality_regression" and rule_dict.get("enabled", True):
                quality_rule = rule_dict
                break

        if not quality_rule:
            return

        # Check tenant-scoped cooldown
        rule_id = quality_rule.get("id", quality_rule.get("rule_id", ""))
        cooldown_minutes = quality_rule.get("cooldown_minutes", 60)
        last_trigger = await history_repo.get_last_trigger_for_rule(
            rule_id, tenant_id=tenant_id,
        )
        if last_trigger:
            from datetime import datetime, timezone, timedelta
            triggered_at = last_trigger.get("triggered_at", "")
            if triggered_at:
                try:
                    last_time = datetime.fromisoformat(triggered_at.replace("Z", "+00:00"))
                    if datetime.now(timezone.utc) - last_time < timedelta(minutes=cooldown_minutes):
                        return  # Still in cooldown
                except (ValueError, TypeError):
                    pass

        # Detect regression
        threshold = quality_rule.get("condition", {}).get("threshold", 0.5)
        from src.chat.quality_regression import detect_regression
        regression = detect_regression(
            tenant_id=tenant_id,
            current_score=aggregate["mean"],
            threshold=threshold,
        )

        if not regression:
            return

        # Log alert and deliver
        from datetime import datetime, timezone
        severity = "critical" if regression.get("drop", 0) > 1.0 else "warning"

        await history_repo.log_alert(
            rule_id=rule_id,
            rule_name=quality_rule.get("name", "Quality Regression"),
            rule_type="quality_regression",
            severity=severity,
            message=f"Quality dropped by {regression['drop']:.2f} points (tenant: {tenant_id})",
            metric_value=aggregate["mean"],
            threshold_value=threshold,
            tenant_id=tenant_id,
        )

        # Deliver via configured channels
        alert_service = get_alert_service()
        if alert_service:
            from src.multi_tenant.alert_delivery import Alert, AlertType, AlertSeverity
            channels = quality_rule.get("notification_channels")
            await alert_service.deliver_alert(
                Alert(
                    alert_id=f"qr-{conversation_id[:8]}",
                    tenant_id=tenant_id,
                    alert_type=AlertType.QUALITY_DROP if hasattr(AlertType, "QUALITY_DROP") else AlertType.ESCALATION,
                    severity=AlertSeverity(severity),
                    title=f"Quality Regression — {tenant_id}",
                    message=f"Mean quality score dropped to {aggregate['mean']:.2f} (threshold: {threshold})",
                ),
                channels=channels,
            )

        logger.info(
            "Quality regression alert: tenant=%s conv=%s drop=%.2f severity=%s",
            tenant_id, conversation_id, regression["drop"], severity,
        )

    except ImportError:
        # Alert infrastructure not available — skip silently
        pass
    except Exception:
        logger.warning(
            "Quality regression evaluation failed (non-fatal): tenant=%s",
            tenant_id, exc_info=True,
        )
