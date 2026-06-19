#!/usr/bin/env python3
"""Wrap-up helper to clear the active implementation-start packet at VERIFIED."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

# Add scripts/ to sys.path so we can import implementation_authorization
sys.path.insert(0, str(Path(__file__).resolve().parent))
import implementation_authorization  # type: ignore[import-not-found]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--project-root", default=None)
    args = parser.parse_args()

    if args.project_root:
        project_root = Path(args.project_root).resolve()
    else:
        project_root = Path(__file__).resolve().parent.parent

    result = implementation_authorization.clear_active_packet_if_terminal(project_root)
    print(f"implementation_start_packet_clear {json.dumps(result)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
