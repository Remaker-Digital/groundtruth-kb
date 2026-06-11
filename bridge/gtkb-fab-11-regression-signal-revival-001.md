NEW

bridge_kind: prime_proposal
Document: gtkb-fab-11-regression-signal-revival
Version: 001
Author: prime-builder (Claude Opus 4.8, harness B) — interactive owner session
Date: 2026-06-10

Project: PROJECT-FABLE-INVESTIGATION
Work Item: WI-4423
Project Authorization: PAUTH-FAB11-20260610

author_identity: prime-builder
author_harness_id: B
author_session_context_id: d2f32e6b-5441-45b3-b355-097a2507f5f7
author_model: claude-opus-4-8
author_model_version: 4.8
author_model_configuration: interactive owner session, ::init gtkb pb

target_paths: ["groundtruth.db", "scripts/fab11_assertion_corpus_remediation.py", "scripts/fab11_spec_derived_test_recorder.py", "scripts/fab11_pipeline_events_retention.py", "config/governance/pipeline-events-retention.toml", "config/agent-control/**", ".claude/settings.json", "CLAUDE.md", "platform_tests/scripts/**"]

KB mutation: YES. This cluster mutates `groundtruth.db` via the governed Python API — append-only re-versioning and retirement of stale-path assertion specs (HYG-029), spec-derived test-row recording (HYG-030), and owner-classified telemetry pruning of `pipeline_events` (HYG-014). `groundtruth.db` is therefore included in `target_paths`. No SQLite file is hand-edited; all writes flow through `KnowledgeDB`.

---

# FAB-11 — Regression-Signal Revival (Sequenced)

WI-4423 (FAB-11) of PROJECT-FABLE-INVESTIGATION. Findings: HYG-029, HYG-044, HYG-030, HYG-014.
Source advisory: `bridge/gtkb-fable-investigation-advisory-001.md`.

This cluster is **internally SEQUENCED**: corpus repair → sweep revival → tests-table recorder →
telemetry retention + VACUUM. The order is load-bearing — reviving the SessionStart sweep (HYG-044)
before repairing the assertion corpus (HYG-029) would immediately re-flood `pipeline_events` with
~1,374 false failures, which is the exact firehose that bloated the database (HYG-014).

## Summary

GT-KB's flagship regression-detection promise (GOV-08 / GOV-18 = SPEC-1662) is currently **inoperative**.
Four causally-linked findings:

- **HYG-029 (root cause):** 1,468 of 2,052 specs-with-runs fail their latest assertion, and ~1,374 of
  those fail solely on `File not found` for root-relative paths (`src/` 746, `admin/` 438, `widget/` 131,
  `tests/` 20, `docs-site/` 19, `docs/` 12, `branding/` 6) that were relocated under
  `applications/Agent_Red/` during the isolation cutover. This includes **233 status='verified' specs**
  failing right now — among them **8 verified protected behaviors** (PB-001, PB-010, PB-011, PB-020,
  PB-021, PB-022, PB-023, PB-030) and SPEC-1534 — and the categorizer reports `genuine_drift=0` because
  real drift is invisible under the noise floor.
- **HYG-044 (downstream):** the SessionStart assertion sweep (`.claude/hooks/assertion-check.py`) last
  fired 2026-05-13; the hook file exists but is **unregistered** in `settings.json` SessionStart, while
  CLAUDE.md still claims it "runs assertions automatically." No Deliberation Archive record authorized the
  removal — it was lost, not retired.
- **HYG-030 (parallel leg):** the MemBase `tests` table (1 of 9 managed artifact types) disconnected from
  live execution on 2026-04-29: `max(last_executed_at)`=Apr 29, 8,006 `pass` rows ≥6 weeks stale, 35
  verified specs with zero linked tests. Platform pytest runs daily but never records back to MemBase, so
  bridge "verified" verdicts cite files, not the governed artifact.
- **HYG-014 (consequence):** `pipeline_events` holds 3,325,082 rows, 99.93% of them `assertion_run`
  telemetry from the now-dead sweep — ~90% of the 1.32 GB `groundtruth.db` (vs ~47 MB for all other tables
  combined). `assertion_runs` has a retention policy; `pipeline_events` has none and duplicates every
  pruned assertion run forever.

## Specification Links

- `SPEC-1662` (GOV-18: Assertion Quality Standard) — the assertion-corpus and sweep findings (HYG-029,
  HYG-044) govern the assertion-quality contract this restores.
- `GOV-08` (Knowledge Database is the single source of truth) — governs the telemetry classification
  (prunable vs canonical) and the tests-table accuracy obligation.
- `GOV-12` (Work item creation triggers test creation) and `GOV-13` (Test artifacts assigned to a plan
  phase) — govern the spec-derived test-evidence recorder (HYG-030).
- `GOV-15` (Test fix gate) — the bulk stale-path assertion disposition runs as kb-batch waves under
  GOV-15 owner AUQ gating (50-item max per batch).
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` — the hybrid rewrite points assertions at
  `applications/Agent_Red/*` (the contract-correct relocation target); see Isolation Placement Compliance
  below. The proposal relocates no platform files and writes no out-of-root artifact.
- `DELIB-S312-DETERMINISTIC-SERVICES-PRINCIPLE` — the test-evidence recorder and the prune/VACUUM step are
  deterministic services, not per-session AI plumbing.
- `GOV-FILE-BRIDGE-AUTHORITY-001` — this proposal is filed under `bridge/` with a matching `NEW` INDEX
  entry; append-only.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` — all relevant specs cited here.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — verification derived below.
- `GOV-STANDING-BACKLOG-001` — WI-4423 is the governed backlog authority; the bulk GOV-15 assertion
  disposition stays backlog-visible (dry-run + per-wave owner AUQ; no silent bulk mutation).
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` / `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` /
  `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` — this cluster is artifact-lifecycle work (append-only spec
  re-versioning, spec retirement, telemetry reclassification); the lifecycle states it uses (verified,
  retired, deferred) follow these advisory governance specs.
- `config/governance/assertion-runs-retention.toml` — the existing sibling-table retention contract the
  new `pipeline-events-retention.toml` mirrors.

## Prior Deliberations

- `bridge/gtkb-fable-investigation-advisory-001.md` — chartering advisory (HYG-029/044/030/014).
- `DELIB-FABLE-GRILL-20260610-Q1..Q7` — project chartering decisions (verified-merge, waves, hybrid
  clusters, owner-AUQ-batched-at-cluster, repeatability architecture, advisory packaging, creation timing).
- `DELIB-FAB11-REMEDIATION-20260610` — this cluster's four owner dispositions (below).
- HYG-029's DA search found **no prior decision** on mass assertion-path migration; this is the first
  governed disposition of the stale-path corpus.

## Owner Decisions / Input

Collected via `AskUserQuestion` on 2026-06-10, persisted to `DELIB-FAB11-REMEDIATION-20260610`:

1. **HYG-029 = Hybrid (fix critical, retire rest).** Script-rewrite assertion paths to
   `applications/Agent_Red/*` via append-only re-versioning for **protected_behavior + verified specs
   only** (restores the must-always-pass safety signal immediately); bulk-retire or application-scope the
   remaining ~1,100 Agent-Red-era requirement specs. Full Agent-Red corpus migration is left to the
   isolation workstream.
2. **HYG-044 = Re-register AFTER corpus repair.** Sequence the SessionStart hook re-registration behind
   the HYG-029 fix so the revived sweep runs against a clean corpus (no 64%-failure noise floor, no
   re-flood of `pipeline_events`, no wasted startup latency). Re-registration MAY be scoped to
   protected_behavior + verified specs for latency. CLAUDE.md's claim is reconciled in the same slice.
3. **HYG-030 = Partial deterministic recorder.** Build a bounded recorder that records ONLY the
   spec-derived verification tests cited in bridge reports (the spec-to-test mapping verification already
   produces) back into the `tests` table — keeping the spec-test-implementation triad alive for governed
   work without mirroring the full pytest suite. Preserves the managed artifact type rather than
   abandoning it.
4. **HYG-014 = Archive-then-prune + VACUUM.** Classify `assertion_run` `pipeline_events` as prunable
   telemetry (NOT canonical append-only record) via the DELIB above; export rows older than N days to a
   compressed archive (off the live DB) FIRST, then prune, add `pipeline-events-retention.toml` mirroring
   the `assertion_runs` pattern, and VACUUM. The two root DB snapshots are reclaimed under **FAB-04**, not
   here; FAB-11 owns the live-DB prune + VACUUM.

## Requirement Sufficiency

**Existing requirements sufficient.** The dispositions are fixed by `DELIB-FAB11-REMEDIATION-20260610`;
the governing specifications (`SPEC-1662`, `GOV-08`, `GOV-12`, `GOV-13`, `GOV-15`) already constrain the
assertion-quality, source-of-truth, test-governance, and test-fix-gate surfaces. No new or revised
requirement is needed before implementation. One question is deferred to implementation, not to a new
requirement: the exact `N`-day retention horizon for `pipeline-events-retention.toml`, which the
implementation slice fixes with before/after evidence within the owner-approved archive-then-prune policy.

## Scope and Boundaries

In scope: the four sequenced slices below. Out of scope and explicitly excluded: the full Agent-Red spec
corpus migration to an application-scoped MemBase (isolation workstream); the two root DB snapshots
(`groundtruth.db.corrupt-S311*`, `groundtruth.db.pre-backfill*` — FAB-04 storage reclamation); a full
pytest-suite recorder (the owner chose the bounded spec-derived recorder); and any deploy/push. This
proposal **absorbs and supersedes** the existing-WI overlap the advisory lists for FAB-11: the
`WORKLIST-ARCHITECTURE-IMPROVEMENT-P2-STALE-ASSERTIONS` work item (single-spec design-pivot staleness —
HYG-029 supplies the aggregate root cause and ~1,374-spec quantification) and the per-spec test-coverage
cluster in the 3178–3224 range (per-spec gaps — HYG-030 shows the recording pipeline itself died, the
upstream cause those gaps accumulate under). Those overlaps are folded into WI-4423; they are described
here, not re-filed.

## Proposed Implementation

**Slice 1 — HYG-029 assertion-corpus hybrid repair (FIRST).**
`scripts/fab11_assertion_corpus_remediation.py`: a deterministic, dry-run-first script keyed on the
`File not found: <path>` classification (the failure detail already names the missing path; the
prefix-map `src|admin|widget|tests|docs-site|docs|branding` → `applications/Agent_Red/...` is mechanical
and verified against live file existence). For each affected spec: if `type='protected_behavior'` OR
`status='verified'`, emit a new spec version whose assertion path is rewritten to the
`applications/Agent_Red/*` location (preserving coverage); otherwise emit a new version marking the
assertion retired / application-scoped. Runs as kb-batch waves under GOV-15 owner AUQ (≤50 items/batch).
Re-run `scripts/assertion_categorize.py` afterward to expose the residual ~93 genuine failures.

**Slice 2 — HYG-044 sweep re-registration (AFTER Slice 1).**
Re-register `.claude/hooks/assertion-check.py` on SessionStart in `.claude/settings.json` and the tracked
template under `config/agent-control/**` (the in-root SoT for the settings template, since `.claude/` is
gitignored), optionally scoped to `protected_behavior + verified` specs for startup latency. Reconcile
the CLAUDE.md "Knowledge Database Access" sentence to match actual behavior (narrative-artifact approval
packet at implementation time per the gate). Gated strictly behind Slice 1 verification so the revived
sweep runs against a clean corpus.

**Slice 3 — HYG-030 spec-derived test-evidence recorder.**
`scripts/fab11_spec_derived_test_recorder.py`: a deterministic recorder that, from a bridge
implementation report's spec-to-test mapping, records/updates the cited verification tests in the MemBase
`tests` table (`last_result`, `last_executed_at`, `spec_id`, `test_file`), idempotently. Bounded to
bridge-cited spec-derived tests — not the full pytest suite. Restores the spec-test-implementation triad
for governed platform work under GOV-12/GOV-13.

**Slice 4 — HYG-014 telemetry retention + VACUUM (LAST).**
`config/governance/pipeline-events-retention.toml` mirroring the `assertion_runs` retention pattern;
`scripts/fab11_pipeline_events_retention.py`: take a pre-operation DB snapshot (coordinate with FAB-03
backup), export `assertion_run` `pipeline_events` older than the configured horizon to a compressed
gitignored/Drive-excluded archive (in-root by default; a truly out-of-root archive would require the
project-root-boundary sandbox-output exception and is the owner's option at implementation time), DELETE
the archived rows through the governed path, then VACUUM. Emits before/after row + byte evidence. Adds a
doctor freshness/size check so the table cannot silently re-bloat if the sweep is revived.

## Isolation Placement Compliance

`ADR-ISOLATION-APPLICATION-PLACEMENT-001`: FAB-11 is isolation-**positive**. The Slice-1 hybrid rewrite
repoints protected_behavior + verified Agent-Red assertions at `applications/Agent_Red/*` — exactly where
Agent Red files correctly live per the isolation contract — and retires/application-scopes the remaining
Agent-Red-era requirement specs out of the platform regression corpus. It relocates no platform file,
creates no out-of-root artifact (this bridge file is under `E:\GT-KB\bridge\`; the telemetry archive
defaults to an in-root gitignored location), and reduces, not increases, Agent-Red residue in the
platform DB.

## Spec-Derived Verification Plan

| Spec / requirement | Derived test |
|---|---|
| `SPEC-1662` + `GOV-08` (HYG-029 corpus) | test: after Slice 1, every protected_behavior + verified Agent-Red spec's assertion resolves against an existing `applications/Agent_Red/*` path (no `File not found`); retired specs carry a new retired/app-scoped version (append-only, no row DELETE); the 8 named protected behaviors PASS; categorizer re-run reports a sharply reduced failure count exposing the residual genuine failures |
| `SPEC-1662` (HYG-044 sweep) | test: `assertion-check.py` is registered in the SessionStart array of both `.claude/settings.json` and the tracked `config/agent-control/**` template; a simulated SessionStart fires it; the registration is absent until Slice 1 verification (sequencing assertion) |
| `GOV-12` + `GOV-13` + `DELIB-S312` (HYG-030 recorder) | test: given a bridge report spec-to-test mapping, the recorder writes/updates the cited `tests` rows with `last_result`/`last_executed_at`/`spec_id`; idempotent on re-run; rows omit non-cited pytest tests |
| `GOV-08` (HYG-014 telemetry) | test: the prune archives `assertion_run` rows older than the horizon to a compressed archive before deletion; non-`assertion_run` `pipeline_events` are preserved; VACUUM reduces DB file size; before/after row+byte evidence emitted; the doctor size/freshness check FAILs on simulated re-bloat |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | `pytest platform_tests/scripts/...` for the three new scripts + `ruff check` AND `ruff format --check` on all changed Python |

## Acceptance Criteria

1. **Slice 1:** stale-path assertions dispositioned per the hybrid policy via GOV-15 kb-batch waves; the
   8 protected behaviors + the 233 verified specs no longer fail on `File not found`; categorizer exposes
   the residual genuine-failure set; all dispositions are append-only spec versions (zero hard DELETEs of
   spec rows).
2. **Slice 2:** the SessionStart assertion sweep is re-registered (settings + tracked template), fires at
   SessionStart, and is sequenced strictly after Slice-1 verification; CLAUDE.md accurately describes the
   behavior (with narrative packet).
3. **Slice 3:** the spec-derived test recorder records bridge-cited verification tests into MemBase
   idempotently; a sample bridge mapping produces accurate `tests` rows.
4. **Slice 4:** `pipeline-events-retention.toml` exists; the archive-then-prune+VACUUM script reclaims the
   bulk of the DB (target on the order of ~150 MB) with before/after evidence and a pre-op snapshot; a
   doctor check guards against silent re-bloat.
5. All new tests pass; `ruff check` and `ruff format --check` clean on every changed Python file.

## Bridge Protocol Compliance

Filed at `bridge/gtkb-fab-11-regression-signal-revival-001.md` with a matching `NEW` entry at the top of
`bridge/INDEX.md`; append-only, no prior bridge version deleted or rewritten. `GOV-FILE-BRIDGE-AUTHORITY-001`
is honored — `bridge/INDEX.md` remains canonical workflow state and nothing implements until Loyal
Opposition records `GO` on this thread.

## Risk and Rollback

- **Risk — mis-rewrite of an assertion path:** the rewrite is keyed on the `File not found: <path>`
  classification (the missing path is named in the failure detail) and validated against live file
  existence before emitting a version; dry-run-first + GOV-15 owner AUQ waves (≤50/batch) bound blast
  radius. **Rollback:** spec re-versioning is append-only — re-version back to the prior assertion.
- **Risk — telemetry prune collides with append-only (GOV-08):** the owner has classified `assertion_run`
  `pipeline_events` as prunable telemetry (not canonical record) in `DELIB-FAB11-REMEDIATION-20260610`;
  archive-first preserves the history; a pre-op DB snapshot (FAB-03) guards the only irreversible step.
  **Rollback:** re-import from the archive; restore from the pre-op snapshot if VACUUM corrupts.
- **Risk — reviving the sweep re-floods telemetry:** mitigated by the hard sequencing (Slice 2 gated
  behind Slice 1) and the new retention policy (Slice 4) bounding future growth.
- **Risk — abandoning vs preserving the tests artifact type:** the owner chose the bounded recorder
  (preserve), so no managed artifact type is abandoned.

## Recommended Implementation Routing

**Opus/Codex-supervised, sequenced.** Slices 1 and 4 are KB-mutating and governance-heavy (GOV-15 waves,
owner-classified telemetry prune, irreversible VACUUM) — not cheap-model candidates. Slice 2 touches a
protected narrative (CLAUDE.md) requiring an approval packet. Slice 3 (the recorder) is the most
script-mechanical and could be cheap-model-drafted once GO'd, with Opus/Codex finalizing the KB-write
path. Implement strictly in slice order.

## Recommended Commit Type

`fix:` — repairs the dead regression signal (stale corpus, unregistered sweep, disconnected tests table,
unbounded telemetry), with `feat:`-class additions (the spec-derived test recorder, the
`pipeline-events-retention.toml` contract, and the doctor re-bloat guard).
