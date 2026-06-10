REVISED
author_identity: Codex Prime Builder
author_harness_id: A
author_session_context_id: 019e8512-f2cf-7401-8777-5289a0d54fba
author_model: GPT-5 Codex
author_model_version: GPT-5
author_model_configuration: Codex Desktop; collaboration_mode=Default; session-stated prime-builder via ::init gtkb pb
author_metadata_source: environment variables set for governed revise_bridge.py filing

bridge_kind: prime_proposal
Document: gtkb-retire-role-assignments-mirror-slice-1-seed-repoint
Version: 003 (REVISED-1)
Date: 2026-06-02 UTC
Author: Prime Builder (Codex, harness A, session-stated `::init gtkb pb`)
Responds to: bridge/gtkb-retire-role-assignments-mirror-slice-1-seed-repoint-002.md
Recommended commit type: `refactor`
Project Authorization: PAUTH-WI-4214-RETIRE-ROLE-ASSIGNMENTS-MIRROR-SLICE-1
Project: PROJECT-GTKB-ROLE-STATUS-ORTHOGONALITY-DISPATCH
Work Item: WI-4214
target_paths: ["scripts/seed_harness_registry.py", "platform_tests/scripts/test_seed_harness_registry.py"]

# Retire `role-assignments.json` Legacy Mirror - Slice 1 Seed Repoint Revision

## Summary

This revision responds to the 002 NO-GO by making the implementation envelope executable before any protected source or test mutation occurs. It adds a live project authorization, parser-readable `target_paths` metadata, and a narrower retirement-program statement that no longer claims this slice leaves `role-assignments.json` with zero total readers.

Slice 1 remains a bounded seed-bootstrap change: repoint `scripts/seed_harness_registry.py` from the legacy `role-assignments.json` plus `harness-identities.json` join to the tracked `harness-registry.json` projection, preserve each projection record's status during fresh-install seeding, and update the seed tests. This proposal does not edit protected narrative artifacts, does not delete `harness-state/role-assignments.json`, and does not migrate `scripts/check_index_role_intent_sentinel.py`; those are future-slice work.

## Code Quality Baseline

| Rule ID | Applies? | Compliance plan | Verification | Waiver / N/A reason |
| --- | --- | --- | --- | --- |
| CQ-SECRETS-001 | Yes | Do not add credentials or secret-shaped literals; use only existing local file paths and public spec IDs. | Credential scan is performed by the bridge helper before live filing; implementation report will include changed-file review. |  |
| CQ-PATHS-001 | Yes | Keep implementation inside `E:\GT-KB` and the two authorized target paths. | `target_paths` metadata plus implementation-start packet will constrain source and test edits. |  |
| CQ-COMPLEXITY-001 | Yes | Keep seed-reader logic small and reuse existing JSON parsing and projection shapes. | Targeted pytest plus ruff check on the two changed Python files. |  |
| CQ-CONSTANTS-001 | Yes | Use existing registry field names and avoid introducing duplicated magic path strings beyond the seed input constant. | Code review of `scripts/seed_harness_registry.py` and ruff check. |  |
| CQ-SECURITY-001 | Yes | Preserve fail-closed behavior by defaulting missing status to `registered` and not broadening dispatch eligibility. | New seed test proves `registered` status remains registered. |  |
| CQ-DOCS-001 | Yes | Carry bridge evidence in this proposal and later implementation report; no protected narrative documentation is edited in this slice. | LO review of this proposal and later implementation report. |  |
| CQ-TESTS-001 | Yes | Update seed tests for projection seeding, status preservation, and stale legacy-mirror irrelevance. | `groundtruth-kb\.venv\Scripts\python.exe -m pytest platform_tests\scripts\test_seed_harness_registry.py -q --tb=short`. |  |
| CQ-LOGGING-001 | N/A |  |  | Seed script behavior under this slice does not add or alter logging surfaces. |
| CQ-VERIFICATION-001 | Yes | Run spec-derived pytest and both ruff gates before filing the post-implementation report. | Implementation report must include exact observed pytest, `ruff check`, and `ruff format --check` results. |  |

Before filing the post-implementation report, Prime Builder will run both required repo-native code-quality gates on the changed Python files:

- `groundtruth-kb\.venv\Scripts\python.exe -m ruff check scripts\seed_harness_registry.py platform_tests\scripts\test_seed_harness_registry.py`
- `groundtruth-kb\.venv\Scripts\python.exe -m ruff format --check scripts\seed_harness_registry.py platform_tests\scripts\test_seed_harness_registry.py`

## Response to NO-GO Findings

- F1, missing project authorization envelope: addressed by adding `Project Authorization`, `Project`, and `Work Item` header lines tied to `PAUTH-WI-4214-RETIRE-ROLE-ASSIGNMENTS-MIRROR-SLICE-1`, created from the owner's current Prime Builder direction and recorded as `DELIB-2799`.
- F2, `target_paths` parser-unreadable: addressed by adding a top-level machine-readable `target_paths: ["scripts/seed_harness_registry.py", "platform_tests/scripts/test_seed_harness_registry.py"]` line before the prose sections.
- F3, incomplete last-functional-reader premise: addressed by correcting the retirement program language. Slice 1 removes the seed-bootstrap reader only. The role-intent sentinel script remains a known direct reader and is assigned to a future slice before deletion of the legacy mirror can be proposed.

## Specification Links

- **REQ-HARNESS-REGISTRY-001** (requirement) - governs seeding the `harnesses` table from harness-state and using `harness-registry.json` as the hot-path projection. Slice 1 changes the fresh-install seed source to the tracked projection and preserves projection status.
- **ADR-ROLE-STATUS-ORTHOGONALITY-001** (architecture decision) - role membership and active/registered status are separate axes. The seed must not coerce every harness to `active`.
- **DCL-SINGLE-ACTIVE-PER-ROLE-DISPATCH-001** (design constraint) - dispatch must only target the single active harness per role. A fresh-install seed that preserves `registered` status avoids creating phantom active dispatch candidates.
- **GOV-SOURCE-OF-TRUTH-FRESHNESS-001** (governance) - prefers fresh authoritative reads over divergent cached copies. `harness-registry.json` is the tracked projection used by live reader paths; the legacy mirror is stale.
- **GOV-STANDING-BACKLOG-001** (governance) - WI-4214 is the MemBase standing-backlog authority for this work.
- **GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001** (governance) - requires a current project-scoped authorization before implementation work proceeds.
- **DCL-PROJECT-AUTHORIZATION-ENVELOPE-001** (design constraint) - requires executable authorization metadata for implementation work.
- **GOV-PROJECT-REQUIRES-LINKED-SPECIFICATIONS-001** (governance) - the project authorization is linked to governing specifications and this proposal cites them.
- **PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001** (Prime Builder behavior) - project authorization does not bypass bridge review or the latest-`GO` implementation-start packet.
- **DCL-WORK-ITEM-MUST-BELONG-TO-APPROVED-PROJECT-001** (design constraint) - WI-4214 is included in the authorized project scope.
- **DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001** (design constraint) - implementation proposals must cite project, work item, and authorization metadata.
- **GOV-FILE-BRIDGE-AUTHORITY-001** (governance) - `bridge/INDEX.md` is the authoritative queue state for this REVISED proposal and future LO verdict.
- **DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001** (design constraint) - this proposal cites the specifications constraining the implementation and maps them to verification.
- **DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001** (design constraint) - the later implementation report must carry forward these specs and include observed test results derived from them.
- **ADR-ISOLATION-APPLICATION-PLACEMENT-001** (architecture decision) - the work is scoped inside `E:\GT-KB`; no Agent Red or archive paths are live dependencies.
- **GOV-ARTIFACT-ORIENTED-GOVERNANCE-001** (governance) - this retirement is handled through WI + PAUTH + bridge evidence rather than ad hoc cleanup.
- **ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001** (architecture decision) - the legacy mirror retirement is sequenced as governed artifact-lifecycle work.
- **DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001** (design constraint) - orphaned/stale artifact retirement is a lifecycle event and is split into bounded slices.

## Prior Deliberations

- **DELIB-2799** - Owner direct instruction on 2026-06-02 to continue the listed priority work as Prime Builder and commit/push possible progress. This deliberation created `PAUTH-WI-4214-RETIRE-ROLE-ASSIGNMENTS-MIRROR-SLICE-1` and resolves pending `DECISION-0888` in favor of filing this REVISED proposal.
- **DELIB-2750** - Earlier WI-4214 role-assignments mirror retirement context and pending authorization decision path.
- **DELIB-2556** - Registry Projection Reconciliation VERIFIED; establishes the prior migration to `harness-registry.json` for resolver/attribution paths.
- **DELIB-S328-ROLE-INTENT-SENTINEL-OWNER-DIRECTIVE** - Role-intent sentinel history; relevant because `scripts/check_index_role_intent_sentinel.py` still reads `role-assignments.json` and is explicitly out of this slice.
- **DELIB-1466** - Role and session lifecycle review background.

## Owner Decisions / Input

- **DELIB-2799** records the owner's 2026-06-02 instruction that Codex is the working Prime Builder, should continue the prioritized work independently, and should commit/push everything possible at the next opportunity.
- This instruction resolves the previously pending `DECISION-0888` by authorizing Prime Builder to create the bounded project authorization and file this REVISED proposal for LO review. It does not authorize implementation before LO records `GO` and Prime Builder creates an implementation-start packet.

## Project Authorization Evidence

`PAUTH-WI-4214-RETIRE-ROLE-ASSIGNMENTS-MIRROR-SLICE-1` was created via:

```text
gt backlog authorize-implementation WI-4214 --project-id PROJECT-GTKB-ROLE-STATUS-ORTHOGONALITY-DISPATCH --authorization-id PAUTH-WI-4214-RETIRE-ROLE-ASSIGNMENTS-MIRROR-SLICE-1 --scope "...bounded Slice 1..." --decision-file .gtkb-state/wi-4214-owner-decision.md --include-spec REQ-HARNESS-REGISTRY-001 --include-spec ADR-ROLE-STATUS-ORTHOGONALITY-001 --include-spec DCL-SINGLE-ACTIVE-PER-ROLE-DISPATCH-001 --allowed-mutation-class source --allowed-mutation-class test_modification --forbid deploy --forbid git_push_force --forbid spec_deletion
```

Authorization summary:

- Project: `PROJECT-GTKB-ROLE-STATUS-ORTHOGONALITY-DISPATCH`
- Work item: `WI-4214`
- Owner decision: `DELIB-2799`
- Included specs: `REQ-HARNESS-REGISTRY-001`, `ADR-ROLE-STATUS-ORTHOGONALITY-001`, `DCL-SINGLE-ACTIVE-PER-ROLE-DISPATCH-001`
- Allowed mutation classes: `source`, `test_modification`
- Forbidden operations: `deploy`, `git_push_force`, `spec_deletion`
- Scope limit: only `scripts/seed_harness_registry.py` and `platform_tests/scripts/test_seed_harness_registry.py`; no protected narrative edits; no deletion of `harness-state/role-assignments.json`; no migration of `scripts/check_index_role_intent_sentinel.py`.

## Requirement Sufficiency

Existing requirements sufficient.

REQ-HARNESS-REGISTRY-001, ADR-ROLE-STATUS-ORTHOGONALITY-001, DCL-SINGLE-ACTIVE-PER-ROLE-DISPATCH-001, and GOV-SOURCE-OF-TRUTH-FRESHNESS-001 are sufficient for the bounded seed-bootstrap repoint. No new or revised requirement is needed before this slice. Later slices that alter protected owner-directive narrative text or delete the tracked legacy mirror require their own bridge proposals and any applicable owner/formal-artifact approvals.

## Retirement Program Context

The retirement program is deliberately split so each step is reviewable and reversible:

- **Slice 1 (this proposal):** repoint the fresh-install seed to `harness-registry.json`, preserve projection `status`, and update seed tests. This removes the seed-bootstrap dependency on the legacy mirror only.
- **Future slice:** migrate or retire `scripts/check_index_role_intent_sentinel.py` so the role-intent sentinel no longer reads `harness-state/role-assignments.json`.
- **Future slice:** reword protected narrative artifacts that still describe `role-assignments.json` as durable role authority. That slice must use applicable owner-question evidence and formal/narrative-artifact approval packets.
- **Future slice:** delete `harness-state/role-assignments.json` only after functional readers and protected prose have been migrated.

## Slice 1 Scope

Authorized target paths:

```json
["scripts/seed_harness_registry.py", "platform_tests/scripts/test_seed_harness_registry.py"]
```

Planned source change:

- Replace the legacy seed reader that joins `harness-state/role-assignments.json` and `harness-state/harness-identities.json` with a reader for tracked `harness-state/harness-registry.json`.
- Seed each harness from the projection fields already present in the registry record: `id`, `harness_name`, `harness_type`, `role`, `status`, and `invocation_surfaces`.
- Preserve each projection record's `status`; if a projection record omits status, default to `registered` as a conservative fail-closed value.
- Preserve idempotence and post-seed projection regeneration.

Planned test change:

- Update the test project fixture to write `harness-registry.json`.
- Add or update coverage proving that a `registered` projection record is seeded as `registered`.
- Add or update coverage proving that stale `role-assignments.json` contents do not affect seeded roles.

Out of scope:

- Editing protected owner-directive prose.
- Deleting `harness-state/role-assignments.json`.
- Migrating or deleting `scripts/check_index_role_intent_sentinel.py`.
- Changing durable role/session semantics outside fresh-install seeding.

## Spec-Derived Verification Plan

- REQ-HARNESS-REGISTRY-001: seed populates the harness table from `harness-registry.json` and regenerates the projection. Command: `groundtruth-kb\.venv\Scripts\python.exe -m pytest platform_tests\scripts\test_seed_harness_registry.py -q --tb=short`.
- ADR-ROLE-STATUS-ORTHOGONALITY-001: a projection record with `status="registered"` remains registered after seeding. Command: `groundtruth-kb\.venv\Scripts\python.exe -m pytest platform_tests\scripts\test_seed_harness_registry.py -q --tb=short`.
- DCL-SINGLE-ACTIVE-PER-ROLE-DISPATCH-001: the seed does not create a phantom active harness when the projection says registered. Command: `groundtruth-kb\.venv\Scripts\python.exe -m pytest platform_tests\scripts\test_seed_harness_registry.py -q --tb=short`.
- GOV-SOURCE-OF-TRUTH-FRESHNESS-001: stale `role-assignments.json` data does not control seed role/status output. Command: `groundtruth-kb\.venv\Scripts\python.exe -m pytest platform_tests\scripts\test_seed_harness_registry.py -q --tb=short`.
- Bridge implementation-start gate: after LO records GO, implementation authorization begins from the live bridge thread before source/test edits. Command: `groundtruth-kb\.venv\Scripts\python.exe scripts\implementation_authorization.py begin --bridge-id gtkb-retire-role-assignments-mirror-slice-1-seed-repoint`.

## Acceptance Criteria

- `scripts/seed_harness_registry.py` no longer reads `harness-state/role-assignments.json` or `harness-state/harness-identities.json` for fresh-install seeding.
- Fresh-install seeding reads tracked `harness-state/harness-registry.json`.
- Projection record status is preserved, including `registered`.
- Existing seed idempotence is preserved.
- `platform_tests/scripts/test_seed_harness_registry.py` covers projection seeding, status preservation, and stale legacy-mirror irrelevance.
- The post-implementation report includes the spec-derived pytest evidence plus both ruff gates listed above.

## Risk / Rollback

Main risk: `harness-registry.json` might be absent in an unusual checkout state where the old two-file seed path happened to exist. That failure should be explicit rather than silently seeding from stale role data. The implementation can keep a clear error message for a missing projection file.

Rollback is straightforward: revert the two authorized files before filing an implementation report, or if implementation has already landed and proves defective, file a corrective bridge proposal to restore or replace the seed reader. This proposal does not delete legacy files, so rollback does not require recovering removed state.

## Pre-Filing Preflight

Preflight commands to run through `revise_bridge.py file` before live filing:

```text
groundtruth-kb\.venv\Scripts\python.exe scripts\bridge_applicability_preflight.py --bridge-id gtkb-retire-role-assignments-mirror-slice-1-seed-repoint --content-file .gtkb-state\bridge-revisions\drafts\gtkb-retire-role-assignments-mirror-slice-1-seed-repoint-003.completed.md
groundtruth-kb\.venv\Scripts\python.exe scripts\adr_dcl_clause_preflight.py --bridge-id gtkb-retire-role-assignments-mirror-slice-1-seed-repoint --content-file .gtkb-state\bridge-revisions\drafts\gtkb-retire-role-assignments-mirror-slice-1-seed-repoint-003.completed.md
```

The live filing is valid only if the applicability preflight reports `preflight_passed: true`, `missing_required_specs: []`, and `missing_advisory_specs: []`. Any clause-preflight gaps must be included in LO review context; this revision includes the required project authorization, project linkage, prior deliberations, owner input, target paths, requirement sufficiency, and spec-derived verification sections intended to satisfy the hard gates.
