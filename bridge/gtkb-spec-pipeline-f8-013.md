# F8: Provenance Reconciliation — REVISED v7

**Revision:** Addresses 1 condition from NO-GO bridge/gtkb-spec-pipeline-f8-012.md

---

## Changes From v6

| Condition | Resolution |
|-----------|-----------|
| 1. Plain-text (non-dict) assertions can crash reconciliation with `AttributeError` | Added `isinstance(assertion, dict)` guard at the top of `_extract_file_targets()` and in composition recursion. Added 3 tests for plain-text and non-machine assertions. |

---

## Design (unchanged from v6)

Type-specific dispatch rules, `_GLOB_CAPABLE_TYPES`, `TypedFileTarget` dataclass, orphan detection, and authority-conflict detection are all unchanged. Only the extraction entry guard and test plan are updated.

## Typed File Target Extraction (updated guard)

```python
from dataclasses import dataclass
from groundtruth_kb.assertions import (
    _normalize_assertion,
    _VALID_ASSERTION_TYPES,
    _MAX_COMPOSITION_DEPTH,
)

_GLOB_CAPABLE_TYPES = frozenset({"grep", "grep_absent", "count"})

@dataclass(frozen=True)
class TypedFileTarget:
    assertion_type: str
    target: str
    use_glob: bool

def _extract_file_targets(assertion, depth: int = 0) -> list[TypedFileTarget]:
    """Extract all typed file targets from an assertion.
    
    Mirrors runner skip semantics (assertions.py:551-554): non-dict assertions
    are plain-text human notes and are silently skipped. This matches
    assertion_schema.py:60-62 which treats non-dict entries as valid notes.
    """
    # Guard: plain-text assertions are human notes — skip silently
    if not isinstance(assertion, dict):
        return []
    
    a_type = assertion.get("type", "")
    
    if a_type not in _VALID_ASSERTION_TYPES:
        return []
    
    # Composition: recurse into children, preserving child types
    if a_type in ("all_of", "any_of"):
        if depth >= _MAX_COMPOSITION_DEPTH:
            return []
        targets = []
        for child in assertion.get("assertions", []):
            # Guard also protects composition children — a plain-text child
            # in an all_of/any_of list is silently skipped, same as runner
            targets.extend(_extract_file_targets(child, depth + 1))
        return targets
    
    normalized = _normalize_assertion(assertion)
    file_target = normalized.get("file")
    
    # glob assertion: always glob dispatch
    if a_type == "glob":
        pattern = normalized.get("pattern")
        if pattern:
            return [TypedFileTarget(assertion_type="glob", target=pattern, use_glob=True)]
        return []
    
    # json_path: always literal resolution
    if a_type == "json_path":
        if file_target:
            return [TypedFileTarget(assertion_type="json_path", target=file_target, use_glob=False)]
        return []
    
    # file_exists: always literal resolution
    if a_type == "file_exists":
        if file_target:
            return [TypedFileTarget(assertion_type="file_exists", target=file_target, use_glob=False)]
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

**Key change:** The type hint for `assertion` is removed (was `dict`, now untyped) to accept any value. The `isinstance` guard at line 1 of the function body handles all non-dict cases including strings, ints, lists, and None. The recursive call for composition children passes through the same guard, so plain-text children inside `all_of`/`any_of` are also safely skipped.

## Revised Test Plan (20 cases)

### Orphan Detection (12 tests — unchanged from v6)
1-12: Same as v6 (grep literal, path alias, target alias, glob assertion, grep file-glob match/no-match, grep_absent file-glob, count file-glob, file_exists with star, all_of with grep/glob/grep_absent children)

### Plain-Text Assertion Safety (3 tests — NEW in v7)
13. **Top-level plain-text assertion** — Spec with `assertions_parsed = ["This spec must be visually reviewed", {"type": "grep", "file": "src/api.py", "pattern": "def handler"}]`; orphan detection processes the spec without error; only the `grep` assertion produces a file target; the plain-text string is silently skipped
14. **Composition with plain-text child** — Spec with `{"type": "all_of", "assertions": ["Manual check: verify layout", {"type": "grep", "file": "src/deleted.py", "pattern": "..."}]}`; extraction returns only the `grep` child's target; plain-text child is skipped; orphan detected for missing file
15. **Non-machine dict child** — Spec with `{"type": "visual", "description": "Check color contrast"}`; extraction returns empty list (type not in `_VALID_ASSERTION_TYPES`); no crash, no orphan

### Authority Conflicts (3 tests — unchanged from v6)
16-18: Same as v6 (alias overlap, composition overlap, glob string match)

### Provenance (2 tests — unchanged)
19. **Expired provisional** — Provisional spec with replacement implemented; expiration detected
20. **Duplicate detection** — 90% title token overlap; duplicate reported

---

*Submitted by: S287-Prime*
*Revision: v7 — addresses NO-GO bridge/gtkb-spec-pipeline-f8-012.md*
