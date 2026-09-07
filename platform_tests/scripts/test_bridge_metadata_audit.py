"""Tests for scripts/bridge_metadata_audit.py (WI-4938)."""

from __future__ import annotations

import json
from pathlib import Path

from scripts.bridge_metadata_audit import (
    COMPLIANCE_COMPLIANT,
    COMPLIANCE_MISSING_FIELDS,
    COMPLIANCE_SYNTHETIC_SESSION,
    audit_bridge_metadata,
    run_cli,
    write_audit_reports,
    write_grandfather_report,
)

CLEAN_ARTIFACT = """GO
author_identity: Prime Builder Cursor
author_harness_id: E
author_session_context_id: cursor-e-20260630-test-session-001
author_model: Composer
author_model_version: 2.5
author_model_configuration: Cursor interactive

Document: gtkb-clean-fixture
Version: 001
"""

MISSING_FIELD_ARTIFACT = """NEW
author_identity: Prime Builder Cursor
author_harness_id: E
author_model: Composer
author_model_version: 2.5
author_model_configuration: Cursor interactive

Document: gtkb-missing-field-fixture
Version: 001
"""

STATIC_ID_ARTIFACT_A = """GO
author_identity: OpenRouter Loyal Opposition
author_harness_id: F
author_session_context_id: openrouter-harness-f
author_model: deepseek/deepseek-v4-pro
author_model_version: deepseek-v4-pro
author_model_configuration: OpenRouter harness

Document: gtkb-static-id-fixture-a
Version: 001
"""

STATIC_ID_ARTIFACT_B = """VERIFIED
author_identity: OpenRouter Loyal Opposition
author_harness_id: F
author_session_context_id: openrouter-harness-f
author_model: deepseek/deepseek-v4-pro
author_model_version: deepseek-v4-pro
author_model_configuration: OpenRouter harness

Document: gtkb-static-id-fixture-b
Version: 001
"""


def _write_bridge(project_root: Path, name: str, content: str) -> None:
    bridge = project_root / "bridge"
    bridge.mkdir(parents=True, exist_ok=True)
    (bridge / name).write_text(content, encoding="utf-8")


def test_audit_classifies_clean_missing_and_static_fixtures(tmp_path: Path) -> None:
    _write_bridge(tmp_path, "gtkb-clean-fixture-001.md", CLEAN_ARTIFACT)
    _write_bridge(tmp_path, "gtkb-missing-field-fixture-001.md", MISSING_FIELD_ARTIFACT)
    _write_bridge(tmp_path, "gtkb-static-id-fixture-a-001.md", STATIC_ID_ARTIFACT_A)
    _write_bridge(tmp_path, "gtkb-static-id-fixture-b-001.md", STATIC_ID_ARTIFACT_B)

    report = audit_bridge_metadata(tmp_path)
    by_document = {finding.document: finding for finding in report.findings}

    assert by_document["gtkb-clean-fixture"].compliance == COMPLIANCE_COMPLIANT
    assert by_document["gtkb-missing-field-fixture"].compliance == COMPLIANCE_MISSING_FIELDS
    assert "author_session_context_id" in by_document["gtkb-missing-field-fixture"].missing_fields
    assert by_document["gtkb-static-id-fixture-a"].compliance == COMPLIANCE_SYNTHETIC_SESSION
    assert by_document["gtkb-static-id-fixture-b"].compliance == COMPLIANCE_SYNTHETIC_SESSION


def test_audit_json_output_is_deterministic(tmp_path: Path) -> None:
    _write_bridge(tmp_path, "gtkb-clean-fixture-001.md", CLEAN_ARTIFACT)
    _write_bridge(tmp_path, "gtkb-missing-field-fixture-001.md", MISSING_FIELD_ARTIFACT)

    timestamp = "2026-07-01T00:00:00Z"
    first = json.dumps(audit_bridge_metadata(tmp_path, generated_at=timestamp).to_dict(), sort_keys=True)
    second = json.dumps(audit_bridge_metadata(tmp_path, generated_at=timestamp).to_dict(), sort_keys=True)
    assert first == second


def test_state_report_writes_json_markdown_without_bridge_mutation(tmp_path: Path) -> None:
    _write_bridge(tmp_path, "gtkb-clean-fixture-001.md", CLEAN_ARTIFACT)
    bridge_path = tmp_path / "bridge" / "gtkb-clean-fixture-001.md"
    before = bridge_path.stat().st_mtime_ns

    report = audit_bridge_metadata(tmp_path, generated_at="2026-07-01T00:00:00Z")
    json_path, markdown_path = write_audit_reports(tmp_path, report)

    assert json_path.is_file()
    assert markdown_path.is_file()
    # Canon s17: reports default to the session-scoped scratchpad, never
    # `.gtkb-state`. Resolved via the same single authority the writer uses.
    from scripts.gtkb_session_id import session_scratch_dirname

    assert json_path.parent == tmp_path / "scratchpad" / session_scratch_dirname() / "bridge-metadata-audit"
    assert ".gtkb-state" not in json_path.parts
    assert markdown_path.parent == json_path.parent
    assert json.loads(json_path.read_text(encoding="utf-8"))["artifact_count"] == 1
    assert "Bridge author-metadata audit" in markdown_path.read_text(encoding="utf-8")
    assert bridge_path.stat().st_mtime_ns == before


def test_cli_json_exit_zero(tmp_path: Path, capsys) -> None:
    _write_bridge(tmp_path, "gtkb-clean-fixture-001.md", CLEAN_ARTIFACT)
    code = run_cli(["--project-root", str(tmp_path), "--json"])
    captured = capsys.readouterr()
    payload = json.loads(captured.out)
    assert code == 0
    assert payload["artifact_count"] == 1


def test_grandfather_report_writes_state_file(tmp_path: Path) -> None:
    _write_bridge(tmp_path, "gtkb-static-id-fixture-a-001.md", STATIC_ID_ARTIFACT_A)
    report = audit_bridge_metadata(tmp_path)
    out_path = write_grandfather_report(tmp_path, report)
    assert out_path.is_file()
    payload = json.loads(out_path.read_text(encoding="utf-8"))
    assert payload["report_kind"] == "grandfather_audit"
    assert payload["summary"][COMPLIANCE_SYNTHETIC_SESSION] == 1
