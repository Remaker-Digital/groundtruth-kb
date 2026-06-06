"""Tests for scripts/gtkb_session_id.py — the shared session-id resolver.

WI-4270 (bridge/gtkb-session-id-shared-resolver-unification-003.md, Codex GO
at -004). Behavior-preserving unification of the session-id env-var membership
and per-surface resolution order.

Coverage:

- T1: ``resolve_session_id`` precedence per ``order`` (explicit wins;
  CLAUDE_CODE_SESSION_ID resolves when sole and beats stale CLAUDE_SESSION_ID
  in bridge order; GTKB_SESSION_ID beats all in marker
  order; "" when nothing is set).
- T2 (drift-lock recurrence guard): the two per-surface orders are checked
  against the canonical membership SET so the membership cannot silently
  diverge again — the class of defect that produced the original
  CLAUDE_CODE_SESSION_ID omission (committed fix ea2040a5).

Spec coverage: ``DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001``;
``DELIB-S312-DETERMINISTIC-SERVICES-PRINCIPLE`` (single membership authority).
"""

from __future__ import annotations

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from scripts.gtkb_session_id import (  # noqa: E402
    BRIDGE_WORK_INTENT_ORDER,
    MARKER_CONTINUITY_ORDER,
    SESSION_ID_ENV_VARS,
    resolve_session_id,
)

# ---------------------------------------------------------------------------
# T1 — resolve_session_id precedence
# ---------------------------------------------------------------------------


def test_explicit_wins_over_env() -> None:
    """A truthy explicit value short-circuits the env walk in any order."""
    env = {"GTKB_SESSION_ID": "from-env", "CLAUDE_SESSION_ID": "also-env"}
    assert resolve_session_id("explicit", order=BRIDGE_WORK_INTENT_ORDER, environ=env) == "explicit"


def test_claude_code_session_id_resolves_when_sole() -> None:
    """CLAUDE_CODE_SESSION_ID (the live Claude Code harness var) resolves when
    it is the only value present — the original ea2040a5 fix, now centralized."""
    env = {"CLAUDE_CODE_SESSION_ID": "cc-sole"}
    assert resolve_session_id(None, order=BRIDGE_WORK_INTENT_ORDER, environ=env) == "cc-sole"


def test_claude_code_session_id_beats_legacy_claude_session_in_bridge_order() -> None:
    """In the bridge work-intent order, the live Claude Code session id wins
    over stale legacy CLAUDE_SESSION_ID."""
    env = {"CLAUDE_SESSION_ID": "cs", "CLAUDE_CODE_SESSION_ID": "cc"}
    assert resolve_session_id(None, order=BRIDGE_WORK_INTENT_ORDER, environ=env) == "cc"


def test_dispatch_run_id_beats_parent_harness_env_in_bridge_order() -> None:
    """A spawned bridge worker's dispatch id must outrank parent harness env."""
    env = {
        "GTKB_BRIDGE_POLLER_RUN_ID": "dispatch-run",
        "CLAUDE_CODE_SESSION_ID": "parent-claude",
        "CODEX_THREAD_ID": "parent-codex-thread",
        "GTKB_SESSION_ID": "parent-gtkb",
    }
    assert resolve_session_id(None, order=BRIDGE_WORK_INTENT_ORDER, environ=env) == "dispatch-run"


def test_gtkb_session_id_beats_all_in_marker_order() -> None:
    """In the marker-continuity order, GTKB_SESSION_ID wins over harness vars."""
    env = {
        "GTKB_SESSION_ID": "gtkb",
        "CODEX_SESSION_ID": "codex",
        "CLAUDE_SESSION_ID": "cs",
        "CLAUDE_CODE_SESSION_ID": "cc",
    }
    assert resolve_session_id(None, order=MARKER_CONTINUITY_ORDER, environ=env) == "gtkb"


def test_empty_when_no_value_present() -> None:
    """No explicit value and an empty environ resolves to the empty string."""
    assert resolve_session_id(None, order=BRIDGE_WORK_INTENT_ORDER, environ={}) == ""


def test_whitespace_only_values_skip_to_next_candidate() -> None:
    """Whitespace-only explicit and first-env values are skipped; the next
    non-empty env value (stripped) wins."""
    env = {"CLAUDE_SESSION_ID": "   ", "CLAUDE_CODE_SESSION_ID": "  cc  "}
    assert resolve_session_id("   ", order=BRIDGE_WORK_INTENT_ORDER, environ=env) == "cc"


def test_default_order_is_bridge_work_intent() -> None:
    """Calling without an explicit order uses BRIDGE_WORK_INTENT_ORDER."""
    env = {"CLAUDE_SESSION_ID": "cs", "GTKB_SESSION_ID": "gtkb"}
    assert resolve_session_id(None, environ=env) == "cs"


# ---------------------------------------------------------------------------
# T2 — drift-lock recurrence guard
# ---------------------------------------------------------------------------


def test_bridge_order_is_full_permutation_of_membership_set() -> None:
    """The bridge order must cover the entire membership set (no member can be
    silently dropped from the bridge surfaces)."""
    assert set(BRIDGE_WORK_INTENT_ORDER) == set(SESSION_ID_ENV_VARS)


def test_marker_order_is_subset_of_membership_set() -> None:
    """The marker order is a documented subset — it must not introduce a member
    that is absent from the canonical authority."""
    assert set(MARKER_CONTINUITY_ORDER) <= set(SESSION_ID_ENV_VARS)


def test_orders_have_no_duplicate_members() -> None:
    assert len(BRIDGE_WORK_INTENT_ORDER) == len(set(BRIDGE_WORK_INTENT_ORDER))
    assert len(MARKER_CONTINUITY_ORDER) == len(set(MARKER_CONTINUITY_ORDER))


def test_orders_have_no_unknown_members() -> None:
    """Neither order may contain a name outside the canonical membership set."""
    assert set(BRIDGE_WORK_INTENT_ORDER) <= set(SESSION_ID_ENV_VARS)
    assert set(MARKER_CONTINUITY_ORDER) <= set(SESSION_ID_ENV_VARS)


def test_claude_code_session_id_locked_into_all_surfaces() -> None:
    """The original defect was the omission of CLAUDE_CODE_SESSION_ID; lock it
    into the membership set and both per-surface orders."""
    assert "CLAUDE_CODE_SESSION_ID" in SESSION_ID_ENV_VARS
    assert "CLAUDE_CODE_SESSION_ID" in BRIDGE_WORK_INTENT_ORDER
    assert "CLAUDE_CODE_SESSION_ID" in MARKER_CONTINUITY_ORDER


def test_dispatch_run_id_is_bridge_only_marker_excluded() -> None:
    assert "GTKB_BRIDGE_POLLER_RUN_ID" in SESSION_ID_ENV_VARS
    assert BRIDGE_WORK_INTENT_ORDER[0] == "GTKB_BRIDGE_POLLER_RUN_ID"
    assert "GTKB_BRIDGE_POLLER_RUN_ID" not in MARKER_CONTINUITY_ORDER
