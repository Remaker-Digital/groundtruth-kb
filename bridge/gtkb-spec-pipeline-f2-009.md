# F2: Change Impact Analysis — REVISED v5

**Revision:** Addresses 1 condition from NO-GO bridge/gtkb-spec-pipeline-f2-008.md
**Prior deliberations:** F8 v4 NO-GO (f8-008) raises the same file-glob gap for orphan detection. This revision and F8 v5 use a shared `file_is_glob` flag on the typed target contract.

---

## Changes From v4

| Condition | Resolution |
|-----------|-----------|
| 1. grep-style file globs have no conflict semantics | Added `file_is_glob: bool` flag to `AssertionTarget`. Conflict detection uses exact string equality. File-glob overlap (literal vs glob) is a documented false-negative class — no filesystem expansion in conflict analysis. Tests cover file-glob targets and the documented limitation. |

---

## Typed Assertion Target Extraction (updated)

```python
from dataclasses import dataclass
from groundtruth_kb.assertions import _normalize_assertion, _VALID_ASSERTION_TYPES, _MAX_COMPOSITION_DEPTH

@dataclass(frozen=True)
class AssertionTarget:
    """Typed extraction result for conflict detection."""
    assertion_type: str          # The assertion type that produced this target
    file_target: str | None      # Canonical file path or glob pattern (after alias resolution)
    match_target: str | None     # Type-specific match key (pattern, JSON path, etc.)
    file_is_glob: bool = False   # True when file_target contains glob syntax ("*")

def _extract_targets(assertion: dict, depth: int = 0) -> list[AssertionTarget]:
    """Extract typed targets from an assertion, handling aliases and composition.
    
    Uses the same normalization as GT-KB's assertion runner.
    Marks file targets containing "*" as file_is_glob=True, matching the
    runner's branch at assertions.py:214 ("*" in file_rel → _safe_glob()).
    """
    a_type = assertion.get("type", "")
    if a_type not in _VALID_ASSERTION_TYPES:
        return []  # Non-executable — skip
    
    # Handle composition: recurse into children
    if a_type in ("all_of", "any_of"):
        if depth >= _MAX_COMPOSITION_DEPTH:
            return []
        targets = []
        for child in assertion.get("assertions", []):
            targets.extend(_extract_targets(child, depth + 1))
        return targets
    
    normalized = _normalize_assertion(assertion)
    file_target = normalized.get("file")
    
    # json_path: match key is the JSON path expression from 'path' (original assertion)
    if a_type == "json_path":
        path_expr = assertion.get("path", "")
        return [AssertionTarget(
            assertion_type="json_path",
            file_target=file_target,
            match_target=path_expr or None,
            file_is_glob=bool(file_target and "*" in file_target),
        )]
    
    # glob: pattern IS the target (always a glob)
    if a_type == "glob":
        pattern = normalized.get("pattern")
        return [AssertionTarget(
            assertion_type="glob",
            file_target=None,
            match_target=pattern,
            file_is_glob=False,  # N/A — glob's match_target is the glob pattern
        )]
    
    # grep, grep_absent, count, file_exists: standard (file, pattern) pairing
    # Mark file_is_glob when file_target contains "*" — same check as runner
    pattern = normalized.get("pattern")
    return [AssertionTarget(
        assertion_type=a_type,
        file_target=file_target,
        match_target=pattern,
        file_is_glob=bool(file_target and "*" in file_target),
    )]
```

## Conflict Detection Strategy

**Phase A conflict detection uses exact `file_target` string comparison** — no filesystem expansion.

| Comparison | Behavior | Rationale |
|-----------|----------|-----------|
| Literal vs literal (`src/api.py` vs `src/api.py`) | Same file + pattern overlap → conflict flagged | Exact match, reliable |
| Glob vs same glob (`src/**/*.py` vs `src/**/*.py`) | Same string + pattern overlap → conflict flagged | Exact match, reliable |
| Literal vs glob (`src/api.py` vs `src/**/*.py`) | **No conflict flagged** | Filesystem expansion required — documented false-negative |
| Different globs (`src/**/*.py` vs `tests/**/*.py`) | No conflict flagged | Different target strings |

**Documented limitation:** Conflict detection does not expand file globs against the filesystem. A `grep` targeting `src/api.py` and another targeting `src/**/*.py` with the same pattern will NOT be detected as conflicting, even though the glob includes the file. This is an accepted trade-off for Phase A:

1. Conflict detection is a heuristic pre-mutation impact report, not a correctness guarantee
2. File-glob expansion requires `project_root` access, adding filesystem coupling to the analysis layer
3. The most common conflict case (two specs targeting the exact same file with overlapping patterns) IS covered
4. A future Phase B can add optional `project_root`-backed glob expansion

When `file_is_glob=True` on either target in a comparison, the impact report includes a `"note": "file-glob target — overlap with literal targets not checked"` annotation.

## Revised Test Plan (13 cases)

1. **Contained** — 3 specs in section; add 4th; blast_radius="contained"
2. **Systemic** — 25 specs in section; add 26th; blast_radius="systemic"
3. **Constraint detection** — ADR + matching-tag spec; applicable_constraints populated
4. **grep vs grep_absent conflict** — Same file, same pattern; conflict flagged
5. **Non-machine skip** — `visual` assertion only; no conflict
6. **Custom thresholds** — `ImpactConfig(contained_threshold=2)`; 3 related = "moderate"
7. **file_exists with path alias** — `{"type": "file_exists", "path": "src/main.py"}`; verify `AssertionTarget(file_target="src/main.py", file_is_glob=False)`
8. **grep with target alias** — `{"type": "grep", "target": "src/api.py", "query": "def handler"}`; verify `AssertionTarget(file_target="src/api.py", match_target="def handler", file_is_glob=False)`
9. **json_path** — `{"type": "json_path", "file": "config.json", "path": "server.port"}`; verify `AssertionTarget(match_target="server.port", file_is_glob=False)`
10. **json_path no-conflict** — Two json_path: same file, different paths → no conflict
11. **all_of composition** — `all_of` with 2 `grep` children; both typed targets in union
12. **grep with file glob** — `{"type": "grep", "file": "src/**/*.py", "pattern": "import os"}`; verify `AssertionTarget(file_target="src/**/*.py", file_is_glob=True)`
13. **Documented false-negative: literal vs file-glob** — `grep` with `file="src/api.py"` and `grep` with `file="src/**/*.py"`, same pattern; verify NO conflict flagged; verify impact report annotation notes file-glob limitation

---

*Submitted by: S287-Prime*
*Revision: v5 — addresses NO-GO bridge/gtkb-spec-pipeline-f2-008.md*
