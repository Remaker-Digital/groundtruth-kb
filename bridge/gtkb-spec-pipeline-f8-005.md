# F8: Provenance Reconciliation — REVISED v3

**Revision:** Addresses 2 conditions from NO-GO bridge/gtkb-spec-pipeline-f8-004.md

---

## Changes From v2

| Condition | Resolution |
|-----------|-----------|
| 1. Orphan detection misses assertion file aliases | Orphan detection now normalizes assertions via `_normalize_assertion()` (assertions.py:137) before checking file targets. Uses `_FILE_ALIASES` (`file`, `file_pattern`, `target`, `path`, `expected`) and `_PATTERN_ALIASES` (`pattern`, `query`). |
| 2. Composition behavior unspecified | `all_of`/`any_of` children are recursed (capped at `_MAX_COMPOSITION_DEPTH=3`) to extract all file targets. No blind spots for executable composition assertions. |

---

## Revised Orphan Detection

```python
from groundtruth_kb.assertions import (
    _normalize_assertion,
    _VALID_ASSERTION_TYPES,
    _MAX_COMPOSITION_DEPTH,
)

def _extract_file_targets(assertion: dict, depth: int = 0) -> list[str]:
    """Extract all file targets from an assertion, handling aliases and composition.
    
    Uses the same normalization as GT-KB's assertion runner.
    Returns list of canonical file paths (after alias resolution).
    """
    a_type = assertion.get("type", "")
    
    if a_type not in _VALID_ASSERTION_TYPES:
        return []  # Non-executable — skip
    
    # Handle composition: recurse into children
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
    
    if file_target:
        return [file_target]
    
    # glob uses pattern as the target (it's a file path pattern, not a regex)
    if a_type == "glob":
        pattern = normalized.get("pattern")
        if pattern:
            return [pattern]  # Treated as glob pattern for existence check
    
    return []  # No file target found


def find_orphaned_specs(kdb, project_root: Path) -> list[dict]:
    """Find specs whose executable assertion file targets no longer exist.
    
    Args:
        project_root: Passed to _safe_resolve() for path resolution.
                      Same parameter as run_all_assertions(db, project_root, ...).
    """
    orphans = []
    for spec in kdb.list_specs():
        assertions = spec.get("assertions_parsed") or []
        for assertion in assertions:
            targets = _extract_file_targets(assertion)
            for target in targets:
                a_type = assertion.get("type", "")
                if a_type == "glob":
                    # Glob: check if pattern matches any files
                    matches = _safe_glob(target, project_root)
                    if matches is not None and len(matches) == 0:
                        orphans.append({
                            "spec_id": spec["id"],
                            "assertion_type": a_type,
                            "target": target,
                            "reason": "glob pattern matches zero files",
                        })
                else:
                    # File path: check if resolved path exists
                    resolved = _safe_resolve(target, project_root)
                    if resolved is not None and not resolved.exists():
                        orphans.append({
                            "spec_id": spec["id"],
                            "assertion_type": a_type,
                            "target": target,
                            "reason": "file does not exist",
                        })
                    # If _safe_resolve returns None (path escape), skip — not an orphan,
                    # just an invalid path that the assertion runner would also reject.
    return orphans
```

**Key behaviors:**
- `file_exists` with `path` alias → normalized to `file` → checked
- `grep` with `target` alias → normalized to `file` → checked
- `grep` with `query` alias → normalized to `pattern` (no file target) → no orphan check for pattern-only assertions
- `all_of` with 2 `grep` children → recurse, extract both file targets, check both
- Non-executable types (`visual`, `manual`, etc.) → skipped entirely
- Path escapes (parent traversal) → `_safe_resolve` returns None → skipped (not an orphan)

## Revised Test Plan (9 cases)

1. **Authority conflict** — stated + inferred, same section, overlapping assertion file; conflict detected
2. **No false conflict** — Different sections; no conflict
3. **Orphan: direct file** — `grep` with `file="src/deleted.py"`; file doesn't exist; orphan detected
4. **Orphan: path alias** — `file_exists` with `path="src/deleted.py"`; orphan detected (alias resolved)
5. **Orphan: target alias** — `grep` with `target="src/deleted.py"`; orphan detected
6. **Orphan: glob pattern** — `glob` with `pattern="src/missing/**/*.py"`; zero matches; orphan detected
7. **Orphan: all_of composition** — `all_of` with 2 `grep` children, one file exists, one doesn't; orphan detected for missing file only
8. **Expired provisional** — Provisional spec with replacement implemented; expiration detected
9. **Duplicate detection** — 90% title token overlap; duplicate reported

---

*Submitted by: S286-Prime*
*Revision: v3 — addresses NO-GO bridge/gtkb-spec-pipeline-f8-004.md*
