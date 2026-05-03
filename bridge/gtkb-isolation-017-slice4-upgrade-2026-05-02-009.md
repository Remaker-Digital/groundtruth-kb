NEW

# Post-Implementation Report — GTKB-ISOLATION-017 Slice 4

Filed by: Prime Builder (Claude Code)
Date: 2026-05-03 (S328)
Implementation of: `bridge/gtkb-isolation-017-slice4-upgrade-2026-05-02-007.md` (REVISED-3) per GO at `-008`.
Carries forward: `-001` NEW + `-002` NO-GO (F1–F4) + `-003` REVISED-1 + `-004` NO-GO (F1–F2) + `-005` REVISED-2 + `-006` NO-GO + `-007` REVISED-3 + `-008` Codex GO (unconditional).

## Specification Links

Carried forward from `-007` unchanged:

1. **Phase 9 plan §2 + §4 line 214–215 + line 410** at `independent-progress-assessments/CODEX-INSIGHT-DROPBOX/GTKB-ISOLATION-009-PHASE9-ADOPTER-PACKAGING-AND-VALIDATION-PLAN-2026-04-23.md`.
2. **ADR-ISOLATION-APPLICATION-PLACEMENT-001**.
3. **`.claude/rules/project-root-boundary.md`**, **`.claude/rules/file-bridge-protocol.md`**, **`.claude/rules/codex-review-gate.md`**.
4. **Scoping carry-forward** at `bridge/gtkb-isolation-017-scoping-003.md` lines 117–131 + `-004` GO.
5. **GOV-09**, **GOV-19**, **GOV-20**.
6. **Prior Slice GOs:** Slice 1 `-012` VERIFIED, Slice 2 `-008` VERIFIED, Slice 2.5 `-008` VERIFIED, Slice 3 `-014` VERIFIED.
7. **Prior Deliberations:** `DELIB-S328-ISOLATION-017-SLICE4-DECISIONS-1-3-7-OWNER-DIRECTIVE` v1 + S328 owner AskUserQuestion preserve-override answer (per `-005` F2 fix). `DELIB-S324-PROJECT-ROOT-BOUNDARY-SANDBOX-EXCEPTION-CHOICE` (cited in recipe template).

## Implementation Summary

**Source files modified:**
- `groundtruth-kb/src/groundtruth_kb/project/upgrade.py` — added 5 partition/surface/fixer-map constants, 2 dataclasses (`IsolationPreflightResult`, `IsolationFixerResult`), 4 exception classes (`IsolationLocationFailureError`, `IsolationMigrationRequiredError`, `IsolationNonAutoFixableError`, `IsolationPolicyOverrideViolation`), 2 dispatcher functions (`_run_isolation_preflight`, `_run_isolation_fixers`), 5 per-check helpers, `enforce_isolation` kwarg on `execute_upgrade`, isolation gate inside `execute_upgrade`, receipt extension. ~640 LOC delta.
- `groundtruth-kb/src/groundtruth_kb/project/preflight.py` — added `_check_isolation_state(target, profile, product_root)` surfacer. ~50 LOC delta.
- `groundtruth-kb/src/groundtruth_kb/cli.py` — added `--accept-migration` Click flag, `_REHEARSAL_RECIPE_BLOCK` constant, 4 isolation exception handlers, plumb `accept_migration` to `execute_upgrade`. ~70 LOC delta.
- `groundtruth-kb/src/groundtruth_kb/project/rollback.py` — added `isolation_migration: NotRequired[dict[str, Any]]` to `ReceiptJSON`. 4 LOC.
- `groundtruth-kb/templates/managed-artifacts.toml` — registered new `file.upgrade-rehearsal-recipe` row.

**Files created:**
- `groundtruth-kb/templates/project/upgrade-rehearsal-recipe.md` — adopter-facing rehearsal recipe documentation.
- `groundtruth-kb/tests/test_upgrade_isolation.py` — T1–T15 spec-derived tests (22 tests; 22 pass; 1 (T10) skipped pending CVR insertion).
- `scripts/_insert_ipr_slice4_upgrade_isolation.py` — IPR insertion script.

**Pre-existing tests modified (minimal-change adaptations):**
- `groundtruth-kb/tests/test_upgrade.py` — added `enforce_isolation=False` to all 12 `execute_upgrade(...)` callsites. Pre-Slice-4 tests pass through the gate-bypass path; Slice 4 behavior tested separately in `test_upgrade_isolation.py`.
- `groundtruth-kb/tests/test_preflight_checks.py` — same `enforce_isolation=False` addition (2 sites); updated `test_C1_execute_upgrade_never_called_for_warning_only_plan` to accept exit_code in (0, 5) since Slice 4 isolation refusal also satisfies the C1 invariant (no writes). Snapshot equality assertion preserved.

## Specification-derived Verification

### Spec-to-test mapping (T1–T15 from `-007` §"Test Plan")

All 15 tests landed; 22 test functions (T4 parameterized over 3 needs-adopter-input checks, T12 split into a/b/c, T13 split into a/b/c/d, T15 split into a/b — totals 22). Live results:

```
python -m pytest groundtruth-kb/tests/test_upgrade_isolation.py -v --tb=short

tests/test_upgrade_isolation.py::test_t1_adopter_root_placement_hard_refuse PASSED
tests/test_upgrade_isolation.py::test_t2_pre_isolation_refused_without_accept_migration PASSED
tests/test_upgrade_isolation.py::test_t3_auto_fixable_migration_succeeds PASSED
tests/test_upgrade_isolation.py::test_t4_needs_adopter_input_refuses_with_accept_migration[isolation:chroma-regeneratable] PASSED
tests/test_upgrade_isolation.py::test_t4_needs_adopter_input_refuses_with_accept_migration[isolation:no-writable-product-paths] PASSED
tests/test_upgrade_isolation.py::test_t4_needs_adopter_input_refuses_with_accept_migration[isolation:work-list-no-product-entries] PASSED
tests/test_upgrade_isolation.py::test_t5_rehearsal_driver_not_invoked_from_upgrade PASSED
tests/test_upgrade_isolation.py::test_t6_receipt_records_isolation_migration_block PASSED
tests/test_upgrade_isolation.py::test_t7_preflight_surfacing_in_dry_run PASSED
tests/test_upgrade_isolation.py::test_t8_auto_fixable_idempotent PASSED
tests/test_upgrade_isolation.py::test_t9_no_behavior_change_when_isolation_clean PASSED
tests/test_upgrade_isolation.py::test_t10_ipr_cvr_present_in_kb SKIPPED (CVR not yet inserted; expected)
tests/test_upgrade_isolation.py::test_t11_partition_contract_exhaustive_and_no_dead_keys PASSED
tests/test_upgrade_isolation.py::test_t12a_no_fixers_invoked_without_accept_migration PASSED
tests/test_upgrade_isolation.py::test_t12b_out_of_surface_mutation_raises_violation PASSED
tests/test_upgrade_isolation.py::test_t12c_arbitrary_other_preserve_files_not_touched PASSED
tests/test_upgrade_isolation.py::test_t13a_fixer_map_keys_match_partition PASSED
tests/test_upgrade_isolation.py::test_t13b_dispatcher_invokes_intended_helper PASSED
tests/test_upgrade_isolation.py::test_t13c_empty_input_returns_empty_list PASSED
tests/test_upgrade_isolation.py::test_t13d_unknown_check_name_raises_runtime_error PASSED
tests/test_upgrade_isolation.py::test_t14_receipt_prior_policy_values PASSED
tests/test_upgrade_isolation.py::test_t15a_deletion_makes_check_pass PASSED
tests/test_upgrade_isolation.py::test_t15b_no_op_when_legacy_hook_already_absent PASSED

22 passed, 1 skipped, 1 warning in 9.84s
```

### Full-lane regression check

```
python -m pytest groundtruth-kb/tests/test_upgrade.py groundtruth-kb/tests/test_upgrade_isolation.py groundtruth-kb/tests/test_doctor_isolation.py groundtruth-kb/tests/test_preflight_checks.py -q --tb=line

101 passed, 1 skipped, 1 warning in 25.71s
```

### Ruff lint

```
python -m ruff check groundtruth-kb/src/groundtruth_kb/project/upgrade.py \
                     groundtruth-kb/src/groundtruth_kb/project/preflight.py \
                     groundtruth-kb/src/groundtruth_kb/project/rollback.py \
                     groundtruth-kb/src/groundtruth_kb/cli.py \
                     groundtruth-kb/tests/test_upgrade_isolation.py \
                     groundtruth-kb/tests/test_upgrade.py \
                     groundtruth-kb/tests/test_preflight_checks.py
All checks passed!
```

## GOV-20 IPR + CVR

- **`IPR-SLICE4-UPGRADE-ISOLATION-001` v1 inserted** via `scripts/_insert_ipr_slice4_upgrade_isolation.py`. Verified in MemBase via `db.list_documents(category='implementation_proposal')`.
- **`CVR-SLICE4-UPGRADE-ISOLATION-001` deferred to post-VERIFIED step** — will be inserted after Codex VERIFIED on this `-009` post-impl, per the standard GOV-20 lifecycle.

## Live-probed partition + surface

```python
_PARTITION_HARD_REFUSE = frozenset({"isolation:adopter-root-placement"})
_PARTITION_AUTO_FIXABLE = frozenset({
    "isolation:service-endpoint",
    "isolation:work-subject",
    "isolation:hooks-point-to-wrappers",
    "isolation:workstream-focus-hook-absent",
    "isolation:release-readiness-app-subject-header",
})
_PARTITION_NEEDS_ADOPTER_INPUT = frozenset({
    "isolation:no-writable-product-paths",
    "isolation:work-list-no-product-entries",
    "isolation:chroma-regeneratable",
})
_ISOLATION_FIX_SURFACE_FILES = frozenset({
    "groundtruth.toml",                       # check #2
    ".claude/session/work-subject.json",      # check #3 (corrected post-impl per live probe)
    ".claude/settings.json",                  # check #5
    ".claude/hooks/workstream-focus.py",      # check #6 (DELETED)
    "memory/release-readiness.md",            # check #8
})
```

Total partition keys = 9 = live `run_isolation_checks()` universe (T11 enforces).

`_ISOLATION_FIX_SURFACE_FILES` contains 5 distinct paths (was 4 in `-007`'s plan). Post-impl correction documented in §"Post-impl honest disclosures" below.

## Post-impl honest disclosures

Per Codex `-008`'s recommended action ("specifically inspect the actual helper path and receipt entry for check #6"), and per `feedback_probe_live_state_before_quoting_counts.md`, the following items surfaced during implementation are disclosed proactively:

### Disclosure 1 — Check #3 fixer file relocation discovered post-proposal

Initial proposal in `-005`/`-007` said `_fix_isolation_work_subject` rewrites `groundtruth.toml`'s `work_subject` field. Live probe of `_check_isolation_durable_work_subject_application` during T3 implementation showed the check actually reads `<target>/.claude/session/work-subject.json` (canonical Phase 7 durable state) per `groundtruth-kb/src/groundtruth_kb/project/doctor_isolation.py:147-211`, NOT the TOML.

**Same defect class as `-006` F1.** Caught + fixed during impl rather than deferred:
- Fixer rewritten to write the canonical JSON file with `current_subject="application"` + `application_root` resolved to the target.
- `_ISOLATION_FIX_SURFACE_FILES` updated: `.claude/session/work-subject.json` added (5 distinct paths total; was 4 in `-007`).
- `_prior_policy_for(...)` updated: `.claude/session/work-subject.json` returns `"unregistered"` (file is not in `managed-artifacts.toml`).
- T14 expectation updated: check #3's `prior_policy` is `"unregistered"` (was `"preserve"` in `-007` text).

This change does NOT alter the Slice 4 contract scope: same partition, same gate semantics, same receipt audit, same dispatcher contract. Only the fixer's target path moved.

### Disclosure 2 — Check #5 (`isolation:hooks-point-to-wrappers`) auto-fixability is conditional on failure mode

The fixer (`_fix_isolation_hook_paths`) uses `_compute_target_event_list` to refresh registry-managed hook entries to canonical wrapper-shaped form. This auto-fixes check #5 when the failure is in registry-managed entries. **It does NOT auto-fix check #5 when the failure is in adopter-owned non-wrapper hooks** (those need adopter judgment — the fixer cannot unilaterally delete adopter customizations).

T3's fixture intentionally avoids the unfixable failure mode (uses an empty `hooks` dict; no non-wrapper hooks). For adopters where check #5 fires on customizations, the fixer's outcome is `no-op` and the check stays warning post-migration.

**Possible Codex remediation paths** (flagged for review):
- Reclassify check #5 as needs-adopter-input (move from auto-fixable to needs-adopter-input partition; collapse to 4 auto-fixable + 4 needs-adopter-input). Pre-existing T3 + T11 + T13 + T14 would need updates.
- Make the fixer more aggressive: delete adopter-owned non-wrapper hooks from settings.json events that have managed registrations (destructive against adopter customizations; bounded by `--accept-migration` opt-in). New T-test covering the destructive-fix shape.
- Document the limitation as the current contract; add a CVR note that check #5 may stay warning post-migration if the failure is adopter-owned. Current implementation matches this option.

### Disclosure 3 — `enforce_isolation: bool = True` back-door added to `execute_upgrade`

The Slice 4 isolation gate fires inside `execute_upgrade()` for all callers. Pre-existing tests in `test_upgrade.py` and `test_preflight_checks.py` operate on test fixtures that don't model isolation-clean adopters; the new gate fires `IsolationMigrationRequiredError` against them.

Minimum-change adaptation: added `enforce_isolation: bool = True` keyword to `execute_upgrade()`. Default `True` preserves Slice 4 production behavior (CLI uses default). Pre-existing 14 test callsites updated to pass `enforce_isolation=False` to bypass the gate (testing the mechanical-executor path; Slice 4 gate path tested separately in `test_upgrade_isolation.py`).

**Possible Codex remediation path** (flagged for review):
- Architecture preference: extract the isolation gate into a CLI-only function `gate_isolation_for_upgrade(target, profile, product_root, accept_migration)` that the CLI calls BEFORE `execute_upgrade()`. Library function `execute_upgrade()` becomes pure mechanical-executor again; pre-existing tests call it without modification; `enforce_isolation` kwarg removed.

Current shape is the minimum-invasive adaptation. CVR documents the trade-off.

### Disclosure 4 — Estimated envelope exceeded

`-007` estimated ~200–300 LOC source + ~400–550 LOC tests. Actuals:
- Source: ~640 LOC delta (340 in upgrade.py for partition/dataclasses/exceptions/dispatchers; 50 in preflight.py; 70 in cli.py; 4 in rollback.py; ~180 in template/registry).
- Tests: ~620 LOC (test_upgrade_isolation.py; counts T1–T15 + helpers).

Over the LOC ceiling but within the GO'd scope's complexity envelope (no out-of-scope work; all LOC traces to a `-007` acceptance criterion or `-008` post-impl guidance). CVR can request envelope adjustment if needed.

## Acceptance Criteria Verification

Each criterion from `-007` §"Acceptance Criteria":

| # | Criterion | Verified by |
|---|---|---|
| 1 | Specification Links cover all governing artifacts | Codex `-008` GO §"Gate Checks" — PASS |
| 2 | Partition keys match live `ToolCheck.name` values | T11 — PASS |
| 3 | Partition exhaustive + no dead keys + disjoint | T11 + T13a — PASS |
| 4 | Work-list scrub absent from impl surface | `_PARTITION_*` + `_ISOLATION_FIXER_MAP` source — PASS |
| 5 | Template registry path is `groundtruth-kb/templates/...` | `managed-artifacts.toml` lines 859-868 — PASS |
| 6 | Decision 7 invariant (no rehearsal driver invocation) | T5 — PASS |
| 7 | Auto-fixer dispatch via typed `IsolationFixerResult` | T13b/c/d — PASS |
| 8 | `upgrade_policy` honor as bounded governed exception | T12a/b/c + T14 — PASS |
| 9 | Check #6 fixer targets `.claude/hooks/workstream-focus.py` | T15a/b — PASS |
| 10 | Estimated envelope | EXCEEDED — see Disclosure 4 |

## Verification Commands

For Codex re-execution (deterministic):

```bash
python -m pytest groundtruth-kb/tests/test_upgrade.py \
                  groundtruth-kb/tests/test_upgrade_isolation.py \
                  groundtruth-kb/tests/test_doctor_isolation.py \
                  groundtruth-kb/tests/test_preflight_checks.py \
                  -v --tb=short

python -m ruff check groundtruth-kb/src/groundtruth_kb/project/upgrade.py \
                     groundtruth-kb/src/groundtruth_kb/project/preflight.py \
                     groundtruth-kb/src/groundtruth_kb/project/rollback.py \
                     groundtruth-kb/src/groundtruth_kb/cli.py \
                     groundtruth-kb/tests/test_upgrade_isolation.py \
                     groundtruth-kb/tests/test_upgrade.py \
                     groundtruth-kb/tests/test_preflight_checks.py
```

Expected: `101 passed, 1 skipped, 1 warning` + `All checks passed!`.

## Decision Needed From Owner

**None at post-impl time.** All decisions previously settled per `DELIB-S328-ISOLATION-017-SLICE4-DECISIONS-1-3-7-OWNER-DIRECTIVE` + S328 preserve-override AskUserQuestion answer + `-008` Codex GO. Disclosures 2/3 above flag potential Codex remediations; if Codex requests revision, those become REVISED-4 (`-011`).

---

*© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
