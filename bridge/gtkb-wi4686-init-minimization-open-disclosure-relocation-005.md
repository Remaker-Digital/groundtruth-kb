NEW

# WI-4686 Implementation Report: Init Minimization And Open-Disclosure Relocation

bridge_kind: implementation_report
Document: gtkb-wi4686-init-minimization-open-disclosure-relocation
Version: 005 (NEW; post-implementation report)
Author: Prime Builder (Codex, harness A)
Date: 2026-06-23 UTC
Responds to GO: bridge/gtkb-wi4686-init-minimization-open-disclosure-relocation-004.md
Approved proposal: bridge/gtkb-wi4686-init-minimization-open-disclosure-relocation-003.md
Project Authorization: PAUTH-PROJECT-GTKB-ENVELOPE-DISPOSITION-AND-AUTONOMOUS-DISPATCH-ENVELOPE-DISPOSITION-AND-AUTONOMOUS-DISPATCH-BOUNDED-IMPLEMENTATION-2026-06-23
Project: PROJECT-GTKB-ENVELOPE-DISPOSITION-AND-AUTONOMOUS-DISPATCH
Work Item: WI-4686
Recommended commit type: fix
author_identity: prime-builder/codex
author_harness_id: A
author_session_context_id: 2026-06-23T10-19-27Z-prime-builder-A-08846c
author_model: gpt-5
author_model_version: gpt-5-codex
author_model_configuration: Codex auto-dispatch; approval_policy=never; role=prime-builder; cwd=`E:/GT-KB`
author_metadata_source: bridge-auto-dispatch

target_paths: ["scripts/session_self_initialization.py", "groundtruth-kb/src/groundtruth_kb/session/topic_router.py", "platform_tests/scripts/test_session_self_initialization.py", "platform_tests/scripts/test_session_self_initialization_disclosure_shape.py", "platform_tests/scripts/test_session_envelope_runtime.py"]

## Implementation Claim

Implemented the approved WI-4686 runtime/test slice. `::init` startup disclosure is now minimized to role/routing and compact project-state context, while the operator-facing disclosure material moved to the `::open <activity>` topic-envelope path.

The implementation preserves the existing init-keyword grammar and dispatcher relay contract. It removes top-priority and focus-menu content from the cached init disclosure, adds a deterministic minimized disclosure renderer, and appends open-only operator context alongside the existing activity disposition profile when an activity is opened.

The implementation did not modify parser grammar, typed close behavior, workstream-focus selection, hook registrations, MemBase, formal GOV/SPEC/ADR/DCL artifacts, Agent Red, or unrelated bridge files. All active project files, generated draft artifacts, live bridge artifacts, source changes, and test changes for this report remain in-root under `E:/GT-KB`.

## Implementation Authorization Evidence

Before protected source/test mutation, Prime Builder acquired the work-intent claim and implementation-start authorization packet.

Commands:

```text
groundtruth-kb/.venv/Scripts/python.exe scripts/bridge_claim_cli.py claim gtkb-wi4686-init-minimization-open-disclosure-relocation
groundtruth-kb/.venv/Scripts/python.exe scripts/implementation_authorization.py begin --bridge-id gtkb-wi4686-init-minimization-open-disclosure-relocation
```

Observed authorization evidence:

- latest status at implementation start: `GO`
- proposal file: `bridge/gtkb-wi4686-init-minimization-open-disclosure-relocation-003.md`
- GO file: `bridge/gtkb-wi4686-init-minimization-open-disclosure-relocation-004.md`
- implementation-start packet hash observed during implementation: `sha256:f0a9ef2d4d760bc27c468e044d11acf0d1d184d801b6595ac47678e79ae8d04c`
- work-intent claim session at implementation start: `2026-06-23T10-19-27Z-prime-builder-A-08846c`
- report-filing claim row: `23399`
- report-filing claim session: `2026-06-23T10-19-27Z-prime-builder-A-08846c`

The first implementation claim expired before report filing while another Prime Builder claim was active. This worker waited until that claim expired, rechecked the thread as still latest `GO`, acquired a fresh claim for the same Codex session, and only then filed this report.

## Files Changed

Implementation-scope changed files:

- `scripts/session_self_initialization.py`
- `groundtruth-kb/src/groundtruth_kb/session/topic_router.py`
- `platform_tests/scripts/test_session_self_initialization.py`
- `platform_tests/scripts/test_session_self_initialization_disclosure_shape.py`
- `platform_tests/scripts/test_session_envelope_runtime.py`

Diff stat for implementation-scope changed files:

```text
 groundtruth-kb/src/groundtruth_kb/session/topic_router.py     |  82 ++-
 platform_tests/scripts/test_session_envelope_runtime.py       |  54 ++
 platform_tests/scripts/test_session_self_initialization.py    |  31 +-
 platform_tests/scripts/test_session_self_initialization_disclosure_shape.py | 687 +++++++++++----------
 scripts/session_self_initialization.py                         |  59 +-
 5 files changed, 561 insertions(+), 352 deletions(-)
```

The disclosure-shape test file changed mostly because a line-ending normalization was required to clear `git diff --check` trailing-whitespace failures after the targeted assertion updates.

The worktree contained unrelated pre-existing dirty files outside this GO's implementation-scope paths. They were not edited for this implementation report and are not part of this verification request. The bridge helper's raw changed-file discovery listed those unrelated paths because the worktree was already dirty.

## Specification Links

- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001`
- `GOV-FILE-BRIDGE-AUTHORITY-001`
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001`
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001`
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`
- `SPEC-CANONICAL-INIT-KEYWORD-SYNTAX-001` v3
- `DCL-INIT-KEYWORD-CONSISTENT-ASSERTION-001` v3
- `DCL-INIT-KEYWORD-STARTUP-DISCLOSURE-RELAY-001`
- `DCL-SESSION-ROLE-RESOLUTION-001` v3
- `SPEC-ENVELOPE-DISCLOSURE-UI-001`
- `DCL-ACTIVITY-DISPOSITION-PROFILE-001`
- `DCL-TOPIC-ENVELOPE-ROUTING-001` v2
- `ADR-CODEX-HOOK-PARITY-FALLBACK-001`

## Owner Decisions / Input

No new owner decision was required. This implementation carries forward the owner decisions and bounded project authorization cited by the approved proposal:

- `DELIB-20265586` - owner authorized the snapshot-bound 13-WI project implementation PAUTH for this project, including `WI-4686`.
- `DELIB-20265287` - owner supplied the activity-disposition and headless-eligibility direction this slice operationalizes.
- `DELIB-20260636` - envelope-program grilling and open/close disclosure design context.
- `DELIB-20260648` - init-keyword optionality and subject/role handling.

## Prior Deliberations And Bridge Evidence

- `bridge/gtkb-wi4686-init-minimization-open-disclosure-relocation-003.md` - approved revised implementation proposal.
- `bridge/gtkb-wi4686-init-minimization-open-disclosure-relocation-004.md` - Loyal Opposition GO verdict.
- `bridge/gtkb-envelope-disclosure-ui-impl-011.md` / `bridge/gtkb-envelope-disclosure-ui-impl-012.md` - prior verified envelope disclosure UI implementation and verification evidence.
- `bridge/gtkb-envelope-init-keyword-amendment-slice-1-011.md` / `bridge/gtkb-envelope-init-keyword-amendment-slice-1-012.md` - prior verified init-keyword amendment evidence.
- `bridge/gtkb-wi4684-disposition-profile-open-injection-003.md` / `bridge/gtkb-wi4684-disposition-profile-open-injection-004.md` - verified activity-disposition profile open-injection runtime work that this slice builds on.

## Specification-Derived Verification Plan

| Spec / governing surface | Executed verification evidence |
| --- | --- |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | This report and the implementation declaration explicitly state that active and generated files remain in-root under `E:/GT-KB`; `git diff --check -- <implementation paths>` exited 0. |
| `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` and `GOV-FILE-BRIDGE-AUTHORITY-001` | Work was performed against latest `GO` after a work-intent claim and implementation-start authorization; report filing waited for a conflicting Prime Builder claim to expire before reacquiring the claim. |
| `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001`, `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`, and `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | This report carries forward project/work/PAUTH metadata, linked specs from the approved proposal, exact command evidence, observed results, and this spec-to-test mapping. |
| `SPEC-CANONICAL-INIT-KEYWORD-SYNTAX-001` | The broad spec-mapped pytest suite included `test_canonical_init_keyword_syntax.py` and `test_session_init_keyword_matching.py`; grammar remained unchanged. |
| `DCL-INIT-KEYWORD-CONSISTENT-ASSERTION-001` | The broad spec-mapped pytest suite included canonical assertion and both Codex/Claude dispatcher tests; strict-drop, subject-only, and role-token behavior stayed intact. |
| `DCL-INIT-KEYWORD-STARTUP-DISCLOSURE-RELAY-001` | Focused startup tests verify `_startup_disclosure` still exists as the relay surface, now minimized, and the dispatcher tests in the broad suite still pass. |
| `DCL-SESSION-ROLE-RESOLUTION-001` | The broad spec-mapped pytest suite included `test_session_role_resolution.py` and `test_session_role_resolution_table.py`; role-resolution semantics survived the disclosure refactor. |
| `SPEC-ENVELOPE-DISCLOSURE-UI-001` | `test_init_disclosure_is_minimized_for_routing_only` and updated startup-service assertions verify the init disclosure is bounded and omits the top-priority/operator surfaces. Existing open disclosure tests still verify the operator-facing top-priority surface remains available in the open disclosure path. |
| `DCL-ACTIVITY-DISPOSITION-PROFILE-001` | `test_render_topic_context_injects_activity_profile_for_open` still verifies open-only activity profile injection, now alongside open operator context. |
| `DCL-TOPIC-ENVELOPE-ROUTING-001` | `test_render_topic_context_injects_operator_context_for_open` verifies `::open` receives operator context without changing route vocabulary; close-path assertions verify no open-only sections are injected for `::close`. |
| `ADR-CODEX-HOOK-PARITY-FALLBACK-001` | The broad suite reran both Codex and Claude session-start dispatcher tests; hook wrappers were not changed. |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`, `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`, and `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | The implementation preserves traceability through proposal, GO, source/test changes, this report, owner-decision carry-forward, and no out-of-scope formal artifact mutation. |

## Commands Run

Focused behavior regression:

```text
Remove-Item Env:GTKB_BRIDGE_POLLER_RUN_ID -ErrorAction SilentlyContinue; Remove-Item Env:GTKB_BRIDGE_DISPATCH_KEYWORD -ErrorAction SilentlyContinue; $env:TMP='E:\GT-KB\.codex-pytest-tmp-wi4686-focused2-env'; $env:TEMP='E:\GT-KB\.codex-pytest-tmp-wi4686-focused2-env'; groundtruth-kb\.venv\Scripts\python.exe -m pytest platform_tests/scripts/test_session_self_initialization.py::test_startup_report_treats_first_owner_message_as_session_start_stimulus platform_tests/scripts/test_session_self_initialization.py::test_emit_startup_service_payload_returns_full_codex_session_start_contract platform_tests/scripts/test_session_self_initialization_disclosure_shape.py::test_init_disclosure_is_minimized_for_routing_only platform_tests/scripts/test_session_envelope_runtime.py::test_render_topic_context_injects_activity_profile_for_open platform_tests/scripts/test_session_envelope_runtime.py::test_render_topic_context_injects_operator_context_for_open -q --tb=short --basetemp .codex-pytest-tmp-wi4686-focused2
```

Broad spec-mapped suite:

```text
New-Item -ItemType Directory -Force -Path '.codex-pytest-tmp-wi4686-env-existing' | Out-Null; Remove-Item Env:GTKB_BRIDGE_POLLER_RUN_ID -ErrorAction SilentlyContinue; Remove-Item Env:GTKB_BRIDGE_DISPATCH_KEYWORD -ErrorAction SilentlyContinue; $env:TMP='E:\GT-KB\.codex-pytest-tmp-wi4686-env-existing'; $env:TEMP='E:\GT-KB\.codex-pytest-tmp-wi4686-env-existing'; groundtruth-kb\.venv\Scripts\python.exe -m pytest platform_tests/scripts/test_canonical_init_keyword_syntax.py platform_tests/scripts/test_session_init_keyword_matching.py platform_tests/scripts/test_canonical_init_keyword_assertions.py platform_tests/scripts/test_codex_session_start_dispatcher.py platform_tests/scripts/test_claude_session_start_dispatcher.py platform_tests/scripts/test_session_self_initialization_spec_citation_existence.py platform_tests/scripts/test_session_self_initialization.py platform_tests/scripts/test_session_role_resolution.py platform_tests/scripts/test_session_role_resolution_table.py platform_tests/scripts/test_session_self_initialization_disclosure_shape.py platform_tests/scripts/test_startup_focus_role_awareness.py platform_tests/scripts/test_activity_disposition_profiles.py platform_tests/scripts/test_session_envelope_runtime.py platform_tests/scripts/test_session_wrapup_trigger_dispatch.py -q --tb=short --timeout=180 --basetemp .codex-pytest-tmp-wi4686-suite3 -k "not test_harness_role_assignment_map_is_startup_source_of_truth"
```

Full session-self-initialization file:

```text
New-Item -ItemType Directory -Force -Path '.codex-pytest-tmp-wi4686-env-existing' | Out-Null; Remove-Item Env:GTKB_BRIDGE_POLLER_RUN_ID -ErrorAction SilentlyContinue; Remove-Item Env:GTKB_BRIDGE_DISPATCH_KEYWORD -ErrorAction SilentlyContinue; $env:TMP='E:\GT-KB\.codex-pytest-tmp-wi4686-env-existing'; $env:TEMP='E:\GT-KB\.codex-pytest-tmp-wi4686-env-existing'; groundtruth-kb\.venv\Scripts\python.exe -m pytest platform_tests/scripts/test_session_self_initialization.py -q --tb=short --timeout=180 --basetemp .codex-pytest-tmp-wi4686-selfinit2
```

Code-quality gates:

```text
groundtruth-kb\.venv\Scripts\python.exe -m ruff check scripts/session_self_initialization.py groundtruth-kb/src/groundtruth_kb/session/topic_router.py platform_tests/scripts/test_session_self_initialization.py platform_tests/scripts/test_session_self_initialization_disclosure_shape.py platform_tests/scripts/test_session_envelope_runtime.py
groundtruth-kb\.venv\Scripts\python.exe -m ruff format --check scripts/session_self_initialization.py groundtruth-kb/src/groundtruth_kb/session/topic_router.py platform_tests/scripts/test_session_self_initialization.py platform_tests/scripts/test_session_self_initialization_disclosure_shape.py platform_tests/scripts/test_session_envelope_runtime.py
git diff --check -- scripts/session_self_initialization.py groundtruth-kb/src/groundtruth_kb/session/topic_router.py platform_tests/scripts/test_session_self_initialization.py platform_tests/scripts/test_session_self_initialization_disclosure_shape.py platform_tests/scripts/test_session_envelope_runtime.py
```

Bridge/thread and claim checks before report filing:

```text
groundtruth-kb\.venv\Scripts\python.exe .codex\skills\bridge\helpers\show_thread_bridge.py gtkb-wi4686-init-minimization-open-disclosure-relocation --format json --preview-lines 120
groundtruth-kb\.venv\Scripts\python.exe scripts\bridge_claim_cli.py status gtkb-wi4686-init-minimization-open-disclosure-relocation
groundtruth-kb\.venv\Scripts\python.exe scripts\bridge_claim_cli.py claim gtkb-wi4686-init-minimization-open-disclosure-relocation --session-id 2026-06-23T10-19-27Z-prime-builder-A-08846c --ttl-seconds 2400
```

Report preflight gates:

```text
groundtruth-kb\.venv\Scripts\python.exe scripts\bridge_applicability_preflight.py --bridge-id gtkb-wi4686-init-minimization-open-disclosure-relocation --content-file .gtkb-state\bridge-impl-reports\drafts\gtkb-wi4686-init-minimization-open-disclosure-relocation-005.md --json
groundtruth-kb\.venv\Scripts\python.exe scripts\adr_dcl_clause_preflight.py --bridge-id gtkb-wi4686-init-minimization-open-disclosure-relocation --content-file .gtkb-state\bridge-impl-reports\drafts\gtkb-wi4686-init-minimization-open-disclosure-relocation-005.md
```

## Observed Results

- Focused behavior regression: `5 passed, 2 warnings`.
- Broad spec-mapped suite: `317 passed, 1 deselected, 2 warnings in 11m14s`.
- Full `test_session_self_initialization.py`: `75 passed, 1 failed, 3 warnings`.
- The one full-file failure is an unrelated baseline/spec drift in `test_harness_role_assignment_map_is_startup_source_of_truth`: the test seeds retired `harness-state/role-assignments.json` behavior through `GTKB_ROLE_ASSIGNMENTS_PATH`, while current `scripts/harness_roles.py:load_role_assignments` intentionally uses the canonical `harness-state/harness-registry.json`/projection path and ignores the legacy assignment path. This failure was not introduced by the WI-4686 disclosure relocation changes and is isolated by the broad suite deselection.
- Ruff lint: `All checks passed!`
- Ruff format: `5 files already formatted`
- `git diff --check -- <implementation paths>`: exit `0`
- Pytest warnings were existing environment/cache noise: unknown `asyncio_mode` config option and `.pytest_cache` cache write warnings.
- Report applicability preflight: `preflight_passed: true`, `missing_required_specs: []`, `missing_advisory_specs: []`, packet hash `sha256:036a0e9419b4676a4eaac52900d914fd4548b428bc309afb3b85e5ea7d36db86`.
- Report clause preflight: exit `0`, 5 clauses evaluated, 4 `must_apply`, 0 evidence gaps in `must_apply`, 0 blocking gaps.

## Acceptance Criteria Status

- Headless dispatch flows using `::init gtkb` or `::init gtkb <role>` do not block on owner-facing menus or focus selection: complete.
- Interactive init-keyword relay still renders cached startup disclosure when the init-keyword path is used: complete, now through a minimized routing disclosure.
- `::open <activity>` remains within the existing activity vocabulary and injects/surfaces the matching activity disposition profile: complete.
- Operator-facing dashboard, active-work-subject, startup briefing, and top-priority context are available through `::open <activity>`: complete.
- Parser grammar, typed close behavior, and one-topic-per-type semantics are unchanged: complete.
- Implementation remained inside the approved root and scoped source/test files: complete.

## Worktree Hygiene Notes

This auto-dispatch run created in-root pytest basetemp directories named `.codex-pytest-tmp-wi4686-*`. A cleanup attempt using recursive removal was blocked by the project's destructive-operation guard. Because this auto-dispatched worker cannot ask the owner for cleanup approval, those test artifacts remain unremoved and are not implementation targets or commit candidates.

## Recommended Commit Type

- Recommended commit type: `fix`
- Justification: the slice corrects the init disclosure placement/size behavior by keeping `::init` bounded and moving the operator-facing content to the already-governed `::open <activity>` path. It adds runtime context rendering, but the user-facing behavior is a repair to the approved startup-disclosure routing contract.

## Risk And Rollback

Residual risk is mostly prompt-context size and startup latency on `::open <activity>` because the open renderer now loads compact startup model data fail-soft. This is bounded by targeted tests and by the non-blocking exception handling in the open context renderer.

Rollback is a normal source/test revert of the five implementation-scope files plus this bridge report. No hook registration, config, MemBase, formal artifact, Agent Red, or credential rollback is required.

## Loyal Opposition Asks

1. Verify the implementation against the approved WI-4686 proposal, linked specifications, and executed command evidence.
2. Confirm the unrelated full-file baseline failure is outside this implementation scope, or return a scoped `NO-GO` if you find a WI-4686 behavioral regression.
3. Return `VERIFIED` if the report and implementation satisfy the approved proposal, otherwise return `NO-GO` with findings.

Copyright (c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
