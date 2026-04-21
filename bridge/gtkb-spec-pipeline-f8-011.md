# F8: Provenance Reconciliation — REVISED v6

**Revision:** Addresses 2 conditions from NO-GO bridge/gtkb-spec-pipeline-f8-010.md

---

## Changes From v5

| Condition | Resolution |
|-----------|-----------|
| 1. `is_glob` dispatch over-generalizes to `file_exists` and `json_path` | Replaced generic `is_glob = "*" in target` with type-specific dispatch. Only `grep`/`grep_absent`/`count` support file-glob expansion (matching runner behavior). `file_exists` and `json_path` always use `_safe_resolve()`. |
| 2. Missing `grep_absent`/`count` file-glob orphan tests | Added explicit orphan tests for `grep_absent` and `count` file-glob targets (direct and nested composition). |

---

## Type-Specific Dispatch Rules

The assertion runner handles file targets differently per type. Orphan detection must match:

| Assertion Type | Runner File Dispatch | Orphan Dispatch | Evidence |
|---------------|---------------------|-----------------|----------|
| `glob` | Always `_safe_glob()` on `pattern` | Always `_safe_glob()` | assertions.py:241-264 |
| `grep` | `_safe_glob()` if `*` in file, else `_safe_resolve()` | Same | assertions.py:214-226 |
| `grep_absent` | `_safe_glob()` if `*` in file, else `_safe_resolve()` | Same | assertions.py:278-290 |
| `count` | `_safe_glob()` if `*` in file, else `_safe_resolve()` | Same | assertions.py:352-364 |
| `file_exists` | Always `_safe_resolve()` | Always `_safe_resolve()` | assertions.py:307-320 |
| `json_path` | Always `_safe_resolve()` | Always `_safe_resolve()` | assertions.py:403-421 |

## Typed File Target Extraction (updated)

```python
from dataclasses import dataclass
from groundtruth_kb.assertions import (
    _normalize_assertion,
    _VALID_ASSERTION_TYPES,
    _MAX_COMPOSITION_DEPTH,
)

# Types whose runner dispatches file targets through _safe_glob() when "*" is present
_GLOB_CAPABLE_TYPES = frozenset({"grep", "grep_absent", "count"})

@dataclass(frozen=True)
class TypedFileTarget:
    """A file target with its originating assertion type and dispatch semantics."""
    assertion_type: str   # Type of the assertion that produced this target
    target: str           # File path or glob pattern
    use_glob: bool        # True ONLY for types whose runner supports glob dispatch AND target contains "*"

def _extract_file_targets(assertion: dict, depth: int = 0) -> list[TypedFileTarget]:
    """Extract all typed file targets from an assertion.
    
    Sets use_glob=True only for grep-style types whose runner branches on
    "*" in file_rel. file_exists and json_path always get use_glob=False
    because their runners always call _safe_resolve().
    """
    a_type = assertion.get("type", "")
    
    if a_type not in _VALID_ASSERTION_TYPES:
        return []
    
    # Composition: recurse into children, preserving child types
    if a_type in ("all_of", "any_of"):
        if depth >= _MAX_COMPOSITION_DEPTH:
            return []
        targets = []
        for child in assertion.get("assertions", []):
            targets.extend(_extract_file_targets(child, depth + 1))
        return targets
    
    normalized = _normalize_assertion(assertion)
    file_target = normalized.get("file")
    
    # glob assertion: always glob dispatch (pattern is the target)
    if a_type == "glob":
        pattern = normalized.get("pattern")
        if pattern:
            return [TypedFileTarget(
                assertion_type="glob",
                target=pattern,
                use_glob=True,
            )]
        return []
    
    # json_path: only 'file' is a file target; always literal resolution
    if a_type == "json_path":
        if file_target:
            return [TypedFileTarget(
                assertion_type="json_path",
                target=file_target,
                use_glob=False,  # Runner always uses _safe_resolve()
            )]
        return []
    
    # file_exists: always literal resolution
    if a_type == "file_exists":
        if file_target:
            return [TypedFileTarget(
                assertion_type="file_exists",
                target=file_target,
                use_glob=False,  # Runner always uses _safe_resolve()
            )]
        return []
    
    # grep, grep_absent, count: glob dispatch only when "*" in file target
    if file_target:
        return [TypedFileTarget(
            assertion_type=a_type,
            target=file_target,
            use_glob=bool(a_type in _GLOB_CAPABLE_TYPES and "*" in file_target),
        )]
    
    return []
```

## Revised Orphan Detection

```python
def find_orphaned_specs(kdb, project_root: Path) -> list[dict]:
    """Find specs whose executable assertion file targets no longer exist.
    
    Dispatches based on TypedFileTarget.use_glob, which is set per assertion
    type to match runner behavior exactly.
    """
    orphans = []
    for spec in kdb.list_specs():
        assertions = spec.get("assertions_parsed") or []
        for assertion in assertions:
            typed_targets = _extract_file_targets(assertion)
            for tt in typed_targets:
                if tt.use_glob:
                    matches = _safe_glob(tt.target, project_root)
                    if matches is not None and len(matches) == 0:
                        orphans.append({
                            "spec_id": spec["id"],
                            "assertion_type": tt.assertion_type,
                            "target": tt.target,
                            "use_glob": True,
                            "reason": "glob pattern matches zero files",
                        })
                else:
                    resolved = _safe_resolve(tt.target, project_root)
                    if resolved is not None and not resolved.exists():
                        orphans.append({
                            "spec_id": spec["id"],
                            "assertion_type": tt.assertion_type,
                            "target": tt.target,
                            "use_glob": False,
                            "reason": "file does not exist",
                        })
    return orphans
```

## Authority-Conflict Detection (unchanged from v5)

Uses `_extract_file_targets()` for both specs, compares target strings with exact equality. Consistent with F2's documented false-negative class for literal-vs-glob overlap.

## Revised Test Plan (17 cases)

### Orphan Detection (12 tests)
1. **Orphan: grep literal file** — `grep` with `file="src/deleted.py"`; orphan detected, `use_glob=False`
2. **Orphan: path alias** — `file_exists` with `path="src/deleted.py"`; orphan detected (alias resolved), `use_glob=False`
3. **Orphan: target alias** — `grep` with `target="src/deleted.py"`; orphan detected
4. **Orphan: glob assertion** — `glob` with `pattern="src/missing/**/*.py"`; zero matches; orphan detected, `use_glob=True`
5. **Orphan: grep with file glob (matching)** — `grep` with `file="src/**/*.py"`, files exist; no orphan, `use_glob=True`
6. **Orphan: grep with file glob (no match)** — `grep` with `file="src/nonexistent/**/*.py"`; orphan detected, `use_glob=True`
7. **Orphan: grep_absent with file glob** — `grep_absent` with `file="src/nonexistent/**/*.py"`; orphan detected via `_safe_glob()`, `assertion_type="grep_absent"`, `use_glob=True`
8. **Orphan: count with file glob** — `count` with `file="src/nonexistent/**/*.py"`; orphan detected via `_safe_glob()`, `assertion_type="count"`, `use_glob=True`
9. **Orphan: file_exists with star in path** — `file_exists` with `file="src/*.py"`; orphan detected via `_safe_resolve()` (literal path, NOT glob expanded), `use_glob=False`. Proves `file_exists` never dispatches through `_safe_glob()`.
10. **Orphan: all_of with grep children** — `all_of` with 2 `grep` children (literal), one missing; orphan for missing child, `assertion_type="grep"`
11. **Orphan: all_of with nested glob child** — `all_of` with `glob` child (zero matches) + `grep` child (exists); orphan for glob child, `use_glob=True`
12. **Orphan: all_of with grep_absent file-glob child** — `all_of` with `grep_absent` child `file="missing/**/*.py"` + `file_exists` child (exists); orphan for `grep_absent` child via `_safe_glob()`, `assertion_type="grep_absent"`, `use_glob=True`

### Authority Conflicts (3 tests — unchanged from v5)
13. **Conflict: same file, different aliases** — Spec A: `grep` with `file`, Spec B: `grep` with `target`; same section → conflict
14. **Conflict: composition child overlap** — Spec A: `grep`, Spec B: `all_of` with `grep` child → conflict
15. **Conflict: glob string match** — Spec A: `grep` with `file="src/**/*.py"`, Spec B: `count` with `file="src/**/*.py"` → conflict

### Provenance (2 tests — unchanged)
16. **Expired provisional** — Provisional spec with replacement implemented; expiration detected
17. **Duplicate detection** — 90% title token overlap; duplicate reported

---

*Submitted by: S287-Prime*
*Revision: v6 — addresses NO-GO bridge/gtkb-spec-pipeline-f8-010.md*
