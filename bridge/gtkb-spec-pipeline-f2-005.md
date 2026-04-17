# F2: Change Impact Analysis — REVISED v3

**Revision:** Addresses 2 conditions from NO-GO bridge/gtkb-spec-pipeline-f2-004.md

---

## Changes From v2

| Condition | Resolution |
|-----------|-----------|
| 1. Conflict heuristic references wrong fields per assertion type | Replaced with normalized target extraction per assertion type, using `_normalize_assertion()` from assertions.py:137 and alias lists `_FILE_ALIASES` (assertions.py:133) and `_PATTERN_ALIASES` (assertions.py:134). |
| 2. Tests don't cover assertion-schema edge cases | Added 4 new tests for `file_exists`+path alias, `grep`+target alias, `count`/`json_path`, and `all_of`/`any_of` composition. |

---

## Normalized Assertion Target Extraction

Before comparing assertions for conflict, F2 normalizes each assertion using the same alias resolution as GT-KB's assertion runner:

```python
from groundtruth_kb.assertions import _normalize_assertion, _VALID_ASSERTION_TYPES

def _extract_target(assertion: dict) -> tuple[str | None, str | None]:
    """Extract (file_target, pattern) from a normalized assertion.
    
    Returns (None, None) for non-executable or untargetable assertions.
    """
    a_type = assertion.get("type", "")
    if a_type not in _VALID_ASSERTION_TYPES:
        return (None, None)  # Non-executable — skip
    
    normalized = _normalize_assertion(assertion)
    file_target = normalized.get("file")    # Canonical after alias resolution
    pattern = normalized.get("pattern")      # Canonical after alias resolution
    return (file_target, pattern)
```

**Per-type behavior after normalization:**

| Type | `file` source (after alias resolution) | `pattern` source | Conflict signal |
|------|---------------------------------------|-----------------|----------------|
| `grep` | `file`, `target`, `path`, `file_pattern`, `expected` → canonical `file` | `pattern`, `query` → canonical `pattern` | Same file + overlapping pattern |
| `grep_absent` | Same as grep | Same as grep | Same file + same pattern as a `grep` → contradiction candidate |
| `glob` | N/A (pattern IS the target) | `pattern` | Same glob pattern |
| `file_exists` | `file`, `path`, `target`, `file_pattern`, `expected` → canonical `file` | N/A | Same file target |
| `count` | Same alias resolution as grep | Same as grep | Same file + same pattern |
| `json_path` | Same alias resolution | `path` field for JSON path | Same file + same JSON path |
| `all_of` | Recurse into `assertions` children | Recurse | Union of child targets |
| `any_of` | Recurse into `assertions` children | Recurse | Union of child targets |

**Composition handling (`all_of`/`any_of`):** Recurse into the `assertions` list field, extract targets from each child. The composite assertion's targets are the union of its children's targets. Recursion depth capped at `_MAX_COMPOSITION_DEPTH = 3` (matching assertions.py).

## Revised Test Plan (10 cases)

1. **Contained** — 3 specs in section; add 4th; blast_radius="contained"
2. **Systemic** — 25 specs in section; add 26th; blast_radius="systemic"
3. **Constraint detection** — ADR + matching-tag spec; applicable_constraints populated
4. **grep vs grep_absent conflict** — Same file, same pattern; conflict flagged
5. **Non-machine skip** — `visual` assertion only; no conflict
6. **Custom thresholds** — `ImpactConfig(contained_threshold=2)`; 3 related = "moderate"
7. **file_exists with path alias** — Assertion `{"type": "file_exists", "path": "src/main.py"}`; verify target extracted as `src/main.py`
8. **grep with target alias** — Assertion `{"type": "grep", "target": "src/api.py", "query": "def handler"}`; verify file=`src/api.py`, pattern=`def handler`
9. **count/json_path** — `count` assertion with `file` and `pattern`; verify target extraction
10. **all_of composition** — `all_of` with 2 `grep` children targeting different files; verify both file targets in union

---

*Submitted by: S286-Prime*
*Revision: v3 — addresses NO-GO bridge/gtkb-spec-pipeline-f2-004.md*
