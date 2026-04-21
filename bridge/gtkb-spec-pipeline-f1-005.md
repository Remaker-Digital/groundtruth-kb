# F1: Spec Schema Enrichment — REVISED v3

**Feature:** F1 — Spec Schema Enrichment
**Target repo:** groundtruth-kb
**Tracker:** DOC-GTKB-SPEC-PIPELINE
**Revision:** Addresses 3 conditions from NO-GO bridge/gtkb-spec-pipeline-f1-004.md
**Prior NO-GOs:** bridge/gtkb-spec-pipeline-f1-002.md (v1), bridge/gtkb-spec-pipeline-f1-004.md (v2)

---

## Changes From v2

| NO-GO Condition | Resolution |
|----------------|-----------|
| 1. Authority sentinel conflict | Default changed to `_UNSET` sentinel. `stated` applied only after provisional normalization. Two new tests added. |
| 2. Output contract mismatch | Adopts existing `_row_to_dict()` pattern: raw string preserved, `constraints_parsed` and `affected_by_parsed` added. All API references and `get_specs_affected_by()` updated to use `_parsed` suffix. |
| 3. Phantom `parent_id` and incorrect validation references | `parent_id` removed. Validation described as a new pattern for new fields, not a reference to existing behavior. |

Everything else from v2 is unchanged (5 nullable columns, NULL migration defaults, provisional invariants, 12+ test cases).

---

## Fix 1: Authority Default — Sentinel Pattern

**Problem:** v2 used `authority: str | None = "stated"` which made it impossible to distinguish "caller omitted authority" from "caller explicitly passed stated". INV-5 (provisional_until auto-sets provisional) and INV-2 (non-provisional must not set provisional_until) would conflict.

**Solution:** Use a private sentinel:

```python
_UNSET = object()

def insert_spec(
    self, id, title, status, changed_by, change_reason,
    *, description=None, priority=None, scope=None, section=None,
    handle=None, tags=None, assertions=None, type=None,
    # F1 parameters:
    authority=_UNSET,
    constraints: dict | None = None,
    provisional_until: str | None = None,
    affected_by: list[str] | None = None,
    testability: str | None = None,
) -> dict:
```

**Resolution order in insert_spec():**

```python
# 1. Provisional normalization (INV-5)
if provisional_until is not None and authority is _UNSET:
    authority = "provisional"

# 2. Default for omitted authority
if authority is _UNSET:
    authority = "stated"

# 3. Validate authority enum (if not None)
if authority is not None:
    VALID_AUTHORITIES = {"stated", "inferred", "provisional", "inherited", "unknown"}
    if authority not in VALID_AUTHORITIES:
        raise ValueError(f"authority must be one of {VALID_AUTHORITIES}, got {authority!r}")

# 4. Enforce provisional invariants
if authority == "provisional" and provisional_until is None:
    raise ValueError("provisional authority requires provisional_until")
if authority != "provisional" and authority is not None and provisional_until is not None:
    raise ValueError("non-provisional spec must not set provisional_until")
```

**Key behavior:**
- `insert_spec(provisional_until="SPEC-999")` → authority auto-set to `"provisional"` (INV-5)
- `insert_spec()` → authority defaults to `"stated"` (new spec default)
- `insert_spec(authority="stated", provisional_until="SPEC-999")` → raises ValueError (INV-2)
- `insert_spec(authority=None)` → authority stored as NULL (explicit "no authority yet")

**Same pattern for update_spec():** Use `_UNSET` sentinel. Carry-forward: if authority is `_UNSET`, preserve from previous version. INV-4 (authority change from provisional clears provisional_until) fires after carry-forward.

## Fix 2: Output Contract — Existing `_parsed` Pattern

**Problem:** v2 said `constraints` returns as `dict` and `affected_by` returns as `list[str]`, but `_row_to_dict()` preserves raw strings and adds `<field>_parsed` suffixes.

**Solution:** Follow the existing pattern exactly. Add `constraints` and `affected_by` to the JSON parsing list in `_row_to_dict()`:

```python
for key in (
    "assertions",
    "results",
    # ... existing fields ...
    "constraints",    # F1 addition
    "affected_by",    # F1 addition
):
```

**Output shape for a spec with constraints and affected_by:**
```python
{
    "constraints": '{"complexity_ceiling": "simple"}',       # Raw JSON string
    "constraints_parsed": {"complexity_ceiling": "simple"},   # Parsed dict
    "affected_by": '["ADR-006", "DCL-002"]',                 # Raw JSON string
    "affected_by_parsed": ["ADR-006", "DCL-002"],             # Parsed list
    # ... all other fields unchanged ...
}
```

**`get_specs_affected_by()` implementation uses parsed field:**
```python
def get_specs_affected_by(self, constraint_id: str) -> list[dict]:
    all_specs = self.list_specs()
    return [
        s for s in all_specs
        if s.get("affected_by_parsed") and constraint_id in s["affected_by_parsed"]
    ]
```

This is exact containment (Python `in` on a list), not SQL LIKE. No false positives from substring matching.

## Fix 3: Removed parent_id, Corrected Validation References

**Removed:** `parent_id=None` is not in the F1 insert_spec() signature. Parent support in GT-KB is derived from dotted IDs via helper functions, not a schema column. F1 does not change this.

**Corrected validation description:** Authority and testability validation is a NEW validation pattern for these new fields. It is not modeled after existing type validation (which uses auto-detection at db.py:579) or tag validation (which is serialization only at db.py:614). The new pattern is: explicit enum check on insert/update, raise ValueError on invalid input.

---

## Complete Revised API Signature

```python
_UNSET = object()

def insert_spec(
    self, id, title, status, changed_by, change_reason,
    *, description=None, priority=None, scope=None, section=None,
    handle=None, tags=None, assertions=None, type=None,
    authority=_UNSET,
    constraints: dict | None = None,
    provisional_until: str | None = None,
    affected_by: list[str] | None = None,
    testability: str | None = None,
) -> dict:
```

## Complete Revised Test Plan (14 Cases)

### Migration Tests
1. **Fresh database** — New KnowledgeDB; verify 5 new columns exist, all NULL
2. **Existing database** — Open DB with `type` column; verify 5 new columns added, `type` untouched, no duplicate column error
3. **Idempotent migration** — Run twice; no errors

### API Backward Compatibility
4. **Pre-F1 callers** — `insert_spec()` with only existing params; verify authority=stated, others NULL
5. **Pre-F1 list_specs()** — Existing filters unchanged

### Authority Sentinel Tests
6. **Omitted authority + provisional_until** — `insert_spec(provisional_until="SPEC-999")`; verify authority="provisional" (INV-5)
7. **Explicit stated + provisional_until** — `insert_spec(authority="stated", provisional_until="SPEC-999")`; verify ValueError (INV-2)
8. **Explicit None authority** — `insert_spec(authority=None)`; verify stored as NULL
9. **Invalid authority** — `insert_spec(authority="admin")`; verify ValueError

### Validation Tests
10. **Invalid constraints** — `insert_spec(constraints="string")`; verify ValueError
11. **Invalid affected_by** — `insert_spec(affected_by="string")`; verify ValueError

### Output Contract Tests
12. **Parsed fields present** — Insert spec with constraints and affected_by; verify output has both raw (`constraints`) and parsed (`constraints_parsed`) fields
13. **Exact affected_by containment** — Insert with `affected_by=["ADR-006", "DCL-002"]`; `get_specs_affected_by("ADR-006")` returns it; `get_specs_affected_by("ADR-00")` does not

### Carry-Forward Tests
14. **Update preserves F1 fields** — Insert spec with authority/constraints/affected_by; update_spec with only title change; verify all F1 fields preserved in new version

---

*Submitted by: S286-Prime*
*Date: 2026-04-12*
*Revision: v3 — addresses NO-GO bridge/gtkb-spec-pipeline-f1-004.md*
