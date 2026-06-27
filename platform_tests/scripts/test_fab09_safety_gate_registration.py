"""FAB-09: Safety-gate registration normalization and capture hook implementation.

Spec-derived tests for WI-4421 / PROJECT-FABLE-INVESTIGATION.

Tests:
  S294 (essential → tracked): safety gates in tracked settings + Codex parity.
  SPEC-AUQ-POLICY-ENGINE-001: owner-decision-capture.py is a real impl, not a stub.
  S292 (no dead-mechanism claims): scheduler.py, SCHEDULE.md, stubs are gone.
  Template parity: active hooks match their template twins.
"""

from __future__ import annotations

import ast
import json
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[2]
_CLAUDE_SETTINGS = _ROOT / ".claude" / "settings.json"
_CODEX_HOOKS = _ROOT / ".codex" / "hooks.json"
_HOOKS_DIR = _ROOT / ".claude" / "hooks"
_TEMPLATES_DIR = _ROOT / "groundtruth-kb" / "templates" / "hooks"


def _load_settings() -> dict:
    return json.loads(_CLAUDE_SETTINGS.read_text(encoding="utf-8"))


def _load_codex_hooks() -> dict:
    return json.loads(_CODEX_HOOKS.read_text(encoding="utf-8"))


def _settings_hook_commands(settings: dict, event: str) -> list[str]:
    """Extract all hook commands for a given event from settings.json."""
    commands: list[str] = []
    for group in settings.get("hooks", {}).get(event, []):
        for hook in group.get("hooks", []):
            cmd = hook.get("command", "")
            if cmd:
                commands.append(cmd)
    return commands


def _codex_hook_commands(codex: dict, event: str) -> list[str]:
    """Extract all hook commands for a given event from .codex/hooks.json."""
    commands: list[str] = []
    for group in codex.get("hooks", {}).get(event, []):
        for hook in group.get("hooks", []):
            cmd = hook.get("command", "")
            if cmd:
                commands.append(cmd)
    return commands


# --- S294: Safety gates in tracked settings ---


def test_destructive_gate_in_tracked_settings():
    settings = _load_settings()
    cmds = _settings_hook_commands(settings, "PreToolUse")
    assert any("destructive-gate.py" in c for c in cmds), (
        "destructive-gate.py must be registered in tracked .claude/settings.json PreToolUse"
    )


def test_credential_scan_in_tracked_settings():
    settings = _load_settings()
    cmds = _settings_hook_commands(settings, "PreToolUse")
    assert any("credential-scan.py" in c for c in cmds), (
        "credential-scan.py must be registered in tracked .claude/settings.json PreToolUse"
    )


def test_destructive_gate_codex_parity():
    codex = _load_codex_hooks()
    cmds = _codex_hook_commands(codex, "PreToolUse")
    assert any("destructive-gate" in c for c in cmds), (
        "destructive-gate must be registered in .codex/hooks.json PreToolUse"
    )


def test_credential_scan_codex_parity():
    codex = _load_codex_hooks()
    cmds = _codex_hook_commands(codex, "PreToolUse")
    assert any("credential-scan" in c for c in cmds), (
        "credential-scan must be registered in .codex/hooks.json PreToolUse"
    )


# --- SPEC-AUQ-POLICY-ENGINE-001: capture hooks are real implementations ---


def test_owner_decision_capture_is_not_stub():
    path = _HOOKS_DIR / "owner-decision-capture.py"
    assert path.exists(), "owner-decision-capture.py must exist"
    content = path.read_text(encoding="utf-8")
    lines = [line for line in content.strip().splitlines() if line.strip()]
    assert len(lines) > 35, (
        f"owner-decision-capture.py has {len(lines)} non-blank lines; "
        "stubs have <35 — this should be a real implementation"
    )
    assert "scaffold stub" not in content.lower(), "owner-decision-capture.py still contains scaffold-stub marker text"


def test_owner_decision_capture_registered_post_tool_use():
    settings = _load_settings()
    cmds = _settings_hook_commands(settings, "PostToolUse")
    assert any("owner-decision-capture.py" in c for c in cmds), (
        "owner-decision-capture.py must be registered in PostToolUse"
    )


def test_gov09_capture_is_not_stub():
    path = _HOOKS_DIR / "gov09-capture.py"
    assert path.exists(), "gov09-capture.py must exist"
    content = path.read_text(encoding="utf-8")
    lines = [line for line in content.strip().splitlines() if line.strip()]
    assert len(lines) > 35, (
        f"gov09-capture.py has {len(lines)} non-blank lines; stubs have <35 — this should be a real implementation"
    )


def test_gov09_capture_registered_user_prompt_submit():
    settings = _load_settings()
    cmds = _settings_hook_commands(settings, "UserPromptSubmit")
    assert any("gov09-capture.py" in c for c in cmds), "gov09-capture.py must be registered in UserPromptSubmit"


# --- S292: dead mechanisms removed ---


def test_scheduler_py_absent():
    assert not (_HOOKS_DIR / "scheduler.py").exists(), "scheduler.py was retired (HYG-045) and must not exist"


def test_schedule_md_absent():
    assert not (_ROOT / ".claude" / "SCHEDULE.md").exists(), "SCHEDULE.md was retired (HYG-045) and must not exist"


def test_claude_md_no_session_scheduler_claim():
    claude_md = (_ROOT / "CLAUDE.md").read_text(encoding="utf-8")
    assert "Session Scheduler" not in claude_md, "CLAUDE.md must not claim a Session Scheduler (HYG-045: retired)"


def test_turn_marker_stub_absent():
    assert not (_HOOKS_DIR / "turn-marker.py").exists(), "turn-marker.py dead stub was retired (HYG-050)"


def test_delib_preflight_gate_stub_absent():
    assert not (_HOOKS_DIR / "delib-preflight-gate.py").exists(), (
        "delib-preflight-gate.py dead stub was retired (HYG-050)"
    )


def test_turn_marker_template_absent():
    assert not (_TEMPLATES_DIR / "turn-marker.py").exists(), "turn-marker.py template twin must also be removed"


def test_delib_preflight_gate_template_absent():
    assert not (_TEMPLATES_DIR / "delib-preflight-gate.py").exists(), (
        "delib-preflight-gate.py template twin must also be removed"
    )


# --- Template parity: active hooks match template twins ---


def _template_parity(hook_name: str) -> None:
    active = (_HOOKS_DIR / hook_name).read_text(encoding="utf-8")
    template = (_TEMPLATES_DIR / hook_name).read_text(encoding="utf-8")
    assert active == template, f"{hook_name}: active hook and template twin have diverged"


def test_delib_common_template_parity():
    _template_parity("_delib_common.py")


def test_owner_decision_capture_template_parity():
    _template_parity("owner-decision-capture.py")


def test_gov09_capture_template_parity():
    _template_parity("gov09-capture.py")


# --- Structural: capture hooks import _delib_common ---


def test_owner_decision_capture_imports_delib_common():
    content = (_HOOKS_DIR / "owner-decision-capture.py").read_text(encoding="utf-8")
    tree = ast.parse(content)
    imports = [
        node.names[0].name
        for node in ast.walk(tree)
        if isinstance(node, ast.ImportFrom) and node.module == "_delib_common"
    ]
    assert "insert_deliberation" in imports, (
        "owner-decision-capture.py must import insert_deliberation from _delib_common"
    )


def test_gov09_capture_imports_delib_common():
    content = (_HOOKS_DIR / "gov09-capture.py").read_text(encoding="utf-8")
    tree = ast.parse(content)
    imports = [
        node.names[0].name
        for node in ast.walk(tree)
        if isinstance(node, ast.ImportFrom) and node.module == "_delib_common"
    ]
    assert "insert_deliberation" in imports, "gov09-capture.py must import insert_deliberation from _delib_common"


# --- Doctor checks: safety-gate registration + stub reporting (HYG-050/S294 deferred items) ---


def test_doctor_safety_gate_registration_pass():
    """_check_safety_gate_registration returns pass when both gates are registered."""
    from groundtruth_kb.project.doctor import _check_safety_gate_registration

    result = _check_safety_gate_registration(_ROOT)
    assert result.status == "pass", f"safety-gate-registration check should pass on live repo: {result.message}"


def test_doctor_capture_hook_stub_status_pass():
    """_check_capture_hook_stub_status returns pass (not stubbed) for live hooks."""
    from groundtruth_kb.project.doctor import _check_capture_hook_stub_status

    result = _check_capture_hook_stub_status(_ROOT)
    assert result.status == "pass", f"capture-hook-stub-status should pass on live repo: {result.message}"


def test_doctor_safety_gate_registration_detects_missing(tmp_path):
    """_check_safety_gate_registration returns warning for empty settings."""
    settings_dir = tmp_path / ".claude"
    settings_dir.mkdir(parents=True)
    (settings_dir / "settings.json").write_text('{"hooks":{}}', encoding="utf-8")

    from groundtruth_kb.project.doctor import _check_safety_gate_registration

    result = _check_safety_gate_registration(tmp_path)
    assert result.status == "warning"
    assert "destructive-gate.py" in result.message
    assert "credential-scan.py" in result.message


def test_doctor_capture_hook_stub_detection(tmp_path):
    """_check_capture_hook_stub_status reports stubs with <35 non-blank lines."""
    hooks_dir = tmp_path / ".claude" / "hooks"
    hooks_dir.mkdir(parents=True)
    (hooks_dir / "owner-decision-capture.py").write_text("# scaffold stub\npass\n", encoding="utf-8")
    (hooks_dir / "gov09-capture.py").write_text(
        "\n".join(f"line_{i} = {i}" for i in range(40)) + "\n", encoding="utf-8"
    )

    from groundtruth_kb.project.doctor import _check_capture_hook_stub_status

    result = _check_capture_hook_stub_status(tmp_path)
    assert result.status == "warning"
    assert "owner-decision-capture.py" in result.message
    assert "stubbed" in result.message


def test_canonical_terminology_names_credential_scan():
    """canonical-terminology.md must name credential-scan.py per FAB-09 AC."""
    ct = (_ROOT / ".claude" / "rules" / "canonical-terminology.md").read_text(encoding="utf-8")
    assert "credential-scan.py" in ct, "canonical-terminology.md scanner-safe-writer entry must name credential-scan.py"
