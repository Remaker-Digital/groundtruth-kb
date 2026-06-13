NEW
author_identity: Codex Prime Builder
author_harness_id: A
author_session_context_id: 019ebc0a-181f-7791-a64b-482f97486014
author_model: GPT-5 Codex coding agent
author_model_version: GPT-5 family; exact runtime build not exposed in session context
author_model_configuration: Codex desktop session; Prime Builder override; approval_policy=never
author_metadata_source: Codex Prime Builder session; .gtkb-state/bridge-author-metadata/current.json

# TAFE Flow CLI Skeleton Proposal

bridge_kind: prime_proposal
Document: gtkb-tafe-flow-cli-skeleton
Version: 001
Author: Prime Builder (Codex, harness A)
Date: 2026-06-13 UTC

Project Authorization: PAUTH-PROJECT-GTKB-TYPED-ARTIFACT-FLOW-ENGINE-TAFE-PHASE-0-SCHEMA-CLI-DOCTOR-WI-4487-4491
Project: PROJECT-GTKB-TYPED-ARTIFACT-FLOW-ENGINE
Work Item: WI-4490

target_paths: ["groundtruth-kb/src/groundtruth_kb/cli.py", "groundtruth-kb/tests/test_tafe_flow_cli.py"]

implementation_scope: source, test
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

---

## Summary

Implement the fourth Phase 0 Typed Artifact-Flow Engine (TAFE) slice: register
a `gt flow` Click command group and add a safe CLI skeleton over the already
VERIFIED flow-definition, flow-runtime, and seed-record substrate.

This slice is intentionally a skeleton. It may add read-only CLI views over
existing MemBase-backed TAFE state and no-op/stub handlers for future mutating
or dispatching commands, but it must not activate runtime dispatch, acquire or
release leases, advance stages, write generated bridge views, run pilots, add
doctor checks, or change `bridge/INDEX.md` authority.

The proposed command surface is:

```text
gt flow define
gt flow list
gt flow show
gt flow start
gt flow status
gt flow claim
gt flow release
gt flow heartbeat
gt flow advance
gt flow dispatch tick
gt flow dispatch health
gt flow render bridge-view
gt flow pilot
```

Phase 0 behavior should be conservative:

- `gt flow define` reports the five canonical reviewed-task flow definitions
  and does not mutate definitions.
- `gt flow list`, `gt flow show`, and `gt flow status` read existing flow
  instance state through `TypedArtifactFlowService`.
- `gt flow start`, claim/release/heartbeat/advance, dispatch, render, and pilot
  commands return explicit "not active in Phase 0" no-op responses without
  mutating MemBase or bridge files.
- JSON output should be available where it is useful for tests and later
  automation, while human output remains readable.

## Specification Links

- `SPEC-TYPED-ARTIFACT-FLOW-ENGINE-UMBRELLA` - requires the shared TAFE substrate to remain parallel-run and bridge-authority-preserving during Phase 0.
- `SPEC-TAFE-R7` - requires canonical access through GT-KB service/CLI surfaces with MemBase as the canonical TAFE state store.
- `GOV-FILE-BRIDGE-AUTHORITY-001` - this proposal/report/verdict chain remains append-only bridge evidence; `bridge/INDEX.md` remains workflow authority.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - project, PAUTH, WI, target paths, and governing specs are linked before implementation.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - machine-readable project authorization metadata is present in this proposal header.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - verification must map CLI behavior tests to the linked TAFE specs.
- `GOV-STANDING-BACKLOG-001` - WI-4491 doctor checks and later phase lease/dispatch/render/pilot work must remain visible sibling backlog, not silently absorbed.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - all work stays under `E:\GT-KB` and affects GT-KB platform code/tests only.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` - CLI surface decisions and verification evidence are preserved through PAUTH, bridge proposal, report, and LO verdict.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` - the command skeleton and tests become durable governed artifacts, not transient session behavior.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - WI-4490 should only close after implementation evidence and a terminal VERIFIED verdict.

## Prior Deliberations

- `DELIB-TAFE-SPEC-PROMOTION-APPROVAL-20260612` - owner approved promoting the TAFE specs to `specified`.
- `DELIB-TAFE-PHASE-0-ENABLEMENT-PAUTH-20260612` - owner authorized WI-4487 through WI-4491 under the active Phase 0 PAUTH.
- `DELIB-TAFE-PHASE-0-ENABLEMENT-GO-DEFERRAL-20260612` - Phase 0 enablement was parked until valid Codex review, preserving review discipline.
- `DELIB-BRIDGE-DISPATCH-OVERHAUL-D3-20260612` - owner selected the TAFE overhaul direction that produced this Phase 0 backlog.
- `DELIB-BRIDGE-DISPATCH-OVERHAUL-D5-20260612` - all work entering TAFE must be classified into one of the five typed flow families.
- `DELIB-BRIDGE-DISPATCH-OVERHAUL-PILOT-ELIGIBILITY-20260612` - live pilot eligibility remains constrained; this slice does not run a pilot.
- `bridge/gtkb-tafe-flow-definitions-schema-005.md` - WI-4487 flow-definition schema/service substrate is VERIFIED.
- `bridge/gtkb-tafe-runtime-tables-schema-004.md` - WI-4488 runtime table/service substrate is VERIFIED.
- `bridge/gtkb-tafe-flow-definition-seed-records-004.md` - WI-4489 seed records are VERIFIED.

## Owner Decisions / Input

No new owner decision is required. Existing owner authority is the active Phase
0 PAUTH
`PAUTH-PROJECT-GTKB-TYPED-ARTIFACT-FLOW-ENGINE-TAFE-PHASE-0-SCHEMA-CLI-DOCTOR-WI-4487-4491`,
backed by `DELIB-TAFE-PHASE-0-ENABLEMENT-PAUTH-20260612`; WI-4490 and the
Phase 0 `gt flow` CLI skeleton are explicitly included in that authorization.

## Requirement Sufficiency

Existing requirements are sufficient. `SPEC-TYPED-ARTIFACT-FLOW-ENGINE-UMBRELLA`,
`SPEC-TAFE-R7`, WI-4490, the VERIFIED WI-4487/WI-4488/WI-4489 substrate, and
the active Phase 0 PAUTH provide enough requirement detail for this bounded CLI
skeleton slice.

No new or revised requirement is needed because this proposal deliberately
excludes runtime execution, dispatch policy, stage leases, stage attempts,
capability snapshots, doctor checks, generated bridge views, pilot activation,
and bridge-authority change.

## Implementation Plan

1. Add a `flow` command group in `groundtruth-kb/src/groundtruth_kb/cli.py`.
2. Add read-only command handlers for `define`, `list`, `show`, and `status`
   using existing `KnowledgeDB` and `TypedArtifactFlowService` APIs.
3. Add no-op/stub handlers for `start`, `claim`, `release`, `heartbeat`,
   `advance`, `dispatch tick`, `dispatch health`, `render bridge-view`, and
   `pilot`; these handlers should make the Phase 0 boundary explicit and avoid
   writing MemBase or bridge files.
4. Add focused Click runner tests in
   `groundtruth-kb/tests/test_tafe_flow_cli.py` proving command registration,
   read-only output, JSON output for automation-friendly paths, and no-op
   behavior for future mutating/dispatching/render/pilot commands.
5. File a post-implementation report with the implementation-start packet hash,
   command evidence, and explicit confirmation that WI-4491 doctor work and
   later lease/dispatch/render/pilot work remain open siblings.

## Spec-Derived Verification Plan

The implementation report must include these commands and expected outcomes:

```text
groundtruth-kb/.venv/Scripts/python.exe -m pytest groundtruth-kb/tests/test_tafe_flow_cli.py -q --tb=short
Expected: pass; verifies command registration, read-only definition/instance/status output, JSON output, and no-op skeleton commands.

groundtruth-kb/.venv/Scripts/python.exe -m pytest groundtruth-kb/tests/test_tafe_flow_definitions.py groundtruth-kb/tests/test_tafe_runtime_tables.py groundtruth-kb/tests/test_tafe_flow_definition_seed_records.py groundtruth-kb/tests/test_tafe_flow_cli.py -q --tb=short
Expected: pass; verifies the CLI skeleton remains compatible with the VERIFIED TAFE schema, runtime, and seed-record substrate.

groundtruth-kb/.venv/Scripts/python.exe -m ruff check groundtruth-kb/src/groundtruth_kb/cli.py groundtruth-kb/tests/test_tafe_flow_cli.py
Expected: pass.

groundtruth-kb/.venv/Scripts/python.exe -m ruff format --check groundtruth-kb/src/groundtruth_kb/cli.py groundtruth-kb/tests/test_tafe_flow_cli.py
Expected: pass.

groundtruth-kb/.venv/Scripts/python.exe -m groundtruth_kb flow --help
groundtruth-kb/.venv/Scripts/python.exe -m groundtruth_kb flow define --json
groundtruth-kb/.venv/Scripts/python.exe -m groundtruth_kb flow start implementation --subject-type bridge-thread --subject-id sample --json
Expected: pass; verifies the command group is registered, definitions are readable, and future mutating command paths return no-op Phase 0 responses.
```

Spec mapping:

- `SPEC-TYPED-ARTIFACT-FLOW-ENGINE-UMBRELLA` - tests prove the CLI surface is available without activating TAFE as bridge authority.
- `SPEC-TAFE-R7` - tests prove TAFE has a canonical GT-KB CLI access path backed by existing service APIs.
- `GOV-FILE-BRIDGE-AUTHORITY-001` - tests and report must confirm `render bridge-view` is a no-op skeleton and does not write `bridge/INDEX.md`.
- `GOV-STANDING-BACKLOG-001` - report must explicitly confirm WI-4491 and later phase lease/dispatch/render/pilot work remain open siblings.

## Acceptance Criteria

- [ ] `gt flow --help` lists Phase 0 skeleton commands.
- [ ] `gt flow define` reads canonical flow definitions and does not mutate flow definitions.
- [ ] `gt flow list`, `gt flow show`, and `gt flow status` read flow-instance state when present and handle empty/missing state clearly.
- [ ] Future mutating/dispatching/render/pilot commands return explicit no-op Phase 0 responses and do not mutate MemBase or bridge files.
- [ ] Focused tests cover both human-readable and JSON output paths.
- [ ] The implementation report confirms WI-4491 and later phase work remain open siblings.

## Risk / Rollback

The main risk is making a skeleton command appear more operational than it is.
The mitigation is to use explicit no-op responses for future mutating paths and
to keep read-only behavior on top of the already VERIFIED service APIs.

Rollback before VERIFIED is a normal source/test revert of the two
implementation-scoped files. No live MemBase seed or bridge authority mutation
is expected in this slice.

## Bridge Filing (INDEX-Canonical)

This proposal is filed under `bridge/` with a `NEW` entry inserted at the top
of the `gtkb-tafe-flow-cli-skeleton` document list in `bridge/INDEX.md`; no
prior version is deleted or rewritten. `bridge/INDEX.md` remains the canonical
workflow state per `GOV-FILE-BRIDGE-AUTHORITY-001/CLAUSE-INDEX-IS-CANONICAL`.

## Recommended Commit Type

feat - this adds the canonical Phase 0 `gt flow` CLI skeleton and focused tests
for WI-4490.

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
