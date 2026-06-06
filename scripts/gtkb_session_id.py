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

- ``BRIDGE_WORK_INTENT_ORDER`` (live-Claude-Code-first): the bridge work-intent
  surfaces -- ``scripts/bridge_claim_cli.py``,
  ``.claude/hooks/bridge-compliance-gate.py``,
  ``.claude/hooks/bridge-axis-2-surface.py``, and the
  ``bridge-propose`` ``write_bridge`` helper. A full permutation of
  ``SESSION_ID_ENV_VARS``.
- ``MARKER_CONTINUITY_ORDER`` (``GTKB_SESSION_ID``-first): the session-role
  marker surfaces -- ``scripts/workstream_focus.py`` (marker writer) and
  ``groundtruth-kb/src/groundtruth_kb/project/doctor.py`` (doctor marker
  resolver) -- so an inherited/dispatched GT-KB session id wins over ambient
  harness env. A documented SUBSET of ``SESSION_ID_ENV_VARS`` (intentionally
  excludes ``GTKB_INHERITED_SESSION_ID`` and ``ANTIGRAVITY_SESSION_ID`` to
  preserve the current marker-continuity behavior).

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
from collections.abc import Iterable, Mapping

# Canonical membership SET: the union of every session-id env var any GT-KB
# surface resolves. Frozen so a caller cannot mutate the authority in place.
# The two order constants below are checked against this set by the drift-lock
# test (platform_tests/scripts/test_gtkb_session_id.py) so membership can never
# silently diverge again -- the recurrence guard for the ea2040a5 defect class.
SESSION_ID_ENV_VARS: frozenset[str] = frozenset(
    {
        "CLAUDE_SESSION_ID",
        "CLAUDE_CODE_SESSION_ID",
        "GTKB_INHERITED_SESSION_ID",
        "CODEX_SESSION_ID",
        "CODEX_THREAD_ID",
        "ANTIGRAVITY_SESSION_ID",
        "GTKB_SESSION_ID",
    }
)

# Bridge work-intent surfaces: live Claude Code first so stale legacy
# CLAUDE_SESSION_ID values cannot beat the active Claude Code session.
# A full permutation of SESSION_ID_ENV_VARS (drift-lock T2).
BRIDGE_WORK_INTENT_ORDER: tuple[str, ...] = (
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
    "SESSION_ID_ENV_VARS",
    "resolve_session_id",
]
