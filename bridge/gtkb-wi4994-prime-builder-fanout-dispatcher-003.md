REVISED

# WI-4994 Prime Builder Fan-Out Dispatcher Proposal

bridge_kind: prime_proposal
Document: gtkb-wi4994-prime-builder-fanout-dispatcher
Version: 003
Author: Prime Builder (Codex, harness A)
Date: 2026-07-03 UTC
Responds to: bridge/gtkb-wi4994-prime-builder-fanout-dispatcher-002.md
Verdict Response: Revised after NO-GO

author_identity: prime-builder/codex
author_harness_id: A
author_session_context_id: 019f247b-4dc8-7b32-a2ab-25839614d33f
author_model: gpt-5.5
author_model_version: 5.5
author_model_configuration: Extra High reasoning; Codex Desktop interactive Prime Builder

Project Authorization: PAUTH-PROJECT-GTKB-OPS-DISPATCHER-MODERNIZATION-WI-4994-PB-FANOUT
Project: PROJECT-GTKB-OPS-DISPATCHER-MODERNIZATION
Work Item: WI-4994

target_paths: ["scripts/gtkb_dispatcher_daemon.py", "scripts/dispatcher_runtime.py", "scripts/bridge_dispatch_concurrency.py", "platform_tests/scripts/test_gtkb_dispatcher_daemon.py", "platform_tests/scripts/test_dispatcher_runtime_work_intent.py", "platform_tests/scripts/test_perrole_concurrency_cap_dispatch.py"]

---

## Revision Claim

The WI-4994 defect remains valid: the dispatcher can run Codex headless Prime Builder workers, but the live daemon only admits one Prime Builder batch per recipient lane and then suppresses additional independent PB work behind recipient-level work-intent and signature state. This revision narrows the implementation design to a concrete dispatcher-owned fan-out algorithm:

- Partition eligible Prime Builder work into one bridge document per worker.
- Acquire a distinct work-intent session for each single-document sub-batch.
- Compute and persist signatures at the sub-batch/document level, not only the recipient level.
- Attempt multiple PB spawns in one dispatcher tick, bounded by existing role-aware live-worker caps and global runaway guards.
- Preserve direct harness launch prohibition by routing every worker through the existing dispatcher `_spawn_harness` envelope.

This revision does not ask this interactive Codex session to directly launch other harnesses. It asks to make the dispatcher perform bounded PB fan-out mechanically.

## NO-GO Findings Addressed

### Gap 1: Batch-Splitting Algorithm

Response: use deterministic one-document-per-worker partitioning for Prime Builder fan-out.

Algorithm:

1. Start with the daemon's current PB-selected actionable items after normal bridge scanning and role filtering.
2. Exclude items already held by another live work-intent holder.
3. Sort the remaining candidate items in the same deterministic order already used by dispatcher selection.
4. Build sub-batches as `[[item_1], [item_2], ...]`.
5. Stop building sub-batches when either remaining Prime Builder capacity is exhausted or no unheld candidate remains.
6. Render the normal dispatch prompt separately for each one-item sub-batch.

One-document sub-batches are intentionally conservative. They maximize claim clarity, make signature dedupe unambiguous, and keep rollback simple. A later capacity-weighted batching strategy can be proposed after timing data shows it is needed.

### Gap 2: Work-Intent Claim Partitioning

Response: call the existing PB work-intent acquisition path independently for each one-document sub-batch with a distinct dispatcher session ID.

Implementation direction:

- For each sub-batch, generate the dispatch ID before claim acquisition.
- Use that dispatch ID as the work-intent session ID for only that document.
- Call `_acquire_prime_work_intent_batch` with the one-item sub-batch, not the whole recipient selection.
- If claim acquisition returns `work_intent_already_held`, skip only that sub-batch and continue evaluating later candidates until capacity is exhausted.
- If a spawn attempt fails before the worker is launched, release the sub-batch claim where the current implementation already releases failed claims or add an explicit release path for that pre-launch failure.
- If launch succeeds, leave the claim under the spawned worker's session ID so the existing implementation-start and completion path can own release/expiry behavior.

The work-intent registry remains the per-document mutual exclusion mechanism. This proposal does not permit concurrent PB workers to claim the same bridge document.

### Gap 3: Multi-Worker Signature Dedup Model

Response: add sub-batch signature accounting while preserving the existing recipient aggregate signature as an operator diagnostic.

Implementation direction:

- Compute `sub_batch_signature = _signature([item])` for each one-document worker candidate.
- Track active or recently dispatched PB sub-batch signatures keyed by recipient plus document name or dispatch ID.
- Suppress a spawn only when the same recipient has an active or non-expired sub-batch signature for the same document.
- Do not suppress a different unheld document merely because the recipient-level aggregate signature matches a prior cycle.
- Keep `last_dispatched_signature` as a backward-compatible aggregate field for reports, but add or derive a multi-worker field such as `last_dispatched_sub_signatures`, `active_sub_signatures`, or equivalent report-facing metadata so operator output can distinguish parallel PB workers.

Loop prevention therefore moves from "one recipient signature blocks the lane" to "the same document/signature is not dispatched twice while it is already active or recently dispatched."

### Gap 4: Existing `bridge_dispatch_concurrency.py` And Slot Accounting

Response: do not create a second live-cap authority. Use the verified CA9165 live-worker cap already enforced at `_spawn_harness` as the hard gate, and treat `scripts/bridge_dispatch_concurrency.py` as optional helper code only if the implementation can reuse it without introducing dual accounting.

Rationale:

- `bridge/gtkb-perrole-concurrency-cap-dispatch-022.md` verified that `_spawn_harness` already gates live spawned workers by role through the current per-role cap.
- `scripts/bridge_dispatch_concurrency.py` is a verified Slice 4 module, but its own header says live wiring was deferred. Wiring it as an additional authoritative slot ledger during WI-4994 would risk two competing cap sources.
- The concrete implementation should calculate available PB attempts from the same live-worker view used by `_spawn_harness`, then still let `_spawn_harness` enforce the final cap for each attempted worker.
- If `bridge_dispatch_concurrency.py` exposes reusable pure helpers for capacity math, they may be used with tests. If not, the implementation may leave the module unchanged and cite the existing `_spawn_harness` cap as the authoritative gate.

This directly addresses the NO-GO distinction: the missing feature is batch architecture and per-sub-batch dedupe, not a new cap.

### Gap 5: Daemon Tick Behavior

Response: spawn multiple PB workers in the same daemon tick, bounded by remaining PB capacity.

Tick behavior:

1. Select the current PB candidate list.
2. Determine remaining Prime Builder launch capacity from live worker count and configured role cap.
3. Build one-document sub-batches up to that capacity.
4. For each sub-batch, acquire a distinct work-intent claim and check sub-batch signature dedupe.
5. Call `_spawn_harness` once per admitted sub-batch.
6. Record partial outcomes: launched count, skipped-held count, skipped-duplicate-signature count, and at-cap count.

Success is not all-or-nothing. If item 1 is held but item 2 is unheld, the daemon may launch item 2. If the first spawn reaches the role cap because another worker appears concurrently, later sub-batches stop cleanly and report at-cap suppression.

## Scope Changes From Version 001

- The design now explicitly uses one-document-per-worker partitioning.
- The design now requires distinct per-sub-batch work-intent session IDs.
- The design now requires per-document or per-sub-batch signature dedupe.
- The design now specifies same-tick multi-spawn behavior.
- The design now references the verified Slice 4 concurrency module and explains that `_spawn_harness` remains the hard cap authority unless a pure helper can be reused without dual accounting.

## In-Root Placement Evidence

All target paths are inside `E:\GT-KB`: `scripts/gtkb_dispatcher_daemon.py`, `scripts/dispatcher_runtime.py`, `scripts/bridge_dispatch_concurrency.py`, `platform_tests/scripts/test_gtkb_dispatcher_daemon.py`, `platform_tests/scripts/test_dispatcher_runtime_work_intent.py`, and `platform_tests/scripts/test_perrole_concurrency_cap_dispatch.py`.

## Specification Links

- `SPEC-CENTRALIZED-DISPATCH-SERVICE-001` - requires stable unattended dispatcher processing; PB fan-out is part of stable headless processing when multiple independent PB items are available.
- `ADR-DISPATCHER-ARCHITECTURE-001` - governs the dispatcher as the control-plane path for cross-harness work and excludes ad hoc direct harness launch.
- `GOV-FILE-BRIDGE-AUTHORITY-001` - requires role-correct append-only bridge state and work-intent discipline for implementation/report transitions.
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` - requires bounded project implementation authorization before protected dispatcher source/test mutation.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - requires PAUTH/project/WI metadata and target paths in this proposal.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - requires concrete links to all relevant governing specifications.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - requires implementation verification to map each linked requirement to executed evidence.
- `DCL-DISPATCH-ENVELOPE-RULES-001` - dispatcher prompts and spawned workers must retain the approved dispatch envelope and role boundaries.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` - this revised proposal preserves the owner request and NO-GO findings as durable bridge artifacts before implementation.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - the owner request and live stability defect crossed the threshold for a work item and proposal revision.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` - this revision keeps the proposed implementation within governed work item, PAUTH, and bridge lifecycle records.

## Prior Deliberations

- `DELIB-20260703-HEADLESS-DISPATCH-STABILITY-GOAL` - owner directed stable unattended headless bridge processing with Codex A as PB and Claude/Ollama as LO, and authorized governed stability WIs under the dispatcher-modernization project.
- `DELIB-20260703-DIRECT-HARNESS-INVOKE-BAN` - owner prohibited direct harness-to-harness standby/fallback. This proposal keeps all spawning inside the dispatcher.
- `DELIB-202665265` - earlier bridge-stability authorization evidence for creating necessary WIs and fixing stability defects discovered during the live soak.
- `bridge/gtkb-wi4988-direct-harness-launch-guard-006.md` - verified direct harness launch guard, which this proposal preserves.
- `bridge/gtkb-perrole-concurrency-cap-dispatch-022.md` - verified per-role concurrency cap in the dispatcher spawn path.
- `bridge/gtkb-bridge-scheduler-lanes-leases-slice-4-004.md` - verified standalone concurrency helper module whose live wiring was deferred.
- `bridge/gtkb-bounded-parallel-cross-harness-dispatch-003.md` - withdrawn prior bounded-parallel proposal; WI-4994 is narrower and limited to dispatcher-owned PB fan-out over independent documents.
- `bridge/gtkb-wi4993-codex-hook-batch-output-normalization-004.md` - verified Codex hook output fix; separate from PB fan-out but part of the same stability goal.

## Owner Decisions / Input

- Owner directive, 2026-07-03: "Can you spawn headless workers and parallelize the PB work?"
- Owner directive, 2026-07-03: direct harness-to-harness interaction is prohibited and must be mechanically enforced.
- Owner directive, 2026-07-03: model and harness timings vary widely; timer policy should start generously and collect data before declaring work hung.
- `DELIB-20260703-HEADLESS-DISPATCH-STABILITY-GOAL` records owner authority to create governed WIs and bounded authorizations needed to stabilize unattended headless dispatch.
- `PAUTH-PROJECT-GTKB-OPS-DISPATCHER-MODERNIZATION-WI-4994-PB-FANOUT` authorizes only bridge, dispatcher runtime/source, and focused tests for WI-4994. It forbids direct harness-to-harness launch, credential changes, production deployment, durable role reassignment beyond A/B/D, and retired poller restoration.

## Requirement Sufficiency

Existing requirements are sufficient. `SPEC-CENTRALIZED-DISPATCH-SERVICE-001` and `ADR-DISPATCHER-ARCHITECTURE-001` already require dispatcher-governed stable headless processing; verified prior work already created role caps and a standalone concurrency helper. This proposal wires a narrowly specified batch architecture into the live daemon path with tests. It does not create a new product requirement or change the direct-launch ban.

## Proposed Implementation Scope

- Add dispatcher PB fan-out logic that splits Prime Builder selections into one-document sub-batches.
- Add per-sub-batch work-intent acquisition with unique dispatch IDs and session IDs.
- Add per-document or per-sub-batch signature dedupe so different unheld documents are not blocked by one recipient-level signature.
- Attempt multiple `_spawn_harness` calls in a single daemon tick until PB capacity is exhausted.
- Preserve `_spawn_harness` as the final role-cap and global-guard enforcement point.
- Preserve the current Codex headless invocation envelope and model pin: `gpt-5.5` with `model_reasoning_effort="xhigh"`.
- Preserve active topology: Codex A as PB, Claude B and Ollama D as LO.
- Add report fields or state metadata sufficient to explain launched, skipped-held, skipped-duplicate, and at-cap PB sub-batches.

## Out Of Scope

- Directly launching Claude, Codex, Ollama, Cursor, Antigravity, OpenRouter, or any other harness from this interactive session.
- Adding a standby or backup path where one harness directly invokes another harness.
- Re-enabling disabled harnesses or changing dispatcher eligibility.
- Changing Claude, Codex, Ollama, or OpenRouter model pins.
- Changing model-specific timeout policy beyond preserving generous allowances already tracked by related timer work.
- Restoring the retired OS poller or retired smart poller.
- Broad scheduler refactors unrelated to bounded PB fan-out.

## Specification-Derived Verification Plan

| Specification / Requirement | Planned Verification |
| --- | --- |
| `SPEC-CENTRALIZED-DISPATCH-SERVICE-001` | Add or extend daemon regression tests showing two independent unheld PB-actionable bridge documents produce two dispatcher-owned Codex PB spawn attempts in one tick when PB capacity is at least two. |
| `ADR-DISPATCHER-ARCHITECTURE-001` | Assert all PB fan-out workers are launched through `_spawn_harness`; no direct harness launcher or harness-to-harness fallback is introduced. |
| `DCL-DISPATCH-ENVELOPE-RULES-001` | Assert each spawned PB worker receives the existing dispatch prompt/envelope and current Codex headless argv/model configuration. |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | Verify each sub-batch acquires a distinct work-intent claim, held documents remain excluded, and same-document duplicate dispatch is suppressed. |
| `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` | Run implementation-start authorization for WI-4994 before protected mutation and keep changes inside authorized target paths. |
| `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` / `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | Proposal/report carry PAUTH/project/WI metadata, target paths, and complete spec links. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | Post-implementation report must include exact command evidence and this mapping before VERIFIED. |
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` / `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` / `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | Bridge revision preserves the live defect, owner direction, and implementation plan as governed artifacts before implementation. |

Expected commands:

```text
python -m pytest platform_tests/scripts/test_gtkb_dispatcher_daemon.py platform_tests/scripts/test_dispatcher_runtime_work_intent.py platform_tests/scripts/test_perrole_concurrency_cap_dispatch.py -q --tb=short
python -m ruff check scripts/gtkb_dispatcher_daemon.py scripts/dispatcher_runtime.py scripts/bridge_dispatch_concurrency.py platform_tests/scripts/test_gtkb_dispatcher_daemon.py platform_tests/scripts/test_dispatcher_runtime_work_intent.py platform_tests/scripts/test_perrole_concurrency_cap_dispatch.py
python -m ruff format --check scripts/gtkb_dispatcher_daemon.py scripts/dispatcher_runtime.py scripts/bridge_dispatch_concurrency.py platform_tests/scripts/test_gtkb_dispatcher_daemon.py platform_tests/scripts/test_dispatcher_runtime_work_intent.py platform_tests/scripts/test_perrole_concurrency_cap_dispatch.py
```

## Acceptance Criteria

- With two independent unheld PB-actionable bridge documents and Prime Builder capacity greater than one, one dispatcher tick attempts independent Codex PB workers through `_spawn_harness`.
- Each worker sub-batch contains one bridge document and has a distinct work-intent session ID.
- Held PB work-intent items remain excluded and do not block later independent unheld candidates.
- Same document/signature dedupe still suppresses duplicate dispatch for an already active or recently dispatched item.
- Multiple PB workers are bounded by the existing role-aware cap and global runaway guards.
- Dispatcher state/reporting can distinguish PB fan-out outcomes well enough to explain launched, held, duplicate, and at-cap items.
- No direct harness-to-harness launch path is added.
- Focused pytest, ruff check, and ruff format-check commands pass.

## Risks / Rollback

Risk: PB fan-out could revive dispatch storms if admission control is too broad. Mitigation: one-document sub-batches, existing `_spawn_harness` role cap, global guard preservation, and explicit at-cap tests.

Risk: fan-out could duplicate implementation of the same document. Mitigation: per-document work-intent claims and same-document signature suppression.

Risk: adding a second concurrency module as a hard authority could create cap drift. Mitigation: preserve `_spawn_harness` as the final cap authority and use `bridge_dispatch_concurrency.py` only if it can be reused without dual accounting.

Rollback: revert the WI-4994 changes to dispatcher runtime/daemon/concurrency wiring and tests. Bridge files, PAUTH, and MemBase records remain append-only audit records.

## Files Expected To Change

- `scripts/gtkb_dispatcher_daemon.py`
- `scripts/dispatcher_runtime.py`
- `scripts/bridge_dispatch_concurrency.py`
- `platform_tests/scripts/test_gtkb_dispatcher_daemon.py`
- `platform_tests/scripts/test_dispatcher_runtime_work_intent.py`
- `platform_tests/scripts/test_perrole_concurrency_cap_dispatch.py`

## Recommended Commit Type

`fix`
