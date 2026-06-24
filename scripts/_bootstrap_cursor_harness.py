#!/usr/bin/env python3
"""One-shot bootstrap for Cursor harness E (owner-directed)."""

from __future__ import annotations

import json
import shutil
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT / "groundtruth-kb" / "src"))

from groundtruth_kb import harness_ops  # noqa: E402
from groundtruth_kb.config import GTConfig  # noqa: E402
from groundtruth_kb.db import KnowledgeDB  # noqa: E402
from groundtruth_kb.gates import GateRegistry  # noqa: E402
from groundtruth_kb.harness_projection import generate_harness_projection  # noqa: E402
from groundtruth_kb.mode_switch.transaction import TransactionValidationError, apply_role_switch  # noqa: E402


def _open_db(config: GTConfig) -> KnowledgeDB:
    registry = GateRegistry.from_config(
        config.governance_gates,
        include_builtins=True,
        gate_config=config.gate_config,
        project_root=config.project_root,
    )
    return KnowledgeDB(db_path=config.db_path, gate_registry=registry)


def main() -> int:
    config = GTConfig.load(config_path=PROJECT_ROOT / "groundtruth.toml")
    db = _open_db(config)
    surfaces = {
        "headless": {
            "argv": [
                "groundtruth-kb/.venv/Scripts/python.exe",
                "scripts/cursor_harness.py",
                "-p",
                "{{PROMPT}}",
                "--skill",
                "bridge-review",
            ]
        },
        "interactive": {"kind": "ide", "name": "Cursor IDE"},
    }
    if db.get_harness("E") is None:
        harness_ops.register_harness(
            db,
            id="E",
            harness_name="cursor",
            harness_type="cursor",
            role=[],
            reviewer_precedence=15,
            invocation_surfaces=surfaces,
            changed_by="cursor-harness-bootstrap",
            change_reason="owner-directed Cursor harness registration",
        )
        print("registered harness E")
    else:
        print("harness E already registered")

    harness_ops.transition_harness(
        db,
        "E",
        "active",
        changed_by="cursor-harness-bootstrap",
        change_reason="owner-directed Cursor harness activation",
        expected_source=None,
    )
    print("activated harness E")

    try:
        apply_role_switch(
            PROJECT_ROOT,
            "E",
            "loyal-opposition",
            change_reason="owner-directed Cursor LO role assignment",
        )
        print("assigned loyal-opposition role")
    except TransactionValidationError as exc:
        print(f"set-role validation failed: {exc}")
        return 1

    generate_harness_projection(db, PROJECT_ROOT)
    print("projection regenerated")

    src = PROJECT_ROOT / ".codex" / "skills"
    dst = PROJECT_ROOT / ".cursor" / "skills"
    if src.is_dir():
        shutil.copytree(src, dst, dirs_exist_ok=True)
        print(f"skills copied to {dst}")
    else:
        print("warning: .codex/skills missing; skipped skill copy")

    registry = json.loads((PROJECT_ROOT / "harness-state" / "harness-registry.json").read_text(encoding="utf-8"))
    cursor = next((h for h in registry.get("harnesses", []) if h.get("id") == "E"), None)
    print("cursor registry:", json.dumps(cursor, indent=2) if cursor else "MISSING")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
