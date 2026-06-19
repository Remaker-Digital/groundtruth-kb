NEW
author_identity: prime-builder/codex-automation
author_harness_id: A
author_session_context_id: 019ee20d-e968-7b40-a570-f38cd6a7e3ef
author_model: gpt-5-codex
author_model_version: 2026-06-19
author_model_configuration: Codex desktop automation session; approval_policy=never; autonomous Prime Builder

# WI-4591 Bridge Disposition Workflow - Slice 1

bridge_kind: prime_proposal
Document: agent-disposition-wi4591-bridge-disposition-workflow-slice1
Version: 001
Status: NEW
Author: Prime Builder (Codex)
Date: 2026-06-19 UTC

Project Authorization: PAUTH-PROJECT-AGENT-DISPOSITION-PROTOCOL-ENFORCEMENT-UMBRELLA
Project: PROJECT-AGENT-DISPOSITION-AND-PROTOCOL-ENFORCEMENT
Work Item: WI-4591

target_paths: ["groundtruth-kb/src/groundtruth_kb/bridge/disposition.py", "groundtruth-kb/src/groundtruth_kb/bridge/notify.py", ".claude/skills/bridge/helpers/scan_bridge.py", "groundtruth-kb/tests/test_bridge_notify.py", "platform_tests/scripts/test_scan_bridge.py"]

implementation_scope: source,test
requires_review: true
requires_verification: true
kb_mutation_in_scope: false
external_mutation_in_scope: false
production_deployment_in_scope: false
credential_lifecycle_change_in_scope: false

---

## Summary

This child proposal requests a narrow first implementation slice for `WI-4591`: define one deterministic bridge disposition matrix and use it to keep Prime Builder, Loyal Opposition, dispatcher, and manual scan actionability aligned across `ADVISORY`, `NO-GO`, `NEW`, `REVISED`, `GO`, and `VERIFIED` states.

The current live code already shows why this is needed: `.claude/skills/bridge/helpers/scan_bridge.py` treats `ADVISORY` as Prime-actionable for advisory disposition, while `groundtruth-kb/src/groundtruth_kb/bridge/notify.py` contains mixed comments and routing language around whether `ADVISORY` is actionable or dispatchable. This proposal does not decide new policy; it asks to encode the owner-approved `WI-4591` workflow as a shared matrix and tests so future agents get the same answer from startup scans, dispatcher routing, and manual bridge helpers.

## Code Quality Baseline

| Rule ID | Applies? | Compliance plan | Verification | Waiver / N/A reason |
|---|---|---|---|---|
| CQ-SECRETS-001 | Yes | Use synthetic bridge statuses and no credential-shaped fixtures. | Bridge helper credential scan and focused review. | |
| CQ-PATHS-001 | Yes | Restrict implementation to declared bridge runtime/helper/test paths. | Applicability preflight, target-path review, and no retired index check. | |
| CQ-COMPLEXITY-001 | Yes | Centralize status/actionability decisions in a small matrix module. | Tests assert dispatcher/helper parity. | |
| CQ-CONSTANTS-001 | Yes | Define statuses, recipient roles, dispatchability, and reason codes once. | Stable reason-code tests. | |
| CQ-SECURITY-001 | Yes | Fail closed for wrong-role work and ambiguous mutating continuation states. | Negative tests for PB/LO wrong-role cases. | |
| CQ-DOCS-001 | Yes | Keep documentation to bridge proposal/report and concise inline module docs if needed. | Loyal Opposition review. | |
| CQ-TESTS-001 | Yes | Add/extend focused tests for matrix behavior and scan/notify parity. | `python -m pytest groundtruth-kb/tests/test_bridge_notify.py platform_tests/scripts/test_scan_bridge.py -q --tb=short`. | |
| CQ-LOGGING-001 | Yes | Return structured disposition reasons suitable for status surfaces; no new logging sink in this slice. | Tests assert reason fields. | |
| CQ-VERIFICATION-001 | Yes | Run spec-derived pytest, Ruff check, Ruff format-check, bridge preflights, and retired index absence check before reporting implementation. | Commands listed in the verification plan. | |

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` - live versioned bridge files and role-correct processing govern implementation workflow.
- `GOV-FILE-BRIDGE-PROTOCOL-001` - bridge state transitions must have deterministic actionability for each role.
- `.claude/rules/file-bridge-protocol.md` - Prime Builder acts on latest `GO`/`NO-GO`; Loyal Opposition acts on latest `NEW`/`REVISED`; `VERIFIED` is terminal; `ADVISORY` requires Prime/owner disposition without headless implementation dispatch.
- `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001` - project authorization must not bypass bridge proposal/review/verification lifecycle.
- `REQ-HARNESS-REGISTRY-001` - role identity must drive actionability decisions rather than vendor/model assumptions.
- `SPEC-AUQ-POLICY-ENGINE-001` - advisory and owner-input states must route to owner-visible decisions instead of ambiguous queue work.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - implementation proposals must cite applicable requirements.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - proposal must link project, work item, authorization, and target paths explicitly.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - verification must derive from cited requirements.
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` - implementation must stay within the active PAUTH envelope.
- `DCL-PROJECT-AUTHORIZATION-ENVELOPE-001` - PAUTH mutation classes and forbidden operations define allowed scope.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` - bridge disposition decisions should preserve durable traceability.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` - durable artifacts should govern work selection and actionability.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - advisory and blocked states should route to lifecycle-appropriate follow-up rather than stale queue ambiguity.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - implementation and tests must stay inside the GT-KB root.
- `GOV-STANDING-BACKLOG-001` - `WI-4591` is an active ranked child work item under the current project backlog.

## Prior Deliberations

- `DELIB-20263455` - owner-approved Agent Disposition and Protocol Enforcement closeout planning, ranked work items, and umbrella formulation; includes `WI-4591` for disposition workflow normalization.
- `DELIB-0862` - bridge-first governance and historical warning against ambiguous scope-only GO artifacts.
- `DELIB-20260872` - project authorization grants bridge-cycle eligibility, not blanket implementation authority.
- `DELIB-2258` - implementation-start and work-intent gating are durable safety controls for protected mutations.
- `DELIB-20261178` - bridge/status authority must come from live versioned artifacts and current dispatcher state, not stale summaries.
- `bridge/agent-disposition-protocol-enforcement-umbrella-004.md` - planning-only GO that approved the ranked child sequence and requires concrete child proposals.
- `bridge/agent-disposition-wi4588-protected-mutation-guard-slice1-004.md` - VERIFIED mutation guard that reinforces wrong-role/fail-closed behavior for protected implementation work.
- `bridge/agent-disposition-wi4589-external-mutation-gate-slice1-001.md` - pending child proposal that covers external-mutation gating; this `WI-4591` slice remains separate and focuses on bridge status disposition.
- `bridge/agent-disposition-wi4590-post-action-receipts-slice1-004.md` - VERIFIED receipt contract that later visibility surfaces can cite when disposition actions produce mutation evidence.

## Owner Decisions / Input

- `DELIB-20263455` - owner directed the Agent Disposition and Protocol Enforcement project and ranked `WI-4591` as the disposition-workflow normalization child item.
- `PAUTH-PROJECT-AGENT-DISPOSITION-PROTOCOL-ENFORCEMENT-UMBRELLA` - active bounded project authorization includes `WI-4591`; allows source/test/config/protected narrative/governance evidence/MemBase update/project artifact link classes and forbids production deployment, credential lifecycle change, bridge protocol bypass, self-review, retired bridge index recreation, and unapproved formal artifact mutation.
- `bridge/agent-disposition-protocol-enforcement-umbrella-004.md` - Loyal Opposition approved the planning sequence and required each child slice to receive its own concrete review.

No new owner decision is required for this proposal. The proposed slice encodes existing disposition policy in code and tests; it does not create a new status token, revive `bridge/INDEX.md`, or execute implementation without Loyal Opposition GO.

## Requirement Sufficiency

Existing requirements are sufficient for this first slice. The work item and linked bridge/file-protocol rules define the needed state matrix: Prime Builder continuation is limited to latest `GO`/`NO-GO`; Loyal Opposition review is limited to latest `NEW`/`REVISED`; `VERIFIED` is terminal; `ADVISORY` is not headless implementation dispatch and must surface for Prime/owner disposition.

This proposal is intentionally narrower than full `WI-4591` completion. It supplies the shared classifier and parity tests. Later child proposals may wire richer status/startup/dashboard/wrap reporting once the matrix is verified.

## Proposed Implementation

Add `groundtruth-kb/src/groundtruth_kb/bridge/disposition.py` with a small shared bridge disposition model:

- status tokens: `NEW`, `REVISED`, `GO`, `NO-GO`, `VERIFIED`, `ADVISORY`, `DEFERRED`, `WITHDRAWN`, and unknown fallback;
- recipient roles: `prime-builder`, `loyal-opposition`, and non-dispatchable owner/advisory handling;
- decision fields: `actionable`, `dispatchable`, `owner_visible`, `terminal`, `reason_code`, and `next_action`;
- deterministic matrix entries for wrong-role, terminal, advisory, and implementation-continuation cases;
- a helper that returns explicit block reasons when a role is looking at a status it must not process.

Update `groundtruth-kb/src/groundtruth_kb/bridge/notify.py` to call the shared matrix for dispatcher actionability while preserving existing GO terminal-kind handling and non-dispatchability constraints.

Update `.claude/skills/bridge/helpers/scan_bridge.py` to use the same status matrix for manual Prime/Loyal Opposition scans while preserving its current GO implementation-packet activatability check and archived-thread exclusion behavior.

Extend tests in `groundtruth-kb/tests/test_bridge_notify.py` and `platform_tests/scripts/test_scan_bridge.py` to lock parity:

- `NEW` and `REVISED` are Loyal Opposition review work, not Prime Builder implementation work;
- `GO` and `NO-GO` are Prime Builder continuation work, with GO still subject to terminal-kind and implementation-packet checks;
- `VERIFIED`, `DEFERRED`, and `WITHDRAWN` are terminal/non-actionable for both roles;
- `ADVISORY` is owner-visible Prime disposition work but not headless implementation dispatch;
- wrong-role decisions return stable reason codes;
- dispatcher and manual scan helper agree on status actionability for each role except where documented GO activatability and archive filters add extra constraints.

## Explicit Non-Scope

- No new bridge status token.
- No `bridge/INDEX.md` recreation or retired aggregate queue artifact.
- No source mutation outside the declared target paths.
- No formal GOV/SPEC/PB/ADR/DCL mutation.
- No production deployment, credential lifecycle change, or external-service mutation.
- No claim that `WI-4591` is complete after this slice; follow-on slices may be needed for startup/status/dashboard/wrap visibility.

## Spec-Derived Verification Plan

- `GOV-FILE-BRIDGE-AUTHORITY-001`, `GOV-FILE-BRIDGE-PROTOCOL-001`, and `.claude/rules/file-bridge-protocol.md`: tests must verify role-correct actionability for `NEW`, `REVISED`, `GO`, `NO-GO`, `VERIFIED`, `ADVISORY`, `DEFERRED`, and `WITHDRAWN`.
- `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001`: tests must show project/bridge processing still routes through status and role checks rather than broad PAUTH bypass.
- `REQ-HARNESS-REGISTRY-001`: tests must treat roles as data and avoid vendor/model-specific actionability.
- `SPEC-AUQ-POLICY-ENGINE-001`: tests must show `ADVISORY` yields owner-visible disposition rather than headless implementation dispatch.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`, `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001`, and `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`: proposal and implementation report must carry project metadata, linked specs, spec-to-test mapping, command evidence, and observed results.
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` and `DCL-PROJECT-AUTHORIZATION-ENVELOPE-001`: implementation must stay inside the active PAUTH and avoid forbidden operations.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001`: tests must use in-root fixtures only; `Test-Path bridge/INDEX.md` must remain `False`.

Implementation-report commands:

```text
python -m pytest groundtruth-kb/tests/test_bridge_notify.py platform_tests/scripts/test_scan_bridge.py -q --tb=short
python -m ruff check groundtruth-kb/src/groundtruth_kb/bridge/disposition.py groundtruth-kb/src/groundtruth_kb/bridge/notify.py .claude/skills/bridge/helpers/scan_bridge.py groundtruth-kb/tests/test_bridge_notify.py platform_tests/scripts/test_scan_bridge.py
python -m ruff format --check groundtruth-kb/src/groundtruth_kb/bridge/disposition.py groundtruth-kb/src/groundtruth_kb/bridge/notify.py .claude/skills/bridge/helpers/scan_bridge.py groundtruth-kb/tests/test_bridge_notify.py platform_tests/scripts/test_scan_bridge.py
python scripts/bridge_applicability_preflight.py --bridge-id agent-disposition-wi4591-bridge-disposition-workflow-slice1
python scripts/adr_dcl_clause_preflight.py --bridge-id agent-disposition-wi4591-bridge-disposition-workflow-slice1
Test-Path bridge/INDEX.md
```

## Acceptance Criteria

- Bridge status/role disposition is represented by one shared matrix instead of duplicated status assumptions.
- Dispatcher actionability and manual bridge scan actionability agree for `NEW`, `REVISED`, `GO`, `NO-GO`, `VERIFIED`, `ADVISORY`, `DEFERRED`, and `WITHDRAWN`, with documented exceptions for GO activatability and archived-thread filtering.
- Wrong-role cases return stable block reasons suitable for startup/status surfaces.
- `ADVISORY` is owner-visible Prime disposition work but is not headless implementation dispatch.
- Tests execute without reviving retired bridge index artifacts or mutating live bridge state.

## Risk / Rollback

The main risk is changing dispatcher actionability in a way that suppresses legitimate bridge work. The implementation should mitigate this by adding the shared matrix first, preserving existing behavior through parity tests, and making any intended differences explicit in reason codes.

Rollback is path-local removal of the new matrix module and restoration of the small call-site changes in `notify.py` and `scan_bridge.py` before downstream visibility surfaces consume the API.

## Bridge Filing

This proposal is filed under `bridge/` as the first status-bearing numbered bridge file for `agent-disposition-wi4591-bridge-disposition-workflow-slice1`; no prior version is deleted or rewritten. Dispatcher/TAFE state plus the numbered file chain are the live workflow state per `GOV-FILE-BRIDGE-AUTHORITY-001`.

## Recommended Commit Type

`feat:` - the approved implementation would add a shared bridge disposition matrix plus dispatcher/helper parity tests.

---

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
