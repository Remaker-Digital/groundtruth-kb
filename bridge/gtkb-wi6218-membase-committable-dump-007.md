NEW
::init gtkb lo
::open build
author_identity: prime-builder/claude/B
author_harness_id: B
author_session_context_id: a0dbbe63-b24f-42eb-9274-e0fec8b23a00
author_model: claude-opus-5
author_model_version: claude-opus-5
author_model_configuration: Claude Code interactive Prime Builder; resolved role prime-builder via the canonical init keyword


# WI-6218 — MemBase Committable Dump: Implementation Report

bridge_kind: implementation_report
Document: gtkb-wi6218-membase-committable-dump
Version: 007

Work Item: WI-6218
Project: PROJECT-GTKB-GET-HEALTHY-PHASE-2
Project Authorization: PAUTH-GET-HEALTHY-PHASE-2-EXECUTION-20260814B

target_paths: ["scripts/membase_dump.py", ".gitignore", "platform_tests/scripts/test_membase_dump.py", "config/membase-dump/dump-policy.toml"]

implementation_scope: source
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

Responds to: bridge/gtkb-wi6218-membase-committable-dump-006.md

---

## Headline

Three of the four GO'd target paths are implemented, tested and measured against
the live database. **The fourth — `config/membase-dump/dump-policy.toml` — could
not be written.** A pre-existing platform classifier treats it as an application
artifact and hard-blocks the write; the remedy is a one-line change to a file
outside this thread's `target_paths`. Details and evidence in § Blocker below.
Nothing was committed, per the owner's 2026-08-14 directive that the verifying
Loyal Opposition is the party that commits.

The policy's exact intended content exists and has been exercised end-to-end
against the live database from a staging path; only its final placement is
blocked.

## Blocker — the policy file could not be written to its scoped path

`scripts/workstream_focus.py` classifies write targets under a 4-category
taxonomy. `config/` is a blanket `APPLICATION_PREFIXES` entry
(`scripts/workstream_focus.py:238-249`), with an explicit carve-out list of
GT-KB platform config subdirectories added by WI-5100
(`scripts/workstream_focus.py:266-271`): `config/agent-control/`,
`config/dispatcher/`, `config/governance/`, `config/harness-parity/`,
`config/project-templates/`, `config/registry/`. Any other `config/<subdir>`
falls through to `application_product`, and the `gtkb_infrastructure` work
subject blocks `application_product` targets (`guard_tool_use`,
`scripts/workstream_focus.py:2410`).

`config/membase-dump/` is a new platform config subdirectory and is not on that
carve-out list. Observed classification:

```
current_subject: gtkb_infrastructure
config/membase-dump/dump-policy.toml        -> application_product
config/dispatcher/rules.toml                -> current_repo_bridge_or_governance
scripts/membase_dump.py                     -> neutral
.gitignore                                  -> neutral
platform_tests/scripts/test_membase_dump.py -> neutral
```

The write was hard-blocked:

```
BLOCKED (GTKB-WORK-SUBJECT): Current work subject is GT-KB. This change targets
application product artifacts (E:\GT-KB\config\membase-dump\dump-policy.toml).
```

This is a classifier gap, not a scope error in `-005`. The PAUTH evaluator
independently classified the same path as mutation class `configuration` and
allowed it (`implementation_authorization.py begin`, `classified_targets`), and
the implementation-start gate admits it because it is a declared `target_path`.
Two gates permit it; the third refuses it on a stale prefix list.

**Why this was not routed around.** The established remedy (the WI-5100
precedent) is to add `config/membase-dump/` to
`CURRENT_REPO_BRIDGE_OR_GOVERNANCE_PREFIXES`. That file is not in this thread's
`target_paths`, and it is itself a governance surface listed in
`CURRENT_REPO_BRIDGE_OR_GOVERNANCE_FILES`. The emergency-bootstrap exception in
`.claude/rules/governance-emergency-bootstrap-protocol.md` does not apply: its
condition (a) requires the normal path to be blocked by the very defect being
repaired, and here the normal path — a `REVISED` proposal adding that one file
to `target_paths` — is fully available. Relocating the policy to an
already-carved-out directory was also rejected: it would deviate from the GO'd
`target_paths`, which the implementation-start gate enforces exactly.

**Recommended disposition (owner/reviewer decision, not requested here as a
blocking ask):** file a narrow `REVISED` proposal adding
`scripts/workstream_focus.py` to `target_paths` for a one-line carve-out
addition, then land the policy file unchanged. The policy content is settled and
proven; only its placement is outstanding.

**Where the content is staged.** The exact intended file content is at
`.gtkb-state/wi6218-dump-probe/dump-policy.toml` (ephemeral runtime evidence,
not a source-of-truth artifact and not a substitute for the scoped path). Every
live-database measurement below was produced with it.

## What changed, file by file

### `scripts/membase_dump.py` (new)

The dump/restore/check service.

- **`dump`** — projects the governed subset to `membase-dump/<table>/schema.sql`
  plus `membase-dump/<table>/<NNNN>.sql` data chunks, then prunes artifacts the
  current database no longer produces.
- **`check`** — regenerates in memory, compares against disk, reports
  missing/stale/changed artifacts, exits 1 on drift, writes nothing.
- **`restore --target`** — rebuilds a database into a new file.

Load-bearing design points:

1. **Selection is data.** `load_policy()` is the only source of the include and
   exclude sets. The module contains no governed table name at all. A table
   present in the database but in neither policy set raises
   `UnclassifiedTableError`; a policy table absent from the database raises
   `MissingTableError`. Both fail closed, so schema growth can neither silently
   enter the projection nor silently escape it.
2. **Fixed row-range sharding.** `chunk_index = rowid // rows_per_chunk`. A chunk
   owns a fixed span of the rowid space, so an append touches only the tail chunk
   and every earlier chunk stays byte-identical.
3. **Budgets fail closed before any write.** `generate_artifacts()` builds the
   whole projection in memory and `_enforce_budgets()` checks the per-file budget
   and the aggregate ceiling before `write_artifacts()` is reached. An oversized
   projection raises with nothing on disk.
4. **Read-only, snapshot-consistent source access.** `open_readonly()` opens
   `mode=ro`; generation runs inside a deferred transaction so a WAL database
   yields one consistent snapshot while another connection is writing.

Three implementation decisions the proposal did not spell out, surfaced here for
review:

- **`schema.sql` per table.** `-005` names only `<table>/<NNNN>.sql`, but the
  proposal's round-trip requirement ("restore into an empty DB") needs DDL. Each
  included table therefore also emits `<table>/schema.sql` carrying its
  `CREATE TABLE` and its index DDL.
- **Explicit rowid emission.** Where a table has no `INTEGER PRIMARY KEY` alias
  column, `rowid` is emitted as an explicit column. This is required, not
  cosmetic: the live database has rowid gaps (`tests` holds 29,020 rows across
  rowids 1..33,569), so re-assigned rowids on restore would change chunk
  membership and break byte-reproducibility. Two included tables are affected
  (`deliberation_specs`, `deliberation_work_items`).
- **Restore load order and pragmas.** Tables, then rows, then indexes, with
  `journal_mode`/`synchronous` off for the load. Measured below: this is the
  difference between a 4.6-second recovery and a multi-hour one. The target is
  always a brand-new file, discarded on failure, so nothing durable is at risk.

### `platform_tests/scripts/test_membase_dump.py` (new, 33 tests)

Behavioral tests against purpose-built fixture databases. The live database is
never read or written by the module. Fixture policies are written per test,
which is itself the proof that selection is data — the same fixture database
projects differently under two different policies with no change to the dumper.

### `.gitignore` (modified, +8 lines)

Adds `!membase-dump/` and `!membase-dump/**` after `.groundtruth-chroma/`, with
a comment tying the projection to the ignored database above it.

**Stated plainly: this negation is currently defensive, not load-bearing.** No
existing pattern covers `membase-dump/`, so the paths were already trackable.
Verified with `git check-ignore -q` (exit 1 = not ignored), calibrated against
`groundtruth.db` (exit 0 = ignored) and the known `secrets/` negation (exit 1).
The negation earns its place by preventing a future broad pattern in that
section from silently un-tracking the projection.

### `config/membase-dump/dump-policy.toml` — NOT WRITTEN

Blocked as above. Content settled: 33 included tables, 26 excluded tables,
exhaustive over all 59 tables in the live schema, with a recorded reason and
recoverability statement on every exclusion.

## Live-database measurements

Produced against the live `groundtruth.db` with the staged policy. Read-only;
the database is byte-unchanged (`dump` uses `mode=ro`).

| Measure | Value |
|---|---|
| Projection total | 179,285,553 bytes (171 MiB) |
| Aggregate ceiling | 262,144,000 bytes (250 MiB) — 68% consumed |
| Files emitted | 87 |
| Largest single artifact | 10,365,459 bytes (`deliberations/0012.sql`) |
| Per-file budget | 26,214,400 bytes (25 MiB) — largest at 40% |
| Restore into a fresh database | 4.6 s, 172,535,808 bytes |
| Real-data round-trip | 87/87 artifacts byte-identical |

**The 171 MiB total is above the ~148 MB `-005` estimated, and the reviewer
should weigh this.** The difference is that `-005` enumerated the governed
classes by name and left "remaining 44 tables … per policy"; the policy resolves
that remainder explicitly and includes 33 tables, among them `harnesses`,
`canonical_terms`, the linkage tables, and the registry receipt tables. It
remains well under the ceiling and every individual artifact is well under the
per-file budget. Any include row the reviewer disagrees with moves to the
exclude set without a design change.

**A tuning defect was found and fixed during measurement.** The first live run
produced `work_items/0000.sql` at 24,599,007 bytes — 94% of the 25 MiB budget,
because `work_items` averages ~2.0 kB/row and the default 20,000-row span put
all 12,477 rows in one chunk. `deliberations/0004.sql` was at 14.0 MB. Chunk
spans are now set from measured average row widths under the rule
`avg_row_width x span <= ~10 MB`, i.e. under half the budget, leaving headroom
for rows inside an already-established span getting wider. That re-run also
exercised stale-artifact pruning on real data (5 artifacts from the previous
chunk sizing were pruned).

## Verification of the GO verdict's expectations (V1-V6)

| ID | Expectation | Result |
|---|---|---|
| V1 | Size-budget guard actually fires | `test_dumper_refuses_to_emit_oversized_chunk` asserts the raise AND that the output directory does not exist; mutation M1 confirms the test fails when the guard is gone |
| V2 | Append-only chunk stability | `test_append_rewrites_only_tail_chunk` uses gapped rowids so range-keyed and position-keyed chunking are distinguishable; every non-tail chunk asserted byte-identical; mutation M3 confirms |
| V3 | Aggregate-ceiling test present, aggregate reported | `test_aggregate_dump_under_ceiling` + `test_dumper_refuses_to_exceed_aggregate_ceiling`; `test_cli_reports_the_measured_aggregate` asserts the CLI prints the measured total; live aggregate 179,285,553 bytes reported above |
| V4 | Policy is the sole source of selection | `test_selection_follows_policy_not_code` (same DB, two policies, different output), `test_excluded_tables_never_appear`, `test_dumper_has_no_hardcoded_table_list`, `test_unclassified_table_is_a_hard_error`; mutations M5 and M8 confirm |
| V5 | First dump NOT committed under this slice | Honored. No projection exists in the worktree; nothing was committed at all. The live projection was written to an ephemeral path and cleared after measurement |
| V6 | Restore refuses to overwrite the canonical DB; WAL safety retained | `test_restore_refuses_the_canonical_database` (asserts the canonical file is byte-unchanged), `test_restore_refuses_an_existing_target`, `test_restore_refuses_a_target_with_wal_sidecars`, `test_dump_under_a_concurrent_writer_sees_a_consistent_snapshot`; mutation M6 confirms |

## Specification Links

Carried forward from `-005`:

- `GOV-STANDING-BACKLOG-001` v5 — WI-6218 is the governing backlog item; the
  governed content this projection makes clonable.
- `GOV-SOURCE-OF-TRUTH-FRESHNESS-001` v5 — `check` is the freshness instrument;
  the figures above are fresh measurements, not carried-forward estimates.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` — durable artifacts over transient
  state; the exclusion policy records which state is deliberately not durable.
- `GOV-FILE-BRIDGE-AUTHORITY-001` v4 — bridge audit-trail discipline governing
  this thread.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` v1 — spec linkage.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` v1 — spec-derived testing.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` v1 — project linkage.
- `SPEC-1662` (GOV-18: Assertion Quality Standard) — the tests assert behavior,
  and each was proven to fail against a mutated implementation.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`, `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`
  — advisory specs surfaced by the `-006` preflight, cited here.
- `.claude/rules/project-root-boundary.md` — every target path and every runtime
  artifact stayed within `E:\GT-KB`.

## Specification-Derived Verification

| Requirement (source) | Test | Result |
|---|---|---|
| `-002` F1.1 selection policy | `test_excluded_tables_never_appear` | PASS — no excluded-table data in any artifact |
| `-002` F1.1 policy is data | `test_selection_follows_policy_not_code` | PASS — same DB, two policies, disjoint output |
| `-002` F1.1 policy is data | `test_dumper_has_no_hardcoded_table_list` | PASS — no governed table name in the module |
| `-002` F1.1 closed classification | `test_unclassified_table_is_a_hard_error` | PASS — names every unclassified table |
| `-002` F1.1 policy integrity | `test_policy_naming_an_absent_table_is_a_hard_error`, `test_policy_rejects_a_table_in_both_sets`, `test_policy_requires_recoverability_on_every_exclusion` | PASS |
| `-002` F1.2 sharding | `test_wide_table_shards_into_multiple_chunks` | PASS — 6 non-empty chunks |
| `-002` F1.2 range key, not position | `test_chunk_membership_follows_the_rowid_range_not_row_position` | PASS — gapped rowids yield one chunk per occupied span |
| `-002` F1.3 size budget | `test_no_emitted_file_exceeds_budget` | PASS — includes a guard against a vacuous pass |
| `-002` F1.3 fail closed | `test_dumper_refuses_to_emit_oversized_chunk`, `test_cli_fails_closed_with_exit_two_on_budget_violation` | PASS — raises, exit 2, nothing written |
| `-002` F1.3 aggregate ceiling | `test_aggregate_dump_under_ceiling`, `test_dumper_refuses_to_exceed_aggregate_ceiling`, `test_cli_reports_the_measured_aggregate` | PASS |
| `-002` F1.4 growth profile | `test_append_rewrites_only_tail_chunk` | PASS — exactly one chunk changed |
| determinism (`-005` §5) | `test_dump_is_byte_reproducible`, `test_dump_output_uses_lf_endings_only` | PASS; plus two consecutive live-DB `check` runs both clean |
| round-trip (`-005` §5) | `test_restore_round_trips_governed_tables`, `test_rowid_gaps_survive_the_round_trip`, `test_awkward_values_round_trip_through_the_projection`, `test_schema_statements_with_embedded_semicolons_restore_correctly`, `test_restore_recreates_indexes_after_loading_rows` | PASS; plus a byte-identical 87/87 real-data round-trip |
| freshness (`-005` §5) | `test_check_reports_drift_without_writing`, `test_check_reports_missing_and_stale_artifacts`, `test_cli_check_exits_nonzero_on_drift` | PASS — drift detected, disk untouched |
| stale pruning | `test_dump_drops_stale_artifacts` | PASS; also exercised on live data |
| read-only source (`GOV-08`) | `test_dump_leaves_the_source_database_unmodified` | PASS |
| WAL safety (`-001` scope 4) | `test_dump_under_a_concurrent_writer_sees_a_consistent_snapshot` | PASS — uncommitted row absent, present after commit |
| canonical-DB safety (V6) | `test_restore_refuses_the_canonical_database` and two sibling refusal tests | PASS |
| value fidelity | `test_awkward_values_round_trip_through_the_projection`, `test_sql_literal_rejects_non_representable_floats` | PASS — storage class preserved, NaN/inf refused |
| `config/membase-dump/dump-policy.toml` | — | **NOT VERIFIED — file not written (see § Blocker)** |

### Red-first evidence

The two Python files are net-new, so "run the tests against HEAD" is vacuous —
every test errors on import. Meaningful proof therefore came from mutation
testing: each guarantee was removed from the implementation, the covering tests
re-run, and the original restored (restoration verified by content comparison
after every run). **All 12 mutations were caught.**

| # | Mutation | Caught by |
|---|---|---|
| M1 | Per-file budget guard removed | `test_dumper_refuses_to_emit_oversized_chunk`, `test_cli_fails_closed_with_exit_two_on_budget_violation` |
| M2 | Aggregate ceiling guard removed | `test_dumper_refuses_to_exceed_aggregate_ceiling` |
| M3 | Chunking switched from rowid range to row position | `test_append_rewrites_only_tail_chunk`, `test_chunk_membership_follows_the_rowid_range_not_row_position` |
| M4 | Explicit rowid dropped for alias-less tables | `test_rowid_gaps_survive_the_round_trip` (1 of 2 targeted; see note) |
| M5 | Unclassified tables silently included | `test_unclassified_table_is_a_hard_error` |
| M6 | Canonical-database restore refusal removed | `test_restore_refuses_the_canonical_database` |
| M7 | Stale-artifact pruning removed | `test_dump_drops_stale_artifacts` (1 of 2 targeted; see note) |
| M8 | Policy include set ignored, every table projected | `test_selection_follows_policy_not_code`, `test_excluded_tables_never_appear` |
| M9 | A timestamp leaks into the artifact body | `test_dump_is_byte_reproducible` |
| M10 | CRLF emitted instead of LF | `test_dump_output_uses_lf_endings_only` |
| M11 | Index DDL deferred then never replayed | `test_restore_recreates_indexes_after_loading_rows` |
| M12 | Schema split naively on `;` (quote-unaware) | `test_schema_statements_with_embedded_semicolons_restore_correctly` |

Two honest notes on partial results. Under M4,
`test_restore_round_trips_governed_tables` still passed — correctly, because its
fixture has no rowid gaps; only the gap-specific test discriminates. Under M7,
`test_check_reports_missing_and_stale_artifacts` still passed — correctly,
because it never calls `write_artifacts` twice.

M12 initially came back **GREEN**, i.e. the test did not catch it: the fixture's
semicolons were mid-line, which a naive line-splitter handles identically. The
fixture was corrected to a multi-line DDL whose string literal ends a line with
a semicolon — the case that actually distinguishes quote-aware splitting — and
M12 then went RED. Reported because the first version of that test was asserting
less than it appeared to.

### A test defect found and corrected

`test_awkward_values_round_trip_through_the_projection` initially asserted that
a REAL value survived the round-trip, and failed. Investigation showed the
**dumper was correct** and the test was wrong: the fixture inserted a float into
a `TEXT`-affinity column, so SQLite converted it to text on insert, before the
dumper ever saw it. The fixture now uses a no-affinity column and asserts
`typeof()` equality between source and restored rows, which genuinely exercises
REAL, BLOB, INTEGER, NULL and TEXT storage classes.

## Commands Executed

```
$ groundtruth-kb\.venv\Scripts\python.exe -m pytest platform_tests/scripts/test_membase_dump.py -q
33 passed, 1 warning in 1.18s

$ groundtruth-kb\.venv\Scripts\python.exe -m ruff check scripts/membase_dump.py platform_tests/scripts/test_membase_dump.py
All checks passed!                                        (exit 0)

$ groundtruth-kb\.venv\Scripts\python.exe -m ruff format --check scripts/membase_dump.py platform_tests/scripts/test_membase_dump.py
2 files already formatted                                 (exit 0)
```

`ruff format --check` failed on the first attempt ("2 files would be
reformatted") while `ruff check` passed; `ruff format` was applied and both
gates re-run to green. Recorded because the two gates are independent and CI
enforces both.

Live-database exercise (staged policy; read-only against `groundtruth.db`):

```
$ ... scripts\membase_dump.py dump --db groundtruth.db --policy <staged> --out <ephemeral>
total: 87 file(s), 179285553 bytes (ceiling 262144000); largest file 10365459 bytes (budget 26214400)
  (5 stale artifacts from the previous chunk sizing were pruned)          exit 0

$ ... scripts\membase_dump.py check --db groundtruth.db --policy <staged> --out <ephemeral>
projection ... is current                                                 exit 0
$ ... (second consecutive run)
projection ... is current                                                 exit 0   <- byte-reproducible on live data

$ ... round-trip: restore -> re-project -> compare
restored 87 artifact(s) in 4.6s
restored database size: 172,535,808 bytes
original artifacts: 87   replayed artifacts: 87
differing artifacts: 0
ROUND-TRIP BYTE-IDENTICAL: True
```

Broader regression sweep over the seven test modules that reference `.gitignore`:

```
$ ... -m pytest platform_tests/scripts/test_no_tracked_pyc_artifacts.py \
    platform_tests/scripts/test_gitignore_tree_stabilization_scratch.py \
    platform_tests/scripts/test_gitignore_session_snapshots.py \
    platform_tests/scripts/test_hygiene_strays_cli.py \
    platform_tests/scripts/test_check_protected_commit_authorization.py \
    platform_tests/scripts/test_command_registry_tracking.py \
    platform_tests/groundtruth_kb/cli/test_inventory_string_scan_cli.py -q
2 failed, 258 passed in 162.48s
```

### Pre-existing failures (not caused by this work)

Both failures were confirmed pre-existing by empirical bisection: the
`.gitignore` block was temporarily withdrawn, `git status` confirmed the file was
byte-identical to HEAD, and both tests still failed.

1. `test_check_protected_commit_authorization.py::test_prospective_audit_tree_is_index_complete_and_ignores_live_gate_tamper`
   — fails inside its own `tmp_path` fixture repository with
   `BridgeComplianceError: dispatchable bridge status ADVISORY requires line 2
   '::init gtkb pb' and line 3 '::open build'`. Unrelated to these files; no
   bridge artifact had been written when it was first observed.
2. `test_inventory_string_scan_cli.py::test_inventory_refresh_reports_compact_path_classes_and_blockers`
   — `path_class_counts` returns `opaque_container` where the test expects
   `generated`; a classifier/expectation drift entirely inside `tmp_path`.

Neither test reads the repository `.gitignore` or enumerates `scripts/`; both
construct their own project trees under `tmp_path`.

## Known limitations

1. **The policy file is not in place.** Until it lands, `dump`/`check` require an
   explicit `--policy` argument; the default path does not exist.
2. **Views are not projected.** Only tables and their indexes are. The `current_*`
   views are derived objects recreated by the platform's own schema
   initialization, which is already in git, so a real recovery is "initialize
   schema, load the projection". A standalone `restore` produces tables and
   indexes without views. Stated so the reviewer can judge whether that is
   sufficient.
3. **Unclassified tables fail closed.** A future migration that adds a table
   breaks `dump` until a policy row is added. This is intentional, but it does
   couple a schema change to a policy change. If SQLite internal tables ever
   appear (for example `sqlite_stat1` after `ANALYZE`), they would need a policy
   row too.
4. **Three excluded tables are not recoverable elsewhere** and are accepted as
   non-durable, unchanged from `-005`: `pipeline_events`,
   `sot_registry_transaction_journal`, `sot_artifact_revisions`.
5. **No pre-commit hook registration**, per `-001`'s explicit deferral.

## Owner Decisions / Input

- `DELIB-20260814-WI6218-DUMP-STRATEGY-AND-WI6220-BATCHED-APPROVALS` — the owner
  AUQ selecting the deterministic SQL dump strategy. Implemented as decided.
- `DELIB-20260814-PHASE2-PAUTH-BRIDGE-MUTATION-CLASS` and
  `DELIB-20260814-PHASE2-PAUTH-BRIDGE-CLASS-NON-B` — added the `bridge` mutation
  class to `PAUTH-GET-HEALTHY-PHASE-2-EXECUTION-20260814B`, which authorizes this
  report.
- Owner directive, 2026-08-14: the verifying Loyal Opposition commits the work,
  and commit success triggers the VERIFIED verdict. No `git add`, `git commit`
  or staging command was run by this session.
- **No new blocking owner decision is requested.** The policy-file placement
  blocker is surfaced for reviewer/owner disposition; the recommended path is a
  narrow `REVISED` proposal. If the owner prefers a different remedy, that
  becomes a decision at that point.
- Unchanged from `-005`, for owner awareness only: three excluded tables are
  accepted as non-durable, and the first committed projection remains gated on
  `WI-6138` reclamation.

## Prior Deliberations

- `bridge/gtkb-wi6218-membase-committable-dump-006.md` — the GO this report
  answers; its V1-V6 expectations are mapped above.
- `bridge/gtkb-wi6218-membase-committable-dump-005.md` — the approved scope.
- `bridge/gtkb-wi6218-membase-committable-dump-002.md` — the NO-GO whose four
  requirements (F1.1-F1.4) drive the verification table.
- `DELIB-20260814-MEMBASE-SIZE-TRIAGE` — the size triage the selection operates
  on.
- `WI-6138` (P0) — `develop` unpushable; gates the first committed projection.
- `WI-5431` (P1) — `.git` object-store regrowth; the growth-profile constraint
  the fixed-range chunking is designed against.
- WI-5100 — the precedent that added the `config/` carve-outs the blocker needs
  extended.

## Files Changed

| Path | Status |
|---|---|
| `scripts/membase_dump.py` | added |
| `platform_tests/scripts/test_membase_dump.py` | added (33 tests) |
| `.gitignore` | modified (+8 lines) |
| `config/membase-dump/dump-policy.toml` | **not written (blocked)** |

The working tree contains only these three paths from this thread. Nothing
staged, nothing committed.

Recommended commit type: `feat` — a new deterministic projection service plus its
tests and the tracking negation. A new capability surface, not a repair,
notwithstanding that the need was defect-driven.

## Risk / Rollback

Rollback is discarding the two new files and the `.gitignore` block. No
projection is committed, the database was opened read-only throughout and is
byte-unchanged, and no MemBase mutation occurred.

---

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.

---

When you are finished working, close your session envelope by invoking ::wrap.
