#!/usr/bin/env python3
"""Codex adapter for the SoT Read-Discipline canonical hook.

Authority: DCL-SOT-READ-HOOK-CONTRACT-001 v1.

Codex CLI's PreToolUse fires on tool_name in {Bash, apply_patch} (per
ADR-CODEX-HOOK-PARITY-FALLBACK-001 v2). This adapter is registered with
matcher "Bash" in .codex/hooks.json and pipes the PreToolUse payload into
the canonical hook at .claude/hooks/sot-read-discipline.py with
GTKB_HARNESS_NAME=codex env override.

Pattern: see .codex/gtkb-hooks/lo-file-safety-gate-bash-adapter.py.
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
CANONICAL_HOOK = PROJECT_ROOT / ".claude" / "hooks" / "sot-read-discipline.py"


def _no_window_subprocess_kwargs() -> dict[str, object]:
    kwargs: dict[str, object] = {}
    if os.name == "nt":
        kwargs["creationflags"] = getattr(subprocess, "CREATE_NO_WINDOW", 0)
    return kwargs


def main() -> int:
    try:
        payload = json.loads(sys.stdin.read() or "{}")
    except json.JSONDecodeError:
        payload = {}
    env = os.environ.copy()
    env.setdefault("GTKB_HARNESS_NAME", "codex")
    env.setdefault("GTKB_HARNESS_ID", "A")
    result = subprocess.run(
        [sys.executable, str(CANONICAL_HOOK)],
        input=json.dumps(payload),
        capture_output=True,
        text=True,
        cwd=str(PROJECT_ROOT),
        env=env,
        check=False,
        **_no_window_subprocess_kwargs(),
    )
    if result.stdout:
        print(result.stdout, end="")
    if result.stderr:
        print(result.stderr, file=sys.stderr, end="")
    return result.returncode


if __name__ == "__main__":
    raise SystemExit(main())
