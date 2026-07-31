REVISED
::init gtkb pb
::open build
author_identity: prime-builder/codex
author_harness_id: A
author_session_context_id: 019f9329-a174-7763-8f7e-29679f39e6bd
author_model: gpt-5.6
author_model_version: gpt-5.6
author_model_configuration: reasoning_effort=high; thread_source=codex-desktop
author_metadata_source: x-codex-turn-metadata


# GT-KB Bridge Corrected Implementation Report - gtkb-wi5589-da-tooling-canonical-inputs - 005

bridge_kind: implementation_report
Document: gtkb-wi5589-da-tooling-canonical-inputs
Version: 005
Responds to: bridge/gtkb-wi5589-da-tooling-canonical-inputs-004.md
Responds to GO: bridge/gtkb-wi5589-da-tooling-canonical-inputs-002.md
Approved proposal: bridge/gtkb-wi5589-da-tooling-canonical-inputs-001.md
Project Authorization: PAUTH-PROJECT-GTKB-OBSOLETE-REFERENCE-PURGE-WI-5589-DELIBERATION-TOOLING-2026-07-18
Project: PROJECT-GTKB-OBSOLETE-REFERENCE-PURGE
Work Item: WI-5589
Recommended commit type: refactor:


target_paths: ["scripts/backfill_lo_reports.py", "scripts/deliberation_health.py", "scripts/harvest_session_deliberations.py", "scripts/inventory_lo_bridge_history_backfill.py", "platform_tests/unit/test_lo_report_backfill.py", "platform_tests/scripts/test_deliberation_archive_spec2098_coverage.py", "platform_tests/scripts/test_harvest_session_thread_level.py", "platform_tests/scripts/test_harvest_loud_wrap.py", "platform_tests/scripts/test_inventory_lo_bridge_history_backfill.py"]

implementation_scope: source
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

## Revision Disposition

Version 004 independently confirmed every substantive implementation claim,
all 98 focused tests, both Ruff gates, the six-file diff scope, and the
specification mapping. Its sole finding was the non-strict Version metadata in
v003. This append-only v005 carries the same implementation evidence with the
strict `Version: 005` header and an exact `Responds to` link to v004. It does
not rewrite v003, modify source/test bytes, broaden target scope, or claim new
implementation work.

## Implementation Claim

Deliberation Archive backfill, health, harvest, and inventory tooling no longer
discover inputs by scanning the governance-retired Loyal Opposition insight dropbox
(`independent-progress-assessments/CODEX-INSIGHT-DROPBOX/INSIGHTS-*.md`). Canonical
Loyal Opposition findings reach the archive as `ADVISORY` status-bearing numbered
bridge entries, which the existing bridge collectors already discover.

Governance-visible behavior change: a bare `backfill_lo_reports.py` run no longer
silently resolves a retired non-canonical carrier; `--report-dir` is now required, so
historical import must be explicitly operator-directed. Health coverage no longer
re-derives an `lo_reports` candidate count from that carrier.

Historical `independent-progress-assessments/...` `source_ref` values in
already-archived rows remain queryable data and are still classified by
`classify_source_ref`; they are never re-resolved as live filesystem inputs
(`DCL-SUPERSEDED-SOT-LEAKAGE-001`).

The diff touches 6 of the 9 declared target paths - a reviewed subset, expressly
permitted by acceptance criterion 4. The three untouched targets
(`platform_tests/unit/test_lo_report_backfill.py`,
`platform_tests/scripts/test_deliberation_archive_spec2098_coverage.py`,
`platform_tests/scripts/test_harvest_loud_wrap.py`) required no change: they exercise
pure parsing, redaction, dedupe, and wrap behavior this slice deliberately preserves.
All three remain green.

## Changes By File

1. `scripts/harvest_session_deliberations.py`
   - `collect_lo_reports()` becomes a retired route returning `[]`. The function and
     its call site in the Phase 1 harvest loop are retained so the call graph and test
     surface are unimpaired (`GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001`).
   - Removed the now-unused `INSIGHT_DIR` module constant.

2. `scripts/deliberation_health.py`
   - Removed the `INSIGHT_DIR` constant and the `INSIGHTS-*.md` filesystem scan in
     `count_candidate_sources()`. `lo_reports` is reported as `0` rather than
     re-derived from a non-canonical carrier; canonical LO advisories are already
     counted by the bridge scan, so coverage is not double-counted.

3. `scripts/inventory_lo_bridge_history_backfill.py`
   - `iter_lo_reports()` becomes a retired route returning `[]`. Inventory now
     enumerates only canonical numbered bridge artifacts via `iter_bridge_files()`.
   - The `CODEX-INSIGHT-DROPBOX` branch in `classify_source_ref` is deliberately
     PRESERVED: it classifies historical `source_ref` strings on already-archived
     rows and is data classification, not live filesystem discovery.

4. `scripts/backfill_lo_reports.py`
   - `--report-dir` is now `required=True`, retiring the implicit default that pointed
     at the retired dropbox. Explicit operator-directed historical import still works.
   - `_make_source_ref()` is PRESERVED: it reproduces historical dedup keys for rows
     already in the archive.

5. `platform_tests/scripts/test_harvest_session_thread_level.py`
   - Three `TestFlagToggle` cases previously monkeypatched `hsd.INSIGHT_DIR` at an
     empty temp dir purely as scan isolation. That scaffolding is removed; the
     substantive thread-level compression assertions are unchanged.

6. `platform_tests/scripts/test_inventory_lo_bridge_history_backfill.py`
   - `test_exclusion_redaction_survivor` was re-anchored from a dropbox fixture onto a
     canonical numbered bridge fixture (`bridge/gtkb-survivor-advisory-001.md`). The
     `SPEC-DA-HARVEST-EXCLUSION` redaction-survivor obligation and its assertions are
     retained in full - coverage moved to the canonical carrier, not dropped. The
     survivor token is still assembled at runtime so no credential-shaped literal
     appears in test source (scanner-safe-writer / SPEC-0058).

## Specification Links

- `DCL-CANONICAL-CARRIER-NONAUTHORITY-001`
- `GOV-FILE-BRIDGE-AUTHORITY-001`
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001`
- `SPEC-AUQ-POLICY-ENGINE-001`
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001`
- `GOV-STANDING-BACKLOG-001`
- `ADR-CODEX-HOOK-PARITY-FALLBACK-001`
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`
- `DCL-SUPERSEDED-SOT-LEAKAGE-001`
- `GOV-SOURCE-OF-TRUTH-FRESHNESS-001`
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001`
- `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001`
- `DCL-PROJECT-AUTHORIZATION-ENVELOPE-001`
- `DCL-PROJECT-AUTHORIZATION-OPERATION-TIME-ENFORCEMENT-001`
- `DCL-DISPATCHER-ACTIVITY-ENVELOPE-AUTHORITY-001`
- `DCL-DISPATCHER-ORDINARY-WORKER-BLACK-BOX-BOUNDARY-001`
- `DCL-ACTIVITY-DISPOSITION-PROFILE-001`
- `GOV-WORK-TREE-HYGIENE-001`
- `GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001`
- `ADR-0001`
- `SPEC-2098`
- `SPEC-DA-HARVEST-INCLUSION`
- `SPEC-DA-HARVEST-EXCLUSION`
- `SPEC-DA-RETROACTIVE-SWEEP`
- `SPEC-DA-THREAD-COMPRESSION`
- `SPEC-DA-COVERAGE-METRIC`
- `SPEC-DA-MECHANICAL-ENFORCE`

## Spec-to-Test Mapping

| Specification | Test / verification | Result |
| --- | --- | --- |
| `DCL-CANONICAL-CARRIER-NONAUTHORITY-001` | `platform_tests/scripts/test_inventory_lo_bridge_history_backfill.py` (13 tests) plus `test_harvest_session_thread_level.py` (11 tests) | PASS - discovery restricted to canonical bridge artifacts |
| `DCL-SUPERSEDED-SOT-LEAKAGE-001` | `test_inventory_lo_bridge_history_backfill.py` classification tests over historical `source_ref` values | PASS - historical refs classified, never resolved |
| `SPEC-DA-HARVEST-EXCLUSION` | `test_inventory_lo_bridge_history_backfill.py::test_exclusion_redaction_survivor` (re-anchored to canonical carrier) | PASS - `redaction_survivor` exclusion reason preserved |
| `SPEC-DA-HARVEST-INCLUSION` | `test_inventory_lo_bridge_history_backfill.py::test_eligible_classification_default` plus already-harvested path tests | PASS |
| `SPEC-DA-THREAD-COMPRESSION` | `test_harvest_session_thread_level.py::TestFlagToggle` (3 updated cases) | PASS - `bridge/<slug>-*.md` compression identity intact |
| `SPEC-DA-COVERAGE-METRIC` | `test_deliberation_archive_spec2098_coverage.py` (8 tests) | PASS - unchanged, still green |
| `SPEC-DA-RETROACTIVE-SWEEP` | `test_inventory_lo_bridge_history_backfill.py` deterministic inventory/replay tests | PASS - inventory deterministic and idempotent |
| `SPEC-DA-MECHANICAL-ENFORCE` | `test_inventory_lo_bridge_history_backfill.py` non-mutating inventory tests | PASS - inventory remains non-mutating |
| `SPEC-2098` | `test_deliberation_archive_spec2098_coverage.py` | PASS |
| `GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001` | Full focused suite: 98 passed / 0 failed (pre-change baseline 94 passed / 4 failed) | PASS - no test count lost, no capability impaired |
| `ADR-0001` | `platform_tests/unit/test_lo_report_backfill.py` (53 tests) | PASS - MemBase / notepad / DA tiers still distinct |
| `GOV-WORK-TREE-HYGIENE-001` | `git status --short` and `git diff --check` over the nine targets | PASS - exactly 6 modified, whitespace clean |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | All targets in-root under `E:\GT-KB` | PASS |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | This mapping plus the executed commands below | PASS - every linked DA specification has executed coverage |
| Python quality gates | `ruff check` and `ruff format --check` on all nine targets | PASS - exit 0 and "9 files already formatted" |

## Commands Executed

```powershell
groundtruth-kb/.venv/Scripts/python.exe -m pytest platform_tests/unit/test_lo_report_backfill.py platform_tests/scripts/test_deliberation_archive_spec2098_coverage.py platform_tests/scripts/test_harvest_session_thread_level.py platform_tests/scripts/test_harvest_loud_wrap.py platform_tests/scripts/test_inventory_lo_bridge_history_backfill.py -q --tb=line
groundtruth-kb/.venv/Scripts/ruff.exe check <nine targets>
groundtruth-kb/.venv/Scripts/ruff.exe format --check <nine targets>
git status --short -- <nine targets>
git diff --stat -- <nine targets>
git diff --check -- <changed targets>
python scripts/bridge_claim_cli.py claim gtkb-wi5589-da-tooling-canonical-inputs
python scripts/implementation_authorization.py begin --bridge-id gtkb-wi5589-da-tooling-canonical-inputs
```

Observed results:

- Pre-change baseline: `94 passed, 4 failed`. The 4 failures were exactly the
  dropbox-coupled assertions this slice retires.
- Post-change: `98 passed, 2 warnings`. Both warnings are pre-existing and
  unrelated (unknown `asyncio_mode` pytest config option; a chromadb
  `asyncio.iscoroutinefunction` DeprecationWarning).
- `ruff check`: `All checks passed!` (exit 0).
- `ruff format --check`: `9 files already formatted` (exit 0).
- `git diff --check`: exit 0, no output.
- `git diff --stat` over the nine targets: 6 files changed, 58 insertions(+),
  50 deletions(-).

## Acceptance Criteria Check

1. **Backfill, health, harvest, and inventory tools accept only canonical MemBase,
   Deliberation Archive, and numbered bridge discovery inputs.** MET - all four
   filesystem discovery routes into the retired dropbox are removed or made
   explicitly operator-supplied.
2. **Historical source references remain queryable data but are never opened,
   imported, copied, or resolved as live paths.** MET - `classify_source_ref`'s
   dropbox branch and `_make_source_ref` are deliberately preserved as data-only
   surfaces; no code path resolves them to the filesystem.
3. **Dedupe, source taxonomy, relation links, redaction, thread compression, coverage
   metrics, and non-mutating inventory tests all pass.** MET - 98/98 focused tests
   green.
4. **Final diff contains exactly the nine declared paths or a reviewed subset, with
   both ruff gates and focused pytest green.** MET - 6-of-9 reviewed subset, both
   ruff gates exit 0, pytest green.

## Concurrency / Work-Tree Disclosure

This session implemented alongside a concurrently active counterpart harness session
working in the same worktree. Disclosures for the reviewer:

- Work-intent claim `gtkb-wi5589-da-tooling-canonical-inputs` was acquired before any
  drafting or mutation (`claim_kind: go_implementation`, session `932aad8d`), and was
  still held and unexpired at report-filing time.
- The implementation-start authorization packet was created from the live latest-`GO`
  and returned `allowed: true` with all nine targets classified (4 `source`,
  5 `test`).
- All nine targets were verified clean immediately before implementation and were
  modified by no other session: `git status --short` over the nine paths shows exactly
  the 6 files this slice changed.
- The wider worktree carries a large volume of unrelated uncommitted changes from the
  concurrent session (445 dirty paths excluded by the report helper, versus 6 changed
  files attributed here). None were staged, committed, reverted, or otherwise
  disturbed by this work.
- `HEAD` was unchanged (`7c033d11c`) across the implementation window.
- No commit was created by this session. Terminal `VERIFIED` finalization is reserved
  for an independent Loyal Opposition session per the Mandatory VERIFIED
  Commit-Finalization Gate; this author session cannot verify its own work.

## Owner Decisions / Input

- `PAUTH-PROJECT-GTKB-OBSOLETE-REFERENCE-PURGE-WI-5589-DELIBERATION-TOOLING-2026-07-18`
  is the active project authorization covering `WI-5589`, backed by owner decision
  `DELIB-20260717-CANONICAL-ARTIFACT-REFERENCE-BOUNDARY`.
- Owner direction in this session authorized draining PB-actionable bridge work
  restricted to threads whose target paths do not overlap the concurrent session's
  uncommitted work; this thread satisfied that constraint.
- No new AskUserQuestion-gated decision class (approval, waiver, priority choice,
  formal artifact approval, requirement clarification, destructive action,
  deployment) applies to this source/test slice.

## Prior Deliberations

- `DELIB-20260717-CANONICAL-ARTIFACT-REFERENCE-BOUNDARY` - owner direction that
  canonical artifacts may depend only on canonical evidence carriers. This slice is a
  direct application.
- `DELIB-0621` - prior Deliberation Archive review covering dedupe, source taxonomy,
  relation links, redaction, and harvest-test obligations; all preserved here.
- `DELIB-20260717-DISPATCHER-CONFIGURATION-TROUBLESHOOTER-HOLD` - preserved; this
  slice does not inspect or mutate dispatcher configuration, TAFE, or runtime state.

## Risk / Rollback

Risk is low and bounded. The change removes input routes into a directory that
governance already retired, so the retired paths were dead or actively undesirable at
runtime. The primary residual risk is a caller that still expects
`backfill_lo_reports.py` to run bare with its old implicit default; that invocation
now fails fast with an explicit argparse error rather than silently scanning a
retired carrier, which is the intended fail-closed behavior.

Rollback is a revert of the six changed files under separate authority. Bridge files
and project authorization records are append-only and are not deleted by rollback.

## Recommended Commit Type

`refactor:` - this retires non-canonical input routes and re-anchors their tests
without adding a capability or changing archive semantics. The proposal suggested
`feat:`; the realized diff is a route retirement with preserved behavior (58
insertions / 50 deletions across 6 files, no new public surface), so `refactor:`
matches the diff more honestly. The reviewer may direct a different type.

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
