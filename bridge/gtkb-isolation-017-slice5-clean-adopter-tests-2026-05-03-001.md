NEW

# Implementation Proposal — GTKB-ISOLATION-017 Slice 5

Proposed by: Prime Builder (Claude Code)
Date: 2026-05-03 (S328)
Subject: Clean-adopter test suite under `groundtruth-kb/tests/adopter/` covering the 10 named tests from Phase 9 §5 + 3 existing-adopter migration fixtures + golden-fixture diff machinery. CI auto-discovery (no workflow changes). Phase 6 overlay refresh/stale/disposability tests **deferred to a follow-on slice** because the underlying overlay infrastructure does not yet exist in the codebase.

## Context

GTKB-ISOLATION-017 is the adopter-packaging program. Slices 1, 2, 2.5, 3, 4 are VERIFIED. Slice 5 is the next gating slice per `bridge/gtkb-isolation-017-scoping-003.md` §"Sequencing Constraints" line 207: "Slice 5 (tests + overlay tests + CI wiring) after Slices 1-4 VERIFIED." Slice 4 closed terminally at `bridge/gtkb-isolation-017-slice4-upgrade-2026-05-02-012.md` 2026-05-03 — Slice 5 is now actionable.

Per `memory/work_list.md` TOP release-path directive, this is the productization-proof slice: "a fresh install behaves correctly from an adopter root without GT-KB product leakage." Owner pre-approved autonomous execution per the work_list contract.

## Specification Links

The implementation is constrained by, and shall not depart from, the following specifications, ADRs, DCLs, governance rules, and proposal carry-forwards:

1. **Phase 9 plan §5 — Clean-Adopter Tests** at `independent-progress-assessments/CODEX-INSIGHT-DROPBOX/GTKB-ISOLATION-009-PHASE9-ADOPTER-PACKAGING-AND-VALIDATION-PLAN-2026-04-23.md` lines 230–257 (10 named test files + 3 migration fixtures + golden-fixture diff requirement).
2. **Phase 9 plan §"Regression Visibility"** at the same plan lines 398–407 (CI must run the suite on every commit; doctor output must be deterministic).
3. **Phase 9 plan §"Exit Criteria" §4** at the same plan lines 341–352 (Phase 6 overlay refresh / stale / disposability behaviors). **NOTE:** the underlying Phase 6 overlay infrastructure does not exist in the codebase (verified by source probe; 0 matches for `def.*overlay`/`class.*Overlay` in `groundtruth-kb/src/`); the 3 overlay tests are scope-deferred per §"Out-of-scope" below.
4. **ADR-ISOLATION-APPLICATION-PLACEMENT-001** — adopter applications live at `<gt-kb-root>/applications/<name>/`.
5. **`.claude/rules/project-root-boundary.md`**, **`.claude/rules/file-bridge-protocol.md`**, **`.claude/rules/codex-review-gate.md`**.
6. **Scoping carry-forward** at `bridge/gtkb-isolation-017-scoping-003.md` lines 133–149 (Slice 5 acceptance criteria) + `-004` GO.
7. **GOV-09**, **GOV-18** (meaningful assertions, no rubber-stamp), **GOV-19** (outside-in testing), **GOV-20** (IPR + CVR).
8. **Prior Slice GOs (carry-forward only):**
    - Slice 1 `-012` VERIFIED — 9 isolation doctor checks via `run_isolation_checks` in `groundtruth-kb/src/groundtruth_kb/project/doctor_isolation.py:552`.
    - Slice 2 `-008` VERIFIED — managed-artifact registry with `owner` / `upgrade_policy` fields + AST-coverage gate at `groundtruth-kb/tests/test_registry_ast_coverage.py`.
    - Slice 2.5 `-008` VERIFIED — `OwnershipMeta.notes` rationale field.
    - Slice 3 `-014` VERIFIED — `gt project init` adopter-subject defaults + byte-level golden fixtures at `groundtruth-kb/tests/fixtures/scaffold_golden/{local-only,dual-agent}/` + capture script at `scripts/_capture_scaffold_golden.py`.
    - Slice 4 `-012` VERIFIED — `gt project upgrade --accept-migration` flow with 4 auto-fixers + receipts; isolation pre-flight gate inside `execute_upgrade()`.
9. **Prior Deliberations:**
    - `DELIB-S328-ISOLATION-017-SLICE4-DECISIONS-1-3-7-OWNER-DIRECTIVE` v1 (Slice 4 owner decisions — carried).
    - `DELIB-S324-PROJECT-ROOT-BOUNDARY-SANDBOX-EXCEPTION-CHOICE` (sandbox-output exception — referenced when Slice 5 fixtures need scratch space outside the project root, e.g., adopter scaffolding via `tmp_path`).
    - `python -m groundtruth_kb.cli deliberations search --query "clean-adopter test suite isolation"` (probe pending — see §"Open Items").

## Scope

### In-scope

Files created (new):

- `groundtruth-kb/tests/adopter/__init__.py` — package marker.
- `groundtruth-kb/tests/adopter/conftest.py` — shared fixtures: `_clean_adopter_factory(tmp_path)` returning a populated adopter root via `scaffold_project(...)`; `_existing_adopter_factory(tmp_path, fixture_name)` returning a pre-isolation-shaped fixture from the committed migration trees; helper `_setup_git(target)` mirroring the pattern in `tests/test_upgrade_isolation.py:67-78`.
- `groundtruth-kb/tests/adopter/test_init_defaults_to_application_subject.py` — Phase 9 §5 test 1 of 10.
- `groundtruth-kb/tests/adopter/test_init_scaffolds_adopter_owned_paths.py` — test 2.
- `groundtruth-kb/tests/adopter/test_init_refuses_to_overwrite_existing_adopter.py` — test 3.
- `groundtruth-kb/tests/adopter/test_upgrade_applies_registry_diff_under_receipts.py` — test 4.
- `groundtruth-kb/tests/adopter/test_upgrade_preserves_adopter_owned_files.py` — test 5.
- `groundtruth-kb/tests/adopter/test_upgrade_rollback_restores_prior_state.py` — test 6.
- `groundtruth-kb/tests/adopter/test_doctor_detects_isolation_violations.py` — test 7.
- `groundtruth-kb/tests/adopter/test_app_subject_cannot_mutate_product_artifacts.py` — test 8.
- `groundtruth-kb/tests/adopter/test_registry_entry_present_for_every_scaffolded_file.py` — test 9.
- `groundtruth-kb/tests/adopter/test_workstream_focus_retired_hook_stays_absent.py` — test 10.
- `groundtruth-kb/tests/adopter/test_golden_fixture_diff_per_version.py` — adopter-side byte-level diff against the Slice 3 golden trees per Phase 9 §5 line 251–252; asserts that `_clean_adopter_factory()` output matches the golden fixture for the current `__version__` (or fails with a clear diff message naming each drift file).
- `groundtruth-kb/tests/adopter/test_existing_adopter_migration_kit.py` — exercises the 3 migration fixtures end-to-end (per Phase 9 §5 line 253–257): pre-isolation fixture → `gt project upgrade --apply --accept-migration` → post-state matches the post-migration golden snapshot → rollback receipt exists + `gt project rollback` reverses.

Fixtures created (new) under `groundtruth-kb/tests/fixtures/adopter/`:

- `pre_isolation_minimal/` — minimal pre-isolation adopter (groundtruth.toml with raw-DB endpoint, missing canonical work-subject.json, legacy workstream-focus.py present, mis-headed release-readiness.md). Targets the 4 auto-fixable checks; `--accept-migration` should converge.
- `pre_isolation_with_managed_drift/` — pre-isolation adopter with one needs-adopter-input check failing (`isolation:no-writable-product-paths` via a stale managed file at the wrong location). Verifies `IsolationNonAutoFixableError` refusal path.
- `pre_isolation_under_product_root/` — adopter laid out **under** the product-root (triggers `isolation:adopter-root-placement` hard-refuse). Verifies `IsolationLocationFailureError` even with `--accept-migration`.

Existing files modified:

- `groundtruth-kb/.github/workflows/ci.yml` — add a comment-block reference (mirroring the Slice 2 reference at lines 21-29) noting that `tests/adopter/` is auto-discovered by the existing `pytest -v --tb=short` invocation; no actual workflow steps added.

Documents (per GOV-20):

- `IPR-SLICE5-CLEAN-ADOPTER-TESTS-001` — pre-implementation review citing this proposal, ADR-ISOLATION-APPLICATION-PLACEMENT-001, the Phase 9 §5 obligations, and the explicit overlay-test deferral.
- `CVR-SLICE5-CLEAN-ADOPTER-TESTS-001` — post-implementation proof (filed at post-impl + Codex VERIFIED time).

### Out-of-scope (explicitly deferred)

- **Phase 6 overlay refresh / stale / disposability tests** (per Phase 9 §4 lines 346–348). The underlying overlay infrastructure does not exist in `groundtruth-kb/src/` (probe at S328: `grep -rE "def.*overlay|class.*Overlay" groundtruth-kb/src/` returns 0 matches). Writing tests for non-existent capabilities would be either rubber-stamp (`pytest.mark.skip` boilerplate) or forward-spec without an executable contract; both violate GOV-18. Deferred to a follow-on slice (e.g., Slice 5.5 or a Phase-6-implementation slice). Tracked as work_list addition at proposal-GO time.
- Phase 9 §6 documentation chapter (Slice 6).
- Phase 9 §7 examples (Slice 7).
- Release ops + program closeout (Slice 8).
- Service-down behavior tests beyond what the existing Slice 1 isolation-doctor checks already exercise (the Phase 4 service endpoint scaffolding from Slice 3 is exercised by `test_doctor_detects_isolation_violations.py`'s `isolation:service-endpoint` assertion path; broader service-resilience tests are out of scope).
- Modifications to existing test files outside `tests/adopter/` — the Slice 4 `tests/test_upgrade_isolation.py` and pre-existing `tests/test_upgrade.py` carry forward unchanged.
- Multi-version golden-fixture diffing (per Phase 9 §5 line 251 "per GT-KB version"). Slice 5 ships golden-diff machinery for the **current** version only; multi-version regression coverage is a future enhancement filed as a separate work_list row.

## Implementation Plan

1. **Create the package + shared conftest** (~80 LOC).
   - `tests/adopter/__init__.py`: empty package marker.
   - `tests/adopter/conftest.py`: `_clean_adopter_factory(tmp_path: Path) -> Path` invokes `scaffold_project(target=tmp_path/'app', gt_kb_root=<derived>, profile='dual-agent', ...)` from `groundtruth_kb.project.scaffold` and returns the populated adopter root. `_existing_adopter_factory(tmp_path: Path, fixture_name: str) -> Path` copies the named fixture tree from `tests/fixtures/adopter/<fixture_name>/` into `tmp_path/'app'` + sets up git per the `_setup_git` pattern. Both factories use a `_pretend_product_root` sibling so `IsolationLocationFailureError` doesn't fire spuriously.

2. **Implement the 10 named tests** (~600–800 LOC tests; ~60-100 LOC each).
   - **`test_init_defaults_to_application_subject.py`**: factory produces an adopter; `gt project doctor` shows `isolation:work-subject` either absent or info-state; `groundtruth.toml`'s scaffolded `[service]` block matches the placeholder.
   - **`test_init_scaffolds_adopter_owned_paths.py`**: every `ownership=adopter-owned` file in the registry's scaffold-superset for the dual-agent profile is present in the produced tree (parameterized over the registry).
   - **`test_init_refuses_to_overwrite_existing_adopter.py`**: invoking `scaffold_project` on a path that already has `groundtruth.toml` raises `ValueError` with the existing-adopter message.
   - **`test_upgrade_applies_registry_diff_under_receipts.py`**: bump the scaffold to an old version, modify a managed file in the adopter to drift from template, run `gt project upgrade --apply` (no `--accept-migration` needed since no isolation failure), and assert the registry diff is applied + a receipt is written under `.claude/upgrade-receipts/active/`.
   - **`test_upgrade_preserves_adopter_owned_files.py`**: customize an `ownership=adopter-owned, upgrade_policy=preserve` file (e.g., the README), run `gt project upgrade --apply`, assert the customization is preserved byte-equal.
   - **`test_upgrade_rollback_restores_prior_state.py`**: snapshot pre-upgrade state; run upgrade; consume the receipt via `gt project rollback`; assert post-rollback state equals pre-upgrade state byte-for-byte.
   - **`test_doctor_detects_isolation_violations.py`**: parameterized over the 9 `_PARTITION_*` checks; for each, set up a fixture that triggers it and assert `run_isolation_checks` returns the matching `name` with status in `{"fail", "warning"}`.
   - **`test_app_subject_cannot_mutate_product_artifacts.py`**: from the clean-adopter fixture, attempt to write to a `gt-kb-managed` path in the adopter (e.g., `.claude/hooks/<managed-file>`); assert the operation either succeeds (filesystem-permits) but the post-write isolation check `isolation:no-writable-product-paths` fires, OR the operation is blocked by an established mechanism. (Test discipline note: this exercises the **detection** contract, not the **enforcement** contract — Slice 5 doesn't add new enforcement; it verifies the existing detection path covers the case.)
   - **`test_registry_entry_present_for_every_scaffolded_file.py`**: walk the produced adopter tree; for every file, assert it is registered in `managed-artifacts.toml` either as a `class=file` row or covered by an `ownership-glob` rule. Mirrors the Slice 2 AST-coverage test pattern but operates on a live scaffold rather than the template tree.
   - **`test_workstream_focus_retired_hook_stays_absent.py`**: clean adopter has no `.claude/hooks/workstream-focus.py`; `isolation:workstream-focus-hook-absent` passes; after `gt project upgrade --apply` (no accept-migration), the file remains absent.

3. **Implement the golden-fixture diff test** (~80 LOC):
   - `test_golden_fixture_diff_per_version.py`: factory produces a clean adopter at the current `__version__`; compare byte-by-byte against `tests/fixtures/scaffold_golden/dual-agent/`; report each drift file with a clear name + diff snippet on failure. Reuses the masking + extra-file/missing-file logic from `tests/test_scaffold_isolation.py:355-475` (TP14/TP15 byte-level fixture comparison).

4. **Capture the 3 migration fixtures** (~60 LOC fixture trees + ~120 LOC test):
   - `tests/fixtures/adopter/pre_isolation_minimal/`: 4-auto-fixable trigger fixture (groundtruth.toml with `endpoint = "groundtruth.db"`, `.claude/hooks/.workstream-focus-state.json` with `current_subject="platform"`, `.claude/hooks/workstream-focus.py` present, `memory/release-readiness.md` with wrong header).
   - `tests/fixtures/adopter/pre_isolation_with_managed_drift/`: 1 needs-adopter-input trigger (e.g., a stale registered hook file).
   - `tests/fixtures/adopter/pre_isolation_under_product_root/`: requires test-time placement under a synthetic product root in `tmp_path`; not a static tree — the test fixture writes the adopter into `<tmp_path>/applications/foo/` to trigger `isolation:adopter-root-placement`.
   - `test_existing_adopter_migration_kit.py`: parameterized over the 3 fixtures; for each, asserts the appropriate Slice 4 outcome (success / `IsolationNonAutoFixableError` / `IsolationLocationFailureError`).

5. **CI documentation comment** (~10 LOC): add a comment-block to `groundtruth-kb/.github/workflows/ci.yml` between the Slice 2 reference (lines 21-29) and the matrix definition, noting that `tests/adopter/` is auto-discovered by the existing `pytest -v --tb=short` invocation. No workflow steps added.

6. **Author IPR + CVR documents** per GOV-20 Phase 1 advisory pilot.

## Test Plan (spec-to-test mapping)

Each Slice 5 test maps directly to a Phase 9 §5 line. The 10 named tests + golden-diff + migration-kit form the test plan; their assertions are the spec-derived verification gate.

Specification → test mapping:

| Spec source | Test file |
|---|---|
| Phase 9 §5 line 235 | `test_init_defaults_to_application_subject.py` |
| Phase 9 §5 line 236 | `test_init_scaffolds_adopter_owned_paths.py` |
| Phase 9 §5 line 237 | `test_init_refuses_to_overwrite_existing_adopter.py` |
| Phase 9 §5 line 238 | `test_upgrade_applies_registry_diff_under_receipts.py` |
| Phase 9 §5 line 239 | `test_upgrade_preserves_adopter_owned_files.py` |
| Phase 9 §5 line 240 | `test_upgrade_rollback_restores_prior_state.py` |
| Phase 9 §5 line 241 | `test_doctor_detects_isolation_violations.py` |
| Phase 9 §5 line 242 | `test_app_subject_cannot_mutate_product_artifacts.py` |
| Phase 9 §5 line 243 | `test_registry_entry_present_for_every_scaffolded_file.py` |
| Phase 9 §5 line 244 | `test_workstream_focus_retired_hook_stays_absent.py` |
| Phase 9 §5 lines 251–252 | `test_golden_fixture_diff_per_version.py` |
| Phase 9 §5 lines 253–257 | `test_existing_adopter_migration_kit.py` (3 parameterized fixtures) |

Verification command for the post-impl: `python -m pytest groundtruth-kb/tests/adopter/ -v --tb=short` plus the existing full lane `python -m pytest groundtruth-kb/tests/ -q --tb=short` to confirm no cross-test interference.

## Acceptance Criteria

This NEW is GO-able when Codex confirms:

1. Specification Links cover all governing artifacts.
2. The 10 named test files from Phase 9 §5 are each present + map to their Phase 9 §5 line per the spec-to-test table.
3. Each test exercises an outside-in surface (GOV-19; CLI / `scaffold_project` / `run_isolation_checks` / `execute_upgrade` / `gt project rollback`) — not internal helpers.
4. Each test assertion is meaningful (GOV-18; named expected values, no rubber-stamp).
5. Golden-fixture diff machinery is byte-level + reports clear drift on failure.
6. 3 migration fixtures cover the 3 Slice 4 outcome paths (auto-fix success, needs-adopter-input refusal, hard-refuse).
7. CI auto-discovery confirmed: no workflow changes needed beyond the documentation comment.
8. **Phase 6 overlay tests are explicitly deferred + tracked** (work_list addition at GO time); no rubber-stamp `pytest.mark.skip` placeholders in the suite.
9. Estimated envelope ~900 LOC tests + 3 fixture trees + ~10 LOC CI comment.

## Risk / Rollback

**Risk 1 — Cross-test interference (medium).** 12 new test functions running in temp directories with git init each. Mitigation: every test uses `tmp_path` (pytest auto-cleanup); `_setup_git` runs in the per-test temp dir; fixtures are read-only template trees copied into per-test temp dirs.

**Risk 2 — CI runtime increase (low).** ~12 new test functions × ~1-3s each (git init + scaffold + assertions) = ~15-40s added to the lane. Mitigation: existing lane ~25s; total stays under typical CI budgets.

**Risk 3 — Golden-fixture brittleness (medium).** Byte-level diff against `tests/fixtures/scaffold_golden/dual-agent/` ties Slice 5 tests to Slice 3's golden snapshot. Any future scaffold change (e.g., adding a new template file) requires re-capturing the golden via `scripts/_capture_scaffold_golden.py` AND updating the Slice 5 expectations. Mitigation: same regeneration script Slice 3 ships; failure message names each drift file.

**Risk 4 — Phase 6 overlay deferral may surface a Codex NO-GO (low).** Codex may push back on deferral if it judges the overlay tests release-blocking for v0.7.0-rc1. Mitigation: the absence of overlay infrastructure is empirically verifiable (probe in §"Specification Links" item 3); deferral is the honest scope-correction per `feedback_scope_reduction_as_no_go_response.md`.

**Rollback path:** Slice 5 ships only test files + fixture trees + a CI documentation comment. No source code changes. Reversible via `git revert` of the implementation commit; no production impact possible.

## Decision Needed From Owner

**None at NEW time.** The Phase 6 overlay deferral is a scoping recommendation per the empirical absence-of-infrastructure probe; if Codex requests escalation to owner for the deferral itself, REVISED-1 surfaces it via AskUserQuestion at that time.

## Open Items

- `python -m groundtruth_kb.cli deliberations search --query "clean-adopter test suite isolation"` probe will run as part of Codex review's Prior Deliberations check; if it returns rows, this proposal will be revised to cite them.
- `_clean_adopter_factory` needs an `_pretend_product_root` sibling to avoid `isolation:adopter-root-placement` firing spuriously on the test fixture. The exact placement strategy will be validated in implementation; if the existing `scaffold_project(...)` API requires a different shape, REVISED-1 documents the adjustment.

---

*© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
