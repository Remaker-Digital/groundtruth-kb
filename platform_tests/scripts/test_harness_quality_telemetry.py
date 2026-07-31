from __future__ import annotations

import ast

import pytest

from scripts.benchmarks import fixture_corpus
from scripts.benchmarks import harness_quality_runner as runner
from scripts.benchmarks import harness_quality_telemetry as telemetry


def _record() -> dict[str, object]:
    fixture = fixture_corpus.require_valid_fixture_corpus()[0]
    target = runner.BenchmarkHarnessTarget(
        harness_id="A",
        provider="codex",
        model="gpt-5-codex",
        author_model_configuration="codex desktop synthetic benchmark",
    )
    record = runner.build_dry_run_evidence_records(
        run_id="run-telemetry",
        harness_targets=(target,),
        benchmark_mode="prime_builder",
        started_at="2026-06-30T08:00:00Z",
        ended_at="2026-06-30T08:00:01Z",
        fixtures=(fixture,),
    )[0]
    record = dict(record)
    record["failure_class"] = fixture.failure_classes[0]
    record["input_tokens"] = 11
    record["output_tokens"] = 7
    record["estimated_cost"] = 0.024
    record["deterministic_score"] = 1.0
    return record


def test_telemetry_rejects_missing_manifest_field() -> None:
    record = _record()
    record.pop("fixture_id")

    with pytest.raises(ValueError, match="missing evidence fields"):
        telemetry.to_tafe_stage_attempt(record)


def test_telemetry_rejects_unknown_failure_class() -> None:
    record = _record()
    record["failure_class"] = "not-a-real-class"

    with pytest.raises(ValueError, match="unknown failure_class"):
        telemetry.to_benchmark_result_record(record)


def test_author_model_configuration_propagates_to_both_outputs() -> None:
    mapped = telemetry.map_evidence_to_telemetry(_record())

    assert mapped["tafe_stage_attempt"]["metadata"]["author_model_configuration"] == (
        "codex desktop synthetic benchmark"
    )
    assert mapped["benchmark_result"]["author_model_configuration"] == "codex desktop synthetic benchmark"


def test_failure_class_preserved_in_tafe_metadata_and_result_record() -> None:
    record = _record()
    mapped = telemetry.map_evidence_to_telemetry(record)

    assert mapped["tafe_stage_attempt"]["metadata"]["failure_class"] == record["failure_class"]
    assert mapped["benchmark_result"]["failure_class"] == record["failure_class"]
    assert mapped["tafe_stage_attempt"]["metadata"]["adaptation_id"] == record["adaptation_id"]
    assert mapped["benchmark_result"]["adaptation_id"] == record["adaptation_id"]


def test_token_cost_reconciliation_is_deterministic() -> None:
    mapped = telemetry.map_evidence_to_telemetry(_record())

    assert mapped["tafe_stage_attempt"]["token_count"] == 18
    assert mapped["benchmark_result"]["token_count"] == 18
    assert mapped["tafe_stage_attempt"]["cost"] == 0.024
    assert mapped["benchmark_result"]["estimated_cost"] == 0.024


def test_idempotency_key_is_stable_for_fixed_record() -> None:
    record = _record()

    assert telemetry.idempotency_key_for(record) == telemetry.idempotency_key_for(dict(record))
    assert telemetry.idempotency_key_for(record).startswith("bench-telemetry-")


def test_outputs_are_advisory_and_do_not_persist_live_state() -> None:
    mapped = telemetry.map_evidence_to_telemetry(_record())

    assert mapped["tafe_stage_attempt"]["advisory_only"] is True
    assert mapped["benchmark_result"]["advisory_only"] is True
    assert "write_path" not in mapped["tafe_stage_attempt"]
    assert "write_path" not in mapped["benchmark_result"]


def test_telemetry_imports_no_live_mutating_surface() -> None:
    module_path = fixture_corpus.PROJECT_ROOT / "scripts/benchmarks/harness_quality_telemetry.py"
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
