#!/usr/bin/env python3
"""Compatibility entrypoint for the canonical WI-4979 auto-resolve planner.

WI-5027 introduced this script path. WI-4979 keeps the path stable while moving
the shared classifier and forbidden-operation list into
``groundtruth_kb.hygiene.auto_resolve`` so there is only one planning engine.
"""

from __future__ import annotations

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
GT_SRC = PROJECT_ROOT / "groundtruth-kb" / "src"
if GT_SRC.is_dir() and str(GT_SRC) not in sys.path:
    sys.path.insert(0, str(GT_SRC))

from groundtruth_kb.hygiene.auto_resolve import (  # noqa: E402,F401
    ACTION_EVIDENCE_REQUIREMENTS,
    ACTUATOR_ACTIONS,
    BRIDGE_STATUS_TOKENS,
    FORBIDDEN_OPERATIONS,
    PROTECTED_EXACT,
    PROTECTED_PREFIXES,
    AutoResolveError,
    GitStatusEntry,
    TriageError,
    build_plan,
    classify_entry,
    collect_git_status,
    format_markdown,
    main,
    parse_porcelain_z,
    refuse_apply,
    summarize_plan,
)

if __name__ == "__main__":
    raise SystemExit(main())
