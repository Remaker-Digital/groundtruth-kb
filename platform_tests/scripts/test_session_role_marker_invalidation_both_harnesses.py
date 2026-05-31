"""Slice 10: subprocess-based regression for marker invalidation across both
SessionStart dispatchers.

bridge/gtkb-interactive-session-role-override-slice-10-regression-tests-005.md
(Codex GO at -006).

Module scope (per the slice proposal):

- Covers DCL-SESSION-ROLE-RESOLUTION-001 assertion 5 (the marker MUST NOT
  survive a SessionStart event) via subprocess isolation, complementing
  Slice 3's in-process direct-call tests in
  ``platform_tests/hooks/test_session_start_marker_invalidation.py``.
- Subprocess isolation catches dispatcher-level regressions that in-process
  importlib loading hides: e.g., a module-import-time side effect that
  would touch the marker path in production but not in a re-import within
  one pytest session.
- Coverage matrix: 4 marker-body variants (absent / clean / stale-session /
  malformed) × 2 dispatchers (Claude / Codex) via ``@pytest.mark.parametrize``.

The subprocess form invokes a small Python one-liner inside the spawned
interpreter that imports each dispatcher by file path and calls
``_invalidate_session_role_marker(tmp_path)``. This gives true subprocess
isolation without invoking the dispatcher's ``main()`` (which has a
hardcoded ``PROJECT_ROOT = Path(r"E:\\GT-KB")`` and would clobber the live
repo's marker).
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]

_DISPATCHERS = {
    "claude": REPO_ROOT / ".claude" / "hooks" / "session_start_dispatch.py",
    "codex": REPO_ROOT / ".codex" / "gtkb-hooks" / "session_start_dispatch.py",
}


def _marker_path(project_root: Path) -> Path:
    """Replicate the dispatcher's marker-path resolution under a fake root."""
    return project_root / ".claude" / "session" / "active-session-role.json"


def _write_marker(project_root: Path, body: str) -> Path:
    marker = _marker_path(project_root)
    marker.parent.mkdir(parents=True, exist_ok=True)
    marker.write_text(body, encoding="utf-8")
    return marker


def _run_invalidation_subprocess(dispatcher_path: Path, project_root: Path) -> subprocess.CompletedProcess[str]:
    """Spawn a fresh Python interpreter that loads ``dispatcher_path`` by file
    location and calls ``_invalidate_session_role_marker(project_root)``.

    Using ``importlib.util.spec_from_file_location`` avoids depending on
    sys.path resolution of the dispatcher module name, and the bare
    ``-c`` invocation ensures no cached bytecode from this pytest process
    is reused.
    """
    program = (
        "import importlib.util, sys\n"
        f"spec = importlib.util.spec_from_file_location('_subproc_dispatcher', r'{dispatcher_path}')\n"
        "module = importlib.util.module_from_spec(spec)\n"
        "spec.loader.exec_module(module)\n"
        f"module._invalidate_session_role_marker(__import__('pathlib').Path(r'{project_root}'))\n"
    )
    return subprocess.run(
        [sys.executable, "-c", program],
        capture_output=True,
        text=True,
        timeout=30,
        check=False,
    )


@pytest.fixture(params=sorted(_DISPATCHERS))
def dispatcher_path(request: pytest.FixtureRequest) -> Path:
    return _DISPATCHERS[request.param]


# ---------------------------------------------------------------------------
# Assertion 5: marker absent before invocation — subprocess is a no-op.
# ---------------------------------------------------------------------------


def test_subprocess_invalidation_noop_when_marker_absent(
    dispatcher_path: Path,
    tmp_path: Path,
) -> None:
    """Calling the dispatcher's invalidation helper in a fresh interpreter when
    no marker exists must succeed silently — the helper is fail-soft on
    FileNotFoundError and must not raise from a subprocess either.
    """
    result = _run_invalidation_subprocess(dispatcher_path, tmp_path)
    assert result.returncode == 0, f"invalidation subprocess failed: stderr={result.stderr!r}"
    assert not _marker_path(tmp_path).exists()


# ---------------------------------------------------------------------------
# Assertion 5: clean marker is deleted by a fresh-interpreter invocation.
# ---------------------------------------------------------------------------


def test_subprocess_invalidation_removes_clean_marker(
    dispatcher_path: Path,
    tmp_path: Path,
) -> None:
    """A well-formed marker (valid JSON, valid role, valid session_id) is
    deleted by the dispatcher's invalidation call. This is the load-bearing
    case for the ephemeral-marker contract: any session-stated role
    declaration from a prior session must be erased before this
    SessionStart's role-rendering path runs.
    """
    body = json.dumps({"role": "loyal-opposition", "session_id": "S375-clean-marker"})
    marker = _write_marker(tmp_path, body)
    assert marker.is_file(), "fixture failed to write marker"

    result = _run_invalidation_subprocess(dispatcher_path, tmp_path)
    assert result.returncode == 0, f"invalidation subprocess failed: stderr={result.stderr!r}"
    assert not marker.exists(), "marker survived subprocess invalidation"


# ---------------------------------------------------------------------------
# Assertion 5: stale-session-id marker is deleted unconditionally.
# ---------------------------------------------------------------------------


def test_subprocess_invalidation_removes_stale_session_marker(
    dispatcher_path: Path,
    tmp_path: Path,
) -> None:
    """A marker whose session_id is from a prior session is still deleted —
    invalidation is unconditional on marker body content.

    This complements the resolver-side stale-marker check (Module 1): even
    if SessionStart invalidation runs after the resolver has already
    treated the marker as stale-and-ignored, the dispatcher still removes
    the file so subsequent reads see the absent state. The two checks form
    layered defense.
    """
    body = json.dumps({"role": "prime-builder", "session_id": "S100-ancient-stale-session-id"})
    marker = _write_marker(tmp_path, body)
    assert marker.is_file()

    result = _run_invalidation_subprocess(dispatcher_path, tmp_path)
    assert result.returncode == 0, f"invalidation subprocess failed: stderr={result.stderr!r}"
    assert not marker.exists(), "stale-session marker was not invalidated"


# ---------------------------------------------------------------------------
# Assertion 5: malformed marker is deleted unconditionally.
# ---------------------------------------------------------------------------


def test_subprocess_invalidation_removes_malformed_marker(
    dispatcher_path: Path,
    tmp_path: Path,
) -> None:
    """Invalidation does not parse the marker before deleting it — a
    corrupt JSON body must still be removed so the next SessionStart
    starts from a clean slate. A parsing-then-deleting implementation
    would fail to clear malformed markers and leave the next session's
    resolver to handle the corruption.
    """
    marker = _write_marker(tmp_path, "{not valid json at all")
    assert marker.is_file()

    result = _run_invalidation_subprocess(dispatcher_path, tmp_path)
    assert result.returncode == 0, f"invalidation subprocess failed: stderr={result.stderr!r}"
    assert not marker.exists(), "malformed marker was not invalidated"
