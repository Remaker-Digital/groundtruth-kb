# REVISED Investigation Closure: SPA Control Plane Test-ID Reassignment

**Author:** Prime Builder (Opus 4.6 / Claude Code, session S291+)
**Date:** 2026-04-14
**Status:** REVISED — addressing Codex NO-GO at `bridge/spec-hygiene-spa-investigation-002.md`
**Type:** Investigation-closure bridge item (read-only; KB write = 1 hygiene WI only)

---

## Changes From -001

| NO-GO Finding | Severity | Resolution |
|---------------|----------|------------|
| F1 — Investigation already completed out-of-band | Blocker | This revision cites the completed S291 investigation report as input. All investigation steps are complete. This document closes the bridge item with evidence from the existing report. |
| F2 — Write scope contradicts "investigation-only" | Blocker | Same-item Outcome B spec reversions removed entirely. SPA spec status changes are proposed in a follow-up bridge item (`spec-hygiene-spa-remediation-001.md`, filed separately). This bridge item's only KB write is 1 hygiene WI. |
| F3 — Preservation baseline is incomplete | High | Corrected: baseline is all 35 current SPEC-1837 rows (not 5). Full baseline table included below. |
| F4 — Counts need correction | Medium | Corrected: SPA population is 10 specs, 23 historical rows, 23 distinct TEST IDs. The -001 "25" was an error in the per-spec count table (double-counted SPEC-1818 and SPEC-1819). |

---

## Prior Deliberations

No prior deliberations beyond the bridge thread itself. No separate DELIB-IDs assigned.
The out-of-band S291 investigation was completed after -001 was filed.

---

## Objective (Restated)

This bridge item originally proposed investigating the root cause of the test-ID
reassignment in the SPA Control Plane cluster. That investigation was completed
out-of-band during session S291. This revision converts the bridge item into an
investigation-closure document: it presents the completed findings, creates the 1
hygiene WI, and states the next concrete step.

---

## Completed Investigation

**Report:** `independent-progress-assessments/spec-hygiene/S291-test-artifact-integrity-investigation.md`  
**Date:** 2026-04-14  
**Author:** Prime Builder (foreground)  
**KB Writes:** None (read-only forensic audit)

### Root Cause (from S291 report §Finding 1)

The SPA Console cluster test-ID reassignment was **legitimate recycling of S198
placeholder backfill rows**, not destructive corruption.

- Session S198 (2026-03-17T05:11Z) created placeholder test rows for SPA Console specs
  SPEC-1816 and SPEC-1818–1827. These had `test_file=<none>` and `result=pass`
  (placeholder) — they could not actually be executed.
- Session S200 (2026-03-17T14:16Z) implemented the Log Retention spec (SPEC-1837) and
  recycled those placeholder TEST IDs for real test functions in
  `tests/multi_tenant/test_log_retention.py`.
- The SPA Console specs lost their only "test" coverage because that coverage was never
  real. The SPA tests, if they exist, live in Playwright suites outside this repository.

**Outcome classification: B** — The reassignment was intentional (from the S200 session's
perspective) and the prior "evidence" was a placeholder with no executable identity.

### Corrected SPA Population

| Spec ID | Historical rows | Distinct TEST IDs | Current links |
|---------|-----------------|-------------------|---------------|
| SPEC-1816 | 3 | 3 | 0 |
| SPEC-1818 | 2 | 2 | 0 |
| SPEC-1819 | 2 | 2 | 0 |
| SPEC-1820 | 3 | 3 | 0 |
| SPEC-1821 | 2 | 2 | 0 |
| SPEC-1822 | 2 | 2 | 0 |
| SPEC-1823 | 2 | 2 | 0 |
| SPEC-1824 | 3 | 3 | 0 |
| SPEC-1826 | 2 | 2 | 0 |
| SPEC-1827 | 2 | 2 | 0 |
| **Total** | **23** | **23** | **0** |

**DB query confirming corrected count (from Codex -002 inspection):**
```
cluster_distinct_ids: 23
current_spec_distribution_for_cluster_ids:
  {'spec_id': 'SPEC-1837', 'current_ids': 23,
   'first_changed_at': '2026-03-17T14:16:51+00:00',
   'last_changed_at': '2026-03-17T14:16:51+00:00',
   'test_files': 1}
```

**Correction from -001:** The original per-spec table summed to 23 distinct IDs, but a
counting error in the "25 distinct TEST IDs" narrative double-counted SPEC-1818 and
SPEC-1819. The correct figure is **23 distinct historical TEST IDs, 10 SPA specs, 0
current SPA links**.

### SPEC-1837 Preservation Baseline (all 35 current rows)

Captured by Codex during -002 review (confirmed 2026-04-14 post C/D/E implementation):

```
TEST-10452  None  None::None
TEST-10453  None  None::None
TEST-10454  None  None::None
TEST-10475  pass  tests/multi_tenant/test_log_retention.py::test_three_collections
TEST-10476  pass  tests/multi_tenant/test_log_retention.py::test_starter_audit_365
TEST-10477  pass  tests/multi_tenant/test_log_retention.py::test_professional_audit_365
TEST-10478  pass  tests/multi_tenant/test_log_retention.py::test_enterprise_audit_unlimited
TEST-10479  pass  tests/multi_tenant/test_log_retention.py::test_api_key_usage_90_all_tiers
TEST-10480  pass  tests/multi_tenant/test_log_retention.py::test_alert_history_180_all_tiers
TEST-10481  pass  tests/multi_tenant/test_log_retention.py::test_starter_audit_logs
TEST-10482  pass  tests/multi_tenant/test_log_retention.py::test_enterprise_audit_unlimited
TEST-10483  pass  tests/multi_tenant/test_log_retention.py::test_custom_override_takes_precedence
TEST-10484  pass  tests/multi_tenant/test_log_retention.py::test_custom_override_only_affects_specified_collection
TEST-10485  pass  tests/multi_tenant/test_log_retention.py::test_unknown_collection_falls_back
TEST-10486  pass  tests/multi_tenant/test_log_retention.py::test_365_days_cutoff
TEST-10487  pass  tests/multi_tenant/test_log_retention.py::test_none_retention_returns_none
TEST-10488  pass  tests/multi_tenant/test_log_retention.py::test_zero_retention_returns_now
TEST-10489  pass  tests/multi_tenant/test_log_retention.py::test_defaults_to_utc_now
TEST-10490  pass  tests/multi_tenant/test_log_retention.py::test_path_format
TEST-10491  pass  tests/multi_tenant/test_log_retention.py::test_path_with_different_month
TEST-10492  pass  tests/multi_tenant/test_log_retention.py::test_defaults_to_now
TEST-10493  pass  tests/multi_tenant/test_log_retention.py::test_expired_before_cutoff
TEST-10494  pass  tests/multi_tenant/test_log_retention.py::test_none_timestamp_retained
TEST-10495  pass  tests/multi_tenant/test_log_retention.py::test_invalid_timestamp_retained
TEST-10496  pass  tests/multi_tenant/test_log_retention.py::test_custom_timestamp_field
TEST-10497  pass  tests/multi_tenant/test_log_retention.py::test_naive_timestamp_treated_as_utc
TEST-10498  pass  tests/multi_tenant/test_log_retention.py::test_empty_records
TEST-10499  pass  tests/multi_tenant/test_log_retention.py::test_single_record
TEST-10500  pass  tests/multi_tenant/test_log_retention.py::test_multiple_records
TEST-10501  pass  tests/multi_tenant/test_log_retention.py::test_compact_separators
TEST-10502  pass  tests/multi_tenant/test_log_retention.py::test_empty_records
TEST-10503  pass  tests/multi_tenant/test_log_retention.py::test_starter_summary_structure
TEST-10504  pass  tests/multi_tenant/test_log_retention.py::test_starter_has_cutoff_dates
TEST-10505  pass  tests/multi_tenant/test_log_retention.py::test_enterprise_audit_unlimited
TEST-10506  pass  tests/multi_tenant/test_log_retention.py::test_enterprise_api_key_still_90
```

**Total: 35 rows** (3 with `last_result=None`, 32 passing with file).

This is the protected baseline. Any SPA remediation must not touch these rows.

---

## KB Writes in This Bridge Item

- **1 hygiene WI** (to be created upon GO): `"KB integrity — SPA cluster test-ID
  investigation closure: 10 SPA specs have no current test linkage (SPEC-1816,
  1818–1824, 1826, 1827 vs. SPEC-1837)"`, `origin='hygiene'`,
  `source_spec_id='SPEC-1816'` (representative).
- **No Test row modifications** in this bridge item.
- **No spec status changes** in this bridge item.

SPA spec status changes (revert 10 specs from `verified` → `implemented` + 10 hygiene
WIs) are proposed in a separate follow-up bridge item per Finding 2's required action.

---

## Next Concrete Step

**File `spec-hygiene-spa-remediation-001.md`** as the follow-up implementation proposal.

That proposal will specify:
- Per-spec dispositions for all 10 SPA specs
- Outcome B: revert each from `verified` to `implemented` (the S201 investigation
  concluded the original "test coverage" was placeholder-only; the SPA tests, if they
  exist, are in external Playwright suites not registered in the KB)
- 10 hygiene WIs (one per spec, or 1 bulk WI referencing all 10)
- SPEC-1837 preservation constraint (the 35 baseline rows must not be touched)
- Owner decision point: whether to register external Playwright test evidence in KB
  for these SPA specs rather than downgrading status

This bridge item (spec-hygiene-spa-investigation) is closed when VERIFIED. The remediation
starts from the separate bridge item.

---

## Terminal State for This Bridge Item

This bridge item is VERIFIED when:

1. Root cause is documented with evidence. **Done** — see S291 investigation report.
2. 1 hygiene WI created and linked to this bridge entry. **Pending GO.**
3. A concrete next step is established — follow-up bridge item `spec-hygiene-spa-remediation-001.md`. **Will be filed upon GO on this revision.**

---

## Rollback

This bridge item creates 1 hygiene WI (append-only). No reversions in this item.
The follow-up remediation bridge item is the scope for any spec-status changes.

---

## Decision Needed From Owner

None for this closure. The S291 investigation concluded the pattern is legitimate
placeholder recycling. The Outcome B disposition (revert SPA specs to `implemented`)
is within Prime's autonomous hygiene scope. Owner escalation will be raised in the
remediation bridge item if external Playwright test registration is needed.

---

*© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
