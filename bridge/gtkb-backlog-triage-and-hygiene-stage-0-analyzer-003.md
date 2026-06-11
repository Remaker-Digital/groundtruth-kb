REVISED

bridge_kind: prime_proposal
Document: gtkb-backlog-triage-and-hygiene-stage-0-analyzer
Version: 003
Author: prime-builder (Claude Opus 4.8, harness B) — interactive owner session
Date: 2026-06-11
Responds-To: bridge/gtkb-backlog-triage-and-hygiene-stage-0-analyzer-002.md

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

No KB mutation: Stage 0 is a READ-ONLY analyzer/benchmark. It adds a benchmark module, registers it in the benchmarks CLI, and adds a pytest. It writes only to `.gtkb-state/benchmarks/<run_id>/` (regenerable evidence). It performs NO `work_items`, `projects`, or `specifications` mutation; `groundtruth.db` is intentionally NOT in target_paths. The destructive/reordering backlog operations are deferred to later stages, each gated by its own bridge GO + owner batch-approval AskUserQuestion per the bounded authorization PAUTH (rowid 190).

---

# Stage 0 — Backlog Triage Analyzer + Criteria Baseline (read-only) (REVISED)

Stage 0 of `PROJECT-GTKB-BACKLOG-TRIAGE-AND-HYGIENE-001` (WI-4442). This is the first of seven reviewable stages chartered by owner decision `DELIB-20261667` (the `/grill-me-for-clarification` interview, 2026-06-11). Stage 0 is deliberately non-mutating: it builds the deterministic evidence base that every later (mutating) stage cites in its owner batch-approval packet.

## Revision Scope

Addresses the finding in the `-002` NO-GO:

- **FINDING-P2-001 (Acceptance asks for benchmark-named output files that the cited shared writer does not produce):** The previous proposal stated that the benchmark would emit `.gtkb-state/benchmarks/<run_id>/backlog_triage.json|md`. However, the shared writer helper (`scripts/benchmarks/common.py:write_run_outputs`) only produces `run.json` and `summary.md`.
  **Fix:** Revised the output-file contract to conform with the existing benchmark-suite convention: `python -m scripts.benchmarks.cli run --benchmark backlog_triage` writes to `.gtkb-state/benchmarks/<run_id>/run.json` and `summary.md`. The per-item signal vector will be stored under the `backlog_triage` result key in `run.json`. Replaced all occurrences of the custom named files with this standard output path contract in the Summary, Proposed Implementation, Spec-Derived Verification Plan, and Acceptance Criteria.

The read-only and no-KB-mutation boundaries are fully preserved.

## Summary

At session start the GT-KB backlog held **1,032 open work items** (raw `gt backlog list --json`, deduped to latest version per id) against a startup-reported "155 open / 162 active" — a count divergence that is itself a hygiene defect. Read-only analysis found the backlog dominated by machine-generated content: **748 items created by `advisory-backlog-router/1.0`**, **982 of 1,032 `approval_state=unapproved`**, **896 `origin=hygiene`**, **790 `component=backlog`**, **840 with no `project_name`** (the row field is unpopulated even though a membership-table grouping exists). Structural defects: **10 doubled-prefix `PROJECT-PROJECT-*` projects** and prefix-variant project splits (e.g. `GTKB-RELIABILITY-FIXES` vs `PROJECT-GTKB-RELIABILITY-FIXES`). The genuinely owner/prime/bridge-authored slice is a minority (~171 owner-directive-sourced, 90 bridge-linked, 43 spec-linked).

Stage 0 makes those findings **reproducible, deterministic, and re-runnable** by landing a `backlog_triage` benchmark module that snapshots the backlog and classifies every open work item by hard signals. The output manifest (stored in `run.json` and `summary.md` under the benchmark output run directory) is the evidence each later stage's batch-approval AUQ cites, and the same module doubles as a permanent benchmark so the doctor/benchmark surface can flag re-accumulation (consumed by Stage 6's regression guard).

## Specification Links

- `GOV-STANDING-BACKLOG-001` — the standing-backlog governance authority; Stage 0 measures the backlog this spec governs (linked in PAUTH).
- `SPEC-AUTO-BACKLOG-FOR-IMPLEMENTATION-BEARING-SPECS-001` — governs the auto-backlog/advisory-router population whose corpus Stage 0 classifies; the `advisory-backlog-router/1.0` signal is the central classifier (linked in PAUTH).
- `SPEC-1662` (GOV-18, Assertion/measurement quality) — the benchmark's classifiers must be meaningful, deterministic, and non-rubber-stamp; Stage 0 is a measurement surface.
- `GOV-08` (Knowledge Database is the single source of truth) — Stage 0 is read-only over `groundtruth.db`; it writes no canonical row and only emits regenerable `.gtkb-state/benchmarks/` evidence.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` — all Stage 0 changes are in-root; see Isolation Placement Compliance below.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` / `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` / `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` — the triage program is durable-artifact-oriented; the analyzer's manifest is the lifecycle evidence later stages act on.
- `GOV-FILE-BRIDGE-AUTHORITY-001` — filed under `bridge/` with a matching `NEW` INDEX entry; append-only.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` — all relevant specs cited here.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — verification derived below.

## Prior Deliberations

- `DELIB-20261667` — the owner decision that chartered this project (5 decisions + 7-stage shape) from the `/grill-me-for-clarification` interview, 2026-06-11. This Stage 0 proposal directly implements that decision's Stage 0.
- `DELIB-S312-DETERMINISTIC-SERVICES-PRINCIPLE` — repetitive AI plumbing (here: re-deriving backlog classification by hand each session) is a defect to engineer into a deterministic service; Stage 0 is that service.
- `bridge/gtkb-self-diagnostic-leak-closure-slice-2-benchmark-suite-009.md` (VERIFIED) — established the `scripts/benchmarks/*.py` module + `cli.py` + `.gtkb-state/benchmarks/<run_id>/` convention this stage follows; the `linkage heat map` / `advisory latency` benchmarks are siblings.
- `bridge/gtkb-self-diagnostic-leak-closure-slice-1-advisory-router-009.md` (VERIFIED) — created the `advisory-backlog-router/1.0` source whose corpus Stage 0 classifies (and Stage 3 later constrains).
- _No prior deliberation proposes a backlog-classification benchmark; this is the first._

## Owner Decisions / Input

Collected via `AskUserQuestion` during the `/grill-me-for-clarification` interview on 2026-06-11, persisted to `DELIB-20261667`:

1. **D1 — Triage scope = GT-KB platform + a separate labeled Agent Red stage.** Stage 0's analyzer reports platform and Agent-Red-scope items as distinct partitions so the later AR lane (Stage 5) is cleanly separable.
2. **D2 — Retirement model = staged batch-approval.** Stage 0 mutates nothing; it produces the candidate-evidence manifest that every later stage's owner batch-approval AUQ cites.
3. **D3 — Ranking axis = composite (articulation + recency + strategic), priority-preserving.** Stage 0 computes the articulation-length, recency, signal, and approval-state inputs the Stage 4 composite consumes; it never reorders.
4. **D4 — Advisory-router corpus (~748) = signal-classify + bulk-dispose.** Stage 0 IS the classifier: it labels each router item by content-hash duplication, bridge/spec/owner linkage, approval_state, and age.
5. **D5 — Include a stop-the-leak stage.** Stage 0's source-attribution counts (router vs human) quantify the leak Stage 3 will constrain.
6. **Plan approval — "Approve & file Stage 0."** Owner authorized persisting the decision, creating the project + bounded authorization, and filing this Stage 0 proposal.

## Requirement Sufficiency

**Existing requirements sufficient.** The Stage 0 scope is fixed by `DELIB-20261667`; the governing specifications (`GOV-STANDING-BACKLOG-001`, `SPEC-AUTO-BACKLOG-FOR-IMPLEMENTATION-BEARING-SPECS-001`, `SPEC-1662`, `GOV-08`) already constrain the backlog-authority, auto-backlog, measurement-quality, and source-of-truth surfaces. No new requirement is needed; Stage 0 is a read-only measurement deriving from existing governance.

## Backlog Visibility

`GOV-STANDING-BACKLOG-001`: Stage 0 performs **no bulk backlog operation** — it writes nothing to `work_items`, `projects`, or `project memberships`. It only reads the backlog and emits a regenerable classification manifest under `.gtkb-state/benchmarks/`. All disposition/retirement/reorder operations are deferred to later stages, each gated by its own bridge GO and owner batch-approval AUQ per the bounded authorization PAUTH (rowid 190), which explicitly forbids `work_item_retirement_without_stage_batch_auq`, `work_item_reorder_without_stage_batch_auq`, and `project_retirement_without_stage_batch_auq`.

## Scope and Boundaries

In scope: a new `scripts/benchmarks/backlog_triage.py` benchmark module exposing the standard `run(window_start, window_end, project_root) -> BenchmarkResult` entry point (per the Slice-2 benchmark convention); its registration in `scripts/benchmarks/cli.py`; and a pytest at `platform_tests/scripts/test_backlog_triage_benchmark.py`. Out of scope and explicitly excluded: ANY mutation of `work_items`, `projects`, memberships, or specifications; the structural project reconciliation (Stage 1); the router-corpus disposition (Stage 2); the router source change (Stage 3); the re-ranking (Stage 4); the Agent Red lane (Stage 5); the closeout/regression-guard (Stage 6); deploy/push.

## Proposed Implementation

**`scripts/benchmarks/backlog_triage.py` (new).** A read-only benchmark module that:

1. Loads the backlog via the canonical read path (the same source `gt backlog list --json` uses), deduplicates to latest-version-per-id, and partitions into open vs non-open by `resolution_status`.
2. Classifies each open item by deterministic hard signals: `changed_by == advisory-backlog-router/*` (router-generated); a content-hash over normalized `title+description` (duplicate detection); presence of `related_bridge_threads`, `related_spec_ids_at_creation`/`source_spec_id`, `source_owner_directive` (signal-bearing); `approval_state`; `origin`; `component`; age in days from `changed_at`; articulation length (`len(description)+len(acceptance_summary)`); and `project_name`-vs-membership-table consistency.
3. Partitions platform-scope vs Agent-Red-scope items (D1) by project membership / id prefix.
4. Emits a `BenchmarkResult` snapshot (JSON) plus a markdown summary to `.gtkb-state/benchmarks/<run_id>/run.json` and `summary.md` via the shared `write_run_outputs` helper, with the per-item signal vector stored under the `backlog_triage` result key in `run.json`. Each open item carries its computed signal vector so later stages can filter deterministically.

**`scripts/benchmarks/cli.py` (modify).** Register `backlog_triage` in the benchmark registry so `run`/`report`/`compare` subcommands surface it alongside the existing benchmarks. No behavior change to existing benchmarks.

**`platform_tests/scripts/test_backlog_triage_benchmark.py` (new).** Tests (see Spec-Derived Verification Plan) covering each classifier branch on a synthetic in-memory fixture, the dedup-to-latest-version logic, the platform/AR partition, the standard run/summary output file structure, and an AST-level assertion that the module performs no mutation (no `insert_*`/`update_*`/`UPDATE`/`DELETE`/`commit` write calls against the DB; read-only connection).

## Isolation Placement Compliance

`ADR-ISOLATION-APPLICATION-PLACEMENT-001`: all Stage 0 changes are in-root under `E:\GT-KB\` — the benchmark module and CLI under `scripts/benchmarks/`, the test under `platform_tests/scripts/`, the regenerable output under `.gtkb-state/benchmarks/`, and this bridge file under `E:\GT-KB\bridge\`. The stage relocates no application file, touches no `applications/` subtree, and writes no out-of-root artifact.

## Spec-Derived Verification Plan

| Spec / requirement | Derived test |
|---|---|
| `SPEC-1662` (GOV-18) + `GOV-STANDING-BACKLOG-001` (deterministic, meaningful classification) | test: on a synthetic fixture of known items, each signal classifier (router-generated, content-hash duplicate, bridge/spec/owner-linked, approval_state, age, articulation length, project_name-vs-membership) returns the asserted label; running twice on identical input yields identical output values (determinism) |
| `SPEC-AUTO-BACKLOG-FOR-IMPLEMENTATION-BEARING-SPECS-001` (router-corpus attribution) | test: items whose `changed_by` matches `advisory-backlog-router/*` are counted in the router partition; signal-bearing router items (bridge/spec/owner-linked) are NOT mis-labeled as no-signal noise |
| `GOV-08` (read-only; no canonical mutation) | test: AST scan of `backlog_triage.py` asserts no `insert_*`/`update_*`/`resolve_*`/`commit`/`UPDATE`/`DELETE` write path; the DB connection is opened read-only; the run leaves `work_items`/`projects` row counts unchanged; outputs are written via the shared benchmark writer to `.gtkb-state/benchmarks/<run_id>/run.json` and `summary.md` |
| D1 (platform vs Agent Red partition) | test: AR-scope items partition separately from platform items; the manifest reports the two partitions distinctly |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | `python -m pytest platform_tests/scripts/test_backlog_triage_benchmark.py -q`; `ruff check` AND `ruff format --check` on every changed Python file |

## Acceptance Criteria

1. `scripts/benchmarks/backlog_triage.py` exists, exposes the standard `run(...)` entry point, and is registered in `scripts/benchmarks/cli.py`.
2. Running the benchmark writes to `.gtkb-state/benchmarks/<run_id>/run.json` and `summary.md` via the shared benchmark-suite writer, storing the per-item signal vector and platform/AR partitions under the `backlog_triage` result key in `run.json`.
3. The module is read-only: the no-mutation AST test and the row-count-unchanged test pass.
4. Classification is deterministic: two runs on identical input produce identical output.
5. All new tests pass; `ruff check` and `ruff format --check` are clean on every changed Python file.

## Bridge Protocol Compliance

Filed at `bridge/gtkb-backlog-triage-and-hygiene-stage-0-analyzer-003.md` with a matching `REVISED` entry directly below the Document header line at the top of `bridge/INDEX.md`; append-only. `GOV-FILE-BRIDGE-AUTHORITY-001` is honored; nothing implements until Loyal Opposition records `GO`. At implementation time the implementation-start packet will be minted from the GO against the bounded authorization PAUTH (rowid 190) under the `source_addition` / `test_addition` mutation classes.

## Risk and Rollback

- **Risk — the analyzer accidentally mutates the backlog:** the AST no-mutation test and the read-only connection make mutation structurally impossible; the row-count-unchanged test is a backstop. **Rollback:** delete the benchmark module + test (additive, no state touched).
- **Risk — a classifier mislabels a signal-bearing item as noise, biasing a later bulk-retire:** Stage 0 only *labels*; no retirement happens here. The labels are reviewed as evidence in Stage 2's owner batch-approval AUQ before any disposition. The duplicate/no-signal classifiers are conservative (a missing signal never forces retirement; it only flags a candidate). **Rollback:** refine the classifier; nothing in the backlog was changed.
- **Risk — the benchmark CLI registration breaks a sibling benchmark:** the change is additive registration only; the existing-benchmark tests guard against regression. **Rollback:** revert the one-line registration.

## Recommended Implementation Routing

**Claude/Codex (deterministic source + test).** Stage 0 is greenfield read-only source plus a pytest under an existing PAUTH with no protected-narrative or KB-mutation surface — cleanly draftable. The intellectual care is in the classifier definitions (meaningful, deterministic, conservative-on-retirement-candidacy per GOV-18), which are specified above and verified by the per-branch tests.

## Recommended Commit Type

`feat:` — net-new benchmark module + CLI registration + test suite (a new measurement capability), with no behavior change to existing surfaces.
