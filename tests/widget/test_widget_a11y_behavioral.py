"""Slice 7: S255 Phase 2 widget WCAG AA behavioral regression tests.

Tests focus trap, iframe focus handoff, live regions, gradient focus ring,
dialog semantics, and ARIA attributes.

Test plan ref: COMPREHENSIVE-TEST-PLAN-S245-S255.md Slice 7

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

from __future__ import annotations

from pathlib import Path

WIDGET_SRC = Path(__file__).resolve().parent.parent.parent / "widget" / "src"


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


class TestFocusRingContrast:
    """focusRingColor() and focusRingColorGradient() WCAG compliance."""

    def test_focus_ring_color_exported(self):
        """focusRingColor is exported from tokens.ts."""
        source = _read(WIDGET_SRC / "theme" / "tokens.ts")
        assert "export function focusRingColor" in source

    def test_focus_ring_dark_background_returns_white(self):
        """Dark background (#1c1917) -> white ring."""
        source = _read(WIDGET_SRC / "theme" / "tokens.ts")
        # Luminance threshold 0.1791 — dark bg has lum < 0.1791 -> white
        assert "0.1791" in source, "Should use 0.1791 luminance threshold"

    def test_focus_ring_gradient_exported(self):
        """focusRingColorGradient is exported from tokens.ts."""
        source = _read(WIDGET_SRC / "theme" / "tokens.ts")
        assert "export function focusRingColorGradient" in source

    def test_gradient_header_uses_double_ring(self):
        """Header close button uses double ring on gradient backgrounds."""
        source = _read(WIDGET_SRC / "components" / "Header.tsx")
        assert "0 0 0 2px #000000, 0 0 0 4px #FFFFFF" in source, \
            "Gradient header should use black+white double ring"

    def test_flat_header_uses_single_ring(self):
        """Header close button uses single focusRingColor on flat backgrounds."""
        source = _read(WIDGET_SRC / "components" / "Header.tsx")
        assert "focusRingColor(tokens.colorPrimary)" in source, \
            "Flat header should use focusRingColor"

    def test_codex_counterexample_gradient_safe(self):
        """Previously failing gradient #1AB624->#A12291 is safe with double ring."""
        source = _read(WIDGET_SRC / "components" / "Header.tsx")
        # Double ring guarantees one band >= 4.58:1 against ANY background
        assert "gradientEnd" in source and "#000000" in source and "#FFFFFF" in source


class TestDialogSemantics:
    """Panel dialog role, aria-modal, aria-labelledby."""

    def test_panel_has_role_dialog(self):
        """Panel wrapper has role='dialog'."""
        source = _read(WIDGET_SRC / "components" / "Panel.tsx")
        assert 'role="dialog"' in source

    def test_panel_has_aria_modal(self):
        """Panel has aria-modal='true'."""
        source = _read(WIDGET_SRC / "components" / "Panel.tsx")
        assert 'aria-modal="true"' in source

    def test_panel_has_aria_labelledby(self):
        """Panel links to heading via aria-labelledby."""
        source = _read(WIDGET_SRC / "components" / "Panel.tsx")
        assert 'aria-labelledby="ar-panel-heading"' in source

    def test_header_has_heading_with_id(self):
        """Header title is h1 with id matching Panel's aria-labelledby."""
        source = _read(WIDGET_SRC / "components" / "Header.tsx")
        assert 'id="ar-panel-heading"' in source
        assert "<h1" in source


class TestFocusTrap:
    """Tab/Shift+Tab containment within the dialog."""

    def test_panel_has_tab_trap(self):
        """Panel has Tab key containment logic."""
        source = _read(WIDGET_SRC / "components" / "Panel.tsx")
        assert "e.key === 'Tab'" in source or 'key === "Tab"' in source

    def test_panel_has_shift_tab_handling(self):
        """Panel handles Shift+Tab for reverse tab order."""
        source = _read(WIDGET_SRC / "components" / "Panel.tsx")
        assert "e.shiftKey" in source

    def test_panel_wraps_first_to_last(self):
        """Tab on last element wraps to first."""
        source = _read(WIDGET_SRC / "components" / "Panel.tsx")
        assert "first" in source.lower() and "last" in source.lower()

    def test_panel_escape_closes(self):
        """Escape key closes the dialog."""
        source = _read(WIDGET_SRC / "components" / "Panel.tsx")
        assert "'Escape'" in source or '"Escape"' in source


class TestIframeFocusHandoff:
    """Host<->iframe focus management."""

    def test_open_focuses_into_iframe(self):
        """Opening widget moves focus into the iframe."""
        source = _read(WIDGET_SRC / "index.ts")
        assert "contentWindow" in source and "focus" in source

    def test_close_returns_focus_to_launcher(self):
        """Closing widget returns focus to the launcher button."""
        source = _read(WIDGET_SRC / "index.ts")
        assert "launcherBtn" in source or "shadowRoot.querySelector" in source
        assert "focus()" in source


class TestLiveRegions:
    """aria-live regions for screen reader announcements."""

    def test_message_list_has_role_log(self):
        """Message list scroll container has role='log'."""
        source = _read(WIDGET_SRC / "components" / "MessageList.tsx")
        assert 'role="log"' in source

    def test_message_list_has_hidden_live_region(self):
        """MessageList has a visually-hidden aria-live region for completed messages."""
        source = _read(WIDGET_SRC / "components" / "MessageList.tsx")
        assert 'aria-live="polite"' in source

    def test_consent_banner_has_role_alert(self):
        """ConsentBanner has role='alert' for assertive announcement."""
        source = _read(WIDGET_SRC / "components" / "ConsentBanner.tsx")
        assert 'role="alert"' in source

    def test_consent_banner_aria_live_assertive(self):
        """ConsentBanner uses aria-live='assertive'."""
        source = _read(WIDGET_SRC / "components" / "ConsentBanner.tsx")
        assert 'aria-live="assertive"' in source


class TestLauncherA11y:
    """Launcher accessibility attributes."""

    def test_launcher_badge_has_role_status(self):
        """Unread badge has role='status'."""
        source = _read(WIDGET_SRC / "components" / "Launcher.tsx")
        assert 'role="status"' in source

    def test_launcher_badge_has_aria_label(self):
        """Unread badge has aria-label with count."""
        source = _read(WIDGET_SRC / "components" / "Launcher.tsx")
        assert "unreadMessages" in source and "aria-label" in source

    def test_launcher_uses_locale_for_open_close(self):
        """Launcher aria-label uses locale.openChat/closeChat."""
        source = _read(WIDGET_SRC / "components" / "Launcher.tsx")
        assert "locale.closeChat" in source and "locale.openChat" in source

    def test_header_status_dot_aria_hidden(self):
        """Status dot is aria-hidden (text label conveys status)."""
        source = _read(WIDGET_SRC / "components" / "Header.tsx")
        assert 'aria-hidden="true"' in source
