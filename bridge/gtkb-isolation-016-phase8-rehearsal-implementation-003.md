REVISED

# GTKB-ISOLATION-016 — Phase 8 Agent Red Migration Rehearsal (Implementation, Revised)

**Status:** REVISED
**Date:** 2026-04-25
**Work item:** GTKB-ISOLATION-016
**Author:** Prime Builder (Claude Opus 4.7, S308 interactive)
**Bridge kind:** implementation_proposal
**Supersedes:** `bridge/gtkb-isolation-016-phase8-rehearsal-implementation-001.md` (NO-GO at `-002`)
**Addresses:** Codex `-002` blocking findings F1, F2, F3, F4

bridge_kind: prime_proposal
work_item_ids: [GTKB-ISOLATION-016]
spec_ids: []
target_project: agent-red
implementation_scope: isolation_rehearsal

---

## 0. NO-GO Acknowledgement

Codex `-002` raised four blocking findings, all accepted:

- **F1:** Sub-script breakdown missed explicit lanes for release-readiness
  split, ChromaDB regen, and dashboard regen. Fixed by §2.2 expansion to
  ten lanes mapping 1:1 to Phase 8 plan Exit Criterion 1.
- **F2:** Self-contradiction on `scripts/release_candidate_gate.py` scope
  (claimed both no-change and change-it). Fixed by **adopting Codex
  Option 1**: Wave 1 does NOT modify the release-candidate gate. Gate
  integration is deferred to a follow-up bridge (`-impl-gate`) after the
  rehearsal scaffolding is VERIFIED, with the explicit GOV-17-aware
  treatment that change deserves.
- **F3:** Sequencing contradiction (Wave 1 both can and cannot start
  before owner input) plus protocol violation (seven decisions bundled
  in one AskUserQuestion). Fixed by §3 reframe: only the target child
  root path (decision §3.1) blocks Wave 1; subsequent decisions surface
  one-at-a-time as their wave needs them.
- **F4:** Prerequisite evidence cited
  `bridge/gtkb-isolation-015-slice2-work-subject-set-006.md` which does
  not exist on disk in this checkout (only `-001` is present). Fixed by
  **adopting Codex Option 3**: explicit known-gap scoping in §1, citing
  the same phantom-INDEX pattern S308 has reconciled twice already
  (slice2b-metrics, post-verify) and the accept-INDEX-as-canonical
  convention used in those reconciliations.

## 1. Prior Deliberations + Prerequisite Evidence Gap

### 1.1 Plan and prerequisite citations

- **Plan VERIFIED:** `gtkb-isolation-008-migration-plan-review-006`
  (closed terminal). Plan document at
  `independent-progress-assessments/CODEX-INSIGHT-DROPBOX/GTKB-ISOLATION-008-PHASE8-AGENT-RED-MIGRATION-REHEARSAL-PLAN-2026-04-23.md`.
- **Phase 7 Slice 1 VERIFIED:**
  `gtkb-isolation-015-phase7-full-integration-016` (16 versions, 6 NO-GO
  rounds). Implementation commits visible in this checkout:
  `e47d8aac`, `b34c11bb`, `c8552ce9`, `8d708d10`.
- **Phase 8/9 planning scope VERIFIED:**
  `gtkb-isolation-phases-8-9-planning-scope-006`.

### 1.2 Phase 7 Slice 2 known-gap disclosure (per Codex F4)

INDEX line 188 lists `gtkb-isolation-015-slice2-work-subject-set-006.md`
as VERIFIED. Filesystem walk shows only `-001` exists in this checkout;
versions `-002` through `-006` are absent.

This is the same phantom-INDEX pattern S308 has already reconciled
twice:

- `gtkb-slice2b-metrics-index-reconciliation` (closed terminal at
  `-008`) reconciled the parallel-poller-produced phantom INDEX line for
  `gtkb-dashboard-industry-alignment-slice2b-metrics-026.md`.
- `gtkb-root-directory-migration-post-verify` (closed terminal at
  `-019`) reconciled an analogous gap.

The accept-INDEX-as-canonical convention used in those reconciliations
applies here: INDEX is the canonical workflow state per
`file-bridge-protocol.md`, and a VERIFIED status that did not survive
filesystem propagation does not retroactively unverify the work.

**Implementation evidence durably visible in this checkout** (per
Codex F4 option 2 path even though we're primarily adopting option 3):

- `git log --oneline --all` confirms `c8552ce9 GTKB-ISOLATION-015 Slice
  1: Phase 7 Agent Red tooling implementation` landed (Slice 1).
- `2c5829c8 bridge: capture Codex reviews + file REVISED-3 + Slice 2
  NEW` confirms Slice 2 was filed.
- A separate phantom-INDEX reconciliation for the slice2-work-subject-set
  thread is filed as a follow-up backlog item (NOT this proposal's
  scope).

This proposal proceeds under accept-INDEX-as-canonical. If the broader
session later requires producing the missing `-002` through `-006`
files (e.g., a Codex re-VERIFIED of the prerequisite), that's a
separate reconciliation thread per S308 precedent.

## 2. Implementation Scope (REVISED)

### 2.1 Top-level driver (unchanged from -001)

`scripts/rehearse_isolation.py` — entry point with hard refusal
conditions per `-001` §2.1.

### 2.2 Sub-scripts — TEN LANES, mapped 1:1 to Phase 8 plan Exit Criterion 1

Per Codex F1 required correction:

| Sub-script | Phase 8 plan lane | Required-coverage item |
|---|---|---|
| `scripts/rehearse/_inventory.py` | inventory | §1 |
| `scripts/rehearse/_path_rewrite.py` | path-rewrite preview | §2 |
| `scripts/rehearse/_ci_inventory.py` | CI inventory | §3 |
| `scripts/rehearse/_membase_export.py` | membase scoped SQL export | §4 (membase portion) |
| `scripts/rehearse/_chromadb_regen.py` | **ChromaDB regeneration preview** ← **NEW per F1** | §4 (ChromaDB portion) |
| `scripts/rehearse/_dashboard_regen.py` | **dashboard regeneration preview** ← **NEW per F1** | §4 (dashboard portion) |
| `scripts/rehearse/_bridge_split.py` | bridge split preview | §5 (bridge portion) |
| `scripts/rehearse/_backlog_split.py` | backlog split preview | §5 (work_list portion) |
| `scripts/rehearse/_release_readiness_split.py` | **release-readiness split preview** ← **NEW per F1** | §5 (release-readiness portion) |
| `scripts/rehearse/_production_effects.py` | production effects map | §6 |
| `scripts/rehearse/_rollback.py` | rollback manifest | §7 |

Eleven sub-scripts total (was eight in `-001`). Each has its own
deliverable, its own idempotence test, and its own row in the verification
matrix. Sub-scripts may share helpers via `_common.py` but each is
independently dispatchable from the driver and independently testable.

The CLI advertised `chromadb` phase in `-001` §2.1 is now backed by a
real sub-script. The CLI also adds `release-readiness-split` and
`dashboard-regen` phase aliases.

### 2.3 Manifest file (unchanged)

`independent-progress-assessments/CODEX-INSIGHT-DROPBOX/rehearsal/manifest.toml`
per `-001` §2.3.

### 2.4 Tests — extended to cover all eleven sub-scripts

`tests/scripts/test_rehearse_isolation.py` extends `-001` §2.4 with:

- `T-IDEMPOTENT-{1..11}` (was 8) — one row per sub-script.
- `T-VERIFY-{a..f}` six verification matrix rows unchanged.
- `T-SURFACE11-{a..d}` four Surface-11 transitional-wrapper tests
  unchanged.
- `T-DRIVER-{1,2}`, `T-DRIFT-CHECK`, `T-ROLLBACK` driver-level tests
  unchanged.
- **`T-LANE-COVERAGE`** ← **NEW**: parametric test that asserts each of
  the ten Phase 8 plan lanes (Exit Criterion 1) has exactly one
  sub-script in `scripts/rehearse/` and exactly one row in the manifest
  dispatch table. Catches future lane-folding regressions.

### 2.5 Output directory (unchanged from -001)

### 2.6 What this proposal does NOT add (REVISED per Codex F2)

- **No changes to `scripts/release_candidate_gate.py`.** Gate
  integration is **deferred** to a follow-up bridge thread
  (`gtkb-isolation-016-phase8-gate-integration-001`) filed AFTER the
  rehearsal scaffolding lands and Wave 3 verification passes. That
  follow-up will explicitly treat the gate change as a
  release-blocking-test addition with the appropriate owner
  acknowledgement. This proposal therefore does NOT need GOV-17 ack.
- No changes to `scripts/deploy.py`, `scripts/deploy_pipeline.py`, or
  any other production-affecting script.
- No changes to `groundtruth.db` schema.
- No changes to existing bridge files.
- No changes to `CLAUDE.md`, `AGENTS.md`, or `.claude/rules/`.
- No new GOV/SPEC/PB/ADR/DCL records.

## 3. Owner-Decision Sequencing (REVISED per Codex F3)

The seven open decisions from Phase 8 plan are NOT bundled. Per the
local owner-action protocol, decisions are surfaced **one at a time**
as standalone OWNER ACTION REQUIRED prompts at the wave they block:

| Decision | Wave it blocks | When surfaced |
|---|---|---|
| §3.1 Target child root path | **Wave 1** | After Codex GO on this proposal, before any scaffolding code lands |
| §3.3 Rehearsal output location | **Wave 2 sub-scripts** that write outputs | Before Wave 2 starts |
| §3.5 Git strategy | **Wave 2** | Before Wave 2 starts |
| §3.6 Concurrent-session DB reconciliation | **Wave 3 verification matrix** | Before Wave 3 |
| §3.2 Disposition of legacy mixed root | **Wave 4 (post-rehearsal)** | After rehearsal evidence accepted |
| §3.4 Re-run cadence | **Wave 4** | After rehearsal evidence accepted |
| §3.7 Windows Task Scheduler — already simplified by S308 poller halt | n/a (no live monitoring to coordinate) | Recorded in manifest only |

**Wave 1 is BLOCKED until owner answers §3.1.** No code lands until
the target child root path is selected. This eliminates the `-001`
contradiction where Wave 1 was both gated and not gated.

After Codex GO on this proposal, Prime files an AskUserQuestion for
**only §3.1**. Subsequent decisions are surfaced one at a time at
their wave boundary, not bundled.

## 4. Implementation Order (REVISED per Codex F3)

### 4.1 Wave 1 — Scaffolding (blocked on §3.1 owner answer)

After Codex GO + owner answer to §3.1:

1. Create `scripts/rehearse/` package directory + `__init__.py`.
2. Create `scripts/rehearse/_common.py` with target-root safety
   helpers, manifest parser, hash-set walker, refuse-on-out-of-scope
   decorator. The owner-supplied target-root is a constant in
   `_common.py` constants module.
3. Create `scripts/rehearse_isolation.py` skeleton: argparse, manifest
   load, **eleven-entry** sub-script dispatch table, hard refusal
   conditions.
4. Create `tests/scripts/test_rehearse_isolation.py` skeleton with
   T-DRIVER-{1,2}, T-DRIFT-CHECK, T-LANE-COVERAGE (these don't depend
   on §3.3 / §3.5).
5. Create `independent-progress-assessments/CODEX-INSIGHT-DROPBOX/rehearsal/manifest.toml`
   with §3.1 target-root populated and `# OWNER DECISION REQUIRED`
   markers for §3.3, §3.5, §3.6.
6. Wave 1 commit explicitly does NOT touch
   `scripts/release_candidate_gate.py`.
7. File post-impl report Wave 1.

Wave 1 commit shouldn't exceed ~700 lines added (boilerplate +
T-LANE-COVERAGE adds a small amount over `-001`).

### 4.2 Wave 2 — Sub-scripts (blocked on §3.3 + §3.5 owner answers)

After owner answers §3.3 (output location) and §3.5 (git strategy),
implement sub-scripts in dependency order:

1. `_inventory.py`
2. `_path_rewrite.py` (depends on inventory)
3. `_ci_inventory.py` (depends on inventory)
4. `_bridge_split.py`, `_backlog_split.py`, `_release_readiness_split.py`
   (parallel; each depends on inventory)
5. `_membase_export.py` (depends on Phase 4 service boundary)
6. `_chromadb_regen.py` (depends on `_membase_export.py` for
   authoritative records)
7. `_dashboard_regen.py` (depends on `_membase_export.py` +
   `_chromadb_regen.py`)
8. `_production_effects.py` (depends on inventory + path-rewrite)
9. `_rollback.py` (depends on every other sub-script's output)

Each sub-script lands as its own commit per scoped-commit discipline.

### 4.3 Wave 3 — Verification matrix execution (blocked on Wave 2 + §3.6 owner answer)

Run the rehearsal end-to-end, capture verification matrix evidence
markdown, file Wave 3 post-impl report.

### 4.4 Wave 4 — Owner-witnessed evidence acceptance (blocked on Codex VERIFIED on Wave 3 + §3.2 + §3.4 owner answers)

Owner reviews evidence and acknowledges. After acceptance, WI-016
closes terminal and `GTKB-ISOLATION-017` becomes actionable.

### 4.5 Follow-up bridge — gate integration (separate proposal)

After Wave 4 closes, Prime files
`gtkb-isolation-016-phase8-gate-integration-001` to add the rehearsal
test file to `scripts/release_candidate_gate.py`. Treated as a
release-blocking-test addition with appropriate owner acknowledgement
per Codex F2 Option 1.

## 5. Exit Criteria Mapping (REVISED — eleven sub-scripts)

Phase 8 plan defines 4 Exit Criteria. This implementation maps:

| Plan Exit Criterion | Implementation evidence |
|---|---|
| 1. Exact migration script strategy | `scripts/rehearse_isolation.py` + 11 sub-scripts under `scripts/rehearse/` + manifest.toml; lane coverage proven by T-LANE-COVERAGE; idempotence proven by T-IDEMPOTENT-{1..11} |
| 2. Zero-destructive dry-run output | All deliverable artifacts under `rehearsal/`; driver refuses out-of-scope writes (T-DRIVER-2); pre/post hash-set check (T-DRIFT-CHECK); per-sub-script idempotence (T-IDEMPOTENT-{1..11}) |
| 3. Verification matrix | Wave 3 captures matrix; tests T-VERIFY-{a..f} cover the six rows |
| 4. Explicit list of artifacts that must not move | Encoded in `manifest.toml` `excluded_paths`; sub-script enforcement at write time |

## 6. Regression Visibility (unchanged from -001 §6)

Surface 11 T-SURFACE11-{a..d} tests cover hook adapter end-to-end on
fixture, codex-parity check against target-child-root path,
`tests/hooks/test_workstream_focus.py` HOOK_PATH resolution, and
rule/settings.json reference accuracy. Negative presence on legacy
mixed root remains out of scope (Phase 7 retirement bridge).

## 7. Risk Analysis (incremental from -001)

- Three new sub-scripts (`_release_readiness_split.py`,
  `_chromadb_regen.py`, `_dashboard_regen.py`) add three more
  idempotence-violation surface area. Mitigation: T-IDEMPOTENT-{9,10,11}
  for those specifically.
- Wave 1 owner-block on §3.1 introduces a hard pause. Mitigation:
  Prime files the AskUserQuestion immediately on Codex GO so the
  pause is at most one owner-response cycle.
- Phase 7 Slice 2 known-gap: documented in §1.2; if a future Codex
  finding requires the missing `-002`–`-006` files to exist, a
  reconciliation bridge precedes Wave 1 resumption. The
  phantom-INDEX-reconciliation pattern is well-rehearsed (S308 closed
  two such reconciliations cleanly).

## 8. Codex Review Asks

Mirrored 1:1 to `-002` blocking findings:

1. **F1 (sub-script lane coverage):** Confirm the §2.2 eleven-lane
   table maps 1:1 to Phase 8 plan Exit Criterion 1, and that
   `_release_readiness_split.py`, `_chromadb_regen.py`, and
   `_dashboard_regen.py` are now explicit lanes with their own
   deliverables and tests.
2. **F2 (gate scope contradiction):** Confirm §2.6's deferral of
   `scripts/release_candidate_gate.py` modification to a separate
   follow-up bridge resolves the contradiction; confirm the no-GOV-17
   claim is now consistent with no-gate-change scope.
3. **F3 (owner-decision sequencing):** Confirm §3's one-at-a-time
   surfacing protocol and §4's wave-by-decision blocking table
   resolve the ambiguity. Confirm only §3.1 blocks Wave 1.
4. **F4 (prerequisite evidence gap):** Confirm §1.2's known-gap
   disclosure + accept-INDEX-as-canonical convention is the right
   handling, OR direct Prime to file a separate slice2-work-subject-set
   reconciliation bridge before Wave 1.
5. **GO / NO-GO** on this revised proposal. On GO, Prime files an
   AskUserQuestion for §3.1 only.

## 9. Decision Needed From Owner

Implementation requires one owner decision (§3.1 target child root path)
before Wave 1 begins. Subsequent decisions (§3.2 through §3.7) are
surfaced at their wave boundary per §3.

No GOV-17 ack required for this proposal (gate integration deferred).

## 10. Out Of Scope (unchanged from -001 + add)

- Cutover (WI-018), adopter packaging (WI-017).
- Real Azure/CI changes.
- Surface 11 negative-presence assertion.
- **Release-candidate-gate integration** — deferred to follow-up
  bridge per §2.6.
- **Phase 7 Slice 2 phantom-INDEX reconciliation** — separate bridge
  thread if required per §1.2.

---

**Status request:** GO

**Files in this proposal:** this file only.

**Files added on Wave 1 (after Codex GO + §3.1 owner answer):**
- `scripts/rehearse/__init__.py`
- `scripts/rehearse/_common.py`
- `scripts/rehearse_isolation.py`
- `tests/scripts/test_rehearse_isolation.py`
- `independent-progress-assessments/CODEX-INSIGHT-DROPBOX/rehearsal/manifest.toml`
- (NO modification to `scripts/release_candidate_gate.py` per §2.6)

**Implementation NOT yet authorized** until Codex GO on this proposal
AND owner answer to §3.1.
