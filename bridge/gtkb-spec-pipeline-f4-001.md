# F4: Cross-Cutting Constraint Propagation — Implementation Proposal

**Feature:** F4 — Cross-Cutting Constraint Propagation
**Target repo:** groundtruth-kb
**Tracker:** DOC-GTKB-SPEC-PIPELINE
**Corruption vectors addressed:** P5 (cross-cutting specs not applied uniformly)
**Dependencies:** F1 (needs `type`, `affected_by` columns), F2 (uses impact analysis for initial propagation)
**Prior deliberations:** DELIB-0706 (GT-KB scope), DELIB-0708 (structured interview — foundational before dependent)

---

## Problem Statement

Cross-cutting specifications — architecture decisions (ADRs) and design constraints (DCLs) — apply to many functional specs but have no mechanism to propagate their constraints automatically. In Agent Red:

- 8 ADRs and 5 DCLs exist, governing decisions like per-agent containers, zero-knowledge boundaries, RBAC architecture, and transport dispatch
- None of these automatically propagate to the specs they constrain
- When a new API endpoint was added during normal feature work, the AI only applied ZK constraints if it happened to recall ADR-006 — which is context-dependent and unreliable
- The owner observed "substantial defects and bad outcomes" when ZK was introduced because existing specs and implementations didn't account for it

The core issue: cross-cutting constraints are **stored** but not **enforced**. They exist as specs in the KB but have no active role in the spec creation or modification workflow.

## Proposed Solution

An **automatic constraint propagation system** that maintains the relationship between cross-cutting specs (ADR/DCL) and the functional specs they constrain.

### Mechanism: Scope Declarations on ADR/DCL Specs

Each ADR/DCL declares the scope of its applicability using the enriched schema from F1:

```python
# Example: ADR-006 (zero-knowledge boundary)
{
    "id": "ADR-006",
    "type": "architecture_decision",
    "constraints": {
        "affected_sections": ["API", "AUTH", "ADMIN_UI", "CONVERSATIONS", "KNOWLEDGE_BASE"],
        "affected_tags": ["security", "multi_tenant", "provisioning"],
        "affected_scopes": ["backend", "Admin", "API"],
        "propagation_rule": "all_matching"  # or "explicit_only"
    }
}
```

### Propagation Function: `propagate_constraints(constraint_id)`

When an ADR/DCL is created or modified:

1. **Identify affected specs** — Query all current specs whose section, scope, or tags match the constraint's declared scope
2. **Update `affected_by` fields** — Add the constraint ID to each affected spec's `affected_by` JSON array
3. **Return propagation report** — List of all specs that were linked, any specs that were already linked, and any specs that were removed from linkage (if scope narrowed)

### Reverse Propagation: `check_constraints(spec_id)`

When a functional spec is created or modified:

1. **Find applicable constraints** — Query all ADR/DCL specs whose scope declarations match this spec's section/scope/tags
2. **Return applicable constraints** — List of constraint IDs, titles, and their assertion summaries
3. **This feeds into F2's impact analysis** — The constraints are included in the ImpactReport

### Assertion Inheritance

When a DCL has machine-checkable assertions, those assertions apply to all affected specs. The propagation system does NOT copy assertions into functional specs (that would create maintenance nightmares). Instead:

- `validate_dcl_constraints()` (existing method in GT-KB) is extended to check all specs in the DCL's scope
- If a functional spec's implementation violates a DCL assertion, the violation is reported against the functional spec with a reference to the DCL
- This gives the AI the signal: "your implementation of SPEC-1234 violates DCL-002 (no mainline in-process dispatch)"

## Counterfactual Test

**If F4 had existed when ADR-006 (ZK) was created:**
- Creating ADR-006 would have triggered `propagate_constraints("ADR-006")` with affected_sections=["API", "AUTH", ...] and affected_tags=["security", "multi_tenant"]
- Every existing spec in those sections (hundreds) would have gotten `affected_by: ["ADR-006"]` added
- When new API endpoints were later created, `check_constraints()` would have returned ADR-006 as an applicable constraint
- The AI would have been forced to acknowledge: "this new endpoint is constrained by the ZK boundary" before implementing it
- DCL assertions for ZK would have run against all affected specs, catching violations at spec-check time rather than after implementation

**Estimated defect prevention:** The ZK redesign (S270+) involved dozens of defects. If even half were caused by "forgot to apply ZK to this endpoint," F4 would have prevented them by making the constraint visible at the point of spec creation.

## API Design

```python
class KnowledgeDB:
    def propagate_constraints(
        self,
        constraint_id: str,  # ADR or DCL spec ID
        dry_run: bool = False,
    ) -> PropagationReport:
        """Propagate a cross-cutting constraint to all matching specs."""
        ...
    
    def check_constraints(
        self,
        spec_id: str = None,
        section: str = None,
        scope: str = None,
        tags: list[str] = None,
    ) -> list[dict]:
        """Return all constraints applicable to the given spec or scope."""
        ...
    
    def get_constraint_coverage(self) -> dict:
        """Report on which specs are covered by constraints and which are not."""
        ...

@dataclass
class PropagationReport:
    constraint_id: str
    affected_specs: list[str]     # Specs that were linked
    already_linked: list[str]     # Specs that were already linked
    removed: list[str]            # Specs that lost linkage (scope narrowed)
    unlinked_in_scope: list[str]  # Specs in scope but manually excluded
```

## Test Plan

1. **Basic propagation** — Create ADR with scope, create 3 specs in scope and 2 outside; verify only 3 get affected_by populated
2. **Reverse check** — Create spec in constrained section; verify check_constraints returns the ADR
3. **Scope change** — Modify ADR scope to narrow; verify removed specs lose the linkage
4. **DCL assertion inheritance** — Create DCL with grep assertion, create spec in scope with violating code; verify assertion failure references the DCL
5. **Dry run** — Verify dry_run=True returns the report without modifying any specs
6. **Coverage report** — Verify coverage report correctly identifies specs in constrained sections without linkage

## Implementation Sequence

1. Add `constraints` scope declaration schema to ADR/DCL specs (piggybacks on F1's `constraints` column)
2. Implement `propagate_constraints()` with section/scope/tag matching
3. Implement `check_constraints()` for reverse lookup
4. Extend `validate_dcl_constraints()` to check all specs in scope
5. Implement `get_constraint_coverage()` for dashboard
6. Write tests (6 cases above)
7. Document constraint declaration format in GT-KB docs

## Risks and Mitigations

| Risk | Mitigation |
|------|-----------|
| Over-propagation: too many specs linked to broad constraints | Scope declarations must be explicit; `propagation_rule=all_matching` vs `explicit_only` gives control |
| Performance: propagating to hundreds of specs | Batch UPDATE with single query; affected_by is append-only JSON |
| Stale linkages after spec retirement | Retirement triggers unlinking from all constraint affected_by lists |

## Open Questions for Codex Review

1. Should propagation be automatic on ADR/DCL create/update, or require explicit call?
2. Should there be a mechanism to exclude specific specs from a constraint's scope (manual override)?
3. Should constraint coverage be a quality gate dimension (D6 in F3)?
4. How should conflicting constraints be handled (two ADRs with overlapping scope and contradictory assertions)?

---

*Submitted by: S286-Prime*
*Date: 2026-04-12*
*Tracker: DOC-GTKB-SPEC-PIPELINE, Feature F4*
