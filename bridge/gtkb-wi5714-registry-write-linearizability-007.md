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
Version: 007
Date: 2026-07-29 UTC
Responds to: bridge/gtkb-wi5714-registry-write-linearizability-006.md

Project Authorization: PAUTH-PROJECT-GTKB-HOUSEKEEPING-HARDENING-WI5714-REGISTRY-LINEARIZABILITY-20260729
Project: PROJECT-GTKB-HOUSEKEEPING-HARDENING
Work Item: WI-5714

target_paths: ["groundtruth-kb/src/groundtruth_kb/project/registry_control_plane.py", "groundtruth-kb/tests/test_registry_control_plane.py"]

implementation_scope: source
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

This proposal performs no production MemBase or `groundtruth.db` mutation.
SQLite projection changes occur only inside pytest-managed temporary registry
fixtures and are discarded runtime evidence.

## Revision Claim

This correction carries forward the accepted generation-CAS design and exact
two-file scope from v005. It changes only the verification lifecycle:

1. The implementation report must prove that the exact-session work-intent
   claim and implementation-start packet were live and valid at protected
   mutation and report-filing time, and must preserve their identifiers,
   timestamps, target scope, PAUTH decision, and provenance as durable evidence.
2. Independent terminal verification must freshly validate that durable
   operation-time evidence and rerun all still-live canonical reads. It must
   not require the claim or GO-derived start packet to remain live after the
   report changes the thread from GO to NEW.
3. Lifecycle verification now names the complete v001-v005 pre-review chain
   and the operative v005 REVISED proposal. This v007 responds to v006 and does
   not reuse the obsolete v003 wording.

No implementation mechanism, retry bound, target, owner authority, or residual
work disposition changes.

## Requirement Sufficiency

Requirements remain sufficient. `DELIB-202667522` authorizes the exact
generation-conflict subclass, fresh-snapshot retry, eight-total-attempt bound,
and deterministic Windows-spawn coverage. The v006 corrections clarify how
durable operation-time proof survives the normal bridge lifecycle; they do not
expand authority.

## In-Root Placement Evidence

Both targets are within `E:/GT-KB`. All concurrency and projection fixtures use
pytest-managed in-root temporary state. No application repository or
harness-local memory is a live dependency.

## Specification Links

- `GOV-PLATFORM-SOT-REGISTRY-001` - preserves one coherent declaration, packaged mirror, and projection generation.
- `GOV-SOURCE-OF-TRUTH-FRESHNESS-001` - requires fresh mutable-state reads while distinguishing durable operation-time proof from controls that are expected to expire.
- `REQ-GTKB-GOVERNED-GIT-LIFECYCLE-001` / `GIT-REQ-A11` - requires accepted concurrent registry writes to be linearizable or conflict-detected with no false success.
- `DCL-SOT-REGISTRY-PROJECTION-PARITY-001` - requires canonical/package/projection/journal coherence after success and exhaustion.
- `DCL-ARTIFACT-REGISTRY-MUTATION-AUTHORIZATION-001` - requires pre-mutation conflict detection without weakening registry mutation evidence.
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` - bounds implementation to WI-5714 and the two declared source/test paths.
- `DCL-PROJECT-AUTHORIZATION-OPERATION-TIME-ENFORCEMENT-001` - requires a live exact claim and start packet when protected mutation begins and durable evidence of that decision afterward.
- `GOV-FILE-BRIDGE-AUTHORITY-001` - governs the complete numbered chain, claim, independent GO, report, verdict, and finalization lifecycle.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - requires these concrete links.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - requires executed evidence for every row below.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - keeps the platform repair outside adopter applications.
- `GOV-WORK-TREE-HYGIENE-001` - limits mutation and diff evidence to the two approved targets.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` - preserves the proposal, findings, implementation report, residual WI-5736, and verdict graph.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - keeps REVISED, GO, report NEW, VERIFIED, and finalization distinct.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` - keeps residual writers in WI-5736 / TEST-11748 instead of widening this slice.

## Prior Deliberations

- `DELIB-202667517` - requires linearizable or conflict-detected shared-control-plane writes with no false success.
- `DELIB-202667522` - authorizes this exact WI-5714 generation-CAS repair and deterministic coverage.
- `DELIB-2521` - supplies freshness authority for live rereads rather than copied proposal observations.

## Owner Decisions / Input

- `DELIB-202667517` and `DELIB-202667522` remain the governing owner decisions.
- No new owner action is required; v006 asks only for lifecycle-compatible evidence wording and current chain references.

## Proposed Scope

1. Add `RegistryGenerationConflict` as a strict subclass of
   `RegistryAuthorizationError` and raise it when an amend-bound expected
   generation differs from the coherent live generation.
2. Bind each `amend_artifact` apply attempt to the snapshot generation it read.
   Retry only `RegistryGenerationConflict`, always from a fresh coherent
   snapshot, and reapply only the caller-declared field delta.
3. Permit eight total attempts including the initial attempt. The eighth
   conflict fails visibly without a journal row, partial mutation, or false
   success.
4. Propagate in-progress, recovery-required, coverage, ordinary authorization,
   lock, and unexpected failures without retry.
5. For amend operations only, compare expected generation before request-digest
   idempotency lookup. Preserve registration dry-run/idempotency ordering.
6. Add deterministic four-process Windows-spawn and in-process interposition
   coverage plus exact subclass, exhaustion, taxonomy, coherent-read, parity,
   and no-partial-write assertions.

## Deterministic Regression Design

Four spawned workers each install a child-local first-call wrapper around the
real `load_registry_snapshot`, capture generation G, and wait on one shared
`Barrier(4)`. Each amends a different record. Retries bypass the barrier. The
final coherent snapshot must retain all four accepted deltas.

A separate in-process test inserts a committed generation between amend read
and apply, then proves exact typed conflict, fresh rebase of only the declared
delta, and preservation of both accepted changes. Exhaustion forces eight
successive conflicts and proves unchanged declaration/package/projection
preimages and journal row count.

## Findings Addressed

### F1 (P1) - Terminal verification cannot require ephemeral controls to remain live

Accepted. The implementation-report freshness gate now requires a fresh live
claim and implementation-start validation before report filing, followed by
durable capture of claim row ID/session/role/acquisition/expiry, packet hash,
creation/expiry, GO/proposal paths, PAUTH decision and hash, and exact targets.
Terminal verification freshly reads that durable report evidence and checks it
proved authorization at mutation/report time. It does not require the released
or expired claim, or the GO-derived packet invalidated by report NEW, to be
currently live. All other mutable registry, WI/project/PAUTH, bridge-chain,
target-diff, and parity evidence is freshly rerun by the verifier.

### F2 (P2) - The lifecycle rows cite stale chain state

Accepted. `GOV-FILE-BRIDGE-AUTHORITY-001` now requires validation of the full
v001-v005 chain reviewed by v006, followed by v006, this v007, independent GO,
report, and verdict. `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` now states that v007
remains REVISED until independent GO; it no longer names v003 as operative.

## Scope Changes

None. The approved mechanism, two target paths, eight-attempt bound, exception
taxonomy, deterministic tests, and WI-5736 residual remain unchanged.

## Cross-Harness Disposition

All harnesses consume the same canonical Python registry service. No adapter,
hook, prompt, rule, template, dispatcher route, or harness configuration is in
scope.

## Residual Defects And Sequencing

- `WI-5736` / `TEST-11748` owns generation binding for non-batch
  `register_artifacts` and `bootstrap_legacy_registry` after WI-5714.
- `WI-5715` overlaps both targets and rebases after WI-5714.
- `WI-5696`, `WI-5697`, and `WI-5702` retain their separate registry scopes.
- `WI-5292` shares requirement lineage but has no target overlap.

## Specification-Derived Verification Plan

| Requirement | Discriminating verification |
| --- | --- |
| `GOV-PLATFORM-SOT-REGISTRY-001` | Run the complete focused module and assert all four accepted disjoint amendments survive in the authoritative declaration and resolver snapshot. |
| `GOV-SOURCE-OF-TRUTH-FRESHNESS-001` | At report time, freshly validate live claim/start packet and capture durable identifiers, timestamps, scope, hashes, and provenance. At terminal review, validate that durable evidence and freshly rerun the promoted regression, focused pytest, exact WI/project/PAUTH reads, complete numbered bridge chain, exact target diff/status, and registry parity. Do not require expired controls to remain live. |
| `REQ-GTKB-GOVERNED-GIT-LIFECYCLE-001` / `GIT-REQ-A11` | Run forced four-process first-read-barrier and deterministic interposition tests; assert preservation or typed conflict, no lost update, no false success, and coherent final reads. |
| `DCL-SOT-REGISTRY-PROJECTION-PARITY-001` | After concurrent success and retry exhaustion, assert canonical/package byte identity, projection parity, and correct terminal journal state. |
| `DCL-ARTIFACT-REGISTRY-MUTATION-AUTHORIZATION-001` | Assert exact conflict before journal/declaration/package/projection mutation and compare pre/post digests and journal row count. |
| `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` | Freshly verify the current WI-5714 PAUTH and exact two-target scope before mutation; preserve the result in the report. |
| `DCL-PROJECT-AUTHORIZATION-OPERATION-TIME-ENFORCEMENT-001` | Begin only after independent GO with the exact-session claim and two-target packet; report durable packet/claim evidence, and have terminal review validate that evidence rather than require current liveness. |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | Validate the complete v001-v005 chain, v006 NO-GO, this v007 REVISED, independent GO, exact-session claim/start evidence, strict NEW report, independent verdict, and governed finalization. |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | Run candidate and filed applicability preflights and require zero missing blocking links. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | Report every command, timestamp/generation anchor, collected/pass count, and acceptance mapping; terminal verification reruns the decisive tests independently. |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | Confirm source/test/runtime paths stay within `E:/GT-KB` and no adopter repository changes. |
| `GOV-WORK-TREE-HYGIENE-001` | Run exact two-path status/diff/diff-check and preserve every unrelated change. |
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | Link v007, WI-5714, TEST-11732, exact changed paths, executed report evidence, verdict, and separately tracked WI-5736 / TEST-11748. |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | Confirm v007 remains REVISED until independent GO; mutation begins only with live claim/start authorization; completion waits for report, VERIFIED, and governed finalization. |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | Confirm both residual writers remain recorded in WI-5736 / TEST-11748 and absent from the WI-5714 diff. |

## Planned Focused Tests

- `test_amend_spawned_disjoint_writers_preserve_every_accepted_delta`
- `test_amend_generation_mismatch_raises_exact_conflict_before_mutation`
- `test_amend_rebases_declared_delta_after_deterministic_interposed_commit`
- `test_amend_retry_exhaustion_is_eight_attempts_and_has_no_side_effects`
- `test_amend_retries_only_generation_conflict`
- Existing `test_fault_phases_never_expose_mixed_generation` cases
- Complete `groundtruth-kb/tests/test_registry_control_plane.py` suite

## Acceptance Criteria

1. Direct stale-generation amend raises exact `RegistryGenerationConflict`
   before canonical, packaged, projection, or journal mutation.
2. Four forced-interleaving spawned writers all report success and all four
   declared deltas survive in one coherent final generation.
3. A deterministic interposed commit causes typed conflict and fresh rebase;
   both accepted changes survive.
4. Only the exact conflict subclass is retried; all other failures propagate.
5. Eight total conflicts fail on the eighth with no false success, journal row,
   or preimage change.
6. Concurrent/fault-phase reads return one coherent generation or typed failure;
   canonical/package bytes, projection, and journal remain consistent.
7. Existing and new focused tests pass with Ruff and exact two-path diff checks.
8. `register_artifacts` and `bootstrap_legacy_registry` remain unchanged and
   visibly assigned to WI-5736.
9. The report proves live authorization at mutation/report time with durable
   claim/start evidence. Terminal verification validates that durable proof and
   freshly reruns all remaining canonical state/tests without requiring those
   ephemeral controls to remain live.

## Pre-Filing Preflight Subsection

Candidate commands:

```powershell
python scripts/bridge_applicability_preflight.py --content-file .gtkb-state/bridge-revisions/drafts/gtkb-wi5714-registry-write-linearizability-007.md
python scripts/adr_dcl_clause_preflight.py --content-file .gtkb-state/bridge-revisions/drafts/gtkb-wi5714-registry-write-linearizability-007.md
```

Observed on 2026-07-29 UTC: applicability exit 0,
`preflight_passed=true`, zero missing required/advisory specifications, and zero
blocking errors. Mandatory clause preflight exit 0: five clauses evaluated,
four `must_apply`, one `may_apply`, zero must-apply evidence gaps, and zero
blocking gaps. The governed revision helper repeats compliance checks on the
metadata-enriched candidate; both commands are repeated against the filed
bridge ID.

## Risk And Rollback

Risk remains moderate because the change touches the shared registry
transaction path. The principal risks are retrying recovery-required state,
breaking registration idempotency, or reapplying a stale full-generation
payload. Exact exception taxonomy, amend-only ordering, forced interposition,
and pre/post parity assertions cover those risks.

Rollback requires separate governed authority to revert only the two approved
paths, followed by the complete focused suite and parity checks. The numbered
chain, WI-5736, TEST-11748, owner decisions, report, and verdict are append-only.

## Files Expected To Change

- `groundtruth-kb/src/groundtruth_kb/project/registry_control_plane.py`
- `groundtruth-kb/tests/test_registry_control_plane.py`

## Recommended Commit Type

`fix`
