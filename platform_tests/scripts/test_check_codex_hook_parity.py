from __future__ import annotations

from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
CODEX_HOOKS = REPO_ROOT / ".codex" / "hooks.json"
CODEX_MCP_WORKER_GUARD_WRAPPER = REPO_ROOT / ".codex" / "gtkb-hooks" / "codex-mcp-worker-guard.cmd"


def test_codex_mcp_worker_guard_wrapper_is_report_only() -> None:
    text = CODEX_MCP_WORKER_GUARD_WRAPPER.read_text(encoding="utf-8")

    assert "scripts\\codex_mcp_worker_guard.py" in text
    assert "--report" in text
    assert "--quiet-when-clean" in text
    assert "--cleanup" not in text
    assert "--yes" not in text
