"""Tests for the _check_sot_read_discipline doctor check.

Authority: DCL-SOT-READ-HOOK-CONTRACT-001 v1.

Verifies the 4-layer assertion: canonical hook presence, Codex adapter presence,
Claude effective coverage (Read+Grep+Glob matcher), Codex effective coverage
(Bash matcher; anti-false-green check that rejects Read/Grep/Glob on Codex).
"""

from __future__ import annotations

import json
from pathlib import Path

from groundtruth_kb.project.doctor import _check_sot_read_discipline


def _make_project(
    tmp_path: Path,
    *,
    claude_settings: dict | None,
    codex_hooks: dict | None,
    canonical_hook: bool = True,
    codex_adapter: bool = True,
) -> Path:
    """Create a fixture project with the requested registration shapes."""
    (tmp_path / ".claude" / "hooks").mkdir(parents=True)
    (tmp_path / ".codex" / "gtkb-hooks").mkdir(parents=True)
    if canonical_hook:
        (tmp_path / ".claude" / "hooks" / "sot-read-discipline.py").write_text("# hook", encoding="utf-8")
    if codex_adapter:
        (tmp_path / ".codex" / "gtkb-hooks" / "sot-read-discipline-bash-adapter.py").write_text(
            "# adapter", encoding="utf-8"
        )
    if claude_settings is not None:
        (tmp_path / ".claude" / "settings.json").write_text(json.dumps(claude_settings), encoding="utf-8")
    if codex_hooks is not None:
        (tmp_path / ".codex" / "hooks.json").write_text(json.dumps(codex_hooks), encoding="utf-8")
    return tmp_path


def _claude_correct() -> dict:
    return {
        "hooks": {
            "PreToolUse": [
                {
                    "matcher": "Read|Grep|Glob",
                    "hooks": [{"command": "python .claude/hooks/sot-read-discipline.py"}],
                }
            ]
        }
    }


def _codex_correct() -> dict:
    return {
        "hooks": {
            "PreToolUse": [
                {
                    "matcher": "Bash",
                    "hooks": [{"command": "python .codex/gtkb-hooks/sot-read-discipline-bash-adapter.py"}],
                }
            ]
        }
    }


def test_clean_passes(tmp_path: Path) -> None:
    target = _make_project(tmp_path, claude_settings=_claude_correct(), codex_hooks=_codex_correct())
    result = _check_sot_read_discipline(target)
    assert result.status == "pass", f"expected pass, got {result.status}: {result.message}"


def test_missing_canonical_hook_warns(tmp_path: Path) -> None:
    target = _make_project(
        tmp_path, claude_settings=_claude_correct(), codex_hooks=_codex_correct(), canonical_hook=False
    )
    result = _check_sot_read_discipline(target)
    assert result.status == "warning"
    assert "canonical hook missing" in result.message


def test_missing_codex_adapter_warns(tmp_path: Path) -> None:
    target = _make_project(
        tmp_path, claude_settings=_claude_correct(), codex_hooks=_codex_correct(), codex_adapter=False
    )
    result = _check_sot_read_discipline(target)
    assert result.status == "warning"
    assert "Codex adapter missing" in result.message


def test_claude_matcher_missing_glob_warns(tmp_path: Path) -> None:
    bad_claude = {
        "hooks": {
            "PreToolUse": [
                {
                    "matcher": "Read|Grep",  # missing Glob
                    "hooks": [{"command": "python .claude/hooks/sot-read-discipline.py"}],
                }
            ]
        }
    }
    target = _make_project(tmp_path, claude_settings=bad_claude, codex_hooks=_codex_correct())
    result = _check_sot_read_discipline(target)
    assert result.status == "warning"
    assert "Claude registration" in result.message


def test_codex_false_green_read_matcher_fails(tmp_path: Path) -> None:
    """Anti-false-green: Codex registering Read/Grep/Glob (unsupported tool-events) is flagged."""
    false_green = {
        "hooks": {
            "PreToolUse": [
                {
                    "matcher": "Read|Grep|Glob",  # Wrong! Codex doesn't have these.
                    "hooks": [{"command": "python .codex/gtkb-hooks/sot-read-discipline-bash-adapter.py"}],
                }
            ]
        }
    }
    target = _make_project(tmp_path, claude_settings=_claude_correct(), codex_hooks=false_green)
    result = _check_sot_read_discipline(target)
    assert result.status == "warning"
    assert "Read/Grep/Glob matcher" in result.message
    assert "ADR-CODEX-HOOK-PARITY-FALLBACK-001" in result.message


def test_codex_missing_bash_warns(tmp_path: Path) -> None:
    no_bash = {"hooks": {"PreToolUse": []}}
    target = _make_project(tmp_path, claude_settings=_claude_correct(), codex_hooks=no_bash)
    result = _check_sot_read_discipline(target)
    assert result.status == "warning"
    assert "Codex registration" in result.message


def test_missing_settings_files_warns(tmp_path: Path) -> None:
    target = _make_project(tmp_path, claude_settings=None, codex_hooks=None)
    result = _check_sot_read_discipline(target)
    assert result.status == "warning"
    assert ".claude/settings.json absent" in result.message
