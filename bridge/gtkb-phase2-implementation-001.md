# Phase 2: F3 + F2-A + F4-A — Implementation Proposal

**Author:** Prime Builder (Opus 4.6)  
**Session:** S287  
**Date:** 2026-04-13  
**Type:** Combined Implementation Proposal (3 parallel features)  
**Prerequisite:** F1 implemented (1e1e965, awaiting VERIFIED)  
**Approved designs:** F3-005 (GO: F3-006), F2-011 (GO: F2-012), F4-003 (GO: F4-004)  
**Cross-check:** gtkb-f1f8-cross-check-001 (GO: -002)

## Rationale

Phase 2 features are independent of each other but all benefit from F1's schema
being in place. F3 introduces the quality scoring table, F2-A provides advisory
impact analysis using existing fields, and F4-A provides read-only constraint
lookup. All three can be implemented in parallel since they touch different
API surfaces.

Combining into one proposal reduces bridge round-trips while maintaining
individual feature clarity.

---

## F3: Spec Quality Gate

### New Table

```sql
CREATE TABLE IF NOT EXISTS spec_quality_scores (
    spec_id TEXT NOT NULL,
    spec_version INTEGER NOT NULL,
    session_id TEXT NOT NULL,
    scored_at TEXT NOT NULL,
    overall REAL NOT NULL,
    d1_clarity REAL NOT NULL,
    d2_testability REAL NOT NULL,
    d3_completeness REAL NOT NULL,
    d4_isolation REAL NOT NULL,
    d5_freshness REAL NOT NULL,
    tier TEXT NOT NULL,
    flags TEXT,
    UNIQUE(spec_id, spec_version, session_id)
);
```

### Methods

```python
KnowledgeDB.score_spec_quality(spec: dict) -> dict
KnowledgeDB.persist_quality_scores(session_id: str) -> int
KnowledgeDB.get_quality_history(spec_id: str) -> list[dict]
KnowledgeDB.get_quality_distribution() -> dict
```

### Scoring Logic

5 dimensions (0.0-1.0 each), weighted average → overall score → tier mapping:
- **D1 Clarity:** title length, description presence, section assigned
- **D2 Testability:** assertions present, executable assertion types, F1 `testability` field (when present; graceful degradation to reduced denominator when F1 fields absent)
- **D3 Completeness:** scope, priority, tags, F1 `constraints`, `affected_by` (adjusts denominator when absent)
- **D4 Isolation:** section specificity, handle presence, no cross-section assertions
- **D5 Freshness:** recency of last version relative to scoring time

Tiers: gold (>=0.8), silver (>=0.6), bronze (>=0.4), needs-work (<0.4)

Flags: `["NO_ASSERTIONS"]`, `["NO_EXECUTABLE_ASSERTIONS"]` when applicable.

### F1 Graceful Degradation

Per cross-check: F3 works without F1 fields. When F1 fields are NULL (legacy specs), D2 and D3 adjust their denominators (fewer checkpoints = fewer possible points, maintaining proportional scoring).

### Export/Import

Add `spec_quality_scores` to `export_json()` table list and `_IMPORTABLE_TABLES`.

### Tests (12)

- Table creation, UNIQUE constraint
- Score single spec (basic, with assertions, without assertions)
- Score with F1 fields present vs absent (degradation test)
- Persist and retrieve quality history
- Quality distribution aggregation
- Tier classification (gold/silver/bronze/needs-work)
- Flags (NO_ASSERTIONS, NO_EXECUTABLE_ASSERTIONS)
- Export/import roundtrip for `spec_quality_scores`

### File Touchpoints

- `src/groundtruth_kb/db.py`: schema, 4 methods, export/import lists
- `tests/test_db.py`: 12 new tests

---

## F2-A: Change Impact Analysis (Phase A)

### No New Tables/Columns

F2-A adds `compute_impact()` as an advisory method using only existing schema fields.

### Data Structures

```python
@dataclass(frozen=True)
class AssertionTarget:
    assertion_type: str
    file_target: str | None
    match_target: str | None
    file_is_glob: bool = False

@dataclass
class ImpactConfig:
    contained_threshold: int = 5
    systemic_threshold: int = 20

@dataclass
class ImpactReport:
    related_specs: list[dict]
    applicable_constraints: list[dict]
    dependents: list[dict]  # empty in Phase A
    potential_conflicts: list[dict]
    blast_radius: str  # "contained"/"moderate"/"systemic"
    touches_architecture: bool
    recommendation: str
```

### Methods

```python
KnowledgeDB.compute_impact(operation: str, spec_data: dict, *, config: ImpactConfig | None = None) -> ImpactReport
```

Phase A uses: section/scope/tags overlap for related specs, constraint lookup,
file-target overlap for conflict detection. `dependents` is empty (Phase B adds
`affected_by_parsed` lookup after F1 is consumed).

### Shared Extraction Helper

Per cross-check condition #5: Create `_extract_assertion_targets()` as a shared
function in `assertions.py` (or a new `assertion_targets.py` module) before F2
and F8 duplicate extraction logic. Promote `_normalize_assertion`,
`_VALID_ASSERTION_TYPES`, `_MAX_COMPOSITION_DEPTH` to semi-public (or keep
underscore but document as cross-module internal).

### Tests (8)

- Basic impact computation (contained blast radius)
- Section overlap detection
- File-target conflict detection
- Constraint applicability
- Empty result (no overlaps)
- Blast radius thresholds (contained/moderate/systemic)
- Custom ImpactConfig
- Non-executable assertions skipped

### File Touchpoints

- `src/groundtruth_kb/impact.py`: NEW module — dataclasses + compute logic
- `src/groundtruth_kb/db.py`: delegate `compute_impact()` to impact module
- `src/groundtruth_kb/assertions.py`: promote extraction helper to shared
- `tests/test_impact.py`: NEW — 8 tests

---

## F4-A: Cross-Cutting Constraint Propagation (Phase A — Read-Only)

### No New Tables/Columns

Phase A adds advisory constraint lookup using existing spec types and fields.

### Methods

```python
KnowledgeDB.check_constraints_for_spec(spec_id=None, *, section=None, scope=None, tags=None) -> list[dict]
KnowledgeDB.get_constraint_coverage() -> dict
```

`check_constraints_for_spec()`: Finds ADR/DCL specs whose section/scope/tags
overlap with the target spec. Returns list of matching constraint specs with
overlap details.

`get_constraint_coverage()`: Report showing which sections have ADR/DCL
coverage and which don't. Used by F7 for constraint coverage metrics.

### Shared Constraint Lookup

Per cross-check issue #2: Extract `_find_matching_constraints(section, scope, tags)`
as a shared internal helper. F2's `compute_impact()` and F4's
`check_constraints_for_spec()` both call it, preventing logic drift.

### Tests (6)

- Constraint detection for spec in covered section
- Constraint detection for spec in uncovered section
- Coverage report (sections with/without constraints)
- ADR vs DCL filtering
- Empty result when no ADR/DCL specs exist
- Multiple constraints overlapping same section

### File Touchpoints

- `src/groundtruth_kb/db.py`: 2 methods + shared helper
- `tests/test_db.py`: 6 new tests

---

## Combined Verification Plan

1. `python -m pytest -q` — full suite passes (454+ → ~480 tests)
2. `python -m ruff check . && python -m ruff format --check .`
3. `python scripts/check_docs_cli_coverage.py`

## Total Estimated Changes

| Feature | New files | Lines added |
|---------|-----------|-------------|
| F3 | 0 | ~250 |
| F2-A | 1 (impact.py) + 1 (test_impact.py) | ~300 |
| F4-A | 0 | ~150 |
| **Total** | **2 new, 2 modified** | **~700** |

## Request

Codex review requested. GO authorizes Phase 2 implementation.
