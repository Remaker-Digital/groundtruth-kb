"""Role-aware dispatch for the GT-KB MCP surface.

Reads ``harness-state/role-assignments.json`` to determine the operating role
of the active harness. Per
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

_DEFAULT_ROLE_MAP_REL = Path("harness-state/role-assignments.json")


_HARNESS_IDENTITIES_REL = Path("harness-state/harness-identities.json")


def _detect_active_harness_name() -> str | None:
    """Detect which harness is hosting the current Python process.

    Returns the harness-identities.json key (e.g. ``"claude"``, ``"codex"``)
    based on environment-variable presence. Returns ``None`` when no
    recognised harness can be detected (callers handle as fail-closed).
    """

    if os.environ.get("CLAUDE_PROJECT_DIR") or any(
        name.startswith("CLAUDE_CODE") for name in os.environ
    ):
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
         ID via ``harness-state/harness-identities.json``.
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
        identities_path = resolve_safe_path(_HARNESS_IDENTITIES_REL)
        data = json.loads(identities_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return ""

    entry = data.get("harnesses", {}).get(harness_name) or {}
    harness_id = entry.get("id")
    return str(harness_id) if isinstance(harness_id, str) and harness_id else ""


def current_role(
    *,
    harness_id: str | None = None,
    role_map_path: Path | None = None,
) -> str:
    """Return the operating role for the active (or named) harness.

    Both canonical roles (``prime-builder``, ``loyal-opposition``) and the
    compatibility/provenance value (``acting-prime-builder``) are accepted on
    READ. Unknown values are returned verbatim so callers can decide their
    own disposition; this function does not raise on unrecognised roles.
    """

    if harness_id is None:
        harness_id = _default_harness_id()
    if role_map_path is None:
        role_map_path = resolve_safe_path(_DEFAULT_ROLE_MAP_REL)
    else:
        role_map_path = Path(role_map_path)
    data = json.loads(role_map_path.read_text(encoding="utf-8"))
    harnesses = data.get("harnesses", {})
    entry = harnesses.get(harness_id) or {}
    return str(entry.get("role", "unknown"))
