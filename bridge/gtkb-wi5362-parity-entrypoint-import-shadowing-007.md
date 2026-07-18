NEW

author_identity: prime-builder/codex/A
author_harness_id: A
author_session_context_id: 019f6668-9974-7d72-a456-826f9a67e627
author_model: OpenAI Codex
author_model_version: gpt-5
author_model_configuration: Codex Desktop interactive Prime Builder; transcript-defined PB role via ::init gtkb pb; build envelope
author_metadata_source: explicit_interactive_session_metadata

# WI-5362 Implementation Report - Parity Entrypoint Import Shadowing

bridge_kind: implementation_report
Document: gtkb-wi5362-parity-entrypoint-import-shadowing
Version: 007
Implements: bridge/gtkb-wi5362-parity-entrypoint-import-shadowing-006.md
Approved proposal: bridge/gtkb-wi5362-parity-entrypoint-import-shadowing-005.md
Project Authorization: PAUTH-DISPATCHER-BLACK-BOX-WI5362-PARITY-ENTRYPOINT-IMPORT-20260716
Project: PROJECT-GTKB-OPS-DISPATCHER-MODERNIZATION-DISPATCHER-BLACK-BOX-HARDENING
Work Item: WI-5362

target_paths: ["scripts/check_harness_parity.py", "platform_tests/scripts/test_check_harness_parity_entrypoint_import.py"]

implementation_scope: source and focused tests
requires_verification: true
kb_mutation_in_scope: false

## Summary

Implemented the approved two-file WI-5362 repair. `scripts/check_harness_parity.py` no longer imports the local adapter generators through the ambiguous package name `scripts`. It now resolves its own sibling script directory and loads `harness_projection_reader.py`, `generate_codex_skill_adapters.py`, `generate_antigravity_skill_adapters.py`, and `generate_api_skill_adapters.py` by exact file path through `importlib.util.spec_from_file_location`.

The loader registers each local module under its normal module name before execution so sibling imports inside the generator modules continue to work. If a local sibling module raises a genuine import error during execution, the error is re-raised and the temporary `sys.modules` entry is cleaned up, so real generator failures remain visible.

Added `platform_tests/scripts/test_check_harness_parity_entrypoint_import.py` to prove direct script execution ignores a conflicting external `scripts` package, that the generator module provenance is repository-local, and that genuine local generator import failures are not masked.

No dispatcher, TAFE, runtime, harness eligibility, routing, lease, registry, credential, release, deployment, Git history, or MemBase mutation was made.

## Implementation-Start Evidence

- Work-intent claim: `go_implementation`, row `32109`, acquired `2026-07-17T09:45:11Z`, session `019f6668-9974-7d72-a456-826f9a67e627`.
- Implementation-start command: `python scripts\implementation_authorization.py begin --bridge-id gtkb-wi5362-parity-entrypoint-import-shadowing --session-id 019f6668-9974-7d72-a456-826f9a67e627`.
- Implementation-start result: latest status `GO`; proposal `bridge/gtkb-wi5362-parity-entrypoint-import-shadowing-005.md`; GO file `bridge/gtkb-wi5362-parity-entrypoint-import-shadowing-006.md`; packet hash `sha256:2970fdf18f9571296b371f0ab5bc152a56458a9a51743d41768c736496ec1b7f`; pre-start packet hash `sha256:f1cd549fd4222d161db306bb948093d41374836288eee6cb64af1497d7ce4877`.
- Authorized target globs: `scripts/check_harness_parity.py`, `platform_tests/scripts/test_check_harness_parity_entrypoint_import.py`.
- Target-scope preflight: `python scripts\impl_start_target_paths_preflight.py --bridge-id gtkb-wi5362-parity-entrypoint-import-shadowing --candidate-paths scripts/check_harness_parity.py platform_tests/scripts/test_check_harness_parity_entrypoint_import.py --json` returned `verdict: in_scope`, `out_of_scope: []`, and `unused_targets: []`.

## Files Changed

- `scripts/check_harness_parity.py` - replaces package-name fallback imports with exact sibling-file module loading for the projection reader and adapter generators.
- `platform_tests/scripts/test_check_harness_parity_entrypoint_import.py` - adds focused subprocess/provenance/import-failure regression coverage for TEST-11478.

The bridge implementation-report helper plan reported `files_changed_count: 2` and `excluded_dirty_count: 1459`; the excluded dirty files are unrelated live worktree state and were not adopted into this implementation report.

## Specification Links

- `DCL-CROSS-HARNESS-PARITY-ENFORCEMENT-001` - governs the Phase 1 parity evaluator and requires deterministic, truthful cross-harness parity evidence.
- `GOV-FILE-BRIDGE-AUTHORITY-001` - requires independent review before either protected target is changed and preserves numbered bridge state.
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` - binds implementation to the active WI-5362 project authorization and exact proposal paths.
- `DCL-PROJECT-AUTHORIZATION-OPERATION-TIME-ENFORCEMENT-001` - requires a live claim and implementation-start packet before protected mutation.
- `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001` - requires shared-path conflict handling and exact target ownership.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - requires concrete specification links carried forward from the proposal.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - requires machine-readable PAUTH, project, work-item, and target-path linkage.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - requires this report to map specifications to executed verification evidence.
- `GOV-STANDING-BACKLOG-001` - governs preservation of WI-5362 and linked TEST-11478 as durable backlog/test evidence.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` - requires the reproduced failure, authorization, proposal, implementation, test, and verdict to remain durable governed artifacts.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` - establishes the artifact-first workflow used to move this defect from evidence through independent verification.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - requires the concrete parity failure to trigger a governed work item and proposal.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - requires every source, test, draft, and bridge artifact used by this repair to remain within `E:\GT-KB`.
- `GOV-WORK-TREE-HYGIENE-001` - requires foreign hunks and unrelated dirty worktree state to be excluded rather than silently absorbed.

## Specification-Derived Verification

| Governing surface | Verification command | Observed result |
| --- | --- | --- |
| `DCL-PROJECT-AUTHORIZATION-OPERATION-TIME-ENFORCEMENT-001`; `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001`; `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001` | `python scripts\implementation_authorization.py begin --bridge-id gtkb-wi5362-parity-entrypoint-import-shadowing --session-id 019f6668-9974-7d72-a456-826f9a67e627` | PASS. Latest status `GO`; active PAUTH `PAUTH-DISPATCHER-BLACK-BOX-WI5362-PARITY-ENTRYPOINT-IMPORT-20260716`; target globs exactly the two approved files. |
| `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001`; `GOV-WORK-TREE-HYGIENE-001` | `python scripts\impl_start_target_paths_preflight.py --bridge-id gtkb-wi5362-parity-entrypoint-import-shadowing --candidate-paths scripts/check_harness_parity.py platform_tests/scripts/test_check_harness_parity_entrypoint_import.py --json` | PASS. `verdict: in_scope`; `out_of_scope: []`; `unused_targets: []`. |
| `DCL-CROSS-HARNESS-PARITY-ENFORCEMENT-001`; TEST-11478 | `python -m pytest platform_tests/scripts/test_check_harness_parity_entrypoint_import.py -q --tb=short` | PASS. `3 passed in 0.89s`. |
| `DCL-CROSS-HARNESS-PARITY-ENFORCEMENT-001` | `python scripts\check_harness_parity.py --all --markdown` | PASS for the WI-5362 import behavior: command reached `# Harness Parity Review` with no import traceback and no external `scripts` provenance. Overall command exit was `1` because the live parity report still contains pre-existing fleet findings (`DEGRADED: 52`, `MISSING: 69`, `UNSUPPORTED: 145`). |
| Regression preservation | `python -m pytest platform_tests/scripts/test_check_harness_parity.py platform_tests/scripts/test_generate_antigravity_skill_adapters.py platform_tests/scripts/test_generate_api_skill_adapters.py -q --tb=short` | PARTIAL / unrelated existing failure. `52 passed`; `test_repository_registry_has_no_unclassified_missing_rows` fails on pre-existing Goose missing capability-surface rows in the live registry. No WI-5362 focused or generator regression failed. |
| Phase parity integration | `python scripts\harness_parity_phase2.py --project-root . --format markdown` | PASS execution with existing WARN data: overall `WARN`; counts `needs_adapter: 5`, `supported: 63`, `waived: 2`; Goose excluded as retired. |
| Phase parity integration | `python scripts\parity_discovery_diff.py --project-root . --markdown` | PASS. Overall status `PASS`; unwaived asymmetries `0`. |
| Source quality | `python -m ruff check scripts\check_harness_parity.py platform_tests\scripts\test_check_harness_parity_entrypoint_import.py` | PASS. `All checks passed!` |
| Source formatting | `python -m ruff format --check scripts\check_harness_parity.py platform_tests\scripts\test_check_harness_parity_entrypoint_import.py` | PASS. `2 files already formatted`. |
| Whitespace | `git diff --check -- scripts\check_harness_parity.py platform_tests\scripts\test_check_harness_parity_entrypoint_import.py` | PASS with only Git's line-ending warning for `scripts/check_harness_parity.py`; exit code `0`. |

## Acceptance Criteria

- Direct entrypoint import shadowing is repaired: satisfied. A conflicting external `scripts` package on `PYTHONPATH` no longer prevents `scripts/check_harness_parity.py --all --markdown` from reaching the parity report.
- Local generator provenance is deterministic: satisfied. The focused test asserts the three adapter generator modules resolve to `E:\GT-KB\scripts\generate_*_skill_adapters.py`.
- Genuine local import failures remain visible: satisfied. The focused test injects a broken local sibling module and verifies its `ImportError` propagates.
- `scripts/__init__.py` is not required: satisfied. The implementation loads exact sibling files and does not create or depend on `scripts/__init__.py`.
- Existing checker/generator behavior remains intact: satisfied for all focused and generator tests; one broader repository-registry parity assertion still fails on unrelated pre-existing Goose missing rows and is reported above.
- Scope remains exact: satisfied. Only the two authorized target files changed.

## Risk And Rollback

Risk remains low and localized to module loading for the parity checker. The new loader is intentionally used only by `scripts/check_harness_parity.py`; it does not change generator modules, registry semantics, harness eligibility, adapter outputs, dispatcher, TAFE, runtime, credential handling, release, deployment, Git history, or MemBase.

Rollback is a focused revert of the loader change in `scripts/check_harness_parity.py` and removal of `platform_tests/scripts/test_check_harness_parity_entrypoint_import.py`, followed by rerunning the focused parity tests.

## Recommended Commit Type

Recommended commit type: `fix`

---

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
