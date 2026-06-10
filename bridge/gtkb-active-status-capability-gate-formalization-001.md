NEW
author_identity: prime-builder/codex/A
author_harness_id: A
author_session_context_id: codex-gtkb-pb-2026-06-02
author_model: GPT-5 Codex
author_model_version: 2026-06-02
author_model_configuration: reasoning=high

bridge_kind: prime_proposal
Document: gtkb-active-status-capability-gate-formalization
Project Authorization: PAUTH-WI-4213-ACTIVE-STATUS-CAPABILITY-GATE
Project: PROJECT-GTKB-ROLE-STATUS-ORTHOGONALITY-DISPATCH
Work Item: WI-4213
target_paths: ["groundtruth.db", ".groundtruth/formal-artifact-approvals/2026-06-02-ADR-ROLE-STATUS-ORTHOGONALITY-001-v2.json", ".groundtruth/formal-artifact-approvals/2026-06-02-DCL-SINGLE-ACTIVE-PER-ROLE-DISPATCH-001-v2.json", ".groundtruth/formal-artifact-approvals/2026-06-02-REQ-HARNESS-REGISTRY-001-v3.json"]

# Implementation Proposal: Active-Status Capability Gate Formalization

## Summary

Complete the formal-authority slice of WI-4213 by revising the durable role/status specifications so active status means bridge-event reception capability, not merely registered harness presence or durable role assignment.

This formalization reconciles three stale authority surfaces before code implementation: ADR-ROLE-STATUS-ORTHOGONALITY-001, DCL-SINGLE-ACTIVE-PER-ROLE-DISPATCH-001, and REQ-HARNESS-REGISTRY-001. It must explicitly allow a harness to retain a durable role while inactive when it lacks event-driven hook capability. Antigravity C is the concrete case: it may hold prime-builder role while inactive/registered because event_driven_hooks is false, and it must not be selected for event-driven bridge dispatch.

## Prior Deliberations

- WI-4213 records the S384 correction: active is capability-gated on bridge-event reception; role/status are orthogonal; WI-3513 remains the durable write-contention fix.
- DELIB-2813 records the current owner directive to continue until the listed items are completed and supports the narrow PAUTH cited above.
- Prior role/status bridge context established single-active-per-role dispatch and the need to keep write-contention concerns out of this slice.


### Helper-suggested candidates

<!-- Pre-populated by helper; review and prune. -->
- DA: `DELIB-2563` — seed=search; bridge_thread; Loyal Opposition Verdict - Role/Status Orthogonality Dispatch Slice 2 Resolver
- DA: `DELIB-2368` — seed=search; bridge_thread; Loyal Opposition Review - Release-Candidate Gate Managed Skill
- DA: `DELIB-2577` — seed=search; bridge_thread; Loyal Opposition Verdict - Role/Status Orthogonality Dispatch Model Scoping
- DA: `DELIB-2562` — seed=search; bridge_thread; Loyal Opposition Verification - Role/Status Orthogonality Dispatch Slice 2 Resol
- DA: `DELIB-2796` — seed=search; bridge_thread; Loyal Opposition Verification - Role/Status Orthogonality Dispatch Slice 2 Resol

## Owner Decisions / Input

No new owner decision is required. The active PAUTH authorizes formal artifact mutation, governance evidence, source, test, and harness-registry lifecycle changes for WI-4213 while preserving normal bridge GO, implementation-start packet, post-implementation report, and Loyal Opposition verification gates.

## Specification Links

- ADR-ROLE-STATUS-ORTHOGONALITY-001
- DCL-SINGLE-ACTIVE-PER-ROLE-DISPATCH-001
- REQ-HARNESS-REGISTRY-001
- GOV-HARNESS-ROLE-PORTABILITY-001
- GOV-GTKB-MULTI-HARNESS-ROLE-CONFIG-001
- GOV-FILE-BRIDGE-AUTHORITY-001
- DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001
- DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001
- DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001
- GOV-SOURCE-OF-TRUTH-FRESHNESS-001
- GOV-STANDING-BACKLOG-001
- ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001
- DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001
- GOV-ARTIFACT-ORIENTED-GOVERNANCE-001

## Requirement Sufficiency

Existing owner direction and WI-4213 are sufficient to formalize the active-status capability gate. The formal slice is intentionally limited to revising existing authority records and creating required approval packets; code and registry implementation will be handled by a follow-up bridge thread after this authority is settled.

## Code Quality Baseline

| Rule ID | Applies? | Compliance plan | Verification | Waiver / N/A reason |
|---|---|---|---|---|
| CQ-SECRETS-001 | Yes | Formal text and approval packets only; no credentials or environment values. | Helper credential scan and packet review. | |
| CQ-PATHS-001 | Yes | Mutate only groundtruth.db and listed in-root formal approval packets. | Applicability preflight and git diff review. | |
| CQ-COMPLEXITY-001 | Yes | Add capability-gate language to existing specs rather than creating a new authority family. | Spec diff/content review. | |
| CQ-CONSTANTS-001 | Yes | Reconcile registered, inactive, active, durable role, and event_driven_hooks terminology explicitly. | DB query and spec text review. | |
| CQ-SECURITY-001 | Yes | Preserve no-dispatch-to-non-event-capable-harnesses as the safe default. | Formal assertion review. | |
| CQ-DOCS-001 | Yes | Keep formal text concise and implementation-test obligations explicit. | Spec content review. | |
| CQ-TESTS-001 | Yes | Define implementation test obligations in DCL and REQ so the follow-up implementation can verify them. | Clause preflight and later implementation tests. | |
| CQ-LOGGING-001 | No | This formalization slice does not change runtime logging. | N/A. | Formal artifact mutation only. |
| CQ-VERIFICATION-001 | Yes | Verify DB rows, spec versions, approval packet existence, and packet hashes before implementation report. | groundtruth_kb spec/DB query plus file hash checks. | |

## Scope

In scope:

- Revise ADR-ROLE-STATUS-ORTHOGONALITY-001 to state that role assignment and active status are orthogonal, and active status requires bridge-event reception capability.
- Revise DCL-SINGLE-ACTIVE-PER-ROLE-DISPATCH-001 to preserve single-active-per-role dispatch while excluding non-event-capable harnesses from active dispatch selection.
- Revise REQ-HARNESS-REGISTRY-001 to allow a durable role to remain on an inactive/registered harness and to remove stale active-only role-retention language.
- Create formal approval packets for those revisions under .groundtruth/formal-artifact-approvals.

Out of scope:

- Source-code implementation, registry regeneration, mode-switch transaction changes, dispatch resolver changes, or tests.
- Any multi-active dispatch redesign.
- WI-3513 bridge write-contention serialization; WI-3513 remains the durable contention fix.
- Deleting or retiring any role assignment records.

## Acceptance Criteria

- ADR-ROLE-STATUS-ORTHOGONALITY-001 states active status is capability-gated by bridge-event reception.
- DCL-SINGLE-ACTIVE-PER-ROLE-DISPATCH-001 preserves single-active-per-role event dispatch and excludes non-event-capable harnesses from active dispatch selection.
- REQ-HARNESS-REGISTRY-001 allows inactive/registered harnesses to retain durable roles when they lack event-driven hook capability.
- Formal approval packets exist for each revised record and cite DELIB-2813 or the carried S384 owner decision evidence.
- No source or runtime registry behavior is changed in this formalization slice.
- WI-4213 remains open after this slice until the follow-up registry/dispatch implementation is verified.

## Specification-Derived Verification Plan

- ADR-ROLE-STATUS-ORTHOGONALITY-001: query the DB/spec surface after mutation and verify the new version includes active-status capability-gate language.
- DCL-SINGLE-ACTIVE-PER-ROLE-DISPATCH-001: query the DB/spec surface after mutation and verify single-active event dispatch excludes non-event-capable harnesses.
- REQ-HARNESS-REGISTRY-001: query the DB/spec surface after mutation and verify durable role retention is allowed for inactive/registered no-hook harnesses.
- GOV-FILE-BRIDGE-AUTHORITY-001: run bridge preflights and preserve the bridge/INDEX.md entry for this proposal and implementation report.
- DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001: include DB query outputs and approval packet hash checks in the post-implementation report.

## Pre-Filing Preflight

Manual catch-22 check performed before filing: this proposal cites role/status specs, registry requirement, bridge authority, project linkage, source-of-truth freshness, standing backlog, and artifact-oriented governance specs triggered by the target paths and implementation proposal content.

The bridge artifact is filed under bridge/, and the live queue state is the bridge/INDEX.md entry for gtkb-active-status-capability-gate-formalization; the helper inserts the NEW: bridge/gtkb-active-status-capability-gate-formalization-001.md line at the top of that document entry without deleting or rewriting prior versions.

After filing, Prime Builder will run applicability, clause, and citation-freshness preflights and will revise if any blocking gap is reported.

## Risk And Rollback

Risk: stale wording may remain in one formal surface and cause implementation ambiguity. Mitigation: revise all three named authority records together and verify by DB query before filing the implementation report. Rollback creates superseding formal revisions or reverts the DB/spec rows under governance; bridge audit files remain append-only.
