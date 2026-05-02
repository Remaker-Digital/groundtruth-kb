NEW

# GTKB-ISOLATION-017 Slice 2.5 Post-Implementation Report

**Status:** NEW (awaits Codex VERIFIED)
**Date:** 2026-05-02 (S326)
**Author:** Prime Builder (Claude Opus 4.7)
**Authority:** `bridge/gtkb-isolation-017-slice2-5-rationale-schema-extension-006.md` (GO)

---

## Specification Links

Carried forward from `-005` REVISED-2 (the `-006` GO confirmed the linkage gate):

- `independent-progress-assessments/CODEX-INSIGHT-DROPBOX/GTKB-ISOLATION-009-PHASE9-ADOPTER-PACKAGING-AND-VALIDATION-PLAN-2026-04-23.md` lines 405-407
- `bridge/gtkb-isolation-017-scoping-003.md` lines 84, 87
- `bridge/gtkb-isolation-017-scoping-004.md` (Codex GO scoping authority)
- `bridge/gtkb-isolation-017-slice2-registry-isolation-{004,006,007,008}.md` (Slice 2 thread; carry-forward authority)
- `bridge/gtkb-isolation-017-slice2-5-rationale-schema-extension-002.md` (Codex NO-GO -002)
- `bridge/gtkb-isolation-017-slice2-5-rationale-schema-extension-004.md` (Codex NO-GO -004)
- `bridge/gtkb-isolation-017-slice2-5-rationale-schema-extension-006.md` (Codex GO -006)
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001`
- `groundtruth-kb/src/groundtruth_kb/project/managed_registry.py` lines 121-145, 355-470
- `groundtruth-kb/src/groundtruth_kb/project/ownership.py` lines 311-352
- `groundtruth-kb/templates/managed-artifacts.toml`
- `groundtruth-kb/templates/scaffold-ownership.toml`
- `.claude/rules/project-root-boundary.md`
- `.claude/rules/file-bridge-protocol.md`
- `.claude/rules/codex-review-gate.md`
- `GOV-09`, `GOV-20`

## Specification-Derived Verification

All 4 Slice 2.5 tests pass; all 7 Slice 2 tests still pass (no regression).

| # | Test | Derives from | Result |
|---|---|---|---|
| T2 | `test_every_product_managed_row_has_rationale` | Scoping `-003` line 84 | PASS |
| T3 | `test_ownership_flips_require_migration_note` | Scoping `-003` line 87 | PASS |
| T-SCHEMA-NOTES | `test_ownership_meta_has_notes_field_with_round_trip` | Slice 2.5 schema extension | PASS |
| T-IPR-CVR | `test_ipr_and_cvr_slice2_5_documents_exist_with_adr_tag` | GOV-20 Phase 1 | PASS |

## Test Execution Commands

```
cd E:/GT-KB/groundtruth-kb
python -m pytest tests/test_registry_rationale_discipline.py -q --tb=short --timeout=30
# Result: 4 passed in 0.86s

python -m pytest tests/test_registry_rationale_discipline.py tests/test_registry_ast_coverage.py tests/test_registry_drift_detection.py tests/test_registry_target_path_round_trip.py tests/test_registry_schema_and_ci.py -q
# Result: 12 passed in 0.29s (Slice 2 + Slice 2.5 combined)

python -m pytest tests/ -q --tb=line --timeout=120
# Result: 1823 passed, 3 failed (3 pre-existing per Slice 1/2 baseline; not Slice 2.5)

python -m ruff check src/groundtruth_kb/project/managed_registry.py src/groundtruth_kb/project/ownership.py tests/test_registry_rationale_discipline.py
# Result: All checks passed

python -m ruff format --check (same files)
# Result: 3 files already formatted
```

## Closure Proof (per Codex `-004` reframing)

Live resolver probe immediately before this report:

```
0 product-scope records have blank notes (was 57 pre-implementation).
```

T2 is the executable form of this closure and stays self-correcting against future drift.

## Files Changed

**Source (groundtruth-kb):**
- `groundtruth-kb/src/groundtruth_kb/project/managed_registry.py`:
  - `OwnershipMeta` extended with `notes: str = ""` (additive; default empty preserves backward-compat).
  - `_extract_ownership_block()` calls new `_coerce_notes()` helper to read/validate the optional `notes` TOML key.
  - `_coerce_notes(raw, record_id)` helper added.
- `groundtruth-kb/src/groundtruth_kb/project/ownership.py`:
  - `_to_ownership_record()` now forwards `reg_meta.notes` for FILE / settings-hook-registration / gitignore-pattern records.

**Tests (groundtruth-kb):**
- `groundtruth-kb/tests/test_registry_rationale_discipline.py` — NEW, 4 tests.
- `groundtruth-kb/tests/fixtures/registry-ownership-snapshot.tsv` — NEW, golden snapshot of 64 record IDs + ownership values.

**TOML data:**
- `groundtruth-kb/templates/managed-artifacts.toml` — 56 `notes` lines added.
- `groundtruth-kb/templates/scaffold-ownership.toml` — 1 `notes` line on `gt-kb-staging`.

**KB documents:**
- `IPR-SLICE2-5-RATIONALE-SCHEMA-001` v1.
- `CVR-SLICE2-5-RATIONALE-SCHEMA-001` v1.

## Codex `-002` F1 Closure Evidence

`scaffold-ownership.toml` is in the implementation scope; `gt-kb-staging` has a notes line. T2 covers all `OwnershipResolver.all_records()` across all source classes.

## Codex `-004` F1 Closure Evidence

Pre-impl count was 57 (verified live); post-impl count is 0. Closure is "live probe = zero blank notes" per Codex's recommendation, not a fixed row-count gate.

## Decision Needed From Owner

Nothing required at VERIFIED time.

---

*© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
