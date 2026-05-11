"""Tests for SPEC-1831: Default Alert Rules Ship with System.

Verifies that the platform seeds 8 default alert rules at startup,
each with severity and cooldown, stored in platform_config.

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""
from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from src.multi_tenant.default_alert_rules import (
    ALERT_RULES_CONFIG_TYPE,
    DEFAULT_ALERT_RULES,
    get_default_alert_rules,
    seed_default_alert_rules,
)


# ---------------------------------------------------------------------------
# Default rule definitions
# ---------------------------------------------------------------------------


class TestDefaultRuleDefinitions:
    """Verify the 8 default alert rules match SPEC-1831."""

    def test_exactly_8_default_rules(self):
        """SPEC-1831: 8 rules ship with the system."""
        assert len(DEFAULT_ALERT_RULES) == 8

    def test_required_rule_ids(self):
        """All 8 SPEC-1831 rules are present by rule_id."""
        expected_ids = {
            "circuit_breaker_open",
            "error_rate_spike",
            "sla_breach_approaching",
            "high_latency",
            "rate_limit_saturation",
            "secret_expiry",
            "audit_log_size",
            "scaling_ceiling",
        }
        actual_ids = {r["rule_id"] for r in DEFAULT_ALERT_RULES}
        assert actual_ids == expected_ids

    def test_every_rule_has_severity(self):
        """Every rule has a severity field (critical, warning, or info)."""
        valid_severities = {"critical", "warning", "info"}
        for rule in DEFAULT_ALERT_RULES:
            assert rule["severity"] in valid_severities, (
                f"Rule '{rule['rule_id']}' has invalid severity: {rule['severity']}"
            )

    def test_every_rule_has_cooldown_minutes(self):
        """Every rule has a positive cooldown_minutes."""
        for rule in DEFAULT_ALERT_RULES:
            assert "cooldown_minutes" in rule, f"Missing cooldown: {rule['rule_id']}"
            assert rule["cooldown_minutes"] > 0, f"Invalid cooldown: {rule['rule_id']}"

    def test_cooldown_matches_severity(self):
        """SPEC-1831: critical=5, warning=15, info=60."""
        expected_cooldown = {"critical": 5, "warning": 15, "info": 60}
        for rule in DEFAULT_ALERT_RULES:
            expected = expected_cooldown[rule["severity"]]
            assert rule["cooldown_minutes"] == expected, (
                f"Rule '{rule['rule_id']}': expected cooldown {expected} "
                f"for severity '{rule['severity']}', got {rule['cooldown_minutes']}"
            )

    def test_every_rule_has_condition(self):
        """Every rule has a condition with metric and operator."""
        for rule in DEFAULT_ALERT_RULES:
            assert "condition" in rule, f"Missing condition: {rule['rule_id']}"
            cond = rule["condition"]
            assert "metric" in cond, f"Missing metric: {rule['rule_id']}"
            assert "operator" in cond, f"Missing operator: {rule['rule_id']}"
            assert "value" in cond, f"Missing value: {rule['rule_id']}"

    def test_every_rule_enabled_by_default(self):
        """Default rules are enabled out of the box."""
        for rule in DEFAULT_ALERT_RULES:
            assert rule.get("enabled") is True, f"Rule disabled: {rule['rule_id']}"

    def test_get_default_alert_rules_returns_copy(self):
        """get_default_alert_rules() returns a copy, not the original."""
        result = get_default_alert_rules()
        assert result == DEFAULT_ALERT_RULES
        assert result is not DEFAULT_ALERT_RULES


# ---------------------------------------------------------------------------
# Seed function
# ---------------------------------------------------------------------------


class TestSeedDefaultAlertRules:
    """Verify the startup seeding behavior."""

    @pytest.mark.asyncio
    async def test_seeds_when_no_rules_exist(self):
        """seed_default_alert_rules() creates document when none exists."""
        mock_repo = AsyncMock()
        mock_repo.get_config = AsyncMock(return_value=None)
        mock_repo.set_config = AsyncMock()

        mock_repo_cls = MagicMock(return_value=mock_repo)
        with patch(
            "src.multi_tenant.repositories.platform.PlatformConfigRepository",
            mock_repo_cls,
        ):
            count = await seed_default_alert_rules()

        assert count == 8
        mock_repo.set_config.assert_called_once()
        doc = mock_repo.set_config.call_args[0][0]
        assert doc.config_type == ALERT_RULES_CONFIG_TYPE
        assert doc.config_key == "all_rules"
        assert len(doc.value) == 8

    @pytest.mark.asyncio
    async def test_skips_when_rules_exist(self):
        """seed_default_alert_rules() returns 0 when rules already exist."""
        mock_repo = AsyncMock()
        mock_repo.get_config = AsyncMock(return_value={"value": {"some": "rules"}})
        mock_repo.set_config = AsyncMock()

        mock_repo_cls = MagicMock(return_value=mock_repo)
        with patch(
            "src.multi_tenant.repositories.platform.PlatformConfigRepository",
            mock_repo_cls,
        ):
            count = await seed_default_alert_rules()

        assert count == 0
        mock_repo.set_config.assert_not_called()

    @pytest.mark.asyncio
    async def test_seed_stores_rules_keyed_by_id(self):
        """Seeded document stores rules as {rule_id: rule_dict}."""
        mock_repo = AsyncMock()
        mock_repo.get_config = AsyncMock(return_value=None)
        mock_repo.set_config = AsyncMock()

        mock_repo_cls = MagicMock(return_value=mock_repo)
        with patch(
            "src.multi_tenant.repositories.platform.PlatformConfigRepository",
            mock_repo_cls,
        ):
            await seed_default_alert_rules()

        doc = mock_repo.set_config.call_args[0][0]
        assert "circuit_breaker_open" in doc.value
        assert "scaling_ceiling" in doc.value
        assert doc.value["circuit_breaker_open"]["severity"] == "critical"

    @pytest.mark.asyncio
    async def test_seed_tolerates_cosmos_failure(self):
        """seed_default_alert_rules() returns 0 on Cosmos write failure."""
        mock_repo = AsyncMock()
        mock_repo.get_config = AsyncMock(return_value=None)
        mock_repo.set_config = AsyncMock(side_effect=RuntimeError("Cosmos 503"))

        mock_repo_cls = MagicMock(return_value=mock_repo)
        with patch(
            "src.multi_tenant.repositories.platform.PlatformConfigRepository",
            mock_repo_cls,
        ):
            count = await seed_default_alert_rules()

        assert count == 0

    def test_config_type_constant(self):
        """Config type is 'alert_rules'."""
        assert ALERT_RULES_CONFIG_TYPE == "alert_rules"
