REVISED

# Scaffold Upgrade Tier A — Pure ADDs + APPEND-GITIGNORE — REVISED-4

bridge_kind: implementation_proposal
Document: gtkb-scaffold-upgrade-tier-a
Version: 009 (REVISED-4 post NO-GO at `-008`)
Author: Prime Builder (Claude, harness B)
Date: 2026-05-11 UTC
Supersedes: `bridge/gtkb-scaffold-upgrade-tier-a-007.md` (REVISED-3; NO-GO at `-008`).

## Revision Notes (REVISED-4)

This revision addresses `FINDING-P1-001` from `bridge/gtkb-scaffold-upgrade-tier-a-008.md`. Two stale claims from `-007` are corrected:

1. **`enforce_isolation` reclassified from "new parameter" to "existing prerequisite."** The parameter already exists in current `groundtruth-kb/src/groundtruth_kb/project/upgrade.py:1199` and is exercised by 14 call sites in `groundtruth-kb/tests/test_upgrade.py`. REVISED-4 cites it as a prerequisite, does not propose to add it, and does not propose new tests for it. The `update_manifest=False` design from `-007` is preserved as the only `execute_upgrade()` signature change in this thread.

2. **Parameter tests relocated to the established test layout.** REVISED-3 placed new tests under `groundtruth-kb/src/groundtruth_kb/project/tests/`, a directory that does not exist in the current checkout. REVISED-4 adds the single new `update_manifest` test to `groundtruth-kb/tests/test_upgrade.py`, where every existing `execute_upgrade()` test lives. The applier-script test moves from the stale `tests/scripts/` path to the established `platform_tests/scripts/` location (verified by repo glob: `platform_tests/scripts/` contains 20+ existing script tests; `tests/` does not exist at repo root).

The `update_manifest=False` design from `-007` is unchanged. The applier script `scripts/scaffold_upgrade_tier_a_apply.py` continues to call:

```
execute_upgrade(
    target=target,
    actions=kept_actions,
    force=False,
    enforce_isolation=False,
    update_manifest=False,
    accept_migration=False,
)
```

Default behavior is preserved for all existing callers: `update_manifest: bool = True` default matches the current unconditional `manifest.scaffold_version = __version__` write at `upgrade.py:1431-1435`. Aligns with `DELIB-S312-DETERMINISTIC-SERVICES-PRINCIPLE` (small, explicit, default-preserving parameter addition that pulls a side-effect out of the mainline path).

## Existing-State Prerequisites (NOT scope of this thread)

- **`enforce_isolation: bool = True` parameter:** Exists at `groundtruth-kb/src/groundtruth_kb/project/upgrade.py:1199`. Consumed at lines 1253-1266 (isolation preflight gating). Exercised in `groundtruth-kb/tests/test_upgrade.py` at lines 174, 190, 200, 225, 243, 346, 418, 444, 450, 593, 641, 689, 711, 800 (every `execute_upgrade(...)` test call uses `enforce_isolation=False`). REVISED-4 does NOT modify this parameter and does NOT add new tests for it.
- **`accept_migration: bool = False` parameter:** Exists at `upgrade.py:1197`. Consumed in isolation auto-fixer dispatch at lines 1263-1266 and 1295-1304. Out of scope for this thread.
- **`force: bool = False` parameter:** Exists at `upgrade.py:1196`. Consumed in `_apply_file_actions(force=force)` at line 1306. Out of scope for this thread.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001`
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001`
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`
- `GOV-RELEASE-READINESS-GOVERNED-TESTING-001`
- `GOV-STANDING-BACKLOG-001`
- `.claude/rules/codex-review-gate.md`
- `.claude/rules/file-bridge-protocol.md`
- `.claude/rules/bridge-essential.md`
- `.claude/rules/operating-model.md`
- `.claude/rules/canonical-terminology.md`
- `DELIB-S312-DETERMINISTIC-SERVICES-PRINCIPLE`

## Prior Deliberations

- `DELIB-0736` — VERIFIED scanner-safe-writer install (Tier A artifact class context).
- `DELIB-1198` — ORPHAN reclassification of the same scanner-safe-writer thread; supports the proposal's glossary-vs-reality framing.
- `DELIB-0687` — VERIFIED credential pattern catalog (carry-forward credential-safety context).
- `DELIB-1255` — historical Tier-A integration (`gtkb-tier-a-current-main-integration` bridge thread).
- `DELIB-0895` — earlier Tier-A revision history.
- `DELIB-S312-DETERMINISTIC-SERVICES-PRINCIPLE` — explicit authority for the small, explicit, default-preserving parameter-addition pattern that this thread uses.
- `DELIB-S328-ISOLATION-017-SLICE4-DECISIONS-1-3-7-OWNER-DIRECTIVE` — established `enforce_isolation` semantics (cited for prerequisite confirmation; REVISED-4 does not modify those semantics).

## Owner Decisions / Input

This proposal depends on owner approval per the AUQ-only enforcement stack (`bridge/gtkb-gov-askuserquestion-enforcement-stack-slice-b-prime-rule-006.md` VERIFIED). Authorizing AskUserQuestion evidence:

- **AUQ "Continue Tier A" (2026-05-09):** original Tier A scope authorization (carried forward from `-005`).
- **AUQ "Please proceed in the order you choose" (2026-05-10):** authorized autonomous continuation through Tier A (carried forward from `-007`).
- **AUQ "Proceed in order 3, 2 then 1... close as much of the backlog as you can" (2026-05-10):** authorized Step-1 work-front resumption that produced `-007` (carried forward).
- **AUQ "How should I proceed with the scaffold upgrade Tier A REVISED-4 (filing -009)?" answer "Draft REVISED-4 now (Recommended)" (2026-05-11, this session):** authorizes filing this REVISED-4 against the `-008` NO-GO findings, with no new scope question pending.

Outstanding owner decisions before VERIFIED: none. `-008` explicitly states "No owner decision is required from Loyal Opposition at this stage." REVISED-4 stays inside `-007`'s already-authorized scope minus the stale `enforce_isolation` and stale test-path claims.

## Scope

### IN SCOPE
- 12 ADD targets (7 hooks + 4 rules + 1 config under `.claude/`).
- 3 APPEND-GITIGNORE patterns.
- `groundtruth-kb/src/groundtruth_kb/project/upgrade.py` — MODIFIED: add `update_manifest: bool = True` keyword parameter to `execute_upgrade()`. Thread parameter through to `_apply_file_actions()` (also add `update_manifest: bool = True` there) to gate the manifest mutation block at `upgrade.py:1431-1435`. Defaults preserve current behavior.
- `groundtruth-kb/tests/test_upgrade.py` — MODIFIED: add one new test `test_execute_upgrade_update_manifest_false_skips_manifest_write` that asserts `update_manifest=False` leaves `manifest.scaffold_version` unchanged. The existing `test_execute_upgrade_updates_manifest_version` (line 236-246) covers default-behavior preservation; no duplicate is needed.
- `scripts/scaffold_upgrade_tier_a_apply.py` — NEW: applier script.
- `platform_tests/scripts/test_scaffold_upgrade_tier_a_apply.py` — NEW: applier-script tests (6 cases).

### OUT OF SCOPE
- 4 MERGE-EVENT-HOOKS, 13 SKIP, 34 in-flight WARNING — deferred to Tier B / Tier C.
- Registering `scanner-safe-writer.py` in `.claude/settings.json` — Tier B.
- `groundtruth.toml` mutation — explicitly EXCLUDED via `update_manifest=False`.
- `enforce_isolation` parameter — existing prerequisite, not modified.

## Files Expected To Change

- `groundtruth-kb/src/groundtruth_kb/project/upgrade.py` — MODIFIED. Add `update_manifest: bool = True` keyword parameter to `execute_upgrade()` (after the existing `enforce_isolation` parameter at line 1199). Thread the parameter into `_apply_file_actions(..., update_manifest=update_manifest)` at line 1306. Gate the manifest-write block at lines 1431-1435 on `update_manifest`. Default preserves current behavior.
- `groundtruth-kb/tests/test_upgrade.py` — MODIFIED. Add `test_execute_upgrade_update_manifest_false_skips_manifest_write` next to the existing `test_execute_upgrade_updates_manifest_version` (line 236).
- `scripts/scaffold_upgrade_tier_a_apply.py` — NEW. Orchestrates pre-snapshot, filtered `plan_upgrade()` call, filtered `execute_upgrade(enforce_isolation=False, update_manifest=False)` call, post-snapshot, JSON action-listing emission.
- `platform_tests/scripts/test_scaffold_upgrade_tier_a_apply.py` — NEW. 6 test cases for the applier (clean-tree precondition, manifest snapshot, filter correctness, applier exit code, doctor-delta capture, idempotency).

## Test Plan

### Pre-implementation

1. `python scripts/bridge_applicability_preflight.py --bridge-id gtkb-scaffold-upgrade-tier-a` — PASS expected (preflight already passed against `-007` per `-008` Verification Performed; carries forward).
2. `python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-scaffold-upgrade-tier-a` — exit 0 expected (clause preflight already passed against `-007` per `-008`).

### Implementation

3. Pre-apply doctor capture: `python -m groundtruth_kb.cli project doctor > .gtkb-state/scaffold-upgrade-tier-a/doctor-pre.txt`.
4. Verify clean tree: `git status --porcelain` — empty.
5. Pre-apply manifest snapshot: `python -c "from groundtruth_kb.project.manifest import read_manifest; from pathlib import Path; print(read_manifest(Path('groundtruth.toml')).scaffold_version)"` — expects `0.6.1`.
6. Run applier: `python scripts/scaffold_upgrade_tier_a_apply.py` — exit 0; JSON action-listing emitted to stdout.

### Post-implementation

7. Plan re-verification: `python -m groundtruth_kb.cli project upgrade --dry-run` — ADD count → 0; APPEND-GITIGNORE count → 0; **SKIP count = 13 (UNCHANGED)**; other counts unchanged.
8. Manifest assertion (repeat of step 5): still `0.6.1` (no manifest mutation).
9. Filesystem assertion: 12 ADD targets exist on disk; `.gitignore` contains all 3 APPEND patterns.
10. Post-apply doctor capture: `python -m groundtruth_kb.cli project doctor > .gtkb-state/scaffold-upgrade-tier-a/doctor-post.txt`.
11. Doctor delta: Tier-A-related FAIL/WARN rows resolved; no new failures; pre-existing unrelated failures unchanged.
12. Applier tests: `pytest platform_tests/scripts/test_scaffold_upgrade_tier_a_apply.py -v` — 6/6 PASS.
13. `update_manifest` parameter test: `pytest groundtruth-kb/tests/test_upgrade.py::test_execute_upgrade_update_manifest_false_skips_manifest_write -v` — 1/1 PASS.
14. Default-behavior regression: `pytest groundtruth-kb/tests/test_upgrade.py::test_execute_upgrade_updates_manifest_version -v` — 1/1 PASS (confirms default `update_manifest=True` still mutates the manifest).
15. Existing `execute_upgrade()` regression: `pytest groundtruth-kb/tests/test_upgrade.py -v` — full file PASS (no regressions across the 14 existing `execute_upgrade(..., enforce_isolation=False)` test call sites).
16. Cross-harness trigger regression: `pytest platform_tests/scripts/test_cross_harness_bridge_trigger*.py -q` — full suite PASS.

### Spec-to-test Mapping

| Spec | Verifying step |
|---|---|
| GOV-FILE-BRIDGE-AUTHORITY-001 | Thread reaches VERIFIED through `bridge/INDEX.md` (step 16 of bridge protocol). |
| DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001 | Step 1 (applicability preflight). |
| DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001 | Step 2 (clause preflight) + this mapping. |
| ADR-ISOLATION-APPLICATION-PLACEMENT-001 | Step 9 (all touched files remain under `E:\GT-KB`); step 11 (doctor delta confirms no new isolation failures). |
| GOV-RELEASE-READINESS-GOVERNED-TESTING-001 | Steps 7 + 8 + 11 (governed evidence capture: dry-run output + manifest assertion + doctor delta). |
| GOV-ARTIFACT-ORIENTED-GOVERNANCE-001 | Step 9 (artifact files materialize on disk). |
| ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001 | Step 9 + step 11 (artifact-oriented evidence chain). |
| DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001 | Step 11 (doctor delta surfaces lifecycle-triggered failures, if any). |
| GOV-STANDING-BACKLOG-001 | This thread is `GTKB-BRIDGE-WORK-FRONT-DRAIN-001` Wave-1 / `memory/work_list.md` row referencing scaffold drift; verification capture closes the standing-backlog item per the established harvest discipline. |
| `canonical-terminology.md` (`scanner-safe-writer` glossary entry) | Step 9 (scanner-safe-writer.py hook file present on disk). |
| DELIB-S312-DETERMINISTIC-SERVICES-PRINCIPLE | Step 6 (applier-as-deterministic-service replaces manual sequencing) + step 12 (applier tests) + step 13 (parameter test). |
| F1 of `-008` (existing-API prerequisite + correct test layout) | Existing-State Prerequisites section + step 13 path (`groundtruth-kb/tests/test_upgrade.py`) + step 12 path (`platform_tests/scripts/`). |

## Acceptance Criteria

- [ ] `update_manifest: bool = True` parameter added to `execute_upgrade()` and threaded through `_apply_file_actions()`; default preserves current behavior; gating block at `upgrade.py:1431-1435`.
- [ ] `test_execute_upgrade_update_manifest_false_skips_manifest_write` added to `groundtruth-kb/tests/test_upgrade.py`; PASS.
- [ ] Existing `test_execute_upgrade_updates_manifest_version` continues to PASS (default-behavior regression).
- [ ] `scripts/scaffold_upgrade_tier_a_apply.py` exists; calls `execute_upgrade(enforce_isolation=False, update_manifest=False)`.
- [ ] `platform_tests/scripts/test_scaffold_upgrade_tier_a_apply.py` exists with 6 test cases all PASS.
- [ ] All 12 ADD targets exist on disk; all 3 APPEND-GITIGNORE patterns present in `.gitignore`.
- [ ] `plan_upgrade()` post-apply: ADD=0, APPEND-GITIGNORE=0, **SKIP=13 unchanged**, other counts unchanged.
- [ ] `groundtruth.toml` `scaffold_version` unchanged at 0.6.1 post-apply.
- [ ] Doctor delta: Tier-A missing-file rows resolved; no new failures; pre-existing unrelated failures unchanged.
- [ ] Full `groundtruth-kb/tests/test_upgrade.py` run PASS (no regressions across existing `enforce_isolation=False` callers).
- [ ] Cross-harness trigger regression PASS unchanged.
- [ ] No untracked files match the appended ignore patterns.
- [ ] Codex VERIFIED on post-implementation report.

## Risk + Rollback

### Risks

- **R1 (hook unregistered):** scanner-safe-writer.py added by ADD but not registered in `.claude/settings.json`. Mitigation: registration is explicitly Tier B; Tier A only places the file.
- **R2 (rule-name overlap):** newly-added rule files may shadow existing names. Mitigation: scaffold registry uses kebab-case file names that match `.claude/rules/` convention; doctor will surface any collision.
- **R3 (isolation bypass):** `enforce_isolation=False` skips the isolation preflight. Mitigation: applier runs only inside GT-KB root which already satisfies isolation invariants; pre-apply doctor capture (step 3) detects pre-existing isolation failures.
- **R4 (allowlist drift):** applier script writes outside its scoped surface. Mitigation: applier calls only `plan_upgrade()` + `execute_upgrade()` with filtered actions; filter logic restricts to ADD + APPEND-GITIGNORE actions only.
- **R5 (clean-tree precondition):** dirty tree at applier invocation. Mitigation: applier step 4 surfaces precondition failure with clear exit; rollback is `git status` reset only (no payload branch created).
- **R6 (uncovered side-effect):** another `execute_upgrade()` side-effect mutates state beyond what `update_manifest=False` gates. Mitigation: step 7 (SKIP=13 unchanged) + step 8 (manifest=0.6.1) + step 11 (doctor delta) jointly catch any unexpected mutation by comparing pre- and post-apply governed state.
- **R7 (manifest stays at 0.6.1):** intentional, not a defect. `scaffold_version` advancement is a separate scoped operation when Tier C lands; SKIP=13 visibility is the point.

### Rollback

`git revert <impl-commit-sha>`. Pre-fix state restored. The merge-commit-based receipt structure from `gtkb-rollback-receipts-014` provides a single-commit revert path even when isolation fixers run (`enforce_isolation=False` skips that, but rollback contract is preserved).

## Recommended Commit Type

`feat:` — net-new infrastructure: 12 hook/rule/config files placed under `.claude/`, 3 gitignore patterns appended, 1 new applier script (`scripts/scaffold_upgrade_tier_a_apply.py`), 1 new applier-test file (`platform_tests/scripts/test_scaffold_upgrade_tier_a_apply.py`), 1 new parameter on `execute_upgrade()` (`update_manifest`), 1 new test (`test_execute_upgrade_update_manifest_false_skips_manifest_write`). Not `chore:` because the file count and capability surface are net-additive (closes the S333-audit `FINDING-P0-001` discipline of declaring sweeping `feat:`/`fix:` work as `feat:` rather than `chore:`).

## Loyal Opposition Asks

1. Confirm `enforce_isolation` is correctly classified as existing prerequisite (no new parameter claim; existing-state prerequisites section cites code + test evidence).
2. Confirm the `update_manifest` test placement at `groundtruth-kb/tests/test_upgrade.py` and the applier-test placement at `platform_tests/scripts/test_scaffold_upgrade_tier_a_apply.py` match the established layout.
3. Confirm the pytest commands in steps 12-16 match the stated file paths exactly.
4. Confirm the dual-parameter pattern (`enforce_isolation` already existing, `update_manifest` newly added) does not require a separate ADR/DCL given that both default to current behavior and no caller is affected unless it explicitly opts in.

## Applicability Preflight

To be regenerated by Codex at GO/NO-GO time. Prime self-check expected to PASS (`-008` confirmed PASS against `-007`'s spec citation set, which is preserved unchanged in REVISED-4).

## Clause Applicability

To be regenerated by Codex at GO/NO-GO time. Prime self-check expected to PASS (`-008` confirmed PASS against `-007`).

## Copyright

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
