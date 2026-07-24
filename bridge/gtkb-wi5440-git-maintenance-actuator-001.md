NEW
::init gtkb lo
::open build

# gtkb-wi5440-git-maintenance-actuator — Governed git-maintenance actuator + bounded orphan sweep for `groundtruth_kb.git_lifecycle`

bridge_kind: prime_proposal
Document: gtkb-wi5440-git-maintenance-actuator
Version: 001
Author: Prime Builder (Claude, harness B)
Date: 2026-07-22 UTC

author_identity: prime-builder/claude
author_harness_id: B
author_session_context_id: 76893073-8a33-4a45-befc-b78ec55b3920
author_model: claude-opus-4-8
author_model_version: claude-opus-4-8
author_model_configuration: Claude Code interactive; resolved role prime-builder via ::init gtkb pb

Project Authorization: PAUTH-PROJECT-GTKB-HOUSEKEEPING-HARDENING-WI5440-GIT-MAINTENANCE-ACTUATOR-20260722
Project: PROJECT-GTKB-HOUSEKEEPING-HARDENING
Work Item: WI-5440

target_paths: ["groundtruth-kb/src/groundtruth_kb/git_lifecycle/maintenance.py", "groundtruth-kb/src/groundtruth_kb/git_lifecycle/__main__.py", "platform_tests/scripts/test_git_lifecycle_maintenance.py"]

implementation_scope: source
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

---

## Summary

GT-KB currently has **no sanctioned way to perform git object-store maintenance**. The
implementation-start gate (`scripts/implementation_start_gate.py`, `_direct_git_effect_from_payload`
at L1327 / block at L1501-L1512) rejects direct `git` maintenance effects with
`BLOCKED (GTKB-GIT-LIFECYCLE)` and redirects the caller to
`python -m groundtruth_kb.git_lifecycle` "so current authority, scope binding, quiescence,
recovery, and evidence are enforced at effect time." That module exposes only
`restore | create | attach | show | validate | preserve | promote | close | resume | recover | drain` —
every one of which governs **work-item branch/scope lifecycle** or **dispatcher drain**. There is
no `gc`, `prune`, `repack`, `reflog expire`, `worktree prune`, or orphan sweep. The gate was built
ahead of the actuator, so the redirect currently resolves to a capability that does not exist and
sanctioned reclamation is impossible.

Measured live at HEAD on 2026-07-22 via `git count-objects -vH`: **17,027 loose objects / 60.92 GiB**,
**275 packs / 34.28 GiB**, **96 garbage files / 9.21 GiB**, `prune-packable: 1` — roughly 104.4 GiB
total, against 208.1 GiB free on the volume. Two independent baselines put regrowth at ~5-7 GB/day
(`DELIB-202666764` forensics: 69.3 GB on 2026-07-17; WI-5431 `status_detail`: 80.29 GiB on
2026-07-17). The 9.21 GiB of `tmp_obj_*` / `tmp_pack_*` garbage is physical evidence of an
interrupted maintenance run.

This proposal delivers **only the actuator** — the sanctioned capability. It deliberately does
**not** perform the reclaim and does **not** untrack `groundtruth.db`; both belong to WI-5431, which
depends on this work item. Scope is held to one new module plus minimal CLI wiring so it does not
overlap the live `gtkb-wi5344-git-lifecycle-bounded-process-tree` thread (currently `NO-GO` at
version 014) in this same package; `service.py` is deliberately excluded from `target_paths`.

Proposed surface — a `maintenance` operation with three subverbs:

1. `plan` — read-only. Enumerates what would be reclaimed (loose/garbage/reflog/worktree
   candidates) and emits evidence. Default, non-mutating.
2. `run` — mutating, fail-closed. Preconditions: (a) a bounded dispatcher drain lease is held, per
   `DCL-DISPATCHER-QUIESCENCE-LEASE-001`, composing the existing `drain acquire` rather than
   inventing a second quiescence mechanism; (b) a pre-flight open-handle check on target paths,
   reporting rather than forcing. Writes an operation journal **before** acting so an interrupted
   run is recoverable.
3. `recover` — resumes or cleans partial state from an interrupted run, including bounded removal
   of orphaned `tmp_obj_*` / `tmp_pack_*` garbage above an age threshold.

Non-destructive invariants enforced in code: never rewrites history, never force-pushes, never
introduces Git LFS, and never removes reachable objects — matching the owner constraints recorded
in the governing PAUTH's `forbidden_operations`.

## Specification Links

- `GOV-WORK-TREE-HYGIENE-001` — Work-Tree Hygiene Governance. The governing hygiene authority for
  worktree and object-store cleanliness; `worktree prune` is one of the actuator verbs and must
  prune only stale registrations, never a live worktree.
- `DCL-DISPATCHER-QUIESCENCE-LEASE-001` — Bounded dispatcher quiescence lease and drain authority.
  The actuator must not mutate the object store without a held bounded drain lease; it composes the
  existing `drain` verb rather than adding a parallel quiescence path.
- `GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001` — GT-KB modernization must be intuitive and
  non-impairing. The actuator is purely additive; all existing `git_lifecycle` verbs must remain
  behaviorally unchanged.
- `DCL-GIT-BRANCH-BINDING-PROMOTION-001` — Maintenance must preserve work-item branch bindings and
  their reachable objects; no bound scope may become unreachable as a side effect of maintenance.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — Governs the spec-to-test mapping below and the
  execution evidence required before `VERIFIED`.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` — Governs the completeness of this
  section.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` — Governs the `Project Authorization` /
  `Project` / `Work Item` linkage lines above.
- `GOV-FILE-BRIDGE-AUTHORITY-001` — Governs append-only bridge filing and the dispatcher/TAFE state
  publication for this thread.
- `GOV-STANDING-BACKLOG-001` — WI-5440 is the MemBase backlog authority for this work.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` — This work converts an ad hoc, gate-blocked operational
  need into a durable governed capability with recorded evidence, per artifact-oriented governance.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` — The actuator emits durable operation journals and
  evidence rather than leaving maintenance as untracked session activity.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` — Lifecycle states are explicit: this proposal is `NEW`,
  WI-5440 is `open`, and the dependent WI-5431 reclaim remains blocked until this lands.

## Prior Deliberations

- `DELIB-202666764` — **Governing owner decision** (2026-07-17, `outcome: owner_decision`,
  `work_item: WI-5431`): authorizes non-destructive reclaim of ~60 GB dangling objects, finishing
  the 2026-04-24 DB untrack decision (keep history; LFS retired), *and* the housekeeping-hardening
  program explicitly naming a "git-maintenance actuator". This proposal implements that named track
  and nothing beyond it.
- `DELIB-20260704-EMERGENCY-GIT-OBJECT-GARBAGE-CLEANUP` — The 2026-07-04 disk-exhaustion outage that
  blocked GT-KB operation. Establishes urgency and the precedent that ad hoc emergency cleanup is
  the failure mode this actuator exists to replace with a governed path.
- `DELIB-20262499` — **Prior Loyal Opposition NO-GO on FAB-04 storage reclamation**
  (`bridge/gtkb-fab-04-storage-reclamation-006.md`). Two blocking causes: worktree deletion deferred
  due to *stranded drafts and handle locks*, and a clause-preflight evidence gap. This proposal
  differs by treating those preconditions as first-class product: the open-handle pre-flight check
  and the journal/`recover` path exist specifically because that prior attempt failed on them.
- `DELIB-FAB04-REMEDIATION-20260610` — Prior owner AUQ authorizing a full `.git` maintenance pass for
  WI-4416/FAB-04. Establishes that a maintenance pass is an owner-sanctioned class of work; this
  proposal supplies the governed mechanism that attempt lacked.
- `INTAKE-c5792b0c` — Confirmed intake: governed Git lifecycle and bounded dispatcher coordination.
  The intake under which the `git_lifecycle` package and its drain authority were established; this
  work extends that package along its existing grain.

## Owner Decisions / Input

This proposal depends on owner approval and is authorized by:

1. `DELIB-202666764` (2026-07-17, `outcome: owner_decision`) — owner authorization of the
   housekeeping-hardening program including the git-maintenance actuator track.
2. Owner AskUserQuestion, 2026-07-22 (this session): *"New PAUTH scoped to WI-5440"* — authorized
   creating `PAUTH-PROJECT-GTKB-HOUSEKEEPING-HARDENING-WI5440-GIT-MAINTENANCE-ACTUATOR-20260722`
   citing `DELIB-202666764`, deliberately scoped to WI-5440 alone and excluding WI-5441/WI-5442.
3. Owner directive, 2026-07-22: non-destructive only — no history rewrite, no force-push, no Git
   LFS. Encoded mechanically as `forbidden_operations` on the PAUTH above.
4. Owner correction, 2026-07-22: there is no drive syncing on `E:`. Recorded because it removes any
   sync-pause precondition from the maintenance window design. The handle-lock precondition stands
   independently on the `DELIB-20262499` evidence.

## Requirement Sufficiency

**Existing requirements sufficient.** The governing requirements are `GOV-WORK-TREE-HYGIENE-001`
(hygiene authority), `DCL-DISPATCHER-QUIESCENCE-LEASE-001` (quiescence precondition),
`GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001` (additive, non-impairing change), and
`DCL-GIT-BRANCH-BINDING-PROMOTION-001` (binding preservation), together with the owner decision
`DELIB-202666764`. No new or revised requirement is needed before implementation; this work supplies
a missing mechanical capability that existing specifications already presuppose.

## Spec-Derived Verification Plan

All tests land in `platform_tests/scripts/test_git_lifecycle_maintenance.py` and run with the repo
venv interpreter:

```text
groundtruth-kb/.venv/Scripts/python.exe -m pytest platform_tests/scripts/test_git_lifecycle_maintenance.py -q --no-header
```

| Specification | Derived test | Expected result |
|---|---|---|
| `DCL-DISPATCHER-QUIESCENCE-LEASE-001` | `test_run_without_drain_lease_fails_closed` | `maintenance run` refuses to mutate when no bounded drain lease is held; non-zero exit, no object-store write. |
| `DCL-DISPATCHER-QUIESCENCE-LEASE-001` | `test_run_composes_existing_drain_lease` | With a held lease, `run` proceeds and releases correctly; no second quiescence mechanism is introduced. |
| `GOV-WORK-TREE-HYGIENE-001` | `test_worktree_prune_removes_only_stale_registrations` | Stale worktree registrations pruned; a live registered worktree is preserved. |
| `GOV-WORK-TREE-HYGIENE-001` | `test_orphan_sweep_bounded_to_tmp_artifacts` | Sweep removes only `tmp_obj_*` / `tmp_pack_*` above the age threshold; never a valid loose object. |
| `DCL-GIT-BRANCH-BINDING-PROMOTION-001` | `test_maintenance_preserves_bound_workitem_refs` | After `run`, every bound work-item branch/ref remains resolvable and its objects reachable. |
| `GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001` | `test_existing_lifecycle_verbs_unchanged` | Regression over the pre-existing verb surface; behavior and exit codes unchanged. |
| `GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001` | `test_plan_is_read_only` | `plan` performs no mutation; object counts identical before/after. |
| (owner constraint, PAUTH `forbidden_operations`) | `test_no_history_rewrite_or_lfs_paths` | No code path invokes history-rewriting, force-push, or LFS verbs. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | this table + executed evidence in the post-implementation report | Every linked spec has an executed derived test before `VERIFIED`. |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | thread chain under `bridge/` | Append-only numbered chain; dispatcher/TAFE state published by the governed writer. |

Interruption-safety is verified by `test_recover_cleans_partial_run`, which simulates an aborted
`run` and asserts `recover` restores a consistent state — the failure class that produced the
current 9.21 GiB of garbage.

Code-quality gates run on changed Python before the post-implementation report is filed:

```text
groundtruth-kb/.venv/Scripts/python.exe -m ruff check <changed.py>
```

```text
groundtruth-kb/.venv/Scripts/python.exe -m ruff format --check <changed.py>
```

## Risk / Rollback

**Risk surface.** The actuator is additive: a new `maintenance.py` module plus CLI wiring in
`__main__.py`. No existing verb is modified, and `service.py` is deliberately outside
`target_paths`. The mutating `run` path is the only real risk; it is gated behind a required drain
lease, an open-handle pre-flight, and a pre-write journal, and `plan` (read-only) is the default
entry point. This proposal performs **no reclamation** — landing it changes no object-store state.

**Concurrency.** `gtkb-wi5344-git-lifecycle-bounded-process-tree` is live at `NO-GO` in this same
package. Its latest declared target envelope is empty, and this proposal's envelope avoids the files
that thread is most likely to revise. If WI-5344 revises into `__main__.py`, the two threads must be
sequenced; that is flagged here for reviewer attention rather than assumed away.

**Rollback.** Single-commit revert. Because the change is additive and performs no reclamation,
reverting removes the new verb and restores the prior surface exactly; no data migration, no history
rewrite, and no state to unwind.

## Intuitiveness/Non-Impairment Disposition

```json
{
  "schema_version": 1,
  "applicability": "applicable",
  "provenance": "WI-5440 under PROJECT-GTKB-HOUSEKEEPING-HARDENING, authorized by PAUTH-PROJECT-GTKB-HOUSEKEEPING-HARDENING-WI5440-GIT-MAINTENANCE-ACTUATOR-20260722 and owner decision DELIB-202666764 (2026-07-17), which names the git-maintenance actuator as an authorized track.",
  "canonical_authority": "GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001, with DCL-DISPATCHER-QUIESCENCE-LEASE-001 for quiescence and GOV-WORK-TREE-HYGIENE-001 for worktree/object-store hygiene.",
  "primary_route": "python -m groundtruth_kb.git_lifecycle maintenance {plan|run|recover}",
  "before_behavior": "Direct git gc/prune/repack/reflog-expire/worktree-prune is blocked by GTKB-GIT-LIFECYCLE at implementation_start_gate.py L1501-L1512 and redirected to groundtruth_kb.git_lifecycle, which exposes only branch-lifecycle and drain verbs. The redirect names a capability that does not exist, so sanctioned object-store maintenance is impossible.",
  "after_behavior": "The existing redirect resolves to a real verb. Operators get read-only plan, quiescence-gated run, and recover. Every pre-existing git_lifecycle verb is behaviorally unchanged.",
  "self_descriptive_naming": "Verb named 'maintenance' with subverbs plan/run/recover, consistent with the existing imperative verb naming in the package (create, attach, preserve, promote, drain, recover) and with the gate's own redirect wording.",
  "obsolete_guidance_disposition": "No guidance becomes obsolete. Existing instructions to avoid ad hoc git gc/prune remain correct and enforced; this proposal supplies the sanctioned route those blocks already point at.",
  "history_preservation": "No history rewrite, no force-push, no Git LFS. Reachable objects are never removed. Only unreachable garbage (tmp_obj_*, tmp_pack_*) above an age threshold is swept, and work-item branch bindings are preserved per DCL-GIT-BRANCH-BINDING-PROMOTION-001.",
  "baseline": "git count-objects -vH measured 2026-07-22: 17027 loose objects / 60.92 GiB; 275 packs / 34.28 GiB; 96 garbage files / 9.21 GiB; prune-packable 1; 208.1 GiB free on volume.",
  "expected_result": "Landing this proposal changes no object-store state; it adds the capability only. Success is the derived pytest suite at platform_tests/scripts/test_git_lifecycle_maintenance.py passing, plus ruff check and ruff format --check clean on changed files.",
  "rollback": "Single-commit revert. The change is additive (one new module plus CLI wiring) and performs no reclamation, so reverting restores the prior surface exactly with no data migration and no state to unwind.",
  "hard_invariants": [
    "never rewrites history",
    "never force-pushes",
    "never introduces Git LFS",
    "never removes reachable objects",
    "run requires a held bounded dispatcher drain lease",
    "plan is read-only and is the default entry point"
  ],
  "fail_closed_conditions": [
    "no bounded dispatcher drain lease held when run is invoked",
    "open handles detected on target paths during pre-flight",
    "operation journal cannot be written before any mutation",
    "a worktree registration cannot be proven stale",
    "an object cannot be proven unreachable"
  ],
  "essential_context_preservation": "Plan and run emit operation journals and evidence under .gtkb-state so an interrupted maintenance run is both diagnosable and recoverable. That missing journal is precisely what produced the current 9.21 GiB of orphaned tmp_obj_* garbage and what blocked the prior FAB-04 attempt recorded in DELIB-20262499."
}
```

## Bridge Filing

This proposal is filed under `bridge/` as the next status-bearing numbered
bridge file for `gtkb-wi5440-git-maintenance-actuator`; no prior version is deleted or rewritten
(append-only). Dispatcher/TAFE state plus the numbered file chain are the live
workflow state per `GOV-FILE-BRIDGE-AUTHORITY-001`.

## Recommended Commit Type

`feat` — this adds a new module and a new operator-facing capability (the `maintenance` verb) that
does not exist today. It is not `chore`: the diff introduces net-new sanctioned functionality that
unblocks a dependent work item, and mislabeling it would misrepresent the change to
commit-history-driven tooling.

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
