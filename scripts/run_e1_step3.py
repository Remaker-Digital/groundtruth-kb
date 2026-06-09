"""GTKB-ISOLATION-018 sub-slice 18.E.1 Step 3 forward executor.

Reads `.tmp/e1-drift/write-set.json` and performs the authorized atomic
moves under `applications/Agent_Red/`:

- 4 recursive cluster directory moves (src, admin, widget, branding)
- 1 cluster file move (config/stripe_product_ids.json)
- 638 paired per-file test moves (selective from tests/, per E.3 disposition)

Invariants:

- Destination parent directories are created (mkdir -p) before each `git mv`.
- Pairing order between `*_sources_*` and `*_destinations_*` lists in the
  write-set is preserved.
- Any non-zero `git mv` exit aborts the loop and prints rollback guidance.
- This script does NOT auto-rollback. The caller invokes
  `python scripts/rollback_e1_write_set.py` on failure.

Authorized by `bridge/gtkb-isolation-018-slice-e1-atomic-code-move-016.md` GO.
Mirror of the rollback script's safety semantics; symmetric for audit clarity.

Copyright 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


WRITE_SET = Path(".tmp/e1-drift/write-set.json")


def git_mv(source: str, destination: str) -> tuple[int, str]:
    """Run `git mv source destination`. Return (exit_code, stderr)."""
    Path(destination).parent.mkdir(parents=True, exist_ok=True)
    result = subprocess.run(
        ["git", "mv", source, destination],
        capture_output=True,
        text=True,
    )
    return result.returncode, result.stderr.strip()


def main() -> int:
    if not WRITE_SET.exists():
        print(f"ERROR: write-set not found at {WRITE_SET}.")
        return 2
    write_set = json.loads(WRITE_SET.read_text(encoding="utf-8"))

    moves: list[tuple[str, str, str]] = []
    for src, dst in zip(
        write_set["cluster_sources_dir_recursive"],
        write_set["cluster_destinations_dir_recursive"],
        strict=True,
    ):
        moves.append(("cluster_dir", src, dst))
    for src, dst in zip(
        write_set["cluster_sources_file"],
        write_set["cluster_destinations_file"],
        strict=True,
    ):
        moves.append(("cluster_file", src, dst))
    for src, dst in zip(
        write_set["tests_migrating_source_paths"],
        write_set["tests_migrating_destination_paths"],
        strict=True,
    ):
        moves.append(("test_file", src, dst))

    print(
        f"Step 3: {len(moves)} moves planned ("
        f"{sum(1 for k, _, _ in moves if k == 'cluster_dir')} cluster_dir + "
        f"{sum(1 for k, _, _ in moves if k == 'cluster_file')} cluster_file + "
        f"{sum(1 for k, _, _ in moves if k == 'test_file')} test_file)"
    )

    failures: list[tuple[str, str, str, str]] = []
    for index, (kind, src, dst) in enumerate(moves, start=1):
        code, err = git_mv(src, dst)
        if code != 0:
            failures.append((kind, src, dst, err))
            print(f"  [{index}/{len(moves)}] FAIL {kind}: {src} -> {dst}: {err}")
            print()
            print("Aborting Step 3. Rollback procedure:")
            print("  python scripts/rollback_e1_write_set.py")
            return 1
        if kind != "test_file" or index % 100 == 0 or index == len(moves):
            print(f"  [{index}/{len(moves)}] OK   {kind}: {src} -> {dst}")

    print(f"Step 3 complete: {len(moves)} moves succeeded, 0 failures.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
