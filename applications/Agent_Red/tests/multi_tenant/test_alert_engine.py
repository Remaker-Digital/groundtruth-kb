"""
Tests for AlertEngine — rule evaluation, cooldown, severity, metric collectors, singleton.

Tests cover:
    - _check_condition() with all 6 operators (gt, lt, gte, lte, eq, ne)
    - evaluate_all() — no rules, single rule fires, single rule does not fire
    - Cooldown enforcement — in cooldown skipped, expired cooldown fires
    - _derive_severity() — circuit_breaker, sla_breach, 2x threshold, default
    - Metric collectors — mock underlying services, verify correct values
    - Multiple rules — mixed fire/skip/cooldown
    - Error handling — missing collector, collector exception
    - Singleton — configure + get, get without configure raises RuntimeError

(C) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

import src.multi_tenant.alert_engine as alert_engine_module
from src.multi_tenant.alert_engine import (
    AlertEngine,
    _METRIC_COLLECTORS,
    _check_condition,
    _collect_circuit_breaker,
    _collect_incident_count,
    _collect_queue_depth,
    _collect_secret_expiry,
    _collect_sla_breach,
    configure_alert_engine,
    get_alert_engine,
)
from src.multi_tenant.cosmos_schema import AlertSeverity


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture()
def mock_rule_repo() -> AsyncMock:
    repo = AsyncMock()
    repo.list_enabled = AsyncMock(return_value=[])
    return repo


@pytest.fixture()
def mock_history_repo() -> AsyncMock:
    repo = AsyncMock()
    repo.log_alert = AsyncMock()
    repo.get_last_trigger_for_rule = AsyncMock(return_value=None)
    return repo


@pytest.fixture()
def mock_incident_repo() -> AsyncMock:
    repo = AsyncMock()
    repo.list_active = AsyncMock(return_value=[])
    return repo


@pytest.fixture()
def engine(mock_rule_repo, mock_history_repo, mock_incident_repo) -> AlertEngine:
    return AlertEngine(mock_rule_repo, mock_history_repo, mock_incident_repo)


@pytest.fixture(autouse=True)
def _reset_singleton():
    """Reset the module-level singleton before and after each test."""
    alert_engine_module._alert_engine = None
    yield
    alert_engine_module._alert_engine = None


def _make_rule(
    rule_id: str = "rule-1",
    name: str = "Test Rule",
    rule_type: str = "queue_depth",
    operator: str = "gt",
    threshold: float = 100,
    cooldown_minutes: int = 60,
) -> dict:
    return {
        "rule_id": rule_id,
        "name": name,
        "rule_type": rule_type,
        "condition": {
            "metric": rule_type,
            "operator": operator,
            "threshold": threshold,
        },
        "cooldown_minutes": cooldown_minutes,
    }


def _mock_collector(return_value: float) -> AsyncMock:
    """Create an AsyncMock collector returning a fixed metric value."""
    return AsyncMock(return_value=return_value)


# ---------------------------------------------------------------------------
# _check_condition — all 6 operators
# ---------------------------------------------------------------------------


class TestCheckCondition:
    """Verify _check_condition evaluates all 6 operators correctly."""

    def test_gt_true(self):
        assert _check_condition(10, "gt", 5) is True

    def test_gt_false(self):
        assert _check_condition(5, "gt", 10) is False

    def test_lt_true(self):
        assert _check_condition(3, "lt", 7) is True

    def test_lt_false(self):
        assert _check_condition(7, "lt", 3) is False

    def test_gte_true_greater(self):
        assert _check_condition(10, "gte", 5) is True

    def test_gte_true_equal(self):
        assert _check_condition(5, "gte", 5) is True

    def test_gte_false(self):
        assert _check_condition(4, "gte", 5) is False

    def test_lte_true_less(self):
        assert _check_condition(3, "lte", 5) is True

    def test_lte_true_equal(self):
        assert _check_condition(5, "lte", 5) is True

    def test_lte_false(self):
        assert _check_condition(6, "lte", 5) is False

    def test_eq_true(self):
        assert _check_condition(42, "eq", 42) is True

    def test_eq_false(self):
        assert _check_condition(42, "eq", 43) is False

    def test_ne_true(self):
        assert _check_condition(10, "ne", 20) is True

    def test_ne_false(self):
        assert _check_condition(10, "ne", 10) is False

    def test_unknown_operator_defaults_to_gt(self):
        """Unknown operator falls back to gt."""
        assert _check_condition(10, "unknown_op", 5) is True
        assert _check_condition(5, "unknown_op", 10) is False


# ---------------------------------------------------------------------------
# _derive_severity
# ---------------------------------------------------------------------------


class TestDeriveSeverity:
    """Verify severity derivation heuristics."""

    def test_circuit_breaker_gte_2_is_critical(self):
        result = AlertEngine._derive_severity("circuit_breaker", 2, 1)
        assert result == AlertSeverity.CRITICAL.value

    def test_circuit_breaker_below_2_is_warning(self):
        result = AlertEngine._derive_severity("circuit_breaker", 1, 1)
        assert result == AlertSeverity.WARNING.value

    def test_sla_breach_below_5_is_critical(self):
        result = AlertEngine._derive_severity("sla_breach", 3.5, 10)
        assert result == AlertSeverity.CRITICAL.value

    def test_sla_breach_above_5_is_warning(self):
        result = AlertEngine._derive_severity("sla_breach", 8, 10)
        assert result == AlertSeverity.WARNING.value

    def test_generic_2x_threshold_is_critical(self):
        """Metric value >= 2x threshold is critical for generic rule types."""
        result = AlertEngine._derive_severity("queue_depth", 200, 100)
        assert result == AlertSeverity.CRITICAL.value

    def test_generic_below_2x_threshold_is_warning(self):
        result = AlertEngine._derive_severity("queue_depth", 150, 100)
        assert result == AlertSeverity.WARNING.value

    def test_zero_threshold_defaults_to_warning(self):
        """When threshold is 0, the 2x check is skipped (threshold > 0 guard)."""
        result = AlertEngine._derive_severity("queue_depth", 999, 0)
        assert result == AlertSeverity.WARNING.value


# ---------------------------------------------------------------------------
# evaluate_all
# ---------------------------------------------------------------------------


class TestEvaluateAll:
    """Verify the main evaluation loop.

    Uses patch.dict on _METRIC_COLLECTORS because evaluate_all() resolves
    collectors via the dict, not by module-level name lookup.
    """

    @pytest.mark.asyncio
    async def test_no_rules_returns_zero_counts(self, engine, mock_rule_repo):
        mock_rule_repo.list_enabled.return_value = []
        result = await engine.evaluate_all()
        assert result == {
            "rules_evaluated": 0,
            "alerts_fired": 0,
            "skipped_cooldown": 0,
            "errors": 0,
        }

    @pytest.mark.asyncio
    async def test_single_rule_fires(self, engine, mock_rule_repo, mock_history_repo):
        rule = _make_rule(rule_type="queue_depth", operator="gt", threshold=50)
        mock_rule_repo.list_enabled.return_value = [rule]

        with patch.dict(
            _METRIC_COLLECTORS,
            {"queue_depth": _mock_collector(120.0)},
        ):
            result = await engine.evaluate_all()

        assert result["rules_evaluated"] == 1
        assert result["alerts_fired"] == 1
        mock_history_repo.log_alert.assert_called_once()

    @pytest.mark.asyncio
    async def test_single_rule_does_not_fire(self, engine, mock_rule_repo, mock_history_repo):
        rule = _make_rule(rule_type="queue_depth", operator="gt", threshold=200)
        mock_rule_repo.list_enabled.return_value = [rule]

        with patch.dict(
            _METRIC_COLLECTORS,
            {"queue_depth": _mock_collector(50.0)},
        ):
            result = await engine.evaluate_all()

        assert result["rules_evaluated"] == 1
        assert result["alerts_fired"] == 0
        mock_history_repo.log_alert.assert_not_called()

    @pytest.mark.asyncio
    async def test_log_alert_receives_correct_args(self, engine, mock_rule_repo, mock_history_repo):
        rule = _make_rule(
            rule_id="r-abc",
            name="High Queue",
            rule_type="queue_depth",
            operator="gt",
            threshold=10,
        )
        mock_rule_repo.list_enabled.return_value = [rule]

        with patch.dict(
            _METRIC_COLLECTORS,
            {"queue_depth": _mock_collector(25.0)},
        ):
            await engine.evaluate_all()

        call_kwargs = mock_history_repo.log_alert.call_args[1]
        assert call_kwargs["rule_id"] == "r-abc"
        assert call_kwargs["rule_name"] == "High Queue"
        assert call_kwargs["rule_type"] == "queue_depth"
        assert call_kwargs["metric_value"] == 25.0
        assert call_kwargs["threshold_value"] == 10


# ---------------------------------------------------------------------------
# Cooldown enforcement
# ---------------------------------------------------------------------------


class TestCooldown:
    """Verify cooldown prevents repeated alerting."""

    @pytest.mark.asyncio
    async def test_in_cooldown_skips_alert(self, engine, mock_rule_repo, mock_history_repo):
        rule = _make_rule(cooldown_minutes=60)
        mock_rule_repo.list_enabled.return_value = [rule]

        recent_trigger = datetime.now(timezone.utc) - timedelta(minutes=30)
        mock_history_repo.get_last_trigger_for_rule.return_value = {
            "triggered_at": recent_trigger.isoformat(),
        }

        with patch.dict(
            _METRIC_COLLECTORS,
            {"queue_depth": _mock_collector(999.0)},
        ):
            result = await engine.evaluate_all()

        assert result["skipped_cooldown"] == 1
        assert result["alerts_fired"] == 0

    @pytest.mark.asyncio
    async def test_expired_cooldown_fires(self, engine, mock_rule_repo, mock_history_repo):
        rule = _make_rule(cooldown_minutes=60)
        mock_rule_repo.list_enabled.return_value = [rule]

        old_trigger = datetime.now(timezone.utc) - timedelta(minutes=90)
        mock_history_repo.get_last_trigger_for_rule.return_value = {
            "triggered_at": old_trigger.isoformat(),
        }

        with patch.dict(
            _METRIC_COLLECTORS,
            {"queue_depth": _mock_collector(999.0)},
        ):
            result = await engine.evaluate_all()

        assert result["alerts_fired"] == 1
        assert result["skipped_cooldown"] == 0

    @pytest.mark.asyncio
    async def test_no_previous_trigger_not_in_cooldown(self, engine, mock_history_repo):
        mock_history_repo.get_last_trigger_for_rule.return_value = None
        in_cooldown = await engine._is_in_cooldown("rule-1", 60)
        assert in_cooldown is False

    @pytest.mark.asyncio
    async def test_empty_triggered_at_not_in_cooldown(self, engine, mock_history_repo):
        mock_history_repo.get_last_trigger_for_rule.return_value = {"triggered_at": ""}
        in_cooldown = await engine._is_in_cooldown("rule-1", 60)
        assert in_cooldown is False

    @pytest.mark.asyncio
    async def test_malformed_triggered_at_not_in_cooldown(self, engine, mock_history_repo):
        mock_history_repo.get_last_trigger_for_rule.return_value = {
            "triggered_at": "not-a-date",
        }
        in_cooldown = await engine._is_in_cooldown("rule-1", 60)
        assert in_cooldown is False


# ---------------------------------------------------------------------------
# Multiple rules
# ---------------------------------------------------------------------------


class TestMultipleRules:
    """Verify mixed scenarios with multiple rules."""

    @pytest.mark.asyncio
    async def test_some_fire_some_skip_some_cooldown(
        self, engine, mock_rule_repo, mock_history_repo
    ):
        rule_fires = _make_rule(rule_id="r-fire", rule_type="queue_depth", threshold=10)
        rule_no_fire = _make_rule(rule_id="r-nope", rule_type="queue_depth", threshold=9999)
        rule_cooldown = _make_rule(rule_id="r-cool", rule_type="queue_depth", threshold=10)

        mock_rule_repo.list_enabled.return_value = [rule_fires, rule_no_fire, rule_cooldown]

        recent = datetime.now(timezone.utc) - timedelta(minutes=5)

        async def _get_last(rule_id):
            if rule_id == "r-cool":
                return {"triggered_at": recent.isoformat()}
            return None

        mock_history_repo.get_last_trigger_for_rule.side_effect = _get_last

        with patch.dict(
            _METRIC_COLLECTORS,
            {"queue_depth": _mock_collector(500.0)},
        ):
            result = await engine.evaluate_all()

        assert result["rules_evaluated"] == 3
        assert result["alerts_fired"] == 1
        assert result["skipped_cooldown"] == 1
        assert result["errors"] == 0


# ---------------------------------------------------------------------------
# Error handling
# ---------------------------------------------------------------------------


class TestErrorHandling:
    """Verify graceful error paths in evaluation."""

    @pytest.mark.asyncio
    async def test_unknown_rule_type_increments_errors(self, engine, mock_rule_repo):
        rule = _make_rule(rule_type="nonexistent_metric")
        mock_rule_repo.list_enabled.return_value = [rule]

        result = await engine.evaluate_all()
        assert result["errors"] == 1
        assert result["rules_evaluated"] == 0

    @pytest.mark.asyncio
    async def test_collector_exception_increments_errors(self, engine, mock_rule_repo):
        rule = _make_rule(rule_type="queue_depth")
        mock_rule_repo.list_enabled.return_value = [rule]

        failing_collector = AsyncMock(side_effect=RuntimeError("NATS down"))
        with patch.dict(
            _METRIC_COLLECTORS,
            {"queue_depth": failing_collector},
        ):
            result = await engine.evaluate_all()

        assert result["errors"] == 1
        assert result["alerts_fired"] == 0


# ---------------------------------------------------------------------------
# Metric collectors
# ---------------------------------------------------------------------------


class TestMetricCollectors:
    """Verify each metric collector returns expected values from mocked services.

    Collectors use lazy imports (from X import Y inside the function body),
    so patches must target the source module where the name is defined.
    """

    @pytest.mark.asyncio
    async def test_collect_queue_depth(self):
        mock_nats = MagicMock()
        mock_nats.is_connected = True
        mock_nats.get_tenant_stream_info = AsyncMock(
            return_value={"messages": 42},
        )

        mock_tenant_repo = MagicMock()
        mock_tenant_repo.list_active_tenant_ids = AsyncMock(
            return_value=["t-1", "t-2"],
        )

        with (
            patch(
                "src.multi_tenant.nats_isolation.get_nats_manager",
                return_value=mock_nats,
            ),
            patch(
                "src.multi_tenant.repository.TenantRepository",
                return_value=mock_tenant_repo,
            ),
        ):
            value = await _collect_queue_depth()

        assert value == 84.0  # 42 * 2 tenants

    @pytest.mark.asyncio
    async def test_collect_queue_depth_nats_disconnected(self):
        mock_nats = MagicMock()
        mock_nats.is_connected = False

        with patch(
            "src.multi_tenant.nats_isolation.get_nats_manager",
            return_value=mock_nats,
        ):
            value = await _collect_queue_depth()

        assert value == 0

    @pytest.mark.asyncio
    async def test_collect_circuit_breaker(self):
        mock_registry = MagicMock()
        mock_registry.health_summary.return_value = {
            "services": {
                "openai": {"state": "open"},
                "cosmos": {"state": "closed"},
                "nats": {"state": "half_open"},
            },
        }

        with patch(
            "src.multi_tenant.pipeline_resilience.get_circuit_breaker_registry",
            return_value=mock_registry,
        ):
            value = await _collect_circuit_breaker()

        assert value == 2.0  # open + half_open

    @pytest.mark.asyncio
    async def test_collect_sla_breach(self):
        mock_monitor = MagicMock()
        mock_monitor.get_uptime_pct.return_value = 99.3

        with patch(
            "src.multi_tenant.sla_monitoring.get_sla_monitor",
            return_value=mock_monitor,
        ):
            value = await _collect_sla_breach()

        # budget_total = 0.5, used = max(0, 99.5 - 99.3) = 0.2
        # remaining_pct = ((0.5 - 0.2) / 0.5) * 100 = 60.0
        assert value == 60.0

    @pytest.mark.asyncio
    async def test_collect_sla_breach_full_budget(self):
        mock_monitor = MagicMock()
        mock_monitor.get_uptime_pct.return_value = 99.9

        with patch(
            "src.multi_tenant.sla_monitoring.get_sla_monitor",
            return_value=mock_monitor,
        ):
            value = await _collect_sla_breach()

        # used = max(0, 99.5 - 99.9) = 0, remaining = 100%
        assert value == 100.0

    @pytest.mark.asyncio
    async def test_collect_secret_expiry(self):
        mock_tenant_repo = MagicMock()
        mock_tenant_repo.list_active_tenant_ids = AsyncMock(return_value=["t-1"])

        mock_secret_svc = MagicMock()
        mock_secret_svc.list_tenant_secrets = AsyncMock(
            return_value=[
                {"name": "key1", "enabled": True},
                {"name": "key2", "enabled": False},
                {"name": "key3", "enabled": False},
            ],
        )

        with (
            patch(
                "src.multi_tenant.repository.TenantRepository",
                return_value=mock_tenant_repo,
            ),
            patch(
                "src.multi_tenant.tenant_secret_service.TenantSecretService",
                return_value=mock_secret_svc,
            ),
        ):
            value = await _collect_secret_expiry()

        assert value == 2.0

    @pytest.mark.asyncio
    async def test_collect_incident_count(self):
        mock_incident_repo = AsyncMock()
        mock_incident_repo.list_active.return_value = [
            {"id": "inc-1"},
            {"id": "inc-2"},
            {"id": "inc-3"},
        ]

        configure_alert_engine(
            rule_repo=AsyncMock(),
            history_repo=AsyncMock(),
            incident_repo=mock_incident_repo,
        )

        value = await _collect_incident_count()
        assert value == 3.0

    @pytest.mark.asyncio
    async def test_collect_incident_count_no_repo(self):
        configure_alert_engine(
            rule_repo=AsyncMock(),
            history_repo=AsyncMock(),
            incident_repo=None,
        )

        value = await _collect_incident_count()
        assert value == 0


# ---------------------------------------------------------------------------
# Singleton
# ---------------------------------------------------------------------------


class TestSingleton:
    """Verify module-level singleton management."""

    def test_get_before_configure_raises(self):
        with pytest.raises(RuntimeError, match="AlertEngine not configured"):
            get_alert_engine()

    def test_configure_then_get(self):
        rule_repo = AsyncMock()
        history_repo = AsyncMock()
        eng = configure_alert_engine(rule_repo, history_repo)

        assert get_alert_engine() is eng

    def test_configure_replaces_previous(self):
        eng1 = configure_alert_engine(AsyncMock(), AsyncMock())
        eng2 = configure_alert_engine(AsyncMock(), AsyncMock())

        assert get_alert_engine() is eng2
        assert eng1 is not eng2

    def test_configure_returns_engine_instance(self):
        eng = configure_alert_engine(AsyncMock(), AsyncMock())
        assert isinstance(eng, AlertEngine)

    def test_configure_with_incident_repo(self):
        incident_repo = AsyncMock()
        eng = configure_alert_engine(AsyncMock(), AsyncMock(), incident_repo)
        assert eng._incident_repo is incident_repo

    def test_configure_without_incident_repo(self):
        eng = configure_alert_engine(AsyncMock(), AsyncMock())
        assert eng._incident_repo is None
