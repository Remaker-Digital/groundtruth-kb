"""Regression tests for GT-KB workstream focus / work-subject hooks."""

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


def _isolate_state(monkeypatch, tmp_path: Path) -> tuple[Path, Path]:
    canonical = tmp_path / "work-subject.json"
    legacy = tmp_path / ".workstream-focus-state.json"
    monkeypatch.setenv("GTKB_WORKSTREAM_FOCUS_STATE", str(canonical))
    monkeypatch.setenv("GTKB_WORKSTREAM_FOCUS_LEGACY_STATE", str(legacy))
    monkeypatch.setenv("GTKB_LIFECYCLE_GUARD_PATH", str(tmp_path / "guard.json"))
    monkeypatch.delenv("GTKB_PRODUCT_ROOT", raising=False)
    return canonical, legacy


def test_default_work_subject_is_application_and_startup_lines_explain_commands(tmp_path, monkeypatch) -> None:
    module = _load_module()
    _isolate_state(monkeypatch, tmp_path)

    state = module.load_state(REPO_ROOT)
    lines = module.render_startup_focus_lines(module.startup_focus_snapshot(REPO_ROOT))

    assert state["default_focus"] == module.FOCUS_APPLICATION
    assert state["current_focus"] == module.FOCUS_APPLICATION
    assert state["current_subject"] == module.SUBJECT_APPLICATION
    assert state["schema_version"] == module.SCHEMA_VERSION
    assert state["role_slot"] == module.ROLE_SLOT_DEFAULT
    assert "Default work subject: Application Focus" in lines
    assert "Current work subject: Application Focus" in lines
    assert "`work subject application`" in lines
    assert "`work subject GT-KB`" in lines
    assert "`application mode`" in lines
    assert "`GT-KB mode`" in lines
    assert ".claude/session/work-subject.json" in lines


def test_canonical_state_file_written_under_claude_session(tmp_path, monkeypatch) -> None:
    module = _load_module()
    canonical, _ = _isolate_state(monkeypatch, tmp_path)

    module.save_state(module.FOCUS_GTKB_INFRASTRUCTURE, REPO_ROOT, updated_by="owner_prompt")

    assert canonical.exists()
    data = json.loads(canonical.read_text(encoding="utf-8"))
    assert data["schema_version"] == module.SCHEMA_VERSION
    assert data["current_subject"] == module.SUBJECT_GTKB
    assert data["role_slot"] == module.ROLE_SLOT_DEFAULT
    assert data["source"] == "standalone owner command"
    assert data["updated_by"] == "owner_prompt"
    assert data["updated_at"]
    assert data["project_root"]
    # gtkb_root may be None; key must exist.
    assert "gtkb_root" in data


def test_legacy_state_migrates_on_load_when_canonical_absent(tmp_path, monkeypatch) -> None:
    module = _load_module()
    _, legacy = _isolate_state(monkeypatch, tmp_path)

    legacy.write_text(
        json.dumps(
            {
                "default_focus": "application",
                "current_focus": "gtkb_infrastructure",
                "application_label": "Agent Red",
                "updated_at": "2026-04-01T00:00:00Z",
                "updated_by": "owner_prompt",
            }
        )
        + "\n",
        encoding="utf-8",
    )

    state = module.load_state(REPO_ROOT)
    assert state["current_subject"] == module.SUBJECT_GTKB
    assert state["current_focus"] == module.FOCUS_GTKB_INFRASTRUCTURE
    assert state["source"] == "legacy workstream alias"


def test_work_subject_application_command_sets_canonical_state(tmp_path, monkeypatch) -> None:
    module = _load_module()
    canonical, _ = _isolate_state(monkeypatch, tmp_path)
    # Seed GT-KB so the command flips state.
    module.save_state(module.FOCUS_GTKB_INFRASTRUCTURE, REPO_ROOT)

    response = module.handle_user_prompt("work subject application", REPO_ROOT)

    assert "Current work subject set to Application Focus" in response["systemMessage"]
    data = json.loads(canonical.read_text(encoding="utf-8"))
    assert data["current_subject"] == module.SUBJECT_APPLICATION


def test_work_subject_gtkb_command_sets_canonical_state(tmp_path, monkeypatch) -> None:
    module = _load_module()
    canonical, _ = _isolate_state(monkeypatch, tmp_path)

    response = module.handle_user_prompt("work subject GT-KB", REPO_ROOT)

    assert "Current work subject set to GT-KB Infrastructure Focus" in response["systemMessage"]
    data = json.loads(canonical.read_text(encoding="utf-8"))
    assert data["current_subject"] == module.SUBJECT_GTKB


def test_legacy_aliases_still_recognized(tmp_path, monkeypatch) -> None:
    module = _load_module()
    _isolate_state(monkeypatch, tmp_path)

    # Application-side legacy alias
    module.handle_user_prompt("application mode", REPO_ROOT)
    assert module.load_state(REPO_ROOT)["current_subject"] == module.SUBJECT_APPLICATION

    # GT-KB-side legacy alias
    module.handle_user_prompt("GT-KB mode", REPO_ROOT)
    assert module.load_state(REPO_ROOT)["current_subject"] == module.SUBJECT_GTKB


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


def test_classify_root_4_categories(tmp_path, monkeypatch) -> None:
    module = _load_module()
    _isolate_state(monkeypatch, tmp_path)

    gtkb_dir = tmp_path / "groundtruth-kb"
    (gtkb_dir / "src" / "groundtruth_kb").mkdir(parents=True)
    monkeypatch.setenv("GTKB_PRODUCT_ROOT", str(gtkb_dir))

    gtkb_target = gtkb_dir / "src" / "groundtruth_kb" / "foo.py"
    assert module.classify_root(str(gtkb_target), REPO_ROOT) == module.ROOT_GTKB_PRODUCT
    assert module.classify_root("src/example.py", REPO_ROOT) == module.ROOT_APPLICATION_PRODUCT
    assert module.classify_root(".claude/rules/new-rule.md", REPO_ROOT) == module.ROOT_CURRENT_REPO_BRIDGE_OR_GOVERNANCE
    assert module.classify_root("bridge/some-proposal-001.md", REPO_ROOT) == module.ROOT_CURRENT_REPO_BRIDGE_OR_GOVERNANCE
    assert module.classify_root("AGENTS.md", REPO_ROOT) == module.ROOT_CURRENT_REPO_BRIDGE_OR_GOVERNANCE
    assert module.classify_root("README.md", REPO_ROOT) == module.ROOT_NEUTRAL


def test_application_subject_blocks_gtkb_product_write(tmp_path, monkeypatch) -> None:
    module = _load_module()
    _isolate_state(monkeypatch, tmp_path)

    gtkb_dir = tmp_path / "groundtruth-kb"
    (gtkb_dir / "src" / "groundtruth_kb").mkdir(parents=True)
    monkeypatch.setenv("GTKB_PRODUCT_ROOT", str(gtkb_dir))

    gtkb_target = gtkb_dir / "src" / "groundtruth_kb" / "foo.py"
    response = module.guard_tool_use(
        {"tool_name": "Write", "tool_input": {"file_path": str(gtkb_target)}},
        REPO_ROOT,
    )

    assert response["decision"] == "block"
    assert "Current work subject is application" in response["reason"]
    assert "work subject GT-KB" in response["reason"]
    assert "GT-KB product artifacts" in response["reason"]


def test_application_subject_allows_current_repo_bridge_or_governance_write(tmp_path, monkeypatch) -> None:
    """Phase 7 relaxation: current-repo bridge/governance paths are NOT blocked under application subject."""

    module = _load_module()
    _isolate_state(monkeypatch, tmp_path)

    response = module.guard_tool_use(
        {"tool_name": "Write", "tool_input": {"file_path": ".claude/rules/new-rule.md"}},
        REPO_ROOT,
    )

    assert response == {}


def test_application_subject_allows_application_write(tmp_path, monkeypatch) -> None:
    module = _load_module()
    _isolate_state(monkeypatch, tmp_path)

    response = module.guard_tool_use(
        {"tool_name": "Write", "tool_input": {"file_path": "src/example.py"}},
        REPO_ROOT,
    )

    assert response == {}


def test_gtkb_subject_blocks_application_product_write(tmp_path, monkeypatch) -> None:
    module = _load_module()
    _isolate_state(monkeypatch, tmp_path)
    module.save_state(module.FOCUS_GTKB_INFRASTRUCTURE, REPO_ROOT)

    response = module.guard_tool_use(
        {"tool_name": "Write", "tool_input": {"file_path": "src/example.py"}},
        REPO_ROOT,
    )

    assert response["decision"] == "block"
    assert "Current work subject is GT-KB" in response["reason"]
    assert "work subject application" in response["reason"]
    assert "application product artifacts" in response["reason"]


def test_gtkb_subject_allows_current_repo_bridge_or_governance_write(tmp_path, monkeypatch) -> None:
    """Phase 7: current-repo bridge/governance is allowed in BOTH subjects."""

    module = _load_module()
    _isolate_state(monkeypatch, tmp_path)
    module.save_state(module.FOCUS_GTKB_INFRASTRUCTURE, REPO_ROOT)

    response = module.guard_tool_use(
        {"tool_name": "Write", "tool_input": {"file_path": ".claude/rules/new-rule.md"}},
        REPO_ROOT,
    )

    assert response == {}


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


def test_bash_guard_only_blocks_mutating_gtkb_product_commands(tmp_path, monkeypatch) -> None:
    module = _load_module()
    _isolate_state(monkeypatch, tmp_path)

    gtkb_dir = tmp_path / "groundtruth-kb"
    (gtkb_dir / "src" / "groundtruth_kb").mkdir(parents=True)
    monkeypatch.setenv("GTKB_PRODUCT_ROOT", str(gtkb_dir))

    # Read commands touching bridge/governance surfaces should not block.
    read_response = module.guard_tool_use(
        {"tool_name": "Bash", "tool_input": {"command": "Get-Content .claude/rules/prime-builder-role.md"}},
        REPO_ROOT,
    )
    assert read_response == {}

    # Mutations to bridge/governance are NOT blocked (Phase 7 relaxation).
    governance_write_response = module.guard_tool_use(
        {
            "tool_name": "Bash",
            "tool_input": {"command": "Set-Content .claude/rules/new-rule.md 'text'"},
        },
        REPO_ROOT,
    )
    assert governance_write_response == {}

    # Mutations to GT-KB product paths ARE blocked under application subject.
    gtkb_target = (gtkb_dir / "src" / "groundtruth_kb" / "foo.py").as_posix()
    gtkb_write_response = module.guard_tool_use(
        {
            "tool_name": "Bash",
            "tool_input": {"command": f"Set-Content {gtkb_target} 'text'"},
        },
        REPO_ROOT,
    )
    assert gtkb_write_response["decision"] == "block"
    assert "work subject GT-KB" in gtkb_write_response["reason"]
