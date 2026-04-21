# NO-GO: Phase 2 F3 + F2-A + F4-A Post-Implementation Verification

**Reviewed report:** bridge/gtkb-phase2-implementation-007.md
**GO reference:** bridge/gtkb-phase2-implementation-006.md
**Full entry read:** bridge/gtkb-phase2-implementation-001.md through bridge/gtkb-phase2-implementation-007.md
**Referenced approvals checked:** bridge/gtkb-spec-pipeline-f2-003.md, bridge/gtkb-spec-pipeline-f2-009.md, bridge/gtkb-spec-pipeline-f2-011.md, bridge/gtkb-spec-pipeline-f2-012.md, bridge/gtkb-spec-pipeline-f3-005.md, bridge/gtkb-spec-pipeline-f3-006.md, bridge/gtkb-spec-pipeline-f4-003.md, bridge/gtkb-spec-pipeline-f4-004.md, bridge/gtkb-f1f8-cross-check-001.md, bridge/gtkb-f1f8-cross-check-002.md
**Target repo inspected:** E:/Claude-Playground/CLAUDE-PROJECTS/groundtruth-kb
**Verdict:** NO-GO

## Rationale

The reported commits are present and the advertised broad verification commands
pass. However, targeted checks found implementation behavior that does not
preserve approved Phase 2/F2/F3 contracts.

The blockers are not formatting or incidental test gaps. F2-A currently narrows
related-spec discovery and report shape below the approved API, skips conflicts
that the approved exact-string glob semantics say should be detected, and F3 can
double-count one spec in quality distribution when multiple session scores share
the same second-level timestamp.

## Findings

### 1. Blocking: F2-A related-spec discovery and report shape are narrower than the approved contract

**Claim:** Phase A impact analysis must use the approved existing-field overlap
contract and expose the approved report shape.

**Evidence:**
- The approved F2 Phase A design says it uses current fields `section`, `scope`,
  `tags`, `type`, and `assertions` at bridge/gtkb-spec-pipeline-f2-003.md:25.
- The same design defines overlap detection as specs sharing `section` or
  `scope` at bridge/gtkb-spec-pipeline-f2-003.md:27.
- The Phase 2 implementation proposal says F2-A uses `section/scope/tags`
  overlap for related specs at bridge/gtkb-phase2-implementation-001.md:132-133.
- The approved API/report shape includes `ImpactReport.related_specs`,
  `ImpactReport.dependents`, and `ImpactReport.recommendation` at
  bridge/gtkb-spec-pipeline-f2-003.md:51-58 and
  bridge/gtkb-phase2-implementation-001.md:116-123.
- Current `compute_impact_analysis()` only collects related specs with exact
  matching section at
  E:/Claude-Playground/CLAUDE-PROJECTS/groundtruth-kb/src/groundtruth_kb/impact.py:162-168.
- Current `compute_impact_analysis()` returns `related_spec_count` and omits
  `related_specs`, `dependents`, and `recommendation` at
  E:/Claude-Playground/CLAUDE-PROJECTS/groundtruth-kb/src/groundtruth_kb/impact.py:184-192.
- Current `KnowledgeDB.compute_impact()` takes only `spec_id`, not the approved
  `operation, spec_data` shape, at
  E:/Claude-Playground/CLAUDE-PROJECTS/groundtruth-kb/src/groundtruth_kb/db.py:1322-1327.
- Targeted verification in a temp DB inserted two specs with the same
  `scope='shared-scope'` but different sections. `db.compute_impact('SPEC-A')`
  returned `related_spec_count: 0`.

**Risk/impact:** F5 and owner-facing advisory flows can understate blast radius
for scope/tag-related changes and cannot consume the approved report fields
without writing around the implementation. This weakens the core GroundTruth KB
vision filter: the owner should get impact evidence before deciding, not a
section-only approximation.

**Required action:** Restore the approved F2-A contract or submit a revised F2
bridge proposal that explicitly narrows it. At minimum, implement section-or-scope
overlap, resolve whether Phase 2's tag overlap remains required, and return the
approved report fields (`related_specs`, `dependents` as an empty Phase A list,
and `recommendation`). Add regression tests for scope-only overlap, tag-only
overlap if retained, and public report shape.

### 2. Blocking: F2-A skips same-glob conflicts despite approved exact-string semantics

**Claim:** Phase A accepts literal-vs-glob as a documented false negative, but
same-string glob targets should still be compared by exact string.

**Evidence:**
- F2 v5 says conflict detection uses exact string equality and the documented
  false-negative class is file-glob overlap such as literal vs glob, at
  bridge/gtkb-spec-pipeline-f2-009.md:12.
- F2 v5 explicitly says `src/**/*.py` vs `src/**/*.py` should be flagged when
  the pattern overlaps because it is an exact match, at
  bridge/gtkb-spec-pipeline-f2-009.md:91.
- F2 v6 preserves the exact-string conflict comparison unchanged at
  bridge/gtkb-spec-pipeline-f2-011.md:17.
- Current conflict detection skips before exact-string comparison whenever
  either side has `file_is_glob=True` at
  E:/Claude-Playground/CLAUDE-PROJECTS/groundtruth-kb/src/groundtruth_kb/impact.py:83-96.
- Targeted verification inserted two specs in the same section with
  `grep` vs `grep_absent`, both targeting `file='src/**/*.py'` and
  `pattern='import os'`. `db.compute_impact('SPEC-A')` returned
  `potential_conflicts: []` and only an annotation saying the same glob could
  not be compared.

**Risk/impact:** This loses reliable conflicts that do not require filesystem
expansion. The approved tradeoff was to skip ambiguous literal-vs-glob overlap,
not to skip exact same-glob contradictions.

**Required action:** Compare exact-equal file targets before applying the
file-glob limitation path, or otherwise preserve exact-string conflict behavior
for same-string globs. Add a regression test for same-glob `grep` vs
`grep_absent` with the same pattern.

### 3. Blocking: F3 quality distribution can double-count one spec as multiple latest scores

**Claim:** `get_quality_distribution()` must aggregate latest scores per spec,
not latest rows per matching second.

**Evidence:**
- F3 includes quality distribution aggregation in the approved test/API scope at
  bridge/gtkb-phase2-implementation-005.md:70-72.
- The cross-check lists `get_quality_distribution()` as an F7 snapshot producer
  at bridge/gtkb-f1f8-cross-check-001.md:27.
- Current `get_quality_distribution()` documents "latest scores per spec" at
  E:/Claude-Playground/CLAUDE-PROJECTS/groundtruth-kb/src/groundtruth_kb/db.py:1226-1227.
- Current `_now()` uses second-level precision at
  E:/Claude-Playground/CLAUDE-PROJECTS/groundtruth-kb/src/groundtruth_kb/db.py:463-464.
- Current distribution query joins each spec to `MAX(scored_at)` at
  E:/Claude-Playground/CLAUDE-PROJECTS/groundtruth-kb/src/groundtruth_kb/db.py:1231-1236.
- Targeted verification scored one spec twice in immediate sessions `S1` and
  `S2`. Both rows had the same `scored_at` value and
  `db.get_quality_distribution()` returned `{'bronze': {'count': 2, ...},
  'total': 2}` for one spec.

**Risk/impact:** F7 health snapshots and any owner-facing quality summary can
inflate counts when scores are persisted more than once within a second. The
current test suite permits this because the history-ordering test only asserts
`>=` on tied timestamps.

**Required action:** Make latest-score selection deterministic per spec under
timestamp ties. Acceptable fixes include higher-precision timestamps, an
explicit tie-breaker such as `(scored_at, session_id)` or rowid, or a query that
selects one row per spec by a deterministic ordering. Add a regression test
that persists two sessions for one spec in the same second and expects
distribution `total == 1`.

## Verified Passing Checks

- `git log --oneline -5` in the target checkout shows `35514fe` and `a21fa19`
  as the two latest commits.
- `git status --short` in the target checkout returned only `?? _site_verify/`.
- `python -m pytest -q` passed: `487 passed, 1 warning`.
- `python -m ruff check .` passed: `All checks passed!`.
- `python -m ruff format --check .` passed: `55 files already formatted`.
- `python scripts/check_docs_cli_coverage.py` passed: `All documentation checks passed.`
- F3 schema/export/import integration points exist:
  `spec_quality_scores` schema at
  E:/Claude-Playground/CLAUDE-PROJECTS/groundtruth-kb/src/groundtruth_kb/db.py:289,
  export table entry at
  E:/Claude-Playground/CLAUDE-PROJECTS/groundtruth-kb/src/groundtruth_kb/db.py:3102,
  and import allowlist/flags validation at
  E:/Claude-Playground/CLAUDE-PROJECTS/groundtruth-kb/src/groundtruth_kb/cli.py:317-335
  and
  E:/Claude-Playground/CLAUDE-PROJECTS/groundtruth-kb/src/groundtruth_kb/cli.py:414-429.
- F4-A has the six restored tests at
  E:/Claude-Playground/CLAUDE-PROJECTS/groundtruth-kb/tests/test_constraint_propagation.py:18,
  :41, :64, :97, :122, and :139.

## Conditions For VERIFIED

1. Fix F2-A related-spec discovery and public report shape, or route the
   narrowed contract through a revised bridge proposal before asking for
   verification.
2. Fix same-string glob conflict detection while retaining the approved
   literal-vs-glob documented false-negative behavior.
3. Fix deterministic latest-score selection in `get_quality_distribution()`.
4. Add targeted regression tests for the three blocker cases above.
5. Re-run `python -m pytest -q`, `python -m ruff check .`,
   `python -m ruff format --check .`, and
   `python scripts/check_docs_cli_coverage.py`.

## Decision Needed

No owner decision is needed if Prime fixes the implementation to match the
approved contracts. Owner/Prime decision is needed only if Prime wants to narrow
the F2-A API/report contract instead of implementing the approved shape.
