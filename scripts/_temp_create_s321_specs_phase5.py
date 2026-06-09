#!/usr/bin/env python3
"""Phase 5: capture spawned-harness durable-role-record-deference directive.

Per owner directive 2026-04-29 (S321):
  "(b) the dispatch prompt ALWAYS defers to the durable record by saying
  'Read your durable role from .claude/rules/operating-role.md'"

Selected option (b) over (a) (runner reads record + crafts prompt) because
deference to the spawned harness's own SessionStart-hook-loaded role
record is more robust: if the durable record changes between dispatch
prompt creation and spawn execution, the spawn still gets the correct
role from its own SessionStart load, not a stale snapshot in the prompt.
"""

from __future__ import annotations

import sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, "tools/knowledge-db")
import db  # noqa: E402

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DB_PATH = PROJECT_ROOT / "groundtruth.db"
CHANGED_BY = "prime-builder/claude"

NEW_SPEC = {
    "id": "DCL-SPAWNED-HARNESS-ROLE-DEFER-DURABLE-RECORD-001",
    "type": "design_constraint",
    "title": "Smart-poller dispatch prompts must defer to the durable role record, not assert role inline",
    "description": (
        "Per owner directive 2026-04-29 (S321): '(b) the dispatch prompt "
        'ALWAYS defers to the durable record by saying "Read your durable '
        "role from .claude/rules/operating-role.md\".'\n\n"
        "RATIONALE: spawned harnesses (claude -p, codex exec) currently "
        "receive role assignment via the dispatch prompt's hard-coded "
        "text ('You are Prime Builder' / 'You are Codex Loyal Opposition'). "
        "This bypasses the durable role record at "
        "`.claude/rules/operating-role.md` and `harness-state/{harness}/"
        "operating-role.md`. The bypass works correctly in default operation "
        "(recipient->role mapping matches durable record) but creates a real "
        "divergence when the owner toggles the durable record (e.g., for a "
        "role-swap session). The spawned harness would receive a prompt-"
        "asserted role contradicting its own SessionStart-hook-loaded role, "
        "creating ambiguity.\n\n"
        "INVARIANT: the dispatch prompt crafted by `_dispatch_prompt()` in "
        "`groundtruth-kb/scripts/bridge_poller_runner.py` MUST instruct the "
        "spawned harness to read its role from the durable record. The "
        "prompt text MUST NOT hard-code the role assignment.\n\n"
        "EXAMPLE NEW PROMPT TEXT:\n"
        "  'Read your durable role record at "
        "`.claude/rules/operating-role.md` (or `harness-state/{harness}/"
        "operating-role.md` if present, which takes precedence) before "
        "acting. Process the bridge entries selected below according to "
        "your declared role.'\n\n"
        "MECHANICAL ENFORCEMENT: a behavioral test verifies "
        "`_dispatch_prompt()` output contains the durable-record reference "
        "and does NOT contain hard-coded role assertions for both PRIME "
        "and CODEX recipients."
    ),
    "scope": "GT-KB platform smart-poller dispatch prompt construction",
    "tags": ["design-constraint", "smart-poller", "durable-record", "role-assignment", "spawned-harness"],
    "assertions": [
        {
            "id": "DCL-SPAWNED-HARNESS-ROLE-DEFER-DURABLE-RECORD-001.A1",
            "kind": "behavioral",
            "description": (
                "_dispatch_prompt(recipient, items, max_items) output text "
                "MUST contain '.claude/rules/operating-role.md' OR equivalent "
                "durable-record reference. Output MUST NOT contain literal "
                "'You are Prime Builder' or 'You are Codex Loyal Opposition' "
                "as standalone role assertions."
            ),
            "verifying_test": "groundtruth-kb/tests/test_bridge_poller_runner.py::test_dispatch_prompt_defers_to_durable_role_record (to be added in implementation slice)",
        },
    ],
    "source_paths": [
        "groundtruth-kb/scripts/bridge_poller_runner.py",
    ],
}

OWNER_QUOTE = (
    "(b) the dispatch prompt ALWAYS defers to the durable record by "
    'saying "Read your durable role from .claude/rules/operating-role.md"'
)


def main() -> int:
    api = db.KnowledgeDB(str(DB_PATH))

    delib_id = "DELIB-S321-SPAWNED-HARNESS-ROLE-DEFER-DURABLE"
    print(f"[idempotent re-run] spec {NEW_SPEC['id']} + DA {delib_id} already inserted; ensuring link exists.")

    # Link spec to DA (only step that failed in initial run due to Unicode print error)
    print(f"[1/1] link spec to DA")
    try:
        api.link_deliberation_spec(
            deliberation_id=delib_id,
            spec_id=NEW_SPEC["id"],
            role="originating",
        )
        print("  OK")
    except Exception as exc:
        print(f"  FAIL: {type(exc).__name__}: {exc}")
        return 1

    print("\n=== SUMMARY ===")
    print(f"  Spec inserted: {NEW_SPEC['id']}")
    print(f"  DA entry inserted: {delib_id}")
    print(f"  Spec->DA link created (role=originating)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
