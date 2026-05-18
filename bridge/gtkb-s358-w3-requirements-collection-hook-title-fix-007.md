NEW

# Implementation Report - W3 GOV-REQUIREMENTS-COLLECTION-HOOK-001 Title Fix (GTKB-GOVERNANCE-CORRECTION-S358-W3)

bridge_kind: implementation_report
Document: gtkb-s358-w3-requirements-collection-hook-title-fix
Version: 007
Author: Prime Builder (Claude, harness B)
Date: 2026-05-18 UTC
Session: S358

Project Authorization: PAUTH-PROJECT-GTKB-GOVERNANCE-CORRECTION-S358-S358-COMBINED-GOVERNANCE-CORRECTION-PROJECT-AUTHORIZATION
Project: PROJECT-GTKB-GOVERNANCE-CORRECTION-S358
Work Item: WI-3367

target_paths: ["groundtruth.db", ".groundtruth/formal-artifact-approvals/*-gov-requirements-collection-hook-001.json"]

## Summary

Post-implementation report for the W3 GOV-REQUIREMENTS-COLLECTION-HOOK-001 title fix, implementing the `-005` proposal under Codex GO at `-006`. The single implementation point (IP-1) is complete: an append-only version 4 of GOV-REQUIREMENTS-COLLECTION-HOOK-001 was inserted into MemBase. v4 corrects only the title - it drops the abandoned-design parenthetical " (LLM classification + retrieval-augmented options)" - and carries the v3 body and every other field forward byte-for-byte. v3 is preserved on the append-only record.

The v4 insert ran through the governed AUQ-backed `gt spec update` service after a full native-format presentation of the v4 title and body to the owner and an explicit owner approval collected via AskUserQuestion. The service produced a matching formal-artifact-approval packet. W3 changed no source, configuration, hook, rule file, or test - `.claude/hooks/spec-classifier.py` already implements the v3 body correctly as a deterministic regex gate, and W3 makes the title match that already-correct body and implementation.

## Specification Links

- GOV-REQUIREMENTS-COLLECTION-HOOK-001 - the target spec; W3 issued its v4. The artifact being corrected.
- SPEC-AUQ-NO-LLM-CLASSIFIER-001 - the deterministic-only, no-LLM-classifier requirement. W3's correction removes the last artifact surface (the title) that still advertised the abandoned LLM-classifier design; the correction aligns the spec's title with this requirement.
- SPEC-AUQ-POLICY-ENGINE-001 - the spec-classifier hook participates in the deterministic AUQ policy engine; the title correction keeps the spec's metadata consistent with the deterministic engine the implementation already realizes.
- GOV-FILE-BRIDGE-AUTHORITY-001 - the bridge index and verdict files are canonical workflow state; this report is filed and reviewed through that workflow.
- DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001 - this report carries a complete, relevance-closed Specification Links section and declares the groundtruth.db MemBase mutation surface and the approval-packet glob in target_paths.
- DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001 - this report carries a spec-to-verification mapping with executed MemBase-inspection evidence below.
- GOV-ARTIFACT-APPROVAL-001 - the GOV v4 record is a formal artifact; the MemBase supersession was gated by a formal-artifact-approval packet presented to and approved by the owner before insertion.
- PB-ARTIFACT-APPROVAL-001 - the protected-artifact approval discipline was applied to the GOV v4 supersession.
- DCL-ARTIFACT-APPROVAL-HOOK-001 - the formal-artifact-approval discipline governs the GOV v4 insert; the insert ran through the governed AUQ-backed `gt spec update` service, which produced a matching approval packet.
- DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001 - this report carries the mandatory Project Authorization, Project, and Work Item header lines.
- ADR-ISOLATION-APPLICATION-PLACEMENT-001 - the write targets are in-root; no application path under applications/ is touched.
- GOV-ARTIFACT-ORIENTED-GOVERNANCE-001 - the correction is preserved as durable artifacts: WI-3367, the proposal chain, the GOV v4 record, the approval packet, and this report.
- ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001 - the fix preserves traceability across the work item, proposal, the v3-to-v4 supersession chain, and this report.
- DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001 - WI-3367 moves through open, in-progress, and verified lifecycle states; the spec moves from v3 to v4.

## Prior Deliberations

- DELIB-S358-GOVERNANCE-CORRECTION-PROJECT-AUTHORIZATION - the owner-decision deliberation (S358, owner_conversation) authorizing the combined governance-correction project; records the W3 scope as a metadata-only v4 title fix. This report implements the W3 workstream.
- DELIB-S330-REQUIREMENTS-COLLECTION-HOOK-WITH-3-OPTION-CLARIFICATION - the deliberation recording the earlier LLM-classifier / retrieval-augmented design for the requirements-collection hook, the design later superseded by the regex-gate pivot. Its last title-level remnant is what W3 removes. It remains v4's `affected_by` reference, carried forward from v3.
- DELIB-1701 - the verified Loyal Opposition GO for the requirements-collection hook revised proposal; it records the no-LLM regex-gate direction now in the v3/v4 body.

## Owner Decisions / Input

- 2026-05-17, S358: the owner directed standing up and running the combined four-workstream governance-correction project; W3 is the GOV-REQUIREMENTS-COLLECTION-HOOK-001 title-fix workstream, with the explicit instruction that v4 is metadata-only and changes only the title. Captured in DELIB-S358-GOVERNANCE-CORRECTION-PROJECT-AUTHORIZATION.
- 2026-05-18, S358: the owner approved GOV-REQUIREMENTS-COLLECTION-HOOK-001 v4 - the corrected title with the v3 body carried forward byte-for-byte - as drafted, after full native-format presentation of the v4 title, body, and metadata. Collected via AskUserQuestion. Recorded in approval packet `.groundtruth/formal-artifact-approvals/2026-05-18-GOV-REQUIREMENTS-COLLECTION-HOOK-001-v4.json`.
- The `-006` GO introduced no new owner decision; it authorized the workstream and explicitly did not pre-grant the per-artifact approval or the verbatim v4 wording. The verbatim v4 record was approved by the owner via AskUserQuestion as recorded above.

## Implemented Changes

### IP-1: GOV-REQUIREMENTS-COLLECTION-HOOK-001 superseded to v4 with the corrected title

An append-only version 4 of GOV-REQUIREMENTS-COLLECTION-HOOK-001 was inserted into MemBase via the governed `gt spec update` service. The v4 title is "A UserPromptSubmit hook MUST classify each owner message and force 3-option clarification when a requirement candidate is detected" - the v3 title with the trailing " (LLM classification + retrieval-augmented options)" removed and nothing else changed. The v4 description equals the v3 description byte-for-byte (the v3 body was extracted programmatically from the v3 MemBase record and supplied verbatim as the `--content-file` input). type (governance), status (verified), priority, testability (observable), assertions, tags, affected_by, and source_paths were all carried forward from v3 by omitting their override flags. The v3-to-v4 supersession is recorded in the v4 `change_reason` field. v3 stays on the append-only record.

## Tags Observation (Out Of Scope For W3)

While reading v3 to prepare v4, Prime Builder observed that the v3 `tags` list still includes `llm-classification` and `retrieval-augmented` - the same abandoned-design remnant the title parenthetical carried. W3's GO'd scope (`-005`) is explicitly title-only ("v4 changes only the title... all non-title fields equal v3 byte-for-byte"); changing the tags would be implementation outside the GO'd scope. v4 therefore carries the tags forward unchanged, faithful to the title-only scope. The stale-tag remnant is captured as a separate standing-backlog work item for future scoped consideration; it is not remediated by W3.

## Clause Scope Clarification (Not a Bulk Operation)

This report is not a bulk standing-backlog operation. It documents a single-field metadata correction tracked by exactly one work item, WI-3367, an active member of PROJECT-GTKB-GOVERNANCE-CORRECTION-S358. No work-item state inventory, bulk transition, or backlog cleanup is performed. The v4 supersession is a single formal-artifact change carrying its own formal-artifact-approval packet. The report references the words "work item" and "backlog" only to identify WI-3367, to describe the spec lifecycle, and to record the out-of-scope tags observation as a future backlog item.

## Specification-Derived Verification

W3 changes no code, so there is no pytest or ruff step; per the `-005` proposal and the inspection-based verification model accepted for the S358 W5 narrative-correction workstream, verification is structural inspection of the MemBase records. Verification was performed with read-only `groundtruth_kb` API calls (`db.get_spec`, `db.get_spec_history`) and read-only inspection of the approval-packet JSON file.

| Specification | Behavior verified | Verification | Result |
|---|---|---|---|
| GOV-REQUIREMENTS-COLLECTION-HOOK-001 | a v4 record exists; its title is the v3 title minus the "(LLM classification + retrieval-augmented options)" parenthetical; the v4 body equals the v3 body byte-for-byte; v3 is preserved | `get_spec_history` + `get_spec` inspection; SHA-256 comparison of v4 and v3 descriptions | PASS: history has v1, v2, v3, v4; current v4 title corrected; `v4 description == v3 description` byte-for-byte (both SHA-256 `7617746664c1ddc25ba6e749767e644be681ff48e79164419c469dc1a9771598`); v3 preserved with its original parenthetical title |
| SPEC-AUQ-NO-LLM-CLASSIFIER-001 | the corrected v4 title no longer advertises an LLM-classifier or retrieval-augmented design | inspection of the v4 title | PASS: v4 title contains no "LLM classification" or "retrieval-augmented" text |
| GOV-ARTIFACT-APPROVAL-001 | the GOV v4 supersession carries a formal-artifact-approval packet with presented_to_user true and a matching content hash | inspection of the approval-packet JSON file | PASS: see Formal-Artifact-Approval Packet Evidence below |
| DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001 | this report carries the spec-to-verification mapping with executed evidence | this section | PASS |

## MemBase Evidence

`db.get_spec_history("GOV-REQUIREMENTS-COLLECTION-HOOK-001")` returns four versions; `db.get_spec()` returns v4 as current:

- History count 4: v1 (status specified), v2 (status specified), v3 (status verified), v4 (status verified).
- v4 current: status verified, type governance, priority None, testability observable; title "A UserPromptSubmit hook MUST classify each owner message and force 3-option clarification when a requirement candidate is detected"; affected_by `["DELIB-S330-REQUIREMENTS-COLLECTION-HOOK-WITH-3-OPTION-CLARIFICATION"]` (carried forward from v3).
- v3 preserved: title "A UserPromptSubmit hook MUST classify each owner message and force 3-option clarification when a requirement candidate is detected (LLM classification + retrieval-augmented options)" - the original parenthetical title.
- `v4 description == v3 description` evaluated True; `sha256(v4 description) == sha256(v3 description) == 7617746664c1ddc25ba6e749767e644be681ff48e79164419c469dc1a9771598`.
- The v4 record was created with `changed_by=gt-cli` - the governed AUQ-backed `gt spec update` service - with a `change_reason` citing DELIB-S358, the bridge thread and `-006` GO, the project authorization, and the AskUserQuestion approval.

## Formal-Artifact-Approval Packet Evidence

The GOV v4 insert ran through the governed `gt spec update` AUQ-backed service with `--owner-presented` and the AskUserQuestion evidence; the service produced a matching approval packet.

- Packet: `.groundtruth/formal-artifact-approvals/2026-05-18-GOV-REQUIREMENTS-COLLECTION-HOOK-001-v4.json`, `full_content_sha256=7617746664c1ddc25ba6e749767e644be681ff48e79164419c469dc1a9771598`.
- Verified: packet `full_content` equals the inserted MemBase v4 `description`; `sha256(v4 description)` equals the packet `full_content_sha256`; packet carries `artifact_type=governance`, `action=update`, `approved_by=owner`, `presented_to_user=true`, `transcript_captured=true`.

The `gt spec update` service deterministically names the approval packet `<date>-<ARTIFACT-ID>-v<N>.json`; the proposal `target_paths` glob (`*-gov-requirements-collection-hook-001.json`) is the lower-cased, version-suffix-free approximation of that deterministic naming, and the packet above is the formal-artifact-approval packet the `-005` proposal authorizes for the GOV v4 supersession.

## Implementation-Start Authorization

The implementation-start authorization packet for W3 was created from the live `-006` GO before the protected MemBase mutation: `python scripts/implementation_authorization.py begin --bridge-id gtkb-s358-w3-requirements-collection-hook-title-fix` -> `packet_hash sha256:83606055901daf8e9e990112fe8bb26520392c0e184cb0a4ed0caefbbb17aac8`, `go_file bridge/gtkb-s358-w3-requirements-collection-hook-title-fix-006.md`, `latest_status GO`, `requirement_sufficiency sufficient`, project authorization `PAUTH-PROJECT-GTKB-GOVERNANCE-CORRECTION-S358-S358-COMBINED-GOVERNANCE-CORRECTION-PROJECT-AUTHORIZATION` validated for `WI-3367`.

## Bridge Preflights

Both mandatory bridge preflights are run on this `-007` operative file after its INDEX entry is filed:

- `python scripts/bridge_applicability_preflight.py --bridge-id gtkb-s358-w3-requirements-collection-hook-title-fix` - expected `preflight_passed: true`, `missing_required_specs: []`, `missing_advisory_specs: []`.
- `python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-s358-w3-requirements-collection-hook-title-fix` - expected exit 0, 0 blocking gaps.

Loyal Opposition reproduces the full preflight tables in the VERIFIED verdict per the file-bridge-protocol Mandatory Applicability Preflight Gate.

## Recommended Commit Type

`docs` - W3's deliverable is one governance-specification version-4 metadata correction in MemBase plus its formal-artifact-approval packet: a governance/specification correction with no code, test, or capability-surface change. The recommended commit type matches the change set per the Conventional Commits Type Discipline.

## Files Changed

MemBase + approval packet:
- groundtruth.db (IP-1 GOV-REQUIREMENTS-COLLECTION-HOOK-001 v4 insert)
- .groundtruth/formal-artifact-approvals/2026-05-18-GOV-REQUIREMENTS-COLLECTION-HOOK-001-v4.json (IP-1)

Bridge:
- bridge/gtkb-s358-w3-requirements-collection-hook-title-fix-007.md
- bridge/INDEX.md (W3 entry)

Commit-scope note: W3 changed no source, configuration, hook, rule, or test file. The W3 commit stages only `groundtruth.db` and the one approval-packet JSON file by explicit path (never `git add -A`); the commit type is `docs`. v3 of the spec is preserved append-only in `groundtruth.db`.

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
