REVISED

# Implementation Proposal - W3 GOV-REQUIREMENTS-COLLECTION-HOOK-001 Title Fix (GTKB-GOVERNANCE-CORRECTION-S358-W3)

bridge_kind: prime_proposal
Document: gtkb-s358-w3-requirements-collection-hook-title-fix
Version: 009
Author: Prime Builder (Claude, harness B)
Date: 2026-05-18 UTC
Session: S358

Project Authorization: PAUTH-PROJECT-GTKB-GOVERNANCE-CORRECTION-S358-S358-COMBINED-GOVERNANCE-CORRECTION-PROJECT-AUTHORIZATION
Project: PROJECT-GTKB-GOVERNANCE-CORRECTION-S358
Work Item: WI-3367

target_paths: ["groundtruth.db", ".groundtruth/formal-artifact-approvals/2026-05-18-GOV-REQUIREMENTS-COLLECTION-HOOK-001-v4.json"]

## Revision Note

Version 009 (REVISED) supersedes the `-008` NO-GO. The `-008` verdict confirmed the W3 implementation is substantively correct: GOV-REQUIREMENTS-COLLECTION-HOOK-001 has an append-only v4 with the corrected title, v3 is preserved, the v4 description hash equals v3 (`7617746664c1ddc25ba6e749767e644be681ff48e79164419c469dc1a9771598`), and the owner-approved formal-artifact-approval packet's `full_content` matches the v4 MemBase description. The sole `-008` blocker was FINDING-F1 (P1): the `-005` proposal's `target_paths` declared the approval-packet glob as `*-gov-requirements-collection-hook-001.json`, but the governed `gt spec update` service deterministically named the packet `2026-05-18-GOV-REQUIREMENTS-COLLECTION-HOOK-001-v4.json`; `implementation_authorization.path_authorized()` returns `False` for that concrete path against the glob, so the actual approval packet fell outside the GO-derived authorization envelope.

`-009` corrects `target_paths` to name the exact approval-packet path `gt spec update` produced, alongside `groundtruth.db`. `fnmatch` of an exact path against itself is unconditionally true, so a Codex GO on `-009` and the re-derived implementation-start authorization packet mechanically cover the actual artifact. The owner selected this revised-proposal-plus-re-GO reconciliation over a target-path waiver via AskUserQuestion (S358).

W3's substantive scope - the metadata-only v4 title fix - is unchanged from `-005`. The v4 record and its approval packet already inserted under the `-006` GO are correct (independently confirmed by the `-008` verdict) and are NOT re-inserted; `-009` corrects only the authorization envelope. After Codex GO on `-009`, Prime Builder regenerates the implementation-start authorization packet from that GO and re-files the post-implementation report citing the corrected scope.

Version 005 (REVISED) superseded the `-004` NO-GO by replacing a nonexistent DELIB citation in the Prior Deliberations section with retrievable Deliberation Archive records. The `-003` target_paths fix (`groundtruth.db` plus the approval-packet glob), the title-only IP-1 scope, the Specification Links, the Owner Decisions / Input section, and the field-level verification plan were unchanged.

## Problem

GOV-REQUIREMENTS-COLLECTION-HOOK-001 was at version 3, status verified. Its title still read:

`A UserPromptSubmit hook MUST classify each owner message and force 3-option clarification when a requirement candidate is detected (LLM classification + retrieval-augmented options)`

The trailing parenthetical, "(LLM classification + retrieval-augmented options)", advertised a design that was abandoned. The v1 of this spec mandated a lightweight LLM classifier with retrieval-augmented options. Per the cost directive recorded in the GOV-REQUIREMENTS-COLLECTION-HOOK-001 v3 body's amendment note ("We will not add an API key for parallel API usage. That incurs an unacceptable additional cost."), the LLM-classifier requirement was removed in v2. The v3 body is already fully correct: it mandates a fixed regex pattern set for detection and explicitly forbids external API calls. The implementation is also correct: `.claude/hooks/spec-classifier.py` is a deterministic regex classifier.

Only the title lagged. This is the W3 surface of the S358 drift-closure sweep: a correction that landed on the spec body and the implementation but not on the spec's own title metadata.

## Claim

Issue a version 4 of GOV-REQUIREMENTS-COLLECTION-HOOK-001 that corrects only the title field, dropping the abandoned-design parenthetical. The v4 title is the v3 title with " (LLM classification + retrieval-augmented options)" removed:

`A UserPromptSubmit hook MUST classify each owner message and force 3-option clarification when a requirement candidate is detected`

v4 changes only the title. The v3 body, assertions, and every other field are carried forward unchanged. v3 stays on the append-only record. No source, hook, configuration, or test changes.

## In-Root Placement Evidence

W3's only write is one MemBase GOV-spec version-4 record in groundtruth.db and its one formal-artifact-approval packet under .groundtruth/formal-artifact-approvals/. Both groundtruth.db and the approval-packet directory are in-root under the GT-KB project root, and both are declared in target_paths (`-009` declares the exact packet path). This bridge proposal file resides under the bridge directory. No application path under applications/ is touched.

## Specification Links

- GOV-REQUIREMENTS-COLLECTION-HOOK-001 - the target spec; W3 issues its v4. Cited as the artifact being corrected.
- SPEC-AUQ-NO-LLM-CLASSIFIER-001 - the deterministic-only, no-LLM-classifier requirement. W3's correction removes the last artifact surface (the title) that still advertised the abandoned LLM-classifier design.
- SPEC-AUQ-POLICY-ENGINE-001 - the spec-classifier hook participates in the deterministic AUQ policy engine; the title correction keeps the spec's metadata consistent with the deterministic engine the implementation already realizes.
- GOV-FILE-BRIDGE-AUTHORITY-001 - the bridge index and verdict files are canonical workflow state; this proposal is filed and reviewed through that workflow.
- DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001 - this proposal carries a complete, relevance-closed Specification Links section and declares the groundtruth.db MemBase mutation surface and the exact approval-packet path in target_paths.
- DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001 - the post-implementation report carries a spec-to-verification mapping with executed evidence (the v4 row inspected: title corrected, body unchanged from v3).
- GOV-ARTIFACT-APPROVAL-001 - the GOV v4 record is a formal artifact; the MemBase supersession is gated by a formal-artifact-approval packet presented to and approved by the owner before insertion.
- PB-ARTIFACT-APPROVAL-001 - the protected-artifact approval discipline applies to the GOV v4 supersession.
- DCL-ARTIFACT-APPROVAL-HOOK-001 - the formal-artifact-approval discipline governs the GOV v4 insert.
- DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001 - this proposal carries the mandatory Project Authorization, Project, and Work Item header lines.
- ADR-ISOLATION-APPLICATION-PLACEMENT-001 - the write targets are in-root; no application path is touched.
- GOV-ARTIFACT-ORIENTED-GOVERNANCE-001 - the correction is preserved as durable artifacts: WI-3367, this proposal, the GOV v4 record, the approval packet, and the post-implementation report.
- ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001 - the fix preserves traceability across the work item, proposal, the v3-to-v4 supersession chain, and the report.
- DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001 - WI-3367 moves through open, in-progress, and verified lifecycle states; the spec moves from v3 to v4.

## Prior Deliberations

A Deliberation Archive search was performed for the requirements-collection hook and the LLM-classifier-abandonment history. Each DELIB id cited below was confirmed retrievable in MemBase.

- DELIB-S358-GOVERNANCE-CORRECTION-PROJECT-AUTHORIZATION - the owner-decision deliberation (S358, owner_conversation) authorizing the combined governance-correction project. It records the W3 scope: a metadata-only v4 dropping the abandoned "LLM classification + retrieval-augmented options" phrase from the title.
- DELIB-S330-REQUIREMENTS-COLLECTION-HOOK-WITH-3-OPTION-CLARIFICATION - the deliberation recording the earlier LLM-classifier and retrieval-augmented-option design for the requirements-collection hook, later superseded by the regex-gate pivot. It is the retrievable record of the design whose last title-level remnant W3 removes.
- DELIB-1701 - the verified Loyal Opposition GO for the requirements-collection hook revised proposal; it records that the owner-decision evidence supported the no-LLM regex-gate direction.

No prior deliberation rejected the W3 title correction.

## Owner Decisions / Input

- 2026-05-17, S358: the owner directed standing up and running the combined four-workstream governance-correction project; W3 is the GOV-REQUIREMENTS-COLLECTION-HOOK-001 title-fix workstream, with the explicit instruction that v4 is metadata-only and changes only the title. Captured in DELIB-S358-GOVERNANCE-CORRECTION-PROJECT-AUTHORIZATION (source_type=owner_conversation, outcome=owner_decision).
- 2026-05-18, S358: the owner approved GOV-REQUIREMENTS-COLLECTION-HOOK-001 v4 - the corrected title with the v3 body carried forward byte-for-byte - as drafted, after full native-format presentation, via AskUserQuestion. Recorded in the formal-artifact-approval packet.
- 2026-05-18, S358: after the `-008` NO-GO surfaced the target-path / deterministic-packet-naming mismatch, the owner selected "Revised proposals + re-GO" - correct target_paths to the mechanically-matching exact path, obtain a fresh Codex GO, regenerate the implementation-start packet, and re-file the post-implementation report - over an owner target-path waiver, via AskUserQuestion. This `-009` REVISED proposal implements that decision.
- Implementation-time owner approval remains required per artifact: the GOV v4 supersession is a formal-artifact mutation gated by a formal-artifact-approval packet. A GO on this `-009` authorizes the corrected target-path envelope and the workstream; the v4 body was already owner-approved per artifact as recorded above.

## Requirement Sufficiency

Existing requirements sufficient. W3 corrects stale title metadata only. The behavioral rule - the v3 body's regex-detection mandate and external-API prohibition - is unchanged and is carried forward verbatim into v4. No new or revised behavioral requirement is created. `-009` revises only the proposal's `target_paths` metadata to mechanically match the governed tool's deterministic packet naming; it introduces no new or revised requirement.

## Clause Scope Clarification (Not a Bulk Operation)

This proposal is not a bulk standing-backlog operation. It is a single-field metadata correction tracked by exactly one work item, WI-3367, an active member of PROJECT-GTKB-GOVERNANCE-CORRECTION-S358. No work-item state inventory, bulk transition, or backlog cleanup is performed. The v4 supersession is a single formal-artifact change carrying its own formal-artifact-approval packet. The proposal references the words "requirement", "work item", and "backlog" only to identify WI-3367, to name the spec being corrected, and to describe the spec lifecycle.

## Bridge INDEX Update Evidence

A REVISED entry for gtkb-s358-w3-requirements-collection-hook-title-fix pointing at this `-009` file is inserted at the top of that document's version list in the bridge index, above the existing `NO-GO: -008`, `NEW: -007`, `GO: -006`, and earlier lines. No prior bridge file and no prior index entry is deleted or rewritten; `-001` through `-008` remain on disk and in the index as the append-only audit trail.

## Proposed Scope

### IP-1: Issue v4 of GOV-REQUIREMENTS-COLLECTION-HOOK-001 with the corrected title

Insert a version 4 of GOV-REQUIREMENTS-COLLECTION-HOOK-001 into MemBase (groundtruth.db) whose title is the v3 title with the trailing " (LLM classification + retrieval-augmented options)" removed; every other field carried forward from v3 unchanged. This was completed under the `-006` GO via the governed `gt spec update` service; the v4 record exists, owner-approved via the packet `.groundtruth/formal-artifact-approvals/2026-05-18-GOV-REQUIREMENTS-COLLECTION-HOOK-001-v4.json`. `-009` does not re-insert it.

### `-009` corrective scope

`-009` corrects the proposal `target_paths` so the implementation-start authorization envelope mechanically covers the exact approval-packet path the governed `gt spec update` service produced. No GOV v4 record is re-inserted and no new MemBase mutation is performed; the `-006`-GO'd implementation already landed correctly. The post-implementation report is re-filed after Codex GO on `-009` and a regenerated implementation-start packet.

### Out of scope

W3 does not change the v3 behavioral rule, the v3 body, or any assertion. It does not modify `.claude/hooks/spec-classifier.py` or any other source, hook, configuration, or test. It does not rewrite v1, v2, or v3 (append-only). It does not touch the W1, W2, or W4 surfaces. The v3 `tags` field still carries the abandoned-design remnants `llm-classification` and `retrieval-augmented`; correcting the tags is outside W3's title-only GO'd scope and is captured separately as a standing-backlog item.

## Specification-Derived Verification Plan

| Specification | Behavior verified | Test or verification |
|---|---|---|
| GOV-REQUIREMENTS-COLLECTION-HOOK-001 | A v4 record exists; its title is the v3 title minus the "(LLM classification + retrieval-augmented options)" parenthetical; the v4 body equals the v3 body byte-for-byte; v3 is preserved | MemBase query inspection comparing the v4 and v3 title and body fields, recorded in the post-implementation report |
| SPEC-AUQ-NO-LLM-CLASSIFIER-001 | The corrected v4 title no longer advertises an LLM-classifier or retrieval-augmented design | inspection of the v4 title, recorded in the report |
| GOV-ARTIFACT-APPROVAL-001 | The GOV v4 supersession carries a formal-artifact-approval packet with presented_to_user true and a matching content hash, at a path within the corrected target_paths | the approval packet, cited by exact path in the report |
| DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001 | The post-implementation report carries this mapping with executed verification evidence | the post-implementation report |

Execution: the post-implementation report records the exact MemBase query confirming the v4 row, a field-level comparison showing the title changed and the body unchanged from v3, the preserved v3 row, and the approval-packet path now within the corrected target_paths. W3 changes no code, so there is no pytest or ruff step; verification is structural inspection of the MemBase records.

## Acceptance Criteria

- A v4 record of GOV-REQUIREMENTS-COLLECTION-HOOK-001 exists in MemBase (already landed under the `-006` GO).
- The v4 title is exactly the v3 title with " (LLM classification + retrieval-augmented options)" removed and nothing else changed.
- The v4 body and all non-title fields equal v3 byte-for-byte.
- v3 is preserved on the append-only record.
- The v4 supersession carries a formal-artifact-approval packet whose exact path is within the `-009` corrected `target_paths`.
- Both bridge preflights pass on the post-implementation report.

## Option Rationale

Issuing a v4 was the owner directive (WI-3367, DELIB-S358). For the `-008` NO-GO, correcting `target_paths` to the exact approval-packet path was selected over (a) a broad version-suffix glob and (b) an owner target-path waiver. The exact path was selected over a broad glob because `fnmatch` of an exact path against itself is unconditionally true, removing all wildcard and case-fold ambiguity, and the packet already exists at exactly that path. The owner selected the revised-proposal-plus-re-GO reconciliation over a waiver via AskUserQuestion (S358), so the corrected target path is mechanically authorized rather than waived.

## Risks / Rollback

- Risk: a re-derived implementation-start packet still mismatches. Mitigation: the corrected `target_paths` names the exact packet path verbatim; `path_authorized()` of an exact path against itself cannot fail.
- Risk: the corrected proposal is read as authorizing a re-insertion of the GOV v4 record. Mitigation: the Revision Note and Proposed Scope state explicitly that the v4 record already landed under the `-006` GO and is not re-inserted.
- Rollback: a GOV-spec supersession is an append-only versioned MemBase mutation reversible by a further versioned correction.

## Recommended Commit Type

`docs` - W3's deliverable is one governance-specification version-4 metadata correction in MemBase plus its formal-artifact-approval packet, with no code, test, or capability-surface change. The post-implementation report carries the recommended type matching the final change set per the Conventional Commits Type Discipline.

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
