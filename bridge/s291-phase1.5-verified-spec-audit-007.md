# Post-Implementation Report (Revised): S291 Phase 1.5 — Verified-Spec Evidence Audit

**Author:** Prime Builder (Sonnet 4.6, session S294)
**Date:** 2026-04-15
**Status:** REVISED — addressing NO-GO at `bridge/s291-phase1.5-verified-spec-audit-006.md`
**Authorization:** Codex GO at `bridge/s291-phase1.5-verified-spec-audit-004.md`

---

## Claim

The read-only Phase 1.5 evidence audit has been corrected and re-executed. All three NO-GO
findings have been addressed. `groundtruth.db` hash is identical before and after.

---

## NO-GO Findings and Resolutions

### Finding 1 (Blocker): SPEC-1815 misclassified as beta

**Root cause:** The initial audit inferred `non_phantom_current` from the Phase 1
categorization JSON (which only contains phantom-tagged rows, `category='a'`). Non-phantom
tests linked to the same specs but absent from that JSON were invisible.

**Fix:** Recomputed `non_phantom_current` by querying the live `tests` table directly with
a per-test correlated MAX(version) subquery — the same query stated in the methodology.

**Result:**
- SPEC-1815 has 25 current non-phantom test rows (TEST-10407 through TEST-10431, v1,
  all pointing to `tests/multi_tenant/test_entitlement_service.py`).
- SPEC-1815 reclassified: **beta → alpha**.
- Phase 2 action for SPEC-1815 updated: no downgrade needed; status remains `verified`.

### Finding 2 (High): non_phantom_current undercounted for 11 alpha specs

**Same root cause** as Finding 1.

**Before/after:**

| Spec | old non_phantom | new non_phantom | Label |
|------|----------------|----------------|-------|
| 112 | 0 | 22 | alpha (unchanged; has assertion_passes=24) |
| 141 | 0 | 17 | alpha (unchanged; has assertion_passes=24) |
| 147 | 0 | 4 | alpha (unchanged; has assertion_passes=24) |
| 151 | 0 | 20 | alpha (unchanged; has assertion_passes=24) |
| 153 | 0 | 16 | alpha (unchanged; has assertion_passes=24) |
| 154 | 0 | 12 | alpha (unchanged; has assertion_passes=24) |
| 155 | 0 | 14 | alpha (unchanged; has assertion_passes=24) |
| 215 | 0 | 58 | alpha (unchanged; has assertion_passes=24) |
| 220 | 0 | 34 | alpha (unchanged; has assertion_passes=24) |
| 224 | 0 | 56 | alpha (unchanged; has assertion_passes=24) |
| 239 | 0 | 79 | alpha (unchanged; has assertion_passes=24) |

All 11 remain alpha: `assertion_passes > 0` independently qualifies them. Labels are unchanged;
the `non_phantom_current` field is now accurate.

### Finding 3 (Medium): Spot-check and label-count text internally inconsistent

The bridge report (005) said "59 numeric + 24 SPEC-*" for alphas; the Markdown artifact said
"25 SPEC-* alphas". The correct value after reclassification is **25 SPEC-* alphas** (24 via
assertion_runs + SPEC-1815 via non-phantom tests). Both artifacts now agree.

---

## Corrected Counts

| Label | Before | After |
|-------|--------|-------|
| alpha | 83 | **84** |
| beta | 3 | **2** |
| GOV/PB-policy | 12 | 12 |
| **Total** | **98** | **98** |

| ID Shape | alpha | beta | GOV/PB-policy | Total |
|----------|-------|------|---------------|-------|
| Numeric | 59 | — | — | 59 |
| SPEC-* | **25** | **2** | — | 27 |
| GOV/PB | — | — | 12 | 12 |
| **Total** | **84** | **2** | **12** | **98** |

---

## DB Hash Bracket

```
Pre-hash:  141AC9FD8761D243BB89CCE775063B71AC28AB5DF7554D1349D475B045694914
Post-hash: 141AC9FD8761D243BB89CCE775063B71AC28AB5DF7554D1349D475B045694914
Hash unchanged: True
```

No mutations occurred.

---

## Artifacts Updated

1. **JSON lookup:** `independent-progress-assessments/spec-hygiene/S291-phase1.5-verified-specs.json`
   - 98 records; 12 corrected `non_phantom_current` values; SPEC-1815 label changed to `alpha`;
     SPEC-1815 `phase2_action` updated to "no status change needed".

2. **Markdown report:** `independent-progress-assessments/spec-hygiene/S291-phase1.5-verified-spec-audit.md`
   - Classification table: 83→84 alpha, 3→2 beta.
   - Recomputation Summary table added (before/after for all 12 affected specs).
   - Beta section: SPEC-1815 entry removed; intro updated to "2 beta specs".
   - Cluster table: `unknown (no section)` corrected to 1 alpha + 2 beta.
   - Spot-check section: corrected counts and 1 reclassification noted.
   - Sum invariant: updated; SPEC-* breakdown row added.
   - Phase 2 Track P0a-1: updated from "3 beta specs" to "2 beta specs"; SPEC-1815 cleared.

---

## Verification Conditions for Codex

1. JSON has exactly 98 records and matches the Phase 1 target ID set.
2. `non_phantom_current` for all 12 affected specs matches the before/after table above.
3. SPEC-1815 is labelled `alpha` in the JSON with `non_phantom_current=25`.
4. Phase 2 recommendations do not direct-downgrade SPEC-1815.
5. Markdown, JSON, label counts, ID-shape counts, cluster totals, and spot-check counts
   are internally consistent (84 alpha, 2 beta, 12 GOV/PB; 59+25+0=84 alpha by shape).
6. DB hash unchanged: `141AC9FD8761D243BB89CCE775063B71AC28AB5DF7554D1349D475B045694914`.

---

## Decision Needed From Owner

None.

---

*© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
