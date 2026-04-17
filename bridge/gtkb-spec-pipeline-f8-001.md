# F8: Provenance Reconciliation — Implementation Proposal

**Feature:** F8 — Provenance Reconciliation
**Target repo:** groundtruth-kb
**Tracker:** DOC-GTKB-SPEC-PIPELINE
**Corruption vectors addressed:** P1 (workarounds calcify into specs and bias future work)
**Dependencies:** F1 (needs authority_tier and provisional_until fields)
**Prior deliberations:** DELIB-0707 (retroactive migration — use implementation as reference), DELIB-0710 (completeness)

---

## Problem Statement

Over time, a spec corpus accumulates artifacts that no longer accurately represent the system or the owner's intent. In Agent Red:

- **615 implementation-derived specs** (29% of corpus) were created by the AI observing existing code. Some accurately document the system; some codified workarounds or accidental complexity. Without an authority marker, all 615 have the same weight as the 757 owner-directed specs.

- **202 retired specs** were successfully identified and removed. But retirement is reactive — these specs existed in the corpus for sessions or months before being flagged. During that time, they may have influenced other specs or implementations.

- **68 unmapped specs** (per MEMORY.md) exist in the KB but can't be traced to current code. These are phantom requirements — the AI may attempt to implement or preserve behavior that no longer exists.

- **Provisional implementations** (mock APIs, workaround code) were never marked as provisional. They entered the spec corpus as permanent requirements and remained there, exerting gravitational pull on future design decisions.

The core issue: the spec corpus has no self-cleaning mechanism. Specs accumulate but are never reconciled against reality unless someone manually audits.

## Proposed Solution

A **provenance reconciliation engine** that periodically identifies and flags specs requiring attention.

### Reconciliation Checks

**Check 1: Authority Mismatch**
Find specs where `authority=inferred` (AI-derived) conflicts with `authority=stated` (owner-directed) specs in the same section/scope. When an inferred spec contradicts a stated spec, the inferred spec is flagged for review — the stated spec has higher authority.

Output: List of `{inferred_spec, stated_spec, conflict_type, recommended_action}`

**Check 2: Orphaned Specs**
Find specs whose assertions reference files or patterns that no longer exist in the codebase. These are phantom requirements — the code they describe has been removed or renamed, but the spec persists.

Output: List of `{spec_id, failing_assertion, reason}` — assertion target not found

**Check 3: Expired Provisionals**
Find specs where `authority=provisional` and `provisional_until` references a spec that is now `implemented` or `verified`. The provisional spec has served its purpose — the permanent replacement exists. The provisional should be retired.

Output: List of `{provisional_spec, replacement_spec, replacement_status}`

**Check 4: Stale Specs**
Find specs that haven't been touched (no version update) in N sessions while their section has had active changes. A spec in an actively-changing section that hasn't been updated may describe outdated behavior.

Output: List of `{spec_id, last_updated, section, section_activity_count}`

**Check 5: Duplicate Detection**
Find spec pairs with >80% title similarity or description similarity. Duplicates create ambiguity about which is authoritative and force the AI to reconcile conflicting signals.

Output: List of `{spec_a, spec_b, similarity_score, overlap_type}`

### Reconciliation Report

```python
@dataclass
class ReconciliationReport:
    timestamp: str
    checks_run: list[str]
    findings: dict              # {check_name: [findings]}
    total_findings: int
    critical_findings: int      # Authority mismatches, orphaned specs
    advisory_findings: int      # Stale specs, potential duplicates
    recommended_actions: list[dict]  # [{spec_id, action, reason}]
```

### Reconciliation Actions

The reconciliation engine does NOT automatically modify specs. It produces a report with recommended actions:

- **Retire** — Spec describes behavior that no longer exists (orphaned)
- **Downgrade** — Inferred spec conflicts with stated spec; mark as superseded
- **Expire** — Provisional spec's replacement is implemented; retire provisional
- **Review** — Stale spec in active section; may need update or retirement
- **Merge** — Duplicate specs should be consolidated into one authoritative spec

All actions require confirmation — either by the AI implementer (for routine cases) or by the owner (for authority conflicts or retirement of stated specs).

## Counterfactual Test

**If F8 had existed throughout Agent Red development:**
- The 615 implementation-derived specs would have been flagged as `authority=inferred` (via F1) and periodically checked against owner-directed specs for conflicts
- The 68 unmapped specs would have been caught as orphaned specs (failing assertion targets) within 1-2 sessions of the code being removed
- Workaround code that became permanent would have been flagged when its provisional_until spec was implemented but the provisional wasn't retired
- Near-duplicate specs would have been surfaced for consolidation, reducing corpus ambiguity

**Estimated cleanup:** Based on Agent Red data:
- ~615 inferred specs to check for authority conflicts → estimated 50-100 findings
- ~68 orphaned specs to flag → all 68 would be caught
- Unknown number of expired provisionals (currently no provisional marking — this improves once F1 is applied retroactively)
- Unknown duplicates (requires similarity analysis)

## API Design

```python
class KnowledgeDB:
    def run_reconciliation(
        self,
        checks: list[str] = None,   # Specific checks, or all if None
        section: str = None,         # Scope to a section
    ) -> ReconciliationReport:
        """Run provenance reconciliation checks and return findings."""
        ...
    
    def get_authority_conflicts(self) -> list[dict]:
        """Find inferred specs that conflict with stated specs."""
        ...
    
    def get_orphaned_specs(self) -> list[dict]:
        """Find specs whose assertion targets no longer exist."""
        ...
    
    def get_expired_provisionals(self) -> list[dict]:
        """Find provisional specs whose replacements are implemented."""
        ...
    
    def get_stale_specs(
        self,
        staleness_threshold_sessions: int = 10,
    ) -> list[dict]:
        """Find specs unchanged for N sessions in actively-changed sections."""
        ...
    
    def get_duplicate_candidates(
        self,
        similarity_threshold: float = 0.8,
    ) -> list[dict]:
        """Find spec pairs with high title/description similarity."""
        ...
```

## Test Plan

1. **Authority conflict** — Create stated spec and conflicting inferred spec in same section; verify conflict detected
2. **Orphaned spec** — Create spec with assertion targeting a file, delete the file; verify orphan detected
3. **Expired provisional** — Create provisional spec with provisional_until=X, set X to implemented; verify expiration detected
4. **Stale spec** — Create spec in section, update other specs in section 10 times, don't update the target; verify staleness detected
5. **Duplicate detection** — Create two specs with near-identical titles; verify duplicate candidate reported
6. **Scoped reconciliation** — Run reconciliation for specific section; verify only findings in that section returned

## Implementation Sequence

1. Implement authority conflict detection (depends on F1 authority field)
2. Implement orphaned spec detection (requires filesystem access for assertion target validation)
3. Implement expired provisional detection (depends on F1 provisional_until field)
4. Implement stale spec detection (uses session snapshot history from F7)
5. Implement duplicate detection (title similarity; ChromaDB for description similarity if available)
6. Implement reconciliation report aggregator
7. Write tests (6 cases above)
8. Create `/reconcile` skill for on-demand runs

## Risks and Mitigations

| Risk | Mitigation |
|------|-----------|
| Orphan detection triggers false positives for specs about external systems | Only check assertion targets that reference local files; external/behavioral assertions are exempt |
| Duplicate detection is too aggressive | High threshold (80%); flag as advisory, not critical |
| Reconciliation report is overwhelming on first run against Agent Red | Prioritize critical findings (orphans, authority conflicts) over advisory (stale, duplicates) |
| Filesystem access needed for orphan detection | Use existing assertion-check infrastructure (assertion runner already validates file targets) |

## Open Questions for Codex Review

1. Should reconciliation run automatically at session start, session end, or only on demand?
2. Should the reconciliation engine be able to auto-execute retirement of expired provisionals, or should every action require confirmation?
3. How should orphan detection handle assertions that reference generated files (build outputs, test fixtures)?
4. Should duplicate detection use pure string similarity or semantic similarity via ChromaDB?

---

*Submitted by: S286-Prime*
*Date: 2026-04-12*
*Tracker: DOC-GTKB-SPEC-PIPELINE, Feature F8*
