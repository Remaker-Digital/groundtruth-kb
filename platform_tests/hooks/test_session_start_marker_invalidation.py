"""Slice 3 of PROJECT-GTKB-INTERACTIVE-SESSION-ROLE-OVERRIDE: SessionStart
marker invalidation.

bridge/gtkb-interactive-session-role-override-slice-3-sessionstart-marker-invalidation-001.md
(Codex GO at -002).

Governing specification:

- ``DCL-SESSION-ROLE-RESOLUTION-001`` assertion 5: the session-state role marker
  MUST NOT survive a SessionStart event; both SessionStart dispatchers MUST
  delete/invalidate any pre-existing marker before SessionStart-time role
  rendering.
- ``ADR-INTERACTIVE-SESSION-ROLE-OVERRIDE-001`` Decision 4: the marker is
  ephemeral and lost across SessionStart events.

The two SessionStart dispatchers (``.claude/hooks`` and ``.codex/gtkb-hooks``)
carry byte-similar implementations of ``_invalidate_session_role_marker``;
every behavioral test is parameterized over both. The marker-path parity test
binds the dispatcher deletion target to the Slice 2 writer path
(``scripts.workstream_focus._session_role_marker_path``) so the two cannot
drift apart.
"""

from __future__ import annotations

import importlib.util
import json
import sys
from datetime import UTC, datetime, timedelta
from pathlib import Path
from types import ModuleType

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]

_DISPATCHERS = {
    "claude": REPO_ROOT / ".claude" / "hooks" / "session_start_dispatch.py",
    "codex": REPO_ROOT / ".codex" / "gtkb-hooks" / "session_start_dispatch.py",
}

if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

_PACKAGE_SRC = REPO_ROOT / "groundtruth-kb" / "src"
if str(_PACKAGE_SRC) not in sys.path:
    sys.path.insert(0, str(_PACKAGE_SRC))


def _load_from_path(synthetic_name: str, path: Path) -> ModuleType:
    spec = importlib.util.spec_from_file_location(synthetic_name, path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _load_dispatcher(harness: str) -> ModuleType:
    return _load_from_path(f"_test_session_start_marker_invalidation_{harness}", _DISPATCHERS[harness])


def _load_workstream_focus() -> ModuleType:
    """Load the Slice 2 writer module from its file path.

    Loading by path (rather than ``import workstream_focus``) is robust to
    sys.path state: only ``REPO_ROOT`` is inserted above, not ``REPO_ROOT/scripts``.
    """
    return _load_from_path("_test_workstream_focus_for_marker_parity", REPO_ROOT / "scripts" / "workstream_focus.py")


@pytest.fixture(params=sorted(_DISPATCHERS))
def dispatcher(request: pytest.FixtureRequest) -> ModuleType:
    return _load_dispatcher(request.param)


def _marker_path(project_root: Path) -> Path:
    return project_root / ".claude" / "session" / "active-session-role.json"


def _write_marker(project_root: Path, body: str = '{"role": "loyal-opposition"}') -> Path:
    path = _marker_path(project_root)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(body, encoding="utf-8")
    return path


# ---------------------------------------------------------------------------
# DCL-SESSION-ROLE-RESOLUTION-001 assertion 5: marker deleted at SessionStart.
# ---------------------------------------------------------------------------


def test_marker_invalidated(dispatcher: ModuleType, tmp_path: Path) -> None:
    """A pre-existing marker is removed by the invalidation helper."""
    marker = _write_marker(tmp_path)
    assert marker.is_file(), "fixture failed to write marker"
    dispatcher._invalidate_session_role_marker(tmp_path)
    assert not marker.exists(), "marker survived SessionStart invalidation"


def test_invalidate_noop_when_absent(dispatcher: ModuleType, tmp_path: Path) -> None:
    """Invalidation is a silent no-op when no marker exists."""
    # No marker written; the parent dir may not even exist.
    dispatcher._invalidate_session_role_marker(tmp_path)  # must not raise
    assert not _marker_path(tmp_path).exists()


def test_invalidate_failsoft_on_oserror(dispatcher: ModuleType, tmp_path: Path) -> None:
    """Invalidation swallows OSError (e.g., the marker path is a directory).

    ``Path.unlink`` on a directory raises an OSError subclass on every
    platform (IsADirectoryError on POSIX, PermissionError on Windows). The
    helper must not let that abort SessionStart.
    """
    marker = _marker_path(tmp_path)
    marker.parent.mkdir(parents=True, exist_ok=True)
    marker.mkdir()  # marker path is now a directory; unlink() will raise OSError
    dispatcher._invalidate_session_role_marker(tmp_path)  # must not raise
    # The helper swallowed the error; the directory is still present.
    assert marker.is_dir()


# ---------------------------------------------------------------------------
# Drift guard: dispatcher deletion path == Slice 2 writer path.
# ---------------------------------------------------------------------------


def test_dispatcher_marker_path_matches_writer(dispatcher: ModuleType, tmp_path: Path) -> None:
    """The path a dispatcher deletes equals the path the Slice 2 writer uses.

    If this fails, SessionStart would delete a different file than the one
    ``scripts/workstream_focus.py`` writes, silently breaking assertion 5.
    """
    workstream_focus = _load_workstream_focus()

    assert dispatcher._session_role_marker_path(tmp_path) == workstream_focus._session_role_marker_path(tmp_path)


def test_both_dispatchers_agree_on_marker_path(tmp_path: Path) -> None:
    """Both SessionStart dispatchers resolve the identical marker path."""
    claude = _load_dispatcher("claude")
    codex = _load_dispatcher("codex")
    assert claude._session_role_marker_path(tmp_path) == codex._session_role_marker_path(tmp_path)
    # And both equal the harness-agnostic .claude/session/ location.
    assert claude._session_role_marker_path(tmp_path) == _marker_path(tmp_path)


# ---------------------------------------------------------------------------
# Ordering invariant: invalidation runs before the dispatch fork and does not
# disturb the mode-switch-drain -> dispatch ordering. Source-inspection keeps
# this side-effect-free (executing main() would apply real pending mode-switch
# transactions against the live repo root).
# ---------------------------------------------------------------------------


def test_invalidation_ordered_before_dispatch_in_main() -> None:
    """In the shared core's main(), the invalidation call appears after
    _purge_previous_diagnostics and before both the mode-switch drain
    (apply_pending) and the dispatch check.

    Slice D of GTKB-STARTUP-REFRACTOR-001 single-sourced main() in
    scripts/session_start_dispatch_core.py; the thin wrappers delegate.
    """
    source = (REPO_ROOT / "scripts" / "session_start_dispatch_core.py").read_text(encoding="utf-8")
    main_idx = source.index("def main()")
    body = source[main_idx:]

    i_purge = body.index("_purge_previous_diagnostics(stdout_path")
    i_invalidate = body.index("_invalidate_session_role_marker()")
    i_apply_pending = body.index("apply_pending")
    i_dispatch = body.index("_bridge_dispatch_keyword_check()")

    assert i_purge < i_invalidate, "invalidation must run after diagnostics purge"
    assert i_invalidate < i_apply_pending, "invalidation must run before the mode-switch drain"
    assert i_apply_pending < i_dispatch, "mode-switch drain must still precede the dispatch check"


# ---------------------------------------------------------------------------
# WI-4540: per-session marker sweep (context-id-scoped + freshness retention).
# bridge/gtkb-wi4540-per-session-role-marker-context-envelope-003.md (GO -004).
# ---------------------------------------------------------------------------


def _per_session_path(project_root: Path, session_id: str) -> Path:
    from scripts.gtkb_session_id import per_session_role_marker_path

    return per_session_role_marker_path(project_root, session_id)


def _write_per_session(
    project_root: Path, session_id: str, *, role: str = "prime-builder", age_seconds: int = 0
) -> Path:
    path = _per_session_path(project_root, session_id)
    path.parent.mkdir(parents=True, exist_ok=True)
    written_at = (datetime.now(UTC) - timedelta(seconds=age_seconds)).isoformat().replace("+00:00", "Z")
    path.write_text(
        json.dumps({"role": role, "session_id": session_id, "written_at": written_at}, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return path


def test_per_session_marker_retained_for_current_context(dispatcher: ModuleType, tmp_path: Path) -> None:
    """DELIB-20263212: the current context's per-session marker SURVIVES a
    SessionStart that carries the same context id (even if it is old)."""
    marker = _write_per_session(tmp_path, "ctx-current", age_seconds=10 * 24 * 3600)  # very old
    dispatcher._sweep_stale_per_session_role_markers(tmp_path, current_session_id="ctx-current")
    assert marker.is_file(), "current context's per-session marker must survive the sweep"


def test_per_session_marker_concurrent_live_session_retained(dispatcher: ModuleType, tmp_path: Path) -> None:
    """WI-4463: a peer session's SessionStart does NOT delete another LIVE
    session's per-session marker (it is fresh, so freshness retention keeps it)."""
    peer = _write_per_session(tmp_path, "ctx-peer-live", age_seconds=5)  # fresh
    dispatcher._sweep_stale_per_session_role_markers(tmp_path, current_session_id="ctx-other")
    assert peer.is_file(), "a concurrent live session's marker must not be swept by a peer SessionStart"


def test_per_session_marker_stale_swept_live_retained(dispatcher: ModuleType, tmp_path: Path) -> None:
    """A stale per-session marker (older than the freshness window) is swept,
    while a fresh one is retained."""
    stale = _write_per_session(tmp_path, "ctx-stale", age_seconds=48 * 3600)
    fresh = _write_per_session(tmp_path, "ctx-fresh", age_seconds=30)
    dispatcher._sweep_stale_per_session_role_markers(tmp_path, current_session_id=None)
    assert not stale.exists(), "stale per-session marker should be swept"
    assert fresh.is_file(), "fresh per-session marker should be retained"


def test_legacy_invalidation_leaves_per_session_markers(dispatcher: ModuleType, tmp_path: Path) -> None:
    """The legacy single-file invalidation deletes only ``active-session-role.json``;
    per-session markers are untouched by it (the additive-transition separation)."""
    legacy = _write_marker(tmp_path)  # legacy single file
    per_session = _write_per_session(tmp_path, "ctx-keep", age_seconds=5)
    dispatcher._invalidate_session_role_marker(tmp_path)
    assert not legacy.exists(), "legacy single-file marker must be invalidated"
    assert per_session.is_file(), "per-session marker must NOT be touched by legacy invalidation"


def test_per_session_sweep_failsoft_on_missing_dir(dispatcher: ModuleType, tmp_path: Path) -> None:
    """The sweep is a silent no-op when the session dir does not exist."""
    dispatcher._sweep_stale_per_session_role_markers(tmp_path / "nonexistent", current_session_id=None)
    # No raise == pass.
