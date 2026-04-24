"""Regression tests for GT-KB workstream focus hooks."""

from __future__ import annotations

import importlib.util
import json
import os
import subprocess
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
MODULE_PATH = REPO_ROOT / "scripts" / "workstream_focus.py"
HOOK_PATH = REPO_ROOT / ".claude" / "hooks" / "workstream-focus.py"


def _load_module():
    spec = importlib.util.spec_from_file_location("workstream_focus", MODULE_PATH)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules["workstream_focus"] = module
    spec.loader.exec_module(module)
    return module


def _run_hook(payload: dict, state_path: Path, *, guard_path: Path | None = None) -> dict:
    env = {
        **dict(os.environ),
        "GTKB_WORKSTREAM_FOCUS_STATE": str(state_path),
        "CLAUDE_PROJECT_DIR": str(REPO_ROOT),
    }
    effective_guard_path = guard_path or (state_path.parent / "lifecycle-guard.json")
    env["GTKB_LIFECYCLE_GUARD_PATH"] = str(effective_guard_path)
    result = subprocess.run(
        [sys.executable, str(HOOK_PATH)],
        cwd=REPO_ROOT,
        env=env,
        input=json.dumps(payload),
        text=True,
        capture_output=True,
        timeout=10,
        check=True,
    )
    return json.loads(result.stdout)


def test_default_focus_is_application_and_startup_lines_explain_commands(tmp_path, monkeypatch) -> None:
    module = _load_module()
    monkeypatch.setenv("GTKB_WORKSTREAM_FOCUS_STATE", str(tmp_path / "focus.json"))
    monkeypatch.setenv("GTKB_LIFECYCLE_GUARD_PATH", str(tmp_path / "guard.json"))

    state = module.load_state(REPO_ROOT)
    lines = module.render_startup_focus_lines(module.startup_focus_snapshot(REPO_ROOT))

    assert state["default_focus"] == module.FOCUS_APPLICATION
    assert state["current_focus"] == module.FOCUS_APPLICATION
    assert "Default focus: Application Focus" in lines
    assert "Current focus: Application Focus" in lines
    assert "`application mode`" in lines
    assert "`GT-KB mode`" in lines


@pytest.mark.skip(reason="workstream-focus.py intentionally retired S304/S305; see REVISED-5 BN-3")
def test_prompt_hook_switches_focus_with_standalone_commands(tmp_path) -> None:
    state_path = tmp_path / "focus.json"

    response = _run_hook({"user_prompt": "GT-KB mode"}, state_path)
    assert "GT-KB Infrastructure Focus" in response["systemMessage"]
    assert json.loads(state_path.read_text(encoding="utf-8"))["current_focus"] == "gtkb_infrastructure"

    response = _run_hook({"user_prompt": "please application mode."}, state_path)
    assert "Application Focus" in response["systemMessage"]
    assert json.loads(state_path.read_text(encoding="utf-8"))["current_focus"] == "application"


def test_prompt_hook_toggles_next_session_role_with_simple_phrase(tmp_path, monkeypatch) -> None:
    module = _load_module()
    role_path = tmp_path / "operating-role.md"
    role_path.write_text("active_role: loyal-opposition\n", encoding="utf-8")
    monkeypatch.setenv("GTKB_OPERATING_ROLE_PATH", str(role_path))
    monkeypatch.setenv("GTKB_LIFECYCLE_GUARD_PATH", str(tmp_path / "guard.json"))

    response = module.handle_user_prompt("switch mode next session", REPO_ROOT)

    assert "Next fresh-session operating mode set to Prime Builder" in response["systemMessage"]
    assert role_path.read_text(encoding="utf-8") == "active_role: prime-builder\n"

    response = module.handle_user_prompt("please change mode next session.", REPO_ROOT)

    assert "Next fresh-session operating mode set to Loyal Opposition" in response["systemMessage"]
    assert role_path.read_text(encoding="utf-8") == "active_role: loyal-opposition\n"


def test_prompt_hook_sets_explicit_next_session_role(tmp_path, monkeypatch) -> None:
    module = _load_module()
    role_path = tmp_path / "operating-role.md"
    role_path.write_text("active_role: loyal-opposition\n", encoding="utf-8")
    monkeypatch.setenv("GTKB_OPERATING_ROLE_PATH", str(role_path))
    monkeypatch.setenv("GTKB_LIFECYCLE_GUARD_PATH", str(tmp_path / "guard.json"))

    response = module.handle_user_prompt("prime builder mode next session", REPO_ROOT)

    assert "Next fresh-session operating mode set to Prime Builder" in response["systemMessage"]
    assert role_path.read_text(encoding="utf-8") == "active_role: prime-builder\n"


def test_prompt_hook_toggles_dashboard_auto_launch(tmp_path, monkeypatch) -> None:
    module = _load_module()
    preferences_path = tmp_path / "session-startup-preferences.json"
    monkeypatch.setenv("GTKB_STARTUP_PREFERENCES_PATH", str(preferences_path))
    monkeypatch.setenv("GTKB_LIFECYCLE_GUARD_PATH", str(tmp_path / "guard.json"))

    response = module.handle_user_prompt("enable dashboard", REPO_ROOT)

    assert "Dashboard auto-launch is enabled" in response["systemMessage"]
    assert json.loads(preferences_path.read_text(encoding="utf-8"))["open_dashboard_on_session_start"] is True

    response = module.handle_user_prompt("disable dashboard", REPO_ROOT)

    assert "Dashboard auto-launch is disabled" in response["systemMessage"]
    assert json.loads(preferences_path.read_text(encoding="utf-8"))["open_dashboard_on_session_start"] is False


@pytest.mark.skip(reason="workstream-focus.py intentionally retired S304/S305; see REVISED-5 BN-3")
def test_prompt_hook_discards_first_fresh_session_message_when_startup_gate_is_armed(tmp_path) -> None:
    state_path = tmp_path / "focus.json"
    guard_path = tmp_path / "guard.json"
    guard_path.write_text(
        json.dumps(
            {
                "discard_next_user_prompt": True,
                "startup_guard_id": "test-guard",
                "startup_response_pending": False,
            }
        )
        + "\n",
        encoding="utf-8",
    )

    response = _run_hook({"user_prompt": "Please resume."}, state_path, guard_path=guard_path)

    assert "first owner message of a fresh session is never actionable" in response["systemMessage"]
    assert response["hookSpecificOutput"]["hookEventName"] == "UserPromptSubmit"
    assert "startup disclosure already generated for this session" in response["hookSpecificOutput"]["additionalContext"]

    guard_state = json.loads(guard_path.read_text(encoding="utf-8"))
    assert guard_state["discard_next_user_prompt"] is False
    assert guard_state["startup_prompt_discarded"] is True
    assert guard_state["startup_response_pending"] is True
    assert guard_state["startup_prompt_preview"] == "Please resume."


@pytest.mark.skip(reason="workstream-focus.py intentionally retired S304/S305; see REVISED-5 BN-3")
def test_startup_response_pending_clears_on_next_owner_prompt_and_allows_normal_processing(tmp_path) -> None:
    state_path = tmp_path / "focus.json"
    guard_path = tmp_path / "guard.json"
    guard_path.write_text(
        json.dumps(
            {
                "discard_next_user_prompt": False,
                "startup_guard_id": "test-guard",
                "startup_prompt_discarded": True,
                "startup_response_pending": True,
            }
        )
        + "\n",
        encoding="utf-8",
    )

    response = _run_hook({"user_prompt": "GT-KB mode"}, state_path, guard_path=guard_path)

    assert "GT-KB Infrastructure Focus" in response["systemMessage"]
    assert json.loads(state_path.read_text(encoding="utf-8"))["current_focus"] == "gtkb_infrastructure"
    guard_state = json.loads(guard_path.read_text(encoding="utf-8"))
    assert guard_state["startup_response_pending"] is False
    assert guard_state["startup_input_gate_cleared_at"]


def test_application_focus_blocks_gtkb_infrastructure_write(tmp_path, monkeypatch) -> None:
    module = _load_module()
    monkeypatch.setenv("GTKB_WORKSTREAM_FOCUS_STATE", str(tmp_path / "focus.json"))
    monkeypatch.setenv("GTKB_LIFECYCLE_GUARD_PATH", str(tmp_path / "guard.json"))

    response = module.guard_tool_use(
        {"tool_name": "Write", "tool_input": {"file_path": ".claude/rules/new-rule.md"}},
        REPO_ROOT,
    )

    assert response["decision"] == "block"
    assert "Application Focus" in response["reason"]
    assert "GT-KB mode" in response["reason"]


def test_application_focus_allows_application_write(tmp_path, monkeypatch) -> None:
    module = _load_module()
    monkeypatch.setenv("GTKB_WORKSTREAM_FOCUS_STATE", str(tmp_path / "focus.json"))
    monkeypatch.setenv("GTKB_LIFECYCLE_GUARD_PATH", str(tmp_path / "guard.json"))

    response = module.guard_tool_use(
        {"tool_name": "Write", "tool_input": {"file_path": "src/example.py"}},
        REPO_ROOT,
    )

    assert response == {}


def test_gtkb_focus_blocks_application_write(tmp_path, monkeypatch) -> None:
    module = _load_module()
    monkeypatch.setenv("GTKB_WORKSTREAM_FOCUS_STATE", str(tmp_path / "focus.json"))
    monkeypatch.setenv("GTKB_LIFECYCLE_GUARD_PATH", str(tmp_path / "guard.json"))
    module.save_state(module.FOCUS_GTKB_INFRASTRUCTURE, REPO_ROOT)

    response = module.guard_tool_use(
        {"tool_name": "Write", "tool_input": {"file_path": "src/example.py"}},
        REPO_ROOT,
    )

    assert response["decision"] == "block"
    assert "GT-KB Infrastructure Focus" in response["reason"]
    assert "application mode" in response["reason"]


def test_startup_response_pending_blocks_tool_use_until_next_owner_prompt(tmp_path, monkeypatch) -> None:
    module = _load_module()
    guard_path = tmp_path / "guard.json"
    monkeypatch.setenv("GTKB_WORKSTREAM_FOCUS_STATE", str(tmp_path / "focus.json"))
    monkeypatch.setenv("GTKB_LIFECYCLE_GUARD_PATH", str(guard_path))
    guard_path.write_text(
        json.dumps(
            {
                "discard_next_user_prompt": False,
                "startup_prompt_discarded": True,
                "startup_response_pending": True,
            }
        )
        + "\n",
        encoding="utf-8",
    )

    response = module.guard_tool_use(
        {"tool_name": "Write", "tool_input": {"file_path": "src/example.py"}},
        REPO_ROOT,
    )

    assert response["decision"] == "block"
    assert "GTKB-STARTUP-INPUT-GATE" in response["reason"]
    assert "Present the startup disclosure" in response["reason"]


def test_bash_guard_only_blocks_mutating_gtkb_commands(tmp_path, monkeypatch) -> None:
    module = _load_module()
    monkeypatch.setenv("GTKB_WORKSTREAM_FOCUS_STATE", str(tmp_path / "focus.json"))

    read_response = module.guard_tool_use(
        {"tool_name": "Bash", "tool_input": {"command": "Get-Content .claude/rules/prime-builder-role.md"}},
        REPO_ROOT,
    )
    write_response = module.guard_tool_use(
        {
            "tool_name": "Bash",
            "tool_input": {"command": "Set-Content .claude/rules/new-rule.md 'text'"},
        },
        REPO_ROOT,
    )

    assert read_response == {}
    assert write_response["decision"] == "block"
