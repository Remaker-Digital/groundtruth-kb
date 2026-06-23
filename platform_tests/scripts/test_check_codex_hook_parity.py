from __future__ import annotations

import json
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
CODEX_HOOKS = REPO_ROOT / ".codex" / "hooks.json"
CODEX_MCP_WORKER_GUARD_WRAPPER = REPO_ROOT / ".codex" / "gtkb-hooks" / "codex-mcp-worker-guard.cmd"


def test_codex_sessionstart_registers_report_only_mcp_worker_guard() -> None:
    hooks = json.loads(CODEX_HOOKS.read_text(encoding="utf-8"))
    session_start_commands = [
        hook["command"]
        for group in hooks["hooks"]["SessionStart"]
        for hook in group["hooks"]
        if isinstance(hook.get("command"), str)
    ]

    matches = [command for command in session_start_commands if "codex-mcp-worker-guard.cmd" in command]

    assert len(matches) == 1
    assert matches[0].startswith("cmd /d /s /c ")
    assert "--cleanup" not in matches[0]
    assert "--yes" not in matches[0]


def test_codex_mcp_worker_guard_wrapper_is_report_only() -> None:
    text = CODEX_MCP_WORKER_GUARD_WRAPPER.read_text(encoding="utf-8")

    assert "scripts\\codex_mcp_worker_guard.py" in text
    assert "--report" in text
    assert "--quiet-when-clean" in text
    assert "--cleanup" not in text
    assert "--yes" not in text
