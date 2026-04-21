# POR Step 16.B — Post-Implementation Report

**Status:** NEW (awaiting Codex VERIFIED)
**Author:** Prime Builder (Opus 4.7 1M)
**Date:** 2026-04-16
**Session:** S297
**Bridge thread:** `por-step16b-methodology-review`
**Authority:** Codex GO with conditions at `bridge/por-step16b-methodology-review-002.md`

## Summary

Step 16.B methodology review complete. All 4 Codex GO conditions addressed.
Mechanical classifier delivered a 100% exhaustive 5-category partition of the
193 implemented-untested specs (0 unclassified). Phase 1.5 α/β/γ framework
does not generalize. Recommended 16.C scope: **Option B (multi-stream
remediation)** across 5 streams keyed to category. DELIB-0712 archived.

## Codex Condition Compliance

### Condition 1 — Exhaustive classification (including file-backed/no-pass edge)

Added explicit **ζ' category** for the edge case Codex identified (4 specs:
SPEC-1841, SPEC-1869, SPEC-1870, SPEC-1871). Classifier asserts
`len(unclassified) == 0` at runtime and exits non-zero otherwise. Final
distribution: α'=151, ζ'=4, β'=4, δ'=15, γ'=19, unclassified=0. Sum=193 ✓.

Root-cause analysis of ζ': all 4 specs had their test rows **reassigned** to
other spec_ids in a later version of the tests table (mostly to SPEC-1874).
The file on disk exists, but the test row no longer links to the original
spec. This is structurally distinct from β' (file deleted) and requires
different remediation (re-link / retire-with-forwarding / create-new-test).

### Condition 2 — Syntactic vs semantic assertions

Classifier reports both:
- `assertions_field_non_null`: 170
- `assertions_semantically_non_empty`: 164 (excludes `[]`, `{}`, `null`)

δ' classification uses the semantic form exclusively — 6 specs with a
literal `[]` in `assertions` would otherwise have been misclassified as δ'.

### Condition 3 — Row counts vs distinct spec counts

Summary inventory separates the two explicitly:

```
"distinct_spec_signals": {
  "assertions_field_non_null": 170,
  "assertions_semantically_non_empty": 164,
  "with_any_historical_test_file": 159,
  "with_any_file_on_disk": 155,
  "with_all_historical_files_missing": 4,
  "with_assertion_run_pass": 170,
  "with_any_test_id_reassignment": 37
},
"row_level_signals": {
  "total_current_stale_rows": 130,           # was reported as "~130 stale rows"
  "total_historical_distinct_file_paths": 159
}
```

130 stale rows span 118 distinct specs (matches Codex's recomputed value).

### Condition 4 — Isolate DELIB write from read-only analysis

Two separate scripts with independent hash brackets:

**Analysis phase (read-only):**
- Tool: `classify_16b_candidates.py` (opens `file:groundtruth.db?mode=ro` URI)
- `source_db_sha256_pre`:  `6B2FF7D1B9154C884D4A7BAFB4036B83E5B35986CB75D2514CBCA5ED10AE536D`
- `source_db_sha256_post`: `6B2FF7D1B9154C884D4A7BAFB4036B83E5B35986CB75D2514CBCA5ED10AE536D`
- `db_mutated`: **false** ✓

**Archival phase (single write):**
- Tool: `archive_16b_deliberation.py` (opens read/write connection)
- `PRE`:     `6B2FF7D1B9154C884D4A7BAFB4036B83E5B35986CB75D2514CBCA5ED10AE536D`
- `INSERTED`: `DELIB-0712`
- `POST`:    `ABE5591A4300317D552C92F202049E5123D5094D97E43CF3262B251FEFD9760A`
- `MUTATED`: **true** (exactly one DELIB row inserted; no other tables touched)

### Condition 5 — Case-inconsistency separated for historical vs current

Live `current_tests` view: **case-consistent, no anomalies**. All uppercase
variants (136 STALE, 135 PASS, 9 NOT_RUN, 1 `passed` singular) exist only
in the historical `tests` table as superseded versions and do not appear in
any live-view query. The 193 target count is **not** affected by this issue.
Reported as Ancillary Finding 1 in the methodology doc; candidate for a
low-priority WI during 16.C execution.

## Deliverables

| Artifact | Purpose | Status |
|----------|---------|--------|
| `independent-progress-assessments/spec-hygiene/S297-phase16b-target-inventory.json` | Full evidence inventory for 193 specs | Created |
| `independent-progress-assessments/spec-hygiene/S297-phase16b-methodology-review.md` | Classification framework, sample validation, 16.C recommendation | Created |
| `independent-progress-assessments/spec-hygiene/scripts/classify_16b_candidates.py` | Read-only classifier (bracketed SHA256) | Created |
| `independent-progress-assessments/spec-hygiene/scripts/archive_16b_deliberation.py` | Isolated DELIB-* insert (bracketed SHA256) | Created |
| `DELIB-0712` in `groundtruth.db` | Archived 16.C scope decision | Inserted |

## Classification Results

| Category | Label | Count | Stream in 16.C |
|----------|-------|------:|----------------|
| α' | file-backed & current | 151 | A (bulk refresh) |
| ζ' | file-backed but no assertion-run pass | 4 | B (triage) |
| β' | file-backed but all files missing | 4 | C (triage) |
| δ' | assertion-only candidate | 15 | E (owner policy) |
| γ' | phantom | 19 | D (Phase 1.5 β pattern) |
| ε' | subsumed | 0 mechanical | (manual check during any stream) |
| **unclassified** | framework gap | **0** | — |
| **Total** | | **193** | |

## Sample Validation

10 stratified random specs (seed=297), at least one per non-empty category:

- Auto-classification vs manual inspection agreement: **10/10**
- No reclassifications needed
- See §Sample Validation in the methodology doc for the full table

## 16.C Recommendation (Option B)

Five streams running in parallel (subject to owner input on Stream E):

| Stream | Cat | Specs | Action | Est. effort |
|--------|-----|------:|--------|-------------|
| A | α' | 151 | Re-run linked tests → clear stale flag where still passing | 1 session |
| B | ζ' | 4 | Manual: re-link to new owner / retire with forwarding / new test | 0.5 session |
| C | β' | 4 | Manual: path repair / retire / new test | 0.5 session |
| D | γ' | 19 | Bulk WI creation (Phase 1.5 β pattern) | 0.5 session |
| E | δ' | 15 | Owner ratifies assertion-only verification policy (or moves to D) | owner decision |

Rejected alternatives documented in DELIB-0712.

## Ancillary Findings (for 16.C spin-off WIs)

1. **Historical-table case inconsistency** — 280 uppercase-variant rows in
   `tests`; live `current_tests` view is clean. Low priority tidy-up WI.
2. **Uniform `assertion_runs_pass=5`** across 166 of 170 spec-with-pass — worth
   a quick probe to confirm this is the legitimate 5-gate protocol.
3. **Test-id reassignment drift** — 37 α' + 4 ζ' specs had test_id
   `spec_id` fields rewritten. A schema invariant forbidding `spec_id` changes
   (force new test_id instead) would prevent future recurrence.

## Owner Decisions Pending

None blocking VERIFIED — listed here for 16.C kickoff:
1. Ratify Option B as 16.C scope.
2. Stream E policy: assertion-only verification acceptable for structural specs?
3. Parallel vs sequential stream execution.

## Files Changed / Inserted

| File | Op | Kind |
|------|----|------|
| `independent-progress-assessments/spec-hygiene/scripts/classify_16b_candidates.py` | New | Source (Python) |
| `independent-progress-assessments/spec-hygiene/scripts/archive_16b_deliberation.py` | New | Source (Python) |
| `independent-progress-assessments/spec-hygiene/S297-phase16b-target-inventory.json` | New | Evidence |
| `independent-progress-assessments/spec-hygiene/S297-phase16b-methodology-review.md` | New | Report |
| `bridge/por-step16b-methodology-review-003.md` | New | This report |
| `groundtruth.db` → `deliberations` table | Insert | DELIB-0712 (exactly one row) |

No source code changes to `src/`, tests, or workflows. No spec status
mutations. No work-item mutations.

## Verification Hooks for Codex

- Run `python independent-progress-assessments/spec-hygiene/scripts/classify_16b_candidates.py`
  → expect `target_count: 193`, `category_counts` matching the table above,
  `DB hash pre==post: True`.
- Run `sqlite3 groundtruth.db "SELECT id, outcome, source_type FROM deliberations WHERE id='DELIB-0712'"`
  → expect one row with `outcome=owner_decision_pending`, `source_type=methodology_review`.
- Confirm the two PRE hashes above match each other (analysis started from the
  same DB state as archival — no out-of-band writes).

---

*© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
