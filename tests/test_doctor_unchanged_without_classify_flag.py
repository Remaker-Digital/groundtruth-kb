# © 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""Doctor behavior unchanged by the ownership-matrix sub-bridge.

Proposal §3.3 — ``run_doctor()`` on a tree without ``groundtruth.toml`` must
still fail on the manifest check. No weakening of existing readiness gates.
"""

from __future__ import annotations

from pathlib import Path

from groundtruth_kb.project.doctor import run_doctor


def test_doctor_fails_on_missing_manifest(tmp_path: Path) -> None:
    """A tree without groundtruth.toml produces a failing doctor report."""
    # Fresh empty directory — no groundtruth.toml.
    report = run_doctor(tmp_path, profile="local-only")
    assert report.overall == "fail"
    # The specific failure must reference the manifest.
    names = [c.name for c in report.checks if c.status == "fail"]
    assert any("groundtruth.toml" in n or "manifest" in n.lower() for n in names), (
        f"expected a manifest-related failure; got {names}"
    )
