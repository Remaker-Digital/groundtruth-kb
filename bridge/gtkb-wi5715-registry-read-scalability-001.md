NEW
::init gtkb pb
::open build
author_identity: prime-builder/codex
author_harness_id: A
author_session_context_id: 019f9b59-52a0-75b2-9973-bd5601f98e9f
author_model: gpt-5
author_model_version: gpt-5
author_model_configuration: Codex desktop interactive; Prime Builder; build activity
author_metadata_source: open session envelope and current transcript

# WI-5715 — Generation-Bound Read Scalability For The SoT Registry

bridge_kind: prime_proposal
Document: gtkb-wi5715-registry-read-scalability
Version: 001
Date: 2026-08-01 UTC

Project Authorization: PAUTH-PROJECT-GTKB-HOUSEKEEPING-HARDENING-WHOLE-PROJECT-20260730
Project: PROJECT-GTKB-HOUSEKEEPING-HARDENING
Work Item: WI-5715
Related Work Items: WI-5675

target_paths: ["groundtruth-kb/src/groundtruth_kb/project/registry_control_plane.py", "groundtruth-kb/src/groundtruth_kb/project/sot_registry.py", "groundtruth-kb/tests/test_registry_control_plane.py"]

implementation_scope: source_and_test
requires_review: true
requires_verification: true
kb_mutation_in_scope: false
Recommended commit type: feat

KB Mutation: This proposal performs no MemBase write or mutation.

## Summary

Replace the registry's globally exclusive read path with a generation-bound
optimistic read fast path while retaining the existing exclusive path as the
single deterministic fallback. Writers, publication, observation, recovery,
and every registry mutation remain exclusively locked.

The change removes routine reader/reader serialization without permitting a
reader to observe a prepared, mixed, or stale generation. It adds no new retry,
sleep, timeout, or throttle constant. One optimistic attempt either proves a
coherent immutable generation or falls back to the existing exclusive read
path, where current typed recovery/corruption behavior remains authoritative.

## Current Revalidated Baseline

At HEAD `75decbfa704fe50288aecbc5669def329a0825df`, all four inspected paths are
clean despite extensive unrelated worktree activity:

| Path | Role | SHA-256 |
| --- | --- | --- |
| `groundtruth-kb/src/groundtruth_kb/project/registry_control_plane.py` | mutation target | `1ed0af2338d8075baa182f632ca98c4d574cdc6f4fb4533b9126688416dc3187` |
| `groundtruth-kb/src/groundtruth_kb/project/sot_registry.py` | mutation target | `2d6d47b38fd3c70abb718276e527ad7ad5e794102f458d4d8acc885b2bf79d25` |
| `groundtruth-kb/tests/test_registry_control_plane.py` | mutation target | `ca05a24781158c11c97312ea43072906e88d4a9a74d4641d25c725703c8c2074` |
| `groundtruth-kb/tests/test_sot_registry.py` | verification only | `c6fcba97dc582cafd8a830cbc94bd4f90a997ca9f62d7490afa9088bd87a19f8` |

Current `load_registry_snapshot` and `registry_read_barrier` take the same
exclusive process-wide file lock as writers while reading/parsing canonical
TOML, packaged TOML, the SQLite projection, parity state, and resolver records.
The lock implementation has a fixed 30-second acquisition timeout.

Owner-approved WI evidence measured four synchronized Windows-spawn readers
against the 2,348-record live registry. They serialized, completing at roughly
0.426, 0.887, 1.341, and 1.760 seconds (1.822 seconds wall). A direct Windows
`msvcrt` shared-byte-lock probe allowed one reader and rejected three, so that
primitive does not provide a viable process-safe shared lock here. A live-data
journal-generation prototype completed the four reads concurrently in 0.507
seconds wall, with each reader returning the same 2,348-record generation.

This session independently observed the production effect: a canonical passive
bridge-aggregate observation twice timed out at the 30-second exclusive lock
before succeeding, and governed bridge publication repeatedly encountered
stale aggregate generations under concurrent workers. This proposal addresses
reader-side lock convoying only; WI-5675 retains the broader timer/write-retry
program.

## Selected Design

### One optimistic attempt

1. Open a fresh, short-lived SQLite read connection in true read-only/query-only
   mode and read the latest registry transaction-journal head.
2. Accept only a complete terminal marker as an optimistic generation:
   - `committed` binds the journal's new canonical, packaged, and projection
     digests;
   - `aborted` binds its old digests.
3. Close the marker connection. Read canonical TOML, packaged TOML, and the
   SQLite projection live without the registry file lock; parse and validate
   the same schema/parity/resolver contracts used today.
4. Read the journal head again through another short-lived read-only connection.
5. Accept the optimistic result only when the exact terminal marker is
   unchanged and all three live digests match the generation it binds.

No cache is introduced. Every accepted result consumes live bytes and remains
sensitive to an out-of-band edit even when the journal marker did not change.

### Single deterministic fallback

Missing/incomplete legacy markers and initial nonterminal markers invoke the
existing exclusive implementation exactly once. After every optimistic body
read, including an exception, re-read the marker before choosing a disposition:

- a changed or newly nonterminal marker discards the attempt and invokes the
  exclusive implementation exactly once;
- an unchanged terminal marker with a body-read exception re-raises the
  original typed error, so stable schema, parity, path, and corruption failures
  are never relabeled as contention;
- an unchanged terminal marker with a successful body read is accepted only
  after the exact three-digest comparison also succeeds.

`registry_read_barrier` is a context manager and cannot replay caller code
after its post-yield marker check. It therefore raises one typed internal
optimistic-conflict signal when that check observes marker interposition. Its
only two external callers today, `load_toml` and `load_projection`, catch that
signal and execute their existing exclusive body once. `load_registry_snapshot`
owns the same one-fallback decision internally. The exclusive path remains the
compatibility and recovery authority; a stranded prepared journal preserves
the current visible recovery-required outcome. This proposal adds no retry loop
and no new time budget.

### Writer invariants

- Registry writes, observation publication, bridge capability publication,
  recovery, registration, and amendment retain the existing exclusive file
  lock and journal ordering.
- No writer code path may use the optimistic reader as mutation authority.
- Generation markers are evidence, not cached content or a second source of
  truth.
- Read-only SQLite connections must reject writes mechanically.

## Exact Implementation Plan

1. Refactor the current locked snapshot loader into a reusable exclusive
   implementation without changing its behavior.
2. Add typed helpers for short-lived read-only journal-head and projection
   reads, including explicit query-only enforcement.
3. Implement one generation-bound optimistic snapshot attempt and exact
   digest/marker validation.
4. Route `load_registry_snapshot` through an internal one-fallback decision;
   make `registry_read_barrier` emit the typed internal interposition signal;
   and make its two current wrappers, `load_toml` and `load_projection`, replay
   their existing exclusive bodies once without changing public return types
   or typed stable-error behavior.
5. Add deterministic Windows-spawn and controlled interposition tests in the
   existing control-plane test module.
6. Run the complete registry-control-plane and `test_sot_registry.py`
   regressions, Ruff, format, compile, and diff checks.
7. Assert only the three declared targets changed.

`groundtruth-kb/tests/test_sot_registry.py` is verification-only. It must not be
edited, restored, staged, or attributed to WI-5715.

## Requirement Sufficiency

Existing requirements sufficient. WI-5715 and the linked owner decisions
already establish coherent highly parallel SoT reads, preservation of live
freshness, writer exclusivity, and visible nonterminal recovery. This proposal
selects the bounded implementation shape and introduces no new authority model.

## Intuitiveness/Non-Impairment Disposition

```json
{
  "schema_version": 1,
  "applicability": "applicable",
  "provenance": "WI-5715; DELIB-202667517; DELIB-20260730-DISPATCHER-NEXT-PARALLEL-SOT-CONCURRENCY-REQUIREMENT; DELIB-202667721",
  "canonical_authority": "GOV-PLATFORM-SOT-REGISTRY-001, GOV-SOURCE-OF-TRUTH-FRESHNESS-001, GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001, and PAUTH-PROJECT-GTKB-HOUSEKEEPING-HARDENING-WHOLE-PROJECT-20260730 v2",
  "primary_route": "One generation-bound optimistic read attempt in registry_control_plane.py, a typed internal interposition signal consumed by the two current sot_registry.py wrappers, and exactly one fallback to the existing exclusive implementation",
  "before_behavior": "Every registry snapshot, TOML read, and projection read acquires the same exclusive process-wide file lock as writers, serializing independent readers and exposing the inherited fixed 30-second lock bound under contention.",
  "after_behavior": "A reader accepts only live canonical, packaged, and projection bytes bound to one unchanged terminal journal marker and its exact digest triple; uncertain generations take the unchanged exclusive authority path exactly once.",
  "self_descriptive_naming": "The internal optimistic-attempt helper, read-only journal reader, and optimistic-conflict signal will name generation binding, read-only access, and interposition explicitly; public loader names and return types remain unchanged.",
  "obsolete_guidance_disposition": "No legacy guidance, cache, projection, or generated summary becomes control authority; incomplete legacy journal state is routed to the existing exclusive compatibility path.",
  "history_preservation": "The registry transaction journal, project records, work-item chain, numbered bridge chain, and foreign worktree changes remain append-only or byte-preserved; no historical row or bridge version is rewritten.",
  "baseline": {
    "registry_control_plane.py": "SHA256 1ed0af2338d8075baa182f632ca98c4d574cdc6f4fb4533b9126688416dc3187",
    "sot_registry.py": "SHA256 2d6d47b38fd3c70abb718276e527ad7ad5e794102f458d4d8acc885b2bf79d25",
    "test_registry_control_plane.py": "SHA256 ca05a24781158c11c97312ea43072906e88d4a9a74d4641d25c725703c8c2074",
    "verification_only_test_sot_registry.py": "SHA256 c6fcba97dc582cafd8a830cbc94bd4f90a997ca9f62d7490afa9088bd87a19f8",
    "measured_reader_behavior": "Four synchronized Windows-spawn readers completed serially at approximately 0.426, 0.887, 1.341, and 1.760 seconds; a generation-bound live-data prototype completed all four in 0.507 seconds wall."
  },
  "expected_result": {
    "coherence": "Four or more spawned readers overlap while returning one identical live generation; no mixed generation is accepted.",
    "compatibility": "CAS, publication, observation, recovery, registration, amendment, typed stable failures, and the complete public-loader regression suite remain unchanged.",
    "scope": "Only the three declared mutation targets change; test_sot_registry.py remains verification-only."
  },
  "rollback": {
    "instructions": "Preserve the report and verdict chain, then perform a separately governed scoped revert of the three declared targets so the existing exclusive loader is again the public path.",
    "test": "Re-run the complete registry-control-plane and public-loader suites, Ruff, format, and exact-path diff checks after rollback."
  },
  "hard_invariants": [
    "Writers, recovery, observation, and publication remain exclusively locked",
    "Every accepted optimistic result is bound to one unchanged terminal marker and exact canonical, packaged, and projection digests",
    "Every optimistic SQLite connection is read-only and query-only",
    "No cache, retry loop, timer, throttle, daemon, configuration surface, dispatcher mutation, or external-system mutation is introduced"
  ],
  "fail_closed_conditions": [
    "Missing, incomplete, changed, or nonterminal generation evidence",
    "Digest mismatch or inability to prove one coherent live generation",
    "Any target hash drift, undeclared path mutation, or overlapping exact claim",
    "Any focused regression, Ruff, format, GO, claim, start-packet, report, or independent-verification failure"
  ],
  "essential_context_preservation": "Keep the exclusive implementation intact as the sole fallback and recovery authority, keep test_sot_registry.py untouched as public-API evidence, and leave the fixed 30-second bound to the separately governed WI-5675/timer-concurrency configuration program."
}
```

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` — this proposal will be filed only through
  the governed writer as the first append-only numbered bridge file
  `bridge/gtkb-wi5715-registry-read-scalability-001.md`; no prior version is
  deleted or rewritten, and no protected implementation begins before GO,
  exact claim, and fresh schema-v3 start authority.
- `GOV-PLATFORM-SOT-REGISTRY-001` — one authoritative registry and coherent
  controlled access.
- `DCL-SOT-REGISTRY-PROJECTION-PARITY-001` — accepted generations preserve
  canonical/package/projection parity.
- `DCL-SOT-REGISTRY-RECORD-SCHEMA-001` — all existing record validation remains
  enforced.
- `GOV-SOURCE-OF-TRUTH-FRESHNESS-001` — every accepted read consumes current
  live bytes; no digest-only cache.
- `REQ-GTKB-GOVERNED-GIT-LIFECYCLE-001` — concurrent workers preserve accepted
  changes and receive visible conflicts.
- `GOV-CROSS-CUTTING-REQUIREMENTS-MECHANICAL-ENFORCEMENT-001` — read-only mode,
  marker equality, and digest equality are mechanically enforced.
- `GOV-DETERMINISTIC-SERVICES-PRINCIPLE-001` — one deterministic attempt and
  fallback; no background worker or timer.
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` and
  `DCL-PROJECT-AUTHORIZATION-OPERATION-TIME-ENFORCEMENT-001` — fresh GO/claim/
  start and exact three-path scope remain mandatory.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` and
  `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` — exact PAUTH,
  project, WI, paths, and specification linkage.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — executed concurrency and
  nonimpairment evidence before VERIFIED.
- `GOV-WORK-TREE-HYGIENE-001` — foreign changes and the verification-only test
  stay excluded.
- `GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001` — existing writers, recovery, and
  registry correctness remain intact.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`,
  `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`, and
  `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` — durable proposal/report/verdict
  lifecycle.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` — all dependencies remain inside
  `E:/GT-KB`.

## Prior Deliberations

- `DELIB-202667517` — highly parallel Prime Builder operation is a platform
  requirement; only short atomic critical sections may serialize.
- `DELIB-20260730-DISPATCHER-NEXT-PARALLEL-SOT-CONCURRENCY-REQUIREMENT` —
  global single-leader serialization is not an acceptable Dispatcher Next
  steady state; MemBase/SoT concurrency must be enhanced or replaced.
- `DELIB-20260801-GTKB-PARALLEL-CONTENTION-TIMER-TOLERANCE` — use generous
  bounded waits now and replace arbitrary timers through governed work without
  weakening authority expiry.
- `DELIB-20260801-GTKB-TIMER-CONCURRENCY-CONFIG-SOT-DIRECTIVE`,
  `DELIB-202667722`, and `DELIB-202667748` — the inherited fixed 30-second
  registry bound remains a measured residual for the WI-5675/timer-governance
  program. WI-5715 adds no timer or configuration constant and does not claim
  to close centralized timer/concurrency policy.
- `DELIB-20260630-PROJECT-LEVEL-WI-APPROVAL-RETIREMENT` and
  `DELIB-20260730-PROJECT-AUTHORITY-INHERITANCE-PULL-FORWARD` — active project
  authority controls; legacy `approval_state` is not authority.
- `DELIB-202667721` — controlling list-free Housekeeping Hardening PAUTH.
- WI-5715 status evidence — measured serialized baseline, rejected Windows
  shared-byte lock, and selected journal-marker design.

## Owner Decisions / Input

- The owner made highly parallel SoT-only coordination a hard activation
  requirement in `DELIB-202667517` and
  `DELIB-20260730-DISPATCHER-NEXT-PARALLEL-SOT-CONCURRENCY-REQUIREMENT`.
- The owner approved normal work under the active list-free Housekeeping
  Hardening PAUTH in `DELIB-202667721`; WI-5715 is an active member.
- No new owner decision is required for this bounded three-target proposal.

## Specification-Derived Verification Plan

| Requirement | Required deterministic evidence |
| --- | --- |
| Parallel coherent reads | Four Windows-spawn readers synchronize before the live read; prove execution overlap and identical generation/result, with a generous upper guard rather than a narrow timing threshold |
| Generation binding | Committed and aborted terminal heads bind new/old digest triples; unchanged marker plus exact three-digest match is required for optimistic success |
| Writer interposition | Controlled commit between marker reads forces exclusive fallback and never returns a mixed generation |
| Prepared/nonterminal journal | Live writer and stranded prepared states preserve bounded fallback and the existing recovery-required outcome |
| Stable failures | Unchanged-marker TOML corruption, projection parity, and record-schema failures preserve their typed errors |
| Legacy compatibility | Missing/incomplete legacy journal state uses the existing exclusive loader |
| Read-only enforcement | Attempted write through every optimistic SQLite connection is rejected |
| Freshness | Out-of-band source edit is read live and detected; no stale digest-keyed cache result |
| Writer nonimpairment | Existing CAS, fault injection, recovery, registration, amendment, passive observation, and bridge publication tests remain green |
| Public API nonimpairment | Complete `groundtruth-kb/tests/test_sot_registry.py` suite remains green without editing that file |

Required commands after governed implementation include:

```powershell
groundtruth-kb\.venv\Scripts\python.exe -m pytest groundtruth-kb/tests/test_registry_control_plane.py groundtruth-kb/tests/test_sot_registry.py -q --tb=short
groundtruth-kb\.venv\Scripts\ruff.exe check groundtruth-kb/src/groundtruth_kb/project/registry_control_plane.py groundtruth-kb/src/groundtruth_kb/project/sot_registry.py groundtruth-kb/tests/test_registry_control_plane.py
groundtruth-kb\.venv\Scripts\ruff.exe format --check groundtruth-kb/src/groundtruth_kb/project/registry_control_plane.py groundtruth-kb/src/groundtruth_kb/project/sot_registry.py groundtruth-kb/tests/test_registry_control_plane.py
git --no-optional-locks diff --check -- groundtruth-kb/src/groundtruth_kb/project/registry_control_plane.py groundtruth-kb/src/groundtruth_kb/project/sot_registry.py groundtruth-kb/tests/test_registry_control_plane.py
```

## Acceptance Criteria

1. On a stable terminal generation, at least four spawned readers overlap and
   return one identical coherent result without acquiring the exclusive writer
   lock.
2. No reader returns mixed canonical, packaged, or projection generations.
3. Marker change, nonterminal state, incomplete legacy state, or a body failure
   paired with changed/nonterminal post-read marker invokes exactly one
   exclusive fallback; no retry loop exists.
4. A body failure paired with an unchanged terminal marker re-raises its
   original error; stable corruption, schema, and parity failures remain
   visible and typed.
5. Every optimistic SQLite handle is opened read-only/query-only and rejects
   writes.
6. All registry content is read live; out-of-band edits cannot be hidden by a
   cache.
7. Writers, recovery, observation, registry publication, CAS, and journal
   ordering remain exclusively locked and behaviorally unchanged.
8. The context-manager conflict signal is caught only by the two current
   wrappers, which replay their exclusive bodies once; no caller code is
   implicitly replayed after `yield`.
9. Existing registry and public-loader regression suites pass, including the
   untouched verification-only test module.
10. No new timer, sleep, retry-count, interval, throttle, daemon, cache, or
   configuration surface is added.
11. Only the three declared targets change; every foreign worktree path is
    preserved.
12. No dispatcher mutation, external-system mutation, credential work, push,
    history rewrite, deployment, release, or destructive cleanup occurs.

## Pre-Filing Preflight Subsection

Fresh candidate checks against this draft produced the following results:

- `bridge_applicability_preflight.py --content-file ... --json` —
  `preflight_passed: true`, `missing_required_specs: []`,
  `missing_advisory_specs: []`; proposal-time evaluation allowed both
  `implementation_packet_create` and `implementation_start` under controlling
  whole-project PAUTH v2 for the exact three-target cohort.
- `adr_dcl_clause_preflight.py --content-file ...` — exit 0; four
  `must_apply` clauses, zero evidence gaps, zero blocking gaps.
- `proposal_target_paths_coverage_preflight.py --content-file ... --json` —
  advisory gap only for `groundtruth-kb/tests/test_sot_registry.py`. That path
  is deliberately verification-only: the proposal executes it for public API
  nonimpairment but does not authorize editing, restoring, staging, or
  attributing it to WI-5715. Adding it to `target_paths` would improperly widen
  mutation authority, so the narrower declared cohort is retained.
- All three mutation targets and the verification-only path match the hashes in
  `Current Revalidated Baseline` and have empty exact-path Git status.

The governed writer must rerun its own compliance and publication checks on
this completed content. No candidate preflight grants protected mutation.

## Risks And Rollback

The primary risk is accepting a mixed generation or hiding stable corruption as
contention. Double-read marker equality, exact digest binding, live-byte reads,
and preservation of the typed exclusive path as the sole fallback address that
risk. The second risk is moving lock pressure rather than removing it; the
spawned overlap test and writer-interposition fixtures distinguish true overlap
from sequential fast execution.

Rollback is a scoped revert of the three target files after preserving the
report/verdict history. The existing exclusive loader remains intact as the
fallback and can be restored as the public path without data migration. No
registry content, identity, or journal record is migrated by this change.

## Recommended Commit Type

Recommended commit type: `feat(registry): add generation-bound parallel reads`.

---

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
