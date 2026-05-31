"""Slice 10: end-to-end verification of the DCL-SESSION-ROLE-RESOLUTION-001
resolution table from a session-level perspective.

bridge/gtkb-interactive-session-role-override-slice-10-regression-tests-005.md
(Codex GO at -006).

Module scope (per the slice proposal):

- Covers DCL-SESSION-ROLE-RESOLUTION-001 assertions 2, 3, 4, 6, and 7 by
  exercising ``scripts.session_role_resolution.resolve_interactive_session_role``
  against real on-disk marker fixtures.
- Headless authorization rows (assertion 1) and parity drift (assertion 8)
  are owned by Module 5 and Module 3 respectively; marker ephemerality
  (assertion 5) is owned by Module 2. This module deliberately does NOT
  duplicate those.
- Existing Slice 4/6 tests cover the resolver via monkeypatched callables;
  this module is the complementary on-disk fixture form that catches drift
  the mock-based tests cannot (marker JSON shape, key spelling, type
  coercion in the read path).

Parameterized over ``harness_name`` in ``{claude, codex}`` so the resolver's
single deterministic table applies to both dispatcher contexts.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

import scripts.session_role_resolution as srr  # noqa: E402

_ROLE_PB = "prime-builder"
_ROLE_LO = "loyal-opposition"
_HARNESSES = ("claude", "codex")
_SESSION_ID_A = "S375-test-session-id-aaaaaaaa"
_SESSION_ID_B = "S375-test-session-id-bbbbbbbb"


@pytest.fixture
def force_durable_pb(monkeypatch: pytest.MonkeyPatch) -> None:
    """Force ``_durable_role`` to return prime-builder for every harness.

    The resolver composes ``_durable_role`` with marker reads; monkeypatching
    the durable lookup at module scope keeps each test focused on one row of
    the resolution table without standing up a fake harness-state fixture.
    """

    monkeypatch.setattr(srr, "_durable_role", lambda project_root, harness_name: _ROLE_PB)


@pytest.fixture
def force_durable_lo(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(srr, "_durable_role", lambda project_root, harness_name: _ROLE_LO)


def _write_marker(project_root: Path, body: dict[str, object]) -> Path:
    marker_path = srr.session_role_marker_path(project_root)
    marker_path.parent.mkdir(parents=True, exist_ok=True)
    marker_path.write_text(json.dumps(body), encoding="utf-8")
    return marker_path


# ---------------------------------------------------------------------------
# Assertion 4: resolved=durable when interactive and marker is absent.
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("harness", _HARNESSES)
def test_assertion4_no_marker_returns_durable(
    tmp_path: Path,
    harness: str,
    force_durable_pb: None,
) -> None:
    """No marker on disk → resolver returns ``(durable, durable_marker_absent)``."""
    role, source = srr.resolve_interactive_session_role(
        tmp_path, current_session_id=_SESSION_ID_A, harness_name=harness
    )
    assert role == _ROLE_PB
    assert source == "durable_marker_absent"


@pytest.mark.parametrize("harness", _HARNESSES)
def test_assertion4_compaction_resume_falls_back_to_durable(
    tmp_path: Path,
    harness: str,
    force_durable_pb: None,
) -> None:
    """Compaction-resume case: a marker that survived from a prior session
    has a stale session_id; the resolver must NOT honor it.

    The runtime invariant is that SessionStart deletes the marker (Slice 3,
    tested in Module 2); the resolver's defense-in-depth check on session_id
    catches the case where SessionStart invalidation silently failed and a
    marker from a previous session is still on disk.
    """
    _write_marker(tmp_path, {"role": _ROLE_LO, "session_id": _SESSION_ID_B})
    role, source = srr.resolve_interactive_session_role(
        tmp_path, current_session_id=_SESSION_ID_A, harness_name=harness
    )
    assert role == _ROLE_PB, "stale marker must not override durable role"
    assert source == "durable_marker_stale_session"


# ---------------------------------------------------------------------------
# Assertion 2: resolved=keyword when interactive declaration (marker honored).
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("harness", _HARNESSES)
def test_assertion2_marker_with_matching_session_id_overrides_durable(
    tmp_path: Path,
    harness: str,
    force_durable_pb: None,
) -> None:
    """A marker written by the interactive declaration path with a matching
    session_id resolves to the marker's role, source=``marker``.

    This is the load-bearing assertion 2 case: ``::init gtkb lo`` writes the
    marker, the next prompt's resolver consults it with the same session_id,
    and the session-stated role wins over the durable role.
    """
    _write_marker(tmp_path, {"role": _ROLE_LO, "session_id": _SESSION_ID_A})
    role, source = srr.resolve_interactive_session_role(
        tmp_path, current_session_id=_SESSION_ID_A, harness_name=harness
    )
    assert role == _ROLE_LO, "declared session role must override durable"
    assert source == "marker"


@pytest.mark.parametrize("harness", _HARNESSES)
def test_assertion2_marker_can_force_pb_over_durable_lo(
    tmp_path: Path,
    harness: str,
    force_durable_lo: None,
) -> None:
    """Symmetric to the above: a PB declaration overrides a durable-LO harness.

    Both directions matter — the override is not biased toward one role.
    """
    _write_marker(tmp_path, {"role": _ROLE_PB, "session_id": _SESSION_ID_A})
    role, source = srr.resolve_interactive_session_role(
        tmp_path, current_session_id=_SESSION_ID_A, harness_name=harness
    )
    assert role == _ROLE_PB
    assert source == "marker"


# ---------------------------------------------------------------------------
# Assertion 3: resolved=marker when interactive continuation (session_id None).
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("harness", _HARNESSES)
def test_assertion3_marker_continuation_without_session_id(
    tmp_path: Path,
    harness: str,
    force_durable_pb: None,
) -> None:
    """When the caller does not pass current_session_id (e.g., the AXIS 2
    surface hook reading the marker mid-session without UPS payload), the
    resolver accepts the marker on the SessionStart-invalidation invariant:
    a present marker mid-session must belong to this session.

    Source is the distinguished ``marker_session_id_unverified`` so consumers
    can track which path the resolution took without changing the returned
    role.
    """
    _write_marker(tmp_path, {"role": _ROLE_LO, "session_id": _SESSION_ID_A})
    role, source = srr.resolve_interactive_session_role(tmp_path, current_session_id=None, harness_name=harness)
    assert role == _ROLE_LO
    assert source == "marker_session_id_unverified"


# ---------------------------------------------------------------------------
# Assertion 6: marker carries session id; stale session_id triggers fallback.
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("harness", _HARNESSES)
def test_assertion6_marker_without_session_id_field_is_stale(
    tmp_path: Path,
    harness: str,
    force_durable_pb: None,
) -> None:
    """A marker with no session_id field when the caller supplies one is
    treated as stale (cannot prove same-session). This is the wire-form
    side of assertion 6: the field must be present AND match.
    """
    _write_marker(tmp_path, {"role": _ROLE_LO})  # no session_id key at all
    role, source = srr.resolve_interactive_session_role(
        tmp_path, current_session_id=_SESSION_ID_A, harness_name=harness
    )
    assert role == _ROLE_PB
    assert source == "durable_marker_stale_session"


@pytest.mark.parametrize("harness", _HARNESSES)
def test_assertion6_marker_session_id_wrong_type_is_stale(
    tmp_path: Path,
    harness: str,
    force_durable_pb: None,
) -> None:
    """A marker whose session_id is not a string (e.g., int) is treated as
    stale. The check is ``isinstance(marker_session_id, str)``; type
    coercion would defeat the equality check.
    """
    _write_marker(tmp_path, {"role": _ROLE_LO, "session_id": 12345})
    role, source = srr.resolve_interactive_session_role(
        tmp_path, current_session_id=_SESSION_ID_A, harness_name=harness
    )
    assert role == _ROLE_PB
    assert source == "durable_marker_stale_session"


# ---------------------------------------------------------------------------
# Assertion 7: marker role must be a member of the canonical role set.
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("harness", _HARNESSES)
def test_assertion7_marker_with_invalid_role_token_is_ignored(
    tmp_path: Path,
    harness: str,
    force_durable_pb: None,
) -> None:
    """A marker whose role is outside ``{prime-builder, loyal-opposition}``
    is treated as invalid; the resolver falls back to durable with
    source=``durable_marker_invalid_role``.

    Together with assertion 6 this prevents a malformed or maliciously
    crafted marker from coercing the session into an unknown role.
    """
    _write_marker(tmp_path, {"role": "system-admin", "session_id": _SESSION_ID_A})
    role, source = srr.resolve_interactive_session_role(
        tmp_path, current_session_id=_SESSION_ID_A, harness_name=harness
    )
    assert role == _ROLE_PB
    assert source == "durable_marker_invalid_role"


@pytest.mark.parametrize("harness", _HARNESSES)
def test_assertion7_marker_with_missing_role_field_is_invalid(
    tmp_path: Path,
    harness: str,
    force_durable_pb: None,
) -> None:
    """A marker with no role field at all is treated as invalid (the
    membership check on ``None`` fails against ``_VALID_ROLES``).
    """
    _write_marker(tmp_path, {"session_id": _SESSION_ID_A})  # no role
    role, source = srr.resolve_interactive_session_role(
        tmp_path, current_session_id=_SESSION_ID_A, harness_name=harness
    )
    assert role == _ROLE_PB
    assert source == "durable_marker_invalid_role"


# ---------------------------------------------------------------------------
# Wire-form robustness: malformed marker files fall back to durable cleanly.
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("harness", _HARNESSES)
def test_malformed_marker_json_treated_as_absent(
    tmp_path: Path,
    harness: str,
    force_durable_pb: None,
) -> None:
    """An on-disk marker that is not valid JSON resolves as if absent.

    The read path catches ``json.JSONDecodeError`` and returns None from
    ``_read_marker``; the resolver path then takes the absent branch.
    """
    marker_path = srr.session_role_marker_path(tmp_path)
    marker_path.parent.mkdir(parents=True, exist_ok=True)
    marker_path.write_text("not-valid-json", encoding="utf-8")
    role, source = srr.resolve_interactive_session_role(
        tmp_path, current_session_id=_SESSION_ID_A, harness_name=harness
    )
    assert role == _ROLE_PB
    assert source == "durable_marker_absent"


@pytest.mark.parametrize("harness", _HARNESSES)
def test_non_object_marker_body_treated_as_absent(
    tmp_path: Path,
    harness: str,
    force_durable_pb: None,
) -> None:
    """A marker whose JSON body is a list rather than an object resolves as
    if absent — the read path requires ``isinstance(body, dict)``.
    """
    marker_path = srr.session_role_marker_path(tmp_path)
    marker_path.parent.mkdir(parents=True, exist_ok=True)
    marker_path.write_text(json.dumps(["not", "an", "object"]), encoding="utf-8")
    role, source = srr.resolve_interactive_session_role(
        tmp_path, current_session_id=_SESSION_ID_A, harness_name=harness
    )
    assert role == _ROLE_PB
    assert source == "durable_marker_absent"


# ---------------------------------------------------------------------------
# Module-level constants the resolver and dispatchers share.
# ---------------------------------------------------------------------------


def test_marker_filename_matches_dispatcher_constant() -> None:
    """The resolver's marker filename constant equals the dispatcher constants.

    This is a defense-in-depth assertion paired with Module 3 (which checks
    parity between the dispatchers themselves); here we additionally bind
    the resolver to that shared name.
    """
    assert srr._SESSION_ROLE_MARKER_NAME == "active-session-role.json"


def test_marker_path_lives_under_claude_session() -> None:
    """Both dispatchers and the resolver agree the marker lives at
    ``<project_root>/.claude/session/active-session-role.json``.
    """
    fake_root = Path("X:/fake/project/root")
    expected = fake_root / ".claude" / "session" / "active-session-role.json"
    assert srr.session_role_marker_path(fake_root) == expected
