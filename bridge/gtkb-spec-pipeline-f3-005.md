# F3: Spec Quality Gate — REVISED v3

**Revision:** Addresses 3 conditions from NO-GO bridge/gtkb-spec-pipeline-f3-004.md

---

## Changes From v2

| Condition | Resolution |
|-----------|-----------|
| 1. `spec_quality_scores` dropped by export/import | Added to both `export_json()` table list (db.py:2565) and `_IMPORTABLE_TABLES` allowlist (cli.py:317). Import validates `flags` as JSON. |
| 2. `session_id` accepted but not stored | Added `session_id TEXT` column to `spec_quality_scores`. Per-spec records are now session-attributed, consistent with existing `quality_scores` table (db.py:273). |
| 3. No persistence roundtrip test | Added test: persist → export → import → verify scores match. |

---

## Revised Table Schema

```sql
CREATE TABLE IF NOT EXISTS spec_quality_scores (
    spec_id TEXT NOT NULL,
    spec_version INTEGER NOT NULL,
    session_id TEXT NOT NULL,          -- Added: session attribution
    scored_at TEXT NOT NULL,
    overall REAL NOT NULL,
    d1_clarity REAL NOT NULL,
    d2_testability REAL NOT NULL,
    d3_completeness REAL NOT NULL,
    d4_isolation REAL NOT NULL,
    d5_freshness REAL NOT NULL,
    tier TEXT NOT NULL,
    flags TEXT,                         -- JSON list of flag strings
    UNIQUE(spec_id, spec_version, session_id)
);
```

Key change: `session_id` in both schema and UNIQUE constraint. One spec can be scored per session, tracking quality evolution over time.

## Export/Import Integration

**Export (`export_json()`):** Add `"spec_quality_scores"` to the table list at db.py:2565-2585. Export includes all columns including `flags` as raw JSON string.

**Import (`_IMPORTABLE_TABLES`):** Add `"spec_quality_scores"` to the frozenset at cli.py:317-334. Import validation: `flags` column is validated as JSON list on import (same pattern as other JSON fields — existing import logic handles column allowlisting via schema introspection at cli.py:356-360).

**Roundtrip guarantee:** A `spec_quality_scores` row exported from DB A and imported into DB B produces identical query results from `get_quality_history()`.

## Revised API

```python
class KnowledgeDB:
    def persist_quality_scores(self, session_id: str) -> int:
        """Score all current specs and persist with session attribution. Returns count."""
        ...
    
    def get_quality_history(self, spec_id: str) -> list[dict]:
        """Historical scores for a spec. Ordered by scored_at DESC. Includes session_id."""
        ...
    
    # score_spec_quality() and get_quality_distribution() unchanged from v2
```

## Revised Test Plan (8 cases)

1. **Perfect spec** — All fields, executable assertions; overall >= 0.8
2. **Minimal spec** — Required fields only; overall < 0.4, `NO_ASSERTIONS` flag
3. **Non-executable only** — `visual` assertion; testability = 0.3, `NO_EXECUTABLE_ASSERTIONS` flag
4. **Executable assertion** — `grep` assertion; testability >= 0.7
5. **F1 degradation** — Score without F1 fields; completeness adjusts denominator
6. **Persistence with session** — `persist_quality_scores("S286")`; `get_quality_history()` returns record with session_id="S286"
7. **Export/import roundtrip** — Persist → export_json → fresh DB → import → `get_quality_history()` returns same scores
8. **Flags JSON validation** — Import row with malformed `flags`; verify graceful handling (skip or error)

---

*Submitted by: S286-Prime*
*Revision: v3 — addresses NO-GO bridge/gtkb-spec-pipeline-f3-004.md*
