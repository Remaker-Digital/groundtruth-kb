"""Tests for Wave 2 Slice 8 ``_membase_export.py``.

Per ``bridge/gtkb-isolation-016-phase8-wave2-slice8-005.md`` (REVISED-2)
and ``-006`` (Codex GO with implementation constraints).

Fixture-based per the Slice 4-9 pattern. Tests construct a synthetic
``groundtruth.db`` SQLite file under ``tmp_path``, populate live table
names per the Codex GO requirement, and assert classification, schema
drift detection, relationship parent-tracing, and per-session ownership
signals.
"""

from __future__ import annotations

import json
import sqlite3
import sys
from pathlib import Path
from typing import Any

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "scripts"))

from rehearse import _membase_export  # noqa: E402

# ---- Fixtures ---------------------------------------------------------


# Live KB schemas (subset of columns needed for each test). The full live
# schema has more columns, but only id/version/content-bearing/session_id/
# type-specific are load-bearing for classification.
_VERSIONED_TABLE_SCHEMA = "id TEXT, version INTEGER, title TEXT, description TEXT"
# Per Codex ``-008`` Finding 1: tests classify by ``test_file`` path.
# Fixture schema must include the path columns so ``_classify_test_path``
# is exercised end-to-end.
_TESTS_TABLE_SCHEMA = (
    "id TEXT, version INTEGER, title TEXT, description TEXT, test_file TEXT, test_class TEXT, test_function TEXT"
)
# Per Codex ``-008`` Finding 1: deliberations classify by
# ``origin_project``. Fixture schema includes the origin columns.
_DELIBERATIONS_TABLE_SCHEMA = (
    "id TEXT, version INTEGER, title TEXT, description TEXT, origin_project TEXT, origin_repo TEXT"
)
_RELATIONSHIP_DELIB_SPECS_SCHEMA = "deliberation_id TEXT, spec_id TEXT"
_RELATIONSHIP_DELIB_WIS_SCHEMA = "deliberation_id TEXT, work_item_id TEXT"
_TELEMETRY_SCHEMA = "id INTEGER PRIMARY KEY, payload TEXT"
_PER_SESSION_PROMPTS_SCHEMA = "id INTEGER PRIMARY KEY, session_id TEXT, prompt TEXT"
_PER_SESSION_SNAPSHOTS_SCHEMA = "id TEXT PRIMARY KEY, snapshot TEXT"
_PER_SESSION_QUALITY_SCHEMA = "id INTEGER PRIMARY KEY, session_id TEXT, score REAL"


def _create_minimal_live_schema(kb_path: Path) -> sqlite3.Connection:
    """Create all 21 live-schema tables in the fixture KB.

    Per Codex GO ``-006`` implementation constraint 5: tests must use
    live table names. This fixture creates every table the live
    ``groundtruth.db`` carries so the lane reaches the per-table
    classification path rather than failing on schema drift.
    """
    conn = sqlite3.connect(kb_path)
    cur = conn.cursor()
    # Versioned artifact tables (12). Per Codex ``-008`` Finding 1:
    # ``tests`` and ``deliberations`` get extended schemas matching the
    # live DB columns the type-specific classifier reads.
    cur.execute(f'CREATE TABLE "tests" ({_TESTS_TABLE_SCHEMA})')
    cur.execute(f'CREATE TABLE "deliberations" ({_DELIBERATIONS_TABLE_SCHEMA})')
    for name in (
        "specifications",
        "work_items",
        "documents",
        "operational_procedures",
        "environment_config",
        "backlog_snapshots",
        "test_plans",
        "test_plan_phases",
        "test_procedures",
        "testable_elements",
    ):
        cur.execute(f'CREATE TABLE "{name}" ({_VERSIONED_TABLE_SCHEMA})')
    # Relationship tables (2).
    cur.execute(f'CREATE TABLE "deliberation_specs" ({_RELATIONSHIP_DELIB_SPECS_SCHEMA})')
    cur.execute(f'CREATE TABLE "deliberation_work_items" ({_RELATIONSHIP_DELIB_WIS_SCHEMA})')
    # Excluded telemetry tables (4).
    for name in ("assertion_runs", "pipeline_events", "quality_scores", "test_coverage"):
        cur.execute(f'CREATE TABLE "{name}" ({_TELEMETRY_SCHEMA})')
    # Per-session tables (3).
    cur.execute(f'CREATE TABLE "session_prompts" ({_PER_SESSION_PROMPTS_SCHEMA})')
    cur.execute(f'CREATE TABLE "session_snapshots" ({_PER_SESSION_SNAPSHOTS_SCHEMA})')
    cur.execute(f'CREATE TABLE "spec_quality_scores" ({_PER_SESSION_QUALITY_SCHEMA})')
    conn.commit()
    return conn


def _build_kb(tmp_path: Path) -> Path:
    """Return path to a freshly-created minimal-schema fixture KB."""
    kb_path = tmp_path / "groundtruth.db"
    conn = _create_minimal_live_schema(kb_path)
    conn.close()
    return kb_path


def _run_lane(
    kb_path: Path,
    output_dir: Path,
    manifest: dict[str, Any] | None = None,
) -> dict[str, Any]:
    return _membase_export.run(
        manifest or {"excluded_paths": []},
        output_dir,
        kb_path=kb_path,
    )


def _read_manifest(output_dir: Path) -> dict[str, Any]:
    return json.loads((output_dir / "membase_export" / "membase-partition-manifest.json").read_text(encoding="utf-8"))


# ---- Common contract --------------------------------------------------


def test_run_dry_run_returns_skipped(tmp_path: Path) -> None:
    """Dry-run never reads the KB; returns skipped."""
    result = _membase_export.run(
        {"excluded_paths": []},
        tmp_path / "output",
        dry_run=True,
        kb_path=tmp_path / "nonexistent.db",
    )
    assert result["status"] == "skipped"
    assert result["metrics"] == {"reason": "dry_run"}


def test_run_returns_error_when_kb_path_missing(tmp_path: Path) -> None:
    """Missing KB path → status='error' with kb_path_not_found warning."""
    result = _membase_export.run(
        {"excluded_paths": []},
        tmp_path / "output",
        kb_path=tmp_path / "nonexistent.db",
    )
    assert result["status"] == "error"
    assert any("kb_path_not_found" in w for w in result["warnings"])


# ---- Read-only access (proposal §1) -----------------------------------


def test_run_opens_kb_via_readonly_uri(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """Lane opens the KB with mode=ro URI per proposal §1 read-only access."""
    kb_path = _build_kb(tmp_path)
    captured_uris: list[str] = []
    real_connect = sqlite3.connect

    def _spy_connect(*args: object, **kwargs: object) -> sqlite3.Connection:
        # ``sqlite3.connect`` takes the database URI as its first positional
        # argument and ``uri=True`` as a keyword. Capturing as ``*args`` avoids
        # the keyword-name collision a named ``uri`` parameter would create.
        if args:
            captured_uris.append(str(args[0]))
        return real_connect(*args, **kwargs)

    monkeypatch.setattr(_membase_export.sqlite3, "connect", _spy_connect)
    _run_lane(kb_path, tmp_path / "output")
    assert captured_uris, "expected at least one sqlite3.connect call"
    assert "?mode=ro" in captured_uris[0]


# ---- Schema drift detection (Codex -006 fix 3) ------------------------


def test_run_returns_error_when_known_versioned_table_lacks_id_version(tmp_path: Path) -> None:
    """Per Codex -006 GO + proposal §3 fix 3: known versioned table
    without id+version columns → status='error' with schema_drift warning.
    """
    kb_path = tmp_path / "fixture.db"
    conn = sqlite3.connect(kb_path)
    # Create specifications WITHOUT version column (simulates schema drift).
    conn.execute('CREATE TABLE "specifications" (id TEXT, title TEXT)')
    # All other tables present with proper shape.
    cur = conn.cursor()
    for name in (
        "tests",
        "work_items",
        "documents",
        "operational_procedures",
        "deliberations",
        "environment_config",
        "backlog_snapshots",
        "test_plans",
        "test_plan_phases",
        "test_procedures",
        "testable_elements",
    ):
        cur.execute(f'CREATE TABLE "{name}" ({_VERSIONED_TABLE_SCHEMA})')
    cur.execute(f'CREATE TABLE "deliberation_specs" ({_RELATIONSHIP_DELIB_SPECS_SCHEMA})')
    cur.execute(f'CREATE TABLE "deliberation_work_items" ({_RELATIONSHIP_DELIB_WIS_SCHEMA})')
    for name in ("assertion_runs", "pipeline_events", "quality_scores", "test_coverage"):
        cur.execute(f'CREATE TABLE "{name}" ({_TELEMETRY_SCHEMA})')
    cur.execute(f'CREATE TABLE "session_prompts" ({_PER_SESSION_PROMPTS_SCHEMA})')
    cur.execute(f'CREATE TABLE "session_snapshots" ({_PER_SESSION_SNAPSHOTS_SCHEMA})')
    cur.execute(f'CREATE TABLE "spec_quality_scores" ({_PER_SESSION_QUALITY_SCHEMA})')
    conn.commit()
    conn.close()

    result = _run_lane(kb_path, tmp_path / "output")
    assert result["status"] == "error"
    assert any("schema_drift" in w and "specifications" in w for w in result["warnings"]), (
        f"expected schema_drift warning naming specifications; got {result['warnings']}"
    )


# ---- Unknown-table detection (Codex -006 constraint 1) ----------------


def test_run_returns_error_on_unclassified_table(tmp_path: Path) -> None:
    """Per Codex -006 GO constraint 1: unknown tables must produce
    status='error', NOT silent ok-with-warning. This is the primary
    drift-prevention guard for future schema additions.
    """
    kb_path = _build_kb(tmp_path)
    # Add an unknown table not in any classification set.
    conn = sqlite3.connect(kb_path)
    conn.execute('CREATE TABLE "experimental_feature_flags" (id TEXT, value TEXT)')
    conn.commit()
    conn.close()

    result = _run_lane(kb_path, tmp_path / "output")
    assert result["status"] == "error"
    assert any("unclassified_table" in w and "experimental_feature_flags" in w for w in result["warnings"]), (
        f"expected unclassified_table warning naming experimental_feature_flags; got {result['warnings']}"
    )


# ---- Versioned-table enumeration (proposal §3, §5.2.1) ----------------


def test_run_enumerates_versioned_records_with_versions_array(tmp_path: Path) -> None:
    """One entry per unique id; versions[] contains every version row."""
    kb_path = _build_kb(tmp_path)
    conn = sqlite3.connect(kb_path)
    conn.execute(
        "INSERT INTO specifications (id, version, title, description) VALUES (?, ?, ?, ?)",
        ("SPEC-1834", 1, "OTEL spec v1", "Initial wiring"),
    )
    conn.execute(
        "INSERT INTO specifications (id, version, title, description) VALUES (?, ?, ?, ?)",
        ("SPEC-1834", 2, "OTEL spec v2", "Promoted to verified"),
    )
    conn.execute(
        "INSERT INTO specifications (id, version, title, description) VALUES (?, ?, ?, ?)",
        ("AR-001", 1, "Adopter spec", "Agent Red specific"),
    )
    conn.commit()
    conn.close()

    result = _run_lane(kb_path, tmp_path / "output")
    assert result["status"] == "ok", result["warnings"]
    payload = _read_manifest(tmp_path / "output")
    spec_records = [r for r in payload["versioned_records"] if r["table_name"] == "specifications"]
    by_id = {r["id"]: r for r in spec_records}
    assert by_id["SPEC-1834"]["versions"] == [1, 2]
    assert by_id["SPEC-1834"]["version_count"] == 2
    assert by_id["SPEC-1834"]["max_version"] == 2
    assert by_id["AR-001"]["versions"] == [1]


# ---- Classification by ID prefix --------------------------------------


def test_run_classifies_ar_prefix_as_adopter(tmp_path: Path) -> None:
    kb_path = _build_kb(tmp_path)
    conn = sqlite3.connect(kb_path)
    conn.execute(
        "INSERT INTO specifications (id, version, title, description) VALUES (?, ?, ?, ?)",
        ("AR-DASH-001", 1, "Dashboard scope", "Agent Red specific"),
    )
    conn.commit()
    conn.close()

    _run_lane(kb_path, tmp_path / "output")
    payload = _read_manifest(tmp_path / "output")
    record = next(r for r in payload["versioned_records"] if r["id"] == "AR-DASH-001")
    assert record["classification"] == "adopter"
    assert record["classification_signal"] == "ar_prefix"


def test_run_classifies_gtkb_prefix_as_framework(tmp_path: Path) -> None:
    kb_path = _build_kb(tmp_path)
    conn = sqlite3.connect(kb_path)
    conn.execute(
        "INSERT INTO specifications (id, version, title, description) VALUES (?, ?, ?, ?)",
        ("GTKB-GOV-001", 1, "Governance", "Framework rule"),
    )
    conn.commit()
    conn.close()

    _run_lane(kb_path, tmp_path / "output")
    payload = _read_manifest(tmp_path / "output")
    record = next(r for r in payload["versioned_records"] if r["id"] == "GTKB-GOV-001")
    assert record["classification"] == "framework"
    assert record["classification_signal"] == "gtkb_prefix"


def test_run_classifies_gtkb_with_adopter_content_as_unclassified(tmp_path: Path) -> None:
    """GTKB-* with explicit adopter content → unclassified per Slice 5
    F1 + Slice 6 F2: a conflict signal, not enough to auto-classify.
    """
    kb_path = _build_kb(tmp_path)
    conn = sqlite3.connect(kb_path)
    conn.execute(
        "INSERT INTO work_items (id, version, title, description) VALUES (?, ?, ?, ?)",
        ("GTKB-MIGRATE-AGENT-RED", 1, "Migrate Agent Red", "Agent Red migration plan"),
    )
    conn.commit()
    conn.close()

    _run_lane(kb_path, tmp_path / "output")
    payload = _read_manifest(tmp_path / "output")
    record = next(r for r in payload["versioned_records"] if r["id"] == "GTKB-MIGRATE-AGENT-RED")
    assert record["classification"] == "unclassified"
    assert record["classification_signal"] == "gtkb_prefix_with_adopter_content"


def test_run_classifies_non_prefixed_id_by_content_scan(tmp_path: Path) -> None:
    """SPEC-/DELIB-/WI-/DOC- IDs classify by content marker presence."""
    kb_path = _build_kb(tmp_path)
    conn = sqlite3.connect(kb_path)
    conn.execute(
        "INSERT INTO specifications (id, version, title, description) VALUES (?, ?, ?, ?)",
        ("SPEC-1834", 1, "OTEL spec", "Generic platform telemetry"),
    )
    conn.execute(
        "INSERT INTO specifications (id, version, title, description) VALUES (?, ?, ?, ?)",
        ("SPEC-2098", 1, "Deliberation Archive", "Generic GroundTruth-KB feature"),
    )
    conn.execute(
        "INSERT INTO specifications (id, version, title, description) VALUES (?, ?, ?, ?)",
        ("SPEC-9999", 1, "Agent Red Shopify", "Agent Red shopify integration"),
    )
    conn.commit()
    conn.close()

    _run_lane(kb_path, tmp_path / "output")
    payload = _read_manifest(tmp_path / "output")
    by_id = {r["id"]: r for r in payload["versioned_records"]}
    assert by_id["SPEC-2098"]["classification"] == "framework"
    assert by_id["SPEC-2098"]["classification_signal"] == "groundtruth_kb_reference"
    assert by_id["SPEC-9999"]["classification"] == "adopter"
    assert by_id["SPEC-9999"]["classification_signal"] == "agent_red_product_reference"
    assert by_id["SPEC-1834"]["classification"] == "unclassified"
    assert by_id["SPEC-1834"]["classification_signal"] == "no_classification_signal"


# ---- Type-specific override: tests.test_file path classification -----
# Per Codex `-008` Finding 1 — REVISED-1.


def test_run_classifies_test_path_groundtruth_kb_as_framework(tmp_path: Path) -> None:
    """tests/groundtruth_kb/* → framework via test_file path.

    The description deliberately contains an adopter content marker
    ("agent red") to prove the path classifier wins over content scan.
    """
    kb_path = _build_kb(tmp_path)
    conn = sqlite3.connect(kb_path)
    conn.execute(
        "INSERT INTO tests (id, version, title, description, test_file, test_class, test_function) "
        "VALUES (?, ?, ?, ?, ?, ?, ?)",
        (
            "TEST-FW-001",
            1,
            "Framework test",
            "agent red references in body should not flip classification",
            "tests/groundtruth_kb/test_assertion_runner.py",
            "TestAssertionRunner",
            "test_pass",
        ),
    )
    conn.commit()
    conn.close()

    _run_lane(kb_path, tmp_path / "output")
    payload = _read_manifest(tmp_path / "output")
    record = next(r for r in payload["versioned_records"] if r["id"] == "TEST-FW-001")
    assert record["classification"] == "framework"
    assert record["classification_signal"] == "test_path_framework_groundtruth_kb"


def test_run_classifies_test_path_transport_as_adopter_named(tmp_path: Path) -> None:
    """tests/transport/* → adopter (named in original Slice 8 proposal)."""
    kb_path = _build_kb(tmp_path)
    conn = sqlite3.connect(kb_path)
    conn.execute(
        "INSERT INTO tests (id, version, title, description, test_file) VALUES (?, ?, ?, ?, ?)",
        ("TEST-TRANSPORT", 1, "Transport", "generic", "tests/transport/test_pipeline.py"),
    )
    conn.commit()
    conn.close()

    _run_lane(kb_path, tmp_path / "output")
    payload = _read_manifest(tmp_path / "output")
    record = next(r for r in payload["versioned_records"] if r["id"] == "TEST-TRANSPORT")
    assert record["classification"] == "adopter"
    assert record["classification_signal"] == "test_path_adopter_named"


def test_run_classifies_test_path_admin_scripts_as_adopter_named(tmp_path: Path) -> None:
    """tests/scripts/test_admin_* → adopter (named)."""
    kb_path = _build_kb(tmp_path)
    conn = sqlite3.connect(kb_path)
    conn.execute(
        "INSERT INTO tests (id, version, title, description, test_file) VALUES (?, ?, ?, ?, ?)",
        ("TEST-ADMIN", 1, "Admin", "x", "tests/scripts/test_admin_team_api.py"),
    )
    conn.commit()
    conn.close()

    _run_lane(kb_path, tmp_path / "output")
    payload = _read_manifest(tmp_path / "output")
    record = next(r for r in payload["versioned_records"] if r["id"] == "TEST-ADMIN")
    assert record["classification"] == "adopter"
    assert record["classification_signal"] == "test_path_adopter_named"


def test_run_classifies_test_path_provider_scripts_as_adopter_named(tmp_path: Path) -> None:
    """tests/scripts/test_provider_* → adopter (named)."""
    kb_path = _build_kb(tmp_path)
    conn = sqlite3.connect(kb_path)
    conn.execute(
        "INSERT INTO tests (id, version, title, description, test_file) VALUES (?, ?, ?, ?, ?)",
        ("TEST-PROVIDER", 1, "Provider", "x", "tests/scripts/test_provider_admin.py"),
    )
    conn.commit()
    conn.close()

    _run_lane(kb_path, tmp_path / "output")
    payload = _read_manifest(tmp_path / "output")
    record = next(r for r in payload["versioned_records"] if r["id"] == "TEST-PROVIDER")
    assert record["classification"] == "adopter"
    assert record["classification_signal"] == "test_path_adopter_named"


def test_run_classifies_test_path_release_candidate_gate_as_mixed_scope(tmp_path: Path) -> None:
    """test_release_candidate_gate.py → unclassified mixed_scope_test.

    Mixed-scope check must run BEFORE the adopter-product default;
    otherwise this path (under tests/scripts/) would absorb into the
    adopter bucket.
    """
    kb_path = _build_kb(tmp_path)
    conn = sqlite3.connect(kb_path)
    conn.execute(
        "INSERT INTO tests (id, version, title, description, test_file) VALUES (?, ?, ?, ?, ?)",
        ("TEST-MIXED", 1, "Gate", "x", "tests/scripts/test_release_candidate_gate.py"),
    )
    conn.commit()
    conn.close()

    _run_lane(kb_path, tmp_path / "output")
    payload = _read_manifest(tmp_path / "output")
    record = next(r for r in payload["versioned_records"] if r["id"] == "TEST-MIXED")
    assert record["classification"] == "unclassified"
    assert record["classification_signal"] == "mixed_scope_test"


def test_run_classifies_other_test_path_under_tests_as_adopter_product(tmp_path: Path) -> None:
    """Any tests/<dir>/ path that is not framework or named → adopter (product default).

    Justification: this lane runs against the *adopter* project's KB.
    Framework tests live in the upstream `groundtruth-kb` repo's KB.
    A future framework-side import of test artifacts would still be
    caught: an explicit ``tests/groundtruth_kb/`` prefix overrides this
    default.
    """
    kb_path = _build_kb(tmp_path)
    conn = sqlite3.connect(kb_path)
    paths = [
        "tests/widget/test_admin.py",
        "tests/multi_tenant/test_auth.py",
        "tests/integration/test_e2e.py",
        "tests/unit/test_parser.py",
    ]
    for i, path in enumerate(paths):
        conn.execute(
            "INSERT INTO tests (id, version, title, description, test_file) VALUES (?, ?, ?, ?, ?)",
            (f"TEST-PROD-{i:03d}", 1, "p", "x", path),
        )
    conn.commit()
    conn.close()

    _run_lane(kb_path, tmp_path / "output")
    payload = _read_manifest(tmp_path / "output")
    prod_records = [r for r in payload["versioned_records"] if r["id"].startswith("TEST-PROD-")]
    assert len(prod_records) == 4
    for record in prod_records:
        assert record["classification"] == "adopter"
        assert record["classification_signal"] == "test_path_adopter_product"


def test_run_falls_through_to_id_prefix_when_test_file_null(tmp_path: Path) -> None:
    """tests with NULL test_file fall through to ID-prefix + content scan."""
    kb_path = _build_kb(tmp_path)
    conn = sqlite3.connect(kb_path)
    conn.execute(
        "INSERT INTO tests (id, version, title, description, test_file) VALUES (?, ?, ?, ?, ?)",
        ("AR-TEST-001", 1, "AR-prefixed test", "no path content", None),
    )
    conn.commit()
    conn.close()

    _run_lane(kb_path, tmp_path / "output")
    payload = _read_manifest(tmp_path / "output")
    record = next(r for r in payload["versioned_records"] if r["id"] == "AR-TEST-001")
    assert record["classification"] == "adopter"
    assert record["classification_signal"] == "ar_prefix"


def test_run_falls_through_when_test_file_outside_tests_dir(tmp_path: Path) -> None:
    """tests with test_file outside tests/ dir fall through to content scan."""
    kb_path = _build_kb(tmp_path)
    conn = sqlite3.connect(kb_path)
    conn.execute(
        "INSERT INTO tests (id, version, title, description, test_file) VALUES (?, ?, ?, ?, ?)",
        ("TEST-OUT", 1, "x", "x", "src/some_module.py"),
    )
    conn.commit()
    conn.close()

    _run_lane(kb_path, tmp_path / "output")
    payload = _read_manifest(tmp_path / "output")
    record = next(r for r in payload["versioned_records"] if r["id"] == "TEST-OUT")
    assert record["classification"] == "unclassified"
    assert record["classification_signal"] == "no_classification_signal"


# ---- Type-specific override: deliberations.origin_project -------------
# Per Codex `-008` Finding 1 — REVISED-1.


def test_run_classifies_deliberation_origin_agent_red_as_adopter(tmp_path: Path) -> None:
    """deliberations.origin_project='agent-red' → adopter via type-specific signal.

    Title/description carry NO scope-bearing content; classification
    must come from origin_project alone.
    """
    kb_path = _build_kb(tmp_path)
    conn = sqlite3.connect(kb_path)
    conn.execute(
        "INSERT INTO deliberations (id, version, title, description, origin_project, origin_repo) "
        "VALUES (?, ?, ?, ?, ?, ?)",
        (
            "DELIB-AR-001",
            1,
            "Generic deliberation",
            "Generic content with no scope markers",
            "agent-red",
            "Remaker-Digital/agent-red-customer-engagement",
        ),
    )
    conn.commit()
    conn.close()

    _run_lane(kb_path, tmp_path / "output")
    payload = _read_manifest(tmp_path / "output")
    record = next(r for r in payload["versioned_records"] if r["id"] == "DELIB-AR-001")
    assert record["classification"] == "adopter"
    assert record["classification_signal"] == "deliberation_origin_project_agent_red"


def test_run_classifies_deliberation_origin_groundtruth_kb_as_framework(tmp_path: Path) -> None:
    """deliberations.origin_project='groundtruth-kb' → framework."""
    kb_path = _build_kb(tmp_path)
    conn = sqlite3.connect(kb_path)
    conn.execute(
        "INSERT INTO deliberations (id, version, title, description, origin_project) VALUES (?, ?, ?, ?, ?)",
        ("DELIB-FW-001", 1, "Generic", "Generic", "groundtruth-kb"),
    )
    conn.commit()
    conn.close()

    _run_lane(kb_path, tmp_path / "output")
    payload = _read_manifest(tmp_path / "output")
    record = next(r for r in payload["versioned_records"] if r["id"] == "DELIB-FW-001")
    assert record["classification"] == "framework"
    assert record["classification_signal"] == "deliberation_origin_project_framework"


def test_run_classifies_deliberation_with_null_origin_falls_through_to_content(tmp_path: Path) -> None:
    """deliberations with NULL origin_project fall through to content scan."""
    kb_path = _build_kb(tmp_path)
    conn = sqlite3.connect(kb_path)
    conn.execute(
        "INSERT INTO deliberations (id, version, title, description, origin_project) VALUES (?, ?, ?, ?, ?)",
        ("DELIB-NULL", 1, "Agent Red", "agent red migration discussion", None),
    )
    conn.commit()
    conn.close()

    _run_lane(kb_path, tmp_path / "output")
    payload = _read_manifest(tmp_path / "output")
    record = next(r for r in payload["versioned_records"] if r["id"] == "DELIB-NULL")
    assert record["classification"] == "adopter"
    assert record["classification_signal"] == "agent_red_product_reference"


# ---- Excluded telemetry (Codex -006 constraint 2) ---------------------


def test_run_excludes_pipeline_events_with_documented_reason(tmp_path: Path) -> None:
    """Per Codex -006 constraint 2: each excluded telemetry table emits
    (row_count, reason, cutover_policy) — NOT silent omission.
    """
    kb_path = _build_kb(tmp_path)
    conn = sqlite3.connect(kb_path)
    for i in range(7):
        conn.execute("INSERT INTO pipeline_events (payload) VALUES (?)", (f"event-{i}",))
    conn.commit()
    conn.close()

    _run_lane(kb_path, tmp_path / "output")
    payload = _read_manifest(tmp_path / "output")
    excluded = {e["name"]: e for e in payload["summary"]["excluded_tables"]}
    assert "pipeline_events" in excluded
    assert excluded["pipeline_events"]["row_count"] == 7
    assert excluded["pipeline_events"]["reason"] == "event_log_regenerated_at_new_root"
    assert excluded["pipeline_events"]["cutover_policy"] == "discard_post_migration"


def test_run_excluded_tables_block_includes_all_four_telemetry_tables(tmp_path: Path) -> None:
    """All four telemetry tables present in excluded_tables block."""
    kb_path = _build_kb(tmp_path)
    _run_lane(kb_path, tmp_path / "output")
    payload = _read_manifest(tmp_path / "output")
    excluded_names = {e["name"] for e in payload["summary"]["excluded_tables"]}
    assert excluded_names == {
        "assertion_runs",
        "pipeline_events",
        "quality_scores",
        "test_coverage",
    }


def test_run_excluded_table_row_counts_reflect_actual_data(tmp_path: Path) -> None:
    """row_count in excluded_tables matches the actual row count at
    discovery time. Critical for cutover sizing.
    """
    kb_path = _build_kb(tmp_path)
    conn = sqlite3.connect(kb_path)
    for i in range(3):
        conn.execute("INSERT INTO assertion_runs (payload) VALUES (?)", (f"run-{i}",))
    for i in range(11):
        conn.execute("INSERT INTO test_coverage (payload) VALUES (?)", (f"cov-{i}",))
    conn.commit()
    conn.close()

    _run_lane(kb_path, tmp_path / "output")
    payload = _read_manifest(tmp_path / "output")
    excluded = {e["name"]: e for e in payload["summary"]["excluded_tables"]}
    assert excluded["assertion_runs"]["row_count"] == 3
    assert excluded["test_coverage"]["row_count"] == 11
    assert excluded["pipeline_events"]["row_count"] == 0
    assert excluded["quality_scores"]["row_count"] == 0


# ---- Relationship parent tracing (Codex -006 constraint 3) ------------


def test_run_classifies_relationship_row_by_parent_deliberation(tmp_path: Path) -> None:
    """deliberation_specs row inherits classification from parent deliberation."""
    kb_path = _build_kb(tmp_path)
    conn = sqlite3.connect(kb_path)
    conn.execute(
        "INSERT INTO deliberations (id, version, title, description) VALUES (?, ?, ?, ?)",
        ("DELIB-S313-001", 1, "Wave 2 review", "Agent Red migration deliberation"),
    )
    conn.execute(
        "INSERT INTO deliberation_specs (deliberation_id, spec_id) VALUES (?, ?)",
        ("DELIB-S313-001", "SPEC-1834"),
    )
    conn.commit()
    conn.close()

    _run_lane(kb_path, tmp_path / "output")
    payload = _read_manifest(tmp_path / "output")
    rel_records = [r for r in payload["relationship_records"] if r["table_name"] == "deliberation_specs"]
    assert len(rel_records) == 1
    record = rel_records[0]
    assert record["deliberation_id"] == "DELIB-S313-001"
    assert record["classification"] == "adopter"
    assert record["classification_signal"] == "from_parent_deliberation"
    assert record["classification_inheritance"] == "from_parent_deliberation"
    assert record["parent_classification"] == "adopter"


def test_run_warns_on_orphan_relationship_row(tmp_path: Path) -> None:
    """Per Codex -006 constraint 3: orphan rows surface as warnings."""
    kb_path = _build_kb(tmp_path)
    conn = sqlite3.connect(kb_path)
    # Insert a relationship row whose parent deliberation does NOT exist.
    conn.execute(
        "INSERT INTO deliberation_work_items (deliberation_id, work_item_id) VALUES (?, ?)",
        ("DELIB-MISSING-PARENT", "WI-3168"),
    )
    conn.commit()
    conn.close()

    result = _run_lane(kb_path, tmp_path / "output")
    assert result["status"] == "ok"
    assert any("orphan_relationship_row" in w and "DELIB-MISSING-PARENT" in w for w in result["warnings"]), (
        f"expected orphan_relationship_row warning; got {result['warnings']}"
    )

    payload = _read_manifest(tmp_path / "output")
    record = next(r for r in payload["relationship_records"] if r["deliberation_id"] == "DELIB-MISSING-PARENT")
    assert record["classification"] == "unclassified"
    assert record["classification_signal"] == "orphan_parent_deliberation_missing"


# ---- Per-session classification (Codex -006 constraint 4) -------------


def test_run_classifies_per_session_row_with_s_n_session_id_as_adopter(tmp_path: Path) -> None:
    """S{N} pattern → adopter per CLAUDE.md session convention."""
    kb_path = _build_kb(tmp_path)
    conn = sqlite3.connect(kb_path)
    conn.execute(
        "INSERT INTO session_prompts (session_id, prompt) VALUES (?, ?)",
        ("S313", "session prompt text"),
    )
    conn.commit()
    conn.close()

    _run_lane(kb_path, tmp_path / "output")
    payload = _read_manifest(tmp_path / "output")
    record = next(r for r in payload["per_session_records"] if r["session_id"] == "S313")
    assert record["classification"] == "adopter"
    assert record["classification_signal"] == "session_owned_by_adopter_per_s_n_convention"


def test_run_classifies_per_session_row_with_unrecognized_session_id_as_unclassified(
    tmp_path: Path,
) -> None:
    """Per Codex -006 constraint 4: undeterminable session ownership →
    unclassified, NOT defaulted to adopter.
    """
    kb_path = _build_kb(tmp_path)
    conn = sqlite3.connect(kb_path)
    conn.execute(
        "INSERT INTO session_prompts (session_id, prompt) VALUES (?, ?)",
        ("unknown-format", "prompt"),
    )
    conn.commit()
    conn.close()

    _run_lane(kb_path, tmp_path / "output")
    payload = _read_manifest(tmp_path / "output")
    record = next(r for r in payload["per_session_records"] if r["session_id"] == "unknown-format")
    assert record["classification"] == "unclassified"
    assert "ownership_undetermined" in record["classification_signal"]


def test_run_classifies_per_session_row_with_empty_session_id_as_unclassified(
    tmp_path: Path,
) -> None:
    """Empty session_id → unclassified with empty-id signal."""
    kb_path = _build_kb(tmp_path)
    conn = sqlite3.connect(kb_path)
    conn.execute(
        "INSERT INTO session_prompts (session_id, prompt) VALUES (?, ?)",
        ("", "prompt without session"),
    )
    conn.commit()
    conn.close()

    _run_lane(kb_path, tmp_path / "output")
    payload = _read_manifest(tmp_path / "output")
    record = next(
        r for r in payload["per_session_records"] if r["table_name"] == "session_prompts" and not r["session_id"]
    )
    assert record["classification"] == "unclassified"
    assert "ownership_undetermined" in record["classification_signal"]


# ---- Version preservation evidence (proposal §2.4) --------------------


def test_run_emits_version_preservation_evidence(tmp_path: Path) -> None:
    kb_path = _build_kb(tmp_path)
    conn = sqlite3.connect(kb_path)
    for v in range(1, 5):
        conn.execute(
            "INSERT INTO specifications (id, version, title, description) VALUES (?, ?, ?, ?)",
            ("SPEC-1834", v, f"v{v}", f"version {v}"),
        )
    for v in range(1, 3):
        conn.execute(
            "INSERT INTO work_items (id, version, title, description) VALUES (?, ?, ?, ?)",
            ("WI-3168", v, f"WI v{v}", f"work item version {v}"),
        )
    conn.commit()
    conn.close()

    _run_lane(kb_path, tmp_path / "output")
    payload = _read_manifest(tmp_path / "output")
    evidence = payload["summary"]["version_preservation_evidence"]
    assert "specifications" in evidence["tables_with_versioning_verified"]
    assert "work_items" in evidence["tables_with_versioning_verified"]
    assert evidence["total_unique_artifacts"] == 2
    assert evidence["total_versioned_rows"] == 6
    assert evidence["max_version_count_observed"]["id"] == "SPEC-1834"
    assert evidence["max_version_count_observed"]["table"] == "specifications"
    assert evidence["max_version_count_observed"]["version_count"] == 4


# ---- Output artifacts -------------------------------------------------


def test_run_writes_partition_manifest_json(tmp_path: Path) -> None:
    kb_path = _build_kb(tmp_path)
    _run_lane(kb_path, tmp_path / "output")
    json_path = tmp_path / "output" / "membase_export" / "membase-partition-manifest.json"
    assert json_path.exists()
    payload = json.loads(json_path.read_text(encoding="utf-8"))
    assert payload["schema_version"] == 1
    assert "summary" in payload
    assert "versioned_records" in payload
    assert "relationship_records" in payload
    assert "per_session_records" in payload


def test_run_writes_preview_markdown_with_all_sections(tmp_path: Path) -> None:
    kb_path = _build_kb(tmp_path)
    _run_lane(kb_path, tmp_path / "output")
    md_path = tmp_path / "output" / "membase_export" / "membase-partition-manifest-preview.md"
    assert md_path.exists()
    content = md_path.read_text(encoding="utf-8")
    assert "# MemBase Partition Manifest" in content
    assert "## Summary" in content
    assert "## Excluded Telemetry Tables" in content
    assert "## Version Preservation Evidence" in content


def test_run_writes_result_json_on_ok_path(tmp_path: Path) -> None:
    """Per Wave 2 -003 §4.2 + Slice 4 -006 F2: result.json emitted at lane root."""
    kb_path = _build_kb(tmp_path)
    result = _run_lane(kb_path, tmp_path / "output")
    assert result["status"] == "ok"
    result_path = tmp_path / "output" / "membase_export" / "result.json"
    assert result_path.exists()
    assert str(result_path) in result["output_files"]


def test_run_writes_result_json_on_error_path(tmp_path: Path) -> None:
    """Error path also emits result.json for forensics."""
    result = _membase_export.run(
        {"excluded_paths": []},
        tmp_path / "output",
        kb_path=tmp_path / "nonexistent.db",
    )
    assert result["status"] == "error"
    result_path = tmp_path / "output" / "membase_export" / "result.json"
    assert result_path.exists()


# ---- Summary aggregation ----------------------------------------------


def test_run_summary_aggregates_classifications_by_type(tmp_path: Path) -> None:
    kb_path = _build_kb(tmp_path)
    conn = sqlite3.connect(kb_path)
    conn.execute(
        "INSERT INTO specifications (id, version, title, description) VALUES (?, ?, ?, ?)",
        ("AR-001", 1, "Adopter", "agent red"),
    )
    conn.execute(
        "INSERT INTO specifications (id, version, title, description) VALUES (?, ?, ?, ?)",
        ("GTKB-GOV-001", 1, "Framework", "governance"),
    )
    conn.commit()
    conn.close()

    _run_lane(kb_path, tmp_path / "output")
    payload = _read_manifest(tmp_path / "output")
    summary = payload["summary"]
    assert summary["versioned_by_classification"]["adopter"] == 1
    assert summary["versioned_by_classification"]["framework"] == 1
    assert summary["tables_discovered"] == 21
    assert summary["tables_versioned"] == 12
    assert summary["tables_relationship"] == 2
    assert summary["tables_excluded_telemetry"] == 4
    assert summary["tables_per_session"] == 3
    assert summary["tables_unclassified"] == 0
