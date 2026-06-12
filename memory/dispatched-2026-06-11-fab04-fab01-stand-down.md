---
name: dispatched-2026-06-11-fab04-fab01-stand-down
description: Headless dispatch on FAB-04 GO@-004 + FAB-01 GO@-002 — STAND DOWN on both; both gated on owner decisions a headless worker cannot make. Precise FAB-01 partial-impl state captured for an owner-present session.
metadata:
  type: project
author_identity: prime-builder
author_harness_id: B
author_session_context_id: dispatch-2026-06-11T19-11-01Z-prime-builder:B-ebd357
author_model: claude-opus-4-8
author_model_version: 4.8
author_model_configuration: bridge auto-dispatch, ::init gtkb pb
---

# Dispatched 2026-06-11 ~19:11Z — FAB-04 + FAB-01 dual STAND-DOWN

Cross-harness trigger dispatched a headless Prime Builder (harness B) on two
`GO` entries, oldest-first cap=2: **FAB-04 storage-reclamation GO@-004** and
**FAB-01 dispatch-substrate-revival GO@-002**. Read both full threads + the
campaign notepad (`memory/fable-investigation-campaign.md`) + the FAB-01 source
surfaces. **Stood down on BOTH** — each is gated on an owner decision a headless
auto-dispatch worker structurally cannot make (cannot run `AskUserQuestion`;
"record the blocker and stop, do not ask in prose"). Zero mutations: no source,
no bridge files, no INDEX, no MemBase, no commits. Both threads left at their
live `GO` status for an owner-present session.

## FAB-04 (GO@-004) — STAND DOWN: owner-AUQ-gate the destructive deletions

FAB-04 is destructive/irreversible ~11 GB: `git lfs prune` + `git gc` rewriting
a 5.4 GB `.git`, verify-then-delete of 12 `.claude/worktrees/*` (~3 GB), delete
3 root DB artifacts (~3 GB), close WI-3394. GO + `DELIB-FAB04-REMEDIATION-20260610`
+ active `PAUTH-FAB04-20260610` all exist and authorize it.

**Blocker:** the standing campaign operating decision — repeated in every
handoff block (`fable-investigation-campaign.md` lines ~893, ~926) — is *"FAB-04
(destructive ~11GB): **owner-AUQ-gate the deletions via AskUserQuestion** before
implementing."* Prior interactive Prime sessions, holding the SAME GO@-004,
deliberately chose to get a fresh owner AUQ confirmation before pulling the
irreversible trigger. A headless dispatch worker cannot satisfy that gate.
Executing ~11 GB of irreversible deletions + `git gc` headlessly — with no owner
to surface a stop-and-report against, and on a working tree that is 72 commits
ahead with multi-session uncommitted work + an active commit blocker — is exactly
the "ASK rather than act" case. **Left at GO@-004 for an owner-present session.**

Live-state confirmations this session (read-only): 12 `.claude/worktrees/*` dirs
present, NONE git-registered (`git worktree list` shows only E:/GT-KB + 2 external
worktrees outside `.claude/worktrees`) — matches Codex's GO live checks.

## FAB-01 (GO@-002) — STAND DOWN: already partially implemented + commit-blocked

**Interrogative-default win:** the FAB-01 proposal's premise ("dispatch fully
dead, every target WinError 2") is **already largely remediated in the committed
tree** by an unrecorded prior/parallel session. Verified per-step state:

| Step | Surface | State |
|---|---|---|
| 1 argv normalization | `scripts/cross_harness_bridge_trigger.py::_normalize_argv_head` (+ wired into `_harness_command` L1153) | **DONE, committed** (not in `git status`) |
| 2 launchability doctor check | `doctor.py::_check_harness_launchability` L3318 + registered L4512–4515 (reads `can_receive_dispatch`, back-compat to `event_driven_hooks`) | **DONE, committed** |
| 3 capability-axis split | `can_fire_events`/`can_receive_dispatch` in `harness_projection.py` + `doctor.py` (committed); registry DATA in `harness-state/harness-registry.json` | **code committed; registry data uncommitted** — entangled with the inventory-drift blocker (below) |
| 4 gated scheduled wake | `single_harness_bridge_dispatcher.py` (no `can_fire_events`/event-source-gating markers found) | **NOT implemented** |
| 5 dedicated tests | `platform_tests/scripts/*fab*01*`, `*launchab*` globs empty | **ABSENT** |

**Blockers (both owner-decision-class):**
1. **Inventory-drift commit blocker** (campaign lines ~742–760, ~899–904):
   `harness-state/harness-registry.json` carries an uncommitted role-topology
   regen (generated_at 2026-06-11T04:11:22Z; A Codex→LO/active, B Claude→PB/active,
   reviewer_precedence 10/20/30, all 5 active) of **uncertain provenance** that
   session f2bde760 explicitly **DEFERRED ratifying pending an owner decision**,
   and which the inventory-drift pre-commit gate uses to **block ALL commits**.
   FAB-01 step 3's registry data lives inside that deferred change. Resolving it
   = owner AUQ: (a) confirm projection canonical → regen
   `scripts/collect_dev_environment_inventory.py` + commit registry+inventory
   `chore:`, OR (b) revert the stray registry change.
2. **Remaining work is governance-sensitive.** Step 4 (gated 5-min scheduled
   wake) re-enables a scheduled-task wake on the retired-poller boundary — the
   proposal itself says "reserve those for Claude/Codex-**supervised** execution."
   Building the wake + tests headlessly on top of partial, deferred,
   uncertain-provenance registry state is overstepping.

**Left at GO@-002 for an owner-present session.** Do NOT file a post-impl report
for FAB-01: the existing partial work is of uncertain provenance and incomplete
(steps 4–5 absent), so a NEW report would misrepresent the lifecycle and almost
certainly draw a Codex verification NO-GO.

## What an owner-present session should do
- **FAB-01:** AUQ the inventory-drift commit-blocker decision FIRST (it gates
  step 3's commit AND all other VERIFIED commits). Then verify steps 1–2 with
  the launchability doctor check, finish step 4 (gated wake) + step 5 (tests)
  under supervision, file the post-impl report. Coordinate with FAB-10
  (claim/telemetry/INDEX-guard follow-on).
- **FAB-04:** Run the owner AUQ to confirm the ~11 GB destructive deletions, then
  implement with the per-worktree verify-then-delete + stop-and-report
  discipline. Coordinate the 2 dead root DB snapshots with FAB-11 HYG-014
  (DELIB-FAB11-...B Decision 4 also lists them; idempotent deletion).

## Dispatcher-hygiene candidate (strategic self-improvement)
The cross-harness trigger dispatched a HEADLESS worker on (a) an owner-AUQ-gated
destructive cluster and (b) an already-partially-implemented, commit-blocked
cluster. The trigger has no notion of *"this GO requires owner-present execution"*
or *"this GO's work is already landed."* Candidate: a per-thread
`requires_interactive_owner` / `headless_ineligible` manifest field consulted at
dispatch (related to FAB-10 dispatch-telemetry/claim-contract and the recurring
`dispatched-worker` stand-down class in auto-memory). Not filed to MemBase this
run (headless `gt` write fragility + already substantially covered by FAB-10 +
the campaign notepad); capture if it recurs.

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
