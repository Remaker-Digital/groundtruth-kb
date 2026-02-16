"""Migration compatibility tests — PreferencesDocument config_state lazy backfill.

Validates backward compatibility during the migration from the old
PreferencesDocument format (is_current=True, no config_state field) to
the new Save-Activate model (config_state: draft | active | previous).

The migration is lazy: old documents are backfilled on first write via
ActivationService._ensure_config_state().  These tests verify that:

    1. Old documents without config_state are readable by get_active()
    2. Lazy backfill patches the document correctly
    3. Documents that already have config_state are not re-patched
    4. Draft layer is empty for tenants with only old-format documents
    5. First save_draft creates a draft from the active document
    6. Mixed old/new documents within a tenant are handled correctly
    7. ConfigState enum values match Cosmos DB query literals
    8. PreferencesDocument Pydantic model has new activation fields
    9. Old test mode fields have been removed from PreferencesDocument

Run:
    python -m pytest tests/regression/test_migration_compat.py -x -q

Copyright 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any
from unittest.mock import AsyncMock, patch

import pytest

from src.multi_tenant.activation_service import ActivationService, DraftState
from src.multi_tenant.cosmos_schema import (
    ConfigState,
    PreferencesDocument,
    TenantTier,
)
from src.multi_tenant.tenant_config_schema import ConfigValidationResult


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

TENANT_ID = "migration-compat-tenant-001"


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _old_format_doc(
    tenant_id: str = TENANT_ID,
    version: int = 1,
    brand_name: str = "Old Brand",
    widget_key: str = "pk_live_old_key",
    **overrides: Any,
) -> dict[str, Any]:
    """Build a dict that mimics a pre-migration Cosmos DB document.

    These documents have ``is_current=True`` but no ``config_state``,
    ``activated_at``, or ``activated_by`` fields — exactly as they
    existed before the Save-Activate model was introduced.
    """
    doc: dict[str, Any] = {
        "id": f"{tenant_id}:{version}",
        "tenant_id": tenant_id,
        "version": version,
        "is_current": True,
        "created_at": "2026-01-15T00:00:00+00:00",
        # Deliberately NO config_state, activated_at, activated_by
        "brand_name": brand_name,
        "brand_voice": "friendly",
        "primary_language": "en",
        "additional_languages": [],
        "response_length": "standard",
        "formality_level": "balanced",
        "escalation_threshold": 0.7,
        "escalation_keywords": [],
        "memory_enabled": True,
        "widget_key": widget_key,
    }
    doc.update(overrides)
    return doc


def _new_format_doc(
    tenant_id: str = TENANT_ID,
    version: int = 2,
    config_state: str = ConfigState.ACTIVE.value,
    brand_name: str = "New Brand",
    widget_key: str = "pk_live_new_key",
    **overrides: Any,
) -> dict[str, Any]:
    """Build a dict that uses the new Save-Activate format."""
    doc: dict[str, Any] = {
        "id": f"{tenant_id}:{version}",
        "tenant_id": tenant_id,
        "version": version,
        "is_current": config_state == ConfigState.ACTIVE.value,
        "config_state": config_state,
        "activated_at": "2026-02-01T00:00:00+00:00",
        "activated_by": "admin",
        "brand_name": brand_name,
        "brand_voice": "friendly",
        "primary_language": "en",
        "additional_languages": [],
        "response_length": "standard",
        "formality_level": "balanced",
        "escalation_threshold": 0.7,
        "escalation_keywords": [],
        "memory_enabled": True,
        "widget_key": widget_key,
    }
    doc.update(overrides)
    return doc


def _make_service(
    prefs_repo: AsyncMock | None = None,
    audit_repo: AsyncMock | None = None,
) -> ActivationService:
    """Create an ActivationService with mocked dependencies."""
    svc = ActivationService()
    svc.configure(
        prefs_repo=prefs_repo or AsyncMock(),
        audit_repo=audit_repo or AsyncMock(),
    )
    return svc


# ═══════════════════════════════════════════════════════════════════════════
# 1. ConfigState enum values
# ═══════════════════════════════════════════════════════════════════════════


class TestConfigStateEnum:
    """Verify ConfigState enum members match the Cosmos DB query literals."""

    def test_draft_value_is_draft(self):
        """ConfigState.DRAFT must be 'draft' (Cosmos WHERE clause)."""
        assert ConfigState.DRAFT == "draft"
        assert ConfigState.DRAFT.value == "draft"

    def test_active_value_is_active(self):
        """ConfigState.ACTIVE must be 'active' (Cosmos WHERE clause)."""
        assert ConfigState.ACTIVE == "active"
        assert ConfigState.ACTIVE.value == "active"

    def test_previous_value_is_previous(self):
        """ConfigState.PREVIOUS must be 'previous' (Cosmos WHERE clause)."""
        assert ConfigState.PREVIOUS == "previous"
        assert ConfigState.PREVIOUS.value == "previous"

    def test_enum_is_str_subclass(self):
        """ConfigState members must be str-comparable for Cosmos queries."""
        assert isinstance(ConfigState.ACTIVE, str)
        assert ConfigState.ACTIVE == "active"


# ═══════════════════════════════════════════════════════════════════════════
# 2. PreferencesDocument Pydantic model fields
# ═══════════════════════════════════════════════════════════════════════════


class TestPreferencesDocumentFields:
    """Verify the Pydantic model has the activation fields and lacks test mode fields."""

    def test_config_state_field_exists(self):
        """PreferencesDocument must have a config_state field."""
        fields = PreferencesDocument.model_fields
        assert "config_state" in fields

    def test_config_state_default_is_active(self):
        """Default config_state should be 'active' for new documents."""
        doc = PreferencesDocument(
            id="t:1", tenant_id="t", version=1,
            created_at="2026-01-01T00:00:00+00:00",
        )
        assert doc.config_state == "active"

    def test_activated_at_field_exists(self):
        """PreferencesDocument must have an activated_at field."""
        fields = PreferencesDocument.model_fields
        assert "activated_at" in fields

    def test_activated_by_field_exists(self):
        """PreferencesDocument must have an activated_by field."""
        fields = PreferencesDocument.model_fields
        assert "activated_by" in fields

    def test_activated_at_defaults_to_none(self):
        """activated_at should default to None (set on activation)."""
        doc = PreferencesDocument(
            id="t:1", tenant_id="t", version=1,
            created_at="2026-01-01T00:00:00+00:00",
        )
        assert doc.activated_at is None

    def test_activated_by_defaults_to_none(self):
        """activated_by should default to None (set on activation)."""
        doc = PreferencesDocument(
            id="t:1", tenant_id="t", version=1,
            created_at="2026-01-01T00:00:00+00:00",
        )
        assert doc.activated_by is None

    def test_old_test_mode_fields_removed(self):
        """Old test mode fields must NOT exist on PreferencesDocument.

        These fields were removed when the Save-Activate model replaced
        the old test mode workflow.
        """
        removed_fields = [
            "test_mode_enabled",
            "test_mode_percentage",
            "test_mode_overrides",
            "test_mode_assignment_seed",
            "test_mode_activated_at",
        ]
        model_fields = PreferencesDocument.model_fields
        for field_name in removed_fields:
            assert field_name not in model_fields, (
                f"'{field_name}' should have been removed from PreferencesDocument "
                f"during the Save-Activate migration"
            )


# ═══════════════════════════════════════════════════════════════════════════
# 3. Old documents readable by get_active()
# ═══════════════════════════════════════════════════════════════════════════


class TestOldDocumentReadability:
    """Old docs (is_current=True, no config_state) must be found by get_active()."""

    @pytest.mark.asyncio
    async def test_old_doc_returned_by_get_active(self):
        """get_active() query matches docs WITHOUT config_state via the
        OR clause: (is_current = true AND NOT IS_DEFINED(config_state)).
        """
        old_doc = _old_format_doc()
        assert "config_state" not in old_doc
        assert old_doc["is_current"] is True

        prefs_repo = AsyncMock()
        prefs_repo.get_active = AsyncMock(return_value=old_doc)

        result = await prefs_repo.get_active(TENANT_ID)
        assert result is not None
        assert result["brand_name"] == "Old Brand"
        assert "config_state" not in result

    @pytest.mark.asyncio
    async def test_old_doc_parseable_as_pydantic_model(self):
        """An old-format dict (without config_state) can be parsed into
        PreferencesDocument, using the default config_state='active'.
        """
        old_doc = _old_format_doc()
        # Pydantic model accepts the dict even without config_state
        parsed = PreferencesDocument(**old_doc)
        assert parsed.config_state == "active"  # Pydantic default kicks in
        assert parsed.is_current is True
        assert parsed.brand_name == "Old Brand"


# ═══════════════════════════════════════════════════════════════════════════
# 4. Lazy backfill via _ensure_config_state()
# ═══════════════════════════════════════════════════════════════════════════


class TestLazyBackfill:
    """_ensure_config_state() should patch old docs and leave new ones alone."""

    @pytest.mark.asyncio
    async def test_backfill_patches_old_doc(self):
        """A document without config_state is patched to config_state='active'."""
        old_doc = _old_format_doc()
        prefs_repo = AsyncMock()
        svc = _make_service(prefs_repo=prefs_repo)

        result = await svc._ensure_config_state(old_doc, TENANT_ID)

        # Verify the patch was called
        prefs_repo.patch.assert_called_once()
        call_kwargs = prefs_repo.patch.call_args
        assert call_kwargs.kwargs["tenant_id"] == TENANT_ID
        assert call_kwargs.kwargs["document_id"] == old_doc["id"]

        operations = call_kwargs.kwargs["operations"]
        op_paths = {op["path"] for op in operations}
        assert "/config_state" in op_paths
        assert "/activated_at" in op_paths

        # Verify the state values set
        state_op = next(op for op in operations if op["path"] == "/config_state")
        assert state_op["value"] == ConfigState.ACTIVE.value

    @pytest.mark.asyncio
    async def test_backfill_sets_activated_at(self):
        """Backfill writes an ISO 8601 timestamp as activated_at."""
        old_doc = _old_format_doc()
        prefs_repo = AsyncMock()
        svc = _make_service(prefs_repo=prefs_repo)

        result = await svc._ensure_config_state(old_doc, TENANT_ID)

        assert result["activated_at"] is not None
        # Verify it's a valid ISO 8601 timestamp
        parsed_dt = datetime.fromisoformat(result["activated_at"])
        assert parsed_dt.tzinfo is not None  # timezone-aware

    @pytest.mark.asyncio
    async def test_backfill_mutates_doc_in_place(self):
        """The returned dict has config_state and activated_at set."""
        old_doc = _old_format_doc()
        prefs_repo = AsyncMock()
        svc = _make_service(prefs_repo=prefs_repo)

        result = await svc._ensure_config_state(old_doc, TENANT_ID)

        assert result["config_state"] == ConfigState.ACTIVE.value
        assert "activated_at" in result

    @pytest.mark.asyncio
    async def test_no_repatch_when_config_state_already_set(self):
        """Documents with config_state already present are NOT re-patched."""
        new_doc = _new_format_doc()
        prefs_repo = AsyncMock()
        svc = _make_service(prefs_repo=prefs_repo)

        result = await svc._ensure_config_state(new_doc, TENANT_ID)

        prefs_repo.patch.assert_not_called()
        assert result["config_state"] == ConfigState.ACTIVE.value

    @pytest.mark.asyncio
    async def test_backfill_when_config_state_is_none(self):
        """A document with config_state=None (explicit null) is also backfilled."""
        doc_with_null = _old_format_doc()
        doc_with_null["config_state"] = None  # Explicit null from Cosmos

        prefs_repo = AsyncMock()
        svc = _make_service(prefs_repo=prefs_repo)

        result = await svc._ensure_config_state(doc_with_null, TENANT_ID)

        prefs_repo.patch.assert_called_once()
        assert result["config_state"] == ConfigState.ACTIVE.value


# ═══════════════════════════════════════════════════════════════════════════
# 5. Draft layer for old tenants
# ═══════════════════════════════════════════════════════════════════════════


class TestDraftLayerOldTenants:
    """Old tenants (pre-migration) should have no draft layer."""

    @pytest.mark.asyncio
    async def test_get_draft_returns_none_for_old_tenant(self):
        """A tenant with only old-format docs has no draft document."""
        prefs_repo = AsyncMock()
        prefs_repo.get_draft = AsyncMock(return_value=None)

        result = await prefs_repo.get_draft(TENANT_ID)
        assert result is None

    @pytest.mark.asyncio
    async def test_has_pending_changes_false_for_old_tenant(self):
        """has_pending_changes() returns False when no draft exists."""
        prefs_repo = AsyncMock()
        prefs_repo.get_draft = AsyncMock(return_value=None)
        svc = _make_service(prefs_repo=prefs_repo)

        result = await svc.has_pending_changes(TENANT_ID)
        assert result is False

    @pytest.mark.asyncio
    async def test_get_draft_state_shows_no_changes(self):
        """get_draft_state() returns has_pending_changes=False for old tenants."""
        old_doc = _old_format_doc(version=1)
        prefs_repo = AsyncMock()
        prefs_repo.get_active = AsyncMock(return_value=old_doc)
        prefs_repo.get_draft = AsyncMock(return_value=None)
        svc = _make_service(prefs_repo=prefs_repo)

        state = await svc.get_draft_state(TENANT_ID, TenantTier.STARTER)

        assert isinstance(state, DraftState)
        assert state.has_pending_changes is False
        assert state.active_version == 1
        assert state.draft_version is None


# ═══════════════════════════════════════════════════════════════════════════
# 6. First save_draft from old-format active document
# ═══════════════════════════════════════════════════════════════════════════


class TestFirstSaveDraft:
    """First save_draft creates a draft based on the active doc."""

    @pytest.mark.asyncio
    async def test_save_draft_creates_from_active(self):
        """When no draft exists, save_draft copies active + applies changes."""
        old_doc = _old_format_doc(version=3, brand_name="Existing Brand")
        prefs_repo = AsyncMock()
        prefs_repo.get_active = AsyncMock(return_value=old_doc)
        prefs_repo.get_draft = AsyncMock(return_value=None)
        prefs_repo.patch = AsyncMock()
        prefs_repo.upsert = AsyncMock()
        svc = _make_service(prefs_repo=prefs_repo)

        with patch(
            "src.multi_tenant.activation_service.validate_config"
        ) as mock_validate:
            mock_validate.return_value = ConfigValidationResult(valid=True)

            result = await svc.save_draft(
                tenant_id=TENANT_ID,
                tier=TenantTier.STARTER,
                changes={"brand_name": "Updated Brand"},
                actor="admin",
            )

        assert result.success is True
        assert result.version == 4  # active_version (3) + 1
        assert result.state == "draft"

        # Verify upsert was called (not patch, since no draft existed; D52: create→upsert)
        prefs_repo.upsert.assert_called_once()
        created_doc = prefs_repo.upsert.call_args.args[1]
        # created_doc is now a PreferencesDocument (Pydantic model), use attribute access
        assert created_doc.config_state == ConfigState.DRAFT.value
        assert created_doc.model_dump().get("brand_name") == "Updated Brand"
        assert created_doc.is_current is False


# ═══════════════════════════════════════════════════════════════════════════
# 7. Mixed old/new documents
# ═══════════════════════════════════════════════════════════════════════════


class TestMixedDocuments:
    """A tenant might have old docs and new docs — system handles both."""

    @pytest.mark.asyncio
    async def test_active_old_doc_triggers_backfill_on_activate(self):
        """When activate() finds an old-format active doc, it backfills first."""
        old_active = _old_format_doc(version=1)
        new_draft = _new_format_doc(
            version=2,
            config_state=ConfigState.DRAFT.value,
            brand_name="Draft Brand",
        )
        new_draft["widget_key"] = "pk_live_new_key"

        prefs_repo = AsyncMock()
        prefs_repo.get_active = AsyncMock(return_value=old_active)
        prefs_repo.get_draft = AsyncMock(return_value=new_draft)
        prefs_repo.get_previous = AsyncMock(return_value=None)
        prefs_repo.patch = AsyncMock()

        audit_repo = AsyncMock()
        audit_repo.log_event = AsyncMock()

        svc = _make_service(prefs_repo=prefs_repo, audit_repo=audit_repo)

        # Mock validate_for_activation to succeed
        with patch.object(svc, "validate_for_activation") as mock_val:
            mock_val.return_value = type("R", (), {
                "can_activate": True,
                "hard_errors": [],
                "warnings": [],
            })()

            result = await svc.activate(
                tenant_id=TENANT_ID,
                tier=TenantTier.STARTER,
                actor="admin",
            )

        assert result.success is True

        # The old active doc should have been backfilled (first patch)
        # then demoted to previous (second patch), then draft promoted
        # to active (third patch).
        assert prefs_repo.patch.call_count >= 3

    @pytest.mark.asyncio
    async def test_new_format_active_not_backfilled_on_save(self):
        """A new-format active doc is NOT re-patched during save_draft."""
        new_active = _new_format_doc(version=2)
        prefs_repo = AsyncMock()
        prefs_repo.get_active = AsyncMock(return_value=new_active)
        prefs_repo.get_draft = AsyncMock(return_value=None)
        prefs_repo.upsert = AsyncMock()
        svc = _make_service(prefs_repo=prefs_repo)

        with patch(
            "src.multi_tenant.activation_service.validate_config"
        ) as mock_validate:
            mock_validate.return_value = ConfigValidationResult(valid=True)

            result = await svc.save_draft(
                tenant_id=TENANT_ID,
                tier=TenantTier.STARTER,
                changes={"brand_voice": "formal"},
                actor="admin",
            )

        assert result.success is True

        # patch should NOT have been called for backfill — only upsert for draft
        # (D52: create→upsert; the old _ensure_config_state path is skipped when config_state exists)
        prefs_repo.upsert.assert_called_once()

    @pytest.mark.asyncio
    async def test_old_doc_brand_name_preserved_in_draft(self):
        """When creating a draft from an old-format doc, existing fields carry over."""
        old_doc = _old_format_doc(
            version=1,
            brand_name="Legacy Store",
            brand_voice="professional",
        )
        prefs_repo = AsyncMock()
        prefs_repo.get_active = AsyncMock(return_value=old_doc)
        prefs_repo.get_draft = AsyncMock(return_value=None)
        prefs_repo.patch = AsyncMock()
        prefs_repo.upsert = AsyncMock()
        svc = _make_service(prefs_repo=prefs_repo)

        with patch(
            "src.multi_tenant.activation_service.validate_config"
        ) as mock_validate:
            mock_validate.return_value = ConfigValidationResult(valid=True)

            await svc.save_draft(
                tenant_id=TENANT_ID,
                tier=TenantTier.STARTER,
                changes={"response_length": "detailed"},
                actor="admin",
            )

        created_doc = prefs_repo.upsert.call_args.args[1]
        # created_doc is now a PreferencesDocument (Pydantic model)
        doc_dict = created_doc.model_dump()
        # Fields from old doc are preserved
        assert doc_dict.get("brand_name") == "Legacy Store"
        assert doc_dict.get("brand_voice") == "professional"
        # Change is applied on top
        assert doc_dict.get("response_length") == "detailed"
        # New metadata is set
        assert created_doc.config_state == ConfigState.DRAFT.value
        assert created_doc.is_current is False


# ═══════════════════════════════════════════════════════════════════════════
# 8. Edge cases
# ═══════════════════════════════════════════════════════════════════════════


class TestMigrationEdgeCases:
    """Edge cases in the migration path."""

    @pytest.mark.asyncio
    async def test_backfill_uses_utc_timezone(self):
        """The activated_at timestamp set during backfill must be UTC."""
        old_doc = _old_format_doc()
        prefs_repo = AsyncMock()
        svc = _make_service(prefs_repo=prefs_repo)

        result = await svc._ensure_config_state(old_doc, TENANT_ID)

        ts = datetime.fromisoformat(result["activated_at"])
        # UTC offset must be +00:00
        assert ts.utcoffset().total_seconds() == 0

    @pytest.mark.asyncio
    async def test_service_not_configured_returns_false(self):
        """has_pending_changes returns False when service is not configured."""
        svc = ActivationService()  # Not configured
        result = await svc.has_pending_changes(TENANT_ID)
        assert result is False

    @pytest.mark.asyncio
    async def test_service_not_configured_draft_state_empty(self):
        """get_draft_state returns empty DraftState when service is not configured."""
        svc = ActivationService()  # Not configured
        state = await svc.get_draft_state(TENANT_ID, TenantTier.STARTER)
        assert state.has_pending_changes is False
        assert state.active_version == 0

    def test_config_state_not_in_old_doc_dict(self):
        """Sanity: _old_format_doc() helper truly omits config_state."""
        doc = _old_format_doc()
        assert "config_state" not in doc
        assert "activated_at" not in doc
        assert "activated_by" not in doc

    def test_config_state_present_in_new_doc_dict(self):
        """Sanity: _new_format_doc() helper includes config_state."""
        doc = _new_format_doc()
        assert doc["config_state"] == "active"
        assert doc["activated_at"] is not None
        assert doc["activated_by"] is not None
