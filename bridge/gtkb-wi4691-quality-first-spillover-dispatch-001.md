NEW

# Quality-First Spillover Dispatch for WI-4691

bridge_kind: prime_proposal
Document: gtkb-wi4691-quality-first-spillover-dispatch
Version: 001
Author: Prime Builder (Codex, harness A via interactive session-role override)
Date: 2026-06-21 UTC

author_identity: prime-builder/codex
author_harness_id: A
author_session_context_id: 019eec0d-db60-7a02-b3bf-85d24df55e76
author_model: GPT-5 Codex
author_model_version: gpt-5
author_model_configuration: Codex desktop interactive Prime Builder override via ::init gtkb pb; approval_policy=never

Project Authorization: PAUTH-PROJECT-GTKB-ENVELOPE-DISPOSITION-AND-AUTONOMOUS-DISPATCH-ENVELOPE-DISPOSITION-AND-AUTONOMOUS-DISPATCH-BOUNDED-IMPLEMENTATION-AUTHORIZATION
Project: PROJECT-GTKB-ENVELOPE-DISPOSITION-AND-AUTONOMOUS-DISPATCH
Work Item: WI-4691

target_paths: ["config/dispatcher/rules.toml", "groundtruth-kb/src/groundtruth_kb/bridge_dispatch_config.py", "scripts/cross_harness_bridge_trigger.py", "platform_tests/scripts/test_bridge_dispatch_config.py", "platform_tests/scripts/test_cross_harness_bridge_trigger.py"]

implementation_scope: dispatcher policy source, config, and regression tests
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

---

## Summary

This proposal moves `WI-4691` from the earlier "default fan-out" wording to the owner's clarified policy: the dispatcher should perform cheap continuous evaluation, then fill available harness capacity by assigning work to eligible harnesses in quality-first tiers. This is spillover, not duplicate fan-out. A bridge work item should be assigned once, to the best available harness whose quality meets the work item's minimum requisite quality; only when that tier is saturated or unavailable should routing spill to the next sufficient tier, with cost used as the tie-breaker among equal-quality peers and availability used after quality and cost.

The current implementation has useful substrate pieces already verified: role/dispatchability orthogonality, ordered fallback, per-role concurrency caps, selected-batch `pending_count` and `selected_count`, and the WI-4698 governance-grade Loyal Opposition quality floor. The remaining gap is that live config and ranking semantics still encode availability/cost-first priority in places, and `WI-4691` still says "fan out" while leaving backpressure/breadth unresolved. This proposal resolves that gap by making quality-first spillover the dispatch policy for the WI-4691 implementation slice.

## First-Line Role Eligibility Check

- Owner session init: `::init gtkb pb`.
- Resolved interactive role for this session: Prime Builder.
- Durable registry note: harness `A` may remain durably assigned Loyal Opposition for headless routing; this filing uses the transcript-defined interactive Prime Builder override allowed by the session-role authority rules and does not change the durable registry.
- Existing bridge thread for `WI-4691`: none (`gt bridge threads --wi WI-4691` returned no thread).
- Status authored here: `NEW`.
- Eligibility result: Prime Builder is authorized to file a new implementation proposal.

## Existing Related Items

- `WI-4691` is open P1 in `PROJECT-GTKB-ENVELOPE-DISPOSITION-AND-AUTONOMOUS-DISPATCH`; it is covered by the active PAUTH listed above.
- The first Activity-Envelope Disposition & Autonomous Dispatch advisory created `WI-4691` as "Dispatcher default fan-out mode" but explicitly deferred fan-out backpressure and breadth.
- The second advisory file approved the advisory and confirmed that each downstream WI still needs its own bridge proposal, GO, implementation-start packet, and verification.
- The VERIFIED WI-4698 thread established the existing governance-grade Loyal Opposition quality floor and confirmed that low-quality LO candidates are excluded before cost-first ranking can choose them.
- `WI-4484` is resolved but its cost-optimized ordered fallback language is now partly superseded by the owner clarification: fallback mechanics remain useful, but cost-first policy does not.
- `WI-4661` remains related because it enabled headless Prime Builder dispatch to Claude Code; its premise that Codex should usually win on cost is now superseded by quality-first Prime Builder selection.

## Proposed Policy

1. **Minimum requisite quality is an eligibility filter.** A dispatchable work item may declare or derive a minimum required quality. Candidate harnesses below that threshold are excluded before ranking. When no candidate meets the threshold, the dispatcher fails closed and leaves the item pending rather than assigning it to an insufficient harness.
2. **Ranking is quality, then cost, then availability.** Among candidates at or above the work item's requisite quality, higher `dispatch_quality` wins. If quality is equal, lower `dispatch_cost` wins. If both are equal, higher `dispatch_availability` wins. Stable deterministic tie-breakers such as reviewer precedence and harness ID remain last.
3. **Spillover is capacity-fill, not broadcast.** The dispatcher should assign distinct pending items across all eligible, ready harnesses with available capacity. It must not send the same work item to multiple harnesses merely because multiple harnesses are active. Existing per-document leases and work-intent claims remain the duplicate-work guard.
4. **High-quality queues saturate first.** A lower-quality sufficient harness receives work only when higher-quality sufficient peers have no available dispatch capacity, are not ready, are in backoff, or have otherwise failed closed for that dispatch cycle.
5. **Quality floor remains conservative for governance-grade LO.** WI-4698's default `80.0` LO floor remains in effect. WI-4691 generalizes the policy surface so future work can derive per-item required quality rather than relying only on a role-wide constant.

## Proposed Implementation Scope

1. Update `config/dispatcher/rules.toml` so the global and role-specific default preference order is quality-first:
   - default: `["quality", "cost", "availability", "reviewer_precedence", "harness_id"]`
   - Prime Builder: `["quality", "cost", "availability", "reviewer_precedence", "harness_id"]`
   - Loyal Opposition: `["quality", "cost", "availability", "reviewer_precedence", "harness_id"]`
2. Update dispatcher status/ranking tests in `platform_tests/scripts/test_bridge_dispatch_config.py` to lock in the new ordering and prove equal-quality candidates use lower cost before availability.
3. Update `scripts/cross_harness_bridge_trigger.py` so a dispatch cycle can continue past the single top-ranked target when there are remaining pending items and additional ready targets with available capacity. The intended behavior is:
   - select oldest/highest-priority pending items for the first eligible target up to that target's effective `max_items`;
   - exclude items already selected or lease-held before considering the next target;
   - skip targets that fail readiness, launchability, backoff, or capacity checks and record skip evidence as today;
   - dispatch additional distinct batches to the next eligible targets until no pending item remains or no eligible capacity remains.
4. Preserve the existing fallback behavior when only one target is available or only one batch has work.
5. Preserve current `pending_count`, `selected_count`, `raw_pending_count`, and selected-batch signature semantics per recipient. If multiple harness-specific recipients are used, each recipient records the pending and selected counts for the candidate batch it evaluated.
6. Leave durable harness activation and benchmark-derived quality-score production out of scope for this implementation. Those remain separate related work items.

## Out Of Scope

- Creating or mutating MemBase work items or specifications.
- Changing the governance-grade LO quality floor value.
- Producing benchmark measurements or updating harness quality scores.
- Activating or suspending harnesses in the registry.
- Dispatching the same bridge item to multiple harnesses for redundant review.
- Production deployment or Agent Red application mutation.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` - all implementation work begins only after a latest `GO` bridge verdict and implementation-start packet.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - this proposal cites the dispatch, bridge, and backlog rules that govern the implementation.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - this proposal carries Project Authorization, Project, Work Item, and inline JSON `target_paths` metadata.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - the verification plan maps each governing specification to concrete tests.
- `GOV-STANDING-BACKLOG-001` - `WI-4691` is open standing-backlog work in the authorized envelope/autonomous-dispatch project.
- `ADR-DISPATCH-ENVELOPE-ARCHITECTURE-001` - dispatch is an envelope-level routing mechanism; this proposal changes routing policy without changing the bridge artifact authority model.
- `SPEC-DISPATCH-ENVELOPE-ELEMENT-001` - bridge items remain dispatch-envelope elements with role/status-derived actionability.
- `DCL-DISPATCH-ENVELOPE-RULES-001` - declarative dispatcher rules determine eligibility and ranking.
- `SPEC-CENTRALIZED-DISPATCH-SERVICE-001` - candidate eligibility and ranking are centralized dispatch-service responsibilities.
- `REQ-HARNESS-REGISTRY-001` - `dispatch_quality`, `dispatch_cost`, `dispatch_availability`, dispatchability, and harness status remain harness metadata inputs.
- `ADR-CODEX-HOOK-PARITY-FALLBACK-001` - cross-harness trigger behavior must remain safe under Codex/Claude hook parity boundaries.
- `ADR-ENVELOPE-META-MODEL-001` - dispatch/session/topic containment remains intact while the dispatch layer chooses recipients.
- `DCL-ENVELOPE-META-MODEL-001` - the implementation preserves the envelope anatomy and uses dispatch metadata as routing context.
- `SPEC-TOPIC-ENVELOPE-ROUTER-001` - topic/activity routing remains separate from harness-quality ranking.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - all target paths are in-root GT-KB platform paths, not Agent Red or an external repository.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` - the owner clarification is captured as bridge policy work before implementation.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` - durable artifacts, tests, and verification drive the change.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - superseded cost-first/fan-out wording is identified and constrained rather than silently carried forward.

## Prior Deliberations

- `DELIB-20265287` - owner decision set that created `WI-4691`, made dispatcher default operation release-gating, and explicitly deferred fan-out backpressure and breadth.
- The Activity-Envelope Disposition & Autonomous Dispatch advisory and GO verdict - the approved program advisory that requires downstream per-WI bridge threads.
- `DELIB-20260620-BRIDGE-DISPATCHER-FABRIC-DELIBERATION` - strategic owner framing for capability-aware, optimizing multi-harness dispatch with reliability and quality as hard eligibility gates.
- `DELIB-20265223` - owner directive enabling headless PB dispatch to both Codex and Claude Code; the cost-favored premise recorded there is superseded by this quality-first policy.
- `DELIB-20263438` - corrected bridge-dispatch architecture: role/dispatchability orthogonality and rule-based dispatch using availability/cost/quality selection.
- `DELIB-20261120` - dispatch deadlock and contention critique cited by the advisory as a substrate precondition.
- `bridge/gtkb-lo-reviewer-pool-governance-grade-routing-008.md` - VERIFIED WI-4698 quality-floor implementation; this proposal builds on it rather than reimplementing it.

## Owner Decisions / Input

- `DELIB-20265287` records the AUQ-backed owner decision that created the autonomous-dispatch project and `WI-4691`.
- The active PAUTH for `PROJECT-GTKB-ENVELOPE-DISPOSITION-AND-AUTONOMOUS-DISPATCH` authorizes WI-4682..WI-4694 through the bridge protocol and includes source, test, config, docs, governance-review, formal-artifact, narrative-edit, and file-deletion mutation classes, while forbidding Agent Red mutation, deployment, and out-of-root writes.
- Current owner directive in this session: "LO rule prefers cost, then availability, then quality" is wrong; priority should be "quality then cost then availability," with minimum requisite quality gating and spillover to lower tiers only after higher-quality queues are saturated.
- No additional owner decision is needed for this proposal because it implements that explicit clarification inside the already-authorized `WI-4691` scope.

## Requirement Sufficiency

Existing requirements sufficient. The owner's current clarification resolves the advisory's deferred backpressure/breadth ambiguity for this slice: dispatch is cheap continuous evaluation plus capacity-fill spillover, not duplicate fan-out. Existing dispatch architecture and harness-registry specs already define role/status eligibility, dispatchability, rule-based ranking, and harness quality/cost/availability metadata. This proposal does not need a new formal requirement before implementation; if Loyal Opposition finds that per-work-item quality classification requires a new spec before implementation, the correct verdict is `NO-GO` with the required spec gap named.

## Spec-Derived Verification Plan

| Specification | Derived test or command | Expected result |
|---|---|---|
| `DCL-DISPATCH-ENVELOPE-RULES-001`, `SPEC-CENTRALIZED-DISPATCH-SERVICE-001`, `REQ-HARNESS-REGISTRY-001` | Add/adjust `platform_tests/scripts/test_bridge_dispatch_config.py` tests for quality-first candidate ordering. | Higher quality wins over lower cost; equal quality uses lower cost; equal quality/cost uses higher availability; deterministic tie-breakers remain last. |
| `SPEC-DISPATCH-ENVELOPE-ELEMENT-001`, `ADR-DISPATCH-ENVELOPE-ARCHITECTURE-001` | Add `platform_tests/scripts/test_cross_harness_bridge_trigger.py` coverage for spillover dispatch. | Multiple ready targets receive distinct pending items when capacity remains; the same item is not broadcast to multiple harnesses. |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | Run the implementation-authorization begin helper after GO, before protected edits. | Authorization packet is created and constrains implementation to the declared target paths. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | Run bridge applicability and ADR/DCL clause preflights for the proposal and later implementation report. | No missing required specs and no blocking clause gaps. |
| `ADR-CODEX-HOOK-PARITY-FALLBACK-001` | Existing trigger tests plus the new spillover tests. | Hook-triggered dispatch behavior remains deterministic and parseable under Codex/Claude headless invocation surfaces. |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | Path review and `git diff --` target-path check. | Only declared in-root GT-KB platform target paths changed. |

Verification commands:

```text
groundtruth-kb/.venv/Scripts/python.exe -m pytest platform_tests/scripts/test_bridge_dispatch_config.py -q --tb=short --basetemp .codex_pytest_tmp/wi4691-dispatch-config
groundtruth-kb/.venv/Scripts/python.exe -m pytest platform_tests/scripts/test_cross_harness_bridge_trigger.py -q --tb=short --basetemp .codex_pytest_tmp/wi4691-cross-harness
groundtruth-kb/.venv/Scripts/python.exe -m ruff check groundtruth-kb/src/groundtruth_kb/bridge_dispatch_config.py scripts/cross_harness_bridge_trigger.py platform_tests/scripts/test_bridge_dispatch_config.py platform_tests/scripts/test_cross_harness_bridge_trigger.py
groundtruth-kb/.venv/Scripts/python.exe -m ruff format --check groundtruth-kb/src/groundtruth_kb/bridge_dispatch_config.py scripts/cross_harness_bridge_trigger.py platform_tests/scripts/test_bridge_dispatch_config.py platform_tests/scripts/test_cross_harness_bridge_trigger.py
```

## Acceptance Criteria

1. Dispatcher rule preference order is quality, then cost, then availability for both Prime Builder and Loyal Opposition defaults.
2. Candidates below a work item's required quality remain ineligible; current governance-grade LO floor behavior stays intact.
3. Equal-quality candidates prefer lower cost before availability.
4. Dispatch spillover assigns distinct pending bridge items across eligible ready targets with capacity, rather than broadcasting the same item to all targets.
5. Existing fallback, readiness, backoff, launchability, per-document lease, work-intent, global cap, per-role cap, and selected-batch signature protections remain intact.
6. If no eligible target meets the required quality or capacity constraints, the item remains pending and status/health surfaces report the failure or saturation rather than silently lowering quality.
7. Focused dispatcher-config and cross-harness trigger tests pass with in-root pytest basetemp paths.

## Risk / Rollback

- Risk: implementing spillover in the cross-harness trigger may be larger than a simple rule-order change. Mitigation: preserve one-target behavior as the degenerate case and lock behavior with targeted tests before widening.
- Risk: changing the dispatcher rules file while it already has local working-tree modifications could accidentally overwrite unrelated edits. Mitigation: implementation must read the current file and patch only the selection-order/prefer lines inside the approved target path.
- Risk: full `test_cross_harness_bridge_trigger.py` may be expensive. Mitigation: run the full file when feasible; otherwise include the new targeted tests plus clearly report any environment limitation in the implementation report.
- Rollback: revert the single implementation commit containing the target-path changes and bridge report. No schema migration or external deployment is in scope.

## Bridge Filing

This proposal is filed as the first status-bearing numbered bridge file for `gtkb-wi4691-quality-first-spillover-dispatch`; no prior version is deleted or rewritten. Dispatcher/TAFE state plus the numbered file chain are the live workflow state per `GOV-FILE-BRIDGE-AUTHORITY-001`.

## Recommended Commit Type

`feat` - the implementation would add dispatch spillover behavior and change dispatcher selection policy, with accompanying regression tests.

---

Copyright 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
