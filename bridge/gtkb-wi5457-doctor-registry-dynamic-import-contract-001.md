NEW

author_identity: prime-builder/codex/A
author_harness_id: A
author_session_context_id: 019f6668-9974-7d72-a456-826f9a67e627
author_model: OpenAI Codex
author_model_version: GPT-5.5
author_model_configuration: Codex Desktop interactive Prime Builder; transcript-defined PB role; build activity envelope; approval_policy=never
author_metadata_source: explicit_interactive_session_metadata

# WI-5457: Declare the doctor registry dynamic-import contract

bridge_kind: prime_proposal
Document: gtkb-wi5457-doctor-registry-dynamic-import-contract
Version: 001
Date: 2026-07-17 UTC

Project Authorization: PAUTH-PROJECT-GTKB-TREE-STABILIZATION-20260715-PROJECT-SCOPE
Project: PROJECT-GTKB-TREE-STABILIZATION
Work Item: WI-5457

target_paths: ["groundtruth-kb/src/groundtruth_kb/project/checks/__init__.py", "platform_tests/scripts/test_doctor_registry_dynamic_import_contract.py"]

implementation_scope: source,test
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

## Summary

Declare the two intentional `importlib.import_module` calls inside
`get_registered_checks()` through the production artifact scanner's literal
function contract. Add one dedicated regression proving both calls are
declared with a nonempty rationale and no unresolved `<dynamic>` request
remains.

This is the missing dependency exposed by the mandatory WI-5414 and WI-5423
verification suite. Implementation must wait until WI-5415 reaches independent
VERIFIED and focused finalization because WI-5415 currently owns the same
doctor-registry source. This proposal does not authorize overlap with that
nonterminal report.

## Claim

Prime Builder proposes one additive source declaration and one new focused
test. The source change must preserve WI-5415's ADR-compliant `pkgutil`
discovery behavior exactly. The scanner, frozen lifecycle tests, registry
modules, dispatcher, TAFE, harness state, MemBase, Git index, and unrelated
worktree bytes are outside implementation scope.

## Requirement Sufficiency

Existing requirements sufficient. `ADR-REGISTRY-DISCOVERY-001` requires
extensible dynamic discovery, while
`DCL-CHANGE-CONTROLLED-ARTIFACT-EVALUABILITY-001` requires the intentional
dynamic imports to be deterministically classified. The existing literal
`__gtkb_dynamic_import_contract__` mechanism and linked TEST-11558 fully define
the bounded correction. No requirement revision is needed.

## In-Root Placement Evidence

Both target paths are inside `E:\GT-KB`. The production target is GT-KB
platform source and the test target is the platform test tree. No adopter,
archive, out-of-root, credential, deployment, or release path is in scope.

## Specification Links

- `ADR-REGISTRY-DISCOVERY-001` - preserves dynamic future-module discovery and rejects a hardcoded module list.
- `DCL-CHANGE-CONTROLLED-ARTIFACT-EVALUABILITY-001` - requires intentional non-literal imports to carry deterministic, nonempty declaration evidence.
- `ADR-OBSOLETE-REFERENCE-PURGE-OBLIGATION-001` - requires the live loading graph to remain free of unresolved dependencies and contamination findings.
- `GOV-WORK-TREE-HYGIENE-001` - requires exact source/test ownership without absorbing WI-5415 or unrelated dirt.
- `GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001` - requires the explicit baseline, result, rollback, invariants, and fail-closed disposition below.
- `GOV-FILE-BRIDGE-AUTHORITY-001` - requires independent GO before protected source/test mutation and independent VERIFIED after implementation.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - requires concrete linkage to every governing requirement.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - binds WI-5457 to its active project authorization and exact targets.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - requires executed spec-derived evidence before VERIFIED.
- `DCL-PROJECT-DEPENDENCY-ORDERING-001` - prevents implementation while WI-5415 owns the shared source.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` - preserves the discovered omission as WI-5457 and TEST-11558.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` - links source, test, proposal, implementation report, verdict, and finalization evidence.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - keeps proposal, blocked dependency, implementation, verification, and terminal states explicit.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - keeps the platform correction inside the GT-KB root and outside adopter scope.

## Prior Deliberations

- The owner's active program goal and standing directive require every discovered black-box or modernization omission to become governed child work and reach VERIFIED terminal closure.
- `bridge/gtkb-wi5415-doctor-registry-dynamic-discovery-003.md` - current implementation report restoring the intentional dynamic loader and owning the shared source until terminal finalization.
- `bridge/gtkb-wi5414-artifact-lifecycle-package-residue-003.md` - mandatory-suite NO-ACTION that reproduces both unresolved import lines.
- `bridge/gtkb-wi5423-artifact-dynamic-import-contract-residue-003.md` - sibling mandatory-suite NO-ACTION reproducing the same dependency.
- WI-5457 and linked TEST-11558 - MemBase artifacts created through the governed `gt backlog add-work-item` service and assigned to `PHASE-014`.

## Owner Decisions / Input

No new owner decision is required. The owner explicitly directed this program
to create all necessary child work and drive it to terminal VERIFIED closure.
Active project authorization
`PAUTH-PROJECT-GTKB-TREE-STABILIZATION-20260715-PROJECT-SCOPE` permits bounded
bridge, source, and test work while preserving independent GO, claim,
implementation-start, verification, and mechanical finalization gates.

## Proposed Scope

- After WI-5415 is independently VERIFIED and finalized, add one module-level literal `__gtkb_dynamic_import_contract__` mapping keyed only by `get_registered_checks`.
- Use one nonempty rationale explaining that doctor modules are discovered from the package path and imported dynamically so decorator registration remains extensible.
- Add `platform_tests/scripts/test_doctor_registry_dynamic_import_contract.py` to parse the exact production source through `scripts.check_artifact_decontamination._import_requests`.
- Assert that the two dynamic calls are represented as two declared dynamic-import records for `get_registered_checks`, share the exact nonempty contract rationale, and produce no `<dynamic>` request.
- Re-run WI-5415's 23-test discovery boundary and the frozen 24-test artifact-decontamination suite.
- Do not edit the scanner, hardcode modules, change registry semantics, touch any third path, or perform a database, dispatcher, TAFE, harness, Git, release, deployment, credential, cleanup, or external-system mutation.

## Intuitiveness/Non-Impairment Disposition

```json
{
  "schema_version": 1,
  "applicability": "applicable",
  "provenance": "WI-5457; TEST-11558; WI-5414 v003 and WI-5423 v003 fresh 23/24 mandatory-suite evidence; WI-5415 v003 dynamic-discovery implementation report",
  "canonical_authority": "ADR-REGISTRY-DISCOVERY-001; DCL-CHANGE-CONTROLLED-ARTIFACT-EVALUABILITY-001; ADR-OBSOLETE-REFERENCE-PURGE-OBLIGATION-001; GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001",
  "primary_route": "The production doctor registry keeps pkgutil discovery and declares its two intentional dynamic imports through the scanner's existing literal function contract",
  "before_behavior": "The ADR-compliant loader discovers future check modules correctly, but the artifact scanner reports both non-literal imports as unresolved and fails the live repository contract",
  "after_behavior": "The same loader behavior remains intact while the scanner records two reviewed declared imports with one explicit nonempty function rationale and zero unresolved dynamic requests",
  "self_descriptive_naming": "__gtkb_dynamic_import_contract__, get_registered_checks, and test_doctor_registry_dynamic_import_contract identify the declaration, function boundary, and regression directly",
  "obsolete_guidance_disposition": "No guidance, registry module list, scanner rule, historical artifact, or prior bridge record is replaced; hardcoded dispatch remains rejected",
  "history_preservation": "WI-5415 source ownership, numbered bridge files, MemBase rows, exact source history, package modules, and all unrelated worktree bytes remain preserved",
  "baseline": "The frozen artifact-decontamination suite passes 23 of 24 and reports unresolved imports at project/checks/__init__.py lines 33 and 37",
  "expected_result": "The dedicated regression observes two declared imports and zero unresolved requests, WI-5415 discovery tests pass 23 of 23, and the frozen artifact-decontamination suite passes 24 of 24",
  "rollback": "A separately governed focused revert removes only the WI-5457 contract declaration and dedicated test after preserving append-only bridge and MemBase evidence",
  "hard_invariants": "No hardcoded module list, discovery behavior change, scanner weakening, broad exemption, third target, peer hunk absorption, database mutation, dispatcher/TAFE/harness mutation, or Git/release/deployment operation",
  "fail_closed_conditions": "WI-5415 is nonterminal, shared-path ownership is ambiguous, the contract is not a literal nonempty function mapping, either call remains unresolved, declared-import count is not two, discovery tests regress, any frozen test fails, authority is stale, or any target drifts",
  "essential_context_preservation": "Verification retains the two exact call lines, function name, rationale, future-module discovery proof, full loading-graph audit, target hashes, and independent bridge/start/finalization evidence"
}
```

## Specification-Derived Verification Plan

| Governing surface | Verification | Expected result |
| --- | --- | --- |
| `DCL-PROJECT-DEPENDENCY-ORDERING-001`; `GOV-WORK-TREE-HYGIENE-001` | Inspect WI-5415's latest bridge status, target ownership, focused finalization evidence, and current scoped diff before implementation start | WI-5415 is terminal VERIFIED/finalized; neither WI-5457 target is owned by a nonterminal peer; only attributable WI-5457 hunks are present. |
| `ADR-REGISTRY-DISCOVERY-001` | `groundtruth-kb/.venv/Scripts/python.exe -m pytest groundtruth-kb/tests/test_doctor_stale_test_slots.py platform_tests/scripts/test_check_gt_cli_availability.py platform_tests/scripts/test_fab08_slot_leak_fix.py -q --tb=short` | 23 tests pass, including synthetic future-module discovery; source retains `pkgutil.iter_modules` and no hardcoded check-module list. |
| `DCL-CHANGE-CONTROLLED-ARTIFACT-EVALUABILITY-001`; TEST-11558 | `groundtruth-kb/.venv/Scripts/python.exe -m pytest platform_tests/scripts/test_doctor_registry_dynamic_import_contract.py -q --tb=short` | The exact source yields two declared records for `get_registered_checks`, one nonempty shared rationale, and zero unresolved `<dynamic>` requests. |
| `ADR-OBSOLETE-REFERENCE-PURGE-OBLIGATION-001` | `groundtruth-kb/.venv/Scripts/python.exe -m pytest platform_tests/scripts/test_modernization_artifact_decontamination.py -q --tb=short --timeout=600` | All 24 frozen tests pass and the live repository audit has no unresolved import finding. |
| Python and exact-scope quality | Ruff check, Ruff format check, `py_compile`, `git diff --check`, target SHA-256 values, and exact authorization validation for both paths | All checks pass; exactly one source declaration hunk and one new dedicated test are attributable to WI-5457. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | Independent LO reruns every mapped command against the exact report bytes | VERIFIED is allowed only when every mapped result and target hash matches the implementation report. |

## Acceptance Criteria

- WI-5415 is terminal VERIFIED/finalized before WI-5457 implementation start.
- The source contains exactly one nonempty `get_registered_checks` dynamic-import contract entry and retains its `pkgutil` discovery implementation.
- The dedicated regression observes two declared dynamic imports for `get_registered_checks`, a shared nonempty rationale, and zero unresolved `<dynamic>` requests.
- WI-5415's complete 23-test boundary passes.
- The frozen artifact-decontamination suite passes 24 of 24 without modifying or weakening the scanner or its existing tests.
- Ruff check, Ruff format check, `py_compile`, `git diff --check`, exact target authorization, applicability preflight, and mandatory clause preflight pass.
- Independent LO VERIFIED and focused mechanical finalization occur before WI-5457, WI-5414, or WI-5423 is treated terminal.

## Risk / Rollback

The main risk is turning a narrow intentional dynamic seam into a broad
scanner exemption. The exact function-name key, nonempty literal rationale,
two-record regression, unchanged scanner, and unchanged discovery tests bound
that risk.

Rollback is a separately governed focused revert of the declaration and
dedicated test only. Bridge files and MemBase history remain append-only.

## Files Expected To Change

- `groundtruth-kb/src/groundtruth_kb/project/checks/__init__.py`
- `platform_tests/scripts/test_doctor_registry_dynamic_import_contract.py`

## Bridge Filing

This proposal is the first status-bearing numbered file for
`gtkb-wi5457-doctor-registry-dynamic-import-contract`. No WI-5415, WI-5414,
WI-5423, or historical artifact is rewritten or deleted.

## Recommended Commit Type

`fix` - declare an intentional dynamic loading boundary omitted from the
artifact-decontamination contract.

---

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
