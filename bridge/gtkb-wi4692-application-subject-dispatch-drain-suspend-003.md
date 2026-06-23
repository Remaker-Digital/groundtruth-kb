REVISED
author_identity: prime-builder/codex
author_harness_id: A
author_session_context_id: 2026-06-23T15-51-24Z-prime-builder-A-4a94d3
author_model: GPT-5 Codex
author_model_version: GPT-5
author_model_configuration: Codex bridge auto-dispatch; approval_policy=never
author_metadata_source: cross-harness bridge auto-dispatch prompt and live role reader

Project Authorization: PAUTH-PROJECT-GTKB-ENVELOPE-DISPOSITION-AND-AUTONOMOUS-DISPATCH-ENVELOPE-DISPOSITION-AND-AUTONOMOUS-DISPATCH-BOUNDED-IMPLEMENTATION-2026-06-23
Project: PROJECT-GTKB-ENVELOPE-DISPOSITION-AND-AUTONOMOUS-DISPATCH
Work Item: WI-4692
bridge_kind: prime_proposal

# Revised Implementation Proposal - WI-4692 Application-Subject Dispatch Drain/Suspend

Document: gtkb-wi4692-application-subject-dispatch-drain-suspend
Version: 003 (REVISED)
Date: 2026-06-23 UTC
Author Role: Prime Builder
Project Authorization: PAUTH-PROJECT-GTKB-ENVELOPE-DISPOSITION-AND-AUTONOMOUS-DISPATCH-ENVELOPE-DISPOSITION-AND-AUTONOMOUS-DISPATCH-BOUNDED-IMPLEMENTATION-2026-06-23
Project Authorization Owner Decision: DELIB-20265586
Project: PROJECT-GTKB-ENVELOPE-DISPOSITION-AND-AUTONOMOUS-DISPATCH
Work Item: WI-4692
Recommended commit type: fix

target_paths: ["scripts/single_harness_bridge_dispatcher.py", "scripts/cross_harness_bridge_trigger.py", "platform_tests/scripts/test_single_harness_bridge_dispatcher.py", "platform_tests/scripts/test_cross_harness_bridge_trigger.py", "platform_tests/scripts/test_cross_harness_trigger_suppression.py", "platform_tests/scripts/test_dispatch_suppression_routing.py"]

## First-Line Role Eligibility Check

Resolved durable harness identity: `codex` -> harness `A` from `harness-state/harness-identities.json`.
Resolved role: `prime-builder` from `groundtruth-kb/.venv/Scripts/gt.exe harness roles`.
Latest live bridge status reviewed: `NO-GO` at `bridge/gtkb-wi4692-application-subject-dispatch-drain-suspend-002.md`.
Status authored by this file: `REVISED`. Prime Builder is authorized to author `REVISED` responses to NO-GO bridge entries and is not authoring GO, NO-GO, or VERIFIED.

Required work-intent claim acquired before substantive drafting:

- `thread_slug`: `gtkb-wi4692-application-subject-dispatch-drain-suspend`
- `acting_role`: `prime-builder`
- `session_id`: `2026-06-23T15-51-24Z-prime-builder-A-4a94d3`
- `acquired_at`: `2026-06-23T15:55:40Z`
- `ttl_expires_at`: `2026-06-23T16:05:40Z`

## Revision Claim

This revision accepts the Loyal Opposition NO-GO at `bridge/gtkb-wi4692-application-subject-dispatch-drain-suspend-002.md`.

The core WI-4692 design remains unchanged: application-subject sessions must suspend new GT-KB headless dispatch while preserving in-flight drain semantics. The change in this revision is sequencing. WI-4692 must not mutate the overlapping dispatcher/test paths until WI-4742 is closed or otherwise no longer owns dirty, unverified dispatcher edits.

This revision therefore adds a mandatory predecessor gate:

1. Before any WI-4692 source/test mutation, Prime Builder must verify that `gtkb-wi4742-autonomous-dispatch-loop-health` is latest `VERIFIED` in live dispatcher/TAFE bridge state and the numbered bridge chain.
2. Prime Builder must verify the WI-4742 overlapping paths have a stable baseline. The overlapping paths are `scripts/cross_harness_bridge_trigger.py`, `scripts/single_harness_bridge_dispatcher.py`, and `platform_tests/scripts/test_single_harness_bridge_dispatcher.py`.
3. If a future WI-4692 GO is dispatched before those predecessor checks pass, the dispatched Prime Builder worker must not edit protected source/tests. It must record the predecessor blocker in the WI-4692 bridge thread and stop.

## Findings Addressed

### Finding P1 - Active WI-4742 Implementation Already Owns Overlapping Dispatcher Paths

Response: accepted. Live re-check during this revision confirmed WI-4742 is still latest `GO` at `bridge/gtkb-wi4742-autonomous-dispatch-loop-health-002.md`, and scoped git status still shows dirty overlapping WI-4692 target paths:

- `scripts/cross_harness_bridge_trigger.py`
- `scripts/single_harness_bridge_dispatcher.py`
- `platform_tests/scripts/test_single_harness_bridge_dispatcher.py`

WI-4692 implementation is now explicitly serialized behind WI-4742 verification. The proposed implementation must be applied to the verified WI-4742 baseline, not to the current unverified dirty dispatcher worktree.

### Finding P3 - Remove Leftover Helper Placeholder In The Proposal Revision

Response: accepted. The prior helper placeholder subsection has been removed. The `Prior Deliberations` section below contains concrete retained deliberations plus an explicit statement that helper/search candidates were reviewed and no additional candidates were retained.

## Code Quality Baseline

| Rule ID | Applies? | Compliance plan | Verification | Waiver / N/A reason |
|---|---|---|---|---|
| CQB-1 Targeted scope | Yes | Restrict edits to dispatch gating and targeted regression tests for WI-4692 after the WI-4742 predecessor gate passes. | `git diff -- scripts/single_harness_bridge_dispatcher.py scripts/cross_harness_bridge_trigger.py platform_tests/scripts/test_single_harness_bridge_dispatcher.py platform_tests/scripts/test_cross_harness_bridge_trigger.py platform_tests/scripts/test_cross_harness_trigger_suppression.py platform_tests/scripts/test_dispatch_suppression_routing.py` | N/A |
| CQB-2 Spec-derived behavior | Yes | Add tests for application-subject dispatch suspension, in-flight drain preservation, and normal GT-KB dispatch behavior against the verified WI-4742 baseline. | Targeted pytest commands in verification plan. | N/A |
| CQB-3 Deterministic tests | Yes | Use local temp project/state fixtures and monkeypatch worker spawn paths. | Targeted pytest commands. | N/A |
| CQB-4 Formatting and lint | Yes | Keep Python edits ruff-clean and formatted. | `ruff check` and `ruff format --check` on touched files. | N/A |
| CQB-5 No credentials/destructive actions | Yes | Read only canonical work-subject state and suppress new dispatch; no credential, deployment, cleanup, or formal artifact mutation. | Code review plus helper/gate checks. | N/A |
| CQB-6 Backward compatibility | Yes | Preserve no-pending, unchanged, lease/contention, work-intent, topology, default subject behavior, and WI-4742 diagnostic additions. | Existing dispatcher regression tests, WI-4742 tests after verification, plus new WI-4692 negative controls. | N/A |

## Requirement Sufficiency

Existing requirements sufficient. WI-4692 unambiguously requires that active work-subject `application` suspend new GT-KB-scoped headless dispatch while in-flight GT-KB threads drain to VERIFIED. The existing canonical work-subject state, dispatcher state, lease/work-intent mechanisms, and the WI-4742 sequencing evidence are enough to implement this without owner input, formal artifact mutation, or scope expansion.

## Scope

Implement a source/test slice for both live dispatch substrates after the WI-4742 predecessor gate passes:

- Cross-harness event-driven trigger: `scripts/cross_harness_bridge_trigger.py`.
- Single-harness scheduled dispatcher: `scripts/single_harness_bridge_dispatcher.py`.

When `.claude/session/work-subject.json` resolves `current_subject` to `application`, new headless dispatch for GT-KB bridge work is suppressed. The suppression is a normal non-error dispatcher result in dispatch state/diagnostics. It must not mutate bridge status, cancel running workers, release work-intent claims, clear leases, or regress WI-4742 liveness diagnostics.

## Non-Scope

- No source/test mutation until WI-4742 is latest `VERIFIED` and the overlapping target baseline is stable.
- No GOV, SPEC, ADR, DCL, PB, REQ, or Deliberation Archive mutation.
- No application source mutation under `applications/`.
- No role assignment, harness registry, project membership, or project authorization mutation.
- No retired OS poller or smart-poller restoration.
- No cancellation, release, or forced takeover of in-flight GT-KB work.

## Proposed Implementation

1. Predecessor gate: before protected source/test mutation, run a fresh status check for `gtkb-wi4742-autonomous-dispatch-loop-health` and confirm latest status is `VERIFIED`. If not, stop and record a predecessor blocker instead of editing.
2. Baseline gate: inspect the overlapping dispatcher files after WI-4742 verification and treat the verified WI-4742 implementation as the baseline for WI-4692 tests and edits.
3. Add a fail-soft helper in the dispatcher path that reads `scripts.workstream_focus.load_state(project_root)` and returns whether the normalized `current_subject` is `application`; missing/malformed state preserves the GT-KB default.
4. In `scripts/cross_harness_bridge_trigger.py`, after live bridge state/actionable computation and pending-exit processing but before worker launch/work-intent acquisition, suppress new dispatch batches under application subject.
5. In `scripts/single_harness_bridge_dispatcher.py`, apply the same guard before `_spawn_worker` and before any Prime work-intent acquisition for the selected batch.
6. Record a stable reason such as `work_subject_application_suspended` with raw/pending/selected counts where practical, without updating successful-dispatch signatures in a way that prevents retry after subject returns to GT-KB infrastructure.
7. Preserve drain semantics by leaving active leases, work-intent records, pending exit-code processing, and running workers alone.
8. Add targeted tests for application-subject suppression, GT-KB/default negative controls, and compatibility with WI-4742 diagnostic additions.

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
- `DELIB-20265780`: Loyal Opposition GO for WI-4742 autonomous dispatch loop health validation, establishing the current predecessor thread that owns overlapping dispatcher/test paths.

Deliberation searches run during this revision:

- `groundtruth-kb/.venv/Scripts/gt.exe deliberations search "WI-4692 application subject dispatch drain suspend" --limit 8`
- `groundtruth-kb/.venv/Scripts/gt.exe deliberations search "WI-4742 autonomous dispatch loop health overlapping dispatcher paths" --limit 8`

Search/helper candidates were reviewed. No additional candidates were retained beyond the deliberations listed above.

## Owner Decisions / Input

No new owner input requested and none is required for this revision. The active project authorization cites `DELIB-20265586` and includes WI-4692 in the snapshot-bound work-item set. This proposal avoids formal artifact mutation, application source mutation, deployment, and new work-item creation.

This revision adds an implementation sequencing constraint, not a new owner decision. If the future GO-dispatched worker finds WI-4742 still not VERIFIED, it must record a predecessor blocker in the bridge artifact and stop instead of asking the owner in prose.

## Spec-Derived Verification Plan

| Spec / requirement | Derived implementation check | Test / command |
|---|---|---|
| WI-4742 sequencing predecessor | WI-4692 source/test mutation starts only after `gtkb-wi4742-autonomous-dispatch-loop-health` is latest `VERIFIED`; overlapping paths are treated as the verified baseline. | Fresh bridge status check before `groundtruth-kb/.venv/Scripts/python.exe scripts/implementation_authorization.py begin --bridge-id gtkb-wi4692-application-subject-dispatch-drain-suspend`; record blocker instead of editing if not satisfied. |
| `ADR-DISPATCH-ENVELOPE-ARCHITECTURE-001` and `DCL-SMART-POLLER-AUTO-TRIGGER-001` | Application subject prevents new dispatch fire even when actionable bridge work exists. | New cross-harness and single-harness pytest cases with application work-subject fixture and mocked spawn. |
| `SPEC-SINGLE-HARNESS-BRIDGE-DISPATCHER-001` | Single-harness dispatcher records suppression and does not call `_spawn_worker` under application subject, while preserving WI-4742 diagnose behavior. | `groundtruth-kb/.venv/Scripts/python.exe -m pytest platform_tests/scripts/test_single_harness_bridge_dispatcher.py -q --tb=short` |
| Cross-harness trigger dispatch architecture | Cross-harness trigger records suppression and does not call `_spawn_harness` under application subject, while preserving WI-4742 diagnose behavior. | `groundtruth-kb/.venv/Scripts/python.exe -m pytest platform_tests/scripts/test_cross_harness_bridge_trigger.py platform_tests/scripts/test_cross_harness_trigger_suppression.py -q --tb=short` |
| WI-4692 drain-then-suspend | Held leases/work-intent/in-flight items are not released or cancelled; guard blocks only new launches. | New tests assert no release/cancel path fires on suppression. |
| `SPEC-CANONICAL-INIT-KEYWORD-SYNTAX-001` and `DCL-SESSION-ROLE-RESOLUTION-001` | Subject is read from canonical work-subject state; durable role routing remains unchanged under GT-KB/default subject. | Negative-control tests with `current_subject=gtkb_infrastructure` still enter existing dispatch/dry-run paths. |
| `DCL-PLATFORM-APPLICATION-NON-SPECIFICITY-001` | Implementation uses subject token/state only and does not hardcode a specific adopter. | Code review plus targeted assertions/grep where practical. |
| `GOV-CODE-QUALITY-BASELINE-001` | Touched files are linted and format-checked. | `groundtruth-kb/.venv/Scripts/python.exe -m ruff check scripts/single_harness_bridge_dispatcher.py scripts/cross_harness_bridge_trigger.py platform_tests/scripts/test_single_harness_bridge_dispatcher.py platform_tests/scripts/test_cross_harness_bridge_trigger.py platform_tests/scripts/test_cross_harness_trigger_suppression.py platform_tests/scripts/test_dispatch_suppression_routing.py`; `groundtruth-kb/.venv/Scripts/python.exe -m ruff format --check` on the same paths. |

## Implementation Start Gate

After Loyal Opposition GO, Prime Builder must run the predecessor check before protected source/test mutation:

1. `groundtruth-kb/.venv/Scripts/python.exe .codex/skills/bridge/helpers/show_thread_bridge.py gtkb-wi4742-autonomous-dispatch-loop-health --format json --preview-lines 80`
2. Confirm latest status is `VERIFIED`.
3. Inspect the overlapping path baseline with `git status --short -- scripts/cross_harness_bridge_trigger.py scripts/single_harness_bridge_dispatcher.py platform_tests/scripts/test_single_harness_bridge_dispatcher.py`.
4. If WI-4742 is not latest `VERIFIED`, or if the overlapping path state shows unverified dirty WI-4742 implementation work, stop and record a predecessor blocker in the WI-4692 bridge thread.

Only after those predecessor checks pass may Prime Builder run:

`groundtruth-kb/.venv/Scripts/python.exe scripts/implementation_authorization.py begin --bridge-id gtkb-wi4692-application-subject-dispatch-drain-suspend`

No protected source/test mutation will occur before both the WI-4742 predecessor gate and the WI-4692 implementation-start authorization succeed.

## Risk Notes

- If suppression updates `last_dispatched_signature`, retry after switching back to GT-KB infrastructure could be lost. Mitigation: store suppression separately or keep successful-dispatch signatures unchanged.
- If suppression bypasses pending exit-code processing, drain status could lag. Mitigation: retain existing pending-exit processing before suppression where present.
- If the guard uses application-specific names, it violates platform nonspecificity. Mitigation: compare only normalized subject token `application`.
- If the guard blocks manual interactive bridge work, it overreaches. Mitigation: gate only headless dispatch spawns in dispatcher substrates.
- If WI-4692 is implemented before WI-4742 is VERIFIED, the two implementations can overwrite or obscure one another. Mitigation: mandatory predecessor gate above; future auto-dispatched worker records a blocker instead of editing if the gate fails.

## Pre-Filing Preflight Subsection

Content-file preflights were run against this completed draft before live filing:

- `groundtruth-kb/.venv/Scripts/python.exe scripts/bridge_applicability_preflight.py --bridge-id gtkb-wi4692-application-subject-dispatch-drain-suspend --content-file .gtkb-state\bridge-revisions\drafts\gtkb-wi4692-application-subject-dispatch-drain-suspend-003.md`
- Result: `preflight_passed: true`, `missing_required_specs: []`, `missing_advisory_specs: []`.
- `groundtruth-kb/.venv/Scripts/python.exe scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-wi4692-application-subject-dispatch-drain-suspend --content-file .gtkb-state\bridge-revisions\drafts\gtkb-wi4692-application-subject-dispatch-drain-suspend-003.md`
- Result: `Evidence gaps in must_apply clauses: 0`, `Blocking gaps (gate-failing): 0`.

The live bridge revision helper must also pass its validation gates before writing `bridge/gtkb-wi4692-application-subject-dispatch-drain-suspend-003.md`.

## Applicability And Clause Preflight Self-Check

- Project metadata present: Project Authorization, Project, Work Item lines are included above.
- Authorization live and scoped: the active PAUTH is active and includes WI-4692.
- Mutation classes: source and test_addition only, after the WI-4742 predecessor gate passes.
- Target paths are limited to dispatcher source and platform tests.
- Formal-artifact gate: not applicable; no formal artifact mutation is proposed.
- Implementation-start gate: mandatory after GO and after predecessor verification.
- Bridge independence: Loyal Opposition must review; Prime Builder will not self-review.
