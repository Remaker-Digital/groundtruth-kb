"""Slice 0d: S249 seed_tenant.py --preset script path behavioral tests.

Exercises PresetService and phase_3b_preset behavior through real function calls
with mocked external dependencies (Cosmos, Azure, HTTP).

Test plan ref: COMPREHENSIVE-TEST-PLAN-S245-S255.md Slice 0d

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

from __future__ import annotations

import os
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

# Ensure SEED_FQDN is set before importing seed_tenant
os.environ.setdefault("SEED_FQDN", "http://localhost:8000")


# ── PresetService behavioral tests ────────────────────────────────

class TestPresetServiceBehavior:
    """Behavioral tests exercising the real PresetService."""

    def test_list_presets_returns_at_least_one(self):
        from src.presets.preset_service import PresetService
        svc = PresetService()
        presets = svc.list_presets()
        assert len(presets) >= 1

    def test_list_presets_includes_knowledge_only(self):
        from src.presets.preset_service import PresetService
        svc = PresetService()
        presets = svc.list_presets()
        preset_ids = [
            p.id if hasattr(p, "id") else p.get("id", "")
            for p in presets
        ]
        assert "knowledge_only" in preset_ids

    def test_get_preset_unknown_returns_none(self):
        from src.presets.preset_service import PresetService
        svc = PresetService()
        result = svc.get_preset("nonexistent_xyz_999")
        assert result is None

    def test_get_preset_valid_returns_preset(self):
        from src.presets.preset_service import PresetService
        svc = PresetService()
        result = svc.get_preset("knowledge_only")
        assert result is not None
        config_fields = (
            result.config_fields if hasattr(result, "config_fields")
            else result.get("config_fields", {})
        )
        assert isinstance(config_fields, dict)


# ── phase_3b_preset behavioral tests ─────────────────────────────

class TestPhase3bPresetBehavior:
    """Behavioral tests for the phase_3b_preset function."""

    @pytest.mark.asyncio
    async def test_no_preset_skips(self):
        """No preset_id -> SKIP status."""
        from scripts.seed_tenant import phase_3b_preset, phase_results
        await phase_3b_preset(dry_run=False, preset_id=None)

        assert "3b_preset" in phase_results
        assert "SKIP" in str(phase_results["3b_preset"]).upper()

    @pytest.mark.asyncio
    async def test_unknown_preset_errors(self):
        """Unknown preset ID -> ERROR status."""
        from scripts.seed_tenant import phase_3b_preset, phase_results
        await phase_3b_preset(dry_run=False, preset_id="totally_invalid_preset_xyz")

        assert "3b_preset" in phase_results
        assert "ERROR" in str(phase_results["3b_preset"]).upper()

    @pytest.mark.asyncio
    async def test_dry_run_records_dry_run_status(self):
        """Dry run with valid preset -> DRY RUN status, no repo access."""
        from scripts.seed_tenant import phase_3b_preset, phase_results
        await phase_3b_preset(dry_run=True, preset_id="knowledge_only")

        assert "3b_preset" in phase_results
        result = str(phase_results["3b_preset"])
        assert "DRY RUN" in result
        assert "knowledge_only" in result

    @pytest.mark.asyncio
    async def test_missing_draft_preferences_errors(self):
        """Success path with None preferences -> ERROR: no preferences document."""
        from scripts.seed_tenant import phase_3b_preset, phase_results

        mock_repo = AsyncMock()
        mock_repo.get_draft = AsyncMock(return_value=None)

        # PreferencesRepository is imported inside phase_3b_preset via local import
        with patch("src.multi_tenant.repository.PreferencesRepository", return_value=mock_repo):
            await phase_3b_preset(dry_run=False, preset_id="knowledge_only")

        assert "3b_preset" in phase_results
        result = str(phase_results["3b_preset"])
        assert "ERROR" in result
        assert "preferences" in result.lower()

    @pytest.mark.asyncio
    async def test_success_path_merges_config_and_records_ok(self):
        """Success path with valid preset + existing prefs -> OK status.

        Patches PreferencesRepository at its source module so the local
        import inside phase_3b_preset picks up the mock. Also patches
        downstream repos (KB, overlays, bindings) at their source modules.
        """
        from scripts.seed_tenant import phase_3b_preset, phase_results

        mock_prefs = {
            "id": "prefs-test",
            "partition_key": "remaker-digital-001",
            "tenant_id": "remaker-digital-001",
            "version": 1,
            "created_at": "2026-01-01T00:00:00Z",
            "_etag": "etag-1",
            "quick_actions": [],
        }
        mock_repo = AsyncMock()
        mock_repo.get_draft = AsyncMock(return_value=mock_prefs.copy())
        mock_repo.upsert = AsyncMock()

        mock_kb_repo = AsyncMock()
        mock_kb_repo.create_item = AsyncMock()

        mock_overlay_repo = AsyncMock()
        mock_overlay_repo.get_overlay = AsyncMock(return_value=None)
        mock_overlay_repo.upsert_overlay = AsyncMock()

        mock_binding_repo = AsyncMock()
        mock_binding_repo.get_binding = AsyncMock(return_value=None)
        mock_binding_repo.upsert_binding = AsyncMock()

        with patch("src.multi_tenant.repository.PreferencesRepository", return_value=mock_repo), \
             patch("src.multi_tenant.repositories.knowledge.KnowledgeBaseRepository", return_value=mock_kb_repo), \
             patch("src.agents.plugins.bindings.SkillBindingService") as mock_sbs, \
             patch("src.agents.plugins.overlay.clear_resolution_cache", MagicMock()), \
             patch("src.multi_tenant.repositories.agent_overlays.TenantAgentOverlayRepository", return_value=mock_overlay_repo), \
             patch("src.multi_tenant.repositories.agent_bindings.AgentSkillBindingRepository", return_value=mock_binding_repo):
            mock_sbs_instance = MagicMock()
            mock_sbs.get_instance.return_value = mock_sbs_instance

            await phase_3b_preset(dry_run=False, preset_id="knowledge_only")

        assert "3b_preset" in phase_results
        result = str(phase_results["3b_preset"])
        assert "OK" in result
        assert "knowledge_only" in result
        mock_repo.get_draft.assert_awaited_once()
