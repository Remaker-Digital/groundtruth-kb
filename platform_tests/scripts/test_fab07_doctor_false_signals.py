# © 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""Retain project-root examples and platform/adopter isolation checks after doctor cleanup."""

from __future__ import annotations

from pathlib import Path

_ROOT = Path(__file__).resolve().parents[2]


def _read(rel: str) -> str:
    return (_ROOT / rel).read_text(encoding="utf-8")


# ---------------------------------------------------------------------------
# HYG-035: narrative file rewording + project-root-boundary carve-out
# ---------------------------------------------------------------------------


_NARRATIVE_FILES = [
    "AGENTS.md",
    ".harness-baseline-configuration/rules/canonical-terminology.md",
    ".harness-baseline-configuration/rules/acting-prime-builder.md",
]


def test_project_root_boundary_examples_carveout() -> None:
    """project-root-boundary.md has the examples/ carve-out."""
    text = _read(".harness-baseline-configuration/rules/project-root-boundary.md")
    assert "groundtruth-kb/examples/" in text
    assert "exempt" in text.lower() or "EXCEPTION" in text


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
    assert "isolation:hook-settings-structure" in names

    for r in results:
        if r.name in (
            "isolation:adopter-root-placement",
            "isolation:work-subject",
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
    assert "isolation:hook-settings-structure" in names
    for r in results:
        if r.name in ("isolation:adopter-root-placement", "isolation:work-subject"):
            assert "platform development repository" not in r.message
