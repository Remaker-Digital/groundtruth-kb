"""
Tests for TestModeService — controlled rollout engine (C2).

Covers:
    - Deterministic session assignment (SHA-256 bucket)
    - Test mode activation (AI behaviour field filtering)
    - Test mode deactivation (rollout vs abandon)
    - Percentage update
    - Config override application
    - Status retrieval
    - Edge cases (no repo, no processor, invalid fields)

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

from __future__ import annotations

import hashlib
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from src.multi_tenant.test_mode_service import (
    TestModeService,
    _AI_BEHAVIOR_FIELDS,
    get_test_mode_service,
)


# ---------------------------------------------------------------------------
# Deterministic session assignment
# ---------------------------------------------------------------------------


class TestSessionAssignment:
    """Tests for TestModeService.should_use_test_config()."""

    def test_zero_percentage_always_false(self):
        assert TestModeService.should_use_test_config("sess-1", 12345, 0) is False

    def test_100_percentage_always_true(self):
        assert TestModeService.should_use_test_config("sess-1", 12345, 100) is True

    def test_deterministic_same_input_same_result(self):
        r1 = TestModeService.should_use_test_config("sess-abc", 999, 50)
        r2 = TestModeService.should_use_test_config("sess-abc", 999, 50)
        assert r1 == r2

    def test_different_sessions_vary(self):
        """With enough sessions, both True and False should appear at 50%."""
        results = set()
        for i in range(200):
            r = TestModeService.should_use_test_config(f"sess-{i}", 42, 50)
            results.add(r)
            if len(results) == 2:
                break
        assert results == {True, False}

    def test_different_seeds_change_assignment(self):
        """Same session_id with different seeds may produce different results."""
        results = set()
        for seed in range(200):
            r = TestModeService.should_use_test_config("fixed-session", seed, 50)
            results.add(r)
            if len(results) == 2:
                break
        assert results == {True, False}

    def test_bucket_math_matches_manual_calculation(self):
        session_id = "test-session-xyz"
        seed = 54321
        digest = hashlib.sha256(f"{seed}:{session_id}".encode()).hexdigest()
        bucket = int(digest[:8], 16) % 100
        expected = bucket < 30
        assert TestModeService.should_use_test_config(session_id, seed, 30) is expected

    def test_negative_percentage_always_false(self):
        assert TestModeService.should_use_test_config("s", 1, -5) is False

    def test_distribution_roughly_correct(self):
        """10% routing should route ~10% of 1000 sessions."""
        count = sum(
            TestModeService.should_use_test_config(f"s-{i}", 777, 10)
            for i in range(1000)
        )
        # Allow generous tolerance (5-15%)
        assert 50 <= count <= 150, f"Expected ~100, got {count}"


# ---------------------------------------------------------------------------
# Activation
# ---------------------------------------------------------------------------


class TestActivate:
    """Tests for TestModeService.activate()."""

    @pytest.fixture()
    def service(self):
        svc = TestModeService()
        processor = AsyncMock()
        processor.update_config = AsyncMock(return_value=MagicMock(success=True))
        repo = AsyncMock()
        svc.configure(processor=processor, repo=repo)
        return svc, processor

    @pytest.mark.asyncio
    async def test_activate_valid_overrides(self, service):
        svc, processor = service
        result = await svc.activate(
            "t-1", "professional",
            overrides={"brand_voice": "friendly", "response_length": "concise"},
        )
        assert result["success"] is True
        assert result["override_count"] == 2
        assert result["rejected_fields"] == []
        processor.update_config.assert_called_once()
        call_kwargs = processor.update_config.call_args.kwargs
        updates = call_kwargs["updates"]
        assert updates["test_mode_enabled"] is True
        assert updates["test_mode_overrides"] == {
            "brand_voice": "friendly",
            "response_length": "concise",
        }

    @pytest.mark.asyncio
    async def test_activate_filters_non_ai_fields(self, service):
        svc, _ = service
        result = await svc.activate(
            "t-1", "professional",
            overrides={
                "brand_voice": "formal",
                "widget_position": "bottom-left",  # not AI behaviour
                "shopify_sync_enabled": True,       # not AI behaviour
            },
        )
        assert result["success"] is True
        assert result["override_count"] == 1
        assert sorted(result["rejected_fields"]) == [
            "shopify_sync_enabled", "widget_position",
        ]

    @pytest.mark.asyncio
    async def test_activate_no_valid_overrides_fails(self, service):
        svc, processor = service
        result = await svc.activate(
            "t-1", "professional",
            overrides={"widget_position": "top-right"},
        )
        assert result["success"] is False
        assert "allowed_fields" in result
        processor.update_config.assert_not_called()

    @pytest.mark.asyncio
    async def test_activate_clamps_percentage(self, service):
        svc, processor = service
        result = await svc.activate(
            "t-1", "starter",
            overrides={"brand_voice": "casual"},
            percentage=80,  # above max 50
        )
        assert result["success"] is True
        assert result["percentage"] == 50  # clamped

    @pytest.mark.asyncio
    async def test_activate_min_percentage(self, service):
        svc, processor = service
        result = await svc.activate(
            "t-1", "starter",
            overrides={"brand_voice": "casual"},
            percentage=0,
        )
        assert result["success"] is True
        assert result["percentage"] == 1  # clamped to min

    @pytest.mark.asyncio
    async def test_activate_generates_seed(self, service):
        svc, processor = service
        result = await svc.activate(
            "t-1", "starter",
            overrides={"formality_level": "formal"},
        )
        assert 100_000 <= result["seed"] <= 999_999

    @pytest.mark.asyncio
    async def test_activate_without_processor(self):
        svc = TestModeService()
        # No configure() call — processor is None
        result = await svc.activate(
            "t-1", "starter",
            overrides={"brand_voice": "friendly"},
        )
        # Should still succeed (just can't persist)
        assert result["success"] is True


# ---------------------------------------------------------------------------
# Deactivation
# ---------------------------------------------------------------------------


class TestDeactivate:
    """Tests for TestModeService.deactivate()."""

    @pytest.fixture()
    def service_with_active_test(self):
        svc = TestModeService()
        processor = AsyncMock()
        processor.update_config = AsyncMock(return_value=MagicMock(success=True))
        repo = AsyncMock()
        repo.get_current = AsyncMock(return_value={
            "test_mode_enabled": True,
            "test_mode_percentage": 20,
            "test_mode_overrides": {"brand_voice": "formal", "response_length": "brief"},
            "test_mode_assignment_seed": 123456,
        })
        svc.configure(processor=processor, repo=repo)
        return svc, processor, repo

    @pytest.mark.asyncio
    async def test_rollout_merges_overrides(self, service_with_active_test):
        svc, processor, _ = service_with_active_test
        result = await svc.deactivate("t-1", "professional", action="rollout")
        assert result["success"] is True
        assert result["action"] == "rollout"
        assert sorted(result["merged_fields"]) == ["brand_voice", "response_length"]
        call_kwargs = processor.update_config.call_args.kwargs
        updates = call_kwargs["updates"]
        assert updates["brand_voice"] == "formal"
        assert updates["response_length"] == "brief"
        assert updates["test_mode_enabled"] is False

    @pytest.mark.asyncio
    async def test_abandon_discards_overrides(self, service_with_active_test):
        svc, processor, _ = service_with_active_test
        result = await svc.deactivate("t-1", "professional", action="abandon")
        assert result["success"] is True
        assert result["action"] == "abandon"
        assert sorted(result["discarded_fields"]) == ["brand_voice", "response_length"]
        call_kwargs = processor.update_config.call_args.kwargs
        updates = call_kwargs["updates"]
        assert updates["test_mode_enabled"] is False
        assert "brand_voice" not in updates

    @pytest.mark.asyncio
    async def test_deactivate_when_not_active(self, service_with_active_test):
        svc, _, repo = service_with_active_test
        repo.get_current = AsyncMock(return_value={
            "test_mode_enabled": False,
        })
        result = await svc.deactivate("t-1", "professional")
        assert result["success"] is False
        assert "not active" in result["error"]

    @pytest.mark.asyncio
    async def test_deactivate_no_config_found(self, service_with_active_test):
        svc, _, repo = service_with_active_test
        repo.get_current = AsyncMock(return_value=None)
        result = await svc.deactivate("t-1", "professional")
        assert result["success"] is False
        assert "No config" in result["error"]

    @pytest.mark.asyncio
    async def test_deactivate_no_repo(self):
        svc = TestModeService()
        result = await svc.deactivate("t-1", "starter")
        assert result["success"] is False


# ---------------------------------------------------------------------------
# Update percentage
# ---------------------------------------------------------------------------


class TestUpdatePercentage:

    @pytest.mark.asyncio
    async def test_update_percentage(self):
        svc = TestModeService()
        processor = AsyncMock()
        processor.update_config = AsyncMock(return_value=MagicMock(success=True))
        svc.configure(processor=processor)
        result = await svc.update_percentage("t-1", "starter", 25)
        assert result["success"] is True
        assert result["percentage"] == 25

    @pytest.mark.asyncio
    async def test_update_percentage_clamps_max(self):
        svc = TestModeService()
        processor = AsyncMock()
        processor.update_config = AsyncMock(return_value=MagicMock(success=True))
        svc.configure(processor=processor)
        result = await svc.update_percentage("t-1", "starter", 99)
        assert result["percentage"] == 50

    @pytest.mark.asyncio
    async def test_update_percentage_clamps_min(self):
        svc = TestModeService()
        processor = AsyncMock()
        processor.update_config = AsyncMock(return_value=MagicMock(success=True))
        svc.configure(processor=processor)
        result = await svc.update_percentage("t-1", "starter", -5)
        assert result["percentage"] == 1


# ---------------------------------------------------------------------------
# Config override application
# ---------------------------------------------------------------------------


class TestApplyOverrides:

    def test_apply_overrides_merges(self):
        svc = TestModeService()
        config = {"brand_voice": "neutral", "widget_position": "bottom-right", "response_length": "standard"}
        overrides = {"brand_voice": "formal", "response_length": "brief"}
        result = svc.apply_test_overrides(config, overrides)
        assert result["brand_voice"] == "formal"
        assert result["response_length"] == "brief"
        assert result["widget_position"] == "bottom-right"  # unchanged

    def test_apply_overrides_does_not_mutate_original(self):
        svc = TestModeService()
        config = {"brand_voice": "neutral"}
        overrides = {"brand_voice": "formal"}
        result = svc.apply_test_overrides(config, overrides)
        assert config["brand_voice"] == "neutral"
        assert result["brand_voice"] == "formal"

    def test_apply_overrides_filters_non_ai_fields(self):
        svc = TestModeService()
        config = {"brand_voice": "neutral", "widget_position": "bottom-right"}
        overrides = {"brand_voice": "formal", "widget_position": "top-left"}
        result = svc.apply_test_overrides(config, overrides)
        assert result["brand_voice"] == "formal"
        assert result["widget_position"] == "bottom-right"  # NOT overridden

    def test_apply_overrides_empty_overrides(self):
        svc = TestModeService()
        config = {"brand_voice": "neutral"}
        result = svc.apply_test_overrides(config, {})
        assert result == config


# ---------------------------------------------------------------------------
# Status
# ---------------------------------------------------------------------------


class TestGetStatus:

    @pytest.mark.asyncio
    async def test_status_when_enabled(self):
        svc = TestModeService()
        repo = AsyncMock()
        repo.get_current = AsyncMock(return_value={
            "test_mode_enabled": True,
            "test_mode_percentage": 15,
            "test_mode_overrides": {"brand_voice": "formal"},
            "test_mode_assignment_seed": 654321,
            "test_mode_activated_at": "2026-02-01T12:00:00Z",
        })
        svc.configure(repo=repo)
        status = await svc.get_status("t-1")
        assert status["enabled"] is True
        assert status["percentage"] == 15
        assert status["override_field_count"] == 1

    @pytest.mark.asyncio
    async def test_status_when_disabled(self):
        svc = TestModeService()
        repo = AsyncMock()
        repo.get_current = AsyncMock(return_value={
            "test_mode_enabled": False,
        })
        svc.configure(repo=repo)
        status = await svc.get_status("t-1")
        assert status["enabled"] is False

    @pytest.mark.asyncio
    async def test_status_no_repo(self):
        svc = TestModeService()
        status = await svc.get_status("t-1")
        assert status["enabled"] is False

    @pytest.mark.asyncio
    async def test_status_no_document(self):
        svc = TestModeService()
        repo = AsyncMock()
        repo.get_current = AsyncMock(return_value=None)
        svc.configure(repo=repo)
        status = await svc.get_status("t-1")
        assert status["enabled"] is False


# ---------------------------------------------------------------------------
# AI behaviour fields constant
# ---------------------------------------------------------------------------


class TestAIBehaviorFields:

    def test_ai_fields_are_frozenset(self):
        assert isinstance(_AI_BEHAVIOR_FIELDS, frozenset)

    def test_expected_fields_present(self):
        expected = {
            "brand_voice", "response_length", "formality_level",
            "escalation_threshold", "escalation_keywords",
            "custom_instructions", "memory_enabled",
            "retrieval_top_k", "retrieval_vector_weight",
            "retrieval_bm25_weight", "retrieval_min_score",
            "intent_source_mapping", "cite_sources_in_response",
        }
        assert expected == _AI_BEHAVIOR_FIELDS

    def test_widget_fields_not_in_ai_behavior(self):
        widget_fields = {
            "widget_position", "widget_theme", "widget_brand_color",
            "launcher_icon", "launcher_style",
        }
        assert widget_fields.isdisjoint(_AI_BEHAVIOR_FIELDS)


# ---------------------------------------------------------------------------
# Singleton
# ---------------------------------------------------------------------------


class TestSingleton:

    def test_singleton_returns_same_instance(self):
        s1 = get_test_mode_service()
        s2 = get_test_mode_service()
        assert s1 is s2

    def test_singleton_is_test_mode_service(self):
        svc = get_test_mode_service()
        assert isinstance(svc, TestModeService)
