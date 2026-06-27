from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

PROJECT_ROOT = Path(r"E:\GT-KB")
OUT_DIR = PROJECT_ROOT / ".codex" / "gtkb-hooks"
HARNESS_NAME = "codex"

sys.path.insert(0, str(PROJECT_ROOT))
from scripts.harness_identity import resolved_harness_id  # noqa: E402


def _persistent_harness_id() -> str:
    harness_id = resolved_harness_id(PROJECT_ROOT, harness_name=HARNESS_NAME)
    if not harness_id:
        raise RuntimeError(f"Could not resolve persistent harness identity for {HARNESS_NAME}")
    return harness_id


stdout = (OUT_DIR / "last-session-stop.json").open("w", encoding="utf-8")
stderr = (OUT_DIR / "last-session-stop.err").open("w", encoding="utf-8")

popen_kwargs: dict[str, object] = {
    "stdin": subprocess.DEVNULL,
    "stdout": stdout,
    "stderr": stderr,
    "cwd": str(PROJECT_ROOT),
    "close_fds": True,
}
if os.name == "nt":
    popen_kwargs["creationflags"] = getattr(subprocess, "CREATE_NO_WINDOW", 0) | getattr(
        subprocess, "CREATE_NEW_PROCESS_GROUP", 0
    )

subprocess.Popen(
    [
        "python",
        str(PROJECT_ROOT / "scripts" / "session_self_initialization.py"),
        "--project-root",
        str(PROJECT_ROOT),
        "--emit-wrapup",
        "--fast-hook",
        "--harness-name",
        HARNESS_NAME,
        "--harness-id",
        _persistent_harness_id(),
    ],
    **popen_kwargs,
)

print("{}")
