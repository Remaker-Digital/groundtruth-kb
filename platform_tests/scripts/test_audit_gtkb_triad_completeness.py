"""Tests for the GT-KB triad-completeness audit."""

from __future__ import annotations

import json
import sqlite3
from pathlib import Path

from scripts.audit_gtkb_triad_completeness import run_audit


def _init_db(path: Path) -> None:
    conn = sqlite3.connect(path)
    conn.executescript(
        """
        CREATE TABLE specifications (
            rowid INTEGER PRIMARY KEY,
            id TEXT NOT NULL,
            version INTEGER NOT NULL,
            title TEXT NOT NULL,
            description TEXT,
            priority TEXT,
            scope TEXT,
            section TEXT,
            handle TEXT,
            tags TEXT,
            status TEXT NOT NULL,
            assertions TEXT,
            changed_by TEXT NOT NULL,
            changed_at TEXT NOT NULL,
            change_reason TEXT NOT NULL,
            type TEXT,
            authority TEXT,
            provisional_until TEXT,
            constraints TEXT,
            affected_by TEXT,
            testability TEXT,
            source_paths TEXT
        );
        CREATE TABLE tests (
            rowid INTEGER PRIMARY KEY,
            id TEXT NOT NULL,
            version INTEGER NOT NULL,
            title TEXT NOT NULL,
            spec_id TEXT NOT NULL,
            test_type TEXT NOT NULL,
            test_file TEXT,
            test_class TEXT,
            test_function TEXT,
            description TEXT,
            expected_outcome TEXT NOT NULL,
            last_result TEXT,
            last_executed_at TEXT,
            changed_by TEXT NOT NULL,
            changed_at TEXT NOT NULL,
            change_reason TEXT NOT NULL
        );
        CREATE TABLE test_coverage (
            rowid INTEGER PRIMARY KEY,
            spec_id TEXT NOT NULL,
            test_file TEXT NOT NULL,
            test_class TEXT,
            test_function TEXT NOT NULL,
            confidence TEXT NOT NULL,
            match_reason TEXT,
            created_at TEXT NOT NULL,
            created_by TEXT NOT NULL
        );
        CREATE TABLE current_deliberations (
            rowid INTEGER PRIMARY KEY,
            id TEXT,
            version INTEGER,
            spec_id TEXT,
            work_item_id TEXT,
            source_type TEXT,
            source_ref TEXT,
            title TEXT,
            summary TEXT,
            content TEXT,
            content_hash TEXT,
            participants TEXT,
            outcome TEXT,
            session_id TEXT,
            sensitivity TEXT,
            redaction_state TEXT,
            redaction_notes TEXT,
            origin_project TEXT,
            origin_repo TEXT,
            changed_by TEXT,
            changed_at TEXT,
            change_reason TEXT
        );
        """
    )
    conn.commit()
    conn.close()


def _insert_spec(
    db_path: Path,
    spec_id: str,
    *,
    status: str = "implemented",
    title: str = "Spec",
    assertions: list[dict] | None = None,
    source_paths: list[str] | None = None,
    description: str = "",
) -> None:
    conn = sqlite3.connect(db_path)
    conn.execute(
        """
        INSERT INTO specifications (
            id, version, title, description, status, assertions, changed_by,
            changed_at, change_reason, type, source_paths
        )
        VALUES (?, 1, ?, ?, ?, ?, 'test', '2026-04-29T00:00:00Z', 'test', 'requirement', ?)
        """,
        (
            spec_id,
            title,
            description,
            status,
            json.dumps(assertions) if assertions is not None else None,
            json.dumps(source_paths) if source_paths is not None else None,
        ),
    )
    conn.commit()
    conn.close()


def _insert_owner_deliberation(db_path: Path, spec_id: str) -> None:
    conn = sqlite3.connect(db_path)
    conn.execute(
        """
        INSERT INTO current_deliberations (
            id, version, spec_id, source_type, source_ref, title, summary,
            content, outcome, changed_by, changed_at, change_reason
        )
        VALUES (?, 1, ?, 'owner_conversation', 'owner_conversation:test',
            'Owner directive', 'Owner directive summary', 'Owner directive content',
            'owner_decision', 'test', '2026-04-29T00:00:00Z', 'test')
        """,
        (f"DELIB-{spec_id}", spec_id),
    )
    conn.commit()
    conn.close()


def _insert_test(db_path: Path, spec_id: str, *, last_result: str | None = "pass") -> None:
    conn = sqlite3.connect(db_path)
    conn.execute(
        """
        INSERT INTO tests (
            id, version, title, spec_id, test_type, test_file, test_function,
            expected_outcome, last_result, last_executed_at, changed_by,
            changed_at, change_reason
        )
        VALUES (?, 1, 'Test', ?, 'unit', 'tests/scripts/test_audit_gtkb_triad_completeness.py',
            'test_fixture', 'pass', ?, '2026-04-29T00:00:00Z', 'test',
            '2026-04-29T00:00:00Z', 'test')
        """,
        (f"TEST-{spec_id}", spec_id, last_result),
    )
    conn.commit()
    conn.close()


def _write_bridge(project_root: Path, index_text: str, files: dict[str, str]) -> Path:
    bridge_dir = project_root / "bridge"
    bridge_dir.mkdir()
    index = bridge_dir / "INDEX.md"
    index.write_text(index_text, encoding="utf-8")
    for rel, content in files.items():
        path = project_root / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")
    return index


def test_audit_flags_terminal_spec_without_test_or_implementation(tmp_path: Path) -> None:
    """Verifies DCL-RETROACTIVE-TRIAD-COMPLETENESS-001.A1: terminal specs need tests and implementation evidence."""
    db_path = tmp_path / "groundtruth.db"
    _init_db(db_path)
    _insert_spec(db_path, "SPEC-MISSING", status="verified")
    index = _write_bridge(tmp_path, "", {})

    report = run_audit(db_path, index, tmp_path)

    kinds = {gap["kind"] for gap in report["gaps"]}
    assert "terminal_spec_without_test_mapping" in kinds
    assert "terminal_spec_without_implementation_evidence" in kinds


def test_audit_accepts_terminal_spec_with_passing_test_and_source_path(tmp_path: Path) -> None:
    """Verifies DCL-GTKB-INDEPENDENT-TEST-SUITE-001.A1: platform audit can pass a complete triad without app tests."""
    db_path = tmp_path / "groundtruth.db"
    _init_db(db_path)
    _insert_spec(
        db_path,
        "DCL-COMPLETE-001",
        status="implemented",
        source_paths=["scripts/audit_gtkb_triad_completeness.py"],
    )
    _insert_owner_deliberation(db_path, "DCL-COMPLETE-001")
    _insert_test(db_path, "DCL-COMPLETE-001", last_result="pass")
    index = _write_bridge(tmp_path, "", {})

    report = run_audit(db_path, index, tmp_path)

    assert report["gap_count"] == 0


def test_audit_flags_go_bridge_without_specification_links(tmp_path: Path) -> None:
    """Verifies DCL-RETROACTIVE-TRIAD-COMPLETENESS-001.A2: historical GO bridges need explicit spec links."""
    db_path = tmp_path / "groundtruth.db"
    _init_db(db_path)
    index = _write_bridge(
        tmp_path,
        "Document: missing-links\nGO: bridge/missing-links-002.md\nNEW: bridge/missing-links-001.md\n",
        {"bridge/missing-links-002.md": "GO\n\n# Review\n\nNo links here.\n"},
    )

    report = run_audit(db_path, index, tmp_path)

    assert any(
        gap["kind"] == "bridge_terminal_without_specification_links_section" and gap["artifact_id"] == "missing-links"
        for gap in report["gaps"]
    )


def test_audit_flags_agent_red_specs_for_reclassification_review(tmp_path: Path) -> None:
    """Verifies DCL-ADOPTER-SPEC-RECLASSIFICATION-001.A1: Agent Red specs are triaged as platform/adopter candidates."""
    db_path = tmp_path / "groundtruth.db"
    _init_db(db_path)
    _insert_spec(
        db_path,
        "SPEC-AGENT-RED-CANDIDATE",
        status="verified",
        title="Agent Red behavior that may be GT-KB platform behavior",
        source_paths=["applications/Agent_Red/example.py"],
    )
    _insert_test(db_path, "SPEC-AGENT-RED-CANDIDATE", last_result="pass")
    index = _write_bridge(tmp_path, "", {})

    report = run_audit(db_path, index, tmp_path)

    assert any(gap["kind"] == "agent_red_scoped_spec_candidate_for_gtkb_reclassification" for gap in report["gaps"])


def test_audit_flags_spec_without_owner_deliberation_origin(tmp_path: Path) -> None:
    """Verifies DCL-SPEC-ORIGIN-DELIBERATION-SUPPORT-001.A1: unsupported specs are owner-decision candidates."""
    db_path = tmp_path / "groundtruth.db"
    _init_db(db_path)
    _insert_spec(db_path, "SPEC-NO-DELIB", status="specified")
    index = _write_bridge(tmp_path, "", {})

    report = run_audit(db_path, index, tmp_path)

    assert any(
        gap["kind"] == "spec_without_owner_deliberation_origin"
        and gap["artifact_id"] == "SPEC-NO-DELIB"
        and gap["severity"] == "critical"
        for gap in report["gaps"]
    )


def test_audit_accepts_owner_deliberation_origin(tmp_path: Path) -> None:
    """Verifies DCL-SPEC-ORIGIN-DELIBERATION-SUPPORT-001.A2: owner deliberation supports spec origin."""
    db_path = tmp_path / "groundtruth.db"
    _init_db(db_path)
    _insert_spec(db_path, "SPEC-WITH-DELIB", status="specified")
    _insert_owner_deliberation(db_path, "SPEC-WITH-DELIB")
    index = _write_bridge(tmp_path, "", {})

    report = run_audit(db_path, index, tmp_path)

    assert not any(
        gap["kind"] == "spec_without_owner_deliberation_origin" and gap["artifact_id"] == "SPEC-WITH-DELIB"
        for gap in report["gaps"]
    )
