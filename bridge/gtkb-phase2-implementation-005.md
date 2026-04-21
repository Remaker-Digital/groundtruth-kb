# Phase 2: F3 + F2-A + F4-A — REVISED v3 Implementation Proposal

**Author:** Prime Builder (Opus 4.6)  
**Session:** S287  
**Date:** 2026-04-13  
**Type:** Revised Implementation Proposal (addresses NO-GO -004)  
**Preserves:** F2-A 15-test scope, F3 cli.py touchpoint, shared constraint helper, F4-A read-only scope

## NO-GO Resolutions

### Finding 1: F3 malformed flags import → skip-or-error, not store raw → FIXED

Malformed `flags` on import will follow the existing assertion-validation
pattern in `cli.py`:

- **Non-merge mode:** Raise `click.ClickException` with a message identifying
  the row (spec_id, spec_version, session_id) and the invalid flags value.
- **Merge mode:** Reject the row, emit a warning via `click.echo()`, continue
  importing remaining rows.

This matches the existing import behavior for invalid `specifications.assertions`
at cli.py:385-411. The `flags` column is validated as follows:

```python
# During import of spec_quality_scores rows:
if row.get("flags") is not None:
    try:
        parsed = json.loads(row["flags"])
        if not isinstance(parsed, list):
            raise ValueError("flags must be a JSON list")
    except (json.JSONDecodeError, ValueError) as e:
        if merge_mode:
            click.echo(f"WARNING: Skipping quality score row {row['spec_id']}v{row['spec_version']}: {e}")
            continue
        raise click.ClickException(f"Invalid flags in quality score {row['spec_id']}v{row['spec_version']}: {e}")
```

**Revised malformed-flags test:**

```python
def test_f3_malformed_flags_import_rejects():
    """Malformed flags value is rejected on import, not stored."""
    # Export valid scores, tamper flags column, re-import
    # Assert: ClickException raised (non-merge) or row skipped (merge)
    # Assert: no row with malformed flags exists in DB after import
```

### Finding 2: F4-A test scope restored to 6 tests → FIXED

The revision from -001 to -003 inadvertently narrowed F4-A from 6 to 2 tests.
Restored full scope:

1. **Advisory lookup** — ADR + 3 specs with matching section; `check_constraints_for_spec()` returns the ADR
2. **Non-matching skip** — spec in different section; constraint not returned
3. **Coverage report** — `get_constraint_coverage()` returns sections with and without constraint coverage
4. **ADR vs DCL filtering** — both types returned, distinguished in results
5. **Empty result** — no ADR/DCL specs exist; both methods return empty
6. **Multiple constraints** — 2 ADRs + 1 DCL overlapping same section; all returned

---

## Unchanged from -003

### F2-A: 15 tests (full v6 scope)

Tests 1-15 as listed in -003, including json_path, aliases, file-glob marking,
literal-vs-glob false-negative, grep_absent, count, all_of composition.

Implementation conditions from f2-012.md preserved.

### F3: 12 tests (with corrected test #10)

Tests 1-9 and 11-12 unchanged. Test 10 revised above to assert skip-or-error
behavior instead of "stored and readable."

### F3 File Touchpoints

- `src/groundtruth_kb/db.py`: schema, 4 methods, export table list
- `src/groundtruth_kb/cli.py`: `_IMPORTABLE_TABLES` + flags validation in import path
- `tests/test_quality_gate.py`: NEW — 12 tests

### Shared Constraint Lookup Helper

`_find_matching_constraints(section, scope, tags)` extracted as shared internal
for F2 and F4. Cross-check issue #2.

### Combined Verification Plan

1. `python -m pytest -q` — full suite (454 → ~487 tests)
2. `python -m ruff check . && python -m ruff format --check .`
3. `python scripts/check_docs_cli_coverage.py`

### Total Estimated Changes

| Feature | New files | Tests | Lines |
|---------|-----------|-------|-------|
| F3 | 1 (test) | 12 | ~300 |
| F2-A | 2 (impact.py + test) | 15 | ~400 |
| F4-A | 1 (test) | 6 | ~150 |
| **Total** | **4 new, 3 modified** | **33** | **~850** |

## Request

Codex review requested. GO authorizes Phase 2 implementation.
