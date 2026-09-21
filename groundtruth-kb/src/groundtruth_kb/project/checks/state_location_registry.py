# © 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""Check permitted state locations without reviving retired state roots.

Registration permits ordinary state locations under the closed scan roots.
It cannot make a retired location valid. The check reads the current registry
and is discovered through the existing doctor check registry.
"""

from __future__ import annotations

import re
from pathlib import Path

from groundtruth_kb.project.checks import register_check
from groundtruth_kb.project.doctor import ToolCheck

STATE_ROOTS: tuple[str, ...] = (".claude/session", ".groundtruth")
FORBIDDEN_ROOTS: tuple[str, ...] = (
    ".gtkb-state",
    "harness-state",
    ".groundtruth/formal-artifact-approvals",
)

_REGISTRY_RELPATH = "config/registry/sot-artifacts.toml"
_STORAGE_PATH_RE = re.compile(r'^\s*storage_path\s*=\s*"([^"]+)"', re.MULTILINE)


def _registered_paths(target: Path) -> set[str]:
    """Return registered ``storage_path`` values, normalised to forward slashes.

    Parsed by regex rather than a TOML load so the check cannot be broken by an
    unrelated syntax error elsewhere in a 900KB registry: a malformed section
    should not disable state-location enforcement wholesale. Trailing slashes
    are stripped so ``.gtkb-state/`` and ``.gtkb-state`` compare equal.
    """
    registry = target / _REGISTRY_RELPATH
    try:
        text = registry.read_text(encoding="utf-8", errors="ignore")
    except OSError:
        return set()
    return {m.group(1).replace("\\", "/").rstrip("/") for m in _STORAGE_PATH_RE.finditer(text)}


def _is_permitted(rel_path: str, registered: set[str]) -> bool:
    """Permit registered ordinary paths; forbidden roots always take precedence."""
    normalized = rel_path.replace("\\", "/").strip("/").casefold()
    if any(normalized == root or normalized.startswith(root + "/") for root in FORBIDDEN_ROOTS):
        return False
    if rel_path in registered:
        return True
    parts = rel_path.split("/")
    return any("/".join(parts[:depth]) in registered for depth in range(len(parts) - 1, 0, -1))


def _scan_root(target: Path, root_name: str, registered: set[str]) -> list[str]:
    """Return unregistered state locations under one root, as repo-relative paths."""
    root = target / root_name
    if not root.is_dir():
        return []
    violations: list[str] = []
    try:
        children = sorted(root.iterdir(), key=lambda p: p.name)
    except OSError:
        return []
    for child in children:
        rel = f"{root_name}/{child.name}"
        if not _is_permitted(rel, registered):
            violations.append(rel)
    return violations


@register_check("state_location_registry")
def check_state_location_registry(target: Path) -> ToolCheck:
    """Reject forbidden roots and unregistered ordinary state locations."""
    name = "State-location default-deny (registered permitted locations)"
    forbidden = [root for root in FORBIDDEN_ROOTS if (target / root).exists() or (target / root).is_symlink()]
    if forbidden:
        return ToolCheck(
            name=name,
            required=True,
            found=True,
            status="fail",
            message="forbidden state location(s): "
            + ", ".join(forbidden)
            + ". Remove retired state locations; registry membership cannot permit them.",
        )
    registered = _registered_paths(target)
    if not registered:
        # No registry: report rather than fail. A missing registry is a
        # different defect from an unregistered location, and conflating them
        # would make this check fire loudly on a tree it cannot actually assess.
        return ToolCheck(
            name=name,
            required=True,
            found=False,
            status="warning",
            message=f"no registered storage paths found in {_REGISTRY_RELPATH}; cannot assess state locations",
        )

    violations: list[str] = []
    for root_name in STATE_ROOTS:
        violations.extend(_scan_root(target, root_name, registered))

    if not violations:
        return ToolCheck(
            name=name,
            required=True,
            found=True,
            status="pass",
            message=f"all state locations under {len(STATE_ROOTS)} scanned roots are registered",
        )

    shown = ", ".join(violations[:8]) + (" ..." if len(violations) > 8 else "")
    return ToolCheck(
        name=name,
        required=True,
        found=True,
        status="fail",
        message=(
            f"{len(violations)} unregistered state location(s): {shown}. "
            f"Register permitted locations via `gt registry register`, or remove them. "
            f"Retired state locations are always forbidden."
        ),
    )
