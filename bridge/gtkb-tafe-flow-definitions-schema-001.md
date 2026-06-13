NEW

# TAFE Flow Definitions Schema Proposal

bridge_kind: prime_proposal
Document: gtkb-tafe-flow-definitions-schema
Version: 001
Author: Prime Builder (Codex, harness A)
Date: 2026-06-13 UTC

author_identity: Codex Prime Builder
author_harness_id: A
author_session_context_id: 019ebe6d-deb1-7ff3-a77c-ed6b1c92f5b8
author_model: GPT-5 Codex coding agent
author_model_version: GPT-5 family; exact runtime build not exposed in session context
author_model_configuration: Codex desktop session; Prime Builder override; approval_policy=never

Project Authorization: PAUTH-PROJECT-GTKB-TYPED-ARTIFACT-FLOW-ENGINE-TAFE-PHASE-0-SCHEMA-CLI-DOCTOR-WI-4487-4491
Project: PROJECT-GTKB-TYPED-ARTIFACT-FLOW-ENGINE
Work Item: WI-4487

target_paths: ["groundtruth-kb/src/groundtruth_kb/db.py", "groundtruth-kb/src/groundtruth_kb/typed_artifact_flow.py", "groundtruth-kb/tests/test_tafe_flow_definitions.py"]

implementation_scope: source
requires_review: true
requires_verification: true
kb_mutation_in_scope: true

---

## Summary

Implement the first Phase 0 Typed Artifact-Flow Engine (TAFE) substrate slice:
add an append-only MemBase `flow_definitions` table and a small source-level
service surface for typed flow templates.

This work is intentionally schema-first. It gives later Phase 0 work a durable
home for the five reviewed-task flow definitions without seeding those rows,
starting runtime flow execution, changing bridge authority, or making
`bridge/INDEX.md` generated. WI-4487 is the prerequisite for WI-4488 and
WI-4489, so this proposal keeps the slice small enough for direct LO review.

## Specification Links

- `SPEC-TYPED-ARTIFACT-FLOW-ENGINE-UMBRELLA` — governs the overall typed flow engine substrate and keeps this slice inside Phase 0 parallel-run enablement.
- `SPEC-TAFE-R1` — requires typed flow definitions that can be extended by new records rather than hard-coded bridge behavior.
- `SPEC-TAFE-R7` — requires MemBase-backed, service-mediated canonical access for TAFE state.
- `GOV-FILE-BRIDGE-AUTHORITY-001` — this proposal and any later report remain append-only bridge artifacts; `bridge/INDEX.md` remains the live workflow authority.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` — the proposal links the governing project, PAUTH, WI, target paths, and TAFE specs before implementation.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` — the project authorization and work-item membership are explicit machine-readable metadata.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — verification must include schema/service tests mapped to the linked TAFE specifications.
- `GOV-STANDING-BACKLOG-001` — WI-4487 remains the MemBase work-item authority; implementation/report evidence must not silently bypass or close sibling work.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` — all changes stay under `E:\GT-KB` and target GT-KB platform code, not Agent Red application code.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` — the schema addition is handled through project authorization, bridge proposal, LO review, implementation report, and later VERIFIED disposition.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` — the proposed schema is a durable governed artifact substrate, not a transient implementation convenience.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` — WI-4487 remains open until implementation evidence and a terminal bridge verdict justify lifecycle advancement.

## Prior Deliberations

- `DELIB-TAFE-SPEC-PROMOTION-APPROVAL-20260612` — TAFE candidate spec promotion approved (8 specs candidate -> specified)
- `DELIB-TAFE-PHASE-0-ENABLEMENT-PAUTH-20260612` — TAFE Phase 0 enablement: owner authorizes WI-4487..WI-4491 via single PAUTH
- `DELIB-TAFE-PHASE-0-ENABLEMENT-GO-DEFERRAL-20260612` — TAFE Phase-0 enablement parked DEFERRED pending a valid Codex GO
- `DELIB-BRIDGE-DISPATCH-OVERHAUL-D3-20260612` — owner selected the TAFE overhaul direction that created the typed-flow Phase 0 backlog.
- `DELIB-BRIDGE-DISPATCH-OVERHAUL-D5-20260612` — all work entering the typed flow engine must be pre-classified into one of the five typed flows.
- `DELIB-BRIDGE-DISPATCH-OVERHAUL-PILOT-ELIGIBILITY-20260612` — live pilot scope excludes implementation-flow cutover; this proposal remains schema-only and does not start a pilot.

## Owner Decisions / Input

No new owner decision is required for this proposal. Existing owner authority is
the active Phase 0 PAUTH
`PAUTH-PROJECT-GTKB-TYPED-ARTIFACT-FLOW-ENGINE-TAFE-PHASE-0-SCHEMA-CLI-DOCTOR-WI-4487-4491`,
backed by `DELIB-TAFE-PHASE-0-ENABLEMENT-PAUTH-20260612`, and the current
work item is explicitly included in that authorization.

## Requirement Sufficiency

Existing requirements sufficient. `SPEC-TYPED-ARTIFACT-FLOW-ENGINE-UMBRELLA`,
`SPEC-TAFE-R1`, `SPEC-TAFE-R7`, WI-4487, and the active Phase 0 PAUTH provide
enough requirement detail for the bounded schema/service slice.

No new or revised requirement is needed before implementation because this
proposal does not decide seed record content, runtime flow-instance schema,
stage leases, dispatch scoring, generated compatibility views, or bridge
authority cutover.

## Spec-Derived Verification Plan

The implementation report must include these commands and expected outcomes:

```text
groundtruth-kb/.venv/Scripts/python.exe -m pytest groundtruth-kb/tests/test_tafe_flow_definitions.py -q --tb=short
Expected: pass; verifies the `flow_definitions` table exists in a temporary MemBase database, has the required identity/version/stage/role/AUQ/never-self-review/deterministic/workspace-isolation fields, preserves append-only version behavior, and exposes service-level create/list/get behavior without requiring live bridge state.

groundtruth-kb/.venv/Scripts/python.exe -m ruff check groundtruth-kb/src/groundtruth_kb/db.py groundtruth-kb/src/groundtruth_kb/typed_artifact_flow.py groundtruth-kb/tests/test_tafe_flow_definitions.py
Expected: pass.

groundtruth-kb/.venv/Scripts/python.exe -m ruff format --check groundtruth-kb/src/groundtruth_kb/db.py groundtruth-kb/src/groundtruth_kb/typed_artifact_flow.py groundtruth-kb/tests/test_tafe_flow_definitions.py
Expected: pass.
```

Spec mapping:

- `SPEC-TYPED-ARTIFACT-FLOW-ENGINE-UMBRELLA` — table/service tests demonstrate a Phase 0 substrate for later typed flows without cutover.
- `SPEC-TAFE-R1` — schema tests assert extensible row-backed flow definitions rather than hard-coded flow templates.
- `SPEC-TAFE-R7` — service tests assert MemBase-backed canonical access through GT-KB source APIs.
- `GOV-FILE-BRIDGE-AUTHORITY-001` — bridge preflights plus the implementation report must show no `bridge/INDEX.md` authority change beyond append-only proposal/report lifecycle entries.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — this section supplies the spec-to-test mapping LO must verify.

Out of scope for this verification: seed rows for the five canonical flow types
(WI-4489), runtime flow-instance tables (WI-4488), `gt flow` CLI commands
(WI-4490), doctor checks (WI-4491), dispatch policy, live pilots, and generated
`INDEX.md` compatibility views.

## Risk / Rollback

Risk is primarily schema drift: adding a canonical table too broad, too narrow,
or with ambiguous JSON field names would make later Phase 0 work expensive to
correct. The mitigation is to keep the schema additive, explicitly versioned,
and tested against temporary MemBase databases before any live-data use.

Rollback is a normal single-commit revert before VERIFIED. If implementation
has instantiated the table in a local live `groundtruth.db`, the source rollback
removes future use while leaving an unused additive table harmlessly present;
no destructive DB cleanup is in scope.

## Bridge Filing (INDEX-Canonical)

This proposal is filed under `bridge/` with a `NEW` entry inserted at the top of
the `gtkb-tafe-flow-definitions-schema` document list in `bridge/INDEX.md`; no prior version is deleted or
rewritten (append-only). `bridge/INDEX.md` remains the canonical workflow state
per `GOV-FILE-BRIDGE-AUTHORITY-001/CLAUSE-INDEX-IS-CANONICAL`.

## Recommended Commit Type

feat — this adds a new TAFE schema/service capability, backed by focused tests.

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
