"""Tests for the harness-state SoT consistency doctor check (WI-4327 / WI-4329).

Spec-derived tests for ``_check_harness_state_sot_consistency`` per the
Phase-1 Foundation proposal (bridge/gtkb-harness-state-sot-consolidation-phase-1-foundation-005.md).
The check is 3-layer:

- L1 — canonical reader entrypoints parse the 3 SoT files cleanly.
- L2 — grep_absent — no direct SoT-file reads outside the canonical
  entrypoints in committed Python code.
- L3 — grep_absent — no references to the retired
  ``harness-state/role-assignments.json`` path outside whitelisted contexts
  (bridge/, independent-progress-assessments/, archive/,
  .groundtruth/formal-artifact-approvals/, and harness_projection.py).

Severity is **warning** initially per proposal §Acceptance Criteria #8.

Copyright (c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC.
All rights reserved.
Licensed under AGPL-3.0-or-later.
"""

from __future__ import annotations

import json
from pathlib import Path

from groundtruth_kb.harness_projection import (
    HARNESS_CAPABILITIES_RELATIVE_PATH,
    HARNESS_IDENTITIES_RELATIVE_PATH,
    HARNESS_REGISTRY_RELATIVE_PATH,
)
from groundtruth_kb.project.doctor import _check_harness_state_sot_consistency


def _write_clean_sot_fixtures(root: Path) -> None:
    """Create canonical 3-SoT-file fixture set under ``root``."""
    (root / HARNESS_REGISTRY_RELATIVE_PATH).parent.mkdir(parents=True, exist_ok=True)
    (root / HARNESS_REGISTRY_RELATIVE_PATH).write_text(
        json.dumps({"schema_version": 1, "harnesses": [{"id": "B", "harness_name": "claude"}]}),
        encoding="utf-8",
    )
    (root / HARNESS_IDENTITIES_RELATIVE_PATH).write_text(
        json.dumps({"schema_version": 1, "harnesses": {"claude": {"id": "B"}}}),
        encoding="utf-8",
    )
    (root / HARNESS_CAPABILITIES_RELATIVE_PATH).parent.mkdir(parents=True, exist_ok=True)
    (root / HARNESS_CAPABILITIES_RELATIVE_PATH).write_text(
        '[[harness]]\nname = "claude"\ntype = "claude"\n',
        encoding="utf-8",
    )


def test_clean_sot_returns_pass(tmp_path: Path) -> None:
    """3-layer check: all SoT files present + clean + no direct reads = PASS."""
    _write_clean_sot_fixtures(tmp_path)
    result = _check_harness_state_sot_consistency(tmp_path)
    assert result.status == "pass"
    assert "clean" in result.message.lower()


def test_missing_registry_returns_warning(tmp_path: Path) -> None:
    """L1: missing registry SoT file surfaces as a warning."""
    # Only write 2 of 3 SoT files; registry is missing.
    (tmp_path / HARNESS_IDENTITIES_RELATIVE_PATH).parent.mkdir(parents=True, exist_ok=True)
    (tmp_path / HARNESS_IDENTITIES_RELATIVE_PATH).write_text("{}", encoding="utf-8")
    (tmp_path / HARNESS_CAPABILITIES_RELATIVE_PATH).parent.mkdir(parents=True, exist_ok=True)
    (tmp_path / HARNESS_CAPABILITIES_RELATIVE_PATH).write_text("", encoding="utf-8")

    result = _check_harness_state_sot_consistency(tmp_path)
    assert result.status == "warning"
    assert "L1" in result.message
    assert "registry" in result.message.lower()


def test_direct_sot_read_outside_entrypoint_returns_warning(tmp_path: Path) -> None:
    """L2: a Python source file that does json.load(...harness-registry.json) outside
    the canonical entrypoint surfaces as a warning.
    """
    _write_clean_sot_fixtures(tmp_path)
    # Plant an offending file under scripts/.
    scripts = tmp_path / "scripts"
    scripts.mkdir(parents=True, exist_ok=True)
    offender = scripts / "bad_direct_read.py"
    offender.write_text(
        'import json\np = "harness-state/harness-registry.json"\nwith open(p) as f:\n    data = json.load(f)\n',
        encoding="utf-8",
    )
    result = _check_harness_state_sot_consistency(tmp_path)
    assert result.status == "warning"
    assert "L2" in result.message
    assert "bad_direct_read.py" in result.message


def test_retired_path_reference_outside_whitelist_returns_warning(tmp_path: Path) -> None:
    """L3: a reference to harness-state/role-assignments.json outside the
    whitelist (bridge/, audit-archive/, formal-artifact-approval/, harness_projection.py)
    surfaces as a warning.
    """
    _write_clean_sot_fixtures(tmp_path)
    # Plant a retired-path reference in an unrelated file under scripts/.
    scripts = tmp_path / "scripts"
    scripts.mkdir(parents=True, exist_ok=True)
    offender = scripts / "uses_retired_path.py"
    offender.write_text(
        '# References the retired SoT mirror outside the whitelist.\nPATH = "harness-state/role-assignments.json"\n',
        encoding="utf-8",
    )
    result = _check_harness_state_sot_consistency(tmp_path)
    assert result.status == "warning"
    assert "L3" in result.message
    assert "uses_retired_path.py" in result.message


def test_whitelisted_retired_path_reference_does_not_trigger_warning(
    tmp_path: Path,
) -> None:
    """L3 whitelist: a retired-path reference under bridge/ MUST NOT trigger a finding
    (audit-trail / bridge-thread carrying the retired-path token is allowed).
    """
    _write_clean_sot_fixtures(tmp_path)
    # Plant a retired-path reference inside scripts/ — should warn — and ALSO
    # under bridge/ — should NOT add a finding from the whitelisted path.
    # We only verify the bridge/ path doesn't introduce an extra finding; the
    # scripts/ counterpart is covered by the previous test.
    bridge = tmp_path / "bridge"
    bridge.mkdir(parents=True, exist_ok=True)
    (bridge / "carrying-retired-path-001.md").write_text(
        "Retired path: harness-state/role-assignments.json (audit trail).\n",
        encoding="utf-8",
    )
    result = _check_harness_state_sot_consistency(tmp_path)
    # No offenders under scripts/ or other non-whitelisted roots → PASS.
    assert result.status == "pass"


def test_l2_does_not_flag_harness_projection_module(tmp_path: Path) -> None:
    """L2 whitelist: harness_projection.py itself reads the SoT files; it MUST be
    whitelisted by basename.
    """
    _write_clean_sot_fixtures(tmp_path)
    src_dir = tmp_path / "groundtruth-kb" / "src" / "groundtruth_kb"
    src_dir.mkdir(parents=True, exist_ok=True)
    # Plant a stand-in harness_projection.py that does the same kind of read
    # as the real module. The basename whitelist must prevent it from being
    # flagged.
    (src_dir / "harness_projection.py").write_text(
        'import json\np = "harness-state/harness-registry.json"\nwith open(p) as f:\n    data = json.load(f)\n',
        encoding="utf-8",
    )
    result = _check_harness_state_sot_consistency(tmp_path)
    assert result.status == "pass"
