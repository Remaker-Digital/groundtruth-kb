"""SPEC-1880 WhatsApp escalation tenant preference coverage."""

from __future__ import annotations

from src.multi_tenant.config.field_mapping import (
    _PREFS_DIRECT_FIELDS,
    _config_to_preferences,
    _preferences_to_config,
)
from src.multi_tenant.cosmos_schema import PreferencesDocument


def test_whatsapp_business_phone_is_persisted_preference_field() -> None:
    assert "whatsapp_business_phone" in PreferencesDocument.model_fields
    assert "whatsapp_business_phone" in _PREFS_DIRECT_FIELDS


def test_whatsapp_business_phone_round_trips_through_config_mapping() -> None:
    prefs = _config_to_preferences(
        tenant_id="tenant-whatsapp",
        config={
            "brand_name": "WhatsApp Shop",
            "whatsapp_business_phone": "+15551234567",
        },
        version=4,
        created_by="spec-1880-test",
    )

    assert prefs.whatsapp_business_phone == "+15551234567"

    restored_config = _preferences_to_config(prefs.model_dump())

    assert restored_config["brand_name"] == "WhatsApp Shop"
    assert restored_config["whatsapp_business_phone"] == "+15551234567"
