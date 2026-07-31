NEW
::init gtkb pb
::open build
author_identity: prime-builder/codex
author_harness_id: A
author_session_context_id: 019fb19b-7814-73c1-8707-204e432cbf00
author_model: GPT-5
author_model_version: GPT-5 Codex desktop runtime
author_model_configuration: Codex Desktop interactive Prime Builder; transcript-resolved role prime-builder; dispatcher deliberately disabled
author_metadata_source: explicit_interactive_session_metadata

# Advisory Report - Bridge-publication recovery retains cross-process filesystem TOCTOU exposure

bridge_kind: governance_review
Document: gtkb-advisory-bridge-publication-recovery-toctou
Version: 001
Date: 2026-07-30 UTC
Project Authorization: PAUTH-PROJECT-GTKB-ADVISORY-CORRECTIONS-20260729-PROGRAM
Project: PROJECT-GTKB-ADVISORY-CORRECTIONS-20260729
Work Item: WI-5758
target_paths: []

implementation_scope: none
requires_review: true
requires_verification: false
kb_mutation_in_scope: false
dispatcher_or_tafe_mutation_in_scope: false

## Summary

Independent implementation review of WI-5758 found a residual concurrency
class in the bridge-publication control plane. The registry file lock
serializes participating control-plane calls, but filesystem creation,
replacement, deletion, and sidecar cleanup are not covered by one end-to-end
cross-process exclusion boundary. Recovery, ordinary consume, and compensation
therefore contain check-then-act windows in which a second actor can change a
bridge file or aggregate member after validation but before evidence append,
capability transition, quarantine, or cleanup.

WI-5758 now applies bounded mitigations inside its reviewed scope: exact
sidecar-to-row bindings, crash-idempotent rollback, atomic rollback quarantine,
stable repeated finalize observation, cleanup ordering, and hard-exit tests.
Those changes close the destructive rollback race found in the new recovery
path. They do not prove universal filesystem/SQLite atomicity across the
pre-existing consume and compensate paths or against direct editors, Git, and
other writers that do not honor `_RegistryFileLock`.

This Advisory preserves that broader obligation for independent review and
later corrective intake. It authorizes no implementation and does not activate
or mutate dispatcher/TAFE state.

## Claim

The transaction is split across two synchronization domains:

1. `_RegistryFileLock` plus SQLite transactions serialize registry revisions
   and capability-row compare-and-set transitions.
2. Bridge files and recovery sidecars remain ordinary filesystem objects that
   other processes can create, replace, delete, or restore without acquiring
   that lock.

A capability-row state transition can prove which caller changed a database
row. It cannot, by itself, prove that the file hashed earlier is still the file
observed, quarantined, or deleted later. Correctness therefore requires exact
generation binding plus a shared filesystem coordination contract across every
supported bridge mutation path.

## Evidence And Race Windows

### E1 - Mint, create, and consume are not one critical section

`scripts/gtkb_bridge_writer.py` calls
`mint_bridge_publication_capability()`, returns after that function releases
the registry lock, writes the durable sidecar, exclusively creates the bridge
file, re-reads it, and only then calls
`consume_bridge_publication_capability()`.

The exclusive create protects one target path from overwrite at that instant.
It does not serialize aggregate changes at sibling `bridge/*-NNN.md` paths,
nor does it exclude an editor, Git operation, repair tool, or direct writer.

### E2 - Recovery finalize remains a bounded stable-observation protocol

`groundtruth-kb/src/groundtruth_kb/project/registry_control_plane.py` now
requires exact target bytes, proves the aggregate preimage without the target,
requires the latest recorded preimage revision, scans the live aggregate,
revalidates target bytes, rescans the aggregate, and revalidates target bytes
again before appending evidence and consuming the row.

This is a strong bounded mitigation: a mutation during either scan fails
closed. It is not universal exclusion. A direct writer can still mutate after
the last validation and before `_append_revision()` completes, or immediately
after the observed linearization point. The resulting staleness is detectable,
but filesystem identity is not atomically locked to the SQLite commit.

### E3 - Atomic quarantine closes the new destructive rollback window

The original WI-5758 recovery implementation validated target bytes, retained
them in memory, and later called `unlink()`. A concurrent replacement between
those operations could be deleted even though it was never authorized by the
capability.

The corrected recovery path uses a deterministic same-volume quarantine under
`.gtkb-state/bridge-publication-recovery/`. It atomically moves the directory
entry, hashes the quarantined bytes against the exact capability row, restores
or retains mismatched/unknown bytes, and deletes only the validated quarantine
after the compensation transaction commits. Two fresh-process hard-exit tests
cover:

- exit after quarantine but before compensation commit; and
- exit after commit but before quarantine cleanup.

Both retries are idempotent and preserve exact bytes. This mitigation should be
extended to the older secret-bearing compensation path rather than assumed to
cover it.

### E4 - Existing compensation retains the adjacent destructive class

`compensate_bridge_publication()` validates target bytes and aggregate lineage,
then later removes the target. It does not yet use the new recovery
quarantine protocol. A replacement between its validation and removal can
therefore reproduce the foreign-byte deletion class outside
`recover_bridge_publication()`.

### E5 - Existing consume retains an observation race

`consume_bridge_publication_capability()` compares the aggregate digest
observed by `_append_revision()` with its prior live scan, which closes an
important portion of the race. It still lacks a filesystem mutex shared with
all direct writers. A subsequent mutation can immediately stale the aggregate,
and an outer failure can enter the compensation window described above.

### E6 - Sidecar identity is now exact, but compare-and-delete is residual

The sidecar persists capability hash, content digest, document, version,
status, target, and session without the raw bearer secret. WI-5758 now passes
those fields to recovery, selects the exact row by capability hash plus
target/session, verifies every binding, and derives claim release from the
verified receipt. A corrupted or stale sidecar can no longer redirect recovery
to the latest row for the same target/session.

The sidecar filename remains target-derived, and cleanup is not a universal
filesystem compare-and-delete primitive. An older process and a retry could
still contend for that path. A future coordinator or generation-specific
sidecar name should close that residual window.

## Consequences

- Foreign or replacement bytes can be lost if an uncorrected destructive path
  validates one generation and removes another.
- A capability can become consumed while target bytes, aggregate digest, and
  appended revision describe different filesystem moments.
- Currentness can be true for a snapshot without proving exclusive ownership
  of the subsequent filesystem-to-database transition.
- Partial detection can retain a file and capability in `recovery_required`
  without one deterministic safe remedy.
- Longer append-only aggregate scans widen overlap windows and increase lock
  convoying even when correctness ultimately fails closed.

## Append-Only SoT And Access-Cost Context

The affected registry identity is a glob-backed aggregate over append-only
bridge history. Preserving role-authored transitions and review chronology is
valuable; this finding does not recommend mutable-in-place bridge history.

The cost of repeatedly proving the full aggregate nevertheless grows with that
history. A read-only live measurement after the WI-5758 state-report change on
2026-07-30 completed successfully in **19.291 seconds** and materialized
**630,546 output characters**. The report now performs a scoped
`bridge-versioned-files` currentness check in addition to enumerating current
thread state. The already-filed
`bridge/gtkb-sot-access-latency-append-only-growth-cost-advisory-001.md`
documents the broader population and earlier multi-minute/time-out cases.

Safety and access cost must be solved together. A coarse lock held across
repeated full-tree hashes can exclude races while creating a scale-dependent
serialized bottleneck. A bounded critical section with an efficient
authoritative aggregate-generation token is the lower-regret direction; full
tree hashing can remain rebuild/parity evidence rather than a repeated hot-path
operation.

## Immediate Mitigations Applied Within WI-5758

1. Bind restart recovery to exact capability hash, content digest, document,
   version, status, target, and session.
2. Accept idempotent terminal `compensated` retries and recover both rollback
   crash windows.
3. Quarantine rollback targets atomically, validate quarantine bytes, and
   restore or retain unknown bytes instead of unlinking an unchecked path.
4. Re-scan finalize aggregate state and target bytes to establish a stable
   bounded observation before the database transition.
5. Ensure sidecar cleanup failure after claim release cannot compensate a
   successfully published file.
6. Emit a runnable operator remedy including the mandatory `--change-reason`.
7. Test real process death rather than only clearing module memory.

These are containment measures, not a claim that every filesystem actor shares
one transaction boundary.

## Recommended Corrective Direction

1. Introduce one cross-process bridge-publication coordinator used by
   mint/create/consume, recovery finalize/rollback, compensation, and sidecar
   cleanup.
2. Keep the critical section bounded: prepare immutable inputs outside it,
   then validate an exact aggregate generation, perform the file/row
   transition, and revalidate before release.
3. Extend atomic quarantine to `compensate_bridge_publication()`.
4. Use capability-state and predecessor-revision/generation compare-and-set
   predicates; row state alone is insufficient.
5. Make sidecar cleanup generation-specific or compare-and-delete under the
   coordinator.
6. Make `_append_revision()` expose the exact digest it observed and bind that
   digest to the capability transition.
7. Investigate an incrementally maintained aggregate-generation index with
   deterministic full-scan rebuild/parity checks, without creating a competing
   SoT.
8. Preserve append-only history; retention, compaction, or archival policy is
   separate architecture work requiring measured evidence and approval.

## Concurrency-Derived Verification Plan

| Test | Deterministic interleaving | Required result |
| --- | --- | --- |
| T1 | Replace target after validation in recovery rollback | Replacement is not deleted; exact unknown bytes are retained; row fails closed. |
| T2 | Repeat T1 in `compensate_bridge_publication()` | Same preservation and `recovery_required` behavior. |
| T3 | Create a sibling bridge member during recovery finalize | No revision or consume transition is attributed to the wrong aggregate generation. |
| T4 | Supply an older sidecar where two same-target/session rows exist | Only the exact capability hash is selected; recency cannot redirect recovery. |
| T5 | Replace sidecar generation after an older process loads it | Older cleanup cannot delete the replacement generation. |
| T6 | Mutate target or sibling member during ordinary consume | Capability remains unconsumed or records exactly one stable authorized generation. |
| T7 | Hard-exit after every file/row/sidecar boundary | Every restart is idempotently finalizable or roll-backable without claim or byte loss. |
| T8 | Run two supported writers and one recovery worker with barriers | Coordinator establishes a deterministic total order for filesystem mutation. |
| T9 | Repeat T1-T8 at representative small and large bridge populations | Safety is invariant; lock hold time and scan cost stay within a declared budget. |
| T10 | Exercise native Windows rename, quarantine, restore, and cleanup | Windows file-sharing semantics preserve the same fail-closed contract. |

## Specification-Derived Verification

The current bounded mitigation was executed before this Advisory was filed:

- `groundtruth-kb/.venv/Scripts/python.exe -m pytest platform_tests/scripts/test_gtkb_bridge_writer.py groundtruth-kb/tests/test_registry_control_plane.py platform_tests/groundtruth_kb/cli/test_bridge_state_report_cli.py platform_tests/groundtruth_kb/cli/test_registry_observe_cli.py -q --tb=short`
  - observed result: `102 passed`, one pre-existing `asyncio_mode` warning, 74.52 seconds;
- post-format focused hard-exit, exact-binding, cleanup-order, recovery, and
  state-report tests: `7 passed`, the same warning, 11.04 seconds;
- Ruff check across all eight WI-5758 target files: `All checks passed!`;
- Ruff format check: `8 files already formatted`;
- `git diff --check -- <eight WI-5758 targets>`: exit 0, only Git's
  informational future-CRLF warnings.

These results verify the bounded mitigations described above. They do not
satisfy future T1-T10 for universal cross-process exclusion; those tests are
the acceptance evidence required of a derived correction.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001`
- `GOV-PLATFORM-SOT-REGISTRY-001`
- `GOV-SOURCE-OF-TRUTH-FRESHNESS-001`
- `DCL-ARTIFACT-REGISTRY-MUTATION-AUTHORIZATION-001`
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001`
- `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001`
- `DCL-PROJECT-AUTHORIZATION-OPERATION-TIME-ENFORCEMENT-001`
- `GOV-WORK-TREE-HYGIENE-001`
- `GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001`
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001`

## Prior Deliberations And Related Work

- `DELIB-202667526` - live control-plane concurrency and lock-convoy evidence.
- `DELIB-202667531` through `DELIB-202667534` - advisory-corrections program
  triage, design constraints, and WI-5758 routing.
- `bridge/gtkb-wi5758-publication-deadlock-closure-001.md` and `-002.md` -
  reviewed bounded implementation scope and independent GO.
- `bridge/gtkb-advisory-work-intent-release-db-lock-concurrency-001.md` -
  separate work-intent SQLite release-lock failure.
- `bridge/gtkb-advisory-implementation-start-peer-scan-liveness-001.md` and
  `bridge/gtkb-advisory-bridge-propose-cold-import-duplicate-audit-latency-001.md`
  - adjacent append-only hot-path costs.
- `bridge/gtkb-sot-access-latency-append-only-growth-cost-advisory-001.md` -
  broader bridge, MemBase, registry-lock, and deliberation-corpus scale report.

## Owner Decisions / Input

No immediate owner decision is required to preserve or independently review
this Advisory. Any derived corrective implementation must first be linked to
an active project and inherit that project's active bounded PAUTH. If no
existing authorized project carrier covers the eventual scope, Prime Builder
must present one AUQ for project approval before implementation. No per-WI or
orphan approval is valid.

## Requirement Sufficiency

Existing requirements are sufficient to preserve this finding and to demand
fail-closed exact-byte behavior. They are not sufficient to select a universal
coordinator or aggregate-index architecture without alternatives investigation
and independent review. WI-5758's active GO authorizes only its eight reviewed
targets and bounded safety corrections, not the broader redesign.

## Risk And Rollback

This report is append-only diagnostic evidence and mutates no implementation
surface. Its principal risk is overstating the bounded WI-5758 mitigations as
universal exclusion; the text explicitly preserves the residual class.

Rollback is not deletion of this history. If evidence is corrected or
superseded, publish a later numbered bridge entry that cites the exact changed
facts and replacement carrier.

## Mutation Boundary

This Advisory authorizes no source, test, configuration, formal-artifact,
project, PAUTH, MemBase, database, dispatcher/TAFE, credential, external-system,
deployment, release, Git-index, commit, push, or destructive-cleanup mutation.
TAFE remains deliberately disabled and untouched.

---

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.

