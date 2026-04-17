# F8: Provenance Reconciliation — REVISED v5

**Revision:** Addresses 2 conditions from NO-GO bridge/gtkb-spec-pipeline-f8-008.md
**Prior deliberations:** F2 v5 (f2-009) introduces `file_is_glob` on the same `AssertionTarget` contract. F8 v5 uses a consistent `is_glob` check for `TypedFileTarget`.

---

## Changes From v4

| Condition | Resolution |
|-----------|-----------|
| 1. Orphan detection sends grep/count/grep_absent file-glob targets through `_safe_resolve()` instead of `_safe_glob()` | Added `is_glob` flag to `TypedFileTarget`. Orphan detection dispatches to `_safe_glob()` when `is_glob=True`, matching the runner's branch at assertions.py:214 (`"*" in file_rel`). |
| 2. Authority-conflict target overlap uses literal file equality, missing aliases/composition/globs | Authority conflicts now use `_extract_file_targets()` for both specs, comparing typed targets with alias resolution, composition recursion, and glob-aware overlap. |

---

## Typed File Target Extraction (updated)

```python
from dataclasses import dataclass
from groundtruth_kb.assertions import (
    _normalize_assertion,
    _VALID_ASSERTION_TYPES,
    _MAX_COMPOSITION_DEPTH,
)

@dataclass(frozen=True)
class TypedFileTarget:
    """A file target with its originating assertion type and glob status."""
    assertion_type: str   # Type of the assertion that produced this target
    target: str           # File path or glob pattern
    is_glob: bool         # True when target contains glob syntax ("*")

def _extract_file_targets(assertion: dict, depth: int = 0) -> list[TypedFileTarget]:
    """Extract all typed file targets from an assertion, handling aliases and composition.
    
    Uses the same normalization as GT-KB's assertion runner.
    Marks targets containing "*" as is_glob=True, matching the runner's
    branch at assertions.py:214 ("*" in file_rel → _safe_glob()).
    """
    a_type = assertion.get("type", "")
    
    if a_type not in _VALID_ASSERTION_TYPES:
        return []  # Non-executable — skip
    
    # Handle composition: recurse into children, preserving CHILD types
    if a_type in ("all_of", "any_of"):
        if depth >= _MAX_COMPOSITION_DEPTH:
            return []
        targets = []
        for child in assertion.get("assertions", []):
            targets.extend(_extract_file_targets(child, depth + 1))
        return targets
    
    normalized = _normalize_assertion(assertion)
    file_target = normalized.get("file")
    
    # glob assertion: pattern IS the target (always treated as glob)
    if a_type == "glob":
        pattern = normalized.get("pattern")
        if pattern:
            return [TypedFileTarget(
                assertion_type="glob",
                target=pattern,
                is_glob=True,  # glob assertions are always glob patterns
            )]
        return []
    
    # json_path: only 'file' is a file target (not 'path' — that's the JSON path expression)
    if a_type == "json_path":
        if file_target:
            return [TypedFileTarget(
                assertion_type="json_path",
                target=file_target,
                is_glob=bool("*" in file_target),
            )]
        return []
    
    # grep, grep_absent, count, file_exists: file target may be literal or glob
    if file_target:
        return [TypedFileTarget(
            assertion_type=a_type,
            target=file_target,
            is_glob=bool("*" in file_target),
        )]
    
    return []
```

## Revised Orphan Detection

```python
def find_orphaned_specs(kdb, project_root: Path) -> list[dict]:
    """Find specs whose executable assertion file targets no longer exist.
    
    Dispatches based on TypedFileTarget.is_glob:
    - is_glob=True → _safe_glob() (expand pattern, check match count)
    - is_glob=False → _safe_resolve() (resolve literal path, check existence)
    
    This matches the assertion runner's dispatch at assertions.py:214-226.
    """
    orphans = []
    for spec in kdb.list_specs():
        assertions = spec.get("assertions_parsed") or []
        for assertion in assertions:
            typed_targets = _extract_file_targets(assertion)
            for tt in typed_targets:
                if tt.is_glob:
                    # Glob target: expand pattern and check match count
                    matches = _safe_glob(tt.target, project_root)
                    if matches is not None and len(matches) == 0:
                        orphans.append({
                            "spec_id": spec["id"],
                            "assertion_type": tt.assertion_type,
                            "target": tt.target,
                            "is_glob": True,
                            "reason": "glob pattern matches zero files",
                        })
                else:
                    # Literal file target: resolve path and check existence
                    resolved = _safe_resolve(tt.target, project_root)
                    if resolved is not None and not resolved.exists():
                        orphans.append({
                            "spec_id": spec["id"],
                            "assertion_type": tt.assertion_type,
                            "target": tt.target,
                            "is_glob": False,
                            "reason": "file does not exist",
                        })
    return orphans
```

## Revised Authority-Conflict Detection

Authority conflicts now use `_extract_file_targets()` instead of raw `file` field equality:

```python
def _assertions_overlap(spec_a: dict, spec_b: dict) -> bool:
    """Check if two specs have overlapping assertion file targets.
    
    Uses typed target extraction with alias resolution and composition recursion.
    Comparison is exact string equality on target values (same as F2's conflict
    detection strategy — no filesystem glob expansion).
    """
    targets_a = set()
    targets_b = set()
    
    for assertion in spec_a.get("assertions_parsed") or []:
        for tt in _extract_file_targets(assertion):
            targets_a.add(tt.target)
    
    for assertion in spec_b.get("assertions_parsed") or []:
        for tt in _extract_file_targets(assertion):
            targets_b.add(tt.target)
    
    return bool(targets_a & targets_b)
```

**Key behaviors:**
- Aliases resolved before comparison: `{"type": "grep", "target": "src/api.py"}` and `{"type": "grep", "file": "src/api.py"}` → same target string → overlap detected
- Composition children included: `all_of` with `grep` targeting `src/api.py` → `src/api.py` in target set
- Glob strings compared as strings: `src/**/*.py` == `src/**/*.py` → overlap; `src/**/*.py` != `tests/**/*.py` → no overlap
- Literal vs glob (`src/api.py` vs `src/**/*.py`): no overlap detected (consistent with F2's documented false-negative class)

## Revised Test Plan (14 cases)

### Orphan Detection (9 tests)
1. **Orphan: direct file** — `grep` with `file="src/deleted.py"`; file absent; orphan detected, `assertion_type="grep"`, `is_glob=False`
2. **Orphan: path alias** — `file_exists` with `path="src/deleted.py"`; orphan detected (alias resolved)
3. **Orphan: target alias** — `grep` with `target="src/deleted.py"`; orphan detected
4. **Orphan: glob assertion** — `glob` with `pattern="src/missing/**/*.py"`; zero matches; orphan detected, `is_glob=True`
5. **Orphan: grep with file glob (matching)** — `grep` with `file="src/**/*.py"`, files exist; no orphan (glob matches files), dispatched via `_safe_glob()`, `is_glob=True`
6. **Orphan: grep with file glob (no match)** — `grep` with `file="src/nonexistent/**/*.py"`, no files; orphan detected via `_safe_glob()`, `is_glob=True`
7. **Orphan: all_of with grep children** — `all_of` with 2 `grep` children (literal files), one missing; orphan for missing child with `assertion_type="grep"`
8. **Orphan: all_of with nested glob child** — `all_of` with 1 `glob` child (zero matches) + 1 `grep` child (existing file); orphan for glob child via `_safe_glob()`, `assertion_type="glob"`
9. **Orphan: all_of with grep file-glob child** — `all_of` with 1 `grep` child `file="missing/**/*.py"` + 1 `file_exists` child (existing); orphan for grep child via `_safe_glob()`, `assertion_type="grep"`, `is_glob=True`

### Authority Conflicts (3 tests)
10. **Conflict: same file, different aliases** — Spec A: `grep` with `file="src/api.py"`, Spec B: `grep` with `target="src/api.py"`; same section → conflict detected (aliases normalized to same target)
11. **Conflict: composition child overlap** — Spec A: `grep` with `file="src/api.py"`, Spec B: `all_of` with `grep` child targeting `src/api.py`; same section → conflict detected (composition child extracted)
12. **Conflict: glob string match** — Spec A: `grep` with `file="src/**/*.py"`, Spec B: `count` with `file="src/**/*.py"`; same section → conflict detected (exact glob string match)

### Provenance (2 tests)
13. **Expired provisional** — Provisional spec with replacement implemented; expiration detected
14. **Duplicate detection** — 90% title token overlap; duplicate reported

---

*Submitted by: S287-Prime*
*Revision: v5 — addresses NO-GO bridge/gtkb-spec-pipeline-f8-008.md*
