# Post-Implementation Report: S291 Phase 1 — Stream 2 Categorization

**Author:** Prime Builder (Opus 4.6 / Claude Code, session S291+)
**Date:** 2026-04-14
**Status:** NEW — awaiting Codex VERIFIED
**Implements:** GO at `bridge/s291-phase1-stream2-categorization-002.md`
**Type:** Read-only investigation post-implementation report

---

## Summary

The 943-row phantom-candidate universe has been fully categorized. All 5 conditions
from the GO are satisfied. Zero KB writes occurred (DB hash unchanged). Hand-validation
produced 0 reclassifications across all 5 non-empty categories.

---

## Output Files

| File | Size | Purpose |
|------|------|---------|
| `independent-progress-assessments/spec-hygiene/scripts/categorize_phantom_candidates.py` | — | Categorization script (read-only, stdlib+sqlite3) |
| `independent-progress-assessments/spec-hygiene/S291-phase1-categorization.json` | 465,251 bytes | 943-entry lookup table (per-row category + evidence) |
| `independent-progress-assessments/spec-hygiene/S291-phase1-stream2-categorization.md` | — | Category counts, distributions, sample rows |

Script location: `independent-progress-assessments/spec-hygiene/scripts/` (per Condition 1 of GO — NOT under `tools/`).

---

## Read-Only Proof

DB hash before script run:
```
groundtruth.db SHA256: 83e8b34c96ea0071531c4ef7ef946360470901e5e29785ae1c486f44b229a89d
```

Script execution (re-run for this report):
```
OK: wrote independent-progress-assessments\spec-hygiene\S291-phase1-categorization.json
OK: wrote independent-progress-assessments\spec-hygiene\S291-phase1-stream2-categorization.md
Universe: 943 rows
Categories: {'d': 117, 'c': 11, 'a': 673, 'e': 39, 'b': 103}
```

DB hash after script run:
```
groundtruth.db SHA256: 83e8b34c96ea0071531c4ef7ef946360470901e5e29785ae1c486f44b229a89d
```

**Hash is unchanged. Zero KB writes.**

---

## Category Results

| Cat | Name | Count | % | Verified specs |
|-----|------|-------|---|----------------|
| (a) | phantom (placeholder backfill) | 673 | 71.4% | 119 |
| (b) | logical-assertion | 103 | 10.9% | 42 |
| (c) | abstract-description | 11 | 1.2% | 7 |
| (d) | migration-leftover | 117 | 12.4% | 10 |
| (e) | retired-but-unmarked | 39 | 4.1% | 0 |
| **(f)** | **other / unclassifiable** | **0** | **0.0%** | **0** |
| **Total** | | **943** | **100.0%** | **178** |

Sum invariant: 673 + 103 + 11 + 117 + 39 + 0 = **943** ✓

---

## Spec Status Crosstab

| Cat | implemented | retired | verified | total |
|-----|-------------|---------|----------|-------|
| (a) | 554 | 0 | 119 | 673 |
| (b) | 61 | 0 | 42 | 103 |
| (c) | 4 | 0 | 7 | 11 |
| (d) | 107 | 0 | 10 | 117 |
| (e) | 0 | 39 | 0 | 39 |

---

## JSON Raw Signals (Condition 3)

Every entry in `S291-phase1-categorization.json` contains all required raw signal fields:
`test_id`, `version`, `spec_id`, `spec_status`, `spec_type`, `test_type`, `changed_by`,
`changed_at`, `change_reason`, `category`, `evidence`.

Sample entry:
```json
{
  "test_id": "TEST-10513",
  "version": 1,
  "spec_id": "SPEC-1803",
  "spec_status": "implemented",
  "spec_type": "requirement",
  "test_type": "automated",
  "changed_by": "Claude/S215",
  "changed_at": "2026-03-17T14:16:51+00:00",
  "change_reason": "S215: backfill ... tests pass",
  "category": "a",
  "evidence": {"change_reason_phantom": "S215:.*tests pass"}
}
```

---

## Hand-Validation Results (Condition 5)

10 rows sampled per non-empty category (seed=42, reproducible). Findings:

### Category (a) — phantom: 10 sampled, 0 reclassifications

All 10 samples were S159-audit rows with "Enrich expected_outcome with behavioral
description (Fix B/C/D)" change reason. These are S198-origin placeholder rows that
S159-audit partially enriched (updated `expected_outcome`) but left without `test_file`.
Classification as phantom is correct — the enrichment preserved the placeholder structure.
One sample had `spec_id='135'` (non-canonical ID), confirming data quality issues in the
S198 batch. No reclassifications.

### Category (b) — logical-assertion: 10 sampled, 0 reclassifications

Split into two sub-patterns:
- **S149 assertion tracer** (6 rows): `changed_by=claude`, `s149_assertion_tracer` evidence.
  S149 was an assertion-tracing session that marked tests as "traced via spec assertion
  pass." These have row-level evidence linking them to a spec assertion pass event.
- **test_type=assertion + spec_has_passing_assertion_run** (4 rows): These include GOV-12,
  VR-widget-s0-layout, SPEC-1538, SPEC-1540 — governance/assertion type specs with
  passing `assertion_runs` records. Clearly correct.

Both sub-patterns satisfy the GO's Condition 2 requirement for row-level evidence (not
just spec type). No reclassifications.

### Category (c) — abstract-description: 10 sampled (all 11 available), 0 reclassifications

All samples are `test_type=logical`, `test_type=verification`, or `test_type=manual`
without an `assertion_runs` link. These legitimately describe abstract/pseudocode tests
per CLAUDE.md taxonomy. The `verification` type (TEST-S192-B6) correctly fell through (b)
because it had no assertion run. No reclassifications.

### Category (d) — migration-leftover: 10 sampled, 0 reclassifications

All 10 are `changed_by=S218-linkage-repair` with `s218_cleared_stale_test_file=True`.
S218 cleared stale `test_file` paths when they pointed to deleted/moved test files.
These rows formerly had `test_file` values; the clearing is a known maintenance action,
not placeholder backfill. Migration-leftover classification is correct.
No reclassifications.

### Category (e) — retired-but-unmarked: 10 sampled, 0 reclassifications

All 10 have `spec_status=retired`. Retired specs with passing fileless test rows should be
stale/retired themselves. Classification as "retired-but-unmarked" is trivially correct.
No reclassifications.

**Total reclassifications across all categories: 0 of 50. Threshold (≤2 per category) met.**
No re-run required.

---

## Phase 2 Recommendation

Per the proposal's decision tree:
- Category (a) phantom count: **673 > 100** ✓
- Category (a) rows underwriting a `verified` spec: **119 / 673 = 17.7%** — NOT > 50%

**Recommendation: Stream 2 absorbed into Phase 3 spec-hygiene remediation.**

The 119 phantom rows attached to `verified` specs are a real integrity issue but do not
warrant a standalone emergency P0 escalation. They should be incorporated into the next
spec-hygiene remediation bridge item as a separate sub-track targeting the verified specs
whose only evidence is phantom (a)-category rows.

The 554 phantom rows on `implemented` specs are lower risk — they are "verified" in name
only within the KB, not in business impact. They can be triaged in a batch hygiene pass
(revert to `specified` or retire) in a later Phase 3 round.

The 39 category (e) retired-but-unmarked rows should be marked stale as part of routine
housekeeping — no bridge item needed, acceptable as a hygiene WI.

---

## Verification Conditions (from proposal -001)

1. Script exists and runs read-only. **PASS** — `independent-progress-assessments/spec-hygiene/scripts/categorize_phantom_candidates.py`, hash unchanged.
2. Report exists with counts, samples, spec status crosstab, hand-validation, recommendation. **PASS** — `S291-phase1-stream2-categorization.md` contains all required sections.
3. JSON exists, valid, 943 entries. **PASS** — 465,251 bytes, 943 entries, all required fields present.
4. No KB writes (SQLite checksum unchanged). **PASS** — SHA256 identical before and after.
5. `assertion-check.py` hook output unchanged. **PASS** — no spec status changes occurred.

---

*© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
