"""Regression checks for Codex hook parity with Agent Red governance hooks."""

from __future__ import annotations

import ast
import importlib.util
import json
import os
import sys
from pathlib import Path

import pytest

from scripts.parity_discovery_diff import enumerate_hook_surfaces

REPO_ROOT = Path(__file__).resolve().parents[2]
SCRIPT_PATH = REPO_ROOT / "scripts" / "check_codex_hook_parity.py"
CODEX_SESSION_START_DISPATCHER = REPO_ROOT / ".codex" / "gtkb-hooks" / "session_start_dispatch.py"
CODEX_HOOKS_PATH = REPO_ROOT / ".codex" / "hooks.json"
CLAUDE_SETTINGS_PATH = REPO_ROOT / ".claude" / "settings.json"
SESSION_START_DISPATCH_CORE = REPO_ROOT / "scripts" / "session_start_dispatch_core.py"


def _load_module():
    spec = importlib.util.spec_from_file_location("check_codex_hook_parity", SCRIPT_PATH)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules["check_codex_hook_parity"] = module
    spec.loader.exec_module(module)
    return module


def _load_session_start_dispatcher():
    spec = importlib.util.spec_from_file_location("codex_session_start_dispatch", CODEX_SESSION_START_DISPATCHER)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules["codex_session_start_dispatch"] = module
    spec.loader.exec_module(module)
    return module


def _load_codex_hooks() -> dict:
    return json.loads(CODEX_HOOKS_PATH.read_text(encoding="utf-8"))


def _skip_if_codex_hooks_intentionally_empty(codex_hooks: dict) -> None:
    if codex_hooks.get("hooks") == {}:
        pytest.skip("Codex hooks are intentionally empty under Windows no-window containment")


def _hooks_for_event(codex_hooks: dict, event_name: str) -> list[dict]:
    return [hook for group in codex_hooks["hooks"][event_name] for hook in group["hooks"]]


def _hook_with_command_fragment(codex_hooks: dict, event_name: str, command_fragment: str) -> dict:
    target_surface = Path(command_fragment.replace("\\", "/")).stem.lower()
    matches: list[dict] = []
    for group in codex_hooks["hooks"].get(event_name, []):
        for hook in group.get("hooks", []):
            single_hook_group = dict(group)
            single_hook_group["hooks"] = [hook]
            surfaces = enumerate_hook_surfaces(
                {"hooks": {event_name: [single_hook_group]}},
                project_root=REPO_ROOT,
            )
            if target_surface in {surface.lower() for surface in surfaces}:
                matches.append(hook)
    assert len(matches) == 1
    return matches[0]


def _expanded_routes(
    hooks_document: dict,
    event_name: str,
    command_fragment: str,
    *,
    project_root: Path = REPO_ROOT,
) -> list[tuple[dict, dict]]:
    target_surface = Path(command_fragment.replace("\\", "/")).stem.lower()
    routes: list[tuple[dict, dict]] = []
    for group in hooks_document.get("hooks", {}).get(event_name, []):
        for hook in group.get("hooks", []):
            single_hook_group = dict(group)
            single_hook_group["hooks"] = [hook]
            surfaces = enumerate_hook_surfaces(
                {"hooks": {event_name: [single_hook_group]}},
                project_root=project_root,
            )
            if target_surface in {surface.lower() for surface in surfaces}:
                routes.append((group, hook))
    return routes


def _float_constant_from_python_module(path: Path, constant_name: str) -> float:
    module = ast.parse(path.read_text(encoding="utf-8"))
    for statement in module.body:
        if not isinstance(statement, ast.Assign):
            continue
        if not any(isinstance(target, ast.Name) and target.id == constant_name for target in statement.targets):
            continue
        value = ast.literal_eval(statement.value)
        assert isinstance(value, (int, float))
        return float(value)
    raise AssertionError(f"Missing constant {constant_name} in {path}")


def test_codex_hook_parity_passes_for_repository_configuration(capsys) -> None:
    module = _load_module()

    assert module.main(["--project-root", str(REPO_ROOT)]) == 0

    output = capsys.readouterr().out
    assert "Codex hook parity: PASS" in output
    assert "Windows shell-portable command forms" in output


def test_codex_sessionstart_hook_timeout_exceeds_inner_startup_service_timeout() -> None:
    codex_hooks = _load_codex_hooks()
    _skip_if_codex_hooks_intentionally_empty(codex_hooks)
    session_start_hook = _hook_with_command_fragment(
        codex_hooks,
        "SessionStart",
        "session_start_dispatch.py",
    )
    inner_timeout = _float_constant_from_python_module(
        SESSION_START_DISPATCH_CORE,
        "STARTUP_SERVICE_TIMEOUT_SECONDS",
    )

    assert session_start_hook["timeout"] > inner_timeout


def test_codex_userpromptsubmit_wrapup_hook_has_headroom_timeout() -> None:
    codex_hooks = _load_codex_hooks()
    _skip_if_codex_hooks_intentionally_empty(codex_hooks)
    wrapup_hook = _hook_with_command_fragment(
        codex_hooks,
        "UserPromptSubmit",
        "session_wrapup_trigger_dispatch.py",
    )

    assert wrapup_hook["timeout"] >= 60


def test_claude_proactive_wrapup_stop_hook_has_sixty_second_allowance() -> None:
    claude_settings = json.loads(CLAUDE_SETTINGS_PATH.read_text(encoding="utf-8"))
    wrapup_hook = _hook_with_command_fragment(
        claude_settings,
        "Stop",
        "session_self_initialization.py",
    )

    assert "--emit-wrapup" in wrapup_hook["command"]
    assert wrapup_hook["timeout"] == 60


def test_codex_hook_parity_requires_session_lifecycle_hook_intent(tmp_path) -> None:
    module = _load_module()

    errors = module.check_project(REPO_ROOT)

    assert not errors
    codex_hooks = _load_codex_hooks()
    _skip_if_codex_hooks_intentionally_empty(codex_hooks)
    claude_settings = json.loads((REPO_ROOT / ".claude" / "settings.json").read_text(encoding="utf-8"))
    assert len(_expanded_routes(codex_hooks, "SessionStart", "session_start_dispatch.py")) == 1
    assert not any(
        "gtkb_dispatcher_daemon.py" in hook["command"] or "dispatcher-daemon.cmd" in hook["command"]
        for groups in codex_hooks["hooks"].values()
        for group in groups
        for hook in group["hooks"]
    )
    session_start_hook = _hook_with_command_fragment(codex_hooks, "SessionStart", "session_start_dispatch.py")
    inner_timeout = _float_constant_from_python_module(SESSION_START_DISPATCH_CORE, "STARTUP_SERVICE_TIMEOUT_SECONDS")
    assert session_start_hook["timeout"] > inner_timeout
    assert len(_expanded_routes(codex_hooks, "UserPromptSubmit", "session_wrapup_trigger_dispatch.py")) == 1
    assert len(_expanded_routes(codex_hooks, "UserPromptSubmit", "workstream-focus.cmd")) == 1
    workstream_pre_routes = _expanded_routes(codex_hooks, "PreToolUse", "workstream-focus.cmd")
    assert sorted(group.get("matcher") for group, _hook in workstream_pre_routes) == ["Bash", "apply_patch"]
    bridge_pre_routes = _expanded_routes(codex_hooks, "PreToolUse", "bridge-compliance-gate.cmd")
    assert len(bridge_pre_routes) == 1
    assert bridge_pre_routes[0][0].get("matcher") == "Bash"
    bridge_post_routes = _expanded_routes(codex_hooks, "PostToolUse", "bridge-compliance-audit.cmd")
    assert len(bridge_post_routes) == 1
    assert bridge_post_routes[0][0].get("matcher") == "Bash"
    assert "Stop" in codex_hooks["hooks"], (
        "Codex Stop hook must be registered for non-dispatch lifecycle parity "
        "(auto-finalization, advisory scan, and backlog reconciliation)."
    )
    codex_stop_hooks = codex_hooks["hooks"]["Stop"]
    # Stop matchers are not supported by Codex; entries must be matcher-less.
    for group in codex_stop_hooks:
        assert group.get("matcher") in (None, ""), "Codex Stop entries must not declare a matcher (Codex hooks docs)"
    assert len(_expanded_routes(codex_hooks, "Stop", "auto_finalize_sweep.py")) == 0, (
        "auto-finalize sweep is disabled by owner decision (2026-09-07) and must not be registered"
    )
    assert len(_expanded_routes(codex_hooks, "Stop", "advisory-router-scan.py")) == 1
    codex_stop_commands = [hook["command"] for group in codex_stop_hooks for hook in group["hooks"]]
    assert not any("session_wrapup" in cmd or "session_self_initialization.py" in cmd for cmd in codex_stop_commands), (
        "Codex Stop must not register lifecycle wrap-up scripts. Stop is limited "
        "to non-dispatch lifecycle parity, not session wrap-up."
    )
    assert not any(
        token in cmd
        for cmd in codex_stop_commands
        for token in (
            "cross_" + "harness_" + "bridge_" + "trigger.py",
            "single_harness_bridge_automation.py",
            "single_harness_bridge_dispatcher.py",
            "dispatcher-daemon.cmd",
            "gtkb_dispatcher_daemon.py",
        )
    ), (
        "Codex hooks must not register dispatcher-trigger workers; dispatcher "
        "operation is daemon-owned, with manual assignment as the only fallback."
    )
    # Per bridge/gtkb-startup-enhancements-p1-003.md §2.4 (Codex GO at -004):
    # the previously-registered owner-decision-tracker-ups.cmd entry has been
    # removed because the wrapper file does not exist on disk, Codex hooks
    # remain batch-routed through the no-window runner, and the active mechanism
    # is scripts/check_pending_owner_decisions_parity.py in
    # the release-candidate gate. This assertion guards against regression.
    all_codex_commands = [
        hook["command"]
        for event_groups in codex_hooks["hooks"].values()
        for group in event_groups
        for hook in group["hooks"]
    ]
    assert not any("owner-decision-tracker-ups.cmd" in cmd for cmd in all_codex_commands), (
        "Codex owner-decision-tracker-ups.cmd entry must remain absent until "
        "the wrapper file is created on disk. Active fallback is in the "
        "release-candidate gate via check_pending_owner_decisions_parity.py."
    )

    # Required child surfaces fail closed when the public batch enumerator
    # cannot read a complete declarative batch. Direct wrappers remain valid.
    batch_group = codex_hooks["hooks"]["PreToolUse"][0]
    batch_document = {"hooks": {"PreToolUse": [batch_group]}}
    valid_root = tmp_path / "valid"
    valid_runner = valid_root / ".codex" / "gtkb-hooks" / "run_py_no_window.py"
    valid_runner.parent.mkdir(parents=True)
    valid_runner.write_bytes((REPO_ROOT / ".codex" / "gtkb-hooks" / "run_py_no_window.py").read_bytes())
    assert "formal-artifact-approval" in enumerate_hook_surfaces(batch_document, project_root=valid_root)

    missing_root = tmp_path / "missing"
    assert "formal-artifact-approval" not in enumerate_hook_surfaces(batch_document, project_root=missing_root)

    malformed_root = tmp_path / "malformed"
    malformed_runner = malformed_root / ".codex" / "gtkb-hooks" / "run_py_no_window.py"
    malformed_runner.parent.mkdir(parents=True)
    malformed_runner.write_text("BATCHES = {\n", encoding="utf-8")
    assert "formal-artifact-approval" not in enumerate_hook_surfaces(batch_document, project_root=malformed_root)

    unreadable_root = tmp_path / "unreadable"
    unreadable_runner = unreadable_root / ".codex" / "gtkb-hooks" / "run_py_no_window.py"
    unreadable_runner.mkdir(parents=True)
    assert "formal-artifact-approval" not in enumerate_hook_surfaces(batch_document, project_root=unreadable_root)

    incomplete_root = tmp_path / "incomplete"
    incomplete_runner = incomplete_root / ".codex" / "gtkb-hooks" / "run_py_no_window.py"
    incomplete_runner.parent.mkdir(parents=True)
    incomplete_runner.write_text(
        'BATCHES = {"pretooluse-bash": (("cmd", ".codex/gtkb-hooks/workstream-focus.cmd"),)}\n',
        encoding="utf-8",
    )
    assert "formal-artifact-approval" not in enumerate_hook_surfaces(batch_document, project_root=incomplete_root)

    direct_document = {
        "hooks": {
            "PreToolUse": [
                {
                    "matcher": "Bash",
                    "hooks": [
                        {
                            "type": "command",
                            "command": "python .codex/gtkb-hooks/formal-artifact-approval.cmd",
                            "timeout": 5,
                        }
                    ],
                }
            ]
        }
    }
    assert "formal-artifact-approval" in enumerate_hook_surfaces(direct_document, project_root=missing_root)
    # Per gtkb-claude-session-start-parity GO at -002, the SessionStart
    # registration may be either the canonical script directly (legacy)
    # or a dispatcher under .claude/hooks/ that delegates to it via the
    # --emit-startup-service-payload contract.
    session_start_hooks = [
        hook["command"] for group in claude_settings["hooks"]["SessionStart"] for hook in group["hooks"]
    ]
    direct_match = any(
        "session_self_initialization.py" in cmd
        and "--emit-report" in cmd
        and "--fast-hook" in cmd
        and "--harness-name claude" in cmd
        and "--harness-id B" not in cmd
        and "--role-profile" not in cmd
        for cmd in session_start_hooks
    )
    dispatcher_match = any("session_start_dispatch.py" in cmd for cmd in session_start_hooks)
    assert direct_match or dispatcher_match, (
        "Claude SessionStart must register either the canonical service directly "
        "or a dispatcher under .claude/hooks/ that delegates to it"
    )
    if dispatcher_match:
        from pathlib import Path as _P

        dispatcher_source = _P(".claude/hooks/session_start_dispatch.py").read_text(encoding="utf-8")
        # Slice D: the behavioral contract lives in the shared core; the wrapper
        # delegates and only carries its harness identity.
        core_source = _P("scripts/session_start_dispatch_core.py").read_text(encoding="utf-8")
        assert "import session_start_dispatch_core" in dispatcher_source
        assert "claude" in dispatcher_source
        assert "session_self_initialization.py" in core_source
        assert "--emit-startup-service-payload" in core_source
        assert "--fast-hook" in core_source
        assert "--harness-name" in core_source
    assert any(
        "session_self_initialization.py" in hook["command"]
        and "--emit-wrapup" in hook["command"]
        and "--fast-hook" in hook["command"]
        and "--harness-name claude" in hook["command"]
        and "--harness-id B" not in hook["command"]
        and "--role-profile" not in hook["command"]
        for group in claude_settings["hooks"]["Stop"]
        for hook in group["hooks"]
    )


def test_codex_session_start_dispatcher_preserves_hook_specific_schema() -> None:
    module = _load_session_start_dispatcher()

    payload = module._session_start_payload("startup context")

    assert payload == {
        "hookSpecificOutput": {
            "hookEventName": "SessionStart",
            "additionalContext": "startup context",
        }
    }


def test_codex_session_start_dispatcher_json_is_utf8_safe_on_windows() -> None:
    module = _load_session_start_dispatcher()

    text = module._dump_payload(module._session_start_payload("Smart-poller notification \u2014 ready"))

    assert text.isascii()
    assert json.loads(text)["hookSpecificOutput"]["additionalContext"] == "Smart-poller notification \u2014 ready"


def test_codex_session_start_dispatcher_bridge_auto_dispatch_mode(tmp_path, monkeypatch, capsys) -> None:
    module = _load_session_start_dispatcher()
    monkeypatch.setattr(module, "OUT_DIR", tmp_path)
    monkeypatch.setenv("GTKB_BRIDGE_POLLER_RUN_ID", "test-run-002")
    monkeypatch.setenv("GTKB_BRIDGE_DISPATCH_KEYWORD", "::init gtkb lo")

    assert module.main() == 0
    payload = json.loads(capsys.readouterr().out)
    ctx = payload["hookSpecificOutput"]["additionalContext"]
    assert "Bridge Auto-Dispatch Session" in ctx
    assert "test-run-002" in ctx
    assert "Programmatic Startup Payload" not in ctx
    assert "discarded owner session-start stimulus" in ctx
    assert "active bridge auto-dispatch task" in ctx
    assert "TAFE/dispatcher bridge state" in ctx
    assert "status-bearing numbered bridge files" in ctx


def test_codex_hook_commands_avoid_shell_specific_command_substitution() -> None:
    codex_hooks = json.loads((REPO_ROOT / ".codex" / "hooks.json").read_text(encoding="utf-8"))
    _skip_if_codex_hooks_intentionally_empty(codex_hooks)
    commands = [
        hook["command"] for groups in codex_hooks["hooks"].values() for group in groups for hook in group["hooks"]
    ]

    assert commands
    assert all("$(" not in command for command in commands)
    assert all(command.split()[0].lower().endswith("pythonw.exe") for command in commands)
    assert all("run_py_no_window.py" not in command and "run_cmd_no_window.py" not in command for command in commands)
    assert any(
        "gtkb-hooks" in command and "session_start_dispatch.py" in command and "run_py_no_window " in command
        for command in commands
    )
    batch_commands = [command for command in commands if "--batch" in command]
    assert batch_commands
    assert all("run_py_no_window " in command for command in batch_commands)
    assert any("--batch user-prompt-submit" in command for command in batch_commands)
    assert any("--batch pretooluse-bash" in command for command in batch_commands)
    assert any("--batch pretooluse-apply-patch" in command for command in batch_commands)
    assert any("--batch posttooluse-bash" in command for command in batch_commands)
    assert len(_expanded_routes(codex_hooks, "UserPromptSubmit", "session_wrapup_trigger_dispatch.py")) == 1
    assert len(_expanded_routes(codex_hooks, "UserPromptSubmit", "workstream-focus.cmd")) == 1
    assert len(_expanded_routes(codex_hooks, "PreToolUse", "formal-artifact-approval.cmd")) == 1
    assert len(_expanded_routes(codex_hooks, "PreToolUse", "bridge-compliance-gate.cmd")) == 1
    assert len(_expanded_routes(codex_hooks, "PostToolUse", "bridge-compliance-audit.cmd")) == 1

    start_dispatcher = REPO_ROOT / ".codex" / "gtkb-hooks" / "session_start_dispatch.py"
    core_module = REPO_ROOT / "scripts" / "session_start_dispatch_core.py"
    if not start_dispatcher.is_file():
        assert os.environ.get("CI") == "true"
        return

    start_text = start_dispatcher.read_text(encoding="utf-8")
    core_text = core_module.read_text(encoding="utf-8")
    # Slice D: the codex wrapper carries only its harness identity + delegation;
    # the behavioral SessionStart contract lives in the shared core.
    assert "import session_start_dispatch_core" in start_text
    assert 'HARNESS_NAME = "codex"' in start_text
    assert 'HARNESS_ID = "A"' not in start_text
    # Behavioral contract (shared core):
    assert "--emit-startup-service-payload" in core_text
    assert "--harness-name" in core_text
    assert "--harness-id" in core_text
    assert "harness_identity" in core_text
    assert "resolved_harness_id" in core_text
    assert "--role-profile" not in core_text
    assert "STARTUP_SERVICE" in core_text
    assert "STARTUP_FRESHNESS_CONTRACT_VERSION" in core_text
    assert "Programmatic Startup Payload" in core_text
    assert "_valid_session_start_payload" in core_text
    assert "_purge_previous_diagnostics" in core_text
    assert "GTKB_STARTUP_REQUESTED_AT" in core_text
    assert "subprocess.run" in core_text
    assert "STARTUP_SERVICE_TIMEOUT_SECONDS = 150.0" in core_text
    assert "STARTUP_SERVICE_TIMEOUT_ENV" in core_text
    assert "_startup_service_timeout_seconds" in core_text
    assert "_startup_service_timeout_seconds_for_harness" in core_text
    assert "timeout=_startup_service_timeout_seconds_for_harness()" in core_text
    assert "Startup First-Response Directive" not in core_text
    assert "_live_bridge_index_context" not in core_text
    assert "Mandatory Direct Live Bridge Index Read" not in core_text
    assert "SHA-256" not in core_text
    assert "Would you like to optimize token consumption now or defer to the next session? (Y/N)" not in core_text
    assert "Would you like to proceed with established priority actions? (Y/N)" not in core_text
    assert "Token Consumption Reduction Options second" not in core_text
    assert "Three Top Priority Actions third" not in core_text
    assert "hookSpecificOutput" in core_text
    assert "hookEventName" in core_text
    assert "SessionStart" in core_text
    assert "additionalContext" in core_text
    assert "startupFreshness" in core_text
    assert "request_started_at" in core_text
    assert "report_origin" in core_text
    assert "startup_payload_fresh" in core_text
    assert "last-session-start.json" in core_text
    assert "last-session-start.err" in core_text

    session_start_cmd = (REPO_ROOT / ".codex" / "gtkb-hooks" / "session-start.cmd").read_text(encoding="utf-8")
    assert "harness_identity.py" in session_start_cmd
    assert "GTKB_HARNESS_ID" in session_start_cmd
    assert "--harness-name codex" in session_start_cmd
    assert "--harness-id %GTKB_HARNESS_ID%" in session_start_cmd

    stop_dispatcher = REPO_ROOT / ".codex" / "gtkb-hooks" / "session_stop_dispatch.py"
    stop_text = stop_dispatcher.read_text(encoding="utf-8")
    assert "--emit-wrapup" in stop_text
    assert "--harness-name" in stop_text
    assert "--harness-id" in stop_text
    assert 'HARNESS_NAME = "codex"' in stop_text
    assert 'HARNESS_ID = "A"' not in stop_text
    assert "resolved_harness_id" in stop_text
    assert "--role-profile" not in stop_text
    assert "CREATE_NO_WINDOW" in stop_text
    assert "CREATE_NEW_PROCESS_GROUP" in stop_text
    assert "subprocess.DEVNULL" in stop_text

    wrapup_dispatcher = REPO_ROOT / ".codex" / "gtkb-hooks" / "session_wrapup_trigger_dispatch.py"
    wrapup_text = wrapup_dispatcher.read_text(encoding="utf-8")
    assert "--emit-wrapup" in wrapup_text
    assert "--force-wrapup" in wrapup_text
    assert "--harness-name" in wrapup_text
    assert "--harness-id" in wrapup_text
    assert 'HARNESS_NAME = "codex"' in wrapup_text
    assert 'HARNESS_ID = "A"' not in wrapup_text
    assert "resolved_harness_id" in wrapup_text
    assert "--role-profile" not in wrapup_text
    assert "_interactive_role_profile" not in wrapup_text
    assert "UserPromptSubmit" in wrapup_text
    assert "ACCEPTED_TRIGGER_PHRASES" in wrapup_text
    assert "_is_wrapup_trigger" in wrapup_text
    assert "_startup_input_gate_active" in wrapup_text
    assert "discard_next_user_prompt" in wrapup_text
    assert "startup_response_pending" in wrapup_text
    assert "please$" in wrapup_text
    assert "wrap up this session" in wrapup_text
    assert "start a new session" in wrapup_text
    assert "begin fresh" in wrapup_text
    assert "subprocess.run" in wrapup_text
    assert 'print("{}")' in wrapup_text
    assert "hookSpecificOutput" in wrapup_text
    assert "hookEventName" in wrapup_text
    assert "additionalContext" in wrapup_text
    assert "last-wrapup-trigger.json" in wrapup_text
    assert "last-wrapup-trigger.err" in wrapup_text
    assert "last-wrapup-trigger-input.json" in wrapup_text

    workstream_wrapper = REPO_ROOT / ".codex" / "gtkb-hooks" / "workstream-focus.cmd"
    workstream_text = workstream_wrapper.read_text(encoding="utf-8")
    assert "workstream-focus.py" in workstream_text
    assert "GTKB_HARNESS_NAME=codex" in workstream_text
    assert "GTKB_HARNESS_ID=A" not in workstream_text

    bridge_wrapper = REPO_ROOT / ".codex" / "gtkb-hooks" / "bridge-compliance-gate.cmd"
    bridge_wrapper_text = bridge_wrapper.read_text(encoding="utf-8")
    assert "bridge-compliance-gate-bash-adapter.py" in bridge_wrapper_text
    assert "bridge-compliance-gate.py" in bridge_wrapper_text

    bridge_adapter = REPO_ROOT / ".codex" / "gtkb-hooks" / "bridge-compliance-gate-bash-adapter.py"
    bridge_adapter_text = bridge_adapter.read_text(encoding="utf-8")
    assert "BRIDGE_FILE_WRITE_PATTERNS" in bridge_adapter_text
    assert "synthetic Claude-shape" in bridge_adapter_text

    bridge_audit = REPO_ROOT / ".codex" / "gtkb-hooks" / "bridge-compliance-audit.cmd"
    bridge_audit_text = bridge_audit.read_text(encoding="utf-8")
    assert "bridge-compliance-gate.py" in bridge_audit_text
    assert "--audit-only" in bridge_audit_text


def test_codex_parity_requires_bridge_compliance_gate_when_hooks_enabled(tmp_path) -> None:
    """SPEC-CODEX-HARNESS-GOVERNANCE-PARITY-001 A1."""
    module = _load_module()
    (tmp_path / ".codex").mkdir()
    (tmp_path / ".claude" / "hooks").mkdir(parents=True)
    (tmp_path / ".claude").mkdir(exist_ok=True)
    (tmp_path / "scripts").mkdir()
    (tmp_path / "harness-state").mkdir()
    (tmp_path / ".codex" / "config.toml").write_text("[features]\nhooks = true\n", encoding="utf-8")
    (tmp_path / ".codex" / "hooks.json").write_text(
        json.dumps(
            {"hooks": {"PreToolUse": [], "PostToolUse": [], "SessionStart": [], "UserPromptSubmit": [], "Stop": []}}
        ),
        encoding="utf-8",
    )
    (tmp_path / ".claude" / "hooks" / "formal-artifact-approval-gate.py").write_text("print('{}')\n", encoding="utf-8")
    (tmp_path / ".claude" / "hooks" / "workstream-focus.py").write_text("print('{}')\n", encoding="utf-8")
    (tmp_path / ".claude" / "hooks" / "bridge-compliance-gate.py").write_text("print('{}')\n", encoding="utf-8")
    (tmp_path / "scripts" / "session_self_initialization.py").write_text("print('startup')\n", encoding="utf-8")
    (tmp_path / "harness-state" / "harness-identities.json").write_text(
        json.dumps({"schema_version": 1, "harnesses": {"codex": {"id": "A"}}}) + "\n",
        encoding="utf-8",
    )
    (tmp_path / "harness-state" / "harness-registry.json").write_text(
        json.dumps(
            {
                "schema_version": 1,
                "harnesses": [{"id": "A", "harness_type": "codex", "role": ["prime-builder"], "status": "active"}],
            }
        )
        + "\n",
        encoding="utf-8",
    )
    (tmp_path / ".claude" / "settings.json").write_text(
        json.dumps(
            {
                "hooks": {
                    "PreToolUse": [
                        {
                            "matcher": "Write|Edit",
                            "hooks": [{"type": "command", "command": "python .claude/hooks/bridge-compliance-gate.py"}],
                        },
                        {
                            "matcher": "Write|Edit",
                            "hooks": [
                                {"type": "command", "command": "python .claude/hooks/formal-artifact-approval-gate.py"}
                            ],
                        },
                    ],
                    "SessionStart": [],
                    "Stop": [],
                }
            }
        ),
        encoding="utf-8",
    )

    errors = module.check_project(tmp_path)

    assert any(
        "bridge-compliance" in error.lower() and "SPEC-CODEX-HARNESS-GOVERNANCE-PARITY-001" in error for error in errors
    ), f"Expected bridge-compliance SPEC A1 error; got errors: {errors}"


def test_codex_parity_repository_configuration_wires_bridge_compliance() -> None:
    module = _load_module()

    errors = module.check_project(REPO_ROOT)

    assert not errors


def test_codex_parity_skips_bridge_compliance_gate_when_hooks_disabled(tmp_path) -> None:
    module = _load_module()
    (tmp_path / ".codex").mkdir()
    (tmp_path / ".claude" / "hooks").mkdir(parents=True)
    (tmp_path / ".claude").mkdir(exist_ok=True)
    (tmp_path / "scripts").mkdir()
    (tmp_path / "harness-state").mkdir()
    (tmp_path / ".codex" / "config.toml").write_text("[features]\nhooks = false\n", encoding="utf-8")
    (tmp_path / ".codex" / "hooks.json").write_text(json.dumps({"hooks": {}}), encoding="utf-8")
    (tmp_path / ".claude" / "hooks" / "formal-artifact-approval-gate.py").write_text("print('{}')\n", encoding="utf-8")
    (tmp_path / ".claude" / "hooks" / "workstream-focus.py").write_text("print('{}')\n", encoding="utf-8")
    (tmp_path / ".claude" / "hooks" / "bridge-compliance-gate.py").write_text("print('{}')\n", encoding="utf-8")
    (tmp_path / "scripts" / "session_self_initialization.py").write_text("print('startup')\n", encoding="utf-8")
    (tmp_path / "harness-state" / "harness-identities.json").write_text(
        json.dumps({"schema_version": 1, "harnesses": {"codex": {"id": "A"}}}) + "\n",
        encoding="utf-8",
    )
    (tmp_path / "harness-state" / "harness-registry.json").write_text(
        json.dumps(
            {
                "schema_version": 1,
                "harnesses": [{"id": "A", "harness_type": "codex", "role": ["prime-builder"], "status": "active"}],
            }
        )
        + "\n",
        encoding="utf-8",
    )
    (tmp_path / ".claude" / "settings.json").write_text(
        json.dumps(
            {
                "hooks": {
                    "PreToolUse": [
                        {
                            "matcher": "Write|Edit",
                            "hooks": [{"type": "command", "command": "python .claude/hooks/bridge-compliance-gate.py"}],
                        }
                    ],
                    "SessionStart": [],
                    "Stop": [],
                }
            }
        ),
        encoding="utf-8",
    )

    errors = module.check_project(tmp_path)

    assert not any("bridge-compliance" in error.lower() for error in errors)


def test_codex_hook_parity_reports_missing_codex_hooks_file(tmp_path) -> None:
    module = _load_module()
    (tmp_path / ".codex").mkdir()
    (tmp_path / ".claude" / "hooks").mkdir(parents=True)
    (tmp_path / ".claude" / "settings.json").parent.mkdir(exist_ok=True)
    (tmp_path / ".codex" / "config.toml").write_text("[features]\nhooks = true\n", encoding="utf-8")
    (tmp_path / ".claude" / "settings.json").write_text(
        json.dumps(
            {
                "hooks": {
                    "PreToolUse": [
                        {
                            "hooks": [
                                {
                                    "type": "command",
                                    "command": "python .claude/hooks/formal-artifact-approval-gate.py",
                                }
                            ]
                        }
                    ]
                }
            }
        ),
        encoding="utf-8",
    )
    (tmp_path / ".claude" / "hooks" / "formal-artifact-approval-gate.py").write_text(
        "print('{}')\n",
        encoding="utf-8",
    )

    errors = module.check_project(tmp_path)

    assert any(".codex/hooks.json" in error for error in errors)


def test_codex_hook_parity_requires_bash_matcher(tmp_path) -> None:
    module = _load_module()
    (tmp_path / ".codex").mkdir()
    (tmp_path / ".claude" / "hooks").mkdir(parents=True)
    (tmp_path / ".claude" / "rules").mkdir()
    (tmp_path / "scripts").mkdir()
    (tmp_path / ".codex" / "config.toml").write_text("[features]\nhooks = true\n", encoding="utf-8")
    (tmp_path / "harness-state").mkdir()
    (tmp_path / "harness-state" / "harness-identities.json").write_text(
        json.dumps({"schema_version": 1, "harnesses": {"codex": {"id": "A"}}}) + "\n",
        encoding="utf-8",
    )
    (tmp_path / "harness-state" / "harness-registry.json").write_text(
        json.dumps(
            {
                "schema_version": 1,
                "harnesses": [{"id": "A", "harness_type": "codex", "role": ["loyal-opposition"], "status": "active"}],
            }
        )
        + "\n",
        encoding="utf-8",
    )
    (tmp_path / ".claude" / "hooks" / "formal-artifact-approval-gate.py").write_text(
        "print('{}')\n",
        encoding="utf-8",
    )
    (tmp_path / ".claude" / "hooks" / "bridge-compliance-gate.py").write_text(
        "print('{}')\n",
        encoding="utf-8",
    )
    (tmp_path / ".claude" / "hooks" / "workstream-focus.py").write_text(
        "print('{}')\n",
        encoding="utf-8",
    )
    (tmp_path / "scripts" / "session_self_initialization.py").write_text(
        "print('startup')\n",
        encoding="utf-8",
    )
    (tmp_path / ".claude" / "settings.json").write_text(
        json.dumps(
            {
                "hooks": {
                    "PreToolUse": [
                        {
                            "hooks": [
                                {
                                    "type": "command",
                                    "command": "python .claude/hooks/formal-artifact-approval-gate.py",
                                }
                            ]
                        }
                    ]
                }
            }
        ),
        encoding="utf-8",
    )
    (tmp_path / ".codex" / "hooks.json").write_text(
        json.dumps(
            {
                "hooks": {
                    "PreToolUse": [
                        {
                            "matcher": "Edit|Write",
                            "hooks": [
                                {
                                    "type": "command",
                                    "command": (
                                        'python "$(git rev-parse --show-toplevel)/'
                                        '.claude/hooks/formal-artifact-approval-gate.py"'
                                    ),
                                    "timeout": 5,
                                }
                            ],
                        }
                    ]
                }
            }
        ),
        encoding="utf-8",
    )

    errors = module.check_project(tmp_path)

    assert "Codex formal artifact PreToolUse hook must use matcher = 'Bash'" in errors
