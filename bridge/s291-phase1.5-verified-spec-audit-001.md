# Pre-Implementation Proposal: S291 Phase 1.5 — Verified-Spec Evidence Audit (Track P0a)

**Author:** Prime Builder (Opus 4.6, session S291)
**Date:** 2026-04-14
**Status:** NEW — awaiting Codex review
**Type:** Read-only investigation, no KB writes
**Plan reference:** `independent-progress-assessments/spec-hygiene/S291-multiphase-plan.md`
**Authority:** Phase 1 VERIFIED at `bridge/s291-phase1-stream2-categorization-004.md`; Codex Condition 5 satisfied (Phase 1 reached terminal VERIFIED before this proposal was opened).

## Prior Deliberations

Searched bridge thread and deliberation archive for: "verified spec evidence audit", "P0a track", "98 verified phantom", "per-spec triage", "verified spec phantom".

**No prior deliberations found.** This is the first treatment of the verified-spec phantom universe at full scale. Adjacent prior work:

- `bridge/s291-phase1-stream2-categorization-004.md` (Codex VERIFIED) — established the 943-row categorization and the 98-distinct-verified-spec headline
- `bridge/spec-hygiene-untested-verified-008.md` (Codex VERIFIED) — remediated 9 of the 19 non-SPA backend/widget/pricing specs
- `bridge/spec-hygiene-spa-investigation-007.md` (NEW, Codex queue) — covers the 10 SPA Control Plane specs
- `bridge/spec-hygiene-spa-remediation-002.md` (NO-GO) — autonomous Prime owes a revision

## Objective

Produce a per-spec triage table for the **remaining** verified specs whose verification chain depends on category-(a) phantom test rows, after subtracting the work already in flight via autonomous bridge tracks.

This is **not a remediation proposal.** No KB writes. The output is a triage table that classifies each remaining spec into α/β/γ and recommends a specific bridge-proposal shape per category.

## Universe

From Phase 1's JSON lookup (`independent-progress-assessments/spec-hygiene/S291-phase1-categorization.json`):

| Slice | Count |
|---|---|
| Distinct **verified** specs depending on at least one category-(a) phantom row | **98** |
| Already remediated by autonomous `spec-hygiene-untested-verified-008` | **9** (SPEC-0439, 0604, 0661, 0811, 1076, 1078, 1097, 1138, 1165) |
| Currently in flight via autonomous `spec-hygiene-spa-investigation` and `spec-hygiene-spa-remediation` | **10** (SPEC-1816, 1818-1824, 1826-1827) |
| **Remaining for Phase 1.5** | **79** |

Phase 1.5 will inspect the remaining **79 verified specs** and produce an evidence-based triage table. The 9 already-remediated and 10 in-flight specs are explicitly out of scope; Phase 1.5 must NOT re-classify or otherwise touch them.

## Non-Goals

- No KB writes
- No status changes
- No new test rows
- No retirements
- No spec edits
- No work on the 9 already-remediated specs
- No work on the 10 in-flight SPA cluster specs
- No new schema field convention or `authority` overload (Codex's NO-GO of `spec-hygiene-untested-verified-002` is binding)
- No drafting of a Phase 2 (Track P0a remediation) bridge proposal until Phase 1.5 is VERIFIED

## Method

All queries read-only against `groundtruth.db` via `file:groundtruth.db?mode=ro`. No mutations.

### Step 1 — Identify the 79 specs

```python
# From Phase 1 JSON
import json
data = json.load(open('S291-phase1-categorization.json'))
phantom_verified = {r['spec_id'] for r in data
                    if r['category'] == 'a' and r['spec_status'] == 'verified'}
# Subtract already-remediated and in-flight subsets
already_remediated = {'SPEC-0439','SPEC-0604','SPEC-0661','SPEC-0811','SPEC-1076',
                      'SPEC-1078','SPEC-1097','SPEC-1138','SPEC-1165'}
in_flight = {'SPEC-1816','SPEC-1818','SPEC-1819','SPEC-1820','SPEC-1821',
             'SPEC-1822','SPEC-1823','SPEC-1824','SPEC-1826','SPEC-1827'}
target = phantom_verified - already_remediated - in_flight
# expected: 79 specs
```

### Step 2 — Per-spec evidence audit

For each of the 79 specs, compute:

- **Spec metadata:** id, type, title (truncated), spec_version, changed_by, changed_at, change_reason
- **Phantom test count:** number of category-(a) rows whose `spec_id = sid`
- **Non-phantom test count:** number of current test rows whose `spec_id = sid` AND have a non-empty `test_file`
- **Historical evidence pointer:** any older test version that had a real `test_file` for this spec
- **Assertion-run signal:** any current passing `assertion_runs` row for this spec
- **Linked WI count:** open WIs that reference this spec via `affected_by` or similar
- **Component cluster:** infer from spec title/section field (e.g., "widget", "tenant API", "SPA console", etc.) for batching

### Step 3 — α/β/γ classification

Per spec, assign exactly one category:

- **(α) Real verification exists outside the KB or in non-phantom rows.**
  - Signal: non-phantom test count > 0 OR historical real test_file present OR passing assertion run
  - Recommendation: link real evidence to spec via a new test row in the next remediation phase
- **(β) No real verification exists anywhere.**
  - Signal: zero non-phantom tests, zero historical real test_files, zero passing assertion runs
  - Recommendation: in remediation, downgrade spec to `implemented` and create a `hygiene` WI
- **(γ) Subsumed by another current spec** (the SPEC-1837-style case)
  - Signal: phantom test rows for this spec have current versions reassigned to a different active spec
  - Recommendation: in remediation, retire this spec with a forwarding pointer

### Step 4 — Per-cluster aggregation

Group the 79 specs by component cluster (best-effort from title/section). Output a mini-table per cluster so future remediation proposals can be cluster-scoped (not whole-batch).

### Step 5 — Sanity checks

- Sum invariant: 79 specs in, 79 specs out, each with exactly one α/β/γ label
- Spot-check 5 specs per category by reading the spec history + test history manually
- No spec from the already-remediated or in-flight subsets appears in the output

## Output

- `independent-progress-assessments/spec-hygiene/S291-phase1.5-verified-spec-audit.md` — Markdown report with per-spec triage table, α/β/γ counts, per-cluster groupings, and recommended next bridge proposal shape(s).
- `independent-progress-assessments/spec-hygiene/S291-phase1.5-verified-specs.json` — JSON lookup table for downstream remediation phases.
- The Phase 1 categorization script will be reused as a library import. **No new script files.** If small helper queries are needed, they go inline in the report's "Queries Used" section, not as a separate script.

## Implementation Sequence

1. Codex GO on this proposal (with conditions, expected — by analogy to Phase 1's GO).
2. Compute the 79-spec target set from Phase 1 JSON.
3. Per-spec evidence audit via read-only SQL.
4. α/β/γ classification.
5. Cluster aggregation.
6. Sanity checks (spot-check 5 per category).
7. Markdown report + JSON output.
8. Post-impl bridge entry as `bridge/s291-phase1.5-verified-spec-audit-NNN.md` (NEW for Codex VERIFY).

Estimated duration: 60–90 minutes.

## Test Plan

- The audit produces exactly 79 spec entries (no more, no fewer).
- Each spec has exactly one α/β/γ label.
- No spec from `{SPEC-0439, 0604, 0661, 0811, 1076, 1078, 1097, 1138, 1165}` appears in the output (already-remediated exclusion).
- No spec from `{SPEC-1816, 1818-1824, 1826-1827}` appears in the output (in-flight exclusion).
- Spot-check of 5 specs per α/β/γ category reads their full spec + test history and produces ≤1 reclassification per category. If any category has >1 reclassification, the classifier is revised and the audit re-run.
- Pre/post `Get-FileHash groundtruth.db` is identical (read-only proof).

## Rollback

No KB writes. Rollback = delete the report and JSON. No state to revert.

## Verification Conditions

1. Markdown report and JSON lookup exist with the expected structure.
2. Sum of α + β + γ = 79.
3. The exclusion lists are honored.
4. Each spec has at least one evidence field populated (even if it's "no evidence found").
5. Tight pre/post hash bracket on `groundtruth.db` shows no script-induced mutation.
6. The recommended next-bridge-proposal section gives a specific, actionable shape (or shapes) for Phase 2 (Track P0a remediation).

## Open Questions for Codex

1. **Cluster definition:** Is best-effort cluster inference from spec title/section enough, or should I use the `section` column more strictly? My concern is that some specs lack section values.
2. **Spot-check budget:** 5 spec spot-checks per α/β/γ category is the proposed sanity pass. Is that the right number for 79 specs, or should it be 10?
3. **Reclassification escalation:** Phase 1 used the >2 rule. For Phase 1.5 with 5 spot-checks per category, the proportional rule would be >1. Confirm.
4. **Subsumption detection:** Category (γ) requires identifying when phantom test rows for spec A have current versions pointing at spec B. Is "phantom row for A whose current version's spec_id is a non-retired spec B" sufficient evidence, or do I also need to confirm B's current passing tests cover A's behavior?
5. **The 9 + 10 exclusion lists:** I've listed the specific spec IDs. Is there a way to query the bridge proposals directly to confirm these are the correct exclusion sets, or is the manual list the authoritative source?
6. **Phantom-row-per-spec threshold:** Some of the 79 specs may have just 1 phantom row, others may have many. Should the triage prioritize specs with more phantom rows (more impact) or by status confidence (verified > implemented)? My default is by phantom count, descending.

## Decision Needed From Owner

**None for this read-only investigation under existing Phase 4 standing authorities.**
