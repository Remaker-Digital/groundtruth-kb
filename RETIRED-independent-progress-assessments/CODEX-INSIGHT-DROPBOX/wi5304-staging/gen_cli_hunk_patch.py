# (c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""WI-5304 verify staging: emit a cli.py hunk patch that EXCLUDES the foreign
assert_cmd (`aggregate_result`) hunk, keeping only the four WI-5304 hunks.

Read-only against the repo except for writing the patch file into this LO
staging dropbox. Fails closed unless exactly four hunks survive and exactly one
(the foreign hunk) is dropped.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]
CLI = "groundtruth-kb/src/groundtruth_kb/cli.py"
OUT = REPO / "independent-progress-assessments/CODEX-INSIGHT-DROPBOX/wi5304-staging/cli_wi5304_hunks.patch"
FOREIGN_SIGNATURE = "aggregate_result"

proc = subprocess.run(
    ["git", "diff", "--no-color", "--", CLI],
    cwd=REPO,
    text=True,
    capture_output=True,
    encoding="utf-8",
    check=True,
)
lines = proc.stdout.splitlines(keepends=True)

header: list[str] = []
hunks: list[list[str]] = []
current: list[str] | None = None
for line in lines:
    if line.startswith("@@ "):
        if current is not None:
            hunks.append(current)
        current = [line]
    elif current is None:
        header.append(line)
    else:
        current.append(line)
if current is not None:
    hunks.append(current)

kept = [h for h in hunks if FOREIGN_SIGNATURE not in "".join(h)]
dropped = [h for h in hunks if FOREIGN_SIGNATURE in "".join(h)]

if len(hunks) != 5 or len(kept) != 4 or len(dropped) != 1:
    sys.stderr.write(
        f"FAIL: expected 5 hunks -> keep 4 drop 1; got total={len(hunks)} "
        f"kept={len(kept)} dropped={len(dropped)}\n"
    )
    raise SystemExit(2)

patch_text = "".join(header) + "".join("".join(h) for h in kept)
OUT.write_bytes(patch_text.encode("utf-8"))

sys.stderr.write(f"OK wrote {OUT} ({len(patch_text)} bytes)\n")
sys.stderr.write("kept hunk headers:\n")
for h in kept:
    sys.stderr.write("  " + h[0])
sys.stderr.write("dropped hunk header:\n")
for h in dropped:
    sys.stderr.write("  " + h[0])
