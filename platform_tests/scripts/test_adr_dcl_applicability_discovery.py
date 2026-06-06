"""Tests for advisory ADR/DCL applicability discovery.

Linked scope: gtkb-adr-dcl-clause-auto-discovery-slice-5, Slice 5.1.
The discovery helper is advisory-only: it can surface candidate ADR/DCL records,
but it must not change the blocking clause preflight contract.
"""

from __future__ import annotations

import importlib.util
import sqlite3
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
SCRIPT_PATH = REPO_ROOT / "scripts" / "adr_dcl_applicability_discovery.py"
CLAUSE_SCRIPT_PATH = REPO_ROOT / "scripts" / "adr_dcl_clause_preflight.py"
CLAUSES_CONFIG = REPO_ROOT / "config" / "governance" / "adr-dcl-clauses.toml"


def _load_module(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def _write_fixture_db(tmp_path: Path) -> Path:
    db_path = tmp_path / "groundtruth.db"
    conn = sqlite3.connect(db_path)
    conn.execute(
        """
        CREATE TABLE current_specifications (
            id TEXT,
            title TEXT,
            description TEXT,
            type TEXT,
            status TEXT,
            scope TEXT,
            section TEXT,
            handle TEXT,
            tags TEXT,
            assertions TEXT,
            source_paths TEXT
        )
        """
    )
    rows = [
        (
            "DCL-HARNESS-STATE-SOT-ASSERTION-001",
            "Harness state source-of-truth assertions",
            "Harness registry role assignment readers must flow through the canonical projection.",
            "design_constraint",
            "verified",
            "harness-state role assignment registry",
            "governance",
            "harness state",
            "harness,registry,role",
            "No direct role assignment reads outside canonical entrypoint.",
            "scripts/harness_roles.py groundtruth-kb/src/groundtruth_kb/harness_projection.py",
        ),
        (
            "ADR-BILLING-EXPORT-001",
            "Billing export format",
            "Invoices are exported as monthly CSV files.",
            "architecture_decision",
            "verified",
            "billing",
            "exports",
            "billing",
            "billing,csv",
            "CSV export remains stable.",
            "applications/Billing/export.py",
        ),
        (
            "ADR-ISOLATION-APPLICATION-PLACEMENT-001",
            "Application placement",
            "All active GT-KB files remain under the project root.",
            "architecture_decision",
            "verified",
            "project root",
            "placement",
            "root boundary",
            "root,boundary",
            "Files remain under E:/GT-KB.",
            ".claude/rules/project-root-boundary.md",
        ),
    ]
    conn.executemany("INSERT INTO current_specifications VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", rows)
    conn.commit()
    conn.close()
    return db_path


def _bridge_content() -> str:
    return (
        "NEW\n\n"
        "# Harness registry proposal\n\n"
        'target_paths: ["scripts/harness_roles.py", "groundtruth-kb/src/groundtruth_kb/harness_projection.py"]\n\n'
        "## Specification Links\n\n"
        "- DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001\n\n"
        "This change updates harness registry role assignment projection behavior.\n"
    )


def test_known_applicable_record_surfaced(tmp_path):
    discovery = _load_module(SCRIPT_PATH, "adr_dcl_applicability_discovery_known")
    content = tmp_path / "candidate.md"
    content.write_text(_bridge_content(), encoding="utf-8")
    payload = discovery.build_payload(
        bridge_id="fixture",
        content_file=content,
        db_path=_write_fixture_db(tmp_path),
        clauses_config=CLAUSES_CONFIG,
    )
    candidates = {row["spec_id"]: row for row in payload["results"] if row["classification"] == "candidate_may_apply"}
    assert "DCL-HARNESS-STATE-SOT-ASSERTION-001" in candidates
    assert candidates["DCL-HARNESS-STATE-SOT-ASSERTION-001"]["score"] >= discovery.DEFAULT_THRESHOLD


def test_output_is_deterministic_for_fixed_input(tmp_path):
    discovery = _load_module(SCRIPT_PATH, "adr_dcl_applicability_discovery_deterministic")
    content = tmp_path / "candidate.md"
    content.write_text(_bridge_content(), encoding="utf-8")
    db_path = _write_fixture_db(tmp_path)
    first = discovery.build_payload(
        bridge_id="fixture",
        content_file=content,
        db_path=db_path,
        clauses_config=CLAUSES_CONFIG,
    )["markdown"]
    second = discovery.build_payload(
        bridge_id="fixture",
        content_file=content,
        db_path=db_path,
        clauses_config=CLAUSES_CONFIG,
    )["markdown"]
    assert first == second


def test_non_overlapping_record_not_flagged(tmp_path):
    discovery = _load_module(SCRIPT_PATH, "adr_dcl_applicability_discovery_negative")
    content = tmp_path / "candidate.md"
    content.write_text(_bridge_content(), encoding="utf-8")
    payload = discovery.build_payload(
        bridge_id="fixture",
        content_file=content,
        db_path=_write_fixture_db(tmp_path),
        clauses_config=CLAUSES_CONFIG,
    )
    by_id = {row["spec_id"]: row for row in payload["results"]}
    assert by_id["ADR-BILLING-EXPORT-001"]["classification"] == "not_applicable"


def test_registered_clause_record_is_declared_not_heuristic(tmp_path):
    discovery = _load_module(SCRIPT_PATH, "adr_dcl_applicability_discovery_declared")
    content = tmp_path / "candidate.md"
    content.write_text('target_paths: ["bridge/example-001.md"]\nproject root E:/GT-KB\n', encoding="utf-8")
    payload = discovery.build_payload(
        bridge_id="fixture",
        content_file=content,
        db_path=_write_fixture_db(tmp_path),
        clauses_config=CLAUSES_CONFIG,
    )
    by_id = {row["spec_id"]: row for row in payload["results"]}
    assert by_id["ADR-ISOLATION-APPLICATION-PLACEMENT-001"]["classification"] == "declared"
    assert by_id["ADR-ISOLATION-APPLICATION-PLACEMENT-001"]["score"] == 0


def test_discovery_main_always_exits_zero_with_high_overlap(tmp_path):
    discovery = _load_module(SCRIPT_PATH, "adr_dcl_applicability_discovery_exit")
    content = tmp_path / "candidate.md"
    content.write_text(_bridge_content(), encoding="utf-8")
    out = tmp_path / "out.md"
    rc = discovery.main(
        [
            "--bridge-id",
            "fixture",
            "--content-file",
            str(content),
            "--db",
            str(_write_fixture_db(tmp_path)),
            "--clauses-config",
            str(CLAUSES_CONFIG),
            "--out",
            str(out),
        ]
    )
    assert rc == 0
    assert "Candidate Applicable ADR/DCLs" in out.read_text(encoding="utf-8")


def test_existing_clause_preflight_unchanged():
    clause_preflight = _load_module(CLAUSE_SCRIPT_PATH, "adr_dcl_clause_preflight_unchanged")
    clauses = clause_preflight.load_clauses(CLAUSES_CONFIG)
    assert len(clauses) == 5
    assert {clause.enforcement_mode for clause in clauses} == {"blocking"}
