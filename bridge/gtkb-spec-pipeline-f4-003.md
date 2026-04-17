# F4: Cross-Cutting Constraint Propagation — REVISED

**Feature:** F4 — Cross-Cutting Constraint Propagation
**Target repo:** groundtruth-kb
**Tracker:** DOC-GTKB-SPEC-PIPELINE
**Revision:** Addresses 4 conditions from NO-GO bridge/gtkb-spec-pipeline-f4-002.md

---

## Changes From v1

| NO-GO Condition | Resolution |
|----------------|-----------|
| 1. F1/F2 dependencies unresolved | Phased: Phase A is read-only advisory (reports applicable constraints, no writes). Phase B (after F1 GO) writes `affected_by` linkage via `update_spec()`. |
| 2. Batch UPDATE violates append-only model | All linkage writes use `update_spec()` which creates a new versioned row. No direct SQL UPDATE. Batch helper creates one new version per affected spec with `changed_by="constraint-propagation"` and `change_reason="Linked to {constraint_id}"`. |
| 3. Link removal not audit-safe | Link removal creates a new spec version with the constraint removed from `affected_by`. Previous version with the link remains queryable. Change reason documents which constraint was removed and why. |
| 4. Inherited assertion result shape undefined | Defined per-functional-spec result schema with DCL source reference, assertion details, and pass/skip/fail status. |

---

## Phased Design

### Phase A: Advisory Constraint Lookup (no F1 dependency)

Read-only functions using existing fields:

```python
class KnowledgeDB:
    def check_constraints_for_spec(
        self,
        spec_id: str = None,
        *,
        section: str = None,
        scope: str = None,
        tags: list[str] = None,
    ) -> list[dict]:
        """Return ADR/DCL specs whose scope overlaps. Read-only, no writes."""
        ...
    
    def get_constraint_coverage(self) -> dict:
        """Report: which sections have constraints vs. which don't."""
        ...
```

Implementation: queries `list_specs(type='architecture_decision')` and `list_specs(type='design_constraint')`, matches section/tags against the target spec. Pure reads.

### Phase B: Linkage Writes (after F1 GO)

```python
class KnowledgeDB:
    def propagate_constraint(
        self,
        constraint_id: str,
        *,
        dry_run: bool = True,  # Default dry_run for safety
    ) -> PropagationReport:
        """Link a constraint to all matching specs via update_spec()."""
        ...
```

**Append-only write model:**
```python
# For each affected spec:
self.update_spec(
    id=spec.id,
    changed_by="constraint-propagation",
    change_reason=f"Linked to {constraint_id} (scope match: section={spec.section})",
    affected_by=updated_affected_by_list,
)
# This creates a NEW version row. Previous version preserved.
```

**Link removal (scope narrowing or retirement):**
```python
self.update_spec(
    id=spec.id,
    changed_by="constraint-propagation",
    change_reason=f"Unlinked from {constraint_id}: constraint scope narrowed from {old_scope} to {new_scope}",
    affected_by=updated_list_without_constraint,
)
# Previous version with link remains in history for audit trail.
```

### Inherited Assertion Results

When `validate_dcl_constraints()` runs against a DCL, it currently returns DCL-level results. F4 extends this to report per-affected-spec:

```python
@dataclass
class InheritedAssertionResult:
    dcl_id: str                  # Source constraint
    dcl_title: str
    affected_spec_id: str        # Functional spec being checked
    affected_spec_title: str
    assertion: dict              # The DCL assertion that was evaluated
    status: str                  # 'pass', 'fail', 'skip'
    detail: str                  # Failure reason or skip reason
```

**Skip cases:** Non-machine assertion types on the DCL are reported as `skip` with `detail="Non-executable assertion type: {type}"`. This uses the same skip logic as assertions.py:560.

## Propagation Report

```python
@dataclass
class PropagationReport:
    constraint_id: str
    affected_specs: list[str]     # Specs newly linked (new version created)
    already_linked: list[str]     # Specs already had this constraint
    removed: list[str]            # Specs that lost linkage (new version created)
    dry_run: bool                 # Whether changes were actually written
```

## Test Plan (synthetic fixtures)

1. **Advisory lookup** — Create ADR + 3 specs with matching section; `check_constraints_for_spec()` returns the ADR
2. **Non-matching skip** — Spec in different section; verify constraint not returned
3. **Propagation dry run** — `propagate_constraint(dry_run=True)`; verify report populated but no spec versions created
4. **Propagation write** — `propagate_constraint(dry_run=False)`; verify new spec versions created with `affected_by` containing constraint ID
5. **Link removal audit** — Remove constraint from scope; verify new version created, previous version still queryable with old `affected_by`
6. **Inherited assertion result** — DCL with grep assertion, affected spec; verify per-spec result with DCL reference

## Implementation Sequence

Phase A: `check_constraints_for_spec()`, `get_constraint_coverage()`, tests 1-2.
Phase B (after F1): `propagate_constraint()` with append-only writes, link removal, inherited assertion results, tests 3-6.

---

*Submitted by: S286-Prime*
*Revision: Addresses NO-GO bridge/gtkb-spec-pipeline-f4-002.md*
