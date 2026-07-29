REVISED
::init gtkb pb
::open build
author_identity: prime-builder/codex
author_harness_id: A
author_session_context_id: 019f9329-a174-7763-8f7e-29679f39e6bd
author_model: gpt-5
author_model_version: gpt-5
author_model_configuration: reasoning_effort=default; thread_source=codex-desktop
author_metadata_source: x-codex-turn-metadata


# Revised Implementation Proposal - Make `amend_artifact` linearizable under concurrent Prime Builder writers

bridge_kind: prime_proposal
Document: gtkb-wi5714-registry-write-linearizability
Version: 003
Date: 2026-07-29 UTC
Responds to: bridge/gtkb-wi5714-registry-write-linearizability-002.md

Project Authorization: PAUTH-PROJECT-GTKB-HOUSEKEEPING-HARDENING-WI5714-REGISTRY-LINEARIZABILITY-20260729
Project Authorization Candidates: [{"project_authorization_id":"PAUTH-PROJECT-GTKB-HOUSEKEEPING-HARDENING-WI5714-REGISTRY-LINEARIZABILITY-20260729","coverage":"exact_singleton","included_work_item_count":1,"specificity_rank":[0,1],"selected":true}]
Project: PROJECT-GTKB-HOUSEKEEPING-HARDENING
Work Item: WI-5714

target_paths: ["groundtruth-kb/src/groundtruth_kb/project/registry_control_plane.py", "groundtruth-kb/tests/test_registry_control_plane.py"]

implementation_scope: source
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

This proposal performs no production MemBase or `groundtruth.db` mutation.
SQLite projection changes occur only inside pytest-managed temporary registry
fixtures and are discarded test runtime evidence, not implementation targets.

## Summary

Make the `amend_artifact` read-modify-write path linearizable under concurrent
Prime Builder writers. Each amendment will bind to the exact coherent registry
generation it read, retry only a typed generation conflict from a fresh
snapshot for no more than eight total attempts, and fail visibly without false
success or partial mutation if contention persists.

This proposal does not claim to repair every registry writer. The generation-
unbound non-batch `register_artifacts` and `bootstrap_legacy_registry` paths are
captured separately as `WI-5736` / `TEST-11748` and must sequence after WI-5714
because they overlap the same source and focused test module.

## Revision Claim

This revision preserves the approved two-file implementation boundary and the
generation-CAS mechanism while replacing the v001 verification design with
measured red/green baselines, a deterministic Windows-spawn regression gate,
exact exception assertions, coherent-read evidence, and specification-specific
verification. It addresses every blocking and non-blocking finding in v002
without widening the owner authorization.

## Requirement Sufficiency

The requirements and owner decisions are sufficient for this bounded repair.
`GIT-REQ-A11` now states the concurrency outcome directly: accepted registry
writes must be linearizable or conflict-detected, readers must see one coherent
committed generation, and no lost update or false success is permitted. No new
owner decision is needed because `DELIB-202667522` explicitly authorizes the
typed generation conflict, fresh-snapshot retry, eight-attempt bound, and
deterministic Windows-spawn coverage proposed here.

## In-Root Placement Evidence

Both implementation targets and all proposed test fixtures remain beneath
`E:/GT-KB`. Test runtime generations use pytest-managed temporary directories;
no project authority depends on harness memory or out-of-root scratch state.

## Specification Links

- `GOV-PLATFORM-SOT-REGISTRY-001` - the repair preserves one coherent canonical declaration, packaged mirror, and MemBase projection for the artifact-membership authority.
- `REQ-GTKB-GOVERNED-GIT-LIFECYCLE-001` - executable assertion `GIT-REQ-A11` requires concurrent registry writes to preserve accepted updates or return a conflict and requires coherent committed reads.
- `DCL-SOT-REGISTRY-PROJECTION-PARITY-001` - every successful or rejected attempt must retain canonical/package byte identity and projection-generation parity.
- `DCL-ARTIFACT-REGISTRY-MUTATION-AUTHORIZATION-001` - generation conflicts must be detected before journal, declaration, packaged, or projection mutation and may not weaken existing mutation evidence.
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` - the active exact-singleton PAUTH limits implementation to WI-5714 and the two declared source/test paths.
- `DCL-PROJECT-AUTHORIZATION-OPERATION-TIME-ENFORCEMENT-001` - implementation begins only after GO through the operation-time authorization packet for those exact paths.
- `GOV-FILE-BRIDGE-AUTHORITY-001` - the numbered chain, exact-session claim, independent GO, implementation report, and independent terminal verdict remain mandatory.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - this revision provides concrete requirement-to-test links rather than auto-linked boilerplate.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - the implementation report must execute and report every verification row below.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - the shared platform control plane remains under `groundtruth-kb/`, outside adopter application scope.
- `GOV-WORK-TREE-HYGIENE-001` - exact two-path status and diff checks preserve all unrelated user and concurrent-worker changes.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` - the revision keeps the NO-GO findings, owner decisions, WI-5714, residual WI-5736, linked tests, implementation report, and verdict as one durable traceable artifact graph.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - filing REVISED requests review but does not advance implementation, verification, completion, or release state.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` - the material residual writers are preserved as WI-5736 / TEST-11748 instead of being hidden or implemented outside authority.

## Prior Deliberations

- `DELIB-202667517` - owner decision requiring highly parallel Prime Builder operation and forbidding false success after overwriting an accepted shared-control-plane mutation; it supplies the authority behind `GIT-REQ-A11`.
- `DELIB-202667522` - owner decision authorizing this exact WI-5714 two-file generation-CAS repair, typed conflict, at-most-eight attempts, and deterministic Windows-spawn coverage.

No prior deliberation chooses a conflicting implementation mechanism. The v002
Loyal Opposition verdict is the operative design review and is addressed below.

## Owner Decisions / Input

- `DELIB-202667517` establishes linearizable or preimage-conflict-detected shared writes as a platform requirement.
- `DELIB-202667522` supplies the exact bounded implementation authorization. It does not bypass GO, claim, implementation-start, report, verification, or finalization gates.

## Measured Reproduced Failure

The pre-fix race was measured on 2026-07-29 UTC with this exact command:

```powershell
groundtruth-kb\.venv\Scripts\python.exe .gtkb-state\propose-drafts\reproduce_wi5714_registry_lost_update.py
```

The in-root diagnostic used Windows `multiprocessing` spawn with two workers.
Inside each spawned child, a child-local wrapper called the real
`load_registry_snapshot` and then waited on one `Barrier(2)` before returning
the first snapshot. This guarantees that both workers read generation G before
either can call `apply_registry_transaction`. The workers amended the `notes`
field of disjoint registry records.

Observed output:

```text
outcomes=[('one', 'ok', ''), ('two', 'ok', '')]
notes={'one': 'first accepted amendment', 'two': ''}
lost_updates=['two']
```

Both workers reported success, but only one of two accepted deltas survived.
This section promotes the measured observation and complete interleaving method
into the governed bridge record; the non-authoritative diagnostic file is not a
closure dependency. The implementation test will carry the same child-local
first-read barrier directly in the declared test module.

## Measured Green Baseline

Command:

```powershell
groundtruth-kb\.venv\Scripts\python.exe -m pytest groundtruth-kb\tests\test_registry_control_plane.py -q --tb=short
```

Result on unmodified source: `29 passed in 17.72s`. This establishes that the
existing focused suite is green while the separate deterministic reproducer is
red.

## Proposed Scope

1. Add `RegistryGenerationConflict` as a strict subclass of
   `RegistryAuthorizationError`. Raise that exact subclass when an amend-bound
   expected generation differs from the coherent live generation. The existing
   base-class stale-generation denial already works; the new behavior is exact
   classification for safe retry.
2. Bind every `amend_artifact` apply attempt to
   `snapshot.generation_digest`. On `RegistryGenerationConflict` only, load a
   fresh coherent snapshot, reapply only the caller-declared field delta to the
   named artifact, and retry. Do not reuse a stale full-generation payload.
3. Use eight total attempts, including the initial attempt. This bound is the
   explicit owner-authorized safety budget, not a claim about dispatcher or
   worker configuration. It absorbs up to seven successive intervening commits.
   If an eighth attempt conflicts, raise a visible generation-conflict
   exhaustion error. A future certified concurrency floor above this liveness
   budget requires a separately reviewed bound change; safety remains intact
   because exhaustion never reports success or mutates a partial generation.
4. Retry no other exception. `RegistryTransactionInProgress`,
   `RegistryRecoveryRequired`, `RegistryCoverageError`, ordinary
   `RegistryAuthorizationError`, lock timeouts, and unexpected failures
   propagate immediately.
5. For amend operations with an expected generation, compare the coherent live
   generation before the request-digest idempotency lookup. This prevents a
   prior identical amend receipt followed by a legitimate later generation
   from being misclassified as recovery-required during retry. Preserve the
   existing registration path's idempotent-retry-before-stale-preimage ordering;
   WI-5714 does not change registration dry-run receipt semantics.
6. Add deterministic Windows-spawn, exact-subclass, retry-exhaustion,
   exception-taxonomy, accepted-delta preservation, coherent-read, parity, and
   no-partial-write coverage in the one approved test module.

## Deterministic Regression Design

The primary regression gate is a four-process Windows-spawn test. Each spawned
worker installs a child-local first-call wrapper around
`load_registry_snapshot`; the wrapper calls the real loader, waits on a shared
`Barrier(4)` only for that first call, then returns the captured snapshot.
Retries bypass the barrier. All four initial reads therefore observe the same
generation G before any apply begins. Each worker amends a different record.

On current source all four calls can report success while only the last full-
generation payload survives, so the assertion that all four deltas remain is
deterministically red. After the repair, one apply commits and the other three
receive the exact typed conflict, rebase their own field delta on fresh coherent
snapshots, and commit in serialized transaction order. The final snapshot must
contain all four accepted deltas. This child-local wrapping works under spawn;
it does not rely on propagating a parent pytest monkeypatch and needs no
production-only injection seam.

A separate in-process test deterministically inserts a committed generation
between amend read and apply, then asserts conflict, fresh rebase, and final
coherent parity. Spawn coverage is therefore both the required multi-process
gate and independently reinforced by a single-process interposition test.

## Rejected Alternative

Holding the registry file lock across the entire amend read-modify-write would
also prevent lost updates. It was rejected because `apply_registry_transaction`
already owns the exclusive lock, so a whole-operation lock requires a new
lock-aware internal transaction entry point or re-entrant lock semantics; it
would also serialize snapshot construction and field transformation for every
amend. Generation-CAS reuses the existing pre-mutation digest check, keeps lock
critical sections bounded to coherent read and commit, provides an actionable
conflict result, and better matches the owner's highly parallel requirement.
Both alternatives touch the same two governed artifacts; CAS has the smaller
transaction refactor and preserves the existing registration contract.

## Findings Addressed

### F1 - Measured red and green baselines

The exact two-process failure command, forced interleaving, observed one-of-two
retention, and 29-test green baseline are disclosed above.

### F2 - Deterministic concurrency gate

The four-process gate forces every first read to complete before any apply by
installing the wrapper inside each spawned child. Only the first read waits, so
fresh-snapshot retries cannot deadlock. The in-process interposition test is a
second deterministic gate; neither test depends on scheduler luck.

### F3 - Exact new subclass

The direct stale-generation test asserts `RegistryGenerationConflict` exactly,
not merely its `RegistryAuthorizationError` base. The proposal explicitly
acknowledges that the base-class denial and pre-mutation placement already pass.

### F4 - Governing assertion and coherent reads

`GIT-REQ-A11` is mapped below to retained accepted deltas, typed conflict,
snapshot coherence, declaration/package identity, projection parity, and no
false success. Generic applicability-preflight filler rows have been removed.

### F5 - Narrow outcome and residual work

Every completion claim is limited to `amend_artifact`. The generation-unbound
non-batch registration and legacy bootstrap paths are recorded in `WI-5736`
with linked `TEST-11748`; they are not authorized or implemented here.

### N1 through N6

The proposal now defines the retry taxonomy and amend-specific ordering,
compares the whole-operation lock alternative, cites both governing owner
decisions, prunes boilerplate links, uses commit type `fix`, and defines eight
total attempts as an explicit owner-authorized safety budget rather than an
unstated worker-cap inference.

## Cross-Harness Disposition

All harnesses consume the same canonical Python registry service. No harness-
local adapter, hook, prompt, rule, template, or configuration projection changes
are proposed for Claude, Codex, Cursor, Goose, Ollama, OpenRouter,
Antigravity, or Alibaba Cloud Studio.

## Residual Defects and Sequencing

- `WI-5736` / `TEST-11748` owns generation binding for non-batch
  `register_artifacts` and `bootstrap_legacy_registry` after WI-5714.
- `WI-5696` retains registry admission and passive content-observation scope.
- `WI-5697` retains identity, locator, lifecycle, move, rename, and delete transitions.
- `WI-5702` retains disaster-recovery scope.
- `WI-5715` retains coherent-read scalability and must rebase after WI-5714 because its source/test paths overlap.
- `WI-5292` shares `GIT-REQ-A11` lineage for MemBase concurrency but has no target-path overlap.

## Specification-Derived Verification Plan

| Requirement | Discriminating verification |
| --- | --- |
| `GOV-PLATFORM-SOT-REGISTRY-001` | Run the complete focused module; assert all four accepted disjoint amendments survive in the final authoritative declaration and resolver snapshot. |
| `REQ-GTKB-GOVERNED-GIT-LIFECYCLE-001` / `GIT-REQ-A11` | Run the forced four-process first-read-barrier gate and the deterministic in-process interposition test; assert preservation or typed conflict, no lost update, no false success, and a coherent committed final read. |
| `DCL-SOT-REGISTRY-PROJECTION-PARITY-001` | After the concurrent wave and after conflict exhaustion, assert canonical/package byte identity, snapshot declaration/projection parity, and terminal journal state. |
| `DCL-ARTIFACT-REGISTRY-MUTATION-AUTHORIZATION-001` | Assert the exact new conflict subclass is raised before journal insertion or any canonical, packaged, or projection change; compare pre/post digests and journal row count. |
| `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` | Verify the active WI-5714-only PAUTH allows only source/test mutation and both changed paths match its exact targets. |
| `DCL-PROJECT-AUTHORIZATION-OPERATION-TIME-ENFORCEMENT-001` | Run `implementation_authorization.py begin` only after GO and confirm its packet binds WI-5714, the current session claim, and exactly the two target paths. |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | Verify the append-only v001-v003 chain, independent GO, exact-session claim, implementation-start evidence, strict NEW report, independent verdict, and governed finalization. |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | Run candidate and live bridge applicability preflights and require zero missing blocking specification links. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | The implementation report must list each command, collected count, result, and acceptance-criterion mapping; terminal verification must rerun them independently. |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | Confirm every source, test, and runtime fixture path resolves within `E:/GT-KB` and no adopter repository is touched. |
| `GOV-WORK-TREE-HYGIENE-001` | Run exact two-path `git status`, `git diff`, and `git diff --check`; preserve the three pre-existing untracked bridge files and every unrelated change. |
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | Confirm the implementation report links this revision, WI-5714, TEST-11732, the exact changed paths, executed results, and the independent verdict; confirm WI-5736 / TEST-11748 remain separately traceable. |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | Confirm v003 remains REVISED until independent GO, protected mutation begins only after implementation-start, and completion is not claimed before independent VERIFIED plus governed finalization. |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | Show that both out-of-scope residual writers are captured in WI-5736 with linked TEST-11748 and are absent from the WI-5714 diff. |

## Planned Focused Tests

- `test_amend_spawned_disjoint_writers_preserve_every_accepted_delta`
- `test_amend_generation_mismatch_raises_exact_conflict_before_mutation`
- `test_amend_rebases_declared_delta_after_deterministic_interposed_commit`
- `test_amend_retry_exhaustion_is_eight_attempts_and_has_no_side_effects`
- `test_amend_retries_only_generation_conflict`
- Existing `test_fault_phases_never_expose_mixed_generation` parameter cases
- Complete `groundtruth-kb/tests/test_registry_control_plane.py` suite

## Acceptance Criteria

1. A direct stale-generation amend apply raises the exact new
   `RegistryGenerationConflict` subclass before canonical, packaged,
   projection, or journal mutation. The pre-existing base-class behavior is
   not counted as the regression proof.
2. Four forced-interleaving Windows-spawn writers amending disjoint records all
   report success and all four caller-declared deltas survive in one coherent
   final generation.
3. A deterministic interposed commit causes the stale attempt to conflict and
   the caller's declared field delta to be reapplied to a fresh snapshot; both
   accepted changes survive.
4. Only `RegistryGenerationConflict` is retried. In-progress, recovery-required,
   coverage, authorization, lock, and unexpected errors propagate immediately.
5. Eight total conflicting attempts fail visibly on the eighth, record no false
   success, insert no journal row, and leave canonical, packaged, and projection
   preimages unchanged.
6. Concurrent and fault-phase reads either return one coherent committed
   generation or a typed failure; no mixed declaration/package/projection state
   is exposed. Canonical and packaged bytes remain identical and projection and
   journal receipts describe the retained generation.
7. The existing 29-test baseline plus all new tests pass; Ruff check, Ruff
   format check, and exact two-path diff checks pass.
8. `register_artifacts` and `bootstrap_legacy_registry` behavior is unchanged by
   this implementation and remains visibly assigned to `WI-5736`.

## Pre-Filing Preflight Subsection

The completed candidate passed both commands before filing:

```powershell
groundtruth-kb\.venv\Scripts\python.exe scripts\bridge_applicability_preflight.py --bridge-id gtkb-wi5714-registry-write-linearizability --content-file .gtkb-state\bridge-revisions\drafts\gtkb-wi5714-registry-write-linearizability-003.md --json
groundtruth-kb\.venv\Scripts\python.exe scripts\adr_dcl_clause_preflight.py --bridge-id gtkb-wi5714-registry-write-linearizability --content-file .gtkb-state\bridge-revisions\drafts\gtkb-wi5714-registry-write-linearizability-003.md
```

Results: applicability preflight exit `0`, `preflight_passed=true`, no missing
required specifications, and no blocking errors; clause preflight exit `0`,
four `must_apply` clauses with evidence, and zero blocking gaps. The governed
revision helper repeats both checks on its final metadata-enriched candidate and
refuses publication on any nonzero result.

## Risk And Rollback

Risk is moderate: the change touches a shared registry transaction path, but is
limited to amend conflict classification, retry orchestration, and focused
tests. The highest risks are accidental retry of recovery-required state,
breaking existing registration idempotency, or a retry that reapplies stale
full-generation data. The exception taxonomy, amend-specific ordering,
deterministic interposition, and exact no-side-effect assertions cover those
risks.

Rollback requires separate governed authority to revert only the two approved
implementation paths, followed by the complete focused suite and parity checks.
The numbered bridge chain, WI-5736, TEST-11748, owner decisions, project
authorization, implementation report, and verdict evidence are append-only and
must not be deleted by rollback.

## Files Expected To Change

- `groundtruth-kb/src/groundtruth_kb/project/registry_control_plane.py`
- `groundtruth-kb/tests/test_registry_control_plane.py`

## Recommended Commit Type

`fix`
