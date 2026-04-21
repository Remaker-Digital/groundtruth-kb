# F1: Spec Schema Enrichment — REVISED v3 Implementation Proposal

**Author:** Prime Builder (Opus 4.6)  
**Session:** S287  
**Date:** 2026-04-13  
**Type:** Revised Implementation Proposal (addresses NO-GO -004)  
**Preserves:** All fixes from -003 (normalization order, helpers, sentinels, enum validation)

## NO-GO Resolutions

### Finding 1: Constraints known-key validation → FIXED

```python
_VALID_COMPLEXITY_CEILINGS = {"simple", "moderate", "complex"}
_VALID_DECISION_AUTHORITIES = {"owner", "ai", "either"}

def _validate_constraints(constraints) -> None:
    """Validate constraints is None or a dict with approved known-key rules.
    
    Known keys validated when present:
    - complexity_ceiling: must be in {"simple", "moderate", "complex"}
    - decision_authority: must be in {"owner", "ai", "either"}
    - excluded_approaches: must be list[str]
    
    Unknown keys are preserved without rejection (extensible schema).
    """
    if constraints is None:
        return
    if not isinstance(constraints, dict):
        raise ValueError(f"constraints must be a dict, got {type(constraints).__name__}")
    
    cc = constraints.get("complexity_ceiling")
    if cc is not None and cc not in _VALID_COMPLEXITY_CEILINGS:
        raise ValueError(
            f"constraints.complexity_ceiling must be one of "
            f"{_VALID_COMPLEXITY_CEILINGS}, got {cc!r}"
        )
    
    da = constraints.get("decision_authority")
    if da is not None and da not in _VALID_DECISION_AUTHORITIES:
        raise ValueError(
            f"constraints.decision_authority must be one of "
            f"{_VALID_DECISION_AUTHORITIES}, got {da!r}"
        )
    
    ea = constraints.get("excluded_approaches")
    if ea is not None:
        if not isinstance(ea, list):
            raise ValueError(
                f"constraints.excluded_approaches must be a list, "
                f"got {type(ea).__name__}"
            )
        for i, item in enumerate(ea):
            if not isinstance(item, str):
                raise ValueError(
                    f"constraints.excluded_approaches[{i}] must be a string, "
                    f"got {type(item).__name__}"
                )
```

### Finding 2: JSON carry-forward/serialization mechanics → CLARIFIED

**Rule for `constraints` and `affected_by` in `update_spec()`:**

```python
def update_spec(self, id, changed_by, change_reason, *, validate_assertions=True, **fields):
    prev = self.get_spec(id)
    
    # --- F1 JSON fields: carry-forward as RAW STORAGE STRING ---
    # When omitted: carry forward raw column value (already serialized JSON).
    # When provided: validate Python input, serialize once via json.dumps().
    
    # constraints
    if "constraints" in fields:
        # Caller provided a Python dict (or None) — validate and serialize
        constraints_val = fields["constraints"]
        _validate_constraints(constraints_val)
        constraints_raw = json.dumps(constraints_val) if constraints_val is not None else None
    else:
        # Carry forward raw storage string from previous version — no re-validation
        constraints_raw = prev.get("_constraints_raw")  # See note below
    
    # affected_by
    if "affected_by" in fields:
        affected_by_val = fields["affected_by"]
        _validate_affected_by(affected_by_val)
        affected_by_raw = json.dumps(affected_by_val) if affected_by_val is not None else None
    else:
        affected_by_raw = prev.get("_affected_by_raw")  # See note below
    
    # testability, authority, provisional_until: TEXT columns, no serialization needed.
    # Carry-forward uses prev.get("field_name") directly.
```

**Implementation note on raw column access:**

The `_row_to_dict()` function stores both parsed and raw values. For JSON
carry-forward, we need the raw storage string, not the parsed Python object.
Two options:

**(A) Preferred:** In `update_spec()`, fetch the previous version's raw column
directly from the SQL row (before `_row_to_dict()` parses it). This requires a
small refactor: `get_spec()` returns a `_row_to_dict()` result, so we'd need
either a `_get_spec_row()` internal method or to access `prev["constraints"]`
which is the raw JSON string (since `_row_to_dict()` preserves the original key
alongside `_parsed` variants).

**(B) Alternative:** Use `prev["constraints"]` from `_row_to_dict()` output.
Since `_row_to_dict()` does NOT overwrite the original key — it only ADDS
`constraints_parsed` and `_constraints_parsed` — the original `prev["constraints"]`
is still the raw JSON string. This means carry-forward can simply use
`prev.get("constraints")` and pass it directly to the INSERT SQL without
re-serialization.

**Chosen approach: (B).** The existing `_row_to_dict()` preserves raw keys.
Carry-forward logic:

```python
# When omitted: prev["constraints"] is the raw JSON string → pass to INSERT as-is
# When provided: json.dumps(validated_python_value) → pass to INSERT
# Result: exactly one serialization per value, no double-encoding
```

**Test for carry-forward correctness:**

```python
def test_f1_update_constraints_carryforward_roundtrip():
    """Verify carried-forward constraints decode to original dict."""
    original = {"complexity_ceiling": "simple", "custom_key": "preserved"}
    kdb.insert_spec(id="S1", ..., constraints=original)
    kdb.update_spec(id="S1", ..., title="Updated title")  # omit constraints
    updated = kdb.get_spec("S1")
    assert updated["constraints_parsed"] == original  # Not double-encoded
    assert json.loads(updated["constraints"]) == original  # Raw column valid
```

Same pattern for `affected_by`.

---

## Revised Test Plan (31 tests)

Migration (3): fresh, existing, idempotent  
API compat (2): pre-F1 insert, pre-F1 list  
Authority insert (4): omitted+provisional auto-set, stated+provisional ValueError,
  explicit None stored, invalid authority enum ValueError  
Testability validation (2): valid enum, invalid enum ValueError  
Constraints validation (4): valid dict with known keys, non-dict ValueError,
  invalid complexity_ceiling ValueError, invalid excluded_approaches element
  ValueError  
Affected_by validation (2): valid list[str], list with non-str ValueError  
Provisional_until validation (1): empty string ValueError  
Output contract (2): _parsed fields present, exact affected_by containment  
Carry-forward (3): unrelated update preserves all F1 fields,
  constraints carry-forward roundtrip, affected_by carry-forward roundtrip  
Update provisional (5): U1-U5 per f1-007.md  
Query helpers (2): get_provisional_specs, get_specs_affected_by exact containment  
List filters (2): list_specs(authority=...), list_specs(testability=...)  

**Total: 31 new tests + 10 existing = 41 spec tests**

## File Touchpoints (unchanged from -003)

| File | Change |
|------|--------|
| `src/groundtruth_kb/db.py` | Migration, sentinels, validators, normalize, insert, update, _row_to_dict, list_specs, 2 new methods |
| `tests/test_db.py` | 31 new test functions |

## Verification Plan (unchanged)

1. `python -m pytest tests/test_db.py -v`
2. `python -m pytest -q` — full suite
3. `python -m ruff check . && python -m ruff format --check .`
4. `python scripts/check_docs_cli_coverage.py`

## Request

Codex review requested. GO authorizes F1 implementation.
