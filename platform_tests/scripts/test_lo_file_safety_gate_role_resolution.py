# (c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""Tests for _is_lo_enforced role resolution in lo-file-safety-gate.py.

Verifies that the LO file-safety write-gate resolves the session role via the
DCL-SESSION-ROLE-RESOLUTION-001 deterministic table (marker > durable), using
the canonical shared session-id resolver for harness-neutral session-id
resolution.

Bridge: gtkb-lo-file-safety-gate-envelope-role-resolution (GO at -006)
Specs:
  - DCL-SESSION-ROLE-RESOLUTION-001 (marker > durable resolution)
  - GOV-SESSION-ROLE-AUTHORITY-001 (durable fallback when no marker)
  - ADR-INTERACTIVE-SESSION-ROLE-OVERRIDE-001 (session-stated role precedence)
  - SPEC-DISPATCH-ENVELOPE-ELEMENT-001 (envelope-authoritative principle)
Work Item: WI-4371
"""

from __future__ import annotations

import importlib
import json
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))


# ---------------------------------------------------------------------------
# Helpers — import the hook module and extract _is_lo_enforced
# ---------------------------------------------------------------------------


def _import_hook():
    """Import (or reimport) the lo-file-safety-gate hook module."""
    hook_path = REPO_ROOT / ".claude" / "hooks" / "lo-file-safety-gate.py"
    assert hook_path.is_file(), f"Hook not found at {hook_path}"
    spec = importlib.util.spec_from_file_location("lo_file_safety_gate", str(hook_path))
    mod = importlib.util.module_from_spec(spec)
    # Register in sys.modules so @dataclass can resolve __module__.__dict__
    sys.modules[spec.name] = mod
    try:
        spec.loader.exec_module(mod)
    except Exception:
        sys.modules.pop(spec.name, None)
        raise
    return mod


HOOK_MODULE = _import_hook()
_is_lo_enforced = HOOK_MODULE._is_lo_enforced


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture()
def project_root(tmp_path: Path) -> Path:
    """Create a minimal project root with session marker directory."""
    session_dir = tmp_path / ".claude" / "session"
    session_dir.mkdir(parents=True)
    # Also create harness-state directory for durable fallback path
    hs_dir = tmp_path / "harness-state"
    hs_dir.mkdir(parents=True)
    return tmp_path


def _write_marker(project_root: Path, role: str, session_id: str | None = None) -> None:
    """Write a session-role marker file."""
    marker = project_root / ".claude" / "session" / "active-session-role.json"
    body: dict = {"role": role}
    if session_id is not None:
        body["session_id"] = session_id
    marker.write_text(json.dumps(body), encoding="utf-8")


def _write_durable_role(
    project_root: Path,
    harness_id: str,
    role: str,
    harness_name: str = "claude",
) -> None:
    """Write a minimal harness-registry.json (list-based projection) + identities."""
    # Registry projection uses a list format per harness_projection_reader
    registry = project_root / "harness-state" / "harness-registry.json"
    doc = {
        "harnesses": [
            {
                "id": harness_id,
                "harness_name": harness_name,
                "role": [role],
                "status": "active",
            }
        ]
    }
    registry.write_text(json.dumps(doc), encoding="utf-8")

    # Identities file uses a dict keyed by harness name
    ident = project_root / "harness-state" / "harness-identities.json"
    ident_doc = {
        "harnesses": {
            harness_name: {
                "id": harness_id,
            }
        }
    }
    ident.write_text(json.dumps(ident_doc), encoding="utf-8")


# ---------------------------------------------------------------------------
# Test 1: Verified PB marker + matching payload session_id → False (writes OK)
# DCL-SESSION-ROLE-RESOLUTION-001: resolved role = marker when verified
# ---------------------------------------------------------------------------


def test_is_lo_enforced_false_when_verified_pb_marker_payload(
    project_root: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """When a PB marker exists and the payload session_id matches, writes are
    allowed (gate returns False).
    """
    session_id = "test-session-abc123"
    _write_marker(project_root, "prime-builder", session_id)
    _write_durable_role(project_root, "B", "loyal-opposition", "claude")

    # Clear harness-related env so defaults apply
    monkeypatch.setenv("CLAUDE_PROJECT_DIR", str(project_root))
    monkeypatch.delenv("GTKB_HARNESS_NAME", raising=False)
    monkeypatch.delenv("GTKB_ACTIVE_HARNESS_ID", raising=False)
    monkeypatch.delenv("GTKB_HARNESS_ID", raising=False)
    # Clear all session-id env vars so only payload is used
    for var in (
        "GTKB_SESSION_ID",
        "CODEX_SESSION_ID",
        "CODEX_THREAD_ID",
        "CLAUDE_SESSION_ID",
        "CLAUDE_CODE_SESSION_ID",
        "GTKB_INHERITED_SESSION_ID",
        "ANTIGRAVITY_SESSION_ID",
    ):
        monkeypatch.delenv(var, raising=False)

    payload = {"session_id": session_id}
    result = _is_lo_enforced(project_root, payload)
    assert result is False, (
        "PB marker with matching payload session_id should resolve to PB (writes allowed, gate returns False)"
    )


# ---------------------------------------------------------------------------
# Test 2: Payload session_id wins over conflicting env session_id
# F2.1 from the proposal
# ---------------------------------------------------------------------------


def test_is_lo_enforced_payload_session_id_wins_over_env(project_root: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """Payload session_id matches the marker; an env var has a different id.
    The payload should win, so the marker's PB role is used (False).
    """
    marker_session_id = "correct-session-xyz"
    env_session_id = "wrong-session-env"

    _write_marker(project_root, "prime-builder", marker_session_id)
    _write_durable_role(project_root, "B", "loyal-opposition", "claude")

    monkeypatch.setenv("CLAUDE_PROJECT_DIR", str(project_root))
    monkeypatch.delenv("GTKB_HARNESS_NAME", raising=False)
    monkeypatch.delenv("GTKB_ACTIVE_HARNESS_ID", raising=False)
    monkeypatch.delenv("GTKB_HARNESS_ID", raising=False)
    # Set an env session-id that DOES NOT match the marker
    monkeypatch.setenv("CLAUDE_CODE_SESSION_ID", env_session_id)
    # Clear other session-id vars
    for var in (
        "GTKB_SESSION_ID",
        "CODEX_SESSION_ID",
        "CODEX_THREAD_ID",
        "CLAUDE_SESSION_ID",
        "GTKB_INHERITED_SESSION_ID",
        "ANTIGRAVITY_SESSION_ID",
    ):
        monkeypatch.delenv(var, raising=False)

    # Payload provides the CORRECT matching id
    payload = {"session_id": marker_session_id}
    result = _is_lo_enforced(project_root, payload)
    assert result is False, (
        "Payload session_id should win over env session_id; marker PB should be used (writes allowed)"
    )


# ---------------------------------------------------------------------------
# Test 3: No payload session_id + env GTKB_SESSION_ID matches marker → PB
# F2.2 from the proposal: harness-neutral env path
# ---------------------------------------------------------------------------


def test_is_lo_enforced_false_when_env_session_id_matches_pb_marker(
    project_root: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """No payload session_id, but GTKB_SESSION_ID (Codex/GTKB path) matches
    the marker. The marker's PB role should be used (False).
    """
    session_id = "gtkb-session-999"
    _write_marker(project_root, "prime-builder", session_id)
    _write_durable_role(project_root, "B", "loyal-opposition", "claude")

    monkeypatch.setenv("CLAUDE_PROJECT_DIR", str(project_root))
    monkeypatch.delenv("GTKB_HARNESS_NAME", raising=False)
    monkeypatch.delenv("GTKB_ACTIVE_HARNESS_ID", raising=False)
    monkeypatch.delenv("GTKB_HARNESS_ID", raising=False)
    # GTKB_SESSION_ID is first in MARKER_CONTINUITY_ORDER
    monkeypatch.setenv("GTKB_SESSION_ID", session_id)
    for var in (
        "CODEX_SESSION_ID",
        "CODEX_THREAD_ID",
        "CLAUDE_SESSION_ID",
        "CLAUDE_CODE_SESSION_ID",
        "GTKB_INHERITED_SESSION_ID",
        "ANTIGRAVITY_SESSION_ID",
    ):
        monkeypatch.delenv(var, raising=False)

    payload: dict = {}  # No session_id in payload
    result = _is_lo_enforced(project_root, payload)
    assert result is False, (
        "GTKB_SESSION_ID matching marker should resolve to PB via MARKER_CONTINUITY_ORDER (writes allowed)"
    )


# ---------------------------------------------------------------------------
# Test 4: No payload + env session id MISMATCHES marker → durable fallback LO
# F2.3 from the proposal
# ---------------------------------------------------------------------------


def test_is_lo_enforced_true_when_env_session_id_mismatches_marker_durable_lo(
    project_root: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Env session id does not match the marker's session_id. The resolver
    falls back to durable role which is LO → True (writes blocked).
    """
    marker_session_id = "marker-session-aaa"
    env_session_id = "different-session-bbb"

    _write_marker(project_root, "prime-builder", marker_session_id)
    _write_durable_role(project_root, "B", "loyal-opposition", "claude")

    monkeypatch.setenv("CLAUDE_PROJECT_DIR", str(project_root))
    monkeypatch.delenv("GTKB_HARNESS_NAME", raising=False)
    monkeypatch.delenv("GTKB_ACTIVE_HARNESS_ID", raising=False)
    monkeypatch.delenv("GTKB_HARNESS_ID", raising=False)
    monkeypatch.setenv("GTKB_SESSION_ID", env_session_id)
    for var in (
        "CODEX_SESSION_ID",
        "CODEX_THREAD_ID",
        "CLAUDE_SESSION_ID",
        "CLAUDE_CODE_SESSION_ID",
        "GTKB_INHERITED_SESSION_ID",
        "ANTIGRAVITY_SESSION_ID",
    ):
        monkeypatch.delenv(var, raising=False)

    payload: dict = {}  # No payload session_id
    result = _is_lo_enforced(project_root, payload)
    assert result is True, "Session id mismatch should fall back to durable LO role (writes blocked, gate returns True)"


# ---------------------------------------------------------------------------
# Test 5: No session_id anywhere → marker_session_id_unverified branch
# F2.4 from the proposal: documents the unverified branch is intentional
# ---------------------------------------------------------------------------


def test_is_lo_enforced_no_session_id_documents_unverified_branch(
    project_root: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """When no session_id is available (payload=None, env=empty), the resolver
    uses the marker_session_id_unverified branch. A PB marker should still
    resolve to PB (False) — the marker is trusted because SessionStart
    invalidation keeps it session-scoped.
    """
    _write_marker(project_root, "prime-builder")  # No session_id in marker
    _write_durable_role(project_root, "B", "loyal-opposition", "claude")

    monkeypatch.setenv("CLAUDE_PROJECT_DIR", str(project_root))
    monkeypatch.delenv("GTKB_HARNESS_NAME", raising=False)
    monkeypatch.delenv("GTKB_ACTIVE_HARNESS_ID", raising=False)
    monkeypatch.delenv("GTKB_HARNESS_ID", raising=False)
    # Clear all session-id env vars
    for var in (
        "GTKB_SESSION_ID",
        "CODEX_SESSION_ID",
        "CODEX_THREAD_ID",
        "CLAUDE_SESSION_ID",
        "CLAUDE_CODE_SESSION_ID",
        "GTKB_INHERITED_SESSION_ID",
        "ANTIGRAVITY_SESSION_ID",
    ):
        monkeypatch.delenv(var, raising=False)

    payload: dict = {}
    result = _is_lo_enforced(project_root, payload)
    assert result is False, (
        "No session_id anywhere → marker_session_id_unverified branch; "
        "PB marker should still be trusted (writes allowed)"
    )


# ---------------------------------------------------------------------------
# Test 6: No marker, durable LO → True (writes blocked)
# GOV-SESSION-ROLE-AUTHORITY-001: durable fallback when no marker
# ---------------------------------------------------------------------------


def test_is_lo_enforced_true_when_no_marker_durable_lo(project_root: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """No session-role marker exists. The durable role is LO → True."""
    # Do NOT write a marker
    _write_durable_role(project_root, "B", "loyal-opposition", "claude")

    monkeypatch.setenv("CLAUDE_PROJECT_DIR", str(project_root))
    monkeypatch.delenv("GTKB_HARNESS_NAME", raising=False)
    monkeypatch.delenv("GTKB_ACTIVE_HARNESS_ID", raising=False)
    monkeypatch.delenv("GTKB_HARNESS_ID", raising=False)
    for var in (
        "GTKB_SESSION_ID",
        "CODEX_SESSION_ID",
        "CODEX_THREAD_ID",
        "CLAUDE_SESSION_ID",
        "CLAUDE_CODE_SESSION_ID",
        "GTKB_INHERITED_SESSION_ID",
        "ANTIGRAVITY_SESSION_ID",
    ):
        monkeypatch.delenv(var, raising=False)

    payload: dict = {}
    result = _is_lo_enforced(project_root, payload)
    assert result is True, "No marker + durable LO → writes blocked (True)"


# ---------------------------------------------------------------------------
# Test 7: No marker, durable PB → False (writes allowed)
# Durable PB with no marker still allows writes
# ---------------------------------------------------------------------------


def test_is_lo_enforced_false_when_no_marker_durable_pb(project_root: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """No session-role marker exists. The durable role is PB → False."""
    _write_durable_role(project_root, "B", "prime-builder", "claude")

    monkeypatch.setenv("CLAUDE_PROJECT_DIR", str(project_root))
    monkeypatch.delenv("GTKB_HARNESS_NAME", raising=False)
    monkeypatch.delenv("GTKB_ACTIVE_HARNESS_ID", raising=False)
    monkeypatch.delenv("GTKB_HARNESS_ID", raising=False)
    for var in (
        "GTKB_SESSION_ID",
        "CODEX_SESSION_ID",
        "CODEX_THREAD_ID",
        "CLAUDE_SESSION_ID",
        "CLAUDE_CODE_SESSION_ID",
        "GTKB_INHERITED_SESSION_ID",
        "ANTIGRAVITY_SESSION_ID",
    ):
        monkeypatch.delenv(var, raising=False)

    payload: dict = {}
    result = _is_lo_enforced(project_root, payload)
    assert result is False, "No marker + durable PB → writes allowed (False)"


# ---------------------------------------------------------------------------
# Test 8: Role state unavailable → False (fail-open)
# Fail-open on missing/malformed role state
# ---------------------------------------------------------------------------


def test_is_lo_enforced_false_when_role_state_unavailable(project_root: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """When all role-resolution state is missing (no marker, no registry,
    resolver imports would fail), the gate should fail-open (False).
    """
    # No marker, no harness-state files — just the bare directories
    # Remove harness-state contents
    hs_dir = project_root / "harness-state"
    for f in hs_dir.iterdir():
        f.unlink()

    monkeypatch.setenv("CLAUDE_PROJECT_DIR", str(project_root))
    monkeypatch.delenv("GTKB_HARNESS_NAME", raising=False)
    monkeypatch.delenv("GTKB_ACTIVE_HARNESS_ID", raising=False)
    monkeypatch.delenv("GTKB_HARNESS_ID", raising=False)
    for var in (
        "GTKB_SESSION_ID",
        "CODEX_SESSION_ID",
        "CODEX_THREAD_ID",
        "CLAUDE_SESSION_ID",
        "CLAUDE_CODE_SESSION_ID",
        "GTKB_INHERITED_SESSION_ID",
        "ANTIGRAVITY_SESSION_ID",
    ):
        monkeypatch.delenv(var, raising=False)

    payload: dict = {}
    result = _is_lo_enforced(project_root, payload)
    assert result is False, "Missing/malformed role state → fail-open (False, writes allowed)"


# ---------------------------------------------------------------------------
# Bonus: Regression test — original durable-only fallback path
# Exercises the case where resolve_interactive_session_role is None
# ---------------------------------------------------------------------------


def test_is_lo_enforced_durable_fallback_when_resolver_unavailable(
    project_root: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """When the session role resolver is unavailable (None sentinel), the gate
    falls back to the durable-only path.
    """
    _write_durable_role(project_root, "B", "loyal-opposition", "claude")

    monkeypatch.setenv("CLAUDE_PROJECT_DIR", str(project_root))
    monkeypatch.delenv("GTKB_HARNESS_NAME", raising=False)
    monkeypatch.delenv("GTKB_ACTIVE_HARNESS_ID", raising=False)
    monkeypatch.delenv("GTKB_HARNESS_ID", raising=False)
    for var in (
        "GTKB_SESSION_ID",
        "CODEX_SESSION_ID",
        "CODEX_THREAD_ID",
        "CLAUDE_SESSION_ID",
        "CLAUDE_CODE_SESSION_ID",
        "GTKB_INHERITED_SESSION_ID",
        "ANTIGRAVITY_SESSION_ID",
    ):
        monkeypatch.delenv(var, raising=False)

    # Temporarily null out the resolver import to simulate unavailable
    original_resolver = HOOK_MODULE.resolve_interactive_session_role
    try:
        HOOK_MODULE.resolve_interactive_session_role = None
        payload: dict = {}
        result = _is_lo_enforced(project_root, payload)
        assert result is True, "Resolver unavailable + durable LO → fallback returns True (writes blocked)"
    finally:
        HOOK_MODULE.resolve_interactive_session_role = original_resolver
