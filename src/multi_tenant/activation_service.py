"""ActivationService — Save → Activate configuration lifecycle manager.

Replaces the wizard (OnboardingWizard) and test mode (TestModeService) with
a two-phase commit model for tenant configuration:

    1. DRAFT   — admin saves changes; chat pipeline is unaffected
    2. ACTIVE  — merchant explicitly activates; pipeline reads new config
    3. PREVIOUS — the prior activation snapshot (one-level undo via Restore)

All four configuration domains activate atomically:
    - Agent Configuration (brand, tone, escalation, custom instructions)
    - Quick Actions (prompts, page assignments)
    - Widget Configuration (appearance, behavior, targeting)
    - Knowledge Base (validated at activation, not snapshotted)

Lifecycle:
    save_draft(changes)        → persist to draft
    activate()                 → validate → promote draft to active
    restore_previous()         → swap active ↔ previous
    discard_draft()            → delete draft
    reinitialize_to_defaults() → superadmin nuclear reset

Architecture:
    - Draft and active configs are both PreferencesDocument instances
      in the ``preferences`` collection, distinguished by ``config_state``
    - The chat pipeline always reads ``config_state='active'`` via
      ``PreferencesRepository.get_active()``
    - Draft reads bypass the 60-second cache (admin-only, low frequency)
    - Activation snapshots are stored permanently for future history UI

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

from __future__ import annotations

import asyncio
import logging
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any

from src.multi_tenant.cosmos_schema import (
    AuditEventType,
    ConfigState,
    PreferencesDocument,
    TenantTier,
)
from src.multi_tenant.tenant_config_schema import (
    resolve_defaults,
    validate_config,
)

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Result types
# ---------------------------------------------------------------------------


@dataclass
class DraftSaveResult:
    """Result of a save_draft() operation."""

    success: bool
    version: int = 0
    errors: list[dict[str, str]] = field(default_factory=list)
    warnings: list[dict[str, str]] = field(default_factory=list)
    changes: dict[str, Any] = field(default_factory=dict)
    state: str = "draft"


@dataclass
class ActivationResult:
    """Result of an activate() operation."""

    success: bool
    version: int = 0
    activated_at: str | None = None
    errors: list[dict[str, str]] = field(default_factory=list)
    warnings: list[dict[str, str]] = field(default_factory=list)


@dataclass
class RestoreResult:
    """Result of a restore_previous() operation."""

    success: bool
    restored_version: int = 0
    restored_activated_at: str | None = None
    error: str | None = None


@dataclass
class DraftState:
    """Current draft state for the activation banner."""

    has_pending_changes: bool
    active_version: int = 0
    active_activated_at: str | None = None
    draft_version: int | None = None
    changed_fields: list[str] = field(default_factory=list)
    draft_config: dict[str, Any] = field(default_factory=dict)
    active_config: dict[str, Any] = field(default_factory=dict)


@dataclass
class ValidationResult:
    """Result of activation validation."""

    can_activate: bool
    hard_errors: list[dict[str, str]] = field(default_factory=list)
    warnings: list[dict[str, str]] = field(default_factory=list)


# ---------------------------------------------------------------------------
# Fields excluded from draft diff (metadata, not merchant config)
# ---------------------------------------------------------------------------

_METADATA_FIELDS = frozenset({
    "id", "tenant_id", "version", "is_current", "config_state",
    "config_name", "appearance_name", "created_at", "created_by",
    "activated_at", "activated_by", "widget_key",
})


# ---------------------------------------------------------------------------
# ActivationService
# ---------------------------------------------------------------------------


class ActivationService:
    """Manages the Save → Activate configuration lifecycle.

    Singleton service wired at application startup.
    """

    def __init__(self) -> None:
        self._prefs_repo: Any = None
        self._audit_repo: Any = None
        self._kb_repo: Any = None
        self._config_processor: Any = None
        self._tenant_repo: Any = None
        self._lock = asyncio.Lock()

    def configure(
        self,
        prefs_repo: Any,
        audit_repo: Any,
        kb_repo: Any | None = None,
        config_processor: Any | None = None,
        tenant_repo: Any | None = None,
    ) -> None:
        """Wire dependencies (called at startup)."""
        self._prefs_repo = prefs_repo
        self._audit_repo = audit_repo
        self._kb_repo = kb_repo
        self._config_processor = config_processor
        self._tenant_repo = tenant_repo
        logger.info("ActivationService configured")

    @property
    def _is_configured(self) -> bool:
        return self._prefs_repo is not None

    # ------------------------------------------------------------------
    # Lazy migration of pre-config_state documents
    # ------------------------------------------------------------------

    async def _ensure_config_state(
        self, doc: dict[str, Any], tenant_id: str,
    ) -> dict[str, Any]:
        """Backfill config_state on old documents that lack the field.

        Old documents have ``is_current=True`` but no ``config_state``.
        On first encounter, patch them to ``config_state='active'`` and
        set ``activated_at`` to now (best approximation).
        """
        if "config_state" not in doc or doc.get("config_state") is None:
            now = datetime.now(timezone.utc).isoformat()
            await self._prefs_repo.patch(
                tenant_id=tenant_id,
                document_id=doc["id"],
                operations=[
                    {"op": "set", "path": "/config_state", "value": ConfigState.ACTIVE.value},
                    {"op": "set", "path": "/activated_at", "value": now},
                ],
            )
            doc["config_state"] = ConfigState.ACTIVE.value
            doc["activated_at"] = now
            logger.info(
                "Lazy-migrated preferences document %s to config_state='active'",
                doc["id"],
            )
        return doc

    # ------------------------------------------------------------------
    # Save Draft
    # ------------------------------------------------------------------

    async def save_draft(
        self,
        tenant_id: str,
        tier: TenantTier,
        changes: dict[str, Any],
        actor: str = "admin",
    ) -> DraftSaveResult:
        """Persist configuration changes to the draft layer.

        If a draft already exists, merges changes into it.
        If no draft exists, creates one by copying the active config
        and applying changes on top.

        Args:
            tenant_id: Tenant partition key.
            tier: Subscription tier (for validation and defaults).
            changes: Partial config dict (only changed fields).
            actor: Who made the change (for audit).

        Returns:
            DraftSaveResult with validation status and draft state.
        """
        if not self._is_configured:
            return DraftSaveResult(
                success=False,
                errors=[{"field": "_system", "message": "Service not configured"}],
            )

        # Validate the incoming changes
        validation = validate_config(changes, tier)
        if validation.errors:
            return DraftSaveResult(
                success=False,
                errors=validation.errors,
                warnings=validation.warnings,
            )

        try:
            async with self._lock:
                # Get the active config (with lazy migration)
                active = await self._prefs_repo.get_active(tenant_id)
                if active:
                    active = await self._ensure_config_state(active, tenant_id)

                # Get existing draft (if any)
                draft = await self._prefs_repo.get_draft(tenant_id)

                if draft is not None:
                    # Merge changes into existing draft
                    for key, value in changes.items():
                        draft[key] = value

                    # Patch the existing draft document
                    operations = [
                        {"op": "set", "path": f"/{key}", "value": value}
                        for key, value in changes.items()
                    ]
                    await self._prefs_repo.patch(
                        tenant_id=tenant_id,
                        document_id=draft["id"],
                        operations=operations,
                    )

                    logger.info(
                        "Updated draft for tenant=%s: %d fields changed",
                        tenant_id[:8], len(changes),
                    )

                    return DraftSaveResult(
                        success=True,
                        version=draft.get("version", 0),
                        changes=changes,
                        warnings=validation.warnings,
                        state="draft",
                    )
                else:
                    # Create new draft from active config + changes
                    # Seed with tier defaults so fresh tenants get complete config
                    base_config: dict[str, Any] = dict(resolve_defaults(tier))
                    active_version = 0

                    if active:
                        active_version = active.get("version", 0)
                        # Copy all PreferencesDocument fields from active
                        # (overrides tier defaults with tenant's actual values)
                        for key, value in active.items():
                            if key not in ("id", "_rid", "_self", "_etag", "_attachments", "_ts"):
                                base_config[key] = value

                    # Apply changes on top
                    for key, value in changes.items():
                        base_config[key] = value

                    # Create draft document
                    draft_version = active_version + 1
                    now = datetime.now(timezone.utc).isoformat()

                    base_config.update({
                        "id": f"{tenant_id}:{draft_version}",
                        "tenant_id": tenant_id,
                        "version": draft_version,
                        "is_current": False,
                        "config_state": ConfigState.DRAFT.value,
                        "created_at": now,
                        "created_by": actor,
                        "activated_at": None,
                        "activated_by": None,
                    })

                    await self._prefs_repo.upsert(
                        tenant_id, PreferencesDocument(**base_config),
                    )

                    logger.info(
                        "Created draft v%d for tenant=%s from active v%d with %d changes",
                        draft_version, tenant_id[:8], active_version, len(changes),
                    )

                    return DraftSaveResult(
                        success=True,
                        version=draft_version,
                        changes=changes,
                        warnings=validation.warnings,
                        state="draft",
                    )
        except Exception as exc:
            logger.error(
                "Failed to save draft for tenant=%s: %s",
                tenant_id[:8], exc, exc_info=True,
            )
            return DraftSaveResult(
                success=False,
                errors=[{"field": "_system", "message": f"Failed to save configuration: {exc}"}],
            )

    # ------------------------------------------------------------------
    # Ensure Draft for Signal (KB/QA pending-change notification)
    # ------------------------------------------------------------------

    async def ensure_draft_for_signal(
        self,
        tenant_id: str,
        tier: TenantTier,
        signal_field: str,
        actor: str = "admin",
    ) -> DraftSaveResult:
        """Ensure a draft exists and set a lightweight signal field.

        Used by KB and QA APIs to signal "pending changes" to the
        activation system without going through full config validation
        (since signal fields are not in the config schema registry).

        The signal field (e.g. ``kb_modified_at``, ``qa_modified_at``)
        is set to the current ISO timestamp.  Because it is not in
        ``_METADATA_FIELDS`` and does not start with ``_``, it will
        appear in the ``changed_fields`` diff returned by
        ``get_draft_state()``.

        Args:
            tenant_id: Tenant partition key.
            tier: Subscription tier.
            signal_field: Name of the signal field to set.
            actor: Who made the change (for audit).

        Returns:
            DraftSaveResult with success status.
        """
        if not self._is_configured:
            return DraftSaveResult(
                success=False,
                errors=[{"field": "_system", "message": "Service not configured"}],
            )

        now = datetime.now(timezone.utc).isoformat()

        try:
            async with self._lock:
                active = await self._prefs_repo.get_active(tenant_id)
                if active:
                    active = await self._ensure_config_state(active, tenant_id)

                draft = await self._prefs_repo.get_draft(tenant_id)

                if draft is not None:
                    # Draft exists — update the signal field
                    await self._prefs_repo.patch(
                        tenant_id=tenant_id,
                        document_id=draft["id"],
                        operations=[
                            {"op": "set", "path": f"/{signal_field}", "value": now},
                        ],
                    )
                    logger.info(
                        "Updated %s signal on draft v%d for tenant=%s",
                        signal_field, draft.get("version", 0), tenant_id[:8],
                    )
                    return DraftSaveResult(
                        success=True,
                        version=draft.get("version", 0),
                        changes={signal_field: now},
                        state="draft",
                    )
                else:
                    # No draft — create one from active + signal
                    base_config: dict[str, Any] = {}
                    active_version = 0

                    if active:
                        active_version = active.get("version", 0)
                        for key, value in active.items():
                            if key not in ("id", "_rid", "_self", "_etag", "_attachments", "_ts"):
                                base_config[key] = value

                    base_config[signal_field] = now

                    draft_version = active_version + 1
                    base_config.update({
                        "id": f"{tenant_id}:{draft_version}",
                        "tenant_id": tenant_id,
                        "version": draft_version,
                        "is_current": False,
                        "config_state": ConfigState.DRAFT.value,
                        "created_at": now,
                        "created_by": actor,
                        "activated_at": None,
                        "activated_by": None,
                    })

                    await self._prefs_repo.upsert(
                        tenant_id, PreferencesDocument(**base_config),
                    )

                    logger.info(
                        "Created draft v%d for tenant=%s via %s signal",
                        draft_version, tenant_id[:8], signal_field,
                    )

                    return DraftSaveResult(
                        success=True,
                        version=draft_version,
                        changes={signal_field: now},
                        state="draft",
                    )
        except Exception as exc:
            logger.error(
                "Failed to create signal draft for tenant=%s: %s",
                tenant_id[:8], exc, exc_info=True,
            )
            return DraftSaveResult(
                success=False,
                errors=[{"field": "_system", "message": f"Failed to signal draft: {exc}"}],
            )

    # ------------------------------------------------------------------
    # Draft State (for activation banner)
    # ------------------------------------------------------------------

    async def get_draft_state(
        self, tenant_id: str, tier: TenantTier,
    ) -> DraftState:
        """Return the current draft state for the activation banner.

        Includes the diff between draft and active configs.
        """
        if not self._is_configured:
            return DraftState(has_pending_changes=False)

        active = await self._prefs_repo.get_active(tenant_id)
        draft = await self._prefs_repo.get_draft(tenant_id)

        if draft is None:
            return DraftState(
                has_pending_changes=False,
                active_version=active.get("version", 0) if active else 0,
                active_activated_at=active.get("activated_at") if active else None,
            )

        # Compute changed fields (draft vs active)
        changed_fields: list[str] = []
        active_config = active or {}
        for key in draft:
            if key in _METADATA_FIELDS:
                continue
            if key.startswith("_"):
                continue
            if draft.get(key) != active_config.get(key):
                changed_fields.append(key)

        return DraftState(
            has_pending_changes=True,
            active_version=active.get("version", 0) if active else 0,
            active_activated_at=active.get("activated_at") if active else None,
            draft_version=draft.get("version", 0),
            changed_fields=changed_fields,
            draft_config={k: draft.get(k) for k in changed_fields},
            active_config={k: active_config.get(k) for k in changed_fields},
        )

    async def has_pending_changes(self, tenant_id: str) -> bool:
        """Lightweight check: does a draft exist for this tenant?"""
        if not self._is_configured:
            return False
        draft = await self._prefs_repo.get_draft(tenant_id)
        return draft is not None

    # ------------------------------------------------------------------
    # Validate for Activation
    # ------------------------------------------------------------------

    async def validate_for_activation(
        self, tenant_id: str, tier: TenantTier,
    ) -> ValidationResult:
        """Run activation validation rules.

        Hard blocks (activation fails):
            - brand_name is non-empty
            - brand_voice is non-empty
            - widget_key exists

        Warnings (activation proceeds):
            - fewer than 1 published KB article
        """
        draft = await self._prefs_repo.get_draft(tenant_id)
        if draft is None:
            # No draft — check if this is a re-activation of a deactivated
            # config (active doc with deactivated_at set).
            active = await self._prefs_repo.get_active(tenant_id)
            if active and active.get("deactivated_at"):
                # Re-activation: validate the active config instead.
                draft = active
            else:
                return ValidationResult(
                    can_activate=False,
                    hard_errors=[{"field": "_system", "message": "No draft to activate"}],
                )

        hard_errors: list[dict[str, str]] = []
        warnings: list[dict[str, str]] = []

        # Hard block: brand_name
        brand_name = draft.get("brand_name")
        if not brand_name or not str(brand_name).strip():
            hard_errors.append({
                "field": "brand_name",
                "message": "Brand name is required before activation",
                "page": "agent-configuration",
            })

        # Hard block: widget_key
        widget_key = draft.get("widget_key")
        if not widget_key:
            hard_errors.append({
                "field": "widget_key",
                "message": "Widget key is missing (set during provisioning)",
                "page": "system",
            })

        # Hard block: brand_voice (mandatory — session 21)
        brand_voice = draft.get("brand_voice")
        if not brand_voice or not str(brand_voice).strip():
            hard_errors.append({
                "field": "brand_voice",
                "message": "Brand voice is required before activation",
                "page": "agent-configuration",
            })

        # Warning: KB articles
        if self._kb_repo is not None:
            try:
                articles = await self._kb_repo.query(
                    tenant_id=tenant_id,
                    query_text=(
                        "SELECT VALUE COUNT(1) FROM c "
                        "WHERE c.is_active = true"
                    ),
                    max_items=1,
                )
                kb_count = articles[0] if articles else 0
                if kb_count < 1:
                    warnings.append({
                        "field": "knowledge_base",
                        "message": "No published knowledge base articles — AI will use "
                                   "general knowledge only",
                        "page": "knowledge-base",
                    })
            except Exception:
                logger.debug("KB count check failed during validation", exc_info=True)

        return ValidationResult(
            can_activate=len(hard_errors) == 0,
            hard_errors=hard_errors,
            warnings=warnings,
        )

    # ------------------------------------------------------------------
    # Activate
    # ------------------------------------------------------------------

    async def activate(
        self,
        tenant_id: str,
        tier: TenantTier,
        actor: str = "admin",
    ) -> ActivationResult:
        """Validate and promote the draft to active.

        Transition:
            1. Validate draft
            2. Mark current 'previous' → cleared (bare version)
            3. Mark current 'active' → 'previous'
            4. Promote draft → 'active' (set activated_at, activated_by)
            5. Invalidate config cache
            6. Audit log

        Returns:
            ActivationResult with success status and any validation errors.
        """
        if not self._is_configured:
            return ActivationResult(
                success=False,
                errors=[{"field": "_system", "message": "Service not configured"}],
            )

        # Validate
        validation = await self.validate_for_activation(tenant_id, tier)
        if not validation.can_activate:
            return ActivationResult(
                success=False,
                errors=validation.hard_errors,
                warnings=validation.warnings,
            )

        try:
            async with self._lock:
                draft = await self._prefs_repo.get_draft(tenant_id)

                # Re-activation path: no draft, but active config is
                # deactivated — just clear deactivated_at.
                if draft is None:
                    active = await self._prefs_repo.get_active(tenant_id)
                    if active and active.get("deactivated_at"):
                        now = datetime.now(timezone.utc).isoformat()
                        await self._prefs_repo.patch(
                            tenant_id=tenant_id,
                            document_id=active["id"],
                            operations=[
                                {"op": "set", "path": "/deactivated_at", "value": None},
                                {"op": "set", "path": "/activated_at", "value": now},
                            ],
                        )
                        version = active.get("version", 1)
                        if self._config_processor is not None:
                            self._config_processor._invalidate_cache(tenant_id)
                        return ActivationResult(
                            success=True,
                            version=version,
                            activated_at=now,
                        )
                    return ActivationResult(
                        success=False,
                        errors=[{"field": "_system", "message": "No draft to activate"}],
                    )

                active = await self._prefs_repo.get_active(tenant_id)
                if active:
                    active = await self._ensure_config_state(active, tenant_id)

                previous = await self._prefs_repo.get_previous(tenant_id)

                now = datetime.now(timezone.utc).isoformat()

                # Step 1: Clear any existing 'previous' document
                if previous:
                    await self._prefs_repo.patch(
                        tenant_id=tenant_id,
                        document_id=previous["id"],
                        operations=[
                            {"op": "set", "path": "/config_state", "value": "archived"},
                        ],
                    )

                # Step 2: Demote current 'active' → 'previous'
                if active:
                    await self._prefs_repo.patch(
                        tenant_id=tenant_id,
                        document_id=active["id"],
                        operations=[
                            {"op": "set", "path": "/config_state", "value": ConfigState.PREVIOUS.value},
                            {"op": "set", "path": "/is_current", "value": False},
                        ],
                    )

                # Step 3: Promote draft → 'active'
                # Clear deactivated_at so widget becomes live immediately.
                await self._prefs_repo.patch(
                    tenant_id=tenant_id,
                    document_id=draft["id"],
                    operations=[
                        {"op": "set", "path": "/config_state", "value": ConfigState.ACTIVE.value},
                        {"op": "set", "path": "/is_current", "value": True},
                        {"op": "set", "path": "/activated_at", "value": now},
                        {"op": "set", "path": "/activated_by", "value": actor},
                        {"op": "set", "path": "/deactivated_at", "value": None},
                    ],
                )

                # Step 4: Invalidate config cache
                if self._config_processor is not None:
                    self._config_processor._invalidate_cache(tenant_id)

                # Step 5: Audit log
                if self._audit_repo is not None:
                    try:
                        await self._audit_repo.log_event(
                            event_type=AuditEventType.CONFIG_UPDATED,
                            tenant_id=tenant_id,
                            actor=actor,
                            actor_type="user" if actor.startswith("user:") else "system",
                            payload={
                                "action": "config_activated",
                                "draft_version": draft.get("version", 0),
                                "previous_active_version": active.get("version", 0) if active else 0,
                            },
                        )
                    except Exception:
                        logger.warning("Audit log failed for activation", exc_info=True)

                logger.info(
                    "Activated config v%d for tenant=%s (previous: v%d)",
                    draft.get("version", 0),
                    tenant_id[:8],
                    active.get("version", 0) if active else 0,
                )

                # KA-6: First-activation ingestion hook
                # If no prior active config existed, this is a first activation.
                # Dispatch a background ingestion job (awaited but isolated —
                # failures must not reverse the successful activation above).
                first_activation_warnings: list[str] = []
                if active is None:
                    try:
                        first_activation_warnings = await self._maybe_start_ingestion(
                            tenant_id
                        )
                    except Exception:
                        logger.warning(
                            "Post-activation ingestion failed for tenant=%s "
                            "(activation itself succeeded)",
                            tenant_id[:8], exc_info=True,
                        )
                        first_activation_warnings = [
                            "Storefront ingestion could not start. "
                            "You can trigger it manually from the Knowledge Base page."
                        ]

                result_warnings = list(validation.warnings or [])
                result_warnings.extend(
                    {"field": "_system", "message": w}
                    for w in first_activation_warnings
                )

                return ActivationResult(
                    success=True,
                    version=draft.get("version", 0),
                    activated_at=now,
                    warnings=result_warnings or None,
                )
        except Exception as exc:
            logger.error(
                "Failed to activate config for tenant=%s: %s",
                tenant_id[:8], exc, exc_info=True,
            )
            return ActivationResult(
                success=False,
                errors=[{"field": "_system", "message": f"Activation failed: {exc}"}],
            )

    # ------------------------------------------------------------------
    # KA-6: First-Activation Ingestion Hook
    # ------------------------------------------------------------------

    async def _maybe_start_ingestion(self, tenant_id: str) -> list[str]:
        """Dispatch background ingestion on first activation (non-blocking).

        Checks for shopify_shop_domain on the TenantDocument. If present,
        dispatches a Shopify ingestion job. Returns a list of informational
        warnings to include in the ActivationResult.
        """
        warnings: list[str] = []
        try:
            from src.multi_tenant.storefront_ingestion import get_ingestion_service

            service = get_ingestion_service()

            # Check if tenant has a Shopify domain
            tenant_doc = await self._tenant_repo.read(tenant_id, tenant_id)
            shop_domain = None
            if isinstance(tenant_doc, dict):
                shop_domain = tenant_doc.get("shopify_shop_domain")

            if shop_domain:
                # Retrieve Shopify access token: Key Vault → env var fallback
                access_token: str | None = None
                try:
                    from src.multi_tenant.tenant_secret_service import (
                        TenantSecretType,
                        get_secret_service,
                    )

                    secret_service = get_secret_service()
                    access_token = await secret_service.get_secret(
                        tenant_id, TenantSecretType.SHOPIFY_TOKEN,
                    )
                except Exception:
                    pass
                if not access_token:
                    import os

                    access_token = os.environ.get("SHOPIFY_ACCESS_TOKEN", "")
                if not access_token:
                    warnings.append(
                        "Shopify access token not available — "
                        "storefront ingestion skipped."
                    )
                    logger.warning(
                        "First-activation ingestion skipped for tenant %s: "
                        "no Shopify access token",
                        tenant_id[:8],
                    )
                else:
                    # Dispatch Shopify ingestion with valid credentials
                    await service.start_ingestion(
                        tenant_id=tenant_id,
                        source_type="shopify",
                        source_config={
                            "shop_domain": shop_domain,
                            "access_token": access_token,
                        },
                    )
                    warnings.append(
                        "Knowledge base population from Shopify storefront "
                        "is in progress. This runs in the background and "
                        "may take a few minutes."
                    )
                    logger.info(
                        "First-activation ingestion dispatched for tenant "
                        "%s (Shopify: %s)",
                        tenant_id[:8], shop_domain,
                    )
            else:
                logger.info(
                    "First activation for tenant %s — no Shopify domain, "
                    "skipping automatic ingestion",
                    tenant_id[:8],
                )

        except Exception:
            logger.warning(
                "First-activation ingestion hook failed for tenant %s (non-fatal)",
                tenant_id[:8],
                exc_info=True,
            )
        return warnings

    # ------------------------------------------------------------------
    # Restore Previous
    # ------------------------------------------------------------------

    async def restore_previous(
        self,
        tenant_id: str,
        tier: TenantTier,
        actor: str = "admin",
    ) -> RestoreResult:
        """Restore the previous activation snapshot.

        Swap: current active becomes previous, previous becomes active.
        Any existing draft is discarded.
        """
        if not self._is_configured:
            return RestoreResult(success=False, error="Service not configured")

        try:
            async with self._lock:
                active = await self._prefs_repo.get_active(tenant_id)
                previous = await self._prefs_repo.get_previous(tenant_id)

                if previous is None:
                    return RestoreResult(
                        success=False,
                        error="No previous configuration to restore",
                    )

                now = datetime.now(timezone.utc).isoformat()

                # Discard any draft first
                draft = await self._prefs_repo.get_draft(tenant_id)
                if draft:
                    await self._prefs_repo.patch(
                        tenant_id=tenant_id,
                        document_id=draft["id"],
                        operations=[
                            {"op": "set", "path": "/config_state", "value": "discarded"},
                            {"op": "set", "path": "/is_current", "value": False},
                        ],
                    )

                # Demote current active → previous
                if active:
                    await self._prefs_repo.patch(
                        tenant_id=tenant_id,
                        document_id=active["id"],
                        operations=[
                            {"op": "set", "path": "/config_state", "value": ConfigState.PREVIOUS.value},
                            {"op": "set", "path": "/is_current", "value": False},
                        ],
                    )

                # Promote previous → active
                # Clear deactivated_at so widget becomes live immediately.
                await self._prefs_repo.patch(
                    tenant_id=tenant_id,
                    document_id=previous["id"],
                    operations=[
                        {"op": "set", "path": "/config_state", "value": ConfigState.ACTIVE.value},
                        {"op": "set", "path": "/is_current", "value": True},
                        {"op": "set", "path": "/activated_at", "value": now},
                        {"op": "set", "path": "/activated_by", "value": f"restore:{actor}"},
                        {"op": "set", "path": "/deactivated_at", "value": None},
                    ],
                )

                # Invalidate cache
                if self._config_processor is not None:
                    self._config_processor._invalidate_cache(tenant_id)

                # Audit log
                if self._audit_repo is not None:
                    try:
                        await self._audit_repo.log_event(
                            event_type=AuditEventType.CONFIG_UPDATED,
                            tenant_id=tenant_id,
                            actor=actor,
                            actor_type="user",
                            payload={
                                "action": "config_restored",
                                "restored_version": previous.get("version", 0),
                                "demoted_version": active.get("version", 0) if active else 0,
                            },
                        )
                    except Exception:
                        logger.warning("Audit log failed for restore", exc_info=True)

                logger.info(
                    "Restored config v%d for tenant=%s",
                    previous.get("version", 0),
                    tenant_id[:8],
                )

                return RestoreResult(
                    success=True,
                    restored_version=previous.get("version", 0),
                    restored_activated_at=now,
                )
        except Exception as exc:
            logger.error(
                "Failed to restore config for tenant=%s: %s",
                tenant_id[:8], exc, exc_info=True,
            )
            return RestoreResult(
                success=False,
                error=f"Restore failed: {exc}",
            )

    # ------------------------------------------------------------------
    # Discard Draft
    # ------------------------------------------------------------------

    async def discard_draft(
        self,
        tenant_id: str,
        actor: str = "admin",
    ) -> bool:
        """Discard the current draft (revert to active or reset to initial).

        If an active config exists, the draft is simply removed (set to
        ``config_state='discarded'``).  The active config remains live.

        If the tenant has **never been activated** (no active document),
        the draft is reset to its initial empty state so the tenant stays
        in "Pending" rather than entering a limbo state with no documents.

        Returns True if a draft was found and handled.
        """
        if not self._is_configured:
            return False

        try:
            draft = await self._prefs_repo.get_draft(tenant_id)
            if draft is None:
                return False

            active = await self._prefs_repo.get_active(tenant_id)

            if active is not None:
                # Normal case: active config exists — discard the draft
                await self._prefs_repo.patch(
                    tenant_id=tenant_id,
                    document_id=draft["id"],
                    operations=[
                        {"op": "set", "path": "/config_state", "value": "discarded"},
                        {"op": "set", "path": "/is_current", "value": False},
                    ],
                )
                logger.info(
                    "Discarded draft v%d for tenant=%s (active exists)",
                    draft.get("version", 0),
                    tenant_id[:8],
                )
            else:
                # Never-activated tenant: reset draft to initial empty state
                # so the tenant stays in "Pending" (draft exists, mandatory
                # fields empty).  We clear user-editable fields back to
                # defaults while keeping the document structure.
                reset_ops = [
                    # Merchant-configurable fields — reset to empty
                    # (must match seed_tenant.py Phase 3 defaults)
                    {"op": "set", "path": "/brand_name", "value": ""},
                    {"op": "set", "path": "/brand_voice", "value": ""},
                    {"op": "set", "path": "/brand_tagline", "value": ""},
                    {"op": "set", "path": "/custom_instructions", "value": ""},
                    {"op": "set", "path": "/return_policy", "value": ""},
                    {"op": "set", "path": "/shipping_info", "value": ""},
                    {"op": "set", "path": "/escalation_keywords", "value": []},
                    {"op": "set", "path": "/escalation_email", "value": None},
                    {"op": "set", "path": "/greeting_message", "value": None},
                    {"op": "set", "path": "/greeting_follow_up", "value": ""},
                    {"op": "set", "path": "/farewell_message", "value": None},
                    {"op": "set", "path": "/warranty_info", "value": None},
                    {"op": "set", "path": "/support_hours", "value": None},
                    {"op": "set", "path": "/custom_policies", "value": None},
                    {"op": "set", "path": "/widget_greeting_message", "value": None},
                    # Activation metadata
                    {"op": "set", "path": "/activated_at", "value": None},
                    {"op": "set", "path": "/activated_by", "value": None},
                    # KB/QA signal fields
                    {"op": "set", "path": "/kb_modified_at", "value": None},
                    {"op": "set", "path": "/qa_modified_at", "value": None},
                ]
                await self._prefs_repo.patch(
                    tenant_id=tenant_id,
                    document_id=draft["id"],
                    operations=reset_ops,
                )
                logger.info(
                    "Reset draft to initial state for tenant=%s (never activated)",
                    tenant_id[:8],
                )

            return True
        except Exception as exc:
            logger.error(
                "Failed to discard draft for tenant=%s: %s",
                tenant_id[:8], exc, exc_info=True,
            )
            return False

    # ------------------------------------------------------------------
    # Reinitialize to Defaults (superadmin only)
    # ------------------------------------------------------------------

    async def reinitialize_to_defaults(
        self,
        tenant_id: str,
        tier: TenantTier,
        actor: str = "superadmin",
    ) -> DraftSaveResult:
        """Create a fresh draft from tier defaults.

        Superadmin-only nuclear option for support escalations.
        Discards any existing draft first.
        """
        if not self._is_configured:
            return DraftSaveResult(
                success=False,
                errors=[{"field": "_system", "message": "Service not configured"}],
            )

        # Discard existing draft
        await self.discard_draft(tenant_id, actor)

        # Get tier defaults as changes
        defaults = resolve_defaults(tier)

        # Preserve widget_key from active config (it's set during provisioning)
        active = await self._prefs_repo.get_active(tenant_id)
        if active and active.get("widget_key"):
            defaults["widget_key"] = active["widget_key"]

        return await self.save_draft(tenant_id, tier, defaults, actor)


# ---------------------------------------------------------------------------
# Module-level singleton
# ---------------------------------------------------------------------------

_service: ActivationService | None = None


def get_activation_service() -> ActivationService:
    """Return the module-level ActivationService singleton."""
    global _service  # noqa: PLW0603
    if _service is None:
        _service = ActivationService()
        logger.info("ActivationService initialised (not yet configured)")
    return _service
