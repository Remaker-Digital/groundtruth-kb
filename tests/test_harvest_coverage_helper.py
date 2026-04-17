# © 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""Tests for groundtruth_kb.reporting.harvest_coverage.

Scope-GO evidence (per bridge/gtkb-da-harvest-coverage-implementation-005.md
Codex GO condition 3):

- duplicate wildcard DELIBs count as one covered thread
- empty index → 100.0% coverage
- set-based correctness (numerator ≤ denominator always)
"""

from __future__ import annotations

from pathlib import Path

import pytest

from groundtruth_kb.reporting.harvest_coverage import (
    _active_verified_threads,
    compute_active_bridge_thread_coverage,
)


class _FakeDB:
    """Minimal fake DB returning pre-seeded DELIB rows for given source_ref."""

    def __init__(self, rows_by_source_ref: dict[str, list[dict[str, object]]]):
        self._rows = rows_by_source_ref

    def list_deliberations(
        self,
        *,
        source_type: str | None = None,
        source_ref: str | None = None,
    ) -> list[dict[str, object]]:
        if source_type != "bridge_thread":
            return []
        if source_ref is None:
            return [r for rows in self._rows.values() for r in rows]
        return list(self._rows.get(source_ref, []))


def _write_index(path: Path, entries: list[tuple[str, list[tuple[str, str]]]]) -> None:
    """Write a bridge INDEX-format file.

    entries: list of (thread_name, [(status, filename), ...]) where the first
    status in the inner list is the latest.
    """
    lines = ["# Bridge Index", ""]
    for name, versions in entries:
        lines.append(f"Document: {name}")
        for status, fname in versions:
            lines.append(f"{status}: bridge/{fname}")
        lines.append("")
    path.write_text("\n".join(lines), encoding="utf-8")


# ---------------------------------------------------------------------------
# _active_verified_threads — INDEX parsing
# ---------------------------------------------------------------------------


def test_active_verified_threads_missing_index_returns_empty(tmp_path: Path) -> None:
    """Missing INDEX returns empty list."""
    result = _active_verified_threads(tmp_path / "does-not-exist.md")
    assert result == []


def test_active_verified_threads_picks_latest_status(tmp_path: Path) -> None:
    """Only entries whose LATEST status is VERIFIED are counted."""
    idx = tmp_path / "INDEX.md"
    _write_index(
        idx,
        [
            ("thread-a", [("VERIFIED", "thread-a-002.md"), ("NEW", "thread-a-001.md")]),
            ("thread-b", [("GO", "thread-b-002.md"), ("NEW", "thread-b-001.md")]),
            ("thread-c", [("VERIFIED", "thread-c-001.md")]),
        ],
    )
    result = _active_verified_threads(idx)
    assert sorted(result) == ["thread-a", "thread-c"]


def test_active_verified_threads_skips_comments_and_blanks(tmp_path: Path) -> None:
    """HTML comments and blank lines are ignored; entries still parsed."""
    idx = tmp_path / "INDEX.md"
    idx.write_text(
        "\n".join(
            [
                "# Bridge Index",
                "",
                "<!-- retired old entry -->",
                "Document: x",
                "<!-- inline comment -->",
                "VERIFIED: bridge/x-001.md",
                "",
                "Document: y",
                "NO-GO: bridge/y-001.md",
            ],
        ),
        encoding="utf-8",
    )
    result = _active_verified_threads(idx)
    assert result == ["x"]


def test_active_verified_threads_empty_index_returns_empty(tmp_path: Path) -> None:
    """Index with only header returns empty list."""
    idx = tmp_path / "INDEX.md"
    idx.write_text("# Bridge Index\n", encoding="utf-8")
    assert _active_verified_threads(idx) == []


# ---------------------------------------------------------------------------
# compute_active_bridge_thread_coverage — coverage formula
# ---------------------------------------------------------------------------


def test_compute_coverage_empty_index_returns_100pct(tmp_path: Path) -> None:
    """Empty INDEX → 100.0% coverage (denominator 0, by convention)."""
    idx = tmp_path / "INDEX.md"
    idx.write_text("# Bridge Index\n", encoding="utf-8")
    db = _FakeDB({})
    result = compute_active_bridge_thread_coverage(idx, db)
    assert result["coverage_pct"] == 100.0
    assert result["denominator_threads"] == 0
    assert result["numerator_threads"] == 0
    assert result["uncovered_thread_names"] == []
    assert result["covered_thread_names"] == []


def test_compute_coverage_all_covered_returns_100pct(tmp_path: Path) -> None:
    """All VERIFIED threads have wildcard DELIBs → 100.0% coverage."""
    idx = tmp_path / "INDEX.md"
    _write_index(
        idx,
        [
            ("thread-a", [("VERIFIED", "thread-a-001.md")]),
            ("thread-b", [("VERIFIED", "thread-b-001.md")]),
        ],
    )
    db = _FakeDB(
        {
            "bridge/thread-a-*.md": [{"id": "DELIB-0001"}],
            "bridge/thread-b-*.md": [{"id": "DELIB-0002"}],
        },
    )
    result = compute_active_bridge_thread_coverage(idx, db)
    assert result["coverage_pct"] == 100.0
    assert result["denominator_threads"] == 2
    assert result["numerator_threads"] == 2
    assert result["uncovered_thread_names"] == []
    assert result["covered_thread_names"] == ["thread-a", "thread-b"]


def test_compute_coverage_duplicate_wildcard_counts_as_one_thread(tmp_path: Path) -> None:
    """Multiple DELIBs for the same wildcard ref still count the thread once.

    Set-based numerator means duplicate rows do not inflate coverage.
    """
    idx = tmp_path / "INDEX.md"
    _write_index(idx, [("thread-a", [("VERIFIED", "thread-a-001.md")])])
    db = _FakeDB(
        {
            "bridge/thread-a-*.md": [
                {"id": "DELIB-0001"},
                {"id": "DELIB-0002"},
                {"id": "DELIB-0003"},
            ],
        },
    )
    result = compute_active_bridge_thread_coverage(idx, db)
    assert result["coverage_pct"] == 100.0
    assert result["numerator_threads"] == 1
    assert result["denominator_threads"] == 1


def test_compute_coverage_partial_coverage_surfaces_uncovered(tmp_path: Path) -> None:
    """Partial coverage returns exact uncovered thread names, sorted."""
    idx = tmp_path / "INDEX.md"
    _write_index(
        idx,
        [
            ("thread-alpha", [("VERIFIED", "thread-alpha-001.md")]),
            ("thread-beta", [("VERIFIED", "thread-beta-001.md")]),
            ("thread-gamma", [("VERIFIED", "thread-gamma-001.md")]),
            ("thread-delta", [("VERIFIED", "thread-delta-001.md")]),
        ],
    )
    db = _FakeDB(
        {
            "bridge/thread-alpha-*.md": [{"id": "DELIB-0001"}],
            "bridge/thread-gamma-*.md": [{"id": "DELIB-0003"}],
        },
    )
    result = compute_active_bridge_thread_coverage(idx, db)
    assert result["denominator_threads"] == 4
    assert result["numerator_threads"] == 2
    assert result["coverage_pct"] == 50.0
    assert result["uncovered_thread_names"] == ["thread-beta", "thread-delta"]
    assert result["covered_thread_names"] == ["thread-alpha", "thread-gamma"]


def test_compute_coverage_non_verified_excluded_from_denominator(tmp_path: Path) -> None:
    """Threads with latest status != VERIFIED do not contribute to denominator."""
    idx = tmp_path / "INDEX.md"
    _write_index(
        idx,
        [
            ("thread-a", [("VERIFIED", "thread-a-001.md")]),
            ("thread-b", [("NO-GO", "thread-b-002.md"), ("NEW", "thread-b-001.md")]),
            ("thread-c", [("REVISED", "thread-c-002.md")]),
        ],
    )
    db = _FakeDB({"bridge/thread-a-*.md": [{"id": "DELIB-0001"}]})
    result = compute_active_bridge_thread_coverage(idx, db)
    assert result["denominator_threads"] == 1
    assert result["numerator_threads"] == 1
    assert result["coverage_pct"] == 100.0


def test_compute_coverage_numerator_never_exceeds_denominator(tmp_path: Path) -> None:
    """Set-based invariant: numerator ≤ denominator. Rogue extra rows don't inflate."""
    idx = tmp_path / "INDEX.md"
    _write_index(
        idx,
        [
            ("thread-a", [("VERIFIED", "thread-a-001.md")]),
        ],
    )
    # Seed DB with rows for threads NOT in the active VERIFIED set — they must be ignored.
    db = _FakeDB(
        {
            "bridge/thread-a-*.md": [{"id": "DELIB-0001"}],
            "bridge/unrelated-thread-*.md": [{"id": "DELIB-0009"}],
            "bridge/another-one-*.md": [{"id": "DELIB-0010"}],
        },
    )
    result = compute_active_bridge_thread_coverage(idx, db)
    assert result["numerator_threads"] == 1
    assert result["denominator_threads"] == 1
    assert result["coverage_pct"] == 100.0


def test_compute_coverage_rounds_to_two_decimals(tmp_path: Path) -> None:
    """Coverage percentage rounded to 2 decimal places."""
    idx = tmp_path / "INDEX.md"
    # 1 of 3 → 33.33%
    _write_index(
        idx,
        [
            ("thread-a", [("VERIFIED", "thread-a-001.md")]),
            ("thread-b", [("VERIFIED", "thread-b-001.md")]),
            ("thread-c", [("VERIFIED", "thread-c-001.md")]),
        ],
    )
    db = _FakeDB({"bridge/thread-a-*.md": [{"id": "DELIB-0001"}]})
    result = compute_active_bridge_thread_coverage(idx, db)
    assert result["coverage_pct"] == pytest.approx(33.33, abs=0.01)
