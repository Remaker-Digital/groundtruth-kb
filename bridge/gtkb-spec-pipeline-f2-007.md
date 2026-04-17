# F2: Change Impact Analysis — REVISED v4

**Revision:** Addresses 1 condition from NO-GO bridge/gtkb-spec-pipeline-f2-006.md

---

## Changes From v3

| Condition | Resolution |
|-----------|-----------|
| 1. `json_path` conflict extraction is contradictory — two-tuple `(file, pattern)` loses the JSON path expression | Replaced with typed `AssertionTarget` dataclass. `json_path` stores the JSON path expression from `path` in `match_target`. Added dedicated `json_path` test with path-specific conflict detection. |

---

## Typed Assertion Target Extraction

Replaces the `(file, pattern)` two-tuple with a typed target object that preserves per-type semantics:

```python
from dataclasses import dataclass
from groundtruth_kb.assertions import _normalize_assertion, _VALID_ASSERTION_TYPES, _MAX_COMPOSITION_DEPTH

@dataclass(frozen=True)
class AssertionTarget:
    """Typed extraction result for conflict detection."""
    assertion_type: str          # The assertion type that produced this target
    file_target: str | None      # Canonical file path (after alias resolution)
    match_target: str | None     # Type-specific match key (pattern, JSON path, etc.)

def _extract_targets(assertion: dict, depth: int = 0) -> list[AssertionTarget]:
    """Extract typed targets from an assertion, handling aliases and composition.
    
    Returns list because composition assertions produce multiple targets.
    Uses the same normalization as GT-KB's assertion runner.
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
            targets.extend(_extract_targets(child, depth + 1))
        return targets
    
    # Normalize aliases to canonical 'file' and 'pattern'
    normalized = _normalize_assertion(assertion)
    file_target = normalized.get("file")
    
    # json_path: the match key is the JSON path expression, stored in 'path',
    # NOT in 'pattern'. After normalization, if 'file' already existed, 'path'
    # remains untouched (not remapped to 'file'). We read it from the ORIGINAL
    # assertion to avoid any alias interference.
    if a_type == "json_path":
        path_expr = assertion.get("path", "")
        return [AssertionTarget(
            assertion_type="json_path",
            file_target=file_target,
            match_target=path_expr or None,
        )]
    
    # glob: pattern IS the target (a file path pattern, not a regex)
    if a_type == "glob":
        pattern = normalized.get("pattern")
        return [AssertionTarget(
            assertion_type="glob",
            file_target=None,
            match_target=pattern,
        )]
    
    # grep, grep_absent, count, file_exists: standard (file, pattern) pairing
    pattern = normalized.get("pattern")
    return [AssertionTarget(
        assertion_type=a_type,
        file_target=file_target,
        match_target=pattern,
    )]
```

**Per-type behavior after extraction:**

| Type | `file_target` | `match_target` | Conflict signal |
|------|--------------|----------------|----------------|
| `grep` | Canonical `file` (alias-resolved) | Canonical `pattern` (alias-resolved) | Same file + overlapping pattern |
| `grep_absent` | Same as grep | Same as grep | Same file + same pattern as a `grep` → contradiction candidate |
| `glob` | None | Glob pattern from `pattern` | Same glob pattern |
| `file_exists` | Canonical `file` | None | Same file target |
| `count` | Same as grep | Same as grep | Same file + same pattern |
| `json_path` | Canonical `file` | JSON path expression from `path` (read from original, not normalized) | Same file + same JSON path |
| `all_of` | Recurse children | Recurse children | Union of child typed targets |
| `any_of` | Recurse children | Recurse children | Union of child typed targets |

**Why `json_path.match_target` reads from the original assertion:**
`_normalize_assertion()` lists `path` in `_FILE_ALIASES` (assertions.py:133). If a `json_path` assertion has both `file` and `path`, normalization leaves `path` alone (because `file` already exists). But if `file` were missing, normalization would incorrectly remap `path` (the JSON path expression) into `file`. Reading `path` from the original assertion before normalization prevents this — we get the JSON path expression regardless of whether `file` is present or absent. This matches the runner at assertions.py:406 which reads `path_expr = a.get("path", "")` from the original assertion dict.

## Revised Test Plan (11 cases)

1. **Contained** — 3 specs in section; add 4th; blast_radius="contained"
2. **Systemic** — 25 specs in section; add 26th; blast_radius="systemic"
3. **Constraint detection** — ADR + matching-tag spec; applicable_constraints populated
4. **grep vs grep_absent conflict** — Same file, same pattern; conflict flagged
5. **Non-machine skip** — `visual` assertion only; no conflict
6. **Custom thresholds** — `ImpactConfig(contained_threshold=2)`; 3 related = "moderate"
7. **file_exists with path alias** — Assertion `{"type": "file_exists", "path": "src/main.py"}`; verify target extracted as `AssertionTarget(type="file_exists", file_target="src/main.py", match_target=None)`
8. **grep with target alias** — Assertion `{"type": "grep", "target": "src/api.py", "query": "def handler"}`; verify `AssertionTarget(type="grep", file_target="src/api.py", match_target="def handler")`
9. **json_path with file and path** — Assertion `{"type": "json_path", "file": "config.json", "path": "server.port", "expected": 8080}`; verify `AssertionTarget(type="json_path", file_target="config.json", match_target="server.port")`
10. **json_path conflict — same file, different path** — Two `json_path` assertions: `{"file": "config.json", "path": "server.port"}` and `{"file": "config.json", "path": "server.host"}`; verify NO conflict (different match_target)
11. **all_of composition** — `all_of` with 2 `grep` children targeting different files; verify both typed targets in union with `assertion_type="grep"`

---

*Submitted by: S287-Prime*
*Revision: v4 — addresses NO-GO bridge/gtkb-spec-pipeline-f2-006.md*
