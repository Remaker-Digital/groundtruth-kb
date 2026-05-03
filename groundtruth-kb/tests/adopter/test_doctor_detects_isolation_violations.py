# © 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""Phase 9 §5 line 241: ``doctor detects isolation violations``.

Spec: each of the 9 Slice 1 isolation checks fires the documented status
when its triggering condition is set up. Outside-in surface:
``run_isolation_checks(target, profile, *, product_root=...)``.

This test does NOT re-test the per-check logic that ``test_doctor_isolation.py``
already covers; it covers the **integration** contract that the orchestrator
returns each check by name and that triggering states surface from the
adopter-test-suite vantage point.

Authority: ``bridge/gtkb-isolation-017-slice5-clean-adopter-tests-2026-05-03-004.md`` GO.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from groundtruth_kb.project.doctor_isolation import run_isolation_checks


def _checks_by_name(adopter: Path, product_root: Path) -> dict[str, object]:
    return {c.name: c for c in run_isolation_checks(adopter, "dual-agent", product_root=product_root)}


def test_check_1_adopter_root_placement_fails_when_under_product_root(tmp_path: Path) -> None:
    """Check #1 fires ``status="fail"`` when adopter is a child of product_root."""
    product_root = tmp_path
    adopter = product_root / "applications" / "test_under"
    adopter.mkdir(parents=True)
    by_name = _checks_by_name(adopter, product_root)
    assert by_name["isolation:adopter-root-placement"].status == "fail"


def test_check_2_service_endpoint_fails_when_raw_db(
    clean_adopter: tuple[Path, Path],
) -> None:
    """Check #2 fires ``status="fail"`` when ``[service].endpoint`` is a raw DB path."""
    adopter, doctor_root = clean_adopter
    toml = adopter / "groundtruth.toml"
    text = toml.read_text(encoding="utf-8")
    text = text.replace(
        'endpoint = "configure-me://placeholder/v1"',
        'endpoint = "groundtruth.db"',
    )
    toml.write_text(text, encoding="utf-8")
    by_name = _checks_by_name(adopter, doctor_root)
    assert by_name["isolation:service-endpoint"].status == "fail"


def test_check_3_work_subject_warns_on_unexpected_subject(
    clean_adopter: tuple[Path, Path],
) -> None:
    """Check #3 fires ``status="warning"`` when ``current_subject`` is not application."""
    adopter, doctor_root = clean_adopter
    state_path = adopter / ".claude" / "session" / "work-subject.json"
    state_path.parent.mkdir(parents=True, exist_ok=True)
    state_path.write_text(json.dumps({"current_subject": "platform"}), encoding="utf-8")
    by_name = _checks_by_name(adopter, doctor_root)
    assert by_name["isolation:work-subject"].status == "warning"


def test_check_6_workstream_focus_warns_when_legacy_hook_present(
    clean_adopter: tuple[Path, Path],
) -> None:
    """Check #6 fires ``status="warning"`` when the legacy hook reappears."""
    adopter, doctor_root = clean_adopter
    legacy = adopter / ".claude" / "hooks" / "workstream-focus.py"
    legacy.parent.mkdir(parents=True, exist_ok=True)
    legacy.write_text("# legacy\n", encoding="utf-8")
    by_name = _checks_by_name(adopter, doctor_root)
    assert by_name["isolation:workstream-focus-hook-absent"].status == "warning"


def test_check_8_release_readiness_warns_on_wrong_header(
    clean_adopter: tuple[Path, Path],
) -> None:
    """Check #8 fires ``status="warning"`` when the header omits "application"."""
    adopter, doctor_root = clean_adopter
    rr = adopter / "memory" / "release-readiness.md"
    rr.write_text("# Platform release readiness\n\nGT-KB ready\n", encoding="utf-8")
    by_name = _checks_by_name(adopter, doctor_root)
    assert by_name["isolation:release-readiness-app-subject-header"].status == "warning"


def test_check_9_chroma_warns_when_db_missing(
    clean_adopter: tuple[Path, Path],
) -> None:
    """Check #9 fires ``status="warning"`` when chroma cache exists without a DB."""
    adopter, doctor_root = clean_adopter
    chroma = adopter / ".groundtruth-chroma"
    chroma.mkdir(parents=True, exist_ok=True)
    db = adopter / "groundtruth.db"
    if db.exists():
        db.unlink()
    by_name = _checks_by_name(adopter, doctor_root)
    assert by_name["isolation:chroma-regeneratable"].status == "warning"


@pytest.mark.parametrize(
    "expected_check_name",
    [
        "isolation:adopter-root-placement",
        "isolation:service-endpoint",
        "isolation:work-subject",
        "isolation:no-writable-product-paths",
        "isolation:hooks-point-to-wrappers",
        "isolation:workstream-focus-hook-absent",
        "isolation:work-list-no-product-entries",
        "isolation:release-readiness-app-subject-header",
        "isolation:chroma-regeneratable",
    ],
)
def test_orchestrator_emits_every_named_check(clean_adopter: tuple[Path, Path], expected_check_name: str) -> None:
    """The orchestrator returns all 9 checks by name in every run."""
    adopter, doctor_root = clean_adopter
    by_name = _checks_by_name(adopter, doctor_root)
    assert expected_check_name in by_name, (
        f"{expected_check_name} missing from orchestrator output; got {sorted(by_name.keys())}"
    )
