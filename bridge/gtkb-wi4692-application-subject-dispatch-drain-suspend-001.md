NEW
author_identity: prime-builder/codex
author_harness_id: A
author_session_context_id: 019ef0d4-5474-7af3-af31-4c8ab4cf4f7a
author_model: GPT-5 Codex
author_model_version: gpt-5-codex
author_model_configuration: Codex desktop heartbeat continuation; approval_policy=never
author_metadata_source: explicit heartbeat proposal metadata

Project Authorization: PAUTH-PROJECT-GTKB-ENVELOPE-DISPOSITION-AND-AUTONOMOUS-DISPATCH-ENVELOPE-DISPOSITION-AND-AUTONOMOUS-DISPATCH-BOUNDED-IMPLEMENTATION-2026-06-23
Project: PROJECT-GTKB-ENVELOPE-DISPOSITION-AND-AUTONOMOUS-DISPATCH
Work Item: WI-4692
bridge_kind: prime_proposal

# Implementation Proposal - WI-4692 Application-Subject Dispatch Drain/Suspend

Document: gtkb-wi4692-application-subject-dispatch-drain-suspend
Version: 001 (NEW)
Date: 2026-06-23 UTC
Author Role: Prime Builder
Project Authorization: PAUTH-PROJECT-GTKB-ENVELOPE-DISPOSITION-AND-AUTONOMOUS-DISPATCH-ENVELOPE-DISPOSITION-AND-AUTONOMOUS-DISPATCH-BOUNDED-IMPLEMENTATION-2026-06-23
Project Authorization Owner Decision: DELIB-20265586
Project: PROJECT-GTKB-ENVELOPE-DISPOSITION-AND-AUTONOMOUS-DISPATCH
Work Item: WI-4692
Recommended commit type: fix

target_paths: ["scripts/single_harness_bridge_dispatcher.py", "scripts/cross_harness_bridge_trigger.py", "platform_tests/scripts/test_single_harness_bridge_dispatcher.py", "platform_tests/scripts/test_cross_harness_bridge_trigger.py", "platform_tests/scripts/test_cross_harness_trigger_suppression.py", "platform_tests/scripts/test_dispatch_suppression_routing.py"]

## First-Line Role Eligibility Check

Resolved current session role is Prime Builder, harness A / Codex. Prime Builder may file NEW bridge proposals and may not write GO, NO-GO, or VERIFIED. This file requests Loyal Opposition review and does not mutate protected source or tests.

## Code Quality Baseline

| Rule ID | Applies? | Compliance plan | Verification | Waiver / N/A reason |
|---|---|---|---|---|
| CQB-1 Targeted scope | Yes | Restrict edits to dispatch gating and targeted regression tests for WI-4692. | `git diff -- scripts/single_harness_bridge_dispatcher.py scripts/cross_harness_bridge_trigger.py platform_tests/scripts/test_single_harness_bridge_dispatcher.py platform_tests/scripts/test_cross_harness_bridge_trigger.py platform_tests/scripts/test_cross_harness_trigger_suppression.py platform_tests/scripts/test_dispatch_suppression_routing.py` | N/A |
| CQB-2 Spec-derived behavior | Yes | Add tests for application-subject dispatch suspension, in-flight drain preservation, and normal GT-KB dispatch behavior. | Targeted pytest commands in verification plan. | N/A |
| CQB-3 Deterministic tests | Yes | Use local temp project/state fixtures and monkeypatch worker spawn paths. | Targeted pytest commands. | N/A |
| CQB-4 Formatting and lint | Yes | Keep Python edits ruff-clean and formatted. | `ruff check` and `ruff format --check` on touched files. | N/A |
| CQB-5 No credentials/destructive actions | Yes | Read only canonical work-subject state and suppress new dispatch; no credential, deployment, cleanup, or formal artifact mutation. | Code review plus helper/gate checks. | N/A |
| CQB-6 Backward compatibility | Yes | Preserve no-pending, unchanged, lease/contention, work-intent, topology, and default subject behavior. | Existing dispatcher regression tests plus new negative controls. | N/A |

## Requirement Sufficiency

Existing requirements sufficient. WI-4692 unambiguously requires that active work-subject `application` suspend NEW GT-KB-scoped headless dispatch while in-flight GT-KB threads drain to VERIFIED. The existing canonical work-subject state and dispatcher state/lease/work-intent mechanisms are enough to implement this without owner input, formal artifact mutation, or scope expansion.

## Scope

Implement a source/test slice for both live dispatch substrates:

- Cross-harness event-driven trigger: `scripts/cross_harness_bridge_trigger.py`.
- Single-harness scheduled dispatcher: `scripts/single_harness_bridge_dispatcher.py`.

When `.claude/session/work-subject.json` resolves `current_subject` to `application`, new headless dispatch for GT-KB bridge work is suppressed. The suppression is a normal non-error dispatcher result in dispatch state/diagnostics. It must not mutate bridge status, cancel running workers, release work-intent claims, or clear leases.

## Non-Scope

- No GOV, SPEC, ADR, DCL, PB, REQ, or Deliberation Archive mutation.
- No application source mutation under `applications/`.
- No role assignment, harness registry, project membership, or project authorization mutation.
- No retired OS poller or smart-poller restoration.
- No cancellation, release, or forced takeover of in-flight GT-KB work.

## Proposed Implementation

1. Add a fail-soft helper in the dispatcher path that reads `scripts.workstream_focus.load_state(project_root)` and returns whether the normalized `current_subject` is `application`; missing/malformed state preserves the GT-KB default.
2. In `scripts/cross_harness_bridge_trigger.py`, after live bridge state/actionable computation and pending-exit processing but before worker launch/work-intent acquisition, suppress new dispatch batches under application subject.
3. In `scripts/single_harness_bridge_dispatcher.py`, apply the same guard before `_spawn_worker` and before any Prime work-intent acquisition for the selected batch.
4. Record a stable reason such as `work_subject_application_suspended` with raw/pending/selected counts where practical, without updating successful-dispatch signatures in a way that prevents retry after subject returns to GT-KB infrastructure.
5. Preserve drain semantics by leaving active leases, work-intent records, pending exit-code processing, and running workers alone.
6. Add targeted tests for application-subject suppression and GT-KB/default negative controls on both substrates.

## Specification Links

- `ADR-ENVELOPE-META-MODEL-001`: dispatch/session/topic envelope containment and dispatch-event placement.
- `DCL-ENVELOPE-META-MODEL-001`: envelope-consuming code must preserve qualified envelope semantics and dispatch-event persistence boundaries.
- `ADR-DISPATCH-ENVELOPE-ARCHITECTURE-001`: dispatch resolves targets through registry data, uses singleton dispatch discipline, and fires only after an activity gate says work exists.
- `ADR-SMART-POLLER-OWNER-OUT-OF-LOOP-001` and `DCL-SMART-POLLER-AUTO-TRIGGER-001`: mechanism-agnostic dispatch-on-actionable-change invariant, with no spawn while idle or unchanged.
- `SPEC-SINGLE-HARNESS-BRIDGE-DISPATCHER-001`: single-harness dispatcher behavior, kind-aware dispatchability, lock/state discipline, spawn semantics, and coexistence.
- `DCL-SINGLE-HARNESS-DISPATCHER-DESKTOP-TASK-001`: scheduled-task wake substrate remains unchanged; this WI changes only spawn eligibility.
- `ADR-SINGLE-HARNESS-OPERATING-MODE-001`: single-harness and multi-harness dispatch substrates are both first-class.
- `SPEC-CANONICAL-INIT-KEYWORD-SYNTAX-001`: subject vocabulary includes `gtkb` and `application`; application subject is resolved from work-subject state, not hardcoded adopter names.
- `DCL-INIT-KEYWORD-CONSISTENT-ASSERTION-001`: headless dispatch receiver behavior is subject-aware and durable-role-aware.
- `DCL-SESSION-ROLE-RESOLUTION-001`, `GOV-SESSION-ROLE-AUTHORITY-001`, `ADR-INTERACTIVE-SESSION-ROLE-OVERRIDE-001`, `ADR-ROLE-AUTHORITY-INTERACTIVE-PERSISTENCE-001`, and `DCL-INTERACTIVE-SESSION-ROLE-PERSISTENCE-001`: role resolution and interactive role persistence are separate from the active subject; this WI does not change role authority.
- `DCL-SESSION-ENVELOPE-DURABILITY-001`: session envelopes carry subject fields and per-harness authority; implementation must not confuse subject with durable role.
- `DCL-ACTIVITY-DISPOSITION-PROFILE-001`: activity disposition direction guardrails declare manipulated objects; application-subject sessions must not silently manipulate GT-KB dispatch work.
- `ADR-APPLICATION-ISOLATION-CONTRACT-001`, `ADR-ISOLATION-APPLICATION-PLACEMENT-001`, `DCL-APP-ROOT-MINIMIZATION-001`, `GOV-AGENT-RED-GTKB-CONFORMANCE-001`, and `GOV-AGENT-RED-NESTED-IN-APPLICATIONS-001`: platform/application lifecycle boundaries and application namespace topology; implementation must remain platform-side and adopter-nonspecific.
- `DCL-PLATFORM-APPLICATION-NON-SPECIFICITY-001`: guard by subject token/state, not by hardcoded application names.
- `DCL-PROJECT-AUTHORIZATION-ENVELOPE-001`: implementation remains inside the active append-only project authorization envelope and snapshot-bound WI set.
- `GOV-FILE-BRIDGE-AUTHORITY-001`: bridge queue state remains live bridge-authority state; proposal/report workflow remains bridge-mediated.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001`: Project Authorization, Project, and Work Item metadata are included.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`: this proposal links relevant implementation specs and governance constraints.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`: implementation report must include spec-derived tests and execution evidence before VERIFIED.
- `GOV-CODE-QUALITY-BASELINE-001`: proposal carries the required code quality baseline table and implementation must verify lint/format/tests.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`, `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`, and `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`: preserve artifact boundaries and avoid unapproved formal artifact changes.

## Prior Deliberations

- `DELIB-20265586`: active owner decision authorizing snapshot-bound implementation for the 13 open project member WIs, including WI-4692.
- `DELIB-20265287`: program-level owner decision for activity-envelope disposition and autonomous dispatch; umbrella advisory lists WI-4692 as drain-then-suspend extending WI-4296.
- `DELIB-20260648`: canonical init keyword amendment: subject mandatory, role optional.
- `DELIB-20260637`: envelope model lineage makes subject part of session payload.
- `DELIB-20265226`: transcript-defined interactive role persistence; relevant because role and subject must stay separate.
- `DELIB-20265219`, `DELIB-20265220`, and `DELIB-20265227`: Agent Red/application isolation lineage; cited only to preserve platform/application lifecycle boundaries, not to mutate app files.


### Helper-suggested candidates

_No prior deliberations: <fill in reason before filing>._

## Owner Decisions / Input

No new owner input requested. The active project authorization cites DELIB-20265586 and includes WI-4692 in the snapshot-bound work-item set. This proposal avoids formal artifact mutation, application source mutation, deployment, and new work-item creation.

## Spec-Derived Verification Plan

| Spec / requirement | Derived implementation check | Test / command |
|---|---|---|
| `ADR-DISPATCH-ENVELOPE-ARCHITECTURE-001` and `DCL-SMART-POLLER-AUTO-TRIGGER-001` | Application subject prevents new dispatch fire even when actionable bridge work exists. | New cross-harness and single-harness pytest cases with application work-subject fixture and mocked spawn. |
| `SPEC-SINGLE-HARNESS-BRIDGE-DISPATCHER-001` | Single-harness dispatcher records suppression and does not call `_spawn_worker` under application subject. | `python -m pytest platform_tests/scripts/test_single_harness_bridge_dispatcher.py -q --tb=short` |
| Cross-harness trigger dispatch architecture | Cross-harness trigger records suppression and does not call `_spawn_harness` under application subject. | `python -m pytest platform_tests/scripts/test_cross_harness_bridge_trigger.py platform_tests/scripts/test_cross_harness_trigger_suppression.py -q --tb=short` |
| WI-4692 drain-then-suspend | Held leases/work-intent/in-flight items are not released or cancelled; guard blocks only new launches. | New tests assert no release/cancel path fires on suppression. |
| `SPEC-CANONICAL-INIT-KEYWORD-SYNTAX-001` and `DCL-SESSION-ROLE-RESOLUTION-001` | Subject is read from canonical work-subject state; durable role routing remains unchanged under GT-KB/default subject. | Negative-control tests with `current_subject=gtkb_infrastructure` still enter existing dispatch/dry-run paths. |
| `DCL-PLATFORM-APPLICATION-NON-SPECIFICITY-001` | Implementation uses subject token/state only and does not hardcode a specific adopter. | Code review plus targeted assertions/grep where practical. |
| `GOV-CODE-QUALITY-BASELINE-001` | Touched files are linted and format-checked. | `ruff check scripts/single_harness_bridge_dispatcher.py scripts/cross_harness_bridge_trigger.py platform_tests/scripts/test_single_harness_bridge_dispatcher.py platform_tests/scripts/test_cross_harness_bridge_trigger.py platform_tests/scripts/test_cross_harness_trigger_suppression.py platform_tests/scripts/test_dispatch_suppression_routing.py`; `ruff format --check` on the same paths. |

## Implementation Start Gate

After Loyal Opposition GO, Prime Builder will run:

`python scripts/implementation_authorization.py begin --bridge-id gtkb-wi4692-application-subject-dispatch-drain-suspend`

No protected source/test mutation will occur before that command succeeds and returns an implementation-start packet for this bridge id.

## Risk Notes

- If suppression updates `last_dispatched_signature`, retry after switching back to GT-KB infrastructure could be lost. Mitigation: store suppression separately or keep successful-dispatch signatures unchanged.
- If suppression bypasses pending exit-code processing, drain status could lag. Mitigation: retain existing pending-exit processing before suppression where present.
- If the guard uses application-specific names, it violates platform nonspecificity. Mitigation: compare only normalized subject token `application`.
- If the guard blocks manual interactive bridge work, it overreaches. Mitigation: gate only headless dispatch spawns in dispatcher substrates.

## Applicability And Clause Preflight Self-Check

- Project metadata present: Project Authorization, Project, Work Item lines are included above.
- Authorization live and scoped: the active PAUTH is active and includes WI-4692.
- Mutation classes: source and test_addition only.
- Target paths are limited to dispatcher source and platform tests.
- Formal-artifact gate: not applicable; no formal artifact mutation is proposed.
- Implementation-start gate: mandatory after GO and before mutation.
- Bridge independence: Loyal Opposition must review; Prime Builder will not self-review.
