REVISED

bridge_kind: prime_proposal
Document: gtkb-fab-17-da-chroma-read-path
Version: 003
Author: prime-builder (Claude Opus 4.8, harness B) — interactive owner session
Date: 2026-06-11
Responds-To: bridge/gtkb-fab-17-da-chroma-read-path-002.md

Project: PROJECT-FABLE-INVESTIGATION
Work Item: WI-4429
Project Authorization: PAUTH-FAB17-20260610

author_identity: prime-builder
author_harness_id: B
author_session_context_id: 9660f4cb-1b84-410e-a024-febdabe7c541
author_model: claude-opus-4-8
author_model_version: 4.8
author_model_configuration: interactive owner session, ::init gtkb pb

target_paths: ["groundtruth-kb/src/groundtruth_kb/db.py", "scripts/benchmarks/**", ".groundtruth-chroma/**", "config/governance/chroma-read-path.toml", "platform_tests/scripts/**"]

No KB mutation: all FAB-17 source/config changes (the DA search read path, the benchmark CLI) plus the Chroma dedup operate on the DERIVED ChromaDB semantic index, never the canonical `groundtruth.db` DA store. The Chroma index is regenerable from the DA; consolidating duplicate copies does not mutate canonical DA records. `groundtruth.db` is intentionally NOT in target_paths.

---

# FAB-17 — DA/Chroma Read-Path Reliability

WI-4429 (FAB-17) of PROJECT-FABLE-INVESTIGATION. Findings: HYG-048 (deliberation-search crash/hang) +
demoted benchmark-CLI repair + chroma triplication. Source advisory:
`bridge/gtkb-fable-investigation-advisory-001.md`.

Common root cause: the ChromaDB read path is not contention-tolerant — an unguarded probe crashes the
mandated deliberation search, the benchmark suite hangs on the same store, and a triplicated index widens
the concurrency surface.

## Revision Scope

REVISED-003 responds to the single NO-GO finding (F1) and the benchmarks-path question in
`bridge/gtkb-fab-17-da-chroma-read-path-002.md`:

- **F1 (Chroma dedup/removal paths not in target_paths):** chose Codex option 1 — added `.groundtruth-chroma/**`
  to `target_paths` as the explicit Chroma deduplication/consolidation perimeter. Area 3 (the triplication
  resolution) stays in FAB-17 because it is part of the read-path reliability story (a triplicated index
  widens the same concurrency surface HYG-048 hardens). PAUTH-FAB17 already authorizes
  `chroma_index_deduplication`. The verification plan now requires proving the dedup touched only the derived
  `.groundtruth-chroma` index and left canonical `groundtruth.db` / DA records unmutated.
- **Benchmarks path clarification:** the `-001` `target_paths` listed
  `groundtruth-kb/src/groundtruth_kb/benchmarks/**`, which does NOT exist (the applicability preflight's
  missing-parent-dir warning). The canonical benchmark package lives under `scripts/benchmarks/` (`__init__.py`,
  `cli.py`, `common.py`, the metric modules). REVISED-003 replaces the phantom `src/.../benchmarks/**` entry
  with `scripts/benchmarks/**`, which covers the benchmark-CLI repair (Area 2) and any sibling benchmark
  module that shares the chroma timeout discipline.

No other substantive change; the HYG-048 search-reliability fix, the timeout/retry degradation, and the owner
disposition are unchanged from -001.

## Summary

- **HYG-048 (search reliability):** `db.search_deliberations` documents a SQLite-LIKE fallback, but its
  first chroma call (`collection.count()` at `db.py:6295`) sits OUTSIDE the try block, so chroma contention
  crashes the mandatory pre-proposal deliberation search (exit 255) instead of degrading. Live this session
  it also hung >3 min twice; the benchmark suite (same chroma store) hung >45 min. The project's normal mode
  is multi-session concurrency.
- **Benchmark CLI (demoted):** `python scripts/benchmarks/cli.py` crashes under its documented invocation
  and the module-form hangs on ChromaDB.
- **Chroma triplication (demoted):** multiple copies of the `.groundtruth-chroma` store widen the
  concurrent-contention surface and waste storage.

## Specification Links

- `SPEC-2098` (Deliberation Archive) — the DA read path whose mandated search must degrade, not crash
  (HYG-048).
- `GOV-08` (Knowledge Database is the single source of truth) — the chroma index is a derived semantic
  index, not the canonical DA store; the fallback to SQLite LIKE keeps the canonical store authoritative.
- `GOV-SOURCE-OF-TRUTH-FRESHNESS-001` — resolving the chroma triplication to one canonical index aligns with
  the no-divergent-aliases discipline.
- `SPEC-DA-DOCTOR-CHECK` — DA read-surface health; the reliability fix keeps the mandated search usable.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` — all FAB-17 changes are in-root; see Isolation Placement
  Compliance below.
- `GOV-STANDING-BACKLOG-001` — WI-4429 is the governed backlog authority; absorbs the overlapping item.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` / `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` /
  `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` — durable-artifact lifecycle for the read-path change.
- `GOV-FILE-BRIDGE-AUTHORITY-001` — filed under `bridge/` with a matching `REVISED` INDEX entry; append-only.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` — all relevant specs cited here.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — verification derived below.

## Prior Deliberations

- `bridge/gtkb-fable-investigation-advisory-001.md` — chartering advisory (HYG-048 + demoted items).
- `DELIB-FABLE-GRILL-20260610-Q1..Q7` — project chartering decisions.
- `DELIB-FAB17-REMEDIATION-20260610` — this cluster's owner fix-scope + determined fixes (below).
- _The DELIB-capture exit-255 friction noted across this campaign (decision-capture committing the SQLite
  row but throwing on the post-commit chroma index) is the same contention class FAB-17 hardens against._

## Owner Decisions / Input

Collected via `AskUserQuestion` on 2026-06-10, persisted to `DELIB-FAB17-REMEDIATION-20260610`:

1. **HYG-048 = Wrap count() + add timeout/retry.** Move the `count()` probe inside the try (restore the
   documented LIKE fallback on any chroma exception) AND add a bounded timeout/retry around the chroma query
   so multi-session contention degrades to text search (`search_method=text_match`) instead of hanging. Add a
   unit test mocking a raising / slow collection.
2. **Benchmark CLI** (determined fix): repair the CLI invocation path + apply the same chroma timeout
   discipline so the benchmark read path does not hang the suite.
3. **Chroma triplication** (determined fix): resolve to a single canonical chroma index.

## Requirement Sufficiency

**Existing requirements sufficient.** The disposition is fixed by `DELIB-FAB17-REMEDIATION-20260610`; the
governing specifications (`SPEC-2098`, `GOV-08`, `GOV-SOURCE-OF-TRUTH-FRESHNESS-001`, `SPEC-DA-DOCTOR-CHECK`)
already constrain the Deliberation Archive read path and the source-of-truth read discipline. No new
requirement is needed; the documented LIKE fallback is the existing contract being restored.

## Scope and Boundaries

In scope: the search-reliability fix + the benchmark CLI repair + the chroma triplication resolution (within
the `.groundtruth-chroma/**` perimeter). Out of scope and explicitly excluded: any change to the canonical DA
store schema or MemBase; a chroma re-index of historical content beyond deduplication; deploy/push. This
proposal absorbs the advisory's overlap for FAB-17 (the chroma/search item 3395) by describing it here.

## Proposed Implementation

**Area 1 — HYG-048 search reliability.** In `db.search_deliberations` (db.py): move the
`collection.count()` probe inside the try/except (or a dedicated try that returns to the SQLite-LIKE
fallback), and wrap the chroma query in a bounded timeout/retry; on any chroma exception or timeout, degrade
to text search with `search_method=text_match`. Add a unit test with a mock collection whose `count()`/query
raises or stalls, asserting the fallback path returns text-match results.

**Area 2 — benchmark CLI.** Repair `scripts/benchmarks/cli.py` (and the `scripts/benchmarks/__init__.py`
package entry) so the documented invocation runs; apply the same chroma timeout/degradation so a contended
store does not hang the benchmark suite.

**Area 3 — chroma triplication.** Add `config/governance/chroma-read-path.toml` declaring the single
canonical `.groundtruth-chroma` index path; consolidate/remove the duplicate copies WITHIN the
`.groundtruth-chroma/**` perimeter; ensure all read paths resolve to the one canonical index. The dedup
removes only derived index copies — never canonical `groundtruth.db` or DA records — and the index is
regenerable from the DA.

## Isolation Placement Compliance

`ADR-ISOLATION-APPLICATION-PLACEMENT-001`: all FAB-17 changes are in-root under `E:\GT-KB\` — the DA read
path in the in-root `groundtruth-kb/src/groundtruth_kb/` tree, the benchmark package under `scripts/benchmarks/`,
the derived Chroma index under `.groundtruth-chroma/`, the chroma read-path config under `config/governance/`,
tests under `platform_tests/`, and this bridge file under `E:\GT-KB\bridge\`. The cluster relocates no
application file, touches no `applications/` subtree, and writes no out-of-root artifact.

## Spec-Derived Verification Plan

| Spec / requirement | Derived test |
|---|---|
| `SPEC-2098` + `GOV-08` (HYG-048) | test: a mock chroma collection whose count()/query raises causes search_deliberations to return SQLite-LIKE results with search_method=text_match (no crash); a slow/stalled collection triggers the timeout → fallback (no multi-minute hang) |
| `SPEC-DA-DOCTOR-CHECK` (benchmark CLI) | test: the documented benchmark CLI invocation runs to completion (or degrades) without hanging on a contended chroma store |
| `GOV-SOURCE-OF-TRUTH-FRESHNESS-001` (chroma triplication) | test: only one canonical `.groundtruth-chroma` index path is referenced; no duplicate index copies remain on the read path; the dedup left canonical `groundtruth.db` / DA records unmutated (row counts unchanged) |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | `pytest platform_tests/scripts/...` + `ruff check` AND `ruff format --check` on changed Python |

## Acceptance Criteria

1. **Area 1:** `search_deliberations` degrades to text-match on chroma exception OR timeout (no crash, no
   multi-minute hang); the mock-collection unit test passes.
2. **Area 2:** the benchmark CLI runs under its documented invocation without hanging.
3. **Area 3:** a single canonical chroma index is used; duplicate copies are removed from the read path
   (within `.groundtruth-chroma/**`); canonical DA records are unchanged.
4. All new tests pass; `ruff check` and `ruff format --check` clean on every changed Python file.

## Bridge Protocol Compliance

Filed at `bridge/gtkb-fab-17-da-chroma-read-path-003.md` with a matching `REVISED` line inserted at the top
of `bridge/INDEX.md`; append-only. `GOV-FILE-BRIDGE-AUTHORITY-001` is honored; nothing implements until Loyal
Opposition records `GO`.

## Backlog Visibility

FAB-17 is WI-4429 under `GOV-STANDING-BACKLOG-001`; this REVISED performs no bulk backlog operation. The
absorbed chroma/search item (3395) is described as an inventory in Scope and Boundaries; its backlog-state
reconciliation is a post-VERIFIED operational step.

## Risk and Rollback

- **Risk — the timeout degrades a legitimate slow-but-succeeding chroma query to text search:** the timeout
  is bounded and only triggers under genuine contention; the text-match fallback is the documented behavior,
  not a quality regression for a mandated existence search. **Rollback:** revert the db.py change.
- **Risk — consolidating the chroma index loses a needed copy:** consolidation keeps the canonical index and
  removes only duplicates within `.groundtruth-chroma/**`; the index is regenerable from the DA. **Rollback:**
  re-index from the DA.
- **Risk — benchmark CLI repair changes benchmark output:** benchmarks are read-only measurement; the repair
  fixes invocation, not metric definitions. **Rollback:** revert the CLI change.

## Recommended Implementation Routing

**Opus/Codex for Area 1** (the DA read path is a mandated-gate dependency where a wrong fallback hides real
DA gaps); **cheap-model-draftable for Areas 2–3** (benchmark CLI repair + chroma dedup) once GO'd.

## Recommended Commit Type

`fix:` — repairs the DA search crash/hang, the benchmark CLI, and the chroma triplication; a small
`feat:`-class addition (the chroma read-path config + the timeout/retry guard).
