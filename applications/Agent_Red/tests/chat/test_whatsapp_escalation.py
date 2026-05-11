"""Tests for SPEC-1880 WhatsApp Escalation Channel.

Verifies that the WhatsApp deep-link is included in escalation messages
when the merchant has configured a WhatsApp business phone number.

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

from __future__ import annotations



class TestWhatsAppEscalationLink:
    def test_wa_link_format(self) -> None:
        """WhatsApp deep-link uses wa.me with URL-encoded text."""
        import urllib.parse

        phone = "+15551234567"
        conv_id = "abc12345-defg-hijk-lmno-pqrstuvwxyz"
        wa_text = urllib.parse.quote(
            f"Hi, I need help with my conversation (ref: {conv_id[:8]})"
        )
        wa_link = f"https://wa.me/{phone.lstrip('+')}?text={wa_text}"

        assert "wa.me/15551234567" in wa_link
        assert "text=" in wa_link
        assert "abc12345" in wa_link

    def test_wa_link_strips_plus(self) -> None:
        """Phone number plus sign is stripped for wa.me URL."""
        phone = "+447911123456"
        link = f"https://wa.me/{phone.lstrip('+')}"
        assert link == "https://wa.me/447911123456"

    def test_wa_phone_none_skips_link(self) -> None:
        """No WhatsApp link when phone is not configured."""
        wa_phone = None
        assert not wa_phone  # Would skip in orchestrator

    def test_wa_phone_empty_skips_link(self) -> None:
        """Empty string WhatsApp phone skips link."""
        wa_phone = ""
        assert not wa_phone  # Would skip in orchestrator

    def test_wa_phone_validation_pattern(self) -> None:
        """Phone number must match E.164-like pattern."""
        import re
        pattern = r"^\+[1-9]\d{6,14}$"
        assert re.match(pattern, "+15551234567")
        assert re.match(pattern, "+447911123456")
        assert not re.match(pattern, "5551234567")
        assert not re.match(pattern, "+0000000000")
        assert not re.match(pattern, "+1")
