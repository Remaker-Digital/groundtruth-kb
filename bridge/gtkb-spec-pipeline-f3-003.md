# F3: Spec Quality Gate — REVISED

**Feature:** F3 — Spec Quality Gate
**Target repo:** groundtruth-kb
**Tracker:** DOC-GTKB-SPEC-PIPELINE
**Revision:** Addresses 4 conditions from NO-GO bridge/gtkb-spec-pipeline-f3-002.md

---

## Changes From v1

| NO-GO Condition | Resolution |
|----------------|-----------|
| 1. F1 dependency unresolved | Graceful degradation: F1 fields scored when present, ignored when absent. Completeness dimension adjusts its denominator based on which fields exist in the schema. |
| 2. Non-executable assertion scoring | Testability scoring aligned with `_VALID_ASSERTION_TYPES` from assertions.py:39: `grep`, `glob`, `grep_absent`, `file_exists`, `count`, `json_path`, `all_of`, `any_of`. Non-machine types contribute zero testability score. |
| 3. Score persistence undecided | Decision: scores ARE persisted in a new `spec_quality_scores` table keyed by `(spec_id, spec_version, scored_at)`. Enables F7 historical trends. Recomputed on demand or at session boundaries. |
| 4. Configurability unspecified | Decision: weights are FIXED in code as product defaults. This is a deliberate product decision — consistent scoring across projects. If per-project weighting is needed later, it becomes a separate proposal. |

---

## Testability Scoring — Aligned With Executable Types

The valid executable assertion types (from assertions.py:39):
`grep`, `glob`, `grep_absent`, `file_exists`, `count`, `json_path`, `all_of`, `any_of`

**D2: Testability (0.0 - 1.0)**
- Has >= 1 assertion of any type → +0.3
- Has >= 1 assertion of executable type → +0.4 (this is the key signal — the assertion RUNS)
- Assertions have `description` field → +0.15
- Assertions target specific files (not wildcards) → +0.15

Non-machine assertion types (`visual`, `behavioral`, `manual`, `requirement`, `functional`, etc.) count for the "has any assertion" check (+0.3) but NOT for the executable check (+0.4). This means a spec with only non-machine assertions scores 0.3/1.0 on testability — it has assertions but none that execute. This directly prevents the corruption vector where weak non-executable assertions create false confidence.

## Graceful F1 Degradation

**D3: Completeness scoring adjusts dynamically:**

```python
def _score_completeness(spec: dict) -> float:
    checks = []
    checks.append(("type", spec.get("type") is not None))
    checks.append(("tags", bool(spec.get("tags"))))
    checks.append(("section", bool(spec.get("section"))))
    checks.append(("scope", bool(spec.get("scope"))))
    checks.append(("priority", bool(spec.get("priority"))))
    checks.append(("description_criteria", _has_acceptance_criteria(spec.get("description", ""))))
    
    # F1 fields — only scored if they exist in the schema
    if "authority" in spec:
        checks.append(("authority", spec.get("authority") is not None))
    if "constraints_parsed" in spec:
        checks.append(("constraints", spec.get("constraints_parsed") is not None))
    
    return sum(1 for _, v in checks if v) / len(checks)
```

When F1 fields are absent, the denominator shrinks and the score is based on existing fields only. When F1 ships, the denominator grows and specs without the new fields score lower. No code change needed — dynamic detection.

## Score Persistence

New table in GT-KB:

```sql
CREATE TABLE IF NOT EXISTS spec_quality_scores (
    spec_id TEXT NOT NULL,
    spec_version INTEGER NOT NULL,
    scored_at TEXT NOT NULL,
    overall REAL NOT NULL,
    d1_clarity REAL NOT NULL,
    d2_testability REAL NOT NULL,
    d3_completeness REAL NOT NULL,
    d4_isolation REAL NOT NULL,
    d5_freshness REAL NOT NULL,
    tier TEXT NOT NULL,
    flags TEXT,  -- JSON list of flag strings
    UNIQUE(spec_id, spec_version, scored_at)
);
```

**Retention:** Scores are append-only. Old scores provide historical trend data. No automatic cleanup — the table is lightweight (~100 bytes per row).

**Recomputation:** `score_spec_quality()` always computes fresh. `persist_quality_scores()` stores the result. Callers decide when to persist (session boundary, on-demand, after spec mutation).

## API Design

```python
@dataclass
class QualityScore:
    overall: float
    dimensions: dict      # {d1_clarity: float, d2_testability: float, ...}
    flags: list[str]
    tier: str             # 'directive', 'behavioral', 'architectural'

class KnowledgeDB:
    def score_spec_quality(self, spec_id: str) -> QualityScore:
        """Compute fresh quality score for a spec."""
        ...
    
    def persist_quality_scores(self, session_id: str) -> int:
        """Score all current specs and persist. Returns count scored."""
        ...
    
    def get_quality_distribution(self) -> dict:
        """Latest scores aggregated. Used by F7 dashboard."""
        ...
    
    def get_quality_history(self, spec_id: str) -> list[dict]:
        """Historical scores for a spec across versions/sessions."""
        ...
```

## Test Plan (synthetic fixtures)

1. **Perfect spec** — All fields populated, executable assertions; verify overall >= 0.8
2. **Minimal spec** — Required fields only; verify overall < 0.4, flag `NO_ASSERTIONS`
3. **Non-executable only** — Spec with `visual` assertion only; verify testability = 0.3 (has assertion but non-executable), flag `NO_EXECUTABLE_ASSERTIONS`
4. **Executable assertion** — Spec with `grep` assertion; verify testability >= 0.7
5. **F1 degradation** — Score spec without F1 fields in schema; verify completeness scores against reduced denominator without error
6. **Persistence roundtrip** — Persist score, retrieve via `get_quality_history()`; verify values match

## Implementation Sequence

1. Create `spec_quality_scores` table in schema migration
2. Implement D1 (clarity), D2 (testability against executable types), D3 (completeness with F1 degradation), D4 (isolation), D5 (freshness)
3. Implement tier recommendation and flag generation
4. Implement persistence and history queries
5. Write 6 tests

---

*Submitted by: S286-Prime*
*Revision: Addresses NO-GO bridge/gtkb-spec-pipeline-f3-002.md*
