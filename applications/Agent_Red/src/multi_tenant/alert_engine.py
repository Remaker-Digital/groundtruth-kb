# © 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""
Alert evaluation engine — evaluates rules against platform metrics.

Metric sources:
  - queue_depth: NATS JetStream per-tenant message count
  - circuit_breaker: ServiceCircuitBreakerRegistry breaker state
  - sla_breach: SLAMonitoringService uptime / error budget
  - secret_expiry: TenantSecretService disabled-secret count
  - incident: Active incident count from IncidentRepository

Operators: gt, lt, gte, lte, eq, ne

Cooldown: After a rule fires, it won't fire again until cooldown_minutes
has elapsed (checked via AlertHistoryRepository.get_last_trigger_for_rule).

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

from __future__ import annotations

import logging
import operator as op_module
from datetime import UTC, datetime, timedelta
from typing import Any

from src.multi_tenant.cosmos_schema import AlertSeverity

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Operator mapping
# ---------------------------------------------------------------------------

_OPERATORS: dict[str, Any] = {
    "gt": op_module.gt,
    "lt": op_module.lt,
    "gte": op_module.ge,
    "lte": op_module.le,
    "eq": op_module.eq,
    "ne": op_module.ne,
}


def _check_condition(metric_value: float, operator_str: str, threshold: float) -> bool:
    """Evaluate ``metric_value <op> threshold``."""
    fn = _OPERATORS.get(operator_str, op_module.gt)
    return bool(fn(metric_value, threshold))


# ---------------------------------------------------------------------------
# Metric collectors — one per rule type
# ---------------------------------------------------------------------------


async def _collect_queue_depth() -> float:
    """Sum of pending messages across all tenant NATS streams."""
    try:
        from src.multi_tenant.nats_isolation import get_nats_manager
        from src.multi_tenant.repository import TenantRepository

        nats_mgr = get_nats_manager()
        if not nats_mgr.is_connected:
            return 0

        tenant_repo = TenantRepository()
        tenant_ids = await tenant_repo.list_active_tenant_ids()

        total = 0
        for tid in tenant_ids:
            try:
                info = await nats_mgr.get_tenant_stream_info(tid)
                if info:
                    total += info.get("messages", 0)
            except Exception:
                pass
        return float(total)
    except Exception:
        logger.debug("Queue depth collection failed", exc_info=True)
        return 0


async def _collect_circuit_breaker() -> float:
    """Count of open circuit breakers."""
    try:
        from src.multi_tenant.pipeline_resilience import get_circuit_breaker_registry

        registry = get_circuit_breaker_registry()
        summary = registry.health_summary()
        services = summary.get("services", {})
        open_count = sum(
            1 for svc in services.values()
            if svc.get("state") in ("open", "half_open")
        )
        return float(open_count)
    except Exception:
        logger.debug("Circuit breaker collection failed", exc_info=True)
        return 0


async def _collect_sla_breach() -> float:
    """Current error budget remaining percentage (0-100).

    A rule like ``sla_breach lt 10`` fires when error budget drops below 10%.
    """
    try:
        from src.multi_tenant.sla_monitoring import get_sla_monitor

        monitor = get_sla_monitor()
        uptime = monitor.get_uptime_pct()
        # SLA target is 99.5%. Error budget = actual_uptime - target.
        # Expose as remaining budget percentage out of 0.5% budget.
        target = 99.5
        budget_total = 100 - target  # 0.5
        if budget_total <= 0:
            return 100.0
        used = max(0, target - uptime)
        remaining_pct = max(0, ((budget_total - used) / budget_total) * 100)
        return round(remaining_pct, 2)
    except Exception:
        logger.debug("SLA breach collection failed", exc_info=True)
        return 100.0  # Assume full budget if unavailable


async def _collect_secret_expiry() -> float:
    """Count of disabled secrets across all tenants."""
    try:
        from src.multi_tenant.repository import TenantRepository
        from src.multi_tenant.tenant_secret_service import TenantSecretService

        tenant_repo = TenantRepository()
        secret_svc = TenantSecretService()
        tenant_ids = await tenant_repo.list_active_tenant_ids()

        disabled = 0
        for tid in tenant_ids:
            try:
                secrets = await secret_svc.list_tenant_secrets(tid)
                disabled += sum(1 for s in secrets if not s.get("enabled", True))
            except Exception:
                pass
        return float(disabled)
    except Exception:
        logger.debug("Secret expiry collection failed", exc_info=True)
        return 0


async def _collect_incident_count() -> float:
    """Count of active (unresolved) incidents."""
    try:
        engine = get_alert_engine()
        if engine._incident_repo is None:
            return 0
        incidents = await engine._incident_repo.list_active()
        return float(len(incidents))
    except Exception:
        logger.debug("Incident count collection failed", exc_info=True)
        return 0


_METRIC_COLLECTORS: dict[str, Any] = {
    "queue_depth": _collect_queue_depth,
    "circuit_breaker": _collect_circuit_breaker,
    "sla_breach": _collect_sla_breach,
    "secret_expiry": _collect_secret_expiry,
    "incident": _collect_incident_count,
}


# ---------------------------------------------------------------------------
# Alert Engine
# ---------------------------------------------------------------------------


class AlertEngine:
    """Evaluates enabled alert rules against live metric sources.

    Usage::

        engine = AlertEngine(rule_repo, history_repo, incident_repo)
        result = await engine.evaluate_all()
    """

    def __init__(
        self,
        rule_repo: Any,
        history_repo: Any,
        incident_repo: Any | None = None,
    ) -> None:
        self._rule_repo = rule_repo
        self._history_repo = history_repo
        self._incident_repo = incident_repo

    async def evaluate_all(self) -> dict[str, Any]:
        """Evaluate all enabled rules. Returns summary of results."""
        rules = await self._rule_repo.list_enabled()
        evaluated = 0
        fired = 0
        skipped_cooldown = 0
        errors = 0

        for rule in rules:
            try:
                rule_type = rule.get("rule_type", "")
                condition = rule.get("condition", {})
                metric_name = condition.get("metric", rule_type)
                operator_str = condition.get("operator", "gt")
                threshold = float(condition.get("threshold", 0))
                cooldown_min = rule.get("cooldown_minutes", 60)

                # 1. Collect metric
                collector = _METRIC_COLLECTORS.get(rule_type)
                if collector is None:
                    logger.debug("No collector for rule type %s", rule_type)
                    errors += 1
                    continue

                metric_value = await collector()
                evaluated += 1

                # 2. Check condition
                if not _check_condition(metric_value, operator_str, threshold):
                    continue

                # 3. Check cooldown
                if await self._is_in_cooldown(rule["rule_id"], cooldown_min):
                    skipped_cooldown += 1
                    continue

                # 4. Fire alert
                severity = self._derive_severity(rule_type, metric_value, threshold)
                message = (
                    f"[{rule.get('name', rule_type)}] "
                    f"{metric_name} = {metric_value} "
                    f"(threshold: {operator_str} {threshold})"
                )

                await self._history_repo.log_alert(
                    rule_id=rule["rule_id"],
                    rule_name=rule.get("name", ""),
                    rule_type=rule_type,
                    severity=severity,
                    message=message,
                    metric_value=metric_value,
                    threshold_value=threshold,
                )
                fired += 1
                logger.warning(
                    "Alert fired: rule=%s metric=%s value=%.2f threshold=%.2f",
                    rule.get("name", ""), metric_name, metric_value, threshold,
                )

            except Exception:
                logger.debug("Rule evaluation failed: %s", rule.get("rule_id", "?"), exc_info=True)
                errors += 1

        return {
            "rules_evaluated": evaluated,
            "alerts_fired": fired,
            "skipped_cooldown": skipped_cooldown,
            "errors": errors,
        }

    async def _is_in_cooldown(self, rule_id: str, cooldown_minutes: int) -> bool:
        """Check if a rule is still within its cooldown period."""
        last = await self._history_repo.get_last_trigger_for_rule(rule_id)
        if last is None:
            return False

        triggered_at_str = last.get("triggered_at", "")
        if not triggered_at_str:
            return False

        try:
            triggered_at = datetime.fromisoformat(triggered_at_str)
            cooldown_until = triggered_at + timedelta(minutes=cooldown_minutes)
            return datetime.now(UTC) < cooldown_until
        except (ValueError, TypeError):
            return False

    @staticmethod
    def _derive_severity(rule_type: str, metric_value: float, threshold: float) -> str:
        """Derive alert severity from rule type and how far metric exceeds threshold.

        Heuristic: if the metric is more than 2x the threshold, it's critical.
        Otherwise, it's a warning. Specific rule types may override.
        """
        if rule_type == "circuit_breaker" and metric_value >= 2:
            return AlertSeverity.CRITICAL.value
        if rule_type == "sla_breach":
            # Low remaining budget is critical
            return AlertSeverity.CRITICAL.value if metric_value < 5 else AlertSeverity.WARNING.value

        if threshold > 0 and metric_value >= threshold * 2:
            return AlertSeverity.CRITICAL.value
        return AlertSeverity.WARNING.value


# ---------------------------------------------------------------------------
# Module-level singleton
# ---------------------------------------------------------------------------

_alert_engine: AlertEngine | None = None


def configure_alert_engine(
    rule_repo: Any,
    history_repo: Any,
    incident_repo: Any | None = None,
) -> AlertEngine:
    """Create and store the module-level AlertEngine singleton."""
    global _alert_engine  # noqa: PLW0603
    _alert_engine = AlertEngine(rule_repo, history_repo, incident_repo)
    logger.info("Alert engine configured")
    return _alert_engine


def get_alert_engine() -> AlertEngine:
    """Get the module-level AlertEngine singleton.

    Raises RuntimeError if not yet configured.
    """
    if _alert_engine is None:
        raise RuntimeError("AlertEngine not configured — call configure_alert_engine() first")
    return _alert_engine
