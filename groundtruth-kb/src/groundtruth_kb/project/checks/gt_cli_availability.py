# (c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""Doctor check: deterministic ``gt`` CLI availability (WI-4466/WI-4954).

WI-4466 (P2, ``command-surface``, origin=defect). A fresh GT-KB checkout exposes
the ``gt`` CLI only as the venv console script at
``groundtruth-kb/.venv/Scripts/gt.exe`` (Windows) / ``groundtruth-kb/.venv/bin/gt``
(POSIX). When that is not on PATH, agents fall back to direct SQLite reads and the
Python entrypoint, which invites inconsistent command paths and lost operators.

This registered doctor check (ADR-REGISTRY-DISCOVERY-001) makes ``gt`` availability
machine-checkable with a deterministic three-state verdict:

- ``pass``    -- ``gt`` resolves on PATH and, when it is a generated GT-KB shim,
  its structural targets are present.
- ``warning`` -- ``gt`` is not on PATH but the canonical source-tree module
  fallback exists, so the CLI is still deterministically available via the
  documented venv-Python + ``PYTHONPATH`` invocation.
- ``fail``    -- neither on PATH nor an in-root venv launcher: the "missing CLI
  availability" condition WI-4466 requires the check to catch; or a generated
  PATH shim is stale/broken and points at a missing launcher target.

It is read-only: no PATH mutation, no launcher placement, no install/bootstrap
wiring, no subprocess launch. The source-tree module fallback paths are resolved
identically to ``scripts/install_gt_path_shim.resolve_venv_python_exe`` and
``resolve_source_tree`` so this check and the WI-4530/WI-4954 generator cannot
drift (tests assert that equivalence).

Governing specs: GOV-STANDING-BACKLOG-001 (WI-4466 backlog authority),
GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001 /
DCL-PROJECT-AUTHORIZATION-ENVELOPE-001 (PAUTH scope),
ADR-ISOLATION-APPLICATION-PLACEMENT-001 (in-root invariant),
ADR-REGISTRY-DISCOVERY-001 (registry extension point),
DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001 (each behaviour has a test).
"""

from __future__ import annotations

import re
import shutil
import sys
from pathlib import Path

from groundtruth_kb.project.checks import register_check
from groundtruth_kb.project.doctor import ToolCheck

_NAME = "gt CLI availability (PATH shim or source-tree module fallback)"

# Windows / POSIX platform tokens, matching scripts/install_gt_path_shim.py.
_WINDOWS_PLATFORMS = frozenset({"win32"})
_MAX_SHIM_INSPECTION_BYTES = 64 * 1024
_GENERATED_SHIM_MARKER = "scripts/install_gt_path_shim.py"
_MODULE_ENTRYPOINT_MARKER = "groundtruth_kb.cli"
_QUOTED_PATH_RE = re.compile(r'"([^"]+)"|exec\s+(\S+)\s+-m\s+groundtruth_kb\.cli')


def _normalize_path_text(value: str | Path) -> str:
    """Normalize a path-ish string for substring checks across slash styles."""
    return str(value).replace("\\", "/").lower()


def _venv_gt_path(target: Path, platform: str | None = None) -> Path:
    """Return the legacy in-root venv ``gt`` launcher path for ``platform``.

    Path-pure; retained to identify stale WI-4530 PATH shims. Defaults to the
    current ``sys.platform``.
    """
    plat = sys.platform if platform is None else platform
    venv = Path(target) / "groundtruth-kb" / ".venv"
    if plat in _WINDOWS_PLATFORMS:
        return venv / "Scripts" / "gt.exe"
    return venv / "bin" / "gt"


def _venv_python_path(target: Path, platform: str | None = None) -> Path:
    """Return the canonical in-root venv Python path for ``platform``."""
    plat = sys.platform if platform is None else platform
    venv = Path(target) / "groundtruth-kb" / ".venv"
    if plat in _WINDOWS_PLATFORMS:
        return venv / "Scripts" / "python.exe"
    return venv / "bin" / "python"


def _source_tree_path(target: Path) -> Path:
    """Return the in-root source-tree import path for ``groundtruth_kb``."""
    return Path(target) / "groundtruth-kb" / "src"


def _display_path(path: Path, target: Path) -> str:
    """Return ``path`` relative to ``target`` (posix) when possible, else absolute."""
    try:
        return path.resolve().relative_to(Path(target).resolve()).as_posix()
    except ValueError:
        return path.as_posix()


def _read_generated_shim(path: Path) -> str | None:
    """Return bounded generated-shim text when ``path`` looks inspectable."""
    try:
        if not path.is_file() or path.stat().st_size > _MAX_SHIM_INSPECTION_BYTES:
            return None
        text = path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return None
    return text if _GENERATED_SHIM_MARKER in text else None


def _quoted_paths(text: str) -> list[Path]:
    """Extract command targets from generated shim text for stale-target checks."""
    paths: list[Path] = []
    for match in _QUOTED_PATH_RE.finditer(text):
        raw = next((group for group in match.groups() if group), None)
        if raw:
            paths.append(Path(raw.strip("'\"")))
    return paths


def _looks_like_legacy_venv_gt(path: Path) -> bool:
    """Return true for a quoted target that resembles the obsolete venv ``gt``."""
    normalized = _normalize_path_text(path)
    return "/groundtruth-kb/.venv/" in normalized and normalized.endswith(("/gt.exe", "/gt"))


def _inspect_generated_shim(on_path: Path, target: Path, text: str) -> ToolCheck:
    """Validate a generated GT-KB shim without executing arbitrary PATH code."""
    expected_python = _venv_python_path(target)
    expected_source = _source_tree_path(target)
    normalized_text = _normalize_path_text(text)
    expected_python_text = _normalize_path_text(expected_python)
    expected_source_text = _normalize_path_text(expected_source)

    if _MODULE_ENTRYPOINT_MARKER in text:
        missing: list[str] = []
        if not expected_python.is_file():
            missing.append(_display_path(expected_python, target))
        if not expected_source.is_dir():
            missing.append(_display_path(expected_source, target))
        if missing:
            return ToolCheck(
                name=_NAME,
                required=False,
                found=False,
                status="fail",
                message=f"gt PATH shim at {on_path} is generated but target(s) are missing: {', '.join(missing)}",
            )
        if expected_python_text not in normalized_text or expected_source_text not in normalized_text:
            return ToolCheck(
                name=_NAME,
                required=False,
                found=True,
                status="warning",
                message=(
                    f"gt PATH shim at {on_path} is generated but does not target this checkout's "
                    "venv Python/source tree; regenerate via scripts/install_gt_path_shim.py"
                ),
            )
        return ToolCheck(
            name=_NAME,
            required=False,
            found=True,
            status="pass",
            message=f"gt on PATH at {on_path}; generated source-tree module shim targets are present",
        )

    legacy_targets = [path for path in _quoted_paths(text) if _looks_like_legacy_venv_gt(path)]
    if legacy_targets:
        missing = [path for path in legacy_targets if not path.is_file()]
        if missing:
            rendered = ", ".join(str(path) for path in missing)
            return ToolCheck(
                name=_NAME,
                required=False,
                found=False,
                status="fail",
                message=f"gt PATH shim at {on_path} points at missing legacy venv console script(s): {rendered}",
            )
        return ToolCheck(
            name=_NAME,
            required=False,
            found=True,
            status="pass",
            message=f"gt on PATH at {on_path}; generated legacy venv console-script target exists",
        )

    return ToolCheck(
        name=_NAME,
        required=False,
        found=True,
        status="warning",
        message=f"gt PATH shim at {on_path} is generated but its launcher target shape is unrecognized",
    )


@register_check("gt_cli_availability")
def check_gt_cli_availability(target: Path) -> ToolCheck:
    """Verify a deterministic ``gt`` invocation path (PATH or in-root venv fallback)."""
    on_path = shutil.which("gt")
    if on_path:
        path = Path(on_path)
        generated = _read_generated_shim(path)
        if generated is not None:
            return _inspect_generated_shim(path, target, generated)
        return ToolCheck(
            name=_NAME,
            required=False,
            found=True,
            status="pass",
            message=f"gt on PATH at {on_path} (not a generated GT-KB shim; structural inspection skipped)",
        )

    venv_python = _venv_python_path(target)
    source_tree = _source_tree_path(target)
    if venv_python.is_file() and source_tree.is_dir():
        python_rel = _display_path(venv_python, target)
        source_rel = _display_path(source_tree, target)
        return ToolCheck(
            name=_NAME,
            required=False,
            found=True,
            status="warning",
            message=(
                f"gt not on PATH; source-tree module fallback present via {python_rel} "
                f"with PYTHONPATH={source_rel} -- generate a launcher via scripts/install_gt_path_shim.py"
            ),
        )

    return ToolCheck(
        name=_NAME,
        required=False,
        found=False,
        status="fail",
        message=(
            "gt CLI unavailable: not on PATH and no in-root venv-Python/source fallback at "
            "groundtruth-kb/.venv plus groundtruth-kb/src -- create the project venv or generate a launcher "
            "via scripts/install_gt_path_shim.py"
        ),
    )
