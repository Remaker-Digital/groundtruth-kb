# Copyright 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""Archive DELIB-S344-SPEC-EXPRESSIONS-TRIANGULATION-001.

Owner-directed canonicalization (S344, 2026-05-11) of the cross-harness-agreed
framing of how a specification's three load-bearing expressions triangulate
intent, conformance, and behavior, plus the Deliberation Archive's reference
(not authoritative) role.

Run: GTKB_FORMAL_APPROVAL_PACKET=.groundtruth/formal-artifact-approvals/2026-05-11-DELIB-S344-SPEC-EXPRESSIONS-TRIANGULATION-001.json python scripts/archive/record_delib_s344_spec_expressions_triangulation.py
"""

from __future__ import annotations

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT))
sys.path.insert(0, str(REPO_ROOT / "groundtruth-kb" / "src"))

from groundtruth_kb.db import KnowledgeDB  # noqa: E402
from scripts._kb_attribution import resolve_changed_by  # noqa: E402

DELIB_ID = "DELIB-S344-SPEC-EXPRESSIONS-TRIANGULATION-001"

CONTENT = """A specification records what the owner wants the application to do, in language precise enough to verify whether an implementation conforms. Each specification has three load-bearing expressions: (1) the specification itself, recorded in MemBase as the authoritative governed record of intent; (2) one or more tests or verification procedures that provide executable evidence of whether an implementation satisfies the specification; and (3) the implementation artifact, such as code, configuration, or another deliverable, whose behavior is exercised by those tests. Each expression is canonical for its own domain: intent, conformance, and behavior. None is sufficient alone: a specification without tests cannot be verified, tests without an implementation verify nothing, and an implementation without a specification has lost its governing intent. Together, the three make drift between intent, verification, and reality detectable. The Deliberation Archive is a reference source, not an authority, for the reasoning behind specifications: owner conversations, rejected alternatives, prior decisions, and tradeoffs. It is consulted to disambiguate intent, interpret a current decision in light of prior reasoning, or resolve apparent contention between specifications; it does not override the specifications it supports."""

SUMMARY = (
    "Canonical articulation of how a specification's three load-bearing "
    "expressions triangulate to make drift between intent, conformance, and "
    "behavior detectable: (1) the spec record in MemBase (intent), (2) tests "
    "or verification procedures providing executable evidence (conformance), "
    "(3) the implementation artifact (behavior). Each expression is canonical "
    "for its own domain; none is sufficient alone. The Deliberation Archive "
    "is a reference source (not authoritative) for the reasoning behind "
    "specifications, consulted to disambiguate intent, interpret current "
    "decisions in light of prior reasoning, or resolve apparent contention "
    "between specifications."
)


def main() -> int:
    db = KnowledgeDB(REPO_ROOT / "groundtruth.db")

    result = db.insert_deliberation(
        id=DELIB_ID,
        source_type="owner_conversation",
        title="Three load-bearing expressions of a specification; Deliberation Archive as reference, not authority",
        summary=SUMMARY,
        content=CONTENT,
        changed_by=resolve_changed_by(),
        change_reason=(
            "Owner-directed canonicalization of cross-harness-agreed framing "
            "(S344, 2026-05-11). Rationale: memory and knowledge are the core "
            "of GT-KB; this articulation explains how the three core artifact "
            "types relate and how the Deliberation Archive's role is bounded. "
            "Text refined by owner with two precision corrections to the "
            "Prime/LO-aligned draft."
        ),
        outcome="owner_decision",
        session_id="S344",
        source_ref="owner_conversation:2026-05-11-S344-spec-expressions-triangulation",
        participants=["owner", "claude-prime-builder", "codex-loyal-opposition"],
    )

    delib_id = result.get("id") if result else DELIB_ID
    version = result.get("version") if result else "?"
    print(f"insert_deliberation id={delib_id} version={version}", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
