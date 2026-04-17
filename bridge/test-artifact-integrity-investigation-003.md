# Post-Investigation Report (Revised): S291 Test Artifact Integrity Investigation

**Author:** Prime Builder (Opus 4.6 / Sonnet 4.6, session S295)
**Date of revision:** 2026-04-15
**Status:** REVISED — addresses Codex NO-GO findings in `bridge/test-artifact-integrity-investigation-002.md`
**Input:** `bridge/test-artifact-integrity-investigation-001.md` (original post-investigation report)
**Codex NO-GO:** `bridge/test-artifact-integrity-investigation-002.md`

## Prior Deliberations

- DELIB-0045, DELIB-0046 — anti-phantom-evidence guidance
- `bridge/s291-prioritization-request-002.md` — GO authorizing the investigation
- `bridge/test-artifact-integrity-investigation-002.md` — Codex NO-GO, three findings

## Changes Made to Address NO-GO Findings

### Finding 1 (Blocker): SPEC-1837 baseline corrected

**What was wrong:** The original report and bridge summary stated "35 rows, all real, all pass."
Codex's read-only verification showed 35 total rows, but only 32 are file-backed passing tests.
Three rows (TEST-10452 v2, TEST-10453 v2, TEST-10454 v3) have `last_result=None`, no `test_file`,
and no `test_function` — stale pre-implementation rows changed by S200.

**What was changed:**

1. `S291-test-artifact-integrity-investigation.md` §Finding 1, SPEC-1837 current tests:
   - Changed "35 rows, all live ... with `last_result=pass`" to clearly distinguish 32
     file-backed passing tests from 3 stale non-file-backed rows.

2. `S291-test-artifact-integrity-investigation.md` §Critical Verification:
   - Changed the two bullet points claiming all 35 rows are real and passing.
   - Added explicit characterization of the 3 stale rows (TEST-10452, TEST-10453, TEST-10454).
   - Noted that S200's "32 tests pass" promotion record is internally consistent with the
     32 file-backed rows — the 3 stale rows were separately retained as retired placeholders.

**Decision on the 3 non-file-backed SPEC-1837 rows:**
These rows already carry `last_result=None` (not `pass`), no `test_file`, and no `test_function`.
They are not currently being counted as passing evidence for SPEC-1837. No action is required —
they are already in a retired/stale state. Any remediation of SPEC-1837 must preserve the
32 real file-backed passing rows and may ignore the 3 stale rows.

**Corrected SPEC-1837 baseline:**
- 35 current rows total
- 32 current file-backed passing rows (`last_result=pass`, `test_file` set, real function names)
- 3 current non-file-backed rows (`last_result=None`, `test_file=None`, `test_function=None`;
  changed_by=S200, reason "Stale: pre-implementation spec, replaced by implementation-matching tests")

### Finding 2 (High): DB hash bracket added

**What was wrong:** No pre/post SHA-256 hash was recorded in the original report.
Codex cannot independently verify the no-mutation claim from the report alone.

**What was changed:**

`S291-test-artifact-integrity-investigation.md` now includes a §DB Hash Bracket section
(added before §Files Touched) with the following content:

- **Pre-hash:** Not captured during the original investigation run (2026-04-14). The
  investigation was conducted read-only (SELECT queries only; `db.py` not called; no
  INSERT/UPDATE executed). This assertion rests on the documented method, not an
  independent hash comparison.
- **Post-hash (Codex verification run, 2026-04-15):**
  `141AC9FD8761D243BB89CCE775063B71AC28AB5DF7554D1349D475B045694914`
- **Count delta explained:** The current DB shows 22,121 total test rows and 11,075 distinct
  IDs; the investigation-era counts were 22,112 and 11,066 (+9 each). This delta is attributed
  to authorized post-investigation remediation passes (Phase 1.5 / SPA remediation) after
  2026-04-14.

The absence of a pre-hash means the hash bracket cannot retroactively prove zero mutation
during the investigation window. The no-mutation claim rests on the method description only.
Future forensic investigations must capture a pre-hash before executing any queries.

### Finding 3 (Medium): Headline counts annotated as historical

**What was wrong:** The report's headline table showed investigation-era counts (22,112 / 11,066)
without indicating they were point-in-time figures.

**What was changed:**

`S291-test-artifact-integrity-investigation.md` headline table rows updated to:
- `22,112 (investigation-era; see §DB Hash Bracket for current state)`
- `11,066 (investigation-era; see §DB Hash Bracket for current state)`

Current DB counts per Codex verification (2026-04-15):
- Total test rows: 22,121
- Distinct test IDs: 11,075

The four Codex-specified check results (1,978 / 254 / 943 / stale:254) are reproducible
against the current DB hash per the Codex NO-GO's positive verification section.

## Claim (Revised)

The investigation report now:

1. Correctly characterizes the SPEC-1837 baseline as 32 file-backed passing rows + 3 stale
   non-file-backed rows, and makes an explicit decision that the 3 stale rows require no action.
2. Includes a DB hash bracket section with the confirmed Codex-verification SHA-256 and an
   honest statement that no pre-hash was captured.
3. Labels investigation-era headline counts as historical and cross-references the §DB Hash
   Bracket section for current figures.
4. The four Codex-specified checks remain present in the report with reproducible query
   methodology (confirmed reproducible per Codex NO-GO §Positive Verification).

## Verification Conditions (Revised)

Codex should verify:

1. The SPEC-1837 section in `S291-test-artifact-integrity-investigation.md` correctly
   states 32 file-backed passing rows + 3 non-file-backed stale rows (not "35 all real all pass").
2. The Critical Verification section accurately characterizes the 3 stale rows and states
   that no action is required.
3. The report includes a §DB Hash Bracket section with the `141AC9FD...` hash and the
   acknowledged absence of a pre-hash.
4. Headline table rows are annotated as investigation-era counts.
5. The four Codex-requested checks remain present with their methodology and results.

## Files Modified

- `independent-progress-assessments/spec-hygiene/S291-test-artifact-integrity-investigation.md`
  (three targeted edits + §DB Hash Bracket section added)

KB writes: **none.**

---

*© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
