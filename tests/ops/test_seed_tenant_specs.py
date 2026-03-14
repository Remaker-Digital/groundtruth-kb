"""Tests for scripts/seed_tenant.py — 26 OPS specs (SPEC-1430..1455).

Covers seed script structure, constants, phase functions, orchestration order,
dry-run behavior, phase headers, and argument parsing. No database connections
are made; all tests operate via import inspection and dry-run execution.

Specs covered:
  SPEC-1430: seed_tenant 0: partition cleanup — all tenant docs deleted before
  SPEC-1431: seed_tenant 0: deletes all docs including conversations (--demo flag note)
  SPEC-1432: seed_tenant 5: (KB article seeding) was removed in S26. Initialization yields zero articles
  SPEC-1433: seed_tenant 0: Clean tenant partition (delete all existing documents)
  SPEC-1434: seed_tenant 1: (containers exist) but is listed
  SPEC-1435: seed_tenant 0: conceptually precedes data creation
  SPEC-1436: seed_tenant 0: phase header "Clean Tenant Partition"
  SPEC-1437: seed_tenant 1: Create Cosmos DB containers
  SPEC-1438: seed_tenant 1: phase header "Cosmos DB Containers"
  SPEC-1439: seed_tenant 2: Create tenant document
  SPEC-1440: seed_tenant 2: phase header "Tenant Document"
  SPEC-1441: seed_tenant 3: Create preferences document
  SPEC-1442: seed_tenant 3: phase header "Preferences (Draft — merchant fields empty)"
  SPEC-1443: seed_tenant 2: widget key (required for activation)
  SPEC-1444: seed_tenant 4: Create team members
  SPEC-1445: seed_tenant 4: phase header "Team Members"
  SPEC-1446: seed_tenant 5: Seed knowledge base
  SPEC-1447: seed_tenant 5: phase header "Knowledge Base"
  SPEC-1448: seed_tenant 6: Platform config (tier defaults)
  SPEC-1449: seed_tenant 6: phase header "Platform Config (Tier Defaults)"
  SPEC-1450: seed_tenant 7: Demo data (optional)
  SPEC-1451: seed_tenant 7: phase header "Demo Data"
  SPEC-1452: seed_tenant 8: SEED SUMMARY
  SPEC-1453: seed_tenant results: print separator
  SPEC-1454: seed_tenant 5: (KB articles) removed — initialization yields zero articles
  SPEC-1455: seed_tenant 4: runs AFTER demo data so superadmin with API key hash overwrites

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

from __future__ import annotations

import asyncio
import inspect
import io
import sys
import textwrap
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

# ---------------------------------------------------------------------------
# Ensure project root is on sys.path so `scripts.seed_tenant` is importable
# ---------------------------------------------------------------------------
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


# ---------------------------------------------------------------------------
# Lazy import helper — seed_tenant triggers `load_env_local()` at import time.
# We mock it so tests don't depend on .env.local existing.
# ---------------------------------------------------------------------------

_seed_module = None


def _get_seed():
    """Lazy-import scripts.seed_tenant with env loading neutralized."""
    global _seed_module
    if _seed_module is not None:
        return _seed_module
    # Ensure minimal env vars so import-time code doesn't fail
    import os
    os.environ.setdefault("COSMOS_DB_ENDPOINT", "https://localhost:8081")
    os.environ.setdefault("COSMOS_DB_KEY", "dummykey==")
    os.environ.setdefault("COSMOS_DB_DATABASE", "agentred")
    import scripts.seed_tenant as mod
    _seed_module = mod
    return mod


# ---------------------------------------------------------------------------
# Constants tests
# ---------------------------------------------------------------------------

class TestConstants:
    """Verify module-level constants match specification expectations."""

    def test_tenant_containers_count(self):
        """TENANT_CONTAINERS has exactly 9 container names."""
        seed = _get_seed()
        assert len(seed.TENANT_CONTAINERS) == 9

    def test_tenant_containers_includes_conversations(self):
        """SPEC-1431: conversations container is in the cleanup list."""
        seed = _get_seed()
        assert "conversations" in seed.TENANT_CONTAINERS

    def test_tenant_containers_are_strings(self):
        """Every entry in TENANT_CONTAINERS is a non-empty string."""
        seed = _get_seed()
        for name in seed.TENANT_CONTAINERS:
            assert isinstance(name, str) and len(name) > 0

    def test_team_members_has_one_entry(self):
        """TEAM_MEMBERS contains exactly 1 member."""
        seed = _get_seed()
        assert len(seed.TEAM_MEMBERS) == 1

    def test_team_member_is_superadmin(self):
        """The sole team member has role 'superadmin'."""
        seed = _get_seed()
        assert seed.TEAM_MEMBERS[0]["role"] == "superadmin"

    def test_quick_actions_count(self):
        """QUICK_ACTIONS contains exactly 4 actions."""
        seed = _get_seed()
        assert len(seed.QUICK_ACTIONS) == 4

    def test_quick_action_labels(self):
        """The 4 quick actions have the expected labels."""
        seed = _get_seed()
        labels = [qa["label"] for qa in seed.QUICK_ACTIONS]
        assert "Track my order" in labels
        assert "Return or exchange" in labels
        assert "Product question" in labels
        assert "Shipping info" in labels

    def test_default_tenant_id(self):
        """Default TENANT_ID is 'remaker-digital-001'."""
        seed = _get_seed()
        assert seed.TENANT_ID == "remaker-digital-001"


# ---------------------------------------------------------------------------
# Phase function existence and async signature tests
# ---------------------------------------------------------------------------

class TestPhaseFunctions:
    """Verify all phase functions exist and have correct signatures."""

    def test_phase_0_exists_and_is_async(self):
        """SPEC-1433: phase_0_clean_partition is defined and async."""
        seed = _get_seed()
        assert hasattr(seed, "phase_0_clean_partition")
        assert inspect.iscoroutinefunction(seed.phase_0_clean_partition)

    def test_phase_1_exists_and_is_async(self):
        """SPEC-1437: phase_1_containers is defined and async."""
        seed = _get_seed()
        assert hasattr(seed, "phase_1_containers")
        assert inspect.iscoroutinefunction(seed.phase_1_containers)

    def test_phase_2_exists_and_is_async(self):
        """SPEC-1439: phase_2_tenant is defined and async."""
        seed = _get_seed()
        assert hasattr(seed, "phase_2_tenant")
        assert inspect.iscoroutinefunction(seed.phase_2_tenant)

    def test_phase_3_exists_and_is_async(self):
        """SPEC-1441: phase_3_preferences is defined and async."""
        seed = _get_seed()
        assert hasattr(seed, "phase_3_preferences")
        assert inspect.iscoroutinefunction(seed.phase_3_preferences)

    def test_phase_4_exists_and_is_async(self):
        """SPEC-1444: phase_4_team is defined and async."""
        seed = _get_seed()
        assert hasattr(seed, "phase_4_team")
        assert inspect.iscoroutinefunction(seed.phase_4_team)

    def test_phase_5_exists_and_is_async(self):
        """SPEC-1446: phase_5_knowledge_base is defined and async."""
        seed = _get_seed()
        assert hasattr(seed, "phase_5_knowledge_base")
        assert inspect.iscoroutinefunction(seed.phase_5_knowledge_base)

    def test_phase_6_exists_and_is_async(self):
        """SPEC-1448: phase_6_platform_config is defined and async."""
        seed = _get_seed()
        assert hasattr(seed, "phase_6_platform_config")
        assert inspect.iscoroutinefunction(seed.phase_6_platform_config)

    def test_phase_7_exists_and_is_async(self):
        """SPEC-1450: phase_7_demo_data is defined and async."""
        seed = _get_seed()
        assert hasattr(seed, "phase_7_demo_data")
        assert inspect.iscoroutinefunction(seed.phase_7_demo_data)

    def test_phase_8_exists_and_is_sync(self):
        """SPEC-1452: phase_8_summary is defined and is NOT async (sync)."""
        seed = _get_seed()
        assert hasattr(seed, "phase_8_summary")
        assert not inspect.iscoroutinefunction(seed.phase_8_summary)

    def test_seed_function_exists_and_is_async(self):
        """The main seed() orchestrator is defined and async."""
        seed = _get_seed()
        assert hasattr(seed, "seed")
        assert inspect.iscoroutinefunction(seed.seed)


# ---------------------------------------------------------------------------
# Phase header output tests (dry-run captures stdout)
# ---------------------------------------------------------------------------

class TestPhaseHeaders:
    """Verify phase functions print the correct header text."""

    def _run_and_capture(self, coro) -> str:
        """Run an async coroutine and capture its stdout."""
        buf = io.StringIO()
        old_stdout = sys.stdout
        sys.stdout = buf
        try:
            asyncio.get_event_loop().run_until_complete(coro)
        except RuntimeError:
            # No running event loop — create a new one
            loop = asyncio.new_event_loop()
            try:
                loop.run_until_complete(coro)
            finally:
                loop.close()
        finally:
            sys.stdout = old_stdout
        return buf.getvalue()

    def test_phase_0_header(self):
        """SPEC-1436: Phase 0 prints 'Clean Tenant Partition'."""
        seed = _get_seed()
        seed.phase_results.clear()
        output = self._run_and_capture(seed.phase_0_clean_partition(dry_run=True))
        assert "Clean Tenant Partition" in output

    def test_phase_1_header(self):
        """SPEC-1438: Phase 1 prints 'Cosmos DB Containers'."""
        seed = _get_seed()
        seed.phase_results.clear()
        # phase_1 imports get_collection_configs — mock it for dry_run
        mock_configs = [
            MagicMock(name=f"container_{i}", partition_key="/tenant_id")
            for i in range(10)
        ]
        with patch("scripts.seed_tenant.get_collection_configs", return_value=mock_configs, create=True):
            # The function imports get_collection_configs inside — we need to patch where it's used
            from unittest.mock import patch as _patch
            with _patch.dict("sys.modules", {
                "src.multi_tenant.cosmos_schema": MagicMock(
                    get_collection_configs=MagicMock(return_value=mock_configs)
                ),
            }):
                output = self._run_and_capture(seed.phase_1_containers(dry_run=True))
        assert "Cosmos DB Containers" in output

    def test_phase_2_header(self):
        """SPEC-1440: Phase 2 prints 'Tenant Document'."""
        seed = _get_seed()
        seed.phase_results.clear()
        seed.generated_credentials.clear()
        with patch.dict("sys.modules", {
            "src.multi_tenant.auth": MagicMock(
                generate_widget_key=MagicMock(return_value="pk_test_1234_abcd"),
                hash_api_key=MagicMock(return_value="hash1"),
                hash_widget_key=MagicMock(return_value="hash2"),
            ),
            "src.multi_tenant.cosmos_schema": MagicMock(
                BillingChannel=MagicMock(side_effect=lambda x: x),
                ConsentStatus=MagicMock(GRANTED="granted"),
                TenantDocument=MagicMock(return_value=MagicMock()),
                TenantStatus=MagicMock(ACTIVE="active"),
                TenantTier=MagicMock(side_effect=lambda x: x),
            ),
        }):
            output = self._run_and_capture(seed.phase_2_tenant(dry_run=True))
        assert "Tenant Document" in output

    def test_phase_3_header(self):
        """SPEC-1442: Phase 3 prints 'Preferences (Draft'."""
        seed = _get_seed()
        seed.phase_results.clear()
        seed.generated_credentials["widget_key"] = "pk_test_dummy_key"
        with patch.dict("sys.modules", {
            "src.multi_tenant.cosmos_schema": MagicMock(
                PreferencesDocument=MagicMock(return_value=MagicMock(
                    brand_name="",
                    config_state="draft",
                    widget_primary_color="#ff3621",
                )),
            ),
        }):
            output = self._run_and_capture(seed.phase_3_preferences(dry_run=True))
        assert "Preferences (Draft" in output

    def test_phase_4_header(self):
        """SPEC-1445: Phase 4 prints 'Team Members'."""
        seed = _get_seed()
        seed.phase_results.clear()
        with patch.dict("sys.modules", {
            "src.multi_tenant.auth": MagicMock(
                generate_user_api_key=MagicMock(return_value="ar_user_test_12345678"),
                hash_api_key=MagicMock(return_value="hash1"),
            ),
            "src.multi_tenant.cosmos_schema": MagicMock(
                TeamMemberDocument=MagicMock(return_value=MagicMock()),
                TeamMemberRole=MagicMock(
                    SUPERADMIN="superadmin",
                    ADMIN="admin",
                    ESCALATION_AGENT="escalation_agent",
                    VIEWER="viewer",
                ),
            ),
        }):
            output = self._run_and_capture(seed.phase_4_team(dry_run=True))
        assert "Team Members" in output

    def test_phase_5_header(self):
        """SPEC-1447: Phase 5 prints 'Knowledge Base'."""
        seed = _get_seed()
        seed.phase_results.clear()
        with patch.dict("sys.modules", {
            "scripts.seed_knowledge_base": MagicMock(
                TOTAL_ARTICLES=0,
                load_to_cosmos=AsyncMock(),
            ),
        }):
            output = self._run_and_capture(seed.phase_5_knowledge_base(dry_run=True, embed=False))
        assert "Knowledge Base" in output

    def test_phase_6_header(self):
        """SPEC-1449: Phase 6 prints 'Platform Config (Tier Defaults)'."""
        seed = _get_seed()
        seed.phase_results.clear()
        mock_tier_defaults = {
            "starter": {"included_conversations": 1000, "rate_limit_rpm": 500},
            "professional": {"included_conversations": 5000, "rate_limit_rpm": 500},
            "business": {"included_conversations": 25000, "rate_limit_rpm": 500},
            "enterprise": {"included_conversations": 100000, "rate_limit_rpm": 500},
        }
        with patch.dict("sys.modules", {
            "src.multi_tenant.cosmos_schema": MagicMock(
                TIER_DEFAULTS=mock_tier_defaults,
                PlatformConfigDocument=MagicMock(return_value=MagicMock()),
            ),
        }):
            output = self._run_and_capture(seed.phase_6_platform_config(dry_run=True))
        assert "Platform Config (Tier Defaults)" in output

    def test_phase_7_header(self):
        """SPEC-1451: Phase 7 prints 'Demo Data'."""
        seed = _get_seed()
        seed.phase_results.clear()
        output = self._run_and_capture(seed.phase_7_demo_data(dry_run=True, demo=False))
        assert "Demo Data" in output

    def test_phase_8_header(self):
        """SPEC-1452: Phase 8 prints 'SEED SUMMARY'."""
        seed = _get_seed()
        seed.phase_results.clear()
        seed.generated_credentials.clear()
        buf = io.StringIO()
        old_stdout = sys.stdout
        sys.stdout = buf
        try:
            seed.phase_8_summary()
        finally:
            sys.stdout = old_stdout
        output = buf.getvalue()
        assert "SEED SUMMARY" in output


# ---------------------------------------------------------------------------
# Dry-run behavior tests
# ---------------------------------------------------------------------------

class TestDryRunBehavior:
    """Verify phase functions update phase_results correctly in dry-run mode."""

    def _run(self, coro):
        """Run coroutine, suppress stdout."""
        buf = io.StringIO()
        old_stdout = sys.stdout
        sys.stdout = buf
        try:
            loop = asyncio.new_event_loop()
            loop.run_until_complete(coro)
            loop.close()
        finally:
            sys.stdout = old_stdout

    def test_phase_0_dry_run_result(self):
        """SPEC-1430/1433: phase_0 dry-run sets phase_results with 'DRY RUN'."""
        seed = _get_seed()
        seed.phase_results.clear()
        self._run(seed.phase_0_clean_partition(dry_run=True))
        assert "0_clean_partition" in seed.phase_results
        assert "DRY RUN" in seed.phase_results["0_clean_partition"]

    def test_phase_0_dry_run_mentions_container_count(self):
        """SPEC-1430: phase_0 dry-run result includes container count."""
        seed = _get_seed()
        seed.phase_results.clear()
        self._run(seed.phase_0_clean_partition(dry_run=True))
        assert "9 containers" in seed.phase_results["0_clean_partition"]

    def test_phase_0_prints_dry_run_for_each_container(self):
        """SPEC-1431: phase_0 dry-run prints DRY RUN line for each container."""
        seed = _get_seed()
        seed.phase_results.clear()
        buf = io.StringIO()
        old_stdout = sys.stdout
        sys.stdout = buf
        try:
            loop = asyncio.new_event_loop()
            loop.run_until_complete(seed.phase_0_clean_partition(dry_run=True))
            loop.close()
        finally:
            sys.stdout = old_stdout
        output = buf.getvalue()
        dry_run_lines = [line for line in output.splitlines() if "DRY RUN" in line]
        assert len(dry_run_lines) == len(seed.TENANT_CONTAINERS)

    def test_phase_7_skip_without_demo_flag(self):
        """SPEC-1450: phase_7 skips when demo=False."""
        seed = _get_seed()
        seed.phase_results.clear()
        self._run(seed.phase_7_demo_data(dry_run=True, demo=False))
        assert "7_demo_data" in seed.phase_results
        assert "SKIPPED" in seed.phase_results["7_demo_data"]

    def test_phase_7_dry_run_with_demo_flag(self):
        """SPEC-1450: phase_7 dry-run with demo=True sets DRY RUN."""
        seed = _get_seed()
        seed.phase_results.clear()
        self._run(seed.phase_7_demo_data(dry_run=True, demo=True))
        assert "7_demo_data" in seed.phase_results
        assert "DRY RUN" in seed.phase_results["7_demo_data"]


# ---------------------------------------------------------------------------
# Orchestrator order tests
# ---------------------------------------------------------------------------

class TestOrchestratorOrder:
    """Verify seed() calls phases in the correct order."""

    def test_seed_calls_phases_in_correct_order(self):
        """SPEC-1434/1435/1455: seed() calls phase 1 first, then 0, 2, 3, 6, 7, 4, 8."""
        seed = _get_seed()
        call_order = []

        async def mock_phase_1(dry_run):
            call_order.append("phase_1")

        async def mock_phase_0(dry_run):
            call_order.append("phase_0")

        async def mock_phase_2(dry_run):
            call_order.append("phase_2")

        async def mock_phase_3(dry_run):
            call_order.append("phase_3")

        async def mock_phase_6(dry_run):
            call_order.append("phase_6")

        async def mock_phase_7(dry_run, demo):
            call_order.append("phase_7")

        async def mock_phase_4(dry_run):
            call_order.append("phase_4")

        def mock_phase_8():
            call_order.append("phase_8")

        with patch.object(seed, "phase_1_containers", mock_phase_1), \
             patch.object(seed, "phase_0_clean_partition", mock_phase_0), \
             patch.object(seed, "phase_2_tenant", mock_phase_2), \
             patch.object(seed, "phase_3_preferences", mock_phase_3), \
             patch.object(seed, "phase_6_platform_config", mock_phase_6), \
             patch.object(seed, "phase_7_demo_data", mock_phase_7), \
             patch.object(seed, "phase_4_team", mock_phase_4), \
             patch.object(seed, "phase_8_summary", mock_phase_8):
            loop = asyncio.new_event_loop()
            loop.run_until_complete(seed.seed(dry_run=True))
            loop.close()

        expected = ["phase_1", "phase_0", "phase_2", "phase_3", "phase_6", "phase_7", "phase_4", "phase_8"]
        assert call_order == expected, f"Expected {expected}, got {call_order}"

    def test_phase_4_runs_after_phase_7(self):
        """SPEC-1455: phase_4 (team) runs AFTER phase_7 (demo data)."""
        seed = _get_seed()
        call_order = []

        async def track_phase_4(dry_run):
            call_order.append("phase_4")

        async def track_phase_7(dry_run, demo):
            call_order.append("phase_7")

        # Patch only phase 4 and 7, let others be no-ops
        async def noop_async(*args, **kwargs):
            pass

        def noop_sync(*args, **kwargs):
            pass

        with patch.object(seed, "phase_1_containers", noop_async), \
             patch.object(seed, "phase_0_clean_partition", noop_async), \
             patch.object(seed, "phase_2_tenant", noop_async), \
             patch.object(seed, "phase_3_preferences", noop_async), \
             patch.object(seed, "phase_6_platform_config", noop_async), \
             patch.object(seed, "phase_7_demo_data", track_phase_7), \
             patch.object(seed, "phase_4_team", track_phase_4), \
             patch.object(seed, "phase_8_summary", noop_sync):
            loop = asyncio.new_event_loop()
            loop.run_until_complete(seed.seed(dry_run=True))
            loop.close()

        idx_4 = call_order.index("phase_4")
        idx_7 = call_order.index("phase_7")
        assert idx_7 < idx_4, "phase_4 must run AFTER phase_7"

    def test_phase_1_runs_before_phase_0(self):
        """SPEC-1434: Phase 1 (containers exist) runs before Phase 0 (cleanup)."""
        seed = _get_seed()
        call_order = []

        async def track_phase_0(dry_run):
            call_order.append("phase_0")

        async def track_phase_1(dry_run):
            call_order.append("phase_1")

        async def noop_async(*args, **kwargs):
            pass

        def noop_sync(*args, **kwargs):
            pass

        with patch.object(seed, "phase_1_containers", track_phase_1), \
             patch.object(seed, "phase_0_clean_partition", track_phase_0), \
             patch.object(seed, "phase_2_tenant", noop_async), \
             patch.object(seed, "phase_3_preferences", noop_async), \
             patch.object(seed, "phase_6_platform_config", noop_async), \
             patch.object(seed, "phase_7_demo_data", noop_async), \
             patch.object(seed, "phase_4_team", noop_async), \
             patch.object(seed, "phase_8_summary", noop_sync):
            loop = asyncio.new_event_loop()
            loop.run_until_complete(seed.seed(dry_run=True))
            loop.close()

        idx_0 = call_order.index("phase_0")
        idx_1 = call_order.index("phase_1")
        assert idx_1 < idx_0, "phase_1 must run BEFORE phase_0"

    def test_phase_0_conceptually_precedes_data_creation(self):
        """SPEC-1435: Phase 0 runs before phases 2, 3, 6, 7, 4 (data creation)."""
        seed = _get_seed()
        call_order = []

        async def track(name):
            call_order.append(name)

        async def t1(dry_run): await track("phase_1")
        async def t0(dry_run): await track("phase_0")
        async def t2(dry_run): await track("phase_2")
        async def t3(dry_run): await track("phase_3")
        async def t6(dry_run): await track("phase_6")
        async def t7(dry_run, demo): await track("phase_7")
        async def t4(dry_run): await track("phase_4")
        def t8(): call_order.append("phase_8")

        with patch.object(seed, "phase_1_containers", t1), \
             patch.object(seed, "phase_0_clean_partition", t0), \
             patch.object(seed, "phase_2_tenant", t2), \
             patch.object(seed, "phase_3_preferences", t3), \
             patch.object(seed, "phase_6_platform_config", t6), \
             patch.object(seed, "phase_7_demo_data", t7), \
             patch.object(seed, "phase_4_team", t4), \
             patch.object(seed, "phase_8_summary", t8):
            loop = asyncio.new_event_loop()
            loop.run_until_complete(seed.seed(dry_run=True))
            loop.close()

        idx_0 = call_order.index("phase_0")
        for data_phase in ["phase_2", "phase_3", "phase_6", "phase_7", "phase_4"]:
            idx = call_order.index(data_phase)
            assert idx_0 < idx, f"phase_0 must precede {data_phase}"


# ---------------------------------------------------------------------------
# Phase 5 removal tests
# ---------------------------------------------------------------------------

class TestPhase5Removed:
    """Verify phase 5 (KB article seeding) is removed from the default seed flow."""

    def test_seed_does_not_call_phase_5(self):
        """SPEC-1432/1454: seed() does NOT call phase_5_knowledge_base."""
        seed = _get_seed()
        phase_5_called = []

        original_phase_5 = seed.phase_5_knowledge_base

        async def tracking_phase_5(*args, **kwargs):
            phase_5_called.append(True)

        async def noop_async(*args, **kwargs):
            pass

        def noop_sync(*args, **kwargs):
            pass

        with patch.object(seed, "phase_1_containers", noop_async), \
             patch.object(seed, "phase_0_clean_partition", noop_async), \
             patch.object(seed, "phase_2_tenant", noop_async), \
             patch.object(seed, "phase_3_preferences", noop_async), \
             patch.object(seed, "phase_5_knowledge_base", tracking_phase_5), \
             patch.object(seed, "phase_6_platform_config", noop_async), \
             patch.object(seed, "phase_7_demo_data", noop_async), \
             patch.object(seed, "phase_4_team", noop_async), \
             patch.object(seed, "phase_8_summary", noop_sync):
            loop = asyncio.new_event_loop()
            loop.run_until_complete(seed.seed(dry_run=True))
            loop.close()

        assert len(phase_5_called) == 0, "seed() should NOT call phase_5_knowledge_base"

    def test_seed_source_has_phase_5_removal_comment(self):
        """SPEC-1432: The seed() source code documents KB article removal."""
        seed = _get_seed()
        source = inspect.getsource(seed.seed)
        assert "Phase 5" in source
        assert "removed" in source.lower() or "KB articles" in source


# ---------------------------------------------------------------------------
# Widget key in Phase 2 tests
# ---------------------------------------------------------------------------

class TestPhase2WidgetKey:
    """Verify widget key handling in Phase 2."""

    def test_phase_2_generates_widget_key(self):
        """SPEC-1443: Phase 2 generates a widget key and stores it in generated_credentials."""
        seed = _get_seed()
        seed.phase_results.clear()
        seed.generated_credentials.clear()

        fake_widget_key = "pk_live_abc123_def456"

        with patch.dict("sys.modules", {
            "src.multi_tenant.auth": MagicMock(
                generate_widget_key=MagicMock(return_value=fake_widget_key),
                hash_api_key=MagicMock(return_value="hash1"),
                hash_widget_key=MagicMock(return_value="hash2"),
            ),
            "src.multi_tenant.cosmos_schema": MagicMock(
                BillingChannel=MagicMock(side_effect=lambda x: x),
                ConsentStatus=MagicMock(GRANTED="granted"),
                TenantDocument=MagicMock(return_value=MagicMock()),
                TenantStatus=MagicMock(ACTIVE="active"),
                TenantTier=MagicMock(side_effect=lambda x: x),
            ),
        }):
            buf = io.StringIO()
            old_stdout = sys.stdout
            sys.stdout = buf
            try:
                loop = asyncio.new_event_loop()
                loop.run_until_complete(seed.phase_2_tenant(dry_run=True))
                loop.close()
            finally:
                sys.stdout = old_stdout

        assert "widget_key" in seed.generated_credentials
        assert seed.generated_credentials["widget_key"] == fake_widget_key


# ---------------------------------------------------------------------------
# Print separator test
# ---------------------------------------------------------------------------

class TestPrintSeparator:
    """Verify separators are printed in output."""

    def test_phase_8_prints_separator_lines(self):
        """SPEC-1453: phase_8_summary prints separator lines."""
        seed = _get_seed()
        seed.phase_results.clear()
        seed.generated_credentials.clear()
        buf = io.StringIO()
        old_stdout = sys.stdout
        sys.stdout = buf
        try:
            seed.phase_8_summary()
        finally:
            sys.stdout = old_stdout
        output = buf.getvalue()
        # Check for separator characters (= and -)
        assert "=" * 65 in output
        assert "-" * 65 in output


# ---------------------------------------------------------------------------
# Argument parsing tests
# ---------------------------------------------------------------------------

class TestArgumentParsing:
    """Verify CLI argument handling."""

    def test_default_is_dry_run(self):
        """Default (no --execute) means dry_run=True."""
        seed = _get_seed()
        # Inspect the main() function source to verify --execute controls dry_run
        source = inspect.getsource(seed.main)
        assert "--execute" in source
        assert "not args.execute" in source or "dry_run = not args.execute" in source

    def test_demo_flag_exists(self):
        """--demo flag is defined in argument parser."""
        seed = _get_seed()
        source = inspect.getsource(seed.main)
        assert "--demo" in source

    def test_embed_flag_exists(self):
        """--embed flag is defined in argument parser."""
        seed = _get_seed()
        source = inspect.getsource(seed.main)
        assert "--embed" in source
