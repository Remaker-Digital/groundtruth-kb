#!/usr/bin/env python3
# © 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""Minimized credential-scan hook for the bridge-poller spike.

Minimized port of ``.claude/hooks/credential-scan.py``. Same trigger shape
(block writes whose content matches the AR-XXXXXXXX credential pattern)
and same deny semantics, without the full credential pattern set or
quarantine logic.

Writes a ``SENTINEL_CRED_HOOK_FIRED-<ts>`` marker into ``SPIKE_EVIDENCE_DIR``
when the hook fires.
"""

from __future__ import annotations

import datetime as dt
import json
import os
import re
import sys
from pathlib import Path
from typing import Any

# Single-pattern minimized credential check. The real hook supports many.
_AR_CREDENTIAL_RE = re.compile(r"\bAR-[A-Z0-9]{8}\b")


def _write_marker() -> None:
    evidence_dir_str = os.environ.get("SPIKE_EVIDENCE_DIR")
    if not evidence_dir_str:
        return
    evidence_dir = Path(evidence_dir_str)
    evidence_dir.mkdir(parents=True, exist_ok=True)
    ts = dt.datetime.now(dt.UTC).strftime("%Y%m%dT%H%M%SZ")
    (evidence_dir / f"SENTINEL_CRED_HOOK_FIRED-{ts}").write_text("ok\n", encoding="utf-8")


def _payload_content(payload: dict[str, Any]) -> str:
    """Best-effort extraction of write content from common Claude Code tool inputs."""
    tool_input = payload.get("tool_input", {})
    parts: list[str] = []
    for key in ("content", "new_string", "old_string", "command"):
        value = tool_input.get(key)
        if isinstance(value, str):
            parts.append(value)
    return "\n".join(parts)


def main() -> int:
    try:
        raw = sys.stdin.read()
        payload = json.loads(raw) if raw.strip() else {}
    except Exception:
        sys.stdout.write(json.dumps({}) + "\n")
        return 0

    content = _payload_content(payload)
    if content and _AR_CREDENTIAL_RE.search(content):
        _write_marker()
        sys.stdout.write(
            json.dumps(
                {
                    "decision": "block",
                    "reason": (
                        "BLOCKED (minimized credential-scan fixture): tool_input "
                        "content matches AR-[A-Z0-9]{8} credential pattern. "
                        "This is a spike fixture; in production the real hook "
                        "scans the full credential pattern set."
                    ),
                }
            )
            + "\n"
        )
        return 0

    sys.stdout.write(json.dumps({}) + "\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
