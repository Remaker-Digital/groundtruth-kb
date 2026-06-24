# © 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""PASS/WARN/FAIL coverage for ``_check_cross_harness_trigger``.

Per Slice 4 D4 (proposal
`bridge/gtkb-bridge-poller-event-driven-replacement-slice-4-smart-poller-retirement-001-015.md`)
the doctor's smart-poller end-to-end activation check was replaced by a
cross-harness event-driven trigger check. Three subchecks, three
representative outcome scenarios per `T-4-doctor-cross-harness-trigger-coverage`.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

import groundtruth_kb.bridge_dispatch_config as bridge_dispatch_config
from groundtruth_kb.project.doctor import _check_cross_harness_trigger


@pytest.fixture(autouse=True)
def _no_cross_harness_trigger_disable(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.delenv(bridge_dispatch_config.CROSS_HARNESS_TRIGGER_DISABLE_ENV_VAR, raising=False)
    monkeypatch.setattr(bridge_dispatch_config, "_read_windows_persistent_env_var", lambda _name, _scope: None)


def _make_settings(target: Path, *, with_post_tool_use: bool, with_stop: bool) -> Path:
    """Write a minimal `.claude/settings.json` with the requested hook entries."""
    settings = {"hooks": {}}
    hook_entry = [
        {
            "hooks": [
                {
                    "type": "command",
                    "command": 'python "$CLAUDE_PROJECT_DIR/scripts/cross_harness_bridge_trigger.py"',
                }
            ]
        }
    ]
    if with_post_tool_use:
        settings["hooks"]["PostToolUse"] = hook_entry
    if with_stop:
        settings["hooks"]["Stop"] = hook_entry

    claude_dir = target / ".claude"
    claude_dir.mkdir(parents=True, exist_ok=True)
    out = claude_dir / "settings.json"
    out.write_text(json.dumps(settings, indent=2), encoding="utf-8")
    return out


def _make_trigger_script(target: Path) -> Path:
    """Write a placeholder cross-harness trigger script under scripts/."""
    scripts_dir = target / "scripts"
    scripts_dir.mkdir(parents=True, exist_ok=True)
    out = scripts_dir / "cross_harness_bridge_trigger.py"
    out.write_text("# placeholder for doctor surface test\n", encoding="utf-8")
    return out


def _make_dispatch_state(target: Path) -> Path:
    state_dir = target / ".gtkb-state" / "bridge-poller"
    state_dir.mkdir(parents=True, exist_ok=True)
    out = state_dir / "dispatch-state.json"
    out.write_text('{"schema_version": 1, "recipients": {}}', encoding="utf-8")
    return out


# ============================================================================
# PASS scenario
# ============================================================================


def test_pass_when_script_settings_and_dispatch_state_all_present(tmp_path: Path) -> None:
    """All three subchecks satisfied → PASS."""
    _make_trigger_script(tmp_path)
    _make_settings(tmp_path, with_post_tool_use=True, with_stop=True)
    _make_dispatch_state(tmp_path)

    result = _check_cross_harness_trigger(tmp_path)
    assert result.status == "pass"
    assert "active" in result.message.lower()
    assert "cross-harness" in result.message.lower() or "cross-harness event-driven trigger" in result.message.lower()


# ============================================================================
# WARN scenario
# ============================================================================


def test_warn_when_dispatch_state_absent_but_script_and_hooks_present(tmp_path: Path) -> None:
    """Trigger registered but has not yet fired → WARN (steady state)."""
    _make_trigger_script(tmp_path)
    _make_settings(tmp_path, with_post_tool_use=True, with_stop=True)
    # No dispatch-state.json

    result = _check_cross_harness_trigger(tmp_path)
    assert result.status == "warning"
    assert "not yet fired" in result.message.lower() or "dispatch-state.json absent" in result.message.lower()


def test_warn_when_process_kill_switch_is_active(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Process-scope operator kill-switch is visible before dispatch-state can mask it."""
    _make_trigger_script(tmp_path)
    _make_settings(tmp_path, with_post_tool_use=True, with_stop=True)
    _make_dispatch_state(tmp_path)
    monkeypatch.setenv(bridge_dispatch_config.CROSS_HARNESS_TRIGGER_DISABLE_ENV_VAR, "1")

    result = _check_cross_harness_trigger(tmp_path)

    assert result.status == "warning"
    assert bridge_dispatch_config.CROSS_HARNESS_TRIGGER_DISABLE_ENV_VAR in result.message
    assert "Process" in result.message
    assert "no-op" in result.message


def test_warn_when_user_scope_kill_switch_is_active(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Persistent User-scope kill-switch is reported without mutating the real environment."""
    _make_trigger_script(tmp_path)
    _make_settings(tmp_path, with_post_tool_use=True, with_stop=True)
    _make_dispatch_state(tmp_path)

    def _persistent_reader(_name: str, scope: str) -> str | None:
        return "1" if scope == "User" else None

    monkeypatch.setattr(bridge_dispatch_config, "_read_windows_persistent_env_var", _persistent_reader)

    result = _check_cross_harness_trigger(tmp_path)

    assert result.status == "warning"
    assert bridge_dispatch_config.CROSS_HARNESS_TRIGGER_DISABLE_ENV_VAR in result.message
    assert "User" in result.message
    assert "no-op" in result.message


# ============================================================================
# FAIL scenarios
# ============================================================================


def test_fail_when_trigger_script_missing(tmp_path: Path) -> None:
    """Script absent → FAIL with installation guidance."""
    _make_settings(tmp_path, with_post_tool_use=True, with_stop=True)

    result = _check_cross_harness_trigger(tmp_path)
    assert result.status == "fail"
    assert "cross_harness_bridge_trigger.py" in result.message


def test_fail_when_settings_json_missing(tmp_path: Path) -> None:
    """`.claude/settings.json` absent → FAIL."""
    _make_trigger_script(tmp_path)

    result = _check_cross_harness_trigger(tmp_path)
    assert result.status == "fail"
    assert "settings.json" in result.message


def test_fail_when_post_tool_use_hook_not_registered(tmp_path: Path) -> None:
    """Trigger script present, settings present, but PostToolUse hook missing → FAIL."""
    _make_trigger_script(tmp_path)
    _make_settings(tmp_path, with_post_tool_use=False, with_stop=True)

    result = _check_cross_harness_trigger(tmp_path)
    assert result.status == "fail"
    assert "PostToolUse" in result.message


def test_fail_when_stop_hook_not_registered(tmp_path: Path) -> None:
    """Trigger script present, settings present, but Stop hook missing → FAIL."""
    _make_trigger_script(tmp_path)
    _make_settings(tmp_path, with_post_tool_use=True, with_stop=False)

    result = _check_cross_harness_trigger(tmp_path)
    assert result.status == "fail"
    assert "Stop" in result.message
