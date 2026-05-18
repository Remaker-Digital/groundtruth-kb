NEW

# Implementation Proposal - W5 Token-Framing-Distortion Correction (GTKB-GOVERNANCE-CORRECTION-S358-W5)

bridge_kind: implementation_proposal
Document: gtkb-s358-w5-token-framing-correction
Version: 001
Author: Prime Builder (Claude, harness B)
Date: 2026-05-18 UTC
Session: S358

Project Authorization: PAUTH-PROJECT-GTKB-GOVERNANCE-CORRECTION-S358-S358-COMBINED-GOVERNANCE-CORRECTION-PROJECT-AUTHORIZATION
Project: PROJECT-GTKB-GOVERNANCE-CORRECTION-S358
Work Item: WI-3370

target_paths: ["CLAUDE.md", ".claude/rules/bridge-essential.md", ".claude/rules/canonical-terminology.md"]

## Problem

Several live, auto-loaded reasoning-shaping rule files frame the retired-poller history as a token-volume problem rather than a work-waste problem. The owner identified this in S358 as an active distortion of reasoning, captured in DELIB-S358-TOKEN-CONCERN-IS-WASTE-NOT-VOLUME.

The S308 poller defect was blind, activity-independent polling: an external Windows OS service woke both harnesses every 3 minutes regardless of whether the bridge had changed, so most spawned sessions did work without information. The defect was pointless repetition, not token expenditure. But three rule files compress the lesson into token-volume language:

(1) CLAUDE.md, in the "Bridge Polling: Halted" rationale, states the poller "drove a ~10x session token-cost regression (~12.5M tokens/day from background spawns alone)" and that "Manual scans recover the cost." The mechanism (blind, activity-independent polling) is absent; only the symptom (token count rose) remains.

(2) bridge-essential.md frames it three times: the Operational Mode section calls the retired tasks a "former token-heavy implementation" and says the OS poller "drove a ~10x session token-cost regression"; the S308 Incident History entry repeats "a ~10x token-cost regression" and states the Lesson as "token cost is a first-class operational metric." That Lesson sentence is the core distortion - it elevates token volume itself to an operational metric.

(3) canonical-terminology.md frames the retired class as a "token-heavy scheduled-task" substrate, and the "OS poller" glossary entry says the class was halted "after a 10x session token-cost regression."

Read in isolation - which is how an auto-loaded rule file is read - this framing yields the wrong rule: "minimize token usage." In S358 it did exactly that: Prime Builder argued against per-item bridge-dispatch parallelism on a "more concurrent spawns means more token cost" basis, treating token volume as a quantity to minimize. That reasoning was distorted; the owner corrected it.

## Claim

Correct the framing in the three rule files so the poller lesson states its mechanism (blind, activity-independent repetition) and its real principle (automation must be activity-driven and deterministic; repeated work that yields no marginal information is the defect), not token volume. The incident facts (the roughly tenfold spawn increase, the blind three-minute interval, the spawn counts) are preserved; only the interpretation - the Lesson - is corrected. The corrected framing aligns the poller-incident text with the framing DELIB-S312-DETERMINISTIC-SERVICES-PRINCIPLE already uses: token cost as "a recurring tax that pays no marginal information dividend" - where the defect is the absence of dividend, not the expenditure.

No incident history is erased and no governance rule is weakened: the do-not-re-enable mandate, the manual-scan fallback, and the cross-harness-trigger operating mode are all unchanged. Only the reason given for the retirement is corrected.

## In-Root Placement Evidence

All three target paths are in-root under the GT-KB project root: CLAUDE.md at the root, and two rule files under the rules directory. This bridge proposal file resides under the bridge directory. No target path is outside the GT-KB project root, and no application path is touched.

## Specification Links

- GOV-FILE-BRIDGE-AUTHORITY-001 - the bridge index and verdict files are canonical workflow state; this proposal is filed and reviewed through that workflow.
- DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001 - this proposal carries a complete, relevance-closed Specification Links section.
- DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001 - the post-implementation report will carry a spec-to-test mapping with executed verification evidence.
- GOV-ARTIFACT-APPROVAL-001 - the three target files are protected narrative artifacts; each correction is gated by a narrative-artifact-approval packet presented to and approved by the owner before the Write.
- PB-ARTIFACT-APPROVAL-001 - the protected-artifact approval discipline applies to this narrative-artifact correction.
- DCL-ARTIFACT-APPROVAL-HOOK-001 - the narrative-artifact-approval gate hook enforces the packet requirement on the protected-file Writes.
- GOV-ARTIFACT-ORIENTED-GOVERNANCE-001 - the correction is preserved as durable artifacts: DELIB-S358-TOKEN-CONCERN-IS-WASTE-NOT-VOLUME, WI-3370, this proposal, and the post-implementation report.
- ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001 - the fix preserves traceability across the deliberation, work item, proposal, and report.
- DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001 - WI-3370 moves through open, in-progress, and verified lifecycle states.
- DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001 - this proposal carries the mandatory Project Authorization, Project, and Work Item header lines.
- ADR-ISOLATION-APPLICATION-PLACEMENT-001 - all target files are in-root; no application path is touched.

## Prior Deliberations

A Deliberation Archive body-search was performed for the token-framing topic. Relevant records:

- DELIB-S358-TOKEN-CONCERN-IS-WASTE-NOT-VOLUME - the owner-decision deliberation (S358, owner_conversation) that authorizes this correction and states the canonical waste-not-volume framing. This proposal implements it.
- DELIB-S312-DETERMINISTIC-SERVICES-PRINCIPLE - the principle this correction aligns the rule files to: token cost as a recurring tax that pays no marginal information dividend; repetitive AI work is the defect.
- DELIB-S319-SMART-POLLER-POLICY-CLARIFICATION and DELIB-S319-SMART-POLLER-OBJECTIVE-CLARIFICATION - the smart-poller clarification deliberations; they record the OLD-poller halt as implementation-specific and the spawn-to-notify objective. They are append-only design-reasoning records and are not rewritten by this proposal; DELIB-S358-TOKEN-CONCERN-IS-WASTE-NOT-VOLUME is the forward-correcting record.

No prior deliberation rejected or already addressed this framing correction.

## Owner Decisions / Input

- 2026-05-18, S358: the owner clarified that the GT-KB token concern is waste - pointless repetition, blind or activity-independent work, or work a deterministic implementation should do - not raw token volume, and directed removing the lingering distortion from the artifacts. Captured as DELIB-S358-TOKEN-CONCERN-IS-WASTE-NOT-VOLUME, owner-approved as drafted via AskUserQuestion.
- 2026-05-18, S358: the owner chose, via AskUserQuestion, to fold this correction into PROJECT-GTKB-GOVERNANCE-CORRECTION-S358 as a fifth workstream and authorized the one-time extension of the project authorization to cover WI-3370.
- The implementation of each protected-file correction additionally requires a per-file narrative-artifact-approval packet presented to and approved by the owner before the Write; that approval is collected at implementation time and is not pre-granted by this proposal.

## Requirement Sufficiency

Existing requirements sufficient. The correct framing is already established by DELIB-S312-DETERMINISTIC-SERVICES-PRINCIPLE and now by DELIB-S358-TOKEN-CONCERN-IS-WASTE-NOT-VOLUME. This proposal aligns three rule files to that existing framing; it does not create, revise, or relax any requirement. No new or revised requirement is needed.

## Clause Scope Clarification (Not a Bulk Operation)

This proposal is not a bulk standing-backlog operation. It is a three-file framing correction tracked by exactly one work item, WI-3370, an active member of PROJECT-GTKB-GOVERNANCE-CORRECTION-S358. No work-item inventory, bulk transition, or backlog cleanup is performed. The proposal references the phrase "work item" and the word "backlog" only to identify WI-3370 and to describe the poller history; it performs no bulk operation. Each artifact correction is an individual formal-artifact change carrying its own narrative-artifact-approval packet.

## MemBase Scope

A MemBase body-search for the distorted framing (patterns: token-cost, token-heavy, first-class operational metric, tokens-per-day) found:

- 10 deliberations carrying the text - Loyal Opposition reviews, a session wrap, a verdict, the two DELIB-S319 smart-poller clarifications, and DELIB-S358-TOKEN-CONCERN-IS-WASTE-NOT-VOLUME itself. Deliberations are append-only Deliberation Archive records, the design-reasoning tier, and are not rewritten; DELIB-S358-TOKEN-CONCERN-IS-WASTE-NOT-VOLUME is the forward-correcting record any future archive query surfaces. None are in this proposal's target set.
- 4 specifications carrying the text - ADR-SMART-POLLER-OWNER-OUT-OF-LOOP-001, DCL-SMART-POLLER-AUTO-TRIGGER-001, DCL-SINGLE-HARNESS-DISPATCHER-DESKTOP-TASK-001, DCL-SESSION-STARTUP-TOKEN-BUDGET-001 - plus 1 document, doc-ia-refactoring-modularity-assessment-2026-02-17. Carrying the text is not the same as carrying the distortion: each needs an individual read to distinguish genuine distortion from correct or incidental framing. This is deferred to a named follow-on so this proposal stays bounded to the auto-loaded reasoning-shaping rule-file surface - the surface where the distortion actively misdirects reasoning.

The follow-on, recommended as a sixth workstream or a standalone reliability-fix work item, audits the 4 specifications plus the 1 document and supersedes any confirmed-distorted live spec with a corrected version. It is named here so it is not lost.

## Bridge INDEX Update Evidence

A NEW entry for gtkb-s358-w5-token-framing-correction is inserted at the top of the bridge index. No prior bridge file and no prior index entry is deleted or rewritten.

## Proposed Scope

### IP-1: Correct the CLAUDE.md Bridge-Polling-Halted rationale

In CLAUDE.md, the "Bridge Polling: Halted" section's rationale paragraph states the poller "drove a ~10x session token-cost regression (~12.5M tokens/day from background spawns alone)" and that "Manual scans recover the cost." Correct the rationale so it names the mechanism: the poller woke both harnesses on a fixed interval regardless of bridge activity, so most spawned sessions did no work; the defect was blind, activity-independent repetition. The incident magnitude (the roughly tenfold spawn increase) is retained as a fact; the framing of it as a "token-cost regression" to be "recovered" is corrected to the work-waste framing. The do-not-re-enable mandate and the manual-scan operating mode are unchanged.

### IP-2: Correct the bridge-essential.md poller-lesson framing

In the bridge-essential rule file, correct three spots: the Operational Mode "former token-heavy implementation" phrasing; the Operational Mode "~10x session token-cost regression" rationale; and, as the core fix, the S308 Incident History entry whose Lesson reads "token cost is a first-class operational metric." Restate the S308 Lesson as: blind, activity-independent automation that does work without information is the defect; automation must be activity-driven and deterministic. The incident facts (the spawn counts, the blind three-minute interval) are retained. The S339 smart-poller-retirement lesson and every do-not-re-enable mandate are unchanged.

### IP-3: Correct the canonical-terminology.md poller entries

In the canonical-terminology rule file, correct the "token-heavy scheduled-task" phrasing in the cross-harness-event-driven-trigger glossary entry and the "OS poller" glossary entry's "halted ... after a 10x session token-cost regression" phrasing, so both describe the retired class by its actual defect (blind, activity-independent polling) rather than by token volume. The glossary definitions, aliases, sources, and do-not-re-enable references are otherwise unchanged.

### Out of scope

This proposal does not rewrite any Deliberation Archive record; deliberations are append-only history. It does not modify the 4 MemBase specifications or the 1 document flagged in the MemBase Scope section; those are a named follow-on. It does not touch the append-only bridge audit trail. It does not change any do-not-re-enable mandate, the cross-harness-trigger operating mode, or any governance rule; only the framing and lesson text is corrected. The Tier-2 DCL-SESSION-STARTUP-TOKEN-BUDGET-001 wording is part of the deferred follow-on, not this proposal.

## Specification-Derived Verification Plan

| Specification | Behavior verified | Test or verification |
|---|---|---|
| DELIB-S358-TOKEN-CONCERN-IS-WASTE-NOT-VOLUME | No poller-retirement passage in the three target files presents token volume as the lesson; each names the blind, activity-independent mechanism | grep verification over the three files, recorded in the post-implementation report |
| DELIB-S312-DETERMINISTIC-SERVICES-PRINCIPLE | The corrected text is consistent with the deterministic-services framing - waste is repetition that yields no marginal information | inspection, recorded in the post-implementation report |
| GOV-ARTIFACT-APPROVAL-001 | Each of the three protected-file corrections carries a narrative-artifact-approval packet with presented_to_user true and a matching content hash | the three approval packets, cited by path in the report |
| GOV-FILE-BRIDGE-AUTHORITY-001 | The do-not-re-enable mandates, the manual-scan fallback, and the cross-harness-trigger operating mode are unchanged | diff inspection, recorded in the report |
| DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001 | The post-implementation report carries this mapping with executed verification evidence | the post-implementation report |

Execution: the post-implementation report records the exact grep commands run over the three files, the diff confirming only framing and lesson text changed, and the three approval-packet paths.

## Acceptance Criteria

- IP-1 through IP-3 landed: the poller-retirement passages in all three files name the blind, activity-independent mechanism and no longer present token volume as the lesson or as an operational metric.
- The incident facts (the roughly tenfold spawn increase, the blind three-minute interval, the spawn counts) are retained.
- No do-not-re-enable mandate, no manual-scan fallback text, and no cross-harness-trigger operating-mode text is removed or weakened.
- Each protected-file Write carries an owner-approved narrative-artifact-approval packet.
- Both bridge preflights pass on the post-implementation report.

## Option Rationale

Correcting the framing in place was selected over two alternatives. Deleting the incident history was rejected because the incident is real and its facts are valuable. Leaving the rule files unchanged and relying only on DELIB-S358-TOKEN-CONCERN-IS-WASTE-NOT-VOLUME to correct forward was rejected because the rule files are auto-loaded every session and the deliberation is not, so the distortion would keep reaching reasoning. Scoping to the three rule files, and deferring the MemBase specifications to a named follow-on, was selected over a single all-surfaces proposal because the rule files are the auto-loaded surface where the distortion actively misdirects reasoning; a bounded proposal lands the high-priority correction faster, and the MemBase specifications need individual per-spec reading that should not gate the rule-file fix.

## Risks / Rollback

- Risk: a correction inadvertently weakens a do-not-re-enable mandate. Mitigation: the corrections touch only the framing and lesson sentences; the mandates are explicitly out of scope; the post-implementation diff confirms it; the acceptance criteria check it.
- Risk: the corrected wording drifts from the DELIB-S358 framing. Mitigation: each correction is checked against DELIB-S358-TOKEN-CONCERN-IS-WASTE-NOT-VOLUME and DELIB-S312-DETERMINISTIC-SERVICES-PRINCIPLE, and the owner approves each protected-file packet.
- Rollback: revert the three files; each is an independent, self-contained text correction with no schema, code, or migration dependency.

## Recommended Commit Type

`docs` - the change corrects governance and rule narrative text in three documentation-class rule files. No code, test, or capability surface changes.

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
