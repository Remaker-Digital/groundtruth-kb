NEW

bridge_kind: implementation_report
Document: gtkb-backlog-triage-and-hygiene-stage-0-analyzer
Version: 005
Author: prime-builder (Claude Opus 4.8, harness B) — interactive owner session
Date: 2026-06-11
Responds-To: bridge/gtkb-backlog-triage-and-hygiene-stage-0-analyzer-004.md

Project: PROJECT-GTKB-BACKLOG-TRIAGE-AND-HYGIENE-001
Work Item: WI-4442
Project Authorization: PAUTH-PROJECT-GTKB-BACKLOG-TRIAGE-AND-HYGIENE-001-BACKLOG-TRIAGE-AND-HYGIENE-BOUNDED-IMPLEMENTATION-AUTHORIZATION

author_identity: prime-builder
author_harness_id: B
author_session_context_id: 0c0caa91-3f63-41d1-b4c6-960f9b137180
author_model: claude-opus-4-8
author_model_version: 4.8
author_model_configuration: interactive owner session, ::init gtkb pb

target_paths: ["scripts/benchmarks/backlog_triage.py", "scripts/benchmarks/cli.py", "platform_tests/scripts/test_backlog_triage_benchmark.py"]

No KB mutation: Stage 0 implementation adds a read-only benchmark module, registers it in the benchmarks CLI, and adds a pytest. The only writes are to `.gtkb-state/benchmarks/<run_id>/` (regenerable evidence). No `work_items`, `projects`, or `specifications` row was mutated; `groundtruth.db` was read with a read-only SQLite URI.

---

# Stage 0 — Post-Implementation Report (Backlog Triage Analyzer)

Implements the GO'd `-003` proposal (Codex GO at `-004`) for Stage 0 of `PROJECT-GTKB-BACKLOG-TRIAGE-AND-HYGIENE-001` (WI-4442; owner decision `DELIB-20261667`). Implementation-start packet `sha256:26f3f715d8d273fbb4f534e623aa86f17440e330c61b32a7a9f3584c62036f24` was minted from the `-004` GO against the bounded PAUTH (mutation classes `source_addition` / `test_addition`). The PAUTH was advanced to v2 to include WI-4442 (per `DCL-WORK-ITEM-MUST-BELONG-TO-APPROVED-PROJECT-001`).

## Files Changed

| File | Change | Lines |
|---|---|---|
| `scripts/benchmarks/backlog_triage.py` | **new** — read-only backlog classification benchmark | ~315 |
| `scripts/benchmarks/cli.py` | **modified** — registered `backlog_triage` in `BENCHMARK_MODULES` (one entry) | +1 |
| `platform_tests/scripts/test_backlog_triage_benchmark.py` | **new** — 12-test suite | ~300 |

## What Was Implemented

A `backlog_triage` benchmark conforming to the Slice-2 benchmark-suite convention (`run(window_start, window_end, project_root) -> BenchmarkResult`; outputs via `write_run_outputs` to `.gtkb-state/benchmarks/<run_id>/run.json` + `summary.md`). It reads `current_work_items` (latest-version view) and `current_project_work_item_memberships` through a read-only SQLite URI (`file:...?mode=ro`), classifies every open work item by hard signals, partitions platform vs Agent-Red scope, and assigns a conservative disposition label. Per Codex `-004` implementation note 1, `dimensions` carries only aggregate scalars (readable markdown) and the full per-item signal vectors are written to a companion `backlog_triage_items.json` in the same run directory (`dimensions.items_file` points to it).

Codex `-004` implementation notes honored: (1) per-item vectors kept out of the markdown table → companion file; (2) read-only SQLite URI used; (3) regression test asserts every `BENCHMARK_MODULES` entry stays importable with a `run()` after registration.

## Classifier-Quality Refinement (GOV-18 / SPEC-1662) — please verify knowingly

Running the analyzer against the **live** corpus exposed a defect that the synthetic unit tests could not: the GO'd proposal listed `source_spec_id` as a spec-linkage signal, but the advisory-backlog-router stamps `source_spec_id='GOV-STANDING-BACKLOG-001'` on **every** item it creates — confirmed **748/748** router items, 0 with genuine `related_spec_ids_at_creation`. Counting `source_spec_id` made `signal_bearing` = **1006/1031** with **0 retire candidates** — a rubber-stamp classifier, which the proposal's own cited governing spec **GOV-18 (SPEC-1662, meaningful/non-rubber-stamp assertions)** forbids.

**Resolution:** `spec_linked` now uses only `related_spec_ids_at_creation` (genuine per-item links). The boilerplate `source_spec_id` is preserved as the informational `has_source_spec_id` field in each per-item vector (auditable, but not a signal). This is a refinement *toward* the proposal's cited GOV-18 requirement, not away from the design; it is called out here so verification accepts it deliberately. A new test (`test_boilerplate_source_spec_id_is_not_a_signal`) locks the behavior in. Post-refinement `signal_bearing` = **198**, with **744** router-noise retire candidates surfaced.

## Specification Links

_Carried forward from the -003 proposal._

- `GOV-STANDING-BACKLOG-001` — backlog governance authority being measured.
- `SPEC-AUTO-BACKLOG-FOR-IMPLEMENTATION-BEARING-SPECS-001` — governs the router population classified here.
- `SPEC-1662` (GOV-18) — meaningful, deterministic, non-rubber-stamp classification (see refinement above).
- `GOV-08` — read-only over `groundtruth.db`; no canonical mutation.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` — all changes in-root.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` / `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` / `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` — durable-artifact evidence.
- `GOV-FILE-BRIDGE-AUTHORITY-001` — filed under `bridge/` with a matching INDEX entry.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` / `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — linkage + spec-derived verification below.

## Prior Deliberations

- `DELIB-20261667` — owner project charter (5 decisions + 7 stages); this report closes Stage 0.
- `bridge/gtkb-self-diagnostic-leak-closure-slice-2-benchmark-suite-009.md` (VERIFIED) — the benchmark-suite convention reused here.
- `bridge/gtkb-self-diagnostic-leak-closure-slice-1-advisory-router-009.md` (VERIFIED) — created the advisory-router whose boilerplate `source_spec_id` stamp the refinement above accounts for.

## Spec-to-Test Mapping

| Spec / requirement | Test(s) | Result |
|---|---|---|
| `SPEC-1662` (GOV-18) meaningful/deterministic | `test_router_and_signal_classification`, `test_boilerplate_source_spec_id_is_not_a_signal`, `test_determinism` | PASS |
| `SPEC-AUTO-BACKLOG-FOR-IMPLEMENTATION-BEARING-SPECS-001` router attribution | `test_router_and_signal_classification`, `test_boilerplate_source_spec_id_is_not_a_signal` | PASS |
| `GOV-STANDING-BACKLOG-001` open-backlog definition + duplicates | `test_open_filter_excludes_terminal`, `test_duplicate_group_resolution` | PASS |
| D1 platform vs Agent Red partition | `test_scope_partition_platform_vs_agent_red` | PASS |
| `GOV-08` read-only / no canonical mutation | `test_read_only_row_counts_unchanged`, `test_no_mutation_ast`, `test_missing_db_is_safe` | PASS |
| Output contract (`run.json`/`summary.md` + companion) | `test_standard_output_contract` | PASS |
| Codex note 3 (siblings still import) | `test_all_benchmark_modules_importable_with_run` | PASS |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` (lint + format) | ruff commands below | PASS |

## Commands Executed and Observed Results

```
python -m pytest platform_tests/scripts/test_backlog_triage_benchmark.py -o addopts="" -q
# 12 passed, 1 warning in 1.00s  (the warning is an env-level unknown config option: asyncio_mode)

python -m ruff check scripts/benchmarks/backlog_triage.py scripts/benchmarks/cli.py platform_tests/scripts/test_backlog_triage_benchmark.py
# All checks passed!

python -m ruff format --check <same three files>
# 3 files already formatted

python -m scripts.benchmarks.cli run --benchmark backlog_triage
# run_id 20260611-082526 -> .gtkb-state/benchmarks/20260611-082526/{run.json,summary.md,backlog_triage_items.json}
```

Note on the `-o addopts=""` override: the repo `pyproject.toml` sets a default `--timeout=30` addopt that requires the `pytest-timeout` plugin, which is absent in the resolved interpreter; the override clears the default addopts so the suite runs. No test behavior is affected.

## Live Baseline Produced (Stage 0 deliverable)

`.gtkb-state/benchmarks/20260611-082526/` (read-only census of the live backlog):

- `total_rows_latest_version` = 3214; `total_open` = **1031**; `total_nonopen` = 2183 (`resolved` 1954, `retired` 101, `wont_fix` 61, `verified` 59, `not_a_defect` 7, `deferred` 1).
- `router_generated` = **748**; `signal_bearing` = **198**; `unapproved` = 985.
- `by_label` = **{keep_signal: 198, retire_candidate_unapproved_noise: 744, review: 89}**.
- `by_scope` = {platform: 984, agent_red: **47**} (the D1 partition for Stage 5).
- `project_name_inconsistent` = **111** (the membership-vs-field divergence Stage 1 repairs).
- `duplicate_items` = 0 (no exact content-hash duplicates remain among open items).

This manifest is the evidence base each later stage's owner batch-approval AUQ will cite. Nothing in the backlog was mutated.

## Acceptance Criteria Check

1. Module exists, exposes `run(...)`, registered in `cli.py` — ✅.
2. Run writes `run.json` + `summary.md` via the shared writer; per-item vectors + partitions persisted (companion file, pointer in `dimensions`) — ✅.
3. Read-only: no-mutation AST test + row-count-unchanged test pass — ✅.
4. Deterministic: two identical runs produce identical output — ✅ (`test_determinism`).
5. All tests pass; `ruff check` and `ruff format --check` clean — ✅ (12 passed; both gates clean).

## Isolation Placement Compliance

`ADR-ISOLATION-APPLICATION-PLACEMENT-001`: all changes in-root under `E:\GT-KB\` (`scripts/benchmarks/`, `platform_tests/scripts/`, regenerable output under `.gtkb-state/benchmarks/`, this report under `bridge/`). No `applications/` subtree touched; no out-of-root artifact written.

## Recommended Commit Type

`feat:` — net-new read-only benchmark module + CLI registration + 12-test suite (a new measurement capability), no behavior change to existing benchmarks. Working tree is left uncommitted pending VERIFIED + owner sweep-commit authorization.

## Owner Decisions / Input

Authorized by `DELIB-20261667` (owner `/grill-me-for-clarification` interview, 2026-06-11): the owner approved the project shape and "Approve & file Stage 0." Stage 0 is read-only and required no separate batch-AUQ (that gate applies only to later mutating stages per the bounded PAUTH). No new owner decision is requested by this report.
