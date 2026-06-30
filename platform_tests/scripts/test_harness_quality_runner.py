from __future__ import annotations

import ast

import pytest

from scripts.benchmarks import fixture_corpus
from scripts.benchmarks import harness_quality_manifest as manifest
from scripts.benchmarks import harness_quality_runner as runner
from scripts.benchmarks.benchmark_dispatch_envelope import create_benchmark_dispatch_envelope


def _fixture() -> fixture_corpus.BenchmarkFixture:
    return fixture_corpus.require_valid_fixture_corpus()[0]


def _target() -> runner.BenchmarkHarnessTarget:
    return runner.BenchmarkHarnessTarget(
        harness_id="A",
        provider="codex",
        model="gpt-5-codex",
        author_model_configuration="codex desktop synthetic benchmark",
    )


def test_evidence_record_is_manifest_complete_and_exact() -> None:
    fixture = _fixture()
    target = _target()
    envelope = create_benchmark_dispatch_envelope(
        run_id="run-001",
        harness_id=target.harness_id,
        benchmark_mode="prime_builder",
        provider=target.provider,
        model=target.model,
        author_model_configuration=target.author_model_configuration,
        run_tier="smoke",
        fixture_id=fixture.fixture_id,
    )

    record = runner.build_evidence_record(
        envelope=envelope,
        fixture=fixture,
        started_at="2026-06-30T08:00:00Z",
        ended_at="2026-06-30T08:00:01Z",
    )

    assert tuple(record) == manifest.REQUIRED_EVIDENCE_FIELDS
    assert set(record) == set(manifest.REQUIRED_EVIDENCE_FIELDS)
    assert record["dispatch_envelope_id"].startswith("bench-env-")
    assert record["failure_class"] == "unscored"


def test_author_model_configuration_propagates_from_dispatch_envelope() -> None:
    records = runner.build_dry_run_evidence_records(
        run_id="run-configuration",
        harness_targets=(_target(),),
        benchmark_mode="prime_builder",
        started_at="2026-06-30T08:00:00Z",
        ended_at="2026-06-30T08:00:01Z",
        fixtures=(_fixture(),),
    )

    assert len(records) == 1
    assert records[0]["author_model_configuration"] == "codex desktop synthetic benchmark"
    assert records[0]["provider"] == "codex"
    assert records[0]["model"] == "gpt-5-codex"


def test_failure_class_is_closed_taxonomy() -> None:
    fixture = _fixture()
    envelope = create_benchmark_dispatch_envelope(
        run_id="run-taxonomy",
        harness_id="A",
        benchmark_mode="prime_builder",
        provider="codex",
        model="gpt-5-codex",
        author_model_configuration="codex desktop synthetic benchmark",
        run_tier="smoke",
        fixture_id=fixture.fixture_id,
    )

    record = runner.build_evidence_record(
        envelope=envelope,
        fixture=fixture,
        started_at="2026-06-30T08:00:00Z",
        ended_at="2026-06-30T08:00:01Z",
        failure_class=fixture.failure_classes[0],
    )

    assert record["failure_class"] in manifest.FAILURE_CLASSES
    with pytest.raises(ValueError, match="unknown failure_class"):
        runner.build_evidence_record(
            envelope=envelope,
            fixture=fixture,
            started_at="2026-06-30T08:00:00Z",
            ended_at="2026-06-30T08:00:01Z",
            failure_class="not-a-real-class",
        )


def test_benchmark_mode_is_synthetic_and_cannot_change_durable_roles() -> None:
    records = runner.build_dry_run_evidence_records(
        run_id="run-lo",
        harness_targets=(runner.BenchmarkHarnessTarget(harness_id="E"),),
        benchmark_mode="loyal_opposition",
        started_at="2026-06-30T08:00:00Z",
        ended_at="2026-06-30T08:00:01Z",
        fixtures=(_fixture(),),
    )

    assert records[0]["benchmark_mode"] == "loyal_opposition"
    assert all(mode.durable_role_changes_allowed is False for mode in manifest.BENCHMARK_MODES)
    with pytest.raises(ValueError, match="unknown benchmark_mode"):
        runner.build_dry_run_evidence_records(
            run_id="run-bad-mode",
            harness_targets=(_target(),),
            benchmark_mode="prime-builder",
            started_at="2026-06-30T08:00:00Z",
            ended_at="2026-06-30T08:00:01Z",
            fixtures=(_fixture(),),
        )


def test_runner_consumes_fixture_corpus_loader_contract() -> None:
    fixtures = fixture_corpus.require_valid_fixture_corpus()
    records = runner.build_dry_run_evidence_records(
        run_id="run-fixtures",
        harness_targets=(_target(),),
        benchmark_mode="prime_builder",
        started_at="2026-06-30T08:00:00Z",
        ended_at="2026-06-30T08:00:01Z",
        fixtures=fixtures,
    )

    assert len(records) == len(fixtures)
    assert {record["fixture_id"] for record in records} == {fixture.fixture_id for fixture in fixtures}
    assert all(record["outcome"] == runner.DRY_RUN_OUTCOME for record in records)
    assert all(record["artifact_links"] for record in records)


def test_record_to_dict_is_json_friendly_without_schema_loss() -> None:
    record = runner.build_dry_run_evidence_records(
        run_id="run-json",
        harness_targets=(_target(),),
        benchmark_mode="prime_builder",
        started_at="2026-06-30T08:00:00Z",
        ended_at="2026-06-30T08:00:01Z",
        fixtures=(_fixture(),),
    )[0]

    payload = runner.record_to_dict(record)

    assert set(payload) == set(manifest.REQUIRED_EVIDENCE_FIELDS)
    assert isinstance(payload["required_source_citations"], list)
    assert isinstance(payload["artifact_links"], list)


def test_runner_imports_no_live_mutating_surface() -> None:
    module_path = fixture_corpus.PROJECT_ROOT / "scripts/benchmarks/harness_quality_runner.py"
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
