"""WI-5742: bounded protected-commit evaluation and its cost reductions.

Spec-derived coverage for the Layer A wall-clock bound (fail-closed,
configuration-sourced, phase-evidence-bearing) and the Layer B cost reductions
(B1 invocation-scoped registry snapshot cache, B2 packet pre-filter, B3
single-pass classification / single registry assessment).

Requirement sources: WI-5742; DCL-PROJECT-AUTHORIZATION-OPERATION-TIME-ENFORCEMENT-001;
DELIB-202667722 (timer governance, relaxed-first defaults, single resolution path);
WI-5806 (invariant-coupled timers externalized together);
GOV-ENV-LOCAL-AUTHORITY-001 (env-local precedence layer).
"""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import pytest
from groundtruth_kb.project.timer_config import (
    FALLBACK_BRIDGE_PUBLICATION_CAPABILITY_TTL_SECONDS,
    FALLBACK_PROTECTED_COMMIT_EVALUATION_BOUND_SECONDS,
    PROTECTED_COMMIT_TIMERS_RELATIVE_PATH,
    TimerConfigError,
    resolve_protected_commit_timers,
)

from scripts import controlled_artifact_paths, implementation_authorization

REPO_ROOT = Path(__file__).resolve().parents[2]
SCRIPT_PATH = REPO_ROOT / "scripts" / "check_protected_commit_authorization.py"

_BOUND_ENV_VAR = "GTKB_PROTECTED_COMMIT_EVALUATION_BOUND_SECONDS"
_TTL_ENV_VAR = "GTKB_BRIDGE_PUBLICATION_CAPABILITY_TTL_SECONDS"


def _load_module():
    spec = importlib.util.spec_from_file_location("check_protected_commit_authorization", SCRIPT_PATH)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules["check_protected_commit_authorization"] = module
    spec.loader.exec_module(module)
    return module


@pytest.fixture(scope="module")
def gate():
    return _load_module()


def _write_timers(root: Path, *, bound: object, ttl: object) -> Path:
    path = root / PROTECTED_COMMIT_TIMERS_RELATIVE_PATH
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        "schema_version = 1\n\n"
        "[protected_commit]\n"
        f"evaluation_bound_seconds = {bound}\n"
        f"bridge_publication_capability_ttl_seconds = {ttl}\n",
        encoding="utf-8",
    )
    return path


class _FakeClock:
    """Deterministic monotonic clock so bound tests never depend on real elapsed time."""

    def __init__(self) -> None:
        self.now = 0.0

    def __call__(self) -> float:
        return self.now

    def advance(self, seconds: float) -> None:
        self.now += seconds


# ---------------------------------------------------------------------------
# Layer A - the bound is configuration-sourced (DELIB-202667722)
# ---------------------------------------------------------------------------


def test_bound_is_configuration_sourced(tmp_path, monkeypatch):
    """Resolution precedence is env-local -> config file -> relaxed fallback."""
    monkeypatch.delenv(_BOUND_ENV_VAR, raising=False)
    monkeypatch.delenv(_TTL_ENV_VAR, raising=False)

    # 3. relaxed in-code fallback when the config surface is absent
    fallback = resolve_protected_commit_timers(tmp_path)
    assert fallback.evaluation_bound_seconds == FALLBACK_PROTECTED_COMMIT_EVALUATION_BOUND_SECONDS
    assert fallback.bridge_publication_capability_ttl_seconds == FALLBACK_BRIDGE_PUBLICATION_CAPABILITY_TTL_SECONDS
    assert "fallback" in fallback.source

    # 2. the config file outranks the fallback
    _write_timers(tmp_path, bound=45, ttl=150)
    from_file = resolve_protected_commit_timers(tmp_path)
    assert from_file.evaluation_bound_seconds == 45
    assert from_file.bridge_publication_capability_ttl_seconds == 150
    assert str(PROTECTED_COMMIT_TIMERS_RELATIVE_PATH.name) in from_file.source

    # 1. env-local outranks the config file
    monkeypatch.setenv(_BOUND_ENV_VAR, "17")
    from_env = resolve_protected_commit_timers(tmp_path)
    assert from_env.evaluation_bound_seconds == 17
    assert from_env.bridge_publication_capability_ttl_seconds == 150
    assert _BOUND_ENV_VAR in from_env.source


def test_production_timer_config_is_present_and_valid(monkeypatch):
    """The shipped config surface exists and satisfies the coupled invariant."""
    monkeypatch.delenv(_BOUND_ENV_VAR, raising=False)
    monkeypatch.delenv(_TTL_ENV_VAR, raising=False)
    assert (REPO_ROOT / PROTECTED_COMMIT_TIMERS_RELATIVE_PATH).is_file()
    timers = resolve_protected_commit_timers(REPO_ROOT)
    assert timers.evaluation_bound_seconds < timers.bridge_publication_capability_ttl_seconds
    assert timers.margin_seconds > 0


# ---------------------------------------------------------------------------
# Layer A - the coupled invariant (WI-5806)
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("bound,ttl", [(120, 120), (121, 120), (300, 120)])
def test_bound_cannot_exceed_paired_capability_ttl(tmp_path, monkeypatch, bound, ttl):
    """A bound at or above the paired TTL is rejected, not silently accepted.

    This is what makes the publication-stranding precondition unrepresentable in
    configuration rather than merely discouraged.
    """
    monkeypatch.delenv(_BOUND_ENV_VAR, raising=False)
    monkeypatch.delenv(_TTL_ENV_VAR, raising=False)
    _write_timers(tmp_path, bound=bound, ttl=ttl)
    with pytest.raises(TimerConfigError) as excinfo:
        resolve_protected_commit_timers(tmp_path)
    assert "strictly less than" in str(excinfo.value)


def test_capability_ttl_ceiling_matches_mint_time_rejection(tmp_path, monkeypatch):
    """A TTL above the current 800s mint-time ceiling is rejected in configuration."""
    monkeypatch.delenv(_BOUND_ENV_VAR, raising=False)
    monkeypatch.delenv(_TTL_ENV_VAR, raising=False)
    _write_timers(tmp_path, bound=10, ttl=801)
    with pytest.raises(TimerConfigError) as excinfo:
        resolve_protected_commit_timers(tmp_path)
    assert "ceiling" in str(excinfo.value)


@pytest.mark.parametrize("bad", ["0", "-5", "'abc'", "true"])
def test_invalid_timer_values_fail_closed(tmp_path, monkeypatch, bad):
    monkeypatch.delenv(_BOUND_ENV_VAR, raising=False)
    monkeypatch.delenv(_TTL_ENV_VAR, raising=False)
    _write_timers(tmp_path, bound=bad, ttl=120)
    with pytest.raises(TimerConfigError):
        resolve_protected_commit_timers(tmp_path)


def test_gate_fails_closed_on_unusable_timer_config(tmp_path, gate, monkeypatch):
    """An invariant-violating config is a gate error, never an unbounded evaluation."""
    monkeypatch.delenv(_BOUND_ENV_VAR, raising=False)
    monkeypatch.delenv(_TTL_ENV_VAR, raising=False)
    _write_timers(tmp_path, bound=200, ttl=120)
    with pytest.raises(gate.GateError) as excinfo:
        gate._resolve_evaluation_budget(tmp_path)
    assert "timer configuration is unusable" in str(excinfo.value)


# ---------------------------------------------------------------------------
# Layer A - termination, deny semantics, and phase evidence
# ---------------------------------------------------------------------------


def test_delayed_evaluation_terminates_within_bound(tmp_path, gate, monkeypatch):
    """A deliberately delayed evaluation terminates and DENIES; it never passes on timeout."""
    clock = _FakeClock()
    budget = gate._EvaluationBudget(10, source="test", clock=clock)

    # Simulate a phase that overruns the budget.
    budget.enter("classification")
    clock.advance(11)

    result = None
    try:
        budget.check()
    except gate.EvaluationBoundExceeded as exc:
        result = exc.as_result()

    assert result is not None, "an exhausted budget must raise, not fall through"
    assert result["status"] == "fail", "the gate must deny on exhaustion, never pass"
    assert result["cleared"] == []
    assert result["protected_paths"] == []


def test_bound_exhaustion_names_executing_phase(gate):
    """The deny output names phase, elapsed, configured bound, and remediation."""
    clock = _FakeClock()
    budget = gate._EvaluationBudget(30, source="config/governance/protected-commit-timers.toml", clock=clock)
    budget.enter("live_go_evidence")
    clock.advance(31.5)

    with pytest.raises(gate.EvaluationBoundExceeded) as excinfo:
        budget.check()

    result = excinfo.value.as_result()
    bound_evidence = result["evaluation_bound"]
    assert bound_evidence["exhausted"] is True
    assert bound_evidence["phase"] == "live_go_evidence"
    assert bound_evidence["bound_seconds"] == 30
    assert bound_evidence["elapsed_seconds"] == pytest.approx(31.5, abs=0.01)
    assert "protected-commit-timers.toml" in bound_evidence["source"]

    errors = " ".join(result["findings"][0]["evidence_errors"])
    assert "executing phase: live_go_evidence" in errors
    assert "elapsed: 31.5s" in errors
    assert "configured bound: 30s" in errors
    assert "remediation:" in errors
    # The remediation must not invite re-creating the stranding precondition.
    assert "not including" in errors


def test_every_declared_phase_is_reportable(gate):
    """Each declared phase name round-trips into the deny evidence."""
    for phase in gate._EVALUATION_PHASES:
        clock = _FakeClock()
        budget = gate._EvaluationBudget(1, source="test", clock=clock)
        budget.enter(phase)
        clock.advance(2)
        with pytest.raises(gate.EvaluationBoundExceeded) as excinfo:
            budget.check()
        assert excinfo.value.as_result()["evaluation_bound"]["phase"] == phase


def test_evaluate_returns_deny_result_rather_than_raising(tmp_path, gate, monkeypatch):
    """evaluate() converts bound exhaustion into a deny verdict, not an exception."""
    clock = _FakeClock()
    budget = gate._EvaluationBudget(5, source="test", clock=clock)

    def _explode(*args, **kwargs):
        clock.advance(6)
        budget.check()
        raise AssertionError("unreachable")

    monkeypatch.setattr(gate, "_resolve_head_oid", _explode)
    result = gate.evaluate(tmp_path, paths=["scripts/example.py"], budget=budget)
    assert result["status"] == "fail"
    assert result["evaluation_bound"]["exhausted"] is True


def test_budget_does_not_fire_before_exhaustion(gate):
    clock = _FakeClock()
    budget = gate._EvaluationBudget(60, source="test", clock=clock)
    budget.enter("classification")
    clock.advance(59.9)
    budget.check()  # must not raise
    assert budget.phase == "classification"


# ---------------------------------------------------------------------------
# Layer B1 - invocation-scoped registry snapshot cache
# ---------------------------------------------------------------------------


def test_single_snapshot_load_per_invocation(monkeypatch):
    """Inside one cache scope, N classifications perform exactly one snapshot load."""
    calls: list[Path] = []
    sentinel = object()

    def _fake_load(*, project_root):
        calls.append(project_root)
        return sentinel

    monkeypatch.setattr(controlled_artifact_paths, "load_registry_snapshot", _fake_load)

    with controlled_artifact_paths.registry_snapshot_cache_scope():
        for _ in range(25):
            controlled_artifact_paths.load_registry_snapshot_cached(project_root=REPO_ROOT)

    assert len(calls) == 1, f"expected exactly 1 snapshot load per invocation, got {len(calls)}"


def test_cache_is_disabled_outside_a_scope(monkeypatch):
    """No caching leaks to callers that did not open a scope: same lock, same freshness."""
    calls: list[Path] = []

    def _fake_load(*, project_root):
        calls.append(project_root)
        return object()

    monkeypatch.setattr(controlled_artifact_paths, "load_registry_snapshot", _fake_load)

    for _ in range(4):
        controlled_artifact_paths.load_registry_snapshot_cached(project_root=REPO_ROOT)

    assert len(calls) == 4, "outside a scope every call must load fresh"


def test_cache_scope_does_not_outlive_the_invocation(monkeypatch):
    calls: list[Path] = []

    def _fake_load(*, project_root):
        calls.append(project_root)
        return object()

    monkeypatch.setattr(controlled_artifact_paths, "load_registry_snapshot", _fake_load)

    with controlled_artifact_paths.registry_snapshot_cache_scope():
        controlled_artifact_paths.load_registry_snapshot_cached(project_root=REPO_ROOT)
        controlled_artifact_paths.load_registry_snapshot_cached(project_root=REPO_ROOT)
    assert len(calls) == 1

    # A second, separate invocation must not reuse the first invocation's snapshot.
    with controlled_artifact_paths.registry_snapshot_cache_scope():
        controlled_artifact_paths.load_registry_snapshot_cached(project_root=REPO_ROOT)
    assert len(calls) == 2

    assert controlled_artifact_paths._REGISTRY_SNAPSHOT_CACHE is None


def test_nested_scope_does_not_leak_into_enclosing_caller(monkeypatch):
    calls: list[Path] = []
    monkeypatch.setattr(
        controlled_artifact_paths,
        "load_registry_snapshot",
        lambda *, project_root: calls.append(project_root) or object(),
    )
    with controlled_artifact_paths.registry_snapshot_cache_scope():
        controlled_artifact_paths.load_registry_snapshot_cached(project_root=REPO_ROOT)
        with controlled_artifact_paths.registry_snapshot_cache_scope():
            controlled_artifact_paths.load_registry_snapshot_cached(project_root=REPO_ROOT)
        assert len(calls) == 2
        # the enclosing scope's cache survived the nested scope
        controlled_artifact_paths.load_registry_snapshot_cached(project_root=REPO_ROOT)
    assert len(calls) == 2


# ---------------------------------------------------------------------------
# Layer B2 - packet pre-filter preserves the verdict
# ---------------------------------------------------------------------------


def _packet(bridge_id: str, *, globs: list[str], expires_at: str) -> dict:
    return {"bridge_id": bridge_id, "target_path_globs": globs, "expires_at": expires_at}


FAR_FUTURE = "2099-01-01T00:00:00Z"
LONG_PAST = "2000-01-01T00:00:00Z"


def test_prefilter_excludes_non_matching_packet():
    """A packet authorizing none of the candidate paths cannot clear any of them."""
    packet = _packet("other-thread", globs=["docs/**"], expires_at=FAR_FUTURE)
    reason = implementation_authorization._packet_cannot_authorize_any(packet, ["scripts/foo.py"])
    assert reason is not None
    assert "authorizes none" in reason


def test_prefilter_excludes_expired_packet():
    """An expired packet can never be valid, so it can never clear a path."""
    packet = _packet("expired-thread", globs=["scripts/**"], expires_at=LONG_PAST)
    reason = implementation_authorization._packet_cannot_authorize_any(packet, ["scripts/foo.py"])
    assert reason is not None
    assert "expired" in reason


def test_prefilter_admits_live_matching_packet():
    """A live, path-matching packet is admitted to full validation."""
    packet = _packet("live-thread", globs=["scripts/**"], expires_at=FAR_FUTURE)
    assert implementation_authorization._packet_cannot_authorize_any(packet, ["scripts/foo.py"]) is None


def test_prefilter_admits_packet_with_unparseable_expiry():
    """An unparseable expiry is admitted so existing fail-closed reporting is preserved."""
    packet = _packet("weird-thread", globs=["scripts/**"], expires_at="not-a-timestamp")
    assert implementation_authorization._packet_cannot_authorize_any(packet, ["scripts/foo.py"]) is None


def test_prefilter_matching_is_identical_to_clearance_matching():
    """The pre-filter admission test uses exactly the clearance matcher.

    If these ever diverged, the pre-filter could drop a packet that would have
    cleared a path -- the one way this optimization could change a verdict.
    """
    cases = [
        (["scripts/**"], "scripts/nested/deep/file.py"),
        (["scripts/check_*.py"], "scripts/check_protected_commit_authorization.py"),
        (["config/governance/**"], "config/governance/protected-commit-timers.toml"),
        (["docs/**"], "scripts/file.py"),
        (["scripts/exact.py"], "scripts/exact.py"),
        (["scripts/exact.py"], "scripts/other.py"),
    ]
    for globs, candidate in cases:
        packet = _packet("t", globs=globs, expires_at=FAR_FUTURE)
        authorized = implementation_authorization.path_authorized(packet, candidate)
        admitted = implementation_authorization._packet_cannot_authorize_any(packet, [candidate]) is None
        assert authorized == admitted, f"divergence for globs={globs} candidate={candidate}"


def test_packet_prefilter_preserves_verdict(tmp_path):
    """Filtered and unfiltered enumeration agree on the valid-packet set.

    The valid-packet set is the only field that decides clearance, so identity
    here is identity of every clearance outcome. Rows and error population are
    also preserved so the fail-closed reporting surface stays populated.
    """
    by_bridge = tmp_path / implementation_authorization.BY_BRIDGE_DIRECTORY_RELATIVE_PATH
    by_bridge.mkdir(parents=True, exist_ok=True)

    import json as _json

    corpus = {
        "expired-matching": _packet("expired-matching", globs=["scripts/**"], expires_at=LONG_PAST),
        "live-nonmatching": _packet("live-nonmatching", globs=["docs/**"], expires_at=FAR_FUTURE),
        "expired-nonmatching": _packet("expired-nonmatching", globs=["docs/**"], expires_at=LONG_PAST),
        "live-matching": _packet("live-matching", globs=["scripts/**"], expires_at=FAR_FUTURE),
    }
    for name, body in corpus.items():
        (by_bridge / f"{name}.json").write_text(_json.dumps(body), encoding="utf-8")

    candidates = ["scripts/foo.py"]
    unfiltered = implementation_authorization.list_named_packets(tmp_path)
    filtered = implementation_authorization.list_named_packets(tmp_path, candidate_paths=candidates)

    assert len(unfiltered) == len(filtered) == len(corpus), "every packet still produces a row"
    assert sorted(r["path"] for r in unfiltered) == sorted(r["path"] for r in filtered)

    valid_unfiltered = sorted(r["path"] for r in unfiltered if r.get("valid") is True)
    valid_filtered = sorted(r["path"] for r in filtered if r.get("valid") is True)
    assert valid_unfiltered == valid_filtered, "clearance-bearing valid set must be identical"

    # Every non-valid row still carries a populated error on both paths.
    for rows in (unfiltered, filtered):
        for row in rows:
            if row.get("valid") is not True:
                assert row.get("error"), f"row {row['path']} lost its fail-closed error text"


def test_default_enumeration_is_unchanged_for_existing_callers(tmp_path):
    """candidate_paths=None preserves the original exhaustive behavior exactly."""
    import json as _json

    by_bridge = tmp_path / implementation_authorization.BY_BRIDGE_DIRECTORY_RELATIVE_PATH
    by_bridge.mkdir(parents=True, exist_ok=True)
    (by_bridge / "a.json").write_text(
        _json.dumps(_packet("a", globs=["docs/**"], expires_at=LONG_PAST)), encoding="utf-8"
    )

    rows = implementation_authorization.list_named_packets(tmp_path)
    assert len(rows) == 1
    assert all("prefiltered" not in row for row in rows), "default path must not pre-filter"


def test_corrupt_packet_row_shape_is_preserved(tmp_path):
    by_bridge = tmp_path / implementation_authorization.BY_BRIDGE_DIRECTORY_RELATIVE_PATH
    by_bridge.mkdir(parents=True, exist_ok=True)
    (by_bridge / "broken.json").write_text("{not json", encoding="utf-8")

    for candidates in (None, ["scripts/foo.py"]):
        rows = implementation_authorization.list_named_packets(tmp_path, candidate_paths=candidates)
        assert len(rows) == 1
        assert rows[0]["valid"] is False
        assert "corrupt or unreadable" in rows[0]["error"]


def test_non_object_packet_root_is_a_clean_deny(tmp_path):
    by_bridge = tmp_path / implementation_authorization.BY_BRIDGE_DIRECTORY_RELATIVE_PATH
    by_bridge.mkdir(parents=True, exist_ok=True)
    (by_bridge / "list.json").write_text("[1, 2, 3]", encoding="utf-8")

    rows = implementation_authorization.list_named_packets(tmp_path, candidate_paths=["scripts/foo.py"])
    assert len(rows) == 1
    assert rows[0]["valid"] is False
    assert "not an object" in rows[0]["error"]


# ---------------------------------------------------------------------------
# Layer B3 - single-pass classification / single registry assessment
# ---------------------------------------------------------------------------


def test_classification_partitions_are_complete_and_disjoint(tmp_path, gate, monkeypatch):
    """The single classification pass partitions the selected set exactly once."""
    selected = ["scripts/a.py", "docs/b.md", "platform_tests/c.py", "README.md"]
    seen: list[str] = []

    def _fake_is_protected(path, *, project_root=None):
        seen.append(path)
        return path.startswith(("scripts/", "platform_tests/"))

    monkeypatch.setattr(gate, "is_protected_path", _fake_is_protected)
    monkeypatch.setattr(gate, "_verified_bridge_finalization_finding", lambda *a, **k: None)
    monkeypatch.setattr(gate, "_registry_commit_findings", lambda *a, **k: [])

    result = gate._evaluate_selected(tmp_path, selected, None, None)

    assert seen == selected, "each path must be classified exactly once, in order"
    assert result["protected_paths"] == ["scripts/a.py", "platform_tests/c.py"]
    assert result["skipped_unprotected"] == ["docs/b.md", "README.md"]
    assert sorted(result["protected_paths"] + result["skipped_unprotected"]) == sorted(selected)


def test_registry_assessment_runs_once(tmp_path, gate, monkeypatch):
    """One evaluation performs exactly one registry commit assessment."""
    calls: list[tuple] = []

    def _fake_assessment(root, selected_paths, snapshot):
        calls.append((root, tuple(selected_paths)))
        return []

    monkeypatch.setattr(gate, "_registry_commit_findings", _fake_assessment)
    monkeypatch.setattr(gate, "is_protected_path", lambda path, **k: False)
    monkeypatch.setattr(gate, "_verified_bridge_finalization_finding", lambda *a, **k: None)

    gate._evaluate_selected(tmp_path, ["docs/a.md", "docs/b.md"], None, None)
    assert len(calls) == 1, f"expected exactly one registry assessment, got {len(calls)}"
