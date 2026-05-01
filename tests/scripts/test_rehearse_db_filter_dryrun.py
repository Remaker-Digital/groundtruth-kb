"""Tests for GTKB-ISOLATION-016 Phase 8 Wave 3 db-filter-dryrun lane.

Per bridge/gtkb-isolation-016-phase8-wave3-execution-007.md (REVISED-3,
GO -008) and predecessor -005 (REVISED-2). Covers T1-T17 + T-F1 + T21
+ T22 from the proposal Specification-Derived Verification matrix.
"""

from __future__ import annotations

import json
import sqlite3
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT / "scripts"))
sys.path.insert(0, str(REPO_ROOT / "tools" / "knowledge-db"))

from rehearse import _common, _db_filter_dryrun  # noqa: E402
from rehearse._common import ManifestValidationError, load_manifest  # noqa: E402

# ----- Fixtures -----


@pytest.fixture
def fixture_legacy_db(tmp_path: Path) -> Path:
    """Build a tiny legacy KB with versioned + relationship + telemetry + per-session tables."""
    db_path = tmp_path / "legacy.db"
    conn = sqlite3.connect(str(db_path))
    cur = conn.cursor()
    cur.executescript(
        """
        CREATE TABLE specifications (id TEXT, version INTEGER, title TEXT);
        CREATE TABLE deliberations (id TEXT, version INTEGER, title TEXT);
        CREATE TABLE work_items (id TEXT, version INTEGER, title TEXT);
        CREATE TABLE deliberation_specs (deliberation_id TEXT, spec_id TEXT, role TEXT);
        CREATE TABLE assertion_runs (id INTEGER PRIMARY KEY, payload TEXT);
        CREATE TABLE pipeline_events (id INTEGER PRIMARY KEY, payload TEXT);
        CREATE TABLE quality_scores (id INTEGER PRIMARY KEY, payload TEXT);
        CREATE TABLE test_coverage (id INTEGER PRIMARY KEY, payload TEXT);
        CREATE TABLE session_prompts (session_id TEXT, version INTEGER, prompt_text TEXT);
        """
    )
    cur.executemany(
        "INSERT INTO specifications VALUES (?, ?, ?)",
        [
            ("AR-WIDGET-001", 1, "Adopter widget spec"),
            ("GTKB-PLATFORM-001", 1, "Framework platform spec"),
            ("SPEC-MYSTERY-001", 1, "Unclassified mystery spec"),
        ],
    )
    cur.executemany(
        "INSERT INTO deliberations VALUES (?, ?, ?)",
        [
            ("DELIB-AR-001", 1, "Adopter delib"),
            ("DELIB-GTKB-001", 1, "Framework delib"),
        ],
    )
    cur.executemany(
        "INSERT INTO work_items VALUES (?, ?, ?)",
        [("WI-AR-001", 1, "Adopter WI")],
    )
    cur.executemany(
        "INSERT INTO deliberation_specs VALUES (?, ?, ?)",
        [
            ("DELIB-AR-001", "AR-WIDGET-001", "primary"),  # both adopter -> kept
            ("DELIB-GTKB-001", "GTKB-PLATFORM-001", "primary"),  # both framework -> excluded
            ("DELIB-ORPHAN-001", "SPEC-MISSING-001", "primary"),  # not in partition manifest -> orphan warning
        ],
    )
    cur.executemany("INSERT INTO assertion_runs (payload) VALUES (?)", [("noise",)] * 5)
    cur.executemany("INSERT INTO pipeline_events (payload) VALUES (?)", [("noise",)] * 3)
    cur.executemany(
        "INSERT INTO session_prompts VALUES (?, ?, ?)",
        [("S001", 1, "adopter prompt"), ("S002", 1, "framework prompt")],
    )
    conn.commit()
    conn.close()
    return db_path


@pytest.fixture
def fixture_partition_manifest(tmp_path: Path) -> Path:
    """Build a partition manifest matching the real Slice 8 output schema.

    Per actual ``_membase_export.py`` output: top-level keys are
    ``versioned_records``, ``relationship_records``, ``per_session_records``,
    ``summary`` (containing ``excluded_tables``); each record uses
    ``table_name`` not ``table``. Each relationship row carries its full
    classification per Slice 8's parent-classification inheritance.
    """
    membase_dir = tmp_path / "membase_export"
    membase_dir.mkdir(parents=True)
    manifest_path = membase_dir / "membase-partition-manifest.json"
    manifest = {
        "status": "ok",
        "summary": {
            "tables_discovered": 9,
            "excluded_tables": [
                {"name": "assertion_runs", "row_count": 5, "reason": "x", "cutover_policy": "regenerate_at_new_root"},
                {"name": "pipeline_events", "row_count": 3, "reason": "x", "cutover_policy": "discard_post_migration"},
                {"name": "quality_scores", "row_count": 0, "reason": "x", "cutover_policy": "regenerate_at_new_root"},
                {"name": "test_coverage", "row_count": 0, "reason": "x", "cutover_policy": "regenerate_at_new_root"},
            ],
        },
        "versioned_records": [
            {"table_name": "specifications", "id": "AR-WIDGET-001", "classification": "adopter", "versions": [1]},
            {"table_name": "specifications", "id": "GTKB-PLATFORM-001", "classification": "framework", "versions": [1]},
            {
                "table_name": "specifications",
                "id": "SPEC-MYSTERY-001",
                "classification": "unclassified",
                "versions": [1],
            },
            {"table_name": "deliberations", "id": "DELIB-AR-001", "classification": "adopter", "versions": [1]},
            {"table_name": "deliberations", "id": "DELIB-GTKB-001", "classification": "framework", "versions": [1]},
            {"table_name": "work_items", "id": "WI-AR-001", "classification": "adopter", "versions": [1]},
        ],
        "relationship_records": [
            {
                "table_name": "deliberation_specs",
                "deliberation_id": "DELIB-AR-001",
                "spec_id": "AR-WIDGET-001",
                "classification": "adopter",
            },
            {
                "table_name": "deliberation_specs",
                "deliberation_id": "DELIB-GTKB-001",
                "spec_id": "GTKB-PLATFORM-001",
                "classification": "framework",
            },
        ],
        "per_session_records": [
            {"table_name": "session_prompts", "session_id": "S001", "row_id": None, "classification": "adopter"},
            {"table_name": "session_prompts", "session_id": "S002", "row_id": None, "classification": "framework"},
        ],
    }
    manifest_path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    return manifest_path


@pytest.fixture
def base_manifest_dict() -> dict:
    return {
        "target_root": "E:/GT-KB/applications/Agent_Red",
        "legacy_root": "E:/GT-KB",
        "applications_namespace": "E:/GT-KB/applications",
        "unclassified_disposition": "leave_behind_with_warning",
    }


# ----- T1: framework rows excluded -----


def test_filtered_db_excludes_all_framework_classified_rows(
    tmp_path: Path, fixture_legacy_db: Path, fixture_partition_manifest: Path, base_manifest_dict: dict
) -> None:
    """T1: derives from ADR-ISOLATION-APPLICATION-PLACEMENT-001."""
    output_dir = tmp_path
    result = _db_filter_dryrun.run(base_manifest_dict, output_dir, dry_run=False, kb_path=fixture_legacy_db)
    assert result["status"] == "ok", result
    out_db = output_dir / "db-filter-dryrun" / "groundtruth-filtered-preview.db"
    conn = sqlite3.connect(str(out_db))
    rows = conn.execute("SELECT id FROM specifications").fetchall()
    conn.close()
    ids = {r[0] for r in rows}
    assert "GTKB-PLATFORM-001" not in ids
    assert "AR-WIDGET-001" in ids


# ----- T2: telemetry tables empty -----


def test_filtered_db_telemetry_tables_have_zero_rows(
    tmp_path: Path, fixture_legacy_db: Path, fixture_partition_manifest: Path, base_manifest_dict: dict
) -> None:
    """T2: derives from Slice 8 Constraint 2."""
    result = _db_filter_dryrun.run(base_manifest_dict, tmp_path, dry_run=False, kb_path=fixture_legacy_db)
    assert result["status"] == "ok"
    out_db = tmp_path / "db-filter-dryrun" / "groundtruth-filtered-preview.db"
    conn = sqlite3.connect(str(out_db))
    for table in ("assertion_runs", "pipeline_events", "quality_scores", "test_coverage"):
        count = conn.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]
        assert count == 0, f"{table} should be empty"
    conn.close()


# ----- T3: adopter row count matches partition manifest summary -----


def test_filtered_db_adopter_row_count_matches_partition_manifest_summary(
    tmp_path: Path, fixture_legacy_db: Path, fixture_partition_manifest: Path, base_manifest_dict: dict
) -> None:
    """T3: derives from Slice 8 contract."""
    result = _db_filter_dryrun.run(base_manifest_dict, tmp_path, dry_run=False, kb_path=fixture_legacy_db)
    summary_path = tmp_path / "db-filter-dryrun" / "db-filter-summary.json"
    summary = json.loads(summary_path.read_text(encoding="utf-8"))
    # Adopter rows in fixture: AR-WIDGET-001, DELIB-AR-001, WI-AR-001 (3 versioned)
    # plus 1 per-session adopter row (S001) = 4 total adopter inserts
    assert summary["row_counts"]["adopter_inserted"] == 4, summary["row_counts"]
    assert result["status"] == "ok"


# ----- T4: unclassified rows emit warning under default disposition -----


def test_unclassified_rows_emit_warning_and_are_not_inserted_under_default_disposition(
    tmp_path: Path, fixture_legacy_db: Path, fixture_partition_manifest: Path, base_manifest_dict: dict
) -> None:
    """T4: derives from DELIB-S325-UNCLASSIFIED-DISPOSITION-CHOICE; Slice 8 Constraint 4."""
    _db_filter_dryrun.run(base_manifest_dict, tmp_path, dry_run=False, kb_path=fixture_legacy_db)
    out_db = tmp_path / "db-filter-dryrun" / "groundtruth-filtered-preview.db"
    conn = sqlite3.connect(str(out_db))
    ids = {r[0] for r in conn.execute("SELECT id FROM specifications").fetchall()}
    conn.close()
    assert "SPEC-MYSTERY-001" not in ids, "unclassified rows must NOT be inserted"
    warnings_path = tmp_path / "db-filter-dryrun" / "db-filter-warnings.txt"
    warnings_text = warnings_path.read_text(encoding="utf-8")
    assert "SPEC-MYSTERY-001" in warnings_text, "unclassified row must produce a warning"


# ----- T5: refuses when partition manifest missing -----


def test_lane_refuses_when_partition_manifest_missing_at_canonical_path(
    tmp_path: Path, fixture_legacy_db: Path, base_manifest_dict: dict
) -> None:
    """T5: derives from algorithm step 1; Slice 8 dependency contract; F1 from -002."""
    # No fixture_partition_manifest fixture -> path missing
    result = _db_filter_dryrun.run(base_manifest_dict, tmp_path, dry_run=False, kb_path=fixture_legacy_db)
    assert result["status"] == "error"
    assert any("partition_manifest_missing" in w for w in result["warnings"])


# ----- T6: propagate Slice 8 status=error -----


def test_lane_propagates_partition_manifest_status_error_for_unknown_table(
    tmp_path: Path, fixture_legacy_db: Path, base_manifest_dict: dict
) -> None:
    """T6: derives from Slice 8 Constraint 1."""
    membase_dir = tmp_path / "membase_export"
    membase_dir.mkdir()
    manifest_path = membase_dir / "membase-partition-manifest.json"
    manifest_path.write_text(json.dumps({"status": "error", "warnings": ["unknown_table: foo_bar"]}), encoding="utf-8")
    result = _db_filter_dryrun.run(base_manifest_dict, tmp_path, dry_run=False, kb_path=fixture_legacy_db)
    assert result["status"] == "error"
    assert any("partition_manifest_status_error" in w for w in result["warnings"])


# ----- T7: legacy DB opened read-only -----


def test_legacy_db_is_opened_read_only(
    tmp_path: Path, fixture_legacy_db: Path, fixture_partition_manifest: Path, base_manifest_dict: dict
) -> None:
    """T7: derives from ADR-ISOLATION-APPLICATION-PLACEMENT-001; §3.5 owner decision."""
    _db_filter_dryrun.run(base_manifest_dict, tmp_path, dry_run=False, kb_path=fixture_legacy_db)
    # Verify legacy DB row counts unchanged (read-only proof).
    conn = sqlite3.connect(str(fixture_legacy_db))
    spec_count = conn.execute("SELECT COUNT(*) FROM specifications").fetchone()[0]
    conn.close()
    assert spec_count == 3, "legacy DB row count must be unchanged after lane runs"


# ----- T8: integrity_check passes -----


def test_filtered_db_passes_pragma_integrity_check(
    tmp_path: Path, fixture_legacy_db: Path, fixture_partition_manifest: Path, base_manifest_dict: dict
) -> None:
    """T8: derives from algorithm step 7."""
    result = _db_filter_dryrun.run(base_manifest_dict, tmp_path, dry_run=False, kb_path=fixture_legacy_db)
    assert result["status"] == "ok"
    summary = json.loads((tmp_path / "db-filter-dryrun" / "db-filter-summary.json").read_text(encoding="utf-8"))
    assert summary["integrity_check"] == "ok"


# ----- T9: orphan relationship rows surfaced as warnings -----


def test_orphan_relationship_rows_emit_warning_not_silent_drop(
    tmp_path: Path, fixture_legacy_db: Path, fixture_partition_manifest: Path, base_manifest_dict: dict
) -> None:
    """T9: derives from Slice 8 Constraint 3."""
    _db_filter_dryrun.run(base_manifest_dict, tmp_path, dry_run=False, kb_path=fixture_legacy_db)
    warnings_text = (tmp_path / "db-filter-dryrun" / "db-filter-warnings.txt").read_text(encoding="utf-8")
    # The framework-vs-framework relationship row should be flagged as orphan
    assert "orphan_relationship" in warnings_text


# ----- T10: idempotent re-run -----


def test_lane_is_idempotent_on_re_run(
    tmp_path: Path, fixture_legacy_db: Path, fixture_partition_manifest: Path, base_manifest_dict: dict
) -> None:
    """T10: derives from Slice 3 idempotency contract."""
    r1 = _db_filter_dryrun.run(base_manifest_dict, tmp_path, dry_run=False, kb_path=fixture_legacy_db)
    summary1 = json.loads((tmp_path / "db-filter-dryrun" / "db-filter-summary.json").read_text(encoding="utf-8"))
    r2 = _db_filter_dryrun.run(base_manifest_dict, tmp_path, dry_run=False, kb_path=fixture_legacy_db)
    summary2 = json.loads((tmp_path / "db-filter-dryrun" / "db-filter-summary.json").read_text(encoding="utf-8"))
    assert r1["status"] == r2["status"] == "ok"
    assert summary1["row_counts"] == summary2["row_counts"]


# ----- T11: writes only under output_dir -----


def test_lane_writes_only_under_output_dir_db_filter_dryrun_subdir(
    tmp_path: Path, fixture_legacy_db: Path, fixture_partition_manifest: Path, base_manifest_dict: dict
) -> None:
    """T11: derives from Rule M2 sandbox-output-dir contract; sandbox-output exception amendment."""
    pre_files = {p for p in tmp_path.rglob("*") if p.is_file()}
    _db_filter_dryrun.run(base_manifest_dict, tmp_path, dry_run=False, kb_path=fixture_legacy_db)
    post_files = {p for p in tmp_path.rglob("*") if p.is_file()}
    new_files = post_files - pre_files
    for f in new_files:
        rel = f.relative_to(tmp_path)
        assert rel.parts[0] == "db-filter-dryrun", f"unexpected write outside lane subdir: {rel}"


# ----- T12, T13, T14, T15: load_manifest M6 and M1 backward compat -----


def _write_manifest(tmp_path: Path, **overrides) -> Path:
    base = {
        "target_root": "E:/GT-KB/applications/Agent_Red",
        "legacy_root": "E:/GT-KB",
        "applications_namespace": "E:/GT-KB/applications",
        "output_dir": "C:/temp/agent-red-rehearsal-test",
        "git_strategy": "clone_with_history_filter",
        "git_filter_command_template": (
            "git filter-repo --path <agent-red-paths-from-_path_rewrite> "
            "--path-rename <each-source>:applications/Agent_Red/<each-target>"
        ),
        "phase_1_authority_matrix_path": (
            "independent-progress-assessments/CODEX-INSIGHT-DROPBOX/"
            "GTKB-ISOLATION-001-PHASE1-AUTHORITY-MATRIX-PLAN-2026-04-22.md"
        ),
        "db_reconciliation_strategy": "manifest_driven_filter",
        "unclassified_disposition": "leave_behind_with_warning",
    }
    base.update(overrides)
    lines = []
    for k, v in base.items():
        if isinstance(v, str):
            lines.append(f'{k} = "{v}"')
    lines.append("[surface_treatments]")
    p = tmp_path / "manifest.toml"
    p.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return p


def test_load_manifest_wave_3_rejects_unknown_db_reconciliation_strategy(tmp_path: Path) -> None:
    """T12: derives from Rule M6."""
    p = _write_manifest(tmp_path, db_reconciliation_strategy="invented_strategy")
    with pytest.raises(ManifestValidationError, match="M6"):
        load_manifest(p, wave=3)


def test_load_manifest_wave_3_rejects_unknown_unclassified_disposition(tmp_path: Path) -> None:
    """T13: derives from Rule M6."""
    p = _write_manifest(tmp_path, unclassified_disposition="invented_disposition")
    with pytest.raises(ManifestValidationError, match="M6"):
        load_manifest(p, wave=3)


def test_load_manifest_wave_3_accepts_manifest_driven_filter(tmp_path: Path) -> None:
    """T14: derives from Rule M6 (positive case)."""
    p = _write_manifest(tmp_path)
    data = load_manifest(p, wave=3)
    assert data["db_reconciliation_strategy"] == "manifest_driven_filter"
    assert data["unclassified_disposition"] == "leave_behind_with_warning"


def test_load_manifest_wave_2_still_accepts_owner_decision_required_for_db_reconciliation(
    tmp_path: Path,
) -> None:
    """T15: derives from Rule M1 backward compatibility."""
    p = _write_manifest(tmp_path, db_reconciliation_strategy="OWNER_DECISION_REQUIRED")
    data = load_manifest(p, wave=2)
    assert data["db_reconciliation_strategy"] == "OWNER_DECISION_REQUIRED"


# ----- T16: db-filter-summary.json has required keys -----


def test_db_filter_summary_json_has_required_keys(
    tmp_path: Path, fixture_legacy_db: Path, fixture_partition_manifest: Path, base_manifest_dict: dict
) -> None:
    """T16: derives from Output Layout schema."""
    _db_filter_dryrun.run(base_manifest_dict, tmp_path, dry_run=False, kb_path=fixture_legacy_db)
    summary = json.loads((tmp_path / "db-filter-dryrun" / "db-filter-summary.json").read_text(encoding="utf-8"))
    required = {
        "lane",
        "manifest_input_path",
        "legacy_db_path",
        "output_db_path",
        "unclassified_disposition",
        "row_counts",
        "tables",
        "integrity_check",
        "elapsed_seconds",
    }
    assert required.issubset(summary.keys()), f"missing: {required - set(summary.keys())}"


# ----- T17: NotImplementedError for non-default dispositions -----


def test_lane_raises_NotImplementedError_for_non_default_dispositions(
    tmp_path: Path, fixture_legacy_db: Path, fixture_partition_manifest: Path, base_manifest_dict: dict
) -> None:
    """T17: derives from Implementation Plan explicit scope-deferral."""
    base_manifest_dict["unclassified_disposition"] = "carry_forward_to_adopter"
    with pytest.raises(NotImplementedError):
        _db_filter_dryrun.run(base_manifest_dict, tmp_path, dry_run=False, kb_path=fixture_legacy_db)


# ----- T-F1: lane input path matches Slice 8 output constant -----


def test_lane_input_path_matches_slice8_output_path_constant() -> None:
    """T-F1 (regression for -002 F1): consumer reads where producer writes."""
    from rehearse import _membase_export

    membase_source = Path(_membase_export.__file__).read_text(encoding="utf-8")
    assert 'output_dir / "membase_export"' in membase_source
    assert _db_filter_dryrun._MEMBASE_SUBDIR == "membase_export"


# ----- T21: rule amendment text matches _OUTPUT_DIR_ALLOWLIST_DESC verbatim -----


def test_project_root_boundary_amendment_text_matches_output_dir_allowlist_desc_constant() -> None:
    """T21 (per -005 F1 fix): rule text and source code stay aligned."""
    rule_path = REPO_ROOT / ".claude" / "rules" / "project-root-boundary.md"
    rule_text = rule_path.read_text(encoding="utf-8")
    assert _common._OUTPUT_DIR_ALLOWLIST_DESC in rule_text, (
        "_OUTPUT_DIR_ALLOWLIST_DESC source constant not found verbatim in "
        "project-root-boundary.md; rule text and code have drifted."
    )


# ----- T22: IPR + CVR documents exist and link to ADR -----


def test_ipr_and_cvr_documents_exist_and_link_to_adr_isolation_application_placement_001() -> None:
    """T22 (per -005 F2 fix): GOV-20 Phase 1 advisory pilot compliance.

    Skips with pending marker before each artifact's creation phase:
    - IPR: created at implementation-commit time (this commit).
    - CVR: created at post-implementation-report-commit time.
    """
    try:
        from db import KnowledgeDB
    except ImportError:
        pytest.skip("KnowledgeDB module not importable")

    db = KnowledgeDB(str(REPO_ROOT / "groundtruth.db"))

    ipr = db.get_document("IPR-WAVE3-DB-FILTER-001")
    if ipr is None:
        pytest.skip("IPR not yet created (pre-IPR-insert phase)")
    ipr_tags = ipr.get("tags") or []
    assert "ADR-ISOLATION-APPLICATION-PLACEMENT-001" in ipr_tags, (
        f"IPR-WAVE3-DB-FILTER-001 must link to ADR; tags = {ipr_tags}"
    )

    cvr = db.get_document("CVR-WAVE3-DB-FILTER-001")
    if cvr is None:
        pytest.skip("CVR not yet created (pre-post-impl-commit phase)")
    cvr_tags = cvr.get("tags") or []
    assert "ADR-ISOLATION-APPLICATION-PLACEMENT-001" in cvr_tags, (
        f"CVR-WAVE3-DB-FILTER-001 must link to ADR; tags = {cvr_tags}"
    )
