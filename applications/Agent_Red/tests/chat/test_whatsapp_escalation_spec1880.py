"""SPEC-1880 production WhatsApp escalation link coverage."""

from __future__ import annotations

from urllib.parse import quote

from src.chat.pipeline.orchestrator import _build_whatsapp_escalation_markdown_link
from src.multi_tenant.cosmos_schema import PreferencesDocument, TenantTier


def _prefs(**overrides: object) -> PreferencesDocument:
    fields = {
        "id": "tenant-whatsapp:1",
        "tenant_id": "tenant-whatsapp",
        "version": 1,
        "created_at": "2026-06-24T00:00:00Z",
    }
    fields.update(overrides)
    return PreferencesDocument(**fields)


def test_professional_tenant_gets_url_encoded_whatsapp_markdown_link() -> None:
    prefs = _prefs(whatsapp_business_phone="+15551234567")
    conversation_id = "abc12345-def0-4000-9000-0123456789ab"

    link = _build_whatsapp_escalation_markdown_link(
        prefs,
        TenantTier.PROFESSIONAL,
        conversation_id,
    )

    expected_text = quote("Hi, I need help with my conversation (ref: abc12345)")
    assert link == (f"[Open WhatsApp](https://wa.me/15551234567?text={expected_text})")


def test_enterprise_tenant_dict_preferences_get_whatsapp_markdown_link() -> None:
    link = _build_whatsapp_escalation_markdown_link(
        {"whatsapp_business_phone": "+447911123456"},
        TenantTier.ENTERPRISE,
        "conv9876-extra-context",
    )

    assert link is not None
    assert link.startswith("[Open WhatsApp](https://wa.me/447911123456?text=")
    assert "conv9876" in link


def test_starter_tenant_does_not_get_whatsapp_link() -> None:
    prefs = _prefs(whatsapp_business_phone="+15551234567")

    assert (
        _build_whatsapp_escalation_markdown_link(
            prefs,
            TenantTier.STARTER,
            "abc12345-def0",
        )
        is None
    )


def test_missing_phone_does_not_get_whatsapp_link() -> None:
    prefs = _prefs()

    assert (
        _build_whatsapp_escalation_markdown_link(
            prefs,
            TenantTier.PROFESSIONAL,
            "abc12345-def0",
        )
        is None
    )
