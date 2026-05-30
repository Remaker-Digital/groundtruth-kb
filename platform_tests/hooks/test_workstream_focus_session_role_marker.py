"""Slice 2 of PROJECT-GTKB-INTERACTIVE-SESSION-ROLE-OVERRIDE: marker write.

bridge/gtkb-interactive-session-role-override-slice-2-session-role-marker-003.md
(Codex GO at -004).

Spec coverage:

- ``ADR-INTERACTIVE-SESSION-ROLE-OVERRIDE-001`` Decision 4: ephemeral
  session-scoped marker; mid-session re-typing overrides.
- ``DCL-SESSION-ROLE-RESOLUTION-001`` assertion 2: marker written on the
  init-keyword code path.
- ``DCL-SESSION-ROLE-RESOLUTION-001`` assertion 6: persisted marker carries
  a non-null session id; no-id condition is the fail-soft branch and writes
  no marker.
- ``DCL-SESSION-ROLE-RESOLUTION-001`` assertion 7: marker role is in
  ``{prime-builder, loyal-opposition}``.
- ``DCL-INIT-KEYWORD-CONSISTENT-ASSERTION-001`` v2: marker is written only on
  the env-var-absent interactive path; headless dispatch (env-var present)
  does not write the marker.

The shared ``scripts/workstream_focus.py`` module is invoked by both the
Claude hook (``.claude/hooks/workstream-focus.py``) and the Codex wrapper
(``.codex/gtkb-hooks/workstream-focus.cmd``), so a single change covers both
harnesses.
"""

from __future__ import annotations

import importlib
import importlib.util
import json
import sys
from pathlib import Path
from types import ModuleType

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
MODULE_PATH = REPO_ROOT / "scripts" / "workstream_focus.py"

if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

_PACKAGE_SRC = REPO_ROOT / "groundtruth-kb" / "src"
if str(_PACKAGE_SRC) not in sys.path:
    sys.path.insert(0, str(_PACKAGE_SRC))


# Env vars the implementation reads in the resolver fallback chain. Each
# test's fixture sanitises these so the resolver cannot pick up stray values
# from the test runner's parent environment.
_ALL_RESOLVER_ENVS = (
    "GTKB_BRIDGE_POLLER_RUN_ID",  # also stripped: this is the headless guard
    "GTKB_SESSION_ID",
    "CODEX_SESSION_ID",
    "CODEX_THREAD_ID",
    "CLAUDE_SESSION_ID",
    "CLAUDE_CODE_SESSION_ID",
)


@pytest.fixture
def clean_env(monkeypatch: pytest.MonkeyPatch) -> None:
    for name in _ALL_RESOLVER_ENVS:
        monkeypatch.delenv(name, raising=False)


def _load_module() -> ModuleType:
    """Load workstream_focus.py under a synthetic name so the test module's
    import is isolated from any prior load (e.g., earlier sys.modules entries).
    """
    spec = importlib.util.spec_from_file_location("_test_workstream_focus_session_role_marker", MODULE_PATH)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@pytest.fixture
def wsf(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> ModuleType:
    """Load workstream_focus.py and redirect project_root + lifecycle guard.

    The lifecycle-guard reader/writer keys off the project_root passed in;
    each test gets a fresh tmp_path so the guard file and the marker file
    are isolated. We also pre-arm the discard-next-user-prompt gate so the
    init-keyword branch is actually exercised (the gate is the precondition
    for ``_consume_discard_first_prompt_gate`` to do any work).
    """
    module = _load_module()
    # Some downstream calls in the init-match branch invoke
    # _set_work_subject_from_init_match which may write outside the project.
    # Stub it to a no-op returning None so the tests stay hermetic.
    monkeypatch.setattr(module, "_set_work_subject_from_init_match", lambda *a, **k: None)
    # Pre-arm the lifecycle guard so the discard-next-user-prompt gate fires.
    guard_dir = tmp_path / ".claude" / "session"
    guard_dir.mkdir(parents=True, exist_ok=True)
    module._write_lifecycle_guard({"discard_next_user_prompt": True}, tmp_path)
    return module


def _marker_path(project_root: Path) -> Path:
    return project_root / ".claude" / "session" / "active-session-role.json"


# ---------------------------------------------------------------------------
# DCL-SESSION-ROLE-RESOLUTION-001 assertion 2 + 7: marker written; role in set.
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    ("mode", "expected_role"),
    [("pb", "prime-builder"), ("lo", "loyal-opposition")],
)
def test_marker_written_on_interactive_init_keyword(
    wsf: ModuleType,
    tmp_path: Path,
    clean_env: None,
    mode: str,
    expected_role: str,
) -> None:
    """An interactive ``::init gtkb <mode>`` prompt with a payload session_id
    writes a marker whose role profile matches the canonical mapping."""
    wsf._consume_discard_first_prompt_gate(f"::init gtkb {mode}", tmp_path, session_id="sess-payload-abc")
    marker_path = _marker_path(tmp_path)
    assert marker_path.is_file(), "marker file was not written"
    body = json.loads(marker_path.read_text(encoding="utf-8"))
    assert body["role"] == expected_role
    assert body["session_id"] == "sess-payload-abc"
    assert body["session_id_source"] == "payload"
    assert body["source"] == "init_keyword"
    assert isinstance(body["written_at"], str) and body["written_at"].endswith("Z")


# ---------------------------------------------------------------------------
# DCL-SESSION-ROLE-RESOLUTION-001 assertion 6: env fallback chain.
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "env_name",
    [
        "GTKB_SESSION_ID",
        "CODEX_SESSION_ID",
        "CODEX_THREAD_ID",
        "CLAUDE_SESSION_ID",
        "CLAUDE_CODE_SESSION_ID",
    ],
)
def test_marker_session_id_resolves_from_env_fallback(
    wsf: ModuleType,
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    clean_env: None,
    env_name: str,
) -> None:
    """When the payload has no session_id, the resolver walks the env chain;
    ``session_id_source`` records which env var supplied the value."""
    monkeypatch.setenv(env_name, f"sess-env-{env_name.lower()}")
    wsf._consume_discard_first_prompt_gate("::init gtkb pb", tmp_path, session_id=None)
    body = json.loads(_marker_path(tmp_path).read_text(encoding="utf-8"))
    assert body["session_id"] == f"sess-env-{env_name.lower()}"
    assert body["session_id_source"] == f"env:{env_name}"


def test_env_fallback_priority_payload_beats_env(
    wsf: ModuleType,
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    clean_env: None,
) -> None:
    """A payload-supplied session_id wins over any env-var candidate."""
    monkeypatch.setenv("GTKB_SESSION_ID", "from-env")
    wsf._consume_discard_first_prompt_gate("::init gtkb pb", tmp_path, session_id="from-payload")
    body = json.loads(_marker_path(tmp_path).read_text(encoding="utf-8"))
    assert body["session_id"] == "from-payload"
    assert body["session_id_source"] == "payload"


def test_env_fallback_priority_first_listed_env_wins(
    wsf: ModuleType,
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    clean_env: None,
) -> None:
    """The first env in the documented order is preferred over later ones."""
    # Set the last env in the chain plus the first; the first must win.
    monkeypatch.setenv("CLAUDE_CODE_SESSION_ID", "from-last")
    monkeypatch.setenv("GTKB_SESSION_ID", "from-first")
    wsf._consume_discard_first_prompt_gate("::init gtkb pb", tmp_path, session_id=None)
    body = json.loads(_marker_path(tmp_path).read_text(encoding="utf-8"))
    assert body["session_id"] == "from-first"
    assert body["session_id_source"] == "env:GTKB_SESSION_ID"


# ---------------------------------------------------------------------------
# DCL-SESSION-ROLE-RESOLUTION-001 assertion 6 fail-soft: no id -> no marker.
# ---------------------------------------------------------------------------


def test_marker_failsoft_when_no_session_id(
    wsf: ModuleType,
    tmp_path: Path,
    clean_env: None,
) -> None:
    """With no payload session_id and no env fallback, no marker is written
    and the lifecycle guard records the fail-soft event. Per assertion 6 the
    handler MUST NOT persist a marker with null session id."""
    result = wsf._consume_discard_first_prompt_gate("::init gtkb pb", tmp_path, session_id=None)
    assert not _marker_path(tmp_path).exists(), "marker must not be written when no id"
    state = wsf._read_lifecycle_guard(tmp_path)
    assert state.get("startup_session_role_marker_failsoft_reason") == "session_id_unresolved"
    assert isinstance(state.get("startup_session_role_marker_failsoft_at"), str)
    # The startup-relay response is still returned (Slice 1 behavior preserved).
    assert result is not None
    assert "hookSpecificOutput" in result


# ---------------------------------------------------------------------------
# DCL-INIT-KEYWORD-CONSISTENT-ASSERTION-001 v2: headless guard.
# ---------------------------------------------------------------------------


def test_marker_not_written_under_headless_dispatch(
    wsf: ModuleType,
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    clean_env: None,
) -> None:
    """When GTKB_BRIDGE_POLLER_RUN_ID is set, the dispatch is headless and the
    marker MUST NOT be written even if a valid session id is available."""
    monkeypatch.setenv("GTKB_BRIDGE_POLLER_RUN_ID", "run-id-123")
    wsf._consume_discard_first_prompt_gate("::init gtkb lo", tmp_path, session_id="should-not-matter")
    assert not _marker_path(tmp_path).exists()
    state = wsf._read_lifecycle_guard(tmp_path)
    # No marker outcome was recorded — neither success nor fail-soft fires on
    # the headless path because the writer branch is short-circuited.
    assert "startup_session_role_marker_written_at" not in state
    assert "startup_session_role_marker_failsoft_at" not in state


# ---------------------------------------------------------------------------
# Non-keyword prompt: no marker, no fail-soft event.
# ---------------------------------------------------------------------------


def test_marker_not_written_for_non_keyword_prompt(
    wsf: ModuleType,
    tmp_path: Path,
    clean_env: None,
) -> None:
    """An ordinary prompt (no canonical init keyword) hits the
    ``init_match is None`` branch above the marker code path; no marker, no
    fail-soft event."""
    wsf._consume_discard_first_prompt_gate("ordinary owner prompt", tmp_path, session_id="sess-1")
    assert not _marker_path(tmp_path).exists()
    state = wsf._read_lifecycle_guard(tmp_path)
    assert "startup_session_role_marker_failsoft_at" not in state


# ---------------------------------------------------------------------------
# ADR Decision 4: mid-session re-typing overrides.
# ---------------------------------------------------------------------------


def test_marker_overwritten_on_redeclaration(
    wsf: ModuleType,
    tmp_path: Path,
    clean_env: None,
) -> None:
    """Two consecutive interactive init-keyword prompts produce a marker whose
    role reflects the most recent declaration; ``written_at`` is monotonically
    non-decreasing across the rewrites."""
    # First declaration: pb. We must re-arm the gate before the second call
    # because the first invocation clears discard_next_user_prompt.
    wsf._consume_discard_first_prompt_gate("::init gtkb pb", tmp_path, session_id="sess-1")
    first = json.loads(_marker_path(tmp_path).read_text(encoding="utf-8"))
    assert first["role"] == "prime-builder"
    # Re-arm and re-declare as lo.
    state = wsf._read_lifecycle_guard(tmp_path)
    state["discard_next_user_prompt"] = True
    wsf._write_lifecycle_guard(state, tmp_path)
    wsf._consume_discard_first_prompt_gate("::init gtkb lo", tmp_path, session_id="sess-2")
    second = json.loads(_marker_path(tmp_path).read_text(encoding="utf-8"))
    assert second["role"] == "loyal-opposition"
    assert second["session_id"] == "sess-2"
    assert second["written_at"] >= first["written_at"]


# ---------------------------------------------------------------------------
# Slice 1 preservation: startup-relay response still returned.
# ---------------------------------------------------------------------------


def test_startup_relay_response_unchanged(
    wsf: ModuleType,
    tmp_path: Path,
    clean_env: None,
) -> None:
    """The init-keyword gate response shape (the Slice 1 contract) is the same
    whether the marker is written or fail-softed; the marker write is purely
    additive on the side."""
    response_with_marker = wsf._consume_discard_first_prompt_gate("::init gtkb pb", tmp_path, session_id="sess-a")
    # New tmp project for a clean second-call state.
    other = tmp_path.parent / "other-root"
    other.mkdir(parents=True, exist_ok=True)
    (other / ".claude" / "session").mkdir(parents=True, exist_ok=True)
    wsf._write_lifecycle_guard({"discard_next_user_prompt": True}, other)
    response_failsoft = wsf._consume_discard_first_prompt_gate("::init gtkb pb", other, session_id=None)
    assert response_with_marker is not None
    assert response_failsoft is not None
    assert (
        response_with_marker["hookSpecificOutput"]["hookEventName"]
        == response_failsoft["hookSpecificOutput"]["hookEventName"]
        == "UserPromptSubmit"
    )


# ---------------------------------------------------------------------------
# Fail-soft on unwritable marker dir.
# ---------------------------------------------------------------------------


def test_marker_write_failsoft_on_oserror(
    wsf: ModuleType,
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    clean_env: None,
) -> None:
    """Simulate a write failure inside ``_write_session_role_marker``; the
    handler must not raise, the marker must not exist, and the lifecycle guard
    must record ``marker_write_oserror`` as the fail-soft reason."""

    def boom(*args, **kwargs):
        raise OSError("simulated unwritable marker dir")

    monkeypatch.setattr(wsf, "_write_session_role_marker", lambda *a, **k: False)
    # The patched _write returns False directly; the handler should treat it
    # as the marker_write_oserror fail-soft path.
    wsf._consume_discard_first_prompt_gate("::init gtkb pb", tmp_path, session_id="sess-write-oserror")
    assert not _marker_path(tmp_path).exists()
    state = wsf._read_lifecycle_guard(tmp_path)
    assert state.get("startup_session_role_marker_failsoft_reason") == "marker_write_oserror"


# ---------------------------------------------------------------------------
# Threading: handle_hook_payload reads payload session_id and forwards it.
# ---------------------------------------------------------------------------


def test_handle_hook_payload_threads_payload_session_id(
    wsf: ModuleType,
    tmp_path: Path,
    clean_env: None,
) -> None:
    """``handle_hook_payload`` reads ``payload['session_id']`` and produces a
    marker whose ``session_id_source`` is ``payload``."""
    wsf.handle_hook_payload({"prompt": "::init gtkb pb", "session_id": "from-hook-payload"}, tmp_path)
    body = json.loads(_marker_path(tmp_path).read_text(encoding="utf-8"))
    assert body["session_id"] == "from-hook-payload"
    assert body["session_id_source"] == "payload"
