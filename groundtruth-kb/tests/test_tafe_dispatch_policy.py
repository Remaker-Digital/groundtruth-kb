from __future__ import annotations

from pathlib import Path

import groundtruth_kb.tafe_dispatch_policy as policy
from groundtruth_kb.tafe_dispatch_policy import (
    DispatchCandidate,
    DispatchNeed,
    evaluate_eligibility,
    select_dispatch_target,
)


def _need(**overrides: object) -> DispatchNeed:
    data = {
        "required_role": "loyal-opposition",
        "subject_scope": "gtkb-platform",
        "artifact_author_session_id": "session-author",
        "required_capabilities": ("bridge-review", "tafe-dispatch"),
        "owner_gate_blocked": False,
        "requires_workspace": True,
    }
    data.update(overrides)
    return DispatchNeed(**data)


def _candidate(**overrides: object) -> DispatchCandidate:
    data = {
        "harness_id": "B",
        "role": "loyal-opposition",
        "subject_scope": "gtkb-platform",
        "health_status": "active",
        "reviewer_precedence": 2,
        "active_session_id": "session-reviewer",
        "stage_lease_available": True,
        "workspace_available": True,
        "capabilities": {"bridge-review": True, "tafe-dispatch": True},
        "cost": 10.0,
        "model_identifier": "test-model",
    }
    data.update(overrides)
    return DispatchCandidate(**data)


def _gate(result: object, name: str) -> object:
    return next(gate for gate in result.gates if gate.name == name)


def test_all_hard_gates_pass_for_eligible_candidate() -> None:
    result = evaluate_eligibility(_need(), _candidate())

    assert result.eligible is True
    assert [gate.name for gate in result.gates] == [
        "role",
        "capability",
        "subject",
        "review_independence",
        "health",
        "stage_lease_availability",
        "owner_gate",
        "workspace_availability",
    ]
    assert all(gate.passed for gate in result.gates)


def test_each_hard_gate_fails_closed_when_its_input_is_invalid() -> None:
    cases = [
        ("role", _need(), _candidate(role="prime-builder")),
        ("capability", _need(), _candidate(capabilities={"bridge-review": True})),
        ("subject", _need(), _candidate(subject_scope="agent-red")),
        ("review_independence", _need(), _candidate(active_session_id="session-author")),
        ("health", _need(), _candidate(health_status="degraded")),
        ("stage_lease_availability", _need(), _candidate(stage_lease_available=False)),
        ("owner_gate", _need(owner_gate_blocked=True), _candidate()),
        ("workspace_availability", _need(), _candidate(workspace_available=False)),
    ]

    for gate_name, need, candidate in cases:
        result = evaluate_eligibility(need, candidate)

        assert result.eligible is False
        failed_gate = _gate(result, gate_name)
        assert failed_gate.passed is False
        assert failed_gate.reason


def test_subject_scope_all_covers_specific_need() -> None:
    result = evaluate_eligibility(_need(subject_scope="bridge"), _candidate(subject_scope="all"))

    assert result.eligible is True


def test_missing_active_session_fails_review_independence_closed() -> None:
    result = evaluate_eligibility(_need(), _candidate(active_session_id=None))

    assert result.eligible is False
    assert _gate(result, "review_independence").passed is False
    assert "fails closed" in _gate(result, "review_independence").reason


def test_workspace_is_ignored_when_need_does_not_require_workspace() -> None:
    result = evaluate_eligibility(
        _need(requires_workspace=False),
        _candidate(workspace_available=False),
    )

    assert result.eligible is True
    assert _gate(result, "workspace_availability").passed is True


def test_precedence_ranking_dominates_cost() -> None:
    expensive_high_precedence = _candidate(harness_id="A", reviewer_precedence=1, cost=1000.0)
    cheap_low_precedence = _candidate(harness_id="B", reviewer_precedence=2, cost=1.0)

    decision = select_dispatch_target(_need(), [cheap_low_precedence, expensive_high_precedence])

    assert decision.selected == "A"
    assert [candidate.harness_id for candidate in decision.ranked_candidates] == ["A", "B"]
    assert "reviewer_precedence" in decision.rationale


def test_cost_breaks_ties_only_within_equal_precedence() -> None:
    expensive = _candidate(harness_id="A", reviewer_precedence=1, cost=20.0)
    cheap = _candidate(harness_id="B", reviewer_precedence=1, cost=5.0)

    decision = select_dispatch_target(_need(), [expensive, cheap])

    assert decision.selected == "B"
    assert [candidate.harness_id for candidate in decision.ranked_candidates] == ["B", "A"]


def test_harness_id_provides_deterministic_final_tie_break() -> None:
    b = _candidate(harness_id="B", reviewer_precedence=1, cost=5.0)
    a = _candidate(harness_id="A", reviewer_precedence=1, cost=5.0)

    decision = select_dispatch_target(_need(), [b, a])

    assert decision.selected == "A"
    assert [candidate.harness_id for candidate in decision.ranked_candidates] == ["A", "B"]


def test_no_eligible_candidate_returns_none_with_breakdown() -> None:
    decision = select_dispatch_target(
        _need(),
        [
            _candidate(harness_id="A", role="prime-builder"),
            _candidate(harness_id="B", health_status="degraded"),
        ],
    )

    assert decision.selected is None
    assert decision.selected_candidate is None
    assert decision.ranked_candidates == ()
    assert len(decision.evaluations) == 2
    assert "No eligible dispatch target" in decision.rationale


def test_mixed_candidate_scenario_selects_expected_harness_and_reports_all_evaluations() -> None:
    same_session = _candidate(harness_id="A", active_session_id="session-author", reviewer_precedence=1)
    selected = _candidate(harness_id="B", reviewer_precedence=1, cost=4.0)
    eligible_but_later = _candidate(harness_id="C", reviewer_precedence=3, cost=1.0)

    decision = select_dispatch_target(_need(), [same_session, eligible_but_later, selected])

    assert decision.selected == "B"
    assert [candidate.harness_id for candidate in decision.ranked_candidates] == ["B", "C"]
    assert [result.candidate_harness_id for result in decision.evaluations] == ["A", "C", "B"]
    assert _gate(decision.evaluations[0], "review_independence").passed is False


def test_policy_module_does_not_expose_live_dispatch_or_io_surface() -> None:
    source = Path(policy.__file__).read_text(encoding="utf-8")

    assert "groundtruth_kb.db" not in source
    assert "subprocess" not in source
    assert "requests" not in source
    assert not hasattr(policy, "dispatch_tick")
    assert not hasattr(policy, "dispatch_health")
