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
    env["CLAUDE_PROJECT_DIR"] = str(_ROOT)
    proc = subprocess.run(
        [sys.executable, str(path)],
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


def test_formal_gate_block_logs_denial(tmp_path: Path) -> None:
    telemetry = tmp_path / "formal.jsonl"
    result = _run(
        _ROOT / ".claude" / "hooks" / "formal-artifact-approval-gate.py",
        {"tool_name": "Bash", "tool_input": {"command": "gt spec update --id DCL-X --content-file missing.md"}},
        telemetry,
    )

    assert result["decision"] == "block"
    record = _first_record(telemetry)
    assert record["gate"] == "formal-artifact-approval-gate"
    assert record["pattern_id"] == "missing-formal-approval-packet"


def test_narrative_gate_block_logs_denial(tmp_path: Path) -> None:
    root = tmp_path / "repo"
    protected = root / "config" / "governance"
    protected.mkdir(parents=True)
    protected.joinpath("narrative-artifact-approval.toml").write_text(
        """
[[protected_artifacts]]
patterns = [".claude/rules/*.md"]
""".strip()
        + "\n",
        encoding="utf-8",
    )
    target = root / ".claude" / "rules" / "foo.md"
    target.parent.mkdir(parents=True)
    telemetry = tmp_path / "narrative.jsonl"
    env = os.environ.copy()
    env["CLAUDE_PROJECT_DIR"] = str(root)
    env["GTKB_GATE_DENIALS_PATH"] = str(telemetry)
    proc = subprocess.run(
        [sys.executable, str(_ROOT / ".claude" / "hooks" / "narrative-artifact-approval-gate.py")],
        input=json.dumps({"tool_name": "Write", "tool_input": {"file_path": str(target), "content": "body\n"}}),
        text=True,
        capture_output=True,
        env=env,
        cwd=str(_ROOT),
        check=True,
    )

    assert json.loads(proc.stdout)["decision"] == "block"
    assert _first_record(telemetry)["gate"] == "narrative-artifact-approval-gate"


def test_scanner_safe_writer_block_logs_denial(tmp_path: Path) -> None:
    telemetry = tmp_path / "scanner.jsonl"
    result = _run(
        _ROOT / ".claude" / "hooks" / "scanner-safe-writer.py",
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


def test_bridge_compliance_gate_block_logs_denial(tmp_path: Path) -> None:
    telemetry = tmp_path / "bridge.jsonl"
    result = _run(
        _ROOT / ".claude" / "hooks" / "bridge-compliance-gate.py",
        {
            "tool_name": "Write",
            "tool_input": {
                "file_path": str(_ROOT / "bridge" / "gtkb-fab14-telemetry-001.md"),
                "content": "NEW\n\nbridge_kind: prime_proposal\nDocument: gtkb-fab14-telemetry\nVersion: 001\n",
            },
            "cwd": str(_ROOT),
        },
        telemetry,
    )

    assert result["hookSpecificOutput"]["permissionDecision"] == "deny"
    assert _first_record(telemetry)["gate"] == "bridge-compliance-gate"


def test_implementation_start_gate_block_logs_denial(tmp_path: Path) -> None:
    telemetry = tmp_path / "impl.jsonl"
    result = _run(
        _ROOT / "scripts" / "implementation_start_gate.py",
        {"tool_name": "Write", "tool_input": {"file_path": str(_ROOT / "pyproject.toml")}},
        telemetry,
    )

    assert result["hookSpecificOutput"]["permissionDecision"] == "deny"
    assert _first_record(telemetry)["gate"] == "implementation-start-gate"
