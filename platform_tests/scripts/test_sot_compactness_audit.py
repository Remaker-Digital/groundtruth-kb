from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
HELPER = REPO_ROOT / "scripts" / "sot_compactness_audit.py"


def _load():
    spec = importlib.util.spec_from_file_location("sot_compactness_audit", HELPER)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


_h = _load()


def test_registry_is_valid_and_covers_required_sot_classes() -> None:
    registry = _h.default_registry()
    assert _h.validate_registry(registry) == ()

    classes = {record.sot_class for record in registry}
    assert "MemBase work_items/projects" in classes
    assert "Deliberation Archive" in classes
    assert "Dispatcher daemon state" in classes
    assert "Harness-local transcript metadata" in classes
    assert "LO advisory dropbox and bridge ADVISORY threads" in classes
    assert "Bridge numbered file chain" in classes
    assert "MemBase project_authorizations" in classes


@pytest.mark.parametrize(
    ("command", "expected"),
    [
        ("gt bridge show demo --json --compact", _h.COMMAND_KIND_COMPACT),
        ("python scripts/advisory_backlog_router.py --dry-run --compact", _h.COMMAND_KIND_COMPACT),
        ("gt deliberations search compact --limit 5 --json", _h.COMMAND_KIND_BOUNDED),
        ("gt session envelope show --harness-name codex", _h.COMMAND_KIND_BOUNDED),
        ("gt bridge show demo --json --history", _h.COMMAND_KIND_ARCHIVAL),
        ("gt projects show PROJECT-X --json", _h.COMMAND_KIND_UNCLASSIFIED),
    ],
)
def test_command_classification(command: str, expected: str) -> None:
    assert _h.classify_command(command) == expected


def test_duplicate_coverage_detects_wi4947_surfaces_as_covered_not_gaps() -> None:
    rows = _h.audit_registry()
    duplicate_ids = {row.surface.surface_id for row in rows if row.status == _h.STATUS_COVERED_DUPLICATE}

    assert "bridge-current-thread" in duplicate_ids
    assert "bridge-role-scan" in duplicate_ids
    assert all(row.status != _h.STATUS_GAP for row in rows if "WI-4947" in row.surface.coverage_refs)


def test_gaps_have_concrete_follow_on_dispositions() -> None:
    rows = _h.audit_registry()
    gaps = [row for row in rows if row.status == _h.STATUS_GAP]

    assert {row.surface.surface_id for row in gaps} == {"membase-project-authorization", "dispatcher-status"}
    assert all(row.surface.follow_on_disposition.startswith("Follow-on:") for row in gaps)
    assert all(row.surface.governing_specs for row in gaps)


def test_markdown_report_includes_summary_gaps_and_corrected_deliberation_refs() -> None:
    rows = _h.audit_registry()
    markdown = _h.render_markdown_report(rows, generated_at="2026-07-06T04-40-00Z")

    assert "# Harness Equivalence Phase 3 SoT Compactness Audit" in markdown
    assert "| `gap` | 2 |" in markdown
    assert "Project authorization / PAUTH detail" in markdown
    assert "Dispatcher health and selection status" in markdown
    assert "DELIB-202665119" in markdown
    assert "DELIB-202665127" in markdown
    assert "DELIB-20260701-ENVELOPE-SHARDING-EXECUTE-RETIRE` is not used as evidence" in markdown


def test_rows_as_json_is_compact_and_omits_raw_payloads() -> None:
    payload = _h.rows_as_json(_h.audit_registry())
    encoded = json.dumps(payload, sort_keys=True)

    assert payload["work_item_id"] == "WI-4966"
    assert payload["summary"][_h.STATUS_GAP] == 2
    assert "raw_payload" not in encoded
    assert "full_payload" not in encoded


def test_write_report_is_limited_to_dropbox_prefix(tmp_path: Path) -> None:
    report_path = (
        tmp_path
        / "independent-progress-assessments"
        / "CODEX-INSIGHT-DROPBOX"
        / "HARNESS-EQUIVALENCE-PHASE-3-SOT-COMPACTNESS-2026-07-06T04-40-00Z.md"
    )

    written = _h.write_report("report\n", report_path, project_root=tmp_path)

    assert written == report_path.resolve()
    assert written.read_text(encoding="utf-8") == "report\n"
    assert not (tmp_path / "bridge").exists()
    assert not (tmp_path / "groundtruth.db").exists()


def test_write_report_rejects_non_dropbox_and_wrong_prefix(tmp_path: Path) -> None:
    bad_dir = tmp_path / "bridge" / "HARNESS-EQUIVALENCE-PHASE-3-SOT-COMPACTNESS-2026.md"
    with pytest.raises(ValueError, match="CODEX-INSIGHT-DROPBOX"):
        _h.write_report("report\n", bad_dir, project_root=tmp_path)

    bad_prefix = tmp_path / "independent-progress-assessments" / "CODEX-INSIGHT-DROPBOX" / "OTHER-2026.md"
    with pytest.raises(ValueError, match="HARNESS-EQUIVALENCE-PHASE-3-SOT-COMPACTNESS-"):
        _h.write_report("report\n", bad_prefix, project_root=tmp_path)
