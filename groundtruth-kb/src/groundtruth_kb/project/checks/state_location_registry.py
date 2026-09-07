# © 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""Default-deny state locations (WI-6739, ADR-REGISTRY-DISCOVERY-001).

GT-KB stores state in exactly two places: defined source of truth, and
per-harness configuration (``DELIB-20260821032900``). Nothing enumerated where
state was permitted to live, and no gate objected when a new state location
appeared. Every session object purged under WI-6738 was a new state location
that no mechanism questioned at creation.

This check converts that one-sentence policy into a mechanical gate: any state
directory *or state file* under a scanned root that matches no registered
permitted location is a violation.

Design decisions, each traceable to a recorded owner decision rather than
inferred here:

* **Permitted locations extend the existing SoT registry.** ``DELIB-20260821053502``
  superseded the original plan for a separate ``state-locations.toml``. The
  earlier rationale -- that the SoT registry was "scoped to SoT artifacts, not
  state paths" -- was false: it already registers ``.gtkb-state/``,
  ``.claude/session/``, ``harness-state/harness-registry.json`` and others.

* **Files count, not only directories.** Owner decision, 2026-08-21.
  ``.claude/session`` holds zero directories and a dozen-plus loose files, and
  those files *are* the remaining session-object population. A directories-only
  rule is not a narrower rule; it is blind to an entire state root.

* **Classification is by longest-prefix match on the path, never by parent
  directory.** ``harness-state/`` legitimately contains per-harness
  configuration (``harness-registry.json``, ``harness-identities.json``,
  ``active-workspace.md``) *and* illegitimate per-harness session state
  (``session-envelope-archive/``, ``session-lifecycle-guard.json``). A
  parent-directory rule cannot separate them; longest-prefix can.

The check reads the registry at run time and never caches it
(``GOV-SOURCE-OF-TRUTH-FRESHNESS-001``). ``doctor.py`` requires no edit: this
module is discovered by ``pkgutil`` through ``project.checks.__init__``.
"""

from __future__ import annotations

import re
from pathlib import Path

from groundtruth_kb.project.checks import register_check
from groundtruth_kb.project.doctor import ToolCheck

#: Closed set of state roots. Deliberately not a whole-tree walk: these are the
#: trees that hold runtime state, and scanning everything would classify source
#: directories as state.
STATE_ROOTS: tuple[str, ...] = (
    ".gtkb-state",
    "harness-state",
    ".claude/session",
    ".groundtruth",
)

#: Roots scanned one level deeper, because their real state lives per-harness.
#: ``harness-state/<harness>/session-envelope-archive`` is invisible at depth 1.
DEEP_ROOTS: frozenset[str] = frozenset({"harness-state"})

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
    """Longest-prefix match: a path is permitted if it or an ancestor is registered.

    Ancestor matching is what makes a registered container meaningful -- a
    registered ``.groundtruth/formal-artifact-approvals/`` should permit the
    files inside it. It is also the reason a blanket ``opaque_container``
    registration on a whole state root defeats this check, which is why WI-6739
    narrows those rows as part of the same work.
    """
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
        if child.is_dir() and root_name in DEEP_ROOTS:
            # Descend one level: the per-harness layer is where state hides.
            try:
                grandchildren = sorted(child.iterdir(), key=lambda p: p.name)
            except OSError:
                continue
            for grandchild in grandchildren:
                deep_rel = f"{rel}/{grandchild.name}"
                if not _is_permitted(deep_rel, registered):
                    violations.append(deep_rel)
            continue
        if not _is_permitted(rel, registered):
            violations.append(rel)
    return violations


@register_check("state_location_registry")
def check_state_location_registry(target: Path) -> ToolCheck:
    """Fail when a state location is not registered as permitted.

    Required check: an unregistered state location is the mechanism by which the
    session-object model accreted, and a warning would leave that mechanism
    intact. Both unregistered directories and unregistered loose files are
    violations, per the owner's granularity decision.
    """
    name = "State-location default-deny (registered permitted locations)"
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
            f"GT-KB stores state only in defined SoT and per-harness configuration."
        ),
    )
