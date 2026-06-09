"""Record GTKB-CORE-001 Phase 0 formal governance artifacts.

This script is intentionally idempotent. It records owner-approved Phase 0
MemBase artifacts for core application specification intake without modifying
GT-KB package code.

Approval packet:
``.groundtruth/formal-artifact-approvals/2026-04-22-core-spec-intake-phase0.json``.
"""

from __future__ import annotations

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "tools" / "knowledge-db"))

from db import KnowledgeDB  # noqa: E402


CHANGED_BY = "prime-builder/codex"
CHANGE_REASON = "Owner-approved GTKB-CORE-001 Phase 0 governance and compatibility formalization."
DELIB_ID = "DELIB-0875"
SOURCE_REF = "owner_conversation:2026-04-22-core-spec-intake-approved"
SOURCE_PATHS = [
    "memory/work_list.md",
    "bridge/gtkb-core-spec-intake-001.md",
    "independent-progress-assessments/CODEX-INSIGHT-DROPBOX/CORE-SPEC-BASELINE-EVALUATION-2026-04-22.md",
    "independent-progress-assessments/CODEX-INSIGHT-DROPBOX/CORE-SPEC-INTAKE-IMPLEMENTATION-PLAN-2026-04-22.md",
]
TAGS = ["gtkb-core-001", "core-spec-intake", "baseline-specifications"]


DELIB_CONTENT = """\
Owner decision: approve GTKB-CORE-001 Phase 0.

Mike approved proceeding with the core application specification intake
workstream after the standing backlog entry and bridge proposal were reviewed.

Approved direction:
- GT-KB should provide a persisted core application specification intake loop.
- New initialized projects should be enrolled by default.
- Automation and unusual cases must have an explicit opt-out path.
- The loop asks one missing baseline question at a time.
- Prompting continues across sessions while required core slots remain missing,
  inferred, or unclear.
- Prompting stops when every required slot is owner-stated or explicitly not
  applicable.
- Completion is derived from persisted MemBase evidence rather than session
  memory.

Implementation boundary:
- This approval authorizes Phase 0 formalization and the next implementation
  proposal.
- It does not itself implement GT-KB package code.
- Package changes still require review, tests, and post-implementation
  verification.
"""


SPECS = [
    {
        "id": "SPEC-CORE-INTAKE-001",
        "title": "GT-KB Prompts For Missing Core Application Specifications",
        "type": "requirement",
        "description": """\
GT-KB must surface a core application specification intake loop for newly
initialized projects. After project initialization, and during later startup or
doctor-style health checks, GT-KB must be able to identify the next missing core
application specification slot and present exactly one deterministic question
for the owner to answer.

The baseline slots include product identity, application type, tenancy,
users/roles, data classification, compliance obligations, security posture,
reliability posture, external integrations, AI usage, operational/release path,
and explicit first-release non-goals.

The prompt is not a long onboarding wizard. It is a persisted missing-spec
detector that reduces owner burden to specifications, clarifications, and
decisions.
""",
    },
    {
        "id": "SPEC-CORE-INTAKE-002",
        "title": "Core Specification Prompting Stops At Persisted Completion",
        "type": "requirement",
        "description": """\
Core application specification prompting must continue while any required core
slot is missing, inferred, or needs clarity. Prompting must stop automatically
once every required core slot is either owner-stated or explicitly marked not
applicable in persisted evidence.

Generated or inferred candidates must not suppress future prompts until the
owner confirms them. Explicit not-applicable decisions must be treated as
complete for that slot, not as missing information.
""",
    },
    {
        "id": "ADR-CORE-INTAKE-001",
        "title": "Core Spec Completion Uses Persisted MemBase Evidence",
        "type": "architecture_decision",
        "description": """\
GT-KB core application specification completion is derived from persisted
MemBase evidence, not from conversation memory or a transient session flag.

The evaluator should prefer stable slot handles, tags, or linked decision
records over fuzzy title matching. This avoids both repeated prompting after
the owner has already answered and premature suppression when an AI merely
inferred a candidate answer.
""",
    },
    {
        "id": "DCL-CORE-INTAKE-001",
        "title": "Core Intake Preserves Scaffold And Automation Compatibility",
        "type": "design_constraint",
        "description": """\
Core application specification intake may become default-on for new projects
only if existing scaffold profile semantics and automation-safe paths remain
compatible.

Existing minimal and full spec scaffold behavior must remain backward-compatible
unless separately approved. Non-interactive and JSON-safe command paths must not
emit interactive prompts. Automation and unusual projects must have an explicit
opt-out path such as a command flag or project configuration setting.
""",
    },
]


def _insert_deliberation_if_absent(db: KnowledgeDB) -> str:
    if db.get_deliberation(DELIB_ID) is not None:
        return "skipped"
    db.insert_deliberation(
        id=DELIB_ID,
        source_type="owner_conversation",
        source_ref=SOURCE_REF,
        title="Owner approval for GT-KB core specification intake Phase 0",
        summary=(
            "Owner approved proceeding with GTKB-CORE-001 Phase 0: default-on "
            "core spec intake with explicit opt-out and persisted stop conditions."
        ),
        content=DELIB_CONTENT,
        participants=["owner", "prime-builder/codex"],
        outcome="owner_decision",
        changed_by=CHANGED_BY,
        change_reason=CHANGE_REASON,
        origin_project="Agent Red Customer Engagement",
        origin_repo="Agent Red Customer Engagement",
    )
    return "created"


def _insert_spec_if_absent(db: KnowledgeDB, spec: dict[str, str]) -> str:
    if db.get_spec(spec["id"]) is not None:
        return "skipped"
    db.insert_spec(
        id=spec["id"],
        title=spec["title"],
        status="specified",
        changed_by=CHANGED_BY,
        change_reason=CHANGE_REASON,
        description=spec["description"],
        type=spec["type"],
        authority="stated",
        testability="structural",
        affected_by=[DELIB_ID],
        source_paths=SOURCE_PATHS,
        tags=TAGS,
    )
    return "created"


def main() -> int:
    db = KnowledgeDB(REPO_ROOT / "groundtruth.db")
    actions: list[tuple[str, str]] = []
    try:
        actions.append((DELIB_ID, _insert_deliberation_if_absent(db)))
        for spec in SPECS:
            actions.append((spec["id"], _insert_spec_if_absent(db, spec)))
    finally:
        db.close()

    print("GTKB-CORE-001 Phase 0 formalization")
    print("=" * 48)
    for artifact_id, action in actions:
        mark = "+" if action == "created" else "="
        print(f"  {mark} {action:<8} {artifact_id}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
