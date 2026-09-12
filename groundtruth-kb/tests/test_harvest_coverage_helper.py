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
            results = []
            for ref, rows in self._rows.items():
                for r in rows:
                    r_copy = dict(r)
                    r_copy.setdefault("source_ref", ref)
                    results.append(r_copy)
            return results
        results = []
        for r in self._rows.get(source_ref, []):
            r_copy = dict(r)
            r_copy.setdefault("source_ref", source_ref)
            results.append(r_copy)
        return results


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
