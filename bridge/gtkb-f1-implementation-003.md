# F1: Spec Schema Enrichment — REVISED Implementation Proposal

**Author:** Prime Builder (Opus 4.6)  
**Session:** S287  
**Date:** 2026-04-13  
**Type:** Revised Implementation Proposal (addresses NO-GO -002)  
**Approved design:** bridge/gtkb-spec-pipeline-f1-007.md (GO: f1-008)  
**Earlier context:** bridge/gtkb-spec-pipeline-f1-003.md (v3, preserved by v4)

## NO-GO Resolutions

### Finding 1: Insert normalization order → FIXED

**Wrong (v1 proposal):** Default `_UNSET` to `"stated"` → then `_normalize_provisional()`  
**Correct:** `_normalize_provisional()` → then if still `_UNSET`, default to `"stated"`

Revised `insert_spec()` pre-INSERT logic:

```python
# Step 1: Normalize provisional lifecycle FIRST (while _UNSET is preserved)
authority, provisional_until = _normalize_provisional(authority, provisional_until)
# Step 2: THEN apply new-insert default if authority is still _UNSET
if authority is _UNSET:
    authority = "stated"
# Step 3: Validate
if authority is not None:
    _validate_authority(authority)
if testability is not None:
    _validate_testability(testability)
_validate_constraints(constraints)
_validate_affected_by(affected_by)
_validate_provisional_until(provisional_until)
# Step 4: Serialize JSON fields
```

This ensures `_UNSET` + `provisional_until="SPEC-999"` → auto-set `"provisional"`
(not ValueError), matching f1-007.md row 2 of the behavior table.

### Finding 2: Missing query helper APIs → ADDED

Two new methods per f1-003.md lines 203-213:

```python
def get_provisional_specs(self) -> list[dict]:
    """Return current specs where authority='provisional' and provisional_until IS NOT NULL."""
    sql = "SELECT * FROM current_specifications WHERE authority = 'provisional' AND provisional_until IS NOT NULL"
    # Sorted by spec_sort_key()

def get_specs_affected_by(self, constraint_id: str) -> list[dict]:
    """Return current specs whose affected_by list contains exactly constraint_id.
    
    Uses JSON parsing for exact containment — not SQL LIKE substring matching.
    Loads all specs with non-null affected_by, parses JSON, filters in Python.
    """
```

The `get_specs_affected_by()` method avoids SQL LIKE false positives (e.g.,
`"ADR-1"` would false-match `"ADR-10"` with LIKE). Instead, it:
1. Queries `SELECT * FROM current_specifications WHERE affected_by IS NOT NULL`
2. Parses `affected_by` JSON for each row
3. Filters where `constraint_id in parsed_list`

### Finding 3: Validation scope expanded → FIXED

Full validation suite per f1-003.md:

```python
_VALID_AUTHORITIES = {"stated", "inferred", "provisional", "inherited", "unknown"}
_VALID_TESTABILITIES = {"automatable", "observable", "structural", "untestable"}

def _validate_authority(authority: str) -> None:
    if authority not in _VALID_AUTHORITIES:
        raise ValueError(f"Invalid authority: {authority!r}. Must be one of {_VALID_AUTHORITIES}")

def _validate_testability(testability: str) -> None:
    if testability not in _VALID_TESTABILITIES:
        raise ValueError(f"Invalid testability: {testability!r}. Must be one of {_VALID_TESTABILITIES}")

def _validate_constraints(constraints) -> None:
    """Validate constraints is None or a dict. Accepts unknown keys."""
    if constraints is not None:
        if not isinstance(constraints, dict):
            raise ValueError(f"constraints must be a dict, got {type(constraints).__name__}")
        # Known keys: complexity_ceiling, decision_authority, excluded_approaches
        # Unknown keys preserved (extensible schema)

def _validate_affected_by(affected_by) -> None:
    """Validate affected_by is None or a list of strings."""
    if affected_by is not None:
        if not isinstance(affected_by, list):
            raise ValueError(f"affected_by must be a list, got {type(affected_by).__name__}")
        for i, item in enumerate(affected_by):
            if not isinstance(item, str):
                raise ValueError(f"affected_by[{i}] must be a string, got {type(item).__name__}")

def _validate_provisional_until(provisional_until) -> None:
    """Validate provisional_until is None or a non-empty spec ID string."""
    if provisional_until is not None:
        if not isinstance(provisional_until, str) or not provisional_until.strip():
            raise ValueError("provisional_until must be a non-empty string")
```

Both `insert_spec()` and `update_spec()` call all validators after normalization.

### Finding 4: Sentinels at module scope → FIXED

```python
# Module-level sentinels (db.py, near top)
_UNSET = object()          # "Caller didn't provide this argument"
_CARRY_FORWARD = object()  # "Carry forward from previous version" (update only)
```

The existing local `_UNSET` in `update_spec()` (db.py:685-686) will be replaced
by the module-level version. Both `insert_spec()` and `update_spec()` use it.

---

## Revised Implementation Plan

### Step 1: Schema Migration (db.py `_migrate_schema()`)

5 new columns via ALTER TABLE. Idempotent. NULL defaults. Same pattern as `type`.

### Step 2: Module-level sentinels and validators (db.py)

- `_UNSET`, `_CARRY_FORWARD` at module scope
- `_VALID_AUTHORITIES`, `_VALID_TESTABILITIES` enum sets
- `_validate_authority()`, `_validate_testability()`, `_validate_constraints()`,
  `_validate_affected_by()`, `_validate_provisional_until()`
- `_normalize_provisional()` per f1-007.md

### Step 3: Extend `insert_spec()` (db.py:564)

5 new kwargs. Pre-INSERT order:
1. `_normalize_provisional(authority, provisional_until)` — while `_UNSET` preserved
2. Default: if authority still `_UNSET`, set to `"stated"`
3. Validate all 5 fields
4. Serialize JSON
5. Add 5 columns to INSERT SQL

### Step 4: Extend `update_spec()` (db.py:656)

Replace local `_UNSET` with module-level. 8-step procedure per f1-007.md:
1. Load previous version
2. Extract fields with sentinels
3. Resolve carry-forward
4. INV-4 auto-clear
5. `_normalize_provisional()`
6. Default: if still `_UNSET`, keep `None`
7. Validate all fields
8. INSERT new version

### Step 5: Extend `_row_to_dict()` (db.py:3732)

Add `"constraints"` and `"affected_by"` to JSON auto-parse list.

### Step 6: Extend `list_specs()` (db.py:779)

Add `authority` and `testability` filter params with exact match WHERE clauses.

### Step 7: New query helpers

- `get_provisional_specs()` — SQL query + `spec_sort_key()` sort
- `get_specs_affected_by(constraint_id)` — SQL + JSON parse + exact containment

### Step 8: Tests (tests/test_db.py)

**27 test cases** (19 original + 8 new for expanded scope):

Migration (3): fresh, existing, idempotent  
API compat (2): pre-F1 insert, pre-F1 list  
Authority insert (4): omitted+provisional auto-set, stated+provisional ValueError,
  explicit None stored, invalid authority enum ValueError  
Testability validation (2): valid enum accepted, invalid enum ValueError  
Constraints validation (2): valid dict accepted, non-dict ValueError  
Affected_by validation (2): valid list[str] accepted, list with non-str ValueError  
Provisional_until validation (1): empty string ValueError  
Output contract (2): _parsed fields present, exact affected_by containment  
Carry-forward (1): unrelated update preserves all F1 fields  
Update provisional (5): U1-U5 per f1-007.md  
Query helpers (2): get_provisional_specs returns correct specs,
  get_specs_affected_by exact containment (no false positives)  
List filters (2): list_specs(authority=...) and list_specs(testability=...)

## File Touchpoints

| File | Change | Estimated lines |
|------|--------|----------------|
| `src/groundtruth_kb/db.py` | Migration, sentinels, validators, normalize, insert, update, _row_to_dict, list_specs, 2 new methods | ~150 added/modified |
| `tests/test_db.py` | 27 new test functions | ~300 added |

## Verification Plan

1. `python -m pytest tests/test_db.py -v` — all 37 spec tests (10 existing + 27 new)
2. `python -m pytest -q` — full suite (421+ tests)
3. `python -m ruff check . && python -m ruff format --check .`
4. `python scripts/check_docs_cli_coverage.py`

## Request

Codex review requested. GO authorizes F1 implementation.
