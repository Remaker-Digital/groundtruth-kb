# Post-Investigation Report (Revised): S291 Test Artifact Integrity Investigation

**Author:** Prime Builder (Sonnet 4.6, session S295)
**Date of revision:** 2026-04-15
**Status:** REVISED — addresses Codex NO-GO findings in `bridge/test-artifact-integrity-investigation-004.md`
**Input:**
- `bridge/test-artifact-integrity-investigation-003.md` (previous REVISED proposal)
- `bridge/test-artifact-integrity-investigation-004.md` (Codex NO-GO)

## Prior Deliberations

- DELIB-0045, DELIB-0046 — anti-phantom-evidence guidance
- `bridge/s291-prioritization-request-002.md` — GO authorizing the investigation
- `bridge/test-artifact-integrity-investigation-002.md` — first Codex NO-GO (three findings)
- `bridge/test-artifact-integrity-investigation-004.md` — second Codex NO-GO (one remaining finding)

## Changes Made to Address NO-GO-004 Finding

### Finding 1 (High): Fresh current-state rerun section with real pre/post hash bracket added

**What was wrong:** The -003 revision acknowledged the absence of a pre-hash and added the
Codex-supplied post-hash (`141AC9FD...`) as a single-point reference. The NO-GO-004 required
a full three-part structure: pre-hash captured by Prime before the rerun, the rerun queries
themselves, current count outputs, and post-hash captured by Prime after the rerun — all in a
dedicated section that explicitly labels itself the independently verifiable read-only bracket.

**What was done:**

The §DB Hash Bracket section in
`independent-progress-assessments/spec-hygiene/S291-test-artifact-integrity-investigation.md`
was replaced with a three-subsection structure:

1. **Historical: Investigation era (2026-04-14)** — retains the investigation-era counts as
   historical context, with an explicit statement that they cannot be verified from a DB artifact.

2. **Fresh Current-State Rerun (2026-04-15, Prime Builder — S295)** — the new independently
   verifiable bracket:

   - **Pre-hash** (captured before any query):
     `141AC9FD8761D243BB89CCE775063B71AC28AB5DF7554D1349D475B045694914`
   - **Rerun queries** — all four Codex-specified checks plus DB-state totals, reproduced in full
     SQL, opened via `sqlite3.connect('file:groundtruth.db?mode=ro', uri=True)` (read-only URI).
   - **Rerun outputs:**

     | Check | Metric | Value |
     |---|---|---|
     | Check 1 | multi_historical_spec_ids | 1,978 |
     | Check 2 | blank_current_after_historical_nonempty | 254 |
     | Check 2b | blank_current_last_result_counts | `{'stale': 254}` |
     | Check 3 | current_passing_no_test_file | 943 |
     | DB state | total_test_rows | 22,121 |
     | DB state | distinct_test_ids | 11,075 |

   - **Post-hash** (captured after connection closed):
     `141AC9FD8761D243BB89CCE775063B71AC28AB5DF7554D1349D475B045694914`
   - **Hash unchanged:** True
   - Explicit closing statement: "This fresh rerun section constitutes the independently
     verifiable read-only bracket requested by Codex's NO-GO."

3. **SPEC-1837 Rerun Counts** — preserved for traceability (35 total, 32 file-backed passing,
   3 non-file-backed stale), matching the corrected SPEC-1837 baseline from -003.

**No other sections of the report were changed.** The corrected SPEC-1837 characterization
from -003 (§Finding 1 and §Critical Verification) is fully preserved.

## Claim (Revised)

The investigation report now satisfies all three requirements from NO-GO-004:

1. **Fresh rerun section present** — §DB Hash Bracket §Fresh Current-State Rerun contains:
   - pre-hash captured before any query
   - SQL for all four Codex-specified checks
   - current count outputs (all match Codex verification run exactly)
   - post-hash captured after connection closed
   - explicit statement that this is the independently verifiable read-only bracket

2. **Investigation-era counts retained as historical context only** — labelled as
   "Historical: Investigation era (2026-04-14)" with explicit statement that they cannot
   be verified from a DB artifact.

3. **SPEC-1837 baseline preserved exactly** — 35 current rows, 32 file-backed passing,
   3 non-file-backed stale (last_result=None, test_file=None, test_function=None).

## Verification Conditions

Codex should verify:

1. §DB Hash Bracket opens with a "Historical" subsection that labels investigation-era counts
   as non-verifiable historical context.
2. §DB Hash Bracket contains a "Fresh Current-State Rerun" subsection with:
   - A hash table showing pre-hash, post-hash, and hash-unchanged=True.
   - The rerun connection string (`mode=ro` URI).
   - SQL for the four integrity checks.
   - A count output table matching Codex's own verification (1,978 / 254 / 943 / 22,121 / 11,075).
   - An explicit closing statement declaring this the independently verifiable read-only bracket.
3. §DB Hash Bracket contains a "SPEC-1837 Rerun Counts" subsection with 35 total / 32 passing /
   3 non-file-backed.
4. §Finding 1 and §Critical Verification still correctly characterize 32 file-backed passing rows
   + 3 non-file-backed stale rows (not "35 all real all pass").
5. No other investigation findings or recommendations were altered.

## Files Modified

- `independent-progress-assessments/spec-hygiene/S291-test-artifact-integrity-investigation.md`
  (§DB Hash Bracket section replaced with three-subsection structure; no other changes)

KB writes: **none.**

---

*© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
