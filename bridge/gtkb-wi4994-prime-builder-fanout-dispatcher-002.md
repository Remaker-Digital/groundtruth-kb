NO-GO

# Loyal Opposition Review — WI-4994 Prime Builder Fan-Out Dispatcher

bridge_kind: lo_verdict
Document: gtkb-wi4994-prime-builder-fanout-dispatcher
Version: 002
Author: Loyal Opposition (Ollama, harness D)
Date: 2026-07-03 UTC
Responds to: bridge/gtkb-wi4994-prime-builder-fanout-dispatcher-001.md
Verdict: NO-GO

author_identity: Ollama Loyal Opposition
author_harness_id: D
author_session_context_id: 2026-07-03T11-36-22Z-loyal-opposition-D-b8a179
author_model: deepseek-v4-pro:cloud
author_model_version: cloud
author_model_configuration: Ollama harness shim; route deepseek-v4-pro-cloud; skill bridge-review; guarded tools Read, Write, Edit, Grep, Glob, Bash

Project Authorization: PAUTH-PROJECT-GTKB-OPS-DISPATCHER-MODERNIZATION-WI-4994-PB-FANOUT
Project: PROJECT-GTKB-OPS-DISPATCHER-MODERNIZATION
Work Item: WI-4994

---

## Applicability Preflight

- packet_hash: `sha256:c18dd364dbe72da58b268e48e8779476b63e7f7c9e7c2c0d1c5cbf315476de36`
- bridge_document_name: `gtkb-wi4994-prime-builder-fanout-dispatcher`
- content_source: `bridge_file_operative`
- content_file: `bridge/gtkb-wi4994-prime-builder-fanout-dispatcher-001.md`
- operative_file: `bridge/gtkb-wi4994-prime-builder-fanout-dispatcher-001.md`
- preflight_passed: `true`
- warnings.missing_parent_dirs: []
- warnings.spec_links_section: {"status": "harvested", "candidate_heading": null}
- missing_required_specs: []
- missing_advisory_specs: ["ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001", "DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001", "GOV-ARTIFACT-ORIENTED-GOVERNANCE-001"]

| Spec | Severity | Cited | Matched By |
|------|----------|-------|------------|
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | `advisory` | `no` | content:deliberation, content:MemBase |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | `advisory` | `no` | content:candidate, content:deferred, content:verified, content:retired |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | `blocking` | `yes` | doc:*, content:Specification Links |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | `blocking` | `yes` | doc:*, content:VERIFIED, content:verification, content:Specification-Derived Verification |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | `advisory` | `no` | content:owner decision, content:requirement, content:specification, content:ADR, content:DCL, content:work item |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | `blocking` | `yes` | doc:*, path:bridge/** |

## Clause Applicability (Slice 2; mandatory gate)

- Bridge id: `gtkb-wi4994-prime-builder-fanout-dispatcher`
- Operative file: `bridge\gtkb-wi4994-prime-builder-fanout-dispatcher-001.md`
- Clauses evaluated: 5
- must_apply: 4, may_apply: 1, not_applicable: 0
- Evidence gaps in must_apply clauses: 0
- Blocking gaps (gate-failing): 0
- Mode: **mandatory** (default invocation). Exit 5 = blocking gap; exit 0 = pass.

| Clause | Spec | Applicability | Evidence found | Severity | Enforcement |
|---|---|---|---|---|---|
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001/CLAUSE-IN-ROOT` | `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | must_apply | yes | blocking | blocking |
| `GOV-FILE-BRIDGE-AUTHORITY-001/CLAUSE-NUMBERED-FILE-CHAIN-IS-CANONICAL` | `GOV-FILE-BRIDGE-AUTHORITY-001` | must_apply | yes | blocking | blocking |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001/CLAUSE-CONCRETE-LINKS` | `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | must_apply | yes | blocking | blocking |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001/CLAUSE-SPEC-TO-TEST-MAPPING` | `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | must_apply | yes | blocking | blocking |
| `GOV-STANDING-BACKLOG-001/CLAUSE-VISIBILITY-BULK-OPS` | `GOV-STANDING-BACKLOG-001` | may_apply | — | blocking | blocking |

## Prior Deliberations

- `DELIB-20260703-HEADLESS-DISPATCH-STABILITY-GOAL` — owner directed stable unattended headless bridge processing with Codex A as PB and Claude/Ollama as LO.
- `DELIB-20260703-DIRECT-HARNESS-INVOKE-BAN` — owner prohibited direct harness-to-harness standby/fallback.
- `bridge/gtkb-wi4988-direct-harness-launch-guard-006.md` — VERIFIED direct harness launch guard.
- `bridge/gtkb-bounded-parallel-cross-harness-dispatch-003.md` — WITHDRAWN CA9165 proposal; per-document leases already satisfy same-role parallel dispatch on different items.
- `bridge/gtkb-perrole-concurrency-cap-dispatch-022.md` — VERIFIED per-role concurrency cap (CA9165) in `_spawn_harness()`.
- `bridge/gtkb-bridge-scheduler-lanes-leases-slice-4-004.md` — VERIFIED Slice 4 `bridge_dispatch_concurrency.py` standalone module (unwired).
- `bridge/gtkb-wi4993-codex-hook-batch-output-normalization-003.md` — contemporaneous Codex hook fix; not directly relevant.

## Verdict Rationale

**NO-GO.** The proposal identifies a real throughput limitation — the dispatcher daemon spawns at most one Prime Builder worker per tick, and the single-recipient signature model prevents a second spawn on the next tick while the first worker is still running. However, the proposal does not provide a concrete, implementable design for the batch-splitting mechanism that would convert available PB role capacity into independent dispatcher-owned PB workers. Five specific gaps block a GO:

### Gap 1: No batch-splitting algorithm specified

The proposal states the goal — "separate unheld Prime Builder-actionable bridge threads can spawn independent Codex headless workers" — but does not specify *how* the selected batch is partitioned across workers. Options (one-item-per-worker, round-robin, capacity-weighted) have different implications for work-intent claim partitioning, signature dedup, and the dispatch prompt construction. The proposal is silent on all of these.

### Gap 2: No work-intent claim partitioning model

The current `_acquire_prime_work_intent_batch` in `dispatcher_runtime.py` (line ~5533) acquires work-intent claims for the entire selected batch under a single session ID. Splitting the batch across multiple concurrent PB workers requires per-item (or per-sub-batch) claim partitioning. The proposal does not address how claims would be partitioned, how claim-release-on-failure would work across multiple workers, or how the existing `bridge_work_intent_registry` would support concurrent claim holders for different items under the same role.

### Gap 3: No multi-worker signature dedup model

The current dispatch dedup model (`run_dispatch_cycle`, line ~5344) compares `prior_dispatched == dispatched_signature` and returns "unchanged" on match. With a single worker per tick, this correctly prevents re-dispatch. With multiple concurrent workers, the signature model must track per-worker (or per-item) signatures to allow a second worker to spawn for a different item while the first is still running. The proposal does not describe this signature model.

### Gap 4: No reference to existing `bridge_dispatch_concurrency.py`

The VERIFIED Slice 4 module (`scripts/bridge_dispatch_concurrency.py`) provides the slot-based worker tracking (`register_worker`, `worker_slot` context manager, `in_flight_count`) that the proposal's fan-out mechanism would need. The proposal does not reference this module, describe how it would be wired into the dispatch path, or explain why the existing per-role cap in `_spawn_harness()` (CA9165, VERIFIED at `gtkb-perrole-concurrency-cap-dispatch-022.md`) is insufficient.

### Gap 5: The per-role cap already gates spawns — the gap is batch architecture, not capping

The CA9165 per-role concurrency cap (`_max_live_dispatched_per_role()`, default 3) already exists in `_spawn_harness()` (line ~4104). The dispatcher *can* spawn up to 3 PB workers — the cap gates at the spawn site. The real limitation is that `run_dispatch_cycle` only attempts one spawn per target per cycle, and the signature dedup prevents a second spawn on the next tick. The proposal's framing that "the dispatcher does not yet convert available PB role capacity into independent dispatcher-owned PB workers" is partially correct, but the solution is a batch-splitting architecture change, not a cap change. The proposal conflates these two concerns.

## Remediation Guidance

A revised proposal should address:

1. **Batch-splitting algorithm**: Specify how the selected batch is partitioned across N workers (one-item-per-worker is the simplest and most collision-safe; round-robin or capacity-weighted are alternatives). Include how the dispatch prompt is constructed for each sub-batch.

2. **Work-intent claim partitioning**: Describe how `_acquire_prime_work_intent_batch` is modified to support per-sub-batch claim acquisition, or how the existing batch-acquire is called independently for each sub-batch with distinct session IDs.

3. **Multi-worker signature model**: Specify whether signatures are per-worker (each sub-batch has its own signature tracked independently) or whether the existing per-recipient signature is split into per-item signatures. The model must preserve the loop-prevention invariant.

4. **Integration with `bridge_dispatch_concurrency.py`**: Reference the VERIFIED Slice 4 module and describe how `register_worker`/`worker_slot` would be called from the dispatch cycle to track per-worker slots, or explain why the existing CA9165 per-role cap in `_spawn_harness()` is sufficient and the Slice 4 module is not needed.

5. **Daemon tick behavior**: Clarify whether multiple workers are spawned in a single tick (requiring multiple `_spawn_harness` calls in one `run_dispatch_cycle`) or across successive ticks (requiring the signature model to allow a second spawn while the first worker's signature is still "live").

## Preflight Advisory Notes

The three advisory-spec gaps (`ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`, `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`, `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`) are non-blocking for a proposal review but should be cited in a revised proposal for full artifact traceability. The blocking specs are all satisfied.

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
