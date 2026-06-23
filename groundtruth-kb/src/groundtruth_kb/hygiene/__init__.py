"""GroundTruth-KB hygiene package — deterministic drift-discovery services.

Provides the ``gt hygiene sweep`` CLI surface and supporting logic for scanning
the repository against owner-curated pattern sets and emitting findings to
``.gtkb-state/hygiene-sweep/<run-id>/``.

Per ``DELIB-S312-DETERMINISTIC-SERVICES-PRINCIPLE``: this package replaces
per-instance manual drift investigation with a deterministic service that
walks files and matches content patterns.

Copyright (c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

from __future__ import annotations

from groundtruth_kb.hygiene.supersession import (
    DEFAULT_MARKERS,
    SupersessionFinding,
    SupersessionMarker,
    SupersessionScanResult,
    emit_supersession_json,
    emit_supersession_markdown,
    run_supersession_scan,
    scan_supersession_file,
    walk_live_files,
)
from groundtruth_kb.hygiene.sweep import (
    Finding,
    Pattern,
    PatternSetError,
    SweepResult,
    emit_json,
    emit_markdown,
    load_pattern_set,
    run_sweep,
    scan_file,
    walk_repo,
)

__all__ = [
    "DEFAULT_MARKERS",
    "Finding",
    "Pattern",
    "PatternSetError",
    "SupersessionFinding",
    "SupersessionMarker",
    "SupersessionScanResult",
    "SweepResult",
    "emit_json",
    "emit_markdown",
    "emit_supersession_json",
    "emit_supersession_markdown",
    "load_pattern_set",
    "run_supersession_scan",
    "run_sweep",
    "scan_file",
    "scan_supersession_file",
    "walk_live_files",
    "walk_repo",
]
