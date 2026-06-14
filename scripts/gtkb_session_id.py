#!/usr/bin/env python3
"""Shared session-id env-var membership + per-surface resolution order.

Single membership authority for the session-id environment variables resolved
across GroundTruth-KB bridge and session-marker surfaces, plus the two
deliberate per-surface precedence orders and one stdlib-only resolver.

Background. The session-id env-var list was hand-maintained in two families
that each disagreed internally. The original Claude Code defect
(``bridge/gtkb-claude-code-session-id-env-var-gap``; minimal fix committed
``ea2040a5``, VERIFIED at ``-012``) was a MEMBERSHIP omission
(``CLAUDE_CODE_SESSION_ID``) in the bridge family -- not an ordering problem.
This module centralizes membership in one frozen SET so it can no longer
silently drift again (the recurrence guard), while preserving each family's
deliberate precedence.

Two intentional precedence policies:

- ``BRIDGE_WORK_INTENT_ORDER`` (dispatch-run-first): the bridge work-intent
  surfaces -- ``scripts/bridge_claim_cli.py``,
  ``.claude/hooks/bridge-compliance-gate.py``,
  ``.claude/hooks/bridge-axis-2-surface.py``, and the
  ``bridge-propose`` ``write_bridge`` helper. Headless bridge dispatch workers
  resolve ``GTKB_BRIDGE_POLLER_RUN_ID`` before any ambient parent harness
  session; remaining order preserves the live-Claude-Code-first behavior. A
  full permutation of ``SESSION_ID_ENV_VARS``.
- ``MARKER_CONTINUITY_ORDER`` (``GTKB_SESSION_ID``-first): the session-role
  marker surfaces -- ``scripts/workstream_focus.py`` (marker writer) and
  ``groundtruth-kb/src/groundtruth_kb/project/doctor.py`` (doctor marker
  resolver) -- so an inherited/dispatched GT-KB session id wins over ambient
  harness env. A documented SUBSET of ``SESSION_ID_ENV_VARS`` (intentionally
  excludes ``GTKB_BRIDGE_POLLER_RUN_ID``, ``GTKB_INHERITED_SESSION_ID`` and
  ``ANTIGRAVITY_SESSION_ID`` to preserve the current marker-continuity
  behavior).

Hook-safe contract: stdlib-only, no third-party or repo-internal imports and no
import-time side effects, so PreToolUse/UserPromptSubmit hooks can import this
module on every invocation without a heavy dependency surface.

Authority: WI-4270; PROJECT-GTKB-BRIDGE-PROTOCOL-RELIABILITY;
``bridge/gtkb-session-id-shared-resolver-unification-003.md`` (Codex GO at
``-004``); ``DELIB-20260625``; ``DELIB-S312-DETERMINISTIC-SERVICES-PRINCIPLE``.

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

from __future__ import annotations

import os
import re
from collections.abc import Iterable, Mapping
from pathlib import Path

# Canonical membership SET: the union of every session-id env var any GT-KB
# surface resolves. Frozen so a caller cannot mutate the authority in place.
# The two order constants below are checked against this set by the drift-lock
# test (platform_tests/scripts/test_gtkb_session_id.py) so membership can never
# silently diverge again -- the recurrence guard for the ea2040a5 defect class.
SESSION_ID_ENV_VARS: frozenset[str] = frozenset(
    {
        "CLAUDE_SESSION_ID",
        "CLAUDE_CODE_SESSION_ID",
        "GTKB_BRIDGE_POLLER_RUN_ID",
        "GTKB_INHERITED_SESSION_ID",
        "CODEX_SESSION_ID",
        "CODEX_THREAD_ID",
        "ANTIGRAVITY_SESSION_ID",
        "GTKB_SESSION_ID",
    }
)

# Bridge work-intent surfaces: headless dispatch run id first so parent harness
# session ids cannot override a spawned worker's bridge work-intent identity.
# Live Claude Code remains ahead of stale legacy CLAUDE_SESSION_ID for ordinary
# interactive bridge writes. A full permutation of SESSION_ID_ENV_VARS
# (drift-lock T2).
BRIDGE_WORK_INTENT_ORDER: tuple[str, ...] = (
    "GTKB_BRIDGE_POLLER_RUN_ID",
    "CLAUDE_CODE_SESSION_ID",
    "CLAUDE_SESSION_ID",
    "GTKB_INHERITED_SESSION_ID",
    "CODEX_SESSION_ID",
    "CODEX_THREAD_ID",
    "ANTIGRAVITY_SESSION_ID",
    "GTKB_SESSION_ID",
)

# Session-role marker surfaces: GTKB_SESSION_ID-first so an inherited/dispatched
# GT-KB session id wins over ambient harness env. A documented SUBSET of
# SESSION_ID_ENV_VARS (drift-lock T2).
MARKER_CONTINUITY_ORDER: tuple[str, ...] = (
    "GTKB_SESSION_ID",
    "CODEX_SESSION_ID",
    "CODEX_THREAD_ID",
    "CLAUDE_SESSION_ID",
    "CLAUDE_CODE_SESSION_ID",
)


# ---------------------------------------------------------------------------
# WI-4540: per-session/per-context session-role marker path authority.
#
# bridge/gtkb-wi4540-per-session-role-marker-context-envelope-003.md (GO at
# -004; R-B1 + additive transition). The single-file marker
# ``.claude/session/active-session-role.json`` is a shared slot across all
# concurrent sessions on a workstation, which produced cross-session clobber
# (WI-4463) and mid-context vanish (advisory Defect 2). The fix keys the marker
# per session: ``.claude/session/role-<sanitized_session_id>.json``. This
# module is the single home for the per-session path + sanitizer so the writer
# (scripts/workstream_focus.py), the WI-4534 guard reader
# (scripts/bridge_work_intent_registry.py), the resolver
# (scripts/session_role_resolution.py), and the SessionStart sweeper
# (scripts/session_start_dispatch_core.py) cannot drift apart. Parity tests
# bind every consumer to these helpers.
#
# stdlib-only (re + pathlib), no import-time side effects: the hook-safe
# contract above still holds.
SESSION_MARKER_DIR_PARTS: tuple[str, ...] = (".claude", "session")
PER_SESSION_ROLE_MARKER_PREFIX = "role-"
PER_SESSION_ROLE_MARKER_SUFFIX = ".json"
# Glob that matches every per-session role marker (used by the SessionStart
# stale-marker sweeper). The legacy single-file marker
# ("active-session-role.json") deliberately does NOT match this glob, so the
# sweeper never touches it.
PER_SESSION_ROLE_MARKER_GLOB = f"{PER_SESSION_ROLE_MARKER_PREFIX}*{PER_SESSION_ROLE_MARKER_SUFFIX}"
_UNSAFE_SESSION_ID_CHARS = re.compile(r"[^A-Za-z0-9._-]+")
# Defensive cap so a pathological env value cannot produce an over-long path
# component on any platform.
_MAX_SANITIZED_SESSION_ID_LEN = 128


def sanitize_session_id(session_id: str) -> str:
    """Return a filesystem-safe token for ``session_id``.

    Collapses any run of characters outside ``[A-Za-z0-9._-]`` to a single
    ``-`` and trims leading/trailing ``-``/``.`` so the result is a clean path
    component. Transcript UUIDs and dispatch ids
    (``<ts>-<role>-<harness>-<hash>``) pass through essentially unchanged.
    """
    cleaned = _UNSAFE_SESSION_ID_CHARS.sub("-", str(session_id)).strip("-.")
    if not cleaned:
        cleaned = "unknown"
    return cleaned[:_MAX_SANITIZED_SESSION_ID_LEN]


def per_session_role_marker_name(session_id: str) -> str:
    """Return the per-session role-marker filename for ``session_id``."""
    return f"{PER_SESSION_ROLE_MARKER_PREFIX}{sanitize_session_id(session_id)}{PER_SESSION_ROLE_MARKER_SUFFIX}"


def session_marker_dir(project_root: Path | str) -> Path:
    """Return the ``.claude/session`` directory under ``project_root``."""
    return Path(project_root).joinpath(*SESSION_MARKER_DIR_PARTS)


def per_session_role_marker_path(project_root: Path | str, session_id: str) -> Path:
    """Return the per-session role-marker path for ``session_id``.

    The single authoritative path builder shared by the WI-4540 writer, the
    guard reader, the resolver, and the SessionStart sweeper.
    """
    return session_marker_dir(project_root) / per_session_role_marker_name(session_id)


def resolve_session_id(
    explicit: str | None = None,
    *,
    order: Iterable[str] = BRIDGE_WORK_INTENT_ORDER,
    environ: Mapping[str, str] | None = None,
) -> str:
    """Return a resolved session id, or ``""`` when none is available.

    Precedence: ``explicit`` wins when truthy after stripping; otherwise the
    first env var in ``order`` whose value is non-empty after stripping; else
    ``""``. ``environ`` defaults to ``os.environ`` and is overridable for tests.

    Stdlib-only and side-effect-free so hooks can call it on every invocation.
    """
    explicit_value = str(explicit or "").strip()
    if explicit_value:
        return explicit_value
    env = os.environ if environ is None else environ
    for name in order:
        value = str(env.get(name) or "").strip()
        if value:
            return value
    return ""


__all__ = [
    "BRIDGE_WORK_INTENT_ORDER",
    "MARKER_CONTINUITY_ORDER",
    "PER_SESSION_ROLE_MARKER_GLOB",
    "PER_SESSION_ROLE_MARKER_PREFIX",
    "PER_SESSION_ROLE_MARKER_SUFFIX",
    "SESSION_ID_ENV_VARS",
    "SESSION_MARKER_DIR_PARTS",
    "per_session_role_marker_name",
    "per_session_role_marker_path",
    "resolve_session_id",
    "sanitize_session_id",
    "session_marker_dir",
]
