REVISED

# Implementation Proposal - W2 Agent-Red GOV Trio v2 Supersession (GTKB-GOVERNANCE-CORRECTION-S358-W2)

bridge_kind: prime_proposal
Document: gtkb-s358-w2-agent-red-gov-trio-v2
Version: 011
Author: Prime Builder (Claude, harness B)
Date: 2026-05-18 UTC
Session: S358

Project Authorization: PAUTH-PROJECT-GTKB-GOVERNANCE-CORRECTION-S358-S358-COMBINED-GOVERNANCE-CORRECTION-PROJECT-AUTHORIZATION
Project: PROJECT-GTKB-GOVERNANCE-CORRECTION-S358
Work Item: WI-3366

target_paths: ["groundtruth.db", ".groundtruth/formal-artifact-approvals/2026-05-18-GOV-AGENT-RED-GTKB-CONFORMANCE-001-v2.json", ".groundtruth/formal-artifact-approvals/2026-05-18-GOV-GTKB-ADOPTION-ENFORCEMENT-001-v2.json", ".groundtruth/formal-artifact-approvals/2026-05-18-GOV-RELEASE-READINESS-GOVERNED-TESTING-001-v2.json"]

## Revision Note

Version 011 (REVISED) supersedes the `-010` NO-GO. The `-010` verdict confirmed the W2 implementation is substantively correct: the three target GOV specs have append-only v2 rows whose owner-approved formal-artifact-approval packets carry `full_content` hashes matching the MemBase descriptions, and both mandatory bridge preflights pass on the `-009` report. The sole `-010` blocker was FINDING-F1 (P1): the `-007` proposal's `target_paths` declared the approval-packet globs as `*-gov-<id>-001.json`, but the governed `gt spec update` service deterministically names approval packets `<date>-<ARTIFACT-ID>-v<N>.json`. `scripts/implementation_authorization.py` authorizes target paths via `fnmatch`, which returns `False` for the concrete `-v2.json` packet names against the `*-001.json` globs, so the actual approval packets fell outside the GO-derived authorization envelope.

`-011` corrects `target_paths` to name the three exact approval-packet paths the `gt spec update` service produced (`.groundtruth/formal-artifact-approvals/2026-05-18-GOV-<ID>-v2.json`), alongside `groundtruth.db`. `fnmatch` of an exact path against itself is unconditionally true, so a Codex GO on `-011` and the re-derived implementation-start authorization packet mechanically cover the actual artifacts. The owner selected this revised-proposal-plus-re-GO reconciliation over a target-path waiver via AskUserQuestion (S358).

W2's substantive scope - the three GOV v2 supersessions reflecting DELIB-S330 - is unchanged from `-007`. The three GOV v2 records and their three approval packets already inserted under the `-008` GO are correct (independently confirmed by the `-010` verdict) and are NOT re-inserted; `-011` corrects only the authorization envelope. After Codex GO on `-011`, Prime Builder regenerates the implementation-start authorization packet from that GO and re-files the post-implementation report citing the corrected scope.

Version 007 (REVISED) superseded the `-006` NO-GO and adopted Loyal Opposition's `-006` Option A ruling: `Requirement Sufficiency` is `Existing requirements sufficient`, and `groundtruth.db` plus the approval-packet target paths are declared in `target_paths`. Each of the three GOV v2 inserts carries its own owner-approved formal-artifact-approval packet for the exact v2 body.

## Problem

Three GOV specifications in MemBase still frame Agent Red as a part of GroundTruth-KB. All three were version 1, status verified, dated 2026-04-20, and were never superseded:

- GOV-AGENT-RED-GTKB-CONFORMANCE-001, titled "Agent Red is a fully conformant GroundTruth-KB-supported application".
- GOV-GTKB-ADOPTION-ENFORCEMENT-001, titled "Agent Red must adopt and enforce available GroundTruth-KB governance capabilities".
- GOV-RELEASE-READINESS-GOVERNED-TESTING-001, with a body whose subject is Agent Red specifically.

All three were sourced from the 2026-04-20 framing of Agent Red as a GT-KB-supported application recorded in DELIB-0834. On 2026-05-04 the owner corrected this framing: DELIB-S330-AGENT-RED-NESTED-IN-APPLICATIONS-RULE records that Agent Red is a separate project with its own repository and lifecycle, nested under applications/Agent_Red/ but not part of GT-KB. The `.claude/rules/` files already reflect the separation; only the MemBase GOV specs and DELIB-0834 lagged. This is the W2 surface of the S358 drift-closure sweep.

## Claim

Supersede the three GOV specs with version 2 records that reflect DELIB-S330, and record DELIB-0834's supersession so the MemBase governance surface matches the rule files and the owner's 2026-05-04 correction:

- GOV-AGENT-RED-GTKB-CONFORMANCE-001 v2: reframe from "Agent Red is a fully conformant GT-KB application" to the DELIB-S330 position - Agent Red is a separate project with its own repository and lifecycle, not part of GT-KB. The sound residual content - that when Agent Red is explicitly in scope as a GT-KB demo/validation context, GT-KB supported-application behavior should be preserved, enforced, documented, and regression-tested where possible - is retained, re-scoped to that explicit-in-scope condition.
- GOV-GTKB-ADOPTION-ENFORCEMENT-001 v2: re-scope from an Agent-Red-specific mandate to the general adopter model - a GT-KB adopter application adopts and enforces available GT-KB governance capabilities to the extent possible; the candidate-skill / work-queue-with-regression-visibility clause is retained generically.
- GOV-RELEASE-READINESS-GOVERNED-TESTING-001 v2: the release-readiness rule is retained and re-scoped per the WI-3366 directive from an Agent-Red subject to "the GT-KB platform and hosted applications". The governed-test-evidence requirement (traceable to DELIB-0828) is preserved unchanged in substance.

Each v2 supersession narrative records that v1's "Agent Red is part of GT-KB" framing is superseded by DELIB-S330-AGENT-RED-NESTED-IN-APPLICATIONS-RULE. DELIB-0834 is append-only and is not rewritten. W2 changes only the three MemBase GOV specs; it edits no source, no rule file, no hook, and no test. v1 of each spec stays on the append-only record.

## In-Root Placement Evidence

W2's only writes are three MemBase GOV-spec version-2 records in groundtruth.db and their three formal-artifact-approval packets under .groundtruth/formal-artifact-approvals/. Both groundtruth.db and the approval-packet directory are in-root under the GT-KB project root, and all four surfaces (groundtruth.db plus the three exact approval-packet paths) are declared in target_paths. This bridge proposal file resides under the bridge directory. No file under applications/ is touched; W2 does not modify any Agent Red file - it corrects GT-KB's own governance records about Agent Red.

## Specification Links

- GOV-AGENT-RED-GTKB-CONFORMANCE-001 - one of the three target specs; W2 issues its v2. Cited as the artifact being revised.
- GOV-GTKB-ADOPTION-ENFORCEMENT-001 - one of the three target specs; W2 issues its v2. Cited as the artifact being revised.
- GOV-RELEASE-READINESS-GOVERNED-TESTING-001 - one of the three target specs; W2 issues its v2. Cited as the artifact being revised.
- ADR-ISOLATION-APPLICATION-PLACEMENT-001 - the isolation principle: GT-KB and its applications have full-lifecycle independence; Agent Red is a separate project placed under applications/. W2 aligns the three GOV specs with this principle and with DELIB-S330.
- GOV-FILE-BRIDGE-AUTHORITY-001 - the bridge index and verdict files are canonical workflow state; this proposal is filed and reviewed through that workflow.
- DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001 - this proposal carries a complete, relevance-closed Specification Links section and declares every protected mutation surface (groundtruth.db plus the three exact formal-artifact-approval packet paths) in target_paths.
- DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001 - the post-implementation report carries a spec-to-verification mapping with executed evidence (the three v2 spec rows inspected against DELIB-S330).
- GOV-ARTIFACT-APPROVAL-001 - the three GOV v2 records are formal artifacts; each MemBase supersession is gated by a formal-artifact-approval packet presented to and approved by the owner before insertion.
- PB-ARTIFACT-APPROVAL-001 - the protected-artifact approval discipline applies to the three GOV v2 supersessions.
- DCL-ARTIFACT-APPROVAL-HOOK-001 - the formal-artifact-approval discipline governs the three GOV v2 inserts.
- DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001 - this proposal carries the mandatory Project Authorization, Project, and Work Item header lines.
- GOV-ARTIFACT-ORIENTED-GOVERNANCE-001 - the correction is preserved as durable artifacts: WI-3366, this proposal, the three GOV v2 records, the approval packets, and the post-implementation report.
- ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001 - the fix preserves traceability across the work item, proposal, the v1-to-v2 supersession chain, and the report.
- DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001 - WI-3366 moves through open, in-progress, and verified lifecycle states; the three GOV specs move from v1 to v2.

## Prior Deliberations

A Deliberation Archive search was performed for the Agent-Red conformance framing and the GT-KB isolation topology.

- DELIB-S358-GOVERNANCE-CORRECTION-PROJECT-AUTHORIZATION - the owner-decision deliberation (S358, owner_conversation) authorizing the combined governance-correction project. It records the W2 scope. This proposal implements the W2 workstream.
- DELIB-S330-AGENT-RED-NESTED-IN-APPLICATIONS-RULE - the owner-decision deliberation (2026-05-04, owner_conversation) that corrects the framing: Agent Red is a separate project, not part of GT-KB, with its own repository and lifecycle. It is the forward-correcting record the three GOV v2 supersessions reflect.
- DELIB-0834 - the owner-decision deliberation (2026-04-20, owner_conversation) "Agent Red is a fully-conformant application sustained by GT-KB" - the source of the v1 Agent-Red framing. Its framing is superseded by DELIB-S330. DELIB-0834 is append-only history and is not rewritten; the three GOV v2 supersession narratives record the supersession pointer.
- DELIB-0828 - the owner approval/challenge that GOV-RELEASE-READINESS-GOVERNED-TESTING-001 v1's body cites as its formalization basis. The release-readiness substance W2 retains traces to this deliberation; W2 re-scopes the subject without weakening the governed-test-evidence requirement DELIB-0828 motivates.

No prior deliberation rejected the W2 supersession.

## Owner Decisions / Input

- 2026-05-04, S330: the owner stated that Agent Red is not part of GT-KB and is a separate project with its own repository, and approved the resulting binding rules as drafted via AskUserQuestion. Captured as DELIB-S330-AGENT-RED-NESTED-IN-APPLICATIONS-RULE (source_type=owner_conversation, outcome=owner_decision).
- 2026-05-17, S358: the owner directed standing up and running the combined four-workstream governance-correction project; W2 is the Agent-Red GOV trio v2 supersession workstream. Captured in DELIB-S358-GOVERNANCE-CORRECTION-PROJECT-AUTHORIZATION.
- 2026-05-18, S358: the owner approved each of the three GOV v2 bodies (GOV-AGENT-RED-GTKB-CONFORMANCE-001, GOV-GTKB-ADOPTION-ENFORCEMENT-001, GOV-RELEASE-READINESS-GOVERNED-TESTING-001) as drafted, after full native-format presentation, via AskUserQuestion - one approval per spec. Recorded in the three formal-artifact-approval packets.
- 2026-05-18, S358: after the `-010` NO-GO surfaced the target-path / deterministic-packet-naming mismatch, the owner selected "Revised proposals + re-GO" - correct target_paths to mechanically-matching exact paths, obtain a fresh Codex GO, regenerate the implementation-start packet, and re-file the post-implementation report - over an owner target-path waiver, via AskUserQuestion. This `-011` REVISED proposal implements that decision.
- Implementation-time owner approval remains per artifact: each GOV v2 supersession is a formal-artifact mutation gated by a formal-artifact-approval packet. A GO on this `-011` authorizes the corrected target-path envelope and the workstream; the three v2 bodies were already owner-approved per artifact as recorded above.

## Requirement Sufficiency

Existing requirements sufficient. The governing requirements for W2 already exist: the owner decisions DELIB-S330-AGENT-RED-NESTED-IN-APPLICATIONS-RULE and DELIB-S358-GOVERNANCE-CORRECTION-PROJECT-AUTHORIZATION decided the Agent-Red separation correction and authorized W2; the three GOV v1 records being revised are themselves the requirement artifacts whose scope and framing are corrected. W2 authors no new requirement and changes no source, configuration, hook, script, or test. `-011` revises only the proposal's `target_paths` metadata to mechanically match the governed tool's deterministic packet naming; it introduces no new or revised requirement.

## Clause Scope Clarification (Not a Bulk Operation)

This proposal is not a bulk standing-backlog operation. It is a three-spec supersession workstream tracked by exactly one work item, WI-3366, an active member of PROJECT-GTKB-GOVERNANCE-CORRECTION-S358. No work-item state inventory, bulk transition, or backlog cleanup is performed. Each of the three GOV v2 supersessions is an individual formal-artifact change carrying its own formal-artifact-approval packet. The proposal references the words "work item" and "backlog" only to identify WI-3366 and to describe the governance-spec lifecycle.

## Bridge INDEX Update Evidence

A REVISED entry for gtkb-s358-w2-agent-red-gov-trio-v2 pointing at this `-011` file is inserted at the top of that document's version list in the bridge index, above the existing `NO-GO: -010`, `NEW: -009`, `GO: -008`, and earlier lines. No prior bridge file and no prior index entry is deleted or rewritten; `-001` through `-010` remain on disk and in the index as the append-only audit trail.

## Proposed Scope

### IP-1: Supersede GOV-AGENT-RED-GTKB-CONFORMANCE-001 to v2

Insert a version 2 of GOV-AGENT-RED-GTKB-CONFORMANCE-001 into MemBase (groundtruth.db) reframing the spec per DELIB-S330. This was completed under the `-008` GO; the v2 record exists, owner-approved via the packet `.groundtruth/formal-artifact-approvals/2026-05-18-GOV-AGENT-RED-GTKB-CONFORMANCE-001-v2.json`. `-011` does not re-insert it.

### IP-2: Supersede GOV-GTKB-ADOPTION-ENFORCEMENT-001 to v2

Insert a version 2 of GOV-GTKB-ADOPTION-ENFORCEMENT-001 into MemBase (groundtruth.db) re-scoping the rule to the general adopter model. This was completed under the `-008` GO; the v2 record exists, owner-approved via the packet `.groundtruth/formal-artifact-approvals/2026-05-18-GOV-GTKB-ADOPTION-ENFORCEMENT-001-v2.json`. `-011` does not re-insert it.

### IP-3: Supersede GOV-RELEASE-READINESS-GOVERNED-TESTING-001 to v2

Insert a version 2 of GOV-RELEASE-READINESS-GOVERNED-TESTING-001 into MemBase (groundtruth.db) re-scoping the rule's subject to the GT-KB platform and hosted applications. This was completed under the `-008` GO; the v2 record exists, owner-approved via the packet `.groundtruth/formal-artifact-approvals/2026-05-18-GOV-RELEASE-READINESS-GOVERNED-TESTING-001-v2.json`. `-011` does not re-insert it.

### `-011` corrective scope

`-011` corrects the proposal `target_paths` so the implementation-start authorization envelope mechanically covers the three exact approval-packet paths the governed `gt spec update` service produced. No GOV v2 record is re-inserted and no new MemBase mutation is performed; the `-008`-GO'd implementation already landed correctly. The post-implementation report is re-filed after Codex GO on `-011` and a regenerated implementation-start packet.

### Out of scope

W2 does not modify any Agent Red file, any `.claude/rules/` file, any source, hook, configuration, or test. It does not rewrite DELIB-0834 or any other Deliberation Archive record. It does not retire the three GOV specs - v1 remains on the record. It does not touch the W1, W3, or W4 surfaces.

## Specification-Derived Verification Plan

| Specification | Behavior verified | Test or verification |
|---|---|---|
| GOV-AGENT-RED-GTKB-CONFORMANCE-001 | A v2 record exists; its content reframes Agent Red as a separate project per DELIB-S330; v1 is preserved | MemBase query inspection of the v2 row against DELIB-S330, recorded in the post-implementation report |
| GOV-GTKB-ADOPTION-ENFORCEMENT-001 | A v2 record exists; its content re-scopes to the general adopter model; v1 is preserved | MemBase query inspection of the v2 row, recorded in the report |
| GOV-RELEASE-READINESS-GOVERNED-TESTING-001 | A v2 record exists; its subject is re-scoped to "GT-KB platform + hosted applications"; the governed-test-evidence requirement is preserved; v1 is preserved | MemBase query inspection of the v2 row, recorded in the report |
| GOV-ARTIFACT-APPROVAL-001 | Each of the three GOV v2 supersessions carries a formal-artifact-approval packet with presented_to_user true and a matching content hash, at a path within the corrected target_paths | the three approval packets, cited by exact path in the report |
| DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001 | The post-implementation report carries this mapping with executed verification evidence | the post-implementation report |

Execution: the post-implementation report records the exact MemBase queries confirming the three v2 rows, their content against DELIB-S330, the preserved v1 rows, and the three approval-packet paths now within the corrected target_paths. W2 changes no code, so there is no pytest or ruff step; verification is structural inspection of the MemBase records.

## Acceptance Criteria

- A v2 record of each of the three target GOV specs exists in MemBase, each reframed per DELIB-S330 (already landed under the `-008` GO).
- GOV-RELEASE-READINESS-GOVERNED-TESTING-001 v2 is re-scoped to "GT-KB platform + hosted applications" and preserves the governed-test-evidence requirement.
- Each v2 supersession narrative cites DELIB-S330 and records the DELIB-0834 supersession.
- v1 of each spec is preserved on the append-only record.
- Each of the three GOV v2 supersessions carries a formal-artifact-approval packet whose exact path is within the `-011` corrected `target_paths`.
- Both bridge preflights pass on the post-implementation report.

## Option Rationale

Supersede-to-v2 was the owner directive (WI-3366, DELIB-S358). For the `-010` NO-GO, correcting `target_paths` to the three exact approval-packet paths was selected over (a) a broad version-suffix glob and (b) an owner target-path waiver. Exact paths were selected over a broad glob because `fnmatch` of an exact path against itself is unconditionally true, removing all wildcard and case-fold ambiguity, and the three packets already exist at exactly those paths. The owner selected the revised-proposal-plus-re-GO reconciliation over a waiver via AskUserQuestion (S358), so the corrected target paths are mechanically authorized rather than waived.

## Risks / Rollback

- Risk: a re-derived implementation-start packet still mismatches. Mitigation: the corrected `target_paths` names the three exact packet paths verbatim; `fnmatch` of an exact path against itself cannot fail.
- Risk: the corrected proposal is read as authorizing a re-insertion of the GOV v2 records. Mitigation: the Revision Note and Proposed Scope state explicitly that the three v2 records already landed under the `-008` GO and are not re-inserted; `-011` corrects only the authorization envelope.
- Rollback: a GOV-spec supersession is an append-only versioned MemBase mutation reversible by a further versioned correction; the three supersessions are independently revertible.

## Recommended Commit Type

`docs` - W2's deliverable is three governance-specification version-2 records in MemBase plus their three formal-artifact-approval packets: a governance/specification correction with no code, test, or capability-surface change. The post-implementation report carries the recommended type matching the final change set per the Conventional Commits Type Discipline.

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
