#!/usr/bin/env python3
"""Codex adapter for the canonical Loyal Opposition file-safety gate.

Normalizes Codex Bash and apply-patch payload shapes to the shared
lo_file_safety_payloads schema before forwarding to the canonical hook.
Preserves the canonical gate's decision and exit-code contract.

Specifications: ADR-CODEX-HOOK-PARITY-FALLBACK-001, ADR-CROSS-HARNESS-PARITY-001.
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
CANONICAL_HOOK = PROJECT_ROOT / ".claude" / "hooks" / "lo-file-safety-gate.py"

_SCRIPTS = PROJECT_ROOT / "scripts"
if str(_SCRIPTS) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS))

try:
    from lo_file_safety_payloads import normalize_codex
except ImportError:
    normalize_codex = None  # type: ignore[assignment]


def _no_window_subprocess_kwargs() -> dict[str, object]:
    kwargs: dict[str, object] = {}
    if os.name == "nt":
        kwargs["creationflags"] = getattr(subprocess, "CREATE_NO_WINDOW", 0)
    return kwargs


def _to_claude_payload(payload: dict) -> dict:
    """Convert Codex payload to Claude-style using the shared normalizer."""
    if normalize_codex is not None:
        normalized = normalize_codex(payload)
        if normalized.tool_name == "Bash":
            return {"tool_name": "Bash", "tool_input": {"command": normalized.command}}
    return payload


def main() -> int:
    try:
        payload = json.loads(sys.stdin.read() or "{}")
    except json.JSONDecodeError:
        payload = {}
    adapted = _to_claude_payload(payload)
    env = os.environ.copy()
    env.setdefault("GTKB_HARNESS_NAME", "codex")
    env.setdefault("GTKB_HARNESS_ID", "A")
    result = subprocess.run(
        [sys.executable, str(CANONICAL_HOOK)],
        input=json.dumps(adapted),
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
