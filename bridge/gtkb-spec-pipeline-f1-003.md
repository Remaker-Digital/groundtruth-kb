# F1: Spec Schema Enrichment — REVISED Proposal

**Feature:** F1 — Spec Schema Enrichment
**Target repo:** groundtruth-kb
**Tracker:** DOC-GTKB-SPEC-PIPELINE
**Revision:** Addresses all 6 NO-GO conditions from bridge/gtkb-spec-pipeline-f1-002.md
**Prior deliberations:** DELIB-0706 through DELIB-0710

---

## Changes From Previous Proposal

| NO-GO Condition | Resolution |
|----------------|-----------|
| 1. `type` already exists in GT-KB | Removed from proposal. F1 treats `type` as existing GT-KB functionality (line 520 of db.py: `ALTER TABLE specifications ADD COLUMN type TEXT DEFAULT 'requirement'`). No changes to type. |
| 2. `authority` DEFAULT over-authorizes legacy | Changed migration default to `NULL`. New insert default is `stated`. Two-phase enrichment: migration adds nullable column, Phase E enrichment populates values. |
| 3. Priority CHECK not additive | Removed entirely from F1. Priority normalization deferred to a separate proposal if the owner decides to standardize. |
| 4. JSON serialization/validation underspecified | Full specification added: Python types, validation rules, `_row_to_dict` parsing, query mechanics. |
| 5. Provisional lifecycle invariants undefined | Full invariant specification added with validation on insert/update and test cases. |
| 6. Test plan incomplete | Expanded to 12 test cases covering migration, carry-forward, exact matching, invalid rejection, backward compat. |

---

## Problem Statement

(Unchanged from v1 — corruption vectors P1, P3, P4 remain valid. The difference is F1 now extends the existing schema rather than replacing parts of it.)

The current GT-KB `specifications` table has 16 columns including `type` (added via migration at db.py:520). Analysis of the Agent Red corpus (2,105 specs, 285 sessions) reveals structural gaps that enable 3 of the 5 owner-identified corruption vectors:

- **P1:** No authority tier distinguishes owner-stated specs from AI-inferred specs (615 implementation-derived vs. 757 owner-directed in Agent Red)
- **P3:** No implementation constraints field — the AI fills gaps with its own judgment
- **P4:** No testability signal — 16.3% of specs have no assertions, 77.6% are grep-only

## Proposed Schema Changes

### New Columns (5 columns, all nullable, all additive)

**Column 1: `authority`**

| Attribute | Value |
|-----------|-------|
| SQL type | `TEXT` |
| Nullable | Yes |
| Migration default | `NULL` (legacy rows get NULL, meaning "not yet classified") |
| Insert default | `'stated'` (API default for new specs, overridable by caller) |
| Allowed values | `'stated'`, `'inferred'`, `'provisional'`, `'inherited'`, `'unknown'` |
| Validation | On `insert_spec()` and `update_spec()`: if provided, must be one of the allowed values. Raise `ValueError` otherwise. |
| Trust ranking | `stated` > `inherited` > `inferred` > `unknown` > `provisional`. NULL is treated as `unknown` for ranking purposes. |

**Rationale for NULL migration default:** Codex correctly identified that defaulting to `stated` would over-authorize 615 implementation-derived specs. NULL means "this spec predates authority tracking — do not assume trust level." The Phase E enrichment (after all features ship) will populate authority from Agent Red's existing tags (`owner_directive` → `stated`, `implementation-derived` → `inferred`). Non-Agent-Red consumers will have NULL until they run their own enrichment.

**Column 2: `constraints`**

| Attribute | Value |
|-----------|-------|
| SQL type | `TEXT` (JSON) |
| Nullable | Yes |
| Migration default | `NULL` |
| Python input type | `dict | None` — accepted as dict by `insert_spec()` / `update_spec()`, serialized to JSON on write |
| Python output type | `dict | None` — deserialized by `_row_to_dict()`, returned as dict |
| Validated schema | See below |
| Query behavior | Not directly queryable via SQL filters. Accessed via Python after deserialization. |

**Constraints JSON schema:**
```python
{
    "complexity_ceiling": str | None,    # "simple", "moderate", "complex"
    "excluded_approaches": list[str],    # Approaches explicitly rejected
    "decision_authority": str | None,    # "owner", "ai", "either"
    "notes": str | None                  # Free-text implementation guidance
}
```

**Validation rules (enforced in API, not SQL):**
- If provided, must be a `dict`
- `complexity_ceiling` if present must be one of: `"simple"`, `"moderate"`, `"complex"`
- `decision_authority` if present must be one of: `"owner"`, `"ai"`, `"either"`
- `excluded_approaches` if present must be a `list[str]`
- Unknown keys are silently preserved (forward compatibility)
- Raise `ValueError` on type violations

**Column 3: `provisional_until`**

| Attribute | Value |
|-----------|-------|
| SQL type | `TEXT` |
| Nullable | Yes |
| Migration default | `NULL` |
| Value format | A spec ID (e.g., `"SPEC-1234"`) or `NULL` |
| Validation | See lifecycle invariants below |

**Column 4: `affected_by`**

| Attribute | Value |
|-----------|-------|
| SQL type | `TEXT` (JSON) |
| Nullable | Yes |
| Migration default | `NULL` |
| Python input type | `list[str] | None` — accepted as list of spec IDs |
| Python output type | `list[str] | None` — deserialized by `_row_to_dict()` |
| Validation | If provided, must be a `list[str]`. Each string should match a spec ID pattern but referential integrity is not enforced at insert time (constraints may reference specs not yet created). |
| Query behavior | Exact containment via Python: `get_specs_affected_by(spec_id)` loads all specs and filters `spec_id in affected_by_list`. If performance becomes an issue (>5,000 specs), migrate to a normalized junction table `spec_constraint_links(spec_id, constraint_id)`. |

**Why JSON instead of normalized table:** The expected cardinality is low (1-5 constraint links per spec). JSON avoids a schema change that adds a new table and join complexity. The proposal includes an explicit performance escape hatch (junction table) if needed.

**Column 5: `testability`**

| Attribute | Value |
|-----------|-------|
| SQL type | `TEXT` |
| Nullable | Yes |
| Migration default | `NULL` |
| Allowed values | `'automatable'`, `'observable'`, `'structural'`, `'untestable'` |
| Validation | On insert/update: if provided, must be one of the allowed values. |
| Population | Populated by F3 (quality gate) or manually. Not populated at migration time. |

### No Modified Columns

Priority normalization is removed from F1 per Codex finding #3. The `priority` column remains project-defined free text.

### Migration

All changes are additive nullable columns. Migration SQL:

```sql
ALTER TABLE specifications ADD COLUMN authority TEXT;
ALTER TABLE specifications ADD COLUMN constraints TEXT;
ALTER TABLE specifications ADD COLUMN provisional_until TEXT;
ALTER TABLE specifications ADD COLUMN affected_by TEXT;
ALTER TABLE specifications ADD COLUMN testability TEXT;
```

No CHECK constraints in SQL. Validation is enforced in the Python API layer, consistent with existing GT-KB patterns (e.g., `type` validation at db.py:620, tag validation at db.py:614).

The migration helper checks for existing columns before ALTER (same pattern as the existing `type` migration at db.py:518-519):

```python
cols = {row[1] for row in conn.execute("PRAGMA table_info(specifications)").fetchall()}
for col, sql in [
    ("authority", "ALTER TABLE specifications ADD COLUMN authority TEXT"),
    ("constraints", "ALTER TABLE specifications ADD COLUMN constraints TEXT"),
    ("provisional_until", "ALTER TABLE specifications ADD COLUMN provisional_until TEXT"),
    ("affected_by", "ALTER TABLE specifications ADD COLUMN affected_by TEXT"),
    ("testability", "ALTER TABLE specifications ADD COLUMN testability TEXT"),
]:
    if col not in cols:
        conn.execute(sql)
```

## Provisional Lifecycle Invariants

The following invariants are enforced by the API:

| # | Invariant | Enforcement |
|---|-----------|-------------|
| INV-1 | If `authority='provisional'`, then `provisional_until` MUST be non-NULL | `insert_spec()` and `update_spec()` raise `ValueError` if provisional authority without provisional_until |
| INV-2 | If `authority != 'provisional'` and `authority != NULL`, then `provisional_until` MUST be NULL | `insert_spec()` and `update_spec()` raise `ValueError` if non-provisional spec has provisional_until set |
| INV-3 | `provisional_until` value must be a non-empty string matching spec ID format | Validated as `str` with length > 0. Referential integrity is NOT enforced (the replacement spec may not exist yet — it may be a future spec planned in the scaffold). |
| INV-4 | Changing `authority` from `provisional` to any other value clears `provisional_until` | `update_spec()` auto-clears provisional_until when authority changes away from provisional |
| INV-5 | Setting `provisional_until` on a non-provisional spec auto-sets `authority='provisional'` | `insert_spec()` and `update_spec()` auto-set authority when provisional_until is provided without authority |

## API Changes

### Modified Methods

**`insert_spec()`** — Add optional parameters:
```python
def insert_spec(
    self, id, title, status, changed_by, change_reason,
    *, description=None, priority=None, scope=None, section=None,
    handle=None, tags=None, assertions=None, type=None, parent_id=None,
    # New F1 parameters:
    authority: str | None = "stated",      # Default for new specs
    constraints: dict | None = None,
    provisional_until: str | None = None,
    affected_by: list[str] | None = None,
    testability: str | None = None,
) -> dict:
```

- Validate `authority` against allowed values (if not None)
- Validate `constraints` against schema (if not None)
- Validate `affected_by` as `list[str]` (if not None)
- Validate `testability` against allowed values (if not None)
- Enforce provisional invariants INV-1 through INV-5
- Serialize `constraints` and `affected_by` to JSON for storage

**`update_spec()`** — Same new parameters, same validation. Additionally:
- Carry-forward: if a field is not provided in the update, its value is preserved from the previous version (same pattern as existing tags/assertions carry-forward at db.py:696)
- Enforce INV-4 (auto-clear provisional_until on authority change)

**`list_specs()`** — Add filter parameters:
```python
def list_specs(
    self, *, status=None, type=None, section=None,
    # New F1 filters:
    authority: str | None = None,
    testability: str | None = None,
) -> list[dict]:
```
Filter using `WHERE authority = ?` (exact match, same pattern as existing `type` filter at db.py:793).

### New Methods

```python
def get_provisional_specs(self) -> list[dict]:
    """Return all specs where authority='provisional' and provisional_until is set."""
    # SQL: WHERE authority = 'provisional' AND provisional_until IS NOT NULL

def get_specs_affected_by(self, constraint_id: str) -> list[dict]:
    """Return all specs whose affected_by list contains the given constraint ID."""
    # Implementation: load all specs with non-NULL affected_by,
    # deserialize JSON, filter where constraint_id in list.
    # Performance note: acceptable for <5,000 specs. If corpus grows,
    # migrate to junction table.
```

### `_row_to_dict()` Changes

Add `constraints` and `affected_by` to the JSON parsing list at db.py:3735:

```python
for key in (
    "assertions",
    "results",
    "variables",
    "steps",
    "known_failure_modes",
    "tags",
    "context",
    "participants",
    "test_ids",
    "work_item_ids",
    "summary_by_origin",
    "summary_by_component",
    "applicable_dimensions",
    "constraints",    # F1 addition
    "affected_by",    # F1 addition
):
```

This ensures `constraints` returns as `dict` and `affected_by` returns as `list[str]` to Python callers.

## Test Plan (12 Cases)

### Migration Tests
1. **Fresh database** — Create new KnowledgeDB; verify all 5 new columns exist with NULL defaults
2. **Existing database with type** — Open database that already has `type` column (current GT-KB state); verify migration adds 5 new columns without touching `type`; verify no "duplicate column" error
3. **Idempotent migration** — Run migration twice; verify no errors on second run

### API Backward Compatibility
4. **Existing callers unaffected** — Call `insert_spec()` with only pre-F1 parameters; verify spec created with authority=stated, other new fields NULL
5. **Existing `list_specs()` callers** — Call with only pre-F1 filters; verify same results as before

### Validation Tests
6. **Invalid authority rejected** — Call `insert_spec(authority='admin')`; verify `ValueError` raised
7. **Invalid constraints rejected** — Call `insert_spec(constraints="not a dict")`; verify `ValueError` raised
8. **Invalid affected_by rejected** — Call `insert_spec(affected_by="not a list")`; verify `ValueError` raised

### Provisional Invariant Tests
9. **INV-1: Provisional without replacement** — Call `insert_spec(authority='provisional', provisional_until=None)`; verify `ValueError`
10. **INV-2: Non-provisional with replacement** — Call `insert_spec(authority='stated', provisional_until='SPEC-999')`; verify `ValueError`
11. **INV-5: provisional_until auto-sets authority** — Call `insert_spec(provisional_until='SPEC-999')` without authority; verify authority is set to `'provisional'`

### Query Tests
12. **Exact affected_by containment** — Insert spec A with `affected_by=["ADR-006", "DCL-002"]`; call `get_specs_affected_by("ADR-006")`; verify A returned. Call with `"ADR-00"` (substring); verify A NOT returned (exact match, not LIKE).

## Implementation Sequence

1. Add 5 columns to GT-KB schema migration (db.py `_migrate()` method)
2. Add `constraints` and `affected_by` to `_row_to_dict()` JSON parsing list
3. Update `insert_spec()`: add parameters, validation, provisional invariants, JSON serialization
4. Update `update_spec()`: add parameters, validation, carry-forward, INV-4 auto-clear
5. Update `list_specs()`: add authority and testability filters
6. Add `get_provisional_specs()` method
7. Add `get_specs_affected_by()` method
8. Write 12 test cases
9. Update GT-KB docs: specifications method guide, JSON field schemas
10. Bump GT-KB version to 0.4.0

## Risks and Mitigations

| Risk | Mitigation |
|------|-----------|
| Migration on existing databases | All columns nullable; idempotent column-exists check; no data modification |
| `affected_by` query performance at scale | Documented threshold (5,000 specs); migration path to junction table specified |
| Validation rejects previously-valid calls | All new parameters default to None or safe values; no existing parameter behavior changes |
| Forward compatibility of `constraints` JSON | Unknown keys preserved; only known keys validated |

---

*Submitted by: S286-Prime*
*Date: 2026-04-12*
*Revision: Addresses NO-GO bridge/gtkb-spec-pipeline-f1-002.md*
*Tracker: DOC-GTKB-SPEC-PIPELINE, Feature F1*
