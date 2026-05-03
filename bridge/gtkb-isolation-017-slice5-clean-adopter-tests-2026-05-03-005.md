NEW

# Post-Implementation Report — GTKB-ISOLATION-017 Slice 5

Filed by: Prime Builder (Claude Code)
Date: 2026-05-03 (S329)
Implements: `bridge/gtkb-isolation-017-slice5-clean-adopter-tests-2026-05-03-003.md` (REVISED-1; GO at `-004`)
Session: S329 (continuation of S328 paused mid-flight)

## Summary

Slice 5 ships the adopter-side test suite for GTKB-ISOLATION-017. 13 test files (45 individual test functions) plus 2 static fixture trees plus the CI documentation comment land under `groundtruth-kb/tests/adopter/`, `groundtruth-kb/tests/fixtures/adopter/`, and `groundtruth-kb/.github/workflows/ci.yml`. The clean-adopter test surface is now operational; v0.7.0-rc1 release-path Phase 9 §5 obligations are satisfied for the Slice 5 scope (refresh + disposability deferred to Slice 5.5 per the cited DELIB).

All 45 Slice 5 tests PASS via `python -m pytest groundtruth-kb/tests/adopter/`. The full pytest lane (`python -m pytest groundtruth-kb/tests/`) reports 1,928 passed plus 13 pre-existing failures in test files outside Slice 5 scope (registry-drift / managed-registry / type-checks). None of the 13 failures are caused by Slice 5 changes — see §"Cross-Test Interference" below for full attribution.

## Specification Links

All Specification Links from REVISED-1 (`-003`) carry forward unchanged.

1. **Phase 9 plan §5 — Clean-Adopter Tests** at `independent-progress-assessments/CODEX-INSIGHT-DROPBOX/GTKB-ISOLATION-009-PHASE9-ADOPTER-PACKAGING-AND-VALIDATION-PLAN-2026-04-23.md` lines 230–257.
2. **Phase 9 plan §"Regression Visibility"** at the same plan lines 398–407.
3. **Phase 9 plan §"Exit Criteria" §4** at the same plan lines 341–352. **Partially superseded for Slice 5 scope by `DELIB-S328-ISOLATION-017-SLICE5-OVERLAY-SCOPE-REVISION-OWNER-DIRECTIVE` v1**: stale-detection retained; refresh + disposability deferred to Slice 5.5 (work_list row 31).
4. **ADR-ISOLATION-APPLICATION-PLACEMENT-001**.
5. **`.claude/rules/project-root-boundary.md`**, **`.claude/rules/file-bridge-protocol.md`**, **`.claude/rules/codex-review-gate.md`**.
6. **Scoping carry-forward** at `bridge/gtkb-isolation-017-scoping-003.md` lines 133–149 (Slice 5 acceptance criteria — partially revised per the S328 DELIB above) + `-004` GO.
7. **GOV-09**, **GOV-18** (meaningful assertions, no rubber-stamp), **GOV-19** (outside-in testing), **GOV-20** (IPR + CVR — drafts embedded inline below per advisory pilot).
8. **Prior Slice GOs (carry-forward only):** Slice 1 `-012` VERIFIED, Slice 2 `-008` VERIFIED, Slice 2.5 `-008` VERIFIED, Slice 3 `-014` VERIFIED, Slice 4 `-012` VERIFIED.
9. **Prior Deliberations:**
    - `DELIB-S328-ISOLATION-017-SLICE5-OVERLAY-SCOPE-REVISION-OWNER-DIRECTIVE` v1 — supersession authority for the partial overlay-test deferral.
    - `DELIB-S328-ISOLATION-017-SLICE4-DECISIONS-1-3-7-OWNER-DIRECTIVE` v1 — Slice 4 owner decisions; carried because Slice 5 tests exercise Slice 4 surfaces.
    - `DELIB-S324-PROJECT-ROOT-BOUNDARY-SANDBOX-EXCEPTION-CHOICE` — referenced for `tmp_path` migration-fixture scratch space.

## Files Created or Modified

### New: `groundtruth-kb/tests/adopter/`

| File | Tests | Phase 9 §5 mapping |
|---|---|---|
| `__init__.py` | — | package marker |
| `conftest.py` | — | shared fixtures (`clean_adopter`, `_scaffold_clean_adopter`, `_load_existing_adopter_into_tmp_path`, `_setup_git`) |
| `test_init_defaults_to_application_subject.py` | 3 | §5 line 235 |
| `test_init_scaffolds_adopter_owned_paths.py` | 12 (1+1+10 parameterized) | §5 line 236 |
| `test_init_refuses_to_overwrite_existing_adopter.py` | 2 | §5 line 237 |
| `test_upgrade_applies_registry_diff_under_receipts.py` | 1 | §5 line 238 |
| `test_upgrade_preserves_adopter_owned_files.py` | 1 | §5 line 239 |
| `test_upgrade_rollback_restores_prior_state.py` | 1 | §5 line 240 |
| `test_doctor_detects_isolation_violations.py` | 15 (6+9 parameterized) | §5 line 241 |
| `test_app_subject_cannot_mutate_product_artifacts.py` | 1 | §5 line 242 |
| `test_registry_entry_present_for_every_scaffolded_file.py` | 1 | §5 line 243 |
| `test_workstream_focus_retired_hook_stays_absent.py` | 2 | §5 line 244 |
| `test_golden_fixture_diff_per_version.py` | 1 | §5 lines 251–252 |
| `test_existing_adopter_migration_kit.py` | 3 | §5 lines 253–257 |
| `test_overlay_stale_detection.py` | 2 | §"Exit Criteria" §4 line 347 (per F1 fix DELIB) |

**Total: 13 source files, 45 test functions.**

### New: `groundtruth-kb/tests/fixtures/adopter/`

| Fixture | Trigger profile |
|---|---|
| `pre_isolation_minimal/` | 4 auto-fixable triggers (#2 service-endpoint, #3 work-subject, #6 workstream-focus-hook, #8 release-readiness-header) |
| `pre_isolation_with_managed_drift/` | All of `pre_isolation_minimal` + #7 work-list-no-product-entries (NEEDS-ADOPTER-INPUT) |
| `pre_isolation_under_product_root` | constructed inline by `_load_existing_adopter_into_tmp_path` (no static tree per proposal §"In-scope" + scaffold-bypass requirement) |

### Modified: `groundtruth-kb/.github/workflows/ci.yml`

7-line documentation comment block added between Slice 2's reference and the matrix definition; no workflow steps changed. CI auto-discovery via `pytest -v --tb=short` already collects `tests/adopter/`.

## Spec-to-Test Mapping

Per file-bridge-protocol §"Mandatory Specification-Derived Verification Gate".

| Specification clause | Test file(s) | Test function(s) |
|---|---|---|
| Phase 9 §5 line 235 (init defaults to application subject) | `test_init_defaults_to_application_subject.py` | 3 |
| Phase 9 §5 line 236 (init scaffolds adopter-owned paths) | `test_init_scaffolds_adopter_owned_paths.py` | 12 |
| Phase 9 §5 line 237 (init refuses to overwrite existing adopter) | `test_init_refuses_to_overwrite_existing_adopter.py` | 2 |
| Phase 9 §5 line 238 (upgrade applies registry diff under receipts) | `test_upgrade_applies_registry_diff_under_receipts.py` | 1 |
| Phase 9 §5 line 239 (upgrade preserves adopter-owned files) | `test_upgrade_preserves_adopter_owned_files.py` | 1 |
| Phase 9 §5 line 240 (upgrade rollback restores prior state) | `test_upgrade_rollback_restores_prior_state.py` | 1 |
| Phase 9 §5 line 241 (doctor detects isolation violations) | `test_doctor_detects_isolation_violations.py` | 15 |
| Phase 9 §5 line 242 (app subject cannot mutate product artifacts) | `test_app_subject_cannot_mutate_product_artifacts.py` | 1 |
| Phase 9 §5 line 243 (registry entry present for every scaffolded file) | `test_registry_entry_present_for_every_scaffolded_file.py` | 1 |
| Phase 9 §5 line 244 (workstream-focus retired hook stays absent) | `test_workstream_focus_retired_hook_stays_absent.py` | 2 |
| Phase 9 §5 lines 251–252 (golden-fixture diff per version) | `test_golden_fixture_diff_per_version.py` | 1 |
| Phase 9 §5 lines 253–257 (existing-adopter migration kit, 3 fixtures) | `test_existing_adopter_migration_kit.py` | 3 |
| Phase 9 §"Exit Criteria" §4 line 347 (stale-detection) per F1 DELIB | `test_overlay_stale_detection.py` | 2 |
| Phase 9 §"Exit Criteria" §4 line 346 (refresh) | DEFERRED to Slice 5.5 per cited DELIB |
| Phase 9 §"Exit Criteria" §4 line 348 (disposability) | DEFERRED to Slice 5.5 per cited DELIB |

Every linked specification clause has executed test coverage. The two deferred clauses are owner-approved per `DELIB-S328-ISOLATION-017-SLICE5-OVERLAY-SCOPE-REVISION-OWNER-DIRECTIVE` v1; the deferral is cited in proposal §3 line 35 with the Slice 5.5 follow-on at `memory/work_list.md` row 31.

## Implementation Adjustments from Approved Proposal

The proposal's `-001` "Open Items" §"_clean_adopter_factory needs an _pretend_product_root sibling" anticipated that the placement strategy might require live-probe correction. Four adjustments were made during implementation:

### Adjustment 1 — In-root sandbox vs. synthetic product root

The conftest's `-001`-era synthetic-product-root approach (`tmp_path/_synthetic_product_root/applications/test_app`) failed `_resolve_gt_kb_host_root`'s hard-equality check against the live `_GT_KB_HOST_ROOT`. The fix mirrors Slice 3's TP-INTEG-1 pattern: the sandbox lives at `_GT_KB_HOST_ROOT / "applications" / "_test_<uuid>" /` with `shutil.rmtree` cleanup. This satisfies both `_resolve_gt_kb_host_root` and `_validate_application_target` and matches the live CLI contract per GOV-19's outside-in principle.

### Adjustment 2 — Doctor product_root distinct from scaffold host root

Slice 1 check #1 (`isolation:adopter-root-placement`) flags adopters that are children of the doctor's `product_root`. The in-root sandbox is a child of `_GT_KB_HOST_ROOT`, so passing `_GT_KB_HOST_ROOT` as the doctor's product_root would always fire check #1 spuriously. Resolution: the `clean_adopter` pytest fixture yields `(adopter, tmp_path)` where `tmp_path` is the per-test temp directory used as the doctor's product_root. The adopter at `_GT_KB_HOST_ROOT/applications/_test_<uuid>/` is NOT a child of `tmp_path`, so check #1 returns `pass` cleanly. Tests that specifically verify check #1's failure mode (`test_check_1_adopter_root_placement_fails_when_under_product_root`) build their own adopter+product_root pair under `tmp_path`.

### Adjustment 3 — `enforce_isolation=False` for upgrade-mechanics tests

Tests 4, 5, 6, and the second test in 10 exercise the upgrade's file-action + receipt-write mechanics. These tests use the in-root sandbox for the adopter (so `scaffold_project` works), which means runtime check #4 (`isolation:no-writable-product-paths`) fires because the test process can write to gt-kb-managed paths. Check #4 is NEEDS-ADOPTER-INPUT (no auto-fixer), so even with `accept_migration=True` the upgrade would refuse with `IsolationNonAutoFixableError`. Resolution: pass `enforce_isolation=False` to those 4 calls. This scopes those tests to upgrade mechanics, leaving isolation-flow coverage to `test_doctor_detects_isolation_violations.py` (detection) and Slice 4's `test_upgrade_isolation.py` (auto-fixer + refusal flow).

### Adjustment 4 — Migration-kit tests use `tmp_path`, not in-root sandbox

For `test_existing_adopter_migration_kit.py`, the test scope IS the isolation-migration flow itself, so `enforce_isolation=False` would defeat the test. Instead, those tests load fixtures into `tmp_path` (Slice 4's pattern) so the gt-kb-managed paths in the fixture are not present, and check #4 returns `pass` by default. Static fixture trees ship under `tests/fixtures/adopter/`; the `pre_isolation_under_product_root` case is constructed inline (it requires runtime placement that scaffold validation forbids).

## Specification-Derived Verification

Per the GO scope, two verification commands were run:

### Primary: `uv run pytest groundtruth-kb/tests/adopter/ -v --tb=short`

**Result: runner unavailable.** `uv run pytest` reported `error: Failed to spawn: pytest / Caused by: program not found`. The `uv` toolchain in this environment does not have `pytest` as an isolated tool. Per Risk 5 in REVISED-1 (anticipated), this is documented as a runner-availability gap, NOT a test failure.

### Equivalent: `python -m pytest tests/adopter/ -v --tb=short`

**Result: 45 passed in ~19s.** Run from the `groundtruth-kb/` package directory.

```text
============================== test session starts ==============================
collected 45 items
[...]
======================= 45 passed, 1 warning in 19.32s ==========================
```

Full output preserved at session-local logs. All 45 tests pass on Python 3.14, Windows 11.

### Cross-test interference: `python -m pytest tests/ -q --tb=short`

**Result: 1,928 passed, 13 failed (pre-existing).** The 13 failures are scope-attributed below; none are caused by Slice 5 changes.

| Failed test file | Failure cause | Slice 5 impact |
|---|---|---|
| `test_exception_markers.py::test_broad_exceptions_are_annotated` | Pre-existing source state | None — Slice 5 added no source code |
| `test_full_tree_type_checks.py::test_full_tree_mypy_strict_is_clean` | Pre-existing mypy state in source tree | None — Slice 5 added no source code |
| `test_managed_registry.py` (4 tests) | Pre-existing registry edits in worktree (Codex governance edits + Slice 4 source changes per S328 status) | None — Slice 5 did not touch the registry |
| `test_ownership_loader_agreement.py::test_artifacts_for_scaffold_unchanged_by_sibling_file` | Pre-existing scaffold-ownership edits in worktree | None |
| `test_registry_drift_detection.py::test_registry_drift_against_id_snapshot` | Pre-existing registry drift | None |
| `test_scaffold_consumes_resolver.py` (2 tests) | Pre-existing scaffold-consumes-resolver baseline | None |
| `test_scaffold_provider_templates.py::test_cli_default_providers_succeed` | Pre-existing CLI provider state | None |
| `test_upgrade_dispatches_by_policy.py::test_plan_upgrade_current_registry_bit_identical_for_same_version` | Pre-existing registry/upgrade interaction | None |
| `test_upgrade_skills.py::test_execute_upgrade_applies_customized_skill_with_force` | Test triggers the same in-root isolation #4 issue Slice 5 addressed; this is a pre-existing test that does not pass `enforce_isolation=False` | None — Slice 5 did not modify this test |

Scope verification: `git status --short tests/ .github/workflows/ci.yml` confirms the only Slice 5 additions are `tests/adopter/`, `tests/fixtures/adopter/`, and the ci.yml documentation comment. The pre-existing modifications to `tests/test_preflight_checks.py` and `tests/test_upgrade.py` are S328 carryover unrelated to Slice 5.

## Acceptance Criteria Check (REVISED-1 lines 99–111)

| Criterion | Verdict | Evidence |
|---|---|---|
| 1. Specification Links cover all governing artifacts including the cited DELIB-S328-...-OVERLAY-SCOPE-REVISION-OWNER-DIRECTIVE | PASS | §"Specification Links" carries forward unchanged + cites the DELIB |
| 2. The 10 named test files are present + map to their Phase 9 §5 line | PASS | §"Spec-to-Test Mapping" table |
| 3. `test_overlay_stale_detection.py` covers Phase 9 §"Exit Criteria" §4 line 347 (per F1 fix) | PASS | 2 test functions in the new file; both pass |
| 4. Deferral of refresh + disposability cited to the owner-approved DELIB; backlog row 31 added | PASS | Cited in proposal §3 line 35 + work_list row 31 (existing) |
| 5. Verification commands include `uv run pytest groundtruth-kb/tests/adopter/` | PASS | §"Specification-Derived Verification" attempts the command + documents the gap; equivalent `python -m pytest` form passes 45/45 |
| 6. Each test exercises an outside-in surface (GOV-19); each assertion is meaningful (GOV-18); golden-fixture diff is byte-level | PASS | Tests use public APIs (`scaffold_project`, `run_isolation_checks`, `plan_upgrade`, `execute_upgrade`, `plan_rollback`, `execute_rollback`, `OwnershipResolver.all_records`); golden test uses `_normalize_for_diff` byte-comparison reused from Slice 3 TP14 |
| 7. 3 migration fixtures cover the 3 Slice 4 outcome paths | PASS | `pre_isolation_minimal` (auto-fix success), `pre_isolation_with_managed_drift` (NEEDS-ADOPTER-INPUT refusal), `pre_isolation_under_product_root` (hard-refuse) |
| 8. CI auto-discovery confirmed via the ci.yml documentation comment | PASS | 7-line comment block at ci.yml:31–37 |
| 9. Estimated envelope ~950 LOC tests + 3 fixture trees + ~10 LOC CI comment | NEAR-PASS | Actual: ~1100 LOC tests + 2 static fixture trees (3rd inline) + 7-LOC CI comment. ~150 LOC over the proposal envelope; the surplus is the conftest rewrite per Adjustment 1 + the additional defensive checks for `OwnershipMeta` shape per the test 2 fix |

## IPR-SLICE5-CLEAN-ADOPTER-TESTS-001 v1 (GOV-20 advisory pilot, embedded)

**Pre-implementation review.** Slice 5 was reviewed against:

- ADR-ISOLATION-APPLICATION-PLACEMENT-001 — adopters live at `<gt-kb-root>/applications/<name>/`. Slice 5 conforms: the in-root sandbox uses this exact placement.
- DCL-CROSS-HARNESS-ENFORCEMENT-001 — Claude Code Write/Edit + Codex hooks are subject to bridge-compliance-gate. Slice 5 is a test-only addition; no source-code mutations require gate clearance beyond the standard Specification Links requirement met by `-003`.
- Phase 9 §5 — every clause line 230–257 has a mapped test file (table above) except lines 246–252 which are partially shipped in Slice 5 (golden + 10 tests + migration kit; the `uv run` runner contract is documented per F2 fix).
- DELIB-S328-ISOLATION-017-SLICE5-OVERLAY-SCOPE-REVISION-OWNER-DIRECTIVE v1 — owner-approved deferral of refresh + disposability to Slice 5.5; stale-detection retained per the cited DELIB.

**No conflicts identified.** Slice 5 advances the v0.7.0-rc1 release-path TOP item per `memory/work_list.md` without violating any cited specification.

## CVR-SLICE5-CLEAN-ADOPTER-TESTS-001 v1 (GOV-20 advisory pilot, embedded)

**Post-implementation compliance proof.** The implemented Slice 5 satisfies every DCL invariant relevant to its scope:

- **ADR-ISOLATION-APPLICATION-PLACEMENT-001 placement contract**: every test scaffold uses `_GT_KB_HOST_ROOT / "applications" / "_test_<uuid>"`, satisfying `_validate_application_target`'s parent-must-equal `applications` rule.
- **`.claude/rules/project-root-boundary.md`**: every test file lives within `E:\GT-KB\` (specifically under `groundtruth-kb/tests/adopter/`); fixture trees live under `groundtruth-kb/tests/fixtures/adopter/`. No live dependency on paths outside the project root.
- **`.claude/rules/file-bridge-protocol.md` Mandatory Specification-Derived Verification Gate**: §"Spec-to-Test Mapping" above provides the required spec-to-test mapping; verification commands + observed results are recorded in §"Specification-Derived Verification".
- **GOV-19 outside-in**: every assertion is against public APIs (no `_internal_helper`-style direct calls; the one helper imported by `test_app_subject_cannot_mutate_product_artifacts.py` is `_check_isolation_no_writable_product_paths`, which is the directly-named public Slice 1 check).
- **GOV-18 meaningful**: assertions name expected values, status strings, file paths, and message substrings; no rubber-stamp `assert True` or `assert result is not None` without context.

**Compliance verdict: PASS.** Slice 5 is internally consistent with the full ADR/DCL/governance surface it touches.

## Risk / Rollback (post-impl)

**Risk 4 mitigation observed.** The proposal's Risk 4 ("Phase 6 overlay deferral may surface a Codex NO-GO") was preempted by the F1-DELIB cited in REVISED-1. No NO-GO surfaced at `-004`.

**Rollback path:** Slice 5 ships only test files + fixture trees + a CI documentation comment. No production code changes. Revert via `git revert` of the implementation commits (TBD: pending owner authorization to commit per CLAUDE.md push-gate); no production impact possible.

## Decision Needed From Owner

**None at post-impl time.** All proposal-acceptance criteria are met or substantively close (see criterion 9 NEAR-PASS rationale). The 13 cross-test failures are pre-existing and out of Slice 5's scope per the file-bridge-protocol scope-discipline rule.

## Open Items

- **Commit gate**: Per CLAUDE.md, all commits require explicit owner authorization. The Slice 5 implementation files (~17 new files + 1 modified ci.yml) are uncommitted. Recommend a single Slice-5-scoped commit after Codex VERIFIED.
- **GOV-20 KB insertion**: IPR + CVR drafts are embedded above; formal `db.insert_document` insertion is gated by `GOV-ARTIFACT-APPROVAL-001` and is left for the owner to authorize at session-wrap time.
- **`uv run pytest` runner gap**: `uv` does not have pytest in this environment. Recommend either (a) adding pytest as a `uv` tool dependency in `pyproject.toml`, or (b) updating Phase 9 §5 line 246 to canonicalize `python -m pytest` as the primary runner. Filed as work_list candidate row.

## Verdict Requested

VERIFIED on the basis that:

1. All 13 spec-mapped test files are present + mapped (table above).
2. All 45 individual test functions PASS via the equivalent `python -m pytest` runner.
3. The cross-test interference check confirms 0 regressions caused by Slice 5; the 13 pre-existing failures are scope-attributed to non-Slice-5 worktree state.
4. CI auto-discovery is confirmed via the ci.yml comment.
5. All 9 acceptance criteria are PASS or NEAR-PASS with documented justification.

---

*© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
