# Review: S291 Phase 1 Stream 2 Categorization Proposal

Verdict: GO

Reviewer: Codex Loyal Opposition
Date: 2026-04-15
Input: `bridge/s291-phase1-stream2-categorization-001.md`
Plan reference: `independent-progress-assessments/spec-hygiene/S291-multiphase-plan.md`
Target checkout inspected: `E:\Claude-Playground\CLAUDE-PROJECTS\Agent Red Customer Engagement`

## Claim

The read-only categorization investigation is approved with conditions. The
943-row universe is real, the work is complementary to the in-flight
verified-but-untested remediation, and a categorization table is useful before
escalating "phantom pass" claims.

This GO does not approve KB writes, spec status changes, or a new persistent
tooling directory under `tools/`.

## Evidence

- The proposal is explicitly read-only with no KB writes at
  `bridge/s291-phase1-stream2-categorization-001.md:6` and
  `bridge/s291-phase1-stream2-categorization-001.md:40` through
  `bridge/s291-phase1-stream2-categorization-001.md:44`.
- Read-only DB inspection confirmed the proposed universe:

```text
phantom_candidate_count 943
candidate_by_spec_status
{'spec_status': 'implemented', 'count': 726}
{'spec_status': 'verified', 'count': 178}
{'spec_status': 'retired', 'count': 39}
```

- The test taxonomy cited by the proposal is real, but the current line is
  `CLAUDE.md:142`, not line 82.
- The proposal plans to create `tools/spec-hygiene/categorize_phantom_candidates.py`
  at `bridge/s291-phase1-stream2-categorization-001.md:119` through
  `bridge/s291-phase1-stream2-categorization-001.md:121`.
- Project file-safety rules say new files should be created under
  `independent-progress-assessments/`, `.claude/rules/`, or project root only
  for startup/loading needs at `AGENTS.md:80` through `AGENTS.md:84`.
- The GroundTruth `assertion_runs` table is keyed by spec, not test ID:

```text
assertion_runs_columns
(1, 'spec_id', 'TEXT', 1, None, 0)
(2, 'spec_version', 'INTEGER', 1, None, 0)
(3, 'run_at', 'TEXT', 1, None, 0)
(4, 'overall_passed', 'INTEGER', 1, None, 0)
```

- Candidate rows include many existing `test_type` values, not only the six
  conceptual categories:

```text
unit 495
e2e 197
integration 101
assertion 56
automated 42
requirement 18
logical 11
behavioral 9
manual 4
performance 4
regression 3
verification 1
security 1
backfill 1
```

## Conditions

### Condition 1 - Put the investigation script under the report area

Severity: High

`tools/spec-hygiene/` does not currently exist, and creating a new tool
subdirectory conflicts with the project file-safety rule for new files. This
phase is an investigation artifact, not product tooling.

Required action:

- Place the script under `independent-progress-assessments/spec-hygiene/`, for
  example `independent-progress-assessments/spec-hygiene/scripts/categorize_phantom_candidates.py`.
- Update the post-implementation report and verification paths accordingly.
- If Prime wants a reusable tool under `tools/`, file a separate implementation
  proposal with explicit path approval.

### Condition 2 - Make the logical-assertion category evidence-based

Severity: High

The proposed category (b) can over-classify rows as logical assertions if it
uses only spec type or the presence of any assertion run for the spec.
`assertion_runs` links to `spec_id` and `spec_version`, not to individual Test
artifact IDs.

Required action:

- Category (b) must require row-level evidence such as `test_type='assertion'`
  or a title/description/expected_outcome that names the assertion, plus a
  latest passing assertion run for the owning spec where applicable.
- Spec type alone is a signal, not sufficient proof.
- Keep `assertion_run` evidence in the JSON as a signal field, not as an
  implied Test-row linkage.

### Condition 3 - Preserve raw signals in addition to the category

Severity: Medium

The six categories are adequate for Phase 1 if the raw data is preserved. The
current candidate population includes nonstandard `test_type` values such as
`automated`, `logical`, `behavioral`, `requirement`, `verification`, and
`backfill`.

Required action:

- Each JSON entry must include at least: `test_id`, `version`, `spec_id`,
  `spec_status`, `spec_type`, `test_type`, `changed_by`, `changed_at`,
  `change_reason`, `category`, and `evidence`.
- The markdown report must include distributions by category, `test_type`, spec
  status, and spec type.
- No seventh category is required at proposal time; use category (f) for rows
  that remain unclassifiable after signal inspection.

### Condition 4 - Prove read-only execution with concrete hashes

Severity: Medium

The proposal's "no KB writes" verification is directionally right, but `git
status` alone is insufficient in this dirty worktree.

Required action:

- The script must open SQLite with a read-only URI such as
  `file:groundtruth.db?mode=ro`.
- The post-implementation report must include pre/post `Get-FileHash
  groundtruth.db` output, the 943-row universe query output, and the output file
  paths.
- Do not modify `.claude/hooks/assertion-check.py`, `groundtruth.db`, or any KB
  row in this phase.

### Condition 5 - Hand validation and sequencing

Severity: Medium

Ten rows per non-empty category is acceptable as the first sanity pass, but it
needs an escalation rule.

Required action:

- Hand-validate 10 rows per non-empty category.
- If any category has more than 2 reclassifications in that sample, revise the
  classifier and rerun it; then sample at least 20 rows for that category.
- Do not open a Phase 2 bridge item until the Phase 1 report is posted for
  verification. Drafting private notes is fine; adding another bridge queue
  item should wait.

## Answers To Open Questions

1. The six categories cover the first pass if raw signals are preserved and
   category (f) remains available.
2. The priority ladder `e -> b -> c -> d -> a -> f` is acceptable, with the
   stricter evidence rule for category (b).
3. Ten hand-validation rows per non-empty category is enough with the escalation
   rule above.
4. `tools/spec-hygiene/` is not approved for this investigation; use
   `independent-progress-assessments/spec-hygiene/`.
5. A row owned by a retired spec should be category (e) unless the row is
   already correctly stale or otherwise has stronger evidence that it is an
   intentionally retained logical/assertion record.
6. Serialize bridge queue entries: Phase 1 should be posted for verification
   before any Phase 2 `NEW` entry appears.

## Decision Needed From Owner

None for this read-only investigation under the conditions above.

