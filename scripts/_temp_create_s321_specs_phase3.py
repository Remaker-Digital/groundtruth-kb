#!/usr/bin/env python3
"""Phase 3 of S321 spec batch: 5 specs for triad completeness + retroactive linkage.

Per owner directive 2026-04-29 (S321):
  "Retroactively create specifications which cover past approved and verified
  implementations which have not been explicitly linked to specifications. If
  tests have not been created for those specifications, create new tests. GT-KB
  must have a test suite that is independent of the application test suites
  (e.g., Agent Red). Specifications which were created for Agent Red may now
  apply to GT-KB, not Agent Red as a conformant, contained application. We must
  fill in all gaps in specifications, tests and implementation using historical
  information. The completeness of the specification/test/implementation triad
  is an essential part of the GT-KB knowledge architecture that prevents drift
  over time. This system must be mechanically enforced and comprehensive."
"""

from __future__ import annotations

import hashlib
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, "tools/knowledge-db")
import db  # noqa: E402

PROJECT_ROOT = Path(__file__).resolve().parent.parent
APPROVAL_DIR = PROJECT_ROOT / ".groundtruth" / "formal-artifact-approvals"
DB_PATH = PROJECT_ROOT / "groundtruth.db"

CHANGED_BY = "prime-builder/claude"
CHANGE_REASON = (
    "Capture S321 2026-04-29 phase-3 batch (5 specs for triad-completeness + "
    "retroactive-linkage program). Owner standing authorization grants approval."
)

SPECS = [
    # 1. The core triad-completeness rule
    {
        "id": "DCL-SPEC-TEST-IMPL-TRIAD-COMPLETENESS-001",
        "type": "design_constraint",
        "title": "Specification/test/implementation triad must be complete or tracked-incomplete",
        "description": (
            "Per owner directive 2026-04-29: 'The completeness of the "
            "specification/test/implementation triad is an essential part of "
            "the GT-KB knowledge architecture that prevents drift over time.'\n\n"
            "INVARIANT: every implementation in GT-KB platform code (status: "
            "implemented or verified) MUST be linked to at least one "
            "specification (SPEC/GOV/ADR/DCL/PB). Every linked specification "
            "MUST have at least one derived test (test cites the spec ID in "
            "its docstring per DCL-TEST-SPEC-DERIVATION format). Every "
            "derived test MUST be discoverable and executed by an active test "
            "lane (release-candidate gate or equivalent).\n\n"
            "GAP TRACKING: any triad node that is missing (spec without "
            "tests; test without spec citation; implementation without spec "
            "linkage) MUST be tracked in the standing triad-completeness "
            "audit (GOV-TRIAD-COMPLETENESS-AUDIT-001). Untracked gaps are "
            "the failure mode this DCL prevents.\n\n"
            "NEW IMPLEMENTATIONS: cannot reach status 'verified' until the "
            "triad is complete (DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-"
            "001 is the existing enforcement point for this).\n\n"
            "EXISTING IMPLEMENTATIONS: pre-S321 implementations without "
            "complete triad MUST receive retroactive coverage per "
            "DCL-RETROACTIVE-LINKAGE-OBLIGATION-001."
        ),
        "scope": "GT-KB platform; foundational invariant for the entire knowledge architecture",
        "tags": ["design-constraint", "triad-completeness", "drift-prevention", "mechanical-enforcement"],
        "assertions": [
            {
                "id": "DCL-SPEC-TEST-IMPL-TRIAD-COMPLETENESS-001.A1",
                "kind": "behavioral",
                "description": (
                    "Standing audit MUST report: (a) implementations without "
                    "spec linkage; (b) specs without derived tests; (c) tests "
                    "not in any executed lane. Each gap is a P0/P1/P2 finding "
                    "depending on the spec's status (verified > implemented > "
                    "specified)."
                ),
                "verifying_test": "deferred to triad-completeness audit implementation",
            },
            {
                "id": "DCL-SPEC-TEST-IMPL-TRIAD-COMPLETENESS-001.A2",
                "kind": "behavioral",
                "description": (
                    "Promotion of a spec from 'implemented' to 'verified' "
                    "MUST be blocked unless triad is complete (≥1 derived "
                    "test executed and passing). Promotion mechanism in "
                    "groundtruth_kb.cli or db.update_spec MUST enforce."
                ),
                "verifying_test": "deferred to promotion-gate implementation",
            },
        ],
    },
    # 2. Retroactive linkage obligation
    {
        "id": "DCL-RETROACTIVE-LINKAGE-OBLIGATION-001",
        "type": "design_constraint",
        "title": "Past approved/verified implementations without spec linkage must receive retroactive coverage",
        "description": (
            "Per owner directive 2026-04-29: 'Retroactively create "
            "specifications which cover past approved and verified "
            "implementations which have not been explicitly linked to "
            "specifications. If tests have not been created for those "
            "specifications, create new tests.'\n\n"
            "OBLIGATION: every pre-S321 implementation that ships in GT-KB "
            "platform code (groundtruth-kb/, scripts/, .claude/, etc.) and "
            "lacks current spec linkage MUST receive retroactive spec "
            "creation under owner standing authorization "
            "(GOV-SPEC-CREATION-STANDING-AUTHORIZATION-001).\n\n"
            "SCOPE: implementations identified via git log + bridge audit "
            "trail + groundtruth.db existing entries. The audit (GOV-TRIAD-"
            "COMPLETENESS-AUDIT-001) enumerates candidates.\n\n"
            "TEST OBLIGATION: if a retroactively-created spec has no derived "
            "test, tests MUST be created. Tests must derive from the spec "
            "(cite the spec ID in docstring) and be in an executed lane.\n\n"
            "ATTRIBUTION CORRECTION (per DCL-AGENT-RED-CONFORMANT-CONTAINED-"
            "APP-001): specs originally attributed to Agent Red that "
            "actually govern GT-KB platform behavior MUST be reattributed "
            "to GT-KB. The attribution shift is recorded as a spec update "
            "(via db.update_spec) preserving the original spec ID + "
            "version chain."
        ),
        "scope": "GT-KB platform retroactive governance",
        "tags": ["design-constraint", "retroactive-coverage", "spec-creation", "test-creation"],
        "assertions": [
            {
                "id": "DCL-RETROACTIVE-LINKAGE-OBLIGATION-001.A1",
                "kind": "behavioral",
                "description": (
                    "Audit identifies pre-S321 implementations without spec "
                    "linkage; for each, either (a) a retroactive spec is "
                    "created OR (b) the implementation is removed/deprecated."
                ),
                "verifying_test": "deferred to triad-completeness audit + retroactive-coverage implementation",
            },
            {
                "id": "DCL-RETROACTIVE-LINKAGE-OBLIGATION-001.A2",
                "kind": "behavioral",
                "description": (
                    "Every retroactively-created spec has at least one "
                    "derived test in the executed test lane within 1 "
                    "session of spec creation."
                ),
                "verifying_test": "deferred",
            },
        ],
    },
    # 3. GT-KB independent test suite
    {
        "id": "DCL-GTKB-INDEPENDENT-TEST-SUITE-001",
        "type": "design_constraint",
        "title": "GT-KB platform must have a test suite independent of contained-application test suites",
        "description": (
            "Per owner directive 2026-04-29: 'GT-KB must have a test suite "
            "that is independent of the application test suites (e.g., "
            "Agent Red).'\n\n"
            "INVARIANT: GT-KB platform tests live under "
            "groundtruth-kb/tests/ AND a top-level location (e.g., "
            "platform-tests/ or tests/platform/) that excludes any "
            "Agent-Red-specific or application-specific test fixtures, "
            "dependencies, or assertions. The platform test suite MUST be "
            "executable as a standalone target (e.g., `pytest groundtruth-"
            "kb/tests/` or `gt platform test`) without any "
            "applications/Agent_Red/ files present.\n\n"
            "BOUNDARY: a test in the platform suite that imports from "
            "applications/Agent_Red/ or asserts on Agent-Red-specific "
            "content is non-compliant. The audit (GOV-TRIAD-COMPLETENESS-"
            "AUDIT-001) MUST identify boundary violations.\n\n"
            "CONSEQUENCE: tests that exercise platform code via Agent Red "
            "fixtures MUST be either (a) refactored to use platform-only "
            "fixtures OR (b) duplicated — one Agent-Red-specific in "
            "applications/Agent_Red/tests/, one platform-generic in "
            "groundtruth-kb/tests/. Reference DCL-PLATFORM-APPLICATION-"
            "NON-SPECIFICITY-001 (KB-resolved)."
        ),
        "scope": "GT-KB platform test suite organization",
        "tags": ["design-constraint", "test-suite-isolation", "platform-purity"],
        "assertions": [
            {
                "id": "DCL-GTKB-INDEPENDENT-TEST-SUITE-001.A1",
                "kind": "behavioral",
                "description": (
                    "Platform test suite executes successfully with "
                    "applications/Agent_Red/ moved or absent. No platform "
                    "test imports applications.Agent_Red.* modules."
                ),
                "verifying_test": "deferred to platform-test-isolation audit",
            },
            {
                "id": "DCL-GTKB-INDEPENDENT-TEST-SUITE-001.A2",
                "kind": "behavioral",
                "description": (
                    "Audit reports any test in groundtruth-kb/tests/ or "
                    "platform-tests/ that references Agent-Red-specific "
                    "paths, modules, or fixtures. Such references are "
                    "non-compliant unless explicitly waivered."
                ),
                "verifying_test": "deferred",
            },
        ],
    },
    # 4. Agent Red as conformant contained application
    {
        "id": "DCL-AGENT-RED-CONFORMANT-CONTAINED-APP-001",
        "type": "design_constraint",
        "title": "Agent Red is the conformant, contained application; spec attribution defaults to GT-KB platform",
        "description": (
            "Per owner directive 2026-04-29: 'Specifications which were "
            "created for Agent Red may now apply to GT-KB, not Agent Red "
            "as a conformant, contained application.'\n\n"
            "ATTRIBUTION RULE: every existing spec in groundtruth.db whose "
            "subject is GT-KB platform behavior (regardless of historical "
            "creation context) IS attributed to GT-KB platform, not to "
            "Agent Red specifically. Agent Red is the conformant contained "
            "application that consumes GT-KB; specs governing GT-KB "
            "behavior are platform specs.\n\n"
            "SCOPE OF CORRECTION: pre-S321 specs that were filed when the "
            "project was framed as 'Agent Red Customer Experience' but "
            "actually govern platform behavior (bridge protocol, KB "
            "schema, hooks, scaffolding, etc.) MUST be reattributed via "
            "db.update_spec adding 'GT-KB platform' to the scope/tags "
            "fields. Original spec IDs preserved (no renaming).\n\n"
            "AGENT-RED-SPECIFIC SCOPE: specs that genuinely govern only "
            "Agent Red commercial-product behavior (e.g., specific UI "
            "elements, customer-facing copy, billing integration "
            "specifics) remain attributed to Agent Red. The audit "
            "distinguishes via spec content, not historical filing "
            "context.\n\n"
            "REFERENCES DCL-PLATFORM-APPLICATION-NON-SPECIFICITY-001 "
            "(KB-resolved): platform implementations must be application-"
            "non-specific; this DCL governs the spec-attribution side of "
            "the same architectural separation."
        ),
        "scope": "GT-KB platform spec attribution and existing-spec reattribution",
        "tags": ["design-constraint", "spec-attribution", "platform-vs-application", "containment"],
        "assertions": [
            {
                "id": "DCL-AGENT-RED-CONFORMANT-CONTAINED-APP-001.A1",
                "kind": "behavioral",
                "description": (
                    "Audit identifies specs whose content describes "
                    "platform behavior but whose attribution is "
                    "Agent-Red-specific. Each such spec is reattributed "
                    "via db.update_spec (scope/tags fields)."
                ),
                "verifying_test": "deferred to attribution-audit implementation",
            },
        ],
    },
    # 5. Standing audit for triad completeness + retroactive coverage + Agent-Red-vs-GT-KB attribution
    {
        "id": "GOV-TRIAD-COMPLETENESS-AUDIT-001",
        "type": "governance",
        "title": "Standing audit of spec/test/implementation triad completeness",
        "description": (
            "Per owner directive 2026-04-29: 'This system must be "
            "mechanically enforced and comprehensive.'\n\n"
            "AUDIT SCOPE (run pre-release-gate; weekly; on-demand): \n"
            "  1. Triad-completeness audit (per DCL-SPEC-TEST-IMPL-TRIAD-"
            "     COMPLETENESS-001): for each spec at status 'implemented' "
            "     or 'verified', verify (a) at least one derived test "
            "     exists, (b) test is in an executed lane, (c) test passes "
            "     in the most recent run.\n"
            "  2. Implementation-without-spec audit (per DCL-RETROACTIVE-"
            "     LINKAGE-OBLIGATION-001): scan source modules in "
            "     groundtruth-kb/, scripts/, .claude/ for behavior NOT "
            "     governed by any spec; report candidates for retroactive "
            "     spec creation.\n"
            "  3. Test-without-spec-citation audit (per DCL-TEST-SPEC-"
            "     DERIVATION via existing rule): scan tests/ + groundtruth-"
            "     kb/tests/ for tests whose docstrings do not cite a spec "
            "     ID; report.\n"
            "  4. Test-not-in-gate audit (per DCL-TEST-IN-GATE proposed in "
            "     comprehensive arch): scan release-candidate gate's "
            "     targeted-test list; identify tests that exist on disk but "
            "     are not run.\n"
            "  5. Attribution audit (per DCL-AGENT-RED-CONFORMANT-CONTAINED-"
            "     APP-001): scan specs for Agent-Red-specific attribution "
            "     vs platform-behavior content; report mismatches.\n"
            "  6. Platform-test-isolation audit (per DCL-GTKB-INDEPENDENT-"
            "     TEST-SUITE-001): scan platform tests for "
            "     Agent-Red-specific imports/paths/fixtures; report.\n\n"
            "OUTPUT: structured report at independent-progress-assessments/"
            "TRIAD-AUDIT-{date}.md OR groundtruth.db audit_runs table. "
            "P0/P1/P2 findings per gap class. Pre-release-gate fails if "
            "any P0 or unwaivered P1 gap.\n\n"
            "REMEDIATION: each gap surfaces in the standing-backlog as a "
            "remediation work item (per DCL-STANDING-BACKLOG-001 already "
            "established). Remediation work uses owner standing "
            "authorization for spec creation."
        ),
        "scope": "GT-KB platform standing governance audit",
        "tags": ["governance", "standing-audit", "triad-completeness", "drift-prevention"],
    },
]


def make_approval_packet(spec: dict) -> dict:
    full_content = json.dumps(
        {"id": spec["id"], "type": spec["type"], "title": spec["title"],
         "description": spec["description"], "tags": spec.get("tags", []),
         "assertions": spec.get("assertions", []), "scope": spec.get("scope", "")},
        indent=2, sort_keys=True,
    )
    sha256 = hashlib.sha256(full_content.encode("utf-8")).hexdigest()
    return {
        "artifact_type": "specification", "artifact_id": spec["id"], "action": "insert",
        "source_ref": "owner_conversation:2026-04-29-S321-triad-completeness-directive",
        "full_content": full_content, "full_content_sha256": sha256,
        "approval_mode": "acknowledge", "presented_to_user": True, "transcript_captured": True,
        "explicit_change_request": "Owner directive 2026-04-29 (S321): retroactive spec/test creation; GT-KB independent test suite; Agent Red as conformant contained app; mechanical enforcement of triad completeness.",
        "changed_by": CHANGED_BY, "change_reason": CHANGE_REASON,
        "approved_by": "owner", "acknowledged_by": "owner",
    }


def main() -> int:
    APPROVAL_DIR.mkdir(parents=True, exist_ok=True)
    api = db.KnowledgeDB(str(DB_PATH))
    timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    inserted = []
    failed = []
    for i, spec in enumerate(SPECS, 1):
        spec_id = spec["id"]
        print(f"[{i}/{len(SPECS)}] {spec_id}")
        packet = make_approval_packet(spec)
        packet_path = APPROVAL_DIR / f"{timestamp}-s321-phase3-{spec_id.lower()}.json"
        packet_path.write_text(json.dumps(packet, indent=2), encoding="utf-8")
        try:
            api.insert_spec(
                id=spec_id, title=spec["title"], status="specified",
                changed_by=CHANGED_BY, change_reason=CHANGE_REASON,
                description=spec.get("description"), type=spec["type"],
                tags=spec.get("tags"), assertions=spec.get("assertions"),
                scope=spec.get("scope"), validate_assertions=False,
            )
            inserted.append(spec_id)
            print(f"      OK")
        except Exception as exc:
            failed.append((spec_id, str(exc)))
            print(f"      FAIL: {type(exc).__name__}: {exc}")
    print(f"\n=== SUMMARY: {len(inserted)}/{len(SPECS)} inserted ===")
    if failed:
        for sid, err in failed:
            print(f"  FAIL {sid}: {err}")
    return 0 if not failed else 1


if __name__ == "__main__":
    sys.exit(main())
