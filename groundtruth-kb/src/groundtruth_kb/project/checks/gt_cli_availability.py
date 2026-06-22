# (c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""Doctor check: deterministic ``gt`` CLI availability (WI-4466).

WI-4466 (P2, ``command-surface``, origin=defect). A fresh GT-KB checkout exposes
the ``gt`` CLI only as the venv console script at
``groundtruth-kb/.venv/Scripts/gt.exe`` (Windows) / ``groundtruth-kb/.venv/bin/gt``
(POSIX). When that is not on PATH, agents fall back to direct SQLite reads and the
Python entrypoint, which invites inconsistent command paths and lost operators.

This registered doctor check (ADR-REGISTRY-DISCOVERY-001) makes ``gt`` availability
machine-checkable with a deterministic three-state verdict:

- ``pass``    -- ``gt`` resolves on PATH (the optimal state).
- ``warning`` -- ``gt`` is not on PATH but the canonical in-root venv launcher
  exists, so the CLI is still deterministically available via the documented
  fallback (the WI-4530 generator / ``python -m groundtruth_kb``).
- ``fail``    -- neither on PATH nor an in-root venv launcher: the "missing CLI
  availability" condition WI-4466 requires the check to catch.

It is read-only: no PATH mutation, no launcher placement, no install/bootstrap
wiring, no subprocess launch. The venv-launcher path is resolved identically to
``scripts/install_gt_path_shim.resolve_venv_gt_exe`` so this check and the WI-4530
generator cannot drift (a test asserts that equivalence).

Governing specs: GOV-STANDING-BACKLOG-001 (WI-4466 backlog authority),
GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001 /
DCL-PROJECT-AUTHORIZATION-ENVELOPE-001 (PAUTH scope),
ADR-ISOLATION-APPLICATION-PLACEMENT-001 (in-root invariant),
ADR-REGISTRY-DISCOVERY-001 (registry extension point),
DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001 (each behaviour has a test).
"""

from __future__ import annotations

import shutil
import sys
from pathlib import Path

from groundtruth_kb.project.checks import register_check
from groundtruth_kb.project.doctor import ToolCheck

_NAME = "gt CLI availability (PATH or in-root venv fallback)"

# Windows / POSIX platform tokens, matching scripts/install_gt_path_shim.py.
_WINDOWS_PLATFORMS = frozenset({"win32"})


def _venv_gt_path(target: Path, platform: str | None = None) -> Path:
    """Return the canonical in-root venv ``gt`` launcher path for ``platform``.

    Path-pure; mirrors ``scripts/install_gt_path_shim.resolve_venv_gt_exe`` so the
    availability check and the launcher generator stay consistent. Defaults to the
    current ``sys.platform``.
    """
    plat = sys.platform if platform is None else platform
    venv = Path(target) / "groundtruth-kb" / ".venv"
    if plat in _WINDOWS_PLATFORMS:
        return venv / "Scripts" / "gt.exe"
    return venv / "bin" / "gt"


def _display_path(path: Path, target: Path) -> str:
    """Return ``path`` relative to ``target`` (posix) when possible, else absolute."""
    try:
        return path.resolve().relative_to(Path(target).resolve()).as_posix()
    except ValueError:
        return path.as_posix()


@register_check("gt_cli_availability")
def check_gt_cli_availability(target: Path) -> ToolCheck:
    """Verify a deterministic ``gt`` invocation path (PATH or in-root venv fallback)."""
    on_path = shutil.which("gt")
    if on_path:
        return ToolCheck(
            name=_NAME,
            required=False,
            found=True,
            status="pass",
            message=f"gt on PATH at {on_path}",
        )

    venv_gt = _venv_gt_path(target)
    if venv_gt.is_file():
        rel = _display_path(venv_gt, target)
        return ToolCheck(
            name=_NAME,
            required=False,
            found=True,
            status="warning",
            message=(
                f"gt not on PATH; canonical in-root venv fallback present at {rel} -- "
                "add it to PATH (generate a launcher via scripts/install_gt_path_shim.py) "
                "or invoke via that path / `python -m groundtruth_kb`"
            ),
        )

    return ToolCheck(
        name=_NAME,
        required=False,
        found=False,
        status="fail",
        message=(
            "gt CLI unavailable: not on PATH and no in-root venv fallback at "
            "groundtruth-kb/.venv -- create the project venv or generate a launcher "
            "via scripts/install_gt_path_shim.py"
        ),
    )
