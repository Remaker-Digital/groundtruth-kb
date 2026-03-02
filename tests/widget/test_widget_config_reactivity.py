"""Tests for SPEC-1612: Widget Panel uses reactive store config for appearance (WI-0934).

Verifies that Panel.tsx resolves design tokens and derived state from the
store's config (updated by setConfigPartial) rather than the stale initial
config prop, so that draft-mode and post-activation changes take effect
without requiring a full page reload.

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

from __future__ import annotations

import re
from pathlib import Path

import pytest

PANEL_PATH = Path("widget/src/components/Panel.tsx")


@pytest.fixture
def panel_source() -> str:
    """Read Panel.tsx source once per test class."""
    return PANEL_PATH.read_text(encoding="utf-8")


class TestWidgetConfigReactivity:
    """Source inspection tests for SPEC-1612 config reactivity fix."""

    def test_panel_uses_store_config_with_prop_fallback(self, panel_source: str):
        """Panel.tsx resolves activeConfig from state.config with prop fallback."""
        assert "state.config || config" in panel_source, (
            "Panel must resolve activeConfig = state.config || config "
            "so that setConfigPartial() updates take effect (SPEC-1612)"
        )

    def test_panel_resolve_tokens_uses_active_config(self, panel_source: str):
        """Panel.tsx calls resolveTokens(activeConfig) not resolveTokens(config)."""
        assert "resolveTokens(activeConfig)" in panel_source, (
            "resolveTokens must use activeConfig (store value), "
            "not the stale config prop (SPEC-1612)"
        )
        # Ensure the OLD stale pattern is gone
        # Match resolveTokens(config) but NOT resolveTokens(activeConfig)
        stale_pattern = re.findall(r"resolveTokens\(config\)", panel_source)
        assert len(stale_pattern) == 0, (
            f"Found {len(stale_pattern)} stale resolveTokens(config) call(s) — "
            "must use resolveTokens(activeConfig) instead"
        )

    def test_no_stale_config_widget_references(self, panel_source: str):
        """No config.widget_ references in Panel.tsx (all must be activeConfig)."""
        # Find config.widget_ but NOT activeConfig.widget_ or state.config
        stale_refs = re.findall(r"(?<!active)config\.widget_", panel_source)
        assert len(stale_refs) == 0, (
            f"Found {len(stale_refs)} stale config.widget_* reference(s) in Panel.tsx. "
            "All must use activeConfig.widget_* for reactive preview (SPEC-1612)"
        )

    def test_derived_state_uses_active_config(self, panel_source: str):
        """Agent name, title, avatar, gradient, branding all derive from activeConfig."""
        derived_fields = [
            "activeConfig.widget_agent_display_name",
            "activeConfig.widget_agent_title",
            "activeConfig.widget_agent_avatar_url",
            "activeConfig.widget_logo_url",
            "activeConfig.widget_greeting_message",
            "activeConfig.widget_show_branding",
            "activeConfig.widget_file_upload_enabled",
            "activeConfig.widget_quick_actions",
            "activeConfig.widget_header_text",
            "activeConfig.widget_header_subtitle",
            "activeConfig.widget_header_gradient_enabled",
            "activeConfig.widget_header_gradient_end",
        ]
        missing = [f for f in derived_fields if f not in panel_source]
        assert len(missing) == 0, (
            f"Panel.tsx missing activeConfig references for: {missing}. "
            "All derived state must use activeConfig for reactive preview."
        )

    def test_active_config_comment_documents_pattern(self, panel_source: str):
        """The WI-0934 comment explains the activeConfig pattern."""
        assert "WI-0934" in panel_source, (
            "Panel.tsx should reference WI-0934 in a comment explaining "
            "the activeConfig pattern"
        )
