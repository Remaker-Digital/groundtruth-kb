# © 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""Tests for groundtruth_kb.project.doctor_isolation — GTKB-ISOLATION-017 Slice 1.

Each test maps to a Phase 9 specification clause. See
``bridge/gtkb-isolation-017-slice1-doctor-checks-007.md`` (REVISED-3, GO -008)
for the spec-to-test mapping.
"""

from __future__ import annotations

import json
import sqlite3
from pathlib import Path

import pytest

from groundtruth_kb.project.doctor import (
    DoctorReport,
    ToolCheck,
    format_doctor_report_json,
)
from groundtruth_kb.project.doctor_isolation import (
    _PRODUCT_SCOPE_OWNERSHIP_LABELS,
    _check_isolation_adopter_root_not_under_product_root,
    _check_isolation_chroma_regeneratable,
    _check_isolation_durable_work_subject_application,
    _check_isolation_hooks_point_to_wrappers,
    _check_isolation_no_writable_product_paths,
    _check_isolation_release_readiness_app_subject_header,
    _check_isolation_service_endpoint_not_raw_db,
    _check_isolation_work_list_no_product_entries,
    _check_isolation_workstream_focus_hook_absent,
    run_isolation_checks,
)

# ---------------------------------------------------------------------------
# T1, T2: adopter-root-not-under-product-root (Phase 9 §4 check 1)
# ---------------------------------------------------------------------------


def test_check_isolation_adopter_root_not_under_product_root_fails_when_under(tmp_path: Path) -> None:
    """T1: Phase 9 §4 check 1; ADR-ISOLATION-APPLICATION-PLACEMENT-001."""
    product_root = tmp_path / "gt-kb"
    adopter = product_root / "applications" / "agent_red"
    adopter.mkdir(parents=True)
    result = _check_isolation_adopter_root_not_under_product_root(adopter, product_root)
    assert result.status == "fail"
    assert "under product root" in result.message


def test_check_isolation_adopter_root_not_under_product_root_passes_when_outside(tmp_path: Path) -> None:
    """T2: Phase 9 §4 check 1; sibling directories pass."""
    product_root = tmp_path / "gt-kb"
    adopter = tmp_path / "agent_red"
    product_root.mkdir()
    adopter.mkdir()
    result = _check_isolation_adopter_root_not_under_product_root(adopter, product_root)
    assert result.status == "pass"


# ---------------------------------------------------------------------------
# T3, T4: service-endpoint-not-raw-db (Phase 9 §4 check 2)
# ---------------------------------------------------------------------------


def test_check_isolation_service_endpoint_fails_on_raw_db_path(tmp_path: Path) -> None:
    """T3: Phase 9 §4 check 2 - raw .db endpoint flagged."""
    toml = tmp_path / "groundtruth.toml"
    toml.write_text('[service]\nendpoint = "groundtruth.db"\n', encoding="utf-8")
    result = _check_isolation_service_endpoint_not_raw_db(tmp_path)
    assert result.status == "fail"
    assert "raw DB path" in result.message


def test_check_isolation_service_endpoint_passes_on_scoped_service_url(tmp_path: Path) -> None:
    """T4: Phase 9 §4 check 2 - scoped service URL passes."""
    toml = tmp_path / "groundtruth.toml"
    toml.write_text('[service]\nendpoint = "http://localhost:8090/agent-red"\n', encoding="utf-8")
    result = _check_isolation_service_endpoint_not_raw_db(tmp_path)
    assert result.status == "pass"


# ---------------------------------------------------------------------------
# T5, T6, T-DEF, T-COMPAT: durable-work-subject (Phase 9 §4 check 3 + Phase 7)
# ---------------------------------------------------------------------------


def test_check_isolation_durable_work_subject_passes_on_phase7_canonical_application(tmp_path: Path) -> None:
    """T5: Phase 7 Durable State Contract; canonical surface = application."""
    state_dir = tmp_path / ".claude" / "session"
    state_dir.mkdir(parents=True)
    (state_dir / "work-subject.json").write_text(
        json.dumps({"schema_version": 1, "current_subject": "application", "application_root": str(tmp_path)}),
        encoding="utf-8",
    )
    result = _check_isolation_durable_work_subject_application(tmp_path)
    assert result.status == "pass"


def test_check_isolation_durable_work_subject_warns_on_phase7_canonical_gtkb_subject(tmp_path: Path) -> None:
    """T6: Phase 7 lines 162-164; non-application subject triggers warning."""
    state_dir = tmp_path / ".claude" / "session"
    state_dir.mkdir(parents=True)
    (state_dir / "work-subject.json").write_text(
        json.dumps({"schema_version": 1, "current_subject": "gt-kb"}),
        encoding="utf-8",
    )
    result = _check_isolation_durable_work_subject_application(tmp_path)
    assert result.status == "warning"
    assert "expected application" in result.message


def test_check_isolation_durable_work_subject_info_when_canonical_absent(tmp_path: Path) -> None:
    """T-DEF: Phase 7 line 161 - missing file → info / default to application."""
    result = _check_isolation_durable_work_subject_application(tmp_path)
    assert result.status == "info"
    assert "absent" in result.message


def test_check_isolation_durable_work_subject_reads_legacy_workstream_focus_state_json(tmp_path: Path) -> None:
    """T-COMPAT: Phase 7 line 154 - legacy migration window."""
    legacy_dir = tmp_path / ".claude" / "hooks"
    legacy_dir.mkdir(parents=True)
    (legacy_dir / ".workstream-focus-state.json").write_text(
        json.dumps({"current_subject": "application"}),
        encoding="utf-8",
    )
    result = _check_isolation_durable_work_subject_application(tmp_path)
    assert result.status == "pass"


# ---------------------------------------------------------------------------
# T7, T-OWN: no-writable-product-paths (Phase 9 §4 check 4)
# ---------------------------------------------------------------------------


def test_check_isolation_no_writable_product_paths_includes_gt_kb_managed_excludes_gt_kb_scaffolded() -> None:
    """T-OWN per Codex `-006` F1 fix.

    Asserts:
      1. At least one ``gt-kb-managed`` record exists in the registry.
      2. ``adopter-groundtruth-toml`` (a ``gt-kb-scaffolded`` row per
         templates/scaffold-ownership.toml lines 23-31) is NOT in the
         write-probe set — adopters edit it freely per the authority matrix.
    """
    from groundtruth_kb.project.ownership import OwnershipResolver

    resolver = OwnershipResolver()
    managed = [r for r in resolver.all_records() if r.ownership == "gt-kb-managed"]
    assert managed, (
        "registry must contain at least one gt-kb-managed record; "
        "if this fails, the registry has no product-scope coverage"
    )

    scaffolded_toml = next(
        (r for r in resolver.all_records() if r.id == "adopter-groundtruth-toml"),
        None,
    )
    assert scaffolded_toml is not None, "adopter-groundtruth-toml must exist in registry"
    assert scaffolded_toml.ownership == "gt-kb-scaffolded", (
        "adopter-groundtruth-toml ownership label drift; expected gt-kb-scaffolded"
    )
    assert scaffolded_toml.ownership not in _PRODUCT_SCOPE_OWNERSHIP_LABELS, (
        "gt-kb-scaffolded must NOT be in the non-writable product-scope set per "
        "authority matrix line 113 + scaffold-ownership.toml note 'adopter edits freely'"
    )


def test_check_isolation_no_writable_product_paths_fails_when_writable(tmp_path: Path) -> None:
    """T7: Phase 9 §4 check 4 - any writable product-scope path fails the check.

    Materializes one product-scope file (a managed hook target) under the
    adopter root; the directory containing it is writable, so the touch-probe
    succeeds → check returns fail.
    """
    from groundtruth_kb.project.ownership import OwnershipResolver

    resolver = OwnershipResolver()
    managed = [
        r
        for r in resolver.all_records()
        if r.ownership == "gt-kb-managed" and r.source_class == "file" and r.source is not None
    ]
    assert managed, "registry must contain at least one gt-kb-managed FILE-class record"

    # Pick the first managed hook record; create the file at its relative target_path.
    record = managed[0]
    rel = getattr(record.source, "target_path", None)
    assert rel, "FILE-class record must expose target_path on its ManagedArtifact source"
    target_file = tmp_path / rel
    target_file.parent.mkdir(parents=True, exist_ok=True)
    target_file.write_text("# placeholder\n", encoding="utf-8")

    result = _check_isolation_no_writable_product_paths(tmp_path, "dual-agent")
    # The directory holding the managed file is writable in tmp_path → fail.
    assert result.status == "fail"


# ---------------------------------------------------------------------------
# T8: hooks-point-to-wrappers (Phase 9 §4 check 5)
# ---------------------------------------------------------------------------


def test_check_isolation_hooks_point_to_wrappers_warns_on_embedded_logic(tmp_path: Path) -> None:
    """T8: Phase 9 §4 check 5 - non-wrapper hook commands warn."""
    settings_dir = tmp_path / ".claude"
    settings_dir.mkdir()
    settings = {
        "hooks": {
            "PreToolUse": [
                {
                    "hooks": [
                        {"type": "command", "command": "echo 'embedded logic right in settings.json'"},
                    ],
                },
            ],
        },
    }
    (settings_dir / "settings.json").write_text(json.dumps(settings), encoding="utf-8")
    result = _check_isolation_hooks_point_to_wrappers(tmp_path, "dual-agent")
    assert result.status == "warning"


# ---------------------------------------------------------------------------
# T9, T10: workstream-focus-hook-absent (Phase 9 §4 check 6 + line 410)
# ---------------------------------------------------------------------------


def test_check_isolation_workstream_focus_hook_absent_warns_when_present(tmp_path: Path) -> None:
    """T9 per F2 fix: Phase 9 line 410 says 'warns', not 'fails'."""
    legacy_hook = tmp_path / ".claude" / "hooks" / "workstream-focus.py"
    legacy_hook.parent.mkdir(parents=True)
    legacy_hook.write_text("# legacy", encoding="utf-8")
    result = _check_isolation_workstream_focus_hook_absent(tmp_path)
    assert result.status == "warning"
    assert "workstream-focus.py" in result.message


def test_check_isolation_workstream_focus_hook_absent_passes_when_absent(tmp_path: Path) -> None:
    """T10: Phase 9 §4 check 6 - absent legacy hook passes."""
    result = _check_isolation_workstream_focus_hook_absent(tmp_path)
    assert result.status == "pass"


# ---------------------------------------------------------------------------
# T11: work-list-no-product-entries (Phase 9 §4 check 7)
# ---------------------------------------------------------------------------


def test_check_isolation_work_list_no_product_entries_warns_on_product_id(tmp_path: Path) -> None:
    """T11: Phase 9 §4 check 7 - product-scope IDs in work_list.md trigger warning."""
    memory_dir = tmp_path / "memory"
    memory_dir.mkdir()
    (memory_dir / "work_list.md").write_text(
        "# Work list\n- GTKB-ISOLATION-017: Slice 1 doctor checks\n",
        encoding="utf-8",
    )
    result = _check_isolation_work_list_no_product_entries(tmp_path)
    assert result.status == "warning"
    assert "product-scope-heuristic" in result.message


# ---------------------------------------------------------------------------
# T12: release-readiness-app-subject-header (Phase 9 §4 check 8)
# ---------------------------------------------------------------------------


def test_check_isolation_release_readiness_app_subject_header_warns_on_combined_claim(tmp_path: Path) -> None:
    """T12: Phase 9 §4 check 8 - combined GT-KB + green-keyword line warns."""
    memory_dir = tmp_path / "memory"
    memory_dir.mkdir()
    (memory_dir / "release-readiness.md").write_text(
        "# Application Release Readiness\n\nGT-KB and Agent Red are both ready for prod.\n",
        encoding="utf-8",
    )
    result = _check_isolation_release_readiness_app_subject_header(tmp_path)
    assert result.status == "warning"


# ---------------------------------------------------------------------------
# T13: chroma-regeneratable (Phase 9 §4 check 9)
# ---------------------------------------------------------------------------


def test_check_isolation_chroma_regeneratable_warns_on_orphan_cache(tmp_path: Path) -> None:
    """T13: Phase 9 §4 check 9 - chroma cache without backing DB warns."""
    chroma = tmp_path / ".groundtruth-chroma"
    chroma.mkdir()
    (chroma / "marker").write_text("placeholder", encoding="utf-8")
    # No groundtruth.db at all → orphan.
    result = _check_isolation_chroma_regeneratable(tmp_path)
    assert result.status == "warning"
    assert "orphan" in result.message


# ---------------------------------------------------------------------------
# T14: preflight ordering (Phase 9 §4 line 224-226)
# ---------------------------------------------------------------------------


def test_run_isolation_checks_returns_checks_in_preflight_order(tmp_path: Path) -> None:
    """T14: environment boundary → service → subject → registry → app-local."""
    product_root = tmp_path / "gt-kb"
    product_root.mkdir()
    adopter = tmp_path / "agent_red"
    adopter.mkdir()
    checks = run_isolation_checks(adopter, "dual-agent", product_root=product_root)
    names = [c.name for c in checks]
    assert names == [
        "isolation:adopter-root-placement",
        "isolation:service-endpoint",
        "isolation:work-subject",
        "isolation:no-writable-product-paths",
        "isolation:hooks-point-to-wrappers",
        "isolation:workstream-focus-hook-absent",
        "isolation:work-list-no-product-entries",
        "isolation:release-readiness-app-subject-header",
        "isolation:chroma-regeneratable",
    ]


# ---------------------------------------------------------------------------
# T15: severity-model info-status (Phase 9 §4 lines 221-223)
# ---------------------------------------------------------------------------


def test_severity_model_info_does_not_affect_overall() -> None:
    """T15: info-status checks are informational only."""
    checks = [
        ToolCheck(name="x", required=True, found=False, status="info", message="info-only"),
        ToolCheck(name="y", required=True, found=True, status="pass", message="ok"),
    ]
    report = DoctorReport(checks=checks, profile="dual-agent")
    assert report.overall == "pass"


# ---------------------------------------------------------------------------
# T16: JSON output schema (Phase 9 §4 lines 226-228)
# ---------------------------------------------------------------------------


def test_format_doctor_report_json_schema_v1() -> None:
    """T16: machine-readable JSON shape feeds the dashboard."""
    checks = [
        ToolCheck(
            name="x",
            required=True,
            found=True,
            version="1.0",
            min_version="0.5",
            status="pass",
            message="ok",
        ),
    ]
    report = DoctorReport(checks=checks, profile="dual-agent")
    j = format_doctor_report_json(report)
    assert j["schema_version"] == "1"
    assert j["profile"] == "dual-agent"
    assert j["overall"] == "pass"
    assert j["checks"][0]["name"] == "x"
    assert j["checks"][0]["status"] == "pass"
    assert j["checks"][0]["version"] == "1.0"
    assert j["checks"][0]["min_version"] == "0.5"


# ---------------------------------------------------------------------------
# T-PROD: required product_root kwarg (F2 fix)
# ---------------------------------------------------------------------------


def test_run_isolation_checks_requires_product_root_kwarg(tmp_path: Path) -> None:
    """T-PROD per F2 fix: no silent fallback when product_root is omitted."""
    with pytest.raises(TypeError):
        run_isolation_checks(tmp_path, "dual-agent")  # type: ignore[call-arg]


# ---------------------------------------------------------------------------
# T-DET: determinism (Phase 9 lines 404-405)
# ---------------------------------------------------------------------------


def test_repeated_runs_produce_identical_output(tmp_path: Path) -> None:
    """T-DET: doctor output is deterministic for identical inputs."""
    product_root = tmp_path / "gt-kb"
    product_root.mkdir()
    adopter = tmp_path / "agent_red"
    adopter.mkdir()
    a = run_isolation_checks(adopter, "dual-agent", product_root=product_root)
    b = run_isolation_checks(adopter, "dual-agent", product_root=product_root)
    assert [(c.name, c.status, c.message) for c in a] == [(c.name, c.status, c.message) for c in b]


# ---------------------------------------------------------------------------
# T-IPR-CVR: GOV-20 Phase 1 advisory pilot artifacts exist with ADR tag.
# ---------------------------------------------------------------------------


def _kb_path() -> Path:
    here = Path(__file__).resolve()
    # tests/test_doctor_isolation.py → groundtruth-kb/ → E:/GT-KB
    return here.parents[2] / "groundtruth.db"


def test_ipr_and_cvr_slice1_documents_exist_with_adr_tag() -> None:
    """T-IPR-CVR: GOV-20 Phase 1 advisory pilot - IPR + CVR docs in KB.

    Skips when ``groundtruth.db`` is unavailable (CI / out-of-tree builds).
    """
    db_path = _kb_path()
    if not db_path.exists():
        pytest.skip(f"groundtruth.db not available at {db_path}")
    conn = sqlite3.connect(str(db_path))
    try:
        conn.row_factory = sqlite3.Row
        rows = conn.execute(
            "SELECT id, category, tags FROM documents WHERE id IN (?, ?)",
            ("IPR-SLICE1-DOCTOR-CHECKS-001", "CVR-SLICE1-DOCTOR-CHECKS-001"),
        ).fetchall()
    finally:
        conn.close()

    found_ids = {r["id"] for r in rows}
    assert "IPR-SLICE1-DOCTOR-CHECKS-001" in found_ids, "IPR-SLICE1 missing from KB"
    assert "CVR-SLICE1-DOCTOR-CHECKS-001" in found_ids, "CVR-SLICE1 missing from KB"

    for r in rows:
        tags = (r["tags"] or "").lower()
        assert "adr-isolation-application-placement-001" in tags, f"{r['id']} missing ADR tag; got tags={r['tags']!r}"
