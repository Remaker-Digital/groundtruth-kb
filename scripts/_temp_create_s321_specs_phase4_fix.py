#!/usr/bin/env python3
"""Phase 4 fix: correct LO-authority framing in DCL + working DA insertion.

Per owner clarification 2026-04-29 (S321):
  "'LO gets explicit authority to reject specs' - LO should get the authority
  to request owner approval/rejection of the spec."

LO does NOT unilaterally reject; LO REQUESTS owner re-authorization.
Owner makes the final decision.

Also fixes API call signatures: insert_deliberation requires id +
changed_by + change_reason as positional args.
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

# === Step 1: update DCL-SPEC-DA-CITATION-MANDATORY-001 with corrected LO-authority framing ===

CORRECTED_DESCRIPTION = (
    "Per owner directive 2026-04-29 (clarified): 'Loyal Opposition has the "
    "authority to request owner approval/rejection of specs that are unclear "
    "or unsupported by the Deliberation Archive. The Deliberation Archive "
    "must capture the user input that is cited as the origination of any "
    "specification. Requirement specifications (specifications) that are "
    "unsupported by the deliberation archive citation are subject to re-"
    "authorization by the user at the discretion of Loyal Opposition.'\n\n"
    "INVARIANT: every specification (SPEC, GOV, ADR, DCL, PB, REQ) MUST "
    "have at least one linked Deliberation Archive entry that captures the "
    "originating user input (verbatim quote OR explicit reference to the "
    "chat/conversation turn that generated the spec). The link is via the "
    "deliberation_specs join table.\n\n"
    "LO AUTHORITY (clarified): Loyal Opposition reviewers have the authority "
    "to REQUEST owner re-authorization for any spec or any bridge proposal "
    "citing a spec where the DA backing is missing, unclear, or "
    "insufficient. LO does NOT have unilateral rejection authority for "
    "specs; the owner makes the final approve/retain/reject decision when "
    "LO surfaces a re-authorization request. LO's request is recorded as a "
    "deliberation entry; the owner's response is recorded as a follow-up "
    "deliberation entry with outcome={owner_decision: re-authorized, "
    "owner_decision: retracted, owner_decision: amended}.\n\n"
    "RETROACTIVE OBLIGATION: pre-S321 specs without DA backing are subject "
    "to retroactive DA entry creation per DCL-RETROACTIVE-LINKAGE-"
    "OBLIGATION-001. The triad audit (GOV-TRIAD-COMPLETENESS-AUDIT-001) "
    "extends to include DA-citation completeness as a 7th audit class.\n\n"
    "MECHANICAL ENFORCEMENT: spec creation via db.insert_spec() MUST be "
    "paired with at least one db.insert_deliberation() call that captures "
    "the originating user input. The pairing is enforced via the formal-"
    "artifact-approval-gate.py hook (existing) extended to verify DA "
    "pairing for spec inserts."
)

# === Step 2: corrected DA entries for the 11 owner directives ===

OWNER_DIRECTIVES = {
    "spec_creation_standing_auth": (
        "I authorize you to create all necessary specifications. The creation "
        "of specifications from my input is *always* allowed. You *never* "
        "need my permission to create a specification, and you *never* "
        "propose an implementation that is not specified."
    ),
    "impl_proposal_spec_linkage": (
        "It must *not* be possible to submit an implementation proposal that "
        "is not linked to any and all relevant specifications. This is an "
        "*essential* part of any and all implementation proposals."
    ),
    "verified_spec_derived_testing": (
        "It must *not* be possible to VERIFY an implementation without "
        "testing each relevant specification against the implementation. The "
        "verification procedure *must* include creation and execution of "
        "tests derived from the specifications linked in the implementation "
        "proposal."
    ),
    "default_workspace_gtkb": (
        "We are *always* working on the GT-KB platform *except* when I "
        "explicitly state that we are not. When I state that we are not "
        "working on GT-KB, the AI agent *must* interrogate me until I state "
        "that we are working on the hosted application."
    ),
    "platform_app_non_specific": (
        "all work on the GT-KB project must be implemented in a fashion that is application non-specific."
    ),
    "strict_mechanical_enforcement": ("We need *STRICT MECHANICAL ENFORCEMENT* of these directives."),
    "smart_poller_auto_trigger": (
        "the requirement has always been for the AI harness to be "
        "automatically triggered by notification without user intervention, "
        "and only in cases where there is work waiting to be done. This is "
        "not negotiable and any implementation which requires user "
        "intervention is a fail."
    ),
    "platform_failure_diagnosis": (
        "IF this happens to a GT-KB user they will consider this a failure "
        "of the platform. We need a deep diagnosis and comprehensive fix "
        "proposed for the GT-KB system which will catch and correct all "
        "omissions like this in the future."
    ),
    "audit_artifacts_for_ambiguity": (
        "We need to carefully inspect all artifacts in this entire project "
        "to remove all ambiguity or confusion about the project."
    ),
    "triad_completeness": (
        "Retroactively create specifications which cover past approved and "
        "verified implementations which have not been explicitly linked to "
        "specifications. If tests have not been created for those "
        "specifications, create new tests. GT-KB must have a test suite "
        "that is independent of the application test suites. We must fill "
        "in all gaps in specifications, tests and implementation. The "
        "completeness of the spec/test/implementation triad is essential "
        "to the GT-KB knowledge architecture and must be mechanically "
        "enforced and comprehensive."
    ),
    "da_citation_mandatory": (
        "Loyal Opposition has the authority to request owner approval/"
        "rejection of specs that are unclear or are unsupported by the "
        "Deliberation Archive. The Deliberation Archive must capture the "
        "user input that is cited as the origination of any specification."
    ),
}

SPEC_TO_DIRECTIVES = {
    "GOV-SPEC-CREATION-STANDING-AUTHORIZATION-001": ["spec_creation_standing_auth"],
    "DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001": [
        "impl_proposal_spec_linkage",
        "strict_mechanical_enforcement",
    ],
    "DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001": [
        "verified_spec_derived_testing",
        "strict_mechanical_enforcement",
    ],
    "DCL-DEFAULT-WORKSPACE-IS-GT-KB-001": ["default_workspace_gtkb"],
    "DCL-WORKSPACE-EXCEPTION-INTERROGATION-001": ["default_workspace_gtkb"],
    "DCL-WORKSPACE-INFERENCE-PROHIBITED-001": ["default_workspace_gtkb", "strict_mechanical_enforcement"],
    "GOV-ARTIFACT-AMBIGUITY-AUDIT-001": ["audit_artifacts_for_ambiguity"],
    "DCL-PLATFORM-APPLICATION-NON-SPECIFICITY-001": ["platform_app_non_specific"],
    "DCL-MECHANICAL-ENFORCEMENT-MANDATORY-001": ["strict_mechanical_enforcement"],
    "ADR-DEFAULT-GT-KB-EXCEPTION-HOSTED-APP-001": ["default_workspace_gtkb"],
    "ADR-SMART-POLLER-OWNER-OUT-OF-LOOP-001": ["smart_poller_auto_trigger"],
    "DCL-SMART-POLLER-AUTO-TRIGGER-001": ["smart_poller_auto_trigger"],
    "PB-INCIDENT-S321-DAEMON-DISPATCH-DISABLED-001": ["smart_poller_auto_trigger"],
    "PB-INCIDENT-S321-PROPOSAL-WITHOUT-SPEC-LINKAGE-001": ["impl_proposal_spec_linkage", "platform_failure_diagnosis"],
    "DCL-SPEC-RELEVANCE-CLOSURE-001": ["impl_proposal_spec_linkage"],
    "DCL-VERIFIED-BRIDGE-HISTORY-001": ["verified_spec_derived_testing"],
    "DCL-CROSS-HARNESS-ENFORCEMENT-001": ["impl_proposal_spec_linkage", "strict_mechanical_enforcement"],
    "ADR-SPEC-COVERAGE-ARCHITECTURE-001": ["platform_failure_diagnosis"],
    "DCL-SPEC-TEST-IMPL-TRIAD-COMPLETENESS-001": ["triad_completeness"],
    "DCL-RETROACTIVE-LINKAGE-OBLIGATION-001": ["triad_completeness"],
    "DCL-GTKB-INDEPENDENT-TEST-SUITE-001": ["triad_completeness"],
    "DCL-AGENT-RED-CONFORMANT-CONTAINED-APP-001": ["triad_completeness"],
    "GOV-TRIAD-COMPLETENESS-AUDIT-001": ["triad_completeness", "strict_mechanical_enforcement"],
    "DCL-SPEC-DA-CITATION-MANDATORY-001": ["da_citation_mandatory"],
}


def main() -> int:
    api = db.KnowledgeDB(str(DB_PATH))

    # Step 1: update DCL-SPEC-DA-CITATION-MANDATORY-001 with corrected LO-authority framing
    print("=== Step 1: update DCL-SPEC-DA-CITATION-MANDATORY-001 (LO-authority clarification) ===")
    try:
        api.update_spec(
            id="DCL-SPEC-DA-CITATION-MANDATORY-001",
            changed_by=CHANGED_BY,
            change_reason="Owner clarification 2026-04-29: LO has authority to REQUEST owner re-authorization, not to unilaterally reject specs. Owner makes the final decision.",
            description=CORRECTED_DESCRIPTION,
            validate_assertions=False,
        )
        print("  OK updated")
    except Exception as exc:
        print(f"  FAIL: {type(exc).__name__}: {exc}")
        return 1

    # Step 2: insert DA entries for each owner directive
    print("\n=== Step 2: insert DA entries (with all required args) ===")
    delib_id_by_key: dict[str, str] = {}
    for i, (key, quote) in enumerate(OWNER_DIRECTIVES.items(), 1):
        delib_id = f"DELIB-S321-{key.upper().replace('_', '-')}"
        title = f"S321 owner directive: {key.replace('_', ' ')}"
        summary = quote[:200]
        try:
            result = api.insert_deliberation(
                id=delib_id,
                source_type="owner_conversation",
                title=title,
                summary=summary,
                content=quote,
                changed_by=CHANGED_BY,
                change_reason=f"Capture S321 owner directive '{key}' as DA entry per DCL-SPEC-DA-CITATION-MANDATORY-001.",
                source_ref=f"owner_conversation:2026-04-29-S321-{key}",
                outcome="owner_decision",
                session_id="S321",
            )
            actual_id = result.get("id") if isinstance(result, dict) else delib_id
            delib_id_by_key[key] = actual_id
            print(f"  [{i:2d}/{len(OWNER_DIRECTIVES)}] OK {actual_id}")
        except Exception as exc:
            err = f"{type(exc).__name__}: {exc}"
            print(f"  [{i:2d}/{len(OWNER_DIRECTIVES)}] FAIL {key}: {err}")

    # Step 3: link each spec to its originating deliberation(s)
    print("\n=== Step 3: link specs to DA entries ===")
    linked = 0
    failed = []
    for spec_id, directive_keys in SPEC_TO_DIRECTIVES.items():
        for directive_key in directive_keys:
            delib_id = delib_id_by_key.get(directive_key)
            if not delib_id:
                failed.append((spec_id, directive_key, "directive not in DA index"))
                continue
            try:
                api.link_deliberation_spec(
                    deliberation_id=delib_id,
                    spec_id=spec_id,
                    role="originating",
                )
                linked += 1
            except Exception as exc:
                failed.append((spec_id, directive_key, f"{type(exc).__name__}: {exc}"))

    total_links = sum(len(v) for v in SPEC_TO_DIRECTIVES.values())
    print(f"  Linked: {linked}/{total_links}")
    if failed:
        print("  First 5 failures:")
        for sid, key, err in failed[:5]:
            print(f"    {sid} -> {key}: {err}")

    print("\n=== SUMMARY ===")
    print(f"  Spec updated: 1 (DCL-SPEC-DA-CITATION-MANDATORY-001 LO-authority clarified)")
    print(f"  DA entries inserted: {len(delib_id_by_key)}/{len(OWNER_DIRECTIVES)}")
    print(f"  Spec-to-DA links created: {linked}/{total_links}")
    return 0 if linked == total_links and len(delib_id_by_key) == len(OWNER_DIRECTIVES) else 1


if __name__ == "__main__":
    sys.exit(main())
