"""Legacy bridge-kind tolerance in the approved-proposal resolver (WI-5837).

Covers DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001 and
GOV-FILE-BRIDGE-AUTHORITY-001: a pre-convention proposal version that declares no
bridge_kind marker is recognized as the operative proposal when a later LO GO
names it, it declares a non-empty target scope, and it is not report-shaped.
"""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
SCRIPT_PATH = REPO_ROOT / "scripts" / "bridge_applicability_preflight.py"

spec = importlib.util.spec_from_file_location("bridge_applicability_preflight", SCRIPT_PATH)
assert spec is not None
preflight = importlib.util.module_from_spec(spec)
assert spec.loader is not None
sys.modules["bridge_applicability_preflight"] = preflight
spec.loader.exec_module(preflight)


def _write_version(root: Path, bridge_id: str, version: int, status: str, content: str) -> None:
    bridge = root / "bridge"
    bridge.mkdir(parents=True, exist_ok=True)
    (bridge / f"{bridge_id}-{version:03d}.md").write_text(f"{status}\n\n{content}", encoding="utf-8")


def _version(root: Path, bridge_id: str, version: int, status: str):
    path = root / "bridge" / f"{bridge_id}-{version:03d}.md"
    return preflight.BridgeVersion(
        status=status,
        rel_path=f"bridge/{bridge_id}-{version:03d}.md",
        abs_path=path,
        version_number=version,
    )


def test_legacy_proposal_resolved_when_marker_absent_go_named_and_target_scope_present(tmp_path: Path) -> None:
    bridge_id = "legacy-thread"
    # -001 legacy proposal: no bridge_kind marker, but declares a target scope.
    _write_version(
        tmp_path,
        bridge_id,
        1,
        "NEW",
        '# Legacy Proposal\n\ntarget_paths: ["scripts/x.py"]\n',
    )
    # -002 independent LO GO naming -001 operative.
    _write_version(
        tmp_path,
        bridge_id,
        2,
        "GO",
        "bridge_kind: lo_verdict\n\n# GO\n\nApproved proposal: bridge/legacy-thread-001.md\n",
    )
    # -003 implementation report (no marker, no Approved proposal: line).
    report = "bridge_kind: implementation_report\n\n# Implementation Report\n"
    versions = [
        _version(tmp_path, bridge_id, 1, "NEW"),
        _version(tmp_path, bridge_id, 2, "GO"),
        _version(tmp_path, bridge_id, 3, "NEW"),
    ]

    proposal_content, rel_path, error = preflight._approved_proposal_for_report(
        bridge_id=bridge_id,
        report_content=report,
        versions=versions,
    )

    assert error is None, error
    assert rel_path == f"bridge/{bridge_id}-001.md"
    assert proposal_content is not None and "target_paths" in proposal_content


def test_legacy_report_shaped_artifact_is_not_resolved_as_proposal(tmp_path: Path) -> None:
    bridge_id = "legacy-report-only"
    # -001 is report-shaped (has an Approved proposal: line and no targets).
    _write_version(
        tmp_path,
        bridge_id,
        1,
        "NEW",
        "# Legacy Report\n\nApproved proposal: bridge/other-thread-001.md\n",
    )
    _write_version(tmp_path, bridge_id, 2, "GO", "bridge_kind: lo_verdict\n\n# GO\n")
    report = "bridge_kind: implementation_report\n\n# Report\n"
    versions = [
        _version(tmp_path, bridge_id, 1, "NEW"),
        _version(tmp_path, bridge_id, 2, "GO"),
        _version(tmp_path, bridge_id, 3, "NEW"),
    ]

    proposal_content, rel_path, error = preflight._approved_proposal_for_report(
        bridge_id=bridge_id,
        report_content=report,
        versions=versions,
    )

    # Report-shaped legacy artifact (no targets, has Approved proposal: line) is not resolved.
    assert error is not None
    assert proposal_content is None
