"""TenantConfigProcessor — validation, cleansing, versioning, and caching.

Work Item #64 (Decision #22): Layer 1 of the 5-layer tenant configuration
system — the standalone validation/cleansing service consumable via API,
CLI, or GUI.

Responsibilities:
    - Accept partial config updates from any client (API, CLI, GUI)
    - Validate against the tenant_config_schema (#63)
    - Resolve config inheritance: platform defaults → tier defaults → tenant
      overrides → incoming changes
    - Persist versioned PreferencesDocument with monotonic version numbers
    - Maintain a 60-second in-memory cache of resolved config per tenant
    - Audit log every config change (CONFIG_UPDATED event)
    - Support rollback to any previous version
    - Map between the schema's expanded field set and PreferencesDocument

The processor is API/CLI/GUI-agnostic — it receives dicts and returns
structured results.  The Configuration API (#65) wraps this as HTTP
endpoints.

Config inheritance (Decision #22):
    platform defaults → tier defaults → tenant overrides → (future A/B)

Cache strategy:
    60-second in-memory TTL per tenant (Decision #22).  Cache is
    invalidated on write.  In a multi-instance deployment, each instance
    maintains its own cache — eventual consistency within 60 seconds is
    acceptable for config changes.

Architecture references:
    - Decision #22: 5-layer tenant configuration management
    - Decision #23: SystemPromptBuilder (consumes resolved config)
    - Work Item #64: TenantConfigProcessor
    - Work Item #63: tenant_config_schema (upstream dependency)
    - Work Item #65: Configuration API (downstream consumer)

Dependencies:
    - tenant_config_schema.py: validate_config, resolve_defaults, get_field_registry
    - cosmos_schema.py: PreferencesDocument, TenantTier, AuditEventType
    - repository.py: PreferencesRepository, AuditLogRepository

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

from __future__ import annotations

import asyncio
import logging
import time
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any

from pydantic import BaseModel, Field

from src.multi_tenant.cosmos_schema import (
    AuditEventType,
    PreferencesDocument,
    TenantTier,
)
from src.multi_tenant.tenant_config_schema import (
    ConfigValidationResult,
    get_field_registry,
    get_fields_for_tier,
    resolve_defaults,
    validate_config,
)

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

CACHE_TTL_SECONDS = 60  # Decision #22: 60-second in-memory cache


# ---------------------------------------------------------------------------
# Result models
# ---------------------------------------------------------------------------


class ConfigUpdateResult(BaseModel):
    """Result of a config update operation."""

    success: bool = Field(default=False, description="Whether the update was persisted")
    version: int = Field(default=0, description="New config version number")
    validation: ConfigValidationResult = Field(
        default_factory=lambda: ConfigValidationResult(valid=True),
        description="Validation result with errors/warnings",
    )
    changes: dict[str, Any] = Field(
        default_factory=dict,
        description="Fields that actually changed (old → new)",
    )
    resolved_config: dict[str, Any] = Field(
        default_factory=dict,
        description="The fully resolved config after the update",
    )


class ConfigReadResult(BaseModel):
    """Result of reading the current resolved config."""

    tenant_id: str = Field(description="Tenant identifier")
    tier: str = Field(description="Current tier")
    version: int = Field(description="Current config version")
    config: dict[str, Any] = Field(description="Fully resolved config values")
    from_cache: bool = Field(default=False, description="Whether this came from cache")


class ConfigVersionInfo(BaseModel):
    """Summary of a config version."""

    version: int = Field(description="Version number")
    is_current: bool = Field(description="Whether this is the active version")
    created_at: str = Field(description="When this version was created")
    created_by: str | None = Field(default=None, description="Who created it")
    field_count: int = Field(default=0, description="Number of configured fields")
    config_name: str | None = Field(default=None, description="Named configuration label")


class NamedConfigSummary(BaseModel):
    """Summary of a named configuration."""

    name: str = Field(description="Configuration name")
    version: int = Field(description="Version number this name points to")
    is_active: bool = Field(description="Whether this is the currently active named config")
    is_default: bool = Field(description="Whether this is the undeletable Default config")
    created_at: str = Field(description="When this named config was created")
    created_by: str | None = Field(default=None, description="Who created it")
    field_count: int = Field(default=0, description="Number of configured fields")


class ConfigRollbackResult(BaseModel):
    """Result of a rollback operation."""

    success: bool = Field(description="Whether the rollback was completed")
    from_version: int = Field(description="Version before rollback")
    to_version: int = Field(description="Version rolled back to")
    new_version: int = Field(description="New version created by rollback")
    message: str = Field(default="", description="Status message")


# ---------------------------------------------------------------------------
# Cache entry
# ---------------------------------------------------------------------------


@dataclass
class _CacheEntry:
    """In-memory cached resolved config for a tenant."""

    resolved: dict[str, Any]
    version: int
    tier: TenantTier
    expires_at: float  # time.monotonic() timestamp


# ---------------------------------------------------------------------------
# PreferencesDocument field mapping
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
    "widget_dark_mode",
    "widget_color_mode",
    "widget_header_gradient_end",
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
}


# Widget appearance fields — subset of _PREFS_DIRECT_FIELDS used for C4
_WIDGET_APPEARANCE_FIELDS = frozenset(
    fname for fname in _PREFS_DIRECT_FIELDS if fname.startswith("widget_")
)


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


# ---------------------------------------------------------------------------
# TenantConfigProcessor
# ---------------------------------------------------------------------------


class TenantConfigProcessor:
    """Validates, cleanses, versions, and caches tenant configuration.

    This is the central service for all config mutations. It is
    API/CLI/GUI-agnostic — callers pass dicts and receive structured
    results.

    Usage::

        processor = get_config_processor()
        processor.configure(prefs_repo, audit_repo)

        # Read current config
        result = await processor.get_config(tenant_id, tier)

        # Update config
        result = await processor.update_config(
            tenant_id=tenant_id,
            tier=tier,
            changes={"brand_name": "New Name", "formality_level": "formal"},
            actor="user:merchant@example.com",
        )

        # Rollback
        result = await processor.rollback(tenant_id, tier, target_version=3)
    """

    def __init__(self) -> None:
        self._prefs_repo: Any | None = None
        self._audit_repo: Any | None = None
        self._cache: dict[str, _CacheEntry] = {}
        self._lock = asyncio.Lock()

    def configure(
        self,
        prefs_repo: Any,
        audit_repo: Any,
    ) -> None:
        """Inject repository dependencies.

        Called at application startup after Cosmos DB is initialized.

        Args:
            prefs_repo: PreferencesRepository instance.
            audit_repo: AuditLogRepository instance.
        """
        self._prefs_repo = prefs_repo
        self._audit_repo = audit_repo
        logger.info("TenantConfigProcessor configured with repositories")

    @property
    def _is_configured(self) -> bool:
        return self._prefs_repo is not None and self._audit_repo is not None

    # ---- Public API: Read --------------------------------------------------

    async def get_config(
        self,
        tenant_id: str,
        tier: TenantTier,
    ) -> ConfigReadResult:
        """Get the fully resolved current config for a tenant.

        Resolution order: platform defaults → tier defaults → tenant
        overrides (from PreferencesDocument).

        Uses the 60-second in-memory cache when available.

        Args:
            tenant_id: Tenant identifier.
            tier: Tenant's current subscription tier.

        Returns:
            ConfigReadResult with the resolved config.
        """
        # Check cache
        cached = self._get_cached(tenant_id)
        if cached is not None:
            return ConfigReadResult(
                tenant_id=tenant_id,
                tier=tier.value,
                version=cached.version,
                config=cached.resolved,
                from_cache=True,
            )

        # Resolve from database
        resolved, version = await self._resolve_config(tenant_id, tier)

        # Cache the result
        self._set_cache(tenant_id, resolved, version, tier)

        return ConfigReadResult(
            tenant_id=tenant_id,
            tier=tier.value,
            version=version,
            config=resolved,
            from_cache=False,
        )

    async def get_config_diff(
        self,
        tenant_id: str,
        tier: TenantTier,
    ) -> dict[str, Any]:
        """Get the tenant's overrides vs. tier defaults.

        Returns only the fields where the tenant has explicitly set a
        value different from the tier default.

        Args:
            tenant_id: Tenant identifier.
            tier: Tenant's current subscription tier.

        Returns:
            Dict of field_name → {"current": value, "default": default}
            for fields that differ from defaults.
        """
        resolved, _ = await self._resolve_config(tenant_id, tier)
        defaults = resolve_defaults(tier)
        diff: dict[str, Any] = {}

        for field_name, current_val in resolved.items():
            default_val = defaults.get(field_name)
            if current_val != default_val:
                diff[field_name] = {
                    "current": current_val,
                    "default": default_val,
                }

        return diff

    # ---- Public API: Write -------------------------------------------------

    async def update_config(
        self,
        tenant_id: str,
        tier: TenantTier,
        changes: dict[str, Any],
        actor: str = "system",
    ) -> ConfigUpdateResult:
        """Validate and apply a partial config update.

        1. Validates all changed fields against the schema
        2. Merges changes into the current resolved config
        3. Creates a new PreferencesDocument version
        4. Invalidates the cache
        5. Logs an audit event

        Args:
            tenant_id: Tenant identifier.
            tier: Tenant's current subscription tier.
            changes: Partial dict of field_name → new_value.
            actor: Who is making the change (for audit log).

        Returns:
            ConfigUpdateResult with validation, changes, and new version.
        """
        result = ConfigUpdateResult()

        # Step 1: Validate the incoming changes
        validation = validate_config(changes, tier)
        result.validation = validation

        if not validation.valid:
            result.success = False
            return result

        # Step 2: Resolve the current config
        current_resolved, current_version = await self._resolve_config(tenant_id, tier)

        # Step 3: Compute actual changes (diff against current)
        actual_changes: dict[str, Any] = {}
        for field_name, new_value in validation.sanitized.items():
            old_value = current_resolved.get(field_name)
            if old_value != new_value:
                actual_changes[field_name] = {
                    "old": old_value,
                    "new": new_value,
                }

        if not actual_changes:
            # No actual changes — return success with current version
            result.success = True
            result.version = current_version
            result.resolved_config = current_resolved
            return result

        # Step 4: Merge changes into the resolved config
        merged = dict(current_resolved)
        for field_name in actual_changes:
            merged[field_name] = actual_changes[field_name]["new"]

        # Step 5: Create new PreferencesDocument version
        new_version = current_version + 1
        prefs_doc = _config_to_preferences(
            tenant_id=tenant_id,
            config=merged,
            version=new_version,
            created_by=actor,
        )

        if not self._is_configured:
            logger.error(
                "TenantConfigProcessor: repositories not configured — "
                "config change for tenant=%s REJECTED. Call configure() "
                "at startup to wire Cosmos DB repositories.",
                tenant_id,
            )
            result.success = False
            result.validation = ConfigValidationResult(
                valid=False,
                errors=[{
                    "field": "_system",
                    "message": "Configuration service is not available. Please try again later.",
                }],
            )
            return result

        async with self._lock:
            await self._prefs_repo.create_version(tenant_id, prefs_doc)

        # Step 6: Invalidate cache
        self._invalidate_cache(tenant_id)

        # Step 7: Audit log
        await self._log_config_change(
            tenant_id=tenant_id,
            actor=actor,
            from_version=current_version,
            to_version=new_version,
            changes=actual_changes,
        )

        # Step 8: Build result
        result.success = True
        result.version = new_version
        result.changes = actual_changes
        result.resolved_config = merged

        logger.info(
            "Config updated: tenant=%s version=%d→%d fields_changed=%d actor=%s",
            tenant_id[:8], current_version, new_version,
            len(actual_changes), actor,
        )

        return result

    async def reset_to_defaults(
        self,
        tenant_id: str,
        tier: TenantTier,
        actor: str = "system",
    ) -> ConfigUpdateResult:
        """Reset all tenant config to tier defaults.

        Creates a new version with only default values — effectively
        clearing all tenant overrides.

        Args:
            tenant_id: Tenant identifier.
            tier: Tenant's current subscription tier.
            actor: Who is performing the reset.

        Returns:
            ConfigUpdateResult with the defaults as resolved config.
        """
        defaults = resolve_defaults(tier)
        current_resolved, current_version = await self._resolve_config(tenant_id, tier)

        # Compute what changed
        actual_changes: dict[str, Any] = {}
        for field_name, default_val in defaults.items():
            current_val = current_resolved.get(field_name)
            if current_val != default_val:
                actual_changes[field_name] = {
                    "old": current_val,
                    "new": default_val,
                }

        if not self._is_configured:
            logger.error(
                "TenantConfigProcessor: repositories not configured — "
                "config reset for tenant=%s REJECTED.",
                tenant_id,
            )
            return ConfigUpdateResult(
                success=False,
                validation=ConfigValidationResult(
                    valid=False,
                    errors=[{
                        "field": "_system",
                        "message": "Configuration service is not available. Please try again later.",
                    }],
                ),
            )

        new_version = current_version + 1
        prefs_doc = _config_to_preferences(
            tenant_id=tenant_id,
            config=defaults,
            version=new_version,
            created_by=actor,
        )

        async with self._lock:
            await self._prefs_repo.create_version(tenant_id, prefs_doc)

        self._invalidate_cache(tenant_id)

        await self._log_config_change(
            tenant_id=tenant_id,
            actor=actor,
            from_version=current_version,
            to_version=new_version,
            changes=actual_changes,
            reset=True,
        )

        logger.info(
            "Config reset to defaults: tenant=%s version=%d→%d actor=%s",
            tenant_id[:8], current_version, new_version, actor,
        )

        return ConfigUpdateResult(
            success=True,
            version=new_version,
            changes=actual_changes,
            resolved_config=defaults,
        )

    # ---- Public API: Named Configurations (C3) ------------------------------

    async def save_named_config(
        self,
        tenant_id: str,
        tier: TenantTier,
        name: str,
        actor: str = "system",
    ) -> ConfigUpdateResult:
        """Save the current config as a named configuration.

        Creates a new version with the given name attached.  The current
        resolved config is snapshot-copied into the new version.

        If a named config with the same name already exists, the old
        version loses its name (replaced by the new snapshot).

        'Default' is the undeletable initial production config.

        Args:
            tenant_id: Tenant identifier.
            tier: Tenant's current subscription tier.
            name: Configuration name (e.g. 'Holiday Mode').
            actor: Who is performing the save.

        Returns:
            ConfigUpdateResult with the new version.
        """
        if not self._is_configured:
            return ConfigUpdateResult(
                success=False,
                validation=ConfigValidationResult(
                    valid=False,
                    errors=[{
                        "field": "_system",
                        "message": "Configuration service is not available.",
                    }],
                ),
            )

        # Get the current resolved config
        resolved, current_version = await self._resolve_config(tenant_id, tier)

        # If a config with this name already exists, clear the old name
        existing = await self._prefs_repo.get_by_name(tenant_id, name)
        if existing is not None:
            try:
                await self._prefs_repo.patch(
                    tenant_id=tenant_id,
                    document_id=existing["id"],
                    operations=[{"op": "set", "path": "/config_name", "value": None}],
                )
            except Exception as exc:
                logger.warning(
                    "Failed to clear old named config '%s' for tenant=%s: %s",
                    name, tenant_id[:8], exc,
                )

        # Create a new version with the name
        new_version = current_version + 1
        prefs_doc = _config_to_preferences(
            tenant_id=tenant_id,
            config=resolved,
            version=new_version,
            created_by=actor,
        )
        prefs_doc.config_name = name

        async with self._lock:
            await self._prefs_repo.create_version(tenant_id, prefs_doc)

        self._invalidate_cache(tenant_id)

        # Audit log
        if self._audit_repo is not None:
            await self._audit_repo.log_event(
                event_type=AuditEventType.CONFIG_UPDATED,
                tenant_id=tenant_id,
                actor=actor,
                actor_type="user" if actor.startswith("user:") else "system",
                payload={
                    "action": "save_named_config",
                    "config_name": name,
                    "from_version": current_version,
                    "to_version": new_version,
                },
            )

        logger.info(
            "Named config saved: tenant=%s name='%s' version=%d actor=%s",
            tenant_id[:8], name, new_version, actor,
        )

        return ConfigUpdateResult(
            success=True,
            version=new_version,
            resolved_config=resolved,
        )

    async def list_named_configs(
        self,
        tenant_id: str,
    ) -> list[NamedConfigSummary]:
        """List all named configurations for a tenant.

        Returns:
            List of NamedConfigSummary, newest first.
        """
        if not self._is_configured:
            return []

        named_versions = await self._prefs_repo.list_named(tenant_id)

        # Determine which version is currently active
        current = await self._prefs_repo.get_current(tenant_id)
        current_version = current.get("version", 0) if current else 0

        return [
            NamedConfigSummary(
                name=v.get("config_name", ""),
                version=v.get("version", 0),
                is_active=v.get("version", 0) == current_version,
                is_default=v.get("config_name", "").lower() == "default",
                created_at=v.get("created_at", ""),
                created_by=v.get("created_by"),
                field_count=sum(
                    1 for fname in _PREFS_DIRECT_FIELDS
                    if v.get(fname) is not None
                ),
            )
            for v in named_versions
            if v.get("config_name")
        ]

    async def activate_named_config(
        self,
        tenant_id: str,
        tier: TenantTier,
        name: str,
        actor: str = "system",
    ) -> ConfigUpdateResult:
        """Activate a named configuration — make it the current active config.

        Resolves the named config's stored values against current tier
        defaults and creates a new version marked as current.

        Args:
            tenant_id: Tenant identifier.
            tier: Tenant's current subscription tier.
            name: Configuration name to activate.
            actor: Who is activating.

        Returns:
            ConfigUpdateResult with the newly activated version.
        """
        if not self._is_configured:
            return ConfigUpdateResult(
                success=False,
                validation=ConfigValidationResult(
                    valid=False,
                    errors=[{
                        "field": "_system",
                        "message": "Configuration service is not available.",
                    }],
                ),
            )

        # Find the named config
        named_doc = await self._prefs_repo.get_by_name(tenant_id, name)
        if named_doc is None:
            return ConfigUpdateResult(
                success=False,
                validation=ConfigValidationResult(
                    valid=False,
                    errors=[{
                        "field": "_system",
                        "message": f"Named configuration '{name}' not found.",
                    }],
                ),
            )

        # Resolve: tier defaults + named config's stored overrides
        defaults = resolve_defaults(tier)
        stored = _preferences_to_config(named_doc)
        resolved = {**defaults, **stored}

        # Get current version
        current = await self._prefs_repo.get_current(tenant_id)
        current_version = current.get("version", 0) if current else 0

        # Create new version with the named config's content, keeping the name
        new_version = current_version + 1
        prefs_doc = _config_to_preferences(
            tenant_id=tenant_id,
            config=resolved,
            version=new_version,
            created_by=actor,
        )
        prefs_doc.config_name = name

        async with self._lock:
            await self._prefs_repo.create_version(tenant_id, prefs_doc)

        self._invalidate_cache(tenant_id)

        # Audit log
        if self._audit_repo is not None:
            await self._audit_repo.log_event(
                event_type=AuditEventType.CONFIG_UPDATED,
                tenant_id=tenant_id,
                actor=actor,
                actor_type="user" if actor.startswith("user:") else "system",
                payload={
                    "action": "activate_named_config",
                    "config_name": name,
                    "from_version": current_version,
                    "to_version": new_version,
                    "source_version": named_doc.get("version", 0),
                },
            )

        logger.info(
            "Named config activated: tenant=%s name='%s' version=%d actor=%s",
            tenant_id[:8], name, new_version, actor,
        )

        return ConfigUpdateResult(
            success=True,
            version=new_version,
            resolved_config=resolved,
        )

    async def delete_named_config(
        self,
        tenant_id: str,
        name: str,
        actor: str = "system",
    ) -> bool:
        """Delete a named configuration.

        The 'Default' config cannot be deleted.  Deleting a named config
        clears the config_name field on the version document — the version
        itself is not removed (preserving full history).

        Args:
            tenant_id: Tenant identifier.
            name: Configuration name to delete.
            actor: Who is deleting.

        Returns:
            True if deleted, False if not found or protected.
        """
        if name.lower() == "default":
            logger.warning(
                "Cannot delete Default config: tenant=%s actor=%s",
                tenant_id[:8], actor,
            )
            return False

        if not self._is_configured:
            return False

        named_doc = await self._prefs_repo.get_by_name(tenant_id, name)
        if named_doc is None:
            return False

        # Clear the name (don't delete the version document)
        await self._prefs_repo.patch(
            tenant_id=tenant_id,
            document_id=named_doc["id"],
            operations=[{"op": "set", "path": "/config_name", "value": None}],
        )

        # Audit log
        if self._audit_repo is not None:
            await self._audit_repo.log_event(
                event_type=AuditEventType.CONFIG_UPDATED,
                tenant_id=tenant_id,
                actor=actor,
                actor_type="user" if actor.startswith("user:") else "system",
                payload={
                    "action": "delete_named_config",
                    "config_name": name,
                    "version": named_doc.get("version", 0),
                },
            )

        logger.info(
            "Named config deleted: tenant=%s name='%s' actor=%s",
            tenant_id[:8], name, actor,
        )

        return True

    # ---- Public API: Named Widget Appearances (C4) -------------------------

    async def save_named_appearance(
        self,
        tenant_id: str,
        tier: TenantTier,
        name: str,
        actor: str = "system",
    ) -> ConfigUpdateResult:
        """Save current widget appearance fields as a named snapshot.

        Only ``widget_*`` fields are included in the snapshot.  If a name
        already exists, the old version's ``appearance_name`` is cleared
        before assigning the name to the new version.

        Args:
            tenant_id: Tenant identifier.
            tier: Tenant tier (for default resolution).
            name: Appearance name (e.g. 'Dark Theme').
            actor: Who is saving.

        Returns:
            ConfigUpdateResult.
        """
        if not self._is_configured:
            return ConfigUpdateResult(
                success=False,
                validation=ConfigValidationResult(
                    valid=False, errors=[{"error": "Service not configured"}],
                ),
            )

        # Get current resolved config
        resolved, current_version = await self._resolve_config(tenant_id, tier)

        # Extract only widget appearance fields
        widget_fields = {
            k: v for k, v in resolved.items()
            if k in _WIDGET_APPEARANCE_FIELDS and v is not None
        }

        # If name exists on another version, clear it
        existing = await self._prefs_repo.get_by_appearance_name(tenant_id, name)
        if existing is not None:
            await self._prefs_repo.patch(
                tenant_id=tenant_id,
                document_id=existing["id"],
                operations=[{"op": "set", "path": "/appearance_name", "value": None}],
            )

        # Build a new version with only widget fields + appearance_name
        new_version = current_version + 1
        doc_id = f"{tenant_id}:{new_version}"

        doc_data: dict[str, Any] = {
            "id": doc_id,
            "tenant_id": tenant_id,
            "version": new_version,
            "is_current": False,  # Appearance versions don't affect main config
            "appearance_name": name,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "created_by": actor,
        }
        # Populate widget fields
        for field_name in _WIDGET_APPEARANCE_FIELDS:
            if field_name in widget_fields:
                doc_data[field_name] = widget_fields[field_name]

        await self._prefs_repo.create(tenant_id, doc_data)

        # Audit log
        if self._audit_repo is not None:
            await self._audit_repo.log_event(
                event_type=AuditEventType.CONFIG_UPDATED,
                tenant_id=tenant_id,
                actor=actor,
                actor_type="user" if actor.startswith("user:") else "system",
                payload={
                    "action": "save_named_appearance",
                    "appearance_name": name,
                    "version": new_version,
                    "field_count": len(widget_fields),
                },
            )

        # Invalidate cache
        self._cache.pop(tenant_id, None)

        logger.info(
            "Named appearance saved: tenant=%s name='%s' version=%d fields=%d actor=%s",
            tenant_id[:8], name, new_version, len(widget_fields), actor,
        )

        return ConfigUpdateResult(
            success=True,
            version=new_version,
            resolved_config=widget_fields,
        )

    async def list_named_appearances(
        self,
        tenant_id: str,
    ) -> list[NamedConfigSummary]:
        """List all named widget appearances for a tenant.

        Returns:
            List of NamedConfigSummary with appearance metadata.
        """
        if not self._is_configured:
            return []

        raw = await self._prefs_repo.list_named_appearances(tenant_id)

        # Determine the current active appearance name
        current_doc = await self._prefs_repo.get_current(tenant_id)
        current_appearance = (
            current_doc.get("appearance_name") if current_doc else None
        )

        results: list[NamedConfigSummary] = []
        for v in raw:
            name = v.get("appearance_name", "")
            results.append(
                NamedConfigSummary(
                    name=name,
                    version=v.get("version", 0),
                    is_active=(name == current_appearance) if current_appearance else False,
                    is_default=name.lower() == "default",
                    created_at=v.get("created_at", ""),
                    created_by=v.get("created_by"),
                    field_count=sum(
                        1 for fname in _WIDGET_APPEARANCE_FIELDS
                        if v.get(fname) is not None
                    ),
                )
            )

        return results

    async def activate_named_appearance(
        self,
        tenant_id: str,
        tier: TenantTier,
        name: str,
        actor: str = "system",
    ) -> ConfigUpdateResult:
        """Activate a named widget appearance.

        Copies the widget_* fields from the named appearance version into
        the current live config, creating a new version.

        Args:
            tenant_id: Tenant identifier.
            tier: Tenant tier.
            name: Appearance name to activate.
            actor: Who is activating.

        Returns:
            ConfigUpdateResult (success=False if not found).
        """
        if not self._is_configured:
            return ConfigUpdateResult(success=False)

        # Find the named appearance doc
        appearance_doc = await self._prefs_repo.get_by_appearance_name(tenant_id, name)
        if appearance_doc is None:
            return ConfigUpdateResult(success=False)

        # Extract widget fields from the appearance snapshot
        widget_overrides: dict[str, Any] = {}
        for fname in _WIDGET_APPEARANCE_FIELDS:
            val = appearance_doc.get(fname)
            if val is not None:
                widget_overrides[fname] = val

        # Apply as partial update (reuses existing update_config logic)
        result = await self.update_config(
            tenant_id=tenant_id,
            tier=tier,
            updates=widget_overrides,
            actor=actor,
        )

        if result.success:
            # Tag the new current version with the appearance name
            current_doc = await self._prefs_repo.get_current(tenant_id)
            if current_doc is not None:
                await self._prefs_repo.patch(
                    tenant_id=tenant_id,
                    document_id=current_doc["id"],
                    operations=[{
                        "op": "set",
                        "path": "/appearance_name",
                        "value": name,
                    }],
                )

            logger.info(
                "Named appearance activated: tenant=%s name='%s' version=%d actor=%s",
                tenant_id[:8], name, result.version, actor,
            )

        return result

    async def delete_named_appearance(
        self,
        tenant_id: str,
        name: str,
        actor: str = "system",
    ) -> bool:
        """Delete a named widget appearance.

        The 'Default' appearance cannot be deleted.  Clearing the
        appearance_name field preserves the version document.

        Args:
            tenant_id: Tenant identifier.
            name: Appearance name to delete.
            actor: Who is deleting.

        Returns:
            True if deleted, False if not found or protected.
        """
        if name.lower() == "default":
            logger.warning(
                "Cannot delete Default appearance: tenant=%s actor=%s",
                tenant_id[:8], actor,
            )
            return False

        if not self._is_configured:
            return False

        appearance_doc = await self._prefs_repo.get_by_appearance_name(tenant_id, name)
        if appearance_doc is None:
            return False

        # Clear the name
        await self._prefs_repo.patch(
            tenant_id=tenant_id,
            document_id=appearance_doc["id"],
            operations=[{"op": "set", "path": "/appearance_name", "value": None}],
        )

        # Audit log
        if self._audit_repo is not None:
            await self._audit_repo.log_event(
                event_type=AuditEventType.CONFIG_UPDATED,
                tenant_id=tenant_id,
                actor=actor,
                actor_type="user" if actor.startswith("user:") else "system",
                payload={
                    "action": "delete_named_appearance",
                    "appearance_name": name,
                    "version": appearance_doc.get("version", 0),
                },
            )

        logger.info(
            "Named appearance deleted: tenant=%s name='%s' actor=%s",
            tenant_id[:8], name, actor,
        )

        return True

    # ---- Public API: Versioning --------------------------------------------

    async def list_versions(
        self,
        tenant_id: str,
        max_items: int = 20,
    ) -> list[ConfigVersionInfo]:
        """List config version history for a tenant.

        Args:
            tenant_id: Tenant identifier.
            max_items: Maximum versions to return.

        Returns:
            List of ConfigVersionInfo, newest first.
        """
        if not self._is_configured:
            return []

        raw_versions = await self._prefs_repo.list_versions(
            tenant_id, max_items=max_items,
        )

        return [
            ConfigVersionInfo(
                version=v.get("version", 0),
                is_current=v.get("is_current", False),
                created_at=v.get("created_at", ""),
                created_by=v.get("created_by"),
                field_count=sum(
                    1 for fname in _PREFS_DIRECT_FIELDS
                    if v.get(fname) is not None
                ),
                config_name=v.get("config_name"),
            )
            for v in raw_versions
        ]

    async def get_version(
        self,
        tenant_id: str,
        tier: TenantTier,
        version: int,
    ) -> ConfigReadResult | None:
        """Get a specific historical config version.

        Resolves the version's stored values against tier defaults to
        produce the full resolved config as it was at that version.

        Args:
            tenant_id: Tenant identifier.
            tier: Tenant's current subscription tier.
            version: Version number to retrieve.

        Returns:
            ConfigReadResult for that version, or None if not found.
        """
        if not self._is_configured:
            return None

        raw = await self._prefs_repo.get_version(tenant_id, version)
        if raw is None:
            return None

        # Resolve: defaults + stored overrides
        defaults = resolve_defaults(tier)
        stored = _preferences_to_config(raw)
        resolved = {**defaults, **stored}

        return ConfigReadResult(
            tenant_id=tenant_id,
            tier=tier.value,
            version=raw.get("version", 0),
            config=resolved,
            from_cache=False,
        )

    async def rollback(
        self,
        tenant_id: str,
        tier: TenantTier,
        target_version: int,
        actor: str = "system",
    ) -> ConfigRollbackResult:
        """Roll back to a previous config version.

        Creates a NEW version with the contents of the target version.
        Does not delete intermediate versions (preserving full history).

        Args:
            tenant_id: Tenant identifier.
            tier: Tenant's current subscription tier.
            target_version: Version number to roll back to.
            actor: Who is performing the rollback.

        Returns:
            ConfigRollbackResult with version info.
        """
        if not self._is_configured:
            logger.error(
                "TenantConfigProcessor: repositories not configured — "
                "rollback for tenant=%s REJECTED.",
                tenant_id,
            )
            return ConfigRollbackResult(
                success=False,
                from_version=0,
                to_version=target_version,
                new_version=0,
                message="Configuration service is not available. Please try again later.",
            )

        # Get target version
        target_raw = await self._prefs_repo.get_version(tenant_id, target_version)
        if target_raw is None:
            return ConfigRollbackResult(
                success=False,
                from_version=0,
                to_version=target_version,
                new_version=0,
                message=f"Version {target_version} not found",
            )

        # Get current version
        current_raw = await self._prefs_repo.get_current(tenant_id)
        current_version = current_raw.get("version", 0) if current_raw else 0

        if target_version == current_version:
            return ConfigRollbackResult(
                success=True,
                from_version=current_version,
                to_version=target_version,
                new_version=current_version,
                message="Already at target version",
            )

        # Extract config from target version
        target_config = _preferences_to_config(target_raw)

        # Resolve against current tier defaults
        defaults = resolve_defaults(tier)
        resolved = {**defaults, **target_config}

        # Create a new version with the target's contents
        new_version = current_version + 1
        prefs_doc = _config_to_preferences(
            tenant_id=tenant_id,
            config=resolved,
            version=new_version,
            created_by=actor,
        )

        async with self._lock:
            await self._prefs_repo.create_version(tenant_id, prefs_doc)

        self._invalidate_cache(tenant_id)

        # Audit log
        if self._audit_repo is not None:
            await self._audit_repo.log_event(
                event_type=AuditEventType.CONFIG_UPDATED,
                tenant_id=tenant_id,
                actor=actor,
                actor_type="user" if actor.startswith("user:") else "system",
                payload={
                    "action": "rollback",
                    "from_version": current_version,
                    "to_version": target_version,
                    "new_version": new_version,
                },
            )

        logger.info(
            "Config rollback: tenant=%s version=%d→%d (rollback to v%d) actor=%s",
            tenant_id[:8], current_version, new_version, target_version, actor,
        )

        return ConfigRollbackResult(
            success=True,
            from_version=current_version,
            to_version=target_version,
            new_version=new_version,
            message=f"Rolled back to version {target_version} (created as version {new_version})",
        )

    # ---- Public API: Utilities ---------------------------------------------

    async def validate_only(
        self,
        tier: TenantTier,
        changes: dict[str, Any],
    ) -> ConfigValidationResult:
        """Validate config changes without persisting.

        Useful for preview/dry-run before committing changes.

        Args:
            tier: Tenant's subscription tier.
            changes: Proposed field changes.

        Returns:
            ConfigValidationResult with errors/warnings.
        """
        return validate_config(changes, tier)

    def get_resolved_preferences(
        self,
        tenant_id: str,
    ) -> PreferencesDocument | None:
        """Get the cached resolved config as a PreferencesDocument.

        Used by the SystemPromptBuilder to get the resolved config
        without a database round-trip. Returns None if not cached.

        Args:
            tenant_id: Tenant identifier.

        Returns:
            PreferencesDocument if cached and not expired, else None.
        """
        cached = self._get_cached(tenant_id)
        if cached is None:
            return None

        return _config_to_preferences(
            tenant_id=tenant_id,
            config=cached.resolved,
            version=cached.version,
        )

    # ---- Cache management --------------------------------------------------

    def _get_cached(self, tenant_id: str) -> _CacheEntry | None:
        """Get cached config if present and not expired."""
        entry = self._cache.get(tenant_id)
        if entry is None:
            return None
        if time.monotonic() > entry.expires_at:
            del self._cache[tenant_id]
            return None
        return entry

    def _set_cache(
        self,
        tenant_id: str,
        resolved: dict[str, Any],
        version: int,
        tier: TenantTier,
    ) -> None:
        """Cache a resolved config with TTL."""
        self._cache[tenant_id] = _CacheEntry(
            resolved=resolved,
            version=version,
            tier=tier,
            expires_at=time.monotonic() + CACHE_TTL_SECONDS,
        )

    def _invalidate_cache(self, tenant_id: str) -> None:
        """Remove a tenant's cached config."""
        self._cache.pop(tenant_id, None)

    def invalidate_all(self) -> None:
        """Clear the entire config cache.

        Useful during testing or after bulk config changes.
        """
        self._cache.clear()

    @property
    def cache_size(self) -> int:
        """Number of entries currently in the cache."""
        return len(self._cache)

    # ---- Internal: config resolution ---------------------------------------

    async def _resolve_config(
        self,
        tenant_id: str,
        tier: TenantTier,
    ) -> tuple[dict[str, Any], int]:
        """Resolve the full config for a tenant.

        Resolution order:
            1. Start with platform defaults
            2. Override with tier defaults
            3. Override with tenant's stored preferences

        Args:
            tenant_id: Tenant identifier.
            tier: Tenant's subscription tier.

        Returns:
            Tuple of (resolved_config_dict, current_version_number).
        """
        # Layer 1+2: platform + tier defaults
        resolved = resolve_defaults(tier)

        # Layer 3: tenant overrides from Cosmos DB
        version = 0
        if self._is_configured:
            try:
                current = await self._prefs_repo.get_current(tenant_id)
            except Exception as exc:
                logger.warning(
                    "Failed to read preferences for tenant=%s from Cosmos DB "
                    "(returning tier defaults): %s",
                    tenant_id[:8], exc,
                )
                current = None

            if current is not None:
                version = current.get("version", 0)
                stored = _preferences_to_config(current)
                resolved.update(stored)
            else:
                logger.debug(
                    "No preferences document found for tenant=%s — "
                    "returning tier defaults only (version=0)",
                    tenant_id[:8],
                )
        else:
            logger.warning(
                "TenantConfigProcessor not configured — returning tier "
                "defaults only for tenant=%s. Config persistence is unavailable.",
                tenant_id[:8],
            )

        return resolved, version

    # ---- Internal: audit logging -------------------------------------------

    async def _log_config_change(
        self,
        tenant_id: str,
        actor: str,
        from_version: int,
        to_version: int,
        changes: dict[str, Any],
        reset: bool = False,
    ) -> None:
        """Log a config change to the audit log."""
        if self._audit_repo is None:
            return

        # Scrub potentially sensitive values from the audit payload
        scrubbed_changes: dict[str, Any] = {}
        registry = get_field_registry()
        for field_name, change in changes.items():
            field_def = registry.get(field_name)
            if field_def and field_def.pii_classification != "none":
                scrubbed_changes[field_name] = {"changed": True, "pii_scrubbed": True}
            else:
                scrubbed_changes[field_name] = change

        await self._audit_repo.log_event(
            event_type=AuditEventType.CONFIG_UPDATED,
            tenant_id=tenant_id,
            actor=actor,
            actor_type="user" if actor.startswith("user:") else "system",
            payload={
                "action": "reset_to_defaults" if reset else "update",
                "from_version": from_version,
                "to_version": to_version,
                "fields_changed": list(changes.keys()),
                "change_count": len(changes),
                "changes": scrubbed_changes,
            },
        )


# ---------------------------------------------------------------------------
# Module-level singleton
# ---------------------------------------------------------------------------

_processor: TenantConfigProcessor | None = None


def get_config_processor() -> TenantConfigProcessor:
    """Return the module-level TenantConfigProcessor singleton."""
    global _processor  # noqa: PLW0603
    if _processor is None:
        _processor = TenantConfigProcessor()
        logger.info("TenantConfigProcessor initialised (not yet configured)")
    return _processor
