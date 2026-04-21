"""D5 I1 evidence: ConsentBanner renders before MessageList in Panel.tsx.

This test discharges Codex review F2 from
``bridge/agent-red-claude-design-gui-refresh-intake-implementation-002.md``:
the ``GOV-CD-PRESERVATION`` I1 invariant cites this exact file, so the path
must exist and produce a PASS/FAIL.

The check is a lightweight static source read — same pattern as
``tests/widget/test_widget_a11y_behavioral.py``. It guards the structural
invariant that the GDPR consent flow is offered before any chat message can
appear, regardless of any future Claude Design-driven refresh.

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

from __future__ import annotations

from pathlib import Path

WIDGET_SRC = Path(__file__).resolve().parent.parent.parent / "widget" / "src"
PANEL_TSX = WIDGET_SRC / "components" / "Panel.tsx"


def _panel_source() -> str:
    return PANEL_TSX.read_text(encoding="utf-8")


class TestConsentBannerOrdering:
    """Structural ordering invariants for ConsentBanner in Panel.tsx."""

    def test_panel_renders_consent_banner(self) -> None:
        source = _panel_source()
        assert "<ConsentBanner" in source, (
            "Panel.tsx must render <ConsentBanner ...>; I1 depends on this."
        )

    def test_panel_renders_message_list(self) -> None:
        source = _panel_source()
        assert "<MessageList" in source, (
            "Panel.tsx must render <MessageList ...>; I1 depends on this."
        )

    def test_consent_banner_appears_before_message_list(self) -> None:
        """I1: ConsentBanner block appears textually before MessageList.

        The render function is declarative JSX; textual order in the source
        reflects render order. Panel.tsx gates ConsentBanner on
        ``consent_collection_enabled === true`` and on the absence of
        ``consentCollected`` — when those gates are satisfied, the banner is
        rendered ahead of the conversation view.
        """
        source = _panel_source()
        consent_idx = source.find("<ConsentBanner")
        message_idx = source.find("<MessageList")
        assert consent_idx != -1, "<ConsentBanner not found in Panel.tsx"
        assert message_idx != -1, "<MessageList not found in Panel.tsx"
        assert consent_idx < message_idx, (
            f"ConsentBanner must be rendered before MessageList (I1). "
            f"Got consent_idx={consent_idx}, message_idx={message_idx}."
        )

    def test_consent_banner_gated_on_collection_flag(self) -> None:
        """I1 is tenant-configurable: banner gated on consent_collection_enabled."""
        source = _panel_source()
        assert "consent_collection_enabled" in source, (
            "ConsentBanner must be gated on consent_collection_enabled "
            "(tenant-configurable per D5 I1 description)."
        )

    def test_consent_banner_suppressed_for_admin_context(self) -> None:
        """Admin context has implicit consent (S259 D14) — banner suppressed."""
        source = _panel_source()
        assert "isAdminContext" in source, (
            "Panel.tsx must reference isAdminContext so admin sessions do "
            "not receive the consent banner."
        )
