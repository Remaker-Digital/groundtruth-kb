from __future__ import annotations

import ast

import pytest

from scripts.benchmarks import fixture_corpus
from scripts.benchmarks import harness_adaptation_impact as impact
from scripts.benchmarks import harness_quality_runner as runner


def _fixture() -> fixture_corpus.BenchmarkFixture:
    return fixture_corpus.require_valid_fixture_corpus()[0]


def _record(
    *,
    adaptation_id: str,
    adaptation_label: str,
    deterministic_score: float,
    fixture: fixture_corpus.BenchmarkFixture | None = None,
) -> dict[str, object]:
    fixture = fixture or _fixture()
    records = runner.build_dry_run_evidence_records(
        run_id="run-adaptation",
        harness_targets=(
            runner.BenchmarkHarnessTarget(
                harness_id="E",
                provider="cursor",
                model="cursor-agent",
                author_model_configuration="cursor synthetic benchmark",
                adaptation_id=adaptation_id,
                adaptation_label=adaptation_label,
            ),
        ),
        benchmark_mode="loyal_opposition",
        started_at="2026-07-01T08:00:00Z",
        ended_at="2026-07-01T08:00:01Z",
        fixtures=(fixture,),
    )
    record = dict(records[0])
    record["deterministic_score"] = deterministic_score
    record["input_tokens"] = 10
    record["output_tokens"] = 5
    record["estimated_cost"] = 0.02
    record["duration_ms"] = 100
    return record


def test_adaptation_identity_is_stable_and_compact_without_raw_inputs() -> None:
    first = impact.create_adaptation_identity(
        harness_id="E",
        label="cursor-route",
        version="v1",
        metadata={"skill": "bridge-review"},
        source_texts={"prompt-template": "raw prompt wording must not leak"},
    )
    second = impact.create_adaptation_identity(
        harness_id="E",
        label="cursor-route",
        version="v1",
        metadata={"skill": "bridge-review"},
        source_texts={"prompt-template": "raw prompt wording must not leak"},
    )

    payload = first.to_dict()

    assert first == second
    assert first.adaptation_id.startswith("adapt-")
    assert payload["raw_inputs_included"] is False
    assert "raw prompt wording" not in repr(payload)
    assert first.evidence_fields()["adaptation_label"] == "cursor-route"


def test_delta_requires_same_harness_mode_fixture_and_run_tier() -> None:
    baseline = _record(
        adaptation_id="adapt-baseline",
        adaptation_label="baseline",
        deterministic_score=0.5,
    )
    candidate = _record(
        adaptation_id="adapt-candidate",
        adaptation_label="candidate",
        deterministic_score=0.8,
    )
    candidate["input_tokens"] = 12

    delta = impact.compute_adaptation_delta(baseline, candidate)

    assert delta["deterministic_score_delta"] == 0.3
    assert delta["token_delta"] == 2
    assert delta["advisory_only"] is True

    candidate["fixture_id"] = "different-fixture"
    with pytest.raises(ValueError, match="share harness, mode, fixture, and run tier"):
        impact.compute_adaptation_delta(baseline, candidate)


def test_delta_set_rejects_mismatched_fixture_sets() -> None:
    fixtures = fixture_corpus.require_valid_fixture_corpus()
    baseline = _record(adaptation_id="adapt-baseline", adaptation_label="baseline", deterministic_score=0.5)
    candidate = _record(
        adaptation_id="adapt-candidate",
        adaptation_label="candidate",
        deterministic_score=0.8,
        fixture=fixtures[1],
    )

    with pytest.raises(ValueError, match="fixture sets differ"):
        impact.compute_adaptation_deltas((baseline,), (candidate,))


def test_impact_report_is_advisory_and_non_mutating() -> None:
    baseline = _record(adaptation_id="adapt-baseline", adaptation_label="baseline", deterministic_score=0.5)
    candidate = _record(adaptation_id="adapt-candidate", adaptation_label="candidate", deterministic_score=0.75)

    report = impact.build_adaptation_impact_report(
        (baseline,),
        (candidate,),
        run_id="run-adaptation",
        generated_at="2026-07-01T08:00:00Z",
    )

    assert report["advisory_only"] is True
    assert report["mutation_boundaries"] == {
        "membase_mutation": False,
        "bridge_mutation": False,
        "dispatcher_ranking_mutation": False,
        "harness_eligibility_mutation": False,
        "durable_role_assignment_mutation": False,
    }
    assert report["summary"]["pair_count"] == 1
    assert report["summary"]["average_deterministic_score_delta"] == 0.25


def test_adaptation_module_imports_no_live_mutating_surface() -> None:
    module_path = fixture_corpus.PROJECT_ROOT / "scripts/benchmarks/harness_adaptation_impact.py"
    tree = ast.parse(module_path.read_text(encoding="utf-8"))
    imported_modules: set[str] = set()
    call_names: set[str] = set()

    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imported_modules.update(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            imported_modules.add(node.module)
        elif isinstance(node, ast.Call):
            if isinstance(node.func, ast.Attribute):
                call_names.add(node.func.attr)
            elif isinstance(node.func, ast.Name):
                call_names.add(node.func.id)

    assert all(not module.startswith("groundtruth_kb.") for module in imported_modules)
    assert not {"write_text", "open", "run", "Popen"} & call_names
