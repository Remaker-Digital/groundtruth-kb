from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
HELPER = REPO_ROOT / "scripts" / "project_child_wi_checklist.py"


def _load():
    spec = importlib.util.spec_from_file_location("project_child_wi_checklist", HELPER)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


_h = _load()


def _payload(**gap_overrides):
    gap = {
        "gap_id": "WI-4970-G08",
        "title": "Child WI generator checklist",
        "summary": "Create deterministic child work recommendations for harness equivalence gaps.",
        "lifecycle_classification": "new_work",
        "target_paths": ["scripts/project_child_wi_checklist.py"],
        "spec_links": ["GOV-STANDING-BACKLOG-001", "DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001"],
        "evidence_refs": [
            {
                "id": "DELIB-20260705-HIGH-PRIORITY-QUEUE-CONTINUE",
                "summary": "Batch C continuation authority",
            }
        ],
        "acceptance_criteria": ["recommendations include WI, linked test, PAUTH, and bridge slug fields"],
    }
    gap.update(gap_overrides)
    return {
        "project_id": "PROJECT-HARNESS-EQUIVALENCE-PHASE-3",
        "parent_work_item_id": "WI-4970",
        "owner_evidence_refs": ["PAUTH-PROJECT-HARNESS-EQUIVALENCE-PHASE-3-WI4970-BATCH-C-20260705"],
        "gaps": [gap],
    }


def test_build_checklist_emits_child_wi_skeleton() -> None:
    rows = _h.build_checklist(_payload())

    assert len(rows) == 1
    row = rows[0]
    assert row.status == "ready"
    assert row.project_id == "PROJECT-HARNESS-EQUIVALENCE-PHASE-3"
    assert row.parent_work_item_id == "WI-4970"
    assert row.candidate_wi_title.startswith("Create child WI: WI-4970-G08")
    assert "regression test" in row.linked_test_prompt
    assert row.proposal_slug == "gtkb-wi-4970-g08-child-wi-generator-checklist"
    assert row.pauth_need == "required before implementation"
    assert row.target_paths == ("scripts/project_child_wi_checklist.py",)
    assert row.owner_evidence_refs == ("PAUTH-PROJECT-HARNESS-EQUIVALENCE-PHASE-3-WI4970-BATCH-C-20260705",)


@pytest.mark.parametrize(
    ("lifecycle", "expected_pauth"),
    [
        ("new_work", "required before implementation"),
        ("supersession", "required before implementation"),
        ("retirement", "required before implementation"),
        ("waiver", "owner decision required before waiver"),
        ("no_op", "not required for dry-run recommendation"),
    ],
)
def test_lifecycle_classifications_drive_pauth_need(lifecycle: str, expected_pauth: str) -> None:
    rows = _h.build_checklist(_payload(lifecycle_classification=lifecycle))

    assert rows[0].lifecycle_classification == lifecycle
    assert rows[0].pauth_need == expected_pauth


def test_validation_blocks_missing_required_evidence_specs_and_targets() -> None:
    rows = _h.build_checklist(
        _payload(
            target_paths=[],
            spec_links=[],
            evidence_refs=[],
        )
    )

    row = rows[0]
    assert row.status == "blocked"
    issues = {(issue.severity, issue.field) for issue in row.issues}
    assert ("error", "target_paths") in issues
    assert ("error", "spec_links") in issues
    assert ("error", "evidence_refs") in issues


def test_oversized_raw_payload_blocks_and_is_not_rendered() -> None:
    raw_marker = "DO_NOT_RENDER_RAW_SOT_PAYLOAD"
    rows = _h.build_checklist(_payload(raw_payload=raw_marker * 200))

    assert rows[0].status == "blocked"
    assert any(issue.field == "raw_payload" and issue.severity == "error" for issue in rows[0].issues)

    markdown = _h.render_markdown_report(rows, generated_at="2026-07-06T00:00:00Z")
    payload_json = json.dumps(_h.rows_as_json(rows), sort_keys=True)
    assert raw_marker not in markdown
    assert raw_marker not in payload_json
    assert "oversized raw payload supplied" in markdown


def test_markdown_report_includes_summary_table_and_compact_evidence() -> None:
    rows = _h.build_checklist(_payload())
    markdown = _h.render_markdown_report(rows, generated_at="2026-07-06T00:00:00Z")

    assert "# Harness Equivalence Phase 3 Child-WI Checklist" in markdown
    assert "no MemBase mutation, no bridge mutation, and no backlog mutation" in markdown
    assert "| Gap | Lifecycle | Candidate WI | Linked Test Prompt | PAUTH | Proposal Slug | Status |" in markdown
    assert "DELIB-20260705-HIGH-PRIORITY-QUEUE-CONTINUE - Batch C continuation authority" in markdown
    assert "raw_payload" not in markdown


def test_write_report_is_limited_to_dropbox_and_does_not_create_authority_records(tmp_path: Path) -> None:
    report_dir = tmp_path / "independent-progress-assessments" / "CODEX-INSIGHT-DROPBOX"
    report_path = report_dir / "HARNESS-EQUIVALENCE-PHASE-3-CHILD-WI-CHECKLIST-2026-07-06T00-00-00Z.md"

    written = _h.write_report("dry run report\n", report_path, project_root=tmp_path)

    assert written == report_path.resolve()
    assert written.read_text(encoding="utf-8") == "dry run report\n"
    assert not (tmp_path / "bridge").exists()
    assert not (tmp_path / "groundtruth.db").exists()


def test_write_report_rejects_non_dropbox_paths(tmp_path: Path) -> None:
    bad_path = tmp_path / "bridge" / "HARNESS-EQUIVALENCE-PHASE-3-CHILD-WI-CHECKLIST-2026-07-06.md"

    with pytest.raises(ValueError, match="CODEX-INSIGHT-DROPBOX"):
        _h.write_report("dry run report\n", bad_path, project_root=tmp_path)
