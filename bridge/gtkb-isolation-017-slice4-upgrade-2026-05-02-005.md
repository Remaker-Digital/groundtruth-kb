REVISED

# Implementation Proposal — GTKB-ISOLATION-017 Slice 4 (Revision 2)

Proposed by: Prime Builder (Claude Code)
Date: 2026-05-02 (S328)
Supersedes: `bridge/gtkb-isolation-017-slice4-upgrade-2026-05-02-003.md` (REVISED-1; NO-GO at `-004`)
Carries forward: `-001` NEW + `-002` Codex NO-GO (F1–F4) + `-003` REVISED-1 + `-004` Codex NO-GO (F1–F2 second-cycle).
Addresses: Codex `-004` findings F1 (auto-fixer dispatch contract not executable against the live `UpgradeAction` executor) + F2 (`upgrade_policy` honor asserted but unimplemented and untested).

## NO-GO Acknowledgement

Codex `-004` confirmed all 4 prior findings are corrected in broad structure, then surfaced two NEW blocking issues exposed by REVISED-1's tighter contract. Both accepted in full.

### F1 (P1) — Auto-fixer dispatch contract is not executable against the live executor

**Acknowledged.** I asserted I'd "inject UpgradeAction rows" for each auto-fixable check, but the live `UpgradeAction.action: Literal[...]` at `groundtruth-kb/src/groundtruth_kb/project/upgrade.py:72-80` permits only `{update, add, skip, merge-event-hooks, append-gitignore, warning, informational}`. The executor at `:836-861` dispatches custom logic only for `merge-event-hooks` and `append-gitignore`; everything else falls through to `_map_target_to_template(action.file)` (`:214-224`) which copies a template-registered file. None of my proposed structured fixers (rewriting `[service]` block, rewriting `work_subject` field, rewriting hook entries by content, etc.) fit that copy-from-template shape.

Fix: choose Codex's option 2 — **typed isolation-fixer dispatch outside `UpgradeAction`**. Fixers run inside the payload branch but are invoked via a typed dispatcher function with a check-name → helper map; they return a typed `IsolationFixerResult` list, not `UpgradeAction` results. The existing `UpgradeAction` executor is unchanged; isolation fixers are a sibling code path within `execute_upgrade()`.

### F2 (P1) — `upgrade_policy` honor is asserted but unimplemented and untested

**Acknowledged.** Acceptance criterion 7 in `-003` said "fixers honor `upgrade_policy` (no override of `preserve` / `transient` / `adopter-opt-in`)" but: (a) the proposed fixers don't consult policy; (b) the files they want to mutate (`groundtruth.toml`, `memory/release-readiness.md`) are `ownership=adopter-owned`, `upgrade_policy=preserve` per the Slice 3 registry pattern at `groundtruth-kb/templates/managed-artifacts.toml:835-857`. The `-003` text was internally inconsistent.

Fix: **explicit governed exception**, per owner decision at S328 (AskUserQuestion answered "--accept-migration overrides preserve for the isolation-fix surface"). The override is bounded by:

1. A `_ISOLATION_FIX_SURFACE_FILES: frozenset[str]` constant listing the exact relative paths the 5 fixers may touch (no other files; defense in depth).
2. The fixers run only when `accept_migration=True` AND the live check fired with `status in {"fail", "warning"}`.
3. The rollback receipt records each preserve-policy mutation with its prior policy classification, providing adopter audit + `git revert -m 1 <merge_commit>` reversal.
4. The governing rule citation is documented inline in the fixer code: this is the `mandatory_at_upgrade` + `one_shot_migration_at_upgrade` decision pair (DELIB-S328-ISOLATION-017-SLICE4-DECISIONS-1-3-7-OWNER-DIRECTIVE) + S328 owner decision authorizing the preserve-override scope (this revision).

Tests cover all four boundary conditions: (a) override fires only with `accept_migration=True`; (b) override fires only for files in `_ISOLATION_FIX_SURFACE_FILES`; (c) arbitrary other preserve files would NOT be touched even with `--accept-migration`; (d) the receipt records each preserve-mutated file.

## Specification Links

All Specification Links from `-001`/`-003` carry forward unchanged. Re-cited briefly here for compliance-gate verification.

1. **Phase 9 plan §2** at `independent-progress-assessments/CODEX-INSIGHT-DROPBOX/GTKB-ISOLATION-009-PHASE9-ADOPTER-PACKAGING-AND-VALIDATION-PLAN-2026-04-23.md` lines 144–197.
2. **ADR-ISOLATION-APPLICATION-PLACEMENT-001**.
3. **`.claude/rules/project-root-boundary.md`**.
4. **`.claude/rules/file-bridge-protocol.md`** (Mandatory Specification Linkage Gate + Verification Gate).
5. **`.claude/rules/codex-review-gate.md`**.
6. **Scoping carry-forward** at `bridge/gtkb-isolation-017-scoping-003.md` lines 117–131 + `-004` GO.
7. **GOV-09**, **GOV-19**, **GOV-20**.
8. **Prior Slice GOs:** Slice 1 `-012` VERIFIED, Slice 2 `-008` VERIFIED, Slice 2.5 `-008` VERIFIED, Slice 3 `-014` VERIFIED.
9. **Prior Deliberations:** `DELIB-S328-ISOLATION-017-SLICE4-DECISIONS-1-3-7-OWNER-DIRECTIVE` v1 + S328 follow-on AskUserQuestion answer authorizing preserve-override scope (per F2 fix; this REVISED-2 cites the answer text in §"NO-GO Acknowledgement F2"). Plus `DELIB-1020`, `DELIB-1011`, `DELIB-0955`, `DELIB-0957`, `DELIB-0958`, `DELIB-0960`, `DELIB-0988`, `DELIB-1003`, `DELIB-1049`, `DELIB-1392`, `DELIB-1395`, `DELIB-S324-PROJECT-ROOT-BOUNDARY-SANDBOX-EXCEPTION-CHOICE` (carried from `-002` and `-004` Prior Deliberations).

## Live-Probed Partition (carried verbatim from `-003`; per F1 fix in `-002`)

Probe command (S328): `python -c "from groundtruth_kb.project.doctor_isolation import run_isolation_checks; ..."`. Verbatim output:

```
  name='isolation:adopter-root-placement'  status=fail
  name='isolation:service-endpoint'  status=info
  name='isolation:work-subject'  status=info
  name='isolation:no-writable-product-paths'  status=fail
  name='isolation:hooks-point-to-wrappers'  status=warning
  name='isolation:workstream-focus-hook-absent'  status=warning
  name='isolation:work-list-no-product-entries'  status=warning
  name='isolation:release-readiness-app-subject-header'  status=warning
  name='isolation:chroma-regeneratable'  status=pass
TOTAL: 9
```

| # | Live `ToolCheck.name` | Category | Auto-fixer (Slice 4) | Touched file (per F2 surface) | Touched-file `upgrade_policy` |
|---|---|---|---|---|---|
| 1 | `isolation:adopter-root-placement` | **HARD-REFUSE** | none | (n/a — refusal) | (n/a) |
| 2 | `isolation:service-endpoint` | **AUTO-FIXABLE** | `_fix_isolation_service_endpoint` | `groundtruth.toml` | `preserve` (override under `--accept-migration`) |
| 3 | `isolation:work-subject` | **AUTO-FIXABLE** | `_fix_isolation_work_subject` | `groundtruth.toml` | `preserve` (override under `--accept-migration`) |
| 4 | `isolation:no-writable-product-paths` | **NEEDS-ADOPTER-INPUT** | none | (n/a — refuse-with-guidance) | (n/a) |
| 5 | `isolation:hooks-point-to-wrappers` | **AUTO-FIXABLE** | `_fix_isolation_hook_paths` | `.claude/settings.json` | settings-hook-registration (`merge-event-hooks` policy; no override needed) |
| 6 | `isolation:workstream-focus-hook-absent` | **AUTO-FIXABLE** | `_fix_isolation_remove_workstream_focus_hook` | `.claude/settings.json` | settings-hook-registration (`merge-event-hooks` policy; no override needed) |
| 7 | `isolation:work-list-no-product-entries` | **NEEDS-ADOPTER-INPUT** | none | (n/a — refuse-with-guidance) | (n/a) |
| 8 | `isolation:release-readiness-app-subject-header` | **AUTO-FIXABLE** | `_fix_isolation_release_readiness_banner` | `memory/release-readiness.md` | `preserve` (override under `--accept-migration`) |
| 9 | `isolation:chroma-regeneratable` | **NEEDS-ADOPTER-INPUT** | none | (n/a — refuse-with-guidance) | (n/a) |

Total: 1 hard-refuse + 5 auto-fixable + 3 needs-adopter-input = 9 ✓ (exhaustive, no overlap).

`_ISOLATION_FIX_SURFACE_FILES` (per F2 fix; the only relative paths the 5 auto-fixers may touch):

```python
_ISOLATION_FIX_SURFACE_FILES: frozenset[str] = frozenset({
    "groundtruth.toml",                    # touched by checks #2, #3
    ".claude/settings.json",               # touched by checks #5, #6
    "memory/release-readiness.md",         # touched by check #8
})
```

3 distinct files for 5 fixers. Of those, 2 (`groundtruth.toml`, `memory/release-readiness.md`) are `upgrade_policy=preserve` and require the `--accept-migration` governed exception. The third (`.claude/settings.json`) uses settings-hook-registration policy via the existing `merge-event-hooks` machinery (no policy override).

## Scope

### In-scope

Files modified:
- `groundtruth-kb/src/groundtruth_kb/project/upgrade.py` — add `IsolationLocationFailureError`, `IsolationMigrationRequiredError`, `IsolationNonAutoFixableError`, plus `IsolationPolicyOverrideViolation` (raised if a fixer attempts to mutate a file outside `_ISOLATION_FIX_SURFACE_FILES`); add `IsolationPreflightResult` and `IsolationFixerResult` dataclasses; add `_run_isolation_preflight(target, profile, product_root)`; add `_run_isolation_fixers(target, profile, auto_fixable_checks)` typed dispatcher returning `list[IsolationFixerResult]`; extend `plan_upgrade()` (currently lines 637–701) with `_check_isolation_state` non-mutating rows; extend `execute_upgrade()` (currently lines 704–806) with `accept_migration: bool = False` keyword-only argument and the typed-fixer invocation inside the payload branch (per F1 fix); extend rollback receipt with an `isolation_migration` block (per F2 fix). **No `UpgradeAction` shape changes**; all isolation-fixer logic is a sibling typed code path within `execute_upgrade()` (per F1 fix).
- `groundtruth-kb/src/groundtruth_kb/cli.py` — add `--accept-migration` Click flag to `project_upgrade` (currently lines 902–993); render the rehearsal-recipe block when isolation checks fail; add exception handlers for the three (now four) new exception classes (exit code 5 = isolation refusal; new in this slice).
- `groundtruth-kb/src/groundtruth_kb/project/preflight.py` — add `_check_isolation_state(target, profile, product_root)` returning `warning`/`informational` `UpgradeAction` rows for `plan_upgrade()` consumption.
- `groundtruth-kb/templates/managed-artifacts.toml` — register the new rehearsal-recipe template file as a `class = "file"` row mirroring Slice 3's pattern at lines 835–857.
- `groundtruth-kb/templates/project/upgrade-rehearsal-recipe.md` *(new)* — adopter-facing rehearsal recipe block (carried from `-003`).

Files created (new):
- `groundtruth-kb/tests/test_upgrade_isolation.py` — Slice 4 spec-derived tests (T1–T14; see §"Test Plan").

Documents (per GOV-20):
- `IPR-SLICE4-UPGRADE-ISOLATION-001` — pre-implementation review citing this proposal, ADR-ISOLATION-APPLICATION-PLACEMENT-001, the four S328 owner decisions (1, 3, 7 from primary directive + the F2 preserve-override authorization), and the Phase 9 §2 obligations Slice 4 owns.
- `CVR-SLICE4-UPGRADE-ISOLATION-001` — post-implementation proof of acceptance criteria below.

### Out-of-scope (deferred to other slices or work items)

- Clean-adopter test suite under `groundtruth-kb/tests/adopter/` (Slice 5).
- Documentation chapter in `groundtruth-kb/docs/` (Slice 6); examples (Slice 7); release ops (Slice 8).
- Phase 6 overlay refresh / stale / disposability tests (Slice 5).
- Auto-fixers for the 3 needs-adopter-input checks (#4, #7, #9); all remain refuse-with-guidance.
- Multi-adopter coordination, deprecation-window code paths, version-pin enforcement.
- Invocation of `scripts/rehearse_isolation.py` from upgrade (decision 7 invariant).
- Extension of `_ISOLATION_FIX_SURFACE_FILES` beyond the 3 listed paths (any addition is a future bridge requiring its own owner-decision packet for the new file's preserve-override).

## Implementation Plan

1. **Add typed dataclasses to `upgrade.py`**:
   ```python
   @dataclass
   class IsolationPreflightResult:
       hard_refuse: list[ToolCheck]
       auto_fixable: list[ToolCheck]
       needs_adopter_input: list[ToolCheck]

   @dataclass
   class IsolationFixerResult:
       check_name: str        # e.g., "isolation:service-endpoint"
       file: str              # relative path; must be in _ISOLATION_FIX_SURFACE_FILES
       outcome: Literal["fixed", "skipped", "no-op"]
       reason: str            # human-readable
       prior_policy: str      # the upgrade_policy at fix time (audit; e.g., "preserve")
   ```

2. **Add module constants to `upgrade.py`**:
   - `_PARTITION_HARD_REFUSE`, `_PARTITION_AUTO_FIXABLE`, `_PARTITION_NEEDS_ADOPTER_INPUT` `frozenset[str]` containing the 1/5/3 live `ToolCheck.name` values from §"Live-Probed Partition".
   - `_ISOLATION_FIX_SURFACE_FILES: frozenset[str]` containing the 3 relative paths above.
   - `_ISOLATION_FIXER_MAP: dict[str, Callable]` mapping each auto-fixable check name to its helper function.

3. **Add exception classes to `upgrade.py`**: `IsolationLocationFailureError`, `IsolationMigrationRequiredError`, `IsolationNonAutoFixableError`, `IsolationPolicyOverrideViolation` (defense-in-depth; raised if a fixer ever attempts to mutate a path outside `_ISOLATION_FIX_SURFACE_FILES`).

4. **Add `_run_isolation_preflight(target, profile, product_root) -> IsolationPreflightResult`**: calls `run_isolation_checks(...)`, partitions returned `ToolCheck` instances using the three partition constants; only checks with `status in {"fail", "warning"}` are included.

5. **Add `_run_isolation_fixers(target, profile, auto_fixable_checks) -> list[IsolationFixerResult]` typed dispatcher**:
   - For each `check` in `auto_fixable_checks`:
     - Look up helper via `_ISOLATION_FIXER_MAP[check.name]`. Missing key → raise `RuntimeError` (defensive; the partition contract test ensures this never fires in practice).
     - Call helper with `target`. Helper returns a string; wrap in `IsolationFixerResult`.
     - Helper internally asserts its target file is in `_ISOLATION_FIX_SURFACE_FILES` (defense in depth via `IsolationPolicyOverrideViolation` if not).

6. **Extend `preflight.py`** with `_check_isolation_state(target, profile, product_root)` returning `UpgradeAction`s in the existing shape. One `informational` row when all checks pass; one `warning` row per failing check.

7. **Extend `plan_upgrade()`** to add the isolation pre-flight rows after the existing pre-flight calls.

8. **Extend `execute_upgrade(target, actions, *, force, accept_migration=False)`**:
   - Add `accept_migration: bool = False` keyword-only argument.
   - Re-run `_run_isolation_preflight(target, profile, product_root)` after the malformed-settings halt, before `_require_git_repo`.
   - Branch as specified in `-003` Implementation Plan §6 (hard-refuse / migration-required / non-auto-fixable / proceed).
   - When proceeding with `accept_migration=True`: invoke `_run_isolation_fixers` BEFORE `_apply_file_actions` inside the payload branch. Concatenate fixer results into the result list with `[FIXED]` / `[SKIPPED]` formatting.
   - Receipt extension: after `merge_commit` is computed (line 783), add to receipt dict:
     ```json
     "isolation_migration": {
       "auto_fixed": [{"check_name": "isolation:work-subject", "file": "groundtruth.toml", "prior_policy": "preserve"}, ...],
       "left_for_adopter": [{"check_name": "isolation:no-writable-product-paths", "message": "..."}, ...],
       "preserve_override_authority": "DELIB-S328 mandatory_at_upgrade + S328 preserve-override decision"
     }
     ```

9. **Add 5 per-check auto-fixer helpers** alongside `_apply_file_actions`. Each helper:
   - Asserts its target file is in `_ISOLATION_FIX_SURFACE_FILES` (defense in depth; raises `IsolationPolicyOverrideViolation` if not).
   - Performs the structured rewrite.
   - Returns `IsolationFixerResult` with `outcome` and `reason`.
   
   Helpers:
   - `_fix_isolation_service_endpoint(target)` → rewrites `[service]` block in `groundtruth.toml`.
   - `_fix_isolation_work_subject(target)` → rewrites `work_subject` in `groundtruth.toml`.
   - `_fix_isolation_hook_paths(target)` → rewrites hook paths in `.claude/settings.json` (uses existing `_compute_target_event_list` machinery for shape consistency; no policy override needed since settings-hook-registration uses overwrite policy).
   - `_fix_isolation_remove_workstream_focus_hook(target)` → deletes defunct hook from `.claude/settings.json`.
   - `_fix_isolation_release_readiness_banner(target)` → rewrites first non-blank line of `memory/release-readiness.md`.

10. **Extend `cli.py:project_upgrade`**: add `--accept-migration` Click flag; thread to `execute_upgrade`; add 4 exception handlers for the new exception classes (all → `SystemExit(5)` with rehearsal-recipe block + per-check guidance).

11. **Author the rehearsal-recipe template** + **register in `managed-artifacts.toml`** (carried from `-003`).

12. **Author IPR and CVR documents** per GOV-20 Phase 1 advisory pilot.

## Test Plan (spec-to-test mapping)

Tests live in `groundtruth-kb/tests/test_upgrade_isolation.py`. GOV-19-compliant + GOV-18-compliant.

T1–T11 carried forward from `-003` with one modification: T3 now asserts `IsolationFixerResult` rows (not generic result strings), and the receipt's `isolation_migration` block per the new schema.

**T12 (NEW per F2 fix) — Preserve-policy override scope.**
Spec source: Codex `-004` F2 + S328 owner decision authorizing preserve-override scope.
Assertions:
- (a) Without `--accept-migration`, `_run_isolation_fixers` is NOT called even if auto-fixable checks fail (already covered by T2; T12 explicitly asserts no fixer is invoked via spy).
- (b) With `--accept-migration`, the override fires only for files in `_ISOLATION_FIX_SURFACE_FILES`; fabricate a fixer that attempts to write to an out-of-surface preserve file → `IsolationPolicyOverrideViolation` raised. (Confirms defense-in-depth assertion in step 9 of Implementation Plan.)
- (c) Arbitrary other adopter-owned `preserve`-policy files in the fixture (e.g., `README.md` from Slice 3, `memory/work_list.md`) are NOT mutated by the migration.

**T13 (NEW per F1 fix) — Dispatcher contract.**
Spec source: Codex `-004` F1 + Implementation Plan §5.
Assertions:
- (a) `_ISOLATION_FIXER_MAP` contains exactly the 5 check names in `_PARTITION_AUTO_FIXABLE` (no missing keys; no extra keys).
- (b) For each `(check_name, helper)` in `_ISOLATION_FIXER_MAP.items()`: monkeypatch the helper to return a sentinel `IsolationFixerResult`; invoke `_run_isolation_fixers` with a synthetic `auto_fixable_checks` list containing exactly that one check; assert the sentinel appears in the returned list. (Proves the dispatcher invokes the intended helper for each check.)
- (c) Calling `_run_isolation_fixers` with an empty `auto_fixable_checks` list returns `[]` and invokes no helpers.
- (d) Calling `_run_isolation_fixers` with an `auto_fixable_checks` list containing a check name NOT in `_ISOLATION_FIXER_MAP` raises `RuntimeError`.

**T14 (NEW per F2 fix) — Receipt records preserve-policy mutations.**
Spec source: Codex `-004` F2 + Implementation Plan §8 (receipt extension).
Assertions: in T3's success path, after migration completes, the rollback receipt at `.claude/upgrade-receipts/active/{receipt_id}.json` contains:
- `isolation_migration.auto_fixed` is a list with one entry per fixer that ran.
- Each entry contains `check_name`, `file`, and `prior_policy` (e.g., `"preserve"` for the 3 preserve-policy files).
- `isolation_migration.preserve_override_authority` cites the DELIB.

Full verification command for the post-impl: `python -m pytest groundtruth-kb/tests/test_upgrade.py groundtruth-kb/tests/test_upgrade_isolation.py groundtruth-kb/tests/test_doctor_isolation.py groundtruth-kb/tests/test_preflight_checks.py -q --tb=short`.

## Acceptance Criteria

This REVISED-2 is GO-able when Codex confirms:

1. Specification Links + Prior Deliberations cover all governing artifacts.
2. Live-Probed Partition keys match `run_isolation_checks()` `ToolCheck.name` values verbatim (per `-002` F1 fix, carried).
3. Partition is exhaustive over the 9 live checks; no overlap; no dead keys; T11 enforces.
4. Work-list scrub absent from implementation surface (per `-002` F2 fix, carried).
5. Template registry path is `groundtruth-kb/templates/managed-artifacts.toml` (per `-002` F3 fix, carried).
6. Decision 7 invariant ("upgrade does NOT invoke rehearsal driver") enforced (T5).
7. **Auto-fixer dispatch contract uses typed `IsolationFixerResult` returned by `_run_isolation_fixers`, NOT `UpgradeAction` rows** (per `-004` F1 fix). T13 enforces dispatcher correctness; the existing `UpgradeAction` executor is unchanged.
8. **`upgrade_policy` honor is implemented as a bounded governed exception**: fixers run only with `accept_migration=True`, only for files in `_ISOLATION_FIX_SURFACE_FILES`, only against checks in `_PARTITION_AUTO_FIXABLE` (per `-004` F2 fix). T12 enforces override-scope correctness; T14 enforces audit-trail visibility in the rollback receipt.
9. Estimated envelope ~200–300 LOC source + ~400–550 LOC tests (slightly larger than `-003` due to typed dispatcher + 3 new tests; still within scoping bridge ceiling).

## Risk / Rollback

**Risk 1 — partition correctness (LOW; unchanged from `-003`).** T11 gates.

**Risk 2 — preserve-override scope creep (LOW NEW).** A future maintainer might be tempted to extend `_ISOLATION_FIX_SURFACE_FILES` to other preserve files for other migrations. **Mitigation:** the constant carries a `# Owner decision required to extend; see DELIB-S328` comment + T12 (b) (defense-in-depth `IsolationPolicyOverrideViolation`) makes any unauthorized extension visible at test time.

**Risk 3 — auto-fixer destructive behavior (medium; unchanged).** Mitigated by payload-branch + rollback-receipt + `git revert -m 1 <merge_commit>`. T6 + T14 cover.

**Risk 4 — pre-flight performance (low; unchanged).**

**Risk 5 — exit code 5 collision (low; unchanged).**

**Rollback path:** as in `-003` — Slice 4 implementation reversible via revert of merge commit on `develop`; specific adopter migrations reversible via `gt project rollback` consuming the receipt + the new `isolation_migration` audit block.

## Decision Needed From Owner

**None at REVISED-2 time.** The F2 design choice (preserve-override vs strict) was decided at S328 via AskUserQuestion in this session ("--accept-migration overrides preserve for the isolation-fix surface"). All other decisions previously settled per DELIB-S328-ISOLATION-017-SLICE4-DECISIONS-1-3-7-OWNER-DIRECTIVE.

## Carry-Forward From `-002` and `-004` That Did Not Block

- `-002` F1–F4 corrections (live partition keys, work_list partition consistency, template paths, partition-contract test) — all carried from `-003` unchanged.
- The ChromaDB deprecation warning surfaced in Slice 3 verification is unrelated to this slice.

---

*© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
