NEW

# Implementation Proposal - W2 Agent-Red GOV Trio v2 Supersession (GTKB-GOVERNANCE-CORRECTION-S358-W2)

bridge_kind: implementation_proposal
Document: gtkb-s358-w2-agent-red-gov-trio-v2
Version: 001
Author: Prime Builder (Claude, harness B)
Date: 2026-05-18 UTC
Session: S358

Project Authorization: PAUTH-PROJECT-GTKB-GOVERNANCE-CORRECTION-S358-S358-COMBINED-GOVERNANCE-CORRECTION-PROJECT-AUTHORIZATION
Project: PROJECT-GTKB-GOVERNANCE-CORRECTION-S358
Work Item: WI-3366

target_paths: [".groundtruth/formal-artifact-approvals/*-gov-agent-red-gtkb-conformance-001.json", ".groundtruth/formal-artifact-approvals/*-gov-gtkb-adoption-enforcement-001.json", ".groundtruth/formal-artifact-approvals/*-gov-release-readiness-governed-testing-001.json"]

## Problem

Three GOV specifications in MemBase still frame Agent Red as a part of GroundTruth-KB. All three are version 1, status verified, dated 2026-04-20, and were never superseded:

- GOV-AGENT-RED-GTKB-CONFORMANCE-001, titled "Agent Red is a fully conformant GroundTruth-KB-supported application", with a body stating "Agent Red is a well-behaved, fully conformant application supported and sustained by GroundTruth-KB. Agent Red must not be treated as an ad hoc exception to GT-KB governance."
- GOV-GTKB-ADOPTION-ENFORCEMENT-001, titled "Agent Red must adopt and enforce available GroundTruth-KB governance capabilities", with a body stating "Agent Red must adopt and enforce, to the extent possible, all GroundTruth-KB governance specifications, managed skills, hooks, subsystems, and integrations."
- GOV-RELEASE-READINESS-GOVERNED-TESTING-001, titled "Production release readiness requires governed test evidence", with a body whose subject is Agent Red specifically ("Agent Red must not be treated as production-release GO merely because implementation work is complete").

All three were sourced from DELIB-0834 (owner_conversation, owner_decision, 2026-04-20), "Agent Red is a fully-conformant application sustained by GT-KB."

On 2026-05-04 the owner corrected this framing. DELIB-S330-AGENT-RED-NESTED-IN-APPLICATIONS-RULE (owner_conversation, owner_decision) records the owner's verbatim statement: "Agent Red is not a part of GT-KB. We have included 4 small demo apps. Agent Red should be pushed to [its own repo] and GroundTruth-KB should be pushed to [its own repo]. These are now separate projects. That was the point of the GT-KB isolation project." DELIB-S330 establishes Agent Red as a separate project with its own repository and lifecycle, nested under applications/Agent_Red/ but not part of GT-KB.

This is the W2 surface of the S358 drift-closure sweep. The `.claude/rules/` files already reflect the separation: `.claude/rules/acting-prime-builder.md` carries an "Agent Red Separate-Project Boundary" section with the corrected narrower interpretation, and `.claude/rules/project-root-boundary.md` and `.claude/rules/canonical-terminology.md` treat Agent Red as a separate project. Only the MemBase GOV specs and DELIB-0834 lag: three governing GOV specs and the owner-decision deliberation behind them still assert the superseded "Agent Red is part of GT-KB" framing.

## Claim

Supersede the three GOV specs with version 2 records that reflect DELIB-S330, and record DELIB-0834's supersession so the MemBase governance surface matches the rule files and the owner's 2026-05-04 correction:

- GOV-AGENT-RED-GTKB-CONFORMANCE-001 v2: reframe from "Agent Red is a fully conformant GT-KB application" to the DELIB-S330 position - Agent Red is a separate project with its own repository and lifecycle, not part of GT-KB, and its files are not live GT-KB artifacts. The sound residual content - that when Agent Red is explicitly in scope as a GT-KB demo/validation context, GT-KB supported-application behavior should be preserved, enforced, documented, and regression-tested where possible - is retained, re-scoped to that explicit-in-scope condition, consistent with the existing `.claude/rules/acting-prime-builder.md` "Agent Red Separate-Project Boundary" section.
- GOV-GTKB-ADOPTION-ENFORCEMENT-001 v2: re-scope from an Agent-Red-specific mandate to the general adopter model - a GT-KB adopter application adopts and enforces available GT-KB governance capabilities to the extent possible; the candidate-skill / work-queue-with-regression-visibility clause is sound and is retained generically. Agent Red is one separate-project adopter, not the subject of the rule.
- GOV-RELEASE-READINESS-GOVERNED-TESTING-001 v2: the release-readiness rule is sound and is retained, re-scoped per the WI-3366 directive from an Agent-Red subject to "the GT-KB platform and hosted applications" - production release readiness (of the platform or a hosted application) requires governed test evidence, regression visibility for governance work, and a passing non-deploying release-candidate gate or an explicit owner-approved documented deferral.

Each v2 supersession narrative records that v1 was sourced from DELIB-0834 (2026-04-20) and that DELIB-0834's "Agent Red is part of GT-KB" framing is superseded by DELIB-S330-AGENT-RED-NESTED-IN-APPLICATIONS-RULE (2026-05-04). This is how W2 "addresses" DELIB-0834: the deliberation is append-only and is not rewritten; DELIB-S330 is the forward-correcting owner-decision record, and every governing GOV spec that depended on DELIB-0834 now carries the supersession pointer.

W2 changes only the three MemBase GOV specs. It edits no source, no rule file, no hook, and no test - the rule files already reflect the separation. v1 of each spec stays on the append-only record.

## In-Root Placement Evidence

W2's only writes are three MemBase GOV-spec version-2 records and their three formal-artifact-approval packets under .groundtruth/formal-artifact-approvals/. Both MemBase (groundtruth.db) and the approval-packet directory are in-root under the GT-KB project root. This bridge proposal file resides under the bridge directory. No file under applications/ is touched; W2 does not modify any Agent Red file - it corrects GT-KB's own governance records about Agent Red.

## Specification Links

- GOV-AGENT-RED-GTKB-CONFORMANCE-001 - one of the three target specs; W2 issues its v2. Cited as the artifact being revised.
- GOV-GTKB-ADOPTION-ENFORCEMENT-001 - one of the three target specs; W2 issues its v2. Cited as the artifact being revised.
- GOV-RELEASE-READINESS-GOVERNED-TESTING-001 - one of the three target specs; W2 issues its v2. Cited as the artifact being revised.
- ADR-ISOLATION-APPLICATION-PLACEMENT-001 - the isolation principle: GT-KB and its applications have full-lifecycle independence; Agent Red is a separate project placed under applications/. W2 aligns the three GOV specs with this principle and with DELIB-S330, the owner conversation behind it.
- GOV-FILE-BRIDGE-AUTHORITY-001 - the bridge index and verdict files are canonical workflow state; this proposal is filed and reviewed through that workflow.
- DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001 - this proposal carries a complete, relevance-closed Specification Links section.
- DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001 - the post-implementation report will carry a spec-to-verification mapping with executed evidence (the three v2 spec rows inspected against DELIB-S330).
- GOV-ARTIFACT-APPROVAL-001 - the three GOV v2 records are formal artifacts; each MemBase supersession is gated by a formal-artifact-approval packet presented to and approved by the owner before insertion.
- PB-ARTIFACT-APPROVAL-001 - the protected-artifact approval discipline applies to the three GOV v2 supersessions.
- DCL-ARTIFACT-APPROVAL-HOOK-001 - the formal-artifact-approval gate hook enforces the packet requirement on the three GOV v2 inserts.
- DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001 - this proposal carries the mandatory Project Authorization, Project, and Work Item header lines.
- GOV-ARTIFACT-ORIENTED-GOVERNANCE-001 - the correction is preserved as durable artifacts: WI-3366, this proposal, the three GOV v2 records, the approval packets, and the post-implementation report.
- ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001 - the fix preserves traceability across the work item, proposal, the v1-to-v2 supersession chain, and the report.
- DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001 - WI-3366 moves through open, in-progress, and verified lifecycle states; the three GOV specs move from v1 to v2.

## Prior Deliberations

A Deliberation Archive search was performed for the Agent-Red conformance framing and the GT-KB isolation topology.

- DELIB-S358-GOVERNANCE-CORRECTION-PROJECT-AUTHORIZATION - the owner-decision deliberation (S358, owner_conversation) authorizing the combined governance-correction project. It records the W2 scope: supersede the three Agent-Red GOV specs with v2 versions reflecting DELIB-S330, address the unsuperseded DELIB-0834, and re-scope the release-readiness rule to "GT-KB platform + hosted applications." This proposal implements the W2 workstream.
- DELIB-S330-AGENT-RED-NESTED-IN-APPLICATIONS-RULE - the owner-decision deliberation (2026-05-04, owner_conversation) that corrects the framing: Agent Red is a separate project, not part of GT-KB, with its own repository and lifecycle, nested under applications/Agent_Red/. It is the forward-correcting record the three GOV v2 supersessions reflect.
- DELIB-0834 - the owner-decision deliberation (2026-04-20, owner_conversation) "Agent Red is a fully-conformant application sustained by GT-KB" - the source of all three v1 GOV specs. Its "Agent Red is part of GT-KB" framing is superseded by DELIB-S330. DELIB-0834 is append-only history and is not rewritten; the three GOV v2 supersession narratives record the supersession pointer so a future reader of the v2 specs (or a DA search) reaches DELIB-S330. This proposal explicitly acknowledges DELIB-0834 as the superseded prior owner decision.
- DELIB-0828 - the owner approval/challenge that GOV-RELEASE-READINESS-GOVERNED-TESTING-001 v1's body cites as its formalization basis ("the next build must be sufficiently well tested for production release"). The release-readiness substance W2 retains traces to this deliberation; W2 re-scopes the subject (from Agent Red to platform + hosted applications) without weakening the governed-test-evidence requirement DELIB-0828 motivates.

No prior deliberation rejected the W2 supersession; W2 implements the DELIB-S330 correction into the three GOV specs that lag it, and explicitly supersedes the DELIB-0834 framing per owner directive.

## Owner Decisions / Input

- 2026-05-04, S330: the owner stated that Agent Red is not part of GT-KB and is a separate project with its own repository, and approved the resulting five binding rules as drafted via AskUserQuestion. Captured as DELIB-S330-AGENT-RED-NESTED-IN-APPLICATIONS-RULE (source_type=owner_conversation, outcome=owner_decision).
- 2026-05-17, S358: the owner directed standing up and running the combined four-workstream governance-correction project; W2 is the Agent-Red GOV trio v2 supersession workstream, with the explicit instruction to supersede the three GOV specs with v2 versions reflecting DELIB-S330, address the unsuperseded DELIB-0834, and re-scope the release-readiness rule to "GT-KB platform + hosted applications." Captured in DELIB-S358-GOVERNANCE-CORRECTION-PROJECT-AUTHORIZATION.
- Implementation-time owner approval is still required per artifact: each of the three GOV v2 supersessions is a formal-artifact mutation requiring a formal-artifact-approval packet presented to and approved by the owner before insertion, with the exact v2 body text in the packet. This GO authorizes the workstream and the reframe direction; it does not pre-grant the per-spec approvals or the verbatim v2 wording.

## Requirement Sufficiency

New or revised requirement required before implementation. W2's deliverable is itself the revision of three governance requirements: each of the three GOV specs is superseded by a version-2 record with corrected scope and framing. W2 performs only this specification-revision work through the governed formal-artifact-approval path; it implements no source, configuration, hook, or test change. The exact v2 body of each spec is captured at implementation time in its formal-artifact-approval packet and approved by the owner before insertion.

## Clause Scope Clarification (Not a Bulk Operation)

This proposal is not a bulk standing-backlog operation. It is a three-spec supersession workstream tracked by exactly one work item, WI-3366, an active member of PROJECT-GTKB-GOVERNANCE-CORRECTION-S358. No work-item state inventory, bulk transition, or backlog cleanup is performed. Each of the three GOV v2 supersessions is an individual formal-artifact change carrying its own formal-artifact-approval packet. The proposal references the words "work item" and "backlog" only to identify WI-3366 and to describe the governance-spec lifecycle.

## Bridge INDEX Update Evidence

A NEW entry for gtkb-s358-w2-agent-red-gov-trio-v2 is inserted at the top of the bridge index, pointing at this -001 file. No prior bridge file and no prior index entry is deleted or rewritten.

## Proposed Scope

### IP-1: Supersede GOV-AGENT-RED-GTKB-CONFORMANCE-001 to v2

Insert a version 2 of GOV-AGENT-RED-GTKB-CONFORMANCE-001 that reframes the spec per DELIB-S330: Agent Red is a separate project with its own repository and lifecycle, not part of GT-KB, and Agent Red files are not live GT-KB artifacts. The retained sound content - that when Agent Red is explicitly in scope as a GT-KB demo or release-readiness validation context, GT-KB supported-application behavior should be preserved, enforced, documented, and regression-tested where possible - is re-scoped to that explicit-in-scope condition, consistent with `.claude/rules/acting-prime-builder.md` "Agent Red Separate-Project Boundary." The v2 title is corrected to remove the "fully conformant GroundTruth-KB-supported application" framing. The v2 supersession narrative cites DELIB-S330 and records that v1's DELIB-0834 framing is superseded. v1 stays on the append-only record.

### IP-2: Supersede GOV-GTKB-ADOPTION-ENFORCEMENT-001 to v2

Insert a version 2 of GOV-GTKB-ADOPTION-ENFORCEMENT-001 that re-scopes the rule from an Agent-Red-specific mandate to the general adopter model: a GT-KB adopter application adopts and enforces, to the extent possible, available GT-KB governance specifications, managed skills, hooks, subsystems, and integrations. The candidate-skill / plug-in / doctor-check work-queue clause with regression visibility is sound and is retained generically. The v2 title and body remove the "Agent Red must" subject; Agent Red is one separate-project adopter, not the rule's subject. The v2 supersession narrative cites DELIB-S330 and records the DELIB-0834 supersession.

### IP-3: Supersede GOV-RELEASE-READINESS-GOVERNED-TESTING-001 to v2

Insert a version 2 of GOV-RELEASE-READINESS-GOVERNED-TESTING-001 that retains the sound release-readiness rule and re-scopes its subject, per the WI-3366 directive, from Agent Red to the GT-KB platform and hosted applications: production release readiness of the GT-KB platform or a hosted application requires release-readiness evidence, regression visibility for governance work, and a passing non-deploying release-candidate gate or an explicit owner-approved documented deferral. The governed-test-evidence requirement (traceable to DELIB-0828) is preserved unchanged in substance. The v2 supersession narrative cites DELIB-S330 and records the DELIB-0834 supersession.

### Out of scope

W2 does not modify any Agent Red file, any `.claude/rules/` file (already corrected), any source, hook, configuration, or test. It does not rewrite DELIB-0834 or any other Deliberation Archive record (append-only). It does not retire the three GOV specs - the owner directive is supersede-to-v2, and v1 remains on the record. It does not touch the W1, W3, or W4 surfaces. The three GOV v2 inserts are MemBase mutations through the formal-artifact-approval workflow; the target_paths are the three approval-packet globs.

## Specification-Derived Verification Plan

| Specification | Behavior verified | Test or verification |
|---|---|---|
| GOV-AGENT-RED-GTKB-CONFORMANCE-001 | A v2 record exists; its content reframes Agent Red as a separate project per DELIB-S330; v1 is preserved; the supersession chain v1->v2 is correct | MemBase query inspection of the v2 row against DELIB-S330, recorded in the post-implementation report |
| GOV-GTKB-ADOPTION-ENFORCEMENT-001 | A v2 record exists; its content re-scopes to the general adopter model; v1 is preserved | MemBase query inspection of the v2 row, recorded in the report |
| GOV-RELEASE-READINESS-GOVERNED-TESTING-001 | A v2 record exists; its subject is re-scoped to "GT-KB platform + hosted applications"; the governed-test-evidence requirement is preserved; v1 is preserved | MemBase query inspection of the v2 row, recorded in the report |
| ADR-ISOLATION-APPLICATION-PLACEMENT-001 | The three v2 specs are consistent with the isolation principle - Agent Red treated as a separate project | inspection of the v2 content against ADR-ISOLATION and DELIB-S330, recorded in the report |
| GOV-ARTIFACT-APPROVAL-001 | Each of the three GOV v2 supersessions carries a formal-artifact-approval packet with presented_to_user true and a matching content hash | the three approval packets, cited by path in the report |
| DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001 | The post-implementation report carries this mapping with executed verification evidence | the post-implementation report |

Execution: the post-implementation report records the exact MemBase queries confirming the three v2 rows, their content against DELIB-S330, the preserved v1 rows, and the three approval-packet paths. W2 changes no code, so there is no pytest or ruff step; verification is structural inspection of the MemBase records, the same inspection-based verification model accepted for the S358 W5 narrative-correction workstream.

## Acceptance Criteria

- A v2 record of each of GOV-AGENT-RED-GTKB-CONFORMANCE-001, GOV-GTKB-ADOPTION-ENFORCEMENT-001, and GOV-RELEASE-READINESS-GOVERNED-TESTING-001 exists in MemBase, each reframed per DELIB-S330.
- GOV-RELEASE-READINESS-GOVERNED-TESTING-001 v2 is re-scoped to "GT-KB platform + hosted applications" and preserves the governed-test-evidence requirement.
- Each v2 supersession narrative cites DELIB-S330 and records that v1's DELIB-0834 framing is superseded.
- v1 of each spec is preserved on the append-only record; no Deliberation Archive record is rewritten.
- Each of the three GOV v2 supersessions carries a formal-artifact-approval packet.
- Both bridge preflights pass on the post-implementation report.

## Option Rationale

Supersede-to-v2 was the owner directive (WI-3366, DELIB-S358) and was selected over two alternatives. Retiring the three specs was rejected: the adoption-enforcement and release-readiness rules carry sound, still-wanted substance (the adopter governance model; the governed-test-evidence requirement) that should be retained and re-scoped, not lost. Editing v1 in place was rejected: GT-KB specs are append-only versioned; v1 is the record of what was governing before the 2026-05-04 correction and stays on the record. For DELIB-0834, recording the supersession pointer in the three v2 narratives (rather than archiving a new standalone superseding deliberation) was selected because DELIB-S330 already exists as the forward-correcting owner-decision record; a fourth deliberation asserting the same correction would duplicate it. The v2 specs carrying the explicit DELIB-0834 -> DELIB-S330 pointer is the minimal, non-duplicating way to address the unsuperseded deliberation.

## Risks / Rollback

- Risk: a v2 reframe drops sound governance substance. Mitigation: IP-2 and IP-3 explicitly retain the adopter-enforcement model and the governed-test-evidence requirement; only the Agent-Red-as-GT-KB-part framing and subject are corrected; the owner approves each v2 body via its packet.
- Risk: the v2 specs and the `.claude/rules/` files drift. Mitigation: the v2 reframe is aligned to the existing `.claude/rules/acting-prime-builder.md` "Agent Red Separate-Project Boundary" wording, which is the already-correct surface.
- Risk: a future reader of v1 misses the correction. Mitigation: each v2 supersession narrative carries the explicit DELIB-0834 -> DELIB-S330 pointer; the v1 rows remain queryable with their version superseded.
- Rollback: a GOV-spec supersession is an append-only versioned MemBase mutation reversible by a further versioned correction. The three supersessions are independent and independently revertible.

## Recommended Commit Type

`docs` - W2's deliverable is three governance-specification version-2 records in MemBase, a governance/specification correction with no code, test, or capability-surface change. The post-implementation report will carry the recommended type matching the final change set per the Conventional Commits Type Discipline.

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
