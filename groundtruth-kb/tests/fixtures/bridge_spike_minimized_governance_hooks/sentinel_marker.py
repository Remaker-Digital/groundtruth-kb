#!/usr/bin/env python3
# © 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""Generic SessionStart sentinel hook for the bridge-poller verification spike.

Writes a ``SENTINEL_HOOK_FIRED-<ts>`` file at the path passed via the
``SPIKE_EVIDENCE_DIR`` env var (set by the spike runner). The file's
existence proves the harness's SessionStart hook fired in the tested mode.

Hook protocol (Claude Code):
- Reads JSON from stdin describing the hook event.
- Writes JSON decision to stdout (or empty object for no-op).
- Exits 0.
"""

from __future__ import annotations

import contextlib
import datetime as dt
import json
import os
import sys
from pathlib import Path


def main() -> int:
    # Drain stdin per the Claude Code hook protocol; we don't need the content.
    with contextlib.suppress(Exception):
        sys.stdin.read()

    evidence_dir_str = os.environ.get("SPIKE_EVIDENCE_DIR")
    if evidence_dir_str:
        evidence_dir = Path(evidence_dir_str)
        evidence_dir.mkdir(parents=True, exist_ok=True)
        ts = dt.datetime.now(dt.UTC).strftime("%Y%m%dT%H%M%SZ")
        marker = evidence_dir / f"SENTINEL_HOOK_FIRED-{ts}"
        marker.write_text("ok\n", encoding="utf-8")

    sys.stdout.write(json.dumps({}) + "\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
