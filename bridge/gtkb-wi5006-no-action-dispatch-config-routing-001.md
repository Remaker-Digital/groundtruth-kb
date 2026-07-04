NEW

# gtkb-wi5006-no-action-dispatch-config-routing — Repair NO-ACTION dispatcher config routing

bridge_kind: prime_proposal
Document: gtkb-wi5006-no-action-dispatch-config-routing
Version: 001
Author: Prime Builder / Codex A
Date: 2026-07-04T04:55:26Z

author_identity: prime-builder/codex/A
author_harness_id: A
author_session_context_id: 019f247b-4dc8-7b32-a2ab-25839614d33f
author_model: GPT-5 Codex
author_model_version: GPT-5
author_model_configuration: Codex desktop; E:/GT-KB; danger-full-access; approval-policy never; interactive role Prime Builder via ::init gtkb pb

Project Authorization: PAUTH-PROJECT-GTKB-OPS-DISPATCHER-MODERNIZATION-WI-5006-NO-ACTION-DISPATCH-ROUTING
Project: PROJECT-GTKB-OPS-DISPATCHER-MODERNIZATION
Work Item: WI-5006

target_paths: ["groundtruth-kb/src/groundtruth_kb/bridge_dispatch_transactions.py", "config/dispatcher/rules.toml", "platform_tests/scripts/test_bridge_dispatch_transactions.py", "platform_tests/scripts/test_bridge_dispatch_config.py", "platform_tests/scripts/test_cross_harness_protocol_parity.py", "platform_tests/scripts/test_dispatcher_runtime.py"]

implementation_scope: source, dispatcher-config, tests, bridge
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

---

## Summary

Live headless soak found a `NO-ACTION` routing split-brain after WI-5002 reached a legitimate Prime Builder `NO-ACTION` disposition at `bridge/gtkb-wi5002-codex-dotdir-sandbox-acl-correction-011.md`. The bridge scan helper correctly reports latest `NO-ACTION` as Loyal Opposition-actionable, and runtime/test surfaces already recognize `NO-ACTION` as the lifecycle state that removes the thread from Prime Builder implementation dispatch. The dispatcher config layer does not: `config/dispatcher/rules.toml` still limits the default LO rule to `NEW`/`REVISED`, and `groundtruth-kb/src/groundtruth_kb/bridge_dispatch_transactions.py` rejects `NO-ACTION` as an invalid status for governed `set-rule` transactions.

This proposal repairs that specific gap: extend the dispatcher config transaction validator to accept `NO-ACTION`, update the governed live/default LO rule to include `NO-ACTION`, and add focused regression tests so future protocol additions cannot be stranded between bridge lifecycle semantics and dispatch configuration. The implementation must preserve dispatcher-owned routing and the direct harness-to-harness launch prohibition.

All generated proposal, bridge, source, test, and dispatcher-config artifacts for this work remain under `E:/GT-KB`; no external workspace, archive path, or harness-local scratchpad is part of the implementation authority.

## Specification Links

- `SPEC-CENTRALIZED-DISPATCH-SERVICE-001` — Dispatch must resolve role targets from governed registry/config and record dispatch decisions without harness-owned fallback.
- `ADR-DISPATCHER-ARCHITECTURE-001` — The persistent daemon is the dispatch control plane; harnesses are consumers only.
- `GOV-FILE-BRIDGE-AUTHORITY-001` — Status-bearing bridge state must remain role-correct and append-only.
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` — Protected source, test, and dispatcher-config mutation requires active project authorization and GO.
- `DCL-PROJECT-AUTHORIZATION-ENVELOPE-001` — Implementation must stay inside the bounded WI-5006 PAUTH.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` — This proposal links the defect repair to governing dispatch and bridge requirements.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` — Machine-readable project authorization, project, and work item headers are present above.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — Verification must prove the spec-derived routing behavior, not only test that code changed.
- `GOV-STANDING-BACKLOG-001` — The live regression has been preserved as `WI-5006` with linked `TEST-11281`.
- `DCL-HARNESS-DISPATCH-ISOLATION-INVARIANT-001` — The repair must keep harnesses from directly triggering or substituting for each other.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` — The live regression was captured as governed backlog, test, PAUTH, and bridge artifacts rather than left as chat-only context.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` — The repair keeps traceability across owner directive, work item, test, proposal, implementation report, and verification.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` — `NO-ACTION` is a bridge lifecycle status and must flow through lifecycle-aware dispatch routing.

## Prior Deliberations

- `DELIB-20260703-HEADLESS-DISPATCH-STABILITY-GOAL` — Owner-directed active goal to make headless bridge processing stable with Claude Code/Ollama/Antigravity as LO and Codex as PB.
- `DELIB-HARNESS-OPS-NO-ACTION-FIRST-CLASS-BRIDGE-STATUS-20260702` — Establishes `NO-ACTION` as a first-class Prime Builder-authored bridge status.
- `DELIB-HARNESS-NO-ACTION-LO-ACTIONABLE-BRIDGE-ROUTING-20260702` — Establishes latest `NO-ACTION` as Loyal Opposition-actionable and non-Prime-implementation-dispatchable.
- `DELIB-HARNESS-NO-ACTION-PRIOR-GO-NONDISPATCHABLE-SUBSEQUENT-GO-FRESH-AUTHORITY-20260702` — Establishes that a prior GO under latest `NO-ACTION` is non-dispatchable until fresh corrected authority exists.
- `INTAKE-f92c585f` — Relevant intake for allowed LO responses to `NO-ACTION` artifacts.
- `INTAKE-f8bc08a3` — Relevant intake for using dispatcher/bridge CLI surfaces as the primary mutating UI for GT-KB artifact operations.
- `bridge/gtkb-ops-lifecycle-protocol-foundation-001.md` through `bridge/gtkb-ops-lifecycle-protocol-foundation-012.md` — WI-4957 made `NO-ACTION` a first-class bridge lifecycle concept and was VERIFIED, but did not update the config transaction validator or live LO rule.

## Owner Decisions / Input

No new owner decision is required. `DELIB-20260703-HEADLESS-DISPATCH-STABILITY-GOAL` authorizes follow-up dispatcher-stability repairs discovered during the live headless bridge soak, and `PAUTH-PROJECT-GTKB-OPS-DISPATCHER-MODERNIZATION-WI-5006-NO-ACTION-DISPATCH-ROUTING` supplies bounded implementation authority for WI-5006. This proposal does not request credential changes, production deployment, durable role reassignment, retired poller restoration, or direct harness-to-harness launch.

## Requirement Sufficiency

Existing requirements sufficient. `SPEC-CENTRALIZED-DISPATCH-SERVICE-001`, `ADR-DISPATCHER-ARCHITECTURE-001`, and the WI-4957 NO-ACTION deliberations already require dispatcher-owned routing where `NO-ACTION` is LO-actionable and not PB implementation-dispatchable. The defect is an implementation/config transaction lag behind those requirements, not an ambiguous requirement.

## Spec-Derived Verification Plan

Verification must prove the following outcomes:

```text
python -m pytest platform_tests/scripts/test_bridge_dispatch_transactions.py platform_tests/scripts/test_bridge_dispatch_config.py platform_tests/scripts/test_cross_harness_protocol_parity.py platform_tests/scripts/test_dispatcher_runtime.py -q --tb=short
```

- `DCL-PROJECT-AUTHORIZATION-ENVELOPE-001` and `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001`: implementation-start preflight must pass only for the declared target paths after GO.
- `SPEC-CENTRALIZED-DISPATCH-SERVICE-001` and `ADR-DISPATCHER-ARCHITECTURE-001`: dispatcher config transactions must accept `NO-ACTION`, and the default LO dispatch rule must include `NO-ACTION` alongside `NEW` and `REVISED`.
- `GOV-FILE-BRIDGE-AUTHORITY-001`: latest `NO-ACTION` bridge entries must remain LO-actionable and not appear in Prime Builder actionable scans.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`: focused tests must fail before the repair or encode the missing behavior directly, then pass after implementation.
- Manual/CLI checks:

```text
python -m groundtruth_kb.cli bridge dispatch config set-rule bridge-loyal-opposition-cheap-fast-default --status NEW --status REVISED --status NO-ACTION --dry-run --json
python -m groundtruth_kb.cli bridge dispatch status --json
python -m groundtruth_kb.cli bridge dispatch health --json
```

Expected result: the dry-run transaction succeeds; dispatcher status/health no longer strands latest `NO-ACTION` bridge entries outside LO routing; no Prime Builder dispatch is selected for the WI-5002 `NO-ACTION` thread.

## Risk / Rollback

Risk is limited to broadening the accepted dispatch-rule status vocabulary and adding `NO-ACTION` to the default LO rule. The intended behavior is narrower than a new routing mode: it aligns config with existing lifecycle semantics already implemented in bridge scans and dispatcher runtime tests. Rollback is a single revert of the source/test/config transaction changes plus restoring the LO rule to `NEW`/`REVISED` through the governed dispatcher config CLI if LO review finds over-routing.

## Bridge Filing

This proposal is filed under `bridge/` as the next status-bearing numbered
bridge file for `gtkb-wi5006-no-action-dispatch-config-routing`; no prior version is deleted or rewritten
(append-only). Dispatcher/TAFE state plus the numbered file chain are the live
workflow state per `GOV-FILE-BRIDGE-AUTHORITY-001`.

## Recommended Commit Type

fix — this repairs a regression between verified bridge lifecycle semantics and the dispatcher config transaction/rule layer.

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
