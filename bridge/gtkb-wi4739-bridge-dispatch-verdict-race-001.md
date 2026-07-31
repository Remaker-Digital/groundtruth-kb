NEW

# gtkb-wi4739-bridge-dispatch-verdict-race - serialize same-document verdict dispatch

bridge_kind: prime_proposal
Document: gtkb-wi4739-bridge-dispatch-verdict-race
Version: 001
Author: Prime Builder (Codex)
Date: 2026-06-29T09:17:28Z

author_identity: prime-builder/codex/A
author_harness_id: A
author_session_context_id: 019f129d-1398-7c51-a127-3c4d40670d6d
author_model: GPT-5 Codex
author_model_version: current Codex runtime
author_model_configuration: Auto-builder autonomous Prime Builder run

Project Authorization: PAUTH-PROJECT-HARNESS-PARITY-PHASE-2-IMPLEMENTATION-2026-06-29
Project: PROJECT-HARNESS-PARITY-PHASE-2
Work Item: WI-4739

target_paths: ["scripts/cross_harness_bridge_trigger.py", "scripts/single_harness_bridge_dispatcher.py", "scripts/gtkb_bridge_writer.py", "platform_tests/scripts/test_cross_harness_bridge_trigger.py", "platform_tests/scripts/test_single_harness_bridge_dispatcher.py", "platform_tests/scripts/test_gtkb_bridge_writer.py"]

implementation_scope: protocol source test
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

---

## Summary

Fix `WI-4739` by making the bridge dispatcher and bridge writer enforce the invariant that one status-bearing bridge document version can have only one active writer path. The motivating defect was a multi-LO dispatch race where two Loyal Opposition harnesses processed the same `NEW` version and both wrote `-002`, causing the correct NO-GO to be lost and leaving a phantom GO that implementation-start would later reject.

The intended behavior is not to disable useful parallel dispatch. It is to preserve parallelism across different bridge documents while proving that a single document/version is assigned to at most one Loyal Opposition target in a dispatch cycle and that the governed bridge writer refuses same-version recreation on disk or from git history.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` — bridge status files are the governed handoff mechanism; this work protects append-only status authority from same-version races.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` — this implementation proposal links the defect fix to governing requirements and verification.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` — the proposal carries project authorization, project, and work item headers for implementation eligibility.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — completion must include spec-derived regression tests for dispatch selection and bridge writer monotonicity.
- `GOV-STANDING-BACKLOG-001` — `WI-4739` is the live governed backlog row for this defect.
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` — the active Phase 2 project authorization bounds which mutations are allowed.
- `DCL-CROSS-HARNESS-ENFORCEMENT-001` — the fix concerns cross-harness dispatcher behavior and must preserve role/action routing boundaries.
- `ADR-DISPATCHER-ARCHITECTURE-001` — dispatcher changes must preserve the governed dispatcher architecture rather than recreating retired poller behavior.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` — the work preserves bridge and backlog artifacts as durable coordination records instead of relying on scratch state.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` — the proposed implementation keeps the bridge artifact trail as the unit of coordination and verification.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` — completion must flow through implementation report and verification rather than treating source changes alone as terminal.

## Prior Deliberations

- `INTAKE-f8bc08a3` — Intake: Dispatcher/Bridge CLI as primary mutating UI for GT-KB artifact operations
- `INTAKE-e584f460` — Intake: All live agent mutations are bridge-first by default
- `INTAKE-b4928376` — Intake: Bridge review eligibility is harness-agnostic; durable role is a fallback, not a review/verdict gate
- `INTAKE-a815f782` — Intake: Bridge dispatch suppression scoped per bridge document (per-document lease)
- `INTAKE-2ce995f2` — Intake: Enable bounded parallel cross-harness auto-dispatch (supersede binary same-role active-session suppression)

These are relevant because the fix stays within the dispatcher/bridge CLI authority model, keeps bridge-first mutation discipline, does not introduce a same-harness review ban, and narrows bounded parallel dispatch only at the per-document contention boundary. The per-document lease intake is the closest prior design anchor: this proposal extends that intent from Prime implementation contention into Loyal Opposition verdict-write contention.

## Owner Decisions / Input

No new owner decision is required before Loyal Opposition review. Implementation is covered by `PAUTH-PROJECT-HARNESS-PARITY-PHASE-2-IMPLEMENTATION-2026-06-29`, whose owner decision is `DELIB-20260629-HARNESS-PARITY-PHASE-2-OWNER-DIRECTIVE`, and `WI-4739` is included in that authorization. Protected source/test mutation still requires this bridge proposal to receive GO, followed by implementation-start authorization.

## Requirement Sufficiency

Existing requirements sufficient. `WI-4739` states the defect and required outcome: dispatcher fan-out must not allow two LO harnesses to write the same next bridge version, and the no-index bridge writer must reject same-version overwrites. The active Phase 2 PAUTH supplies project-level authorization, while the linked bridge governance specs supply the mutation and verification constraints.

## Spec-Derived Verification Plan

Planned verification:

```text
python -m pytest platform_tests/scripts/test_cross_harness_bridge_trigger.py -q --tb=short
python -m pytest platform_tests/scripts/test_single_harness_bridge_dispatcher.py -q --tb=short
python -m pytest platform_tests/scripts/test_gtkb_bridge_writer.py -q --tb=short
python -m ruff check scripts/cross_harness_bridge_trigger.py scripts/single_harness_bridge_dispatcher.py scripts/gtkb_bridge_writer.py platform_tests/scripts/test_cross_harness_bridge_trigger.py platform_tests/scripts/test_single_harness_bridge_dispatcher.py platform_tests/scripts/test_gtkb_bridge_writer.py
python -m ruff format --check scripts/cross_harness_bridge_trigger.py scripts/single_harness_bridge_dispatcher.py scripts/gtkb_bridge_writer.py platform_tests/scripts/test_cross_harness_bridge_trigger.py platform_tests/scripts/test_single_harness_bridge_dispatcher.py platform_tests/scripts/test_gtkb_bridge_writer.py
```

Expected regression coverage:

- `GOV-FILE-BRIDGE-AUTHORITY-001`: tests prove a versioned bridge file cannot be recreated at the same version on disk or from git history.
- `DCL-CROSS-HARNESS-ENFORCEMENT-001` and `ADR-DISPATCHER-ARCHITECTURE-001`: tests prove multi-target dispatch partitions selected bridge documents so the same `NEW`/`REVISED` document/version is not sent to more than one LO target in one cycle.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`: the implementation report must map every test run above to the accepted behavior and call out any unrelated dirty-worktree failures separately.
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001`: implementation-start must authorize exactly the target paths listed in this proposal before source/test edits begin.

## Risk / Rollback

Primary risk is over-serialization: a too-broad guard could reduce useful LO parallelism. The implementation must therefore serialize only identical document/version assignments and preserve parallel work across distinct bridge documents. Secondary risk is hiding launch failures behind unchanged signatures; dispatch-state tests must preserve per-target observability.

Rollback is a single implementation commit revert plus removal of any filed implementation report if the report has not yet been reviewed. No MemBase or formal governance mutation is in scope for the implementation.

## Bridge Filing

This proposal is filed under `bridge/` as the next status-bearing numbered
bridge file for `gtkb-wi4739-bridge-dispatch-verdict-race`; no prior version is deleted or rewritten
(append-only). Dispatcher/TAFE state plus the numbered file chain are the live
workflow state per `GOV-FILE-BRIDGE-AUTHORITY-001`.

## Recommended Commit Type

fix - this closes a bridge-dispatch correctness defect and adds regression tests for the race.

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
