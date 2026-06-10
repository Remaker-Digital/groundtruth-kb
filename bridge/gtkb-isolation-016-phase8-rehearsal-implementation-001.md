NEW

# GTKB-ISOLATION-016 — Phase 8 Agent Red Migration Rehearsal (Implementation)

**Status:** NEW
**Date:** 2026-04-25
**Work item:** GTKB-ISOLATION-016
**Author:** Prime Builder (Claude Opus 4.7, S308 interactive)
**Bridge kind:** implementation_proposal
**Plan source (VERIFIED):** `bridge/gtkb-isolation-008-migration-plan-review-006.md`
**Plan document:** `independent-progress-assessments/CODEX-INSIGHT-DROPBOX/GTKB-ISOLATION-008-PHASE8-AGENT-RED-MIGRATION-REHEARSAL-PLAN-2026-04-23.md`
**Prerequisite (VERIFIED):** `bridge/gtkb-isolation-015-slice2-work-subject-set-006.md` (Phase 7 Slice 2)

bridge_kind: prime_proposal
work_item_ids: [GTKB-ISOLATION-016]
spec_ids: []
target_project: agent-red
implementation_scope: isolation_rehearsal
requires_review: true
requires_verification: true

---

## 0. What This Proposal Is And Is Not

This proposal authorizes implementation of the Phase 8 rehearsal driver
described in the VERIFIED Phase 8 plan. It does **NOT** authorize:

- The actual extraction (cutover) — that is `GTKB-ISOLATION-018` and
  requires its own bridge plus GOV-16 owner approval.
- Any modification of the legacy mixed root, the GT-KB product
  repository, the production Azure environment, ACS configuration, or
  Key Vault contents.
- Adopter packaging — that is `GTKB-ISOLATION-017` (Phase 9).

The rehearsal is **zero-destructive by design**: it copies files into a
target child root, emits preview artifacts, and proves split handling.
No legacy file is renamed, deleted, or overwritten.

## 1. Prior Deliberations

- **Plan VERIFIED:** `gtkb-isolation-008-migration-plan-review-006`
  closed terminal after 6 versions including 1 NO-GO (F1: hook file
  presence re-check). Plan document covers all 7 required-coverage
  items, all 16 mixed-state surfaces, and all 4 exit criteria.
- **Phase 7 enforcement (prerequisite) VERIFIED:**
  `gtkb-isolation-015-phase7-full-integration-016` (Slice 1 — runtime
  enforcement, 16 versions, 6 NO-GO rounds) and
  `gtkb-isolation-015-slice2-work-subject-set-006` (Slice 2 — typed
  `work_subject.set` handler). All Phase 7 guardrails the rehearsal
  must respect are landed.
- **Phase 8/9 planning scope:**
  `gtkb-isolation-phases-8-9-planning-scope-004` (GO) authorized the
  planning work. `-006` VERIFIED both phase plans.
- **Authority matrix (Phase 1):** classifications A/B/C/D for each of
  the 16 surfaces are fixed in the Phase 1 plan. The implementation
  bridge does not re-derive them; it consumes them.
- No prior bridge thread exists for this implementation. This is the
  first execution proposal for Phase 8.

## 2. Implementation Scope

### 2.1 Top-level driver (one new file)

**`scripts/rehearse_isolation.py`** — entry point that orchestrates
all sub-scripts per the manifest. Reads
`independent-progress-assessments/CODEX-INSIGHT-DROPBOX/rehearsal/manifest.toml`,
then dispatches to sub-scripts in deterministic order.

CLI shape (proposed; refined during implementation):

```
python scripts/rehearse_isolation.py
    --target-root <path>           # MUST resolve outside legacy mixed root
    --manifest <path>              # default: rehearsal/manifest.toml
    --phase {inventory,rewrite,ci,bridge-split,backlog-split,
             release-readiness-split,chromadb,dashboard,verify,rollback,all}
    --dry-run                       # default true; --no-dry-run forbidden in v1
```

**Hard refusal conditions** (driver exits 2 before any work):

1. `--target-root` resolves inside the legacy mixed root.
2. Any output path resolves outside `--target-root` or the rehearsal
   output directory.
3. Pre-run hash set of legacy root differs from a stored baseline AND
   `--accept-drift` is not passed.

### 2.2 Sub-scripts (eight new files)

Per Phase 8 plan §"Exit Criteria" item 1, the driver delegates to
subject-scoped sub-scripts. Each is idempotent and produces
deterministic output from a fixed manifest:

| Sub-script | Required-coverage item | Deliverable |
|---|---|---|
| `scripts/rehearse/_inventory.py` | §1 Dry-Run Inventory | `dryrun-inventory.json`, `dryrun-ignored.json` |
| `scripts/rehearse/_path_rewrite.py` | §2 Import/Path Rewrites | `path-rewrite-map.json`, `path-rewrite-preview.diff` |
| `scripts/rehearse/_ci_inventory.py` | §3 CI/Test Command Rewrites | `ci-command-inventory.csv`, `ci-rewrite-preview.md` |
| `scripts/rehearse/_dashboard_membase.py` | §4 Dashboard + MemBase | scoped SQL export script + regen recipe |
| `scripts/rehearse/_bridge_split.py` | §5 Bridge/Backlog Split | `bridge-split-plan.md`, two preview INDEXes |
| `scripts/rehearse/_backlog_split.py` | §5 (cont.) | per-line work_list/release-readiness previews + quarantine |
| `scripts/rehearse/_production_effects.py` | §6 Production Deployment Effects | `production-effects-map.md` with `deploy-blocking`/`deploy-safe-after-review` tags |
| `scripts/rehearse/_rollback.py` | §7 Rollback | `rollback-manifest.md` + per-step reverse patches |

Sub-scripts share a common helpers module
(`scripts/rehearse/_common.py`) for: target-root resolution, manifest
parsing, hash-set walking, output-path safety check, and the per-script
"refuse-on-out-of-scope-write" decorator.

### 2.3 Manifest file (one new file)

**`independent-progress-assessments/CODEX-INSIGHT-DROPBOX/rehearsal/manifest.toml`**

Single source of truth for the rehearsal. Contains:

- `target_root` (string path; verified at runtime against owner decision §3.1)
- `legacy_root` (string path; verified to be the current Agent Red workspace)
- `output_dir` (string path under target child root or sandbox)
- `phase_1_authority_matrix_path` (citation)
- `surface_treatments` (table of 16 surfaces with action/recipe/rollback/verification)
- `excluded_paths` (paths the rehearsal must never touch — secrets, prod manifests)
- `python_version` and `dependencies` (per Phase 8 plan §"Exit Criteria" item 1)
- `drift_tolerance` (declared tolerance for chromadb byte-difference per surface 7)

The manifest is committed under `rehearsal/` so re-runs produce
byte-identical output (per Exit Criterion 1: idempotence requirement).

### 2.4 Tests (one new test file + extended hook test)

**`tests/scripts/test_rehearse_isolation.py`** — covers:

- Driver refuses `--target-root` inside legacy mixed root (T-DRIVER-1).
- Driver refuses output paths outside target child root or output dir
  (T-DRIVER-2).
- Each sub-script run twice from the same manifest produces
  byte-identical output (T-IDEMPOTENT-{1..8}).
- Hash-set integrity check fires when legacy root mutates between
  pre-run and post-run walks (T-DRIFT-CHECK).
- Rollback manifest's reverse patches return target child root to
  initial-copy state when applied in reverse order (T-ROLLBACK).
- Verification matrix from Exit Criterion 3 runs against fixture
  state and passes for the "happy path" + fails on each failure
  scenario (T-VERIFY-{a..f}, six rows).
- Surface 11 (`.claude/hooks/workstream-focus.py`) end-to-end fixture
  per Phase 8 plan §"Regression Visibility" (T-SURFACE11-{a..d}).

**`tests/hooks/test_workstream_focus.py`** — extension only (existing
file preserved): assert that after rehearsal, `HOOK_PATH` resolves to
the target child root copy and the hook executes against a fixture
payload without legacy-root reachback.

Aggregate test runtime target: under 10 seconds for the unit-level
tests; the verification matrix may take longer because it walks file
systems, but each row should complete under 60 seconds.

### 2.5 Output directory (created at runtime, not in repo)

`<target-child-root>/independent-progress-assessments/CODEX-INSIGHT-DROPBOX/rehearsal/`
holds all rehearsal-produced artifacts. The rehearsal driver creates
the directory; `.gitignore` at the target child root excludes it from
tracking (rehearsal output is evidence, not source).

### 2.6 What this proposal does NOT add

- No changes to `scripts/deploy.py`, `scripts/deploy_pipeline.py`,
  `scripts/release_candidate_gate.py`, or any other production-affecting
  script.
- No changes to `groundtruth.db` schema.
- No changes to existing bridge files.
- No changes to `CLAUDE.md`, `AGENTS.md`, or `.claude/rules/`.
- No new GOV/SPEC/PB/ADR/DCL records (operational rehearsal, not
  governance change).

## 3. Open Decisions Requiring Owner Input Before Implementation Starts

Per Phase 8 plan §"Open Decisions For The Implementation Bridge", the
following must be answered before sub-script implementation begins.
Codex GO on this proposal authorizes scaffolding (driver entry point,
manifest schema, common helpers, test harness) but not the surface-
specific sub-script bodies that depend on these decisions.

1. **Target child root path.** Phase 2 outcome. Candidates: a sibling
   directory under `E:\Claude-Playground\` (e.g.,
   `E:\Claude-Playground\agent-red-app\`), a fresh top-level workspace,
   or an entirely different drive. Affects sandbox isolation guarantees.
2. **Disposition of legacy mixed root after rehearsal.** Three options:
   keep as read-only archive (no filesystem change), freeze via NTFS
   permissions (deny-write to specific user accounts), or remove (full
   delete after evidence accepted). Recommend "keep as read-only
   archive" until cutover (`GTKB-ISOLATION-018`) — preserves rollback
   surface.
3. **Rehearsal output location.** Two options: (a) write previews to
   the target child root (becomes part of the eventual real root), or
   (b) write to a separate sandbox directory that never becomes the
   target child root. Option (b) is safer for repeated rehearsal but
   adds a copy step at cutover. Recommend (b) — clean-room rehearsal.
4. **Re-run cadence.** One-shot rehearsal vs periodic re-runs until
   cutover. Affects manifest committing strategy and CI integration.
5. **Git strategy for target child root.** Three options: fresh repo
   (no history), clone with history filter (preserves Agent Red commits
   only), clean worktree (shares history but separate working tree).
   Each has different blast radius for accidental cross-root commits.
6. **Concurrent-session DB reconciliation.** Two options: quiesce the
   legacy root during rehearsal (pause sessions), or use a snapshot
   timestamp accepting minor drift. Recommend quiesce for the first
   rehearsal; revisit if periodic re-runs adopted (#4).
7. **Windows Task Scheduler migration window.** Bridge-monitor
   scheduled tasks (`AgentRedFileBridgeIndexScan-*`,
   `AgentRedBridgeLivenessAlert`, `AgentRedPollerLivenessWatcher`) are
   currently `Disabled` per the S308 poller-halt directive. Re-enabling
   at the target child root post-cutover is out of scope for this
   rehearsal — manifest records the registration inventory only. (This
   was not anticipated in the Phase 8 plan; the S308 poller-halt
   simplifies the Task Scheduler aspect of rehearsal because there's
   nothing to migrate.)

## 4. Implementation Order

### 4.1 Wave 1 — Scaffolding (no owner decisions blocking)

After Codex GO on this proposal, but before owner answers the §3
decisions:

1. Create `scripts/rehearse/` package directory + `__init__.py`.
2. Create `scripts/rehearse/_common.py` with target-root safety
   helpers, manifest parser, hash-set walker, refuse-on-out-of-scope
   decorator.
3. Create `scripts/rehearse_isolation.py` skeleton: argparse, manifest
   load, sub-script dispatch table, hard refusal conditions.
4. Create `tests/scripts/test_rehearse_isolation.py` skeleton with
   T-DRIVER-1 / T-DRIVER-2 / T-DRIFT-CHECK tests (these don't depend
   on owner decisions).
5. Create `independent-progress-assessments/CODEX-INSIGHT-DROPBOX/rehearsal/manifest.toml`
   with placeholder values for §3 decision fields and explicit
   `# OWNER DECISION REQUIRED` markers.
6. Add `scripts/rehearse/` and the test file to
   `scripts/release_candidate_gate.py`.
7. File post-impl report Wave 1 with commit hash.

Wave 1 commit shouldn't exceed ~600 lines added (most of it
boilerplate + tests).

### 4.2 Wave 2 — Sub-scripts (gated on owner decisions §3.1, §3.3, §3.5)

After owner answers decisions §3.1 (target root), §3.3 (output
location), and §3.5 (git strategy), implement sub-scripts in dependency
order:

1. `_inventory.py` (depends on target-root + legacy-root only).
2. `_path_rewrite.py` (depends on inventory output).
3. `_ci_inventory.py` (depends on inventory output).
4. `_bridge_split.py`, `_backlog_split.py` (parallel; each depends on
   inventory).
5. `_production_effects.py` (depends on inventory + path-rewrite).
6. `_dashboard_membase.py` (depends on Phase 4 service boundary;
   needs scoped SQL export query).
7. `_rollback.py` (depends on every other sub-script's output).

Each sub-script lands as its own commit (per scoped-commit discipline)
with its corresponding tests.

### 4.3 Wave 3 — Verification matrix execution (gated on Wave 2 complete + owner decision §3.6)

Run the rehearsal end-to-end, capture verification matrix evidence
markdown, file Wave 3 post-impl report with all rehearsal outputs as
review evidence. This is the gate to consider the rehearsal complete
and WI-016 ready for Codex VERIFIED.

### 4.4 Wave 4 — Owner-witnessed evidence acceptance (gated on Codex VERIFIED on Wave 3)

Owner reviews rehearsal evidence and acknowledges acceptance. After
acceptance, WI-016 closes terminal and `GTKB-ISOLATION-017` (Phase 9
adopter packaging) becomes actionable. No automated step here — this
is owner-acknowledgement gating the next WI.

## 5. Exit Criteria Mapping

Phase 8 plan defines 4 Exit Criteria. This implementation maps to each:

| Plan Exit Criterion | Implementation evidence |
|---|---|
| 1. Exact migration script strategy | `scripts/rehearse_isolation.py` + `scripts/rehearse/*.py` + manifest.toml; idempotence proven by tests T-IDEMPOTENT-{1..8} |
| 2. Zero-destructive dry-run output | All 8 deliverable artifacts under `rehearsal/`; driver refuses out-of-scope writes (T-DRIVER-2); pre/post hash-set check (T-DRIFT-CHECK) |
| 3. Verification matrix | Wave 3 captures matrix results; tests T-VERIFY-{a..f} cover the six rows |
| 4. Explicit list of artifacts that must not move | Encoded in `manifest.toml` `excluded_paths` field; sub-script enforcement at write time |

## 6. Regression Visibility

- Tests added to `scripts/release_candidate_gate.py` so any future
  change that breaks rehearsal idempotence or the safety conditions
  fails the release-candidate gate.
- Surface 11 (transitional wrapper pair) coverage per Phase 8 plan
  §"Regression Visibility" — explicit T-SURFACE11-{a..d} tests for the
  hook adapter end-to-end on a fixture payload, the codex-parity
  check, the existing `tests/hooks/test_workstream_focus.py`
  path-resolution, and the rule reference / settings.json
  registration.
- Negative presence assertion on legacy mixed root for Surface 11 is
  reserved for the Phase 7-aligned retirement bridge per the plan and
  is **explicitly out of scope for this rehearsal**.
- Release-candidate gate at the target child root must report
  application subject only; combined-subject claims must fail (covered
  by T-VERIFY-c).

## 7. Risk Analysis

### 7.1 Failure modes for the change itself

- **Driver writes outside target child root.** Mitigation: T-DRIVER-2
  + the refuse-on-out-of-scope decorator on every sub-script
  filesystem-write call site. Multi-layer defense.
- **Inventory misclassifies a surface.** Mitigation: classification
  source (Phase 1 authority matrix row id) is recorded per inventory
  row; Codex review of inventory output catches misclassification
  before any path rewrite uses it.
- **Idempotence violated by hidden timestamp/randomness.** Mitigation:
  T-IDEMPOTENT-* tests run each sub-script twice and compare bytes;
  any sub-script using `time.time()` or `uuid` must mock or use
  manifest-fixed values.
- **Concurrent session inserts into `groundtruth.db` during rehearsal.**
  Mitigation: §3.6 owner decision requires either quiesce or accept
  drift tolerance; quiesce is recommended for first rehearsal.
- **Surface 11 pair gets out of sync.** Specific risk per Phase 7
  history. Mitigation: T-SURFACE11-{a..d} catch all four sub-failures
  the Phase 7 §E review surfaced.

### 7.2 Failure modes the change prevents

- Cutover (`GTKB-ISOLATION-018`) shipping without dry-run evidence
  for any of the 16 surfaces.
- Production-affecting rewrites being applied without explicit
  `deploy-blocking` flagging.
- Bridge / backlog being silently dropped during the split.
- Application subject + GT-KB subject false "combined ready" claim
  (release-readiness gate enforcement).

### 7.3 Rollback (rehearsal-level)

- Per Phase 8 plan: rehearsal is reversible because legacy mixed root
  is never mutated.
- T-ROLLBACK proves reverse-patch sequence returns target child root
  to initial-copy state.
- If implementation discovers the rollback contract cannot be
  satisfied by some sub-script, the sub-script must add a
  `--no-mutate` mode and that mode becomes the only mode wired into
  the driver until rollback is restored.

## 8. Codex Review Asks

1. Confirm §2's eight sub-script breakdown and the dispatch-table
   driver shape match the plan's Exit Criterion 1.
2. Confirm §2.3's manifest schema covers everything Exit Criterion 1
   requires (Python version, dependencies, offline behavior).
3. Confirm §3's seven open decisions accurately mirror the plan's
   "Open Decisions For The Implementation Bridge" + the S308
   poller-halt update on §3.7.
4. Confirm §4's wave sequencing (scaffolding → sub-scripts gated on
   owner decisions → verification matrix → owner acceptance) is
   correct, particularly that Wave 1 can proceed before owner answers
   §3 decisions.
5. Confirm §5's Exit Criteria mapping table is complete.
6. Confirm §6's regression visibility scope (Surface 11
   T-SURFACE11-{a..d}) accurately implements the plan's
   §"Regression Visibility" requirement, and that the negative
   presence assertion on legacy mixed root is correctly excluded.
7. **GO / NO-GO** on this implementation proposal. On GO, Prime files
   an AskUserQuestion to surface decisions §3.1, §3.3, §3.5 (and
   recommendations for the others) before Wave 1 begins.

## 9. Decision Needed From Owner

Implementation requires owner decisions §3.1 through §3.7 before any
sub-script body work begins (Wave 2). Wave 1 (scaffolding) can proceed
on Codex GO alone. After Codex GO, Prime files an AskUserQuestion
covering the seven decisions.

No GOV-17 ack required — the rehearsal does not modify protected
automation scripts. Wave 2's `_dashboard_membase.py` will produce a
scoped SQL export script as evidence; it does not execute it against
production data.

## 10. Out Of Scope

(See §0 and §2.6.) Additionally:

- Cutover execution (`GTKB-ISOLATION-018`) — separate bridge.
- Adopter packaging (`GTKB-ISOLATION-017`, Phase 9) — separate bridge.
- Production deploy effects beyond mapping them in
  `production-effects-map.md`.
- Real GitHub Actions workflow modifications.
- Real Azure resource changes.
- Modification of any test in `tests/` other than the explicit
  Surface-11 path-resolution rewrite.
- The `WI-CPD-PHASE-NUMBER-CHAOS` deploy_pipeline cleanup
  (canonical-deploy thread §0.1 disclosure; separate WI).

---

**Status request:** GO

**Files in this proposal:** this file only.

**Files added on Wave 1 (after Codex GO):**
- `scripts/rehearse/__init__.py`
- `scripts/rehearse/_common.py`
- `scripts/rehearse_isolation.py`
- `tests/scripts/test_rehearse_isolation.py`
- `independent-progress-assessments/CODEX-INSIGHT-DROPBOX/rehearsal/manifest.toml`
- `scripts/release_candidate_gate.py` modification (add new test file)

**Wave 2+ files** added incrementally per owner decisions and §4.2
ordering.

**Implementation NOT yet authorized** until Codex GO on this
proposal. Wave 2 NOT yet authorized until owner answers §3 decisions
via AskUserQuestion after GO.
