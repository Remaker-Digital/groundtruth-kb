NEW
::init gtkb pb
::open build
author_identity: prime-builder/codex
author_harness_id: A
author_session_context_id: 019fb19b-7814-73c1-8707-204e432cbf00
author_model: GPT-5
author_model_version: GPT-5 Codex desktop runtime
author_model_configuration: Codex Desktop interactive Prime Builder; transcript-resolved role prime-builder; dispatcher deliberately disabled

bridge_kind: governance_review
Document: gtkb-advisory-wi5757-implementation-start-orchestration-concurrency
Version: 001
Date: 2026-07-30 UTC
Project: PROJECT-GTKB-ADVISORY-CORRECTIONS-20260729
Related Work Item: WI-5757
Work Item Candidate: not yet created
target_paths: []

implementation_scope: none
requires_review: true
requires_verification: false
kb_mutation_in_scope: false
dispatcher_or_tafe_mutation_in_scope: false

# Advisory Report — Implementation-Start Single-Flight And Handle-Propagation Failure

## Executive Finding

During WI-5757 implementation start, three duplicate `implementation_authorization.py begin` process trees were concurrently executing the same bridge/session operation. The duplicates were not three separately intended starts. A long-running command returned a nested execution-session handle that the orchestration wrapper did not surface to its caller. The caller therefore treated the absence of visible output as an incomplete or failed invocation and launched replacements while the prior processes continued.

The exact duplicate roots were process IDs `32252`, `22936`, and `77976`; their complete verified trees contained nine processes. All nine exact processes were stopped after command-line and parent/child verification. A single controlled replacement was then launched with a surfaced execution handle (`40911`) and completed successfully, producing one valid schema-v3 WI-5757 packet.

This is a concrete concurrency failure, not a theoretical concern. It can create competing named-packet and `current.json` writes, amplify claim/PAUTH freshness races, and multiply already-costly source-of-truth scans.

## Authority Boundary

This is a Prime Builder `NEW` governance-review Advisory Report filed under the in-root `E:/GT-KB/bridge/` surface. It is not an implementation proposal, work item, project authorization, owner approval, bridge `GO`, implementation-start packet, or authority to change source, tests, database, packets, processes, dispatcher, or TAFE.

If adopted, derived work should become an active member of `PROJECT-GTKB-ADVISORY-CORRECTIONS-20260729` and inherit only an active whole-project PAUTH. No per-WI PAUTH should be created or treated as implementation approval.

TAFE and the dispatcher remained deliberately disabled and were neither activated nor mutated.

## Incident Evidence

| Evidence | Observed result |
| --- | --- |
| Logical operation | `implementation_authorization.py begin --bridge-id gtkb-wi5757-advisory-router-dedup-starvation` |
| Claim/session | one GO-implementation claim for session `019fb19b-7814-73c1-8707-204e432cbf00` |
| Duplicate root processes | `32252`, `22936`, `77976` |
| Total verified processes | 9 |
| Duplicate cause | nested long-running execution handle not surfaced by the wrapper |
| Containment | exact trees stopped after read-only process forensics |
| Controlled replacement | handle `40911`; one process tree; completed successfully |
| Result | pre-start hash `sha256:7117a028c591441b49da7d33cacc48d82a99f96c1a35f4cda5482ca908db00f3`; finalized packet hash `sha256:1bace810670534db9f519d7ab097e95088139d23032a80710c7bc3343e2dc2d1` |
| Target mutation before containment | none |
| TAFE/dispatcher | untouched |

The uncontrolled invocations ran for several minutes without caller-visible output. The controlled replacement required approximately six minutes from launch to packet output. A prior WI-5758 implementation-start operation in the same program required roughly 527 seconds. These are material implementation-start latency cases because they make dropped handles and duplicate relaunches likely and because every duplicate repeats expensive fresh-state work.

## Root Cause And Amplifiers

### Lost execution handle

The nested execution result carried a session ID, but wrapper composition exposed only an empty output string when the command yielded. The caller lost the ability to poll, wait, cancel, or correlate the live operation.

### Missing per-bridge/session single-flight boundary

`implementation_authorization.py begin` did not return a typed `already_in_progress`/attach result for the same bridge/session fingerprint. Equivalent callers were allowed to enter the expensive scan concurrently.

### High-cost fresh source-of-truth reconstruction

Implementation start resolves bridge history, claim state, project/membership/PAUTH authority, target ownership, specifications, packets, and worker-role provenance. Freshness is load-bearing, but re-running the same scan three times adds no governance value. It multiplies filesystem enumeration, parsing, hashing, sorting, database reads, and lock pressure.

Append-only source-of-truth history remains valuable. The defect is repeated full reconstruction without single-flight reuse or phase visibility, not append-only storage by itself.

## Risk And Impact

- **P0 — competing publication:** duplicate workers can race named-packet writes and the shared `current.json` alias. Atomic per-file replacement does not serialize the semantic relation among claim state, PAUTH state, named packet, alias, and returned result.
- **P1 — freshness divergence:** workers can observe different claim expiry, project, PAUTH, bridge, or target state while the user perceives one operation.
- **P1 — latency feedback loop:** a slow scan loses visibility; the caller relaunches; duplicates increase resource/lock pressure; all scans become slower; more relaunch becomes likely.
- **P1 — false operator state:** a missing handle makes "running" indistinguishable from "not started," forcing manual process forensics.
- **P2 — non-portable containment:** identifying and terminating exact process trees is deterministic service work, not a safe normal session procedure.

## Recommended Corrective Design

1. Add a crash-recoverable single-flight mutex keyed by normalized project root, bridge slug, and implementation session.
2. Store command fingerprint, owner PID, execution handle, acquired time, heartbeat, phase, authority-generation digest, and completion result.
3. Make duplicate callers attach to the existing handle or return typed `already_completed`, `busy_other_session`, or `stale_lock_recovered` results; never launch a second scan silently.
4. Surface execution handles at the top level through direct, nested, delegated, and wrapper-of-wrapper calls, including poll and cancellation mechanics.
5. Emit structured phase telemetry and elapsed time for admission, bridge resolution, claim, project/membership/PAUTH, targets/specs, SoT scan/hash, packet build, named-packet write, `current.json` update, validation, and completion.
6. Under the mutex, build and validate the complete packet, atomically publish the named packet, then atomically update `current.json` with the exact named-packet identity and verify coherence before returning.
7. Use one shared fresh scan result for attached duplicate callers. Performance work may use authoritative generation digests and deterministic indexes, but must not substitute stale summaries for canonical reads.
8. Add deterministic multi-process, crash-boundary, stale-lock, input-drift, alias-coherence, and nested-handle tests.

## Append-Only SoT Performance Context

The incident demonstrates a concrete cost multiplier over growing authoritative histories. Future telemetry should record artifact count, bytes read, database rows visited, hashes computed, and elapsed time per phase. The remedy should target deterministic current-state indexes, generation-aware reuse, and single-flight execution while preserving required historical records.

Do not respond by weakening fresh authority checks or arbitrarily deleting history. Any checkpoint, snapshot, partition, or index design must prove how it remains bound to append-only canonical generations.

## Proposed Derived Work

If adopted, create one project-member work item covering:

- three-simultaneous-call reproduction with one writer;
- single-flight mutex and crash recovery;
- top-level handle propagation;
- phase telemetry and bounded warnings;
- named-packet/`current.json` semantic atomicity;
- generation-aware scan reuse without freshness loss; and
- measured latency acceptance thresholds.

Exact implementation targets should be selected only after the CLI and wrapper boundaries are traced in a fresh proposal.

## Specification-Derived Verification Outline

A later implementation proposal must map the cited concurrency and freshness requirements to deterministic multi-process tests. At minimum, a future `python -m pytest` suite must launch three synchronized identical start calls, observe one writer and two attached/typed duplicate results, verify identical packet identity, inject crashes at each publication phase, exercise stale-lock recovery, change a load-bearing claim/PAUTH input during execution, and prove `current.json` resolves to the exact named packet returned to all callers. Observed results and per-phase timing must be carried in the implementation report.

## Requirement Sufficiency

Existing requirements are sufficient to preserve the finding and derive a corrective work item. Implementation design still requires a separate reviewed proposal that selects the mutex/receipt mechanism and exact target paths.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001`
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001`
- `DCL-PROJECT-AUTHORIZATION-OPERATION-TIME-ENFORCEMENT-001`
- `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001`
- `GOV-SOURCE-OF-TRUTH-FRESHNESS-001`
- `GOV-DETERMINISTIC-SERVICES-PRINCIPLE-001`
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`
- `GOV-WORK-TREE-HYGIENE-001`
- `GOV-STANDING-BACKLOG-001`
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`

## Prior Decisions And Related Work

- `DELIB-20260730-PROJECT-AUTHORITY-INHERITANCE-PULL-FORWARD` — project-only implementation authorization model.
- `DELIB-20260730-DISPATCHER-NEXT-PARALLEL-SOT-CONCURRENCY-REQUIREMENT` — concurrent GT-KB work must avoid corrupt IDs, lost updates, stale reads, and unbounded database-lock failures.
- WI-5675 — broader MemBase concurrency and storage decision carrier; coordinate without losing this implementation-start-specific incident.
- WI-5714 — registry-control-plane generation/CAS precedent.
- WI-5757 — operation whose implementation-start exposed the failure.
- `bridge/gtkb-advisory-implementation-start-peer-scan-liveness-001.md` — related scan-cost evidence; this report adds the observed duplicate-process/handle-loss mechanism.

## Owner Decisions / Input

No immediate owner decision is needed to preserve and review this Advisory. If review derives a backlog work item not already covered by an approved project, Prime Builder must later present one AUQ before implementation. This report itself grants no implementation authority.

## Pre-Filing Requirements

Before filing, acquire the exact draft claim; confirm Prime Builder `NEW` authority; run credential, compliance audit-only, applicability, and mandatory clause preflights; and file append-only without activating or mutating TAFE/dispatcher.

---

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
