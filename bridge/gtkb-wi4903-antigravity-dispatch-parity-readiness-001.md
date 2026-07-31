NEW

# gtkb-wi4903-antigravity-dispatch-parity-readiness - Antigravity dispatch parity readiness probe and waivers

bridge_kind: prime_proposal
Document: gtkb-wi4903-antigravity-dispatch-parity-readiness
Version: 001
Author: Prime Builder (Codex)
Date: 2026-06-29T10:04:45Z

author_identity: prime-builder/codex/A
author_harness_id: A
author_session_context_id: 019f12d3-184b-7f01-aebf-2d2308b377a7
author_model: GPT-5 Codex
author_model_version: current Codex runtime
author_model_configuration: Auto-builder autonomous Prime Builder run

Project Authorization: PAUTH-PROJECT-HARNESS-PARITY-PHASE-2-IMPLEMENTATION-2026-06-29
Project: PROJECT-HARNESS-PARITY-PHASE-2
Work Item: WI-4903

target_paths: ["scripts/verify_antigravity_dispatch.py", "scripts/generate_antigravity_skill_adapters.py", "platform_tests/scripts/test_verify_antigravity_dispatch.py", "platform_tests/scripts/test_generate_antigravity_skill_adapters.py", "config/agent-control/harness-capability-registry.toml", ".agent/skills/**"]

implementation_scope: source test config skill_update
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

---

## Summary

Implement the proposal-ready slice of `WI-4903`: make Antigravity dispatch parity measurable and bridge-governed without changing live dispatcher topology. The work will harden or extend the existing Antigravity readiness/projection surfaces so Prime Builder can tell whether Antigravity has feasible headless Prime Builder, Loyal Opposition, advisory, and verification routes, and so impossible gaps are represented as typed parity waivers instead of hidden release risks.

This proposal does not activate retired Antigravity harness `C`, does not move Codex `A` or Cursor `E` between roles, and does not revise the `WI-4885` topology decision. It keeps the current release-health quarantine intact: topology activation remains blocked until a later owner decision or a separate GO'd thread changes that state.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` - protected harness/parity implementation must flow through the bridge and preserve append-only bridge evidence.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - this proposal links the implementation to governing requirements and verification.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - project authorization, project, work item, and target path metadata are required for implementation eligibility.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - completion must map every claimed behavior to executed tests or checks.
- `GOV-STANDING-BACKLOG-001` - `WI-4903` is the governed backlog row for this Antigravity parity work.
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` - the active Phase 2 PAUTH bounds the allowed mutation classes and work item set.
- `DCL-CROSS-HARNESS-ENFORCEMENT-001` - Antigravity parity work must preserve cross-harness bridge/governance behavior.
- `ADR-DISPATCHER-ARCHITECTURE-001` - dispatcher readiness and launch behavior must stay within the governed dispatcher architecture and must not restore retired pollers.
- `GOV-HARNESS-ONBOARDING-CONTRACT-001` - harness readiness must be represented by explicit capability, guard, author metadata, and adapter evidence.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` - readiness findings and waivers must be durable governed artifacts, not harness-local notes.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` - implementation should preserve reusable readiness evidence for later harness-parity work.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - newly discovered readiness gaps must route to backlog/waiver artifacts rather than ad hoc scratchpads.

## Prior Deliberations

- `DELIB-20260629-HARNESS-PARITY-PHASE-2-OWNER-DIRECTIVE` - owner directive creating and authorizing the release-blocking Phase 2 harness parity project.
- `bridge/gtkb-wi4885-dispatch-topology-activation-008.md` - latest NO-GO holding Antigravity/Codex/Cursor topology activation pending owner decision; this proposal avoids that blocked mutation.
- `bridge/gtkb-antigravity-lo-hallucination-prevention-005.md` - prior evidence that Antigravity's hookless verdict path needs governed helper coverage.
- `WI-4749` - related backlog row for extending verdict-evidence-anchor protection to Antigravity's hookless write path.
- `DELIB-20266285` - owner-approved typed parity waiver pattern already used for cross-harness impossible or surface-different gaps.

## Owner Decisions / Input

No new owner decision is required before Loyal Opposition review. Implementation is covered by `PAUTH-PROJECT-HARNESS-PARITY-PHASE-2-IMPLEMENTATION-2026-06-29`, whose owner decision is `DELIB-20260629-HARNESS-PARITY-PHASE-2-OWNER-DIRECTIVE`, and `WI-4903` is included in that authorization.

This proposal explicitly excludes Antigravity activation, durable role changes, dispatcher target selection changes, credential lifecycle action, and production deployment. Any future topology change remains governed by the blocked `WI-4885` decision path or a separate owner-approved bridge.

## Requirement Sufficiency

Existing requirements sufficient. `WI-4903` defines the Antigravity readiness/parity outcome, and the active Phase 2 project authorization covers source, test, config, skill-update, and documentation changes for that work item. The linked bridge, project-authorization, cross-harness enforcement, dispatcher architecture, and harness-onboarding specifications define the implementation and verification constraints.

## Spec-Derived Verification Plan

Planned verification:

```text
python -m pytest platform_tests/scripts/test_verify_antigravity_dispatch.py -q --tb=short
python -m pytest platform_tests/scripts/test_generate_antigravity_skill_adapters.py -q --tb=short
python scripts/generate_antigravity_skill_adapters.py --check --update-registry
python scripts/verify_antigravity_dispatch.py --help
gt bridge dispatch status --json
```

Expected coverage:

- `GOV-FILE-BRIDGE-AUTHORITY-001`: Antigravity bridge/verdict readiness checks must use governed helper paths or report an explicit typed waiver for hookless limitations.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` and `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001`: implementation-start must authorize exactly the target paths listed above before any protected mutation.
- `DCL-CROSS-HARNESS-ENFORCEMENT-001` and `GOV-HARNESS-ONBOARDING-CONTRACT-001`: tests and readiness output must classify Antigravity role/task routes as supported, blocked by implementation gap, or impossible with waiver evidence.
- `ADR-DISPATCHER-ARCHITECTURE-001`: `gt bridge dispatch status --json` must remain readable and must not show an unintended topology activation for retired Antigravity `C` from this implementation.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`: the implementation report must carry forward this mapping with exact command output and observed results.

## Risk / Rollback

Primary risk is accidentally treating readiness/projection work as permission to activate Antigravity as a dispatch target. The implementation must therefore avoid durable role/status mutation and keep `harness-state/harness-registry.json` outside the mutation target list. Secondary risk is over-waiving feasible gaps; waiver records must be typed, evidence-backed, and review-triggered rather than used as a blanket release escape.

Rollback is a single implementation commit revert. No production deployment, credential lifecycle action, or dispatcher topology change is in scope.

## Bridge Filing

This proposal is filed under `bridge/` as the next status-bearing numbered
bridge file for `gtkb-wi4903-antigravity-dispatch-parity-readiness`; no prior version is deleted or rewritten
(append-only). Dispatcher/TAFE state plus the numbered file chain are the live
workflow state per `GOV-FILE-BRIDGE-AUTHORITY-001`.

## Recommended Commit Type

feat:

Justification: this adds or hardens an Antigravity readiness/parity capability surface plus regression tests and generated adapter/registry evidence.

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
