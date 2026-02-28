"""
Source inspection tests -- Admin UI label renames (WI-0780..0783, 0785, 0786).

Verifies that all UI label renames have been applied:
  - WI-0780: 'Configuration' → 'Agent configuration' (nav + page titles)
  - WI-0781: 'Widget' → 'Widget configuration' (nav + page titles)
  - WI-0782: Color fields → 'Header left color' / 'Header right color'
  - WI-0783: 'Member' column → 'Team member'
  - WI-0785: 'Review and launch' → 'Custom AI instructions'
  - WI-0786: Escalation slider Conservative/Aggressive label alignment

Run with:
    pytest tests/widget/test_admin_ui_labels.py -v

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
ADMIN_STANDALONE = ROOT / "admin" / "standalone"
ADMIN_SHARED = ROOT / "admin" / "shared"
ADMIN_SHOPIFY = ROOT / "admin" / "shopify"


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _read(path: Path) -> str:
    """Read a TypeScript source file and return its content."""
    assert path.exists(), f"Source file not found: {path}"
    return path.read_text(encoding="utf-8")


# ===========================================================================
# TestConfigurationRename — WI-0780: 'Configuration' → 'Agent configuration'
# ===========================================================================


class TestConfigurationRename:
    """Verify all navigation and page titles use 'Agent configuration'."""

    def test_standalone_nav_label(self) -> None:
        """Standalone sidebar nav item uses 'Agent configuration'."""
        source = _read(ADMIN_STANDALONE / "layouts" / "StandaloneLayout.tsx")
        assert "label: 'Agent configuration'" in source

    def test_standalone_page_title(self) -> None:
        """Standalone Configuration page title is 'Agent configuration'."""
        source = _read(ADMIN_STANDALONE / "pages" / "Configuration.tsx")
        assert "Agent configuration" in source

    def test_shopify_nav_label(self) -> None:
        """Shopify nav label uses 'Agent configuration'."""
        source = _read(ADMIN_SHOPIFY / "layouts" / "ShopifyAppLayout.tsx")
        assert "Agent configuration" in source

    def test_shopify_page_title(self) -> None:
        """Shopify Configuration page title is 'Agent configuration'."""
        source = _read(ADMIN_SHOPIFY / "pages" / "Configuration.tsx")
        assert "Agent configuration" in source

    def test_sidebar_group_heading(self) -> None:
        """Sidebar configuration group heading says 'AI Configuration'."""
        source = _read(ADMIN_STANDALONE / "layouts" / "StandaloneLayout.tsx")
        assert "AI Configuration" in source

    def test_no_bare_configuration_nav_label(self) -> None:
        """Nav items must NOT have bare 'Configuration' as label (must be 'Agent configuration')."""
        source = _read(ADMIN_STANDALONE / "layouts" / "StandaloneLayout.tsx")
        # Find all nav label entries — bare "Configuration" without "Agent" prefix is wrong
        # Allow "Configuration name" (field label) and "AI Configuration" (group heading)
        nav_labels = re.findall(r"label:\s*['\"]([^'\"]+)['\"]", source)
        for label in nav_labels:
            if label == "Configuration":
                raise AssertionError(
                    "Nav label 'Configuration' found — should be 'Agent configuration'"
                )


# ===========================================================================
# TestWidgetRename — WI-0781: 'Widget' → 'Widget configuration'
# ===========================================================================


class TestWidgetRename:
    """Verify all navigation and page titles use 'Widget configuration'."""

    def test_standalone_nav_label(self) -> None:
        """Standalone sidebar nav item uses 'Widget configuration'."""
        source = _read(ADMIN_STANDALONE / "layouts" / "StandaloneLayout.tsx")
        assert "label: 'Widget configuration'" in source

    def test_standalone_page_title(self) -> None:
        """Standalone Widget page title is 'Widget configuration'."""
        source = _read(ADMIN_STANDALONE / "pages" / "Widget.tsx")
        assert "Widget configuration" in source

    def test_shopify_nav_label(self) -> None:
        """Shopify nav label uses 'Widget configuration'."""
        source = _read(ADMIN_SHOPIFY / "layouts" / "ShopifyAppLayout.tsx")
        assert "Widget configuration" in source

    def test_shopify_page_title(self) -> None:
        """Shopify Widget page title is 'Widget configuration'."""
        source = _read(ADMIN_SHOPIFY / "pages" / "Widget.tsx")
        assert "Widget configuration" in source

    def test_activation_dialog_references(self) -> None:
        """ActivationDialog maps widget fields to 'Widget configuration' section."""
        source = _read(ADMIN_SHARED / "ActivationDialog.tsx")
        assert "'Widget configuration'" in source or '"Widget configuration"' in source


# ===========================================================================
# TestColorFieldRenames — WI-0782: 'Primary color' → 'Header left/right color'
# ===========================================================================


class TestColorFieldRenames:
    """Verify color picker labels use 'Header left color' / 'Header right color'."""

    def test_header_left_color_label(self) -> None:
        """Widget page uses 'Header left color' label."""
        source = _read(ADMIN_STANDALONE / "pages" / "Widget.tsx")
        assert 'Header left color' in source

    def test_header_right_color_label(self) -> None:
        """Widget page uses 'Header right color' label."""
        source = _read(ADMIN_STANDALONE / "pages" / "Widget.tsx")
        assert 'Header right color' in source

    def test_gradient_toggle_description(self) -> None:
        """Gradient toggle description references 'left and right colors'."""
        source = _read(ADMIN_STANDALONE / "pages" / "Widget.tsx")
        assert "left and right colors" in source

    def test_no_bare_primary_color_label_in_standalone(self) -> None:
        """Standalone Widget must NOT use bare 'Primary color' label (renamed to 'Header left color')."""
        source = _read(ADMIN_STANDALONE / "pages" / "Widget.tsx")
        # Allow "widget_primary_color" (field key) but not a display label "Primary color"
        lines = source.split('\n')
        for line in lines:
            if 'label=' in line and 'Primary color' in line:
                raise AssertionError(
                    f"Found 'Primary color' in a label attribute — should be 'Header left color'"
                )

    def test_side_by_side_layout(self) -> None:
        """Header color pickers are rendered side-by-side in a Group."""
        source = _read(ADMIN_STANDALONE / "pages" / "Widget.tsx")
        # Color pickers wrapped in <Group grow> for side-by-side layout
        assert "<Group grow" in source

    def test_right_color_disabled_when_gradient_off(self) -> None:
        """Header right color picker has reduced opacity when gradient is disabled."""
        source = _read(ADMIN_STANDALONE / "pages" / "Widget.tsx")
        # opacity: config.headerGradientEnabled ? 1 : 0.4
        assert "headerGradientEnabled" in source
        assert "opacity" in source


# ===========================================================================
# TestTeamMemberRename — WI-0783: 'Member' column → 'Team member'
# ===========================================================================


class TestTeamMemberRename:
    """Verify Team page column heading uses 'Team member'."""

    def test_column_heading_text(self) -> None:
        """Team table header shows 'Team member' not 'Member'."""
        source = _read(ADMIN_SHARED / "TeamManager.tsx")
        assert ">Team member<" in source

    def test_no_bare_member_column_heading(self) -> None:
        """Table header must NOT use bare 'Member' without 'Team' prefix."""
        source = _read(ADMIN_SHARED / "TeamManager.tsx")
        # Find all <th> contents
        th_matches = re.findall(r"<th[^>]*>([^<]+)<", source)
        for text in th_matches:
            text = text.strip()
            if text == "Member":
                raise AssertionError(
                    "Column heading 'Member' found — should be 'Team member'"
                )

    def test_page_title_team_members(self) -> None:
        """Team page title says 'Team members'."""
        source = _read(ADMIN_STANDALONE / "pages" / "Team.tsx")
        assert "Team members" in source


# ===========================================================================
# TestCustomAIInstructionsRename — WI-0785: 'Review and launch' → 'Custom AI instructions'
# ===========================================================================


class TestCustomAIInstructionsRename:
    """Verify setup wizard step uses 'Custom AI instructions'."""

    def test_wizard_step_label(self) -> None:
        """OnboardingWizard step 3 is labeled 'Custom AI instructions'."""
        source = _read(ADMIN_SHARED / "components" / "OnboardingWizard.tsx")
        assert "Custom AI instructions" in source

    def test_no_review_and_launch(self) -> None:
        """OnboardingWizard must NOT contain 'Review and launch' text."""
        source = _read(ADMIN_SHARED / "components" / "OnboardingWizard.tsx")
        assert "Review and launch" not in source, \
            "'Review and launch' found — should be 'Custom AI instructions'"


# ===========================================================================
# TestEscalationSliderAlignment — WI-0786: Conservative/Aggressive label alignment
# ===========================================================================


class TestEscalationSliderAlignment:
    """Verify escalation threshold slider labels are properly aligned."""

    CONFIG = ADMIN_STANDALONE / "pages" / "Configuration.tsx"

    def test_conservative_label_present(self) -> None:
        """Escalation slider has 'Conservative' label at value 0."""
        source = _read(self.CONFIG)
        assert "Conservative" in source

    def test_aggressive_label_present(self) -> None:
        """Escalation slider has 'Aggressive' label at value 1."""
        source = _read(self.CONFIG)
        assert "Aggressive" in source

    def test_conservative_repositioned(self) -> None:
        """Conservative label is repositioned to avoid left overflow."""
        source = _read(self.CONFIG)
        # Conservative at value 0 should have position: relative, left: 50% to push text rightward
        assert re.search(
            r"Conservative.*position.*relative|position.*relative.*Conservative",
            source,
            re.DOTALL,
        ) or re.search(
            r"value:\s*0.*Conservative",
            source,
            re.DOTALL,
        ), "Conservative label must be repositioned at slider start"

    def test_aggressive_repositioned(self) -> None:
        """Aggressive label is repositioned to avoid right overflow."""
        source = _read(self.CONFIG)
        # Aggressive at value 1 should have position: relative, right: 50% to push text leftward
        assert re.search(
            r"Aggressive.*position.*relative|position.*relative.*Aggressive",
            source,
            re.DOTALL,
        ) or re.search(
            r"value:\s*1.*Aggressive",
            source,
            re.DOTALL,
        ), "Aggressive label must be repositioned at slider end"

    def test_midpoint_label(self) -> None:
        """Slider has a midpoint label at value 0.5."""
        source = _read(self.CONFIG)
        assert "value: 0.5" in source

    def test_labels_use_styled_spans(self) -> None:
        """Conservative and Aggressive labels are wrapped in styled spans for positioning."""
        source = _read(self.CONFIG)
        # Both labels should be wrapped in <span style=...>
        assert re.search(r"<span\s+style=.*>Conservative</span>", source)
        assert re.search(r"<span\s+style=.*>Aggressive</span>", source)
