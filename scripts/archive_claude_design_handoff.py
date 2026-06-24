"""Archive a Claude Design handoff into the Deliberation Archive.

Compatibility / maintainer wrapper. The reusable handoff inspection, validation,
content-formatting, and archival pipeline now lives in the package module
``groundtruth_kb.design_import`` and is exposed package-wide via
``gt design import``. This script preserves the original CLI contract
(PROC-CD-DA-ARCHIVAL-001) and the **Agent Red-scoped** Deliberation Archive
target: standalone ``--apply`` runs continue to write to the AR
``tools/knowledge-db`` shim database with its transport-gate wiring, unchanged by
the package extraction.

Implements PROC-CD-DA-ARCHIVAL-001 (``archive-claude-design-handoff``) from
``bridge/agent-red-claude-design-gui-refresh-intake-implementation-002.md``.

Each handoff produces one ``report`` DA row (Prime's inspection record).
The KB's ``current_deliberations`` table enforces a closed source_type set
(``bridge_thread``, ``lo_review``, ``owner_conversation``, ``proposal``,
``report``, ``session_harvest``), so Prime inspection records are classified
as ``report``. Mid-handoff owner decisions can be added as separate
``owner_conversation`` rows via subsequent invocations.

Usage
-----
::

    python scripts/archive_claude_design_handoff.py \\
        --handoff-path <zip-or-directory> \\
        --date 2026-04-18 \\
        --session-id S302 \\
        --owner-decision "token-only-candidate + net-new-feature-proposals" \\
        --apply

Omit ``--apply`` for a dry run. Exit code 0 on success (including skipped
idempotent re-runs); 2 on validation/IO error.

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from groundtruth_kb.design_import import (
    ArchiveResult,
    HandoffEntry,
    HandoffInspection,
    archive,
    format_inspection_content,
    inspect_handoff,
    validate_handoff_format,
)

REPO_ROOT = Path(__file__).resolve().parent.parent

# Re-export the package pipeline names so existing callers and the script-level
# regression test (which loads this file by path) keep their import contract.
__all__ = [
    "ArchiveResult",
    "HandoffEntry",
    "HandoffInspection",
    "archive",
    "format_inspection_content",
    "inspect_handoff",
    "validate_handoff_format",
    "main",
]

# Attribution recorded on DA rows created by this standalone script (preserved
# from the pre-extraction behavior).
_SCRIPT_CHANGED_BY = "archive_claude_design_handoff.py"


def _load_ar_kb():
    """Load the Agent Red-scoped KnowledgeDB (``tools/knowledge-db`` shim).

    Preserves this script's historical Deliberation Archive target so standalone
    ``--apply`` runs continue to write to the AR ``knowledge.db`` with the AR
    transport-gate wiring, unchanged by the package extraction. The package
    module's own default (root ``groundtruth.db``) is intentionally *not* used
    here.
    """
    sys.path.insert(0, str(REPO_ROOT / "tools" / "knowledge-db"))
    from db import KnowledgeDB

    return KnowledgeDB()


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Archive a Claude Design handoff into the Deliberation Archive.")
    parser.add_argument(
        "--handoff-path",
        required=True,
        help="Path to the handoff zip or directory.",
    )
    parser.add_argument(
        "--date",
        required=True,
        help="Handoff date in ISO format, e.g., 2026-04-18.",
    )
    parser.add_argument(
        "--session-id",
        required=True,
        help="Session id that inspected the handoff, e.g., S302.",
    )
    parser.add_argument(
        "--owner-decision",
        default=None,
        help="Triage outcome / owner decision text (becomes a DA section).",
    )
    parser.add_argument(
        "--notes",
        default=None,
        help=(
            "Canonical owner-supplied inspection-text channel for the handoff. "
            "Accepts owner-supplied inspection markdown (pre-read by the caller "
            "— pass the string, not a path). Redaction-safe free text; "
            "included verbatim in the DA row's Notes section."
        ),
    )
    parser.add_argument(
        "--source-ref",
        default=None,
        help="Override source_ref (default: claude-design-handoff:<date>:<name>).",
    )
    parser.add_argument(
        "--apply",
        action="store_true",
        help="Insert the DA row. Omit for a dry run.",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    args = _build_parser().parse_args(argv)
    path = Path(args.handoff_path).resolve()
    # Standalone --apply targets the Agent Red-scoped KnowledgeDB; dry runs need
    # no database access.
    db = _load_ar_kb() if args.apply else None
    try:
        result = archive(
            handoff_path=path,
            date=args.date,
            session_id=args.session_id,
            owner_decision=args.owner_decision,
            notes=args.notes,
            source_ref=args.source_ref,
            apply=args.apply,
            db=db,
            changed_by=_SCRIPT_CHANGED_BY,
        )
    except (FileNotFoundError, ValueError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2

    print(f"action:          {result.action}")
    print(f"source_ref:      {result.source_ref}")
    print(f"content_hash:    {result.content_hash}")
    if result.delib_id is not None:
        print(f"delib_id:        {result.delib_id}")
    if result.redaction_reason:
        print(f"redaction:       {result.redaction_reason}")
    if result.warnings:
        print("format warnings:")
        for w in result.warnings:
            print(f"  - {w}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
