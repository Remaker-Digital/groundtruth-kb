NEW
author_identity: prime-builder/claude
author_harness_id: B
author_session_context_id: 96b4ab64-e440-47b7-8c81-cd55bc7a5c1e
author_model: claude-opus-4-8
author_model_version: 4.8
author_model_configuration: default

# Defect-Fix Proposal - harness-roles test path canonicalization to harness-registry.json

bridge_kind: prime_proposal
Document: gtkb-harness-roles-test-path-canonicalization
Version: 001
Date: 2026-06-21 UTC

Project Authorization: PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING
Project: PROJECT-GTKB-RELIABILITY-FIXES
Work Item: WI-4398

target_paths: ["platform_tests/hooks/test_workstream_focus.py"]

Defect-fix proposal focused on reproducing, correcting, and verifying a fault.

## Claim

Four tests in `platform_tests/hooks/test_workstream_focus.py` set up the harness role map by writing a legacy `harness-state` mirror file (`tmp_path / "role-assignments.json"`) and pointing `GTKB_ROLE_ASSIGNMENTS_PATH` at it, but the production code they exercise — `scripts/workstream_focus.py::detect_counterpart_state` / `render_active_work_subject` — resolves role state through `scripts/harness_roles.py::load_role_assignments`, which was migrated (WI-3342 IP-3) to read **only** the registry projection `harness-state/harness-registry.json` and to ignore both the `assignment_path` parameter and the `GTKB_ROLE_ASSIGNMENTS_PATH` env var. The tests' role-map setup is therefore dead: production reads an unseeded `harness-registry.json`, the role map is empty/absent, and the affected counterpart/work-subject tests fail. The fix updates those four tests to seed the canonical `harness-registry.json` projection through the same helper the green sibling tests already use (`_write_registry_projection`), matching how production reads role state.

## Defect / Reproduction

Production read path (post-WI-3342-IP-3):
- `scripts/workstream_focus.py:894` calls `load_role_assignments(root, assignment_path)`.
- `scripts/harness_roles.py:251-282` `load_role_assignments` discards `assignment_path` (line 263 `_ = assignment_path`) and loads exclusively from `load_harness_projection(project_root)` over `harness-state/harness-registry.json`.
- `GTKB_ROLE_ASSIGNMENTS_PATH` is consulted only by the path-resolution helper `role_assignments_path` (`harness_roles.py:202-208`), which no longer feeds `load_role_assignments`. So setting that env var has no effect on `workstream_focus.py`'s role reads.

Failing tests (each seeds `tmp_path / "role-assignments.json"` + `GTKB_ROLE_ASSIGNMENTS_PATH`, neither of which production honors):
- `test_detect_counterpart_state_subject_mismatch_warns` (`test_workstream_focus.py:1278`)
- `test_detect_counterpart_state_subject_mismatch_symmetric_from_codex_side` (`:1314`)
- `test_detect_counterpart_state_subject_match_no_warning` (`:1371`)
- `test_render_active_work_subject_combines_focus_overlay_and_counterpart` (`:1415`)

The first three call `module.detect_counterpart_state()` with no project_root, so `load_role_assignments` resolves `harness-registry.json` under the real `PROJECT_ROOT` (or an unseeded location) rather than the seeded legacy mirror, and `per_harness_role_sets` is not populated from the intended fixture; the assertions on `same_role_slot` / `subject_mismatch` / collision warnings do not hold. The fourth seeds only the legacy mirror, so the role-slot rendering path likewise has no registry projection to read.

Reproduction (logical): run the four named tests; they fail because the fixture writes the retired mirror format and relies on the retired env override, while the code under test reads the registry projection. The contrast is already demonstrated by the GREEN sibling tests in the same file (`test_detect_counterpart_state_same_role_warns` `:1246`, `..._different_role_warns` `:1263`, `..._no_counterpart_files_no_warning` `:1200`, `..._missing_counterpart_no_crash` `:1402`) which seed `harness-registry.json` via `_write_registry_projection(tmp_path, {...})` and pass `tmp_path` as the project root.

Note on the WI's "approximately 7 failing tests": the WI enumerates the `counterpart_state`, `harness_state_records_for_*`, and `prompt_hook_*` families. The `harness_state_records_for_project` test (`:1446`) and the role-toggle `prompt_hook_*` tests (`:749`, `:786`, `:811`) already assert/read `harness-registry.json` (via `_harness_state_records_for_project`, `_projection_role`, `_seed_registry`) and are GREEN; they are listed in the WI as the canonical pattern the failing tests must converge to, not as additional broken tests. The concrete, currently-failing defect is the four legacy-mirror counterpart/work-subject tests above. This proposal fixes exactly those four and introduces no other behavior change.

## In-Root Placement Evidence

All target paths are inside `E:\GT-KB`: `platform_tests/hooks/test_workstream_focus.py`. The change is test-only; no production source, config, hook, or generated artifact is modified.

## Specification Links

- `GOV-14` - UI element test maintenance — add/retire tests when the surface they assert changes. The harness role-record surface migrated from the `role-assignments.json` mirror to the `harness-registry.json` projection; the affected tests must be updated to assert the new surface, which is exactly this maintenance obligation.
- `GOV-10` - Test artifacts must exercise exposed production interfaces. The fixed tests will drive the real production read path (`load_role_assignments` → `harness-registry.json` projection) instead of a retired interface (`GTKB_ROLE_ASSIGNMENTS_PATH` / legacy mirror) that production no longer consults.
- `GOV-19` - Outside-in testing principle. Seeding the canonical projection that production reads keeps the test boundary at the real interface; the fix removes inside-knowledge coupling to a retired env override.
- `GOV-HARNESS-STATE-SOT-CONSOLIDATION-001` - Harness State Source-of-Truth Consolidation establishes `harness-registry.json` (DB-projected) as the canonical harness/role SoT; the test fix aligns the fixtures with that consolidated SoT.
- `RETIRE-SPEC-HARNESS-STATE-ROLE-ASSIGNMENTS-001` - Retire the `harness-state/role-assignments.json` legacy mirror. This defect is residual test coupling to that retired mirror; the fix removes the mirror-format fixtures from the affected tests (consistent with retirement) without asserting global grep-absence (out of scope here).
- `GOV-SOURCE-OF-TRUTH-FRESHNESS-001` - State claims derive from fresh canonical reads. The tests must derive role state from the canonical registry projection, not a fixture-only retired mirror; the fix makes the fixtures read-consistent with the canonical SoT.
- `GOV-RELIABILITY-FAST-LANE-001` - Reliability fast-lane for small defect fixes. This is a single-concern, test-only defect fix (no new public surface, no new/revised spec), eligible for the fast lane under the standing reliability PAUTH.
- `GOV-STANDING-BACKLOG-001` - WI-4398 is a standing-backlog work item (origin=defect, P2) under PROJECT-GTKB-RELIABILITY-FIXES.
- `GOV-FILE-BRIDGE-AUTHORITY-001` - This proposal proceeds through the bridge protocol (NEW → GO → implement → report → VERIFIED); the bridge `VERIFIED` is the authoritative terminal signal for the fix.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` - The fix preserves the durable test artifact's integrity by keeping its fixtures consistent with the canonical harness-state artifact (the registry projection).
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` - Test fixtures remain artifact-backed (seeded `harness-registry.json`) rather than coupled to a retired env-override surface that no longer reflects production state.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - Touching the test that asserts a migrated surface triggers updating that test to the current canonical surface; this fix is that lifecycle update.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - This proposal cites all governing specs (mandatory linkage).
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - The verification plan derives its checks from the cited specs (mandatory).
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - The proposal carries Project Authorization / Project / Work Item linkage lines (mandatory).
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - The change is confined to GT-KB platform tests (`platform_tests/...`); no application/adopter surface is touched and no application-placement boundary is crossed.
- `SPEC-AUQ-POLICY-ENGINE-001` - Not directly exercised by this test-only fix; cited for completeness because the scaffold seeded it. No AUQ-policy behavior changes; the only owner-decision dependency is the standing PAUTH authorization recorded under § Owner Decisions / Input.
- `ADR-CODEX-HOOK-PARITY-FALLBACK-001` - Not directly exercised by this fix; cited for completeness because the scaffold seeded it. The change touches no `.codex` hooks and no Codex/Claude parity surface; harness-parity behavior is unaffected.

## Prior Deliberations

- `DELIB-20264139` - Loyal Opposition Review: gtkb-harness-registry-reader-migration-001 — the migration that repointed role readers to the `harness-registry.json` projection; this defect is residual test coupling left after that migration.
- `DELIB-20261788` - Bridge thread: gtkb-harness-state-sot-consolidation-phase-1 (GO) — establishes `harness-registry.json` as the consolidated harness-state SoT that the fixed tests must seed.
- `DELIB-20261849` - Bridge thread: gtkb-retire-role-assignments-mirror-slice-1-seed-repoint — the role-assignments mirror retirement program of which this test cleanup is a consistency follow-on.
- `DELIB-20263486` - Loyal Opposition Test Suite Audit — Regression & Drift Analysis — prior LO audit of regression/drift in the test suite, the context in which mirror/projection test inconsistencies surface.
- `DELIB-20265457` - Owner decision authorizing the PROJECT-GTKB-RELIABILITY-FIXES proposal batch (WI-4398 is in scope).

## Owner Decisions / Input

- `PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING` (standing authorization established by `DELIB-S351-RELIABILITY-FAST-LANE-DIRECTION`) - WI-4398 is origin=defect, single-concern, test-only, introduces no new public surface and no new/revised spec, and is bounded to one test file (well under the fast-lane size guide), so it is covered by the reliability fast-lane standing authorization through active PROJECT-GTKB-RELIABILITY-FIXES membership.
- `DELIB-S351-RELIABILITY-FAST-LANE-DIRECTION` - the standing fast-lane direction that authorizes bounded reliability defect fixes to proceed under the standing PAUTH without a fresh per-item owner approval.
- `DELIB-20265457` - owner AUQ (2026-06-21) directing authoring of NEW proposals for the open PROJECT-GTKB-RELIABILITY-FIXES work items batch; WI-4398 (P2, defect) is in that batch.

## Requirement Sufficiency

Existing requirements sufficient. `GOV-14` (test maintenance when the asserted surface changes) and `GOV-HARNESS-STATE-SOT-CONSOLIDATION-001` / `RETIRE-SPEC-HARNESS-STATE-ROLE-ASSIGNMENTS-001` (canonical harness-state SoT = `harness-registry.json`) already establish that these tests must assert the registry projection. This fix conforms the affected fixtures to that existing contract. No new or revised requirement/specification is introduced; this is the defect-removal (not behavior-change) path.

## Proposed Scope

Test-only change in `platform_tests/hooks/test_workstream_focus.py`, scoped to the four currently-failing tests:

1. `test_detect_counterpart_state_subject_mismatch_warns` (`:1278`): replace the `_write_role_map(tmp_path / "role-assignments.json", ...)` + `monkeypatch.setenv("GTKB_ROLE_ASSIGNMENTS_PATH", ...)` setup with `_write_registry_projection(tmp_path, {"A": ("codex", "loyal-opposition"), "B": ("claude", "prime-builder")})`, and pass `tmp_path` as the project root to `detect_counterpart_state(tmp_path)` (matching the green `..._same_role_warns` / `..._different_role_warns` siblings). Keep the per-harness lifecycle-guard seeding and `HARNESS_LIFECYCLE_GUARDS` monkeypatch that drive the subject-mismatch assertion; only the role-map source changes.
2. `test_detect_counterpart_state_subject_mismatch_symmetric_from_codex_side` (`:1314`): same substitution (seed `harness-registry.json` via `_write_registry_projection` with the codex/claude roles), pass `tmp_path` to `detect_counterpart_state(tmp_path)`, retain the codex/claude guard files and `HARNESS_LIFECYCLE_GUARDS` monkeypatch and the symmetric-asymmetry assertion.
3. `test_detect_counterpart_state_subject_match_no_warning` (`:1371`): same substitution; seed the projection, pass `tmp_path`, keep the matching-subject guard seeding and the `subject_mismatch is False` assertion.
4. `test_render_active_work_subject_combines_focus_overlay_and_counterpart` (`:1415`): replace the legacy `_write_role_map(...role-assignments.json...)` + env override with `_write_registry_projection(tmp_path, {"B": ("claude", "prime-builder")})`; call `render_active_work_subject(tmp_path, overlay_status=...)` so the role read resolves the seeded projection under the isolated root.

Constraints / non-goals:
- No production source change. `scripts/workstream_focus.py`, `scripts/harness_roles.py`, and `scripts/session_self_initialization.py` are NOT modified by this fix; the WI's "papering-over" refactor (re-adding `GTKB_ROLE_ASSIGNMENTS_PATH` / `assignment_path` handling to `harness_roles.py`) is explicitly rejected — it was already reverted by the 2026-06-07 reconciliation and would re-introduce a retired surface.
- `platform_tests/scripts/test_session_self_initialization.py` is OUT OF SCOPE. Its legacy `role-assignments.json` / `GTKB_ROLE_ASSIGNMENTS_PATH` usages still pass because `scripts/session_self_initialization.py` continues to honor that env override (`session_self_initialization.py:287-288, 310`); those tests are not part of this defect and are left unchanged to avoid regressing green tests.
- The `xfail`-marked counterpart `harness_type` regression block (`test_workstream_focus.py:1213-1243`) describes a separate, out-of-scope production defect and is not touched.
- No `_write_role_map` removal: the helper is left in place (still used by tests outside this WI's failing set); only the four failing tests stop calling it with the legacy path.

## Specification-Derived Verification Plan

| Spec clause | Derived test | Assertion |
|---|---|---|
| `GOV-14` / `GOV-HARNESS-STATE-SOT-CONSOLIDATION-001` (tests assert the migrated canonical surface) | `test_detect_counterpart_state_subject_mismatch_warns` (fixed) | With `harness-registry.json` seeded via `_write_registry_projection` and `tmp_path` passed as project root, `detect_counterpart_state(tmp_path)` returns `subject_mismatch is True` and emits the gtkb/application divergence warning. |
| `GOV-14` / `GOV-SOURCE-OF-TRUTH-FRESHNESS-001` (role state from canonical projection) | `test_detect_counterpart_state_subject_mismatch_symmetric_from_codex_side` (fixed) | Codex-side seed of the projection yields `subject_mismatch is True` against Claude's guard (symmetric detection holds with the registry-projection source). |
| `GOV-10` (exercise production read path, not retired override) | `test_detect_counterpart_state_subject_match_no_warning` (fixed) | With matching subjects and the projection seeded, `detect_counterpart_state(tmp_path)` returns `subject_mismatch is False` and emits no work-subject warning. |
| `RETIRE-SPEC-HARNESS-STATE-ROLE-ASSIGNMENTS-001` (no reliance on retired mirror/override) | `test_render_active_work_subject_combines_focus_overlay_and_counterpart` (fixed) | With the projection seeded and no `GTKB_ROLE_ASSIGNMENTS_PATH`, `render_active_work_subject(tmp_path, ...)` renders the "Work-subject bridge role slot:" line and the no-overlay note. |
| `GOV-19` (no regression to green sibling/role-toggle tests) | full-module run of `test_workstream_focus.py` | The previously-green tests (`..._same_role_warns`, `..._different_role_warns`, `..._no_counterpart_files_no_warning`, `..._missing_counterpart_no_crash`, `harness_state_records_for_project`, `prompt_hook_*`) remain PASS. |

Execution commands:
- `python -m pytest platform_tests/hooks/test_workstream_focus.py -q --tb=short`
- `python -m ruff check platform_tests/hooks/test_workstream_focus.py`
- `python -m ruff format --check platform_tests/hooks/test_workstream_focus.py`

## Acceptance Criteria

1. The four named tests pass by seeding `harness-state/harness-registry.json` (via `_write_registry_projection`) and reading through the production `load_role_assignments` → projection path; no test sets `GTKB_ROLE_ASSIGNMENTS_PATH` or writes `role-assignments.json` after the fix.
2. The full `test_workstream_focus.py` module passes (no regression to previously-green tests), confirming the change is isolated to the four failing tests.
3. No production source file is modified (target_paths is the single test file).
4. `ruff check` and `ruff format --check` are clean on the changed file.

## Risks / Rollback

- Risk: over-broadening to currently-green session-self-init tests. Mitigation: scope is fixed to the four failing tests in one file; `test_session_self_initialization.py` and production sources are explicitly excluded.
- Risk: a fixed test still depends on per-harness lifecycle-guard seeding that was previously paired with the legacy role map. Mitigation: the guard seeding and `HARNESS_LIFECYCLE_GUARDS` monkeypatch are retained verbatim; only the role-map *source* changes from legacy mirror to registry projection.
- Risk: the registry-projection seed under `tmp_path` is read against the wrong root if `detect_counterpart_state()` is still called without an argument. Mitigation: the fixed tests pass `tmp_path` explicitly (mirroring the green siblings), so the projection read resolves under the isolated root.
- Rollback: revert the four test edits; the change is test-only, additive in its use of an existing helper, fully reversible with no migration and no production impact.

## Files Expected To Change

- `platform_tests/hooks/test_workstream_focus.py`

## Recommended Commit Type

`fix`
