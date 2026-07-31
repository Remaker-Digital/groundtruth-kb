"""Owner-decision tracker integration with the Deliberation Archive.

Slice 4 of GTKB-ARTIFACT-RECORDER-CLI: bridges resolved AskUserQuestion outcomes
detected by ``.claude/hooks/owner-decision-tracker.py`` to the canonical
``record_deliberation`` service from Slice 1.
"""

from groundtruth_kb.owner_decision.auto_archive import (
    DecisionForArchive,
    archive_decision,
    should_auto_archive,
)
from groundtruth_kb.owner_decision.resolution_signals import (
    ResolutionSignal,
    build_live_bridge_status_reader,
    extract_bridge_slugs,
    read_owner_decision_deliberations,
    resolve_pending_entries,
)

__all__ = [
    "DecisionForArchive",
    "ResolutionSignal",
    "archive_decision",
    "build_live_bridge_status_reader",
    "extract_bridge_slugs",
    "read_owner_decision_deliberations",
    "resolve_pending_entries",
    "should_auto_archive",
]
