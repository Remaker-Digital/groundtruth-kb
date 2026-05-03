# © 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""Phase 9 §"Exit Criteria" §4 line 347: ``stale overlays emit warnings``.

Slice 5 retains stale-detection per
``DELIB-S328-ISOLATION-017-SLICE5-OVERLAY-SCOPE-REVISION-OWNER-DIRECTIVE`` v1
(refresh + disposability deferred to Slice 5.5). The test wraps Slice 1's
check #9 (``isolation:chroma-regeneratable``) in the clean-adopter test
surface.

Outside-in surface: ``run_isolation_checks(target, profile, *, product_root=...)``.

Authority: ``bridge/gtkb-isolation-017-slice5-clean-adopter-tests-2026-05-03-004.md`` GO.
"""

from __future__ import annotations

from pathlib import Path

from groundtruth_kb.project.doctor_isolation import run_isolation_checks


def test_stale_chroma_without_db_emits_warning(
    clean_adopter: tuple[Path, Path],
) -> None:
    """``.groundtruth-chroma`` present, ``groundtruth.db`` missing → check #9 warns.

    Validates Phase 9 §"Exit Criteria" §4 line 347 in the clean-adopter
    surface: stale overlays emit warnings.
    """
    adopter, doctor_root = clean_adopter
    chroma = adopter / ".groundtruth-chroma"
    chroma.mkdir(parents=True, exist_ok=True)
    db = adopter / "groundtruth.db"
    if db.exists():
        db.unlink()

    checks = run_isolation_checks(adopter, "dual-agent", product_root=doctor_root)
    by_name = {c.name: c for c in checks}
    chroma_check = by_name["isolation:chroma-regeneratable"]
    assert chroma_check.status == "warning", (
        f"stale chroma cache without DB should warn; got {chroma_check.status} message={chroma_check.message!r}"
    )
    assert "orphan" in chroma_check.message.lower() or "regenerat" in chroma_check.message.lower()


def test_chroma_with_present_db_passes(
    clean_adopter: tuple[Path, Path],
) -> None:
    """Inverse contract: ``.groundtruth-chroma`` + non-empty ``groundtruth.db``
    → check #9 returns ``status="pass"``.

    A clean adopter ships an initialized ``groundtruth.db`` from
    ``bootstrap._initialize_database``; creating ``.groundtruth-chroma``
    next to it should make check #9 pass (non-orphan cache).
    """
    adopter, doctor_root = clean_adopter
    chroma = adopter / ".groundtruth-chroma"
    chroma.mkdir(parents=True, exist_ok=True)
    db = adopter / "groundtruth.db"
    assert db.exists() and db.stat().st_size > 0, "scaffold should have produced a non-empty groundtruth.db"

    checks = run_isolation_checks(adopter, "dual-agent", product_root=doctor_root)
    by_name = {c.name: c for c in checks}
    chroma_check = by_name["isolation:chroma-regeneratable"]
    assert chroma_check.status == "pass", (
        f"chroma+db pair should pass check #9; got {chroma_check.status} message={chroma_check.message!r}"
    )
