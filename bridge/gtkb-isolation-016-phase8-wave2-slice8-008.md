NO-GO

# Loyal Opposition Verification - GTKB-ISOLATION-016 Phase 8 Wave 2 Slice 8 Post-Implementation

Reviewed: 2026-04-27
Subject: `bridge/gtkb-isolation-016-phase8-wave2-slice8-007.md`
Scope: post-implementation verification for `scripts/rehearse/_membase_export.py`
Verdict: NO-GO

## Prior Deliberations

- `DELIB-1106` covers the Wave 2 implementation umbrella and remains relevant context for Stage B lane behavior.
- No harvested deliberation was found for the exact `gtkb-isolation-016-phase8-wave2-slice8` bridge thread yet; the live bridge thread `bridge/gtkb-isolation-016-phase8-wave2-slice8-001.md` through `-007.md` is the operative review record.

## Claim

NO-GO. The implementation fixes the prior live-schema/table-shape blockers from `-004` and satisfies the `-006` constraints around unknown tables, telemetry exclusions, relationship rows, and per-session ownership. However, it does not implement the approved type-specific classification overrides that remained part of the Slice 8 design, especially test-path classification.

## Verification Performed

- `python -m pytest tests/scripts/test_rehearse_membase_export.py -q --tb=short --timeout=60`
  - Result: `24 passed in 2.44s`.
- `python -m pytest tests/scripts/test_rehearse_isolation.py -q --tb=short --timeout=60`
  - Result: `66 passed in 0.53s`.
- `python -m ruff check scripts/rehearse/_membase_export.py tests/scripts/test_rehearse_membase_export.py`
  - Result: `All checks passed!`.
- `python -m ruff format --check scripts/rehearse/_membase_export.py tests/scripts/test_rehearse_membase_export.py`
  - Result: `2 files already formatted`.
- `python scripts/rehearse_isolation.py --phase membase --execute --output-dir C:\temp\agent-red-rehearsal-slice8-codex-verify`
  - Result: `membase ... ok`.
- `python -m pytest @tmp/rehearse-test-files.txt -q --tb=line --timeout=120`
  - Result: `265 passed, 1 failed`.
  - Failure is in `tests/scripts/test_rehearse_lint_clean.py::test_rehearse_package_passes_ruff_format_check` because unrelated WIP `scripts/rehearse/_chromadb_regen.py` would be reformatted. This is not the Slice 8 blocker, but it means the whole rehearsal package is not currently green.

Live manifest count checks matched the database:

- versioned rows: manifest `40034`, live DB `40034`;
- unique versioned artifacts: manifest `17352`, live DB `17352`;
- relationship rows: manifest `445`, live DB `445`;
- per-session rows: manifest `138`, live DB `138`.

## Finding 1 - P1: Approved Type-Specific Classification Overrides Are Missing

### Claim

The implementation omits the type-specific classification layer that the approved proposal carried forward. It classifies versioned records only by ID prefix plus a small set of content-bearing columns, not by test path, procedure kind, or document topic as specified.

### Evidence

- The original Slice 8 proposal defines type-specific overrides:
  - tests: test path is the strongest signal;
  - `tests/groundtruth_kb/...` -> framework;
  - `tests/transport/...`, `tests/scripts/test_admin_*`, `tests/scripts/test_provider_*` -> adopter;
  - mixed tests such as `test_release_candidate_gate.py` -> `unclassified` with `mixed_scope_test`.
- The REVISED-1 and REVISED-2 proposals preserved the classification algorithm with "ID prefix + content scan + type-specific overrides."
- `scripts/rehearse/_membase_export.py` defines `_CONTENT_BEARING_COLUMNS` as only `title`, `description`, `content`, `subject`, `scope`, `rationale`, and `summary`.
- `_enumerate_versioned_table()` selects only `id`, `version`, and those content-bearing columns, then calls `_classify_artifact_id()` for every versioned table, including `tests`.
- The implementation never selects or scans `tests.test_file`, `tests.test_class`, or `tests.test_function`.
- `tests/scripts/test_rehearse_membase_export.py` has no tests for `test_file`, `tests/groundtruth_kb`, `tests/transport`, `test_release_candidate_gate.py`, or `mixed_scope_test`; the original proposal explicitly listed these as tests.
- Live DB has test-path data:
  - 454 distinct `tests.test_file` values.
  - Examples include `tests/agents`, `tests/chat`, `tests/multi_tenant`, `tests/integration`, `tests/security`, and other application test directories.
- Live manifest output classified test records as:
  - `unclassified`: 10,669
  - `adopter`: 473
  - `framework`: 0
- Sample live path-classifiable records:
  - `tests/agents/...` records such as `TEST-0001` through `TEST-0005` are `unclassified` with `no_classification_signal`.
  - `tests/integration/...` records such as `TEST-0384` through `TEST-0388` are `unclassified` with `no_classification_signal`.

### Risk / Impact

The manifest is supposed to reduce cutover ambiguity by partitioning MemBase artifacts into framework, adopter, and unclassified buckets. Dropping the strongest test classification signal turns thousands of records with useful path evidence into owner-decision work. That increases manual owner burden and weakens ISOLATION-018 cutover readiness, contrary to the GroundTruth KB vision filter.

The issue is not that many records are unclassified; conservative classification is acceptable when signals are absent. The issue is that an approved signal source exists in the live schema and is not used.

### Required Action

- Implement the promised type-specific override layer for versioned tables.
- For `tests`, select and classify from at least `test_file`, and preferably `test_class` / `test_function` where useful.
- Restore or add regression tests for:
  - framework test paths such as `tests/groundtruth_kb/...` when present in fixtures;
  - adopter test paths such as `tests/transport/...` or current Agent Red application test directories;
  - mixed-scope test paths such as `test_release_candidate_gate.py`;
  - a live-schema fixture proving `tests.test_file` is actually read.
- Either implement the originally promised procedure/document topic overrides or explicitly revise the design to remove them with evidence that the remaining content-scan columns are sufficient.
- Re-run focused Slice 8 tests, driver tests, and live smoke; include a manifest sample proving path-classified test records no longer collapse to `no_classification_signal`.

### Owner Decision Needed

No.

## Finding 2 - P2: Whole Rehearsal Package Is Not Currently Green

### Claim

The broader `tests/scripts/test_rehearse_*.py` package is not fully green in this checkout.

### Evidence

- `python -m pytest @tmp/rehearse-test-files.txt -q --tb=line --timeout=120` collected 266 tests.
- Result: `265 passed, 1 failed`.
- Failure: `tests/scripts/test_rehearse_lint_clean.py::test_rehearse_package_passes_ruff_format_check`.
- Ruff reported `scripts\rehearse\_chromadb_regen.py` would be reformatted.

### Risk / Impact

This appears to be unrelated Slice 10 WIP, not a Slice 8 implementation defect. It does, however, contradict any claim that the whole rehearsal package is currently clean.

### Required Action

- Do not treat this as a Slice 8 functional blocker unless Slice 8 claims full package cleanliness.
- Prime should either format the WIP ChromaDB lane separately or scope future verification claims to the exact suites that are expected to be green.

### Owner Decision Needed

No.

## Verified Good Parts To Preserve

- Live table discovery matches the current 21 non-internal tables.
- Unknown table handling returns `status="error"`.
- Excluded telemetry tables include row count, reason, and cutover policy.
- Relationship row counts match live DB counts and parent classification is traceable.
- Per-session rows avoid defaulting unknown session ownership to adopter.
- Version preservation evidence matches live DB row and unique-artifact counts.
- SQLite read-only URI access and focused Slice 8 tests are green.

## Decision Needed From Owner

None.

