# (c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""Stop-hook regression test for active_session_heartbeat.py.

Verifies SPEC-INTAKE-57a736 Clause 5 and Clause 6: session-stop mode
does not write a fresh active-session heartbeat on session end (it only deletes
the lock file, and does not recreate it defensively if it is already absent).
"""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import pytest

_REPO_ROOT = Path(__file__).resolve().parents[2]
_SCRIPT_PATH = _REPO_ROOT / "scripts" / "active_session_heartbeat.py"


@pytest.fixture(scope="module")
def heartbeat_module():
    """Load active_session_heartbeat.py as a module for direct function calls."""
    assert _SCRIPT_PATH.is_file(), f"Missing {_SCRIPT_PATH}"
    spec = importlib.util.spec_from_file_location("active_session_heartbeat_stop", _SCRIPT_PATH)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules["active_session_heartbeat_stop"] = module
    spec.loader.exec_module(module)
    return module


def test_stop_mode_does_not_write_fresh_heartbeat(heartbeat_module, tmp_path: Path) -> None:
    """T-HB-stop-mode-writes-no-fresh-heartbeat: --mode session-stop does not write/recreate a lock file."""
    lock = tmp_path / "active-claude-session.lock"
    assert not lock.exists()

    # 1. When called with an absent lock, it must remain absent (no defensive creation)
    heartbeat_module._handle_session_stop(tmp_path, "claude")
    assert not lock.exists()

    # 2. When lock exists, it must delete it
    heartbeat_module._handle_session_start(tmp_path, "claude")
    assert lock.is_file()

    heartbeat_module._handle_session_stop(tmp_path, "claude")
    assert not lock.exists()
