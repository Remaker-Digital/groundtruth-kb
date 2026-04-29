#!/usr/bin/env python3
# © 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""Minimized formal-artifact-approval-gate hook for the bridge-poller spike.

Minimized port of ``.claude/hooks/formal-artifact-approval-gate.py``. Same
trigger-condition shape (block writes to a protected-spec target) and same
deny semantics (exit non-zero with a JSON ``decision: "block"`` payload),
but no project-specific KB integration.

Writes a ``SENTINEL_GOV_HOOK_FIRED-<ts>`` marker into ``SPIKE_EVIDENCE_DIR``
when the hook fires. The spike runner's findings derivation uses both this
marker AND the post-attempt content of ``protected-spec.json`` to classify
whether the governance gate actually blocked the write.

Hook protocol (Claude Code):
- Stdin JSON: ``{"tool_name": ..., "tool_input": {...}, ...}``.
- Stdout JSON: ``{"decision": "block", "reason": "..."}`` or ``{}``.
- Exit: 0 always (per Claude Code hook protocol — hooks do not raise).
"""

from __future__ import annotations

import datetime as dt
import json
import os
import sys
from pathlib import Path
from typing import Any

PROTECTED_SPEC_FILENAME = "protected-spec.json"


def _write_marker() -> None:
    evidence_dir_str = os.environ.get("SPIKE_EVIDENCE_DIR")
    if not evidence_dir_str:
        return
    evidence_dir = Path(evidence_dir_str)
    evidence_dir.mkdir(parents=True, exist_ok=True)
    ts = dt.datetime.now(dt.UTC).strftime("%Y%m%dT%H%M%SZ")
    (evidence_dir / f"SENTINEL_GOV_HOOK_FIRED-{ts}").write_text("ok\n", encoding="utf-8")


def _is_protected_write(payload: dict[str, Any]) -> bool:
    tool_name = payload.get("tool_name", "")
    if tool_name not in {"Edit", "Write", "MultiEdit", "NotebookEdit"}:
        return False
    tool_input = payload.get("tool_input", {})
    file_path = str(tool_input.get("file_path", ""))
    return file_path.endswith(PROTECTED_SPEC_FILENAME)


def main() -> int:
    try:
        raw = sys.stdin.read()
        payload = json.loads(raw) if raw.strip() else {}
    except Exception:
        sys.stdout.write(json.dumps({}) + "\n")
        return 0

    if _is_protected_write(payload):
        _write_marker()
        sys.stdout.write(
            json.dumps(
                {
                    "decision": "block",
                    "reason": (
                        "BLOCKED (minimized formal-artifact-approval-gate fixture): "
                        f"writes to {PROTECTED_SPEC_FILENAME} require approval evidence. "
                        "This is a spike fixture; in production the real hook checks "
                        "GTKB_FORMAL_APPROVAL_PACKET."
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
