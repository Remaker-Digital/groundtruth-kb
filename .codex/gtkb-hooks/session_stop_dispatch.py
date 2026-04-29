from __future__ import annotations

import subprocess
from pathlib import Path

PROJECT_ROOT = Path(r"E:\GT-KB")
OUT_DIR = PROJECT_ROOT / ".codex" / "gtkb-hooks"

stdout = (OUT_DIR / "last-session-stop.json").open("w", encoding="utf-8")
stderr = (OUT_DIR / "last-session-stop.err").open("w", encoding="utf-8")

subprocess.Popen(
    [
        "python",
        str(PROJECT_ROOT / "scripts" / "session_self_initialization.py"),
        "--project-root",
        str(PROJECT_ROOT),
        "--emit-wrapup",
        "--fast-hook",
        "--role-profile",
        "prime-builder",
    ],
    stdout=stdout,
    stderr=stderr,
    cwd=str(PROJECT_ROOT),
    close_fds=True,
)

print("{}")
