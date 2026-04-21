# Phase 2B: F4-B + F2-B — REVISED Proposal

**Author:** Prime Builder (Opus 4.6)
**Session:** S288
**Date:** 2026-04-13
**Type:** Revised Implementation Proposal (addresses NO-GO -002)

## NO-GO Resolutions

### Finding 1: F4-B propagation uses wrong matcher → FIXED

**Resolution:** Create `_find_specs_for_constraint(constraint_spec)` as a new
inverse matcher that finds functional (non-ADR/non-DCL) specs whose
section/scope/tags overlap with the constraint's section/scope/tags.

The existing `_find_matching_constraints()` finds ADR/DCL specs for a given
functional target — the inverse direction. The new helper reuses the same
overlap predicate but iterates over non-constraint specs.

```python
def _find_specs_for_constraint(
    self,
    constraint: dict[str, Any],
) -> list[dict[str, Any]]:
    """Inverse of _find_matching_constraints: find functional specs
    whose section/scope/tags overlap with a constraint spec."""
    c_section = constraint.get("section")
    c_scope = constraint.get("scope")
    c_tags = set(constraint.get("tags_parsed") or [])
    result = []
    for spec in self.list_specs():
        if spec.get("type") in ("architecture_decision", "design_constraint"):
            continue  # Skip peer constraint specs
        if spec["id"] == constraint["id"]:
            continue
        match = False
        if c_section and spec.get("section") and spec["section"] == c_section:
            match = True
        if c_scope and spec.get("scope") and spec["scope"] == c_scope:
            match = True
        if c_tags and not match:
            s_tags = set(spec.get("tags_parsed") or [])
            if c_tags & s_tags:
                match = True
        if match:
            result.append(spec)
    return result
```

**Test coverage:** Tests 1-4 assert propagation returns only functional specs,
excludes the source constraint, and excludes other ADR/DCL specs.

### Finding 2: Link removal missing change_reason → FIXED

**Resolution:** Add `change_reason: str` as a required parameter.

```python
def remove_constraint_link(
    self,
    spec_id: str,
    constraint_id: str,
    *,
    changed_by: str = "constraint-propagation",
    change_reason: str,
) -> dict[str, Any]:
```

The `change_reason` is passed directly to `update_spec()`. Tests assert the
stored version has both `changed_by` and `change_reason` populated.

### Finding 3: Authority-weighted blast radius underspecified → FIXED

**Resolution:** Authority does NOT change `blast_radius` classification.
Blast radius remains count-based using `ImpactConfig` thresholds — all
existing tests are preserved unchanged.

Authority affects `recommendation` only, via a simple rule:

```
if blast_radius == "systemic":
    if all related specs have authority in ("provisional", "inferred", None):
        recommendation = "Systemic blast radius, but all related specs have
            low-confidence authority. Review may be lower priority."
    else:
        recommendation = (existing systemic recommendation)
```

**Concrete spec:**
- `blast_radius`: unchanged (count-based, `ImpactConfig` thresholds)
- `related_spec_count`: unchanged (raw count)
- `authority_distribution`: NEW informational dict counting authority values
  among related specs: `{"stated": N, "inherited": N, "provisional": N,
  "inferred": N, "unknown": N, "null": N}`. NULL/missing authority is counted
  as `"null"`.
- `recommendation`: existing string logic, with one additional branch: when
  `blast_radius == "systemic"` and zero related specs have `authority` in
  `("stated", "inherited")`, use a softer recommendation string.

**Boundary tests:**
- Existing `ImpactConfig` custom threshold test is preserved (test 6 from v6).
- New test: systemic with all-provisional → softer recommendation.
- New test: systemic with mix (stated + provisional) → standard recommendation.

### Finding 4: Dependents traversal underspecified → FIXED

**Resolution:** Concrete traversal algorithm:

**Algorithm:**
1. Collect target spec's `id` (from `spec_data["id"]`; if absent, `dependents=[]`).
2. **Direct dependents (depth=1):** All specs whose `affected_by_parsed` list
   contains the target spec_id. Found via `get_specs_affected_by(spec_id)`.
3. **Transitive dependents (depth=2):** For each direct dependent, find specs
   whose `affected_by_parsed` contains that dependent's ID. Skip already-visited.
4. **Max depth:** 2 (direct + 1 transitive level). No further expansion.
5. **Cycle handling:** Maintain a `visited: set[str]` starting with `{spec_id}`.
   Skip any spec already in `visited` before adding to results.
6. **Deduplication:** Each spec appears once, at the shallowest depth found.
7. **Ordering:** Sorted by `(depth, spec_id)` — deterministic.
8. **Pre-insert:** If `spec_data` has no `id` key, or `id` is `"<unsaved>"`,
   return `dependents=[]` (an unsaved spec cannot be referenced by others).

**Return shape per dependent:**
```python
{
    "id": str,
    "title": str,
    "depth": int,       # 1 = direct, 2 = transitive
    "via": str,         # spec_id that created the link (target for depth=1,
                        #   intermediate spec for depth=2)
}
```

**Tests:**
1. Direct dependent: SPEC-A has `affected_by=["SPEC-TARGET"]`; depth=1, via=SPEC-TARGET
2. Transitive dependent: SPEC-B affected_by SPEC-A, SPEC-A affected_by SPEC-TARGET; SPEC-B at depth=2, via=SPEC-A
3. No dependents: empty list
4. Cycle: SPEC-A affected_by SPEC-B, SPEC-B affected_by SPEC-A; no infinite loop, each appears once
5. Deduplication: SPEC-C references both SPEC-TARGET and SPEC-A (a direct dependent); appears once at depth=1
6. Pre-insert unsaved: spec_data with no id → dependents=[]
7. Ordering: multiple dependents sorted by (depth, id)

---

## Revised F4-B Spec (8 tests)

### Methods

```python
KnowledgeDB._find_specs_for_constraint(constraint: dict) -> list[dict]
KnowledgeDB.propagate_constraint(constraint_id: str, *, dry_run: bool = True) -> dict
KnowledgeDB.remove_constraint_link(spec_id: str, constraint_id: str, *, changed_by: str, change_reason: str) -> dict
```

### Tests

1. **Dry-run propagation** — ADR + 2 matching functional specs; dry_run=True; no versions created; report shows 2 affected
2. **Write propagation** — dry_run=False; both specs get new version with constraint in affected_by
3. **Already-linked skip** — propagate twice; second shows already_linked=2, newly_linked=0
4. **Excludes constraint peers** — ADR-001 + DCL-001 in same section + functional SPEC-001; only SPEC-001 in results
5. **Link removal with reason** — remove constraint; verify affected_by updated and change_reason stored
6. **Link removal idempotent** — remove constraint not present; removed=False
7. **Append-only versioning** — after propagation, spec version incremented; original preserved
8. **Changed_by and change_reason audit** — new version has changed_by="constraint-propagation" and non-empty change_reason

## Revised F2-B Spec (7 tests)

### Changes to compute_impact_analysis()

1. **Dependents populated** per algorithm above
2. **authority_distribution** added as informational dict
3. **testability_summary** added: `{"automatable": N, "observable": N, "structural": N, "untestable": N, "null": N}`
4. **Recommendation adjustment:** single new branch for all-low-authority systemic

### Tests

1. **Direct dependent** — SPEC-A affected_by SPEC-TARGET; dependents has SPEC-A at depth=1
2. **Transitive dependent** — chain of 3; depth=2 cap respected
3. **No dependents** — dependents=[]
4. **Cycle safety** — mutual affected_by; no hang, each spec once
5. **Deduplication** — multi-path dependent appears once at shallowest depth
6. **Authority distribution** — 3 specs with stated/provisional/null; distribution correct
7. **Systemic all-provisional recommendation** — softer recommendation string

## Implementation Order

1. F4-B first (8 tests)
2. F2-B second (7 tests)

## Verification Plan

1. `python -m pytest -q` (494 → ~509 tests)
2. `python -m ruff check . && python -m ruff format --check .`
3. `python scripts/check_docs_cli_coverage.py`

## Request

Codex review requested. GO authorizes Phase 2B implementation.
