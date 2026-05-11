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


def _write_role_map(path: Path, roles: dict[str, tuple[str, str]]) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(
            {
                "schema_version": 1,
                "harnesses": {
                    harness_id: {"harness_type": harness_type, "role": role}
                    for harness_id, (harness_type, role) in roles.items()
                },
            }
        )
        + "\n",
        encoding="utf-8",
    )
    return path


def test_default_work_subject_is_gtkb_and_startup_lines_explain_commands(tmp_path, monkeypatch) -> None:
    module = _load_module()
    _isolate_state(monkeypatch, tmp_path)

    state = module.load_state(REPO_ROOT)
    lines = module.render_startup_focus_lines(module.startup_focus_snapshot(REPO_ROOT))

    assert state["default_focus"] == module.FOCUS_GTKB_INFRASTRUCTURE
    assert state["current_focus"] == module.FOCUS_GTKB_INFRASTRUCTURE
    assert state["current_subject"] == module.SUBJECT_GTKB
    assert state["schema_version"] == module.SCHEMA_VERSION
    assert state["role_slot"] == module.ROLE_SLOT_DEFAULT
    assert "Default work subject: GT-KB Infrastructure Focus" in lines
    assert "Current work subject: GT-KB Infrastructure Focus" in lines
    assert "GT-KB is the default work subject" in lines
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


def test_hook_payload_accepts_claude_prompt_field_for_user_promptsubmit(tmp_path, monkeypatch) -> None:
    module = _load_module()
    canonical, _ = _isolate_state(monkeypatch, tmp_path)
    module.save_state(module.FOCUS_GTKB_INFRASTRUCTURE, REPO_ROOT)

    response = module.handle_hook_payload(
        {
            "hook_event_name": "UserPromptSubmit",
            "prompt": "work subject application",
        },
        REPO_ROOT,
    )

    assert "Current work subject set to Application Focus" in response["systemMessage"]
    assert json.loads(canonical.read_text(encoding="utf-8"))["current_subject"] == module.SUBJECT_APPLICATION


def test_hook_payload_accepts_claude_prompt_field_for_startup_gate(tmp_path, monkeypatch) -> None:
    module = _load_module()
    _isolate_state(monkeypatch, tmp_path)
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

    response = module.handle_hook_payload(
        {
            "hook_event_name": "UserPromptSubmit",
            "prompt": "::init gtkb pb",
        },
        REPO_ROOT,
    )

    assert "GTKB STARTUP INPUT GATE (init-keyword match)" in response["systemMessage"]
    assert "ADR-SESSION-START-INIT-KEYWORD-CONTRACT-001" in response["systemMessage"]
    assert "first owner message of a fresh session is never actionable" not in response["systemMessage"]
    assert response["hookSpecificOutput"]["hookEventName"] == "UserPromptSubmit"
    guard_state = json.loads(guard_path.read_text(encoding="utf-8"))
    assert guard_state["discard_next_user_prompt"] is False
    assert guard_state["startup_prompt_discarded"] is True
    assert guard_state["startup_response_pending"] is True
    assert guard_state["startup_prompt_preview"] == "::init gtkb pb"


def test_user_promptsubmit_clears_stale_startup_gate_after_startup_stop(tmp_path, monkeypatch) -> None:
    module = _load_module()
    canonical, _ = _isolate_state(monkeypatch, tmp_path)
    guard_path = tmp_path / "guard.json"
    guard_path.write_text(
        json.dumps(
            {
                "discard_next_user_prompt": True,
                "first_wrapup_suppressed": True,
                "startup_guard_id": "test-guard",
                "startup_response_pending": False,
                "suppress_next_wrapup": False,
            }
        )
        + "\n",
        encoding="utf-8",
    )
    module.save_state(module.FOCUS_GTKB_INFRASTRUCTURE, REPO_ROOT)

    response = module.handle_hook_payload(
        {
            "hook_event_name": "UserPromptSubmit",
            "prompt": "work subject application",
        },
        REPO_ROOT,
    )

    assert "first owner message of a fresh session is never actionable" not in response["systemMessage"]
    assert "Current work subject set to Application Focus" in response["systemMessage"]
    assert json.loads(canonical.read_text(encoding="utf-8"))["current_subject"] == module.SUBJECT_APPLICATION
    guard_state = json.loads(guard_path.read_text(encoding="utf-8"))
    assert guard_state["discard_next_user_prompt"] is False
    assert guard_state["stale_startup_gate_cleared"] is True
    assert guard_state["stale_startup_gate_reason"] == "startup_stop_already_suppressed"
    assert guard_state["startup_prompt_preview"] == "work subject application"


def test_prompt_hook_accepts_bom_prefixed_stdin_from_windows_pipeline(tmp_path) -> None:
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
    env = {
        **dict(os.environ),
        "GTKB_WORKSTREAM_FOCUS_STATE": str(state_path),
        "GTKB_LIFECYCLE_GUARD_PATH": str(guard_path),
        "CLAUDE_PROJECT_DIR": str(REPO_ROOT),
    }

    result = subprocess.run(
        [sys.executable, str(HOOK_PATH)],
        cwd=REPO_ROOT,
        env=env,
        input=("\ufeff" + json.dumps({"prompt": "::init gtkb pb", "hook_event_name": "UserPromptSubmit"})).encode(
            "utf-8"
        ),
        capture_output=True,
        timeout=10,
        check=True,
    )

    response = json.loads(result.stdout.decode("utf-8"))
    assert "GTKB STARTUP INPUT GATE (init-keyword match)" in response["systemMessage"]
    assert "ADR-SESSION-START-INIT-KEYWORD-CONTRACT-001" in response["systemMessage"]
    assert "first owner message of a fresh session is never actionable" not in response["systemMessage"]
    assert json.loads(guard_path.read_text(encoding="utf-8"))["startup_response_pending"] is True


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
    role_path = _write_role_map(
        tmp_path / "role-assignments.json",
        {"A": ("codex", "loyal-opposition"), "B": ("claude", "prime-builder")},
    )
    monkeypatch.setenv("GTKB_ROLE_ASSIGNMENTS_PATH", str(role_path))
    monkeypatch.setenv("GTKB_HARNESS_NAME", "codex")
    monkeypatch.setenv("GTKB_HARNESS_ID", "A")
    monkeypatch.setenv("GTKB_LIFECYCLE_GUARD_PATH", str(tmp_path / "guard.json"))

    response = module.handle_user_prompt("switch mode next session", REPO_ROOT)

    assert "Next fresh-session operating mode set to Prime Builder" in response["systemMessage"]
    assert "Harness parity after role change:" in response["systemMessage"]
    data = json.loads(role_path.read_text(encoding="utf-8"))
    assert data["harnesses"]["A"]["role"] == "prime-builder"
    assert data["harnesses"]["B"]["role"] == "loyal-opposition"

    response = module.handle_user_prompt("please change mode next session.", REPO_ROOT)

    assert "Next fresh-session operating mode set to Loyal Opposition" in response["systemMessage"]
    data = json.loads(role_path.read_text(encoding="utf-8"))
    assert data["harnesses"]["A"]["role"] == "loyal-opposition"


def test_prompt_hook_sets_explicit_next_session_role(tmp_path, monkeypatch) -> None:
    module = _load_module()
    role_path = _write_role_map(
        tmp_path / "role-assignments.json",
        {"A": ("codex", "loyal-opposition"), "B": ("claude", "prime-builder")},
    )
    monkeypatch.setenv("GTKB_ROLE_ASSIGNMENTS_PATH", str(role_path))
    monkeypatch.setenv("GTKB_HARNESS_NAME", "codex")
    monkeypatch.setenv("GTKB_HARNESS_ID", "A")
    monkeypatch.setenv("GTKB_LIFECYCLE_GUARD_PATH", str(tmp_path / "guard.json"))

    response = module.handle_user_prompt("prime builder mode next session", REPO_ROOT)

    assert "Next fresh-session operating mode set to Prime Builder" in response["systemMessage"]
    data = json.loads(role_path.read_text(encoding="utf-8"))
    assert data["harnesses"]["A"]["role"] == "prime-builder"
    assert data["harnesses"]["B"]["role"] == "loyal-opposition"


def test_prompt_hook_uses_harness_id_role_map_when_named(tmp_path, monkeypatch) -> None:
    module = _load_module()
    role_path = _write_role_map(
        tmp_path / "role-assignments.json",
        {"A": ("codex", "loyal-opposition"), "B": ("claude", "prime-builder")},
    )
    monkeypatch.setenv("GTKB_ROLE_ASSIGNMENTS_PATH", str(role_path))
    monkeypatch.setenv("GTKB_HARNESS_NAME", "codex")
    monkeypatch.setenv("GTKB_HARNESS_ID", "A")
    monkeypatch.setenv("GTKB_LIFECYCLE_GUARD_PATH", str(tmp_path / "guard.json"))

    response = module.handle_user_prompt("switch mode next session", REPO_ROOT)

    assert "Next fresh-session operating mode set to Prime Builder" in response["systemMessage"]
    assert str(role_path) in response["systemMessage"]
    assert "harness `A`" in response["systemMessage"]
    assert json.loads(role_path.read_text(encoding="utf-8"))["harnesses"]["A"]["role"] == "prime-builder"


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
    assert (
        "startup disclosure already generated for this session" in response["hookSpecificOutput"]["additionalContext"]
    )

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
    assert (
        module.classify_root("bridge/some-proposal-001.md", REPO_ROOT) == module.ROOT_CURRENT_REPO_BRIDGE_OR_GOVERNANCE
    )
    assert module.classify_root("AGENTS.md", REPO_ROOT) == module.ROOT_CURRENT_REPO_BRIDGE_OR_GOVERNANCE
    assert module.classify_root("README.md", REPO_ROOT) == module.ROOT_NEUTRAL


def test_application_subject_blocks_gtkb_product_write(tmp_path, monkeypatch) -> None:
    module = _load_module()
    _isolate_state(monkeypatch, tmp_path)
    module.save_state(module.FOCUS_APPLICATION, REPO_ROOT)

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
    module.save_state(module.FOCUS_APPLICATION, REPO_ROOT)

    response = module.guard_tool_use(
        {"tool_name": "Write", "tool_input": {"file_path": ".claude/rules/new-rule.md"}},
        REPO_ROOT,
    )

    assert response == {}


def test_application_subject_allows_application_write(tmp_path, monkeypatch) -> None:
    module = _load_module()
    _isolate_state(monkeypatch, tmp_path)
    module.save_state(module.FOCUS_APPLICATION, REPO_ROOT)

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
    assert "startup disclosure has been emitted" in response["reason"]
    assert "init-keyword contract" in response["reason"]
    assert "ADR-SESSION-START-INIT-KEYWORD-CONTRACT-001" in response["reason"]
    assert "first owner message of this fresh session was discarded" not in response["reason"]


def test_bash_guard_only_blocks_mutating_gtkb_product_commands(tmp_path, monkeypatch) -> None:
    module = _load_module()
    _isolate_state(monkeypatch, tmp_path)
    module.save_state(module.FOCUS_APPLICATION, REPO_ROOT)

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


# ---- GTKB-ISOLATION-015 Slice 1 §A / §C / §E regression coverage ----------


def test_startup_focus_lines_include_role_slot_topology_mode_stimulus_and_bridge_authority(
    tmp_path, monkeypatch
) -> None:
    module = _load_module()
    _isolate_state(monkeypatch, tmp_path)

    snapshot = module.startup_focus_snapshot(REPO_ROOT)
    lines = module.render_startup_focus_lines(snapshot)

    assert snapshot["role_slot"] == module.ROLE_SLOT_DEFAULT
    assert snapshot["topology_mode"] == module.TOPOLOGY_MODE_DEFAULT
    assert "Bridge role slot:" in lines
    assert module.ROLE_SLOT_DEFAULT in lines
    assert "Harness topology:" in lines
    assert module.TOPOLOGY_MODE_SINGLE in lines
    assert "First owner message" in lines
    assert "stimulus" in lines
    assert "bridge/INDEX.md" in lines
    assert "canonical handoff/review" in lines


def test_save_state_persists_topology_mode_default(tmp_path, monkeypatch) -> None:
    module = _load_module()
    canonical, _ = _isolate_state(monkeypatch, tmp_path)

    module.save_state(module.FOCUS_APPLICATION, REPO_ROOT, updated_by="owner_prompt")
    data = json.loads(canonical.read_text(encoding="utf-8"))
    assert data["topology_mode"] == module.TOPOLOGY_MODE_SINGLE


def test_overlay_startup_note_absent_is_informational(tmp_path, monkeypatch) -> None:
    module = _load_module()
    _isolate_state(monkeypatch, tmp_path)
    note = module.overlay_startup_note({"overlay_present": False})
    assert note["level"] == "info"
    assert any("No session overlay active" in line for line in note["lines"])
    assert not any(line.startswith("WARNING") for line in note["lines"])


def test_overlay_startup_note_stale_is_warning(tmp_path, monkeypatch) -> None:
    module = _load_module()
    _isolate_state(monkeypatch, tmp_path)
    note = module.overlay_startup_note({"overlay_present": True, "is_stale": True})
    assert note["level"] == "warning"
    assert any("stale" in line for line in note["lines"])
    assert any(line.startswith("WARNING") for line in note["lines"])


def test_overlay_startup_note_root_mismatch_is_warning() -> None:
    module = _load_module()
    note = module.overlay_startup_note({"overlay_present": True, "root_mismatch": True})
    assert note["level"] == "warning"
    assert any("different project root" in line for line in note["lines"])


def test_overlay_startup_note_subject_mismatch_is_warning() -> None:
    module = _load_module()
    note = module.overlay_startup_note({"overlay_present": True, "subject_mismatch": True})
    assert note["level"] == "warning"
    assert any("work subject differs" in line for line in note["lines"])


def test_overlay_startup_note_projection_diff_is_warning() -> None:
    module = _load_module()
    note = module.overlay_startup_note({"overlay_present": True, "projection_diff": True})
    assert note["level"] == "warning"
    assert any("projection differs" in line for line in note["lines"])


def test_overlay_startup_note_never_canonical_phrasing() -> None:
    module = _load_module()
    note = module.overlay_startup_note({"overlay_present": True, "is_stale": True})
    joined = " ".join(note["lines"])
    assert "never canonical" in joined
    assert "Deliberation Archive" in joined


def test_detect_counterpart_state_no_counterpart_files_no_warning(tmp_path, monkeypatch) -> None:
    module = _load_module()
    monkeypatch.setenv("GTKB_HARNESS_NAME", "claude")
    monkeypatch.setenv("GTKB_HARNESS_ID", "B")
    role_map = _write_role_map(
        tmp_path / "role-assignments.json",
        {"B": ("claude", "prime-builder")},
    )
    monkeypatch.setenv("GTKB_ROLE_ASSIGNMENTS_PATH", str(role_map))
    result = module.detect_counterpart_state()
    assert result["warnings"] == []
    assert result["counterpart_present"] is False


def test_detect_counterpart_state_same_role_warns(tmp_path, monkeypatch) -> None:
    module = _load_module()
    monkeypatch.setenv("GTKB_HARNESS_NAME", "claude")
    monkeypatch.setenv("GTKB_HARNESS_ID", "B")
    role_map = _write_role_map(
        tmp_path / "role-assignments.json",
        {"A": ("codex", "prime-builder"), "B": ("claude", "prime-builder")},
    )
    monkeypatch.setenv("GTKB_ROLE_ASSIGNMENTS_PATH", str(role_map))
    result = module.detect_counterpart_state()
    assert result["same_role_slot"] is True
    assert result["counterpart_present"] is True
    assert any("prime-builder" in msg and "collide" in msg for msg in result["warnings"])


def test_detect_counterpart_state_different_role_warns(tmp_path, monkeypatch) -> None:
    module = _load_module()
    monkeypatch.setenv("GTKB_HARNESS_NAME", "claude")
    monkeypatch.setenv("GTKB_HARNESS_ID", "B")
    role_map = _write_role_map(
        tmp_path / "role-assignments.json",
        {"A": ("codex", "loyal-opposition"), "B": ("claude", "prime-builder")},
    )
    monkeypatch.setenv("GTKB_ROLE_ASSIGNMENTS_PATH", str(role_map))
    result = module.detect_counterpart_state()
    assert result["same_role_slot"] is False
    assert result["counterpart_present"] is True
    assert any("prime-builder" in msg and "loyal-opposition" in msg for msg in result["warnings"])


def test_detect_counterpart_state_subject_mismatch_warns(tmp_path, monkeypatch) -> None:
    module = _load_module()
    canonical, _ = _isolate_state(monkeypatch, tmp_path)
    monkeypatch.setenv("GTKB_HARNESS_NAME", "claude")
    monkeypatch.setenv("GTKB_HARNESS_ID", "B")
    role_map = _write_role_map(
        tmp_path / "role-assignments.json",
        {"A": ("codex", "loyal-opposition"), "B": ("claude", "prime-builder")},
    )
    monkeypatch.setenv("GTKB_ROLE_ASSIGNMENTS_PATH", str(role_map))
    codex_guard = tmp_path / ".codex" / "session-lifecycle-guard.json"
    claude_guard = tmp_path / ".claude" / "session-lifecycle-guard.json"
    codex_guard.parent.mkdir(parents=True, exist_ok=True)
    claude_guard.parent.mkdir(parents=True, exist_ok=True)
    codex_guard.write_text(
        json.dumps({"current_subject": module.FOCUS_GTKB_INFRASTRUCTURE}) + "\n",
        encoding="utf-8",
    )
    claude_guard.write_text(
        json.dumps({"current_subject": module.FOCUS_APPLICATION}) + "\n",
        encoding="utf-8",
    )
    monkeypatch.setattr(
        module,
        "HARNESS_LIFECYCLE_GUARDS",
        {"codex": codex_guard, "claude": claude_guard},
    )
    module.save_state(module.FOCUS_APPLICATION, REPO_ROOT, updated_by="owner_prompt")

    result = module.detect_counterpart_state()
    assert result["subject_mismatch"] is True
    assert any(
        module.FOCUS_GTKB_INFRASTRUCTURE in msg and module.FOCUS_APPLICATION in msg for msg in result["warnings"]
    )


def test_detect_counterpart_state_subject_mismatch_symmetric_from_codex_side(tmp_path, monkeypatch) -> None:
    """Symmetric §E regression (bridge -014 P1).

    Reproduces the live asymmetry Codex demonstrated: Codex on
    gtkb_infrastructure, Claude on application, shared canonical set to
    application. Before -014's fix, detect_counterpart_state() with
    GTKB_HARNESS_NAME=codex read our_subject from the shared canonical
    (application), compared against counterpart Claude guard (application),
    and returned subject_mismatch=False — silently missing the split.

    After the fix, our_subject is read from our own harness guard first, so
    Codex sees our_subject=gtkb_infrastructure and correctly warns.
    """
    module = _load_module()
    canonical, _ = _isolate_state(monkeypatch, tmp_path)
    monkeypatch.setenv("GTKB_HARNESS_NAME", "codex")
    monkeypatch.setenv("GTKB_HARNESS_ID", "A")
    role_map = _write_role_map(
        tmp_path / "role-assignments.json",
        {"A": ("codex", "prime-builder"), "B": ("claude", "loyal-opposition")},
    )
    monkeypatch.setenv("GTKB_ROLE_ASSIGNMENTS_PATH", str(role_map))
    codex_guard = tmp_path / ".codex" / "session-lifecycle-guard.json"
    claude_guard = tmp_path / ".claude" / "session-lifecycle-guard.json"
    codex_guard.parent.mkdir(parents=True, exist_ok=True)
    claude_guard.parent.mkdir(parents=True, exist_ok=True)
    # Codex harness's own guard says gtkb_infrastructure.
    codex_guard.write_text(
        json.dumps({"current_subject": module.FOCUS_GTKB_INFRASTRUCTURE}) + "\n",
        encoding="utf-8",
    )
    # Claude's guard says application — matches shared canonical.
    claude_guard.write_text(
        json.dumps({"current_subject": module.FOCUS_APPLICATION}) + "\n",
        encoding="utf-8",
    )
    monkeypatch.setattr(
        module,
        "HARNESS_LIFECYCLE_GUARDS",
        {"codex": codex_guard, "claude": claude_guard},
    )
    # Shared canonical is application (what Claude last wrote). If the old
    # implementation read our_subject from this file, it would compare
    # application (ours) against application (claude's guard) and miss.
    module.save_state(module.FOCUS_APPLICATION, REPO_ROOT, updated_by="owner_prompt")

    result = module.detect_counterpart_state()
    assert result["subject_mismatch"] is True, (
        "Codex-side must detect subject divergence against Claude's guard; "
        "pre-fix behavior silently missed this because our_subject came from "
        "the shared canonical instead of codex's own guard."
    )
    assert any(
        module.FOCUS_GTKB_INFRASTRUCTURE in msg and module.FOCUS_APPLICATION in msg for msg in result["warnings"]
    )


def test_detect_counterpart_state_subject_match_no_warning(tmp_path, monkeypatch) -> None:
    module = _load_module()
    canonical, _ = _isolate_state(monkeypatch, tmp_path)
    monkeypatch.setenv("GTKB_HARNESS_NAME", "claude")
    monkeypatch.setenv("GTKB_HARNESS_ID", "B")
    role_map = _write_role_map(
        tmp_path / "role-assignments.json",
        {"A": ("codex", "loyal-opposition"), "B": ("claude", "prime-builder")},
    )
    monkeypatch.setenv("GTKB_ROLE_ASSIGNMENTS_PATH", str(role_map))
    codex_guard = tmp_path / ".codex" / "session-lifecycle-guard.json"
    claude_guard = tmp_path / ".claude" / "session-lifecycle-guard.json"
    codex_guard.parent.mkdir(parents=True, exist_ok=True)
    claude_guard.parent.mkdir(parents=True, exist_ok=True)
    for guard in (codex_guard, claude_guard):
        guard.write_text(
            json.dumps({"current_subject": module.FOCUS_APPLICATION}) + "\n",
            encoding="utf-8",
        )
    monkeypatch.setattr(
        module,
        "HARNESS_LIFECYCLE_GUARDS",
        {"codex": codex_guard, "claude": claude_guard},
    )
    module.save_state(module.FOCUS_APPLICATION, REPO_ROOT, updated_by="owner_prompt")

    result = module.detect_counterpart_state()
    assert result["subject_mismatch"] is False
    assert not any("work subject" in msg for msg in result["warnings"])


def test_detect_counterpart_state_missing_counterpart_no_crash(tmp_path, monkeypatch) -> None:
    module = _load_module()
    monkeypatch.setenv("GTKB_HARNESS_NAME", "claude")
    monkeypatch.setenv("GTKB_HARNESS_ID", "B")
    role_map = _write_role_map(
        tmp_path / "role-assignments.json",
        {"B": ("claude", "prime-builder")},
    )
    monkeypatch.setenv("GTKB_ROLE_ASSIGNMENTS_PATH", str(role_map))
    result = module.detect_counterpart_state()
    assert result["counterpart_present"] is False
    assert result["warnings"] == []


def test_render_active_work_subject_combines_focus_overlay_and_counterpart(tmp_path, monkeypatch) -> None:
    module = _load_module()
    _isolate_state(monkeypatch, tmp_path)
    monkeypatch.setenv("GTKB_HARNESS_NAME", "claude")
    role_map = _write_role_map(
        tmp_path / "role-assignments.json",
        {"B": ("claude", "prime-builder")},
    )
    monkeypatch.setenv("GTKB_ROLE_ASSIGNMENTS_PATH", str(role_map))

    rendered = module.render_active_work_subject(
        REPO_ROOT,
        overlay_status={"overlay_present": False},
    )
    assert "Active Work Subject" not in rendered  # heading is rendered by caller
    assert "Bridge role slot:" in rendered
    assert "No session overlay active" in rendered


def test_assert_readiness_subject_scope_hard_rejects_unlabeled_combined_green() -> None:
    module = _load_module()
    with pytest.raises(module.SubjectScopeError, match="combined application \\+ GT-KB"):
        module.assert_readiness_subject_scope(application_green=True, gtkb_green=True, dual_scope_declared=False)


def test_assert_readiness_subject_scope_permits_dual_scope_declaration() -> None:
    module = _load_module()
    module.assert_readiness_subject_scope(application_green=True, gtkb_green=True, dual_scope_declared=True)


def test_harness_state_records_for_project_returns_sandbox_relative_paths(tmp_path) -> None:
    module = _load_module()
    sandbox = tmp_path / "sandbox"
    role_assignment_path, lifecycle_guards = module._harness_state_records_for_project(sandbox)

    assert role_assignment_path == sandbox / "harness-state" / "role-assignments.json"
    assert lifecycle_guards["codex"] == sandbox / "harness-state" / "codex" / "session-lifecycle-guard.json"
    assert lifecycle_guards["claude"] == sandbox / "harness-state" / "claude" / "session-lifecycle-guard.json"
    assert role_assignment_path != module.PROJECT_ROOT / "harness-state" / "role-assignments.json"
    assert lifecycle_guards["codex"] != module.HARNESS_LIFECYCLE_GUARDS["codex"]


def test_detect_counterpart_state_uses_project_root_paths_when_provided(tmp_path, monkeypatch) -> None:
    """Per bridge/harness-state-preferences-path-cli-2026-04-28-005.md class-level fix.

    When detect_counterpart_state is called with a sandbox project_root, it
    must read the sandbox role-assignment map, not the canonical map.
    """
    module = _load_module()
    sandbox = tmp_path / "sandbox"
    sandbox.mkdir()
    recorded_paths: list[Path] = []

    def _fake_load(project_root: Path, assignment_path: Path | None = None) -> dict:
        recorded_paths.append(assignment_path or project_root / "harness-state" / "role-assignments.json")
        return {"harnesses": {}}

    monkeypatch.setattr(module, "load_role_assignments", _fake_load)
    monkeypatch.setattr(module, "_read_counterpart_subject", lambda _path: None)

    module.detect_counterpart_state(sandbox)

    assert recorded_paths, "expected detect_counterpart_state to load role assignments"
    canonical_root = module.PROJECT_ROOT
    for path in recorded_paths:
        assert sandbox in path.parents, (
            f"role assignment path {path!r} should be under sandbox {sandbox!r} but is not — class-level fix regressed"
        )
        assert canonical_root not in path.parents, (
            f"role assignment path {path!r} should NOT be under canonical "
            f"PROJECT_ROOT {canonical_root!r} — class-level fix regressed"
        )


def test_detect_counterpart_state_falls_back_to_canonical_when_project_root_omitted(tmp_path, monkeypatch) -> None:
    module = _load_module()
    recorded_paths: list[Path] = []

    def _fake_load(project_root: Path, assignment_path: Path | None = None) -> dict:
        recorded_paths.append(assignment_path or project_root / "harness-state" / "role-assignments.json")
        return {"harnesses": {}}

    monkeypatch.setattr(module, "load_role_assignments", _fake_load)
    monkeypatch.setattr(module, "_read_counterpart_subject", lambda _path: None)
    monkeypatch.setenv("CLAUDE_PROJECT_DIR", str(module.PROJECT_ROOT))

    module.detect_counterpart_state()  # no project_root arg

    assert recorded_paths, "expected detect_counterpart_state to load role assignments"
    assert recorded_paths == [module.PROJECT_ROOT / "harness-state" / "role-assignments.json"]


def test_assert_readiness_subject_scope_permits_single_green() -> None:
    module = _load_module()
    module.assert_readiness_subject_scope(application_green=True, gtkb_green=False, dual_scope_declared=False)
    module.assert_readiness_subject_scope(application_green=False, gtkb_green=True, dual_scope_declared=False)
