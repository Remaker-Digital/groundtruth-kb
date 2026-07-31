NEW
::init gtkb pb
::open build

author_identity: prime-builder/codex/A
author_harness_id: A
author_session_context_id: 019fb19b-7814-73c1-8707-204e432cbf00
author_model: gpt-5.6-sol
author_model_version: gpt-5.6-sol
author_model_configuration: Codex Desktop interactive Prime Builder; transcript-defined ::init gtkb pb; dispatcher deliberately disabled
author_metadata_source: explicit_interactive_session_metadata

# Advisory Report - Implementation-start peer scan has append-only SoT scale-dependent liveness failure

bridge_kind: governance_review
Document: gtkb-advisory-implementation-start-peer-scan-liveness
Version: 001
Date: 2026-07-30 UTC

target_paths: []
implementation_scope: none
requires_review: true
requires_verification: false
kb_mutation_in_scope: false
dispatcher_or_tafe_mutation_in_scope: false

## Summary

The implementation-start authorization path has a reproducible liveness failure
whose cost grows with two append-only system-of-truth populations. For every
named implementation packet, the peer dirty-path collision guard resolves that
packet's bridge lifecycle; each lifecycle resolution linearly enumerates the
entire top-level `bridge/` directory. At the observed repository scale this is
an approximately `507 x 14,086 = 7,141,602` directory-entry comparison upper
bound before the requested start transaction can complete.

The exact no-write WI-5761 positive-path probe produced no output for more than
90 seconds. A second no-write diagnostic emitted a 15-second faulthandler stack
inside this repeated enumeration path. Both exact processes were terminated
only after their command lines were verified. No authorization packet, source
change, test change, database mutation, dispatcher/TAFE action, or external
action occurred, and the WI-5761 claim was released.

This is not an argument against append-only system-of-truth history in general.
It is a concrete case where a hot operation repeatedly performs unindexed full
enumeration of an append-only SoT. The resulting latency already prevents
ordinary governed implementation starts and will worsen as packets and bridge
history accumulate.

## Advisory Classification

- Category: concurrency and append-only SoT access-cost/liveness defect.
- Affected operation: implementation-start authorization with non-empty target paths.
- Immediate consumer: `scripts/implementation_authorization.py begin`.
- Scale dimensions: named implementation packets and top-level bridge files.
- Concurrency sensitivity: concurrent sessions add packets/history and hold
  work-intent claims while a slow start is evaluating, increasing claim-TTL and
  collision windows even when no database lock is involved.
- Authority: review-only advisory. This artifact does not authorize corrective
  implementation or create project/WI approval.

## Claim

`peer_report_dirty_path_collision_reason()` has an avoidable
`O(named_packets x bridge_files)` access pattern over append-only governed
state. The current population makes the start gate practically non-live. The
gate should preserve fail-closed collision semantics while replacing repeated
full-tree discovery with bounded or indexed lifecycle access.

## Source And Context

The failure was encountered while processing the independently approved GO for
`gtkb-wi5761-project-reactivation-invariant`. That proposal declares seven
clean source/test targets and is an active member of an active, whole-project
authorized project. The proposal applicability preflight passed. The
implementation-start no-write probe was therefore exercising the ordinary
positive path, not a synthetic standalone benchmark.

The first probe was:

```text
python scripts/implementation_authorization.py begin --bridge-id gtkb-wi5761-project-reactivation-invariant --session-id 019fb19b-7814-73c1-8707-204e432cbf00 --no-write
```

It emitted no output for more than 90 seconds. A second probe used
`faulthandler.dump_traceback_later(15)` around the same no-write path and
captured the stack below.

## Evidence

### E1 - Repeated peer iteration

`scripts/implementation_authorization.py:1643-1651` iterates every JSON packet
under the named `by-bridge` packet directory. For each historical peer packet,
line 1651 calls `_peer_implementation_report_paths()`.

### E2 - Each peer resolves a bridge lifecycle

`scripts/implementation_authorization.py:1596-1600` shows
`_peer_implementation_report_paths()` calling `bridge_entry()` for the peer
bridge ID. This occurs inside the per-packet loop rather than against a shared
bridge-history index.

### E3 - Each lifecycle resolution scans the entire bridge directory

`scripts/bridge_lifecycle_resolver.py:131-146` implements
`_exact_version_paths()` by iterating `bridge_dir.iterdir()` and applying an
exact-name regular expression for the one requested bridge ID. Repeating this
for every packet re-enumerates the same append-only SoT population.

### E4 - Live cardinality

At the time of the failure:

- named implementation packets: 507;
- top-level bridge Markdown files: 14,086;
- naive repeated-scan upper bound: 7,141,602 directory-entry comparisons.

This bound excludes lifecycle parsing, file reads, packet validation, dirty-tree
enumeration, Python object allocation, and filesystem metadata overhead. It is
therefore a conservative explanation for the observed latency rather than a
complete cost model.

### E5 - Captured no-write diagnostic stack

The 15-second stack was:

```text
pathlib.Path.iterdir
scripts/bridge_lifecycle_resolver.py:141 in _exact_version_paths
scripts/bridge_lifecycle_resolver.py:666 in resolve_bridge_lifecycle
scripts/implementation_authorization.py:327/352 in bridge_entry
scripts/implementation_authorization.py:1599 in _peer_implementation_report_paths
scripts/implementation_authorization.py:1651 in peer_report_dirty_path_collision_reason
scripts/implementation_authorization.py:1977 in create_authorization_packet
```

The stack directly connects the no-output start-gate wait to repeated access of
the append-only bridge SoT.

### E6 - Safety disposition

- Both probes used `--no-write`.
- The exact hung/diagnostic processes were identified by PID and command line
  before termination.
- No implementation authorization packet was created.
- No declared WI-5761 target changed.
- The work-intent claim was released.
- TAFE and dispatcher state were not activated or mutated.

## Risk And Impact

1. Governed implementation can be denied in practice without an explicit
   authorization verdict because the start transaction does not return.
2. The latency grows as either append-only SoT population grows, so historical
   success is not evidence of future liveness.
3. A claim must remain held during evaluation. Long evaluations increase claim
   expiry, retry, and cross-session contention windows.
4. Operators are encouraged to terminate apparently hung processes. Without a
   bounded diagnostic contract this can make the difference between a slow read
   and a deadlock unclear.
5. Repeated retries multiply filesystem pressure and can amplify concurrency
   interference even when the root cause is algorithmic rather than a lock.
6. Because this is an authorization hot path, bypassing the guard is not an
   acceptable workaround. Corrective work must retain fail-closed collision
   semantics and authoritative lifecycle resolution.

## Related Work And Non-Duplication

- `WI-5658` / `gtkb-wi5658-protected-commit-checker-performance` addresses an
  analogous `O(packets x committed-bridge-files)` defect in the protected-commit
  checker. It demonstrates the same useful correction pattern - enumerate and
  index once - but targets a different operation and code path.
- `WI-5521` / `gtkb-wi5521-dirty-peer-collision` governs semantic completeness
  of dirty-peer attribution. A liveness correction must preserve those intended
  semantics; this advisory does not replace that work.
- `WI-5178` / `gtkb-wi5178-operation-time-authority-enforcement` previously
  observed silent implementation-start behavior and recommended instrumentation.
  Its version-010 review identified full dirty-tree scanning and database-lock
  contention as hypotheses. The present stack and cardinality isolate a third,
  concrete cause: repeated exact bridge-lifecycle discovery inside the packet
  loop.

The corrective intake should reconcile these related threads before creating a
new work item. If an existing active WI already owns this exact start-gate
repeated-scan defect, route this evidence into that WI instead of duplicating it.

## Recommended Corrective Direction

1. Build one authoritative bridge-history inventory/index per start-gate
   evaluation, then resolve all peer lifecycles from that stable snapshot.
2. Preserve exact-version, duplicate-version, unreadable-chain, and lifecycle
   validation semantics. An optimization must not turn fail-closed reads into
   fail-soft authorization.
3. Bound the operation with explicit phase timing and a diagnostic timeout or
   progress contract. Timeout behavior must fail closed and identify the phase
   and observed cardinality.
4. Avoid introducing a new mutable cache as competing authority. An ephemeral
   per-evaluation index derived from the authoritative bridge tree is the
   lowest-risk starting point; any durable index needs its own consistency and
   rebuild contract.
5. Add scale regression tests using representative packet and bridge counts,
   plus output-equivalence tests against the pre-change resolver semantics.
6. Measure separately: directory enumeration, lifecycle materialization,
   implementation-report reads, dirty-tree discovery, and database access.
   This will prevent one hot-path fix from hiding the next dominant cost.
7. Treat append-only retention policy or archival redesign as separate
   architecture work. This local advisory establishes an inefficient access
   pattern; it does not conclude that authoritative history should be deleted.

## Acceptance Evidence For A Future Correction

- Start-gate work scales approximately with `packets + bridge_files`, not their
  product, on a representative repository fixture.
- The WI-5761 no-write start probe returns a deterministic authorization result
  within a declared budget.
- Collision outcomes are byte-for-byte or structurally equivalent across
  clean, dirty-overlap, non-overlap, terminal, malformed, duplicate-version,
  and unreadable-chain fixtures.
- A timeout or phase-budget breach fails closed with actionable diagnostics and
  leaves no packet or partial authority state.
- Concurrent claim acquisition/release tests show no stale claim or partial
  packet after timeout/failure.
- Existing focused implementation-authorization, lifecycle-resolver, and
  protected-commit performance suites remain green.

## Requirement Sufficiency

Existing governance is sufficient to review and route this advisory. It is not
sufficient authority to implement a correction. A later implementation must be
part of an active project, inherit that project's active bounded PAUTH, receive
an independent bridge GO, acquire a matching claim, and pass the
implementation-start gate.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` - preserves role-correct append-only bridge filing.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` - requires the discovered defect to become durable governed input.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` - routes the finding through an artifact rather than chat-only memory.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - requires later work to enter the governed lifecycle.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - applies to any later correction proposal.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - requires scale, semantic-equivalence, and concurrency-derived verification.
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` - later source/test work must inherit active project authorization.
- `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001` - performance pressure cannot bypass review or start gates.
- `DCL-PROJECT-AUTHORIZATION-OPERATION-TIME-ENFORCEMENT-001` - the corrected start path must still validate operation-time authority.
- `GOV-WORK-TREE-HYGIENE-001` - concurrent/foreign worktree changes remain unattributed and protected.
- `GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001` - correction must improve liveness without weakening intuitive fail-closed behavior.

## Specification-Derived Verification Plan

| Requirement | Future verification | Expected result |
| --- | --- | --- |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | Review this `NEW` advisory in an independent Loyal Opposition session | Role-correct verdict; no self-review. |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | Preserve this evidence in the selected existing or new work item | Finding remains discoverable and linked. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | Run scale, equivalence, malformed-chain, timeout, and concurrent-claim tests | Liveness improves without semantic weakening. |
| `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` | Validate project membership and active project PAUTH before later mutation | No WI-only or orphan implementation authority. |
| `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001` | Exercise the corrected ordinary `begin --no-write` path | No bypass; deterministic bounded result. |
| `GOV-WORK-TREE-HYGIENE-001` | Re-run with unrelated dirty and concurrently claimed paths | Foreign work is preserved and collisions remain fail closed. |
| `GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001` | Compare before/after decisions over the same fixture corpus | Authorization decisions remain equivalent. |

## Decision Needed

No immediate owner decision is required. Loyal Opposition should review the
diagnosis and route it to an existing exact-scope work item or recommend a new
project-linked corrective item. Any future implementation approval remains a
separate owner/governance action at project level.

## Explicit Non-Approval And TAFE Exclusion

This Advisory Report is not a GO, project authorization, implementation-start
packet, or authorization to modify source, tests, configuration, metadata,
dispatcher/TAFE state, Git history, deployment, credentials, or external
systems. The TAFE dispatcher is deliberately disabled and was not activated or
mutated while producing this report.

---

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
