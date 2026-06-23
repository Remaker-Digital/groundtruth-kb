NEW

# WI-4684 Slice 2: Inject Activity Disposition Profiles on ::open

bridge_kind: prime_proposal
Document: gtkb-wi4684-disposition-profile-open-injection
Version: 001
Author: Prime Builder (Codex, harness A)
Date: 2026-06-23 UTC

author_identity: prime-builder/codex
author_harness_id: A
author_session_context_id: 019ef0d4-5474-7af3-af31-4c8ab4cf4f7a
author_model: GPT-5 Codex
author_model_version: gpt-5-codex
author_model_configuration: Codex Desktop interactive Prime Builder; owner init ::init gtkb pb

Project Authorization: PAUTH-PROJECT-GTKB-ENVELOPE-DISPOSITION-AND-AUTONOMOUS-DISPATCH-ENVELOPE-DISPOSITION-AND-AUTONOMOUS-DISPATCH-BOUNDED-IMPLEMENTATION-2026-06-23
Project: PROJECT-GTKB-ENVELOPE-DISPOSITION-AND-AUTONOMOUS-DISPATCH
Work Item: WI-4684

target_paths: ["groundtruth-kb/src/groundtruth_kb/session/topic_router.py", "platform_tests/scripts/test_session_envelope_runtime.py", "platform_tests/scripts/test_session_wrapup_trigger_dispatch.py"]

implementation_scope: source,test_addition
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

---

## Summary

This is WI-4684 Slice 2. Slice 1 is already VERIFIED in
`bridge/gtkb-wi4684-disposition-profiles-slice1-006.md`: it added the
schema-versioned activity disposition profile config, the read-only loader, and
tests for `DCL-ACTIVITY-DISPOSITION-PROFILE-001` assertions A1-A3. This proposal
wires that verified loader into the shared `::open <activity>` topic-envelope
renderer so the existing UserPromptSubmit hook injects the selected activity
profile as additional context when an activity is opened.

The change is intentionally narrow: only the shared router/context-rendering
source and its focused tests are in scope. It does not edit the profile config,
does not change hook registrations, does not implement the A5 soft-reminder
gate, does not implement the WI-4685 single-active invariant, and does not
change the five-to-six topic parser/runtime vocabulary already proposed under
WI-4683.

## Specification Links

- `DCL-ACTIVITY-DISPOSITION-PROFILE-001` - primary governing DCL. This slice
  targets A4: an interception surface for `::open` must inject the profile. A1-A3
  were already covered by the VERIFIED Slice 1 loader/config; A5 remains out of
  scope for a later soft-reminder-gate slice.
- `ADR-ACTIVITY-ENVELOPE-DISPOSITION-001` - architecture decision that each
  activity carries a named disposition profile injected by the harness at
  `::open <activity>`.
- `ADR-CODEX-HOOK-PARITY-FALLBACK-001` - the injection remains hook-primary
  through the existing Codex UserPromptSubmit hook, with the shared router
  source providing the agent-fallback-renderable context.
- `DCL-TOPIC-ENVELOPE-ROUTING-001` - the renderer is part of the
  topic-envelope router surface and must continue to honor the strict command
  route model.
- `SPEC-TOPIC-ENVELOPE-ROUTER-001` - topic-envelope commands remain strict and
  routed through the existing `handle_topic_command` / `render_topic_context`
  flow.
- `DCL-SESSION-ENVELOPE-DURABILITY-001` - profile injection is rendered from the
  accepted topic-envelope event without mutating the persisted envelope schema.
- `ADR-ENVELOPE-META-MODEL-001` - the profile enriches the existing
  `intent_hint` leg rather than adding a fourth envelope leg.
- `DCL-ENVELOPE-META-MODEL-001` - keeps the implementation aligned with the
  invocation + intent_hint + payload model.
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` - the cited 2026-06-23 PAUTH is
  active, includes WI-4684, and permits the proposed source/test_addition
  mutation classes.
- `GOV-FILE-BRIDGE-AUTHORITY-001` - bridge GO and implementation-start packet
  are required before any protected source/test mutation.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - this proposal cites
  the governing specs that drive the implementation and tests.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - Project, Work Item, and
  Project Authorization metadata are present above.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - verification is derived
  directly from the linked DCL/ADR requirements.
- `GOV-STANDING-BACKLOG-001` - WI-4684 is active project backlog work and remains
  open because A4/A5 were deferred from Slice 1.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - all target paths remain inside the
  GT-KB root and do not touch Agent Red application files.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` - the proposal preserves the slice
  boundary and artifact trace from DCL assertion to code/tests.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` - the change links durable
  specifications, bridge evidence, source, and tests in the artifact graph.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - A4 is a lifecycle transition from
  specified runtime behavior toward implementation while A5 remains deferred.

## Prior Deliberations

- `DELIB-20260621-EXPLICIT-HINT-CONTEXT-LOAD-REFRAME` - DEC-2 and DEC-3 define
  the four-class activity profile and `::open` injection model.
- `DELIB-20265287` - D2/D4/F2 define named versioned profiles, per-activity
  headless eligibility, and profile-as-intent_hint enrichment.
- `DELIB-20260637` - envelope meta-model refinement: invocation + intent_hint +
  payload with dispatch/session/topic containment.
- `bridge/gtkb-activity-disposition-profile-adr-dcl-002.md` - terminal GO for
  the ADR/DCL that this slice implements.
- `bridge/gtkb-wi4684-disposition-profiles-slice1-006.md` - VERIFIED Slice 1
  evidence for the profile config and loader (DCL A1-A3).
- `bridge/gtkb-wi4683-router-runtime-six-member-vocabulary-001.md` - adjacent
  WI-4683 source/test proposal for six-member parser/runtime vocabulary. This
  Slice 2 proposal deliberately does not duplicate that parser work.

## Owner Decisions / Input

No new owner decision is required. The governing owner decisions are already
recorded in `DELIB-20260621-EXPLICIT-HINT-CONTEXT-LOAD-REFRAME`,
`DELIB-20265287`, and the current bounded implementation authorization
`DELIB-20265586` / `PAUTH-PROJECT-GTKB-ENVELOPE-DISPOSITION-AND-AUTONOMOUS-DISPATCH-ENVELOPE-DISPOSITION-AND-AUTONOMOUS-DISPATCH-BOUNDED-IMPLEMENTATION-2026-06-23`.

This proposal does not request formal-artifact mutation, profile-content
refinement, or an owner choice. The owner-reserved per-activity content
refinement remains WI-4730.

## Requirement Sufficiency

Existing requirements are sufficient. `DCL-ACTIVITY-DISPOSITION-PROFILE-001`
A4 and `ADR-ACTIVITY-ENVELOPE-DISPOSITION-001` explicitly require profile
injection at `::open <activity>`. The already-VERIFIED Slice 1 loader supplies
the profile source; this slice only connects that source to the existing
hook-rendered topic context.

## Proposed Implementation

1. Update `groundtruth-kb/src/groundtruth_kb/session/topic_router.py` to load the
   activity profile for accepted `::open <activity>` commands and append a
   concise "Activity Disposition Profile" section to the existing context.
2. Render the four DCL payload classes in a compact, deterministic form:
   skills, terminology, history_state sources, and direction fields
   (stance/guardrails/manipulates), plus `headless_eligibility`.
3. Keep profile loading fail-soft in the hook-render path: if profile loading is
   unavailable or invalid, the command-accepted context still renders with a
   clear profile-unavailable note rather than blocking `::open`.
4. Update focused tests to prove:
   - open context includes the profile for an accepted activity;
   - close context does not inject the open-only profile section;
   - profile loader errors are fail-soft;
   - the Codex UserPromptSubmit hook path receives the same profile-enriched
     shared renderer.

## Out of Scope

- `DCL-ACTIVITY-DISPOSITION-PROFILE-001` A5 soft-reminder gate registration.
- WI-4685 single-active activity invariant and bare `::close` behavior.
- WI-4683 six-member parser/runtime vocabulary change; `ops` rendering will work
  automatically after WI-4683 lands, but this proposal does not edit that regex.
- Profile config edits or owner-refined per-activity profile content (WI-4730).
- Any MemBase, formal artifact, hook registration, config, or Agent Red change.

## Spec-Derived Verification Plan

| Linked requirement | Test / command | Expected result |
|---|---|---|
| `DCL-ACTIVITY-DISPOSITION-PROFILE-001` A4 and `ADR-ACTIVITY-ENVELOPE-DISPOSITION-001` open injection | `test_render_topic_context_injects_activity_profile_for_open` in `test_session_envelope_runtime.py` | rendered `::open build` context includes profile heading, `headless_eligibility`, skills, terminology, history_state, and direction content |
| Open-only injection boundary | `test_render_topic_context_does_not_inject_profile_for_close` | `::close build` context keeps existing route summary without the open-only profile block |
| Hook fail-soft behavior | `test_render_topic_context_profile_loader_failure_is_non_blocking` | loader failure renders accepted command context plus a profile-unavailable note |
| Codex UserPromptSubmit hook parity | `test_hook_render_topic_context_includes_activity_profile` in `test_session_wrapup_trigger_dispatch.py` | hook-imported shared renderer includes the disposition profile section |
| Strict router behavior remains unchanged | existing topic parser tests in both focused files | existing strict command acceptance/rejection behavior still passes |

Implementation report commands:

```text
groundtruth-kb/.venv/Scripts/python.exe -m pytest platform_tests/scripts/test_session_envelope_runtime.py platform_tests/scripts/test_session_wrapup_trigger_dispatch.py -q --tb=short --basetemp .gtkb-state/pytest-wi4684-open-profile
groundtruth-kb/.venv/Scripts/python.exe -m ruff check groundtruth-kb/src/groundtruth_kb/session/topic_router.py platform_tests/scripts/test_session_envelope_runtime.py platform_tests/scripts/test_session_wrapup_trigger_dispatch.py
groundtruth-kb/.venv/Scripts/python.exe -m ruff format --check groundtruth-kb/src/groundtruth_kb/session/topic_router.py platform_tests/scripts/test_session_envelope_runtime.py platform_tests/scripts/test_session_wrapup_trigger_dispatch.py
```

## Pre-Filing Preflight Subsection

Pre-filing preflights were run against this completed draft before filing:

```text
python scripts/bridge_applicability_preflight.py --bridge-id gtkb-wi4684-disposition-profile-open-injection --content-file .gtkb-state/propose-drafts/gtkb-wi4684-disposition-profile-open-injection-001.md --json
python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-wi4684-disposition-profile-open-injection --content-file .gtkb-state/propose-drafts/gtkb-wi4684-disposition-profile-open-injection-001.md
```

Results:

- Applicability preflight passed: `preflight_passed: true`,
  `missing_required_specs: []`, `missing_advisory_specs: []`,
  `packet_hash: sha256:90505ff678f45883a6ca51a6677c1ad5c92169fce1062da58885f2dd0d13414b`.
- Clause preflight passed: 5 clauses evaluated, 3 `must_apply`, 2 `may_apply`,
  0 `not_applicable`, 0 evidence gaps in `must_apply`, and 0 blocking gaps.
- Phantom-spec sweep passed: all 18 cited specs were found in
  `current_specifications`; `missing: []`.
- `target_paths` parsed as valid inline JSON and the draft had no remaining
  `TODO:` placeholders.

## Risk / Rollback

Risk is moderate-low. The change affects hook-rendered context, not command
acceptance or envelope persistence. The primary risk is noisy or oversized
context; the implementation will keep the rendered profile compact and covered
by focused string assertions.

Rollback is a single git revert of the source/test commit plus the associated
implementation report. No config, MemBase, or formal-artifact rollback is needed
because this proposal does not mutate those surfaces.

## Bridge Filing

This proposal is filed under `bridge/` as the first status-bearing numbered
bridge file for `gtkb-wi4684-disposition-profile-open-injection`; no prior
version is deleted or rewritten. Dispatcher/TAFE state plus the numbered file
chain are the live workflow state per `GOV-FILE-BRIDGE-AUTHORITY-001`.

## Recommended Commit Type

`feat` - adds the runtime context-injection behavior for the already-defined
activity disposition profile model.

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
