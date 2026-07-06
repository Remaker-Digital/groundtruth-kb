"""Tests for the WI-4968 harness envelope-equivalence evidence helper."""

from __future__ import annotations

import json
from pathlib import Path

from scripts import harness_envelope_equivalence as helper


def _write_json(path: Path, payload: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")


def _seed_registry(root: Path) -> None:
    _write_json(
        root / "harness-state" / "harness-registry.json",
        {
            "schema_version": 1,
            "harnesses": [
                {
                    "id": "A",
                    "harness_name": "codex",
                    "role": ["prime-builder"],
                    "status": "active",
                    "activity_envelope_projection_mode": "native",
                    "compact_result_envelope_mode": "native",
                    "compact_session_envelope_mode": "native",
                    "full_transcript_archive_required": False,
                },
                {
                    "id": "D",
                    "harness_name": "ollama",
                    "role": ["loyal-opposition"],
                    "status": "active",
                    "activity_envelope_projection_mode": "compact-provider",
                    "compact_result_envelope_mode": "compact-provider",
                    "compact_session_envelope_mode": "compact-provider",
                    "full_transcript_archive_required": False,
                },
                {
                    "id": "F",
                    "harness_name": "openrouter",
                    "role": ["loyal-opposition"],
                    "status": "active",
                    "activity_envelope_projection_mode": "compact-provider",
                    "compact_result_envelope_mode": "",
                    "compact_session_envelope_mode": "compact-provider",
                    "full_transcript_archive_required": False,
                },
            ],
        },
    )
    _write_json(
        root / "harness-state" / "codex" / "session-envelope.json",
        {
            "envelope_schema_version": 1,
            "harness_id": "A",
            "harness_name": "codex",
            "session_id": "A-fixture",
            "role_resolved": "prime-builder",
            "status": "open",
        },
    )
    _write_json(
        root / "harness-state" / "openrouter" / "session-envelope-archive" / "2026-session-envelope.json",
        {
            "envelope_schema_version": 1,
            "harness_id": "F",
            "harness_name": "openrouter",
            "session_id": "F-fixture",
            "role_resolved": "loyal-opposition",
            "status": "closed",
        },
    )


def _seed_capability_registry(root: Path) -> None:
    path = root / "config" / "agent-control" / "harness-capability-registry.toml"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        """
[harnesses.codex]
activity_envelope_manifest_source = "config/agent-control/activity-disposition-profiles.toml"
result_envelope_limitations = "native compact result/session evidence"

[harnesses.ollama]
activity_envelope_manifest_source = "config/agent-control/activity-disposition-profiles.toml"
result_envelope_limitations = "provider compact result/session evidence"
""".lstrip(),
        encoding="utf-8",
    )


def _seed_waivers(root: Path) -> None:
    path = root / "config" / "harness-parity" / "phase2-waivers.toml"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        """
[[waivers]]
id = "WAIVER-P2-OLLAMA-FULL-TRANSCRIPT-ARCHIVE"
harness = "ollama"
dimension = "full_transcript_archive"
reason_class = "vendor_limitation"
rationale = "Ollama is assessed through compact dispatch/result/session envelopes."
owner_decision = "DELIB-20260701-ENVELOPE-SHARDING-EXECUTE-RETIRE"
evidence = "config/agent-control/harness-capability-registry.toml::[harnesses.ollama]"
evaluator_behavior = "waive"
status = "active"

[[waivers]]
id = "WAIVER-P2-OPENROUTER-FULL-TRANSCRIPT-ARCHIVE"
harness = "openrouter"
dimension = "full_transcript_archive"
reason_class = "vendor_limitation"
rationale = "OpenRouter is assessed through compact dispatch/result/session envelopes."
owner_decision = "DELIB-20260701-ENVELOPE-SHARDING-EXECUTE-RETIRE"
evidence = "config/agent-control/harness-capability-registry.toml::[harnesses.openrouter]"
evaluator_behavior = "waive"
status = "active"

[[waivers]]
id = "WAIVER-RETIRED"
harness = "codex"
dimension = "full_transcript_archive"
reason_class = "obsolete"
rationale = "retired"
status = "retired"
""".lstrip(),
        encoding="utf-8",
    )


def _seed_root(root: Path) -> None:
    _seed_registry(root)
    _seed_capability_registry(root)
    _seed_waivers(root)


def test_build_report_classifies_equivalent_limited_waived_missing_and_superseded(tmp_path: Path) -> None:
    _seed_root(tmp_path)

    report = helper.build_report(project_root=tmp_path)

    assert report["status"] == "WARN"
    lanes = {lane["harness_name"]: lane for lane in report["lanes"]}
    assert lanes["codex"]["overall_classification"] == helper.STATUS_EQUIVALENT
    assert lanes["ollama"]["dimensions"]["result"]["status"] == helper.STATUS_LIMITED
    assert lanes["ollama"]["dimensions"]["full_transcript_archive"]["status"] == helper.STATUS_WAIVED
    assert lanes["ollama"]["overall_classification"] == helper.STATUS_MISSING
    assert lanes["ollama"]["dimensions"]["session_envelope_evidence"]["status"] == helper.STATUS_MISSING
    assert lanes["openrouter"]["dimensions"]["result"]["status"] == helper.STATUS_MISSING
    assert all(
        lane["dimensions"]["verified_sharding_boundary"]["status"] == helper.STATUS_SUPERSEDED
        for lane in lanes.values()
    )
    assert report["summary"]["typed_waiver_count"] == 2


def test_render_markdown_includes_baseline_waivers_and_evidence_gaps(tmp_path: Path) -> None:
    _seed_root(tmp_path)
    report = helper.build_report(project_root=tmp_path)

    markdown = helper.render_markdown(report)

    assert "WI-4950" in markdown
    assert "WAIVER-P2-OLLAMA-FULL-TRANSCRIPT-ARCHIVE" in markdown
    assert "`ollama`: `missing-evidence`" in markdown
    assert "bridge/gtkb-envelope-sharding-harness-projection-parity-004.md" in markdown


def test_main_writes_json_output(tmp_path: Path) -> None:
    _seed_root(tmp_path)
    output = tmp_path / "out" / "report.json"

    exit_code = helper.main(["--project-root", str(tmp_path), "--json", "--output", str(output)])

    assert exit_code == 0
    payload = json.loads(output.read_text(encoding="utf-8"))
    assert payload["evidence_id"] == helper.EVIDENCE_ID
    assert payload["summary"]["harness_count"] == 3
