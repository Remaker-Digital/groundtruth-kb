# F2: Change Impact Analysis — REVISED v6

**Revision:** Addresses 1 condition from NO-GO bridge/gtkb-spec-pipeline-f2-010.md

---

## Changes From v5

| Condition | Resolution |
|-----------|-----------|
| 1. File-glob test coverage omits `grep_absent` and `count` | Added tests 14 (`grep_absent` file glob) and 15 (`count` file glob). Test 13 (false-negative) documented as type-agnostic with shared-extraction-helper justification. |

---

## Design (unchanged from v5)

All Phase A semantics, typed `AssertionTarget` with `file_is_glob`, `json_path` preservation, exact-string conflict comparison, and documented false-negative class are unchanged. Only the test plan is expanded.

**Why the same extraction path covers all grep-style types:** `_extract_targets()` has a single code path for `grep`, `grep_absent`, `count`, and `file_exists` (the "standard (file, pattern) pairing" branch at the end of the function). All four types go through `_normalize_assertion()` → `normalized.get("file")` → `"*" in file_target` check → `AssertionTarget(file_is_glob=...)`. There is no type-specific branching for these types in extraction — they share the identical code path. The per-type tests below prove that each type is correctly handled by this shared path.

## Revised Test Plan (15 cases)

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
12. **grep with file glob** — `{"type": "grep", "file": "src/**/*.py", "pattern": "import os"}`; verify `AssertionTarget(file_target="src/**/*.py", match_target="import os", file_is_glob=True)`
13. **Documented false-negative: literal vs file-glob** — `grep` with `file="src/api.py"` and `grep` with `file="src/**/*.py"`, same pattern; verify NO conflict flagged; verify annotation notes file-glob limitation. **Type-agnostic justification:** This test uses `grep` but the comparison logic operates on `AssertionTarget` objects, not assertion dicts — the `file_is_glob` annotation and exact-string comparison are type-independent. Tests 12, 14, 15 prove each grep-style type correctly sets `file_is_glob=True`.
14. **grep_absent with file glob** — `{"type": "grep_absent", "file": "src/**/*.py", "pattern": "import os"}`; verify `AssertionTarget(assertion_type="grep_absent", file_target="src/**/*.py", match_target="import os", file_is_glob=True)`
15. **count with file glob** — `{"type": "count", "file": "src/**/*.py", "pattern": "TODO"}`; verify `AssertionTarget(assertion_type="count", file_target="src/**/*.py", match_target="TODO", file_is_glob=True)`

---

*Submitted by: S287-Prime*
*Revision: v6 — addresses NO-GO bridge/gtkb-spec-pipeline-f2-010.md*
