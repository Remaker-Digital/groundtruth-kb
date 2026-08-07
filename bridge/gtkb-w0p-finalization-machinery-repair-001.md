NEW
::init gtkb pb
::open build
author_identity: prime-builder/claude
author_harness_id: B
author_session_context_id: d8a2e6f9-d4dd-4b89-a0bd-bbcda10b4452
author_model: claude-fable-5
author_model_version: claude-fable-5
author_model_configuration: Claude Code interactive; resolved role prime-builder via ::init gtkb pb; activity build

bridge_kind: prime_proposal
Document: gtkb-w0p-finalization-machinery-repair
Version: 001
Date: 2026-08-07 UTC
Project Authorization: PAUTH-PROJECT-GTKB-BRIDGE-PROTOCOL-RELIABILITY-WHOLE-PROJECT-20260730
Project: PROJECT-GTKB-BRIDGE-PROTOCOL-RELIABILITY
Work Item: WI-5977
target_paths: [".claude/skills/gtkb-verify/helpers/write_verdict.py", "scripts/gtkb_bridge_writer.py", "groundtruth-kb/src/groundtruth_kb/project/registry_control_plane.py", "platform_tests/scripts/test_write_verdict_refinalize.py", "platform_tests/scripts/test_bridge_writer_withdrawn_mapping.py", "platform_tests/scripts/test_bridge_publication_preimage_scoping.py", "platform_tests/scripts/test_capability_crash_recovery_consumption.py"]

# Worker 0-prime — Finalization Machinery Repair (stranded-VERIFIED re-entry, capability crash recovery, WITHDRAWN filing, WI-5977 preimage scoping)

## Summary

Two owner custodial `--no-verify` interventions were required within 24 hours
(single-thread finalization at commit `86baa93ed`; 8-thread batch at
`a8ab14b60..77775f9a7`) because the VERIFIED finalization machinery cannot
recover its own failure states. Production rate exceeded finalization rate
~10:1 in one worker/LO cycle. This proposal makes the governed tooling able to
finalize a stranded file-only VERIFIED end-to-end with zero owner terminal
intervention, including under concurrent-session contention. Owner priority
decision: DELIB-20260806011899 (machinery repairs promoted into Wave 1);
after-action evidence: bridge/gtkb-w0-plumbing-stranded-finalization-afteraction-001.md
and bridge/gtkb-w0-batch-finalization-afteraction-001.md.

## Live Anchor Evidence (verified 2026-08-07)

1. Re-entry deadlock (register F-128): `_assert_verification_ready` in
   `.claude/skills/gtkb-verify/helpers/write_verdict.py` raises
   `VerifiedFinalizationError: VERIFIED finalization requires a
   post-implementation report latest status of NEW, REVISED, or NO-ACTION; got
   VERIFIED at bridge/gtkb-w0-worker-enablement-plumbing-006.md` (owner
   terminal reproduction, 2026-08-07). A crashed finalization strands a
   terminal verdict that then blocks its own recovery. NOTE: this file is
   currently dirty with gtkb-w0-skill-rename-path-repair worktree changes;
   implementation of THIS thread is sequenced strictly after that thread's
   finalization (see Sequencing).
2. Capability crash state: `registry_control_plane.py:3272-3330` marks
   `capability_state = 'recovery_required'`; recovery entrypoints
   `recover_bridge_publication` / `compensate_bridge_publication` exist but are
   not wired into any verdict-finalization re-entry path. Observed gate
   refusal: "bridge publication capability is not consumed
   ('recovery_required')" (owner terminal, 2026-08-07).
3. Stale evidence hash: gate refusal "Verdict applicability freshness check
   rejected a stale packet_hash; expected sha256:25eaf886... for
   bridge/gtkb-w0-worker-enablement-plumbing-005.md" — no governed restamp
   path exists (wi5826-class).
4. WITHDRAWN filing gap (register F-130): `scripts/gtkb_bridge_writer.py:351`
   and `:386` raise `bridge status WITHDRAWN has no formal responder-role
   envelope mapping` — audit-record statuses cannot be filed through the
   governed writer and therefore receive no publication capability.
5. WI-5977 root cause (owner-verified open P0): bridge publication compensation
   gates on a whole-aggregate (15,532-file) preimage digest that ANY concurrent
   bridge write invalidates; live failure text at `gtkb_bridge_writer.py:1052`
   ("aggregate preimage; file and claim are retained") and transcript evidence
   `BridgePublicationError: bridge aggregate preimage is not current`
   (friction investigation P8, loop 15).

## Proposed Change

1. (Slice A — re-entry) Add `--refinalize-existing` mode to
   `write_verdict.py`: when thread-latest is a terminal VERIFIED that is
   untracked or whose declared same-transaction set is dirty, validate the
   EXISTING verdict body via `validate_verified_body()`, re-derive its declared
   path set, repair its publication capability (Slice A2), and create the
   same-transaction commit. No new verdict version is written; append-only
   history is preserved. Harden the crash path: the existing fail-closed
   cleanup wraps the full mint-to-commit span so a crash can no longer strand a
   consumed-less verdict silently (register F-127 root).
2. (Slice A2 — capability recovery) Wire `recover_bridge_publication` into the
   refinalize path: a `recovery_required` capability for the exact verdict
   path/digest is finalized (content-matched) or compensated-and-reminted
   before commit. No change to mint ceilings or TTL policy (WI-5839 scope
   untouched).
3. (Slice B — evidence restamp) During refinalize, when the predecessor
   report's applicability packet_hash fails freshness solely because the
   packet was regenerated after verdict authoring, recompute the packet against
   the committed predecessor bytes and restamp the comparison hash in the
   TRANSACTION EVIDENCE (not in the committed verdict body — append-only
   preserved), recording old/new hashes in the finalization log.
4. (Slice C — WITHDRAWN mapping) Add a formal responder-role envelope mapping
   for `WITHDRAWN` (and `DEFERRED`) audit/parking statuses to
   `gtkb_bridge_writer.py` (role: filer's resolved role; activity: build),
   so audit records file through the governed writer and receive publication
   capabilities. Unblocks governed filing of after-action records (F-130).
5. (Slice D — WI-5977 preimage scoping) Replace the whole-aggregate preimage
   gate in the publication compensation path with a THREAD-SCOPED preimage
   (digest over the thread's own numbered files only). Concurrent writes to
   unrelated threads no longer invalidate an in-flight publication. Retry
   semantics and the retained-file-and-claim failure contract are unchanged.
6. Tests (4 new modules per target_paths): refinalize end-to-end on a fixture
   stranded VERIFIED (crash-injected mint, dirty declared set); recovery
   consumption state machine; WITHDRAWN/DEFERRED writer mapping + capability
   mint; preimage scoping under simulated concurrent unrelated write (the
   WI-5977 reproduction) plus same-thread conflict still failing closed.

## Sequencing

Implementation begins only after `gtkb-w0-skill-rename-path-repair` reaches
VERIFIED and its finalization commits land (its dirty set includes
`write_verdict.py`). `gtkb_bridge_writer.py` and `registry_control_plane.py`
are clean at HEAD as of filing. The sibling GO'd thread
`gtkb-w0-executable-go-pre-verdict-validation` touches the verdict path's
GO-emission region; hunks are disjoint from Slices A-C (finalization/refinalize
region); its implementer re-verifies anchors at implementation start.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` — finalization durability and audit-trail
  authority this repairs; permanent bridge repair authority.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` — triggered by the
  `groundtruth-kb/src/groundtruth_kb/project/**` target; all changes remain
  in-root platform code with no application-subtree coupling.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` — this section is
  the mechanically-enforced linkage surface; every governing artifact above and
  below is cited concretely.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — the Specification-Derived
  Verification Plan maps every linked requirement to an executable test; the
  eventual VERIFIED requires their execution evidence.
- `.claude/rules/file-bridge-protocol.md` § Mandatory VERIFIED
  Commit-Finalization Gate — the contract Slice A restores reachability for.
- `.claude/rules/governance-emergency-bootstrap-protocol.md` — the exception
  lane this proposal is designed to retire from routine use.
- `DCL-NO-ACTION-STATUS-SEMANTICS-001` — status-semantics boundary respected by
  Slice C (WITHDRAWN/DEFERRED mappings only; no verdict-status changes).
- WI-5977 (P0, PROJECT-GTKB-BRIDGE-PROTOCOL-RELIABILITY) — Slice D is its
  direct fix.
- WI-5839 thread (`bridge/gtkb-wi5839-capability-ttl-sizing-*`) — adjacent TTL
  scope explicitly NOT modified here.
- Friction register F-127/F-128/F-130/F-131/F-132
  (`.gtkb-state/friction-investigation/findings-register.md`) — evidence base.

## Prior Deliberations

- `DELIB-20260806011899` — owner decision promoting machinery repair into
  Wave 1 (batch finalization capture).
- `DELIB-20260806011898` — single-thread custodial finalization capture
  (plumbing incident; the motivating failure).
- `DELIB-202667661` — WI-5688 terminal finalization recovery verdict (prior
  recovery-lane precedent).
- `DELIB-202667451` — WI-5657 audit-only finalization recovery (audit-record
  filing precedent for Slice C).
- `DELIB-202667242` — NO-GO on WI-5468 verdict-publication terminal
  finalization repair: prior rejected approach acknowledged; this proposal
  differs by repairing recovery states in-place (no verdict reissue) and by
  scoping the preimage rather than retrying against the whole aggregate.
- `DELIB-202668159` — WI-5881 durable cross-process bridge recovery
  reservations (reservation semantics Slice A2 builds on).

## Owner Decisions / Input

- AUQ 2026-08-07 "Scripted per-thread batch (Recommended)" — the custodial
  batch whose repetition this proposal eliminates (DELIB-20260806011899).
- Owner directive 2026-08-06 (DELIB-20260806011872): Dispatcher Next priority;
  this thread is substrate repair, not legacy dispatcher revival.
- AUQ set 2026-08-05/06 authorizing the W0 program and split-phase execution.

## Requirement Sufficiency

Existing requirements sufficient: GOV-FILE-BRIDGE-AUTHORITY-001 (durable
finalization), WI-5977 (preimage root cause), and the Mandatory VERIFIED
Commit-Finalization Gate define the required behavior; this thread implements
them. No new GOV/SPEC required.

## Specification-Derived Verification Plan

| Requirement | Test | Expected |
|---|---|---|
| Gate reachability (file-bridge-protocol finalization gate) | test_write_verdict_refinalize.py: fixture stranded VERIFIED (crash-injected) -> refinalize | Same-transaction commit created; verdict body byte-identical; second run idempotent no-op |
| Capability recovery (F-130 layer 1) | test_capability_crash_recovery_consumption.py | recovery_required -> consumed for matching digest; mismatched digest fails closed |
| Evidence freshness (F-130 layer 2) | refinalize fixture with regenerated packet | Restamp recorded in transaction evidence; committed verdict unchanged; mismatched predecessor bytes still fail closed |
| WITHDRAWN filing (F-130 layer 3) | test_bridge_writer_withdrawn_mapping.py | Governed write succeeds with capability mint; UNKNOWN statuses still rejected |
| WI-5977 preimage scoping | test_bridge_publication_preimage_scoping.py | Concurrent unrelated bridge write no longer invalidates publication; same-thread concurrent write still fails closed |
| Code quality | ruff check + ruff format --check on all changed .py | Both gates pass |

## Acceptance Criteria

1. A fixture stranded file-only VERIFIED finalizes end-to-end through
   `--refinalize-existing` with zero manual git operations, under a
   concurrently-writing unrelated bridge thread.
2. Only the seven declared target_paths change; timer values, TTL policy,
   protected-commit checker, and verdict bodies are untouched.
3. Append-only invariant: no committed bridge file is modified; refinalize
   never writes a new verdict version.
4. All four new test modules pass; ruff both gates pass.
5. The emergency-bootstrap custodial lane is not required for the next
   stranded-VERIFIED occurrence (demonstrated on fixture; live validation on
   the next real occurrence is post-implementation evidence).

## Risk and Rollback

- Highest-risk slice is D (preimage scoping): compensations currently gated on
  the whole aggregate could admit a publication that a concurrent SAME-thread
  write invalidated. Mitigation: thread-scoped digest still covers every file
  of the publishing thread; the same-thread conflict test asserts fail-closed
  behavior is preserved. Rollback: single-commit revert restores the aggregate
  gate.
- Slice B restamps only transaction evidence, never committed bytes; a
  restamp bug cannot corrupt history. Rollback per-slice: slices are
  independent commits within one thread.

## Intuitiveness/Non-Impairment Disposition

```json
{
  "schema_version": 1,
  "applicability": "applicable",
  "provenance": "WI-5977; GOV-FILE-BRIDGE-AUTHORITY-001; DELIB-20260806011899; register F-127/F-128/F-130/F-132",
  "canonical_authority": "GOV-FILE-BRIDGE-AUTHORITY-001; file-bridge-protocol Mandatory VERIFIED Commit-Finalization Gate",
  "primary_route": "governed finalization tooling recovers its own failure states: refinalize re-entry for stranded terminal verdicts, capability crash-recovery consumption, transaction-evidence hash restamp, WITHDRAWN/DEFERRED writer mappings, thread-scoped publication preimage (WI-5977)",
  "before_behavior": "stranded file-only VERIFIED threads required owner custodial --no-verify commits (twice in 24h, 9 threads); WITHDRAWN audit records unfilable through the governed writer; any concurrent bridge write invalidated in-flight publication compensation via the whole-aggregate preimage",
  "after_behavior": "stranded terminal verdicts finalize through governed tooling with zero owner terminal intervention including under concurrent unrelated writes; audit statuses file governed with publication capability; same-thread conflicts still fail closed",
  "self_descriptive_naming": "write_verdict.py --refinalize-existing; thread-scoped preimage digest in the publication compensation path",
  "obsolete_guidance_disposition": "emergency-bootstrap custodial lane retained for genuine novel deadlocks but retired from routine stranded-VERIFIED use; no rule text deleted",
  "history_preservation": "append-only preserved: refinalize never rewrites committed files or verdict bodies; restamps live in transaction evidence only",
  "baseline": {
    "custodial_interventions_24h": 2,
    "stranded_verified_finalized_custodially": 9,
    "withdrawn_writer_mapping": "absent (gtkb_bridge_writer.py:351,386)",
    "preimage_scope": "whole aggregate, 15532 files (WI-5977)"
  },
  "expected_result": {
    "custodial_interventions_for_stranded_verified": "0 (fixture-proven; live-validated on next occurrence)",
    "withdrawn_writer_mapping": "present with capability mint",
    "preimage_scope": "thread-scoped digest"
  },
  "rollback": "per-slice independent commits; Slice D single-commit revert restores aggregate gate",
  "hard_invariants": "append-only bridge history; fail-closed on digest mismatch and same-thread conflicts; no TTL/timer/checker changes",
  "fail_closed_conditions": "verdict body fails validate_verified_body; capability digest mismatch; predecessor bytes differ from verdict-time claim; same-thread concurrent write during publication",
  "essential_context_preservation": "finalization log records every recovery consumption and restamp with old/new hashes and actor provenance"
}
```

## Cross-Harness Disposition

Canonical helper is `.claude/skills/gtkb-verify/helpers/write_verdict.py`;
`.codex/.cursor/.goose` projections are REGENERATED from canonical post-merge
(same generator used by the rename sweep), not hand-edited. `gtkb_bridge_writer.py`
and `registry_control_plane.py` are single-copy shared surfaces.

## Recommended Commit Type

feat (per-slice commits: feat for A/A2/C/D, fix acceptable for B).

---

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.

---

When you are finished working, close your session envelope by invoking ::wrap.
