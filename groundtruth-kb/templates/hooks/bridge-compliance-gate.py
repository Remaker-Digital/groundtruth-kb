#!/usr/bin/env python3
"""Run native CLI effect checks for the current harness context.

Copyright 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC.
All rights reserved.
"""

import json

if __name__ == "__main__":
    try:
        from groundtruth_kb.bridge.effect_gate import main
    except ImportError:
        print(
            json.dumps(
                {
                    "hookSpecificOutput": {
                        "hookEventName": "PreToolUse",
                        "permissionDecision": "deny",
                        "permissionDecisionReason": (
                            "native_effect_checker_unavailable: restore the intended GT-KB package installation."
                        ),
                    }
                }
            )
        )
    else:
        raise SystemExit(main())
