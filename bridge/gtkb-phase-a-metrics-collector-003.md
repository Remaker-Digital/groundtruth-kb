# GT-KB Phase A Metrics Collector - Post-Implementation Report

**Status:** NEW (post-impl)
**Author:** Prime Builder (Opus 4.7)
**Date:** 2026-04-17
**Session:** S299 (auto-scan spawn)
**Implements:** `bridge/gtkb-phase-a-metrics-collector-002.md` (Codex GO)
**Target repo:** `groundtruth-kb`
**Parent commit at impl start:** `0a60054` (matches GO review target)
**Delivered commit:** `41ac869` on GT-KB main (10 files, +698/-0)

## Summary

Delivered `scripts/collect_phase_a_metrics.py` (final Phase A deliverable of
Tier A). Script consumes `.claude/hooks/scanner-safe-writer.log` (JSONL
schema v1) and emits aggregated deny-event metrics to stdout as JSON
(default, stable automation contract) or Markdown (human presentation).
Single GT-KB commit. Full suite 1161 -> 1189 (+28 new tests).

All three binding conditions from Codex GO -002 addressed before commit.

## Deliverables

1. **`scripts/collect_phase_a_metrics.py`** (~290 lines, stdlib only).
2. **Fixtures** under `tests/fixtures/phase_a_metrics/` (8 files):
   - `canonical_only.log` (3 records, canonical catalog)
   - `fallback_only.log` (2 records, fallback catalog)
   - `mixed_catalogs.log` (5 records including 1 multi-hit record for
     per-hit counting semantics)
   - `malformed_lines.log` (2 valid denies + 2 malformed lines)
   - `unknown_schema_version.log` (1 schema=1 valid + schema=2 + missing)
   - `wrong_event.log` (1 valid deny + 1 `event=pass` + 1 `hook=other-hook`)
   - `empty.log` (zero-byte)
   - `pattern_name_stability.log` (G5 regression fixture: same
     `pattern_name` with different `pattern_description`)
3. **`tests/test_phase_a_metrics_collector.py`** (28 tests).

No edits to `scanner-safe-writer.py`, `templates/`, or any production
source file - exit criterion 11 met.

## Binding Conditions Addressed (Codex GO -002)

### 1. Medium - whole-`scripts/` strict-mypy gate replaced with scoped gate

Verification gate for this bridge is the targeted:

```text
python -m mypy --strict --no-incremental scripts/collect_phase_a_metrics.py
Success: no issues found in 1 source file
```

No claim that `tests/test_full_tree_type_checks.py` covers this script. The
unrelated pre-existing `scripts/audit_*.py` and `scripts/check_docs_*.py`
debt is out of scope and untouched.

### 2. Medium - required edge tests + multi-hit pinning

Both tests promoted to **required** in the committed test module:

- `test_unique_file_paths_deduplicates` - authors 3 records sharing the
  same `file_path`, asserts `unique_file_paths == ["bridge/same-file-001.md"]`
- `test_session_id_null_folded_to_unknown` - asserts
  `by_session_id == {"(unknown)": 1}` for a `session_id: null` record.

Multi-hit record included in `mixed_catalogs.log` (record `mixed-005` has
two hits: `aws_access_key_id` + `anthropic_api_key`). Per-hit counting
semantics pinned by `test_multi_hit_record_counts_each_hit`:

- `total_deny_events == 5` (records, not hits)
- `sum(by_pattern_name.values()) == 6` (hits, not records)
- `by_pattern_name["aws_access_key_id"] == 3`
- `by_pattern_name["anthropic_api_key"] == 2`
- `by_pattern_name["generic_api_key"] == 1`

Documented in the `collect_metrics` docstring: "Per-pattern counts
increment once per hit, not once per record."

### 3. Low - warn-and-skip semantics + pattern_description output exclusion

**Warn on stderr:** implemented. `collect_metrics(log_path, warn_stream=...)`
emits one concise line to the provided stream per distinct unknown
`schema_version` value observed. CLI routes `warn_stream=sys.stderr`.
JSON stdout remains deterministic.

- `test_unknown_schema_version_emits_stderr_warning` pins library behavior.
- `test_cli_unknown_schema_version_warns_on_stderr` pins CLI boundary
  behavior (subprocess asserts both parseable stdout JSON and non-empty
  stderr containing `warning` + `schema_version`).

**Pattern-description output exclusion:** implemented and pinned.

- `test_json_stdout_excludes_pattern_description` asserts the JSON report
  contains no `pattern_description` substring and no description values
  (e.g., `"AWS access key ID"`).
- `test_markdown_output_excludes_pattern_description` asserts the Markdown
  render contains no `pattern_description` substring.
- `test_pattern_names_indexed_not_descriptions` (G5 contract test) feeds
  two records with identical `pattern_name` but divergent
  `pattern_description` values; asserts both collapse into a single
  `pattern_name` bucket with count 2.

## Verification Evidence

Commands executed in `E:\Claude-Playground\CLAUDE-PROJECTS\groundtruth-kb`:

```text
python -m ruff check scripts/collect_phase_a_metrics.py tests/test_phase_a_metrics_collector.py
# All checks passed!

python -m mypy --strict --no-incremental scripts/collect_phase_a_metrics.py
# Success: no issues found in 1 source file

python -m pytest tests/test_phase_a_metrics_collector.py -q
# 28 passed, 1 warning in 0.51s

python -m pytest -q
# 1189 passed, 1 warning in 254.60s (baseline 1161 + 28 new)

python -m ruff check .
# All checks passed!

python -m ruff format --check .
# 126 files already formatted
```

Post-commit state:

```text
git log --oneline -1
# 41ac869 feat(metrics): Phase A scanner-safe-writer metrics collector (Tier A #6)

git show --stat 41ac869
# 10 files changed, 698 insertions(+)
```

## Test Inventory (28 tests)

Required from proposal (10):
- `test_empty_log_returns_zero_metrics`
- `test_canonical_only_fixture`
- `test_fallback_only_fixture`
- `test_mixed_catalogs_fixture`
- `test_malformed_lines_counted_in_forward_compat`
- `test_unknown_schema_version_skipped_and_counted`
- `test_wrong_event_counted_in_forward_compat`
- `test_pattern_names_indexed_not_descriptions` (G5 contract)
- `test_by_date_groups_utc_date_from_timestamp`
- `test_cli_markdown_output_contains_headers`

Promoted from optional per binding condition 2 (3):
- `test_unique_file_paths_deduplicates`
- `test_session_id_null_folded_to_unknown`
- `test_cli_json_output_parses`

Added for binding conditions 2 and 3 (5):
- `test_multi_hit_record_counts_each_hit`
- `test_unknown_schema_version_emits_stderr_warning`
- `test_cli_unknown_schema_version_warns_on_stderr`
- `test_json_stdout_excludes_pattern_description`
- `test_markdown_output_excludes_pattern_description`

Additional defensive coverage (10):
- `test_empty_file_returns_zero_metrics`
- `test_pattern_name_ordering_is_deterministic`
- `test_fixture_exists_and_is_readable[<fixture>]` (parametrized x 8)

## Exit Criteria Check (from proposal -001)

| # | Criterion | Status |
|---|-----------|--------|
| 1 | Script exists, executable, follows design | ✅ |
| 2 | Indexes only on stable fields; never on `pattern_description` | ✅ pinned by 3 tests |
| 3 | Schema v1 fence: unknown versions counted in forward_compat and NOT in totals | ✅ |
| 4 | Malformed lines counted, not crashing | ✅ |
| 5 | JSON + Markdown both deterministic | ✅ |
| 6 | Fixtures under `tests/fixtures/phase_a_metrics/` | ✅ 8 files (7 designed + empty) |
| 7 | ~10 tests, all pass | ✅ 28 pass |
| 8 | `mypy --strict` clean on script | ✅ scoped gate per binding condition 1 |
| 9 | `ruff check` clean | ✅ |
| 10 | Full suite 1161 -> ~1171 | ✅ 1161 -> 1189 (+28) |
| 11 | No edits to production source / templates | ✅ |
| 12 | Single GT-KB commit | ✅ `41ac869` |

## Notes for Codex Verification

- Parallel uncommitted work exists in the GT-KB worktree:
  `src/groundtruth_kb/intake.py`, `project/doctor.py`, `project/scaffold.py`,
  `project/upgrade.py`, and `templates/skills/spec-intake/`. These are Tier
  A #5 in-flight by a separate thread and were **NOT** included in commit
  `41ac869`. `git show --stat 41ac869` verifies only the 10 Tier A #6 files.
- Log path default (`.claude/hooks/scanner-safe-writer.log`) resolves
  relative to CWD per open-question #3 in the proposal. No change in scope.
- No `--force` bypass was attempted. The bridge file itself is being
  written via helper-less `Write` tool; this post-impl report contains no
  credential values, only canonical pattern-name identifiers as strings.

## Copyright

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC.
All rights reserved.
