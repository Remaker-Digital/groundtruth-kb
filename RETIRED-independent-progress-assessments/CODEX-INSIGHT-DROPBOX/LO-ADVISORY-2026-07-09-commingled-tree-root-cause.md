# LO Advisory — Commingled-tree verification NO-GOs: root cause + minimal fix

author_identity: loyal-opposition/claude
author_harness_id: B
author_session_context_id: 85e78bc0-61f1-4383-84cd-fb4128f29b95
author_model: claude-opus-4-8
author_model_version: claude-opus-4-8
author_model_configuration: Claude Code interactive; resolved role loyal-opposition via ::init gtkb lo

Date: 2026-07-09 UTC
Role: loyal-opposition (session-stated via ::init gtkb lo)
Classification: advisory (adapt) — refines the fix direction of WI-5105
Related: WI-5105 (backlog), WI-5100/WI-5083 (instance 1), WI-5066 -004 (instance 2), WI-5041<->WI-5066 (latent instance 3)
Specs/WIs: WI-4471 (existing guard), WI-5100, WI-5083, WI-5066, WI-5041, WI-5095

## Executive Summary

Three commingled-tree verification failures occurred in a single LO session
(2026-07-09). The failure mode is: two independent GO'd bridge threads modify the
same file in one shared worktree, so neither can be atomically VERIFIED-finalized
(the finalization gate stages whole files). This is NOT a code-quality problem —
it is a coordination gap, and it is structural: 3 distinct `target_paths` overlap
pairs exist right now among the 12 open GO'd threads.

A cross-thread overlap guard already exists in the impl-start-gate (WI-4471). Its
one defect is precise and its fix is minimal: it blocks only on a *live
work-intent claim*, but commingling is caused by uncommitted *changes* whose
claim has already been released. Augmenting the guard to also treat a dirty,
overlapping, packet-reserved target file as a collision closes the gap.

## Observation 1 — The failure mode, with three same-session instances

VERIFIED finalization (`.claude/rules/file-bridge-protocol.md` mandatory VERIFIED
commit-finalization gate) stages the declared verified paths via whole-file
`git add` and commits them. When two threads' changes coexist uncommitted in one
file, the verifier cannot commit exactly one thread's change:

- **Instance 1 (this session): WI-5100 vs WI-5083.** `scripts/workstream_focus.py`
  carried WI-5100's carve-out AND WI-5083's separately-GO'd, unreported startup-gate
  change. WI-5100 verification -> NO-GO (`bridge/gtkb-wi5100-...-004.md`).
- **Instance 2: WI-5066 `-004` NO-GO.** The WI-5066 `-003` report changed
  `scripts/dispatcher_runtime.py` overlapping WI-5064/WI-5065 reports; could not be
  atomically finalized (`bridge/gtkb-wi5066-...-004.md`).
- **Instance 3 (latent): WI-5041 vs WI-5066.** Both GO'd, both target
  `scripts/dispatcher_runtime.py` + `platform_tests/scripts/test_dispatcher_runtime.py`.
  Will commingle if implemented in parallel.

## Observation 2 — Live exposure is structural, not incidental (quantified)

Read-only enumeration of the 12 open GO-latest threads and their `target_paths`
(probe: `independent-progress-assessments/CODEX-INSIGHT-DROPBOX/overlap_probe.py`)
found **3 overlap pairs** touching 5 shared files:

| Pair | Shared target_paths |
| --- | --- |
| `gtkb-antigravity-supported-skill-target-parity-alignment` vs `gtkb-wi5095-adapter-registry-sha-refresh-in-flow` | `config/agent-control/harness-capability-registry.toml` |
| `gtkb-cloud-harness-template-slice4a-native-hook-wiring` vs `gtkb-wi5066-openrouter-silent-stall-timeout` | `scripts/cloud_harness_base.py`, `platform_tests/scripts/test_cloud_harness_base.py` |
| `gtkb-wi5041-dispatcher-thread-reoffer-backoff` vs `gtkb-wi5066-openrouter-silent-stall-timeout` | `scripts/dispatcher_runtime.py`, `platform_tests/scripts/test_dispatcher_runtime.py` |

WI-5066 alone sits in two overlaps. With an active dispatch fleet implementing in
parallel, every pair is a latent commingled-tree NO-GO.

## Observation 3 — The guard exists; it keys on the wrong (ephemeral) signal

`scripts/implementation_authorization.py` already carries a WI-4471 cross-thread
overlap guard (L1951-2001). At `begin --bridge-id X` it:

1. scans other bridges' named packets in the by-bridge dir;
2. computes `target_patterns_overlap(other.target_path_globs, X.targets)` (L1979) —
   a correct exact+glob overlap predicate;
3. **but only reports a collision when `current_holder(other) is not None`** — i.e.,
   the other thread has a LIVE work-intent claim (L1986-2000). L1989-1990:
   `if holder is None: continue` (allow).

### Deficiency rationale

Work-intent claims are ephemeral: draft-claim TTL defaults to ~600 s and the claim
is released when the drafting/implementation step completes
(`scripts/bridge_work_intent_registry.py`). Commingling, by contrast, is caused by
a **durable** condition: uncommitted changes sitting in a shared file whose thread
has already released its claim (implemented, report filed, but not yet
VERIFIED-finalized — often precisely because it is awaiting an independent LO
verdict). The exact slip is:

> Thread Y runs `begin` (creates its by-bridge packet) -> implements into shared
> file Z -> Y's claim releases/expires (Z still dirty, uncommitted) -> later, thread
> X runs `begin`; the guard finds Y's packet overlaps Z, checks `current_holder(Y)`
> -> `None` -> `continue` -> X is allowed -> X implements into Z -> Z now commingles X+Y.

This is exactly instance 1 (WI-5083's implementation was in-tree with its claim
released when WI-5100 proceeded). The guard's packet-overlap detection was right;
its liveness predicate was wrong for this failure mode.

## Proposed Solution (recommended, least-regret) — durable-signal augmentation

Augment the existing WI-4471 guard so that when `target_patterns_overlap` finds an
overlap with another bridge Y's packet AND `current_holder(Y) is None`, it performs
a second, durable check on the *overlapping files only*:

- Run `git status --porcelain -- <overlapping paths>` (bounded to the overlap
  witnesses, not the whole tree).
- **If any overlapping file is dirty/untracked -> BLOCK** with a reason naming Y and
  the dirty shared path(s): "target Z is uncommitted and reserved by open thread Y
  (packet present, claim released); commit or VERIFIED-finalize Y before mutating Z."
- **If the overlapping files are clean -> allow** (no commingling risk; sequential
  commit is still possible). This preserves the current permissive behavior for the
  common clean case and adds cost only when a real dirty overlap exists.

Keep the guard fail-soft (a git error yields allow, matching the existing
registry-read fail-soft at L1961-1962) so a lookup failure never converts an
authorized edit into a spurious block.

### Option rationale

This is the minimal change at the mandatory chokepoint every protected mutation
already passes through (`implementation_authorization.py begin`). It reuses the
existing `target_patterns_overlap` predicate and the existing by-bridge packet
scan; it adds one bounded `git status` on the overlap witnesses. It is
bias-aligned (on the path the agent already traverses) rather than a new behavior
an agent must remember. It targets the observed durable failure signal directly.

Rejected alternatives:

- **File-level work-intent claims** (extend the claim registry to lock
  `target_paths`, not just the slug). More complete, but a schema change touching
  every claim path and every claim reader; higher blast radius; and it still relies
  on claim lifetime rather than the durable git signal. Defer unless the augmented
  guard proves insufficient.
- **Per-implementation git worktree isolation** (each Prime worker in its own
  worktree). Cleanest true isolation, but a large infra change that complicates
  shared-DB/state finalization and the VERIFIED commit transaction. Out of
  proportion to the defect.
- **Advisory-only overlap report at GO time** (surface overlaps, no enforcement).
  Lowest cost, but discipline has already failed 3x in one session; a warning that
  does not fail closed will not stop the token-costly re-verification loops.

## Prime Builder Implementation Context

- **Objective:** close the claim-released-but-uncommitted gap in the WI-4471
  overlap guard so a second `begin` on a dirty shared target fails closed.
- **Evidence paths:** `scripts/implementation_authorization.py` L1951-2001 (the
  guard; the `if holder is None: continue` at L1989-1990 is the edit site);
  `scripts/bridge_work_intent_registry.py` (claim TTL / release semantics);
  `overlap_probe.py` in the dropbox (the exposure enumeration).
- **File touchpoints:** `scripts/implementation_authorization.py` (guard body) +
  `platform_tests/scripts/test_implementation_authorization.py` (new case:
  overlapping packet, no live claim, dirty shared file -> collision; clean shared
  file -> allow; fail-soft on git error -> allow).
- **Verification steps:** unit test the three branches above; then confirm on the
  live tree that a `begin` for WI-5041 while `dispatcher_runtime.py` carries
  uncommitted WI-5066 work would block (and vice-versa).
- **Rollback notes:** single-function change; revert restores the prior
  claim-only behavior. No data/KB mutation.
- **Sequencing caveat (do not commingle the fix itself):** this fix touches
  `implementation_authorization.py`, which is not currently in any open GO thread's
  target_paths — so it is a clean, non-overlapping change to implement.
- **Open decisions:** whether the dirty-overlap outcome is a hard BLOCK (recommended,
  matching the token-cost of the re-verification loops) or a WARN with an override
  env var. LO recommendation: BLOCK, with the same owner-authorized bypass pattern
  used elsewhere for genuine exceptions.

## Immediate (pre-fix) mitigation

Until the guard is augmented, sequence the 3 known overlap pairs: fully
implement -> report -> VERIFY -> commit ONE thread of each pair before beginning the
other, so the second implements on a clean tree. WI-5105 tracks the coordination
item; this advisory supplies its root cause and fix direction.

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
