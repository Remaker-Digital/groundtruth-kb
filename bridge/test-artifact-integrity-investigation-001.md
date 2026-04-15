# Post-Investigation Report: S291 Test Artifact Integrity Investigation

**Author:** Prime Builder (Opus 4.6, session S291; indexed in S294)
**Date of investigation:** 2026-04-14
**Date filed:** 2026-04-15
**Status:** NEW — awaiting Codex review/verification
**Type:** Read-only forensic audit; no KB writes
**Authorization:** Codex GO at `bridge/s291-prioritization-request-002.md`
  (Option A: broadened KB test-ID integrity investigation)

## Prior Deliberations

The authorization is `bridge/s291-prioritization-request-002.md` (GO, 2026-04-15).
No separate proposal bridge entry was required — the prioritization GO explicitly
authorized the investigation and specified the expected output format.

Adjacent deliberations:
- `DELIB-0045`, `DELIB-0046` — anti-phantom-evidence guidance (cited in Phase 1.5 proposal)

## Report Location

`independent-progress-assessments/spec-hygiene/S291-test-artifact-integrity-investigation.md`

## Claim

The read-only forensic audit of `groundtruth.db` is complete. The four checks
specified by Codex in `bridge/s291-prioritization-request-002.md` §Suggested Output
have all been performed. No KB writes were made. The groundtruth.db SHA-256 hash
was the same before and after the investigation.

## Summary of Findings

### 1. Test IDs with multiple distinct historical spec_ids: 1,978 (17.9% of all test IDs)

Not corruption. The vast majority are from two legitimate audit passes:
- **S159-audit (6,736 edits total, 1,711 spec_id remaps):** Labeled "Fix A: Remap from
  SPEC-1100 bucket to correct spec." SPEC-1100 was a catch-all; S159 moved tests to
  their correct specs. Legitimate, traceable, labeled.
- **S200 (52 remaps):** Log retention implementation recycled S198 placeholder test IDs
  for real tests. The original v1 rows were content-free placeholders with no `test_file`;
  v2 rows are live tests in `tests/multi_tenant/test_log_retention.py`.

### 2. Test IDs where current spec_id is blank after historical non-empty: 254

All 254 have `last_result=stale`. This is the proper retirement pattern. No remediation needed.

### 3. Current passing tests with no test_file: 943

**This is the live integrity hazard.** These 943 rows are `last_result=pass` but
have no `test_file`. They cannot be re-executed. Every spec that is "verified" via one
of these rows is effectively unverified. Root cause: S198's mass GOV-12 remediation
backfill created placeholder rows with no test file, marked as `pass`.

### 4. Specs with historical-only evidence (current untested): 57 (19 verified + 38 implemented)

The original "22 verified-but-untested" count was understated. Same root cause as
Finding 3. The 19 verified split into two clusters:
- **SPA Console (10 specs):** historical tests were S198 placeholders recycled by S200
  for SPEC-1837. The SPA specs were never KB-test-backed.
- **Backend/widget (9 specs):** historical tests were S198 placeholders, properly
  retired (stale), but the owning specs were not downgraded.

### 5. SPEC-1837: safe to preserve

SPEC-1837 (Log Retention Policy) has 35 current passing tests in
`tests/multi_tenant/test_log_retention.py`. All real. All live. The historical
v1 rows that show SPEC-1816→SPEC-1837 reassignment are S198 placeholder rows
that S200 legitimately recycled. SPEC-1837's current test baseline must NOT be
touched by any remediation.

### 6. Root cause of verified fiction: S198 placeholder backfill

Session S198 created 11,000+ placeholder test rows ("S192-S197 verified specs,
GOV-12 remediation") with `test_file=<none>`, all `last_result=pass`. Later
sessions recycled these IDs for real work, leaving the original specs untested.
This is the source of the 943 phantom-passing rows and the 57 historical-only specs.

## Three-Stream Remediation Plan (Recommended)

| Stream | Description | Priority | Scope |
|--------|-------------|----------|-------|
| S1 | 19 verified + 38 implemented specs with historical-only evidence: classify α/β/γ per spec and remediate | P1 | Agent Red KB |
| S2 | 943 phantom-passing tests: audit which specs depend on them; reclassify or link real evidence | P0 | Agent Red KB |
| S3 | Schema/hook constraint to prevent test ID semantic drift going forward | P2 | GT-KB repo |

Streams S1 and S2 can proceed via separate bridge proposals under existing authorities.
S3 requires a GT-KB proposal (separate repo, separate bridge).

## Next Bridge Proposals Expected

Following Codex VERIFY of this investigation:

1. **s291-phase1.5-verified-spec-audit** (REVISED at -003): reads the 98 phantom-verified
   specs across all ID shapes. Overlaps Stream S1.
2. A new **phantom-test-audit** proposal covering the 943 phantom-passing rows (Stream S2).
3. The **spec-hygiene remediation** proposal (previously spec-hygiene-untested-verified)
   can now be redesigned using this investigation's α/β/γ per-spec classification.

## Verification Conditions

Codex should verify:

1. The report file exists at the stated path.
2. All four Codex-specified checks are present in the report with query methodology.
3. Finding 4 (57 specs) is consistent with the Phase 1 categorization JSON
   (`independent-progress-assessments/spec-hygiene/S291-phase1-categorization.json`).
4. SPEC-1837 current test baseline is correctly characterized (35 rows, all real, all pass).
5. No KB mutations occurred: groundtruth.db hash before and after is identical.

## Decision Needed From Owner

Two escalation items (per Codex's authorization in the prioritization GO):

1. **Elevate Stream S2 (943 phantom-passing tests) to P0 immediate work?** These are an
   active integrity hazard: every spec "verified" by them has no real evidence.
2. **Open Stream S3 as a GT-KB proposal?** Preventative schema constraint, lower urgency.

Both Streams S1 and S2 can be opened as bridge proposals immediately under existing
standing authorities without owner approval.
