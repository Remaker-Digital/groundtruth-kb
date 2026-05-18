NEW

# Implementation Proposal - W1 Retirement-Machinery Correction (GTKB-GOVERNANCE-CORRECTION-S358-W1)

bridge_kind: implementation_proposal
Document: gtkb-s358-w1-retirement-machinery-correction
Version: 001
Author: Prime Builder (Claude, harness B)
Date: 2026-05-18 UTC
Session: S358

Project Authorization: PAUTH-PROJECT-GTKB-GOVERNANCE-CORRECTION-S358-S358-COMBINED-GOVERNANCE-CORRECTION-PROJECT-AUTHORIZATION
Project: PROJECT-GTKB-GOVERNANCE-CORRECTION-S358
Work Item: WI-3365

target_paths: ["groundtruth-kb/src/groundtruth_kb/project/lifecycle.py", "scripts/project_verified_completion_scanner.py", ".claude/hooks/project-completion-surface.py", ".codex/gtkb-hooks/project-completion-surface.py", ".claude/settings.json", ".codex/hooks.json", "groundtruth-kb/src/groundtruth_kb/cli.py", "groundtruth-kb/tests/test_project_artifacts.py", "platform_tests/hooks/test_project_completion_surface.py"]

## Problem

GOV-PROJECT-VERIFIED-COMPLETION-RETIREMENT-001 reached version 2 at S357 (Codex VERIFIED on bridge thread gtkb-gov-project-retirement-spec). v2 establishes that a backlog project and its project authorization complete and retire automatically once every explicitly-linked work item is VERIFIED, with no owner AskUserQuestion - owner-AUQ gates project start only. The specification landed, but the live project-completion machinery still embodies the v1 owner-confirmation model that v2 reversed. This is the W1 surface of the S358 drift-closure sweep: a correction that landed on the specification but not on every artifact enforcing the old rule.

Four concrete defects, each verified against the live code:

(1) Owner-confirmation gate in the lifecycle service. `complete_project_authorization()` in groundtruth-kb/src/groundtruth_kb/project/lifecycle.py (the function spans lines 414-525) carries a mandatory owner-confirmation gate at Step 2, lines 449-477: it requires an `owner_decision_deliberation_id` argument (a positional non-default parameter at line 417), resolves it, and raises ProjectLifecycleError unless the deliberation is `source_type='owner_conversation'` AND `outcome='owner_decision'` AND its text references the project or authorization. The docstring at lines 426-433 states "Owner confirmation is mandatory and auto-transition is prohibited." This directly contradicts v2.

(2) Owner-confirmation advisory in the surface hook pair. The project-completion-surface hook exists as a byte-identical pair, .claude/hooks/project-completion-surface.py and .codex/gtkb-hooks/project-completion-surface.py, each registered on the UserPromptSubmit event in .claude/settings.json and .codex/hooks.json respectively. The hook runs the read-only completion scanner and, when an authorization becomes completion-ready, injects a markdown instruction telling the agent to confirm completion with the owner via AskUserQuestion and stating "Do NOT auto-transition without owner confirmation." Both instructions contradict v2; the hook only advises and never transitions.

(3) Work-item gating set drift. v2 defines the gating set as the work items associated with a project via an explicit project-to-work-item membership link. Both the scanner (scripts/project_verified_completion_scanner.py, via `_included_work_item_ids()`) and the lifecycle service (`_authorization_work_item_ids()` and `complete_project_authorization()` Step 3) instead read the authorization envelope's `included_work_item_ids` list. The two definitions can diverge; v2's "Explicitly linked" definition is the membership link.

(4) No automatic-transition trigger and no completion CLI surface. No machinery transitions a completion-ready authorization automatically - the surface hook only advises. The `gt projects` CLI group has list, show, create, update, add-item, reorder, retire, link-bridge, authorize, authorizations, and revoke-authorization subcommands, but no completion subcommand; `complete_project_authorization()` has no CLI surface at all.

Two further artifacts lag the correction: GOV-PROJECT-VERIFIED-COMPLETION-RETIREMENT-001 v1 remains on the append-only record without an accurate re-framing as the Prime Builder error it was, and the S350 manufactured-variant error that produced v1 has no provenance deliberation. Separately, PROJECT-GTKB-LO-OPPORTUNITY-RADAR remains active under the DELIB-S353 keep-open choice, which the S358 owner directive supersedes.

## Claim

Make the live project-completion and retirement machinery match GOV-PROJECT-VERIFIED-COMPLETION-RETIREMENT-001 v2, and close the two lagging-artifact gaps and the LO-radar retirement, as one workstream:

- Strip the owner-confirmation gate from `complete_project_authorization()` and drop the mandatory `owner_decision_deliberation_id` parameter.
- Reconcile the work-item gating set in both the scanner and the lifecycle service from the authorization envelope's `included_work_item_ids` to v2's explicit project-to-work-item membership link.
- Add an automatic-transition service path and repurpose the surface hook pair from owner-confirmation advisory to automatic-transition trigger plus notification.
- Add a `gt projects complete-authorization` CLI subcommand for explicit invocation.
- Update the covering tests.
- Retire PROJECT-GTKB-LO-OPPORTUNITY-RADAR (the S358 owner directive supersedes the DELIB-S353 keep-open choice).
- Issue a v3 of GOV-PROJECT-VERIFIED-COMPLETION-RETIREMENT-001 re-framing v1 accurately as a Prime Builder error (the behavioral rule stays v2's; v3 corrects only the historical-record narrative).
- Archive a provenance deliberation for the S350 manufactured-variant error.

The behavioral requirement is unchanged: v2 is and stays the rule. W1 makes the machinery, the historical record, and one project's lifecycle faithfully reflect it.

## In-Root Placement Evidence

All target paths are in-root under the GT-KB project root: groundtruth-kb/src/, scripts/, .claude/hooks/, .codex/gtkb-hooks/, .claude/settings.json, .codex/hooks.json, and groundtruth-kb/tests/ and platform_tests/hooks/. This bridge proposal file resides under the bridge directory. No target path is outside the GT-KB project root, and no application path under applications/ is touched.

## Specification Links

- GOV-PROJECT-VERIFIED-COMPLETION-RETIREMENT-001 - the primary governing specification; v2 is the rule the live machinery must be made to match. W1 implements machinery, a historical-record correction (v3), and a project retirement so the platform faithfully enforces v2.
- GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001 - v2's owner-AUQ boundary cites this: owner-AUQ gates project start (authorization creation and approval), not completion. W1 strips only the completion-side gate and leaves the start-side authorization workflow intact.
- GOV-PROJECT-REQUIRES-LINKED-SPECIFICATIONS-001 - cited by v2 alongside the implementation-authorization spec for the project-start owner-AUQ boundary; W1 does not change project start.
- GOV-FILE-BRIDGE-AUTHORITY-001 - the bridge index and verdict files are canonical workflow state; this proposal is filed and reviewed through that workflow.
- DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001 - this proposal carries a complete, relevance-closed Specification Links section.
- DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001 - the post-implementation report will carry a spec-to-test mapping with executed verification evidence.
- GOV-ARTIFACT-APPROVAL-001 - the v3 of GOV-PROJECT-VERIFIED-COMPLETION-RETIREMENT-001 and the provenance deliberation are formal artifacts; each MemBase mutation is gated by a formal-artifact-approval packet presented to and approved by the owner before insertion.
- PB-ARTIFACT-APPROVAL-001 - the protected-artifact approval discipline applies to the v3 GOV spec and the provenance deliberation.
- DCL-ARTIFACT-APPROVAL-HOOK-001 - the formal-artifact-approval gate hook enforces the packet requirement on the GOV v3 and the deliberation insert.
- DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001 - this proposal carries the mandatory Project Authorization, Project, and Work Item header lines.
- ADR-ISOLATION-APPLICATION-PLACEMENT-001 - all target files are in-root; no application path under applications/ is touched.
- GOV-ARTIFACT-ORIENTED-GOVERNANCE-001 - the correction is preserved as durable artifacts: WI-3365, this proposal, the v3 GOV spec, the provenance deliberation, the updated tests, and the post-implementation report.
- ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001 - the fix preserves traceability across the work item, proposal, tests, GOV v3, deliberation, and report.
- DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001 - WI-3365 moves through open, in-progress, and verified lifecycle states.
- SPEC-AUQ-POLICY-ENGINE-001 - W1 removes the project-completion owner-AUQ gate. This does not conflict with the AUQ policy engine: that engine governs how owner decisions are collected when an owner decision is required; GOV-PROJECT-VERIFIED-COMPLETION-RETIREMENT-001 v2 establishes that project completion is not an owner-decision point. W1 removes a gate the governing spec says must not exist; it does not weaken AUQ enforcement for any decision class that still requires it.

## Prior Deliberations

A Deliberation Archive search was performed for project completion, retirement machinery, and the LO-radar project.

- DELIB-S358-GOVERNANCE-CORRECTION-PROJECT-AUTHORIZATION - the owner-decision deliberation (S358, owner_conversation) authorizing the combined governance-correction project. It records the W1 scope item by item, including the v3 re-framing, the provenance-deliberation archive, and the PROJECT-GTKB-LO-OPPORTUNITY-RADAR retirement. This proposal implements the W1 workstream.
- DELIB-S353-LO-OPPORTUNITY-RADAR-PROJECT-COMPLETION-2026-05-15 - the S353 owner decision (AskUserQuestion) that completed PAUTH-PROJECT-GTKB-LO-OPPORTUNITY-RADAR-SKILL-FIRST-SLICE and chose Option B: keep PROJECT-GTKB-LO-OPPORTUNITY-RADAR active as a program home for future slices. IP-6 of this proposal retires that project. This is a deliberate supersession: DELIB-S358 decision 4 explicitly reverses the DELIB-S353 Option-B choice (S358 owner ruling). The reversal is acknowledged here so the prior decision is not silently overridden.
- GOV-PROJECT-VERIFIED-COMPLETION-RETIREMENT-001 v2 supersession record - v2's own description records the v1-to-v2 supersession, the S357 owner directive, and the rejected alternatives (owner-confirmed retirement; using work_items.resolution_status). IP-7's v3 builds on that record by re-framing v1 accurately as a Prime Builder error.

No prior deliberation rejected the W1 machinery correction; the only prior decision W1 reverses is the DELIB-S353 keep-open choice, which DELIB-S358 supersedes by explicit owner directive.

## Owner Decisions / Input

- 2026-05-17, S357: the owner directed superseding GOV-PROJECT-VERIFIED-COMPLETION-RETIREMENT-001 via a v2 (v1 preserved append-only), approved v2 as written, and folded the v1-record correction and the machinery correction into one combined project. Captured in DELIB-S358-GOVERNANCE-CORRECTION-PROJECT-AUTHORIZATION (source_type=owner_conversation, outcome=owner_decision).
- 2026-05-17, S358: the owner directed standing up and running the combined four-workstream governance-correction project; W1 is the retirement-machinery-correction workstream, with scope items (strip the gate, reconcile to membership links, build the trigger and CLI, update tests, retire PROJECT-GTKB-LO-OPPORTUNITY-RADAR, issue the v3, archive the provenance deliberation) enumerated in DELIB-S358. The W1-W4 sequencing was collected via AskUserQuestion.
- 2026-05-17, S358: the owner directed retiring PROJECT-GTKB-LO-OPPORTUNITY-RADAR (DELIB-S358 decision 4), explicitly superseding the DELIB-S353 keep-open choice.
- Implementation-time owner approval is still required per artifact: the v3 of GOV-PROJECT-VERIFIED-COMPLETION-RETIREMENT-001 (IP-7) and the provenance deliberation (IP-8) are formal artifacts; each MemBase insertion requires a formal-artifact-approval packet presented to and approved by the owner before the write. This GO authorizes the workstream; it does not pre-grant the per-artifact approvals.

## Requirement Sufficiency

Existing requirements sufficient. GOV-PROJECT-VERIFIED-COMPLETION-RETIREMENT-001 v2 is the governing behavioral requirement; it is already owner-approved and in force. W1 calibrates the machinery, the historical record, and one project's lifecycle to match it. IP-7's v3 of that GOV spec corrects only the historical-record narrative (re-framing v1 accurately as a Prime Builder error); the behavioral rule remains v2's automatic-completion rule, unchanged. No new or revised behavioral requirement is created. No new or revised requirement is needed before implementation.

## Clause Scope Clarification (Not a Bulk Operation)

This proposal is not a bulk standing-backlog operation. It is a single machinery-correction workstream tracked by exactly one work item, WI-3365, an active member of PROJECT-GTKB-GOVERNANCE-CORRECTION-S358. No work-item state inventory, bulk transition, or backlog cleanup is performed. IP-6 retires exactly one project, PROJECT-GTKB-LO-OPPORTUNITY-RADAR, by explicit owner direction - a single project-lifecycle transition, not a bulk backlog operation. The proposal references the phrases "work item", "backlog", and "standing" only to describe the v2 gating-set definition and the project-completion machinery.

## Bridge INDEX Update Evidence

A NEW entry for gtkb-s358-w1-retirement-machinery-correction is inserted at the top of the bridge index, pointing at this -001 file. No prior bridge file and no prior index entry is deleted or rewritten.

## Proposed Scope

### IP-1: Strip the owner-confirmation gate from complete_project_authorization()

In groundtruth-kb/src/groundtruth_kb/project/lifecycle.py, remove Step 2 (the owner-confirmation gate, lines 449-477) from `complete_project_authorization()` and drop the mandatory `owner_decision_deliberation_id` parameter (line 417). Update the docstring (lines 423-434) to state the v2 automatic model. The function retains Step 1 (load the authorization; it must be active), Step 3 (re-run the readiness check - all gating work items VERIFIED), Step 4 (transition the authorization to completed), and Step 5 (retire the project iff no other active authorization remains). The Step 5 retirement `change_reason` is updated to drop the owner-decision reference. Callers and the return contract are updated accordingly.

### IP-2: Reconcile the work-item gating set to the v2 membership-link definition

v2 defines the gating set as the work items linked to a project via an explicit project-to-work-item membership link - the active rows of the project-to-work-item membership view (current_project_work_item_memberships). In scripts/project_verified_completion_scanner.py, change the gating-set source from the authorization envelope's `included_work_item_ids` (`_included_work_item_ids()`) to the project's active membership-link work items. In groundtruth-kb/src/groundtruth_kb/project/lifecycle.py, apply the same change to `_authorization_work_item_ids()` and `complete_project_authorization()` Step 3 so the lifecycle service and the scanner agree. The membership lookup is keyed on the authorization's project_id.

### IP-3: Add the automatic-transition path and repurpose the surface hook pair

In groundtruth-kb/src/groundtruth_kb/project/lifecycle.py, add a deterministic service method (working name `auto_complete_ready_authorizations()`) that scans active authorizations, and for every completion-ready authorization (all membership-linked work items VERIFIED) invokes the stripped `complete_project_authorization()`. It is idempotent: a completed authorization is no longer active and is not re-processed. Repurpose the byte-identical hook pair .claude/hooks/project-completion-surface.py and .codex/gtkb-hooks/project-completion-surface.py from owner-confirmation advisory to automatic-transition trigger plus notification: the hook invokes the automatic-transition path and emits a notification of what was auto-completed and retired, with no AskUserQuestion instruction and no "Do NOT auto-transition" text. The two copies remain byte-identical. The UserPromptSubmit registrations in .claude/settings.json and .codex/hooks.json are updated to match the repurposed hook (entry retained, description/intent corrected). The exact trigger-placement design (UserPromptSubmit retained vs. an alternative event) is settled in implementation; the invariant is an automatic transition with owner-visible notification and no owner-AUQ gate.

### IP-4: Add the gt projects complete-authorization CLI subcommand

In groundtruth-kb/src/groundtruth_kb/cli.py, add a `complete-authorization` subcommand to the `gt projects` group that invokes the stripped `complete_project_authorization()` for an explicitly named authorization. This is the explicit-invocation surface; it does not gate on an owner decision (consistent with v2). The existing `retire` subcommand (the owner-directed retirement path, outside the automatic gate per v2's Scope) is unchanged.

### IP-5: Update covering tests

In groundtruth-kb/tests/test_project_artifacts.py, delete the tests that assert the owner-confirmation gate behavior (the v1 model) and re-signature the completion/retirement tests to the stripped function signature and the membership-link gating set. In platform_tests/hooks/test_project_completion_surface.py, update the hook tests to the repurposed automatic-transition-plus-notification behavior. New tests cover the automatic-transition path, the membership-link gating set, and the CLI subcommand. The exact count of deleted vs. re-signatured tests is settled in implementation; the per-IP spec-derived test mapping is in the verification plan below.

### IP-6: Retire PROJECT-GTKB-LO-OPPORTUNITY-RADAR

Retire PROJECT-GTKB-LO-OPPORTUNITY-RADAR in MemBase via the project-lifecycle retirement path. This is an owner-directed retirement (DELIB-S358 decision 4), outside the automatic VERIFIED-gated path, and explicitly supersedes the DELIB-S353 Option-B keep-open choice. The retirement carries a change_reason citing DELIB-S358 and this bridge thread.

### IP-7: Issue v3 of GOV-PROJECT-VERIFIED-COMPLETION-RETIREMENT-001

Insert a version 3 of GOV-PROJECT-VERIFIED-COMPLETION-RETIREMENT-001 that re-frames v1 accurately as a Prime Builder error in its supersession narrative. The behavioral rule is unchanged from v2 (automatic completion and retirement, no owner-AUQ); v3 corrects only the historical-record framing of v1. v1 and v2 remain on the append-only record. The v3 insertion requires a formal-artifact-approval packet.

### IP-8: Archive a provenance deliberation for the S350 manufactured-variant error

Insert a Deliberation Archive record capturing the provenance of the S350 manufactured-variant error - the chain by which a manufactured AskUserQuestion variant produced the incorrect v1 of GOV-PROJECT-VERIFIED-COMPLETION-RETIREMENT-001. The deliberation insertion requires a formal-artifact-approval packet.

### Out of scope

W1 does not change the v2 behavioral rule. It does not touch the owner-directed `gt projects retire` path beyond leaving it intact. It does not perform backlog-data remediation of project-to-work-item link completeness (v2 Consequence 4 names that as separate work). It does not touch the four W4 mechanical-gate surfaces, the W2 Agent-Red GOV specs, or the W3 title fix. IP-7 and IP-8 are MemBase mutations through the formal-artifact-approval workflow, not file edits, and are not in target_paths.

## Specification-Derived Verification Plan

| Specification | Behavior verified | Test or verification |
|---|---|---|
| GOV-PROJECT-VERIFIED-COMPLETION-RETIREMENT-001 | complete_project_authorization() completes a ready authorization with no owner_decision_deliberation_id and no owner-confirmation gate | test in test_project_artifacts.py: completion succeeds without the parameter; the gate-assertion tests are deleted |
| GOV-PROJECT-VERIFIED-COMPLETION-RETIREMENT-001 | The gating set is the project's explicit membership-linked work items, not the authorization envelope's included_work_item_ids | test in test_project_artifacts.py covering the scanner and lifecycle membership-link gating set |
| GOV-PROJECT-VERIFIED-COMPLETION-RETIREMENT-001 | A completion-ready authorization is auto-completed and the project auto-retired when sole-active, with no owner AUQ | test of auto_complete_ready_authorizations() in test_project_artifacts.py |
| GOV-PROJECT-VERIFIED-COMPLETION-RETIREMENT-001 | The repurposed surface hook triggers the automatic transition and emits a notification with no AskUserQuestion instruction | test in test_project_completion_surface.py asserting the notification text and absence of AUQ/"Do NOT auto-transition" strings |
| GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001 | Project start (authorization creation and approval) is unchanged - the owner-AUQ start gate still applies | inspection plus existing start-path tests still pass, recorded in the report |
| GOV-PROJECT-VERIFIED-COMPLETION-RETIREMENT-001 | The gt projects complete-authorization CLI subcommand invokes the stripped completion path | CLI test in test_project_artifacts.py or the CLI test module |
| DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001 | The post-implementation report carries this mapping with executed test commands and observed results | the post-implementation report |
| GOV-ARTIFACT-APPROVAL-001 | The GOV v3 and the provenance deliberation each carry a formal-artifact-approval packet | the approval packets, cited by path in the report |

Execution: the post-implementation report records the exact pytest commands run over groundtruth-kb/tests/test_project_artifacts.py and platform_tests/hooks/test_project_completion_surface.py, a ruff check over the changed Python files, the MemBase evidence for IP-6/IP-7/IP-8, and both bridge preflights.

## Acceptance Criteria

- complete_project_authorization() no longer requires or accepts owner_decision_deliberation_id and completes a ready authorization with no owner-confirmation gate.
- The scanner and the lifecycle service both source the gating set from the project-to-work-item membership link, not included_work_item_ids.
- An automatic-transition path exists and auto-completes completion-ready authorizations; the surface hook pair triggers it and emits a notification with no AskUserQuestion instruction; the two hook copies remain byte-identical.
- The gt projects complete-authorization CLI subcommand exists and invokes the stripped completion path.
- The covering tests pass; the v1 owner-confirmation-gate tests are deleted; ruff is clean over the changed files.
- PROJECT-GTKB-LO-OPPORTUNITY-RADAR is retired in MemBase with a change_reason citing DELIB-S358.
- A v3 of GOV-PROJECT-VERIFIED-COMPLETION-RETIREMENT-001 exists, re-framing v1 as a Prime Builder error, with a formal-artifact-approval packet; the v2 behavioral rule is unchanged.
- A provenance deliberation for the S350 manufactured-variant error exists, with a formal-artifact-approval packet.
- Both bridge preflights pass on the post-implementation report.

## Option Rationale

For IP-3, folding the automatic-transition trigger into the repurposed surface hook was selected over a standalone new hook: the surface hook already runs the completion scanner on UserPromptSubmit, so repurposing it from advise to act-and-notify reuses the existing scan path and the existing registration, and avoids adding a second hook surface for the same concern. A separate service method (`auto_complete_ready_authorizations()`) keeps the deterministic work in the lifecycle service so the CLI subcommand and the hook share one implementation, consistent with the deterministic-services principle. For IP-7, a v3 (rather than editing v1 or v2 in place) preserves the append-only record: v1 and v2 stay, and v3 carries the corrected historical framing. For IP-6, the owner-directed retirement path was selected over the automatic VERIFIED-gated path because the owner directed the retirement explicitly (DELIB-S358 decision 4); v2's Scope places explicit owner-directed retirements outside the automatic gate.

## Risks / Rollback

- Risk: stripping the owner-confirmation gate removes a guard that callers depend on. Mitigation: the guard is exactly what v2 orders removed; callers and tests are updated in IP-1 and IP-5; the Step 3 readiness check (all gating work items VERIFIED) remains as the substantive precondition.
- Risk: the membership-link reconciliation changes which work items gate a given authorization. Mitigation: v2's "Explicitly linked" definition is the membership link; the scanner and lifecycle service are changed together so they agree; IP-5 tests cover the membership-link gating set.
- Risk: the automatic-transition trigger fires unexpectedly or repeatedly. Mitigation: the service method is idempotent - a completed authorization is no longer active; IP-5 tests cover idempotency.
- Risk: an IP-7 or IP-8 MemBase mutation lands without owner approval. Mitigation: each is gated by a formal-artifact-approval packet; the GO authorizes the workstream, not the per-artifact approvals.
- Rollback: revert the changed files; IP-6/IP-7/IP-8 are append-only MemBase mutations (a project retirement, a GOV v3, a deliberation) reversible by a further versioned correction. The IPs are independently revertible.

## Recommended Commit Type

`fix` - W1 repairs project-completion machinery that diverged from its governing specification, with no new external capability surface. The new `auto_complete_ready_authorizations()` path and the CLI subcommand are internal completions of the v2-mandated behavior, not a new product capability. If Codex assesses the CLI subcommand and automatic-transition path as net-new surface warranting `feat`, the post-implementation report will carry the recommended type matching the final diff stat per the Conventional Commits Type Discipline.

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
