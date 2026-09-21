"""FAB-14 HYG-040: blocking gates append central denial telemetry."""

from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[2]


def _run(path: Path, payload: dict, telemetry: Path) -> dict:
    env = os.environ.copy()
    env["GTKB_GATE_DENIALS_PATH"] = str(telemetry)
    env["GTKB_PROJECT_ROOT"] = str(_ROOT)
    proc = subprocess.run(
        [sys.executable, "-B", str(path)],
        input=json.dumps(payload),
        text=True,
        capture_output=True,
        env=env,
        cwd=str(_ROOT),
        check=True,
    )
    return json.loads(proc.stdout)


def _first_record(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8").splitlines()[0])


def test_scanner_safe_writer_block_logs_denial(tmp_path: Path) -> None:
    telemetry = tmp_path / "scanner.jsonl"
    result = _run(
        _ROOT / ".harness-baseline-configuration" / "hooks" / "scanner-safe-writer.py",
        {
            "tool_name": "Write",
            "tool_input": {
                "file_path": "bridge/test-001.md",
                "content": "token = 'abcdefghijklmnopqrstuvwxyz1234567890'",
            },
            "session_id": "test",
        },
        telemetry,
    )

    assert result["hookSpecificOutput"]["permissionDecision"] == "deny"
    assert _first_record(telemetry)["gate"] == "scanner-safe-writer"
