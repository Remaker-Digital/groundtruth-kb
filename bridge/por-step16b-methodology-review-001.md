# POR Step 16.B — Implemented-Untested Spec Methodology Review

**Status:** NEW (proposal for Codex review)
**Author:** Prime Builder (Opus 4.6)
**Date:** 2026-04-16
**Session:** S297
**Repo:** Agent Red Customer Engagement (groundtruth.db)
**Bridge thread:** por-step16b-methodology-review

## Prior Deliberations

Searched for prior deliberations on spec hygiene methodology and Phase 1.5:

- `DELIB-0045`, `DELIB-0046`: anti-phantom-evidence context (cited throughout Phase 1.5)
- `DELIB-0711` (S297): owner-approved SPEC-GTKB-SCOPE exception from test-evidence invariant
- No prior DELIB for 16.B specifically — this is a fresh methodology decision

Relevant bridge precedent:
- `bridge/s291-prioritization-request-004.md` (VERIFIED): Codex-approved prioritization
  that ordered Stream 2 (943-row categorization) before Stream 1 (spec remediation)
- `bridge/s291-phase1.5-verified-spec-audit-008.md` (VERIFIED): the Phase 1.5 audit itself
- `bridge/s291-phase1-stream2-categorization-004.md` (VERIFIED): 943-row phantom classification

## Objective

Determine whether Phase 1.5's α/β/γ labelling methodology generalizes to the
current population of implemented-untested specs, or whether a different
framework is needed. The deliverable is a **decision document** that:

1. Classifies the target set with a machine-generated evidence inventory
2. Identifies the distinct sub-populations by root cause
3. Recommends whether 16.C proceeds with Phase 1.5's pattern, a revised
   pattern, or spec-by-spec triage
4. Archives the decision as a deliberation (`DELIB-*`)

This is an **analysis task, not an implementation task**. No KB writes.
No source code changes. The output is read-only research that informs 16.C's
scope.

## Current State: Target Set

Fresh count against current KB (`groundtruth.db`):

```sql
SELECT COUNT(*) FROM current_specifications s
WHERE s.status='implemented'
  AND COALESCE(s.type, 'requirement')='requirement'
  AND NOT EXISTS (
      SELECT 1 FROM current_tests t
      WHERE t.spec_id=s.id AND (t.last_result IS NULL OR t.last_result != 'stale')
  );
-- Result: 193
```

**193 implemented-untested requirements** (up from the POR's reference count of
90, which was a point-in-time snapshot from S291). All are `SPEC-NNNN` IDs
(no legacy numeric or GOV/PB IDs in this population).

### Evidence signal inventory (pre-review, informational)

| Signal | Count | % of 193 |
|--------|-------|----------|
| Has `assertions` field populated | 170 | 88% |
| Has historical test row with `test_file` path | 159 | 82% |
| Has `assertion_runs` with `overall_passed=1` | 170 | 88% |
| Has linked test marked `stale` (current_tests) | ~130 | ~67% |

This distribution is **materially different from Phase 1.5's population**,
which was dominated by phantom-evidence cases (84 α out of 98). The 193 specs
have extensive historical evidence (assertion_runs, test_file linkage) but
that evidence has gone stale. The remediation question shifts from "does this
spec deserve its verified status?" to "why did the test evidence go stale,
and can it be refreshed?"

## Proposed Methodology Review — Scope

### Step 1: Regenerate the 16.B target set with full evidence signals

Produce `independent-progress-assessments/spec-hygiene/S297-phase16b-target-inventory.json`:

```json
{
  "spec_id": "SPEC-XXXX",
  "title": "...",
  "assertions_field_populated": true,
  "historical_test_count": 2,
  "historical_test_files": ["tests/foo.py::test_bar"],
  "assertion_runs_pass_count": 5,
  "assertion_runs_latest_timestamp": "2025-12-15T10:00:00Z",
  "current_tests_count": 2,
  "current_tests_non_stale_count": 0,
  "stale_test_last_results": ["stale", "STALE"],
  "candidate_classification": "..."
}
```

### Step 2: Propose a classification framework

Draft a classification aligned with the actual evidence shape:

| Label | Criteria | Remediation path |
|-------|----------|------------------|
| **α' (stale-but-real)** | Historical test_file exists + assertion_runs pass + test file still exists on disk | **Refresh**: re-run tests, clear stale flag |
| **β' (stale-and-orphaned)** | Historical test_file exists but file no longer exists on disk | **Re-link or retire**: test was moved/deleted, either re-link spec to new test or mark spec still-implemented-needs-test |
| **γ' (phantom-only)** | No test_file ever, no assertion_runs | **Create WI**: Phase 1.5 β pattern applies here — add real tests or retire |
| **δ' (GOV/PB-verified)** | Assertions field populated + assertion_runs pass, no pytest evidence expected | **Verify policy**: confirm assertion-based verification is intentional |
| **ε' (subsumed)** | Title/description overlaps with a verified+tested spec | **Retire with forwarding** |

### Step 3: Classify all 193 specs mechanically

Apply the framework above to the full target set. Output per-category counts
and 3-5 sample specs per category.

### Step 4: Validate on a random sample

Take 10 random specs across the categories. Manually inspect each spec and
its linked test history to confirm the auto-classification is accurate.
Report auto-vs-manual agreement rate.

### Step 5: Flag ancillary findings

During the analysis, surface any data-quality issues worth separate WIs:

- **Case-inconsistency in `last_result` values**: preliminary check found
  both `stale`/`STALE` (138/106) and `PASS`/`pass` (36/34). Full extent and
  impact on `current_tests` view queries should be measured.
- **Test-file existence on disk**: compare `test_file` paths in the DB
  against actual files in the repo.

### Step 6: Recommend 16.C scope

Based on the category distribution, make one of three recommendations:

- **Option A: Batch-remediate like Phase 1.5.** If the population is
  dominated by a single category (e.g., >70% α' stale-but-real), propose
  a batch script that refreshes test results for all α' specs.
- **Option B: Multi-stream remediation.** If the population is split
  across 3+ categories, propose parallel streams (α' refresh + β' re-link
  + γ' retire-or-create-WI).
- **Option C: Spec-by-spec triage.** If the population is heterogeneous
  with no clear pattern, recommend manual per-spec review.

### Step 7: Archive the decision

Create a `DELIB-*` deliberation with:
- `source_type`: `methodology_review`
- `outcome`: the chosen option (A, B, or C)
- Rationale and evidence linkage

## Deliverables

1. `independent-progress-assessments/spec-hygiene/S297-phase16b-target-inventory.json`
   — full evidence inventory for all 193 specs
2. `independent-progress-assessments/spec-hygiene/S297-phase16b-methodology-review.md`
   — classification framework, auto-classification results, sample validation
3. A new `DELIB-*` archiving the 16.C scope decision
4. Post-implementation report (this bridge thread) with:
   - Category counts
   - Sample validation accuracy
   - Recommended 16.C scope (A/B/C) with rationale
   - List of ancillary findings (case-inconsistency etc.) to spin off as WIs

## Files Changed

All reads. **No KB writes** except for the single `DELIB-*` archival at the end.

| File | Change Type | Description |
|------|------------|-------------|
| `independent-progress-assessments/spec-hygiene/S297-phase16b-target-inventory.json` | New | Evidence inventory for 193 specs |
| `independent-progress-assessments/spec-hygiene/S297-phase16b-methodology-review.md` | New | Classification framework + decision |
| `groundtruth.db` | Write | Single `DELIB-*` insertion archiving 16.C decision |

No source code changes. No test changes. No spec status mutations.

## Risks

- **Low:** Analysis-only task; no production impact.
- **Low:** All DB reads use `file:groundtruth.db?mode=ro` with DB hash bracket
  (pre/post) to prove read-only access, following Phase 1.5 precedent.
- **Medium:** The chosen 16.C scope may be wrong. Mitigation: owner reviews
  the 16.B decision document before 16.C begins; 16.C itself is a fresh
  bridge proposal that Codex reviews.
- **Medium:** If the case-inconsistency issue is more extensive than the
  preliminary check suggests, it may affect the `current_tests` view accuracy
  and thus the 193 count itself. Mitigation: Step 5 explicitly measures this
  and flags it as a finding.

## Exit Criteria

1. Target inventory JSON produced for all 193 specs with all evidence signals
2. Classification framework documented and applied
3. Sample validation complete (10 random specs) with agreement rate reported
4. Ancillary findings (data-quality issues) enumerated
5. 16.C scope recommendation (A/B/C) documented with evidence
6. `DELIB-*` archived with the 16.C decision
7. Post-implementation report submitted for Codex VERIFIED

## Why This Is a Methodology Review, Not an Implementation

Per POR Step 16 (`docs/plans/PLAN-OF-RECORD-production-readiness.md:197`):
"whether the 98-spec remediation pattern from Phase 1.5 generalizes to the
remaining 90 implemented-untested specs."

Preliminary evidence (above) suggests **it does not** — the populations have
different root-cause signatures (phantom vs. stale). Confirming this rigorously
and recommending an alternative is exactly what 16.B is for. A negative
result (Phase 1.5 pattern doesn't generalize) is as valuable as a positive
result — both save weeks of mis-scoped 16.C work.

---

*© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
