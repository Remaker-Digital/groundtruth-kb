REVISED

bridge_kind: prime_proposal
Document: gtkb-fab-13-retention-policy-umbrella
Version: 003
Author: prime-builder (Claude Opus 4.8, harness B) — interactive owner session
Date: 2026-06-11
Responds-To: bridge/gtkb-fab-13-retention-policy-umbrella-002.md

Project: PROJECT-FABLE-INVESTIGATION
Work Item: WI-4425
Project Authorization: PAUTH-FAB13-20260610

author_identity: prime-builder
author_harness_id: B
author_session_context_id: 9660f4cb-1b84-410e-a024-febdabe7c541
author_model: claude-opus-4-8
author_model_version: 4.8
author_model_configuration: interactive owner session, ::init gtkb pb

target_paths: ["groundtruth.db", ".claude/hooks/owner-decision-tracker.py", ".claude/hooks/*.json", "memory/pending-owner-decisions.md", "memory/archive/**", "scripts/cross_harness_bridge_trigger.py", "groundtruth-kb/src/groundtruth_kb/session/envelope.py", "config/governance/runtime-evidence-retention.toml", ".gtkb-state/**", ".codex/gtkb-hooks/**", ".driveignore", ".gitignore", "platform_tests/scripts/**"]

KB mutation: YES (narrow). The only MemBase write is the DA-harvest of resolved owner decisions before ledger rotation (Decision 1) — deliberation inserts via the existing harvest mechanism, never a delete of MemBase or DA records. `groundtruth.db` is therefore included in `target_paths`. All other changes are hook/source/config/runtime-file lifecycle, not KB writes.

---

# FAB-13 — Retention-Policy Umbrella for Runtime Stores

WI-4425 (FAB-13) of PROJECT-FABLE-INVESTIGATION. Findings: HYG-021, HYG-055, HYG-056 (plus absorbed
sub-findings: envelope.py full git-status capture; .gtkb-state ~3.6 GB no-GC; .gtkb-state conflict-copy
locks/claims). Source advisory: `bridge/gtkb-fable-investigation-advisory-001.md`.

Common root cause: fire-and-forget runtime evidence with no lifecycle, amplified by the Google-Drive-synced
repo volume. One retention-policy decision per store, governed under one umbrella.

## Revision Scope

REVISED-003 responds to the single NO-GO finding in
`bridge/gtkb-fab-13-retention-policy-umbrella-002.md`:

- **F1 (runtime deletion/prune surfaces not in target_paths):** added the concrete runtime
  deletion/rotation perimeters to `target_paths` — `.gtkb-state/**` (dispatch-runs, JSONL diagnostics,
  duplicated uv-caches, aged pytest-tmp dirs, conflict-copy locks/claims), `.codex/gtkb-hooks/**` (the
  Codex hook-state conflict copies), and `.claude/hooks/*.json` (the Claude hook-state JSON the
  `.driveignore` extension and the duplicate purge touch). The implementation can now create, rotate,
  prune, or delete only within these reviewable perimeters.
- The Required-Revision item 2 (separate code/config changes from one-time destructive cleanup) is
  satisfied by the new `## Deletion Perimeter` verification split below: the implementation report must
  prove the destructive cleanup stayed inside the enumerated perimeters and touched no canonical state.

No other substantive change; the three retention decisions, horizons, and the DA-harvest-before-archive
invariant are unchanged from -001. Full Drive-unsync remains an owner infrastructure recommendation only,
not a bridge mutation.

## Summary

- **HYG-021 (decision ledger):** memory/pending-owner-decisions.md is 996 KB / 13,791 lines holding ZERO
  pending decisions — a monotonic resolved-AUQ append log with no rotation, parsed on every hook Stop event
  and re-surfaced into context (the 4282 SessionStart re-surfacing item). The Deliberation Archive already
  exists to hold resolved evidence.
- **HYG-055 (dispatch evidence):** .gtkb-state/bridge-poller/dispatch-runs is 1.49 GB / 6,591 files (never
  pruned); trigger-diagnostic.jsonl is 86 MB / 107K records (no rotation); dispatch-failures keeps only ONE
  1 MB rollover (overwrite) — so the June dispatch-storm failure reasons are already destroyed while 86 MB
  of low-value diagnostics are kept forever. Retention is inverted relative to evidentiary value. Absorbed:
  envelope.py embeds full 160 KB git-status dumps; .gtkb-state is 356 dirs / 40K files / ~3.6 GB with no GC.
- **HYG-056 (Drive-sync):** the repo lives on a Google-Drive-synced volume that generates ' (N)' duplicate
  files in-repo (62 live duplicates incl. SQLite wal/shm at root, 10 copies of Codex hook state, conflict-copy
  locks in .gtkb-state). .driveignore covers only .git/ + SQLite. Two prior corruption incidents (S311 SQLite,
  May git-object loss) trace to this sync interference.

## Specification Links

- `GOV-08` (Knowledge Database is the single source of truth) — the resolved-decision DA-harvest before
  rotation keeps the canonical record in the DA, not a 1 MB markdown append log (HYG-021).
- `GOV-SOURCE-OF-TRUTH-FRESHNESS-001` — the ' (N)' conflict copies of hot state/lock files are exactly the
  divergent-alias / stale-state read class this spec targets (HYG-056).
- `DCL-SMART-POLLER-AUTO-TRIGGER-001` — the dispatch audit-trail invariants the rotation must preserve
  (failures keep enough rollovers for the storm window) (HYG-055).
- `SPEC-DA-HARVEST-INCLUSION` — governs the DA harvest of resolved decisions prior to rotation (HYG-021).
- `GOV-STANDING-BACKLOG-001` — WI-4425 is the governed backlog authority; absorbs the overlapping item.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` — the retention/GC/purge routines operate only on in-root
  runtime stores; see Isolation Placement Compliance below.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` / `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` /
  `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` — durable-artifact lifecycle for the resolved-decision harvest.
- `GOV-FILE-BRIDGE-AUTHORITY-001` — filed under `bridge/` with a matching `REVISED` INDEX entry; append-only.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` — all relevant specs cited here.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — verification derived below.

## Isolation Placement Compliance

`ADR-ISOLATION-APPLICATION-PLACEMENT-001`: FAB-13 operates only on **in-root** runtime stores under
`E:\GT-KB` (`.gtkb-state/`, `.claude/hooks/`, `.codex/gtkb-hooks/`, `memory/`, `.driveignore`,
`.gitignore`) and writes no out-of-root artifact (this bridge file is under `E:\GT-KB\bridge\`; dated
archives land under `E:\GT-KB\memory\archive\`). It relocates no subtree and creates no application
artifact; the full Drive-unsync of `E:\GT-KB` is explicitly an owner infrastructure recommendation, not a
bridge mutation.

## Prior Deliberations

- `bridge/gtkb-fable-investigation-advisory-001.md` — chartering advisory (HYG-021/055/056).
- `DELIB-FABLE-GRILL-20260610-Q1..Q7` — project chartering decisions.
- `DELIB-FAB13-REMEDIATION-20260610` — this cluster's three owner dispositions (below).
- `DELIB-S312-DETERMINISTIC-SERVICES-PRINCIPLE` — the retention/GC routines are deterministic services.
- _The full Drive-unsync of E:\GT-KB is an owner infrastructure decision surfaced here, not a bridge action._

## Owner Decisions / Input

Collected via `AskUserQuestion` on 2026-06-10, persisted to `DELIB-FAB13-REMEDIATION-20260610`:

1. **HYG-021 = Rotate >30 days to dated archive + DA harvest.** Extend owner-decision-tracker.py with
   size/age rotation moving resolved entries older than 30 days to memory/archive/pending-owner-decisions-YYYYMM.md,
   DA-harvesting each before rotation, plus a one-time backfill rotation of the current 13.7K lines.
2. **HYG-055 = Cap + rotate.** 14-day / 200 MB cap on dispatch-runs; 10 MB × 5 rollovers for BOTH
   trigger-diagnostic.jsonl and dispatch-failures.jsonl (failures retain ≥30 days of storm forensics);
   truncate the envelope git-status capture; .gtkb-state GC for duplicated uv-caches / pytest-tmp dirs.
   Deletion of these regenerable runtime artifacts is owner-approved (exempting the protected-removal rule).
3. **HYG-056 = Purge dups + extend .driveignore.** One-time purge of the 62 ' (N)' duplicates (gitignore
   already covers the families) + extend .driveignore to .gtkb-state/, .claude/hooks/*.json +
   .codex/gtkb-hooks/ state, and *.lock. The full Drive-unsync of E:\GT-KB is surfaced to the owner as the
   deeper root-cause infrastructure action (origin + DB-snapshot backup), outside the bridge's scope.

## Requirement Sufficiency

**Existing requirements sufficient.** The dispositions are fixed by `DELIB-FAB13-REMEDIATION-20260610`; the
governing specifications (`GOV-08`, `GOV-SOURCE-OF-TRUTH-FRESHNESS-001`, `DCL-SMART-POLLER-AUTO-TRIGGER-001`,
`SPEC-DA-HARVEST-INCLUSION`) already constrain the source-of-truth, dispatch-audit, and DA-harvest surfaces.
No new requirement is needed. The retention horizons (30 days / 14 days / 200 MB / 10 MB × 5) are owner-fixed
above and recorded as the implementation defaults in `runtime-evidence-retention.toml`.

## Scope and Boundaries

In scope: the three retention decisions + the absorbed sub-findings (envelope git-status truncation,
.gtkb-state GC, conflict-copy lock purge). Out of scope and explicitly excluded: the full Drive-unsync of
E:\GT-KB (owner infrastructure action, surfaced not implemented); any delete of canonical MemBase or DA
records (only regenerable runtime artifacts are pruned); deploy/push. This proposal absorbs the advisory's
overlapping item for FAB-13 (the SessionStart resolved-entry re-surfacing item, the 4282 reference), folding
it into WI-4425's scope and describing it here rather than re-filing; backlog-state reconciliation is a
post-VERIFIED operational step.

## Proposed Implementation

**Area 1 — HYG-021 decision-ledger rotation.** Extend `.claude/hooks/owner-decision-tracker.py` with a
size/age rotation: on Stop, if the resolved section exceeds a threshold, DA-harvest resolved entries older
than 30 days (via the existing harvest path) then move them to `memory/archive/pending-owner-decisions-YYYYMM.md`
and truncate the live file to pending + a recent window. Ship a one-time backfill rotation of the current
13.7K lines (harvest-then-archive).

**Area 2 — HYG-055 dispatch-evidence retention.** Add `config/governance/runtime-evidence-retention.toml`
(the owner-fixed horizons). In `scripts/cross_harness_bridge_trigger.py`: cap dispatch-runs (under
`.gtkb-state/bridge-poller/`) at 14 days / 200 MB (age+size prune); replace the single-rollover
`_rotate_dispatch_failures_if_needed` with N-rollover (10 MB × 5) retention; add 10 MB × 5 rotation to
`_emit_trigger_diagnostic`. In `groundtruth-kb/src/groundtruth_kb/session/envelope.py`, truncate the
`_git_status` capture to a bounded summary (count + first N lines). Add a `.gtkb-state` GC routine for the
duplicated uv-caches and aged pytest-tmp dirs. All deletions are of regenerable runtime artifacts within
`.gtkb-state/**` (owner-approved here).

**Area 3 — HYG-056 Drive-sync hygiene.** One-time purge of the 62 ' (N)' duplicate files (gitignore already
covers the families, no history risk) — these live under `.gtkb-state/**`, `.codex/gtkb-hooks/**`, and the
repo-root SQLite sidecars; extend `.driveignore` with `.gtkb-state/`, `.claude/hooks/*.json` +
`.codex/gtkb-hooks/` state, and `*.lock`; generalize the `.gitignore` ' (N)' duplicate pattern to a `* (N).*`
family. Document the full-unsync recommendation (origin + DB-snapshot backup) with the S311 + git-object
incident evidence for the owner's separate infrastructure decision.

## Deletion Perimeter

Per NO-GO Required-Revision item 2, the one-time destructive cleanup is separated from the code/config
changes and bounded to these reviewable perimeters (all in `target_paths`):

- `.gtkb-state/**` — dispatch-runs age/size prune, JSONL rotation rollovers, duplicated uv-caches and aged
  pytest-tmp GC, conflict-copy lock/claim purge.
- `.codex/gtkb-hooks/**` — Codex hook-state ' (N)' conflict-copy purge.
- `.claude/hooks/*.json` — Claude hook-state JSON conflict-copy purge (and the `.driveignore` coverage).
- repo-root SQLite sidecar ' (N)' duplicates (siblings of `groundtruth.db`, already in `target_paths`).

The implementation report must enumerate exactly which paths were deleted and prove no canonical state
(MemBase rows, DA records, live hook config, the live `groundtruth.db`) was removed — only regenerable
runtime artifacts and ' (N)' duplicates.

## Spec-Derived Verification Plan

| Spec / requirement | Derived test |
|---|---|
| `GOV-08` + `SPEC-DA-HARVEST-INCLUSION` (HYG-021) | test: rotation DA-harvests a resolved entry (DA row exists) BEFORE moving it to the dated archive; the live ledger shrinks to pending + recent window; no resolved entry is lost (archive ∪ DA = original) |
| `DCL-SMART-POLLER-AUTO-TRIGGER-001` (HYG-055, code/config) | test: dispatch-failures retains 5 rollovers spanning ≥30 days (not a single overwrite); trigger-diagnostic rotates at 10 MB × 5; dispatch-runs pruned by 14d/200MB cap; envelope git-status is a bounded summary |
| `GOV-SOURCE-OF-TRUTH-FRESHNESS-001` (HYG-056, destructive cleanup) | test: no ' (N)' duplicate matches the `* (N).*` family outside .git/.venv after purge; .driveignore covers .gtkb-state/, hook-state JSON, and *.lock; the deletion perimeter stayed inside `.gtkb-state/**` + `.codex/gtkb-hooks/**` + `.claude/hooks/*.json` + root SQLite sidecars |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | `pytest platform_tests/scripts/...` for the rotation/retention/purge routines + `ruff check` AND `ruff format --check` on changed Python |

## Acceptance Criteria

1. **Area 1:** the decision ledger stays bounded (pending + recent window); resolved history is DA-harvested
   then archived to dated sidecars; the one-time backfill rotation completes with no record loss.
2. **Area 2:** runtime-evidence-retention.toml exists; dispatch-runs capped (14d/200MB); both JSONL logs
   rotate (10 MB × 5); dispatch-failures retains ≥30 days; envelope git-status is bounded; .gtkb-state GC runs.
3. **Area 3:** the 62 duplicates are purged within the enumerated deletion perimeter; .driveignore covers
   .gtkb-state/hook-state/locks; the .gitignore ' (N)' family is generalized; the full-unsync recommendation
   is documented for the owner.
4. The destructive cleanup touched no canonical state (deletion-perimeter evidence in the report); all new
   tests pass; `ruff check` and `ruff format --check` clean on every changed Python file.

## Bridge Protocol Compliance

Filed at `bridge/gtkb-fab-13-retention-policy-umbrella-003.md` with a matching `REVISED` line inserted at
the top of this thread's entry in `bridge/INDEX.md`; append-only, no prior bridge version deleted or
rewritten. The HYG-055 rotation PRESERVES the dispatch audit-trail invariants
(`DCL-SMART-POLLER-AUTO-TRIGGER-001`) by widening, not narrowing, the retained failure window.
`GOV-FILE-BRIDGE-AUTHORITY-001` is honored; nothing implements until Loyal Opposition records `GO`.

## Backlog Visibility

FAB-13 is WI-4425 under `GOV-STANDING-BACKLOG-001`; this REVISED performs no bulk backlog operation. The
absorbed SessionStart re-surfacing item is described as an inventory in Scope and Boundaries; its
backlog-state reconciliation is a post-VERIFIED operational step.

## Risk and Rollback

- **Risk — rotation loses a resolved decision:** harvest-to-DA happens BEFORE archive/truncate; a test
  asserts archive ∪ DA = original. **Rollback:** dated archives retain every rotated entry; restore by
  concatenation.
- **Risk — pruning deletes evidence still needed:** caps are owner-fixed to retain ≥30 days of failures and
  a 14-day run window; only regenerable artifacts within the deletion perimeter are deleted (owner-approved).
  **Rollback:** evidence regenerates on the next dispatch; nothing canonical is touched.
- **Risk — envelope git-status truncation loses forensic detail:** the bounded summary keeps the count +
  first N lines; the mass-modification signal is preserved as a count. **Rollback:** revert envelope.py.
- **Risk — .driveignore change misses a surface or the sync client ignores it:** the in-repo purge is
  independent of the sync client; the full-unsync recommendation is the durable fix surfaced to the owner.

## Recommended Implementation Routing

**Opus/Codex-supervised for Areas 1–2** (the owner-decision-tracker hook, the dispatch-trigger rotation
paths, and envelope.py are load-bearing). **Area 3 (purge + .driveignore/.gitignore)** is mechanical and
cheap-model-draftable once GO'd. Coordinate the dispatch-trigger edits (Area 2) with FAB-10/FAB-01 which
also touch `cross_harness_bridge_trigger.py`.

## Recommended Commit Type

`fix:` — repairs unbounded/inverted retention across three runtime stores, with `feat:`-class additions
(runtime-evidence-retention.toml, the rotation/GC routines, the generalized .driveignore/.gitignore family).
