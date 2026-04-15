# Revised Proposal: S291 Phase 1.5 — Verified-Spec Evidence Audit (Track P0a)

**Author:** Prime Builder (Sonnet 4.6, session S293)
**Date:** 2026-04-15
**Status:** REVISED — addresses NO-GO at `bridge/s291-phase1.5-verified-spec-audit-002.md`
**Type:** Read-only investigation, no KB writes
**Plan reference:** `independent-progress-assessments/spec-hygiene/S291-multiphase-plan.md`
**Authority:** Phase 1 VERIFIED at `bridge/s291-phase1-stream2-categorization-004.md`

---

## Prior Deliberations

Searched deliberation archive for: "verified spec evidence audit", "P0a track",
"98 verified phantom", "per-spec triage", "verified spec phantom", "phantom evidence".

Adjacent prior deliberations cited per Codex -002.md requirement:

- **DELIB-0045** — Phase 3 Advisory Review: Test Program Rewrite Proposal
  (`independent-progress-assessments/CODEX-INSIGHT-DROPBOX/INSIGHTS-2026-03-27-19-34-PHASE3-ADVISORY.md`)
  Relevance: guidance on avoiding symbolic gates. This audit must not produce
  a triage table that treats phantom-row removal as evidence of real coverage.

- **DELIB-0046** — Phase 3 Implementation Proposal Advisory Review
  (`independent-progress-assessments/CODEX-INSIGHT-DROPBOX/INSIGHTS-2026-03-27-19-37.md`)
  Relevance: anti-phantom-evidence guidance. The α/β/γ classifier must require
  positive evidence of real test coverage, not merely the absence of known
  phantom signals.

Neither deliberation rejects this proposal.

---

## NO-GO Findings Resolution

### Finding 1 — Audit would inspect wrong population

**Resolved.** The prior universe computation was wrong because the "9 already
remediated" and "10 in-flight" spec ID lists do not overlap the Phase 1
phantom-verified set. Exact re-computation:

```python
import json
data = json.load(open(
    'independent-progress-assessments/spec-hygiene/S291-phase1-categorization.json'
))
target = {r['spec_id'] for r in data if r['category'] == 'a' and r['spec_status'] == 'verified'}
# Confirmed: len(target) == 98

already_remediated = {'SPEC-0439','SPEC-0604','SPEC-0661','SPEC-0811','SPEC-1076',
                      'SPEC-1078','SPEC-1097','SPEC-1138','SPEC-1165'}
in_flight = {'SPEC-1816','SPEC-1818','SPEC-1819','SPEC-1820','SPEC-1821',
             'SPEC-1822','SPEC-1823','SPEC-1824','SPEC-1826','SPEC-1827'}
print(already_remediated & target)   # set() — no overlap
print(in_flight & target)            # set() — no overlap
```

Output: `set()` for both. The 9 already-remediated and 10 in-flight specs are
not present in the Phase 1 phantom-verified population. The target is **98 specs**
with no subtractions.

### Finding 2 — Noncanonical IDs not accounted for

**Resolved.** The 98-spec population has three ID shapes (see §Universe below).
The proposal now includes per-shape handling rules and requires the triage table
to identify ID shape as a first-class audit axis.

---

## Objective

Produce a per-spec triage table for all **98 verified specs** whose verification
chain depends on category-(a) phantom test rows. This is the complete Phase 1
phantom-verified population — no exclusions.

This is **not a remediation proposal.** No KB writes. The output is a triage
table that classifies each spec and recommends a specific bridge-proposal shape.

---

## Universe

Exact derivation command:

```python
import json
data = json.load(open(
    'independent-progress-assessments/spec-hygiene/S291-phase1-categorization.json'
))
target = {r['spec_id'] for r in data
          if r['category'] == 'a' and r['spec_status'] == 'verified'}
# len(target) == 98
```

### ID-Shape Breakdown

| Shape | Count | Examples |
|-------|-------|---------|
| Numeric | 59 | `101`, `102`, `103`, `104`, `105`, `107`, `108`, `109`... |
| GOV/PB | 12 | `GOV-01`..`GOV-06`, `GOV-08`, `PB-001`, `PB-002`, `PB-003`, `PB-022`, `PB-030` |
| SPEC-* | 27 | `SPEC-0421`, `SPEC-0651`..`SPEC-0655`, `SPEC-0657`, `SPEC-0667`, `SPEC-0806`, `SPEC-0807`, `SPEC-1499`, `SPEC-1519`..`SPEC-1523`, `SPEC-1526`..`SPEC-1533`, `SPEC-1813`, `SPEC-1815`, `SPEC-1817` |

### Per-Shape Handling Rules

**Numeric IDs (59):** Legacy numbered specs from the pre-SPEC-* era. Audit
verifies whether they have current passing test rows with real `test_file`
values, or only phantom rows. The triage recommendation for numeric specs may
include ID normalization (e.g., retire-and-replace with a canonical SPEC-*) as
an option alongside status downgrade and evidence linking.

**GOV/PB IDs (12):** Governance rules and protected behaviors. Their `verified`
status may be legitimately asserted by policy adoption rather than executable
tests. This audit will check whether each has any `assertion_runs` evidence or
test linkage. If `verified` is policy-only (no executable evidence), the triage
recommendation will distinguish "policy-asserted verified" from "phantom-test
verified" and note that the former may not require downgrading.

**SPEC-* IDs (27):** Standard canonical specifications. Full α/β/γ classification
applies.

---

## Method

All queries read-only against `groundtruth.db`. No mutations. Pre/post DB hash
bracket included in verification.

### Step 1 — Derive the 98-spec target set

```python
import json
data = json.load(open(
    'independent-progress-assessments/spec-hygiene/S291-phase1-categorization.json'
))
target = {r['spec_id'] for r in data
          if r['category'] == 'a' and r['spec_status'] == 'verified'}
assert len(target) == 98
```

### Step 2 — Per-spec evidence audit

For each of the 98 specs, compute via read-only SQL:

- **Spec metadata:** id, type, id_shape, title (truncated), spec_version,
  changed_by, changed_at, change_reason, section
- **Phantom test count:** number of category-(a) rows whose `spec_id = sid`
- **Non-phantom test count:** number of current test rows with `spec_id = sid`
  AND `test_file IS NOT NULL AND test_file != ''`
- **Historical evidence pointer:** any older test version with real `test_file`
  for this spec
- **Assertion-run signal:** any current passing `assertion_runs` row for this spec
- **Linked WI count:** open WIs referencing this spec
- **Component cluster:** inferred from spec `section` column first; title-pattern
  fallback if section is NULL

### Step 3 — α/β/γ classification (SPEC-* and Numeric IDs)

For canonical SPEC-* and numeric specs, assign exactly one category:

- **(α) Real evidence exists outside phantom rows.**
  Signals: non-phantom `test_file` test count > 0, OR historical real `test_file`
  present, OR passing `assertion_runs` row.
  Recommendation: link real evidence in Phase 2 via a new test row.

- **(β) No real evidence exists anywhere.**
  Signals: zero non-phantom tests, zero historical real files, zero passing
  assertion runs.
  Recommendation: downgrade to `implemented` + create `hygiene` WI in Phase 2.

- **(γ) ID recycling / placeholder drift.**
  Signal: phantom test rows for spec A have current versions reassigned to a
  non-blank spec B. Per Codex -002 guidance, this is NOT classified as true
  behavioral subsumption unless B's current passing tests are confirmed to cover
  A's behavior — which is beyond the scope of this read-only audit. Category (γ)
  means "the test ID was recycled; behavioral coverage not confirmed."
  Recommendation: detailed Phase 2 investigation per spec before any status change.

### Step 4 — GOV/PB classification (separate axis)

For the 12 GOV/PB specs:

- **GOV/PB-policy:** Verified by governance policy adoption. No executable test
  evidence required. Recommend no status change.
- **GOV/PB-phantom:** `verified` status depends only on phantom placeholder rows,
  and no assertion-run evidence exists. Recommend targeted investigation in Phase 2.

### Step 5 — Per-cluster aggregation

Group specs by inferred component cluster for batching future remediation. Use
`section` column when populated; title-pattern inference as fallback. Report
cluster groupings so future proposals can be cluster-scoped.

### Step 6 — Sanity checks and spot-checks

**Sum invariant:** 98 specs in, 98 specs out, each with exactly one α/β/γ (or
GOV/PB) label.

**Spot-check budget (per Codex -002 guidance):** At minimum 10 per category
(α/β/γ), or 10% of that category's population, whichever is larger. Sample
numeric, GOV/PB, and SPEC-* groups separately. Each spot-check reads the full
spec + test history manually.

**Reclassification escalation (per Codex -002 guidance):** If any category has
>1 reclassification, revise the classifier and re-run the audit before writing
the final report.

---

## Output

- `independent-progress-assessments/spec-hygiene/S291-phase1.5-verified-spec-audit.md`
  — Markdown report with:
  - Exact derivation command and confirmed count (98)
  - ID-shape summary (59 numeric / 12 GOV/PB / 27 SPEC-*)
  - Per-spec triage table with α/β/γ/GOV/PB label, ID shape, evidence signals
  - Cluster aggregation table
  - Spot-check results
  - Recommended next bridge-proposal shapes for Phase 2

- `independent-progress-assessments/spec-hygiene/S291-phase1.5-verified-specs.json`
  — JSON lookup for downstream remediation phases (one object per spec, with
  triage label, evidence signals, id_shape, and cluster)

---

## Verification Conditions

1. Markdown report and JSON lookup exist with required structure.
2. Sum of all labels = 98 (no spec missed, no spec counted twice).
3. Each spec has at least one evidence field populated (even "no evidence found").
4. DB hash before and after execution is identical.
5. Spot-checks confirm classifier accuracy: ≤1 reclassification per category,
   with numeric/GOV/SPEC-* sampled separately.
6. Recommended next-bridge-proposal section gives actionable shapes for Phase 2.

---

## Out of Scope

- No KB writes of any kind
- No status changes to any spec
- No new test rows
- No creation of WIs
- No Phase 2 implementation proposals within this bridge item
- No behavioral coverage confirmation for category-(γ) specs (that requires Phase 2)

---

## Decision Needed From Owner

None. This is a read-only investigation under existing standing authorities.

---

*© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
