"""
PreferencesDocument ↔ config schema field mapping.

Maps between the expanded config schema field set and the
PreferencesDocument Cosmos DB model. Contains the direct field sets
and bidirectional conversion functions.

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from src.multi_tenant.cosmos_schema import PreferencesDocument
from src.multi_tenant.tenant_config_schema import get_field_registry


# ---------------------------------------------------------------------------
# Direct field mapping
# ---------------------------------------------------------------------------

# Fields that map directly between the config schema and PreferencesDocument.
# Config schema may have more fields than PreferencesDocument — unmapped fields
# are stored in a JSON extension field or will be added to PreferencesDocument
# in future iterations.
_PREFS_DIRECT_FIELDS: set[str] = {
    # AI behavior (original 12 fields)
    "brand_name",
    "brand_voice",
    "primary_language",
    "additional_languages",
    "response_length",
    "formality_level",
    "return_policy",
    "shipping_info",
    "escalation_threshold",
    "escalation_keywords",
    "memory_enabled",
    "custom_instructions",
    # Widget appearance — visual (21 fields)
    "widget_primary_color",
    "widget_background_color",
    "widget_position",
    "widget_offset_x",
    "widget_offset_y",
    "widget_agent_avatar_url",
    "widget_agent_display_name",
    "widget_agent_title",
    "widget_logo_url",
    "widget_show_branding",
    "widget_mobile_enabled",
    "widget_mobile_fullscreen",
    "widget_mobile_position",
    "widget_mobile_offset_x",
    "widget_mobile_offset_y",
    "widget_dark_mode",
    "widget_color_mode",
    "widget_header_gradient_end",
    "widget_header_gradient_enabled",
    "widget_font_family",
    "widget_border_radius",
    "widget_launcher_size",
    "widget_launcher_icon",
    "widget_header_title",
    "widget_header_subtitle",
    "widget_agent_bubble_color",
    "widget_agent_bubble_text_color",
    "widget_customer_bubble_color",
    "widget_customer_bubble_text_color",
    "widget_launcher_shape",
    "widget_launcher_color",
    "widget_shadow_intensity",
    "widget_panel_width",
    "widget_panel_height",
    "widget_locale",
    # Widget appearance — behavior (14 fields)
    "widget_offline_message",
    "widget_auto_open",
    "widget_auto_open_delay",
    "widget_operating_hours",
    "widget_offline_behavior",
    "widget_prechat_form",
    "widget_chat_rating_enabled",
    "widget_sound_enabled",
    "widget_file_upload_enabled",
    "widget_greeting_enabled",
    "widget_greeting_mode",
    "widget_greeting_message",
    "widget_pre_chat_form_enabled",
    "widget_pre_chat_fields",
    "widget_offline_form_enabled",
    # Widget authentication
    "widget_key",
    # Widget appearance — content and targeting (3 fields)
    "widget_header_text",
    "widget_input_placeholder",
    "widget_page_rules",
    # Widget engagement triggers (WI-0816)
    "widget_exit_intent_enabled",
    "widget_scroll_depth_trigger",
    # Integrations (C10)
    "shopify_sync_enabled",
    "zendesk_escalation_enabled",
    "mailchimp_segment_sync",
    "google_analytics_enabled",
    "shopify_integration_status",
    "zendesk_integration_status",
    "mailchimp_integration_status",
    "google_analytics_integration_status",
    # Notifications (WI-G)
    "notification_email",
    # Retrieval tuning (RAG Phase 1)
    "retrieval_top_k",
    "retrieval_vector_weight",
    "retrieval_bm25_weight",
    "retrieval_min_score",
    # Intent-to-source routing (RAG Phase 1)
    "intent_source_mapping",
    # Source citation (RAG Phase 1)
    "cite_sources_in_response",
    # MCP Server Configuration (AGNTCY Phase 3)
    "mcp_servers",
    "mcp_enabled",
    # Stripe MCP (AGNTCY Phase 3B — Cycle 5)
    "stripe_mcp_enabled",
    "stripe_mcp_status",
    "mutation_policy",
}


# Widget appearance fields — subset of _PREFS_DIRECT_FIELDS used for C4
_WIDGET_APPEARANCE_FIELDS = frozenset(
    fname for fname in _PREFS_DIRECT_FIELDS if fname.startswith("widget_")
)


# ---------------------------------------------------------------------------
# Bidirectional conversion
# ---------------------------------------------------------------------------


def _config_to_preferences(
    tenant_id: str,
    config: dict[str, Any],
    version: int,
    created_by: str | None = None,
) -> PreferencesDocument:
    """Map a resolved config dict to a PreferencesDocument for persistence.

    Fields in the config schema that are not directly represented in
    PreferencesDocument are stored in the document model as-is where
    field names match, and are otherwise preserved through the config
    resolution pipeline (they appear in the resolved config returned
    to callers but may not all persist individually in
    PreferencesDocument today).

    Args:
        tenant_id: Tenant identifier.
        config: Resolved config dict (validated field_name → value).
        version: Version number to assign.
        created_by: Actor who created this version.

    Returns:
        PreferencesDocument ready for persistence.
    """
    now = datetime.now(timezone.utc).isoformat()

    # Extract fields that map directly to PreferencesDocument
    prefs_kwargs: dict[str, Any] = {}
    for field_name in _PREFS_DIRECT_FIELDS:
        if field_name in config:
            prefs_kwargs[field_name] = config[field_name]

    return PreferencesDocument(
        id=f"{tenant_id}:{version}",
        tenant_id=tenant_id,
        version=version,
        is_current=True,
        config_state="active",
        activated_at=now,
        activated_by=created_by,
        created_at=now,
        created_by=created_by,
        **prefs_kwargs,
    )


def _preferences_to_config(prefs_doc: dict[str, Any]) -> dict[str, Any]:
    """Extract config values from a PreferencesDocument dict.

    Reverses the mapping — reads stored preferences and returns the
    subset of config fields that were persisted.

    Args:
        prefs_doc: Raw Cosmos DB document (dict) from PreferencesRepository.

    Returns:
        Dict of field_name → value for known config fields.
    """
    result: dict[str, Any] = {}
    registry = get_field_registry()

    for field_name in registry:
        if field_name in prefs_doc and prefs_doc[field_name] is not None:
            result[field_name] = prefs_doc[field_name]

    # Also read fields in _PREFS_DIRECT_FIELDS that aren't in the registry
    # (e.g. widget_key, integration statuses, notification_email)
    for field_name in _PREFS_DIRECT_FIELDS:
        if field_name not in result and field_name in prefs_doc and prefs_doc[field_name] is not None:
            result[field_name] = prefs_doc[field_name]

    return result
