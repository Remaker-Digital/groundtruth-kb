NEW

# WI-4684 Slice 2 Implementation Report: Activity Disposition Profile `::open` Injection

bridge_kind: implementation_report
Document: gtkb-wi4684-disposition-profile-open-injection
Version: 003 (NEW; post-implementation report)
Author: Prime Builder (Codex, harness A)
Date: 2026-06-23 UTC
Responds to GO: bridge/gtkb-wi4684-disposition-profile-open-injection-002.md
Approved proposal: bridge/gtkb-wi4684-disposition-profile-open-injection-001.md
Recommended commit type: feat
author_identity: prime-builder/codex
author_harness_id: A
author_session_context_id: 2026-06-23T05-59-07Z-prime-builder-A-706c9b
author_model: GPT-5 Codex
author_model_version: gpt-5-codex
author_model_configuration: Codex auto-dispatch; durable Prime Builder role; workspace E:\GT-KB

## Implementation Claim

Implemented the approved WI-4684 Slice 2 runtime wiring. The shared topic-envelope renderer now appends an open-only `Activity Disposition Profile` section for accepted `::open <activity>` commands by reading the verified `groundtruth_kb.activity.profiles.load_activity_profiles` loader from Slice 1.

The profile section renders the four DCL payload classes in a compact deterministic form: skills, terminology, history_state sources, and direction fields (stance, guardrails, manipulates), plus the `headless_eligibility` token. Loader failures are fail-soft: the accepted command context still renders and includes a profile-unavailable note.

This implementation did not edit profile config, hook registrations, MemBase, formal artifacts, Agent Red, WI-4683 parser/runtime vocabulary, WI-4685 single-active behavior, or A5 soft-reminder-gate behavior.

## Implementation Authorization Evidence

Before protected source/test mutation, Prime Builder acquired the work-intent claim and implementation-start authorization packet.

Commands:

```text
groundtruth-kb/.venv/Scripts/python.exe scripts/implementation_authorization.py begin --bridge-id gtkb-wi4684-disposition-profile-open-injection
groundtruth-kb/.venv/Scripts/python.exe scripts/bridge_claim_cli.py claim gtkb-wi4684-disposition-profile-open-injection
```

Observed authorization evidence:

- latest status: `GO`
- proposal file: `bridge/gtkb-wi4684-disposition-profile-open-injection-001.md`
- GO file: `bridge/gtkb-wi4684-disposition-profile-open-injection-002.md`
- packet hash: `sha256:3f0079b114fb203fda8fa5c548f0e3267463a29bae3bcee1954557d4d0ee8504`
- target path globs:
  - `groundtruth-kb/src/groundtruth_kb/session/topic_router.py`
  - `platform_tests/scripts/test_session_envelope_runtime.py`
  - `platform_tests/scripts/test_session_wrapup_trigger_dispatch.py`
- work-intent claim row: `21637`
- work-intent claim session: `2026-06-23T05-59-07Z-prime-builder-A-706c9b`

## Specification Links

- `DCL-ACTIVITY-DISPOSITION-PROFILE-001`
- `ADR-ACTIVITY-ENVELOPE-DISPOSITION-001`
- `ADR-CODEX-HOOK-PARITY-FALLBACK-001`
- `DCL-TOPIC-ENVELOPE-ROUTING-001`
- `SPEC-TOPIC-ENVELOPE-ROUTER-001`
- `DCL-SESSION-ENVELOPE-DURABILITY-001`
- `ADR-ENVELOPE-META-MODEL-001`
- `DCL-ENVELOPE-META-MODEL-001`
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001`
- `GOV-FILE-BRIDGE-AUTHORITY-001`
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001`
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`
- `GOV-STANDING-BACKLOG-001`
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001`
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`

## Owner Decisions / Input

No new owner decision was required. This implementation carries forward the owner decisions and bounded project authorization cited by the approved proposal: `DELIB-20260621-EXPLICIT-HINT-CONTEXT-LOAD-REFRAME`, `DELIB-20265287`, `DELIB-20260637`, and `DELIB-20265586`.

## Prior Deliberations

- `DELIB-20260621-EXPLICIT-HINT-CONTEXT-LOAD-REFRAME` - four-class activity profile and `::open` injection model.
- `DELIB-20265287` - named disposition profiles, per-activity headless eligibility, and profile-as-`intent_hint` enrichment.
- `DELIB-20260637` - envelope meta-model lineage: invocation + intent_hint + payload.
- `DELIB-20265586` - bounded PAUTH batch including WI-4684.
- `bridge/gtkb-wi4684-disposition-profiles-slice1-006.md` - VERIFIED profile config and loader for A1-A3.
- `bridge/gtkb-wi4683-router-runtime-six-member-vocabulary-001.md` - adjacent parser/runtime vocabulary work; not implemented or claimed here.
- `bridge/gtkb-wi4684-disposition-profile-open-injection-001.md` - approved Slice 2 implementation proposal.
- `bridge/gtkb-wi4684-disposition-profile-open-injection-002.md` - Loyal Opposition GO verdict.

## Specification-Derived Verification Plan

| Spec / governing surface | Executed verification evidence |
| --- | --- |
| `DCL-ACTIVITY-DISPOSITION-PROFILE-001` A4 and `ADR-ACTIVITY-ENVELOPE-DISPOSITION-001` | `test_render_topic_context_injects_activity_profile_for_open` verifies accepted `::open build` context includes the profile heading, `headless_eligibility`, skills, terminology, history_state, and direction content. |
| Open-only injection boundary from the approved proposal | `test_render_topic_context_does_not_inject_profile_for_close` verifies accepted `::close build` context does not include the profile block. |
| Fail-soft loader behavior from the approved proposal | `test_render_topic_context_profile_loader_failure_is_non_blocking` monkeypatches the loader to fail and verifies the accepted command context still renders with an unavailable note. |
| `ADR-CODEX-HOOK-PARITY-FALLBACK-001` | `test_hook_render_topic_context_includes_activity_profile` verifies the Codex UserPromptSubmit hook-imported shared renderer includes the profile block. |
| `DCL-TOPIC-ENVELOPE-ROUTING-001` and `SPEC-TOPIC-ENVELOPE-ROUTER-001` | Existing strict parser/runtime tests in `test_session_envelope_runtime.py` and `test_session_wrapup_trigger_dispatch.py` were rerun and still pass. |
| `DCL-SESSION-ENVELOPE-DURABILITY-001`, `ADR-ENVELOPE-META-MODEL-001`, and `DCL-ENVELOPE-META-MODEL-001` | The implementation only enriches rendered context from the accepted topic event. It does not mutate session-envelope persistence schema or add a new envelope leg. |
| `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` and `GOV-FILE-BRIDGE-AUTHORITY-001` | Implementation authorization and work-intent claim evidence above show the mutation was scoped to the latest GO and approved target paths. |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`, `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001`, and `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | This report carries forward linked specs, project/work/PAUTH evidence from the approved proposal, exact executed command evidence, and spec-to-test mapping. |
| `GOV-STANDING-BACKLOG-001`, `ADR-ISOLATION-APPLICATION-PLACEMENT-001`, `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`, `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`, and `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | Changed paths remain in-root, match the approved target paths, preserve the slice boundary, and leave A5/WI-4683/WI-4685 out of scope. |

## Commands Run

```text
groundtruth-kb/.venv/Scripts/python.exe -m pytest platform_tests/scripts/test_session_envelope_runtime.py platform_tests/scripts/test_session_wrapup_trigger_dispatch.py -q --tb=short --basetemp .gtkb-state/pytest-wi4684-open-profile
groundtruth-kb/.venv/Scripts/python.exe -m ruff check groundtruth-kb/src/groundtruth_kb/session/topic_router.py platform_tests/scripts/test_session_envelope_runtime.py platform_tests/scripts/test_session_wrapup_trigger_dispatch.py
groundtruth-kb/.venv/Scripts/python.exe -m ruff format --check groundtruth-kb/src/groundtruth_kb/session/topic_router.py platform_tests/scripts/test_session_envelope_runtime.py platform_tests/scripts/test_session_wrapup_trigger_dispatch.py
groundtruth-kb/.venv/Scripts/python.exe scripts/bridge_applicability_preflight.py --bridge-id gtkb-wi4684-disposition-profile-open-injection
groundtruth-kb/.venv/Scripts/python.exe scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-wi4684-disposition-profile-open-injection
```

## Observed Results

- Pytest: `13 passed, 2 warnings in 0.99s`.
- Pytest warnings were pre-existing environment/cache noise: unknown `asyncio_mode` config option and `.pytest_cache` cache creation warning.
- Ruff lint: `All checks passed!`
- Ruff format: `3 files already formatted`.
- Applicability preflight: `preflight_passed: true`, `missing_required_specs: []`, `missing_advisory_specs: []`, packet hash `sha256:2c1ef8429f076a48afb2ccfa43300d488e034c68a50b193eb83610d0bb2cd1b4`.
- Clause preflight: exit 0, 5 clauses evaluated, 0 evidence gaps in `must_apply`, 0 blocking gaps.

## Files Changed

Implementation-scope changed files:

- `groundtruth-kb/src/groundtruth_kb/session/topic_router.py`
- `platform_tests/scripts/test_session_envelope_runtime.py`
- `platform_tests/scripts/test_session_wrapup_trigger_dispatch.py`

Diff stat for implementation-scope changed files:

```text
 groundtruth-kb/src/groundtruth_kb/session/topic_router.py     | 78 +++++++++++++++++++++-
 platform_tests/scripts/test_session_envelope_runtime.py       | 60 ++++++++++++++++-
 platform_tests/scripts/test_session_wrapup_trigger_dispatch.py | 17 +++++
 3 files changed, 152 insertions(+), 3 deletions(-)
```

The worktree contained unrelated pre-existing dirty files outside this GO's target paths. They were not edited for this implementation report and are not part of this verification request.

## Recommended Commit Type

- Recommended commit type: `feat`
- Justification: the implementation adds a new runtime context-injection capability to the topic-envelope renderer and verifies Codex hook parity.

## Acceptance Criteria Status

- Accepted `::open build` context injects the activity disposition profile: complete.
- Accepted `::close build` context does not inject the open-only profile block: complete.
- Profile loader failures are non-blocking and produce a clear unavailable note: complete.
- Codex UserPromptSubmit hook path receives the shared profile-enriched renderer: complete.
- Strict router command parsing remains unchanged: complete.
- WI-4683 parser vocabulary, WI-4685 single-active invariant, and A5 soft-reminder-gate behavior are not claimed: preserved out of scope.

## Risk And Rollback

Residual risk is limited to context verbosity because this change affects rendered prompt context, not command acceptance or persisted envelope schema. The rendered profile remains deterministic and compact enough for direct test assertions.

Rollback is a single git revert of the three implementation-scope files plus the bridge implementation report. No config, MemBase, formal artifact, hook registration, Agent Red, or profile-content rollback is required.

## Loyal Opposition Asks

1. Verify the implementation against the linked specifications and executed command evidence.
2. Return `VERIFIED` if the report and implementation satisfy the approved proposal, otherwise return `NO-GO` with findings.

Copyright (c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
