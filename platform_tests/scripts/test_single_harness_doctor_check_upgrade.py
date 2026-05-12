# (c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""Doctor check upgrade tests for IP-4 of
bridge/gtkb-single-harness-bridge-dispatcher-slice-2-005.md (Codex GO at -006).

Spec: DCL-SINGLE-HARNESS-DISPATCHER-DESKTOP-TASK-001 v1 § Doctor Check.

Key contract:
- Status is WARN (not FAIL) for any "applicable but not fully healthy" case.
- Status is PASS for "applicable + script + task registered + last-run-time fresh".
- Status is PASS for "not applicable" (multi-harness topology).
- On non-Windows host with applicability: WARN with platform-extension pointer.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT / "groundtruth-kb" / "src") not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT / "groundtruth-kb" / "src"))


def _make_synthetic_project(root: Path, single_harness: bool = False) -> Path:
    """Create a minimal synthetic GT-KB project with the requested topology."""
    (root / "harness-state").mkdir(parents=True, exist_ok=True)
    (root / "harness-state" / "harness-identities.json").write_text(
        json.dumps(
            {"schema_version": 1, "harnesses": {"claude": {"id": "B"}, "codex": {"id": "A"}}}
        ),
        encoding="utf-8",
    )
    if single_harness:
        (root / "harness-state" / "role-assignments.json").write_text(
            json.dumps(
                {
                    "schema_version": 1,
                    "harnesses": {
                        "B": {"role": ["prime-builder", "loyal-opposition"], "harness_type": "claude"}
                    },
                }
            ),
            encoding="utf-8",
        )
    else:
        (root / "harness-state" / "role-assignments.json").write_text(
            json.dumps(
                {
                    "schema_version": 1,
                    "harnesses": {
                        "B": {"role": ["prime-builder"], "harness_type": "claude"},
                        "A": {"role": ["loyal-opposition"], "harness_type": "codex"},
                    },
                }
            ),
            encoding="utf-8",
        )
    return root


# ──────────────────────────────────────────────────────────────────────────
# T-SHD-S2-doctor-pass-not-applicable (carry-forward from Slice 1)
# ──────────────────────────────────────────────────────────────────────────


def test_doctor_pass_not_applicable_in_multi_harness(tmp_path: Path) -> None:
    """Multi-harness topology -> PASS with 'not applicable'."""
    from groundtruth_kb.project.doctor import _check_single_harness_dispatcher_when_required

    _make_synthetic_project(tmp_path, single_harness=False)
    check = _check_single_harness_dispatcher_when_required(tmp_path)
    assert check.status == "pass"
    assert "not applicable" in check.message


# ──────────────────────────────────────────────────────────────────────────
# T-SHD-S2-doctor-missing-task-WARN (F4 closure)
# ──────────────────────────────────────────────────────────────────────────


def test_doctor_warns_when_applicable_and_script_present_but_task_missing(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """DCL-SINGLE-HARNESS-DISPATCHER-DESKTOP-TASK-001 § Doctor Check: WARN
    (NOT FAIL) when applicable + script present but task missing.

    Per F4 of bridge/gtkb-single-harness-bridge-dispatcher-slice-2-002.md
    closure: severity matches DCL exactly (WARN, not FAIL).
    """
    from groundtruth_kb.project import doctor as doctor_mod

    _check_single_harness_dispatcher_when_required = (
        doctor_mod._check_single_harness_dispatcher_when_required
    )

    _make_synthetic_project(tmp_path, single_harness=True)
    # Place the dispatcher script at the expected location to satisfy the
    # "script present" precondition.
    scripts_dir = tmp_path / "scripts"
    scripts_dir.mkdir(parents=True, exist_ok=True)
    (scripts_dir / "single_harness_bridge_dispatcher.py").write_text(
        "# stub for doctor-check test", encoding="utf-8"
    )

    # On Windows, the doctor probes Get-ScheduledTask for the task; if the
    # task is not registered, expect WARN with 'not registered'. Simulate that
    # branch so the test stays hermetic even on a workstation where the
    # production scheduled task is installed.
    # On non-Windows, expect WARN with the platform-extension pointer.
    if sys.platform == "win32":
        def _fake_run(*args, **kwargs):
            return doctor_mod.subprocess.CompletedProcess(
                args[0], 0, stdout="NOT_REGISTERED\n", stderr=""
            )

        monkeypatch.setattr(doctor_mod.subprocess, "run", _fake_run)

    check = _check_single_harness_dispatcher_when_required(tmp_path)

    assert check.status == "warning", f"Expected WARN (not {check.status}) per F4 / DCL"
    if sys.platform == "win32":
        assert "not registered" in check.message.lower() or "absent" in check.message.lower()
    else:
        assert "windows" in check.message.lower() or "decision deferred" in check.message.lower()


# ──────────────────────────────────────────────────────────────────────────
# T-SHD-S2-doctor-script-missing-WARN
# ──────────────────────────────────────────────────────────────────────────


def test_doctor_warns_when_applicable_but_script_missing(tmp_path: Path) -> None:
    """Applicable + script missing -> WARN (script-missing branch; pre-Slice-2 baseline)."""
    from groundtruth_kb.project.doctor import _check_single_harness_dispatcher_when_required

    _make_synthetic_project(tmp_path, single_harness=True)
    # Intentionally do NOT create the dispatcher script.

    check = _check_single_harness_dispatcher_when_required(tmp_path)
    assert check.status == "warning"
    assert "single_harness_bridge_dispatcher.py is absent" in check.message


# ──────────────────────────────────────────────────────────────────────────
# T-SHD-S2-doctor-non-windows-warn
# ──────────────────────────────────────────────────────────────────────────


def test_doctor_warn_when_non_windows_host_applicable(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """On non-Windows host with applicable topology + script present -> WARN
    with platform-extension pointer (Slice 2 ships Windows-only)."""
    from groundtruth_kb.project import doctor as doctor_mod

    _make_synthetic_project(tmp_path, single_harness=True)
    scripts_dir = tmp_path / "scripts"
    scripts_dir.mkdir(parents=True, exist_ok=True)
    (scripts_dir / "single_harness_bridge_dispatcher.py").write_text(
        "# stub", encoding="utf-8"
    )

    monkeypatch.setattr(doctor_mod.sys, "platform", "linux")

    check = doctor_mod._check_single_harness_dispatcher_when_required(tmp_path)
    assert check.status == "warning"
    assert "windows-only" in check.message.lower() or "decision deferred" in check.message.lower()


# ──────────────────────────────────────────────────────────────────────────
# T-SHD-S2-doctor-role-map-missing
# ──────────────────────────────────────────────────────────────────────────


def test_doctor_warns_when_role_map_missing(tmp_path: Path) -> None:
    """No role-assignments.json -> WARN (applicability undeterminable)."""
    from groundtruth_kb.project.doctor import _check_single_harness_dispatcher_when_required

    check = _check_single_harness_dispatcher_when_required(tmp_path)
    assert check.status == "warning"
    assert "missing" in check.message.lower()
