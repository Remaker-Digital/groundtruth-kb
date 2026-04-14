#!/usr/bin/env python3
"""Requirement intake classifier hook — classifies owner input against active specs.

Install: copy to .claude/hooks/intake-classifier.py
Event: UserPromptSubmit

Classifies owner language into directive, constraint, preference, question,
or exploration categories. High-confidence directives trigger the intake
capture workflow.

Copyright (c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
Licensed under AGPL-3.0-or-later.
"""

import json
import sys
from pathlib import Path


def main() -> None:
    hook_input = json.loads(sys.stdin.read())
    prompt = hook_input.get("prompt", "")
    if not prompt:
        return

    cwd = Path.cwd()
    toml_path = cwd / "groundtruth.toml"
    if not toml_path.exists():
        return

    try:
        from groundtruth_kb.config import GTConfig
        from groundtruth_kb.db import KnowledgeDB
        from groundtruth_kb.intake import classify_requirement

        config = GTConfig.from_toml(toml_path)
        db = KnowledgeDB(db_path=config.db_path)
        result = classify_requirement(db, prompt)

        if result["confidence"] > 0.8 and result["classification"] == "directive":
            print(
                json.dumps(
                    {
                        "classification": result["classification"],
                        "confidence": result["confidence"],
                        "related_specs": result["related_specs"][:3],
                    }
                )
            )
    except Exception:
        pass  # Non-blocking


if __name__ == "__main__":
    main()
