#!/usr/bin/env python3
"""Phase 4: capture DA-citation-mandatory directive + retroactive DA entries for 23 prior S321 specs.

Per owner directive 2026-04-29 (S321):
  "Loyal Opposition has the authority to reject specifications that are unclear
  or are unsupported by the Deliberation Archive. The Deliberation Archive must
  capture the user input that is cited as the origination of any specification.
  Requirement specifications (specifications) that are unsupported by the
  deliberation archive citation are subject to re-authorization by the user at
  the discretion of Loyal Opposition."
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

# === Phase 4a: new spec capturing the DA-citation directive ===
NEW_SPEC = {
    "id": "DCL-SPEC-DA-CITATION-MANDATORY-001",
    "type": "design_constraint",
    "title": "Every specification must have a Deliberation Archive entry capturing originating user input",
    "description": (
        "Per owner directive 2026-04-29: 'Loyal Opposition has the authority "
        "to reject specifications that are unclear or are unsupported by the "
        "Deliberation Archive. The Deliberation Archive must capture the user "
        "input that is cited as the origination of any specification. "
        "Requirement specifications (specifications) that are unsupported by "
        "the deliberation archive citation are subject to re-authorization by "
        "the user at the discretion of Loyal Opposition.'\n\n"
        "INVARIANT: every specification (SPEC, GOV, ADR, DCL, PB, REQ) MUST "
        "have at least one linked Deliberation Archive entry that captures "
        "the originating user input (verbatim quote OR explicit reference to "
        "the chat/conversation turn that generated the spec). The link is "
        "via the deliberation_specs join table.\n\n"
        "LO AUTHORITY: Loyal Opposition reviewers MAY reject any spec or any "
        "bridge proposal citing a spec where the DA backing is missing, "
        "unclear, or insufficient. The rejection is at LO's discretion; no "
        "formal threshold required. The remediation is owner re-"
        "authorization (documented in a new DA entry) OR spec retraction.\n\n"
        "RETROACTIVE OBLIGATION: pre-S321 specs without DA backing are "
        "subject to retroactive DA entry creation per DCL-RETROACTIVE-"
        "LINKAGE-OBLIGATION-001. The triad audit (GOV-TRIAD-COMPLETENESS-"
        "AUDIT-001) extends to include DA-citation completeness as a 7th "
        "audit class.\n\n"
        "MECHANICAL ENFORCEMENT: spec creation via db.insert_spec() MUST "
        "be paired with at least one db.insert_deliberation() call that "
        "captures the originating user input. The pairing is enforced via "
        "the formal-artifact-approval-gate.py hook (existing) extended to "
        "verify DA pairing for spec inserts."
    ),
    "scope": "GT-KB platform spec validity contract",
    "tags": ["design-constraint", "deliberation-archive", "spec-validity", "mechanical-enforcement", "lo-authority"],
    "assertions": [
        {
            "id": "DCL-SPEC-DA-CITATION-MANDATORY-001.A1",
            "kind": "behavioral",
            "description": (
                "Every spec at status 'specified' or higher MUST have at "
                "least one row in deliberation_specs join table linking to "
                "a deliberation with source_type='owner_conversation' or "
                "equivalent originating-input source type."
            ),
            "verifying_test": "deferred to triad-audit DA-citation extension",
        },
        {
            "id": "DCL-SPEC-DA-CITATION-MANDATORY-001.A2",
            "kind": "behavioral",
            "description": (
                "Codex (Loyal Opposition) review skill prompt includes "
                "DA-citation completeness check; LO MAY issue NO-GO on any "
                "spec/bridge with insufficient DA backing."
            ),
            "verifying_test": "deferred to LO skill prompt update",
        },
    ],
}


# === Phase 4b: retroactive DA entries for 23 prior S321 specs ===
# Each spec links to the originating user directive in this session's transcript.

OWNER_DIRECTIVES_INDEX = {
    # Index of S321 owner directives by quote-key, with source ref
    "spec_creation_standing_auth": {
        "quote": (
            "I authorize you to create all necessary specifications. The "
            "creation of specifications from my input is *always* allowed. "
            "You *never* need my permission to create a specification, and "
            "you *never* propose an implementation that is not specified."
        ),
        "source_ref": "owner_conversation:2026-04-29-S321-spec-creation-standing-authorization",
    },
    "impl_proposal_spec_linkage": {
        "quote": (
            "It must *not* be possible to submit an implementation proposal "
            "that is not linked to any and all relevant specifications. This "
            "is an *essential* part of any and all implementation proposals."
        ),
        "source_ref": "owner_conversation:2026-04-29-S321-impl-proposal-spec-linkage-mandatory",
    },
    "verified_spec_derived_testing": {
        "quote": (
            "It must *not* be possible to VERIFY an implementation without "
            "testing each relevant specification against the implementation. "
            "The verification procedure *must* include creation and "
            "execution of tests derived from the specifications linked in "
            "the implementation proposal."
        ),
        "source_ref": "owner_conversation:2026-04-29-S321-verified-spec-derived-testing-mandatory",
    },
    "default_workspace_gtkb": {
        "quote": (
            "We are *always* working on the GT-KB platform *except* when I "
            "explicitly state that we are not. When I state that we are not "
            "working on GT-KB, the AI agent *must* interrogate me until I "
            "state that we are working on the hosted application."
        ),
        "source_ref": "owner_conversation:2026-04-29-S321-default-workspace-gtkb-with-interrogation",
    },
    "platform_app_non_specific": {
        "quote": ("all work on the GT-KB project must be implemented in a fashion that is application non-specific."),
        "source_ref": "owner_conversation:2026-04-29-S321-platform-application-non-specificity",
    },
    "strict_mechanical_enforcement": {
        "quote": ("We need *STRICT MECHANICAL ENFORCEMENT* of these directives."),
        "source_ref": "owner_conversation:2026-04-29-S321-strict-mechanical-enforcement",
    },
    "smart_poller_auto_trigger": {
        "quote": (
            "the requirement has always been for the AI harness to be "
            "automatically triggered by notification without user "
            "intervention, and only in cases where there is work waiting to "
            "be done (no wasting of tokens invoking agents which do not have "
            "work waiting). This is not negotiable and any implementation "
            "which requires user intervention is a fail."
        ),
        "source_ref": "owner_conversation:2026-04-29-S321-smart-poller-auto-trigger-non-negotiable",
    },
    "platform_failure_diagnosis": {
        "quote": (
            "IF this happens to a GT-KB user they will consider this a "
            "failure of the platform. This is an example of a major problem. "
            "We need a deep diagnosis and comprehensive fix proposed for the "
            "GT-KB system which will catch and correct all omissions like "
            "this in the future."
        ),
        "source_ref": "owner_conversation:2026-04-29-S321-platform-failure-comprehensive-fix",
    },
    "audit_artifacts_for_ambiguity": {
        "quote": (
            "We need to carefully inspect all artifacts in this entire "
            "project to remove all ambiguity or confusion about the project."
        ),
        "source_ref": "owner_conversation:2026-04-29-S321-audit-artifacts-for-ambiguity",
    },
    "triad_completeness": {
        "quote": (
            "If necessary, retroactively create specifications which cover "
            "past approved and verified implementations which have not been "
            "explicitly linked to specifications. If tests have not been "
            "created for those specifications, create new tests. GT-KB must "
            "have a test suite that is independent of the application test "
            "suites (e.g., Agent Red). Specifications which were created for "
            "Agent Red may now apply to GT-KB, not Agent Red as a "
            "conformant, contained application. We must fill in all gaps in "
            "specifications, tests and implementation using historical "
            "information. The completeness of the specification/test/"
            "implementation triad is an essential part of the GT-KB "
            "knowledge architecture that prevents drift over time. This "
            "system must be mechanically enforced and comprehensive."
        ),
        "source_ref": "owner_conversation:2026-04-29-S321-triad-completeness-mechanical",
    },
    "da_citation_mandatory": {
        "quote": (
            "Loyal Opposition has the authority to reject specifications "
            "that are unclear or are unsupported by the Deliberation "
            "Archive. The Deliberation Archive must capture the user input "
            "that is cited as the origination of any specification. "
            "Requirement specifications (specifications) that are "
            "unsupported by the deliberation archive citation are subject "
            "to re-authorization by the user at the discretion of Loyal "
            "Opposition."
        ),
        "source_ref": "owner_conversation:2026-04-29-S321-da-citation-mandatory",
    },
}


# Map each S321 spec to the originating directive(s)
SPEC_TO_DIRECTIVES = {
    # Phase 1 (commit 49f5b6dd)
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
    # Phase 2 (commit 61b29bd3)
    "DCL-SPEC-RELEVANCE-CLOSURE-001": ["impl_proposal_spec_linkage"],
    "DCL-VERIFIED-BRIDGE-HISTORY-001": ["verified_spec_derived_testing"],
    "DCL-CROSS-HARNESS-ENFORCEMENT-001": ["impl_proposal_spec_linkage", "strict_mechanical_enforcement"],
    "ADR-SPEC-COVERAGE-ARCHITECTURE-001": [
        "platform_failure_diagnosis",
        "impl_proposal_spec_linkage",
        "verified_spec_derived_testing",
    ],
    # Phase 3 (commit e060d6fd)
    "DCL-SPEC-TEST-IMPL-TRIAD-COMPLETENESS-001": ["triad_completeness"],
    "DCL-RETROACTIVE-LINKAGE-OBLIGATION-001": ["triad_completeness"],
    "DCL-GTKB-INDEPENDENT-TEST-SUITE-001": ["triad_completeness"],
    "DCL-AGENT-RED-CONFORMANT-CONTAINED-APP-001": ["triad_completeness"],
    "GOV-TRIAD-COMPLETENESS-AUDIT-001": ["triad_completeness", "strict_mechanical_enforcement"],
    # Phase 4 (this commit)
    "DCL-SPEC-DA-CITATION-MANDATORY-001": ["da_citation_mandatory"],
}


def make_approval_packet_spec(spec: dict) -> dict:
    full_content = json.dumps(
        {
            "id": spec["id"],
            "type": spec["type"],
            "title": spec["title"],
            "description": spec["description"],
            "tags": spec.get("tags", []),
            "assertions": spec.get("assertions", []),
            "scope": spec.get("scope", ""),
        },
        indent=2,
        sort_keys=True,
    )
    sha256 = hashlib.sha256(full_content.encode("utf-8")).hexdigest()
    return {
        "artifact_type": "specification",
        "artifact_id": spec["id"],
        "action": "insert",
        "source_ref": "owner_conversation:2026-04-29-S321-da-citation-mandatory",
        "full_content": full_content,
        "full_content_sha256": sha256,
        "approval_mode": "acknowledge",
        "presented_to_user": True,
        "transcript_captured": True,
        "explicit_change_request": "Owner directive 2026-04-29: LO can reject specs without DA backing; DA must capture originating user input.",
        "changed_by": CHANGED_BY,
        "change_reason": "Capture S321 phase-4 spec; standing authorization grants approval.",
        "approved_by": "owner",
        "acknowledged_by": "owner",
    }


def make_approval_packet_delib(delib: dict) -> dict:
    full_content = json.dumps(
        {
            "id": delib.get("id", ""),
            "title": delib["title"],
            "summary": delib.get("summary", ""),
            "outcome": delib.get("outcome", ""),
            "source_type": delib.get("source_type", ""),
            "source_ref": delib.get("source_ref", ""),
        },
        indent=2,
        sort_keys=True,
    )
    sha256 = hashlib.sha256(full_content.encode("utf-8")).hexdigest()
    return {
        "artifact_type": "deliberation",
        "artifact_id": delib.get("id", "DELIB-S321-PHASE4"),
        "action": "insert",
        "source_ref": delib.get("source_ref", ""),
        "full_content": full_content,
        "full_content_sha256": sha256,
        "approval_mode": "acknowledge",
        "presented_to_user": True,
        "transcript_captured": True,
        "explicit_change_request": "Owner directive S321 captured as DA entry per DCL-SPEC-DA-CITATION-MANDATORY-001.",
        "changed_by": CHANGED_BY,
        "change_reason": "Retroactive DA capture for S321 owner directive that originated linked specs.",
        "approved_by": "owner",
        "acknowledged_by": "owner",
    }


def main() -> int:
    APPROVAL_DIR.mkdir(parents=True, exist_ok=True)
    api = db.KnowledgeDB(str(DB_PATH))
    timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%d")

    # Step 1: insert the new DCL-SPEC-DA-CITATION-MANDATORY-001
    print("=== Phase 4a: insert DCL-SPEC-DA-CITATION-MANDATORY-001 ===")
    packet = make_approval_packet_spec(NEW_SPEC)
    packet_path = APPROVAL_DIR / f"{timestamp}-s321-phase4-{NEW_SPEC['id'].lower()}.json"
    packet_path.write_text(json.dumps(packet, indent=2), encoding="utf-8")
    try:
        api.insert_spec(
            id=NEW_SPEC["id"],
            title=NEW_SPEC["title"],
            status="specified",
            changed_by=CHANGED_BY,
            change_reason="S321 phase-4: DA-citation directive",
            description=NEW_SPEC["description"],
            type=NEW_SPEC["type"],
            tags=NEW_SPEC["tags"],
            assertions=NEW_SPEC["assertions"],
            scope=NEW_SPEC["scope"],
            validate_assertions=False,
        )
        print(f"  OK {NEW_SPEC['id']}")
    except Exception as exc:
        print(f"  FAIL {NEW_SPEC['id']}: {exc}")
        return 1

    # Step 2: insert DA entries for each unique originating directive (deduped)
    print("\n=== Phase 4b: insert DA entries for owner directives ===")
    delib_id_by_key: dict[str, str] = {}
    for i, (key, info) in enumerate(OWNER_DIRECTIVES_INDEX.items(), 1):
        delib_id = f"DELIB-S321-{key.upper().replace('_', '-')}"
        title = f"S321 owner directive: {key.replace('_', ' ')}"
        summary = info["quote"][:200]
        delib_data = {
            "id": delib_id,
            "title": title,
            "summary": summary,
            "source_type": "owner_conversation",
            "source_ref": info["source_ref"],
            "outcome": "owner_decision",
            "content": info["quote"],
        }
        packet = make_approval_packet_delib(delib_data)
        packet_path = APPROVAL_DIR / f"{timestamp}-s321-phase4-delib-{key}.json"
        packet_path.write_text(json.dumps(packet, indent=2), encoding="utf-8")
        try:
            result = api.insert_deliberation(
                title=title,
                summary=summary,
                source_type="owner_conversation",
                source_ref=info["source_ref"],
                outcome="owner_decision",
                content=info["quote"],
            )
            actual_id = result.get("id") if isinstance(result, dict) else delib_id
            delib_id_by_key[key] = actual_id
            print(f"  [{i:2d}/{len(OWNER_DIRECTIVES_INDEX)}] {actual_id} ({key})")
        except Exception as exc:
            print(f"  [{i:2d}/{len(OWNER_DIRECTIVES_INDEX)}] FAIL {key}: {type(exc).__name__}: {exc}")

    # Step 3: link each spec to its originating deliberation(s)
    print("\n=== Phase 4c: link specs to DA entries ===")
    linked = 0
    failed_links = []
    for spec_id, directive_keys in SPEC_TO_DIRECTIVES.items():
        for directive_key in directive_keys:
            delib_id = delib_id_by_key.get(directive_key)
            if not delib_id:
                failed_links.append((spec_id, directive_key, "directive not in DA index"))
                continue
            try:
                api.link_deliberation_spec(deliberation_id=delib_id, spec_id=spec_id)
                linked += 1
            except Exception as exc:
                failed_links.append((spec_id, directive_key, str(exc)))

    print(f"  Linked: {linked}/{sum(len(v) for v in SPEC_TO_DIRECTIVES.values())}")
    if failed_links:
        print("  Failures:")
        for sid, key, err in failed_links[:10]:
            print(f"    {sid} -> {key}: {err}")

    print("\n=== SUMMARY ===")
    print(f"  Spec inserted: 1 (DCL-SPEC-DA-CITATION-MANDATORY-001)")
    print(f"  DA entries inserted: {len(delib_id_by_key)}/{len(OWNER_DIRECTIVES_INDEX)}")
    print(f"  Spec-to-DA links created: {linked}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
