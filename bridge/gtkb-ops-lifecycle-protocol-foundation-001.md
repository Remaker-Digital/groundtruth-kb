NEW
author_identity: Codex Prime Builder
author_harness_id: A
author_session_context_id: codex-20260702-ops-dispatcher-synthesis
author_model: GPT-5
author_model_version: 2026-07-02
author_model_configuration: Codex desktop; E:/GT-KB; danger-full-access; approval-policy never; interactive role Prime Builder via ::init gtkb pb

# OPS Lifecycle And Bridge Protocol Foundation

bridge_kind: prime_proposal
Document: gtkb-ops-lifecycle-protocol-foundation
Version: 001
Date: 2026-07-02 UTC

Project Authorization: PAUTH-PROJECT-GTKB-OPS-LIFECYCLE-PROTOCOL-FOUNDATION-WI-4957
Project: PROJECT-GTKB-OPS-LIFECYCLE-PROTOCOL-FOUNDATION
Work Item: WI-4957

target_paths: [".claude/rules/file-bridge-protocol.md", ".claude/rules/canonical-terminology.md", "groundtruth-kb/src/groundtruth_kb/bridge", "groundtruth-kb/src/groundtruth_kb/activity/ops.py", "groundtruth-kb/src/groundtruth_kb/dispatcher", "groundtruth-kb/src/groundtruth_kb/db.py", "groundtruth-kb/src/groundtruth_kb/cli.py", "platform_tests/groundtruth_kb", "platform_tests/scripts", "groundtruth-kb/tests"]

implementation_scope: source+formal-artifact+schema+tests
requires_review: true
requires_verification: true
kb_mutation_in_scope: true

## Summary

Implement the OPS lifecycle and bridge protocol foundation from `independent-progress-assessments/CODEX-INSIGHT-DROPBOX/OPS-LIFECYCLE-DISPATCHER-MODEL-CONSOLIDATION-2026-07-02.md` as the parent model for dispatcher modernization. This Wave 1 child proposal embeds the required formalization and bounded implementation for OPS lifecycle vocabulary, bridge status behavior, quarantine, circuit breaker, diagnostic context, service logs, audit records, and validators.

This proposal does not implement dispatch lane utility ranking. It creates the lifecycle/protocol foundation that lane scoring must respect.

## Claim

Prime Builder proposes to formalize and implement the OPS lifecycle/bridge protocol substrate required before target-selection scoring can safely control production dispatch. The dispatcher must prove that an artifact/work item is lifecycle-eligible before it ranks candidate harness/model lanes.

## Requirement Sufficiency

Existing requirements sufficient.

Existing dispatcher and bridge authority specs are sufficient for proposal filing and implementation-start authorization. This slice still updates or creates formal ADR/DCL/GOV/spec/vocabulary records as implementation deliverables because the OPS consolidation identified protocol and schema gaps that must become governed artifacts.

The governing owner decisions authorize embedded formalization inside Wave 1 child implementation proposals rather than a separate formalization-only gate.

## In-Root Placement Evidence

All implementation outputs, generated artifacts, tests, and formalization side effects for this proposal remain under the GT-KB project root `E:/GT-KB`. The status-bearing bridge proposal is filed under `E:/GT-KB/bridge/gtkb-ops-lifecycle-protocol-foundation-001.md`. No Agent Red application source or external archive path is in scope.

## OPS Consolidation Integration

This proposal directly implements the OPS consolidation slices:

- Slice 1: vocabulary and state model specs for registration_state, dispatch_state, health_state, quarantine reason codes, GO dispatch-delay reason codes, and OPS remediation dispositions.
- Slice 2: bridge protocol extensions for NO-ACTION, LO routing, corrected GO fresh authority, work_item_sequence_number, prior GO non-dispatchability, and clean implementation-facing context.
- Slice 3: dispatcher quarantine and circuit breaker behavior, including third-NO-ACTION circuit breaker, sequence mismatch quarantine, claim release, and OPS diagnosis work item creation.
- Slice 4: OPS proposal/verdict/after-action schema requirements.
- Slice 5: context packaging and TTL for OPS diagnosis work items.
- Slice 6: service logs, audit records, and dashboard/audit projection foundations needed to keep ordinary bridge artifacts clean.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` - requires protected source/config changes to proceed through bridge proposal, GO, implementation report, and verification.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - requires project authorization, project, work item, and target path metadata.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - requires concrete governing specification links.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - requires verification mapped to cited specifications.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - keeps this platform work inside GT-KB and out of Agent Red application source.
- `SPEC-CENTRALIZED-DISPATCH-SERVICE-001` - dispatcher owns dispatch decisions and records dispatch activity.
- `ADR-DISPATCHER-ARCHITECTURE-001` - dispatcher is a persistent daemon-owned black-box service; harnesses are dispatch consumers only.

## Prior Deliberations

- `DELIB-20260702-DISPATCH-LANE-SCORING-EXTENDS-OPS-LIFECYCLE-CONSOLIDATION` - current lane-scoring deliberation extends the OPS lifecycle consolidation rather than competing with it.
- `DELIB-20260702-DISPATCH-OPS-CREATE-ACTUAL-PROJECT-WIS-BRIDGE-PROPOSALS` - owner selected actual governed project/work-item/bridge proposal creation.
- `DELIB-20260702-DISPATCH-OPS-WAVE1-THREE-CHILD-PROPOSALS` - Wave 1 uses three child implementation proposals.
- `DELIB-20260702-DISPATCH-OPS-WAVE1-CHILD-PROPOSALS-EMBED-FORMALIZATION` - child proposals embed required formalization with implementation.
- `DELIB-20260702-DISPATCH-LIFECYCLE-FIRST-SCORING-LAST-PRECEDENCE` - lifecycle eligibility precedes lane scoring.
- `DELIB-HARNESS-OPS-NO-ACTION-FIRST-CLASS-BRIDGE-STATUS-20260702` - NO-ACTION is a first-class PB-authored bridge status token.
- `DELIB-HARNESS-NO-ACTION-LO-ACTIONABLE-BRIDGE-ROUTING-20260702` - NO-ACTION routes to LO and is never PB implementation-dispatchable.
- `DELIB-HARNESS-NO-ACTION-PRIOR-GO-NONDISPATCHABLE-SUBSEQUENT-GO-FRESH-AUTHORITY-20260702` - NO-ACTION makes the prior GO non-dispatchable; later corrected GO is fresh authority.
- `DELIB-HARNESS-OPS-NO-ACTION-CIRCUIT-BREAKER-20260702` - third NO-ACTION creates circuit-breaker OPS diagnosis.
- `DELIB-HARNESS-WORK-ITEM-SEQUENCE-MISMATCH-OPS-QUARANTINE-20260702` - sequence mismatch triggers OPS quarantine.
- `DELIB-HARNESS-OPS-DIAGNOSTIC-CONTEXT-REQUIRED-FIELDS-20260702` - OPS diagnosis work items require diagnostic_context fields.
- `DELIB-ACTIVITY-LIFECYCLE-EVENTS-AUTHORITY-MEMBASE-20260702` - lifecycle events use append-only MemBase/KB authority with generated projections.

## Owner Decisions / Input

- `DELIB-20260702-DISPATCH-OPS-CREATE-ACTUAL-PROJECT-WIS-BRIDGE-PROPOSALS` - owner selected actual project, WI, and bridge proposal creation.
- `PAUTH-PROJECT-GTKB-OPS-LIFECYCLE-PROTOCOL-FOUNDATION-WI-4957` - active child-project authorization for this work item.

## Proposed Scope

- Create or update formal vocab/spec records for OPS lifecycle state, bridge status transitions, quarantine reason codes, dispatch-delay reason codes, remediation dispositions, producer/audit metadata, and diagnostic context.
- Update bridge protocol text so latest `NO-ACTION` is PB-authored, LO-actionable, non-PB-dispatchable, and makes the preceding GO non-dispatchable.
- Implement corrected GO behavior as fresh authority with prior rejection/supersession lineage restricted to audit/OPS surfaces.
- Implement sequence mismatch and third-NO-ACTION quarantine/circuit-breaker behavior that creates a separate OPS diagnosis work item and releases claims for failed workflow attempts.
- Add validators/templates/helpers for OPS proposal, GO, NO-GO, VERIFIED, PB after-action, NO-ACTION, and OPS diagnosis required fields.
- Add context-package freshness fields and retrieval instructions for OPS diagnosis work items.
- Add focused tests for bridge routing, lifecycle transitions, quarantine, service-log/audit projection, and clean implementation-facing context.

## Out Of Scope

- Lane-scoring registry/projection schema; that is `WI-4958`.
- Runtime utility ranking among lanes; follow-on after Wave 1 foundation.
- AUQ/headless hook launch hygiene; that is `WI-4959`.
- Production deployment or credential lifecycle changes.
- Agent Red application source mutation.

## Specification-Derived Verification Plan

| Spec | Verification |
| --- | --- |
| `SPEC-CENTRALIZED-DISPATCH-SERVICE-001` | Focused dispatcher/bridge tests prove lifecycle eligibility is evaluated before dispatch selection and that dispatcher audit/service-log records capture quarantine and OPS diagnosis events. |
| `ADR-DISPATCHER-ARCHITECTURE-001` | Tests prove the daemon/dispatcher remains the dispatch control plane and harnesses remain consumers only; no harness-to-harness OPS messaging path is introduced. |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | Target-path and preflight checks prove all mutations are in GT-KB platform paths and no Agent Red application source is changed. |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | Bridge proposal, GO, implementation report, and VERIFIED flow remain role-correct; NO-ACTION status tests prove PB/LO routing boundaries. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | Implementation report must map each protocol/vocabulary/schema change to targeted tests and preflights. |

Required focused checks include bridge status transition tests for NO-ACTION, dispatcher routing tests proving NO-ACTION routes only to LO, circuit-breaker tests proving third NO-ACTION creates OPS diagnosis and blocks the failed workflow, sequence mismatch quarantine tests, corrected GO fresh-authority tests, clean bridge artifact tests excluding OPS lineage from PB implementation context, OPS diagnostic_context validation tests, and vocabulary-governance tests.

## Acceptance Criteria

- Formal records define the OPS lifecycle vocabulary and bridge protocol extensions identified in the consolidation report.
- Latest `NO-ACTION` is LO-actionable and never PB implementation-dispatchable.
- A prior GO rejected by NO-ACTION is non-dispatchable; a later corrected GO is fresh implementation authority.
- Third NO-ACTION and sequence mismatch create separate OPS diagnosis work items with required diagnostic_context fields.
- Dispatcher quarantine state remains minimal: non-dispatchable flag plus reason code.
- Ordinary bridge artifacts remain free of OPS failure/recovery lineage; lineage lives in service logs/audit/OPS diagnosis surfaces.
- Targeted tests and preflights pass, with any pre-existing unrelated failures explicitly scoped.

## Risks / Rollback

Risk is moderate because this changes bridge lifecycle semantics and dispatcher actionability. The main risk is accidental role confusion or implementation-facing context noise. Mitigation: implement narrow validators and routing tests before broad runtime changes.

Rollback is a normal source/test revert plus append-only supersession or correction of any newly created formal records. Bridge files and MemBase audit/version history must not be deleted.

## Files Expected To Change

- `.claude/rules/file-bridge-protocol.md`
- `.claude/rules/canonical-terminology.md`
- `groundtruth-kb/src/groundtruth_kb/bridge/`
- `groundtruth-kb/src/groundtruth_kb/activity/ops.py`
- `groundtruth-kb/src/groundtruth_kb/dispatcher/`
- `groundtruth-kb/src/groundtruth_kb/db.py`
- `groundtruth-kb/src/groundtruth_kb/cli.py`
- `platform_tests/groundtruth_kb/`
- `platform_tests/scripts/`
- `groundtruth-kb/tests/`

## Recommended Commit Type

`feat`
