"""Tests for the Claude directive adapter hook."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path
import pytest

REPO_ROOT = Path(__file__).resolve().parents[3]
HOOK_PATH = REPO_ROOT / ".claude" / "hooks" / "directive-enforcement-claude-adapter.py"


def test_pre_tool_use_allow() -> None:
    # Build payload for allowed operation
    payload = {
        "tool_name": "Write",
        "tool_input": {"file_path": "bridge/INDEX.md", "content": "some content"},
        "cwd": str(REPO_ROOT),
    }

    proc = subprocess.run(
        [sys.executable, str(HOOK_PATH)], input=json.dumps(payload), text=True, capture_output=True, check=True
    )
    assert proc.returncode == 0
    res = json.loads(proc.stdout)
    assert res == {}  # Empty dict indicates pass


def test_pre_tool_use_block_violation() -> None:
    # Build payload for blocked operation (outside allowed_root)
    payload = {
        "tool_name": "Write",
        "tool_input": {"file_path": "C:\\Windows\\system32.dll", "content": "malicious content"},
        "cwd": str(REPO_ROOT),
    }

    proc = subprocess.run([sys.executable, str(HOOK_PATH)], input=json.dumps(payload), text=True, capture_output=True)
    # The hook script exits with 0 but outputs a JSON structure containing 'permissionDecision': 'deny'
    assert proc.returncode == 0
    res = json.loads(proc.stdout)
    decision = res.get("hookSpecificOutput", {}).get("permissionDecision")
    assert decision == "deny"
    assert "resolves outside allowed root" in res["hookSpecificOutput"]["permissionDecisionReason"]
