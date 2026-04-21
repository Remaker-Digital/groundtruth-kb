# F8: Provenance Reconciliation — REVISED v4

**Revision:** Addresses 1 condition from NO-GO bridge/gtkb-spec-pipeline-f8-006.md

---

## Changes From v3

| Condition | Resolution |
|-----------|-----------|
| 1. Composition extraction loses child assertion type — nested `glob` treated as literal file path | Returns `list[TypedFileTarget]` instead of `list[str]`. Each target carries its assertion type through composition traversal. `find_orphaned_specs()` dispatches to `_safe_glob()` or `_safe_resolve()` per target's type. Added nested `glob` composition tests. |

---

## Typed File Target Extraction

```python
from dataclasses import dataclass
from groundtruth_kb.assertions import (
    _normalize_assertion,
    _VALID_ASSERTION_TYPES,
    _MAX_COMPOSITION_DEPTH,
)

@dataclass(frozen=True)
class TypedFileTarget:
    """A file target with its originating assertion type preserved."""
    assertion_type: str   # Type of the assertion that produced this target
    target: str           # File path or glob pattern

def _extract_file_targets(assertion: dict, depth: int = 0) -> list[TypedFileTarget]:
    """Extract all typed file targets from an assertion, handling aliases and composition.
    
    Uses the same normalization as GT-KB's assertion runner.
    Returns typed targets so the caller can dispatch glob vs file-path checks.
    """
    a_type = assertion.get("type", "")
    
    if a_type not in _VALID_ASSERTION_TYPES:
        return []  # Non-executable — skip
    
    # Handle composition: recurse into children, preserving CHILD types
    if a_type in ("all_of", "any_of"):
        if depth >= _MAX_COMPOSITION_DEPTH:
            return []  # Depth limit — same as assertion runner
        targets = []
        for child in assertion.get("assertions", []):
            targets.extend(_extract_file_targets(child, depth + 1))
        return targets
    
    # Normalize aliases to canonical 'file' and 'pattern'
    normalized = _normalize_assertion(assertion)
    file_target = normalized.get("file")
    
    if a_type == "glob":
        # glob uses pattern as the target (it's a file path pattern, not a regex)
        pattern = normalized.get("pattern")
        if pattern:
            return [TypedFileTarget(assertion_type="glob", target=pattern)]
        return []
    
    # json_path: read 'path' from original assertion (JSON path expression, not a file)
    # Only the 'file' field is a file target for json_path assertions
    if a_type == "json_path":
        if file_target:
            return [TypedFileTarget(assertion_type="json_path", target=file_target)]
        return []
    
    # All other types: file_exists, grep, grep_absent, count
    if file_target:
        return [TypedFileTarget(assertion_type=a_type, target=file_target)]
    
    return []  # No file target found
```

**Key difference from v3:** Each child in `all_of`/`any_of` produces targets tagged with the CHILD's type, not the parent composition type. This ensures:
- A `glob` child inside `all_of` → `TypedFileTarget(assertion_type="glob", target="src/**/*.py")`
- A `grep` child inside `all_of` → `TypedFileTarget(assertion_type="grep", target="src/api.py")`

## Revised Orphan Detection

```python
def find_orphaned_specs(kdb, project_root: Path) -> list[dict]:
    """Find specs whose executable assertion file targets no longer exist.
    
    Dispatches to _safe_glob() for glob-typed targets and _safe_resolve()
    for literal file targets — matching the assertion runner's behavior.
    """
    orphans = []
    for spec in kdb.list_specs():
        assertions = spec.get("assertions_parsed") or []
        for assertion in assertions:
            typed_targets = _extract_file_targets(assertion)
            for tt in typed_targets:
                if tt.assertion_type == "glob":
                    # Glob: check if pattern matches any files
                    matches = _safe_glob(tt.target, project_root)
                    if matches is not None and len(matches) == 0:
                        orphans.append({
                            "spec_id": spec["id"],
                            "assertion_type": tt.assertion_type,
                            "target": tt.target,
                            "reason": "glob pattern matches zero files",
                        })
                else:
                    # File path: check if resolved path exists
                    resolved = _safe_resolve(tt.target, project_root)
                    if resolved is not None and not resolved.exists():
                        orphans.append({
                            "spec_id": spec["id"],
                            "assertion_type": tt.assertion_type,
                            "target": tt.target,
                            "reason": "file does not exist",
                        })
                    # If _safe_resolve returns None (path escape), skip — not an orphan,
                    # just an invalid path that the assertion runner would also reject.
    return orphans
```

**Dispatch logic matches the assertion runner:**
- `glob` → `_safe_glob()` (assertions.py:250) — expands pattern, counts matches
- `grep`, `grep_absent`, `count`, `file_exists`, `json_path` → `_safe_resolve()` (assertions.py:174) — resolves literal path, checks existence
- Composition children dispatch by their own `assertion_type`, not the parent's

## Revised Test Plan (11 cases)

1. **Authority conflict** — stated + inferred, same section, overlapping assertion file; conflict detected
2. **No false conflict** — Different sections; no conflict
3. **Orphan: direct file** — `grep` with `file="src/deleted.py"`; file doesn't exist; orphan detected with `assertion_type="grep"`
4. **Orphan: path alias** — `file_exists` with `path="src/deleted.py"`; orphan detected (alias resolved), `assertion_type="file_exists"`
5. **Orphan: target alias** — `grep` with `target="src/deleted.py"`; orphan detected, `assertion_type="grep"`
6. **Orphan: glob pattern** — `glob` with `pattern="src/missing/**/*.py"`; zero matches; orphan detected with `assertion_type="glob"`
7. **Orphan: all_of with grep children** — `all_of` with 2 `grep` children, one file exists, one doesn't; orphan detected for missing file with `assertion_type="grep"` (not "all_of")
8. **Orphan: all_of with nested glob** — `all_of` with 1 `glob` child `pattern="src/nonexistent/**/*.py"` + 1 `grep` child with existing file; orphan detected for glob with `assertion_type="glob"` and uses `_safe_glob()` (not `_safe_resolve()`)
9. **Orphan: any_of with mixed types** — `any_of` with 1 `glob` child (matching pattern) + 1 `grep` child (missing file); orphan for grep child only, glob child resolves via `_safe_glob()` and finds matches
10. **Expired provisional** — Provisional spec with replacement implemented; expiration detected
11. **Duplicate detection** — 90% title token overlap; duplicate reported

---

*Submitted by: S287-Prime*
*Revision: v4 — addresses NO-GO bridge/gtkb-spec-pipeline-f8-006.md*
