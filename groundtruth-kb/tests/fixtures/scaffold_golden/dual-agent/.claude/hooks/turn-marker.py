#!/usr/bin/env python3
# © 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""Turn-marker hook (UserPromptSubmit).

Records a lightweight turn-start marker for downstream hooks that need to
correlate activity within a single turn (delib-preflight-gate,
owner-decision-capture, gov09-capture).

Currently a scaffold stub: exits 0 on any input. Real implementation lands
in a follow-up commit per the fast-iterate posture.

See: bridge/gtkb-da-governance-completeness-implementation-015.md §5.5
See: memory/feedback_iterate_fast_on_main.md (S300)
"""

from __future__ import annotations

import sys


def main() -> int:
    """Hook entry point. Stub implementation: no-op exit 0."""
    return 0


if __name__ == "__main__":
    sys.exit(main())
