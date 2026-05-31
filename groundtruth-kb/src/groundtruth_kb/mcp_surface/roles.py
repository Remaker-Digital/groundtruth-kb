"""Role-aware dispatch for the GT-KB MCP surface.

Reads the harness registry hot-path projection
``harness-state/harness-registry.json`` to determine the operating role of the
active harness (WI-3342 IP-4: migrated from the legacy
``harness-state/role-assignments.json`` / ``harness-state/harness-identities.json``). Per
``bridge/gtkb-role-session-lifecycle-simplification-003.md`` (REVISED-1 GO at
-004), the canonical role set is ``prime-builder`` and ``loyal-opposition``;
``acting-prime-builder`` is READ-accepted as compatibility/provenance but is
not a SET target.

Slice 1 uses role-awareness for response labelling only. Slice 4 introduces
mutation-class tools that are gated on role.
"""

from __future__ import annotations

import json
import os
from pathlib import Path

from groundtruth_kb.mcp_surface.boundary import resolve_safe_path

CANONICAL_ROLES: frozenset[str] = frozenset({"prime-builder", "loyal-opposition"})
COMPATIBILITY_ROLES: frozenset[str] = frozenset({"acting-prime-builder"})

# WI-3342 IP-4: role and identity state both resolve from the DB-backed harness
# registry projection. The legacy harness-state/role-assignments.json and
# harness-state/harness-identities.json are no longer read in this module.
_HARNESS_REGISTRY_REL = Path("harness-state/harness-registry.json")


def _detect_active_harness_name() -> str | None:
    """Detect which harness is hosting the current Python process.

    Returns the harness-identities.json key (e.g. ``"claude"``, ``"codex"``)
    based on environment-variable presence. Returns ``None`` when no
    recognised harness can be detected (callers handle as fail-closed).
    """

    if os.environ.get("CLAUDE_PROJECT_DIR") or any(name.startswith("CLAUDE_CODE") for name in os.environ):
        return "claude"
    if any(name.startswith("CODEX_") for name in os.environ):
        return "codex"
    return None


def _default_harness_id() -> str:
    """Resolve the active harness ID for the current process.

    Order:
      1. ``GTKB_HARNESS_ID`` env var (explicit override; mandatory for
         deterministic test contexts).
      2. Environment-variable harness detection (``CLAUDE_PROJECT_DIR`` or
         any ``CLAUDE_CODE*`` var indicates the Claude harness; any
         ``CODEX_*`` var indicates the Codex harness) mapped to the durable
         ID via the harness registry projection.
      3. Empty string -- fail-closed. Callers consult ``current_role`` which
         returns ``"unknown"`` for an empty/unmapped ID rather than
         silently mis-attributing the role to another harness.

    Note: this function never hardcodes a specific harness ID as a fallback.
    Hardcoding (e.g. always returning ``"B"``) was a known defect in the
    Slice 1 NEW post-impl per Codex NO-GO at
    ``bridge/gtkb-mcp-stable-harness-surface-conversion-006.md`` F2.
    """

    explicit = os.environ.get("GTKB_HARNESS_ID")
    if explicit:
        return explicit

    harness_name = _detect_active_harness_name()
    if harness_name is None:
        return ""

    try:
        registry_path = resolve_safe_path(_HARNESS_REGISTRY_REL)
        data = json.loads(registry_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return ""

    for record in data.get("harnesses", []):
        if isinstance(record, dict) and record.get("harness_name") == harness_name:
            harness_id = record.get("id")
            return str(harness_id) if isinstance(harness_id, str) and harness_id else ""
    return ""


def _canonical_role(role_field: object) -> str:
    """Normalize a registry-projection ``role`` field to one scalar role token.

    The registry projection stores ``role`` as the list-valued role-set wire
    form -- ``["prime-builder"]`` / ``["loyal-opposition"]`` (singleton, the
    multi-harness norm) or ``["prime-builder", "loyal-opposition"]`` (the
    single-harness operating mode per ``ADR-SINGLE-HARNESS-OPERATING-MODE-001``).
    The MCP ``current_role`` status surface contract is a single canonical
    scalar, so this helper collapses the role-set to one token:

    - singleton list -> its sole element;
    - multi-element list -> the deterministic primary role: ``prime-builder``
      if present, else ``loyal-opposition``, else the first element;
    - legacy scalar ``str`` (e.g. ``acting-prime-builder``) -> returned
      verbatim, preserving the Acting-Prime Compatibility Contract;
    - empty list or any other shape -> ``"unknown"`` (fail-soft; never raises).

    NOTE: the returned value is a *scalar primary role* for display and
    labelling only. It is NOT a substitute for full role-set authority.
    Routing and topology code that needs the complete role set -- e.g.
    detecting the single-harness ``shared`` slot -- must use the role-set
    membership and role-slot helpers (such as
    ``groundtruth_kb.mode_switch.derive.role_slot_from_active_harness``), not
    this scalar.
    """

    # Legacy scalar wire form: returned verbatim.
    if isinstance(role_field, str):
        return role_field
    # List wire form: the role-set. Collapse to one scalar token.
    if isinstance(role_field, list) and role_field:
        if len(role_field) == 1:
            # Singleton role-set (multi-harness norm): the sole element.
            return str(role_field[0])
        # Multi-element role-set (single-harness operating mode): the
        # deterministic primary role.
        if "prime-builder" in role_field:
            return "prime-builder"
        if "loyal-opposition" in role_field:
            return "loyal-opposition"
        return str(role_field[0])
    # Empty list or any other shape: fail-soft.
    return "unknown"


def current_role(
    *,
    harness_id: str | None = None,
    role_map_path: Path | None = None,
) -> str:
    """Return the operating role for the active (or named) harness.

    The registry projection stores ``role`` as the list-valued role-set wire
    form; the return value is normalized to one canonical scalar role token by
    ``_canonical_role`` (singleton role-set -> its element; multi-element
    single-harness role-set -> the deterministic primary role; legacy scalar
    -> verbatim; empty/malformed -> ``"unknown"``). Both canonical roles
    (``prime-builder``, ``loyal-opposition``) and the compatibility/provenance
    value (``acting-prime-builder``) are accepted on READ; this function does
    not raise on unrecognised roles.

    The returned scalar is a *primary role* for display and labelling. It is
    NOT full role-set authority: routing and topology code that must detect
    the single-harness ``shared`` slot uses the role-set membership / role-slot
    helpers, not this scalar.
    """

    if harness_id is None:
        harness_id = _default_harness_id()
    role_map_path = resolve_safe_path(_HARNESS_REGISTRY_REL) if role_map_path is None else Path(role_map_path)
    data = json.loads(role_map_path.read_text(encoding="utf-8"))
    for record in data.get("harnesses", []):
        if isinstance(record, dict) and record.get("id") == harness_id:
            return _canonical_role(record.get("role", "unknown"))
    return "unknown"
