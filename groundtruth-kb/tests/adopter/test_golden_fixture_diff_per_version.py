# © 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""Phase 9 §5 lines 251-252: ``per-version golden fixture diff``.

Spec: a freshly scaffolded dual-agent adopter must byte-equal the committed
golden fixture at ``tests/fixtures/scaffold_golden/dual-agent/``. Drift in
either direction (scaffold change without fixture re-capture, or fixture
re-capture without scaffold change) is surfaced as a clear file-by-file diff.

Outside-in surface: ``scaffold_project`` output directory + filesystem
byte-comparison against the committed fixture tree.

Reuses Slice 3 TP14/TP15's masking logic for ``created_at`` (the only
deterministic dynamic field). ``groundtruth.db`` is excluded (binary,
non-deterministic SQLite page checksums). To regenerate the fixture when
scaffold templates legitimately change, run:
``python scripts/_capture_scaffold_golden.py``.

Authority: ``bridge/gtkb-isolation-017-slice5-clean-adopter-tests-2026-05-03-004.md`` GO.
"""

from __future__ import annotations

import re
import shutil
from pathlib import Path

import pytest

from groundtruth_kb.project.scaffold import (
    _GT_KB_HOST_ROOT,
    ScaffoldOptions,
    scaffold_project,
)

_GOLDEN_FIXTURE_ROOT = Path(__file__).resolve().parents[1] / "fixtures" / "scaffold_golden"
_CREATED_AT_RE = re.compile(rb'created_at = "[^"]*"')
_CREATED_AT_MASK = b'created_at = "<NORMALIZED-FOR-FIXTURE-DIFF>"'

# Match the exact scaffold options Slice 3 used to capture the golden.
# Diverging on any of these (project_name, owner, profile, flags) would
# produce non-deterministic-looking diffs that this test cannot mask.
_GOLDEN_PROFILE = "dual-agent"
_GOLDEN_SANDBOX_NAME = "_test_golden_dual_agent"
_GOLDEN_OWNER = "GoldenFixtureOwner"


def _normalize_for_diff(content: bytes, rel_path: Path) -> bytes:
    """Mask the only known dynamic scaffold field (``groundtruth.toml::created_at``)."""
    if rel_path.name == "groundtruth.toml":
        return _CREATED_AT_RE.sub(_CREATED_AT_MASK, content)
    return content


def _list_fixture_files(profile: str) -> set[Path]:
    fixture_root = _GOLDEN_FIXTURE_ROOT / profile
    return {f.relative_to(fixture_root) for f in fixture_root.rglob("*") if f.is_file()}


def _scaffold_at_golden_options(sandbox: Path) -> None:
    options = ScaffoldOptions(
        project_name=sandbox.name,
        profile=_GOLDEN_PROFILE,
        owner=_GOLDEN_OWNER,
        target_dir=sandbox,
        gt_kb_root=_GT_KB_HOST_ROOT,
        seed_example=False,
        include_ci=False,
        init_git=False,
    )
    scaffold_project(options)


@pytest.fixture
def golden_sandbox() -> Path:
    """Yield the in-root sandbox path for the dual-agent golden capture.

    Uses the same path Slice 3's ``_run_golden_scaffold`` uses so this test
    + Slice 3's TP14/TP15 share a coordinated sandbox layout (sequential
    pytest execution prevents collision; the per-test cleanup ensures
    re-runs don't accumulate state).
    """
    sandbox = _GT_KB_HOST_ROOT / "applications" / _GOLDEN_SANDBOX_NAME
    if sandbox.exists():
        shutil.rmtree(sandbox, ignore_errors=True)
    try:
        yield sandbox
    finally:
        if sandbox.exists():
            shutil.rmtree(sandbox, ignore_errors=True)


def test_clean_adopter_byte_matches_golden_fixture(golden_sandbox: Path) -> None:
    """Scaffold a dual-agent adopter at the golden options; byte-compare each
    fixture file against the produced adopter.

    Failure modes surfaced explicitly:

    - Adopter is missing a file the fixture has → "missing" drift.
    - Adopter has a file the fixture doesn't have → "extra" drift.
    - File bytes diverge after ``_normalize_for_diff`` masking → "byte" drift.
    """
    _scaffold_at_golden_options(golden_sandbox)

    fixture_files = _list_fixture_files(_GOLDEN_PROFILE)
    fixture_root = _GOLDEN_FIXTURE_ROOT / _GOLDEN_PROFILE

    drift_missing: list[str] = []
    drift_byte: list[str] = []
    for rel in sorted(fixture_files):
        scaffold_path = golden_sandbox / rel
        if not scaffold_path.exists():
            drift_missing.append(rel.as_posix())
            continue
        scaffold_bytes = _normalize_for_diff(scaffold_path.read_bytes(), rel)
        fixture_bytes = _normalize_for_diff((fixture_root / rel).read_bytes(), rel)
        if scaffold_bytes != fixture_bytes:
            drift_byte.append(rel.as_posix())

    drift_extra: list[str] = []
    for path in golden_sandbox.rglob("*"):
        if not path.is_file():
            continue
        rel = path.relative_to(golden_sandbox)
        if rel.name == "groundtruth.db":
            # Excluded from the golden by design (non-deterministic binary).
            continue
        if rel not in fixture_files:
            drift_extra.append(rel.as_posix())

    parts: list[str] = []
    if drift_missing:
        parts.append(f"{len(drift_missing)} missing in scaffold: {drift_missing[:10]}")
    if drift_extra:
        parts.append(f"{len(drift_extra)} extra in scaffold: {drift_extra[:10]}")
    if drift_byte:
        parts.append(f"{len(drift_byte)} byte-different: {drift_byte[:10]}")

    assert not parts, (
        "scaffold output drifted from committed golden; "
        "regenerate with `python scripts/_capture_scaffold_golden.py` if "
        "the change is intentional. Drift summary: " + " | ".join(parts)
    )
