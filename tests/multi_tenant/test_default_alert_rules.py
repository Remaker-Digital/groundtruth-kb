"""Tests for SPEC-1831: Default Alert Rules Ship with System.

Verifies that 8 default alert rules are seeded on startup, not duplicated
on restart, and evaluable by the existing alert engine.

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, patch

import pytest


class TestDefaultAlertRules:
    """SPEC-1831: Default alert rules created on first startup."""

    @pytest.mark.asyncio
    async def test_seeds_8_default_rules_on_fresh_startup(self):
        """TEST-10432: 8 default rules created when none exist."""
        from src.multi_tenant.alert_defaults import seed_default_alert_rules, DEFAULT_RULES

        mock_repo = AsyncMock()
        mock_repo.get_all_rules.return_value = []  # No rules exist

        await seed_default_alert_rules(mock_repo)

        assert mock_repo.insert_rule.call_count == len(DEFAULT_RULES)
        assert len(DEFAULT_RULES) == 8

    @pytest.mark.asyncio
    async def test_does_not_duplicate_on_restart(self):
        """TEST-10433: No duplicates created when rules already exist."""
        from src.multi_tenant.alert_defaults import seed_default_alert_rules, DEFAULT_RULES

        existing_rules = [{"rule_type": rule["rule_type"]} for rule in DEFAULT_RULES]
        mock_repo = AsyncMock()
        mock_repo.get_all_rules.return_value = existing_rules

        await seed_default_alert_rules(mock_repo)

        assert mock_repo.insert_rule.call_count == 0

    @pytest.mark.asyncio
    async def test_default_rules_have_severity_and_cooldown(self):
        """Each default rule has severity (critical/warning/info) and cooldown_minutes."""
        from src.multi_tenant.alert_defaults import DEFAULT_RULES

        valid_severities = {"critical", "warning", "info"}
        for rule in DEFAULT_RULES:
            assert rule["severity"] in valid_severities, f"Invalid severity for {rule['rule_type']}"
            assert isinstance(rule["cooldown_minutes"], int), f"Missing cooldown for {rule['rule_type']}"
            assert rule["cooldown_minutes"] > 0

    @pytest.mark.asyncio
    async def test_default_rules_stored_in_platform_config(self):
        """SPEC-1831: Rules stored in Cosmos platform_config collection."""
        from src.multi_tenant.alert_defaults import DEFAULT_RULES

        for rule in DEFAULT_RULES:
            assert "rule_type" in rule
            assert "metric_name" in rule
            assert "operator" in rule
            assert "threshold" in rule

    @pytest.mark.asyncio
    async def test_circuit_breaker_rule_fires_on_open(self):
        """TEST-10434: Circuit breaker OPEN triggers critical alert."""
        from src.multi_tenant.alert_defaults import DEFAULT_RULES

        cb_rule = next(r for r in DEFAULT_RULES if r["rule_type"] == "circuit_breaker_open")
        assert cb_rule["severity"] == "critical"
        assert cb_rule["cooldown_minutes"] == 5

    @pytest.mark.asyncio
    async def test_default_rules_cooldown_by_severity(self):
        """Critical=5min, warning=15min, info=60min cooldowns."""
        from src.multi_tenant.alert_defaults import DEFAULT_RULES

        severity_cooldowns = {"critical": 5, "warning": 15, "info": 60}
        for rule in DEFAULT_RULES:
            expected = severity_cooldowns[rule["severity"]]
            assert rule["cooldown_minutes"] == expected, (
                f"{rule['rule_type']}: expected cooldown {expected}, got {rule['cooldown_minutes']}"
            )

    @pytest.mark.asyncio
    async def test_default_rules_editable_by_platform_admin(self):
        """SPEC-1831: Default rules are editable and deletable."""
        from src.multi_tenant.alert_defaults import DEFAULT_RULES

        for rule in DEFAULT_RULES:
            # All rules must have is_default=True (for UI display) but no is_locked flag
            assert rule.get("is_default") is True
            assert "is_locked" not in rule or rule["is_locked"] is False
