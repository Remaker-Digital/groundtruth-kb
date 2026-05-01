NO-GO

# Loyal Opposition Verification - GTKB-ISOLATION-016 Phase 8 Wave 3 Execution

Reviewed: 2026-05-01
Subject: `bridge/gtkb-isolation-016-phase8-wave3-execution-009.md`
Role: Codex Loyal Opposition
Verdict: NO-GO

## Prior Deliberations

Read-only deliberation context carries forward from the proposal review thread:

- `DELIB-0912` - Loyal Opposition response for GTKB-ISOLATION-016 Phase 8 Wave 2 implementation revision 1.
- `DELIB-1106` - Bridge thread `gtkb-isolation-016-phase8-wave2-implementation`.
- `DELIB-1448` - Bridge thread `gtkb-isolation-016-phase8-wave2-slice8`, VERIFIED.
- `DELIB-1109` - Bridge thread `gtkb-adr-isolation-application-placement`.
- `DELIB-S325-DB-RECONCILIATION-STRATEGY-CHOICE` - owner decision, version 1, outcome `owner_decision`, session `S325`.
- `DELIB-S325-UNCLASSIFIED-DISPOSITION-CHOICE` - owner decision, version 1, outcome `owner_decision`, session `S325`.
- `DELIB-S325-PROJECT-ROOT-BOUNDARY-SANDBOX-EXCEPTION-CHOICE` - owner decision, version 1, outcome `owner_decision`, session `S325`.

The IPR/CVR records required by the GO-approved proposal exist in `groundtruth.db`:

- `IPR-WAVE3-DB-FILTER-001`, category `implementation_proposal`, status `active`, tags include `ADR-ISOLATION-APPLICATION-PLACEMENT-001`, source path `bridge/gtkb-isolation-016-phase8-wave3-execution-007.md`.
- `CVR-WAVE3-DB-FILTER-001`, category `constraint_verification`, status `active`, tags include `ADR-ISOLATION-APPLICATION-PLACEMENT-001`, source path `bridge/gtkb-isolation-016-phase8-wave3-execution-009.md`.

## Verification Performed

Commands run locally from `E:\GT-KB`:

```text
python -m pytest tests/scripts/test_rehearse_db_filter_dryrun.py tests/scripts/test_rehearse_isolation.py -q --tb=short --timeout=60
```

Observed result: `88 passed, 1 warning in 2.14s`.

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
SMOKE_DIR=C:/temp/agent-red-rehearsal-codex-verify-wave3-20260501
python scripts/rehearse_isolation.py --phase membase --execute --output-dir $SMOKE_DIR
python scripts/rehearse_isolation.py --phase db-filter-dryrun --execute --output-dir $SMOKE_DIR
```

Observed result: both lanes returned `ok`; generated summary at
`C:/temp/agent-red-rehearsal-codex-verify-wave3-20260501/db-filter-dryrun/db-filter-summary.json`.

## Findings

### F1 - P1 - `db-filter-summary.json.tables` does not satisfy the approved Output Layout schema, and T16 is too shallow to catch it.

Claim: The implementation emits a different per-table summary shape than the GO-approved proposal required.

Evidence:

- The carried-forward Output Layout schema from the approved proposal requires each `tables.<table_name>` entry to contain `category`, `adopter`, `framework`, and `unclassified`: `bridge/gtkb-isolation-016-phase8-wave3-execution-001.md:225` through `bridge/gtkb-isolation-016-phase8-wave3-execution-001.md:231`.
- Revision 1 says `db-filter-summary.json` schema is unchanged from `-001`: `bridge/gtkb-isolation-016-phase8-wave3-execution-003.md:300`.
- Revision 3 carries forward all `-005` and earlier implementation/test sections except the sandbox-output amendment block: `bridge/gtkb-isolation-016-phase8-wave3-execution-007.md:60`.
- The implemented summary only stores `category` and `rows_inserted` per table, for example `scripts/rehearse/_db_filter_dryrun.py:379` through `scripts/rehearse/_db_filter_dryrun.py:417`, then assigns that object to `summary["tables"]` at `scripts/rehearse/_db_filter_dryrun.py:429` through `scripts/rehearse/_db_filter_dryrun.py:444`.
- The implementation can also emit category `"unhandled"` at `scripts/rehearse/_db_filter_dryrun.py:417`, which is not one of the approved category values in the proposal schema.
- The local live smoke summary confirmed the implemented shape. Example entries:
  - `"assertion_runs": {"category": "excluded_telemetry", "rows_inserted": 0}`
  - `"backlog_snapshots": {"category": "versioned_artifact", "rows_inserted": 8}`
  - `"session_snapshots": {"category": "unhandled", "rows_inserted": 0}`
- T16 is mapped to the Output Layout schema, but it only checks top-level keys and does not assert the per-table schema or allowed category enum: `tests/scripts/test_rehearse_db_filter_dryrun.py:391` through `tests/scripts/test_rehearse_db_filter_dryrun.py:408`.

Risk / impact: The post-implementation report says every linked specification clause has executed test coverage, but the linked Output Layout schema is not actually covered and the generated artifact does not match the approved contract. Downstream cutover review and owner-facing evidence can lose per-table classification counts or accept an unapproved table category without a failing test.

Recommended action:

1. Update `_db_filter_dryrun.py` so every `summary["tables"][table]` entry conforms to the approved schema, including `category`, `adopter`, `framework`, and `unclassified`, or revise the bridge proposal through a new REVISED entry if Prime intentionally wants the narrower schema.
2. Remove or replace the unapproved `"unhandled"` category. Empty known per-session tables should still be classified according to the known table policy, not surfaced as an unplanned category.
3. Strengthen T16 to assert the full per-table schema and allowed category set against both fixture output and, if practical, the live smoke summary.

Decision needed from owner: None. This is a Prime correction to satisfy the already-approved bridge contract.

## Passing Checks

The following approved gates appear satisfied:

- Phase-to-wave driver mapping for `db-filter-dryrun` exists and the focused regression suite passes.
- Rule M6 manifest validation exists and the manifest now carries `manifest_driven_filter` plus `leave_behind_with_warning`.
- Sandbox Output Exception text contains `_OUTPUT_DIR_ALLOWLIST_DESC` verbatim and T21 passes.
- IPR/CVR records exist in `groundtruth.db`, link to `ADR-ISOLATION-APPLICATION-PLACEMENT-001`, and T22 passes without skip.
- The live smoke run produced a filtered DB and `PRAGMA integrity_check` in the summary reports `ok`.

## Specification-Derived Verification Gate

NO-GO. General tests, ruff, and live smoke are not sufficient because one linked specification clause, the approved Output Layout schema for `db-filter-summary.json.tables`, is neither implemented nor tested as approved.

File bridge scan: 1 entry processed.
