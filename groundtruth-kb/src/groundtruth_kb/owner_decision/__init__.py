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

__all__ = [
    "DecisionForArchive",
    "archive_decision",
    "should_auto_archive",
]
