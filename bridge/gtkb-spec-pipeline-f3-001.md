# F3: Spec Quality Gate — Implementation Proposal

**Feature:** F3 — Spec Quality Gate
**Target repo:** groundtruth-kb
**Tracker:** DOC-GTKB-SPEC-PIPELINE
**Corruption vectors addressed:** P4 (unclear specs produce weak tests), P1 (workaround calcification), P3 (assumption-driven implementation)
**Dependencies:** F1 (needs enriched schema fields to score against)
**Prior deliberations:** DELIB-0710 (quality ranking — clarity and completeness)

---

## Problem Statement

The current GT-KB accepts any spec that has the required fields (id, version, title, status, changed_by, changed_at, change_reason). There is no validation of *quality*. A spec titled "do the thing" with no description, no assertions, and no tags is structurally valid.

This enables corruption vector P4: unclear specs produce weak tests that pass falsely. The AI's bias is toward communicating successful outcomes. When a spec is vague, the rational strategy is to write a vague test — and vague tests pass. The system reports green while actual behavior is unverified.

**Agent Red evidence:**
- 16.3% of specs (344) have no assertions at all — these are unfalsifiable
- 77.6% of assertions are `grep` type — existence checks, not behavioral verification
- 7.4% of specs have empty descriptions — the title is the entire specification
- Average title length is 82 chars — many are sufficient, but some are too terse to be unambiguous
- The owner observed that "the lack of clarity is not directly stated and results in weak tests, because the AI bias is toward communicating successful outcomes"

## Proposed Solution

A **post-creation quality scoring function** in GT-KB that evaluates every spec against quality dimensions and returns a structured score. Not a gate that blocks — an assessment that informs.

### Core Function: `score_spec_quality(spec_id) -> QualityScore`

```python
@dataclass
class QualityScore:
    overall: float          # 0.0 to 1.0
    dimensions: dict        # {dimension_name: {score, reason, suggestions}}
    flags: list[str]        # Critical issues that warrant attention
    tier: str               # 'directive', 'behavioral', 'architectural' — recommended tier
```

### Quality Dimensions

**D1: Clarity (0.0 - 1.0)**
- Title uses assertion language (MUST, MUST NOT, SHALL) → +0.3
- Title length 40-120 chars (not too terse, not too verbose) → +0.2
- Description present and >50 chars → +0.3
- Description includes rationale ("because", "to prevent", "so that") → +0.2

**D2: Testability (0.0 - 1.0)**
- Has at least one assertion → +0.3
- Has at least one non-grep assertion (behavioral, functional, test_run) → +0.3
- Assertions have descriptions → +0.2
- Assertions target specific files (not wildcards) → +0.2

**D3: Completeness (0.0 - 1.0)**
- `type` field set (not default) → +0.1
- `authority` field set → +0.1
- `tags` present → +0.1
- `section` present → +0.1
- `scope` present → +0.1
- `constraints` present (if complexity > simple) → +0.2
- `priority` set → +0.1
- Description includes acceptance criteria or numbered requirements → +0.2

**D4: Isolation (0.0 - 1.0)**
- Spec does not duplicate title/description of existing spec → +0.4
- `affected_by` populated if in a constrained section → +0.3
- No circular dependencies via `affected_by` → +0.3

**D5: Freshness (0.0 - 1.0)**
- Assertions last validated within 30 days → +0.5
- Spec version updated within 90 days → +0.3
- No stale test references → +0.2

### Tier Recommendation

Based on the scoring, the quality gate recommends which template tier the spec should follow:

- **Directive** (overall >= 0.4): One-line requirement. Suitable for simple UI rules, naming conventions, config constraints.
- **Behavioral** (overall >= 0.6): Requires description with rationale, 1+ non-grep assertion. Suitable for feature requirements, API contracts.
- **Architectural** (overall >= 0.8): Requires structured description (Decision/Context/Requirements/Consequences), multiple assertion types, cross-cutting linkages. Suitable for ADRs, security boundaries.

If a spec's content suggests it should be Behavioral or Architectural (based on section, tags, or complexity indicators) but scores as Directive, the quality gate flags it for enrichment.

### Flag Conditions

The quality gate raises flags (not blocks) for:
- `NO_ASSERTIONS`: Spec has no assertions — unfalsifiable
- `GREP_ONLY`: All assertions are existence checks — behaviorally untested
- `DUPLICATE_CANDIDATE`: Title/description >80% similar to existing spec
- `MISSING_RATIONALE`: Architectural/security spec without description rationale
- `PROVISIONAL_NO_EXPIRY`: authority=provisional but provisional_until is NULL
- `CROSS_CUTTING_UNLINKED`: Spec in constrained section but affected_by is empty

## Counterfactual Test

**If F3 had existed from session 1:**
- The 344 specs without assertions would have been flagged `NO_ASSERTIONS` at creation time, prompting the AI to add at least structural assertions
- The 615 implementation-derived specs would have scored lower on Clarity (no owner-originated rationale) and been flagged as needing enrichment
- The weak tests that the owner observed would have been indirectly prevented: a spec flagged `GREP_ONLY` signals that a `grep` test is the ceiling — the AI would know that behavioral testing was needed
- The quality score history would provide a trendline: "are we writing better specs over time?"

## API Design

```python
class KnowledgeDB:
    def score_spec_quality(
        self,
        spec_id: str,
    ) -> QualityScore:
        """Score a spec across 5 quality dimensions. Returns scores, flags, and tier recommendation."""
        ...
    
    def score_all_specs(
        self,
        status: str = None,
        type: str = None,
    ) -> list[QualityScore]:
        """Batch scoring for dashboards and reports. Filters optional."""
        ...
    
    def get_quality_distribution(self) -> dict:
        """Returns histogram of quality scores across the corpus. Used by F7 dashboard."""
        ...
```

## Integration Points

- **F1 (Schema Enrichment):** Quality gate scores against the enriched schema fields. If F1 fields are NULL, completeness score is lower.
- **F5 (Intake Pipeline):** Requirement candidates are scored before promotion to specs. Low-scoring candidates get enrichment suggestions.
- **F7 (Health Dashboard):** Quality distribution is a dashboard metric. Session-over-session quality trends detect drift.
- **F8 (Provenance Reconciliation):** Low-quality implementation-derived specs are prioritized for reconciliation.

## Test Plan

1. **Perfect spec** — Create a spec with all fields populated, behavioral assertions, rationale in description; verify overall >= 0.8
2. **Minimal spec** — Create a spec with only required fields; verify overall < 0.4 and flags include NO_ASSERTIONS
3. **Grep-only spec** — Create a spec with grep assertions only; verify GREP_ONLY flag
4. **Duplicate detection** — Create two specs with near-identical titles; verify DUPLICATE_CANDIDATE flag on the second
5. **Tier recommendation** — Verify architectural-section specs with low scores get flagged for enrichment
6. **Batch scoring** — Score all Agent Red specs; verify distribution matches expected patterns (majority 0.4-0.6 range)

## Implementation Sequence

1. Define `QualityScore` dataclass
2. Implement D1 (Clarity) scoring
3. Implement D2 (Testability) scoring
4. Implement D3 (Completeness) scoring
5. Implement D4 (Isolation) scoring — includes duplicate detection
6. Implement D5 (Freshness) scoring
7. Implement tier recommendation logic
8. Implement flag generation
9. Add `score_spec_quality()`, `score_all_specs()`, `get_quality_distribution()` to API
10. Write tests (6 cases above)

## Risks and Mitigations

| Risk | Mitigation |
|------|-----------|
| Scoring formula is subjective | Weight adjustments are configurable; calibrate against Agent Red corpus where known-good and known-bad specs exist |
| Duplicate detection is too sensitive | Use title-only matching first; add description similarity (ChromaDB) in later iteration |
| Freshness scoring penalizes stable specs | Freshness dimension has lower weight (1 of 5); stable verified specs should score high on other dimensions |

## Open Questions for Codex Review

1. Should quality scores be stored in the KB (enabling historical trends) or computed on demand?
2. Should the scoring weights be fixed in code or configurable per project?
3. Is 5 dimensions the right granularity, or should D1 (Clarity) be split into title clarity vs. description clarity?
4. Should `score_all_specs()` run automatically at session start as part of F7, or only on demand?

---

*Submitted by: S286-Prime*
*Date: 2026-04-12*
*Tracker: DOC-GTKB-SPEC-PIPELINE, Feature F3*
