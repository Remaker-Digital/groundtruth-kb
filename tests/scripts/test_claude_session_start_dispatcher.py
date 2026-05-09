"""Tests for the Claude SessionStart hook dispatcher.

Authority: bridge/gtkb-claude-session-start-parity-001.md (Codex GO at -002).

Verifies:
- Dispatcher emits a properly-shaped SessionStart `hookSpecificOutput` envelope
  (`GOV-SESSION-SELF-INITIALIZATION-001`).
- Payload includes the canonical role/governance disclosure
  (`PB-SESSION-STARTUP-GOVERNANCE-DISCLOSURE-001`).
- Payload includes token-budget content
  (`DCL-SESSION-STARTUP-TOKEN-BUDGET-001`).
- Envelope shape matches the Codex dispatcher
  (`SPEC-CODEX-STARTUP-INPUT-GATE-TRIGGER-001` parallel/precedent).
- Diagnostic files land under `.claude/hooks/`
  (`ADR-ISOLATION-APPLICATION-PLACEMENT-001`).
- `.claude/settings.json` SessionStart timeout matches `.codex/hooks.json`.
- Canonical service `--emit-report --fast-hook --harness-name claude` no
  longer prints the `scripts.check_harness_parity` import error
  (Change 3 — harness-parity import repair).
- Dispatcher fails soft and emits a degraded-banner fallback when the
  startup service is unreachable.
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[2]
DISPATCHER = PROJECT_ROOT / ".claude" / "hooks" / "session_start_dispatch.py"
DIAG_JSON = PROJECT_ROOT / ".claude" / "hooks" / "last-session-start.json"
DIAG_ERR = PROJECT_ROOT / ".claude" / "hooks" / "last-session-start.err"
CLAUDE_SETTINGS = PROJECT_ROOT / ".claude" / "settings.json"
CODEX_HOOKS = PROJECT_ROOT / ".codex" / "hooks.json"
STARTUP_SERVICE = PROJECT_ROOT / "scripts" / "session_self_initialization.py"


def _run_dispatcher(env: dict[str, str] | None = None) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(DISPATCHER)],
        cwd=str(PROJECT_ROOT),
        capture_output=True,
        text=True,
        encoding="utf-8",
        timeout=90,
        check=False,
        env=env,
    )


def test_dispatcher_emits_session_start_envelope() -> None:
    """`hookSpecificOutput.hookEventName == 'SessionStart'` per Claude Code contract.

    Spec: GOV-SESSION-SELF-INITIALIZATION-001.
    """
    result = _run_dispatcher()
    assert result.returncode == 0, f"dispatcher non-zero exit: {result.stderr}"
    payload = json.loads(result.stdout)
    assert "hookSpecificOutput" in payload
    hook_output = payload["hookSpecificOutput"]
    assert hook_output["hookEventName"] == "SessionStart"
    assert isinstance(hook_output["additionalContext"], str)
    assert len(hook_output["additionalContext"]) > 100


def test_envelope_contains_governance_disclosure() -> None:
    """Role / governance / bridge / poller / role-mapping disclosure present.

    Spec: PB-SESSION-STARTUP-GOVERNANCE-DISCLOSURE-001.
    """
    result = _run_dispatcher()
    payload = json.loads(result.stdout)
    ctx = payload["hookSpecificOutput"]["additionalContext"]
    assert "Programmatic Startup Payload" in ctx
    assert "Role being assumed:" in ctx
    assert "Role mapping source:" in ctx
    assert "harness-state/role-assignments.json" in ctx


def test_envelope_contains_token_budget_content() -> None:
    """Startup payload exposes token-budget context per DCL.

    Spec: DCL-SESSION-STARTUP-TOKEN-BUDGET-001.
    """
    result = _run_dispatcher()
    payload = json.loads(result.stdout)
    ctx = payload["hookSpecificOutput"]["additionalContext"]
    assert "Token measurement status:" in ctx
    assert "reducing startup token consumption" in ctx.lower() or "token consumption" in ctx.lower()


def test_bridge_auto_dispatch_context_bypasses_interactive_startup() -> None:
    """Bridge poller dispatch sessions must process the initial prompt.

    The verified smart poller launches headless harnesses with
    ``GTKB_BRIDGE_POLLER_RUN_ID`` in the environment. In that mode the
    SessionStart hook must not emit interactive fresh-session semantics that
    cause Codex to discard the auto-dispatch prompt as a startup stimulus.
    """
    env = dict(os.environ)
    env["GTKB_BRIDGE_POLLER_RUN_ID"] = "test-run-001"

    result = _run_dispatcher(env=env)
    assert result.returncode == 0, f"dispatcher non-zero exit: {result.stderr}"
    payload = json.loads(result.stdout)
    ctx = payload["hookSpecificOutput"]["additionalContext"]
    assert "Bridge Auto-Dispatch Session" in ctx
    assert "test-run-001" in ctx
    assert "Programmatic Startup Payload" not in ctx
    assert "discarded owner session-start stimulus" in ctx
    assert "active bridge auto-dispatch task" in ctx
    assert "bridge/INDEX.md" in ctx


def test_envelope_shape_parity_with_codex() -> None:
    """Claude dispatcher emits same envelope keys as the Codex dispatcher.

    Both dispatchers must produce `hookSpecificOutput` with exactly the
    `hookEventName` and `additionalContext` keys at minimum.

    Spec: SPEC-CODEX-STARTUP-INPUT-GATE-TRIGGER-001 (parallel/precedent).
    """
    result = _run_dispatcher()
    payload = json.loads(result.stdout)
    hook_output = payload["hookSpecificOutput"]
    required_keys = {"hookEventName", "additionalContext"}
    assert required_keys.issubset(hook_output.keys())


def test_diagnostic_files_land_in_claude_hooks_dir() -> None:
    """Diagnostic files must resolve under E:\\GT-KB\\.claude\\hooks\\.

    Spec: ADR-ISOLATION-APPLICATION-PLACEMENT-001.
    """
    _run_dispatcher()
    assert DIAG_JSON.is_file(), f"missing {DIAG_JSON}"
    assert DIAG_ERR.is_file(), f"missing {DIAG_ERR}"
    # Both files must be under the project root
    assert PROJECT_ROOT in DIAG_JSON.resolve().parents
    assert PROJECT_ROOT in DIAG_ERR.resolve().parents
    # Diagnostic JSON must contain the canonical hookSpecificOutput envelope
    content = DIAG_JSON.read_text(encoding="utf-8")
    assert "hookSpecificOutput" in content


def test_session_start_timeout_alignment() -> None:
    """`.claude/settings.json` SessionStart timeout matches `.codex/hooks.json`.

    Both must be 60 s (Codex's existing value); this prevents Claude-side
    truncation under load.
    """
    claude = json.loads(CLAUDE_SETTINGS.read_text(encoding="utf-8"))
    codex = json.loads(CODEX_HOOKS.read_text(encoding="utf-8"))

    def _session_start_timeout(settings: dict) -> int:
        for entry in settings.get("hooks", {}).get("SessionStart", []):
            for hook in entry.get("hooks", []):
                if "timeout" in hook:
                    return int(hook["timeout"])
        return -1

    claude_timeout = _session_start_timeout(claude)
    codex_timeout = _session_start_timeout(codex)
    assert claude_timeout > 0, "Claude settings has no SessionStart timeout"
    assert codex_timeout > 0, "Codex hooks has no SessionStart timeout"
    assert claude_timeout == codex_timeout, f"Claude SessionStart timeout {claude_timeout}s != Codex {codex_timeout}s"


def test_harness_parity_import_repaired() -> None:
    """The canonical service no longer prints the import error.

    Change 3 — repairs `No module named 'scripts.check_harness_parity'`
    by ensuring project root is on sys.path before sibling imports.
    """
    result = subprocess.run(
        [
            sys.executable,
            str(STARTUP_SERVICE),
            "--emit-report",
            "--fast-hook",
            "--harness-name",
            "claude",
        ],
        cwd=str(PROJECT_ROOT),
        capture_output=True,
        text=True,
        encoding="utf-8",
        timeout=60,
        check=False,
    )
    assert "No module named 'scripts.check_harness_parity'" not in result.stdout
    assert "Harness parity:" in result.stdout
    # Should NOT be "unavailable" anymore
    assert "Harness parity: unavailable" not in result.stdout


def test_dispatcher_fallback_on_broken_startup_service(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    """If the startup service path is unreachable, dispatcher emits a fallback.

    Validates fail-soft behavior — dispatcher must always emit a valid
    SessionStart envelope, even when the canonical service is broken.
    """
    import importlib.util

    spec = importlib.util.spec_from_file_location(
        "session_start_dispatch_test_fallback",
        DISPATCHER,
    )
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)

    # Point STARTUP_SERVICE at a path that does not exist; subprocess.run
    # will raise FileNotFoundError, which the dispatcher catches and routes
    # through `_fallback_context`.
    module.STARTUP_SERVICE = tmp_path / "does_not_exist.py"

    rc = module.main()
    captured = capsys.readouterr()
    assert rc == 0
    assert captured.out, "dispatcher emitted no stdout on broken-service path"
    payload = json.loads(captured.out)
    assert payload["hookSpecificOutput"]["hookEventName"] == "SessionStart"
    ctx = payload["hookSpecificOutput"]["additionalContext"]
    assert "Startup Service Degraded" in ctx
    assert "Dashboard" in ctx
