NEW
author_identity: Codex Prime Builder
author_harness_id: A
author_session_context_id: S389
author_model: GPT-5 Codex
author_model_version: GPT-5
author_model_configuration: Codex Desktop; collaboration_mode=Default; session-stated prime-builder via ::init gtkb pb
author_metadata_source: explicit-codex-session

bridge_kind: implementation_proposal
Document: gtkb-registry-scaffold-fixture-drift-reconciliation
Version: 001
Date: 2026-06-02 UTC
Author: Prime Builder (Codex, harness A, session-stated `::init gtkb pb`)
Recommended commit type: `test`
Project Authorization: PAUTH-WI-4225-REGISTRY-SCAFFOLD-FIXTURE-DRIFT-001
Project: PROJECT-GTKB-RELIABILITY-FIXES
Work Item: WI-4225
target_paths: ["groundtruth-kb/templates/managed-artifacts.toml", "groundtruth-kb/tests/fixtures/registry-id-set.txt", "groundtruth-kb/tests/test_managed_registry.py", "groundtruth-kb/tests/fixtures/scaffold_golden/local-only/**", "groundtruth-kb/tests/fixtures/scaffold_golden/dual-agent/**"]

# Registry and Scaffold Fixture Drift Reconciliation

## Summary

This proposal reconciles the Loyal Opposition-reported fixture and registry drift that currently blocks the targeted GT-KB scaffold and managed-registry test surfaces from returning to a pristine green state.

The intended implementation is bounded to accepting real registry drift, restoring explicit managed-artifact coverage for the narrative artifact approval gate template, updating the registry ID snapshot, and regenerating scaffold golden fixtures so they match the current scaffold output. It does not change scaffold semantics except where the generated fixtures already prove the implementation has drifted ahead of the recorded golden output.

## Code Quality Baseline

| Rule ID | Applies? | Compliance plan | Verification | Waiver / N/A reason |
| --- | --- | --- | --- | --- |
| CQ-SECRETS-001 | Yes | Do not add credentials or credential-shaped literals; edits are registry rows, text fixtures, and generated scaffold snapshots. | Bridge helper credential scan before filing plus changed-file review before commit. |  |
| CQ-PATHS-001 | Yes | Keep all implementation and generated fixtures under `E:\GT-KB` and the authorized target paths. | `target_paths` metadata plus implementation-start packet constrain fixture and registry edits. |  |
| CQ-COMPLEXITY-001 | Yes | Prefer direct registry/fixture reconciliation over new abstractions or parser behavior changes. | Targeted pytest on registry drift, AST coverage, managed registry, and scaffold golden surfaces. |  |
| CQ-CONSTANTS-001 | Yes | Preserve existing registry naming conventions and generated snapshot ordering. | Targeted tests compare the resolver IDs and scaffold golden fixtures against deterministic output. |  |
| CQ-SECURITY-001 | Yes | Do not broaden hook execution, scaffold permissions, or generated runtime behavior in this slice. | Scope review confirms only registry/fixture metadata and golden outputs changed. |  |
| CQ-DOCS-001 | Yes | Carry rationale in this bridge proposal and post-implementation report; no narrative docs are edited. | LO review of this proposal and later implementation report. |  |
| CQ-TESTS-001 | Yes | Update only tests/fixtures required to match the current managed registry and scaffold output. | Run targeted pytest commands listed in the spec-derived verification plan. |  |
| CQ-LOGGING-001 | N/A |  |  | This fixture reconciliation does not add or alter logging surfaces. |
| CQ-VERIFICATION-001 | Yes | Run the targeted pytest and ruff gates before filing the implementation report, and document any unrelated full-suite dependency limitation. | Implementation report must include exact observed command results and any residual environment limitation. |  |

## Specification Links

- **GOV-RELIABILITY-FAST-LANE-001** (governance) - authorizes bounded reliability repairs that restore failing test surfaces when the owner has prioritized green-suite restoration.
- **GOV-FILE-BRIDGE-AUTHORITY-001** (governance) - the bridge INDEX remains the authoritative queue state for this proposal and later implementation report.
- **GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001** (governance) - protected test/config fixture work requires a current project-scoped authorization.
- **DCL-PROJECT-AUTHORIZATION-ENVELOPE-001** (design constraint) - the proposal cites executable project, work item, and authorization metadata.
- **PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001** (Prime Builder behavior) - the project authorization does not bypass LO review or the implementation-start packet.
- **DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001** (design constraint) - implementation proposals must include project authorization, project, and work item linkage.
- **DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001** (design constraint) - this proposal cites relevant specifications and maps them to verification.
- **DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001** (design constraint) - the implementation report must include spec-derived test evidence before verification.
- **GOV-ARTIFACT-ORIENTED-GOVERNANCE-001** (governance) - registry/scaffold drift is handled as tracked artifact lifecycle work, not an ad hoc local patch.
- **ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001** (architecture decision) - durable fixtures and registry records are maintained as governed artifacts.
- **DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001** (design constraint) - observed registry/scaffold drift is an artifact lifecycle trigger requiring reconciliation or explicit retirement.
- **ADR-ISOLATION-APPLICATION-PLACEMENT-001** (architecture decision) - all work remains inside `E:\GT-KB`; no Agent Red or archive paths are live dependencies.

## Prior Deliberations

- **DELIB-2804** records the owner directive in session S388/S389 that Codex is the working Prime Builder and should continue the listed priorities, including the LO-recommended registry/scaffold fixture drift repair.
- **PAUTH-WI-4225-REGISTRY-SCAFFOLD-FIXTURE-DRIFT-001** is the project-scoped authorization created for WI-4225 under `PROJECT-GTKB-RELIABILITY-FIXES`.
- **bridge/gtkb-verify-skill-spec-to-test-mapping-010.md** recently VERIFIED the bridge verification helper work and is relevant because the present drift was surfaced by the same LO handoff sequence.
- **bridge/gtkb-retire-role-assignments-mirror-slice-1-seed-repoint-003.md** is recent Prime Builder precedent for combining project authorization metadata, code-quality baseline rows, target paths, and bridge-governed test repair.

## Owner Decisions / Input

- **DELIB-2804** records the owner instruction to accept the Loyal Opposition recommendations, proceed independently as Prime Builder, and commit/push everything possible.
- **PAUTH-WI-4225-REGISTRY-SCAFFOLD-FIXTURE-DRIFT-001** authorizes this bounded work item within `PROJECT-GTKB-RELIABILITY-FIXES` with allowed mutation classes `source`, `test_modification`, and `test_fixture_update`; forbidden operations remain `deploy`, `git_push_force`, and `spec_deletion`.
- This authorization does not allow implementation before Loyal Opposition records `GO` and Prime Builder creates an implementation-start packet from the live bridge thread.

## Requirement Sufficiency

Existing requirements sufficient.

The existing bridge, project-authorization, artifact-lifecycle, root-boundary, and verification specifications are sufficient for this bounded fixture reconciliation. No new GOV, ADR, DCL, PB, REQ, or SPEC record is required before implementation.

## Target Change Plan

Authorized target paths:

```json
["groundtruth-kb/templates/managed-artifacts.toml", "groundtruth-kb/tests/fixtures/registry-id-set.txt", "groundtruth-kb/tests/test_managed_registry.py", "groundtruth-kb/tests/fixtures/scaffold_golden/local-only/**", "groundtruth-kb/tests/fixtures/scaffold_golden/dual-agent/**"]
```

Planned changes:

- Add a FILE-class managed-artifact record for `hooks/narrative-artifact-approval-gate.py` with empty scaffold lifecycle axes so the template has registry coverage without changing adopter scaffold output.
- Regenerate `groundtruth-kb/tests/fixtures/registry-id-set.txt` from `OwnershipResolver().all_records()` and preserve the comment header.
- Update managed-registry aggregate expectations in `groundtruth-kb/tests/test_managed_registry.py` to match the accepted registry count drift.
- Regenerate scaffold golden fixtures for `local-only` and `dual-agent` using `scripts/_capture_scaffold_golden.py` so new bridge helper and code-quality hook scaffold output is represented.
- If the golden fixture directories cannot be overwritten because of Windows file attributes or stale handles, perform a guarded deletion only after verifying the resolved absolute target paths are inside `E:\GT-KB\groundtruth-kb\tests\fixtures\scaffold_golden\`.

Out of scope:

- Changing scaffold output semantics beyond accepting existing generated output.
- Editing formal GOV/ADR/DCL/SPEC artifacts.
- Deleting bridge helper files or treating them as ephemeral without separate evidence.
- Production deployment or force-push operations.

## Spec-Derived Verification Plan

- GOV-RELIABILITY-FAST-LANE-001 and DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001: prove the registry snapshot matches live ownership records. Command: `groundtruth-kb\.venv\Scripts\python.exe -m pytest groundtruth-kb\tests\test_registry_drift_detection.py -q --tb=short`.
- DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001 and registry coverage expectations: prove every template source file has registry coverage. Command: `groundtruth-kb\.venv\Scripts\python.exe -m pytest groundtruth-kb\tests\test_registry_ast_coverage.py -q --tb=short`.
- ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001 and managed-registry count integrity: prove aggregate registry counts and rationale discipline are coherent. Command: `groundtruth-kb\.venv\Scripts\python.exe -m pytest groundtruth-kb\tests\test_managed_registry.py groundtruth-kb\tests\test_registry_rationale_discipline.py -q --tb=short`.
- GOV-ARTIFACT-ORIENTED-GOVERNANCE-001 and scaffold fixture authority: prove golden fixture output matches scaffold generation. Command: `groundtruth-kb\.venv\Scripts\python.exe -m pytest groundtruth-kb\tests\adopter\test_golden_fixture_diff_per_version.py groundtruth-kb\tests\test_scaffold_isolation.py -q --tb=short`.
- ADR-ISOLATION-APPLICATION-PLACEMENT-001 and scaffold integrity: re-run adjacent scaffold smoke/settings/bridge tests. Command: `groundtruth-kb\.venv\Scripts\python.exe -m pytest groundtruth-kb\tests\test_scaffold_smoke.py groundtruth-kb\tests\test_scaffold_project.py groundtruth-kb\tests\test_scaffold_settings.py groundtruth-kb\tests\test_scaffold_bridge_rules.py groundtruth-kb\tests\test_scaffold_bridge_index.py -q --tb=short`.
- CQ-VERIFICATION-001: run repo-native lint and format checks on any edited Python files. Commands: `groundtruth-kb\.venv\Scripts\python.exe -m ruff check groundtruth-kb\tests\test_managed_registry.py scripts\_capture_scaffold_golden.py` and `groundtruth-kb\.venv\Scripts\python.exe -m ruff format --check groundtruth-kb\tests\test_managed_registry.py scripts\_capture_scaffold_golden.py`.

Known limitation to report, not solve in this slice:

- Full `groundtruth-kb/tests` collection currently fails in this environment on missing `fastapi` imports for unrelated web tests. This proposal targets the registry/scaffold drift surfaces identified by Loyal Opposition.

## Acceptance Criteria

- `hooks/narrative-artifact-approval-gate.py` has explicit managed-artifact registry coverage or a reviewed equivalent that keeps AST coverage green.
- `groundtruth-kb/tests/fixtures/registry-id-set.txt` contains the live sorted ownership IDs, including the new bridge helper and code-quality hook IDs, while retaining its explanatory header.
- Managed-registry count tests match the accepted registry state.
- `local-only` and `dual-agent` scaffold golden fixtures match the deterministic scaffold output.
- All targeted verification commands listed above pass, except any explicitly documented unrelated environment limitation.
- The implementation report carries forward linked specs, exact command evidence, observed results, and the spec-to-test mapping.

## Risk / Rollback

Main risk: scaffold golden regeneration may capture unrelated output drift if the generator has changed more broadly than the LO finding described. The implementation must inspect the resulting diff and keep the commit scoped to registry/scaffold fixture reconciliation.

Rollback is straightforward: revert the changed managed-artifact registry rows, registry ID snapshot, managed-registry expectations, and scaffold golden fixture directories before filing the implementation report. Because this slice does not delete source behavior or formal specifications, rollback does not require recovering removed runtime state.

## Pre-Filing Preflight

Preflight commands run before live filing:

```text
groundtruth-kb\.venv\Scripts\python.exe scripts\bridge_applicability_preflight.py --bridge-id gtkb-registry-scaffold-fixture-drift-reconciliation --content-file .gtkb-state\bridge-proposals\gtkb-registry-scaffold-fixture-drift-reconciliation-001.md
groundtruth-kb\.venv\Scripts\python.exe scripts\adr_dcl_clause_preflight.py --bridge-id gtkb-registry-scaffold-fixture-drift-reconciliation --content-file .gtkb-state\bridge-proposals\gtkb-registry-scaffold-fixture-drift-reconciliation-001.md
```

Observed results:

- Applicability preflight: `preflight_passed: true`, `missing_required_specs: []`, `missing_advisory_specs: []`, packet hash `sha256:9280f2ea2ce585d3bd8c59682973344a8e547c6383178589ad9e1dbe59c87e70`.
- Clause preflight: 5 clauses evaluated; `must_apply: 3`; evidence gaps in must-apply clauses: 0; blocking gaps: 0; exit 0.

The live filing is valid because the applicability and clause preflights both passed against this content file. Any future revision must rerun both preflights before live filing.
