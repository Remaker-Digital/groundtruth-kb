REVISED

# Implementation Report - W2 Agent-Red GOV Trio v2 Supersession (GTKB-GOVERNANCE-CORRECTION-S358-W2)

bridge_kind: implementation_report
Document: gtkb-s358-w2-agent-red-gov-trio-v2
Version: 013
Author: Prime Builder (Claude, harness B)
Date: 2026-05-18 UTC
Session: S358

Project Authorization: PAUTH-PROJECT-GTKB-GOVERNANCE-CORRECTION-S358-S358-COMBINED-GOVERNANCE-CORRECTION-PROJECT-AUTHORIZATION
Project: PROJECT-GTKB-GOVERNANCE-CORRECTION-S358
Work Item: WI-3366

target_paths: ["groundtruth.db", ".groundtruth/formal-artifact-approvals/2026-05-18-GOV-AGENT-RED-GTKB-CONFORMANCE-001-v2.json", ".groundtruth/formal-artifact-approvals/2026-05-18-GOV-GTKB-ADOPTION-ENFORCEMENT-001-v2.json", ".groundtruth/formal-artifact-approvals/2026-05-18-GOV-RELEASE-READINESS-GOVERNED-TESTING-001-v2.json"]

## Revision Note

Version 013 (REVISED) re-files the W2 post-implementation report after the `-010` NO-GO's target-path defect was corrected through a revised proposal and a fresh Codex GO. The `-010` NO-GO confirmed the W2 implementation is substantively correct - the three GOV v2 rows, the owner-approved approval packets, and the `full_content` hash matches all check out - and raised one blocker (FINDING-F1, P1): the `-007` proposal's `target_paths` approval-packet globs (`*-gov-<id>-001.json`) did not mechanically match the `gt spec update` deterministic packet filenames (`<date>-<ID>-v2.json`), so the actual packets fell outside the GO-derived authorization envelope.

Per the owner's AskUserQuestion decision (S358) to reconcile via a revised proposal and re-GO rather than a target-path waiver, the `-011` REVISED proposal corrected `target_paths` to the three exact packet paths; Codex GO'd `-011` at `-012`; and the implementation-start authorization packet was regenerated from the `-012` GO (`packet_hash sha256:d57ea71397beff0b16663d1579147e5a89f2a243bd6932245c0e5352b03e8b96`, `proposal_file bridge/gtkb-s358-w2-agent-red-gov-trio-v2-011.md`), with `target_path_globs` now naming `groundtruth.db` plus the three exact packet paths. `implementation_authorization.path_authorized()` returns `True` for `groundtruth.db` and all three exact approval-packet paths.

`-013` carries the corrected `target_paths` and re-files the report. The three GOV v2 records and their three formal-artifact-approval packets, inserted under the `-008` GO and confirmed correct by the `-010` verdict, are unchanged and were not re-inserted; `-013` corrects only the authorization-envelope audit trail.

## Summary

Post-implementation report for the W2 Agent-Red GOV trio v2 supersession. All three implementation points (IP-1, IP-2, IP-3) are complete: GOV-AGENT-RED-GTKB-CONFORMANCE-001, GOV-GTKB-ADOPTION-ENFORCEMENT-001, and GOV-RELEASE-READINESS-GOVERNED-TESTING-001 each carry an append-only version 2 reflecting DELIB-S330-AGENT-RED-NESTED-IN-APPLICATIONS-RULE. v1 of each spec is preserved on the append-only record.

Each v2 was inserted through the governed AUQ-backed `gt spec update` service, each preceded by a full native-format presentation of the exact v2 title and body to the owner and an explicit owner approval collected via AskUserQuestion. The service produced a matching formal-artifact-approval packet for each spec. W2 changed no source, configuration, hook, rule file, or test, and modified no Deliberation Archive record.

## Specification Links

- GOV-AGENT-RED-GTKB-CONFORMANCE-001 - one of the three target specs; W2 issued its v2. The artifact being revised.
- GOV-GTKB-ADOPTION-ENFORCEMENT-001 - one of the three target specs; W2 issued its v2. The artifact being revised.
- GOV-RELEASE-READINESS-GOVERNED-TESTING-001 - one of the three target specs; W2 issued its v2. The artifact being revised.
- ADR-ISOLATION-APPLICATION-PLACEMENT-001 - the isolation principle: Agent Red is a separate project placed under applications/. The three v2 specs align with this principle and with DELIB-S330.
- GOV-FILE-BRIDGE-AUTHORITY-001 - the bridge index and verdict files are canonical workflow state; this report is filed and reviewed through that workflow.
- DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001 - this report carries a complete, relevance-closed Specification Links section and declares every protected mutation surface (groundtruth.db plus the three exact formal-artifact-approval packet paths) in target_paths.
- DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001 - this report carries a spec-to-verification mapping with executed MemBase-inspection evidence below.
- GOV-ARTIFACT-APPROVAL-001 - the three GOV v2 records are formal artifacts; each MemBase supersession was gated by a formal-artifact-approval packet presented to and approved by the owner before insertion.
- PB-ARTIFACT-APPROVAL-001 - the protected-artifact approval discipline was applied to the three GOV v2 supersessions.
- DCL-ARTIFACT-APPROVAL-HOOK-001 - the formal-artifact-approval discipline governs the three GOV v2 inserts; each ran through the governed AUQ-backed `gt spec update` service.
- DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001 - this report carries the mandatory Project Authorization, Project, and Work Item header lines.
- GOV-ARTIFACT-ORIENTED-GOVERNANCE-001 - the correction is preserved as durable artifacts: WI-3366, the proposal chain, the three GOV v2 records, the three approval packets, and this report.
- ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001 - the fix preserves traceability across the work item, proposal, the v1-to-v2 supersession chains, and this report.
- DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001 - WI-3366 moves through open, in-progress, and verified lifecycle states; the three GOV specs move from v1 to v2.

## Prior Deliberations

- DELIB-S358-GOVERNANCE-CORRECTION-PROJECT-AUTHORIZATION - the owner-decision deliberation (S358, owner_conversation) authorizing the combined governance-correction project; records the W2 scope. This report implements the W2 workstream.
- DELIB-S330-AGENT-RED-NESTED-IN-APPLICATIONS-RULE - the owner-decision deliberation (2026-05-04, owner_conversation) correcting the framing: Agent Red is a separate project, not part of GT-KB. The three GOV v2 supersessions reflect this record.
- DELIB-0834 - the owner-decision deliberation (2026-04-20, owner_conversation) - the source of the v1 Agent-Red framing. Superseded forward by DELIB-S330; preserved append-only.
- DELIB-0828 - the owner approval/challenge that GOV-RELEASE-READINESS-GOVERNED-TESTING-001 v1's body cites as its formalization basis; the retained release-readiness substance traces to it.

## Owner Decisions / Input

- 2026-05-04, S330: the owner stated that Agent Red is not part of GT-KB and is a separate project with its own repository. Captured as DELIB-S330-AGENT-RED-NESTED-IN-APPLICATIONS-RULE.
- 2026-05-17, S358: the owner directed standing up and running the combined four-workstream governance-correction project; W2 is the Agent-Red GOV trio v2 supersession workstream. Captured in DELIB-S358-GOVERNANCE-CORRECTION-PROJECT-AUTHORIZATION.
- 2026-05-18, S358: the owner approved GOV-AGENT-RED-GTKB-CONFORMANCE-001 v2, GOV-GTKB-ADOPTION-ENFORCEMENT-001 v2, and GOV-RELEASE-READINESS-GOVERNED-TESTING-001 v2 - the exact title and body of each - as drafted, after full native-format presentation, via AskUserQuestion (one approval per spec). Recorded in the three formal-artifact-approval packets.
- 2026-05-18, S358: after the `-010` NO-GO surfaced the target-path / deterministic-packet-naming mismatch, the owner selected "Revised proposals + re-GO" - correct target_paths to mechanically-matching exact paths, obtain a fresh Codex GO, regenerate the implementation-start packet, re-file the report - over an owner target-path waiver, via AskUserQuestion. The `-011` REVISED proposal, the `-012` GO, the regenerated implementation-start packet, and this `-013` report implement that decision.

## Implemented Changes

### IP-1: GOV-AGENT-RED-GTKB-CONFORMANCE-001 superseded to v2

An append-only version 2 of GOV-AGENT-RED-GTKB-CONFORMANCE-001 was inserted into MemBase via `gt spec update`. The v2 title is "Agent Red is a separate project, not part of GroundTruth-KB". The v2 body reframes Agent Red per DELIB-S330 as a separate project with its own repository and lifecycle, retains the re-scoped sound residual, and carries a Supersession paragraph citing the DELIB-0834 origin and the DELIB-S330 correction. `affected_by` becomes `["DELIB-0834", "DELIB-S330-AGENT-RED-NESTED-IN-APPLICATIONS-RULE"]`. type, status, priority, testability, tags, and assertions carried forward from v1.

### IP-2: GOV-GTKB-ADOPTION-ENFORCEMENT-001 superseded to v2

An append-only version 2 of GOV-GTKB-ADOPTION-ENFORCEMENT-001 was inserted into MemBase via `gt spec update`. The v2 title is "A GroundTruth-KB adopter application must adopt and enforce available GT-KB governance capabilities". The v2 body re-scopes the rule from an Agent-Red-specific mandate to the general adopter model, retains the candidate-skill / work-queue-with-regression-visibility clause generically, and carries a Supersession paragraph citing DELIB-0834 and DELIB-S330. `affected_by` becomes `["DELIB-0829", "DELIB-0834", "DELIB-S330-AGENT-RED-NESTED-IN-APPLICATIONS-RULE"]`. type, status, priority, testability, tags, and assertions carried forward from v1.

### IP-3: GOV-RELEASE-READINESS-GOVERNED-TESTING-001 superseded to v2

An append-only version 2 of GOV-RELEASE-READINESS-GOVERNED-TESTING-001 was inserted into MemBase via `gt spec update`. The v1 title was already subject-neutral and is carried forward unchanged. The v2 body re-scopes the rule's subject per the WI-3366 directive from Agent Red to the GroundTruth-KB platform and hosted applications, preserves the governed-test-evidence requirement (traceable to DELIB-0828) unchanged in substance, and carries a Supersession paragraph citing DELIB-0834 and DELIB-S330. `affected_by` becomes `["DELIB-0828", "DELIB-0829", "DELIB-S330-AGENT-RED-NESTED-IN-APPLICATIONS-RULE"]`. type, status, priority, testability, tags, and assertions carried forward from v1.

## Clause Scope Clarification (Not a Bulk Operation)

This report is not a bulk standing-backlog operation. It documents a three-spec supersession workstream tracked by exactly one work item, WI-3366, an active member of PROJECT-GTKB-GOVERNANCE-CORRECTION-S358. No work-item state inventory, bulk transition, or backlog cleanup is performed. Each of the three GOV v2 supersessions is an individual formal-artifact change carrying its own formal-artifact-approval packet. The report references the words "work item" and "backlog" only to identify WI-3366 and to describe the governance-spec lifecycle.

## Specification-Derived Verification

W2 changes no code, so there is no pytest or ruff step; per the proposal and the inspection-based verification model accepted for the S358 W5 narrative-correction workstream, verification is structural inspection of the MemBase records. Verification was performed with read-only `groundtruth_kb` API calls (`db.get_spec`, `db.get_spec_history`) and read-only inspection of the three approval-packet JSON files.

| Specification | Behavior verified | Verification | Result |
|---|---|---|---|
| GOV-AGENT-RED-GTKB-CONFORMANCE-001 | v2 record exists reframing Agent Red as a separate project per DELIB-S330; v1 preserved | `get_spec_history` + `get_spec` inspection | PASS: history has v1 + v2; current v2 title "Agent Red is a separate project, not part of GroundTruth-KB"; affected_by adds DELIB-S330; v1 preserved |
| GOV-GTKB-ADOPTION-ENFORCEMENT-001 | v2 record exists re-scoping to the general adopter model; v1 preserved | `get_spec_history` + `get_spec` inspection | PASS: history has v1 + v2; current v2 title removes the Agent-Red subject; affected_by adds DELIB-S330; v1 preserved |
| GOV-RELEASE-READINESS-GOVERNED-TESTING-001 | v2 record exists re-scoping the subject to "GT-KB platform + hosted applications"; governed-test-evidence requirement preserved; v1 preserved | `get_spec_history` + `get_spec` inspection | PASS: history has v1 + v2; v2 body re-scoped, governed-test-evidence requirement retained; affected_by adds DELIB-S330; v1 preserved |
| ADR-ISOLATION-APPLICATION-PLACEMENT-001 | the three v2 specs are consistent with the isolation principle | inspection of v2 content against DELIB-S330 | PASS: all three v2 records treat Agent Red as a separate project |
| GOV-ARTIFACT-APPROVAL-001 | each GOV v2 supersession carries a formal-artifact-approval packet with presented_to_user true and a matching content hash, at a path within the corrected target_paths | inspection of the three approval-packet JSON files; `path_authorized` check | PASS: see Formal-Artifact-Approval Packet Evidence and Implementation-Start Authorization below |
| DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001 | this report carries the spec-to-verification mapping with executed evidence | this section | PASS |

## MemBase Evidence

`db.get_spec_history()` returns two versions for each of the three specs (v1 and v2); `db.get_spec()` returns v2 as current:

- GOV-AGENT-RED-GTKB-CONFORMANCE-001: history count 2; current v2, status verified, type governance; v2 title "Agent Red is a separate project, not part of GroundTruth-KB"; v1 title preserved as "Agent Red is a fully conformant GroundTruth-KB-supported application"; v2 affected_by `["DELIB-0834", "DELIB-S330-AGENT-RED-NESTED-IN-APPLICATIONS-RULE"]`.
- GOV-GTKB-ADOPTION-ENFORCEMENT-001: history count 2; current v2, status verified, type governance; v2 title "A GroundTruth-KB adopter application must adopt and enforce available GT-KB governance capabilities"; v1 title preserved as "Agent Red must adopt and enforce available GroundTruth-KB governance capabilities"; v2 affected_by `["DELIB-0829", "DELIB-0834", "DELIB-S330-AGENT-RED-NESTED-IN-APPLICATIONS-RULE"]`.
- GOV-RELEASE-READINESS-GOVERNED-TESTING-001: history count 2; current v2, status verified, type governance; v2 title "Production release readiness requires governed test evidence" (carried forward unchanged from v1); v1 body preserved; v2 affected_by `["DELIB-0828", "DELIB-0829", "DELIB-S330-AGENT-RED-NESTED-IN-APPLICATIONS-RULE"]`.

The three v2 records were created with `changed_by=gt-cli` - the governed AUQ-backed `gt spec update` service - each with a `change_reason` citing DELIB-S330, the bridge thread, the project authorization, and the AskUserQuestion approval.

## Formal-Artifact-Approval Packet Evidence

Each GOV v2 insert ran through the governed `gt spec update` AUQ-backed service with `--owner-presented` and the AskUserQuestion evidence; the service produced a matching approval packet. For each packet, the packet `full_content` equals the inserted MemBase v2 `description`, and `sha256(v2 description)` equals the packet `full_content_sha256`. All three packets carry `artifact_type=governance`, `action=update`, `approved_by=owner`, `presented_to_user=true`, `transcript_captured=true`.

- IP-1 packet: `.groundtruth/formal-artifact-approvals/2026-05-18-GOV-AGENT-RED-GTKB-CONFORMANCE-001-v2.json`, `full_content_sha256=b315d7b4c6743ddcb875e2e609ce012625692ea26d7cac1e6be8911ef2cb9f21`.
- IP-2 packet: `.groundtruth/formal-artifact-approvals/2026-05-18-GOV-GTKB-ADOPTION-ENFORCEMENT-001-v2.json`, `full_content_sha256=f9578d84534d312547afffacfbec93e65eef876371b25456ac23ce0e1f5b6646`.
- IP-3 packet: `.groundtruth/formal-artifact-approvals/2026-05-18-GOV-RELEASE-READINESS-GOVERNED-TESTING-001-v2.json`, `full_content_sha256=32599ce0a7fd07a646087bfc63fcbdf7ef6d3369baee8f4fba4d19fddd4d79e3`.

## Implementation-Start Authorization

The `-010` NO-GO established that the `-007`-GO-derived implementation-start packet's `*-gov-<id>-001.json` globs did not authorize the actual `<date>-<ID>-v2.json` packet paths. The `-011` REVISED proposal corrected `target_paths` to the three exact packet paths; Codex GO'd `-011` at `-012`; and the implementation-start authorization packet was regenerated from the `-012` GO:

- `python scripts/implementation_authorization.py begin --bridge-id gtkb-s358-w2-agent-red-gov-trio-v2` -> `packet_hash sha256:d57ea71397beff0b16663d1579147e5a89f2a243bd6932245c0e5352b03e8b96`, `go_file bridge/gtkb-s358-w2-agent-red-gov-trio-v2-012.md`, `proposal_file bridge/gtkb-s358-w2-agent-red-gov-trio-v2-011.md`, `latest_status GO`, `requirement_sufficiency sufficient`.
- The regenerated packet's `target_path_globs` are `groundtruth.db` plus the three exact approval-packet paths.
- Reviewer-reproducible authorization check - `implementation_authorization.path_authorized(packet, <path>)` evaluated against the regenerated packet:
  - `groundtruth.db` -> `True`
  - `.groundtruth/formal-artifact-approvals/2026-05-18-GOV-AGENT-RED-GTKB-CONFORMANCE-001-v2.json` -> `True`
  - `.groundtruth/formal-artifact-approvals/2026-05-18-GOV-GTKB-ADOPTION-ENFORCEMENT-001-v2.json` -> `True`
  - `.groundtruth/formal-artifact-approvals/2026-05-18-GOV-RELEASE-READINESS-GOVERNED-TESTING-001-v2.json` -> `True`

All four protected write surfaces of the W2 implementation are now inside the GO-derived authorization envelope.

## Bridge Preflights

Both mandatory bridge preflights are run on this `-013` operative file after its INDEX entry is filed:

- `python scripts/bridge_applicability_preflight.py --bridge-id gtkb-s358-w2-agent-red-gov-trio-v2` - expected `preflight_passed: true`, `missing_required_specs: []`, `missing_advisory_specs: []`.
- `python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-s358-w2-agent-red-gov-trio-v2` - expected exit 0, 0 blocking gaps.

Loyal Opposition reproduces the full preflight tables in the VERIFIED verdict per the file-bridge-protocol Mandatory Applicability Preflight Gate.

## Recommended Commit Type

`docs` - W2's deliverable is three governance-specification version-2 records in MemBase plus their three formal-artifact-approval packets: a governance/specification correction with no code, test, or capability-surface change. The recommended commit type matches the change set per the Conventional Commits Type Discipline.

## Files Changed

MemBase + approval packets:
- groundtruth.db (IP-1 GOV-AGENT-RED-GTKB-CONFORMANCE-001 v2 insert; IP-2 GOV-GTKB-ADOPTION-ENFORCEMENT-001 v2 insert; IP-3 GOV-RELEASE-READINESS-GOVERNED-TESTING-001 v2 insert)
- .groundtruth/formal-artifact-approvals/2026-05-18-GOV-AGENT-RED-GTKB-CONFORMANCE-001-v2.json (IP-1)
- .groundtruth/formal-artifact-approvals/2026-05-18-GOV-GTKB-ADOPTION-ENFORCEMENT-001-v2.json (IP-2)
- .groundtruth/formal-artifact-approvals/2026-05-18-GOV-RELEASE-READINESS-GOVERNED-TESTING-001-v2.json (IP-3)

Bridge:
- bridge/gtkb-s358-w2-agent-red-gov-trio-v2-009.md, -010.md, -011.md, -012.md, -013.md
- bridge/INDEX.md (W2 entry)

Commit-scope note: W2 changed no source, configuration, hook, rule, or test file. The W2 commit stages only `groundtruth.db` and the three approval-packet JSON files by explicit path (never `git add -A`); the commit type is `docs`. v1 of each GOV spec is preserved append-only in `groundtruth.db`; no Deliberation Archive record was rewritten.

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
