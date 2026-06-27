"""Coverage-completeness gate for cross-harness parity (WI-4892, Slice 6, final).

Asserts the program's terminal invariant: the live tree has **0 unwaived**
cross-harness hook-surface asymmetries, and every typed parity waiver validates
(`PARITY-WAIVER-SCHEMA`) and cites an `owner_approval_ref`. This is the CI/release
hard gate in test form — `groundtruth-kb-tests.yml` also runs the diff CLI
directly (exit non-zero on asymmetry).

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

from __future__ import annotations

import sys
from pathlib import Path

_PROJECT_ROOT = Path(__file__).resolve().parents[2]
_SCRIPTS = _PROJECT_ROOT / "scripts"
if str(_SCRIPTS) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS))

import check_harness_parity as parity  # noqa: E402
import parity_discovery_diff as diff  # noqa: E402


def _live_registry() -> dict:
    registry, _ = parity.load_registry(_PROJECT_ROOT)
    return registry


def test_zero_unwaived_asymmetries_live() -> None:
    report = diff.run_discovery_diff(_PROJECT_ROOT)
    assert report.overall_status == "PASS", (
        f"{len(report.findings)} unwaived asymmetry(ies): {', '.join(f.capability_key for f in report.findings)}"
    )
    assert report.findings == []


def test_every_waiver_validates_and_cites_owner_ref() -> None:
    registry = _live_registry()
    waivers = parity.load_parity_waivers(registry)
    assert waivers, "expected the Slice-6 typed parity waivers to be present"
    for index, waiver in enumerate(waivers):
        errors = parity.validate_parity_waiver(waiver)
        assert not errors, f"parity_waivers[{index}] ({waiver.get('capability_id')}): {errors}"
        assert str(waiver.get("owner_approval_ref") or "").strip(), (
            f"parity_waivers[{index}] ({waiver.get('capability_id')}) missing owner_approval_ref"
        )


def test_full_parity_schema_valid_live() -> None:
    assert parity.validate_parity_schema(_live_registry()) == []
