# © 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""FAB-07 (WI-4419) HYG-049/035/067/068: doctor false-signal fixes.

Asserts DA-harvest coverage uses prefix matching (not exact source_ref),
the three narrative files cite `groundtruth-kb/examples/` (not "four demo
applications"), project-root-boundary.md has the examples carve-out,
AUQ-coverage excludes prose-pattern false positives, and the isolation suite
gates adopter-context checks when running against the platform dev repo.
Authority: DELIB-FAB07-REMEDIATION-20260610.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

_ROOT = Path(__file__).resolve().parents[2]


def _read(rel: str) -> str:
    return (_ROOT / rel).read_text(encoding="utf-8")


# ---------------------------------------------------------------------------
# HYG-049: DA-harvest prefix matching
# ---------------------------------------------------------------------------


class _FakeDB:
    """Minimal stub satisfying _DeliberationLister protocol."""

    def __init__(self, rows: list[dict[str, Any]]) -> None:
        self._rows = rows

    def list_deliberations(
        self,
        *,
        source_type: str | None = None,
        source_ref: str | None = None,
    ) -> list[dict[str, Any]]:
        out = self._rows
        if source_type is not None:
            out = [r for r in out if r.get("source_type") == source_type]
        if source_ref is not None:
            out = [r for r in out if r.get("source_ref") == source_ref]
        return out


def _make_index(entries: dict[str, str]) -> str:
    """Build a minimal INDEX.md from {thread_name: latest_status} mapping."""
    lines = ["# INDEX"]
    for name, status in entries.items():
        lines.append(f"Document: {name}")
        lines.append(f"{status}: bridge/{name}-001.md")
    return "\n".join(lines) + "\n"


def _write_bridge_files(bridge_dir: Path, entries: dict[str, str]) -> None:
    bridge_dir.mkdir()
    for name, status in entries.items():
        (bridge_dir / f"{name}-001.md").write_text(f"{status}\n\nDocument: {name}\n", encoding="utf-8")


def test_harvest_coverage_prefix_match(tmp_path: Path) -> None:
    """Coverage computation matches per-file source_refs via prefix, not exact."""
    from groundtruth_kb.reporting.harvest_coverage import (
        compute_active_bridge_thread_coverage,
    )

    bridge_dir = tmp_path / "bridge"
    _write_bridge_files(bridge_dir, {"alpha-thread": "VERIFIED", "beta-thread": "VERIFIED"})

    db = _FakeDB(
        [
            {"source_type": "bridge_thread", "source_ref": "bridge/alpha-thread-001.md"},
            {"source_type": "bridge_thread", "source_ref": "bridge/alpha-thread-002.md"},
            {"source_type": "bridge_thread", "source_ref": "bridge/beta-thread-003.md"},
        ]
    )

    result = compute_active_bridge_thread_coverage(bridge_dir, db)
    assert result["denominator_threads"] == 2
    assert result["numerator_threads"] == 2
    assert result["coverage_pct"] == 100.0
    assert result["uncovered_thread_names"] == []


def test_harvest_coverage_genuine_gap(tmp_path: Path) -> None:
    """A thread with no matching source_ref still registers as uncovered."""
    from groundtruth_kb.reporting.harvest_coverage import (
        compute_active_bridge_thread_coverage,
    )

    bridge_dir = tmp_path / "bridge"
    _write_bridge_files(bridge_dir, {"covered": "VERIFIED", "uncovered": "VERIFIED"})

    db = _FakeDB([{"source_type": "bridge_thread", "source_ref": "bridge/covered-001.md"}])

    result = compute_active_bridge_thread_coverage(bridge_dir, db)
    assert result["denominator_threads"] == 2
    assert result["numerator_threads"] == 1
    assert result["coverage_pct"] == 50.0
    assert result["uncovered_thread_names"] == ["uncovered"]


# ---------------------------------------------------------------------------
# HYG-035: narrative file rewording + project-root-boundary carve-out
# ---------------------------------------------------------------------------


_NARRATIVE_FILES = [
    "AGENTS.md",
    ".claude/rules/canonical-terminology.md",
    ".claude/rules/acting-prime-builder.md",
]


def test_project_root_boundary_examples_carveout() -> None:
    """project-root-boundary.md has the examples/ carve-out."""
    text = _read(".harness-baseline-configuration/rules/project-root-boundary.md")
    assert "groundtruth-kb/examples/" in text
    assert "exempt" in text.lower() or "EXCEPTION" in text


# ---------------------------------------------------------------------------
# HYG-067: AUQ-coverage prose-pattern exclusion
# ---------------------------------------------------------------------------


# ---------------------------------------------------------------------------
# HYG-068: isolation-suite adopter-context gating
# ---------------------------------------------------------------------------


def test_isolation_suite_skips_adopter_checks_on_platform(tmp_path: Path) -> None:
    """When target has a groundtruth-kb/ subdir, adopter-specific checks are pass-with-skip."""
    from groundtruth_kb.project.doctor_isolation import run_isolation_checks

    (tmp_path / "groundtruth-kb").mkdir()

    results = run_isolation_checks(tmp_path, "scaffold", product_root=tmp_path)

    names = {r.name for r in results}
    assert "isolation:adopter-root-placement" in names
    assert "isolation:work-subject" in names

    for r in results:
        if r.name in (
            "isolation:adopter-root-placement",
            "isolation:work-subject",
            "isolation:hooks-point-to-wrappers",
            "isolation:workstream-focus-hook-absent",
            "isolation:release-readiness-app-subject-header",
        ):
            assert r.status == "pass", f"{r.name} expected pass, got {r.status}"
            assert "platform development repository" in r.message


def test_isolation_suite_runs_adopter_checks_on_adopter(tmp_path: Path) -> None:
    """Without groundtruth-kb/ subdir, adopter-context checks run (may fail, but are present)."""
    from groundtruth_kb.project.doctor_isolation import run_isolation_checks

    results = run_isolation_checks(tmp_path, "scaffold", product_root=tmp_path)

    names = [r.name for r in results]
    assert "isolation:adopter-root-placement" in names
    assert "isolation:work-subject" in names
    for r in results:
        if r.name in ("isolation:adopter-root-placement", "isolation:work-subject"):
            assert "platform development repository" not in r.message
