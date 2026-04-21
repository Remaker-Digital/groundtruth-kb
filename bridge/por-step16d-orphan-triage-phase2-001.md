NEW

# POR Step 16.D Phase 2 — Orphan-Test Triage: Sibling-Match Auto-Link + Classification Report

**Status:** NEW
**Author:** Prime Builder (Opus 4.7, in-session S302)
**Date:** 2026-04-18
**Backlog Slot:** F2 Phase 2 (follow-on from Phase 1 VERIFIED at `bridge/por-step16d-phantom-link-cleanup-006.md`)
**Prior POR reference:** `docs/plans/PLAN-OF-RECORD-production-readiness.md:203-204` (updated in Phase 1)

## Why this is Phase 2 (not mega-scope)

Phase 1 cleaned phantom links. This Phase 2 addresses the subset of orphans
that are mechanically auto-linkable AND produces the classification report
that drives all subsequent work. The remaining ~2,184 orphans require
judgment-based decisions (retire vs re-spec vs new-spec) that are not
mechanically tractable from a single scan — they need a classification
report to scope properly.

Per `memory/feedback_no_deferrals_ever.md`: this is dependency ordering,
not deferral. The report IS deliverable scope — without it, Phase 3 scope
cannot be defined concretely, and we would be forcing subjective-chunk
breakdowns that the rule forbids.

## Observed Baseline (post-Phase-1)

```sql
-- Live KB query (2026-04-18, post-commit 8dcdd4ae):
total_latest_tests          = 11,142
empty_spec_id_orphans       = 2,322  ← Phase 2 target pool
phantom_spec_id             = 0      (Phase 1 closed)
valid_spec_link             = 8,820
```

## Structural Classification (from live exploration)

Orphan structural breakdown:

| Class | Count | Mechanical Handling |
|---|---|---|
| **A. Sibling-match** — orphan triple (file, class, func) has a non-orphan sibling with a valid spec link | **133** | **Auto-apply** in Phase 2 (copy spec_id from sibling). Low risk. |
| **B. File-bucket** — test_file has OTHER tests that link to a spec (e.g., half of a test class is linked) | ~estimated 600-800 | Report only; Phase 3 or later |
| **C. Fully-orphaned file** — test_file exists but ALL tests in that file are orphans | ~estimated 1,000-1,200 | Report only; needs new-spec vs retire decision |
| **D. NULL/stale file** — test_file is NULL OR file does not exist on disk | 5 + unknown | Report only; likely retire |

Exact B/C/D counts produced by the Phase 2 classification script (part of
the deliverable).

## Proposed Scope

### §1 — Sibling-Match Auto-Link (133 orphans)

Build `tools/knowledge-db/triage_orphan_tests_phase2.py` with 3 modes:

- `--dry-run`: Report sibling-match candidates; no mutation.
- `--apply`: For each of the 133 sibling-match orphans, `KnowledgeDB.update_test(test_id, spec_id=<sibling_spec_id>, changed_by="por_step16d_phase2", change_reason="Auto-linked via sibling-match — same (test_file, test_class, test_function) triple as TEST-YYYY which links to SPEC-ZZZZ")`.
- `--verify`: Assert post-apply invariants (see §3).

**Sibling-match definition (strict):**

An orphan `O` has a sibling-match if there exists another latest-version
test `S` such that:
- `S.test_file == O.test_file` (non-empty on both)
- `COALESCE(S.test_class, '') == COALESCE(O.test_class, '')`
- `S.test_function == O.test_function`
- `S.spec_id` is non-empty AND resolves to an existing spec in `specifications`
- (Optional tie-break: if multiple candidate siblings exist with different spec_ids, take the one with earliest `changed_at`.)

Rationale: the orphan and sibling point to the **same physical test in the same file** — the spec link is definitively transferable. The 133 count is from the live query already done.

### §2 — Classification Report (all 2,322 orphans)

Same script emits `.groundtruth/por-16d-phase2-classification.json`:

```json
{
  "phase": "POR-16D-Phase-2",
  "as_of": "2026-04-18T...",
  "counts": {"A_sibling_match": 133, "B_file_bucket": N, "C_fully_orphaned_file": N, "D_null_or_missing": N},
  "A_sibling_match": [
    {"test_id": "TEST-XXXX", "sibling_test_id": "TEST-YYYY", "linked_spec_id": "SPEC-ZZZZ"},
    ...
  ],
  "B_file_bucket": [
    {"test_id": "TEST-XXXX", "test_file": "tests/...", "test_class": "...", "test_function": "...", "candidate_specs_in_same_file": ["SPEC-AAAA", "SPEC-BBBB"]},
    ...
  ],
  "C_fully_orphaned_file": [
    {"test_file": "tests/...", "orphan_count": N, "sample_test_ids": [...]}
    ...  (grouped by file)
  ],
  "D_null_or_missing": [
    {"test_id": "TEST-XXXX", "test_file": null | "missing_path/..."},
    ...
  ]
}
```

The report is the Phase 2 **deliverable** — Phase 3 scope cannot be defined without it.

### §3 — Verification Invariants

`--verify` mode asserts:

| Invariant | Check | Expected |
|---|---|---|
| I1 | Class-A orphans count (post-apply) | 0 |
| I2 | Total latest-version test count | 11,142 (unchanged) |
| I3 | Empty-spec orphan count (post-apply) | 2,189 = 2,322 - 133 |
| I4 | Report file exists + has all 4 class keys | PASS |
| I5 | Sum of class counts in report = 2,322 (pre-apply) | PASS |

Pre-apply snapshot saved to `.groundtruth/por-16d-phase2-snapshot.json` for
I4-style version-increment validation of the 133 affected IDs.

### §4 — POR §Step 16.D Update

Update `docs/plans/PLAN-OF-RECORD-production-readiness.md:203-204` with
post-Phase-2 breakdown:

- Phase 2 complete: 133 orphans auto-linked via sibling-match; 2,189 remain
  (B: ~N, C: ~N, D: ~N).
- Phase 3 scope (tentative): tackle class B (file-bucket linkage) with
  Codex-reviewed heuristic thresholds.
- Phase 4 scope (tentative): tackle class C (fully-orphaned files) with
  per-file spec-write or bulk-retire decisions.
- Phase 5 scope (tentative): tackle class D (stale file references).

Phase N counts determined by the classification report.

### §5 — Archive DELIB-xxxx

`source_type="report"`, `outcome="informational"`, `source_ref="bridge/por-step16d-orphan-triage-phase2-*.md"`.

Content: Phase 2 results (133 auto-linked, classification B/C/D counts,
forward links to Phase 3+).

## Files Touched

| File | Change kind | Est. delta |
|---|---|---|
| `tools/knowledge-db/triage_orphan_tests_phase2.py` (new) | 3-mode script | +~280 lines |
| `.groundtruth/por-16d-phase2-snapshot.json` (new) | Pre-apply snapshot for I4/I5 | +~35 KB |
| `.groundtruth/por-16d-phase2-classification.json` (new) | Classification report (Phase 2 deliverable) | +~800 KB |
| `docs/plans/PLAN-OF-RECORD-production-readiness.md` | Phase 2 status update | +~15 / -~5 lines |
| `groundtruth.db` | 133 test row versions + 1 DELIB row | (binary) |

**Total: 3 new tracked files + POR edit + KB mutation.**

## Non-Scope (Phase 2 exclusions)

- **Class B file-bucket linkage** — strategy requires Codex review of the classification report; Phase 3.
- **Class C fully-orphaned files** — needs per-file judgment (retire vs new-spec); Phase 4.
- **Class D stale references** — needs inspection of whether on-disk file exists; Phase 5.
- **POR §16.E exit verification** — runs after all orphan classes triaged.
- **Creating new specs** — out of scope; would require GOV-06 "specify on contact" framing.
- **Test file modifications on disk** — no `.py` files edited.

## Verification Plan

```text
$ python tools/knowledge-db/triage_orphan_tests_phase2.py --dry-run
# Expect: "Class A sibling-match candidates: 133. Total orphans to classify: 2,322."

$ python tools/knowledge-db/triage_orphan_tests_phase2.py --apply
# Expect: "Auto-linked 133 class-A orphans. Post-apply orphans: 2189."
# Creates .groundtruth/por-16d-phase2-snapshot.json and -classification.json.

$ python tools/knowledge-db/triage_orphan_tests_phase2.py --verify
# Expect all 5 invariants PASS.
```

No pytest or lint implications — KB data operation + report generation.

## Implementation Sequence

1. Create `tools/knowledge-db/triage_orphan_tests_phase2.py`.
2. Run `--dry-run`; capture output.
3. Run `--apply`; captures sibling-links + writes snapshot + classification report.
4. Run `--verify`; all 5 invariants PASS.
5. Update POR §Step 16.D text.
6. Archive DELIB-xxxx.
7. Commit on `develop`: `feat(por): Step 16.D Phase 2 — orphan-test sibling-match auto-link + classification report`.
8. File post-impl report.
9. On VERIFIED: push to `origin/develop` + file Phase 3 proposal based on classification-report findings.

## Prior Deliberations

- **DELIB-0822** (Phase 1 closure) — baseline correction + phantom cleanup summary. Phase 2 continues this thread.
- 16.A/16.B/16.C DELIBs (0711-0714) — methodology precedent for multi-stream spec hygiene.

## Owner Decisions Required

None. Defaults pinned:

- **Auto-apply scope = Class A sibling-match only** (lowest risk class with definitive transfer signal). Other classes need judgment beyond mechanical sibling matching.
- **Retain the 73 duplicate TEST rows** (TEST-3247 vs TEST-7589 pattern). Class A auto-link will leave both rows in place; the duplicate TEST ID issue is a separate hygiene concern, not Phase 2 scope.
- **Report location = `.groundtruth/por-16d-phase2-classification.json`** (commit as audit evidence, like Phase 1 snapshot).

## Requested Verdict

**GO** to implement §1 + §2 + §3 + §4 + §5, or **NO-GO** with specific findings.

---

*© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
