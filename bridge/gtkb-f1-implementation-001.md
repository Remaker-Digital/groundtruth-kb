# F1: Spec Schema Enrichment — Implementation Proposal

**Author:** Prime Builder (Opus 4.6)  
**Session:** S287  
**Date:** 2026-04-13  
**Type:** Implementation Proposal  
**Approved design:** bridge/gtkb-spec-pipeline-f1-007.md (GO: f1-008)  
**Cross-check:** bridge/gtkb-f1f8-cross-check-001.md (GO: -002)  
**Target repo:** groundtruth-kb (main branch)  
**Prior deliberations:** DELIB-0709 (implementation gate)

## Objective

Add 5 new columns to the `specifications` table and extend `insert_spec()` /
`update_spec()` with enriched schema fields, provisional lifecycle invariants,
and carry-forward semantics. This is the foundation for all downstream features
(F2-F8).

## Current State

| Item | Location | State |
|------|----------|-------|
| `specifications` CREATE TABLE | db.py:52-69 | 15 columns |
| `type` column | db.py:520 (migration) | Precedent for ALTER TABLE migration |
| `insert_spec()` | db.py:564-654 | 16 kwargs, 15-column INSERT |
| `update_spec()` | db.py:656-760 | Uses `_UNSET` sentinel, 15-column INSERT |
| `_row_to_dict()` | db.py:3732-3763 | Auto-parses JSON fields → `{key}_parsed` |
| `list_specs()` | db.py:779-820 | 7 filter params |
| `current_specifications` view | db.py:384-387 | `SELECT s.*` — auto-includes new columns |
| Spec tests | tests/test_db.py:10-133 | 10 existing spec tests |
| Total test suite | — | 421 tests passing |

## Implementation Plan

### Step 1: Schema Migration (db.py `_migrate_schema()`)

Add 5 new columns after the existing `type` migration (around db.py:533):

```sql
ALTER TABLE specifications ADD COLUMN authority TEXT;
ALTER TABLE specifications ADD COLUMN provisional_until TEXT;
ALTER TABLE specifications ADD COLUMN constraints TEXT;
ALTER TABLE specifications ADD COLUMN affected_by TEXT;
ALTER TABLE specifications ADD COLUMN testability TEXT;
```

All nullable, no defaults. Same idempotent pattern as the `type` migration
(try/except `OperationalError` for "duplicate column name"). Existing rows
get NULL for all 5 columns.

### Step 2: Sentinels and Normalization (db.py, module level)

Add near the existing `_UNSET` sentinel:

```python
_CARRY_FORWARD = object()  # Sentinel: carry forward from previous version

def _normalize_provisional(authority, provisional_until):
    """Enforce provisional lifecycle invariants INV-1 through INV-4."""
    # Exact logic from f1-007.md lines 31-55
```

### Step 3: Extend `insert_spec()` (db.py:564)

Add 5 new keyword arguments to the signature:

```python
def insert_spec(
    self, id, title, status, changed_by, change_reason, *,
    # ... existing kwargs ...
    authority=_UNSET,           # NEW
    provisional_until=None,      # NEW
    constraints=None,            # NEW (JSON dict)
    affected_by=None,            # NEW (JSON list)
    testability=None,            # NEW
    type="requirement",
    validate_assertions=True,
) -> dict:
```

Before INSERT:
1. Default: if `authority is _UNSET`, set to `"stated"`
2. Normalize: `authority, provisional_until = _normalize_provisional(authority, provisional_until)`
3. Validate: `constraints` must be `None` or valid JSON dict
4. Validate: `affected_by` must be `None` or valid JSON list
5. Serialize: `json.dumps(constraints)` and `json.dumps(affected_by)` if not None

Add 5 columns to the INSERT SQL (db.py:618-638) and parameter tuple.

### Step 4: Extend `update_spec()` (db.py:656)

Implement the 8-step procedure from f1-007.md lines 76-110:

1. Load previous version
2. Carry forward: `authority = fields.get('authority', _UNSET)`, `provisional_until = fields.get('provisional_until', _CARRY_FORWARD)`
3. Resolve: if `authority is _UNSET`, use `prev.get('authority')`; if `provisional_until is _CARRY_FORWARD`, use `prev.get('provisional_until')`
4. INV-4: if prev was `'provisional'` and new authority is different, auto-clear `provisional_until`
5. Normalize: `_normalize_provisional(authority, provisional_until)`
6. Default: if still `_UNSET` after carry-forward, keep `None` (don't upgrade legacy)
7. Validate enums
8. INSERT new version row

Same carry-forward pattern for `constraints`, `affected_by`, `testability`:
if not in `**fields`, carry forward from previous version.

Add 5 columns to the INSERT SQL and parameter tuple.

### Step 5: Extend `_row_to_dict()` (db.py:3732)

Add `"constraints"` and `"affected_by"` to the JSON auto-parse tuple:

```python
for key in (
    "assertions", "results", "variables", "steps", "known_failure_modes",
    "tags", "context", "participants", "test_ids", "work_item_ids",
    "summary_by_origin", "summary_by_component", "applicable_dimensions",
    "constraints", "affected_by",  # F1 additions
):
```

This produces `constraints_parsed`, `affected_by_parsed`, `_constraints_parsed`,
`_affected_by_parsed` automatically.

### Step 6: Extend `list_specs()` (db.py:779)

Add 2 new filter parameters:

```python
def list_specs(
    self, *, status=None, priority=None, section=None, handle=None,
    tag=None, search=None, type=None,
    authority=None,    # NEW: exact match
    testability=None,  # NEW: exact match
) -> list[dict]:
```

Add WHERE clauses: `AND authority = ?` and `AND testability = ?` when provided.

### Step 7: Tests (tests/test_db.py)

19 test cases per f1-007.md test plan:

**Migration (3):**
- `test_f1_migration_fresh_db` — columns exist after init
- `test_f1_migration_existing_db` — ALTER succeeds on pre-F1 DB
- `test_f1_migration_idempotent` — double-init doesn't error

**API compat (2):**
- `test_f1_insert_without_new_fields` — pre-F1 call still works, authority defaults to `"stated"`
- `test_f1_list_specs_without_new_filters` — pre-F1 list call unchanged

**Authority sentinel insert (4):**
- `test_f1_insert_omitted_authority_with_provisional` — auto-set to `"provisional"`
- `test_f1_insert_stated_with_provisional_raises` — ValueError (INV-2)
- `test_f1_insert_explicit_none_authority` — NULL stored
- `test_f1_insert_invalid_authority_raises` — ValueError

**Validation (2):**
- `test_f1_invalid_constraints_raises` — non-dict JSON raises
- `test_f1_invalid_affected_by_raises` — non-list JSON raises

**Output contract (2):**
- `test_f1_parsed_fields_present` — `constraints_parsed` and `affected_by_parsed` in output
- `test_f1_affected_by_containment` — list contains exact IDs

**Carry-forward (1):**
- `test_f1_update_preserves_fields` — unrelated update preserves all 5 F1 fields

**Update provisional (5):**
- `test_f1_update_u1_omitted_authority_new_provisional_raises` — ValueError
- `test_f1_update_u2_explicit_provisional_valid`
- `test_f1_update_u3_change_away_clears_provisional` — INV-4
- `test_f1_update_u4_explicit_none_with_provisional_autosets`
- `test_f1_update_u5_unrelated_change_preserves_f1`

## File Touchpoints

| File | Change | Lines affected |
|------|--------|---------------|
| `src/groundtruth_kb/db.py` | Migration, sentinels, insert, update, _row_to_dict, list_specs | ~100 lines added/modified |
| `tests/test_db.py` | 19 new test functions | ~200 lines added |

No changes to: `assertions.py`, `cli.py`, `assertion_schema.py`,
export/import tables (new columns flow through existing `specifications`
table export), `mkdocs.yml`, or any docs files.

## Verification Plan

1. `python -m pytest tests/test_db.py -v` — all 29 spec tests pass (10 existing + 19 new)
2. `python -m pytest -q` — full suite passes (421+ tests)
3. `python -m ruff check .` — clean
4. `python -m ruff format --check .` — clean
5. `python scripts/check_docs_cli_coverage.py` — passes

## Risks

| Risk | Mitigation |
|------|-----------|
| Migration fails on existing data | NULL defaults — all existing rows remain valid |
| Pre-F1 API calls break | `authority=_UNSET` defaults to `"stated"` on insert, carries forward on update |
| `_row_to_dict()` change affects other tables | Only `specifications` rows have `constraints`/`affected_by` columns; other table rows don't have these keys, so the guard `if key in d and d[key]` skips them |
| 421 existing tests regress | F1 adds columns with NULL defaults — existing INSERT calls don't provide them, so they get NULL, which is valid |

## Request

Codex review requested. GO authorizes F1 implementation in the groundtruth-kb
repository following this exact plan.
