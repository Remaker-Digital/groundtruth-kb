# Investigation Proposal: SPA Control Plane Test-ID Reassignment Root Cause

**Author:** Prime Builder (Opus 4.6 / Claude Code, session S291+)
**Date:** 2026-04-14
**Type:** Investigation-only bridge item (no KB writes beyond 1 hygiene WI; no code changes)
**Companion:** `bridge/spec-hygiene-untested-verified-005.md` (Tracks C/D/E)

---

## Prior Deliberations

No prior deliberations found for SPA cluster test-ID reassignment, SPA Control Plane
verification integrity, or SPEC-1837 test-ID origin. Codex confirmed in the
`spec-hygiene-untested-verified-004.md` review.

---

## Objective

Determine the root cause of the test-ID reassignment in the SPA Control Plane cluster:
**why do TEST IDs historically linked to SPEC-1816/1818–1827 now point to SPEC-1837
(`Log Retention Policy and Archival`) in their latest versions?**

This is an investigation to produce a documented finding and a concrete next-step
disposition. Implementation (if needed) follows in a separate bridge item.

---

## Scope

- **10 SPA Control Plane specs:** SPEC-1816, SPEC-1818, SPEC-1819, SPEC-1820,
  SPEC-1821, SPEC-1822, SPEC-1823, SPEC-1824, SPEC-1826, SPEC-1827
- **Known TEST IDs currently covering SPEC-1837:** TEST-10481, TEST-10482, TEST-10483,
  TEST-10484, TEST-10485 (and possibly TEST-10505, TEST-10506 per Codex review -003)
- **SPEC-1837:** `Log Retention Policy and Archival`, status `implemented`, type `requirement`

---

## Exact DB Counts (from Codex NO-GO -004 inspection)

| Spec ID | all_rows | distinct_ids | current_links |
|---------|----------|--------------|---------------|
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
| **Total** | **25** | **25** | **0** |

---

## SPEC-1837 Preservation Constraint

The 5 current SPEC-1837 test rows (TEST-10481..10485) are **passing evidence** for a
separate spec and must not be modified by this investigation. This investigation
queries but does not write to any TEST row currently covering SPEC-1837.

---

## Investigation Steps

1. **Query test version history for SPA cluster.** For each of the 25 distinct TEST IDs
   historically linked to SPEC-1816/1818–1827:
   - Retrieve all version rows: `spec_id`, `version`, `test_file`, `test_function`,
     `last_result`, `created_at` (or equivalent timestamp if available).
   - Identify the version at which `spec_id` changed from a SPA spec to SPEC-1837.

2. **Inspect SPEC-1837 content.** Read `SPEC-1837` current version. Confirm whether
   `Log Retention Policy and Archival` has any functional relationship to SPA Control
   Plane behavior. This determines whether the reassignment was intentional or erroneous.

3. **Cross-reference with KB write history.** If KB session metadata or commit history
   is available, identify the session (session ID or date range) when the reassignment
   occurred. Check MEMORY.md and CLAUDE_ARCHIVE.md for relevant session notes.

4. **Inspect test files on disk.** For each TEST ID now covering SPEC-1837, check whether
   `test_file` and `test_function` describe SPA behavior or log-retention behavior.
   This is the clearest signal of whether the reassignment was intentional.

5. **Document findings:** Root cause classification (see Possible Outcomes below) plus
   evidence for the classification.

---

## Possible Outcomes and Dispositions

### Outcome A — Reassignment was accidental (bulk-write error, session drift)

Indicators: Test functions describe SPA UI/API behavior, not log retention.
`spec_id` changed in a batch that also affected other specs.

Disposition: Create a follow-up implementation bridge item
(`spec-hygiene-spa-restore-001.md`) proposing:
- New Test artifacts (new TEST IDs) for each SPA spec with a valid test function on disk.
  (Do not reassign SPEC-1837's current TEST IDs.)
- Or, if the test functions are gone from disk: revert each SPA spec to `implemented`
  with a hygiene WI, similar to Tracks C/D/E.

### Outcome B — Reassignment was intentional (SPA restructured under SPEC-1837)

Indicators: Test functions describe log-retention behavior relevant to both SPA and
backend. A session note or commit references consolidating SPA tests under SPEC-1837.

Disposition: Revert each of the 10 SPA specs from `status = 'verified'` to
`status = 'implemented'` with `change_reason` recording the rationale. Create 1
hygiene WI per spec (or 1 WI covering all 10). Document that SPEC-1837 legitimately
absorbed the SPA test evidence.

### Outcome C — Mixed (some intentional, some accidental)

Handle per-spec using A or B disposition as appropriate. Document which specs fall
into each category.

---

## KB Writes in This Bridge Item

- **1 hygiene WI** created: `"KB integrity — SPA cluster test-ID reassignment
  investigation (SPEC-1816/1818–1827 vs. SPEC-1837)"`, `origin='hygiene'`.
- No Test row modifications in this bridge item.
- No spec status changes in this bridge item.
- If Outcome B is confirmed during investigation and the revertion is straightforward
  (≤ 10 simple spec-status writes with hygiene WIs), Prime may include the reversions
  in the post-investigation report and request a combined VERIFIED. If the work is
  more complex, a follow-up bridge item is required.

---

## Terminal State for This Bridge Item

This bridge item is VERIFIED when:

1. Root cause is documented in the post-investigation report with evidence (version
   history, test-file inspection, session-note cross-reference).
2. 1 hygiene WI created and linked to this bridge entry.
3. A concrete next step is established — one of:
   - Follow-up implementation bridge item `spec-hygiene-spa-restore-001.md` filed (Outcome A).
   - Outcome B reversions completed and post-impl report filed requesting VERIFIED.
   - Outcome B reversions scoped for follow-up if complex.

"Investigation in progress" is not a terminal state. The investigation must complete
with a documented outcome before VERIFIED is requested.

---

## Rollback

This bridge item proposes only a hygiene WI (append-only) and read-only queries.
Nothing to roll back.

---

## Decision Needed From Owner

**None.** Investigation-only work is within Prime's autonomous scope. If Outcome B
requires reverting 10 verified specs, that is a hygiene action covered by existing
WI taxonomy (no new schema changes). Prime will raise owner questions only if the
investigation reveals unexpected scope or decisions outside the current artifact model.

---

*© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
