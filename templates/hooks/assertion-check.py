#!/usr/bin/env python3
"""
SessionStart hook — Run GroundTruth assertions at the start of each session.

Reads the knowledge database, runs all assertions on implemented/verified
specs, and injects a summary into the session context. Failing assertions
on implemented/verified specs indicate regressions.

Hook type: SessionStart
Stdin:  JSON (SessionStart payload, includes CLAUDE_PROJECT_DIR)
Stdout: JSON {"additionalContext": "..."} or {}
Exit:   Always 0 (hooks must not block session start)

Customize: adjust PROJECT_DIR resolution and TOML path for your project layout.
"""

import json
import os
import sys
from pathlib import Path

PROJECT_DIR = Path(os.environ.get("CLAUDE_PROJECT_DIR", os.getcwd()))
TOML_PATH = PROJECT_DIR / "groundtruth.toml"


def main() -> None:
    # Read stdin (required by hook protocol, consume but ignore)
    _stdin = sys.stdin.read()  # noqa: F841

    if not TOML_PATH.exists():
        print(json.dumps({}))
        return

    try:
        from groundtruth_kb.assertions import run_all_assertions
        from groundtruth_kb.config import GTConfig
        from groundtruth_kb.db import KnowledgeDB
        from groundtruth_kb.gates import GateRegistry

        config = GTConfig.load(config_path=TOML_PATH)
        registry = GateRegistry.from_config(
            config.governance_gates,
            gate_config=config.gate_config,
            project_root=config.project_root,
        )
        db = KnowledgeDB(db_path=config.db_path, gate_registry=registry)

        summary = run_all_assertions(db, project_root=config.project_root)
        db.close()

        if not summary or "error" in summary:
            print(json.dumps({}))
            return

        passed = summary.get("passed", 0)
        failed = summary.get("failed", 0)
        total = summary.get("specs_with_assertions", 0)
        details = summary.get("details", [])

        lines = [f"Assertion check: {passed}/{total} passed, {failed} failed."]
        if failed > 0:
            lines.append("REGRESSIONS DETECTED — investigate before proceeding.")
            for r in details:
                if not r.get("skipped") and not r.get("overall_passed"):
                    lines.append(f"  FAIL: {r.get('spec_id', '?')}")

        context = "\n".join(lines)
        print(json.dumps({"additionalContext": context}))

    except Exception as e:
        # Hook must never block session start
        print(json.dumps({"additionalContext": f"Assertion hook error: {e}"}))


if __name__ == "__main__":
    main()
