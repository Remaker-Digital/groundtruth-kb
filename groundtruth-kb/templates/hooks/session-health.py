#!/usr/bin/env python3
"""Session health hook — captures a health snapshot on session stop.

Install: copy to .claude/hooks/session-health.py
Event: Stop

This hook captures a session health snapshot when the AI session ends,
enabling trend tracking across sessions via `gt health trends`.

Copyright (c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
Licensed under AGPL-3.0-or-later.
"""

import json
import sys
from pathlib import Path


def main() -> None:
    hook_input = json.loads(sys.stdin.read())
    session_id = hook_input.get("session_id", "unknown")

    # Find groundtruth.toml to resolve DB path
    cwd = Path.cwd()
    toml_path = cwd / "groundtruth.toml"
    if not toml_path.exists():
        return  # Not a groundtruth project

    try:
        from groundtruth_kb.config import GTConfig
        from groundtruth_kb.db import KnowledgeDB

        config = GTConfig.from_toml(toml_path)
        db = KnowledgeDB(db_path=config.db_path)
        db.capture_session_snapshot(session_id)
    except Exception:
        pass  # Non-blocking — don't fail the session stop


if __name__ == "__main__":
    main()
