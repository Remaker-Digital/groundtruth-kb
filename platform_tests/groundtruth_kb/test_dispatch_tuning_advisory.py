from __future__ import annotations

import copy
import hashlib
import json
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT / "groundtruth-kb" / "src"))

from groundtruth_kb import dispatch_tuning_advisory as advisory  # noqa: E402


def _ref(name: str, *, approved: bool = False, schema_id: str | None = None) -> dict[str, object]:
    result: dict[str, object] = {"id": name, "sha256": f"sha256:{hashlib.sha256(name.encode()).hexdigest()}"}
    if approved:
        result["approved"] = True
    if schema_id is not None:
        result["schema_id"] = schema_id
    return result


def _packet() -> dict[str, object]:
    return {
        "hypothesis": "prefer lower-cost profile when quality is retained",
        "target_dimension": "model_profile",
        "mode": "benchmark",
        "baseline": _ref("baseline-profile"),
        "candidate": _ref("candidate-profile"),
        "population": {**_ref("fixture-set-1"), "fixture_ids": ["fixture-b", "fixture-a"]},
        "profile_filters": {"role": "loyal-opposition", "complexity": "medium"},
        "source_window": {"start": "2026-07-01T00:00:00Z", "end": "2026-07-10T00:00:00Z"},
        "sample_sufficiency": {"observed": 40, "minimum": 20},
        "coverage_requirement": {"observed_ratio": 0.95, "minimum_ratio": 0.9},
        "freshness": {"status": "fresh"},
        "evidence": {
            "metrics_snapshot": _ref(
                "metrics-snapshot",
                schema_id="gtkb.dispatch_default_metrics_snapshot.v1",
            ),
            "benchmark": _ref("benchmark-evidence"),
            "adaptation": _ref("adaptation-evidence"),
            "scoring_snapshot": _ref("scoring-snapshot", approved=True),
        },
        "primary_quality_metrics": [
            {
                "name": "verification_rate",
                "baseline": 0.9,
                "candidate": 0.94,
                "expected_direction": "increase",
                "minimum_delta": 0.01,
            }
        ],
        "operational_guardrails": [
            {
                "name": "elapsed_seconds",
                "baseline": 50,
                "candidate": 48,
                "expected_direction": "not_increase",
                "minimum_delta": 0,
            }
        ],
        "failure_metrics": [
            {
                "name": "failure_rate",
                "baseline": 0.08,
                "candidate": 0.05,
                "expected_direction": "decrease",
                "minimum_delta": 0.01,
            }
        ],
        "costs": {
            "provider_reported": {"baseline": 2.5, "candidate": 1.5, "currency": "USD"},
            "benchmark_estimated": {"baseline": 2.4, "candidate": 1.4, "currency": "USD"},
        },
        "limitations": ["benchmark population only"],
    }


def test_advisory_is_deterministic_content_addressed_and_complete() -> None:
    packet = _packet()
    reordered = copy.deepcopy(packet)
    reordered["evidence"] = dict(reversed(list(reordered["evidence"].items())))
    reordered["population"]["fixture_ids"].reverse()

    first = advisory.evaluate_dispatch_tuning(packet)
    second = advisory.evaluate_dispatch_tuning(reordered)

    assert first == second
    assert json.dumps(first, sort_keys=True, separators=(",", ":")) == json.dumps(
        second, sort_keys=True, separators=(",", ":")
    )
    assert first["schema_id"] == advisory.SCHEMA_ID
    assert first["outcome"] == "recommend"
    assert first["advisory_only"] is True
    assert first["production_activation_allowed"] is False
    assert first["insufficiency_reasons"] == []
    assert first["limitations"] == ["benchmark population only"]
    assert set(first["evidence"]) == {"metrics_snapshot", "benchmark", "adaptation", "scoring_snapshot"}
    assert first["comparison"]["population"]["fixture_ids"] == ["fixture-a", "fixture-b"]


def test_valid_candidate_that_fails_quality_is_not_recommended() -> None:
    packet = _packet()
    packet["primary_quality_metrics"][0]["candidate"] = 0.85

    result = advisory.evaluate_dispatch_tuning(packet)

    assert result["outcome"] == "do_not_recommend"
    assert result["rationale"] == "candidate_failed_quality_or_guardrail"
    assert result["insufficiency_reasons"] == []


@pytest.mark.parametrize(
    ("mutation", "reason"),
    [
        (lambda packet: packet.update(mode="live"), "comparison_mode_not_isolated"),
        (lambda packet: packet["freshness"].update(status="stale"), "evidence_stale_or_freshness_unknown"),
        (lambda packet: packet["sample_sufficiency"].update(observed=5), "sample_insufficient"),
        (lambda packet: packet["coverage_requirement"].update(observed_ratio=0.5), "coverage_insufficient"),
        (lambda packet: packet["evidence"].pop("adaptation"), "adaptation_missing_or_untraceable"),
        (
            lambda packet: packet["evidence"]["metrics_snapshot"].update(schema_id="wrong-schema"),
            "metrics_snapshot_missing_or_untraceable",
        ),
        (lambda packet: packet["population"].pop("sha256"), "population_missing_empty_or_untraceable"),
        (
            lambda packet: packet["candidate"].update(sha256="not-content-addressed"),
            "baseline_or_candidate_not_content_addressed",
        ),
    ],
)
def test_stale_incomplete_untraceable_or_insufficient_evidence_fails_closed(mutation, reason: str) -> None:
    packet = _packet()
    mutation(packet)

    result = advisory.evaluate_dispatch_tuning(packet)

    assert result["outcome"] == "insufficient_evidence"
    assert reason in result["insufficiency_reasons"]
    assert result["production_activation_allowed"] is False


def test_output_is_allowlisted_and_cost_sources_remain_separate() -> None:
    packet = _packet()
    packet.update(
        prompt="forbidden prompt",
        messages=["forbidden message"],
        tool_arguments={"credential": "forbidden secret"},
        provider_body={"generated_text": "forbidden body"},
        environment={"TOKEN": "forbidden environment"},
    )

    result = advisory.evaluate_dispatch_tuning(packet)
    serialized = json.dumps(result, sort_keys=True)

    assert "forbidden" not in serialized
    assert set(result["measurements"]["costs"]) == {"provider_reported", "benchmark_estimated"}
    assert result["measurements"]["costs"]["provider_reported"]["candidate"] == 1.5
    assert result["measurements"]["costs"]["benchmark_estimated"]["candidate"] == 1.4


def test_production_activation_always_refuses_without_future_authority_chain() -> None:
    with pytest.raises(advisory.ProductionActivationRefused, match="separate specification, PAUTH, GO, and gate"):
        advisory.assert_production_activation_forbidden(
            advisory.evaluate_dispatch_tuning(_packet()),
            authorization_chain={"claimed": True},
        )
