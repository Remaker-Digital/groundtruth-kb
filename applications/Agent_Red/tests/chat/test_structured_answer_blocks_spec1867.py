# © 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""SPEC-1867 structured answer block backend coverage."""

from __future__ import annotations

from src.chat.blocks import extract_blocks
from src.chat.models import validated_event
from src.multi_tenant.cosmos_schema import TenantTier
from src.multi_tenant.schema.validation import validate_field
from src.multi_tenant.tenant_config_schema import (
    get_fields_for_tier,
    reset_field_registry,
)


def test_extract_blocks_emits_only_accepted_v1_block_types() -> None:
    text = (
        "Return checklist\n"
        "1. Find your order number\n"
        "2. Print the return label\n\n"
        "Q: Can I exchange instead?\n"
        "A: Yes, choose exchange during the return flow.\n\n"
        "Product: Red Jacket, SKU RJ-100, price $99.\n"
        "[Start Return](https://example.com/returns)"
    )

    blocks = extract_blocks(text)
    block_types = [block["type"] for block in blocks]

    assert block_types == ["steps", "faq", "action"]
    assert set(block_types) <= {"steps", "faq", "action"}
    assert "product" not in block_types
    assert "product_card" not in block_types
    assert blocks[0]["items"] == ["Find your order number", "Print the return label"]
    assert blocks[1]["items"][0]["question"] == "Can I exchange instead?"
    assert blocks[2]["label"] == "Start Return"


def test_validated_event_includes_non_empty_blocks_and_preserves_sources() -> None:
    blocks = [
        {"type": "steps", "title": "Return checklist", "items": ["Find order", "Print label"]},
        {"type": "action", "label": "Start Return", "url": "https://example.com/returns"},
    ]
    sources = [{"title": "Returns FAQ", "url": "https://example.com/faq"}]

    event = validated_event(
        conversation_id="conv-1867",
        message_id="msg-1867",
        sources=sources,
        blocks=blocks,
    )

    assert event.data["conversation_id"] == "conv-1867"
    assert event.data["message_id"] == "msg-1867"
    assert event.data["critic_passed"] is True
    assert event.data["sources"] == sources
    assert event.data["blocks"] == blocks
    assert "blocks" not in validated_event("conv-1867", "msg-empty", blocks=[]).data
    assert "blocks" not in validated_event("conv-1867", "msg-none").data


def test_structured_blocks_enabled_is_professional_plus_tier_gated() -> None:
    reset_field_registry()
    try:
        starter_fields = get_fields_for_tier(TenantTier.STARTER)
        professional_fields = get_fields_for_tier(TenantTier.PROFESSIONAL)
        enterprise_fields = get_fields_for_tier(TenantTier.ENTERPRISE)

        assert "structured_blocks_enabled" not in starter_fields
        assert "structured_blocks_enabled" in professional_fields
        assert "structured_blocks_enabled" in enterprise_fields

        starter_valid, starter_error, starter_value = validate_field(
            "structured_blocks_enabled",
            True,
            TenantTier.STARTER,
        )
        assert starter_valid is False
        assert starter_value is None
        assert starter_error is not None
        assert "tier" in starter_error.lower()

        professional_valid, professional_error, professional_value = validate_field(
            "structured_blocks_enabled",
            True,
            TenantTier.PROFESSIONAL,
        )
        assert professional_valid is True
        assert professional_error is None
        assert professional_value is True

        enterprise_valid, enterprise_error, enterprise_value = validate_field(
            "structured_blocks_enabled",
            True,
            TenantTier.ENTERPRISE,
        )
        assert enterprise_valid is True
        assert enterprise_error is None
        assert enterprise_value is True
    finally:
        reset_field_registry()
