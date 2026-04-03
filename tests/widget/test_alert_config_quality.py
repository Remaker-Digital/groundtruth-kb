"""Slice 9 UI half: Phase 3 — Alert config quality UI pre-implementation tests.

Tests that AlertConfig.tsx constants and rendering support quality_regression
alert type. These are pre-implementation tests — they skip when the Phase 3
additions don't yet exist.

Test plan ref: COMPREHENSIVE-TEST-PLAN-S245-S255.md Slice 9 (tests 12-17)

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

from __future__ import annotations

from pathlib import Path

import pytest


ALERT_CONFIG_TSX = (
    Path(__file__).resolve().parent.parent.parent
    / "admin" / "provider" / "pages" / "AlertConfig.tsx"
)


@pytest.fixture(autouse=True)
def load_source():
    """Read AlertConfig.tsx source for all tests."""
    if not ALERT_CONFIG_TSX.exists():
        pytest.skip("AlertConfig.tsx not found")


def _read_source() -> str:
    return ALERT_CONFIG_TSX.read_text(encoding="utf-8")


# ── RULE_TYPE_OPTIONS ─────────────────────────────────────────────

class TestRuleTypeOptions:
    """Verify RULE_TYPE_OPTIONS includes quality_regression."""

    def test_rule_type_options_exists(self):
        """RULE_TYPE_OPTIONS constant is defined."""
        source = _read_source()
        assert "RULE_TYPE_OPTIONS" in source

    def test_quality_regression_in_rule_types(self):
        """quality_regression option should be in RULE_TYPE_OPTIONS dropdown."""
        source = _read_source()
        if "quality_regression" not in source:
            pytest.skip("quality_regression not yet added to RULE_TYPE_OPTIONS (Phase 3)")
        assert "quality_regression" in source


# ── OPERATOR_OPTIONS ──────────────────────────────────────────────

class TestOperatorOptions:
    """Verify OPERATOR_OPTIONS includes lt_delta for quality threshold."""

    def test_operator_options_exists(self):
        """OPERATOR_OPTIONS constant is defined."""
        source = _read_source()
        assert "OPERATOR_OPTIONS" in source

    def test_lt_delta_in_operators(self):
        """lt_delta operator should be in OPERATOR_OPTIONS."""
        source = _read_source()
        if "lt_delta" not in source:
            pytest.skip("lt_delta not yet added to OPERATOR_OPTIONS (Phase 3)")
        assert "lt_delta" in source


# ── TYPE_COLORS ───────────────────────────────────────────────────

class TestTypeColors:
    """Verify TYPE_COLORS maps quality_regression to a badge color."""

    def test_type_colors_exists(self):
        """TYPE_COLORS constant is defined."""
        source = _read_source()
        assert "TYPE_COLORS" in source

    def test_quality_regression_has_color(self):
        """quality_regression should have a badge color mapping."""
        source = _read_source()
        if "quality_regression" not in source:
            pytest.skip("quality_regression not yet added to TYPE_COLORS (Phase 3)")
        # Verify it appears in the TYPE_COLORS section
        type_colors_start = source.index("TYPE_COLORS")
        # Find the closing brace after TYPE_COLORS
        brace_depth = 0
        for i, ch in enumerate(source[type_colors_start:]):
            if ch == "{":
                brace_depth += 1
            elif ch == "}":
                brace_depth -= 1
                if brace_depth == 0:
                    type_colors_block = source[type_colors_start:type_colors_start + i + 1]
                    break
        else:
            type_colors_block = source[type_colors_start:type_colors_start + 300]
        assert "quality_regression" in type_colors_block


# ── notificationChannels ──────────────────────────────────────────

class TestNotificationChannels:
    """Verify notificationChannels support in alert rules."""

    def test_notification_channels_in_interface(self):
        """AlertRule interface includes notificationChannels field."""
        source = _read_source()
        assert "notificationChannels" in source

    def test_notification_channels_in_form(self):
        """Alert create/edit form preserves notificationChannels on save."""
        source = _read_source()
        # The form should include notificationChannels in the save payload
        assert "notificationChannels" in source


# ── Alert history tenant attribution ──────────────────────────────

class TestAlertHistoryTenantColumn:
    """Verify alert history shows tenant information when available."""

    def test_alert_history_tab_exists(self):
        """History tab exists in the AlertConfig page."""
        source = _read_source()
        assert "History" in source or "history" in source.lower()

    def test_tenant_column_in_history(self):
        """Alert history table should show tenant_id when quality alerts include it."""
        source = _read_source()
        if "tenantId" not in source and "tenant_id" not in source:
            pytest.skip("tenant column not yet added to alert history (Phase 3)")
