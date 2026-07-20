#!/usr/bin/env python3
"""One-shot capture of WI-5144 verification command stdout/stderr."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PY = ROOT / "groundtruth-kb" / ".venv" / "Scripts" / "python.exe"
OUT = ROOT / "bridge" / "_capture_wi5144_evidence.txt"

COMMANDS: list[tuple[str, list[str]]] = [
    (
        "1. bridge_applicability_preflight.py",
        [
            str(PY),
            str(ROOT / "scripts" / "bridge_applicability_preflight.py"),
            "--bridge-id",
            "gtkb-wi5144-hp08-semantic-adapter-drift",
        ],
    ),
    (
        "2. adr_dcl_clause_preflight.py",
        [
            str(PY),
            str(ROOT / "scripts" / "adr_dcl_clause_preflight.py"),
            "--bridge-id",
            "gtkb-wi5144-hp08-semantic-adapter-drift",
        ],
    ),
    (
        "3. git rev-parse HEAD",
        ["git", "-C", str(ROOT), "rev-parse", "HEAD"],
    ),
    (
        "4. git status --short",
        [
            "git",
            "-C",
            str(ROOT),
            "status",
            "--short",
            "--",
            ".claude/skills/verify/helpers/write_verdict.py",
            "scripts/bridge_review_independence.py",
            "scripts/check_harness_parity.py",
            "platform_tests/scripts/test_check_harness_parity.py",
        ],
    ),
    (
        "5. git diff --quiet HEAD",
        [
            "git",
            "-C",
            str(ROOT),
            "diff",
            "--quiet",
            "HEAD",
            "--",
            ".claude/skills/verify/helpers/write_verdict.py",
            "scripts/bridge_review_independence.py",
            "scripts/check_harness_parity.py",
            "platform_tests/scripts/test_check_harness_parity.py",
        ],
    ),
    (
        "6. pytest test_check_harness_parity.py",
        [
            str(PY),
            "-m",
            "pytest",
            str(ROOT / "platform_tests" / "scripts" / "test_check_harness_parity.py"),
            "-q",
            "--tb=short",
        ],
    ),
    (
        "7. ruff check",
        [
            str(PY),
            "-m",
            "ruff",
            "check",
            str(ROOT / "scripts" / "check_harness_parity.py"),
            str(ROOT / "platform_tests" / "scripts" / "test_check_harness_parity.py"),
        ],
    ),
    (
        "8. ruff format --check",
        [
            str(PY),
            "-m",
            "ruff",
            "format",
            "--check",
            str(ROOT / "scripts" / "check_harness_parity.py"),
            str(ROOT / "platform_tests" / "scripts" / "test_check_harness_parity.py"),
        ],
    ),
    (
        "9. git rev-parse HEAD:scripts/check_harness_parity.py",
        ["git", "-C", str(ROOT), "rev-parse", "HEAD:scripts/check_harness_parity.py"],
    ),
    (
        "10. git rev-parse HEAD:platform_tests/scripts/test_check_harness_parity.py",
        [
            "git",
            "-C",
            str(ROOT),
            "rev-parse",
            "HEAD:platform_tests/scripts/test_check_harness_parity.py",
        ],
    ),
]


def main() -> int:
    chunks: list[str] = []
    for label, cmd in COMMANDS:
        chunks.append(f"=== {label} ===")
        chunks.append(f"command: {' '.join(cmd)}")
        proc = subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True)
        chunks.append(f"exit_code: {proc.returncode}")
        chunks.append("--- stdout ---")
        chunks.append(proc.stdout if proc.stdout else "")
        chunks.append("--- stderr ---")
        chunks.append(proc.stderr if proc.stderr else "")
        if label.startswith("5."):
            chunks.append(f"echo exit:{proc.returncode}")
        chunks.append("")
    text = "\n".join(chunks)
    OUT.write_text(text, encoding="utf-8", newline="\n")
    sys.stdout.write(text)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
