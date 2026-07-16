---
name: gtkb-hygiene-reclaim
description: Use only from an active GT-KB ops activity envelope (`::open ops`) when planning, deep-cleaning, reviewing, trashing, purging, restoring, or auditing GT-KB hygiene-reclaim candidates through the production gt hygiene reclaim plan/history/deep-clean/trash/purge/restore CLI with registry, Git-root, ops-evidence, and quiescence gates.
allowed-tools: Bash, Read
license: "Proprietary - Remaker Digital"
metadata:
  project: groundtruth-kb
  category: hygiene-reclaim
---

# GT-KB Hygiene Reclaim

Use this skill to orchestrate the production `gt hygiene reclaim` command
family. Keep repeatable discovery, hashing, revalidation, state transitions,
and history reconstruction in the deterministic CLI rather than reproducing
them in model context.

This is an **ops-envelope-only** skill. Use it only after the current worker has
opened the `ops` activity envelope. If a request for deep cleaning arrives
outside `::open ops`, open or require the ops envelope before loading or acting
on this skill.

## When To Use

- Run an autonomous ops deep clean that leaves the GT-KB directory clean and
  tidy without per-batch owner interaction.
- Create a compact, read-only reclaim plan and inspect registry/Git readiness
  while the ops envelope is active.
- List reclaim history or inspect one exact run or item when needed.
- Prepare one exact, reversible trash batch for owner decision.
- Permanently purge exact receipted trash payloads after separate owner
  authorization when physical disk space must be reclaimed.
- Restore exact previously trashed items after validating their recorded state.
- Verify trash, purge, or restore results against append-only history.

## When Not To Use

- Do not use this skill for general configured-string hygiene scans; use
  `gtkb-hygiene-sweep` for that workflow.
- Do not use this skill from the global baseline or from any activity envelope
  other than `ops`.
- Do not create or invoke a private reclaim script or duplicate CLI. The
  production `gt hygiene reclaim` interface is the only execution surface.
- Do not use this skill as cleanup approval. Planning and history are read-only;
  actuators require exact ops-envelope evidence and quiescence evidence. When
  the current ops directive authorizes autonomous deep cleaning, use that as the
  batch evidence instead of asking the owner for per-item or per-batch approval.

## Compact Read-Only Start

Start with a fresh compact plan:

```powershell
gt hygiene reclaim plan --json
```

Initially ingest only the compact summary: run ID, plan hash, candidate count,
logical bytes, registry readiness, Git readiness, executable status, and blocker
codes. Do not load the complete manifest or every candidate payload into model
context. Read-only planning may continue when readiness is non-passing, but a
known or newly discovered non-passing registry state blocks live trash until
the registry is corrected and a fresh plan passes.

Use compact history to orient without opening all run payloads:

```powershell
gt hygiene reclaim history --json
```

Inspect exact details only when they are needed for a proposed batch or a
verification question:

```powershell
gt hygiene reclaim history --run-id <run-id> --json
gt hygiene reclaim history --run-id <run-id> --item-id <item-id> --json
```

Keep the read-only `plan` and `history` phase separate from `deep-clean`,
`trash`, `purge`, and `restore` actuator phases. A candidate count, size, age,
ignored status, untracked status, or unreachable status is never actuation
authority.

## Preservation Invariants

Every registry match is a preservation veto; absence from the registry is not
trash authority. Git tracked/ignored/untracked state is discovery and diagnostic
evidence only; it is not the SoT for whether a known junk path is load-bearing.
Preserve all Git roots, including refs, worktree HEADs, stashes, valid reflog
object IDs, and every index stage. Preserve bridge files, numbered bridge
history, manifests, append-only events, receipts, and other audit history.
Refuse ambiguous, malformed, contradictory, newly reachable, changed,
out-of-root, cross-device, active-session, registered, or protected candidates.

## Exact Trash Decision

For routine ops deep cleaning, prefer `gt hygiene reclaim deep-clean` and do
not present per-batch owner decisions. This exact-batch decision path is for
manual/non-deep-clean exceptions.

Before presenting a trash decision, inspect only the exact run and proposed
item IDs. Confirm all of the following:

- the immutable plan hash exactly matches the selected run;
- the exact item IDs and their identity hashes are fixed for this batch;
- registry readiness and Git-root readiness are passing and current;
- batch-specific owner evidence and apply evidence can bind the same run ID,
  plan hash, and item IDs;
- fresh quiescence evidence can cover the operation window;
- the current authorization permits this exact live actuator operation.

Present one owner decision at a time in this form, then stop and wait:

> [!IMPORTANT]
> **OWNER ACTION REQUIRED**
>
> **Decision:** Approve or reject this exact reversible trash batch.
>
> **Why it matters:** Trash moves only the listed items out of active scan paths.
> A same-volume trash move frees zero physical bytes.
>
> **Exact batch:** Run `<run-id>`; plan hash `<plan-hash>`; item IDs
> `<item-id-1>, <item-id-2>`; logical bytes `<bytes>`; physical bytes reclaimed
> `0`.
>
> **Evidence:** Registry/Git readiness `<result>`; quiescence `<reference>`;
> owner/apply record target `<reference>`.
>
> **Reply:** `APPROVE <run-id> <plan-hash> <comma-separated-item-ids>` or
> `REJECT <brief reason>`.

Approval in conversation is not itself sufficient actuator input. Capture or
obtain non-empty, batch-specific owner and apply evidence through the governed
path required by the current authorization. Both references must bind the exact
run ID, plan hash, and item IDs shown to the owner.

## Ops Deep Clean

Use the deterministic deep-clean actuator for the regular ops hygiene task. It
plans, trashes, purges, and replans until the production planner returns zero
candidates or the configured cycle bound is hit:

```powershell
gt hygiene reclaim deep-clean --help
gt hygiene reclaim deep-clean --owner-evidence <ops-envelope-evidence-ref> --quiescence-evidence <quiescence-evidence-ref> --json
```

Before running it, record fresh quiescence evidence and an exact ops-envelope
evidence reference. Do not ask the owner to approve individual batches when the
current ops directive authorizes autonomous deep cleaning. Stop only for a CLI
refusal, non-executable plan, cycle bound, quiescence failure, registry/Git
readiness blocker, or direct owner stop instruction.

After it finishes, verify:

- final status is `clean`;
- final candidate count is `0`;
- reclaim trash payload count is `0`;
- append-only histories validate with no corrupt or partial runs;
- `trashed_remaining` reconstructed from history is `0`;
- physical bytes reclaimed and current disk free are reported separately.

## Actuator Contract

Use command help to confirm the installed contract, then pass the exact run,
plan hash, repeated exact item IDs, batch-specific owner and apply evidence,
and quiescence evidence to the production command. The production CLI carries
the owner and apply references as repeatable `--owner-evidence` values:

```powershell
gt hygiene reclaim trash --help
gt hygiene reclaim trash --run-id <run-id> --plan-hash <plan-hash> --item-id <item-id> --owner-evidence <owner-evidence-ref> --owner-evidence <apply-evidence-ref> --quiescence-evidence <quiescence-evidence-ref> --json
```

Immediately before each move, require the CLI's operation-time revalidation of
root identity, plan/item hashes, registry matches, Git roots, candidate state,
destination safety, authorization, and quiescence. Stop on any refused or
partial result. Same-volume reversible trash removes logical bytes from active
scan paths but reclaims **zero physical bytes** from the volume.

Purge only exact receipted trash payloads, never an inferred directory or
wildcard. Purge is irreversible for the payload and is the governed phase that
reclaims physical disk bytes:

```powershell
gt hygiene reclaim purge --help
gt hygiene reclaim purge --run-id <run-id> --plan-hash <plan-hash> --item-id <item-id> --owner-evidence <purge-owner-evidence-ref> --quiescence-evidence <quiescence-evidence-ref> --json
```

Require operation-time validation of the event chain, plan hash, current
trashed state, trash receipt, payload containment, payload identity hash, source
absence, authorization, and quiescence. Stop on any refused or partial result.
After purge, `restore` must refuse the item because the payload no longer
exists.

Restore only exact recorded items, never an inferred directory or wildcard:

```powershell
gt hygiene reclaim restore --help
gt hygiene reclaim restore --run-id <run-id> --item-id <item-id> --json
```

Require operation-time validation of payload identity, event history, original
path, destination absence, path containment, and current authorization. Refuse
overwrite, missing or changed payload, path escape, or an active destination.

After `trash`, `purge`, or `restore`, verify append-only history for every
exact item and the batch receipt:

```powershell
gt hygiene reclaim history --run-id <run-id> --json
gt hygiene reclaim history --run-id <run-id> --item-id <item-id> --json
```

Report planned, trashed, purged, restored, refused, partial, stale, corrupt, or
unsupported state exactly as recorded. Do not reinterpret a non-passing state
as success.

## Ops Envelope Boundary

The `ops` activity profile is the surfacing gate for this skill. Workers with
an opened ops envelope may use `gt hygiene reclaim deep-clean` autonomously when
the current ops directive asks for regular deep cleaning or disk clearing. Other
activity envelopes must not use this skill; they should open `ops` or hand off
to an ops worker.

## Forbidden Operations

This skill must never perform or recommend:

- unreceipted purge, wildcard deletion, or purge outside
  `gt hygiene reclaim purge`;
- `git gc`, Git prune/worktree prune, or `git reflog expire` as part of this
  skill;
- stash deletion (`git stash drop` or `git stash clear`);
- branch deletion, including `git branch -d` or `git branch -D`;
- commit, push, release, or deployment;
- credential creation, reading, changing, rotation, upload, or disclosure.

The skill does not mutate the SoT registry, Git roots, bridge history, audit
history, generated Codex adapter, manifest, capability registry, or scenario
router. Route any needed correction or integration through its separately
authorized owner.

## Verification Evidence

Record the compact plan result, exact run ID and plan hash, exact item IDs,
registry/Git readiness, decision evidence, apply evidence, quiescence evidence,
operation-time revalidation result, actuator receipt when authorized, and
post-operation history verification. Clearly separate logical bytes moved from
physical bytes reclaimed.

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
