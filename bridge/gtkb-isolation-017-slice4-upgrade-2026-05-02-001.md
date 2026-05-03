NEW

# Implementation Proposal — GTKB-ISOLATION-017 Slice 4

Proposed by: Prime Builder (Claude Code)
Date: 2026-05-02 (S328)
Subject: `gt project upgrade` — isolation gating + opt-in migration of auto-fixable in-place isolation defects + out-of-band rehearsal-recipe documentation. All three Slice-4-clustered Phase 9 owner decisions (1, 3, 7) pre-decided at S328 and archived as DELIB.

## Context

GTKB-ISOLATION-017 is the adopter-packaging program. Slices 1, 2, 2.5, and 3 are VERIFIED at S326–S327 (latest: `bridge/gtkb-isolation-017-slice3-init-defaults-2026-05-02-014.md`). This proposal opens Slice 4 per the scoping GO at `bridge/gtkb-isolation-017-scoping-004.md` lines 117–131, gating on the three S328 owner pre-decisions captured in `DELIB-S328-ISOLATION-017-SLICE4-DECISIONS-1-3-7-OWNER-DIRECTIVE` (groundtruth.db v1, 2026-05-02).

Per `memory/work_list.md` TOP directive (S327 release-path; commit `a3f592d7`), this is the next gating slice on the v0.7.0-rc1 release path. Feature freeze remains in effect for governance scope; ISOLATION-017 itself is the freeze-blocking critical path.

## Specification Links

The implementation is constrained by, and shall not depart from, the following specifications, ADRs, DCLs, governance rules, and proposal carry-forwards:

1. **Phase 9 plan §2 — `gt project upgrade`** at `independent-progress-assessments/CODEX-INSIGHT-DROPBOX/GTKB-ISOLATION-009-PHASE9-ADOPTER-PACKAGING-AND-VALIDATION-PLAN-2026-04-23.md` lines 144–197 (the canonical upgrade-deliverable enumeration). Probed 2026-05-02; line range stable since the 2026-04-26 ADR supersession edit.
2. **ADR-ISOLATION-APPLICATION-PLACEMENT-001** — adopter applications live at `<gt-kb-root>/applications/<name>/`. Slice 4 enforces this contract at upgrade time as a hard refuse for adopter-root-placement violations (cannot be auto-fixed).
3. **`.claude/rules/project-root-boundary.md`** — "All GT-KB application files MUST be within `E:\GT-KB\applications\`." Slice 4's adopter-root-placement refusal is the mechanical enforcement at upgrade time.
4. **`.claude/rules/file-bridge-protocol.md`** — Mandatory Specification Linkage Gate + Mandatory Specification-Derived Verification Gate; this proposal complies with both.
5. **`.claude/rules/codex-review-gate.md`** — pre-implementation Codex review required before any code change.
6. **Scoping carry-forward** at `bridge/gtkb-isolation-017-scoping-003.md` lines 117–131 (Slice 4 acceptance criteria) and `bridge/gtkb-isolation-017-scoping-004.md` (Codex GO; Slice 4 has no carry-forward of its own — Slice 8 owns the post-Phase-9 acceptance carry-forward).
7. **GOV-09** (Owner Input Classification) — owner has classified Phase 9 §2 obligations as specification language; Slice 4 implements without re-litigating scope.
8. **GOV-19** (Outside-in testing) — tests exercise `plan_upgrade`, `execute_upgrade`, and the new pre-flight isolation gate via the `gt project upgrade` CLI surface and the library functions consumed by it.
9. **GOV-20** (Architecture decisions) — Slice 4 ships an IPR + CVR pair to record (a) how the upgrade flow honors ADR-ISOLATION-APPLICATION-PLACEMENT-001 + the three S328 owner decisions and (b) post-impl proof that the gating + migration paths each test spec-derived.
10. **Prior Slice GOs (carry-forward only):**
    - `bridge/gtkb-isolation-017-slice1-doctor-checks-012.md` VERIFIED — provides `run_isolation_checks(target, profile, *, product_root)` at `groundtruth-kb/src/groundtruth_kb/project/doctor_isolation.py:552`. Probed 2026-05-02; all 9 `_check_isolation_*` functions exist and the orchestrator returns them in preflight order. Slice 4 consumes this surface unchanged.
    - `bridge/gtkb-isolation-017-slice2-registry-isolation-008.md` VERIFIED — registry now carries `owner` / `upgrade_policy` fields; the `upgrade_policy` filter (`groundtruth-kb/src/groundtruth_kb/project/upgrade.py:44` `_NO_UPGRADE_ACTION_POLICIES`) already preserves adopter-owned files; Slice 4 reuses the filter without modification.
    - `bridge/gtkb-isolation-017-slice3-init-defaults-2026-05-02-014.md` VERIFIED — `gt project init` now scaffolds Phase 4 service-endpoint template + adopter README quickstart block; Slice 4 documents the rehearsal recipe in upgrade output that points adopters at the same README block.
11. **Prior Deliberations:**
    - `DELIB-S328-ISOLATION-017-SLICE4-DECISIONS-1-3-7-OWNER-DIRECTIVE` v1 (2026-05-02) — owner pre-decisions for this Slice 4 (mandatory_at_upgrade / one_shot_migration_at_upgrade / out_of_band_recipe_only). Each test in §"Test Plan" derives from one of these decisions or a prior carry-forward.
    - `DELIB-S324-PROJECT-ROOT-BOUNDARY-SANDBOX-EXCEPTION-CHOICE` — rehearsal output may live outside `E:\GT-KB`; Slice 4's recipe documentation references this sandbox exception when documenting the out-of-band rehearsal recipe.
    - `python -m groundtruth_kb.cli deliberations search --query "gt project upgrade isolation migration" --limit 5` (probe pending — see §"Open Items" if rows exist).

## Scope

### In-scope

Files modified:
- `groundtruth-kb/src/groundtruth_kb/project/upgrade.py` — add `IsolationLocationFailureError` + `IsolationMigrationRequiredError` + `IsolationNonAutoFixableError` exception classes; add `_run_isolation_preflight(target, profile)` helper that wraps `run_isolation_checks` and partitions the 9 checks into (a) hard-refuse, (b) auto-fixable, (c) needs-adopter-input categories; extend `plan_upgrade()` (currently lines 637–701) to surface the partition outcome as `warning`/`informational` UpgradeAction rows; extend `execute_upgrade()` (currently lines 704–806) to (i) re-validate the partition under `--accept-migration` and refuse on hard-refuse and needs-adopter-input categories; (ii) emit `UpgradeAction(action="update", ...)` rows for the auto-fixable subset (TOML field rewrites + hook-path rewrites + work_list scrub for product entries + release-readiness banner rewrite); (iii) extend the rollback receipt with an `isolation_migration` block recording which checks were auto-fixed and which were left for adopter input.
- `groundtruth-kb/src/groundtruth_kb/cli.py` — add `--accept-migration` flag to `project_upgrade` (currently lines 902–993); render the upgrade-output rehearsal recipe block when isolation checks fail (per decision 7 = `out_of_band_recipe_only`); add `IsolationLocationFailureError`/`IsolationMigrationRequiredError`/`IsolationNonAutoFixableError` exception handlers (exit code 5 = isolation refusal; new in this slice).
- `groundtruth-kb/src/groundtruth_kb/project/preflight.py` — add `_check_isolation_state(target, profile, product_root)` returning the partition's surfaceable `warning`/`informational` UpgradeAction rows for `plan_upgrade()` consumption (mirrors the existing `_check_bridge_inflight` / `_check_scaffold_coverage` pattern). Probed 2026-05-02 — file exists, 490-test surface in `tests/test_preflight_checks.py`.
- `groundtruth-kb/src/groundtruth_kb/templates/managed-artifacts.toml` — register the rehearsal-recipe template file (see "Files created" below) so Slice 2 AST gate stays green.
- `groundtruth-kb/src/groundtruth_kb/templates/project/upgrade-rehearsal-recipe.md` *(new)* — adopter-facing rehearsal recipe block surfaced by `gt project upgrade` when isolation checks fail. Cites `scripts/rehearse_isolation.py --execute` invocation, the sandbox path constraint per `DELIB-S324-PROJECT-ROOT-BOUNDARY-SANDBOX-EXCEPTION-CHOICE`, and the two-step adopter recipe (rehearse → review → upgrade --accept-migration).

Files created (new):
- `groundtruth-kb/tests/test_upgrade_isolation.py` — Slice 4 spec-derived tests (see §"Test Plan" for the spec-to-test mapping).

Documents (per GOV-20):
- `IPR-SLICE4-UPGRADE-ISOLATION-001` — pre-implementation review citing this proposal, ADR-ISOLATION-APPLICATION-PLACEMENT-001, the three S328 owner decisions, and the Phase 9 §2 obligations Slice 4 owns.
- `CVR-SLICE4-UPGRADE-ISOLATION-001` — post-implementation proof that `gt project upgrade --apply` (a) refuses pre-isolation adopters without `--accept-migration`, (b) refuses adopter-root-placement violations even with `--accept-migration`, (c) refuses needs-adopter-input checks even with `--accept-migration`, (d) successfully migrates auto-fixable checks under `--accept-migration` via the existing payload-branch + rollback-receipt flow, (e) does not invoke the rehearsal driver from upgrade (decision 7 invariant), (f) records the isolation-migration block in the rollback receipt.

### Out-of-scope (deferred to other slices or work items)

- Clean-adopter test suite under `groundtruth-kb/tests/adopter/` (Slice 5).
- Documentation chapter in `groundtruth-kb/docs/` (Slice 6) — Slice 4 ships only the in-CLI rehearsal recipe block surfaced when isolation checks fail, not the standalone docs chapter.
- Examples (Slice 7) and release ops (Slice 8).
- Phase 6 overlay refresh / stale / disposability tests (Slice 5).
- Auto-fixers for the 5 needs-adopter-input checks (#1 adopter-root-placement, #4 no-writable-product-paths, #7 work-list-no-product-entries, #9 chroma-regeneratable, plus any future check that requires adopter judgment). These remain refuse-with-guidance for Slice 4. A future enhancement bridge may add interactive auto-fix paths.
- Multi-adopter coordination, deprecation-window code paths, version-pin enforcement (per decisions 1+3 = mandatory + one-shot, no deprecation window code-path is needed).
- Invocation of `scripts/rehearse_isolation.py` from upgrade (per decision 7 = out-of-band recipe only).

## Implementation Plan

1. **Add exception classes to `upgrade.py`** alongside `MalformedSettingsError` (lines 431–448), `NotAGitRepositoryError` (lines 468–482), `DirtyWorkingTreeError` (lines 485–499), `MergeFailedError` (lines 502–514):
   - `IsolationLocationFailureError` — adopter root is under product root (check #1 fail). Cannot be fixed by upgrade. Adopter must relocate filesystem.
   - `IsolationMigrationRequiredError` — one or more isolation checks fail AND `--accept-migration` not present. Refuses with rehearsal-recipe block + per-check guidance.
   - `IsolationNonAutoFixableError` — one or more checks in the needs-adopter-input set fail AND `--accept-migration` is present. Refuses with per-check guidance pointing at the offending file/configuration.

2. **Add `_run_isolation_preflight(target, profile, product_root)`** to `upgrade.py`:
   - Calls `groundtruth_kb.project.doctor_isolation.run_isolation_checks(target, profile, product_root=product_root)`.
   - Partitions the 9-check result into 3 sets via name → category mapping:
     - **Hard-refuse**: `{"isolation:adopter-root-placement"}` (cannot be fixed by upgrade).
     - **Auto-fixable**: `{"isolation:service-endpoint", "isolation:durable-work-subject-application", "isolation:hooks-point-to-wrappers", "isolation:workstream-focus-hook-absent", "isolation:release-readiness-app-subject-header"}` (5 checks).
     - **Needs-adopter-input**: `{"isolation:no-writable-product-paths", "isolation:work-list-no-product-entries", "isolation:chroma-regeneratable"}` (3 checks; require adopter judgment on what to do with offending content).
   - Returns a typed dataclass (`IsolationPreflightResult`) with three lists of `ToolCheck` instances filtered to `status in {"fail", "warning"}` per category.

3. **Extend `preflight.py`** with `_check_isolation_state(target, profile, product_root)` that wraps `_run_isolation_preflight` and returns a list of `UpgradeAction`s:
   - One `informational` row when all isolation checks pass: `"Isolation: all 9 checks pass."`.
   - One `warning` row per failing check (use the check's `name` and `message` directly), prefixed `[ISOLATION]`.
   - This matches the existing `_check_bridge_inflight` / `_check_scaffold_coverage` shape; the CLI surfaces them via the `WARNING` / `INFORMATIONAL` formatter at `cli.py:949–950`.

4. **Extend `plan_upgrade(target, *, ignore_inflight_bridges)`** at line 637:
   - Resolve `product_root` once (use the same `Path(__file__).resolve().parents[3]` pattern as `doctor.py:1925`).
   - Call `actions.extend(_check_isolation_state(target, profile.name, product_root))` immediately after the existing `_check_bridge_inflight` and `_check_scaffold_coverage` calls (around line 682).
   - The new isolation rows are non-mutating per the existing `_NON_MUTATING_ACTION_KINDS` filter (line 91); they are visible to dry-run reporting but never reach `execute_upgrade()`.

5. **Extend `execute_upgrade(target, actions, *, force, accept_migration=False)`** at line 704 with a new keyword-only argument:
   - Add `accept_migration: bool = False` parameter (default preserves existing behavior).
   - Re-run `_run_isolation_preflight(target, profile, product_root)` early (after the malformed-settings halt at line 739, before `_require_git_repo` at line 743).
   - Branch:
     - If hard-refuse non-empty → `raise IsolationLocationFailureError(target, hard_refuse_checks)`.
     - If (auto-fixable non-empty OR needs-adopter-input non-empty) AND not `accept_migration` → `raise IsolationMigrationRequiredError(target, all_failing_checks)`.
     - If needs-adopter-input non-empty AND `accept_migration` → `raise IsolationNonAutoFixableError(target, needs_adopter_input_checks)`.
     - If auto-fixable non-empty AND `accept_migration` → continue; injected `UpgradeAction` rows for each auto-fixable check are added to the front of the action list before the existing payload-branch flow runs.
   - The injected migration actions reuse `action="update"` for groundtruth.toml field rewrites, `action="update"` for hook-path rewrites, etc. — same shape as existing actions; no new action types needed.
   - Receipt extension: after `merge_commit` is computed (line 783), add `"isolation_migration": {...}` to the receipt dict before `write_receipt` (line 797). The dict records which checks were auto-fixed (by name) and which were left for adopter input (with their messages).

6. **Add per-check auto-fixer helpers** alongside the existing `_apply_file_actions` family (around line 809):
   - `_fix_isolation_service_endpoint(target)` — rewrite `[service]` block in groundtruth.toml to use the scoped service URL form (the same pattern Slice 3 scaffolds).
   - `_fix_isolation_work_subject(target)` — rewrite `work_subject` field in groundtruth.toml to `"application"`.
   - `_fix_isolation_hook_paths(target)` — rewrite `.claude/settings.json` hook entries to use wrapper paths (consume the existing `_compute_target_event_list` pattern at line 245).
   - `_fix_isolation_remove_workstream_focus_hook(target)` — delete the defunct hook entry from `.claude/settings.json`.
   - `_fix_isolation_release_readiness_banner(target)` — rewrite the first non-blank line of `memory/release-readiness.md` to assert application subject (mirror the Slice 3 banner template).
   - Each helper returns a result string in the same shape as existing executors (`"FIXED <file> — <reason>"` or `"SKIPPED <file> — <reason>"`).

7. **Extend `cli.py:project_upgrade`** at line 902:
   - Add `--accept-migration` Click flag: `@click.option("--accept-migration", is_flag=True, default=False, help="Opt in to one-shot isolation migration of auto-fixable in-place defects.")`.
   - Thread `accept_migration` through to `execute_upgrade` (line 978).
   - Add exception handlers for the three new exception classes:
     - `IsolationLocationFailureError` → `SystemExit(5)` with the recipe block + manual-relocation guidance.
     - `IsolationMigrationRequiredError` → `SystemExit(5)` with the recipe block + per-check guidance + `--accept-migration` instruction.
     - `IsolationNonAutoFixableError` → `SystemExit(5)` with per-check guidance + manual-fix instructions.
   - Render the rehearsal-recipe block (template at `templates/project/upgrade-rehearsal-recipe.md`) into each isolation-refusal exception's user-visible message.

8. **Author the rehearsal-recipe template** at `templates/project/upgrade-rehearsal-recipe.md`:
   - Two-step recipe: (1) `python scripts/rehearse_isolation.py --execute --output-dir <sandbox-path>` (cite `DELIB-S324` sandbox exception), (2) inspect the rehearsal output, (3) re-run `gt project upgrade --apply --accept-migration` if the rehearsal preview is acceptable.
   - Per-check guidance pointers (one paragraph per check, naming the file/configuration the adopter must inspect for needs-adopter-input checks).

9. **Register the new template** in `templates/managed-artifacts.toml` so the Slice 2 AST gate stays green.

10. **Author IPR and CVR documents** per GOV-20 Phase 1 advisory pilot.

## Test Plan (spec-to-test mapping)

Tests live in `groundtruth-kb/tests/test_upgrade_isolation.py` unless noted. Each test is GOV-19-compliant (outside-in surface — `plan_upgrade`, `execute_upgrade`, `gt project upgrade` CLI) and GOV-18-compliant (meaningful — never rubber-stamp).

**T1 — adopter-root-placement hard refuse (decision 1: mandatory_at_upgrade; carries from Slice 1 check #1).**
Spec source: ADR-ISOLATION-APPLICATION-PLACEMENT-001 + Slice 1 doctor check `_check_isolation_adopter_root_not_under_product_root`.
Assertion: `execute_upgrade(target_under_product_root, [], accept_migration=True)` raises `IsolationLocationFailureError`. Exit code via CLI = 5.

**T2 — pre-isolation adopter refused without --accept-migration (decision 1: mandatory_at_upgrade).**
Spec source: `DELIB-S328-ISOLATION-017-SLICE4-DECISIONS-1-3-7-OWNER-DIRECTIVE` decision 1.
Assertion: `execute_upgrade(target_with_failing_checks, [], accept_migration=False)` raises `IsolationMigrationRequiredError`. CLI exit code = 5. CLI output contains rehearsal recipe block.

**T3 — auto-fixable migration succeeds with --accept-migration (decision 3: one_shot_migration_at_upgrade).**
Spec source: `DELIB-S328-ISOLATION-017-SLICE4-DECISIONS-1-3-7-OWNER-DIRECTIVE` decision 3.
Assertion: a fixture adopter with all 5 auto-fixable checks failing AND no needs-adopter-input checks failing AND no hard-refuse → `execute_upgrade(..., accept_migration=True)` returns successfully with `len(results) >= 5` "FIXED" rows. After execution, re-running `run_isolation_checks` shows all 5 previously-failing auto-fixable checks now pass.

**T4 — needs-adopter-input check refuses even with --accept-migration.**
Spec source: scoping bridge §"Acceptance" line 126 ("Upgrade preserves adopter-owned files; refuses silent overwrite") + decision 1 mandatory enforcement.
Assertion: a fixture adopter with check #4 (`isolation:no-writable-product-paths`) failing → `execute_upgrade(..., accept_migration=True)` raises `IsolationNonAutoFixableError`. CLI exit code = 5. CLI output names check #4 and points at the offending file.

**T5 — rehearsal driver NOT invoked from upgrade (decision 7: out_of_band_recipe_only).**
Spec source: `DELIB-S328-ISOLATION-017-SLICE4-DECISIONS-1-3-7-OWNER-DIRECTIVE` decision 7.
Assertion: monkeypatch `scripts.rehearse_isolation.main` to raise on call; `execute_upgrade(..., accept_migration=True)` on a fixture with auto-fixable failures runs to completion without invoking the rehearsal entry point. Negative-presence test: grep upgrade.py source for `rehearse_isolation` → 0 hits in the implementation surface (allowed: docstring/comment references).

**T6 — payload-branch + rollback-receipt flow preserved.**
Spec source: scoping `-003` line 127 ("Rollback restores pre-upgrade state via receipts") + `bridge/gtkb-rollback-receipts-014.md` carry-forward (probed: receipt machinery present at `upgrade.py:786–797`).
Assertion: on successful migration (T3 flow), the rollback receipt at `.claude/upgrade-receipts/active/{receipt_id}.json` contains the new `isolation_migration` block with the list of auto-fixed checks. Existing `gt project rollback` consumes the same receipt successfully.

**T7 — pre-flight surfacing in dry-run.**
Spec source: scoping `-003` line 122 ("Upgrade detects mixed-root state via doctor checks") + existing pre-flight pattern at `upgrade.py:678–683`.
Assertion: `gt project upgrade --dry-run` on a fixture adopter with isolation failures emits `[WARNING] [ISOLATION] ...` rows in the action list output. Dry-run does NOT raise (matches existing pre-flight pattern; mutating-action filter at `cli.py:971` already excludes `warning`/`informational`).

**T8 — auto-fixable migration is idempotent.**
Assertion: running `execute_upgrade(..., accept_migration=True)` twice in succession (with a clean tree between runs) produces "FIXED" results on the first pass and "SKIPPED — already at target" or no-op pre-flight clean on the second.

**T9 — no behavior change when isolation checks all pass.**
Spec source: implicit invariant; the existing test suite (`tests/test_upgrade.py`) must continue to pass without modification.
Assertion: `tests/test_upgrade.py` test count unchanged before and after Slice 4. (Verified empirically; not a separate test file assertion.)

**T10 — IPR + CVR present.**
Spec source: GOV-20.
Assertion: KB query `db.list_documents(category='implementation_proposal')` returns `IPR-SLICE4-UPGRADE-ISOLATION-001`; `db.list_documents(category='constraint_verification')` returns `CVR-SLICE4-UPGRADE-ISOLATION-001`.

Each test runs under the existing `pytest` lane: `python -m pytest groundtruth-kb/tests/test_upgrade_isolation.py -v`. Verification command for the post-impl: `python -m pytest groundtruth-kb/tests/test_upgrade.py groundtruth-kb/tests/test_upgrade_isolation.py groundtruth-kb/tests/test_doctor_isolation.py groundtruth-kb/tests/test_preflight_checks.py -q --tb=short`.

## Acceptance Criteria

This NEW is GO-able when Codex confirms:

1. Specification Links cover all governing artifacts including the 3 S328 decisions DELIB.
2. The hard-refuse / auto-fixable / needs-adopter-input partition is correct and exhaustive over the 9 Slice 1 isolation checks.
3. The implementation surface (`upgrade.py` + `cli.py` + `preflight.py` + new template + new test file) preserves the existing payload-branch + rollback-receipt contract.
4. Decision 7 invariant ("upgrade does NOT invoke the rehearsal driver") is testable via T5.
5. Per-check auto-fixer helpers honor the existing `upgrade_policy` filter (no override of `preserve` / `transient` / `adopter-opt-in` policies).
6. Estimated envelope (~150–250 LOC source + ~250–400 LOC tests) stays within the 450/550 ceiling from scoping bridge §"Slice 4 — Estimated envelope".
7. Risks and mitigations are credible.

## Risk / Rollback

**Risk 1 — partition correctness (medium):** The hard-refuse / auto-fixable / needs-adopter-input partition is a judgment call over 9 checks; mis-categorizing a check (e.g., treating #4 as auto-fixable when it requires adopter judgment about the offending content) would cause silent data loss in adopter trees. **Mitigation:** T4 directly tests one needs-adopter-input check refuses even with `--accept-migration`; the partition is documented in source comments + the IPR. Codex review of the partition is the gating step.

**Risk 2 — auto-fixer destructive behavior (medium):** The 5 auto-fixers each mutate adopter-owned configuration (groundtruth.toml, .claude/settings.json, memory/release-readiness.md). A bug in any auto-fixer could destroy adopter customizations not covered by the existing `upgrade_policy` filter. **Mitigation:** All mutations run inside the existing payload-branch + rollback-receipt flow; `gt project rollback` reverses any failed migration via `git revert -m 1 <merge_commit>`. T6 specifically asserts receipt round-trip.

**Risk 3 — pre-flight performance (low):** Adding `_check_isolation_state` to `plan_upgrade` adds 9 doctor checks to every dry-run. **Mitigation:** Slice 1 doctor checks are filesystem-bound (TOML parse + path tests); empirical cost is ~50–200ms per `plan_upgrade` call. Acceptable.

**Risk 4 — exit code 5 collision (low):** Exit code 5 is currently unused in `cli.py:project_upgrade` (probed: 1, 2, 3, 4 are taken). **Mitigation:** None needed; documented in CVR.

**Rollback path:**
- If Slice 4 implementation introduces a critical bug after merge: the bridge thread itself is reversible via revert of the merge commit on `develop`.
- If a specific adopter migration goes wrong: `gt project rollback` consumes the rollback receipt and reverts the payload via `git revert -m 1 <merge_commit>`.

## Decision Needed From Owner

**None at NEW time.** All 7 Phase 9 decisions in the scoping Decision Map are either (a) Slice 4-clustered and pre-decided at S328 (decisions 1, 3, 7 — DELIB-S328-ISOLATION-017-SLICE4-DECISIONS-1-3-7-OWNER-DIRECTIVE) or (b) deferred to other slices (2/4 → Slice 8, 5 → Slice 8 closeout, 6 → Slice 7).

## Open Items

- None at NEW time. The `python -m groundtruth_kb.cli deliberations search --query "gt project upgrade isolation migration" --limit 5` probe will run as part of Codex review's Prior Deliberations check; if it returns rows, this proposal will be revised to cite them.

---

*© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
