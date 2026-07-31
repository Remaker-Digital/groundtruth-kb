NEW

# WI-5429 - Admit only governed finalized dispatcher runtime generations

bridge_kind: prime_proposal
Document: gtkb-wi5429-finalized-runtime-generation-admission
Version: 001
Author: Prime Builder (Codex, harness A)
Date: 2026-07-17 UTC

author_identity: prime-builder/codex/A
author_harness_id: A
author_session_context_id: 019f5f66-9582-7f03-a3f1-3c75e6bd9d0a
author_model: GPT-5.5 Codex
author_model_version: 5.5
author_model_configuration: OpenAI Codex desktop interactive; reasoning=xhigh; approval_policy=never

Project Authorization: PAUTH-DISPATCHER-BLACK-BOX-WI5429-FINALIZED-GENERATION-ADMISSION-20260717
Project: PROJECT-GTKB-OPS-DISPATCHER-MODERNIZATION-DISPATCHER-BLACK-BOX-HARDENING
Work Item: WI-5429

target_paths: ["scripts/dispatcher_generation_admission.py", "scripts/ensure_dispatcher_daemon.py", "scripts/gtkb_dispatcher_daemon.py", "platform_tests/scripts/test_dispatcher_generation_admission.py", "platform_tests/scripts/test_dispatcher_daemon_supervision.py"]

implementation_scope: source | protocol
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

---

## Summary

Ordinary dead-daemon recovery currently imports and starts the dispatcher source
present in the shared working tree. That source may be authorized but not yet
independently VERIFIED and atomically committed. WI-5427 demonstrated the
failure mode when its candidate generation became the live daemon before its
implementation report or terminal review. A dirty shared worktree must not be
treated as deployment authority, but unrelated dirt must not strand the bridge.

Add a deterministic generation-admission service that derives trust from the
existing atomic VERIFIED finalization invariant: the implementation paths,
implementation report, and terminal VERIFIED verdict are committed together.
The service will validate the commit and bridge provenance for every changed
runtime path, materialize the accepted runtime bytes from Git objects into an
in-root generation directory, verify their hashes before every launch, and
atomically retain the last admitted generation. The supervisor will recover a
dead daemon from that admitted generation and will ignore arbitrary dirty
working-tree runtime bytes. An alive daemon may hand off only to an admitted
generation and only through WI-5427's quiescent hidden-process path.

This proposal does not modify the VERIFIED finalizer. It consumes the finalizer's
existing atomic commit result as evidence. It also does not adopt the current
WI-5427 candidate bytes. Shared source edits are hard-sequenced behind terminal,
focused finalization of WI-5427, WI-5448, and WI-5451, followed by exact
pre-start byte verification.

## Specification Links

- `SPEC-CENTRALIZED-DISPATCH-SERVICE-001` - recovery must preserve the one
  daemon-owned dispatch service, canonical role/target resolution, trigger
  semantics, and audit trail.
- `ADR-DISPATCHER-ARCHITECTURE-001` - admitted generation execution remains
  inside the existing dispatcher daemon and supervisor architecture; no
  alternate queue, poller, or harness-owned automation is introduced.
- `DCL-DISPATCHER-DAEMON-SUPERVISION-CONTRACT-001` - the supervisor must keep
  recovery unattended, idempotent, provenance checked, hidden on Windows, and
  non-destructive to live work.
- `GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001` - dirty runtime bytes are rejected
  by falling back to the last admitted generation, never by disabling a harness,
  pausing the bridge, or mutating eligibility/routing.
- `GOV-WORK-TREE-HYGIENE-001` - foreign and unfinalized working-tree bytes remain
  quarantined and cannot become runtime authority merely because the daemon is
  absent.
- `GOV-FILE-BRIDGE-AUTHORITY-001` - implementation requires this proposal,
  independent GO, exact work-intent claim, implementation-start authorization,
  post-implementation review, and atomic VERIFIED finalization.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - the proposal binds
  the implementation to concrete governing requirements and exact targets.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - the active PAUTH,
  project, WI-5429, and target paths are explicit and mechanically checkable.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - independent verification
  must execute the spec-to-test matrix below, including real Git-object and
  provenance fixtures.
- `DCL-PROJECT-AUTHORIZATION-ENVELOPE-001` - the bounded PAUTH permits source and
  test work only after the remaining bridge and operation-time gates pass.
- `DCL-PROJECT-DEPENDENCY-ORDERING-001` - WI-5427 finalization and WI-5451
  executable dependency-closure identity are predecessors; WI-5448 owns
  overlapping dead-daemon recovery bytes and must also be dispositioned first.
- `GOV-STANDING-BACKLOG-001` - WI-5429 and its linked `TEST-11540` preserve the
  observed defect and acceptance contract in MemBase.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` - admission evidence is durable and
  reconstructable from PAUTH, bridge, Git, manifest, test, and commit artifacts.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` - the trusted generation is a
  content-addressed artifact backed by governed evidence rather than an
  inference from mutable process or worktree state.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - implementation, verification, and
  activation remain distinct lifecycle transitions.

## Prior Deliberations

- `DELIB-20260715-FLEET-HARNESS-DEFECT-REPAIR-AUTHORIZATION` - Mike
  authorized bounded PAUTH carriers and governed proposal lifecycles for every
  newly discovered in-scope fleet defect while preserving all later gates.
- `bridge/gtkb-wi5427-daemon-generation-handoff-001.md` - proposed deterministic
  loaded/current generation identity and a quiescent supervisor-owned handoff.
- `bridge/gtkb-wi5427-daemon-generation-handoff-002.md` - independent GO for the
  WI-5427 four-file generation-handoff slice.
- `bridge/gtkb-wi5427-daemon-generation-handoff-003.md` - current NEW
  implementation report whose unfinalized candidate bytes exposed this
  admission defect; it is evidence, not adopted implementation.
- `WI-5451` / `TEST-11554` - governed successor for complete executable
  dependency-closure identity. WI-5429 consumes that identity after terminal
  finalization rather than duplicating its manifest logic.

## Owner Decisions / Input

- `DELIB-20260715-FLEET-HARNESS-DEFECT-REPAIR-AUTHORIZATION` authorizes this
  bounded PAUTH and proposal lifecycle.
- `PAUTH-DISPATCHER-BLACK-BOX-WI5429-FINALIZED-GENERATION-ADMISSION-20260717`
  is active and includes WI-5429 plus the governing specifications.
- No new owner decision is required to review this proposal. Any future live
  scheduled-task re-registration or generation activation is outside this
  PAUTH and would require its own governed operational authority.

## Requirement Sufficiency

Existing requirements sufficient. `SPEC-CENTRALIZED-DISPATCH-SERVICE-001`,
`ADR-DISPATCHER-ARCHITECTURE-001`,
`DCL-DISPATCHER-DAEMON-SUPERVISION-CONTRACT-001`, and
`GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001` define the daemon, recovery,
availability, and nonimpairment boundaries. WI-5429 and linked `TEST-11540`
provide the concrete governed-finalization acceptance condition. WI-5451 and
linked `TEST-11554` separately define the prerequisite executable
dependency-closure identity.

## Proposed Implementation

1. Add `scripts/dispatcher_generation_admission.py` as the single admission
   service. Given a candidate local commit and the WI-5451 runtime manifest, it
   will:
   - read candidate bytes through Git object commands, never through working-tree
     source paths;
   - prove that every runtime-path delta since the previously admitted
     generation is covered by an atomic focused commit containing the relevant
     implementation/report paths and a terminal VERIFIED verdict;
   - reject missing, non-terminal, uncommitted, unreachable, path-incomplete, or
     ambiguous provenance with explicit diagnostics;
   - materialize exact path bytes under
     `.gtkb-state/dispatcher-generations/<generation>/`, preserving relative
     paths required by Python imports;
   - hash and size-check every materialized path against the manifest, then
     atomically update the last-admitted pointer only after complete validation.
2. Change the supervisor's earliest recovery path so it does not import or spawn
   the mutable working-tree daemon before admission. A dead daemon is started
   from the last valid materialized generation. If a newer candidate is not yet
   VERIFIED, recovery continues on the prior admitted generation and reports
   `unfinalized_generation_rejected`; unrelated dirty paths are non-blocking.
3. Integrate admitted-generation identity into WI-5427's status and handoff
   flow. An alive daemon may hand off only when the candidate generation is
   admitted, exact materialized hashes pass, PID provenance is valid, and all
   workers and document leases are quiescent.
4. Keep the canonical live project root as the daemon's data root. Bridge,
   TAFE, claims, leases, registry, configuration, and audit state continue to be
   read through existing canonical surfaces; only executable code is loaded
   from the admitted generation directory.
5. Do not prune generations in this slice. Retention is bounded to atomic
   replacement of the active pointer plus immutable content-addressed
   directories; cleanup requires a separately governed hygiene operation.

## Intuitiveness/Non-Impairment Disposition

```json
{
  "schema_version": 1,
  "applicability": "applicable",
  "provenance": "DELIB-20260715-FLEET-HARNESS-DEFECT-REPAIR-AUTHORIZATION; PAUTH-DISPATCHER-BLACK-BOX-WI5429-FINALIZED-GENERATION-ADMISSION-20260717; WI-5429; TEST-11540",
  "canonical_authority": "GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001; SPEC-CENTRALIZED-DISPATCH-SERVICE-001; ADR-DISPATCHER-ARCHITECTURE-001; DCL-DISPATCHER-DAEMON-SUPERVISION-CONTRACT-001",
  "primary_route": "Validate terminal focused Git and bridge provenance, materialize exact admitted bytes from Git objects, preserve the last admitted generation, and use only the canonical hidden daemon supervisor and WI-5427 quiescent handoff path.",
  "before_behavior": "A dead-daemon supervisor can import and start current working-tree runtime bytes even when those bytes are still awaiting independent verification and focused finalization.",
  "after_behavior": "Dead-daemon recovery runs the last content-addressed governed finalized generation; a newer generation becomes eligible only after complete terminal focused provenance, and unrelated worktree dirt never disables a harness or strands the bridge.",
  "self_descriptive_naming": "dispatcher_generation_admission, admitted_generation, unfinalized_generation_rejected, materialized_generation, and last_admitted_generation describe authority and state directly.",
  "obsolete_guidance_disposition": "A clean worktree, current HEAD, proposal GO, active PAUTH, or authorization alone is not deployment authority. Existing WI-5427 loaded/current identity remains useful only after WI-5451 closes the executable dependency set and WI-5429 adds terminal admission.",
  "history_preservation": "Bridge chains, Git commits, PAUTH records, test artifacts, manifests, generation diagnostics, and content-addressed generation directories remain auditable; this slice rewrites or deletes none of them.",
  "baseline": {
    "wi5427_state": "NEW implementation report awaiting independent terminal verification",
    "recovery_source": "current working-tree scripts",
    "trusted_generation_artifact": "absent",
    "unrelated_dirty_worktree_policy": "can be conflated with executable generation dirt"
  },
  "expected_result": {
    "recovery_source": "hash-verified materialized Git-object bytes from the last admitted terminal generation",
    "new_generation_policy": "admitted only after exact focused VERIFIED commit provenance and complete WI-5451 runtime dependency identity",
    "availability_policy": "unrelated dirt and a rejected candidate do not disable dispatch; recovery continues on the last admitted generation",
    "live_work_policy": "workers and leases defer handoff and remain byte-for-byte unmodified"
  },
  "rollback": {
    "instructions": "Revert only the five declared target paths in one governed focused transaction; generation activation or scheduled-task changes require separate operational authority.",
    "verification": "Rerun admission and supervision tests, confirm the prior admitted generation remains hash-valid, and confirm dispatcher, TAFE, lease, claim, eligibility, and routing state is unchanged."
  },
  "hard_invariants": [
    "Codex A remains Prime Builder only and never publishes a Loyal Opposition verdict.",
    "No arbitrary dirty working-tree runtime byte is executed by ordinary recovery.",
    "No candidate is admitted from PAUTH, GO, claim, implementation-start, clean-worktree, or HEAD evidence without terminal focused VERIFIED commit provenance.",
    "No worker is terminated and no live worker or provenance-valid lease is bypassed during handoff.",
    "No harness is made non-dispatchable to solve generation admission or console-window behavior.",
    "No dispatcher configuration, TAFE document, claim, lease, eligibility, routing, credential, deployment, release, or unrelated source state is mutated by implementation or tests.",
    "All executable generation files remain within E:\\GT-KB."
  ],
  "fail_closed_conditions": [
    "Terminal bridge or focused commit provenance is absent, ambiguous, stale, path-incomplete, or unreadable.",
    "The candidate commit is missing, unreachable, or its Git-object bytes do not match the manifest.",
    "The WI-5451 executable dependency closure is missing or incomplete.",
    "Materialized generation bytes fail hash, size, path-boundary, or import-root validation.",
    "PID provenance or dispatch quiescence cannot be established.",
    "A shared target differs from the terminal predecessor bytes recorded at implementation start."
  ],
  "essential_context_preservation": "The admitted generation retains its candidate commit, terminal bridge thread and verdict path, exact runtime path manifest, per-path Git blob hash, materialized hash, PAUTH and work-item provenance, predecessor generation, admission timestamp, and diagnostic history."
}
```

## Spec-Derived Verification Plan

| Specification / invariant | Verification | Expected result |
| --- | --- | --- |
| `SPEC-CENTRALIZED-DISPATCH-SERVICE-001`; `ADR-DISPATCHER-ARCHITECTURE-001` | `groundtruth-kb/.venv/Scripts/python.exe -m pytest platform_tests/scripts/test_dispatcher_generation_admission.py platform_tests/scripts/test_dispatcher_daemon_supervision.py -q --tb=short` | One canonical daemon/supervisor path remains; a dead daemon launches exact admitted Git-object bytes and preserves canonical project-root data surfaces. |
| `DCL-DISPATCHER-DAEMON-SUPERVISION-CONTRACT-001` | Focused tests for dead-daemon recovery, last-admitted fallback, materialized-byte tamper rejection/rematerialization, idempotent concurrent supervisor cycles, hidden Windows launch flags, and successor attestation. | Recovery is unattended and deterministic; no working-tree runtime byte is executed merely because the daemon is absent. |
| `GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001` | Fixtures keep unrelated worktree paths dirty and simulate active workers/leases while recording all registry/config/lease bytes before and after. | Unrelated dirt does not block recovery; active work defers handoff; eligibility, routing, claims, leases, and TAFE bytes remain unchanged. |
| `GOV-WORK-TREE-HYGIENE-001` | Synthetic Git repository tests change runtime files after the last VERIFIED commit and also create staged/untracked runtime variants. | Every unfinalized variant is rejected; the prior admitted generation remains runnable; foreign bytes remain untouched. |
| `GOV-FILE-BRIDGE-AUTHORITY-001`; `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`; `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | Synthetic bridge chains cover valid atomic VERIFIED finalization, NEW/GO/NO-GO without VERIFIED, verdict-only commits, omitted implementation paths, and tampered manifests. | Only complete terminal focused provenance is admitted, with stable diagnostics and a reconstructable evidence chain. |
| `DCL-PROJECT-DEPENDENCY-ORDERING-001` | Read-only bridge/MemBase checks plus exact pre-start target hashes. | WI-5427, WI-5448, and WI-5451 are terminally dispositioned before shared-file mutation; no predecessor or foreign hunk is adopted. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | Run the focused admission/supervision suites, existing daemon tests, Ruff check/format check, applicability preflight, clause preflight, and `git diff --check` for exact targets. | All commands pass; preflights report no missing required/advisory specs and zero blocking clause gaps. |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | Verify candidate creation, admission, handoff, and terminal activation are distinct recorded states. | An authorized or GO-approved but unverified candidate cannot become admitted or active. |

## Risk / Rollback

Risk is high because this code chooses executable bytes during unattended
recovery. The design therefore fails closed on provenance ambiguity while
remaining available through the last admitted generation. It never deletes or
rewrites dirty source, Git objects, bridge files, leases, or harness state.
Materialized-directory integrity is checked before every spawn, and all
concurrent pointer writes are atomic.

Rollback is one focused revert of the five declared target paths after stopping
new admissions through a separately authorized operational action. The prior
content-addressed generation and audit evidence remain available; this
implementation performs no live restart, task registration, deployment, or
generation activation.

## Bridge Filing

This proposal is filed under `bridge/` as the next status-bearing numbered
bridge file for `gtkb-wi5429-finalized-runtime-generation-admission`; no prior version is deleted or rewritten
(append-only). Dispatcher/TAFE state plus the numbered file chain are the live
workflow state per `GOV-FILE-BRIDGE-AUTHORITY-001`.

## Recommended Commit Type

`fix(dispatcher):` because the change prevents recovery from executing
unverified runtime code while preserving existing dispatcher availability and
topology.

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
