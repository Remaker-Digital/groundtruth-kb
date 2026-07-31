NEW

# Implementation Proposal — WI-4482 Formal-Artifact-Approval Ceremony

bridge_kind: prime_proposal
Document: gtkb-wi4482-formal-artifact-approval
Version: 001
Author: Prime Builder (Cursor, harness E)
Date: 2026-06-30T20:35:00Z

author_identity: prime-builder/cursor/E
author_harness_id: E
author_session_context_id: cursor-pb-s520-wi4482-formal-artifact-approval-20260630
author_model: Cursor Agent
author_model_version: composer-2.5-fast
author_model_configuration: Cursor Prime Builder interactive session

Project Authorization: PAUTH-PROJECT-GTKB-ENVELOPE-OPEN-CLOSE-WI-4482-EXPLICIT-HINT-UMBRELLA
Project: PROJECT-GTKB-ENVELOPE-OPEN-CLOSE-ACTION-REFINEMENT
Work Item: WI-4482

target_paths: [".groundtruth/formal-artifact-approvals/2026-06-30-ADR-EXPLICIT-HINT-CONTEXT-MANAGEMENT-001.json", ".groundtruth/formal-artifact-approvals/2026-06-30-DCL-ACTIVITY-ENVELOPE-INTERCEPTION-001.json", ".groundtruth/formal-artifact-approvals/2026-06-30-wi4482-canonical-terminology-glossary-patch.json", "groundtruth.db", ".claude/rules/canonical-terminology.md"]

implementation_scope: governance | protocol
requires_review: true
requires_verification: true
kb_mutation_in_scope: true

---

## Claim

Sibling thread to `gtkb-wi4482-explicit-hint-context-management-umbrella` (GO at `-002`).
That governance_review GO authorized the four deliverables at scope level; it is NOT
per-artifact owner content approval per `GOV-ARTIFACT-APPROVAL-001` and LO finding F1
on `-002`.

This thread performs the per-artifact approval ceremony for three downstream artifacts:

1. **Narrative glossary patch** — `.claude/rules/canonical-terminology.md` (explicit
   hint, activity envelope, session envelope, init-keyword v3 reconciliation). Draft:
   `.gtkb-state/propose-drafts/wi4482/glossary-canonical-terminology-patch.md`.
2. **`ADR-EXPLICIT-HINT-CONTEXT-MANAGEMENT-001`** (architecture_decision). Draft:
   `.gtkb-state/propose-drafts/wi4482/ADR-EXPLICIT-HINT-CONTEXT-MANAGEMENT-001.md`.
3. **`DCL-ACTIVITY-ENVELOPE-INTERCEPTION-001`** (design_constraint). Draft:
   `.gtkb-state/propose-drafts/wi4482/DCL-ACTIVITY-ENVELOPE-INTERCEPTION-001.md`.

## Specification Links

- `GOV-ARTIFACT-APPROVAL-001`
- `PB-ARTIFACT-APPROVAL-001`
- `ADR-ARTIFACT-FORMALIZATION-GATE-001`
- `DCL-ARTIFACT-APPROVAL-HOOK-001`
- `GOV-FILE-BRIDGE-AUTHORITY-001`
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001`
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`
- `GOV-STANDING-BACKLOG-001`
- `bridge/gtkb-wi4482-explicit-hint-context-management-umbrella-001.md`
- `bridge/gtkb-wi4482-explicit-hint-context-management-umbrella-002.md` (parent GO)

## Prior Deliberations

- `DELIB-20260612-EXPLICIT-HINT-LAYER-DECISION-SET`
- `DELIB-20260621-EXPLICIT-HINT-CONTEXT-LOAD-REFRAME`
- `DELIB-20265287`
- `DELIB-20260648` (init-keyword v3)
- `DELIB-20260637` (topic → activity rename lineage)

## Owner Decisions / Input

Authorized by `PAUTH-PROJECT-GTKB-ENVELOPE-OPEN-CLOSE-WI-4482-EXPLICIT-HINT-UMBRELLA`
and parent GO at `bridge/gtkb-wi4482-explicit-hint-context-management-umbrella-002.md`.

**Per-artifact content approvals are obtained post-GO of this thread** via owner
AskUserQuestion (one artifact per turn): `Approve as drafted` / `Approve with edits` /
`Reject`.

## Requirement Sufficiency

Existing requirements sufficient. Verbatim bodies are drafted in
`.gtkb-state/propose-drafts/wi4482/` and summarized in this proposal.

## Proposed Scope

### IP-1: Present 3 artifact bodies to owner (sequential AUQ)

Order: glossary patch → ADR → DCL (glossary first because ADR/DCL reference terms).

### IP-2: Write 3 approval packets

- `.groundtruth/formal-artifact-approvals/2026-06-30-wi4482-canonical-terminology-glossary-patch.json` (narrative; targets glossary patch)
- `.groundtruth/formal-artifact-approvals/2026-06-30-ADR-EXPLICIT-HINT-CONTEXT-MANAGEMENT-001.json`
- `.groundtruth/formal-artifact-approvals/2026-06-30-DCL-ACTIVITY-ENVELOPE-INTERCEPTION-001.json`

Each packet: `presented_to_user=true`, `transcript_captured=true`, matching
`full_content_sha256`, owner `explicit_change_request` from AUQ.

Generate via `gt generate-approval-packet` where applicable; validate via
`python scripts/validate_formal_artifact_packet.py`.

### IP-3: Apply approved artifacts

- Insert ADR + DCL MemBase rows with `GTKB_FORMAL_APPROVAL_PACKET` set.
- Apply glossary patch to `.claude/rules/canonical-terminology.md` with
  `GTKB_NARRATIVE_ARTIFACT_APPROVAL_PACKET` set.
- Mirror detail additions to `groundtruth-kb/docs/reference/canonical-terminology-detail.md`
  when the glossary patch references detail entries.

### IP-4: Verification

- `python -m pytest platform_tests/scripts/test_check_canonical_terminology_doctor_integration.py -q --tb=short`
- Doctor canonical-terminology check passes with new terms.
- Bridge preflights on this thread.

## Specification-Derived Verification Plan

| Check | Command | Expected |
|-------|---------|----------|
| Packet schema | `python scripts/validate_formal_artifact_packet.py <each-packet>` | exit 0 |
| Doctor integration | `python -m pytest platform_tests/scripts/test_check_canonical_terminology_doctor_integration.py -q` | PASS |
| Applicability | `python scripts/bridge_applicability_preflight.py --bridge-id gtkb-wi4482-formal-artifact-approval` | preflight_passed |
| Clause gate | `python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-wi4482-formal-artifact-approval` | exit 0 |

## Risk / Rollback

Per-artifact rollback: revert individual MemBase insert + glossary diff; packets remain
append-only audit evidence.

## Recommended Commit Type

docs — governance artifact inserts and glossary narrative updates only.

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
