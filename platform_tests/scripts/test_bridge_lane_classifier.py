"""Tests for scripts/bridge_lane_classifier.py - bridge scheduler Slice 5 (WI-3376).

Per bridge/gtkb-bridge-scheduler-lanes-leases-slice-5-003.md (Loyal Opposition
GO at -004). Covers T1-T22 of the proposal's spec-to-test mapping, plus T23 for
the governance-signal-in-kind branch specified in Scope item 4.

The classifier is a pure stdlib module; these tests construct
LaneClassificationInput contexts directly and assert the classified lane and
concurrency profile. They touch no filesystem path.

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

from __future__ import annotations

import builtins
import importlib.util
import sys
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[2]
SCRIPT_PATH = PROJECT_ROOT / "scripts" / "bridge_lane_classifier.py"


@pytest.fixture(scope="module")
def mod():
    """Load scripts/bridge_lane_classifier.py as a module without side effects."""
    spec = importlib.util.spec_from_file_location("bridge_lane_classifier", SCRIPT_PATH)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    # Register in sys.modules before exec_module: dataclasses resolves field
    # annotations via sys.modules[cls.__module__] under PEP 563 string
    # annotations (`from __future__ import annotations`).
    sys.modules[spec.name] = module
    try:
        spec.loader.exec_module(module)
        yield module
    finally:
        sys.modules.pop(spec.name, None)


def _ctx(mod, **kwargs):
    return mod.LaneClassificationInput(**kwargs)


# --- T1-T7: bridge-kind -> lane for NEW / REVISED entries --------------------


def test_t1_new_implementation_proposal_is_review(mod):
    ctx = _ctx(
        mod,
        latest_status="NEW",
        current_bridge_kind="implementation_proposal",
        effective_prime_bridge_kind="implementation_proposal",
    )
    assert mod.classify_lane(ctx) == mod.LANE_REVIEW


def test_t2_new_prime_implementation_proposal_is_review(mod):
    ctx = _ctx(
        mod,
        latest_status="NEW",
        current_bridge_kind="prime_implementation_proposal",
        effective_prime_bridge_kind="prime_implementation_proposal",
    )
    assert mod.classify_lane(ctx) == mod.LANE_REVIEW


def test_t3_implementation_report_is_verification(mod):
    ctx = _ctx(
        mod,
        latest_status="NEW",
        current_bridge_kind="implementation_report",
        effective_prime_bridge_kind="implementation_report",
    )
    assert mod.classify_lane(ctx) == mod.LANE_VERIFICATION


def test_t4_post_implementation_report_is_verification(mod):
    ctx = _ctx(
        mod,
        latest_status="REVISED",
        current_bridge_kind="post_implementation_report",
        effective_prime_bridge_kind="post_implementation_report",
    )
    assert mod.classify_lane(ctx) == mod.LANE_VERIFICATION


def test_t5_hyphenated_post_implementation_report_is_verification(mod):
    ctx = _ctx(
        mod,
        latest_status="NEW",
        current_bridge_kind="post-implementation-report",
        effective_prime_bridge_kind="post-implementation-report",
    )
    assert mod.classify_lane(ctx) == mod.LANE_VERIFICATION


def test_t6_prime_implementation_report_is_verification(mod):
    ctx = _ctx(
        mod,
        latest_status="NEW",
        current_bridge_kind="prime_implementation_report",
        effective_prime_bridge_kind="prime_implementation_report",
    )
    assert mod.classify_lane(ctx) == mod.LANE_VERIFICATION


def test_t7_prime_builder_implementation_report_is_verification(mod):
    ctx = _ctx(
        mod,
        latest_status="NEW",
        current_bridge_kind="prime_builder_implementation_report",
        effective_prime_bridge_kind="prime_builder_implementation_report",
    )
    assert mod.classify_lane(ctx) == mod.LANE_VERIFICATION


# --- T8-T11: status-primary rule for the GO/NO-GO verdict-chain shape --------


def test_t8_go_verdict_chain_is_implementation(mod):
    ctx = _ctx(
        mod,
        latest_status="GO",
        current_bridge_kind="loyal_opposition_verdict",
        effective_prime_bridge_kind="implementation_proposal",
    )
    assert mod.classify_lane(ctx) == mod.LANE_IMPLEMENTATION


def test_t9_nogo_verdict_chain_is_implementation(mod):
    ctx = _ctx(
        mod,
        latest_status="NO-GO",
        current_bridge_kind="loyal_opposition_verdict",
        effective_prime_bridge_kind="implementation_proposal",
    )
    assert mod.classify_lane(ctx) == mod.LANE_IMPLEMENTATION


def test_t10_go_with_no_useful_top_kind_is_implementation(mod):
    ctx = _ctx(mod, latest_status="GO", current_bridge_kind=None, effective_prime_bridge_kind=None)
    assert mod.classify_lane(ctx) == mod.LANE_IMPLEMENTATION


def test_t11_verified_is_review_and_flagged_terminal(mod):
    ctx = _ctx(mod, latest_status="VERIFIED", current_bridge_kind="loyal_opposition_verdict")
    assert mod.classify_lane(ctx) == mod.LANE_REVIEW
    assert mod.is_terminal(ctx) is True


# --- T12-T16: governance override --------------------------------------------


def test_t12_membase_mutation_proposal_is_governance(mod):
    ctx = _ctx(
        mod,
        latest_status="NEW",
        current_bridge_kind="implementation_proposal",
        effective_prime_bridge_kind="implementation_proposal",
        mutates_membase=True,
    )
    assert mod.classify_lane(ctx) == mod.LANE_GOVERNANCE


def test_t13_formal_artifact_mutation_proposal_is_governance(mod):
    ctx = _ctx(
        mod,
        latest_status="NEW",
        current_bridge_kind="implementation_proposal",
        effective_prime_bridge_kind="implementation_proposal",
        formal_artifact_mutation=True,
    )
    assert mod.classify_lane(ctx) == mod.LANE_GOVERNANCE


def test_t14_owner_decision_sensitive_proposal_is_governance(mod):
    ctx = _ctx(
        mod,
        latest_status="NEW",
        current_bridge_kind="implementation_proposal",
        effective_prime_bridge_kind="implementation_proposal",
        owner_decision_sensitive=True,
    )
    assert mod.classify_lane(ctx) == mod.LANE_GOVERNANCE


def test_t15_explicit_batch_safe_releases_governance_override(mod):
    ctx = _ctx(
        mod,
        latest_status="NEW",
        current_bridge_kind="implementation_proposal",
        effective_prime_bridge_kind="implementation_proposal",
        formal_artifact_mutation=True,
        explicit_batch_safe=True,
    )
    assert mod.classify_lane(ctx) == mod.LANE_REVIEW


def test_t16_loyal_opposition_advisory_is_governance(mod):
    ctx = _ctx(mod, latest_status="NEW", current_bridge_kind="loyal_opposition_advisory")
    assert mod.classify_lane(ctx) == mod.LANE_GOVERNANCE


# --- T17: fail-soft default --------------------------------------------------


def test_t17_unknown_or_missing_kind_fails_soft_to_review(mod):
    for kind in (None, "", "   ", "some_future_kind"):
        ctx = _ctx(
            mod,
            latest_status="NEW",
            current_bridge_kind=kind,
            effective_prime_bridge_kind=kind,
        )
        # Must not raise and must return the conservative fail-soft lane.
        assert mod.classify_lane(ctx) == mod.LANE_REVIEW


# --- T18-T20: concurrency profiles -------------------------------------------


def test_t18_verification_profile_is_aggressive(mod):
    assert mod.lane_concurrency_profile(mod.LANE_VERIFICATION)["parallelism"] == "aggressive"


def test_t19_governance_profile_is_serialized(mod):
    profile = mod.lane_concurrency_profile(mod.LANE_GOVERNANCE)
    assert profile["parallelism"] == "serialized"
    assert profile["max_concurrency"] == 1


def test_t20_every_lane_serializes_verdict_writes(mod):
    assert frozenset(
        {mod.LANE_REVIEW, mod.LANE_IMPLEMENTATION, mod.LANE_VERIFICATION, mod.LANE_GOVERNANCE}
    ) == mod.CANONICAL_LANES
    for lane in mod.CANONICAL_LANES:
        profile = mod.lane_concurrency_profile(lane)
        assert profile["lane"] == lane
        assert profile["verdict_writes_serialized"] is True


# --- T21: deterministic + no filesystem access -------------------------------


def test_t21_deterministic_and_no_filesystem_access(mod, monkeypatch):
    ctx = _ctx(
        mod,
        latest_status="NEW",
        current_bridge_kind="implementation_proposal",
        effective_prime_bridge_kind="implementation_proposal",
    )
    first = mod.classify_lane(ctx)
    second = mod.classify_lane(ctx)
    assert first == second == mod.LANE_REVIEW

    # classify_lane must touch no filesystem: make open() raise, then re-call.
    def _no_open(*args, **kwargs):
        raise AssertionError("classify_lane must not access the filesystem")

    monkeypatch.setattr(builtins, "open", _no_open)
    assert mod.classify_lane(ctx) == mod.LANE_REVIEW


# --- T22: effective_prime_bridge_kind preferred over current_bridge_kind -----


def test_t22_effective_prime_kind_preferred_over_current(mod):
    # Top file is a verdict; the operative Prime version is a report.
    ctx = _ctx(
        mod,
        latest_status="NEW",
        current_bridge_kind="loyal_opposition_verdict",
        effective_prime_bridge_kind="implementation_report",
    )
    assert mod.classify_lane(ctx) == mod.LANE_VERIFICATION


# --- T23: governance-signal-in-kind branch (Scope item 4) --------------------


def test_t23_governance_signal_kind_is_governance(mod):
    for kind in ("formal_artifact_proposal", "governance_amendment", "formal-artifact-update"):
        ctx = _ctx(
            mod,
            latest_status="NEW",
            current_bridge_kind=kind,
            effective_prime_bridge_kind=kind,
        )
        assert mod.classify_lane(ctx) == mod.LANE_GOVERNANCE
