NEW

# gtkb-dispatcher-black-box-spec-foundation (Slice 1) — Dispatcher Black-Box Governance/Spec Foundation

bridge_kind: prime_proposal
Document: gtkb-dispatcher-black-box-spec-foundation
Version: 001
Author: Prime Builder (Codex)
Date: 2026-07-15T17:11:09Z

author_identity: prime-builder/codex
author_harness_id: A
author_session_context_id: 019f6668-9974-7d72-a456-826f9a67e627
author_model: GPT-5 Codex
author_model_version: GPT-5
author_model_configuration: Codex Desktop, GT-KB Prime Builder interactive session

Project Authorization: PAUTH-DISPATCHER-BLACK-BOX-WI5268-SPEC-FOUNDATION-20260715
Project: PROJECT-GTKB-OPS-DISPATCHER-MODERNIZATION-DISPATCHER-BLACK-BOX-HARDENING
Work Item: WI-5268

target_paths: ["groundtruth.db", ".groundtruth/formal-artifact-approvals/2026-07-15-dispatcher-black-box-foundation-*.json"]

implementation_scope: governance
requires_review: true
requires_verification: true
kb_mutation_in_scope: true

---

## Summary

Create the governed formal-artifact foundation for the dispatcher/TAFE/harness black-box boundary before any source, config, hook, prompt, CLI, or runtime implementation begins. This slice implements `WI-5268` only: it records the ordinary-worker boundary, the worker-safe packet contract, and the activity-envelope authority model as MemBase formal artifacts with matching approval packets.

The implementation will create or update formal artifacts in `groundtruth.db` and approval packets under `.groundtruth/formal-artifact-approvals/`. It will not mutate dispatcher runtime code, bridge/TAFE internals, harness-state/configuration, prompts/skills, gates/hooks, or child work items `WI-5269` through `WI-5276`.

## Specification Links

- `ADR-DISPATCHER-ARCHITECTURE-001` — dispatch is a daemon-owned black-box service; this slice formalizes the worker-side boundary needed to preserve that architecture.
- `DCL-HARNESS-DISPATCH-ISOLATION-INVARIANT-001` — harnesses are consumers/producers of artifacts, not dispatch controllers; the new foundation must prevent ordinary workers from depending on black-box internals.
- `GOV-FILE-BRIDGE-AUTHORITY-001` — the proposal is filed through the append-only bridge chain and live dispatcher/TAFE publication path.
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` — the cited PAUTH is bounded owner-approval evidence for this project scope.
- `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001` — PAUTH does not bypass Loyal Opposition GO, target paths, implementation-start, reports, or verification.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` — this implementation-targeting proposal carries concrete governing spec links.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` — this proposal includes machine-readable PAUTH, project, and work-item metadata.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — verification must prove every new/updated formal artifact has derived checks and evidence.
- `GOV-STANDING-BACKLOG-001` — `WI-5268` and its linked test are the durable backlog authority for this slice.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` — the advisory intake decisions crossed the threshold for durable formal artifacts.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` — the black-box decisions become durable artifact-graph nodes rather than transient chat memory.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` — owner decisions, advisory findings, and accepted future work must move through explicit artifact lifecycle states.

## Prior Deliberations

- `DELIB-20260715-DISPATCHER-BLACKBOX-PHASED-HARDENING` — owner selected safe-worker facades first, then audit/soft-deny, then hard gates after parity exists.
- `DELIB-20260715-DISPATCHER-BLACKBOX-PROJECT-HOME` — owner selected a child project under dispatcher modernization.
- `DELIB-20260715-DISPATCHER-BLACKBOX-ORDINARY-WORKER-DEFINITION` — ordinary worker means any session envelope not yet initialized with an activity envelope.
- `DELIB-20260715-DISPATCHER-BLACKBOX-ACTIVITY-ENVELOPE-AUTHORITY` — ordinary bridge work uses worker-safe packets; protected internals require explicit activity-envelope authority.
- `DELIB-20260715-DISPATCHER-BLACKBOX-SAFE-PACKET-CONTENT` — worker-safe packets must include full assigned proposal/verdict/report/review content plus governing metadata and omit raw internals.
- `DELIB-20260715-DISPATCHER-BLACKBOX-SPEC-FOUNDATION-FIRST` — owner required formal governance/spec foundation before implementation work.
- `DELIB-20260715-DISPATCHER-BLACKBOX-OPS-BUILD-ENVELOPES` — owner clarified ops envelope controls black-box configuration mutation; build envelope controls direct internal mutation only with case authorization.
- `DELIB-20260715-DISPATCHER-BLACKBOX-WI5268-APPROVAL` — owner approved PAUTH creation and proposal filing for `WI-5268` only.
- `DELIB-20265888` — prior dispatcher architecture decision: dispatch is a GT-KB-owned black-box service and harnesses are consumers only.

## Owner Decisions / Input

- Owner approved the advisory intake path through the decisions listed in `## Prior Deliberations`.
- Owner explicitly approved the next governed step with `APPROVE WI-5268`, captured as `DELIB-20260715-DISPATCHER-BLACKBOX-WI5268-APPROVAL`.
- The active authorization is `PAUTH-DISPATCHER-BLACK-BOX-WI5268-SPEC-FOUNDATION-20260715`, scoped to `WI-5268` only.

## Requirement Sufficiency

New or revised requirement required before downstream implementation. This proposal is the foundation slice that creates those requirements as formal artifacts before child implementation work proceeds.

The accepted proposal-filing scope is defined by `WI-5268`, `TEST-11423`, the cited PAUTH, and the owner deliberations above. The implementation must produce the following formal artifacts, with exact text supplied in validated formal-artifact approval packets:

- `DCL-DISPATCHER-ORDINARY-WORKER-BLACK-BOX-BOUNDARY-001`
- `DCL-DISPATCHER-WORKER-SAFE-PACKET-CONTRACT-001`
- `DCL-DISPATCHER-ACTIVITY-ENVELOPE-AUTHORITY-001`
- `ADR-DISPATCHER-WORKER-CONTEXT-FACADE-001`

## Specification-Derived Verification Plan

Implementation verification must carry an explicit spec-to-test mapping from the linked specifications to concrete command evidence and observed results. This governance-only slice primarily uses `gt` CLI assertions rather than source-level pytest, but the implementation report must still use this section shape and include the observed command results.

```text
python -m groundtruth_kb.cli tests show TEST-11423 --json
```

Expected: `TEST-11423` exists, links to `ADR-DISPATCHER-ARCHITECTURE-001`, and its expected outcome matches the foundation boundary claims.

```text
python -m groundtruth_kb.cli spec show DCL-DISPATCHER-ORDINARY-WORKER-BLACK-BOX-BOUNDARY-001 --json
python -m groundtruth_kb.cli spec show DCL-DISPATCHER-WORKER-SAFE-PACKET-CONTRACT-001 --json
python -m groundtruth_kb.cli spec show DCL-DISPATCHER-ACTIVITY-ENVELOPE-AUTHORITY-001 --json
python -m groundtruth_kb.cli spec show ADR-DISPATCHER-WORKER-CONTEXT-FACADE-001 --json
```

Expected: each artifact exists in MemBase, has the correct formal type, cites the advisory and owner decisions, and contains enforceable language for ordinary workers, worker-safe packets, ops/build activity envelopes, capability/audit requirements, and phased hardening gates.

```text
python scripts/validate_formal_artifact_packet.py .groundtruth/formal-artifact-approvals/2026-07-15-dispatcher-black-box-foundation-<artifact>.json
```

Expected: each approval packet exits 0 and validates against the live formal-artifact approval gate.

```text
python scripts/bridge_applicability_preflight.py --bridge-id gtkb-dispatcher-black-box-spec-foundation
python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-dispatcher-black-box-spec-foundation
```

Expected: applicability preflight passes with no missing required specs, and clause preflight reports zero blocking gaps.

## Risk / Rollback

Risk: a weak foundation would either overexpose black-box internals to ordinary workers or overconstrain future ops/build maintenance. Mitigation: this slice writes only formal artifacts and approval packets, with no source/config/runtime changes, so Loyal Opposition can require wording corrections before mechanics are built.

Rollback: revert the single governance commit containing the MemBase formal-artifact rows and approval packets, then file a REVISED bridge proposal with corrected artifact text. No runtime behavior changes are included in this slice.

## Bridge Filing

This proposal is filed under `bridge/` as the next status-bearing numbered
bridge file for `gtkb-dispatcher-black-box-spec-foundation`; no prior version is deleted or rewritten
(append-only). Dispatcher/TAFE state plus the numbered file chain are the live
workflow state per `GOV-FILE-BRIDGE-AUTHORITY-001`.

## Recommended Commit Type

chore — governed metadata/formal-artifact foundation only; no source/runtime implementation.

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
