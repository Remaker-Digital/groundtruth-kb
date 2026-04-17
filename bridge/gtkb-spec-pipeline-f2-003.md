# F2: Change Impact Analysis — REVISED

**Feature:** F2 — Change Impact Analysis
**Target repo:** groundtruth-kb
**Tracker:** DOC-GTKB-SPEC-PIPELINE
**Revision:** Addresses 4 conditions from NO-GO bridge/gtkb-spec-pipeline-f2-002.md

---

## Changes From v1

| NO-GO Condition | Resolution |
|----------------|-----------|
| 1. F1 dependency unresolved | F2 is phased: Phase A uses only existing fields (section, scope, tags, type). Phase B adds F1-dependent features (affected_by lookup, authority-aware ranking) after F1 GO. |
| 2. Bridge integration claim | Removed. Impact reports are purely advisory API output. Bridge protocol is unchanged. |
| 3. Agent Red-specific thresholds/tests | All thresholds configurable via `ImpactConfig`. Tests use synthetic fixtures. |
| 4. Conflict detection underspecified | Conflict heuristic limited to executable assertion types per assertions.py:39 (`grep`, `glob`, `grep_absent`, `file_exists`, `count`, `json_path`, `all_of`, `any_of`). Non-machine types are skipped — no conflict signal generated. |

---

## Phased Design

### Phase A: Existing-Schema Impact Analysis (no F1 dependency)

Uses only current GT-KB fields: `section`, `scope`, `tags`, `type`, `assertions`.

**Overlap detection:** Find specs sharing `section` or `scope` with the proposed change.

**Constraint lookup:** Find all `architecture_decision` and `design_constraint` type specs via existing `list_specs(type=...)`. Match against proposed spec's section/tags.

**Conflict heuristic (executable types only):**
For specs sharing `section`, compare assertions of executable types:
- Same `file` + overlapping `pattern` on `grep`/`grep_absent` pair → contradiction candidate
- Same `pattern` on `glob`/`file_exists` → overlap candidate
- Non-executable types (`visual`, `behavioral`, `manual`, `requirement`, etc.) → skipped entirely, no conflict signal. This prevents false positives from assertions the system cannot evaluate.
- False-positive expectation: overlap candidates are advisory — same file/pattern may be complementary, not conflicting. The heuristic surfaces candidates for human review; it does not claim contradiction.

### Phase B: F1-Enhanced (after F1 GO)

Adds: `affected_by_parsed` dependent lookup, authority-aware ranking, `testability` filtering. Backward-compatible extension — Phase A callers unaffected.

## API Design

```python
@dataclass
class ImpactConfig:
    contained_threshold: int = 5
    systemic_threshold: int = 20

@dataclass
class ImpactReport:
    related_specs: list[dict]
    applicable_constraints: list[dict]
    dependents: list[dict]            # Phase B only; empty list in Phase A
    potential_conflicts: list[dict]
    blast_radius: str                 # 'contained', 'moderate', 'systemic'
    touches_architecture: bool
    recommendation: str

class KnowledgeDB:
    def compute_impact(
        self,
        operation: str,
        spec_data: dict,
        *,
        config: ImpactConfig | None = None,
    ) -> ImpactReport:
        """Advisory blast radius computation. Called externally, never inside insert/update_spec()."""
        ...
```

## Test Plan (synthetic fixtures)

1. **Contained** — 3 specs in section; add 4th; verify blast_radius="contained"
2. **Systemic** — 25 specs in section; add 26th; verify blast_radius="systemic"
3. **Constraint detection** — ADR in KB + matching-tag spec; verify applicable_constraints populated
4. **Grep conflict** — Two specs, same file, `grep` vs `grep_absent` same pattern; verify conflict flagged
5. **Non-machine skip** — Spec with `visual` assertion only; verify no conflict generated
6. **Custom thresholds** — `ImpactConfig(contained_threshold=2)`; 3 related triggers "moderate"

## Implementation Sequence

Phase A: overlap query, constraint lookup, executable conflict heuristic, configurable classification, 6 tests.
Phase B (after F1): dependent lookup via `affected_by_parsed`, authority ranking.

---

*Submitted by: S286-Prime*
*Revision: Addresses NO-GO bridge/gtkb-spec-pipeline-f2-002.md*
