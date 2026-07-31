from __future__ import annotations

import ast

from scripts.benchmarks import fixture_corpus
from scripts.benchmarks import harness_quality_reporting as reporting
from scripts.benchmarks import harness_quality_runner as runner
from scripts.benchmarks import harness_quality_scoring as scoring
from scripts.benchmarks import harness_quality_telemetry as telemetry


def _target() -> runner.BenchmarkHarnessTarget:
    return runner.BenchmarkHarnessTarget(
        harness_id="A",
        provider="codex",
        model="gpt-5-codex",
        author_model_configuration="codex desktop synthetic benchmark",
    )


def _records(run_id: str, run_tier: str) -> tuple[dict[str, object], ...]:
    fixture = fixture_corpus.require_valid_fixture_corpus()[0]
    records = runner.build_dry_run_evidence_records(
        run_id=run_id,
        harness_targets=(_target(),),
        benchmark_mode="prime_builder",
        started_at="2026-06-30T08:00:00Z",
        ended_at="2026-06-30T08:00:01Z",
        run_tier=run_tier,
        fixtures=(fixture,),
    )
    record = dict(records[0])
    record["failure_class"] = fixture.failure_classes[0]
    record["input_tokens"] = 10
    record["output_tokens"] = 5
    record["estimated_cost"] = 0.02
    return (record,)


def test_cadence_report_separates_smoke_full_and_adjudicated_tiers() -> None:
    payload = {"run_id": "run-report", "evidence_records": list(_records("run-report", "smoke"))}

    report = reporting.build_cadence_report(payload, generated_at="2026-06-30T08:00:00Z")
    tiers = {tier["tier_id"]: tier for tier in report["tiers"]}

    assert report["advisory_only"] is True
    assert tiers["smoke"]["record_count"] == 1
    assert tiers["full_quality"]["record_count"] == 0
    assert tiers["adjudicated_calibration"]["includes_adjudication"] is True
    assert tiers["smoke"]["estimated_cost"] == 0.02
    assert tiers["smoke"]["adaptation_ids"] == ["adaptation-default"]
    assert report["summary"]["adaptation_count"] == 1


def test_report_consumes_scoring_and_telemetry_payloads_without_mutation() -> None:
    fixture = fixture_corpus.require_valid_fixture_corpus()[0]
    records = _records("run-scored", "full_quality")
    scoring_payload = scoring.score_evidence_records(tuple(dict(record) for record in records), fixtures=(fixture,))
    telemetry_payload = {
        "records": [telemetry.to_benchmark_result_record(dict(records[0]))],
    }

    report = reporting.build_cadence_report(
        {"run_id": "run-scored", "records": list(records)},
        scoring_payload=scoring_payload,
        telemetry_payload=telemetry_payload,
        generated_at="2026-06-30T08:00:00Z",
    )
    full_quality = {tier["tier_id"]: tier for tier in report["tiers"]}["full_quality"]

    assert full_quality["average_deterministic_score"] == 1.0
    assert full_quality["telemetry_record_count"] == 1
    assert report["mutation_boundaries"] == {
        "membase_mutation": False,
        "bridge_mutation": False,
        "dispatcher_ranking_mutation": False,
        "harness_eligibility_mutation": False,
    }


def test_report_adds_trend_deltas_and_advisory_suggestions() -> None:
    current = {"run_id": "run-current", "evidence_records": list(_records("run-current", "smoke"))}
    previous = {"run_id": "run-previous", "evidence_records": []}

    report = reporting.build_cadence_report(
        current,
        previous_payload=previous,
        generated_at="2026-06-30T08:00:00Z",
    )
    smoke_trend = {trend["tier_id"]: trend for trend in report["trends"]}["smoke"]

    assert smoke_trend["record_count_delta"] == 1.0
    assert any(item["kind"] == "coverage_gap" for item in report["remediation_suggestions"])
    assert all(item["advisory_only"] is True for item in report["remediation_suggestions"])


def test_render_markdown_contains_tier_table_and_bridge_topics() -> None:
    report = reporting.build_cadence_report(
        {"run_id": "run-md", "evidence_records": list(_records("run-md", "smoke"))},
        generated_at="2026-06-30T08:00:00Z",
    )

    markdown = reporting.render_markdown(report)

    assert "# Harness quality cadence report run-md" in markdown
    assert "| `smoke` | 1 |" in markdown
    assert "Adaptations" in markdown
    assert "candidate bridge" in markdown


def test_reporting_module_imports_no_live_mutating_surface() -> None:
    module_path = fixture_corpus.PROJECT_ROOT / "scripts/benchmarks/harness_quality_reporting.py"
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
