NEW

# Enforce project authorization bounds at operation time

bridge_kind: prime_proposal
Document: gtkb-wi5178-operation-time-authority-enforcement
Version: 001
Author: Prime Builder (Codex A)
Date: 2026-07-16T19:02:43Z

author_identity: prime-builder/codex/A
author_harness_id: A
author_session_context_id: 019f5f6d-60cd-7040-b73f-c7d23757c4bc
author_model: Codex
author_model_version: GPT-5
author_model_configuration: Codex Desktop, Prime Builder, high reasoning

Project Authorization: PAUTH-PROJECT-GTKB-PLATFORM-MODERNIZATION-AUTHORITY-FOUNDATIONS-WI5178-PREDECESSOR-CLOSURE-20260715
Project: PROJECT-GTKB-PLATFORM-MODERNIZATION-AUTHORITY-FOUNDATIONS
Work Item: WI-5178

target_paths: ["config/governance/project-authorization-operation-taxonomy.toml", "groundtruth-kb/src/groundtruth_kb/governance/project_authorization_operation_time.py", "groundtruth-kb/tests/test_project_authorization_operation_time_enforcement.py", "scripts/implementation_authorization.py", "scripts/implementation_start_gate.py", "scripts/bridge_work_intent_registry.py", "platform_tests/scripts/test_implementation_authorization.py", "platform_tests/scripts/test_implementation_start_gate.py", "platform_tests/scripts/test_bridge_work_intent_registry.py"]

implementation_scope: source, configuration, test, protocol
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

---

## Summary

Complete WI-5178 by making the active project-authorization envelope
executable at every protected operation boundary. The deterministic evaluator,
taxonomy, and evaluator unit test already exist as untracked candidate bytes;
the evaluator's 13 tests pass. Integration remains incomplete: a 21-case
packet/start/work-intent selection currently reports 17 failures and 4 passes.
Current failures show that protected targets can start without PAUTH, mutation
classes and explicit forbidden operations are not enforced, packet-load drift
does not fail closed, complete PAUTH/taxonomy evidence is not serialized, and
work-intent acquire/extend/renew/reclassify can proceed without the required
operation-time decision.

Adopt the independently reviewable evaluator/taxonomy/test candidates and wire
them through authorization-packet creation and load, durable implementation
start, and work-intent mutations. The packet must bind the full versioned PAUTH
envelope, normalized target classifications, normalized requested operations,
evaluator/taxonomy hashes, and observed decisions. Every state-changing
boundary must re-evaluate current PAUTH and taxonomy bytes immediately before
effect and fail closed on missing authority, expiry, status/spec/envelope drift,
disallowed mutation classes, or forbidden operations.

This scope shares `scripts/implementation_authorization.py` with WI-5346 and
`scripts/bridge_work_intent_registry.py` with WI-5341/concurrent work. Proposal
parallelism is allowed; implementation must acquire the exact matching claim,
rehash all nine targets at start, and preserve or sequence around every foreign
hunk. The proposal does not authorize whole-file replacement or absorption of
unrelated work.

## Specification Links

- `DCL-PROJECT-AUTHORIZATION-OPERATION-TIME-ENFORCEMENT-001` — requires PAUTH bounds to be evaluated at each operation boundary immediately before effect.
- `DCL-PROJECT-AUTHORIZATION-ENVELOPE-001` — defines the complete, versioned PAUTH envelope that must be bound into implementation authority.
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` — requires protected implementation to carry active project authority and fail closed on authority drift.
- `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001` — forbids treating project-level PAUTH as a replacement for bridge GO, work-intent, or implementation-start gates.
- `DCL-CHANGE-CONTROLLED-ARTIFACT-EVALUABILITY-001` — requires the taxonomy and evaluator to be deterministic, inspectable, and hash-bound evidence.
- `GOV-FILE-BRIDGE-AUTHORITY-001` — governs the proposal/GO/claim/start/report/VERIFIED lifecycle and exact target scope.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` — requires the complete governing specification set in this proposal.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` — binds WI-5178 to its dedicated Authority Foundations PAUTH.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — requires executed evaluator and integration evidence before VERIFIED.
- `DCL-PROJECT-DEPENDENCY-ORDERING-001` — requires preservation/sequencing of WI-5346, WI-5341, and any other concurrent shared-file hunks.
- `GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001` — prohibits enforcement that weakens bridge, dispatcher, startup, or ordinary authorized operation behavior.
- `GOV-STANDING-BACKLOG-001` — keeps WI-5178 and its exact residual failures visible until independently verified and finalized.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` — requires all implementation, taxonomy, tests, and evidence to remain within `E:\GT-KB`.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` — links the PAUTH schema, taxonomy, evaluator, tests, proposal, and verdict as durable artifacts.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` — requires the WI to remain open until its distinct implementation and verification lifecycle completes.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` — requires the acceptance defect and its repair evidence to remain durably traceable.

## Prior Deliberations

- `DELIB-202666316` — specifically authorizes one bounded WI-5178 proposal and dedicated PAUTH while preserving all implementation and verification gates.
- `DELIB-20260715-AUTHORITY-FOUNDATIONS-PROJECT-AUTHORIZATION` — establishes the project-level implementation envelope and quarantines pre-authorization dirty candidates until independently adopted.
- `DELIB-202666274` — authorizes all required modernization blocker repairs at project scope while retaining mechanical-operation restrictions.

## Owner Decisions / Input

`DELIB-202666316` authorizes this exact WI-5178 proposal and the active
`PAUTH-PROJECT-GTKB-PLATFORM-MODERNIZATION-AUTHORITY-FOUNDATIONS-WI5178-PREDECESSOR-CLOSURE-20260715`.
`DELIB-202666274` confirms project-level authorization for required
modernization work. No new owner decision is required. Protected mutation
still requires independent GO, exact matching claim, and implementation-start
authority. This proposal does not request staging, commit, push, release,
deployment, dispatcher/TAFE mutation, harness mutation, credential lifecycle,
destructive cleanup, or external-system mutation.

## Requirement Sufficiency

Existing requirements sufficient. The operation-time DCL, PAUTH-envelope DCL,
registered taxonomy, deterministic evaluator, frozen RC acceptance manifest,
and existing tests completely specify the required behavior. No new or revised
requirement is needed before implementation.

## Spec-Derived Verification Plan

| Governing specification | Verification evidence | Expected result |
|---|---|---|
| `DCL-PROJECT-AUTHORIZATION-OPERATION-TIME-ENFORCEMENT-001`; `DCL-PROJECT-AUTHORIZATION-ENVELOPE-001`; `DCL-CHANGE-CONTROLLED-ARTIFACT-EVALUABILITY-001` | `groundtruth-kb/.venv/Scripts/python.exe -m pytest groundtruth-kb/tests/test_project_authorization_operation_time_enforcement.py -q --tb=short` | All 13 evaluator/taxonomy tests pass. |
| `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001`; `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001` | Frozen `AT-AUTHORITY-OPERATION-TIME`: `groundtruth-kb/.venv/Scripts/python.exe -m pytest groundtruth-kb/tests/test_project_authorization_operation_time_enforcement.py platform_tests/scripts/test_implementation_authorization.py platform_tests/scripts/test_implementation_start_gate.py platform_tests/scripts/test_bridge_work_intent_registry.py -q --tb=short` | Full activity passes after companion WI-5346/WI-5341 repairs; no protected start, packet load, or work-intent mutation bypasses PAUTH bounds. |
| `GOV-FILE-BRIDGE-AUTHORITY-001`; `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001`; `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`; `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | Mandatory applicability/clause preflights, implementation-start packet, and post-implementation spec-to-test report | No missing required/advisory specs or blocking clause gaps; exact nine-path authority and executed evidence are present. |
| `DCL-PROJECT-DEPENDENCY-ORDERING-001`; `GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001` | Fresh pre-start SHA-256 inventory; hunk-level diff review; `groundtruth-kb/.venv/Scripts/python.exe -m ruff check` and `python -m ruff format --check` on all changed Python targets | No foreign shared-file hunk is absorbed or lost; formatting/lint pass; unrelated authorized flows retain behavior. |
| `GOV-STANDING-BACKLOG-001`; `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`; `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`; `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | WI-5178 MemBase history plus the numbered proposal/report/verdict chain | WI-5178 remains open until exact implementation is independently VERIFIED and mechanically finalized with evidence. |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | Mandatory clause preflight and implementation-report path inventory | `CLAUSE-IN-ROOT` passes and all dependencies resolve under `E:\GT-KB`. |

## Risk / Rollback

This is a high-impact fail-closed authority path. Over-enforcement could strand
valid implementation; under-enforcement could permit protected effects outside
PAUTH bounds. Normalize operations and mutation classes only through the
registered taxonomy, bind evaluator/taxonomy hashes, and keep denial reasons
deterministic. The evaluator, taxonomy, and unit test currently pass and should
remain byte-identical unless independent review finds a concrete defect.

The two shared scripts are moving concurrently. At 2026-07-16T19:02Z the
observed hashes were `00C98C...190E` for
`scripts/implementation_authorization.py` and `A91015...DDD3` for
`scripts/bridge_work_intent_registry.py`; these are evidence snapshots, not
ownership claims. Implementation must rehash every target after claim/start,
then apply only attributable hunks. Rollback is the exact WI-5178 hunk set and
the three adopted untracked evaluator/taxonomy/test files; no whole-file
rollback of a shared target is permitted.

## Bridge Filing

This proposal is filed under `bridge/` as the next status-bearing numbered
bridge file for `gtkb-wi5178-operation-time-authority-enforcement`; no prior version is deleted or rewritten
(append-only). Dispatcher/TAFE state plus the numbered file chain are the live
workflow state per `GOV-FILE-BRIDGE-AUTHORITY-001`.

## Recommended Commit Type

`fix` — closes a production authority-enforcement gap against already frozen
requirements and acceptance tests.

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
