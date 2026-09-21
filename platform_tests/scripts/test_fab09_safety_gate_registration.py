"""FAB-09: Safety-gate registration normalization and capture hook implementation.

Spec-derived tests for WI-4421 / PROJECT-FABLE-INVESTIGATION.

Tests:
  S294 (essential â†’ tracked): safety gates in tracked settings + Codex parity.
  S292 (no dead-mechanism claims): scheduler.py, SCHEDULE.md, stubs are gone.
  Template parity: active hooks match their template twins.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

_SOURCE_ROOT = Path(__file__).resolve().parents[2]
_ROOT = _SOURCE_ROOT
_CLAUDE_SETTINGS = _ROOT / ".claude" / "settings.json"
_CODEX_HOOKS = _ROOT / ".codex" / "hooks.json"
_HOOKS_DIR = _SOURCE_ROOT / ".harness-baseline-configuration" / "hooks"
_TEMPLATES_DIR = _ROOT / "groundtruth-kb" / "templates" / "hooks"


@pytest.fixture(scope="module", autouse=True)
def current_projection(tmp_path_factory):
    """Check disposable current derivations, never another installed harness."""
    from scripts.check_harness_parity import _load_projector

    global _ROOT, _CLAUDE_SETTINGS, _CODEX_HOOKS, _HOOKS_DIR
    target = tmp_path_factory.mktemp("safety-registration")
    projector = _load_projector(_SOURCE_ROOT)
    for harness in ("claude", "codex"):
        plan = projector.build_plan(harness)
        assert not plan.gaps, plan.gaps
        for relative, content in plan.writes.items():
            output = target / relative
            output.parent.mkdir(parents=True, exist_ok=True)
            output.write_text(content, encoding="utf-8")
    _ROOT = target
    _CLAUDE_SETTINGS = target / ".claude/settings.json"
    _CODEX_HOOKS = target / ".codex/hooks.json"
    _HOOKS_DIR = _SOURCE_ROOT / ".harness-baseline-configuration/hooks"
    yield
    _ROOT = _SOURCE_ROOT


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


# --- S292: dead mechanisms removed ---


def test_scheduler_py_absent():
    assert not (_HOOKS_DIR / "scheduler.py").exists(), "scheduler.py was retired (HYG-045) and must not exist"


def test_schedule_md_absent():
    assert not (_ROOT / ".claude" / "SCHEDULE.md").exists(), "SCHEDULE.md was retired (HYG-045) and must not exist"


def test_claude_md_no_session_scheduler_claim():
    claude_md = (_SOURCE_ROOT / "AGENTS.md").read_text(encoding="utf-8")
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


def test_retired_deliberation_archive_helper_is_absent():
    assert not (_HOOKS_DIR / "_delib_common.py").exists()
    assert not (_TEMPLATES_DIR / "_delib_common.py").exists()
    assert not (_SOURCE_ROOT / ".harness-baseline-configuration/hooks/_delib_common.py").exists()


# --- Structural: capture hooks import _delib_common ---


# --- Doctor checks: safety-gate registration + stub reporting (HYG-050/S294 deferred items) ---


def test_doctor_safety_gate_registration_pass():
    """_check_safety_gate_registration returns pass when both gates are registered."""
    from groundtruth_kb.project.doctor import _check_safety_gate_registration

    result = _check_safety_gate_registration(_ROOT)
    assert result.status == "pass", f"safety-gate-registration check should pass on live repo: {result.message}"


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


def test_authored_terminology_directs_canonical_cli_retrieval():
    """Terminology retrieval uses the current service, without a copied glossary."""
    ct = (_SOURCE_ROOT / ".harness-baseline-configuration" / "rules" / "canonical-terminology.md").read_text(
        encoding="utf-8"
    )
    assert "gt terms show <id>" in ct
    assert 'gt authority resolve "<term>" --scope <scope>' in ct
    assert "second glossary" in ct
