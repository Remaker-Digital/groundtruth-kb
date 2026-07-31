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
Document: gtkb-advisory-router-candidate-store-concurrency
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

# Advisory Report — Advisory Router Candidate-Store Concurrent-Writer Safety

## Summary

WI-5757 readiness and code review identified a concurrent-writer race in the append-only advisory candidate store. `run()` loads and folds `.gtkb-state/advisory-candidates/candidates.jsonl`, checks candidate and work-item state, and later appends without an interprocess lock, compare-and-swap token, unique constraint, or under-lock reload. Two hook or manual router processes can therefore both observe the same versioned `source_key` as absent and both append a staged event.

The finding did not block WI-5757. Promotion remains owner-gated, and the live backfill was executed only after verifying there was no other router process. That serialized pass staged seven candidates and the immediate repeat staged zero. No simultaneous duplicate-write reproduction was attempted, so this report distinguishes the deterministic source-level race from an observed production duplication incident.

## Authority And Scope Boundary

This Prime Builder `NEW` governance-review Advisory is filed under the GT-KB project root. All generated artifacts remain in-root under E:\GT-KB\bridge\. It grants no implementation authority, project authorization, work-item approval, backlog promotion, candidate mutation, MemBase mutation, dispatcher activation, or TAFE mutation. `target_paths` is empty.

If review derives corrective work, it must become a project member and proceed through the parent project's active whole-project PAUTH, a separate implementation proposal, independent `GO`, claim, schema-v3 packet, implementation report, and verification.

## Evidence

### Pre-append state is reconstructed outside writer exclusion

In `scripts/advisory_backlog_router.py`, `run()` loads the JSONL events and folds `status_map` before entering its advisory loop. It then uses that process-local snapshot for the candidate-store and existing-work-item decisions.

No project-rooted writer lock, database transaction, filesystem compare-and-swap, or other cross-process exclusion surrounds the load, fold, checks, and append.

### Append occurs later without an authoritative reload

`stage_advisory_candidate()` creates the event, opens the JSONL store in append mode, and writes one line. It does not reload and fold the store after acquiring a writer boundary because no such boundary exists. The later `status_map` update protects only the current process.

An interleaving is therefore possible:

1. process A loads state with key K absent;
2. process B loads the same state with K absent;
3. A passes both dedup checks;
4. B passes both dedup checks;
5. A appends staged event K;
6. B appends a second staged event K.

### Last-scan publication is also last-writer-wins

`.gtkb-state/advisory-router/last-scan.json` is written directly with `write_text()`. Concurrent completions can overwrite one another, and a crash during publication can leave an incomplete observation surface.

### Current measured store context

After the WI-5757 single-writer backfill, the candidate store contained 285 lines and 286,104 bytes. Live scans over 95 advisory heads took approximately 5–11 seconds. This is useful baseline context, not an independently extreme-latency finding. Candidate-store growth and fold cost should be benchmarked before selecting a scaling remedy.

## Risk And Impact

- duplicate staged events for one logical versioned advisory;
- avoidable append-only SoT growth and parse/fold cost;
- ambiguous provenance when duplicate events fold to one visible current state;
- retries that cannot distinguish a recovered prior append from a new append;
- malformed or incomplete trailing records if a writer terminates mid-append;
- misleading last-scan state under concurrent completion; and
- increased likelihood of duplicate owner-review noise even though promotion remains gated.

Owner-gated promotion contains the immediate blast radius: duplicate staging does not itself create or approve duplicate implementation work. It does not make the candidate store concurrency-safe.

## Recommended Corrective Design

1. Add a project-rooted advisory-router interprocess writer lock.
2. Hold the lock across authoritative reload, current-state fold, duplicate decision, append, durability, and receipt publication.
3. After lock acquisition, discard any pre-lock snapshot and recompute from canonical bytes.
4. Define a stable logical idempotency identity from source kind, governed slug, numbered version, and content/path binding.
5. Return a durable receipt for the committed event so retries recover `already_staged` instead of appending again.
6. Serialize exactly one UTF-8 LF-terminated record, flush/synchronize to the supported durability contract, and detect/quarantine an incomplete trailing record without rewriting valid history.
7. Publish last-scan evidence with an atomic temporary-file replacement and a stable run ID linked to event receipts.
8. Use bounded lock wait and typed contention results; timeout must fail closed rather than proceed unlocked.
9. Preserve stage-only and TAFE boundaries. The correction must not autonomously create work items, activate dispatcher topology, or mutate TAFE.
10. Add an evidence-producing benchmark for store bytes/events, load, parse, fold, append, memory, and duplicate/superseded-event behavior before choosing snapshots, checkpoints, indexes, or partitions.

## Append-Only SoT Considerations

Append-only history provides provenance, but the router currently rereads and folds the full candidate log. Its cost will grow with event count. Corrective design should consider generation-bound current-state indexes or checkpoints while preserving the canonical event history and proving invalidation on every append.

Do not default to deleting valid history. Storage retention, partitioning, snapshotting, or compaction requires explicit authority and evidence that audit and recovery invariants remain intact.

## Specification-Derived Verification Outline

A future `python -m pytest` multi-process suite should use deterministic barriers and prove:

1. two processes staging the same absent key commit exactly one event;
2. the loser returns an idempotent existing-result or typed contention outcome;
3. concurrent distinct keys both survive without interleaving or loss;
4. lock timeout fails closed and names the contested state;
5. termination at each write boundary does not cause a retry to duplicate the logical event;
6. an incomplete trailing record is detected without rewriting prior valid history;
7. last-scan publication is atomic and linked to a stable run ID;
8. sequential reruns remain idempotent;
9. load/parse/fold/append benchmarks are captured across growing event counts; and
10. no MemBase, bridge-status, dispatcher, or TAFE mutation occurs outside approved scope.

## Requirement Sufficiency

Existing requirements are sufficient to preserve the concurrency finding. A later implementation proposal must select the cross-platform lock, durability contract, idempotency receipt schema, incomplete-record recovery policy, timeout behavior, and exact source/test targets before implementation.

## Specification Links

- `GOV-STANDING-BACKLOG-001`
- `DCL-STANDING-BACKLOG-SCHEMA-001`
- `GOV-FILE-BRIDGE-AUTHORITY-001`
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`
- `GOV-DETERMINISTIC-SERVICES-PRINCIPLE-001`
- `GOV-SOURCE-OF-TRUTH-FRESHNESS-001`
- `GOV-WORK-TREE-HYGIENE-001`
- `GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001`
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001`
- `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001`
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`
- `SPEC-1662`
- `SPEC-1830`
- `GOV-10`

## Related Work And Non-Duplication

- WI-5757 repairs advisory version identity and starvation under single-writer execution; it does not claim this race fixed.
- `bridge/gtkb-advisory-wi5757-implementation-start-orchestration-concurrency-001.md` covers lost execution handles and duplicate implementation-start scans, not this JSONL writer boundary.
- `bridge/gtkb-advisory-implementation-start-peer-scan-liveness-001.md` covers another append-only scan surface; its latency evidence is not generalized to this store.
- `bridge/gtkb-advisory-work-intent-release-db-lock-concurrency-001.md` concerns SQLite work-intent locking, not JSONL append atomicity.

## Owner Decision

No immediate owner decision is needed to preserve and review this report. If review derives an unapproved backlog item, Prime Builder must later present one AUQ before implementation. This report neither creates nor approves that item.

## Pre-Filing Requirements

Before filing, acquire the exact draft claim; confirm Prime Builder `NEW` authority; run credential, compliance audit-only, applicability, and mandatory clause preflights; and file append-only without activating or mutating TAFE/dispatcher.

---

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
