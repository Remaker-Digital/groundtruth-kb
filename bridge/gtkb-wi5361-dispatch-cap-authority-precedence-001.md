NEW

# WI-5361: Make dispatcher cap precedence explicit and auditable

bridge_kind: prime_proposal
Document: gtkb-wi5361-dispatch-cap-authority-precedence
Version: 001
Author: Prime Builder (Codex A)
Date: 2026-07-16 UTC

author_identity: prime-builder/codex/A
author_harness_id: A
author_session_context_id: 019f5f66-9582-7f03-a3f1-3c75e6bd9d0a
author_model: OpenAI Codex
author_model_version: gpt-5.5
author_model_configuration: Codex Desktop interactive Prime Builder; reasoning xhigh

Project Authorization: PAUTH-DISPATCHER-BLACK-BOX-WI5361-CAP-AUTHORITY-20260716
Project: PROJECT-GTKB-OPS-DISPATCHER-MODERNIZATION-DISPATCHER-BLACK-BOX-HARDENING
Work Item: WI-5361

target_paths: ["groundtruth-kb/src/groundtruth_kb/bridge_dispatch_config.py", "groundtruth-kb/src/groundtruth_kb/bridge_dispatch_transactions.py", "platform_tests/groundtruth_kb/test_bridge_dispatch_cap_authority.py"]

implementation_scope: source | dispatcher policy authority | test
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

---

## Summary

Canonical `gt harness show --harness A` reports harness version 61 with
`invocation_surfaces.dispatch.dispatch_max_items=1`, while the current
dispatcher status and report select A with `dispatch_max_items=4`. The wrong
value is introduced before launch by `apply_dispatch_config_to_record()`, which
always replaces the projected harness cap with an unqualified legacy
`rules.toml` `max_items` value. The runtime capacity helper already enforces the
selected target value, so changing it would duplicate authority and overlap
WI-5297.

Define one precedence contract in the existing dispatcher config projection:
an explicit audited `set-caps` or `add-harness --max-items` transaction writes
both `max_items` and `max_items_override=true`; a marked override wins over the
canonical harness value. Without that marker, a valid canonical
`dispatch_max_items` wins, and an unmarked legacy config cap is only a fallback
when the canonical record has no valid cap. Candidate summaries expose
`dispatch_max_items_source` as `dispatcher_config_override`,
`harness_registry`, or `dispatcher_config_fallback`. No live config, harness
eligibility, ranking, routing, worker, lease, TAFE, or runtime state is mutated
by this implementation.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` - requires this numbered, independently reviewed bridge lifecycle.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - requires concrete governing links before GO.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - binds the proposal to the active project, PAUTH, work item, and exact targets.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - requires executed spec-to-test evidence before VERIFIED.
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` - preserves the post-GO claim and implementation-start gates.
- `DCL-PROJECT-AUTHORIZATION-OPERATION-TIME-ENFORCEMENT-001` - requires active exact-scope PAUTH evidence when protected implementation starts.
- `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001` - PAUTH does not substitute for independent GO.
- `SPEC-CENTRALIZED-DISPATCH-SERVICE-001` - requires one daemon-owned target resolution and dispatch audit path.
- `ADR-DISPATCHER-ARCHITECTURE-001` - keeps selection and launch capacity under the centralized dispatcher architecture.
- `SPEC-DISPATCHER-CONTROL-SURFACE-001` - requires operator cap changes to use the canonical control surface.
- `DCL-DISPATCHER-CONFIG-CLI-ONLY-001` - requires audited config transactions instead of direct config edits.
- `GOV-HARNESS-STATE-SOT-CONSOLIDATION-001` - makes the harness registry projection authoritative unless an explicit policy override exists.
- `DCL-HARNESS-STATE-SOT-READER-CONTRACT-001` - requires consumers to read canonical projected harness metadata consistently.
- `REQ-HARNESS-REGISTRY-001` - governs persisted harness dispatch metadata including `dispatch_max_items`.
- `GOV-SOURCE-OF-TRUTH-FRESHNESS-001` - prohibits stale duplicate values from silently overriding current canonical metadata.
- `GOV-SOT-SINGLETON-001` - requires one deterministically explained authority for the effective cap.
- `DCL-DISPATCH-ENVELOPE-RULES-001` - requires the selected target envelope to carry the correct bounded dispatch behavior.
- `GOV-STANDING-BACKLOG-001` - WI-5361 and TEST-11477 preserve the defect and acceptance evidence.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` - preserves the repair as work item, proposal, test, report, and verdict artifacts.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` - requires durable lifecycle evidence for the owner-directed repair.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - keeps the item open through implementation report, independent verification, and focused commit.

## Prior Deliberations

- `DELIB-20260715-FLEET-HARNESS-DEFECT-REPAIR-AUTHORIZATION` - authorizes bounded carriers for fleet defects while preserving exact GO, target, claim, implementation-start, independent verification, and focused-commit gates.
- `DELIB-202666235` - independent WI-5233 GO established that the dispatch-surface cap is authoritative at the runtime capacity boundary; this proposal corrects the upstream projection that feeds that boundary.
- `bridge/gtkb-dispatch-selection-binding-sot-consolidation-003.md` through `-010.md` - established registry/MemBase authority for dispatch capability and ranking while retaining caps as policy-capable config fields.
- `bridge/gtkb-wi5233-dispatch-selection-order-cap-repair-001.md` through `-004.md` - established that runtime launch capacity must honor the selected target's dispatch-surface cap; WI-5361 fixes the earlier projection that currently selects the wrong cap.
- `bridge/gtkb-wi5310-codex-effective-workspace-profile-008.md` - records F2 evidence that A is selected at 4 despite canonical value 1 and requires this separate carrier.

## Owner Decisions / Input

`DELIB-20260715-FLEET-HARNESS-DEFECT-REPAIR-AUTHORIZATION` authorizes this
bounded defect-repair carrier. The owner's durable routing direction also says
functional funded harnesses should be dispatchable by default and target
selection rules are orthogonal. This proposal changes neither eligibility nor
target ranking; it only resolves the effective per-target cap after a target is
selected. No additional owner decision is required.

## Requirement Sufficiency

Existing requirements sufficient. The centralized dispatcher, canonical
harness-state authority, audited control-surface, and source-of-truth freshness
requirements already demand deterministic cap resolution. WI-5361 records the
missing precedence rule as a bounded implementation defect; no new product or
governance requirement is needed.

## Spec-Derived Verification Plan

| Governing requirement | Executed evidence required before verification |
| --- | --- |
| Registry authority, freshness, singleton (`GOV-HARNESS-STATE-SOT-CONSOLIDATION-001`, `DCL-HARNESS-STATE-SOT-READER-CONTRACT-001`, `REQ-HARNESS-REGISTRY-001`, `GOV-SOURCE-OF-TRUTH-FRESHNESS-001`, `GOV-SOT-SINGLETON-001`) | New focused tests prove canonical cap 1 beats unmarked legacy cap 4, malformed/missing canonical cap falls back to legacy 4, and marked audited override 4 beats canonical 1; each case asserts `dispatch_max_items_source`. |
| Audited control surface (`SPEC-DISPATCHER-CONTROL-SURFACE-001`, `DCL-DISPATCHER-CONFIG-CLI-ONLY-001`) | Focused transaction tests prove `set_caps()` and `add_harness(max_items=...)` serialize `max_items_override=true`, round-trip through `load_bridge_dispatch_config()`, and preserve transaction audit behavior. No direct live config mutation is used. |
| Central dispatcher and envelope (`SPEC-CENTRALIZED-DISPATCH-SERVICE-001`, `ADR-DISPATCHER-ARCHITECTURE-001`, `DCL-DISPATCH-ENVELOPE-RULES-001`) | A synthetic status fixture proves selected candidate cap/source match the effective value. A report fixture over that status proves `effective_per_cycle_ceiling` uses the same value. Existing WI-5233 runtime tests remain the launch-enforcement boundary; no runtime source change is made. |
| Bridge/project gates (`GOV-FILE-BRIDGE-AUTHORITY-001`, project/PAUTH DCLs, proposal linkage DCLs) | Read back latest GO, matching claim, PAUTH, exact target set, and successful implementation-start packet before any protected edit; report the packet and commands in the implementation report. |
| Spec-derived verification and artifact lifecycle | `groundtruth-kb/.venv/Scripts/python.exe -m pytest platform_tests/groundtruth_kb/test_bridge_dispatch_cap_authority.py platform_tests/groundtruth_kb/cli/test_bridge_dispatch_config_transactions_cli.py platform_tests/groundtruth_kb/cli/test_bridge_dispatch_report_cli.py -q --tb=short` passes; focused Ruff checks pass; a NEW implementation report carries exact results for independent LO verification. |

The focused test module uses only temporary project roots and synthetic
registry/config data. It does not start the daemon, invoke a harness, alter
eligibility, or touch live dispatcher state.

## Risk / Rollback

The main compatibility risk is treating every existing legacy `max_items` row
as an override and thereby preserving the defect, or ignoring an operator's
future explicit `set-caps` request. The marker distinguishes those cases.
Unmarked legacy values remain usable as fallback for records that have no valid
canonical cap, avoiding an abrupt unbounded/default transition. Rollback is one
focused source/test commit; no data migration, live transaction, or runtime
state rollback is required.

## Bridge Filing

This proposal is filed under `bridge/` as the next status-bearing numbered
bridge file for `gtkb-wi5361-dispatch-cap-authority-precedence`; no prior version is deleted or rewritten
(append-only). Dispatcher/TAFE state plus the numbered file chain are the live
workflow state per `GOV-FILE-BRIDGE-AUTHORITY-001`.

## Recommended Commit Type

`fix:` - this corrects an observed dispatcher authority defect and adds focused
regression coverage without adding a new operator capability.

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
