from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

from click.testing import CliRunner

REPO_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO_ROOT / "groundtruth-kb" / "src"))

from groundtruth_kb.cli import main  # noqa: E402


def _ref(name: str, *, approved: bool = False, schema_id: str | None = None) -> dict[str, object]:
    result: dict[str, object] = {"id": name, "sha256": f"sha256:{hashlib.sha256(name.encode()).hexdigest()}"}
    if approved:
        result["approved"] = True
    if schema_id is not None:
        result["schema_id"] = schema_id
    return result


def _packet() -> dict[str, object]:
    metric = {
        "name": "quality",
        "baseline": 0.8,
        "candidate": 0.9,
        "expected_direction": "increase",
        "minimum_delta": 0.01,
    }
    guardrail = {
        "name": "failures",
        "baseline": 0.1,
        "candidate": 0.05,
        "expected_direction": "not_increase",
        "minimum_delta": 0,
    }
    return {
        "hypothesis": "candidate improves quality without increasing failures",
        "target_dimension": "ranking_weight",
        "mode": "shadow",
        "baseline": _ref("baseline"),
        "candidate": _ref("candidate"),
        "population": {**_ref("fixtures"), "fixture_ids": ["one", "two"]},
        "profile_filters": {"role": "loyal-opposition"},
        "source_window": {"start": "2026-07-01T00:00:00Z", "end": "2026-07-10T00:00:00Z"},
        "sample_sufficiency": {"observed": 25, "minimum": 20},
        "coverage_requirement": {"observed_ratio": 1.0, "minimum_ratio": 0.9},
        "freshness": {"status": "fresh"},
        "evidence": {
            "metrics_snapshot": _ref("metrics", schema_id="gtkb.dispatch_default_metrics_snapshot.v1"),
            "benchmark": _ref("benchmark"),
            "adaptation": _ref("adaptation"),
            "scoring_snapshot": _ref("scoring", approved=True),
        },
        "primary_quality_metrics": [metric],
        "operational_guardrails": [guardrail],
        "failure_metrics": [guardrail],
        "costs": {
            "provider_reported": {"baseline": 1.0, "candidate": 0.8, "currency": "USD"},
            "benchmark_estimated": {"baseline": 0.9, "candidate": 0.7, "currency": "USD"},
        },
        "limitations": [],
    }


def _project(tmp_path: Path) -> tuple[Path, Path, Path]:
    root = tmp_path / "project"
    root.mkdir()
    config = root / "groundtruth.toml"
    config.write_text('[groundtruth]\ndb_path = "./groundtruth.db"\nproject_root = "."\n', encoding="utf-8")
    (root / "config" / "dispatcher").mkdir(parents=True)
    (root / "harness-state").mkdir()
    tracked = {
        root / "config" / "dispatcher" / "rules.toml": "selection_order = []\n",
        root / "harness-state" / "harness-registry.json": '{"schema_version":1,"harnesses":[]}\n',
        root / "approved-scoring-snapshot.json": '{"id":"production","approved":true}\n',
    }
    for path, content in tracked.items():
        path.write_text(content, encoding="utf-8")
    evidence = root / "tuning-evidence.json"
    evidence.write_text(json.dumps(_packet()), encoding="utf-8")
    return root, config, evidence


def test_tuning_evaluate_cli_is_deterministic_read_only_and_advisory_only(tmp_path: Path) -> None:
    root, config, evidence = _project(tmp_path)
    tracked = [
        root / "config" / "dispatcher" / "rules.toml",
        root / "harness-state" / "harness-registry.json",
        root / "approved-scoring-snapshot.json",
        evidence,
    ]
    before = {path: path.read_bytes() for path in tracked}
    args = [
        "--config",
        str(config),
        "bridge",
        "dispatch",
        "tuning",
        "evaluate",
        "--input",
        str(evidence),
        "--json",
    ]

    first = CliRunner().invoke(main, args)
    second = CliRunner().invoke(main, args)

    assert first.exit_code == 0, first.output
    assert second.exit_code == 0, second.output
    assert first.output == second.output
    payload = json.loads(first.output)
    assert payload["schema_id"] == "gtkb.dispatch_tuning_advisory.v1"
    assert payload["outcome"] == "recommend"
    assert payload["advisory_only"] is True
    assert payload["production_activation_allowed"] is False
    assert {path: path.read_bytes() for path in tracked} == before


def test_tuning_cli_registers_no_apply_or_activation_command(tmp_path: Path) -> None:
    _root, config, _evidence = _project(tmp_path)

    result = CliRunner().invoke(main, ["--config", str(config), "bridge", "dispatch", "tuning", "--help"])

    assert result.exit_code == 0, result.output
    assert "evaluate" in result.output
    assert "apply" not in result.output.lower()
    assert "activate" not in result.output.lower()


def test_tuning_cli_returns_insufficient_for_well_formed_but_incomplete_evidence(tmp_path: Path) -> None:
    _root, config, evidence = _project(tmp_path)
    evidence.write_text(json.dumps({"mode": "offline", "prompt": "must not appear"}), encoding="utf-8")

    result = CliRunner().invoke(
        main,
        [
            "--config",
            str(config),
            "bridge",
            "dispatch",
            "tuning",
            "evaluate",
            "--input",
            str(evidence),
            "--json",
        ],
    )

    assert result.exit_code == 0, result.output
    payload = json.loads(result.output)
    assert payload["outcome"] == "insufficient_evidence"
    assert payload["insufficiency_reasons"]
    assert "must not appear" not in result.output


def test_tuning_cli_rejects_evidence_outside_project_root(tmp_path: Path) -> None:
    _root, config, _evidence = _project(tmp_path)
    outside = tmp_path / "outside.json"
    outside.write_text(json.dumps(_packet()), encoding="utf-8")

    result = CliRunner().invoke(
        main,
        [
            "--config",
            str(config),
            "bridge",
            "dispatch",
            "tuning",
            "evaluate",
            "--input",
            str(outside),
            "--json",
        ],
    )

    assert result.exit_code != 0
    assert "inside the project root" in result.output
