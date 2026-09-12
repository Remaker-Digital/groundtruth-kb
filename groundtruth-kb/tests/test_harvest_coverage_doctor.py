# © 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""Tests for groundtruth_kb.project.doctor._check_da_harvest_coverage.

Scope-GO evidence (per bridge/gtkb-da-harvest-coverage-implementation-005.md
Codex GO condition 3): below-WARN, at-WARN, at-ERROR threshold behavior.
"""

from __future__ import annotations

import hashlib
from pathlib import Path

from groundtruth_kb.db import KnowledgeDB
from groundtruth_kb.project.doctor import (
    _check_da_harvest_coverage,
)


def _write_index(path: Path, entries: list[tuple[str, list[tuple[str, str]]]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    lines = ["# Bridge Index", ""]
    for name, versions in entries:
        lines.append(f"Document: {name}")
        for status, fname in versions:
            lines.append(f"{status}: bridge/{fname}")
        lines.append("")
    path.write_text("\n".join(lines), encoding="utf-8")


def _seed_bridge_thread_row(db: KnowledgeDB, thread_name: str, serial: int) -> None:
    """Insert one canonical wildcard DELIB for a thread using upsert.

    Uses unique content per row so content-hash doesn't collide.
    """
    content = (
        f"test payload for {thread_name} #{serial}\n"
        + hashlib.sha256(
            f"{thread_name}-{serial}".encode(),
        ).hexdigest()
    )
    db.upsert_deliberation_source(
        source_type="bridge_thread",
        source_ref=f"bridge/{thread_name}-*.md",
        content=content,
        title=f"Bridge thread: {thread_name}",
        summary=f"Test seed for {thread_name}",
        outcome="go",
        origin_project="gt-kb-test",
        origin_repo="test/test",
        changed_by="test_harvest_coverage_doctor.py",
        change_reason="unit test seed",
    )


def _make_project_dir(
    tmp_path: Path,
    verified_threads: list[str],
    threads_with_canonical: list[str],
) -> Path:
    """Build a minimal project dir with INDEX.md + groundtruth.db.

    verified_threads: thread names whose latest INDEX status will be VERIFIED.
    threads_with_canonical: subset of verified_threads to have canonical wildcard rows.
    """
    target = tmp_path / "project"
    target.mkdir()
    idx = target / "bridge" / "INDEX.md"
    entries = [(name, [("VERIFIED", f"{name}-001.md")]) for name in verified_threads]
    _write_index(idx, entries)

    # Create the DB and seed rows
    db_path = target / "groundtruth.db"
    db = KnowledgeDB(db_path=db_path)
    for name in threads_with_canonical:
        _seed_bridge_thread_row(db, name, 1)
    db.close()

    return target


def test_check_da_harvest_coverage_skipped_when_missing_index(tmp_path: Path) -> None:
    """Missing INDEX.md → skipped with warning (not fail)."""
    target = tmp_path / "project"
    target.mkdir()
    # Create DB but no INDEX
    KnowledgeDB(db_path=target / "groundtruth.db").close()
    result = _check_da_harvest_coverage(target)
    assert result.status == "warning"
    assert "skipped" in result.message.lower()


def test_check_da_harvest_coverage_skipped_when_missing_db(tmp_path: Path) -> None:
    """Missing groundtruth.db → skipped with warning."""
    target = tmp_path / "project"
    idx = target / "bridge" / "INDEX.md"
    _write_index(idx, [("thread-a", [("VERIFIED", "thread-a-001.md")])])
    result = _check_da_harvest_coverage(target)
    assert result.status == "warning"
    assert "skipped" in result.message.lower()


def test_check_da_harvest_coverage_empty_index_passes(tmp_path: Path) -> None:
    """Empty INDEX (0 denominator) → 100% coverage → pass."""
    target = tmp_path / "project"
    target.mkdir()
    (target / "bridge").mkdir()
    (target / "bridge" / "INDEX.md").write_text("# Bridge Index\n", encoding="utf-8")
    KnowledgeDB(db_path=target / "groundtruth.db").close()
    result = _check_da_harvest_coverage(target)
    assert result.status == "pass"
    assert "100.00%" in result.message
    assert "0/0" in result.message
