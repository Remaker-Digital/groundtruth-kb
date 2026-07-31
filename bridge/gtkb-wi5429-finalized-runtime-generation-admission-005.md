REVISED
::init gtkb lo
::open build
author_identity: prime-builder/codex
author_harness_id: A
author_session_context_id: 019f765b-9cc2-7ae3-bfa1-fc2e2b6fca41
author_model: GPT-5
author_model_version: GPT-5
author_model_configuration: reasoning_effort=high; thread_source=codex-desktop
author_metadata_source: x-codex-turn-metadata

# WI-5429 - Finalized Runtime Generation Admission Revision

bridge_kind: prime_proposal
Document: gtkb-wi5429-finalized-runtime-generation-admission
Version: 005
Responds to: bridge/gtkb-wi5429-finalized-runtime-generation-admission-004.md
Corrects: bridge/gtkb-wi5429-finalized-runtime-generation-admission-001.md
Date: 2026-07-18 UTC

Project Authorization: PAUTH-DISPATCHER-BLACK-BOX-WI5429-FINALIZED-GENERATION-ADMISSION-V2-20260718
Supersedes Authorization: PAUTH-DISPATCHER-BLACK-BOX-WI5429-FINALIZED-GENERATION-ADMISSION-20260717
Project: PROJECT-GTKB-OPS-DISPATCHER-MODERNIZATION-DISPATCHER-BLACK-BOX-HARDENING
Work Item: WI-5429

target_paths: ["scripts/dispatcher_generation_admission.py", "scripts/ensure_dispatcher_daemon.py", "scripts/gtkb_dispatcher_daemon.py", "platform_tests/scripts/test_dispatcher_generation_admission.py", "platform_tests/scripts/test_dispatcher_daemon_supervision.py"]

implementation_scope: source | protocol
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

---

## Revision Claim

This REVISED proposal preserves the WI-5429 generation-admission design from
version 001 and corrects every blocking item in the version 004 NO-GO:

- the malformed PAUTH is replaced by
  `PAUTH-DISPATCHER-BLACK-BOX-WI5429-FINALIZED-GENERATION-ADMISSION-V2-20260718`;
- explicit `ADR-ISOLATION-APPLICATION-PLACEMENT-001/CLAUSE-IN-ROOT` evidence is
  added below;
- Mike's owner decision `DELIB-20260718-DISPATCHER-HOLD-NARROW-WI5429-FIRST`
  establishes the non-circular sequence: WI-5429 first, then WI-5427, then the
  WI-5448/WI-5451 recovery/dependency-closure successors.

This revision authorizes no source or test mutation by itself. Protected target
edits still require an independent Loyal Opposition GO, an exact matching
work-intent claim, schema-v3 implementation-start authorization, operation-time
project-authorization validation, dirty-peer collision clearance, and focused
post-implementation verification.

## Specification Links

- `SPEC-CENTRALIZED-DISPATCH-SERVICE-001` - recovery remains one centralized
  dispatcher service; no alternate queue, poller, or direct harness automation
  is introduced.
- `ADR-DISPATCHER-ARCHITECTURE-001` - admitted-generation execution stays within
  the current supervisor and daemon architecture.
- `DCL-DISPATCHER-DAEMON-SUPERVISION-CONTRACT-001` - recovery must stay
  unattended, hidden on Windows, provenance-checked, idempotent, and
  non-destructive to active work.
- `GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001` - unfinalized dirty runtime bytes
  are rejected by falling back to the last admitted generation, not by disabling
  dispatch or changing harness eligibility.
- `GOV-WORK-TREE-HYGIENE-001` - foreign and unfinalized working-tree bytes remain
  quarantined and cannot become runtime authority.
- `GOV-FILE-BRIDGE-AUTHORITY-001` - implementation requires this REVISED
  proposal, independent GO, exact work-intent claim, implementation-start
  packet, report, and independent verification.
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` - source/test work remains
  inside the corrected PAUTH and operation-time enforcement path.
- `DCL-PROJECT-AUTHORIZATION-ENVELOPE-001` - the corrected PAUTH includes only
  registered forbidden operation tokens and excludes runtime-state/configuration
  mutation by scope and by allowed mutation class.
- `DCL-PROJECT-AUTHORIZATION-OPERATION-TIME-ENFORCEMENT-001` - the implementation
  start packet and protected mutation gate must revalidate the active PAUTH at
  execution time.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - this revision binds
  exact targets, PAUTH, project, work item, and governing requirements.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - the project, PAUTH,
  WI-5429, and target paths are explicit and mechanically checkable.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - verification must prove the
  source of executable runtime bytes with focused admission and supervisor
  tests, not only prose review.
- `DCL-PROJECT-DEPENDENCY-ORDERING-001` - the prior cyclic order is replaced by
  the owner-approved sequence in this revision and by operation-time dirty-peer
  safeguards before shared-file mutation.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - all implementation targets,
  generated artifacts, bridge output, and runtime generation materialization
  stay within the GT-KB root boundary.
- `GOV-STANDING-BACKLOG-001` - WI-5429 and TEST-11540 remain the durable backlog
  and test carriers for the defect.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`,
  `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`, and
  `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - trusted runtime generations are
  durable evidence-backed artifacts with distinct proposal, implementation,
  verification, and activation states.

## Prior Deliberations

- `DELIB-20260715-FLEET-HARNESS-DEFECT-REPAIR-AUTHORIZATION` - owner authorized
  bounded governed repair carriers for newly discovered fleet defects.
- `DELIB-20260717-DISPATCHER-CONFIGURATION-TROUBLESHOOTER-HOLD` - owner held
  dispatcher configuration and live dispatcher runtime-state mutation unless
  later narrowed.
- `DELIB-20260718-DISPATCHER-HOLD-NARROW-WI5429-FIRST` - owner narrowed the hold
  for bounded bridge-governed WI-5429/WI-5427 source/test repair and selected
  WI-5429 first, then WI-5427.
- `bridge/gtkb-wi5429-finalized-runtime-generation-admission-001.md` - original
  generation-admission proposal.
- `bridge/gtkb-wi5429-finalized-runtime-generation-admission-002.md` - invalid
  GO corrected by later Prime/LO entries.
- `bridge/gtkb-wi5429-finalized-runtime-generation-admission-003.md` - Prime
  NO-ACTION identifying clause, PAUTH, and sequence defects.
- `bridge/gtkb-wi5429-finalized-runtime-generation-admission-004.md` - corrected
  LO NO-GO requiring this revision.
- `bridge/gtkb-wi5427-daemon-generation-handoff-006.md` - sibling NO-GO that
  recommends WI-5429 first before WI-5427 refiling.
- `bridge/gtkb-wi5448-dead-daemon-lease-restart-002.md` and
  `bridge/gtkb-wi5451-runtime-dependency-closure-002.md` - approved successor
  threads that remain sequenced after the WI-5429/WI-5427 repair.

## Owner Decisions / Input

`DELIB-20260718-DISPATCHER-HOLD-NARROW-WI5429-FIRST` is the controlling new owner
decision. It narrows the July 17 dispatcher troubleshooter hold only for bounded
bridge-governed WI-5429/WI-5427 source/test work and establishes this sequence:

1. WI-5429 REVISED proposal, independent GO, implementation-start, report, and
   independent verification.
2. WI-5427 revision after WI-5429, with a fresh baseline against the post-WI-5429
   file state and explicit composition with the admission gate.
3. WI-5448 dead-daemon lease restart after the WI-5427/WI-5429 baseline is
   terminally dispositioned.
4. WI-5451 runtime dependency closure after WI-5427 and WI-5448, preserving its
   executable dependency identity scope.

The decision does not authorize direct dispatcher configuration changes, live
daemon restart/activation, runtime-state mutation, TAFE or claim/lease mutation,
eligibility/routing changes, credential work, external-system mutation,
destructive cleanup, Git push, deployment, or release.

## Findings Addressed

### F1 - ADR-ISOLATION-APPLICATION-PLACEMENT-001/CLAUSE-IN-ROOT Evidence

Response: all declared target paths resolve under `E:\GT-KB`:

- `E:\GT-KB\scripts\dispatcher_generation_admission.py`
- `E:\GT-KB\scripts\ensure_dispatcher_daemon.py`
- `E:\GT-KB\scripts\gtkb_dispatcher_daemon.py`
- `E:\GT-KB\platform_tests\scripts\test_dispatcher_generation_admission.py`
- `E:\GT-KB\platform_tests\scripts\test_dispatcher_daemon_supervision.py`

Bridge output is the append-only file
`E:\GT-KB\bridge\gtkb-wi5429-finalized-runtime-generation-admission-005.md`.
The non-dispatchable draft and candidate preflight files stay under
`E:\GT-KB\.gtkb-state\bridge-revisions\drafts\` and
`E:\GT-KB\.tmp\bridge-revisions\`. Runtime generation materialization, if later
implemented after GO/start, stays under
`E:\GT-KB\.gtkb-state\dispatcher-generations\<generation>\`. No generated
artifact, bridge output, test fixture, runtime materialization directory, or
source path is outside `E:\GT-KB`; no Agent Red or external checkout path is
part of this scope.

### F2 - PAUTH Forbidden Operation Token Mismatch

Response: corrected. Active PAUTH
`PAUTH-DISPATCHER-BLACK-BOX-WI5429-FINALIZED-GENERATION-ADMISSION-V2-20260718`
was created on 2026-07-18T20:05:49Z and cites
`DELIB-20260718-DISPATCHER-HOLD-NARROW-WI5429-FIRST`. Its allowed mutation
classes are exactly `bridge`, `metadata`, `source`, `test`, and
`governance_evidence`. Its forbidden operations are registered taxonomy
operations only:

- `credential_lifecycle`
- `destructive_cleanup`
- `dispatcher_mutation`
- `external_system_mutation`
- `git_history_rewrite`
- `git_push`
- `production_deployment`
- `release`

The prior PAUTH
`PAUTH-DISPATCHER-BLACK-BOX-WI5429-FINALIZED-GENERATION-ADMISSION-20260717` was
revoked on 2026-07-18T20:05:56Z as superseded because it carried the
unregistered `tafe_mutation` and `runtime_state_mutation` operation tokens. The
runtime-state and TAFE prohibitions remain in the corrected PAUTH scope prose
and are enforced by excluding `runtime_state` and `configuration` from the
allowed mutation classes plus by the normal protected-path and runtime-state
governance gates.

### F3 - Circular WI-5427 / WI-5429 / WI-5448 / WI-5451 Sequence

Response: corrected by owner decision and by an operation-time safety boundary.
The old circular requirement "WI-5427, WI-5448, and WI-5451 before WI-5429" is
withdrawn from WI-5429. The new sequence is:

1. WI-5429 proceeds first through this corrected REVISED proposal.
2. WI-5427 is revised after WI-5429 reaches the required gate, recomputing its
   target-file baseline against the post-WI-5429 state and describing how its
   handoff-request TTL/self-heal logic composes with generation admission.
3. WI-5448 remains after the WI-5427/WI-5429 shared-file baseline is no longer
   ambiguous.
4. WI-5451 remains after WI-5427 and WI-5448 so executable dependency identity
   can be finalized against stable runtime ownership.

The current dirty-peer guard is not bypassed. If
`scripts/implementation_authorization.py begin --bridge-id gtkb-wi5429-finalized-runtime-generation-admission`
or the protected mutation gate reports a WI-5427 non-terminal implementation
report collision on the overlapping dirty files, Prime Builder must stop before
source/test mutation and file the smallest governed collision-disposition step
needed to clear or explicitly re-scope that stale dirty-byte ownership. Mike's
sequence decision resolves the review-level ordering cycle and hold scope; it
does not create permission to ignore operation-time collision checks.

## Scope Changes

This revision changes only governance evidence and sequence relative to version
001. The technical implementation remains the same high-level WI-5429 design:
add a generation-admission service, materialize trusted runtime bytes from Git
objects, start dead-daemon recovery from the last admitted generation rather
than arbitrary working-tree bytes, and admit newer generations only after
terminal focused provenance.

The revision removes the prior requirement that WI-5427, WI-5448, and WI-5451 be
terminal before WI-5429 proposal approval or source/test implementation. It adds
the explicit WI-5429-first sequence and makes operation-time dirty-peer
collision clearance a hard implementation-start condition.

Out of scope remains unchanged: no live daemon handoff, stop/restart, scheduled
task registration, runtime-state mutation, TAFE mutation, claim/lease mutation,
dispatcher configuration/routing/eligibility change, credential operation,
external-system mutation, destructive cleanup, unrelated source/test/config
mutation, Git history rewrite, Git push, production deployment, or release.

## Requirement Sufficiency

Existing requirements sufficient. The cited dispatcher, supervision,
nonimpairment, bridge-authority, authorization-envelope, project-ordering,
worktree-hygiene, artifact-lifecycle, and in-root placement specifications cover
the corrected WI-5429 design and implementation gates. No new or revised
requirement is needed before Loyal Opposition can review this REVISED proposal.

## Pre-Filing Preflight Subsection

This candidate is filed through
`.codex/skills/bridge/helpers/revise_bridge.py file`, which writes a temporary
candidate under `E:\GT-KB\.tmp\bridge-revisions\`, runs
`scripts/bridge_applicability_preflight.py --bridge-id gtkb-wi5429-finalized-runtime-generation-admission --content-file <candidate> --json`,
runs
`scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-wi5429-finalized-runtime-generation-admission --content-file <candidate>`,
and writes the live append-only bridge file only if both preflights pass. No
source, test, dispatcher, TAFE, runtime, lease, claim, Git, deployment, or
external-system mutation is part of filing this proposal.

## Intuitiveness/Non-Impairment Disposition

```json
{
  "schema_version": 1,
  "applicability": "applicable",
  "provenance": "DELIB-20260718-DISPATCHER-HOLD-NARROW-WI5429-FIRST; PAUTH-DISPATCHER-BLACK-BOX-WI5429-FINALIZED-GENERATION-ADMISSION-V2-20260718; WI-5429; TEST-11540",
  "canonical_authority": "GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001; SPEC-CENTRALIZED-DISPATCH-SERVICE-001; ADR-DISPATCHER-ARCHITECTURE-001; DCL-DISPATCHER-DAEMON-SUPERVISION-CONTRACT-001",
  "primary_route": "Admit dispatcher runtime generations only after terminal focused provenance, materialize exact Git-object bytes under the GT-KB root, and keep recovery on the last admitted generation when a candidate is unfinalized or ambiguous.",
  "before_behavior": "Dead-daemon recovery can execute current working-tree dispatcher runtime bytes even when those bytes are dirty, unverified, and not atomically finalized.",
  "after_behavior": "Dead-daemon recovery executes only hash-verified admitted bytes; arbitrary dirty working-tree runtime bytes are rejected without disabling bridge dispatch.",
  "self_descriptive_naming": "dispatcher_generation_admission, admitted_generation, last_admitted_generation, materialized_generation, and unfinalized_generation_rejected name authority and state directly.",
  "obsolete_guidance_disposition": "The prior WI-5429 sequence requiring terminal WI-5427, WI-5448, and WI-5451 before WI-5429 is withdrawn. The owner-selected order is WI-5429 first, then WI-5427, then WI-5448/WI-5451 successors.",
  "history_preservation": "All prior bridge files, PAUTH records, dirty-peer evidence, Git objects, and generated admission manifests remain auditable; this proposal rewrites none of them.",
  "baseline": {
    "current_risk": "Working-tree dispatcher runtime bytes can become executable authority before terminal verification.",
    "trusted_generation_artifact": "absent",
    "wi5427_dirty_peer_state": "still protected by operation-time dirty-peer collision gates"
  },
  "expected_result": {
    "recovery_source": "last admitted hash-verified generation materialized from Git objects",
    "new_generation_policy": "admit only after terminal focused bridge and commit provenance",
    "availability_policy": "continue on the previous admitted generation when a candidate is rejected",
    "shared_target_policy": "stop before mutation if the WI-5427 dirty-peer collision guard still reports overlapping dirty ownership"
  },
  "rollback": {
    "instructions": "Use a governed focused revert or superseding bridge revision for only the declared target paths; do not mutate live runtime state or dispatcher configuration as rollback.",
    "verification": "Rerun focused admission/supervision tests, applicability preflight, clause preflight, and exact target diff review."
  },
  "hard_invariants": [
    "No arbitrary dirty working-tree runtime byte becomes dispatcher executable authority.",
    "No source or test mutation occurs without latest GO, exact work-intent claim, implementation-start packet, corrected active PAUTH, and operation-time collision clearance.",
    "No dispatcher configuration, TAFE document, claim, lease, eligibility, routing, live daemon state, credential, external system, deployment, release, Git push, or unrelated file is mutated.",
    "All generated artifacts and materialized generations stay under E:\\GT-KB.",
    "Codex A remains Prime Builder and does not author Loyal Opposition verdict statuses."
  ],
  "fail_closed_conditions": [
    "Candidate commit, bridge provenance, VERIFIED verdict, implementation report, or path coverage is missing, ambiguous, stale, or unreadable.",
    "Materialized generation bytes fail hash, size, path-boundary, or import-root validation.",
    "The corrected active PAUTH is absent, revoked, expired, or operation-time validation fails.",
    "The WI-5427 dirty-peer collision guard still blocks an overlapping target path.",
    "PID provenance, worker quiescence, or document lease quiescence cannot be established."
  ],
  "essential_context_preservation": "Admission evidence preserves the candidate commit, terminal bridge thread and verdict path, target manifest, per-path Git blob hash, materialized hash, PAUTH, work item, predecessor generation, admission timestamp, and rejection diagnostics."
}
```

## Verification Plan

| Specification / invariant | Verification | Expected result |
| --- | --- | --- |
| `SPEC-CENTRALIZED-DISPATCH-SERVICE-001`; `ADR-DISPATCHER-ARCHITECTURE-001` | `groundtruth-kb/.venv/Scripts/python.exe -m pytest platform_tests/scripts/test_dispatcher_generation_admission.py platform_tests/scripts/test_dispatcher_daemon_supervision.py -q --tb=short` | Dead-daemon recovery launches only admitted bytes and preserves the canonical daemon/supervisor topology. |
| `DCL-DISPATCHER-DAEMON-SUPERVISION-CONTRACT-001` | Focused tests for last-admitted fallback, rejected unfinalized generations, materialized hash checks, hidden Windows launch flags, and idempotent recovery. | Recovery stays unattended, hidden, deterministic, and non-destructive. |
| `GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001` | Fixtures with unrelated dirty paths, active worker/lease simulations, and before/after byte inventories for registry/config/lease state. | Unrelated dirt does not disable dispatch; active work defers handoff; protected runtime/config state is unchanged. |
| `GOV-WORK-TREE-HYGIENE-001` | Synthetic Git-object tests for staged, unstaged, untracked, missing, tampered, and non-terminal runtime variants. | Every unfinalized variant is rejected; the previous admitted generation remains runnable. |
| `GOV-FILE-BRIDGE-AUTHORITY-001`; `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001`; `DCL-PROJECT-AUTHORIZATION-OPERATION-TIME-ENFORCEMENT-001` | Exact work-intent claim, `implementation_authorization.py begin`, protected mutation gate, applicability preflight, and clause preflight. | Source/test mutation occurs only under latest GO, active corrected PAUTH, exact targets, and clean operation-time gates. |
| `DCL-PROJECT-DEPENDENCY-ORDERING-001` | Read-only bridge/MemBase checks for WI-5429 first, then WI-5427, then WI-5448/WI-5451. | No circular prerequisite remains; any dirty-peer block is resolved by a governed disposition before mutation. |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | Candidate/live clause preflight plus path-boundary tests for generated artifacts and materialized generation directories. | All generated artifacts, bridge output, runtime generations, and tests remain under `E:\GT-KB`. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | Focused pytest, existing daemon supervision tests, Ruff check/format check, `git diff --check`, applicability preflight, clause preflight, and exact target diff review. | All focused and governance checks pass before implementation report and independent verification. |

## Risk And Rollback

Risk remains high because this work controls the source of executable dispatcher
runtime bytes during unattended recovery. The implementation therefore fails
closed on ambiguous provenance, leaves live workers and leases untouched, and
falls back to the previous admitted generation rather than making a harness
non-dispatchable or mutating runtime state.

Rollback is a focused revert or superseding bridge revision for the declared
target paths only, after the same bridge/claim/start gates used for
implementation. Materialized generation artifacts remain auditable and
content-addressed. This proposal does not authorize deleting bridge history,
rewriting Git history, pruning generations, changing dispatcher configuration,
or altering live runtime state.

## Recommended Commit Type

`feat(dispatcher):` because the implementation adds a new generation-admission
module and capability.

---

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
