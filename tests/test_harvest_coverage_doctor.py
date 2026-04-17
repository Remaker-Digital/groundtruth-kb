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
    DA_HARVEST_COVERAGE_ERROR_THRESHOLD,
    DA_HARVEST_COVERAGE_WARN_THRESHOLD,
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


def test_check_da_harvest_coverage_passes_at_100_percent(tmp_path: Path) -> None:
    """All active VERIFIED threads covered → pass."""
    threads = [f"thread-{i}" for i in range(5)]
    target = _make_project_dir(tmp_path, threads, threads)
    result = _check_da_harvest_coverage(target)
    assert result.status == "pass"
    assert "100.00%" in result.message
    assert "5/5" in result.message


def test_check_da_harvest_coverage_passes_at_warn_threshold(tmp_path: Path) -> None:
    """Coverage exactly at WARN threshold (95%) → pass (boundary = pass)."""
    # 20 threads, 19 covered = 95.00%
    threads = [f"thread-{i:02d}" for i in range(20)]
    target = _make_project_dir(tmp_path, threads, threads[:19])
    result = _check_da_harvest_coverage(target)
    assert result.status == "pass"
    assert "95.00%" in result.message
    # Sanity: confirm constant is what we think
    assert DA_HARVEST_COVERAGE_WARN_THRESHOLD == 95.0


def test_check_da_harvest_coverage_warns_below_warn_threshold(tmp_path: Path) -> None:
    """Below WARN but at-or-above ERROR threshold → warning."""
    # 10 threads, 9 covered = 90.00% (below 95 WARN, above 80 ERROR)
    threads = [f"thread-{i:02d}" for i in range(10)]
    target = _make_project_dir(tmp_path, threads, threads[:9])
    result = _check_da_harvest_coverage(target)
    assert result.status == "warning"
    assert "90.00%" in result.message
    assert "below WARN threshold" in result.message


def test_check_da_harvest_coverage_warns_exactly_at_error_threshold(tmp_path: Path) -> None:
    """Coverage exactly at ERROR threshold (80%) → warning (boundary = warning, not fail)."""
    # 10 threads, 8 covered = 80.00%
    threads = [f"thread-{i:02d}" for i in range(10)]
    target = _make_project_dir(tmp_path, threads, threads[:8])
    result = _check_da_harvest_coverage(target)
    assert result.status == "warning"
    assert "80.00%" in result.message
    assert DA_HARVEST_COVERAGE_ERROR_THRESHOLD == 80.0


def test_check_da_harvest_coverage_fails_below_error_threshold(tmp_path: Path) -> None:
    """Below ERROR threshold → fail."""
    # 10 threads, 7 covered = 70.00%
    threads = [f"thread-{i:02d}" for i in range(10)]
    target = _make_project_dir(tmp_path, threads, threads[:7])
    result = _check_da_harvest_coverage(target)
    assert result.status == "fail"
    assert "70.00%" in result.message
    assert "below ERROR threshold" in result.message


def test_check_da_harvest_coverage_fails_at_0_percent(tmp_path: Path) -> None:
    """0% coverage → fail."""
    threads = [f"thread-{i:02d}" for i in range(5)]
    target = _make_project_dir(tmp_path, threads, [])
    result = _check_da_harvest_coverage(target)
    assert result.status == "fail"
    assert "0.00%" in result.message


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


def test_check_da_harvest_coverage_message_includes_uncovered_preview(tmp_path: Path) -> None:
    """Below-threshold result mentions at least one uncovered thread name."""
    threads = [f"thread-{i:02d}" for i in range(10)]
    target = _make_project_dir(tmp_path, threads, threads[:7])
    result = _check_da_harvest_coverage(target)
    assert result.status == "fail"
    # Uncovered threads are sorted; at least one name should appear
    assert "thread-07" in result.message or "thread-08" in result.message or "thread-09" in result.message


def test_check_da_harvest_coverage_previews_only_three_uncovered(tmp_path: Path) -> None:
    """Message previews up to 3 uncovered threads + 'N more' suffix."""
    threads = [f"thread-{i:02d}" for i in range(20)]
    # Cover only 10 → 50% coverage, 10 uncovered
    target = _make_project_dir(tmp_path, threads, threads[:10])
    result = _check_da_harvest_coverage(target)
    assert result.status == "fail"
    assert "(+7 more)" in result.message
