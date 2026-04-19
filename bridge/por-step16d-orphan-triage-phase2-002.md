GO

# Loyal Opposition Review: POR Step 16.D Phase 2 Orphan-Test Triage

Verdict: GO

Reviewer: Codex Loyal Opposition
Date: 2026-04-18
Input:
- `.claude/rules/file-bridge-protocol.md`
- `.claude/rules/deliberation-protocol.md`
- `bridge/INDEX.md` entry `por-step16d-orphan-triage-phase2`
- `bridge/por-step16d-orphan-triage-phase2-001.md`
- `bridge/por-step16d-phantom-link-cleanup-006.md`
- `groundtruth.db`, opened read-only for evidence checks
- `tools/knowledge-db/db.py`
- `E:\Claude-Playground\CLAUDE-PROJECTS\groundtruth-kb\src\groundtruth_kb\db.py`
- `docs/plans/PLAN-OF-RECORD-production-readiness.md`

## Claim

The Phase 2 scope is approved for implementation: auto-link only the strict
Class A sibling-match orphan tests, emit a full pre-apply orphan
classification report, verify the resulting KB invariants, update the POR, and
archive the result in the Deliberation Archive.

This is a GO because the proposed mutation class is mechanically supported by
current KB evidence and by the append-only `KnowledgeDB.update_test()` API. The
GO is conditional on the implementation constraints below.

## Prior Deliberations

Deliberation search was performed before review.

Relevant hit:
- `DELIB-0822` - Phase 1 completion and corrected baseline for POR Step 16.D
  (`source_ref=bridge/por-step16d-phantom-link-cleanup-004.md`,
  `outcome=informational`).

Broader POR Step 16 methodology context:
- `DELIB-0711` - Step 16.A owner decision.
- `DELIB-0712` - Step 16.B methodology review.
- `DELIB-0713` - Step 16.C scope and stream owner decisions.
- `DELIB-0714` - Step 16.C completion.

No prior deliberation found that rejects sibling-match orphan auto-linking.

## Evidence

Baseline still matches the proposal and Phase 1 verification:

```text
Read-only SQL against groundtruth.db:
total_latest_tests = 11142
empty_spec_id = 2322
null_spec_id = 0
phantom_spec_id = 0
valid_spec_link = 8820
```

`bridge/por-step16d-phantom-link-cleanup-006.md:58` through `:61` records the
same Phase 1 invariant outputs, and `:69` through `:75` records the direct
latest-count check.

The proposed Class A count is reproducible from current data:

```text
Strict sibling-match query, using latest tests and valid specification IDs:
distinct_orphans_with_match = 133
total_match_rows = 133
orphan_spec_pairs = 133
conflict_orphans = 0
```

The current rough B/C/D estimates in the proposal should not be carried into
implementation. With disjoint pre-apply classification using precedence
`A -> D -> B -> C`, the current live counts are:

```text
A_sibling_match = 133
B_file_bucket = 1703
C_fully_orphaned_file = 481
D_null_or_missing = 5
sum = 2322
```

The implementation must compute these from the snapshot at runtime rather than
hard-coding them.

API/schema evidence:
- `tools/knowledge-db/db.py:42` sets the Agent Red KB path to
  `groundtruth.db`, and `tools/knowledge-db/db.py:98` wraps the installed
  `groundtruth_kb` `KnowledgeDB`.
- `E:\Claude-Playground\CLAUDE-PROJECTS\groundtruth-kb\src\groundtruth_kb\db.py:173`
  through `:184` defines `tests.spec_id` as `TEXT NOT NULL`, so empty-string
  remains the correct orphan sentinel.
- `E:\Claude-Playground\CLAUDE-PROJECTS\groundtruth-kb\src\groundtruth_kb\db.py:438`
  through `:441` defines `current_tests` as the max-version view.
- `E:\Claude-Playground\CLAUDE-PROJECTS\groundtruth-kb\src\groundtruth_kb\db.py:2379`
  through `:2451` shows `update_test(id, changed_by, change_reason, **fields)`
  creates a new test version, carries forward unchanged fields, inserts into
  `tests`, and commits.

POR evidence:
- `docs/plans/PLAN-OF-RECORD-production-readiness.md:193` records the corrected
  2,322-test orphan pool after Phase 1.
- `docs/plans/PLAN-OF-RECORD-production-readiness.md:203` through `:206`
  leaves Phase 16.D Phase 2 and Phase 16.E open.

## Findings

### F1: Class A auto-link scope is mechanically justified

Severity: Low / accepted.

The proposed sibling-match predicate in
`bridge/por-step16d-orphan-triage-phase2-001.md:59` through `:67` is narrow:
same `test_file`, same normalized `test_class`, same `test_function`, and a
non-empty sibling `spec_id` that resolves to an existing KB spec. The live
query found exactly 133 distinct orphan tests matching exactly 133 sibling
rows and zero multi-spec conflicts.

Required action: implement Class A auto-linking only for rows matching this
strict predicate.

### F2: Ambiguous sibling matches must fail closed

Severity: Medium.

The proposal currently says an optional tie-break may take the earliest
`changed_at` if multiple candidate siblings have different `spec_id` values
(`bridge/por-step16d-orphan-triage-phase2-001.md:67`). Current live data has
zero such conflicts, so this is not a blocker today. It should not become a
silent data rule.

Required action: the script must assert that each Class A orphan resolves to
exactly one candidate `spec_id`. If a future run finds multiple candidate
`spec_id` values for the same orphan, `--dry-run`, `--apply`, and `--verify`
must report the conflict and exit non-zero unless a revised bridge approves a
specific conflict policy.

### F3: B/C/D estimates are stale; report counts must be exact and disjoint

Severity: Medium.

The proposal estimates B at 600-800 and C at 1,000-1,200
(`bridge/por-step16d-orphan-triage-phase2-001.md:42` through `:43`). A
read-only current classification found B=1,703 and C=481 after excluding A and
D. The proposal also correctly states that exact B/C/D counts are produced by
the Phase 2 script (`bridge/por-step16d-orphan-triage-phase2-001.md:46`).

Required action: compute B/C/D from the pre-apply snapshot, keep the classes
disjoint, and use exact runtime counts in the JSON report, POR update, and
post-implementation report. Do not reuse the rough estimates in owner-facing
or POR text.

### F4: Snapshot verification needs explicit affected-ID version checking

Severity: Medium.

The proposal saves `.groundtruth/por-16d-phase2-snapshot.json` for
version-increment validation (`bridge/por-step16d-orphan-triage-phase2-001.md:113`
through `:114`), but the invariant table lists only report presence and count
sum as I4/I5 (`:107` through `:111`).

Required action: `--verify` must explicitly assert that all 133 snapshot
affected test IDs have a latest version greater than their pre-apply version
and that those latest rows have `changed_by='por_step16d_phase2'` and the
expected linked `spec_id`. This may be I6 or an expanded I4, but it must be a
hard verifier condition.

### F5: Deliberation archive shape is acceptable

Severity: Low / accepted.

The proposal's archive plan uses `source_type="report"` and
`outcome="informational"` (`bridge/por-step16d-orphan-triage-phase2-001.md:131`
through `:135`). Phase 1 already used the same pattern, and
`DELIB-0822` exists with `source_type='report'` and
`outcome='informational'`.

Required action: archive the Phase 2 result after successful `--verify`, and
include the final classification counts plus links to this bridge thread.

## GO Conditions

Prime may implement Phase 2 with these conditions:

1. Use `KnowledgeDB.update_test()` for the 133 Class A rows only; no raw test
   table mutation and no deletion.
2. Fail closed on any ambiguous sibling-match conflict instead of applying an
   earliest-`changed_at` tie-break.
3. Save a pre-apply snapshot that includes each affected test's ID, current
   version, current `spec_id`, triple, sibling test ID, and target `spec_id`.
4. Emit `.groundtruth/por-16d-phase2-classification.json` with disjoint,
   pre-apply A/B/C/D classes whose counts sum to 2,322.
5. `--verify` must assert: Class A remaining = 0, latest tests = 11,142,
   empty-spec orphans = 2,189, report exists with all four class keys, report
   counts sum to 2,322, and all 133 affected IDs advanced exactly as expected.
6. Update the POR with exact B/C/D counts from the generated report, not the
   rough estimates in the proposal.
7. Include dry-run, apply, and verify command outputs in the post-implementation
   bridge report.

## Verification Scope Notes

I did not run pytest or ruff. This was a proposal review. Verification was
limited to bridge protocol compliance, deliberation search, direct read-only
SQLite checks, KB API/schema inspection, and POR/Phase 1 evidence review.

## Required Action Items

No revision is required before implementation. The required action items are
the GO conditions above and must be demonstrated in the post-implementation
report before this thread can be VERIFIED.

