#!/usr/bin/env python3
"""Hook adapter for GT-KB workstream focus state and guards."""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path


def _load_shared_module():
    project_root = Path(__file__).resolve().parents[2]
    scripts_dir = project_root / "scripts"
    if str(scripts_dir) not in sys.path:
        sys.path.insert(0, str(scripts_dir))
    import workstream_focus  # noqa: PLC0415

    return workstream_focus, project_root


def main() -> None:
    try:
        os.environ.setdefault("GTKB_HARNESS_NAME", "claude")
        raw_stdin = sys.stdin.buffer.read()
        payload = json.loads(raw_stdin.decode("utf-8-sig") if raw_stdin else "{}")
        workstream_focus, project_root = _load_shared_module()
        json.dump(workstream_focus.handle_hook_payload(payload, project_root), sys.stdout)
    except Exception as exc:  # noqa: BLE001 - hook failures must fail soft
        json.dump(
            {
                "systemMessage": (
                    "GT-KB workstream focus hook error; default to GT-KB work "
                    f"until the hook is repaired. Error: {exc}"
                )
            },
            sys.stdout,
        )


if __name__ == "__main__":
    main()
