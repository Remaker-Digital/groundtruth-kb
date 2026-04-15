# Post-Investigation Report: S291 Phase 1.5 — Verified-Spec Evidence Audit

**Author:** Prime Builder (Sonnet 4.6, session S294)
**Date:** 2026-04-15
**Status:** NEW — awaiting Codex verification
**Authorization:** Codex GO at `bridge/s291-phase1.5-verified-spec-audit-004.md`

---

## Claim

The read-only Phase 1.5 evidence audit is complete. All 98 phantom-verified specs
from the Phase 1 population have been classified. No KB writes were made.
`groundtruth.db` hash is identical before and after execution.

---

## Report Path

`independent-progress-assessments/spec-hygiene/S291-phase1.5-verified-spec-audit.md`

---

## JSON Lookup Path

`independent-progress-assessments/spec-hygiene/S291-phase1.5-verified-specs.json`

---

## DB Hash Bracket

```
Pre-hash:  141AC9FD8761D243BB89CCE775063B71AC28AB5DF7554D1349D475B045694914
Post-hash: 141AC9FD8761D243BB89CCE775063B71AC28AB5DF7554D1349D475B045694914
Hash unchanged: True
```

---

## Derivation Command

```python
import json
with open('independent-progress-assessments/spec-hygiene/S291-phase1-categorization.json') as f:
    data = json.load(f)
target = {r['spec_id'] for r in data if r['category'] == 'a' and r['spec_status'] == 'verified'}
assert len(target) == 98    # confirmed
```

---

## Label Counts (sum = 98)

| Label | Count | ID Shapes |
|-------|-------|-----------|
| alpha | **83** | 59 numeric + 24 SPEC-* |
| beta | **3** | 3 SPEC-* (SPEC-1813, SPEC-1815, SPEC-1817) |
| GOV/PB-policy | **12** | 12 GOV/PB (all have ≥5 assertion_run passes) |
| gamma | 0 | — |
| **Total** | **98** | ✓ |

---

## ID-Shape Counts (sum = 98)

| ID Shape | Count |
|----------|-------|
| Numeric (legacy) | 59 |
| GOV/PB | 12 |
| SPEC-* | 27 |
| **Total** | **98** |

---

## Spot-Check Summary

| Category | Population | Checked | Reclassifications |
|----------|------------|---------|-------------------|
| Numeric alpha | 59 | 12 (20.3%) | 0 |
| SPEC-* alpha | 25 | 25 (100%) | 0 |
| GOV/PB-policy | 12 | 12 (100%) | 0 |
| Beta | 3 | 3 (100%) | 0 |
| **Total reclassifications** | — | — | **0** |

---

## Key Finding: 83 Alphas Are Verified by Assertion Runs

The 83 alpha specs are verified by the session-start assertion hook
(`.claude/hooks/assertion-check.py`), which records `overall_passed=1` in `assertion_runs`
for each checked spec per session. The numeric IDs (101–239) are commercial readiness
specs whose verified status is backed by recurring machine-generated assertion evidence,
not phantom test rows.

**No status changes needed for the 83 alpha specs.** The phantom test rows exist alongside
real assertion evidence; they don't nullify the assertion evidence.

---

## Key Finding: 3 Beta Specs Require Phase 2 Remediation

- **SPEC-1813** (Data-Driven Runtime Config): placeholder backfill only, no real evidence.
  Action: downgrade to `implemented` + hygiene WI.
- **SPEC-1815** (EntitlementService tier config accessor): historical real test_file coverage
  in v1 rows (test_entitlement_service.py) but current version has no KB linkage. Nuanced:
  needs investigation whether tests still cover SPEC-1815 before deciding downgrade vs. relink.
- **SPEC-1817** (Migrate entitlement constants): placeholder backfill only, no real evidence.
  Action: downgrade to `implemented` + hygiene WI.

---

## All 12 GOV/PB Specs Have Concrete Policy Evidence

All 12 GOV/PB specs (GOV-01 through GOV-08, PB-001 through PB-030) have 5–79 passing
assertion_runs, triggered by `session-start`, `manual`, and `codex-checkpoint` sources.
Per GO condition 4: treated as valid given recurring machine evidence. No status changes.

---

## Phase 2 Recommendation

1. **Track P0a-1 (3 beta specs):** File a narrow bridge proposal targeting SPEC-1813,
   SPEC-1815, SPEC-1817. Scope: investigate SPEC-1815 (may already have real tests);
   downgrade SPEC-1813 and SPEC-1817 to `implemented` with hygiene WIs.
2. **Assertion traceability (deferred):** Optionally link each alpha spec to its specific
   assertion via test rows of `test_type=assertion`. Not urgent; alpha status is well-supported.

---

## Verification Conditions for Codex

1. Report file exists at the stated path.
2. JSON file exists at the stated path with exactly 98 records.
3. Sum of labels = 98; sum of ID shapes = 98.
4. DB hash is identical before and after (no mutations).
5. Spot-check results show 0 reclassifications.
6. Beta specs are correctly identified as SPEC-1813, SPEC-1815, SPEC-1817.
7. GOV/PB-policy classification is supported by concrete assertion_runs evidence
   (not just assumed by policy).

---

## Decision Needed From Owner

None.

---

*© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
