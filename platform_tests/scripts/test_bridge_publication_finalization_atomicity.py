"""WI-5742: stranding prevention for bridge-publication finalization.

Scope note (read this before extending):

WI-5742's proposal described three layers. Layers A (fail-closed wall-clock
bound) and B (cost reductions) are implemented and covered here and in
``test_protected_commit_evaluation_bound.py``. Layer C -- reordering the
publication transaction to mint the capability *after* the gates pass (C-ii)
plus compensation robustness (C-iii) -- is NOT implemented in this change and
is deferred to its own governed cycle. Layer C lives entirely in
``registry_control_plane.py``, which was outside this change's authored scope.

What that means for this module: the tests below assert the stranding-prevention
property *as actually delivered*, which is structural rather than
transactional. The delivered guarantee is:

    gate duration <= configured bound  <  capability TTL

The bound is enforced fail-closed at runtime (Layer A) and the strict inequality
is enforced at configuration-resolution time by the validated accessor. Together
those make "the gate outlives the capability minted for the publication it
gates" -- the precondition for every recorded stranding incident -- structurally
unreachable, without changing the publication transaction's ordering.

Tests named for Layer C behavior (late mint, compensation after a sibling
aggregate append) are deliberately NOT stubbed as passing here. Asserting them
against an unimplemented layer would be false coverage.

Requirement sources: WI-5742 (stranding clause); GOV-FILE-BRIDGE-AUTHORITY-001
(append-only numbered chain); REQ-GTKB-GOVERNED-GIT-LIFECYCLE-001;
WI-5806 / DELIB-202667722 (invariant-coupled timers).
"""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import pytest
from groundtruth_kb.project.timer_config import (
    PROTECTED_COMMIT_TIMERS_RELATIVE_PATH,
    TimerConfigError,
    resolve_protected_commit_timers,
)

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


class _FakeClock:
    def __init__(self) -> None:
        self.now = 0.0

    def __call__(self) -> float:
        return self.now

    def advance(self, seconds: float) -> None:
        self.now += seconds


# ---------------------------------------------------------------------------
# The delivered structural guarantee
# ---------------------------------------------------------------------------


def test_shipped_bound_fits_inside_capability_ttl(monkeypatch):
    """The shipped configuration cannot let a gate outlive the capability TTL."""
    monkeypatch.delenv(_BOUND_ENV_VAR, raising=False)
    monkeypatch.delenv(_TTL_ENV_VAR, raising=False)
    timers = resolve_protected_commit_timers(REPO_ROOT)
    assert timers.evaluation_bound_seconds < timers.bridge_publication_capability_ttl_seconds
    assert timers.margin_seconds > 0, (
        "the gate bound must leave positive headroom under the capability TTL; "
        "zero or negative headroom is the publication-stranding precondition"
    )


def test_stranding_precondition_is_unrepresentable_in_configuration(tmp_path, monkeypatch):
    """No configuration can express a bound that reaches the capability TTL."""
    monkeypatch.delenv(_BOUND_ENV_VAR, raising=False)
    monkeypatch.delenv(_TTL_ENV_VAR, raising=False)
    path = tmp_path / PROTECTED_COMMIT_TIMERS_RELATIVE_PATH
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        "schema_version = 1\n\n[protected_commit]\n"
        "evaluation_bound_seconds = 240\n"
        "bridge_publication_capability_ttl_seconds = 120\n",
        encoding="utf-8",
    )
    with pytest.raises(TimerConfigError):
        resolve_protected_commit_timers(tmp_path)


def test_env_override_cannot_break_the_invariant(tmp_path, monkeypatch):
    """An env-local override is still validated against the coupled invariant."""
    monkeypatch.delenv(_TTL_ENV_VAR, raising=False)
    monkeypatch.setenv(_BOUND_ENV_VAR, "500")
    with pytest.raises(TimerConfigError):
        resolve_protected_commit_timers(tmp_path)


def test_measured_gate_cost_headroom_is_documented(monkeypatch):
    """Regression lock on the relationship the WI-5742 evidence rests on.

    Measured on the 812-path / 94-protected corpus that produced the 241.664s
    pre-fix baseline, post-fix end-to-end evaluation was 59.367s and 84.286s on
    two runs (the spread is concurrent control-plane lock contention). The bound
    must stay above the WORST observed cost -- so legitimate commits are not
    denied -- and below the capability TTL, so publications cannot strand.
    """
    monkeypatch.delenv(_BOUND_ENV_VAR, raising=False)
    monkeypatch.delenv(_TTL_ENV_VAR, raising=False)
    observed_post_fix_wall_seconds = 84.286
    timers = resolve_protected_commit_timers(REPO_ROOT)
    assert timers.evaluation_bound_seconds > observed_post_fix_wall_seconds, (
        "the configured bound must exceed measured gate cost or legitimate commits will be denied"
    )
    assert timers.bridge_publication_capability_ttl_seconds > observed_post_fix_wall_seconds


# ---------------------------------------------------------------------------
# Gate failure leaves nothing behind
# ---------------------------------------------------------------------------


def test_gate_failure_leaves_no_terminal_artifact(tmp_path, gate, monkeypatch):
    """A bound-exhausted evaluation writes nothing and mutates nothing.

    The gate is a read-only evaluation: on the failure path there must be no
    terminal artifact to unwind, which is what keeps the append-only numbered
    chain byte-identical across a gate failure.
    """
    bridge_dir = tmp_path / "bridge"
    bridge_dir.mkdir(parents=True, exist_ok=True)
    chain = bridge_dir / "gtkb-example-001.md"
    chain.write_text("NEW\n\n# example\n", encoding="utf-8")

    before = {p: p.read_bytes() for p in sorted(tmp_path.rglob("*")) if p.is_file()}

    clock = _FakeClock()
    budget = gate._EvaluationBudget(5, source="test", clock=clock)

    def _explode(*args, **kwargs):
        clock.advance(6)
        budget.check()
        raise AssertionError("unreachable")

    monkeypatch.setattr(gate, "_resolve_head_oid", _explode)
    result = gate.evaluate(tmp_path, paths=["scripts/foo.py"], budget=budget)

    assert result["status"] == "fail"
    assert result["evaluation_bound"]["exhausted"] is True

    after = {p: p.read_bytes() for p in sorted(tmp_path.rglob("*")) if p.is_file()}
    assert before == after, "a gate failure must not create, delete, or modify any file"


def test_bound_exhaustion_never_clears_a_path(gate):
    """Exhaustion is a deny for every path; it can never clear one."""
    clock = _FakeClock()
    budget = gate._EvaluationBudget(1, source="test", clock=clock)
    budget.enter("per_path")
    clock.advance(2)
    with pytest.raises(gate.EvaluationBoundExceeded) as excinfo:
        budget.check()
    result = excinfo.value.as_result()
    assert result["status"] == "fail"
    assert result["cleared"] == []
    assert result["evidence_summary"]["live_go_packets_valid"] == 0


def test_bound_exhaustion_is_actionable_not_a_stack_trace(gate):
    """The deny is human-actionable text naming the slow phase and the remedy."""
    clock = _FakeClock()
    budget = gate._EvaluationBudget(45, source="config/governance/protected-commit-timers.toml", clock=clock)
    budget.enter("registry_assessment")
    clock.advance(46)
    with pytest.raises(gate.EvaluationBoundExceeded) as excinfo:
        budget.check()

    message = str(excinfo.value)
    assert "registry_assessment" in message
    assert "45s budget" in message
    assert "Traceback" not in message

    errors = " ".join(excinfo.value.as_result()["findings"][0]["evidence_errors"])
    assert "remediation:" in errors
    assert "protected-commit-timers.toml" in errors


# ---------------------------------------------------------------------------
# Layer C -- deferred, deliberately not asserted here
# ---------------------------------------------------------------------------


@pytest.mark.skip(
    reason=(
        "Layer C (late-mint publication reorder C-ii + compensation robustness C-iii) is deferred to "
        "its own governed cycle; it lives in registry_control_plane.py, outside this change's authored "
        "scope. Asserting it here would be false coverage. See this module's docstring."
    )
)
def test_finalize_verified_near_bound_is_atomic():  # pragma: no cover - deferred layer
    raise NotImplementedError("Layer C not implemented in WI-5742's emergency-bootstrap scope")


@pytest.mark.skip(
    reason=(
        "Layer C (C-iii compensation robustness after a sibling aggregate append) is deferred to its "
        "own governed cycle. See this module's docstring."
    )
)
def test_compensation_succeeds_after_sibling_aggregate_append():  # pragma: no cover - deferred layer
    raise NotImplementedError("Layer C not implemented in WI-5742's emergency-bootstrap scope")
