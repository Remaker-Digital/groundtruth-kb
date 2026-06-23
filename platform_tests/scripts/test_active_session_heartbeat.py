# (c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""Tests for scripts/active_session_heartbeat.py.

Per ``bridge/gtkb-cross-harness-trigger-active-session-suppression-001-005.md``
GO at ``-006`` (REVISED-2):

The heartbeat script writes/refreshes/deletes a per-role active-session
lock file at ``<state-dir>/active-{role}-session.lock``. The cross-harness
trigger reads the same path to detect when a counterpart harness holds a
foreground session and should suppress dispatch to that role.

These tests cover the heartbeat script in isolation. Integration with the
trigger's suppression gate is covered in
``test_cross_harness_bridge_trigger.py``.
"""

from __future__ import annotations

import importlib.util
import json
import sys
import time
from pathlib import Path

import pytest

_REPO_ROOT = Path(__file__).resolve().parents[2]
_SCRIPT_PATH = _REPO_ROOT / "scripts" / "active_session_heartbeat.py"


@pytest.fixture(scope="module")
def heartbeat_module():
    """Load active_session_heartbeat.py as a module for direct function calls.

    Tests exercise the helper functions directly (not via the CLI argparse
    front door) so failures show clearer assertion messages and avoid
    spawning subprocesses for every test.
    """
    assert _SCRIPT_PATH.is_file(), f"Missing {_SCRIPT_PATH}"
    spec = importlib.util.spec_from_file_location("active_session_heartbeat", _SCRIPT_PATH)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules["active_session_heartbeat"] = module
    spec.loader.exec_module(module)
    return module


def test_heartbeat_session_start_creates_lock(heartbeat_module, tmp_path: Path) -> None:
    """T-HB-session-start-creates-lock: --mode session-start writes the lock file with current timestamp."""
    heartbeat_module._handle_session_start(
        tmp_path,
        "claude",
        interactive_role="prime-builder",
        interactive_role_source="init_keyword",
        durable_registry_role="loyal-opposition",
    )
    lock = tmp_path / "active-claude-session.lock"
    assert lock.is_file()
    payload = json.loads(lock.read_text(encoding="utf-8"))
    assert "opened_at" in payload
    assert "last_refreshed" in payload
    assert payload["opened_at"] == payload["last_refreshed"]
    assert payload["harness_name"] == "claude"
    assert payload["role_authority"]["interactive_resolved_role"] == "prime-builder"
    assert payload["role_authority"]["interactive_role_source"] == "init_keyword"
    assert payload["role_authority"]["durable_registry_role"] == "loyal-opposition"
    assert payload["role_authority"]["authority_mode"] == "interactive_transcript"


def test_heartbeat_tool_use_refreshes_existing_lock(heartbeat_module, tmp_path: Path) -> None:
    """T-HB-tool-use-refreshes-mtime: when a lock exists, --mode tool-use updates last_refreshed
    but preserves opened_at.
    """
    heartbeat_module._handle_session_start(tmp_path, "codex")
    lock = tmp_path / "active-codex-session.lock"
    initial = json.loads(lock.read_text(encoding="utf-8"))
    initial_opened_at = initial["opened_at"]

    # Sleep > 1s so the timestamp string actually changes (ISO seconds resolution).
    time.sleep(1.1)
    heartbeat_module._handle_tool_use(tmp_path, "codex")

    refreshed = json.loads(lock.read_text(encoding="utf-8"))
    assert refreshed["opened_at"] == initial_opened_at, "opened_at must persist across tool-use"
    assert refreshed["last_refreshed"] != initial_opened_at, "last_refreshed must update"
    assert refreshed["role_authority"]["harness_name"] == "codex"


def test_heartbeat_tool_use_creates_when_absent(heartbeat_module, tmp_path: Path) -> None:
    """T-HB-tool-use-creates-when-absent (defensive): if SessionStart hook failed to fire, tool-use creates the lock."""
    lock = tmp_path / "active-claude-session.lock"
    assert not lock.exists()

    heartbeat_module._handle_tool_use(tmp_path, "claude")
    assert lock.is_file()
    payload = json.loads(lock.read_text(encoding="utf-8"))
    assert "opened_at" in payload
    assert "last_refreshed" in payload


def test_atomic_write_json_retries_transient_replace_permission_error(
    heartbeat_module, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """T-HB-retry-transient-replace-denied: a one-shot Windows replace race is retried."""
    lock = tmp_path / "active-codex-session.lock"
    original_replace = heartbeat_module.os.replace
    calls: list[tuple[str, str]] = []

    def _flaky_replace(src: str, dst: str) -> None:
        calls.append((src, dst))
        if len(calls) == 1:
            raise PermissionError("simulated transient access denied")
        original_replace(src, dst)

    monkeypatch.setattr(heartbeat_module.os, "replace", _flaky_replace)
    monkeypatch.setattr(heartbeat_module, "REPLACE_RETRY_DELAYS_SECONDS", (0.0,))

    heartbeat_module._atomic_write_json(lock, {"ok": True})

    assert len(calls) == 2
    assert lock.is_file()
    assert json.loads(lock.read_text(encoding="utf-8")) == {"ok": True}


def test_heartbeat_session_stop_removes_lock(heartbeat_module, tmp_path: Path) -> None:
    """T-HB-session-stop-removes-lock: --mode session-stop deletes the lock."""
    heartbeat_module._handle_session_start(tmp_path, "claude")
    lock = tmp_path / "active-claude-session.lock"
    assert lock.is_file()

    heartbeat_module._handle_session_stop(tmp_path, "claude")
    assert not lock.exists()


def test_heartbeat_session_stop_idempotent(heartbeat_module, tmp_path: Path) -> None:
    """T-HB-session-stop-idempotent: --mode session-stop on absent lock exits 0; no exception."""
    lock = tmp_path / "active-codex-session.lock"
    assert not lock.exists()

    # Should not raise.
    heartbeat_module._handle_session_stop(tmp_path, "codex")
    assert not lock.exists()


def test_heartbeat_main_requires_state_dir(heartbeat_module) -> None:
    """T-SUPPRESS-heartbeat-script-requires-state-dir: argparse must reject missing --state-dir.

    Per the GO'd proposal F1 fix, --state-dir is REQUIRED (no default). The
    hook registration must pass the same path the trigger uses; making the
    coupling explicit at config time eliminates the silent failure mode.
    """
    with pytest.raises(SystemExit) as exc_info:
        heartbeat_module.main(["--mode", "tool-use", "--role", "claude"])
    assert exc_info.value.code != 0


def test_heartbeat_main_respects_state_dir(heartbeat_module, tmp_path: Path) -> None:
    """T-SUPPRESS-heartbeat-script-respects-state-dir: lock file is written under --state-dir, not a hidden default."""
    custom_dir = tmp_path / "custom-heartbeat-dir"
    rc = heartbeat_module.main(
        [
            "--mode",
            "session-start",
            "--role",
            "codex",
            "--state-dir",
            str(custom_dir),
        ]
    )
    assert rc == 0
    assert (custom_dir / "active-codex-session.lock").is_file()


def test_heartbeat_main_requires_source_when_interactive_and_durable_roles_differ(
    heartbeat_module, tmp_path: Path
) -> None:
    """T-HB-role-authority-fail-closed: differing interactive/durable roles require an explicit source."""
    with pytest.raises(SystemExit) as exc_info:
        heartbeat_module.main(
            [
                "--mode",
                "session-start",
                "--role",
                "codex",
                "--state-dir",
                str(tmp_path),
                "--interactive-role",
                "pb",
                "--durable-role",
                "lo",
            ]
        )
    assert exc_info.value.code != 0
    assert not (tmp_path / "active-codex-session.lock").exists()


def test_heartbeat_main_records_split_role_authority(heartbeat_module, tmp_path: Path) -> None:
    """T-HB-role-authority-payload: lock discloses interactive role/source and durable role separately."""
    rc = heartbeat_module.main(
        [
            "--mode",
            "session-start",
            "--role",
            "codex",
            "--state-dir",
            str(tmp_path),
            "--interactive-role",
            "pb",
            "--interactive-role-source",
            "init_keyword",
            "--durable-role",
            "lo",
        ]
    )
    assert rc == 0
    payload = json.loads((tmp_path / "active-codex-session.lock").read_text(encoding="utf-8"))
    assert payload["role_authority"]["interactive_resolved_role"] == "prime-builder"
    assert payload["role_authority"]["interactive_role_source"] == "init_keyword"
    assert payload["role_authority"]["durable_registry_role"] == "loyal-opposition"
    assert "non-overriding" in payload["role_authority"]["durable_registry_authority"]


def test_heartbeat_fire_and_forget_on_error(heartbeat_module, tmp_path: Path) -> None:
    """T-HB-fire-and-forget-on-error: even on internal exception, main() returns 0.

    The script must never block the hook chain. We force an exception by
    monkeypatching _atomic_write_json to raise; main() must still exit 0.
    """
    # Save originals to restore.
    original = heartbeat_module._atomic_write_json

    def _raise(*_args, **_kwargs):
        raise RuntimeError("simulated write failure")

    heartbeat_module._atomic_write_json = _raise
    try:
        rc = heartbeat_module.main(
            [
                "--mode",
                "session-start",
                "--role",
                "claude",
                "--state-dir",
                str(tmp_path),
            ]
        )
        assert rc == 0
    finally:
        heartbeat_module._atomic_write_json = original
