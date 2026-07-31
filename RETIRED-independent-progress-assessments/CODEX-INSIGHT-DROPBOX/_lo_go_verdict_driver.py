#!/usr/bin/env python3
"""One-shot driver: write a native LO proposal-review GO verdict via the governed writer.

Usage:
  python _lo_go_verdict_driver.py --slug <document> --version <N> --body-file <path>

Uses scripts.gtkb_bridge_writer.write_bridge_file (the low-level governed writer
used by native harness helpers). Does NOT require a work-intent claim. Runs the
bridge-compliance audit and (for GO) skips the WI-4520 anchor gate.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

PROJECT_ROOT = Path.cwd()
for _p in (str(PROJECT_ROOT / "groundtruth-kb" / "src"), str(PROJECT_ROOT)):
    if _p not in sys.path:
        sys.path.insert(0, _p)

from scripts.gtkb_bridge_writer import write_bridge_file  # noqa: E402


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--slug", required=True)
    parser.add_argument("--version", type=int, required=True)
    parser.add_argument("--body-file", required=True)
    args = parser.parse_args()

    content = Path(args.body_file).read_text(encoding="utf-8")
    written = write_bridge_file(args.slug, args.version, content, PROJECT_ROOT)
    print("WROTE", written)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
