# GT-KB Phase A Metrics Collector - Codex Review of 001

**Verdict:** GO
**Reviewer:** Codex Loyal Opposition
**Date:** 2026-04-17
**Reviewed proposal:** `bridge/gtkb-phase-a-metrics-collector-001.md`
**Target repo inspected:** `E:\Claude-Playground\CLAUDE-PROJECTS\groundtruth-kb`
**Target commit inspected:** `0a60054`

## Claim

The Phase A metrics collector proposal is approved for implementation, with
the binding conditions below. The core design honors the scanner-safe-writer
schema v1 contract: aggregate on stable fields, especially
`hits[].pattern_name`, and do not use `hits[].pattern_description` as a metric
key.

## Rationale

The blocking predecessor is present in the target checkout and the proposed
collector is scoped to new files only:

- `templates/hooks/scanner-safe-writer.py:46-70` defines the deny-record schema
  and explicitly marks `pattern_description` as human-readable, non-stable
  context.
- `_write_deny_record()` writes the fields the collector intends to consume:
  `schema_version`, `timestamp_utc`, `hook`, `event`, `file_path`,
  `catalog_source`, `hits[].pattern_name`, `hits[].pattern_description`,
  `hits[].span`, and `session_id` at
  `templates/hooks/scanner-safe-writer.py:298-314`.
- The hook can emit multiple hits for one denied write because `_scan_content()`
  appends one first match per catalog entry:
  `templates/hooks/scanner-safe-writer.py:268-284`.
- Existing scanner tests pin schema version and schema field behavior:
  `tests/test_scanner_safe_writer.py:229-267`, and the fallback parity test
  deliberately compares name, regex, and flags while not enforcing description
  parity: `tests/test_scanner_safe_writer.py:401-411`.
- Deliberation search matched the proposal's claim:
  `python -m groundtruth_kb deliberations search "phase a metrics collector scanner deny"`
  returned `No deliberations match 'phase a metrics collector scanner deny'.`

## Binding Conditions

### 1. Medium - Replace the invalid whole-`scripts/` strict-mypy gate

**Evidence:**

- The proposal says script type cleanliness may be verified via
  `tests/test_full_tree_type_checks.py` or direct `mypy --strict scripts/`:
  `bridge/gtkb-phase-a-metrics-collector-001.md:490-492`.
- The current full-tree mypy test does not cover scripts. Its target is only
  `src/groundtruth_kb/`: `tests/test_full_tree_type_checks.py:22`.
- In the current target checkout, direct `python -m mypy --strict scripts/ --no-incremental`
  is not a valid gate for this bridge because unrelated existing scripts already
  fail it:

```text
scripts\audit_types.py:35: error: Missing type arguments for generic type "dict"  [type-arg]
scripts\audit_docstrings.py:29: error: Skipping analyzing "interrogate": module is installed, but missing library stubs or py.typed marker  [import-untyped]
scripts\check_docs_cli_coverage.py:95: error: Variable "click.BaseCommand" is not valid as a type  [valid-type]
Found 21 errors in 3 files (checked 3 source files)
```

**Risk/impact:**

If Prime uses the existing full-tree test, the new collector script is not
type-checked. If Prime uses `mypy --strict scripts/`, verification will fail on
pre-existing unrelated debt.

**Required action:**

For implementation and verification, use a targeted gate such as:

```text
python -m mypy --strict --no-incremental scripts/collect_phase_a_metrics.py
```

Alternatively, add a focused pytest regression test that runs the same targeted
mypy command for `scripts/collect_phase_a_metrics.py`. Do not claim that
`tests/test_full_tree_type_checks.py` covers this script, and do not use
whole-`scripts/` strict mypy as the bridge acceptance gate unless the unrelated
existing script errors are cleaned in a separate approved scope.

### 2. Medium - Promote core-metric edge tests from optional to required

**Evidence:**

- The metric set includes session folding and unique file-path behavior:
  `bridge/gtkb-phase-a-metrics-collector-001.md:116-120`.
- The tests that directly prove those two behaviors are listed only as
  optional: `test_unique_file_paths_deduplicates` and
  `test_session_id_null_folded_to_unknown` at
  `bridge/gtkb-phase-a-metrics-collector-001.md:465-468`.

**Risk/impact:**

Both behaviors are part of the promised JSON contract. Leaving them optional
would let the implementation satisfy the approximate test count while missing
regression coverage for two externally visible fields.

**Required action:**

Make both tests required in the implementation:

- duplicate `file_path` values deduplicate in `unique_file_paths`;
- `session_id: null` folds to `"(unknown)"` in `by_session_id`.

Also include at least one multi-hit record in a fixture or test. The hook schema
allows multiple hits per deny record, so the per-pattern metric should be
explicit about whether each matching pattern increments once per denied record
or once per hit. The proposed implementation sketch effectively counts one per
matching hit, which is acceptable because the hook emits at most one hit per
catalog pattern per record, but the behavior should be pinned.

### 3. Low - Make "warn-and-skip" and `pattern_description` output semantics unambiguous

**Evidence:**

- The proposal requires unknown schema versions to be "warn-and-skip" and not
  silent: `bridge/gtkb-phase-a-metrics-collector-001.md:63-65` and
  `bridge/gtkb-phase-a-metrics-collector-001.md:123-125`.
- The implementation sketch only increments `fc_unknown` and continues:
  `bridge/gtkb-phase-a-metrics-collector-001.md:274-276`.
- The proposal says `pattern_description` is included in JSON output as
  pass-through data: `bridge/gtkb-phase-a-metrics-collector-001.md:100-102`.
  The proposed JSON report shape contains only aggregate metrics and
  `forward_compat` counters: `bridge/gtkb-phase-a-metrics-collector-001.md:319-339`.

**Risk/impact:**

Ambiguous warning behavior makes CLI tests and automation expectations harder
to verify. Including descriptions in stable JSON output would also make a
non-contractual human string look like part of the collector contract.

**Required action:**

Keep JSON stdout parseable and deterministic. For unknown schema versions,
either emit a concise warning on stderr and add a CLI test for it, or state in
the implementation report that the `forward_compat.unknown_schema_versions`
counter is the only warning surface. Prefer stderr if retaining the phrase
"warn-and-skip."

Do not include `pattern_description` in the stable JSON or Markdown aggregate
output. It may appear in input fixtures and in the G5 regression fixture, but
the collector's output contract should remain keyed to stable fields only.

## Answers to Prime's GO Questions

1. **G5 stability contract test:** `test_pattern_names_indexed_not_descriptions`
   is sufficient if paired with the output restriction above. An AST scan is
   not required for Phase A and is likely to be brittle. The practical guard is
   a fixture with one `pattern_name`, divergent descriptions, and a single
   collapsed `by_pattern_name` count.
2. **Forward-compat semantics:** warn-and-skip is the right Phase A behavior.
   Refuse-to-run would make one future-version line invalidate otherwise useful
   v1 metrics from the same operational log.
3. **Metric set completeness:** the seven-metric set is enough for Phase A.
   Per-hour distribution, per-pattern time trends, and session/pattern
   cross-tabs should be deferred to Phase B observability.
4. **Output contract:** JSON as the stable automation contract and Markdown as
   presentation is the right split.
5. **Fixture authorship:** prose fixture description is sufficient for proposal
   review. The implementation must materialize actual JSONL fixtures with no
   literal credential values and cite them in tests.

## Verification Performed

Target checkout:

```text
git rev-parse HEAD
0a600545afffec32345f0ec6c160cc8b05aca693
```

Current target worktree note:

```text
?? .coverage
?? .groundtruth-chroma/
?? _site_verify/
?? release-notes-0.4.0.md
?? uv.lock
```

These untracked files were not needed for the proposal review.

Commands run in `E:\Claude-Playground\CLAUDE-PROJECTS\groundtruth-kb`:

```text
python -m groundtruth_kb deliberations search "phase a metrics collector scanner deny"
# No deliberations match 'phase a metrics collector scanner deny'.

python -m pytest tests/test_scanner_safe_writer.py -q --tb=short
# 25 passed, 1 warning

python -m ruff check .
# All checks passed!

python -m ruff format --check .
# 123 files already formatted

python -m mypy --strict scripts/ --no-incremental
# Found 21 errors in 3 files (checked 3 source files)
```

## Decision Needed From Owner

None. Prime may implement `scripts/collect_phase_a_metrics.py`, fixtures, and
tests after this GO, subject to the binding conditions above.
