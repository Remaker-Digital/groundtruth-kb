"""Regression checks for Codex hook parity with Agent Red governance hooks."""

from __future__ import annotations

import importlib.util
import json
import os
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
SCRIPT_PATH = REPO_ROOT / "scripts" / "check_codex_hook_parity.py"
CODEX_SESSION_START_DISPATCHER = REPO_ROOT / ".codex" / "gtkb-hooks" / "session_start_dispatch.py"


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


def test_codex_hook_parity_passes_for_repository_configuration(capsys) -> None:
    module = _load_module()

    assert module.main(["--project-root", str(REPO_ROOT)]) == 0

    output = capsys.readouterr().out
    assert "Codex hook parity: PASS" in output
    assert "Windows shell-portable command forms" in output


def test_codex_hook_parity_requires_session_lifecycle_hook_intent() -> None:
    module = _load_module()

    errors = module.check_project(REPO_ROOT)

    assert not errors
    codex_hooks = json.loads((REPO_ROOT / ".codex" / "hooks.json").read_text(encoding="utf-8"))
    claude_settings = json.loads((REPO_ROOT / ".claude" / "settings.json").read_text(encoding="utf-8"))
    assert any(
        "gtkb-hooks" in hook["command"] and "session_start_dispatch.py" in hook["command"]
        for group in codex_hooks["hooks"]["SessionStart"]
        for hook in group["hooks"]
    )
    assert any(
        "single_harness_bridge_automation.py" in hook["command"] and "--ensure" in hook["command"]
        for group in codex_hooks["hooks"]["SessionStart"]
        for hook in group["hooks"]
    )
    assert all(
        hook.get("timeout", 0) >= 60
        for group in codex_hooks["hooks"]["SessionStart"]
        for hook in group["hooks"]
        if "session_start_dispatch.py" in hook.get("command", "")
    )
    assert any(
        "gtkb-hooks" in hook["command"] and "session_wrapup_trigger_dispatch.py" in hook["command"]
        for group in codex_hooks["hooks"]["UserPromptSubmit"]
        for hook in group["hooks"]
    )
    assert any(
        "gtkb-hooks" in hook["command"] and "workstream-focus.cmd" in hook["command"]
        for group in codex_hooks["hooks"]["UserPromptSubmit"]
        for hook in group["hooks"]
    )
    assert any(
        group.get("matcher") == "Bash" and any("workstream-focus.cmd" in hook["command"] for hook in group["hooks"])
        for group in codex_hooks["hooks"]["PreToolUse"]
    )
    assert any(
        group.get("matcher") == "Bash"
        and any("bridge-compliance-gate.cmd" in hook["command"] for hook in group["hooks"])
        for group in codex_hooks["hooks"]["PreToolUse"]
    )
    assert any(
        group.get("matcher") == "Bash"
        and any("bridge-compliance-audit.cmd" in hook["command"] for hook in group["hooks"])
        for group in codex_hooks["hooks"]["PostToolUse"]
    )
    # Per bridge/gtkb-bridge-poller-event-driven-replacement-slice-3-hook-registrations
    # Codex GO at -004: Slice 3 registers a Codex `Stop` hook that invokes
    # scripts/cross_harness_bridge_trigger.py with --stop-hook. The hook satisfies
    # the OpenAI Codex Stop output contract by emitting `{}` JSON to stdout. The
    # previous absence assertion is replaced with presence assertions scoped to
    # bridge dispatch substrates. Codex Stop may invoke the cross-harness trigger
    # and the single-harness activation manager; lifecycle wrap-up remains banned.
    assert "Stop" in codex_hooks["hooks"], (
        "Codex Stop hook must be registered (Slice 3 cross-harness trigger). "
        "Pre-Slice-3 baseline (`Stop` absent from `.codex/hooks.json`) is "
        "superseded by gtkb-bridge-poller-event-driven-replacement-slice-3 GO -004."
    )
    codex_stop_hooks = codex_hooks["hooks"]["Stop"]
    # Stop matchers are not supported by Codex; entries must be matcher-less.
    for group in codex_stop_hooks:
        assert group.get("matcher") in (None, ""), "Codex Stop entries must not declare a matcher (Codex hooks docs)"
    assert any(
        "cross_harness_bridge_trigger.py" in hook.get("command", "") and "--stop-hook" in hook.get("command", "")
        for group in codex_stop_hooks
        for hook in group["hooks"]
    ), (
        "Codex Stop must invoke cross_harness_bridge_trigger.py with --stop-hook "
        "(satisfies OpenAI Codex Stop JSON output contract by emitting `{}` on stdout)"
    )
    assert any(
        "single_harness_bridge_automation.py" in hook.get("command", "")
        and "--ensure" in hook.get("command", "")
        and "--dispatch-now" in hook.get("command", "")
        for group in codex_stop_hooks
        for hook in group["hooks"]
    ), (
        "Codex Stop must invoke single_harness_bridge_automation.py so single-harness "
        "topology gets an immediate post-session dispatch and multi-harness topology "
        "keeps the scheduled task deactivated."
    )
    # Lifecycle wrap-up scripts must NOT be registered through Codex Stop —
    # the parity test continues to ban that surface (the active wrap-up
    # mechanism is the release-candidate gate / harness-specific tooling).
    codex_stop_commands = [hook["command"] for group in codex_stop_hooks for hook in group["hooks"]]
    assert not any("session_wrapup" in cmd or "session_self_initialization.py" in cmd for cmd in codex_stop_commands), (
        "Codex Stop must not register lifecycle wrap-up scripts. Stop is limited "
        "to bridge dispatch substrates, not session wrap-up."
    )
    # Per bridge/gtkb-startup-enhancements-p1-003.md §2.4 (Codex GO at -004):
    # the previously-registered owner-decision-tracker-ups.cmd entry has been
    # removed because the wrapper file does not exist on disk, Codex hooks
    # are disabled on Windows per ADR-CODEX-HOOK-PARITY-FALLBACK-001, and the
    # active mechanism is scripts/check_pending_owner_decisions_parity.py in
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
    single_harness_automation_match = any(
        "single_harness_bridge_automation.py" in cmd and "--ensure" in cmd for cmd in session_start_hooks
    )
    assert direct_match or dispatcher_match, (
        "Claude SessionStart must register either the canonical service directly "
        "or a dispatcher under .claude/hooks/ that delegates to it"
    )
    assert single_harness_automation_match, (
        "Claude SessionStart must register the single-harness bridge automation activation hook"
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


def test_codex_session_start_dispatcher_bridge_auto_dispatch_mode(monkeypatch, capsys) -> None:
    module = _load_session_start_dispatcher()
    monkeypatch.setenv("GTKB_BRIDGE_POLLER_RUN_ID", "test-run-002")

    assert module.main() == 0
    payload = json.loads(capsys.readouterr().out)
    ctx = payload["hookSpecificOutput"]["additionalContext"]
    assert "Bridge Auto-Dispatch Session" in ctx
    assert "test-run-002" in ctx
    assert "Programmatic Startup Payload" not in ctx
    assert "discarded owner session-start stimulus" in ctx
    assert "active bridge auto-dispatch task" in ctx
    assert "bridge/INDEX.md" in ctx


def test_codex_hook_commands_avoid_shell_specific_command_substitution() -> None:
    codex_hooks = json.loads((REPO_ROOT / ".codex" / "hooks.json").read_text(encoding="utf-8"))
    commands = [
        hook["command"] for groups in codex_hooks["hooks"].values() for group in groups for hook in group["hooks"]
    ]

    assert commands
    assert all("$(" not in command for command in commands)
    assert any(
        "gtkb-hooks" in command and "session_start_dispatch.py" in command and command.startswith("python ")
        for command in commands
    )
    assert any(
        "gtkb-hooks" in command and "session_wrapup_trigger_dispatch.py" in command and command.startswith("python ")
        for command in commands
    )
    assert any(
        "gtkb-hooks" in command and "workstream-focus.cmd" in command and command.startswith("cmd /d /s /c ")
        for command in commands
    )
    assert any(
        "gtkb-hooks" in command and "bridge-compliance-gate.cmd" in command and command.startswith("cmd /d /s /c ")
        for command in commands
    )
    assert any(
        "gtkb-hooks" in command and "bridge-compliance-audit.cmd" in command and command.startswith("cmd /d /s /c ")
        for command in commands
    )

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
    assert "STARTUP_SERVICE_TIMEOUT_SECONDS = 50.0" in core_text
    assert "timeout=STARTUP_SERVICE_TIMEOUT_SECONDS" in core_text
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
    (tmp_path / ".codex" / "config.toml").write_text("[features]\ncodex_hooks = true\n", encoding="utf-8")
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
        json.dumps({"schema_version": 1, "harnesses": [{"id": "A", "harness_type": "codex", "role": ["prime-builder"], "status": "active"}]})
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
    (tmp_path / ".codex" / "config.toml").write_text("[features]\ncodex_hooks = false\n", encoding="utf-8")
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
        json.dumps({"schema_version": 1, "harnesses": [{"id": "A", "harness_type": "codex", "role": ["prime-builder"], "status": "active"}]})
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


def test_codex_hook_parity_reports_missing_codex_hooks(tmp_path) -> None:
    module = _load_module()
    (tmp_path / ".codex").mkdir()
    (tmp_path / ".claude" / "hooks").mkdir(parents=True)
    (tmp_path / ".claude" / "settings.json").parent.mkdir(exist_ok=True)
    (tmp_path / ".codex" / "config.toml").write_text("[features]\ncodex_hooks = true\n", encoding="utf-8")
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
    (tmp_path / ".codex" / "config.toml").write_text("[features]\ncodex_hooks = true\n", encoding="utf-8")
    (tmp_path / "harness-state").mkdir()
    (tmp_path / "harness-state" / "harness-identities.json").write_text(
        json.dumps({"schema_version": 1, "harnesses": {"codex": {"id": "A"}}}) + "\n",
        encoding="utf-8",
    )
    (tmp_path / "harness-state" / "harness-registry.json").write_text(
        json.dumps({"schema_version": 1, "harnesses": [{"id": "A", "harness_type": "codex", "role": ["loyal-opposition"], "status": "active"}]})
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
