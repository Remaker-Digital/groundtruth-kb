# F1: Spec Schema Enrichment — REVISED v4

**Feature:** F1 — Spec Schema Enrichment
**Target repo:** groundtruth-kb
**Tracker:** DOC-GTKB-SPEC-PIPELINE
**Revision:** Addresses 2 conditions from NO-GO bridge/gtkb-spec-pipeline-f1-006.md
**Prior NO-GOs:** f1-002 (v1), f1-004 (v2), f1-006 (v3)

---

## Changes From v3

| NO-GO Condition | Resolution |
|----------------|-----------|
| 1. `authority=None` + `provisional_until` bypasses validation | New rule: if `provisional_until` is provided, authority is ALWAYS normalized to `"provisional"` regardless of what the caller passed — including explicit `None`. The only way to set `provisional_until` without getting `authority="provisional"` is to pass a different valid authority string, which raises ValueError per INV-2. |
| 2. `update_spec()` normalization order unspecified | Full pseudocode provided for `update_spec()` with 5 concrete test cases covering add, clear, conflict, and carry-forward scenarios. |

Everything else from v3 is unchanged (5 columns, NULL migration defaults, `_parsed` output pattern, 14 base tests).

---

## Fix 1: Closed Provisional Loophole

**New normalization rule for both `insert_spec()` and `update_spec()`:**

If `provisional_until` is non-None, authority MUST be `"provisional"`. Period. No exceptions.

```python
# Unified normalization logic (used by both insert and update):

def _normalize_provisional(authority, provisional_until):
    """Returns (authority, provisional_until) after normalization.
    
    Rules:
    1. provisional_until present → authority MUST be 'provisional'
       - If authority is _UNSET or None: auto-set to 'provisional'
       - If authority is 'provisional': valid, no change
       - If authority is anything else: ValueError (INV-2)
    2. provisional_until absent → authority MUST NOT be 'provisional'
       - If authority is 'provisional': ValueError (INV-1)
       - All other values: valid
    """
    if provisional_until is not None:
        if authority is _UNSET or authority is None:
            authority = "provisional"
        elif authority != "provisional":
            raise ValueError(
                f"provisional_until requires authority='provisional', got {authority!r}"
            )
    else:
        if authority is not None and authority is not _UNSET and authority == "provisional":
            raise ValueError(
                "authority='provisional' requires provisional_until to be set"
            )
    return authority, provisional_until
```

**Key behavior table:**

| authority param | provisional_until param | Result |
|----------------|------------------------|--------|
| `_UNSET` (omitted) | `None` (omitted) | authority=`"stated"`, provisional_until=None |
| `_UNSET` (omitted) | `"SPEC-999"` | authority=`"provisional"`, provisional_until=`"SPEC-999"` |
| `None` (explicit) | `None` (omitted) | authority=NULL, provisional_until=None |
| `None` (explicit) | `"SPEC-999"` | authority=`"provisional"`, provisional_until=`"SPEC-999"` ← **v4 fix** |
| `"stated"` | `None` | authority=`"stated"`, provisional_until=None |
| `"stated"` | `"SPEC-999"` | **ValueError** (INV-2) |
| `"provisional"` | `None` | **ValueError** (INV-1) |
| `"provisional"` | `"SPEC-999"` | authority=`"provisional"`, provisional_until=`"SPEC-999"` |

Row 4 is the v4 fix: `authority=None` + `provisional_until` now auto-sets provisional instead of bypassing validation.

## Fix 2: Explicit `update_spec()` Normalization Order

```python
def update_spec(self, id, changed_by, change_reason, **fields):
    # Step 1: Load previous version
    prev = self.get_spec(id)
    
    # Step 2: Carry forward — for each field, if not provided, preserve previous value
    # Use _UNSET sentinel for authority (same as insert)
    authority = fields.get('authority', _UNSET)
    provisional_until = fields.get('provisional_until', _CARRY_FORWARD)
    
    # Step 3: Resolve carry-forward BEFORE normalization
    if authority is _UNSET:
        authority = prev.get('authority')  # Carry forward from previous version
    if provisional_until is _CARRY_FORWARD:
        provisional_until = prev.get('provisional_until')
    
    # Step 4: Apply INV-4 — changing authority AWAY from provisional clears provisional_until
    prev_authority = prev.get('authority')
    if prev_authority == 'provisional' and authority != 'provisional' and authority is not None:
        provisional_until = None  # Auto-clear
    
    # Step 5: Normalize provisional lifecycle (same function as insert)
    authority, provisional_until = _normalize_provisional(authority, provisional_until)
    
    # Step 6: Apply default for omitted authority (only if still _UNSET after carry-forward)
    # This case only happens if previous version had NULL authority and caller didn't specify
    if authority is _UNSET:
        authority = None  # Keep NULL — don't upgrade legacy rows to 'stated'
    
    # Step 7: Validate enums
    if authority is not None:
        _validate_authority(authority)
    
    # Step 8: Insert new version row with resolved values
    ...
```

**Key difference from `insert_spec()`:** On update, omitted authority carries forward from the previous version rather than defaulting to `"stated"`. This prevents legacy specs from being silently promoted to owner-stated authority when an unrelated field is updated.

## Complete `update_spec()` Test Cases (5 new cases)

### Update Case U1: Omitted authority + new provisional_until
```python
# Spec exists with authority='stated'
kdb.update_spec(id="S1", changed_by="test", change_reason="test",
                provisional_until="SPEC-999")
# Expected: authority carried forward as 'stated'
# provisional_until='SPEC-999' + authority='stated' → ValueError (INV-2)
# The caller must explicitly set authority='provisional' to make it provisional.
```

### Update Case U2: Explicit provisional + new provisional_until
```python
kdb.update_spec(id="S1", changed_by="test", change_reason="test",
                authority="provisional", provisional_until="SPEC-999")
# Expected: authority='provisional', provisional_until='SPEC-999' — valid
```

### Update Case U3: Change away from provisional (INV-4)
```python
# Spec exists with authority='provisional', provisional_until='SPEC-999'
kdb.update_spec(id="S1", changed_by="test", change_reason="test",
                authority="stated")
# Expected: authority='stated', provisional_until=None (auto-cleared by INV-4)
```

### Update Case U4: Explicit authority=None + new provisional_until
```python
kdb.update_spec(id="S1", changed_by="test", change_reason="test",
                authority=None, provisional_until="SPEC-999")
# Expected: authority='provisional' (auto-set, same as insert v4 fix)
```

### Update Case U5: Unrelated field change preserves F1 fields
```python
# Spec exists with authority='inferred', constraints={"complexity_ceiling": "simple"},
#   affected_by=["ADR-006"], testability='automatable'
kdb.update_spec(id="S1", changed_by="test", change_reason="test",
                title="Updated title only")
# Expected: all F1 fields preserved from previous version
```

## Complete Test Plan (19 cases)

**Migration (3):** Fresh DB, existing DB with type, idempotent
**API compat (2):** Pre-F1 insert, pre-F1 list_specs
**Authority sentinel insert (4):** Omitted+provisional, explicit stated+provisional (ValueError), explicit None (NULL stored), invalid authority (ValueError)
**Validation (2):** Invalid constraints, invalid affected_by
**Output contract (2):** _parsed fields present, exact affected_by containment
**Carry-forward (1):** Update preserves F1 fields
**Update provisional (5):** U1-U5 above

---

*Submitted by: S286-Prime*
*Revision: v4 — addresses NO-GO bridge/gtkb-spec-pipeline-f1-006.md*
