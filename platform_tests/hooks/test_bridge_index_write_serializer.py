# (c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""Tests for the bridge INDEX atomic-write guard hook (WI-4481).

Verifies the PreToolUse guard blocks raw agent Write/Edit/MultiEdit/Bash/
apply_patch mutations of ``bridge/INDEX.md`` (directing to the serialized
``gt bridge index`` CLI), while letting the serialized CLI, reads, and
non-INDEX writes pass. Covers the GO'd verification plan plus multi-surface
parity and a redirect false-positive guard.

Bridge: bridge/gtkb-bridge-index-atomic-write-guard-002.md (GO)
Specs:
  - GOV-FILE-BRIDGE-AUTHORITY-001 (CLAUSE-INDEX-IS-CANONICAL)
  - ADR-CODEX-HOOK-PARITY-FALLBACK-001 (.claude + .codex parity)
Work Item: WI-4481
"""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]


def _import_hook():
    hook_path = REPO_ROOT / ".claude" / "hooks" / "bridge-index-write-serializer.py"
    assert hook_path.is_file(), f"Hook not found at {hook_path}"
    spec = importlib.util.spec_from_file_location("bridge_index_write_serializer", str(hook_path))
    mod = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = mod
    try:
        spec.loader.exec_module(mod)
    except Exception:
        sys.modules.pop(spec.name, None)
        raise
    return mod


HOOK = _import_hook()


@pytest.fixture()
def root(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    # Force _project_root to resolve from payload cwd, not the real CLAUDE_PROJECT_DIR.
    monkeypatch.delenv("CLAUDE_PROJECT_DIR", raising=False)
    (tmp_path / "bridge").mkdir(parents=True)
    return tmp_path


def _is_block(decision: dict) -> bool:
    return (
        decision.get("decision") == "block"
        and decision.get("hookSpecificOutput", {}).get("permissionDecision") == "deny"
    )


def _payload(root: Path, tool: str, tool_input: dict) -> dict:
    return {"tool_name": tool, "tool_input": tool_input, "cwd": str(root)}


# --- Write/Edit/MultiEdit tool surface (primary clobber path, WI-4481) ---


def test_write_to_index_is_blocked(root: Path) -> None:
    decision = HOOK.gate_decision(_payload(root, "Write", {"file_path": "bridge/INDEX.md", "content": "x"}))
    assert _is_block(decision)
    assert "bridge index" in decision["reason"]


def test_edit_to_index_is_blocked(root: Path) -> None:
    decision = HOOK.gate_decision(
        _payload(root, "Edit", {"file_path": "bridge/INDEX.md", "old_string": "a", "new_string": "b"})
    )
    assert _is_block(decision)


def test_multiedit_to_index_is_blocked(root: Path) -> None:
    decision = HOOK.gate_decision(_payload(root, "MultiEdit", {"file_path": "bridge/INDEX.md", "edits": []}))
    assert _is_block(decision)


def test_absolute_index_path_is_blocked(root: Path) -> None:
    abs_index = str(root / "bridge" / "INDEX.md")
    decision = HOOK.gate_decision(_payload(root, "Write", {"file_path": abs_index, "content": "x"}))
    assert _is_block(decision)


def test_write_to_non_index_bridge_file_passes(root: Path) -> None:
    decision = HOOK.gate_decision(_payload(root, "Write", {"file_path": "bridge/some-thread-001.md", "content": "NEW"}))
    assert decision == {}


def test_write_to_non_bridge_file_passes(root: Path) -> None:
    decision = HOOK.gate_decision(_payload(root, "Write", {"file_path": "scripts/foo.py", "content": "x"}))
    assert decision == {}


# --- Bash surface (Codex primary surface; Claude residual) ---


def test_bash_redirect_to_index_is_blocked(root: Path) -> None:
    decision = HOOK.gate_decision(_payload(root, "Bash", {"command": 'echo "x" > bridge/INDEX.md'}))
    assert _is_block(decision)


def test_bash_append_to_index_is_blocked(root: Path) -> None:
    decision = HOOK.gate_decision(_payload(root, "Bash", {"command": "printf 'x' >> bridge/INDEX.md"}))
    assert _is_block(decision)


def test_powershell_set_content_index_is_blocked(root: Path) -> None:
    decision = HOOK.gate_decision(_payload(root, "Bash", {"command": "Set-Content -Path bridge/INDEX.md -Value 'x'"}))
    assert _is_block(decision)


def test_serialized_cli_add_document_passes(root: Path) -> None:
    # The sanctioned route writes INDEX inside Python under the lock; its command
    # line names a versioned path (not INDEX.md) and carries no redirect.
    cmd = "python -m groundtruth_kb bridge index add-document myslug --status NEW --path bridge/myslug-001.md"
    decision = HOOK.gate_decision(_payload(root, "Bash", {"command": cmd}))
    assert decision == {}


def test_serialized_cli_set_status_passes(root: Path) -> None:
    cmd = "python -m groundtruth_kb bridge index set-status myslug --status GO --path bridge/myslug-002.md"
    decision = HOOK.gate_decision(_payload(root, "Bash", {"command": cmd}))
    assert decision == {}


def test_reading_index_passes(root: Path) -> None:
    decision = HOOK.gate_decision(_payload(root, "Bash", {"command": "cat bridge/INDEX.md"}))
    assert decision == {}


def test_grep_literal_redirect_char_does_not_false_positive(root: Path) -> None:
    # Grepping for a literal '>' inside INDEX is a read, not a redirect-write.
    decision = HOOK.gate_decision(_payload(root, "Bash", {"command": 'grep ">" bridge/INDEX.md'}))
    assert decision == {}


# --- apply_patch surface (Codex) ---


def test_apply_patch_targeting_index_is_blocked(root: Path) -> None:
    patch = "*** Begin Patch\n*** Update File: bridge/INDEX.md\n@@\n+NEW: bridge/x-001.md\n*** End Patch\n"
    decision = HOOK.gate_decision(_payload(root, "apply_patch", {"patch": patch}))
    assert _is_block(decision)


def test_apply_patch_non_index_passes(root: Path) -> None:
    patch = "*** Begin Patch\n*** Update File: bridge/other-001.md\n@@\n+x\n*** End Patch\n"
    decision = HOOK.gate_decision(_payload(root, "apply_patch", {"patch": patch}))
    assert decision == {}


# --- Unrelated tools pass ---


def test_read_tool_passes(root: Path) -> None:
    decision = HOOK.gate_decision(_payload(root, "Read", {"file_path": "bridge/INDEX.md"}))
    assert decision == {}
