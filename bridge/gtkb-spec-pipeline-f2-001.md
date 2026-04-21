# F2: Change Impact Analysis — Implementation Proposal

**Feature:** F2 — Change Impact Analysis
**Target repo:** groundtruth-kb
**Tracker:** DOC-GTKB-SPEC-PIPELINE
**Corruption vectors addressed:** P2 (chat misinterpretation causing dramatic spec changes), P5 (cross-cutting specs not applied uniformly)
**Dependencies:** F1 (needs enriched schema for authority tiers and affected_by linkages)
**Prior deliberations:** DELIB-0708 (structured interview vision), DELIB-0710 (quality ranking)

---

## Problem Statement

When a spec is created or modified in the current GT-KB, there is no computation of what else in the corpus is affected. The operation is atomic — the spec changes, and nothing else happens. This enables two corruption vectors:

**P2 — Dramatic unwarned spec changes:** In Agent Red, the owner observed that casual chat language was misinterpreted, causing core system elements to be ripped and replaced. The mechanism: a new requirement triggers spec creation, which triggers implementation, which touches code governed by other specs — but the downstream impact was never previewed. By the time the damage was visible, multiple specs and implementations had been modified.

**P5 — Cross-cutting specs not uniformly applied:** SPEC-1843 (zero-knowledge operator boundary) affected every API endpoint, database query, and log statement in Agent Red. But when new endpoints were added or existing ones modified, the ZK constraint was only considered if the developer (AI) happened to think about it. There was no automatic check.

**Agent Red evidence:**
- The ZK architecture redesign (S270+) required touching dozens of specs and caused "substantial defects and bad outcomes" (owner quote, S286)
- ADR-006 (zero-knowledge boundary) has no explicit linkage to the hundreds of specs it constrains
- 8 ADRs and 5 DCLs exist but none automatically propagate their constraints to affected specs
- The bridge protocol caught many issues through Codex review, but only *after* the changes were proposed — the blast radius was never computed *before* the proposal

## Proposed Solution

A **pre-mutation impact analysis** function in the GT-KB API that computes the blast radius of any spec CRUD operation before it executes.

### Core Function: `compute_impact(operation, spec_data)`

**Input:**
- `operation`: One of `create`, `update`, `retire`
- `spec_data`: The proposed spec (for create/update) or spec ID (for retire)

**Output:** An `ImpactReport` object containing:

```python
@dataclass
class ImpactReport:
    # Specs that share the same section/scope and may need review
    related_specs: list[dict]       # [{id, title, relationship}]
    
    # Cross-cutting specs (ADR/DCL) that constrain this spec's scope
    applicable_constraints: list[dict]  # [{id, title, assertion_summary}]
    
    # Specs that explicitly reference this spec (via affected_by or handle)
    dependents: list[dict]          # [{id, title, dependency_type}]
    
    # Specs that may contradict this spec (same section, conflicting assertions)
    potential_conflicts: list[dict] # [{id, title, conflict_type}]
    
    # Severity classification
    blast_radius: str               # 'contained' (<5 affected), 'moderate' (5-20), 'systemic' (>20)
    
    # Whether this touches cross-cutting architecture
    touches_architecture: bool
    
    # Recommended action
    recommendation: str             # 'proceed', 'review_recommended', 'owner_confirmation_required'
```

### Impact Computation Logic

1. **Section/scope overlap:** Find all current specs with matching `section` or `scope` values. These are related but not necessarily conflicting.

2. **Cross-cutting constraint lookup:** Find all `architecture_decision` and `design_constraint` type specs. For each, check if the proposed spec's section/scope/tags fall within the constraint's declared scope. Return applicable constraints with their assertions.

3. **Dependent lookup:** Query the `affected_by` field (from F1) across all specs to find any that declare dependency on the spec being modified.

4. **Conflict detection:** For specs sharing the same section, compare assertion targets. If two specs assert different behaviors for the same file/pattern, flag as potential conflict. This is heuristic, not proof — it surfaces candidates for human review.

5. **Blast radius classification:**
   - `contained`: <5 related specs, no cross-cutting constraints, no dependents
   - `moderate`: 5-20 related specs, or 1+ cross-cutting constraints
   - `systemic`: >20 related specs, or touches ADR/DCL scope, or >3 dependents

6. **Recommendation:**
   - `proceed`: blast_radius=contained and no conflicts
   - `review_recommended`: blast_radius=moderate or potential_conflicts detected
   - `owner_confirmation_required`: blast_radius=systemic or touches_architecture=true

### Integration Points

**For AI implementers (Claude Code):** Before calling `insert_spec()` or `update_spec()`, the implementer calls `compute_impact()` and includes the impact report in the bridge proposal. Codex reviews the impact assessment alongside the spec change.

**For the intake pipeline (F5):** When a requirement candidate is being promoted to a spec, the intake pipeline runs impact analysis and presents the blast radius to the owner before committing.

**For constraint propagation (F4):** When a new DCL/ADR is created, F4 uses the impact analysis to identify all affected specs and populate their `affected_by` fields.

**Not a gate — an advisory.** Impact analysis returns information; it does not block operations. The decision to proceed, review, or seek confirmation is made by the caller (AI implementer, intake pipeline, or owner). This preserves autonomy while making consequences visible.

## Counterfactual Test

**If F2 had existed during the ZK redesign (S270+):**
- When SPEC-1843 was first written, `compute_impact()` would have returned blast_radius=systemic with >100 related specs in the API, AUTH, and ADMIN_UI sections
- The recommendation would have been `owner_confirmation_required` with the full list of affected specs
- The owner would have seen the scope before implementation began, enabling phased rollout rather than a big-bang redesign
- Each subsequent spec modification would have shown its ZK constraint linkage, preventing the "implemented an endpoint without considering ZK" failure

**If F2 had existed during chat misinterpretation incidents (P2):**
- A casual remark interpreted as a spec directive would trigger `compute_impact(create, proposed_spec)`
- If the proposed spec conflicted with existing verified specs, the conflict would surface immediately
- The AI would present the impact report before proceeding, giving the owner a chance to say "no, I was just thinking out loud"

## API Design

```python
class KnowledgeDB:
    def compute_impact(
        self,
        operation: str,      # 'create', 'update', 'retire'
        spec_id: str = None, # Required for update/retire
        spec_data: dict = None,  # Required for create/update
    ) -> ImpactReport:
        """Compute blast radius of a spec mutation before executing it."""
        ...
    
    def get_constraints_for_scope(
        self,
        section: str = None,
        scope: str = None,
        tags: list[str] = None,
    ) -> list[dict]:
        """Return all ADR/DCL specs whose scope overlaps the given parameters."""
        ...
```

## Test Plan

1. **Contained impact** — Create a spec in an isolated section with no related specs; verify blast_radius=contained
2. **Moderate impact** — Create a spec in ADMIN_UI (356 existing specs); verify related_specs populated and blast_radius=moderate
3. **Systemic impact** — Create a spec tagged security/zero-knowledge; verify touches_architecture=true and applicable_constraints includes ADR-006
4. **Conflict detection** — Create two specs asserting different patterns for the same file; verify potential_conflicts flagged
5. **Dependent tracking** — Create spec A, create spec B with affected_by=[A], modify A; verify B appears in dependents
6. **Recommendation logic** — Verify all three recommendation levels trigger at correct thresholds

## Implementation Sequence

1. Define `ImpactReport` dataclass in GT-KB
2. Implement section/scope overlap query
3. Implement cross-cutting constraint lookup (depends on F1 `type` column)
4. Implement dependent lookup (depends on F1 `affected_by` column)
5. Implement heuristic conflict detection
6. Implement blast radius classification and recommendation logic
7. Write tests (6 cases above)
8. Document API in GT-KB docs

## Risks and Mitigations

| Risk | Mitigation |
|------|-----------|
| Conflict detection produces too many false positives | Start with high-confidence heuristics (same file, same pattern); tune thresholds based on Agent Red data |
| Performance on large spec corpora (2,000+ specs) | Pre-compute section/scope index; cache cross-cutting constraint list (changes rarely) |
| Advisory nature means impact can be ignored | The bridge protocol requires impact reports in proposals; Codex reviews whether impact was considered |

## Open Questions for Codex Review

1. Should the conflict detection be purely structural (assertion overlap) or also semantic (title/description similarity via ChromaDB)?
2. Should `compute_impact()` be called automatically inside `insert_spec()`/`update_spec()`, or always externally by the caller?
3. Is the blast radius threshold (5/20) appropriate, or should it be configurable per project?

---

*Submitted by: S286-Prime*
*Date: 2026-04-12*
*Tracker: DOC-GTKB-SPEC-PIPELINE, Feature F2*
