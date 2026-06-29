# (c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""Run a Codex .cmd hook without creating a visible Windows console."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

CREATE_NO_WINDOW = 0x08000000


def main(argv: list[str]) -> int:
    if not argv:
        print("usage: run_cmd_no_window.py <hook.cmd> [args...]", file=sys.stderr)
        return 2
    script = Path(argv[0])
    if script.suffix.lower() != ".cmd":
        print(f"refusing non-.cmd hook target: {script}", file=sys.stderr)
        return 2
    completed = subprocess.run(
        [str(script), *argv[1:]],
        check=False,
        creationflags=CREATE_NO_WINDOW if sys.platform == "win32" else 0,
    )
    return int(completed.returncode)


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
