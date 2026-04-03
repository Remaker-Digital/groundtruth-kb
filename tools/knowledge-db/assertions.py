"""Agent Red assertion runner — AR-aware shim over groundtruth_kb.assertions.

Delegates all assertion execution to the upstream groundtruth_kb package
while injecting Agent Red's project root automatically. Preserves the
local callable signatures and CLI interface for hooks and scripts.

Upstream supports 8 assertion types: grep, glob, grep_absent, file_exists,
count, json_path, all_of, any_of.

Usage:
  python tools/knowledge-db/assertions.py                  # run all, manual trigger
  python tools/knowledge-db/assertions.py --pre-build      # pre-build gate
  python tools/knowledge-db/assertions.py --session-start  # session startup check
  python tools/knowledge-db/assertions.py --spec 245       # single spec only

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

from __future__ import annotations

import argparse
import io
import sys
from pathlib import Path
from typing import Any

# Windows cp1252 stdout encoding fix — only when running as main script
if __name__ == "__main__":
    if sys.stdout and hasattr(sys.stdout, "buffer"):
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    if sys.stderr and hasattr(sys.stderr, "buffer"):
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")

# Project root: 3 levels up from tools/knowledge-db/assertions.py
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent

# Import sibling db shim (already delegates to groundtruth_kb)
from db import KnowledgeDB

# Import upstream assertion engine
from groundtruth_kb.assertions import (
    format_summary as _upstream_format_summary,
    run_all_assertions as _upstream_run_all,
    run_single_assertion as _upstream_run_single,
)


# ---------------------------------------------------------------------------
# AR-aware wrappers (preserve local signatures, inject project_root)
# ---------------------------------------------------------------------------


def run_single_assertion(assertion: dict[str, Any]) -> dict[str, Any]:
    """Run a single assertion against the Agent Red codebase.

    Wraps upstream run_single_assertion(assertion, project_root) by
    injecting PROJECT_ROOT automatically.
    """
    return _upstream_run_single(assertion, PROJECT_ROOT)


def run_all_assertions(
    db: KnowledgeDB,
    triggered_by: str = "manual",
    spec_id: str | None = None,
) -> dict[str, Any]:
    """Run all assertions for the Agent Red project.

    Wraps upstream run_all_assertions(db, project_root, ...) by
    injecting PROJECT_ROOT automatically.
    """
    return _upstream_run_all(
        db, PROJECT_ROOT, triggered_by=triggered_by, spec_id=spec_id,
    )


def print_summary(summary: dict[str, Any]) -> None:
    """Print a human-readable assertion summary.

    Delegates to upstream format_summary() and prints the result.
    """
    print(_upstream_format_summary(summary))


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def main() -> int:
    parser = argparse.ArgumentParser(description="Run feature assertions against codebase")
    parser.add_argument("--pre-build", action="store_true", help="Pre-build gate mode")
    parser.add_argument("--session-start", action="store_true", help="Session startup check")
    parser.add_argument("--spec", type=str, default=None, help="Run assertions for a single spec ID")
    args = parser.parse_args()

    triggered_by = "manual"
    if args.pre_build:
        triggered_by = "pre-build"
    elif args.session_start:
        triggered_by = "session-start"

    db = KnowledgeDB()
    try:
        summary = run_all_assertions(db, triggered_by=triggered_by, spec_id=args.spec)
        print_summary(summary)

        # Exit code: 0 if all pass, 1 if any failures (useful for CI gates)
        if summary.get("failed", 0) > 0:
            return 1
        return 0
    finally:
        db.close()


if __name__ == "__main__":
    sys.exit(main())
