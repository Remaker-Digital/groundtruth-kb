VERIFIED

# Loyal Opposition Verification - GTKB-ISOLATION-016 Phase 8 Wave 3 Execution Revision 1

Reviewed: 2026-05-01
Subject: `bridge/gtkb-isolation-016-phase8-wave3-execution-011.md`
Role: Codex Loyal Opposition
Verdict: VERIFIED

## Review Scope

The live bridge index showed `gtkb-isolation-016-phase8-wave3-execution` at latest status `REVISED` with `bridge/gtkb-isolation-016-phase8-wave3-execution-011.md`.

All prior bridge versions in the entry were read before this response. This verification is scoped to the Prime revision that addresses Codex `-010` finding F1:

- per-table `db-filter-summary.json.tables` entries must contain `category`, `adopter`, `framework`, and `unclassified`;
- `category` must be one of the approved enum values: `versioned_artifact`, `relationship`, `excluded_telemetry`, `per_session`;
- the unapproved `unhandled` category must be absent;
- T16 must assert the full per-table schema.

## Verification Performed

Commands run locally from `E:\GT-KB`:

```text
python -m pytest tests/scripts/test_rehearse_db_filter_dryrun.py tests/scripts/test_rehearse_isolation.py -q --tb=short --timeout=60
```

Observed result: `88 passed, 1 warning in 2.21s`.

```text
python -m ruff check scripts/rehearse/_db_filter_dryrun.py scripts/rehearse/_common.py scripts/rehearse_isolation.py tests/scripts/test_rehearse_db_filter_dryrun.py tests/scripts/test_rehearse_isolation.py
```

Observed result: `All checks passed!`.

```text
python -m ruff format --check scripts/rehearse/_db_filter_dryrun.py scripts/rehearse/_common.py scripts/rehearse_isolation.py tests/scripts/test_rehearse_db_filter_dryrun.py tests/scripts/test_rehearse_isolation.py
```

Observed result: `5 files already formatted`.

Live smoke run:

```text
SMOKE_DIR=C:/temp/agent-red-rehearsal-codex-verify-wave3-20260501-r2
python scripts/rehearse_isolation.py --phase membase --execute --output-dir $SMOKE_DIR
python scripts/rehearse_isolation.py --phase db-filter-dryrun --execute --output-dir $SMOKE_DIR
```

Observed result: both lanes returned `ok`; generated summary at `C:/temp/agent-red-rehearsal-codex-verify-wave3-20260501-r2/db-filter-dryrun/db-filter-summary.json`.

Additional live-artifact checks:

```text
bad_table_entries= 0
table_count= 21
categories= ['excluded_telemetry', 'per_session', 'relationship', 'versioned_artifact']
integrity_check= ok
```

Filtered DB spot checks:

```text
specifications_gtkb_prefix= 0
assertion_runs= 0
integrity_check= ok
```

## Findings

No blocking findings.

## Gate Checks

### F1 Closure - PASS

Claim: The revised implementation now satisfies the approved per-table Output Layout schema and removes the unapproved `unhandled` category.

Evidence:

- `_db_filter_dryrun.py` defines the closed approved table category enum and classifies discovered tables only through closed-set membership: `scripts/rehearse/_db_filter_dryrun.py:60`, `scripts/rehearse/_db_filter_dryrun.py:65`, `scripts/rehearse/_db_filter_dryrun.py:425`.
- Excluded telemetry, versioned artifact, relationship, and per-session summaries now populate `table_counts[table]` as `{category, adopter, framework, unclassified}`: `scripts/rehearse/_db_filter_dryrun.py:434`, `scripts/rehearse/_db_filter_dryrun.py:453`, `scripts/rehearse/_db_filter_dryrun.py:464`, `scripts/rehearse/_db_filter_dryrun.py:474`.
- Unknown tables now produce `unknown_tables_in_legacy_db` error output instead of a silent or unapproved category: `scripts/rehearse/_db_filter_dryrun.py:525`.
- T16 now asserts the required per-table keys, approved category enum, and integer count types: `tests/scripts/test_rehearse_db_filter_dryrun.py:415` through `tests/scripts/test_rehearse_db_filter_dryrun.py:426`.
- The live smoke summary contained 21 table entries, zero bad per-table schema entries, and only approved categories.

Risk / impact: The Output Layout drift identified in `-010` is closed, and future drift in the per-table schema should fail T16.

Recommended action: None for this finding.

Decision needed from owner: None.

### Specification-Derived Verification Gate - PASS

Claim: The implementation report's linked verification obligations are satisfied for this revision.

Evidence:

- The manifest carries `db_reconciliation_strategy = "manifest_driven_filter"` and `unclassified_disposition = "leave_behind_with_warning"`: `independent-progress-assessments/CODEX-INSIGHT-DROPBOX/rehearsal/manifest.toml:40`, `independent-progress-assessments/CODEX-INSIGHT-DROPBOX/rehearsal/manifest.toml:48`.
- M6 validation remains present for the Wave 3 fields: `scripts/rehearse/_common.py:357` through `scripts/rehearse/_common.py:370`.
- The sandbox-output exception contains the exact `_OUTPUT_DIR_ALLOWLIST_DESC` text required by T21: `.claude/rules/project-root-boundary.md:36` through `.claude/rules/project-root-boundary.md:53`.
- T22 hard-passed inside the focused suite, proving the IPR/CVR records exist and link to `ADR-ISOLATION-APPLICATION-PLACEMENT-001`.
- The live smoke run produced `integrity_check=ok`, zero `GTKB-%` specification rows in the filtered preview DB, and zero `assertion_runs` rows.

Risk / impact: No remaining verification gap was found in the revised post-implementation report.

Recommended action: Proceed to bridge closure for this entry.

Decision needed from owner: None.

## Non-Blocking Observation

The driver still prints `rehearse_isolation: Wave 2 dispatch` even when `--phase db-filter-dryrun` is selected: `scripts/rehearse_isolation.py:283`. This appears to be stale display text only: the actual code calls `_wave_for_phase(args.phase)` and passes that value to `load_manifest()` at `scripts/rehearse_isolation.py:260` through `scripts/rehearse_isolation.py:261`, and the focused regression suite passed the Wave 3 CLI-path tests. This does not block VERIFIED, but Prime should consider correcting the banner in a later cleanup to avoid operator confusion.

## Verdict

VERIFIED. Prime Builder's `-011` revision closes Codex `-010` F1 and satisfies the post-implementation verification gate for `gtkb-isolation-016-phase8-wave3-execution`.

File bridge scan: 1 entry processed.
