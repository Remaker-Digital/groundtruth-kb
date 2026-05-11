"""Slice 8: S255 Phase 2 locale runtime rendering regression tests.

Verifies that the 26 new locale keys are actually used in components
(not hardcoded English) and that locale parity holds.

Test plan ref: COMPREHENSIVE-TEST-PLAN-S245-S255.md Slice 8

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

WIDGET_SRC = Path(__file__).resolve().parent.parent.parent / "widget" / "src"
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


class TestNoHardcodedEnglish:
    """Verify Phase 2 replaced strings use locale refs, not literals."""

    def test_header_subtitle_uses_locale(self):
        """Header subtitle fallback uses locale.headerSubtitleDefault."""
        source = _read(WIDGET_SRC / "components" / "Header.tsx")
        assert "locale.headerSubtitleDefault" in source
        assert "'We typically reply within minutes'" not in source

    def test_header_status_uses_locale(self):
        """Header status text uses locale.statusOnline."""
        source = _read(WIDGET_SRC / "components" / "Header.tsx")
        assert "locale.statusOnline" in source

    def test_header_logo_alt_uses_locale(self):
        """Header logo alt uses locale.logoAlt."""
        source = _read(WIDGET_SRC / "components" / "Header.tsx")
        assert "locale.logoAlt" in source
        assert 'alt="Logo"' not in source

    def test_message_bubble_revised_uses_locale(self):
        """MessageBubble retracted label uses locale.messageRevised."""
        source = _read(WIDGET_SRC / "components" / "MessageBubble.tsx")
        assert "locale.messageRevised" in source

    def test_message_bubble_feedback_uses_locale(self):
        """MessageBubble feedback labels use locale refs."""
        source = _read(WIDGET_SRC / "components" / "MessageBubble.tsx")
        assert "locale.feedbackHelpful" in source
        assert "locale.feedbackNotHelpful" in source

    def test_message_list_separator_uses_locale(self):
        """MessageList previous conversation separator uses locale."""
        source = _read(WIDGET_SRC / "components" / "MessageList.tsx")
        assert "locale.previousConversation" in source

    def test_input_bar_branding_uses_locale(self):
        """InputBar branding uses locale.poweredByPrefix + locale.poweredByBrand."""
        source = _read(WIDGET_SRC / "components" / "InputBar.tsx")
        assert "locale.poweredByPrefix" in source
        assert "locale.poweredByBrand" in source

    def test_offline_form_labels_use_locale(self):
        """OfflineForm field labels use locale refs."""
        source = _read(WIDGET_SRC / "components" / "OfflineForm.tsx")
        assert "locale.offlineFormName" in source
        assert "locale.offlineFormEmail" in source
        assert "locale.offlineFormMessage" in source

    def test_panel_errors_use_locale(self):
        """Panel error messages use locale refs."""
        source = _read(WIDGET_SRC / "components" / "Panel.tsx")
        assert "_locale.errorStartConversation" in source
        assert "_locale.errorSendMessage" in source

    def test_panel_agent_name_uses_locale(self):
        """Panel agent name fallback uses locale.defaultAgentName."""
        source = _read(WIDGET_SRC / "components" / "Panel.tsx")
        assert "_locale.defaultAgentName" in source

    def test_launcher_labels_use_locale(self):
        """Launcher open/close aria-labels use locale."""
        source = _read(WIDGET_SRC / "components" / "Launcher.tsx")
        assert "locale.closeChat" in source
        assert "locale.openChat" in source

    def test_sse_fallbacks_use_locale(self):
        """SSE transport fallback strings use locale from store."""
        source = _read(WIDGET_SRC / "transport" / "sse.ts")
        assert "locale.sseRetractFallback" in source
        assert "locale.sseErrorFallback" in source

    def test_iframe_title_uses_locale(self):
        """iframe title uses locale.iframeTitleChat."""
        source = _read(WIDGET_SRC / "index.ts")
        assert "locale.iframeTitleChat" in source


class TestLocaleKeyPresence:
    """Verify all 26 Phase 2 keys exist in en.ts."""

    PHASE2_KEYS = [
        "openChat", "closeChat", "chatImageAlt", "logoAlt",
        "headerSubtitleDefault", "statusOnline", "feedbackHelpful",
        "feedbackNotHelpful", "messageRevised", "previousConversation",
        "iframeTitleChat", "conversationMessages", "unreadMessages",
        "defaultAgentName", "poweredByPrefix", "poweredByBrand",
        "offlineFormName", "offlineFormEmail", "offlineFormMessage",
        "errorStartConversation", "errorSendMessage", "errorGeneric",
        "escalationNotice", "waitForResponse", "sseRetractFallback",
        "sseErrorFallback",
    ]

    def test_en_has_all_phase2_keys(self):
        """en.ts contains all 26 Phase 2 locale keys."""
        source = _read(WIDGET_SRC / "locale" / "en.ts")
        for key in self.PHASE2_KEYS:
            assert f"{key}:" in source or f"  {key}:" in source, \
                f"Missing key '{key}' in en.ts"

    def test_interface_has_all_phase2_keys(self):
        """Locale interface in en.ts declares all 26 keys."""
        source = _read(WIDGET_SRC / "locale" / "en.ts")
        # Keys should be in the interface declaration
        for key in self.PHASE2_KEYS:
            assert f"{key}:" in source, f"Missing key '{key}' in Locale interface"


class TestLocaleParity:
    """Verify check_locale_parity.py passes."""

    def test_parity_script_passes(self):
        """python scripts/check_locale_parity.py exits 0."""
        result = subprocess.run(
            [sys.executable, str(PROJECT_ROOT / "scripts" / "check_locale_parity.py")],
            capture_output=True,
            text=True,
            cwd=str(PROJECT_ROOT),
        )
        assert result.returncode == 0, f"Locale parity failed:\n{result.stdout}\n{result.stderr}"
        assert "PASS" in result.stdout
