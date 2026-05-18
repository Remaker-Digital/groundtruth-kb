REVISED

# Implementation Proposal - W3 GOV-REQUIREMENTS-COLLECTION-HOOK-001 Title Fix (GTKB-GOVERNANCE-CORRECTION-S358-W3)

bridge_kind: implementation_proposal
Document: gtkb-s358-w3-requirements-collection-hook-title-fix
Version: 005
Author: Prime Builder (Claude, harness B)
Date: 2026-05-18 UTC
Session: S358

Project Authorization: PAUTH-PROJECT-GTKB-GOVERNANCE-CORRECTION-S358-S358-COMBINED-GOVERNANCE-CORRECTION-PROJECT-AUTHORIZATION
Project: PROJECT-GTKB-GOVERNANCE-CORRECTION-S358
Work Item: WI-3367

target_paths: ["groundtruth.db", ".groundtruth/formal-artifact-approvals/*-gov-requirements-collection-hook-001.json"]

## Revision Note

Version 005 (REVISED) supersedes the `-004` NO-GO. The `-004` review confirmed the `-003` target_paths fix is correct - `groundtruth.db` plus the formal-artifact approval-packet glob - and that both mandatory preflights pass. It raised one finding:

- FINDING-F1 (P1): the `-003` Prior Deliberations section cited `DELIB-S332-NO-LLM-API-PARALLEL-USE-DIRECTIVE`, but a direct MemBase lookup shows that DELIB id does not exist. The id was carried over from the `.claude/hooks/spec-classifier.py` header, which itself carries that nonexistent citation as pre-existing drift. A bridge proposal must not carry an unretrievable DELIB id as decision evidence.

This revision fixes F1. The Prior Deliberations section drops the nonexistent `DELIB-S332-NO-LLM-API-PARALLEL-USE-DIRECTIVE` citation and cites only records confirmed retrievable in MemBase: `DELIB-S358-GOVERNANCE-CORRECTION-PROJECT-AUTHORIZATION`, `DELIB-S330-REQUIREMENTS-COLLECTION-HOOK-WITH-3-OPTION-CLARIFICATION` (the deliberation recording the LLM-classifier / retrieval-augmented design later superseded by the regex-gate pivot), and `DELIB-1701` (the verified Loyal Opposition GO for the requirements-collection hook, recording the no-LLM regex-gate direction). The Problem section's reference to the S332 cost directive is re-sourced to the GOV-REQUIREMENTS-COLLECTION-HOOK-001 v3 body's amendment note, where that directive is actually recorded - no DELIB id is asserted for it. The `-003` target_paths fix (`groundtruth.db` + the approval-packet glob), the title-only IP-1 scope, the Specification Links, the Owner Decisions / Input section, and the field-level verification plan are otherwise unchanged.

## Problem

GOV-REQUIREMENTS-COLLECTION-HOOK-001 is at version 3, status verified. Its title still reads:

`A UserPromptSubmit hook MUST classify each owner message and force 3-option clarification when a requirement candidate is detected (LLM classification + retrieval-augmented options)`

The trailing parenthetical, "(LLM classification + retrieval-augmented options)", advertises a design that was abandoned. The v1 of this spec mandated a lightweight LLM classifier with retrieval-augmented options. Per the cost directive recorded in the GOV-REQUIREMENTS-COLLECTION-HOOK-001 v3 body's amendment note ("We will not add an API key for parallel API usage. That incurs an unacceptable additional cost."), the LLM-classifier requirement was removed in v2. The v3 body is already fully correct: it mandates a fixed regex pattern set for detection and explicitly forbids external API calls ("The hook MUST detect canonical specification-language triggers using a fixed set of regex patterns"; "The hook MUST NOT make external API calls (no LLM, no retrieval-augmented options)"). The implementation is also correct: `.claude/hooks/spec-classifier.py` is a deterministic regex classifier - its only imports are json, re, and sys; there is no LLM, retrieval, or HTTP client, and its module docstring states "The hook is a regex gate, not an LLM classifier."

Only the title lags. This is the W3 surface of the S358 drift-closure sweep: a correction that landed on the spec body and the implementation but not on the spec's own title metadata. The stale title misrepresents a verified governance spec - a reader scanning titles sees an LLM/retrieval mandate that the body forbids and the implementation does not contain.

## Claim

Issue a version 4 of GOV-REQUIREMENTS-COLLECTION-HOOK-001 that corrects only the title field, dropping the abandoned-design parenthetical. The v4 title is the v3 title with " (LLM classification + retrieval-augmented options)" removed:

`A UserPromptSubmit hook MUST classify each owner message and force 3-option clarification when a requirement candidate is detected`

v4 changes only the title. The v3 body, assertions, and every other field are carried forward unchanged. The behavioral rule is not touched - it is already correct and verified. v3 stays on the append-only record. No source, hook, configuration, or test changes: `.claude/hooks/spec-classifier.py` already implements the v3 body correctly, and W3 makes the title match the already-correct body and implementation.

## In-Root Placement Evidence

W3's only write is one MemBase GOV-spec version-4 record in groundtruth.db and its one formal-artifact-approval packet under .groundtruth/formal-artifact-approvals/. Both groundtruth.db and the approval-packet directory are in-root under the GT-KB project root, and both are declared in target_paths. This bridge proposal file resides under the bridge directory. No application path under applications/ is touched.

## Specification Links

- GOV-REQUIREMENTS-COLLECTION-HOOK-001 - the target spec; W3 issues its v4. Cited as the artifact being corrected.
- SPEC-AUQ-NO-LLM-CLASSIFIER-001 - the deterministic-only, no-LLM-classifier requirement. W3's correction removes the last artifact surface (the title) that still advertised the abandoned LLM-classifier design; the correction aligns the spec's title with this requirement.
- SPEC-AUQ-POLICY-ENGINE-001 - the spec-classifier hook participates in the deterministic AUQ policy engine; the title correction keeps the spec's metadata consistent with the deterministic engine the implementation already realizes.
- GOV-FILE-BRIDGE-AUTHORITY-001 - the bridge index and verdict files are canonical workflow state; this proposal is filed and reviewed through that workflow.
- DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001 - this proposal carries a complete, relevance-closed Specification Links section and, per the -002 NO-GO, declares the groundtruth.db MemBase mutation surface in target_paths.
- DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001 - the post-implementation report will carry a spec-to-verification mapping with executed evidence (the v4 row inspected: title corrected, body unchanged from v3).
- GOV-ARTIFACT-APPROVAL-001 - the GOV v4 record is a formal artifact; the MemBase supersession is gated by a formal-artifact-approval packet presented to and approved by the owner before insertion.
- PB-ARTIFACT-APPROVAL-001 - the protected-artifact approval discipline applies to the GOV v4 supersession.
- DCL-ARTIFACT-APPROVAL-HOOK-001 - the formal-artifact-approval gate hook enforces the packet requirement on the GOV v4 insert.
- DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001 - this proposal carries the mandatory Project Authorization, Project, and Work Item header lines.
- ADR-ISOLATION-APPLICATION-PLACEMENT-001 - the write targets are in-root; no application path is touched.
- GOV-ARTIFACT-ORIENTED-GOVERNANCE-001 - the correction is preserved as durable artifacts: WI-3367, this proposal, the GOV v4 record, the approval packet, and the post-implementation report.
- ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001 - the fix preserves traceability across the work item, proposal, the v3-to-v4 supersession chain, and the report.
- DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001 - WI-3367 moves through open, in-progress, and verified lifecycle states; the spec moves from v3 to v4.

## Prior Deliberations

A Deliberation Archive search was performed for the requirements-collection hook and the LLM-classifier-abandonment history. Each DELIB id cited below was confirmed retrievable in MemBase.

- DELIB-S358-GOVERNANCE-CORRECTION-PROJECT-AUTHORIZATION - the owner-decision deliberation (S358, owner_conversation) authorizing the combined governance-correction project. It records the W3 scope: a metadata-only v4 dropping the abandoned "LLM classification + retrieval-augmented options" phrase from the title, with the body and implementation already correct. This proposal implements the W3 workstream.
- DELIB-S330-REQUIREMENTS-COLLECTION-HOOK-WITH-3-OPTION-CLARIFICATION - the deliberation recording the earlier LLM-classifier and retrieval-augmented-option design for the requirements-collection hook, the design later superseded by the regex-gate pivot. It is the retrievable record of the design whose last title-level remnant W3 removes.
- DELIB-1701 - the verified Loyal Opposition GO for the requirements-collection hook revised proposal; it records that the owner-decision evidence supported the no-LLM regex-gate direction. It confirms that the regex-gate mandate now in the v3 body is the verified, owner-supported direction the v4 title must match.

The prior NO-GO at this thread's `-004` found that the `-003` Prior Deliberations section cited `DELIB-S332-NO-LLM-API-PARALLEL-USE-DIRECTIVE`, a DELIB id that does not exist in MemBase; `-005` removes that citation and cites only the retrievable records above. No prior deliberation rejected the W3 title correction; W3 completes the regex-gate pivot by aligning the spec's title with the already-corrected v3 body and the already-correct implementation.

## Owner Decisions / Input

- 2026-05-17, S358: the owner directed standing up and running the combined four-workstream governance-correction project; W3 is the GOV-REQUIREMENTS-COLLECTION-HOOK-001 title-fix workstream, with the explicit instruction that v4 is metadata-only and changes only the title (the body and implementation are already correct). Captured in DELIB-S358-GOVERNANCE-CORRECTION-PROJECT-AUTHORIZATION (source_type=owner_conversation, outcome=owner_decision).
- Implementation-time owner approval is still required: the GOV v4 supersession is a formal-artifact mutation requiring a formal-artifact-approval packet presented to and approved by the owner before insertion, with the exact v4 title and the carried-forward v3 body in the packet. This GO authorizes the workstream; it does not pre-grant the per-artifact approval.

## Requirement Sufficiency

Existing requirements sufficient. W3 corrects stale title metadata only. The behavioral rule - the v3 body's regex-detection mandate and external-API prohibition - is unchanged and is carried forward verbatim into v4. No new or revised behavioral requirement is created; the v4 record exists solely to make the title field consistent with the already-correct body and implementation. No new or revised requirement is needed before implementation.

## Clause Scope Clarification (Not a Bulk Operation)

This proposal is not a bulk standing-backlog operation. It is a single-field metadata correction tracked by exactly one work item, WI-3367, an active member of PROJECT-GTKB-GOVERNANCE-CORRECTION-S358. No work-item state inventory, bulk transition, or backlog cleanup is performed. The proposal references the words "requirement", "work item", and "backlog" only to identify WI-3367, to name the spec being corrected (the requirements-collection hook), and to describe the spec lifecycle. The v4 supersession is a single formal-artifact change carrying its own formal-artifact-approval packet.

## Bridge INDEX Update Evidence

A REVISED entry for gtkb-s358-w3-requirements-collection-hook-title-fix pointing at this -005 file is inserted at the top of that document's version list in the bridge index, above the NO-GO: -004, REVISED: -003, NO-GO: -002, and NEW: -001 lines. No prior bridge file and no prior index entry is deleted or rewritten; -001 through -004 remain on disk and in the index as the append-only audit trail.

## Proposed Scope

### IP-1: Issue v4 of GOV-REQUIREMENTS-COLLECTION-HOOK-001 with the corrected title

Insert a version 4 of GOV-REQUIREMENTS-COLLECTION-HOOK-001 into MemBase (groundtruth.db) whose title is the v3 title with the trailing " (LLM classification + retrieval-augmented options)" removed. The v4 title is exactly:

`A UserPromptSubmit hook MUST classify each owner message and force 3-option clarification when a requirement candidate is detected`

Every other field - the description/body, assertions, type, status, and all remaining metadata - is carried forward from v3 unchanged. v3 stays on the append-only record. The v4 insertion carries a formal-artifact-approval packet whose full content is the v4 record (corrected title plus the carried-forward v3 body), owner-approved before insertion.

### Out of scope

W3 does not change the v3 behavioral rule, the v3 body, or any assertion. It does not modify `.claude/hooks/spec-classifier.py` (already a correct deterministic regex gate) or any other source, hook, configuration, or test. It does not rewrite v1, v2, or v3 (append-only). It does not touch the W1, W2, or W4 surfaces. The v4 insert is a MemBase mutation to groundtruth.db through the formal-artifact-approval workflow; groundtruth.db and the single approval-packet glob are declared in target_paths.

## Specification-Derived Verification Plan

| Specification | Behavior verified | Test or verification |
|---|---|---|
| GOV-REQUIREMENTS-COLLECTION-HOOK-001 | A v4 record exists; its title is the v3 title minus the "(LLM classification + retrieval-augmented options)" parenthetical; the v4 body equals the v3 body byte-for-byte; v3 is preserved | MemBase query inspection comparing the v4 and v3 title and body fields, recorded in the post-implementation report |
| SPEC-AUQ-NO-LLM-CLASSIFIER-001 | The corrected v4 title no longer advertises an LLM-classifier or retrieval-augmented design | inspection of the v4 title, recorded in the report |
| GOV-ARTIFACT-APPROVAL-001 | The GOV v4 supersession carries a formal-artifact-approval packet with presented_to_user true and a matching content hash | the approval packet, cited by path in the report |
| DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001 | The post-implementation report carries this mapping with executed verification evidence | the post-implementation report |

Execution: the post-implementation report records the exact MemBase query confirming the v4 row, a field-level comparison showing the title changed and the body unchanged from v3, the preserved v3 row, and the approval-packet path. W3 changes no code, so there is no pytest or ruff step; verification is structural inspection of the MemBase records, the inspection-based verification model accepted for the S358 W5 narrative-correction workstream.

## Acceptance Criteria

- A v4 record of GOV-REQUIREMENTS-COLLECTION-HOOK-001 exists in MemBase.
- The v4 title is exactly the v3 title with " (LLM classification + retrieval-augmented options)" removed and nothing else changed.
- The v4 body and all non-title fields equal v3 byte-for-byte.
- v3 is preserved on the append-only record.
- The v4 supersession carries a formal-artifact-approval packet.
- Both bridge preflights pass on the post-implementation report.

## Option Rationale

Issuing a v4 was the owner directive (WI-3367, DELIB-S358) and was selected over two alternatives. Editing the v3 title in place was rejected: GT-KB specs are append-only versioned; v3 is the record of the spec as it stood, and the title correction is itself a versioned change. Leaving the title and relying on the correct body was rejected: a spec title is a primary scanning surface, and a verified governance spec whose title advertises a forbidden design is an active misrepresentation that a reader hits before the body. A metadata-only v4 is the minimal correction: it touches exactly the one stale field and carries everything else forward. For the -002 NO-GO F1, adding groundtruth.db to target_paths was the direct fix the verdict prescribed; the approval-packet glob is retained. For the -004 NO-GO F1, the nonexistent DELIB citation was replaced with retrievable records (each confirmed by direct MemBase lookup) rather than capturing a new DELIB for the S332 cost directive: that directive is already durably recorded in the GOV-REQUIREMENTS-COLLECTION-HOOK-001 v3 body's amendment note, so a new DELIB would duplicate an existing record.

## Risks / Rollback

- Risk: the v4 body diverges from v3 during the carry-forward. Mitigation: the acceptance criteria require a byte-for-byte body comparison; the approval packet's full content is inspected against v3 before insertion.
- Risk: the v4 title is over-corrected (more than the parenthetical removed). Mitigation: the proposal states the exact v4 title verbatim; the acceptance criteria require exactly the parenthetical removed and nothing else.
- Rollback: a GOV-spec supersession is an append-only versioned MemBase mutation reversible by a further versioned correction.

## Recommended Commit Type

`docs` - W3's deliverable is one governance-specification version-4 metadata correction in MemBase, with no code, test, or capability-surface change. The post-implementation report will carry the recommended type matching the final change set per the Conventional Commits Type Discipline.

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
