"""Deterministic session-role resolution (DCL-SESSION-ROLE-RESOLUTION-001).

Slice 4 of PROJECT-GTKB-INTERACTIVE-SESSION-ROLE-OVERRIDE
(bridge/gtkb-interactive-session-role-override-slice-4-axis2-role-awareness-001.md,
Codex GO at -002).

This module is the SINGLE deterministic implementation of the INTERACTIVE rows
of ``DCL-SESSION-ROLE-RESOLUTION-001`` (the ``GTKB_BRIDGE_POLLER_RUN_ID``-absent
rows). The headless rows (env-var present) remain owned by the SessionStart
dispatchers and are intentionally NOT implemented here.

Consumers (Slices 4-7): the AXIS 2 surface hook, workstream-focus menu,
MemBase attribution, and the doctor checks all resolve "what role is this
interactive session operating as" through ``resolve_interactive_session_role``
so the resolution table lives in exactly one place.

Resolution (marker > durable), per the DCL interactive rows:

- marker absent / unreadable / malformed -> (durable, "durable_marker_absent")
- marker role not in {prime-builder, loyal-opposition}
                                         -> (durable, "durable_marker_invalid_role")  # assertion 7
- current_session_id given and marker session_id mismatches
                                         -> (durable, "durable_marker_stale_session")  # assertion 6
- current_session_id given and matches   -> (marker_role, "marker")
- current_session_id is None (unavailable)
                                         -> (marker_role, "marker_session_id_unverified")

The ``marker_session_id_unverified`` branch accepts the marker because Slice 3
deletes the marker at every SessionStart in both dispatchers, so a marker
present mid-session belongs to the current session. The session-id check is
defense-in-depth for the case where SessionStart invalidation silently failed.

The resolver is strictly READ-ONLY: it never writes the marker and never
mutates the durable role map. The durable fallback is composed from the
lower-level identity/role primitives with ``bootstrap_missing=False`` so no
identity-bootstrap or startup-self-correction write path is reachable.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

ROLE_PRIME = "prime-builder"
ROLE_LO = "loyal-opposition"
_VALID_ROLES = frozenset({ROLE_PRIME, ROLE_LO})

# MUST equal scripts.workstream_focus._SESSION_ROLE_MARKER_NAME (Slice 2) and
# the SessionStart dispatchers' _SESSION_ROLE_MARKER_NAME (Slice 3). A parity
# test asserts the read path equals the Slice 2 write path so the deletion /
# read target cannot drift from the write target.
_SESSION_ROLE_MARKER_NAME = "active-session-role.json"


def session_role_marker_path(project_root: Path) -> Path:
    """Return the ephemeral session-state role marker path (read target)."""
    return project_root / ".claude" / "session" / _SESSION_ROLE_MARKER_NAME


def _durable_role(project_root: Path, harness_name: str) -> str:
    """Resolve the harness's durable operating role, READ-ONLY.

    Returns ``"prime-builder"`` or ``"loyal-opposition"``. Composed from the
    lower-level primitives (``resolved_harness_id`` with
    ``bootstrap_missing=False`` + ``load_role_assignments`` + ``primary_role``)
    so no role-map or identity write path is reachable. Fail-soft: any lookup
    problem yields ``primary_role({})`` (the empty-record default).
    """
    try:
        from scripts.harness_identity import resolved_harness_id as _resolved_id
        from scripts.harness_roles import load_role_assignments, primary_role
    except ImportError:  # pragma: no cover - direct script execution path
        from harness_identity import resolved_harness_id as _resolved_id  # type: ignore[no-redef]
        from harness_roles import load_role_assignments, primary_role  # type: ignore[no-redef]

    try:
        harness_id = _resolved_id(project_root, harness_name=harness_name, bootstrap_missing=False)
        document = load_role_assignments(project_root)
        harnesses = document.get("harnesses", {}) if isinstance(document, dict) else {}
        record = harnesses.get(harness_id, {}) if harness_id else {}
        if not isinstance(record, dict):
            record = {}
        return primary_role(record)
    except Exception:  # noqa: BLE001 - a UserPromptSubmit consumer must fail soft.
        # Fall back to the empty-record default (loyal-opposition) rather than
        # raising; consumers treat the returned role as advisory surface state.
        try:
            from scripts.harness_roles import primary_role  # type: ignore[no-redef]
        except ImportError:  # pragma: no cover
            from harness_roles import primary_role  # type: ignore[no-redef]
        return primary_role({})


def _read_marker(project_root: Path) -> dict[str, Any] | None:
    """Read + JSON-parse the marker; return None when absent/unreadable/malformed."""
    marker_path = session_role_marker_path(project_root)
    try:
        raw = marker_path.read_text(encoding="utf-8")
    except (FileNotFoundError, OSError):
        return None
    try:
        body = json.loads(raw)
    except json.JSONDecodeError:
        return None
    return body if isinstance(body, dict) else None


def _read_per_session_marker(project_root: Path, session_id: str) -> dict[str, Any] | None:
    """Read the WI-4540 per-session marker keyed under ``session_id``.

    Returns the parsed body dict, or None when the per-session marker is
    absent/unreadable/malformed. The path is built by the single shared
    authority in ``scripts/gtkb_session_id.py`` so the read target cannot drift
    from the Slice-2/WI-4540 writer. Fail-soft import so a UserPromptSubmit
    consumer never raises.
    """
    try:
        from scripts.gtkb_session_id import per_session_role_marker_path
    except ImportError:  # pragma: no cover - direct script execution path
        from gtkb_session_id import per_session_role_marker_path  # type: ignore[no-redef]

    marker_path = per_session_role_marker_path(project_root, session_id)
    try:
        raw = marker_path.read_text(encoding="utf-8")
    except (FileNotFoundError, OSError):
        return None
    try:
        body = json.loads(raw)
    except json.JSONDecodeError:
        return None
    return body if isinstance(body, dict) else None


def resolve_interactive_session_role(
    project_root: Path,
    *,
    current_session_id: str | None = None,
    harness_name: str = "claude",
) -> tuple[str, str]:
    """Return ``(role_profile, source)`` for an interactive session.

    ``role_profile`` is in ``{prime-builder, loyal-opposition}``. ``source`` is
    one of ``marker``, ``marker_session_id_unverified``, ``durable_marker_absent``,
    ``durable_marker_invalid_role``, ``durable_marker_stale_session``. See the
    module docstring for the deterministic resolution table.

    READ-ONLY: never writes the marker or the durable role map. Callers SHOULD
    pass the RAW UserPromptSubmit payload ``session_id`` (not a sanitized cache
    key) as ``current_session_id`` so the comparison is like-for-like with the
    Slice 2 writer's stored raw id.
    """
    durable = _durable_role(project_root, harness_name)

    # WI-4663: Load per-harness session envelope and prefer its role_resolved
    # over the registry durable role if the envelope is status="open".
    envelope_path = project_root / "harness-state" / harness_name / "session-envelope.json"
    envelope_role = None
    if envelope_path.is_file():
        try:
            envelope_data = json.loads(envelope_path.read_text(encoding="utf-8"))
            if isinstance(envelope_data, dict) and envelope_data.get("status") == "open":
                role_resolved = envelope_data.get("role_resolved")
                if role_resolved in _VALID_ROLES:
                    envelope_role = role_resolved
        except Exception:
            pass

    fallback = envelope_role if envelope_role is not None else durable

    # WI-4540 (bridge -004, R-B1 + additive transition): the per-session marker
    # is the authority. When a current_session_id is available, prefer the
    # per-session marker keyed under it; it survives a SessionStart that carries
    # a different context id (no shared single-file slot to clobber). When no
    # per-session marker exists, fall back to the legacy single-file marker for
    # the additive transition window (existing resolver behavior, unchanged).
    if current_session_id is not None:
        per_session = _read_per_session_marker(project_root, current_session_id)
        if per_session is not None:
            role = per_session.get("role")
            if role not in _VALID_ROLES:  # assertion 7
                return fallback, "durable_marker_invalid_role"
            marker_session_id = per_session.get("session_id")
            if not (isinstance(marker_session_id, str) and marker_session_id == current_session_id):
                return fallback, "durable_marker_stale_session"  # assertion 6
            return role, "marker"

    body = _read_marker(project_root)
    if body is None:
        return fallback, "durable_marker_absent"

    role = body.get("role")
    if role not in _VALID_ROLES:  # assertion 7
        return fallback, "durable_marker_invalid_role"

    if current_session_id is not None:
        marker_session_id = body.get("session_id")
        if not (isinstance(marker_session_id, str) and marker_session_id == current_session_id):
            return fallback, "durable_marker_stale_session"  # assertion 6
        return role, "marker"

    # current_session_id unavailable: accept the marker. Slice 3 deletes the
    # marker at every SessionStart, so a present marker belongs to this session.
    return role, "marker_session_id_unverified"
