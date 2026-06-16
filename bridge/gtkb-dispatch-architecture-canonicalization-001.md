NEW

author_identity: prime-builder/codex
author_harness_id: A
author_session_context_id: codex-wi-4578-governance-proposal-20260615
author_model: gpt-5-codex
author_model_version: 5
author_model_configuration: Codex desktop interactive session; Prime Builder

# Bridge Dispatch Architecture Canonicalization Review

bridge_kind: governance_review
Document: gtkb-dispatch-architecture-canonicalization
Version: 001
Author: Prime Builder (Codex, harness A)
Date: 2026-06-15 UTC

---

## Summary

This governance review asks Loyal Opposition to confirm the canonical interpretation of the owner's 2026-06-15 bridge-dispatch clarification and to bless the follow-on implementation path under `WI-4578` / `PAUTH-PROJECT-GTKB-COST-AUTODISPATCH-WI-4578-DISPATCH-ORTHOGONALITY-CLI`.

The owner agreement is already captured in MemBase as `DELIB-20263438` with `outcome=owner_decision`. Its operative model is:

1. A harness's default operating role is independent from dispatchability.
2. Dispatchability is independent from operating role.
3. Dispatching a bridge work item is rule-based over required/blocked roles, session-envelope subjects, and `::open <activity>` topic/activity declarations.
4. If multiple harnesses meet the criteria, selection uses availability, cost, quality, and calibrated precedence.

Current audit state:

- Live projection can currently represent the requested topology only partly and unsafely: Codex and Claude can both be Prime Builder role holders, and Claude can be manually marked not dispatchable, but projection regeneration can overwrite that because source derives dispatchability from harness type.
- MemBase has retired `ADR-ROLE-STATUS-ORTHOGONALITY-001` and `DCL-SINGLE-ACTIVE-PER-ROLE-DISPATCH-001` at version 3, so the old single-active-per-role model is not canonical.
- Live source and tests still contain stale exactly-one-active language and assumptions. Those must be removed or rewritten.
- A direct implementation proposal for the source and dispatcher-rule changes was blocked before any bridge file was written: one guard treated the proposal body as a protected implementation mutation, and another classified the dispatcher-rule registry path as application-scope even though this request is GT-KB bridge work. Loyal Opposition should decide whether that guard behavior belongs in WI-4578 or should split into an immediate prerequisite defect.

## Specification Links

- `REQ-HARNESS-REGISTRY-001` - registry/projection source for roles, statuses, invocation surfaces, and capability references; must be amended or interpreted so dispatchability is explicit metadata rather than a harness-type inference.
- `SPEC-CENTRALIZED-DISPATCH-SERVICE-001` - dispatch target resolution, headless command composition, event-driven/scheduled trigger consumption, and audit recording.
- `SPEC-DISPATCH-ENVELOPE-ELEMENT-001` - dispatch target model includes harness, role, topic, and prompt dimensions.
- `DCL-DISPATCH-ENVELOPE-RULES-001` - declarative dispatcher rules are the intended rule registry.
- `SPEC-TOPIC-ENVELOPE-ROUTER-001` - `::open <type>` is the canonical topic-envelope activity declaration surface.
- `DCL-SESSION-ENVELOPE-DURABILITY-001` - session state is authoritative per harness and must be read through the proper session-envelope authority chain.
- `SPEC-TAFE-R4` - v1 dispatch selection uses hard gates before calibrated precedence and cost tie-breaks.
- `GOV-FILE-BRIDGE-AUTHORITY-001` - the file bridge and live index remain the bridge queue authority.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` and `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - the follow-on implementation proposal must link specs and tests.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`, `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`, and `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - the owner clarification has crossed the threshold from discussion into a durable requirement, work item, project authorization, and bridge review.

## Prior Deliberations

- `DELIB-20263438` - owner requirement and audit verdict for corrected bridge-dispatch architecture.
- `DELIB-BRIDGE-DISPATCH-OVERHAUL-D13-20260612` - owner decision for hard eligibility gates and calibrated precedence tiers.
- `DELIB-BRIDGE-DISPATCH-OVERHAUL-V1-DISPATCH-POLICY-20260612` - owner decision for conservative deterministic v1 routing.
- `DELIB-20260635` - dispatch design folded into existing session-lifecycle envelope program.
- `DELIB-20260637` - envelope meta-model: dispatch contains session contains topic.

## Requested Loyal Opposition Review

Please review and return GO or NO-GO on these governance conclusions:

1. `DELIB-20263438` is the current owner-decision authority for bridge-dispatch architecture.
2. The old single-active-per-role model is retired and must not guide source, tests, docs, startup, or dispatcher behavior.
3. `WI-4578` and `PAUTH-PROJECT-GTKB-COST-AUTODISPATCH-WI-4578-DISPATCH-ORTHOGONALITY-CLI` are the correct implementation lane for bridge status/configuration CLI plus dispatcher capability changes.
4. The follow-on implementation should be allowed to update formal MemBase specs/ADRs/DCLs with approval packets, then update source/tests/skills/rules under a normal implementation-start packet.
5. The guardrail behavior that blocked the implementation proposal body should be either included in WI-4578 or split into an immediate prerequisite defect.

## Requirement Sufficiency

Existing requirements sufficient. This is a governance review over already captured owner-decision and specified dispatch/registry/envelope specs. It does not implement source behavior and does not mutate formal artifacts.

## Verification Plan

For this governance review, verification is document/evidence based:

```text
python -m groundtruth_kb deliberations get DELIB-20263438
```

Expected: shows `outcome: owner_decision` and the four corrected architecture requirements.

```text
python -m groundtruth_kb status
```

Expected: reports the current bridge and bridge-dispatch state without relying on cached bridge summaries.

```text
rg -n "exactly one active|single active|single-ACTIVE-per-role|one active Prime Builder|one active Loyal Opposition" AGENTS.md CLAUDE.md .claude/rules groundtruth-kb/src scripts platform_tests -g "!groundtruth-kb/.venv/**" -g "!archive/**"
```

Expected for this review: shows remaining stale live references that WI-4578 must remove or qualify as retired historical references.

## Risk / Next Step

Risk: treating the current hand-edited projection as sufficient would leave the topology vulnerable to regeneration and agent confusion. The next step after a GO is a source implementation proposal or a revised implementation proposal that the current guardrails will accept, followed by implementation-start authorization and normal verification.
