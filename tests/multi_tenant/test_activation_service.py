"""Comprehensive tests for ActivationService — Save/Activate lifecycle.

Covers the two-phase commit model for tenant configuration:
    - save_draft (new draft, update draft, validation errors/warnings)
    - get_draft_state (no draft, with draft, changed fields)
    - has_pending_changes (no draft, with draft)
    - validate_for_activation (all pass, hard blocks, warnings)
    - activate (success, validation failure, no draft)
    - restore_previous (success, no previous)
    - discard_draft (success, no draft)
    - reinitialize_to_defaults (success)
    - _ensure_config_state (lazy migration, already migrated)
    - Service not configured (RuntimeError paths)

Run:
    pytest tests/multi_tenant/test_activation_service.py -v

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from src.multi_tenant.activation_service import (
    ActivationResult,
    ActivationService,
    DraftSaveResult,
    DraftState,
    RestoreResult,
    ValidationResult,
)
from src.multi_tenant.cosmos_schema import (
    AuditEventType,
    ConfigState,
    TenantTier,
)


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

STARTER_TENANT_ID = "t-starter-001"
PROFESSIONAL_TENANT_ID = "t-pro-002"
ENTERPRISE_TENANT_ID = "t-ent-003"


# ---------------------------------------------------------------------------
# Mock document factories
# ---------------------------------------------------------------------------


def _make_active_doc(
    tenant_id: str = STARTER_TENANT_ID,
    version: int = 1,
    *,
    brand_name: str = "Test Brand",
    widget_key: str = "pk_test_123",
    brand_voice: str = "friendly",
    primary_color: str = "#ff3621",
    welcome_message: str = "Hello!",
) -> dict[str, Any]:
    """Build a mock active preferences document."""
    return {
        "id": f"prefs-{tenant_id}-{version}",
        "tenant_id": tenant_id,
        "version": version,
        "config_state": ConfigState.ACTIVE.value,
        "is_current": True,
        "brand_name": brand_name,
        "widget_key": widget_key,
        "brand_voice": brand_voice,
        "primary_color": primary_color,
        "welcome_message": welcome_message,
        "activated_at": "2026-01-15T00:00:00Z",
        "activated_by": "admin",
        "created_at": "2026-01-15T00:00:00Z",
        "created_by": "admin",
    }


def _make_draft_doc(
    tenant_id: str = STARTER_TENANT_ID,
    version: int = 2,
    *,
    brand_name: str = "Test Brand",
    widget_key: str = "pk_test_123",
    brand_voice: str = "friendly",
    primary_color: str = "#0000ff",
    welcome_message: str = "Hi there!",
) -> dict[str, Any]:
    """Build a mock draft preferences document."""
    return {
        "id": f"prefs-{tenant_id}-{version}",
        "tenant_id": tenant_id,
        "version": version,
        "config_state": ConfigState.DRAFT.value,
        "is_current": False,
        "brand_name": brand_name,
        "widget_key": widget_key,
        "brand_voice": brand_voice,
        "primary_color": primary_color,
        "welcome_message": welcome_message,
        "activated_at": None,
        "activated_by": None,
        "created_at": "2026-01-20T00:00:00Z",
        "created_by": "admin",
    }


def _make_previous_doc(
    tenant_id: str = STARTER_TENANT_ID,
    version: int = 0,
) -> dict[str, Any]:
    """Build a mock previous preferences document."""
    return {
        "id": f"prefs-{tenant_id}-{version}",
        "tenant_id": tenant_id,
        "version": version,
        "config_state": ConfigState.PREVIOUS.value,
        "is_current": False,
        "brand_name": "Old Brand",
        "widget_key": "pk_test_old",
        "brand_voice": "professional",
        "primary_color": "#000000",
        "welcome_message": "Welcome",
        "activated_at": "2026-01-10T00:00:00Z",
        "activated_by": "admin",
        "created_at": "2026-01-10T00:00:00Z",
        "created_by": "admin",
    }


# ---------------------------------------------------------------------------
# Dependency mock builder
# ---------------------------------------------------------------------------


def _make_service(
    *,
    active: dict[str, Any] | None = None,
    draft: dict[str, Any] | None = None,
    previous: dict[str, Any] | None = None,
    kb_count: int = 5,
    configure: bool = True,
) -> tuple[ActivationService, AsyncMock, AsyncMock, AsyncMock, MagicMock]:
    """Build an ActivationService with mock dependencies.

    Returns:
        (service, prefs_repo, audit_repo, kb_repo, config_processor)
    """
    prefs_repo = AsyncMock()
    prefs_repo.get_active = AsyncMock(return_value=active)
    prefs_repo.get_draft = AsyncMock(return_value=draft)
    prefs_repo.get_previous = AsyncMock(return_value=previous)
    prefs_repo.create = AsyncMock(side_effect=lambda tid, doc: doc)
    prefs_repo.patch = AsyncMock(return_value=None)
    prefs_repo.delete_document = AsyncMock(return_value=None)

    audit_repo = AsyncMock()
    audit_repo.log_event = AsyncMock(return_value=None)

    kb_repo = AsyncMock()
    kb_repo.query = AsyncMock(return_value=[kb_count])

    config_processor = MagicMock()
    config_processor._invalidate_cache = MagicMock()

    service = ActivationService()
    if configure:
        service.configure(prefs_repo, audit_repo, kb_repo, config_processor)

    return service, prefs_repo, audit_repo, kb_repo, config_processor


# ---------------------------------------------------------------------------
# validate_config mock — patches the module-level import used by save_draft
# ---------------------------------------------------------------------------

_VALIDATE_CONFIG_PATH = "src.multi_tenant.activation_service.validate_config"
_RESOLVE_DEFAULTS_PATH = "src.multi_tenant.activation_service.resolve_defaults"


class _FakeValidationResult(dict):
    """Dict subclass that also supports attribute access.

    The activation service code accesses the validate_config result via
    both dict-style (``validation.get("errors")``, ``validation["errors"]``)
    and attribute-style (``validation.errors``). This helper satisfies both.
    """

    def __getattr__(self, key: str) -> Any:
        try:
            return self[key]
        except KeyError:
            raise AttributeError(key) from None


def _mock_validate_ok():
    """Return a mock validate_config that reports success."""
    mock = MagicMock()
    mock.return_value = _FakeValidationResult(
        errors=[], warnings=[], valid=True,
    )
    return mock


def _mock_validate_with_errors(errors: list[dict[str, str]]):
    """Return a mock validate_config that reports errors."""
    mock = MagicMock()
    mock.return_value = _FakeValidationResult(
        errors=errors, warnings=[], valid=False,
    )
    return mock


def _mock_validate_with_warnings(warnings: list[dict[str, str]]):
    """Return a mock validate_config that passes with warnings."""
    mock = MagicMock()
    mock.return_value = _FakeValidationResult(
        errors=[], warnings=warnings, valid=True,
    )
    return mock


# =========================================================================
# Test: Service Not Configured
# =========================================================================


class TestServiceNotConfigured:
    """Verify all methods handle the unconfigured state gracefully."""

    @pytest.mark.asyncio
    async def test_save_draft_unconfigured(self):
        """save_draft returns failure when service is not configured."""
        service = ActivationService()
        result = await service.save_draft(
            STARTER_TENANT_ID, TenantTier.STARTER, {"brand_name": "X"}, "admin",
        )
        assert isinstance(result, DraftSaveResult)
        assert result.success is False
        assert any("not configured" in e["message"].lower() for e in result.errors)

    @pytest.mark.asyncio
    async def test_get_draft_state_unconfigured(self):
        """get_draft_state returns empty state when unconfigured."""
        service = ActivationService()
        state = await service.get_draft_state(STARTER_TENANT_ID, TenantTier.STARTER)
        assert isinstance(state, DraftState)
        assert state.has_pending_changes is False

    @pytest.mark.asyncio
    async def test_has_pending_changes_unconfigured(self):
        """has_pending_changes returns False when unconfigured."""
        service = ActivationService()
        result = await service.has_pending_changes(STARTER_TENANT_ID)
        assert result is False

    @pytest.mark.asyncio
    async def test_activate_unconfigured(self):
        """activate returns failure when service is not configured."""
        service = ActivationService()
        result = await service.activate(
            STARTER_TENANT_ID, TenantTier.STARTER, "admin",
        )
        assert isinstance(result, ActivationResult)
        assert result.success is False
        assert any("not configured" in e["message"].lower() for e in result.errors)

    @pytest.mark.asyncio
    async def test_restore_previous_unconfigured(self):
        """restore_previous returns failure when unconfigured."""
        service = ActivationService()
        result = await service.restore_previous(
            STARTER_TENANT_ID, TenantTier.STARTER, "admin",
        )
        assert isinstance(result, RestoreResult)
        assert result.success is False
        assert "not configured" in result.error.lower()

    @pytest.mark.asyncio
    async def test_discard_draft_unconfigured(self):
        """discard_draft returns False when unconfigured."""
        service = ActivationService()
        result = await service.discard_draft(STARTER_TENANT_ID, "admin")
        assert result is False

    @pytest.mark.asyncio
    async def test_reinitialize_unconfigured(self):
        """reinitialize_to_defaults returns failure when unconfigured."""
        service = ActivationService()
        result = await service.reinitialize_to_defaults(
            STARTER_TENANT_ID, TenantTier.STARTER, "superadmin",
        )
        assert isinstance(result, DraftSaveResult)
        assert result.success is False


# =========================================================================
# Test: configure()
# =========================================================================


class TestConfigure:
    """Verify dependency wiring."""

    def test_configure_sets_dependencies(self):
        """configure() wires all four dependencies."""
        service = ActivationService()
        prefs = AsyncMock()
        audit = AsyncMock()
        kb = AsyncMock()
        proc = MagicMock()

        service.configure(prefs, audit, kb, proc)

        assert service._prefs_repo is prefs
        assert service._audit_repo is audit
        assert service._kb_repo is kb
        assert service._config_processor is proc
        assert service._is_configured is True

    def test_configure_optional_deps(self):
        """configure() works with only required deps (kb and processor optional)."""
        service = ActivationService()
        prefs = AsyncMock()
        audit = AsyncMock()

        service.configure(prefs, audit)

        assert service._is_configured is True
        assert service._kb_repo is None
        assert service._config_processor is None

    def test_not_configured_initially(self):
        """A fresh ActivationService is not configured."""
        service = ActivationService()
        assert service._is_configured is False


# =========================================================================
# Test: save_draft — new draft creation
# =========================================================================


class TestSaveDraftNewDraft:
    """Save draft when no existing draft exists."""

    @pytest.mark.asyncio
    async def test_creates_draft_from_active(self):
        """New draft is created by copying active config and applying changes."""
        active = _make_active_doc()
        service, prefs_repo, _, _, _ = _make_service(active=active)

        changes = {"brand_name": "Updated Brand"}

        with patch(_VALIDATE_CONFIG_PATH, _mock_validate_ok()):
            result = await service.save_draft(
                STARTER_TENANT_ID, TenantTier.STARTER, changes, "admin",
            )

        assert result.success is True
        assert result.version == 2  # active.version (1) + 1
        assert result.state == "draft"
        assert result.changes == changes

        # Verify create was called with a PreferencesDocument
        prefs_repo.create.assert_awaited_once()
        created_doc = prefs_repo.create.call_args[0][1]
        assert created_doc.config_state == ConfigState.DRAFT.value
        assert created_doc.brand_name == "Updated Brand"
        assert created_doc.is_current is False
        assert created_doc.version == 2

    @pytest.mark.asyncio
    async def test_creates_draft_without_active(self):
        """New draft is created even when no active config exists."""
        service, prefs_repo, _, _, _ = _make_service(active=None)

        changes = {"brand_name": "First Config"}

        with patch(_VALIDATE_CONFIG_PATH, _mock_validate_ok()):
            result = await service.save_draft(
                STARTER_TENANT_ID, TenantTier.STARTER, changes, "admin",
            )

        assert result.success is True
        assert result.version == 1  # 0 + 1

        created_doc = prefs_repo.create.call_args[0][1]
        assert created_doc.brand_name == "First Config"
        assert created_doc.config_state == ConfigState.DRAFT.value

    @pytest.mark.asyncio
    async def test_draft_preserves_active_fields(self):
        """Draft copies all non-Cosmos-metadata fields from active."""
        active = _make_active_doc(brand_name="Original", widget_key="pk_123")
        service, prefs_repo, _, _, _ = _make_service(active=active)

        changes = {"primary_color": "#ff0000"}

        with patch(_VALIDATE_CONFIG_PATH, _mock_validate_ok()):
            await service.save_draft(
                STARTER_TENANT_ID, TenantTier.STARTER, changes, "admin",
            )

        created_doc = prefs_repo.create.call_args[0][1]
        # Active fields should be preserved
        assert created_doc.brand_name == "Original"
        # Changed field should be updated — extra fields stored via model_extra
        doc_dict = created_doc.model_dump()
        assert doc_dict.get("primary_color") == "#ff0000"

    @pytest.mark.asyncio
    async def test_draft_id_format(self):
        """Draft document ID follows tenant_id:version format."""
        active = _make_active_doc(version=3)
        service, prefs_repo, _, _, _ = _make_service(active=active)

        with patch(_VALIDATE_CONFIG_PATH, _mock_validate_ok()):
            await service.save_draft(
                STARTER_TENANT_ID, TenantTier.STARTER, {"brand_name": "X"}, "admin",
            )

        created_doc = prefs_repo.create.call_args[0][1]
        assert created_doc.id == f"{STARTER_TENANT_ID}:4"

    @pytest.mark.asyncio
    async def test_draft_sets_metadata(self):
        """New draft sets created_at, created_by, and clears activation fields."""
        active = _make_active_doc()
        service, prefs_repo, _, _, _ = _make_service(active=active)

        with patch(_VALIDATE_CONFIG_PATH, _mock_validate_ok()):
            await service.save_draft(
                STARTER_TENANT_ID, TenantTier.STARTER,
                {"brand_name": "X"}, "user:mike",
            )

        created_doc = prefs_repo.create.call_args[0][1]
        assert created_doc.created_by == "user:mike"
        assert created_doc.activated_at is None
        assert created_doc.activated_by is None
        assert created_doc.created_at is not None


# =========================================================================
# Test: save_draft — update existing draft
# =========================================================================


class TestSaveDraftUpdateExisting:
    """Save draft when a draft already exists (merge changes)."""

    @pytest.mark.asyncio
    async def test_merges_into_existing_draft(self):
        """Changes are merged into the existing draft via patch."""
        active = _make_active_doc()
        draft = _make_draft_doc(primary_color="#0000ff")
        service, prefs_repo, _, _, _ = _make_service(active=active, draft=draft)

        changes = {"welcome_message": "New welcome!"}

        with patch(_VALIDATE_CONFIG_PATH, _mock_validate_ok()):
            result = await service.save_draft(
                STARTER_TENANT_ID, TenantTier.STARTER, changes, "admin",
            )

        assert result.success is True
        assert result.changes == changes

        # Should patch, not create
        prefs_repo.patch.assert_awaited()
        prefs_repo.create.assert_not_awaited()

    @pytest.mark.asyncio
    async def test_patch_operations_match_changes(self):
        """Patch operations contain all changed fields."""
        draft = _make_draft_doc()
        active = _make_active_doc()
        service, prefs_repo, _, _, _ = _make_service(active=active, draft=draft)

        changes = {"brand_name": "New", "primary_color": "#aabbcc"}

        with patch(_VALIDATE_CONFIG_PATH, _mock_validate_ok()):
            await service.save_draft(
                STARTER_TENANT_ID, TenantTier.STARTER, changes, "admin",
            )

        patch_call = prefs_repo.patch.call_args
        operations = patch_call.kwargs.get("operations", patch_call[1].get("operations", []))

        # Should have one set operation per changed field
        patched_paths = {op["path"] for op in operations}
        assert "/brand_name" in patched_paths
        assert "/primary_color" in patched_paths

    @pytest.mark.asyncio
    async def test_returns_existing_draft_version(self):
        """Update returns the existing draft's version, not a new one."""
        draft = _make_draft_doc(version=5)
        active = _make_active_doc()
        service, _, _, _, _ = _make_service(active=active, draft=draft)

        with patch(_VALIDATE_CONFIG_PATH, _mock_validate_ok()):
            result = await service.save_draft(
                STARTER_TENANT_ID, TenantTier.STARTER,
                {"brand_name": "X"}, "admin",
            )

        assert result.version == 5


# =========================================================================
# Test: save_draft — validation errors and warnings
# =========================================================================


class TestSaveDraftValidation:
    """Validation during save_draft."""

    @pytest.mark.asyncio
    async def test_validation_errors_block_save(self):
        """When validate_config returns errors, save is rejected."""
        service, prefs_repo, _, _, _ = _make_service(active=_make_active_doc())

        errors = [{"field_name": "brand_name", "message": "Too long"}]
        mock_validate = _mock_validate_with_errors(errors)

        with patch(_VALIDATE_CONFIG_PATH, mock_validate):
            result = await service.save_draft(
                STARTER_TENANT_ID, TenantTier.STARTER,
                {"brand_name": "X" * 500}, "admin",
            )

        assert result.success is False
        assert len(result.errors) > 0
        prefs_repo.create.assert_not_awaited()
        prefs_repo.patch.assert_not_awaited()

    @pytest.mark.asyncio
    async def test_validation_warnings_allow_save(self):
        """Warnings are returned but do not block the save."""
        active = _make_active_doc()
        service, prefs_repo, _, _, _ = _make_service(active=active)

        warnings = [{"field_name": "primary_color", "message": "Non-standard"}]
        mock_validate = _mock_validate_with_warnings(warnings)

        with patch(_VALIDATE_CONFIG_PATH, mock_validate):
            result = await service.save_draft(
                STARTER_TENANT_ID, TenantTier.STARTER,
                {"primary_color": "#xyz"}, "admin",
            )

        assert result.success is True
        assert result.warnings == warnings

    @pytest.mark.asyncio
    async def test_empty_changes_validated(self):
        """Even empty changes go through validation."""
        service, _, _, _, _ = _make_service(active=_make_active_doc())

        with patch(_VALIDATE_CONFIG_PATH, _mock_validate_ok()) as mock_val:
            await service.save_draft(
                STARTER_TENANT_ID, TenantTier.STARTER, {}, "admin",
            )
            mock_val.assert_called_once()


# =========================================================================
# Test: get_draft_state
# =========================================================================


class TestGetDraftState:
    """Draft state retrieval for the activation banner."""

    @pytest.mark.asyncio
    async def test_no_draft_returns_no_pending_changes(self):
        """When no draft exists, has_pending_changes is False."""
        active = _make_active_doc(version=3)
        service, _, _, _, _ = _make_service(active=active, draft=None)

        state = await service.get_draft_state(STARTER_TENANT_ID, TenantTier.STARTER)

        assert state.has_pending_changes is False
        assert state.active_version == 3
        assert state.active_activated_at == "2026-01-15T00:00:00Z"
        assert state.draft_version is None
        assert state.changed_fields == []

    @pytest.mark.asyncio
    async def test_no_draft_no_active_returns_empty(self):
        """When neither draft nor active exists, returns bare state."""
        service, _, _, _, _ = _make_service(active=None, draft=None)

        state = await service.get_draft_state(STARTER_TENANT_ID, TenantTier.STARTER)

        assert state.has_pending_changes is False
        assert state.active_version == 0
        assert state.active_activated_at is None

    @pytest.mark.asyncio
    async def test_with_draft_returns_pending(self):
        """When a draft exists, has_pending_changes is True."""
        active = _make_active_doc(version=1)
        draft = _make_draft_doc(version=2, primary_color="#ff0000")
        service, _, _, _, _ = _make_service(active=active, draft=draft)

        state = await service.get_draft_state(STARTER_TENANT_ID, TenantTier.STARTER)

        assert state.has_pending_changes is True
        assert state.active_version == 1
        assert state.draft_version == 2

    @pytest.mark.asyncio
    async def test_changed_fields_detected(self):
        """Changed fields between draft and active are listed."""
        active = _make_active_doc(
            brand_name="Original",
            primary_color="#ff3621",
            welcome_message="Hello!",
        )
        draft = _make_draft_doc(
            brand_name="Updated",  # changed
            primary_color="#0000ff",  # changed
            welcome_message="Hello!",  # same
        )
        service, _, _, _, _ = _make_service(active=active, draft=draft)

        state = await service.get_draft_state(STARTER_TENANT_ID, TenantTier.STARTER)

        assert "brand_name" in state.changed_fields
        assert "primary_color" in state.changed_fields
        # welcome_message is the same in both, so not listed as changed
        # (both are different defaults from the factories, but let's verify
        # the logic works correctly for what's actually different)

    @pytest.mark.asyncio
    async def test_metadata_fields_excluded_from_diff(self):
        """Metadata fields (id, version, config_state, etc.) are excluded from diff."""
        active = _make_active_doc(version=1)
        draft = _make_draft_doc(version=2)
        # version, config_state, is_current, activated_at, activated_by all differ
        # but should NOT appear in changed_fields
        service, _, _, _, _ = _make_service(active=active, draft=draft)

        state = await service.get_draft_state(STARTER_TENANT_ID, TenantTier.STARTER)

        for field in ("id", "version", "config_state", "is_current",
                      "activated_at", "activated_by", "widget_key"):
            assert field not in state.changed_fields

    @pytest.mark.asyncio
    async def test_draft_config_contains_changed_values(self):
        """draft_config and active_config contain only the changed fields' values."""
        active = _make_active_doc(brand_name="OldName", primary_color="#000000")
        draft = _make_draft_doc(brand_name="NewName", primary_color="#ffffff")
        service, _, _, _, _ = _make_service(active=active, draft=draft)

        state = await service.get_draft_state(STARTER_TENANT_ID, TenantTier.STARTER)

        if "brand_name" in state.changed_fields:
            assert state.draft_config["brand_name"] == "NewName"
            assert state.active_config["brand_name"] == "OldName"

    @pytest.mark.asyncio
    async def test_draft_without_active_shows_all_as_changed(self):
        """When no active exists, all non-metadata draft fields are 'changed'."""
        draft = _make_draft_doc(brand_name="Fresh", primary_color="#abcdef")
        service, _, _, _, _ = _make_service(active=None, draft=draft)

        state = await service.get_draft_state(STARTER_TENANT_ID, TenantTier.STARTER)

        assert state.has_pending_changes is True
        # Fields with values in draft but not in active should appear as changed
        assert "brand_name" in state.changed_fields


# =========================================================================
# Test: has_pending_changes
# =========================================================================


class TestHasPendingChanges:
    """Lightweight pending changes check."""

    @pytest.mark.asyncio
    async def test_no_draft_returns_false(self):
        """Returns False when no draft exists."""
        service, _, _, _, _ = _make_service(draft=None)
        result = await service.has_pending_changes(STARTER_TENANT_ID)
        assert result is False

    @pytest.mark.asyncio
    async def test_with_draft_returns_true(self):
        """Returns True when a draft exists."""
        service, _, _, _, _ = _make_service(draft=_make_draft_doc())
        result = await service.has_pending_changes(STARTER_TENANT_ID)
        assert result is True

    @pytest.mark.asyncio
    async def test_different_tenants_independent(self):
        """Pending changes check is tenant-scoped."""
        prefs_repo = AsyncMock()

        async def _get_draft(tenant_id):
            if tenant_id == STARTER_TENANT_ID:
                return _make_draft_doc(tenant_id=STARTER_TENANT_ID)
            return None

        prefs_repo.get_draft = AsyncMock(side_effect=_get_draft)

        service = ActivationService()
        service.configure(prefs_repo, AsyncMock())

        assert await service.has_pending_changes(STARTER_TENANT_ID) is True
        assert await service.has_pending_changes(PROFESSIONAL_TENANT_ID) is False


# =========================================================================
# Test: validate_for_activation
# =========================================================================


class TestValidateForActivation:
    """Activation validation rules."""

    @pytest.mark.asyncio
    async def test_all_pass(self):
        """Valid draft passes activation validation."""
        draft = _make_draft_doc(
            brand_name="Valid Brand",
            widget_key="pk_test_abc",
            brand_voice="friendly",
        )
        service, _, _, kb_repo, _ = _make_service(draft=draft, kb_count=3)

        result = await service.validate_for_activation(
            STARTER_TENANT_ID, TenantTier.STARTER,
        )

        assert result.can_activate is True
        assert result.hard_errors == []
        assert result.warnings == []

    @pytest.mark.asyncio
    async def test_no_draft_fails(self):
        """Validation fails when there is no draft to activate."""
        service, _, _, _, _ = _make_service(draft=None)

        result = await service.validate_for_activation(
            STARTER_TENANT_ID, TenantTier.STARTER,
        )

        assert result.can_activate is False
        assert any("No draft" in e["message"] for e in result.hard_errors)

    @pytest.mark.asyncio
    async def test_hard_block_empty_brand_name(self):
        """Empty brand_name blocks activation."""
        draft = _make_draft_doc(brand_name="")
        service, _, _, _, _ = _make_service(draft=draft, kb_count=5)

        result = await service.validate_for_activation(
            STARTER_TENANT_ID, TenantTier.STARTER,
        )

        assert result.can_activate is False
        assert any(e["field"] == "brand_name" for e in result.hard_errors)

    @pytest.mark.asyncio
    async def test_hard_block_whitespace_brand_name(self):
        """Whitespace-only brand_name blocks activation."""
        draft = _make_draft_doc(brand_name="   ")
        service, _, _, _, _ = _make_service(draft=draft, kb_count=5)

        result = await service.validate_for_activation(
            STARTER_TENANT_ID, TenantTier.STARTER,
        )

        assert result.can_activate is False
        assert any(e["field"] == "brand_name" for e in result.hard_errors)

    @pytest.mark.asyncio
    async def test_hard_block_no_widget_key(self):
        """Missing widget_key blocks activation."""
        draft = _make_draft_doc(widget_key="")
        # Override to truly remove widget_key
        draft["widget_key"] = ""
        service, _, _, _, _ = _make_service(draft=draft, kb_count=5)

        result = await service.validate_for_activation(
            STARTER_TENANT_ID, TenantTier.STARTER,
        )

        assert result.can_activate is False
        assert any(e["field"] == "widget_key" for e in result.hard_errors)

    @pytest.mark.asyncio
    async def test_hard_block_none_widget_key(self):
        """None widget_key blocks activation."""
        draft = _make_draft_doc()
        draft["widget_key"] = None
        service, _, _, _, _ = _make_service(draft=draft, kb_count=5)

        result = await service.validate_for_activation(
            STARTER_TENANT_ID, TenantTier.STARTER,
        )

        assert result.can_activate is False
        assert any(e["field"] == "widget_key" for e in result.hard_errors)

    @pytest.mark.asyncio
    async def test_multiple_hard_blocks(self):
        """Both brand_name and widget_key can fail simultaneously."""
        draft = _make_draft_doc(brand_name="", widget_key="")
        draft["widget_key"] = ""
        service, _, _, _, _ = _make_service(draft=draft, kb_count=5)

        result = await service.validate_for_activation(
            STARTER_TENANT_ID, TenantTier.STARTER,
        )

        assert result.can_activate is False
        error_fields = [e["field"] for e in result.hard_errors]
        assert "brand_name" in error_fields
        assert "widget_key" in error_fields

    @pytest.mark.asyncio
    async def test_hard_error_no_brand_voice(self):
        """Missing brand_voice blocks activation (mandatory — session 21)."""
        draft = _make_draft_doc(brand_voice="")
        service, _, _, _, _ = _make_service(draft=draft, kb_count=5)

        result = await service.validate_for_activation(
            STARTER_TENANT_ID, TenantTier.STARTER,
        )

        assert result.can_activate is False
        assert any(e["field"] == "brand_voice" for e in result.hard_errors)

    @pytest.mark.asyncio
    async def test_hard_error_whitespace_brand_voice(self):
        """Whitespace-only brand_voice blocks activation (mandatory — session 21)."""
        draft = _make_draft_doc(brand_voice="   ")
        service, _, _, _, _ = _make_service(draft=draft, kb_count=5)

        result = await service.validate_for_activation(
            STARTER_TENANT_ID, TenantTier.STARTER,
        )

        assert result.can_activate is False
        assert any(e["field"] == "brand_voice" for e in result.hard_errors)

    @pytest.mark.asyncio
    async def test_warning_no_kb_articles(self):
        """Zero published KB articles generates a warning."""
        draft = _make_draft_doc()
        service, _, _, _, _ = _make_service(draft=draft, kb_count=0)

        result = await service.validate_for_activation(
            STARTER_TENANT_ID, TenantTier.STARTER,
        )

        assert result.can_activate is True
        assert any(w["field"] == "knowledge_base" for w in result.warnings)

    @pytest.mark.asyncio
    async def test_kb_warning_with_empty_query_result(self):
        """Empty KB query result list triggers the warning."""
        draft = _make_draft_doc()
        service, _, _, kb_repo, _ = _make_service(draft=draft)
        kb_repo.query = AsyncMock(return_value=[])

        result = await service.validate_for_activation(
            STARTER_TENANT_ID, TenantTier.STARTER,
        )

        assert result.can_activate is True
        assert any(w["field"] == "knowledge_base" for w in result.warnings)

    @pytest.mark.asyncio
    async def test_kb_query_failure_silenced(self):
        """KB query exception is caught and does not block activation."""
        draft = _make_draft_doc()
        service, _, _, kb_repo, _ = _make_service(draft=draft)
        kb_repo.query = AsyncMock(side_effect=RuntimeError("DB offline"))

        result = await service.validate_for_activation(
            STARTER_TENANT_ID, TenantTier.STARTER,
        )

        # Should still succeed — KB failure is not a hard block
        assert result.can_activate is True

    @pytest.mark.asyncio
    async def test_no_kb_repo_skips_kb_check(self):
        """When kb_repo is None, KB check is skipped (no warning)."""
        draft = _make_draft_doc()
        service = ActivationService()
        service.configure(AsyncMock(), AsyncMock(), kb_repo=None)
        service._prefs_repo.get_draft = AsyncMock(return_value=draft)

        result = await service.validate_for_activation(
            STARTER_TENANT_ID, TenantTier.STARTER,
        )

        assert result.can_activate is True
        assert not any(w["field"] == "knowledge_base" for w in result.warnings)

    @pytest.mark.asyncio
    async def test_hard_blocks_and_warnings_coexist(self):
        """Hard errors and warnings can both be present."""
        draft = _make_draft_doc(brand_name="", brand_voice="")
        service, _, _, _, _ = _make_service(draft=draft, kb_count=0)

        result = await service.validate_for_activation(
            STARTER_TENANT_ID, TenantTier.STARTER,
        )

        assert result.can_activate is False
        assert len(result.hard_errors) > 0
        assert len(result.warnings) > 0

    @pytest.mark.asyncio
    async def test_validation_result_includes_page_hints(self):
        """Hard errors include page hints for UI navigation."""
        draft = _make_draft_doc(brand_name="")
        service, _, _, _, _ = _make_service(draft=draft, kb_count=5)

        result = await service.validate_for_activation(
            STARTER_TENANT_ID, TenantTier.STARTER,
        )

        brand_error = next(
            e for e in result.hard_errors if e["field"] == "brand_name"
        )
        assert "page" in brand_error


# =========================================================================
# Test: activate
# =========================================================================


class TestActivate:
    """Promote draft to active configuration."""

    @pytest.mark.asyncio
    async def test_activate_success(self):
        """Successful activation promotes draft and demotes active."""
        active = _make_active_doc(version=1)
        draft = _make_draft_doc(
            version=2, brand_name="New Brand", widget_key="pk_test_123",
        )
        service, prefs_repo, audit_repo, kb_repo, config_proc = _make_service(
            active=active, draft=draft, kb_count=5,
        )

        result = await service.activate(
            STARTER_TENANT_ID, TenantTier.STARTER, "user:mike",
        )

        assert result.success is True
        assert result.version == 2
        assert result.activated_at is not None
        assert result.errors == []

    @pytest.mark.asyncio
    async def test_activate_demotes_active_to_previous(self):
        """Current active config is demoted to 'previous' state."""
        active = _make_active_doc(version=1)
        draft = _make_draft_doc(version=2, brand_name="X", widget_key="pk_123")
        service, prefs_repo, _, _, _ = _make_service(
            active=active, draft=draft, kb_count=5,
        )

        await service.activate(STARTER_TENANT_ID, TenantTier.STARTER, "admin")

        # Find the patch call that demotes active → previous
        patch_calls = prefs_repo.patch.call_args_list
        demote_call = None
        for c in patch_calls:
            doc_id = c.kwargs.get("document_id", c[1].get("document_id", ""))
            ops = c.kwargs.get("operations", c[1].get("operations", []))
            for op in ops:
                if op.get("value") == ConfigState.PREVIOUS.value and doc_id == active["id"]:
                    demote_call = c
                    break

        assert demote_call is not None, "Active was not demoted to previous"

    @pytest.mark.asyncio
    async def test_activate_promotes_draft_to_active(self):
        """Draft is promoted to 'active' state with activation timestamp."""
        active = _make_active_doc()
        draft = _make_draft_doc(version=2, brand_name="X", widget_key="pk_123")
        service, prefs_repo, _, _, _ = _make_service(
            active=active, draft=draft, kb_count=5,
        )

        await service.activate(STARTER_TENANT_ID, TenantTier.STARTER, "admin")

        # Find the patch call that promotes draft → active
        patch_calls = prefs_repo.patch.call_args_list
        promote_found = False
        for c in patch_calls:
            doc_id = c.kwargs.get("document_id", c[1].get("document_id", ""))
            ops = c.kwargs.get("operations", c[1].get("operations", []))
            if doc_id == draft["id"]:
                op_values = {op.get("path"): op.get("value") for op in ops}
                if op_values.get("/config_state") == ConfigState.ACTIVE.value:
                    promote_found = True
                    assert op_values.get("/is_current") is True
                    assert op_values.get("/activated_at") is not None
                    assert op_values.get("/activated_by") == "admin"

        assert promote_found, "Draft was not promoted to active"

    @pytest.mark.asyncio
    async def test_activate_archives_old_previous(self):
        """Existing 'previous' document is archived before demotion."""
        active = _make_active_doc()
        draft = _make_draft_doc(version=2, brand_name="X", widget_key="pk_123")
        previous = _make_previous_doc(version=0)
        service, prefs_repo, _, _, _ = _make_service(
            active=active, draft=draft, previous=previous, kb_count=5,
        )

        await service.activate(STARTER_TENANT_ID, TenantTier.STARTER, "admin")

        # Verify archive patch on previous document
        patch_calls = prefs_repo.patch.call_args_list
        archived = False
        for c in patch_calls:
            doc_id = c.kwargs.get("document_id", c[1].get("document_id", ""))
            ops = c.kwargs.get("operations", c[1].get("operations", []))
            if doc_id == previous["id"]:
                for op in ops:
                    if op.get("value") == "archived":
                        archived = True

        assert archived, "Previous document was not archived"

    @pytest.mark.asyncio
    async def test_activate_invalidates_cache(self):
        """Config processor cache is invalidated on activation."""
        active = _make_active_doc()
        draft = _make_draft_doc(version=2, brand_name="X", widget_key="pk_123")
        service, _, _, _, config_proc = _make_service(
            active=active, draft=draft, kb_count=5,
        )

        await service.activate(STARTER_TENANT_ID, TenantTier.STARTER, "admin")

        config_proc._invalidate_cache.assert_called_once_with(STARTER_TENANT_ID)

    @pytest.mark.asyncio
    async def test_activate_logs_audit_event(self):
        """Activation writes an audit log entry."""
        active = _make_active_doc()
        draft = _make_draft_doc(version=2, brand_name="X", widget_key="pk_123")
        service, _, audit_repo, _, _ = _make_service(
            active=active, draft=draft, kb_count=5,
        )

        await service.activate(STARTER_TENANT_ID, TenantTier.STARTER, "user:mike")

        audit_repo.log_event.assert_awaited_once()
        call_kwargs = audit_repo.log_event.call_args.kwargs
        assert call_kwargs["event_type"] == AuditEventType.CONFIG_UPDATED
        assert call_kwargs["tenant_id"] == STARTER_TENANT_ID
        assert call_kwargs["actor"] == "user:mike"
        assert call_kwargs["payload"]["action"] == "config_activated"

    @pytest.mark.asyncio
    async def test_activate_audit_actor_type_user(self):
        """Actor starting with 'user:' is logged as type 'user'."""
        active = _make_active_doc()
        draft = _make_draft_doc(version=2, brand_name="X", widget_key="pk_123")
        service, _, audit_repo, _, _ = _make_service(
            active=active, draft=draft, kb_count=5,
        )

        await service.activate(STARTER_TENANT_ID, TenantTier.STARTER, "user:mike")

        call_kwargs = audit_repo.log_event.call_args.kwargs
        assert call_kwargs["actor_type"] == "user"

    @pytest.mark.asyncio
    async def test_activate_audit_actor_type_system(self):
        """Actor NOT starting with 'user:' is logged as type 'system'."""
        active = _make_active_doc()
        draft = _make_draft_doc(version=2, brand_name="X", widget_key="pk_123")
        service, _, audit_repo, _, _ = _make_service(
            active=active, draft=draft, kb_count=5,
        )

        await service.activate(STARTER_TENANT_ID, TenantTier.STARTER, "admin")

        call_kwargs = audit_repo.log_event.call_args.kwargs
        assert call_kwargs["actor_type"] == "system"

    @pytest.mark.asyncio
    async def test_activate_validation_failure(self):
        """Activation fails when draft has hard validation errors."""
        draft = _make_draft_doc(brand_name="", widget_key="pk_test_123")
        service, prefs_repo, _, _, _ = _make_service(draft=draft, kb_count=5)

        result = await service.activate(
            STARTER_TENANT_ID, TenantTier.STARTER, "admin",
        )

        assert result.success is False
        assert len(result.errors) > 0
        # Draft should NOT be promoted
        # (patch is only called during validation's get_draft, not for promotion)

    @pytest.mark.asyncio
    async def test_activate_no_draft(self):
        """Activation fails when no draft exists."""
        service, _, _, _, _ = _make_service(active=_make_active_doc(), draft=None)

        result = await service.activate(
            STARTER_TENANT_ID, TenantTier.STARTER, "admin",
        )

        assert result.success is False
        assert any("No draft" in e["message"] for e in result.errors)

    @pytest.mark.asyncio
    async def test_activate_without_prior_active(self):
        """Activation succeeds even when there is no prior active config."""
        draft = _make_draft_doc(
            version=1, brand_name="First", widget_key="pk_first",
        )
        service, prefs_repo, _, _, _ = _make_service(
            active=None, draft=draft, kb_count=5,
        )

        result = await service.activate(
            STARTER_TENANT_ID, TenantTier.STARTER, "admin",
        )

        assert result.success is True
        assert result.version == 1

    @pytest.mark.asyncio
    async def test_activate_without_config_processor(self):
        """Activation succeeds when config_processor is None."""
        active = _make_active_doc()
        draft = _make_draft_doc(version=2, brand_name="X", widget_key="pk_123")
        service = ActivationService()
        prefs_repo = AsyncMock()
        prefs_repo.get_active = AsyncMock(return_value=active)
        prefs_repo.get_draft = AsyncMock(return_value=draft)
        prefs_repo.get_previous = AsyncMock(return_value=None)
        prefs_repo.patch = AsyncMock()

        kb_repo = AsyncMock()
        kb_repo.query = AsyncMock(return_value=[5])

        service.configure(prefs_repo, AsyncMock(), kb_repo, config_processor=None)

        result = await service.activate(
            STARTER_TENANT_ID, TenantTier.STARTER, "admin",
        )

        assert result.success is True

    @pytest.mark.asyncio
    async def test_activate_audit_failure_does_not_block(self):
        """Audit log failure does not prevent successful activation."""
        active = _make_active_doc()
        draft = _make_draft_doc(version=2, brand_name="X", widget_key="pk_123")
        service, _, audit_repo, _, _ = _make_service(
            active=active, draft=draft, kb_count=5,
        )
        audit_repo.log_event = AsyncMock(side_effect=RuntimeError("DB error"))

        result = await service.activate(
            STARTER_TENANT_ID, TenantTier.STARTER, "admin",
        )

        assert result.success is True

    @pytest.mark.asyncio
    async def test_activate_fails_without_brand_voice(self):
        """Activation fails when brand_voice is empty (mandatory — session 21)."""
        draft = _make_draft_doc(brand_voice="")
        service, _, _, _, _ = _make_service(draft=draft, kb_count=0)

        result = await service.activate(
            STARTER_TENANT_ID, TenantTier.STARTER, "admin",
        )

        assert result.success is False
        assert any(e["field"] == "brand_voice" for e in result.errors)

    @pytest.mark.asyncio
    async def test_activate_returns_warnings(self):
        """Activation succeeds with warnings (e.g. no KB articles)."""
        draft = _make_draft_doc()  # brand_voice="friendly" (valid)
        service, _, _, _, _ = _make_service(draft=draft, kb_count=0)

        result = await service.activate(
            STARTER_TENANT_ID, TenantTier.STARTER, "admin",
        )

        assert result.success is True
        assert len(result.warnings) > 0


# =========================================================================
# Test: restore_previous
# =========================================================================


class TestRestorePrevious:
    """Restore previous activation snapshot."""

    @pytest.mark.asyncio
    async def test_restore_success(self):
        """Successful restore swaps active and previous."""
        active = _make_active_doc(version=2)
        previous = _make_previous_doc(version=1)
        service, prefs_repo, audit_repo, _, _ = _make_service(
            active=active, previous=previous,
        )

        result = await service.restore_previous(
            STARTER_TENANT_ID, TenantTier.STARTER, "admin",
        )

        assert result.success is True
        assert result.restored_version == 1
        assert result.restored_activated_at is not None
        assert result.error is None

    @pytest.mark.asyncio
    async def test_restore_demotes_active(self):
        """Current active is demoted to 'previous'."""
        active = _make_active_doc(version=2)
        previous = _make_previous_doc(version=1)
        service, prefs_repo, _, _, _ = _make_service(
            active=active, previous=previous,
        )

        await service.restore_previous(
            STARTER_TENANT_ID, TenantTier.STARTER, "admin",
        )

        patch_calls = prefs_repo.patch.call_args_list
        demoted = False
        for c in patch_calls:
            doc_id = c.kwargs.get("document_id", c[1].get("document_id", ""))
            ops = c.kwargs.get("operations", c[1].get("operations", []))
            if doc_id == active["id"]:
                for op in ops:
                    if op.get("value") == ConfigState.PREVIOUS.value:
                        demoted = True

        assert demoted, "Active was not demoted to previous"

    @pytest.mark.asyncio
    async def test_restore_promotes_previous(self):
        """Previous is promoted to 'active' with new activated_at."""
        active = _make_active_doc(version=2)
        previous = _make_previous_doc(version=1)
        service, prefs_repo, _, _, _ = _make_service(
            active=active, previous=previous,
        )

        await service.restore_previous(
            STARTER_TENANT_ID, TenantTier.STARTER, "admin",
        )

        patch_calls = prefs_repo.patch.call_args_list
        promoted = False
        for c in patch_calls:
            doc_id = c.kwargs.get("document_id", c[1].get("document_id", ""))
            ops = c.kwargs.get("operations", c[1].get("operations", []))
            if doc_id == previous["id"]:
                op_map = {op["path"]: op["value"] for op in ops}
                if op_map.get("/config_state") == ConfigState.ACTIVE.value:
                    promoted = True
                    assert op_map.get("/is_current") is True
                    assert "/activated_at" in op_map
                    assert op_map.get("/activated_by") == "restore:admin"

        assert promoted, "Previous was not promoted to active"

    @pytest.mark.asyncio
    async def test_restore_discards_existing_draft(self):
        """Any existing draft is discarded during restore."""
        active = _make_active_doc(version=2)
        previous = _make_previous_doc(version=1)
        draft = _make_draft_doc(version=3)
        service, prefs_repo, _, _, _ = _make_service(
            active=active, previous=previous, draft=draft,
        )

        await service.restore_previous(
            STARTER_TENANT_ID, TenantTier.STARTER, "admin",
        )

        # Draft should be patched to 'discarded'
        patch_calls = prefs_repo.patch.call_args_list
        draft_discarded = False
        for c in patch_calls:
            doc_id = c.kwargs.get("document_id", c[1].get("document_id", ""))
            ops = c.kwargs.get("operations", c[1].get("operations", []))
            if doc_id == draft["id"]:
                for op in ops:
                    if op.get("value") == "discarded":
                        draft_discarded = True

        assert draft_discarded, "Draft was not discarded during restore"

    @pytest.mark.asyncio
    async def test_restore_no_previous_fails(self):
        """Restore fails when no previous configuration exists."""
        service, _, _, _, _ = _make_service(
            active=_make_active_doc(), previous=None,
        )

        result = await service.restore_previous(
            STARTER_TENANT_ID, TenantTier.STARTER, "admin",
        )

        assert result.success is False
        assert "No previous" in result.error

    @pytest.mark.asyncio
    async def test_restore_invalidates_cache(self):
        """Config processor cache is invalidated on restore."""
        active = _make_active_doc()
        previous = _make_previous_doc()
        service, _, _, _, config_proc = _make_service(
            active=active, previous=previous,
        )

        await service.restore_previous(
            STARTER_TENANT_ID, TenantTier.STARTER, "admin",
        )

        config_proc._invalidate_cache.assert_called_once_with(STARTER_TENANT_ID)

    @pytest.mark.asyncio
    async def test_restore_logs_audit_event(self):
        """Restore writes an audit log entry."""
        active = _make_active_doc(version=2)
        previous = _make_previous_doc(version=1)
        service, _, audit_repo, _, _ = _make_service(
            active=active, previous=previous,
        )

        await service.restore_previous(
            STARTER_TENANT_ID, TenantTier.STARTER, "user:mike",
        )

        audit_repo.log_event.assert_awaited_once()
        call_kwargs = audit_repo.log_event.call_args.kwargs
        assert call_kwargs["payload"]["action"] == "config_restored"
        assert call_kwargs["payload"]["restored_version"] == 1
        assert call_kwargs["payload"]["demoted_version"] == 2

    @pytest.mark.asyncio
    async def test_restore_audit_failure_does_not_block(self):
        """Audit log failure does not prevent successful restore."""
        active = _make_active_doc()
        previous = _make_previous_doc()
        service, _, audit_repo, _, _ = _make_service(
            active=active, previous=previous,
        )
        audit_repo.log_event = AsyncMock(side_effect=RuntimeError("DB error"))

        result = await service.restore_previous(
            STARTER_TENANT_ID, TenantTier.STARTER, "admin",
        )

        assert result.success is True

    @pytest.mark.asyncio
    async def test_restore_without_active(self):
        """Restore succeeds even when there is no current active config."""
        previous = _make_previous_doc(version=1)
        service, prefs_repo, _, _, _ = _make_service(
            active=None, previous=previous,
        )

        result = await service.restore_previous(
            STARTER_TENANT_ID, TenantTier.STARTER, "admin",
        )

        assert result.success is True
        assert result.restored_version == 1


# =========================================================================
# Test: discard_draft
# =========================================================================


class TestDiscardDraft:
    """Discard the current draft."""

    @pytest.mark.asyncio
    async def test_discard_success_with_active(self):
        """Discards draft when active config exists (normal case)."""
        active = _make_active_doc()
        draft = _make_draft_doc(version=2)
        service, prefs_repo, _, _, _ = _make_service(active=active, draft=draft)

        result = await service.discard_draft(STARTER_TENANT_ID, "admin")

        assert result is True

        # Verify draft was patched to 'discarded'
        prefs_repo.patch.assert_awaited_once()
        patch_call = prefs_repo.patch.call_args
        doc_id = patch_call.kwargs.get("document_id", patch_call[1].get("document_id", ""))
        assert doc_id == draft["id"]

        ops = patch_call.kwargs.get("operations", patch_call[1].get("operations", []))
        op_map = {op["path"]: op["value"] for op in ops}
        assert op_map.get("/config_state") == "discarded"
        assert op_map.get("/is_current") is False

    @pytest.mark.asyncio
    async def test_discard_resets_when_never_activated(self):
        """Resets draft to initial state when no active config exists."""
        draft = _make_draft_doc(version=1)
        service, prefs_repo, _, _, _ = _make_service(draft=draft)

        result = await service.discard_draft(STARTER_TENANT_ID, "admin")

        assert result is True

        # Verify draft was reset (not discarded) — brand_name cleared
        prefs_repo.patch.assert_awaited_once()
        patch_call = prefs_repo.patch.call_args
        doc_id = patch_call.kwargs.get("document_id", patch_call[1].get("document_id", ""))
        assert doc_id == draft["id"]

        ops = patch_call.kwargs.get("operations", patch_call[1].get("operations", []))
        op_map = {op["path"]: op["value"] for op in ops}
        # Should reset fields, NOT set config_state to discarded
        assert "/config_state" not in op_map
        # All merchant-configurable fields must match seed_tenant.py defaults
        assert op_map.get("/brand_name") == ""
        assert op_map.get("/brand_voice") == ""
        assert op_map.get("/custom_instructions") == ""
        assert op_map.get("/return_policy") == ""
        assert op_map.get("/shipping_info") == ""
        assert op_map.get("/escalation_keywords") == []
        assert op_map.get("/escalation_email") is None
        assert op_map.get("/greeting_message") is None
        assert op_map.get("/farewell_message") is None
        assert op_map.get("/warranty_info") is None
        assert op_map.get("/support_hours") is None
        assert op_map.get("/custom_policies") is None
        assert op_map.get("/widget_greeting_message") == ""
        assert op_map.get("/activated_at") is None
        assert op_map.get("/activated_by") is None

    @pytest.mark.asyncio
    async def test_discard_no_draft(self):
        """Discard returns False when no draft exists."""
        service, prefs_repo, _, _, _ = _make_service(draft=None)

        result = await service.discard_draft(STARTER_TENANT_ID, "admin")

        assert result is False
        prefs_repo.patch.assert_not_awaited()

    @pytest.mark.asyncio
    async def test_discard_does_not_affect_active(self):
        """Discarding a draft does not touch the active config."""
        active = _make_active_doc()
        draft = _make_draft_doc()
        service, prefs_repo, _, _, _ = _make_service(active=active, draft=draft)

        await service.discard_draft(STARTER_TENANT_ID, "admin")

        # Only one patch call — for the draft, not the active
        assert prefs_repo.patch.await_count == 1
        doc_id = prefs_repo.patch.call_args.kwargs.get(
            "document_id",
            prefs_repo.patch.call_args[1].get("document_id", ""),
        )
        assert doc_id == draft["id"]


# =========================================================================
# Test: reinitialize_to_defaults
# =========================================================================


class TestReinitializeToDefaults:
    """Superadmin nuclear reset to tier defaults."""

    @pytest.mark.asyncio
    async def test_reinitialize_success(self):
        """Reinitialize creates a fresh draft from tier defaults."""
        active = _make_active_doc(widget_key="pk_preserve_me")
        service, prefs_repo, _, _, _ = _make_service(active=active, draft=None)

        with patch(_VALIDATE_CONFIG_PATH, _mock_validate_ok()):
            with patch(_RESOLVE_DEFAULTS_PATH) as mock_defaults:
                mock_defaults.return_value = {
                    "brand_name": "Default Brand",
                    "brand_voice": "friendly",
                    "primary_color": "#ff3621",
                }
                result = await service.reinitialize_to_defaults(
                    STARTER_TENANT_ID, TenantTier.STARTER, "superadmin",
                )

        assert result.success is True
        assert result.state == "draft"

    @pytest.mark.asyncio
    async def test_reinitialize_preserves_widget_key(self):
        """Widget key from active config is preserved in the new draft."""
        active = _make_active_doc(widget_key="pk_must_keep")
        service, prefs_repo, _, _, _ = _make_service(active=active, draft=None)

        defaults_dict = {"brand_name": "Default", "brand_voice": "friendly"}

        with patch(_VALIDATE_CONFIG_PATH, _mock_validate_ok()):
            with patch(_RESOLVE_DEFAULTS_PATH, return_value=defaults_dict):
                await service.reinitialize_to_defaults(
                    STARTER_TENANT_ID, TenantTier.STARTER, "superadmin",
                )

        # The defaults should have been mutated to include widget_key
        assert defaults_dict.get("widget_key") == "pk_must_keep"

    @pytest.mark.asyncio
    async def test_reinitialize_discards_existing_draft(self):
        """Existing draft is discarded before creating the new one."""
        active = _make_active_doc()
        old_draft = _make_draft_doc(version=2)
        service, prefs_repo, _, _, _ = _make_service(
            active=active, draft=old_draft,
        )

        # After discard, get_draft should return None so a new draft is created
        call_count = 0

        async def _get_draft_side_effect(tenant_id):
            nonlocal call_count
            call_count += 1
            # First call: discard_draft checks for existing → returns old
            # Second call: save_draft checks for existing → returns None (discarded)
            if call_count <= 1:
                return old_draft
            return None

        prefs_repo.get_draft = AsyncMock(side_effect=_get_draft_side_effect)

        with patch(_VALIDATE_CONFIG_PATH, _mock_validate_ok()):
            with patch(_RESOLVE_DEFAULTS_PATH, return_value={"brand_name": "Default"}):
                result = await service.reinitialize_to_defaults(
                    STARTER_TENANT_ID, TenantTier.STARTER, "superadmin",
                )

        assert result.success is True

    @pytest.mark.asyncio
    async def test_reinitialize_without_active(self):
        """Reinitialize works even when there is no active config."""
        service, _, _, _, _ = _make_service(active=None, draft=None)

        with patch(_VALIDATE_CONFIG_PATH, _mock_validate_ok()):
            with patch(_RESOLVE_DEFAULTS_PATH, return_value={"brand_name": "Fresh"}):
                result = await service.reinitialize_to_defaults(
                    STARTER_TENANT_ID, TenantTier.STARTER, "superadmin",
                )

        assert result.success is True

    @pytest.mark.asyncio
    async def test_reinitialize_uses_superadmin_actor(self):
        """The actor defaults to 'superadmin'."""
        active = _make_active_doc()
        service, prefs_repo, _, _, _ = _make_service(active=active, draft=None)

        with patch(_VALIDATE_CONFIG_PATH, _mock_validate_ok()):
            with patch(_RESOLVE_DEFAULTS_PATH, return_value={"brand_name": "X"}):
                await service.reinitialize_to_defaults(
                    STARTER_TENANT_ID, TenantTier.STARTER,
                )

        # Verify the created document has superadmin as created_by
        created_doc = prefs_repo.create.call_args[0][1]
        assert created_doc.created_by == "superadmin"


# =========================================================================
# Test: _ensure_config_state (lazy migration)
# =========================================================================


class TestEnsureConfigState:
    """Lazy migration of pre-config_state documents."""

    @pytest.mark.asyncio
    async def test_old_doc_without_config_state_gets_patched(self):
        """Document missing config_state is patched to 'active'."""
        old_doc = {
            "id": "prefs-old",
            "tenant_id": STARTER_TENANT_ID,
            "is_current": True,
            "brand_name": "Old Brand",
        }
        # No "config_state" key at all
        service, prefs_repo, _, _, _ = _make_service()

        result = await service._ensure_config_state(old_doc, STARTER_TENANT_ID)

        assert result["config_state"] == ConfigState.ACTIVE.value
        assert result["activated_at"] is not None

        prefs_repo.patch.assert_awaited_once()
        patch_call = prefs_repo.patch.call_args
        ops = patch_call.kwargs.get("operations", patch_call[1].get("operations", []))
        op_map = {op["path"]: op["value"] for op in ops}
        assert op_map["/config_state"] == ConfigState.ACTIVE.value
        assert "/activated_at" in op_map

    @pytest.mark.asyncio
    async def test_old_doc_with_none_config_state_gets_patched(self):
        """Document with config_state=None is patched to 'active'."""
        old_doc = {
            "id": "prefs-none",
            "tenant_id": STARTER_TENANT_ID,
            "config_state": None,
            "is_current": True,
        }
        service, prefs_repo, _, _, _ = _make_service()

        result = await service._ensure_config_state(old_doc, STARTER_TENANT_ID)

        assert result["config_state"] == ConfigState.ACTIVE.value
        prefs_repo.patch.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_doc_with_config_state_unchanged(self):
        """Document that already has config_state is not patched."""
        doc = _make_active_doc()
        service, prefs_repo, _, _, _ = _make_service()

        result = await service._ensure_config_state(doc, STARTER_TENANT_ID)

        assert result["config_state"] == ConfigState.ACTIVE.value
        prefs_repo.patch.assert_not_awaited()

    @pytest.mark.asyncio
    async def test_draft_doc_not_patched(self):
        """A draft document with config_state is not patched."""
        doc = _make_draft_doc()
        service, prefs_repo, _, _, _ = _make_service()

        result = await service._ensure_config_state(doc, STARTER_TENANT_ID)

        assert result["config_state"] == ConfigState.DRAFT.value
        prefs_repo.patch.assert_not_awaited()

    @pytest.mark.asyncio
    async def test_migration_sets_activated_at(self):
        """Migrated document gets activated_at set to current time."""
        old_doc = {
            "id": "prefs-migrate",
            "tenant_id": STARTER_TENANT_ID,
            "is_current": True,
        }
        service, _, _, _, _ = _make_service()

        result = await service._ensure_config_state(old_doc, STARTER_TENANT_ID)

        # activated_at should be a valid ISO timestamp
        activated_at = result["activated_at"]
        assert activated_at is not None
        # Should be parseable
        parsed = datetime.fromisoformat(activated_at)
        assert parsed.tzinfo is not None


# =========================================================================
# Test: module-level singleton
# =========================================================================


class TestModuleSingleton:
    """Module-level get_activation_service() function."""

    def test_singleton_returns_same_instance(self):
        """get_activation_service returns the same instance each time."""
        from src.multi_tenant.activation_service import get_activation_service

        # Reset the module-level singleton for isolated test
        import src.multi_tenant.activation_service as _mod
        original = _mod._service

        try:
            _mod._service = None
            svc1 = get_activation_service()
            svc2 = get_activation_service()
            assert svc1 is svc2
        finally:
            _mod._service = original

    def test_singleton_is_not_configured(self):
        """Freshly created singleton is not yet configured."""
        from src.multi_tenant.activation_service import get_activation_service

        import src.multi_tenant.activation_service as _mod
        original = _mod._service

        try:
            _mod._service = None
            svc = get_activation_service()
            assert svc._is_configured is False
        finally:
            _mod._service = original


# =========================================================================
# Test: cross-tier behavior
# =========================================================================


class TestCrossTierBehavior:
    """Verify behavior across different tenant tiers."""

    @pytest.mark.asyncio
    async def test_save_draft_professional_tier(self):
        """save_draft works for Professional tier."""
        active = _make_active_doc(tenant_id=PROFESSIONAL_TENANT_ID)
        service, _, _, _, _ = _make_service(active=active)

        with patch(_VALIDATE_CONFIG_PATH, _mock_validate_ok()):
            result = await service.save_draft(
                PROFESSIONAL_TENANT_ID, TenantTier.PROFESSIONAL,
                {"brand_name": "Pro Brand"}, "admin",
            )

        assert result.success is True

    @pytest.mark.asyncio
    async def test_save_draft_enterprise_tier(self):
        """save_draft works for Enterprise tier."""
        active = _make_active_doc(tenant_id=ENTERPRISE_TENANT_ID)
        service, _, _, _, _ = _make_service(active=active)

        with patch(_VALIDATE_CONFIG_PATH, _mock_validate_ok()):
            result = await service.save_draft(
                ENTERPRISE_TENANT_ID, TenantTier.ENTERPRISE,
                {"brand_name": "Ent Brand"}, "admin",
            )

        assert result.success is True

    @pytest.mark.asyncio
    async def test_validate_with_kb_articles_enterprise(self):
        """Enterprise tenant with sufficient KB articles passes validation."""
        draft = _make_draft_doc(tenant_id=ENTERPRISE_TENANT_ID)
        service, _, _, _, _ = _make_service(draft=draft, kb_count=10)

        result = await service.validate_for_activation(
            ENTERPRISE_TENANT_ID, TenantTier.ENTERPRISE,
        )

        assert result.can_activate is True
        assert not any(w["field"] == "knowledge_base" for w in result.warnings)


# =========================================================================
# Test: edge cases
# =========================================================================


class TestEdgeCases:
    """Edge cases and boundary conditions."""

    @pytest.mark.asyncio
    async def test_save_draft_with_cosmos_metadata_fields(self):
        """Active doc with Cosmos metadata (_rid, _self, etc.) is handled."""
        active = _make_active_doc()
        active["_rid"] = "abc123"
        active["_self"] = "/dbs/db/colls/coll"
        active["_etag"] = '"etag"'
        active["_attachments"] = "attachments/"
        active["_ts"] = 1234567890

        service, prefs_repo, _, _, _ = _make_service(active=active)

        with patch(_VALIDATE_CONFIG_PATH, _mock_validate_ok()):
            result = await service.save_draft(
                STARTER_TENANT_ID, TenantTier.STARTER,
                {"brand_name": "X"}, "admin",
            )

        assert result.success is True

        # Cosmos metadata should NOT be in the created draft
        created_doc = prefs_repo.create.call_args[0][1]
        for key in ("_rid", "_self", "_etag", "_attachments", "_ts"):
            assert key not in created_doc

    @pytest.mark.asyncio
    async def test_activate_payload_includes_versions(self):
        """Audit payload includes both draft and previous active versions."""
        active = _make_active_doc(version=5)
        draft = _make_draft_doc(version=6, brand_name="X", widget_key="pk_123")
        service, _, audit_repo, _, _ = _make_service(
            active=active, draft=draft, kb_count=5,
        )

        await service.activate(STARTER_TENANT_ID, TenantTier.STARTER, "admin")

        payload = audit_repo.log_event.call_args.kwargs["payload"]
        assert payload["draft_version"] == 6
        assert payload["previous_active_version"] == 5

    @pytest.mark.asyncio
    async def test_restore_without_existing_draft(self):
        """Restore succeeds when there is no draft to discard."""
        active = _make_active_doc()
        previous = _make_previous_doc()
        service, _, _, _, _ = _make_service(
            active=active, previous=previous, draft=None,
        )

        result = await service.restore_previous(
            STARTER_TENANT_ID, TenantTier.STARTER, "admin",
        )

        assert result.success is True

    @pytest.mark.asyncio
    async def test_multiple_saves_increment_correctly(self):
        """Multiple save_draft calls with no existing draft each increment version."""
        active = _make_active_doc(version=1)
        service, prefs_repo, _, _, _ = _make_service(active=active, draft=None)

        with patch(_VALIDATE_CONFIG_PATH, _mock_validate_ok()):
            result = await service.save_draft(
                STARTER_TENANT_ID, TenantTier.STARTER,
                {"brand_name": "First"}, "admin",
            )

        assert result.version == 2

    @pytest.mark.asyncio
    async def test_activate_without_audit_repo(self):
        """Activation succeeds when audit_repo is None."""
        active = _make_active_doc()
        draft = _make_draft_doc(version=2, brand_name="X", widget_key="pk_123")
        service = ActivationService()
        prefs_repo = AsyncMock()
        prefs_repo.get_active = AsyncMock(return_value=active)
        prefs_repo.get_draft = AsyncMock(return_value=draft)
        prefs_repo.get_previous = AsyncMock(return_value=None)
        prefs_repo.patch = AsyncMock()

        kb_repo = AsyncMock()
        kb_repo.query = AsyncMock(return_value=[5])

        service.configure(prefs_repo, audit_repo=None, kb_repo=kb_repo)

        result = await service.activate(
            STARTER_TENANT_ID, TenantTier.STARTER, "admin",
        )

        assert result.success is True

    @pytest.mark.asyncio
    async def test_lazy_migration_during_save_draft(self):
        """save_draft triggers lazy migration on active doc without config_state."""
        active = {
            "id": "prefs-old",
            "tenant_id": STARTER_TENANT_ID,
            "version": 1,
            "is_current": True,
            "brand_name": "Old",
        }
        # No config_state
        service, prefs_repo, _, _, _ = _make_service(active=active, draft=None)

        with patch(_VALIDATE_CONFIG_PATH, _mock_validate_ok()):
            result = await service.save_draft(
                STARTER_TENANT_ID, TenantTier.STARTER,
                {"brand_name": "New"}, "admin",
            )

        assert result.success is True

        # patch should have been called for both migration and create for draft
        # The first patch call should be the lazy migration
        first_patch = prefs_repo.patch.call_args_list[0]
        ops = first_patch.kwargs.get("operations", first_patch[1].get("operations", []))
        op_map = {op["path"]: op["value"] for op in ops}
        assert op_map["/config_state"] == ConfigState.ACTIVE.value

    @pytest.mark.asyncio
    async def test_lazy_migration_during_activate(self):
        """activate triggers lazy migration on active doc without config_state."""
        active = {
            "id": "prefs-old",
            "tenant_id": STARTER_TENANT_ID,
            "version": 1,
            "is_current": True,
            "brand_name": "Old",
        }
        draft = _make_draft_doc(version=2, brand_name="X", widget_key="pk_123")
        service, prefs_repo, _, _, _ = _make_service(
            active=active, draft=draft, kb_count=5,
        )

        await service.activate(STARTER_TENANT_ID, TenantTier.STARTER, "admin")

        # First patch call on active should be the lazy migration
        active_patches = [
            c for c in prefs_repo.patch.call_args_list
            if c.kwargs.get("document_id", c[1].get("document_id", "")) == "prefs-old"
        ]
        assert len(active_patches) >= 1
        first_ops = active_patches[0].kwargs.get(
            "operations", active_patches[0][1].get("operations", []),
        )
        migrated = any(
            op.get("path") == "/config_state" and op.get("value") == ConfigState.ACTIVE.value
            for op in first_ops
        )
        assert migrated, "Lazy migration was not applied during activate"


# ---------------------------------------------------------------------------
# D44: Activation clears deactivated_at
# ---------------------------------------------------------------------------


class TestActivateClearsDeactivatedAt:
    """Ensure activate() sets deactivated_at=None on the promoted draft."""

    @pytest.mark.asyncio
    async def test_activate_clears_deactivated_at(self) -> None:
        """After activation, the new active doc must have deactivated_at=None."""
        svc, prefs_repo, audit_repo, kb_repo, _ = _make_service()

        active_doc = _make_active_doc(PROFESSIONAL_TENANT_ID, version=1)
        draft_doc = _make_draft_doc(
            PROFESSIONAL_TENANT_ID, version=2,
            brand_name="Updated Brand", brand_voice="professional",
        )

        prefs_repo.get_active.return_value = active_doc
        prefs_repo.get_draft.return_value = draft_doc
        prefs_repo.get_previous.return_value = None
        prefs_repo.patch.return_value = None

        result = await svc.activate(PROFESSIONAL_TENANT_ID, TenantTier.PROFESSIONAL)
        assert result.success

        # Find the patch call that promotes draft → active
        promote_calls = [
            c for c in prefs_repo.patch.call_args_list
            if c.kwargs.get("document_id", "") == draft_doc["id"]
        ]
        assert len(promote_calls) >= 1
        ops = promote_calls[0].kwargs.get("operations", [])
        deact_ops = [op for op in ops if op.get("path") == "/deactivated_at"]
        assert len(deact_ops) == 1
        assert deact_ops[0]["value"] is None, "activate() must clear deactivated_at"


# ---------------------------------------------------------------------------
# D44: restore_previous clears deactivated_at
# ---------------------------------------------------------------------------


class TestRestorePreviousClearsDeactivatedAt:
    """Ensure restore_previous() sets deactivated_at=None on the promoted doc."""

    @pytest.mark.asyncio
    async def test_restore_clears_deactivated_at(self) -> None:
        """After roll back, the restored doc must have deactivated_at=None."""
        svc, prefs_repo, audit_repo, kb_repo, _ = _make_service()

        active_doc = _make_active_doc(PROFESSIONAL_TENANT_ID, version=2)
        active_doc["deactivated_at"] = "2026-02-15T12:00:00Z"

        previous_doc = _make_active_doc(PROFESSIONAL_TENANT_ID, version=1)
        previous_doc["id"] = f"prefs::{PROFESSIONAL_TENANT_ID}::previous"
        previous_doc["config_state"] = ConfigState.PREVIOUS.value

        prefs_repo.get_active.return_value = active_doc
        prefs_repo.get_previous.return_value = previous_doc
        prefs_repo.get_draft.return_value = None
        prefs_repo.patch.return_value = None

        result = await svc.restore_previous(
            PROFESSIONAL_TENANT_ID, TenantTier.PROFESSIONAL,
        )
        assert result.success

        # Find the patch call that promotes previous → active
        promote_calls = [
            c for c in prefs_repo.patch.call_args_list
            if c.kwargs.get("document_id", "") == previous_doc["id"]
        ]
        assert len(promote_calls) >= 1
        ops = promote_calls[0].kwargs.get("operations", [])
        deact_ops = [op for op in ops if op.get("path") == "/deactivated_at"]
        assert len(deact_ops) == 1
        assert deact_ops[0]["value"] is None, "restore_previous() must clear deactivated_at"


# ---------------------------------------------------------------------------
# D44: Deactivate endpoint
# ---------------------------------------------------------------------------


class TestDeactivateEndpoint:
    """Tests for POST /api/config/deactivate."""

    @pytest.mark.asyncio
    async def test_deactivate_sets_deactivated_at(self) -> None:
        """Deactivate patches the active doc with deactivated_at timestamp."""
        from src.multi_tenant.tenant_config_api import deactivate_config
        from src.multi_tenant.activation_service import ActivationService

        prefs_repo = AsyncMock()
        audit_repo = AsyncMock()
        active_doc = _make_active_doc(PROFESSIONAL_TENANT_ID, version=1)
        prefs_repo.get_active.return_value = active_doc
        prefs_repo.patch.return_value = None

        svc = ActivationService()
        svc.configure(prefs_repo, audit_repo)

        # Mock the get_activation_service and get_tenant_context
        ctx = MagicMock()
        ctx.tenant_id = PROFESSIONAL_TENANT_ID
        ctx.user_id = "admin"

        with patch("src.multi_tenant.tenant_config_api.get_activation_service", return_value=svc), \
             patch("src.multi_tenant.tenant_config_api.get_tenant_context", return_value=ctx):
            result = await deactivate_config(ctx=ctx)

        assert result["success"] is True
        assert "deactivated_at" in result

        # Verify patch was called with deactivated_at
        prefs_repo.patch.assert_called_once()
        patch_ops = prefs_repo.patch.call_args.kwargs.get("operations", [])
        deact_ops = [op for op in patch_ops if op.get("path") == "/deactivated_at"]
        assert len(deact_ops) == 1
        assert deact_ops[0]["value"] is not None

    @pytest.mark.asyncio
    async def test_deactivate_409_when_no_active_config(self) -> None:
        """Deactivate returns 409 when no active config exists."""
        from fastapi import HTTPException
        from src.multi_tenant.tenant_config_api import deactivate_config
        from src.multi_tenant.activation_service import ActivationService

        prefs_repo = AsyncMock()
        audit_repo = AsyncMock()
        prefs_repo.get_active.return_value = None

        svc = ActivationService()
        svc.configure(prefs_repo, audit_repo)

        ctx = MagicMock()
        ctx.tenant_id = PROFESSIONAL_TENANT_ID

        with patch("src.multi_tenant.tenant_config_api.get_activation_service", return_value=svc), \
             pytest.raises(HTTPException) as exc_info:
            await deactivate_config(ctx=ctx)

        assert exc_info.value.status_code == 409

    @pytest.mark.asyncio
    async def test_deactivate_409_when_already_deactivated(self) -> None:
        """Deactivate returns 409 when config is already deactivated."""
        from fastapi import HTTPException
        from src.multi_tenant.tenant_config_api import deactivate_config
        from src.multi_tenant.activation_service import ActivationService

        prefs_repo = AsyncMock()
        audit_repo = AsyncMock()
        active_doc = _make_active_doc(PROFESSIONAL_TENANT_ID, version=1)
        active_doc["deactivated_at"] = "2026-02-15T00:00:00Z"
        prefs_repo.get_active.return_value = active_doc

        svc = ActivationService()
        svc.configure(prefs_repo, audit_repo)

        ctx = MagicMock()
        ctx.tenant_id = PROFESSIONAL_TENANT_ID

        with patch("src.multi_tenant.tenant_config_api.get_activation_service", return_value=svc), \
             pytest.raises(HTTPException) as exc_info:
            await deactivate_config(ctx=ctx)

        assert exc_info.value.status_code == 409


# ---------------------------------------------------------------------------
# D44: Activation status is_active field
# ---------------------------------------------------------------------------


class TestActivationStatusIsActive:
    """Tests for the is_active field in activation-status response."""

    @pytest.mark.asyncio
    async def test_is_active_true_when_configured_and_not_deactivated(self) -> None:
        """is_active=True when config is activated and not deactivated."""
        from src.multi_tenant.tenant_config_api import get_activation_status
        from src.multi_tenant.activation_service import ActivationService

        prefs_repo = AsyncMock()
        audit_repo = AsyncMock()
        active_doc = _make_active_doc(PROFESSIONAL_TENANT_ID, version=1)
        # Ensure activated_at is set and no deactivated_at
        active_doc.pop("deactivated_at", None)

        draft_state = DraftState(
            has_pending_changes=False,
            active_version=1,
            active_activated_at="2026-02-15T00:00:00Z",
        )

        svc = ActivationService()
        svc.configure(prefs_repo, audit_repo)
        svc.get_draft_state = AsyncMock(return_value=draft_state)
        prefs_repo.get_active.return_value = active_doc

        ctx = MagicMock()
        ctx.tenant_id = PROFESSIONAL_TENANT_ID
        ctx.tier = TenantTier.PROFESSIONAL
        ctx.status = "active"

        with patch("src.multi_tenant.tenant_config_api.get_activation_service", return_value=svc), \
             patch("src.multi_tenant.tenant_config_api._resolve_tier", return_value=TenantTier.PROFESSIONAL):
            result = await get_activation_status(ctx=ctx)

        assert result.is_active is True
        assert result.is_configured is True

    @pytest.mark.asyncio
    async def test_is_active_false_when_deactivated(self) -> None:
        """is_active=False when config has deactivated_at set."""
        from src.multi_tenant.tenant_config_api import get_activation_status
        from src.multi_tenant.activation_service import ActivationService

        prefs_repo = AsyncMock()
        audit_repo = AsyncMock()
        active_doc = _make_active_doc(PROFESSIONAL_TENANT_ID, version=1)
        active_doc["deactivated_at"] = "2026-02-15T12:00:00Z"

        draft_state = DraftState(
            has_pending_changes=False,
            active_version=1,
            active_activated_at="2026-02-15T00:00:00Z",
        )

        svc = ActivationService()
        svc.configure(prefs_repo, audit_repo)
        svc.get_draft_state = AsyncMock(return_value=draft_state)
        prefs_repo.get_active.return_value = active_doc

        ctx = MagicMock()
        ctx.tenant_id = PROFESSIONAL_TENANT_ID
        ctx.tier = TenantTier.PROFESSIONAL
        ctx.status = "active"

        with patch("src.multi_tenant.tenant_config_api.get_activation_service", return_value=svc), \
             patch("src.multi_tenant.tenant_config_api._resolve_tier", return_value=TenantTier.PROFESSIONAL):
            result = await get_activation_status(ctx=ctx)

        assert result.is_active is False
        assert result.is_configured is True

    @pytest.mark.asyncio
    async def test_is_active_false_when_never_activated(self) -> None:
        """is_active=False when tenant has never activated."""
        from src.multi_tenant.tenant_config_api import get_activation_status
        from src.multi_tenant.activation_service import ActivationService

        prefs_repo = AsyncMock()
        audit_repo = AsyncMock()

        draft_state = DraftState(
            has_pending_changes=True,
            active_version=0,
            active_activated_at=None,
        )

        svc = ActivationService()
        svc.configure(prefs_repo, audit_repo)
        svc.get_draft_state = AsyncMock(return_value=draft_state)

        ctx = MagicMock()
        ctx.tenant_id = PROFESSIONAL_TENANT_ID
        ctx.tier = TenantTier.PROFESSIONAL
        ctx.status = "active"

        with patch("src.multi_tenant.tenant_config_api.get_activation_service", return_value=svc), \
             patch("src.multi_tenant.tenant_config_api._resolve_tier", return_value=TenantTier.PROFESSIONAL):
            result = await get_activation_status(ctx=ctx)

        assert result.is_active is False
        assert result.is_configured is False


# ---------------------------------------------------------------------------
# D44: Conversation creation gate
# ---------------------------------------------------------------------------


class TestConversationCreationGate:
    """Tests for the activation gate on POST /api/chat/conversations."""

    @pytest.mark.asyncio
    async def test_gate_blocks_when_never_activated(self) -> None:
        """403 returned when tenant has never activated config."""
        from fastapi import HTTPException
        from src.chat.endpoints import start_conversation
        from src.chat.models import ConversationStartRequest

        prefs_repo_mock = AsyncMock()
        prefs_repo_mock.get_active.return_value = None

        ctx = MagicMock()
        ctx.tenant_id = PROFESSIONAL_TENANT_ID
        ctx.tier = TenantTier.PROFESSIONAL

        req = ConversationStartRequest()

        with patch("src.chat.endpoints.PreferencesRepository", return_value=prefs_repo_mock), \
             pytest.raises(HTTPException) as exc_info:
            await start_conversation(request=req, ctx=ctx)

        assert exc_info.value.status_code == 403
        assert exc_info.value.detail["type"] == "not_active"

    @pytest.mark.asyncio
    async def test_gate_blocks_when_deactivated(self) -> None:
        """403 returned when tenant config is deactivated."""
        from fastapi import HTTPException
        from src.chat.endpoints import start_conversation
        from src.chat.models import ConversationStartRequest

        active_doc = _make_active_doc(PROFESSIONAL_TENANT_ID, version=1)
        active_doc["deactivated_at"] = "2026-02-15T12:00:00Z"

        prefs_repo_mock = AsyncMock()
        prefs_repo_mock.get_active.return_value = active_doc

        ctx = MagicMock()
        ctx.tenant_id = PROFESSIONAL_TENANT_ID
        ctx.tier = TenantTier.PROFESSIONAL

        req = ConversationStartRequest()

        with patch("src.chat.endpoints.PreferencesRepository", return_value=prefs_repo_mock), \
             pytest.raises(HTTPException) as exc_info:
            await start_conversation(request=req, ctx=ctx)

        assert exc_info.value.status_code == 403
        assert exc_info.value.detail["type"] == "not_active"

    @pytest.mark.asyncio
    async def test_gate_allows_when_active(self) -> None:
        """Conversation creation succeeds when tenant config is active."""
        from src.chat.endpoints import start_conversation
        from src.chat.models import ConversationStartRequest, ConversationStartResponse

        active_doc = _make_active_doc(PROFESSIONAL_TENANT_ID, version=1)
        active_doc.pop("deactivated_at", None)

        prefs_repo_mock = AsyncMock()
        prefs_repo_mock.get_active.return_value = active_doc

        mock_session = AsyncMock()
        mock_session.start_conversation.return_value = ConversationStartResponse(
            conversation_id="conv-123",
            stream_url="/api/chat/stream/conv-123",
            ws_url="/ws/chat/conv-123",
            created_at="2026-02-15T12:00:00Z",
        )

        ctx = MagicMock()
        ctx.tenant_id = PROFESSIONAL_TENANT_ID
        ctx.tier = TenantTier.PROFESSIONAL

        req = ConversationStartRequest()

        with patch("src.chat.endpoints.PreferencesRepository", return_value=prefs_repo_mock), \
             patch("src.chat.endpoints._get_session", return_value=mock_session):
            result = await start_conversation(request=req, ctx=ctx)

        assert result.conversation_id == "conv-123"
        mock_session.start_conversation.assert_called_once()
