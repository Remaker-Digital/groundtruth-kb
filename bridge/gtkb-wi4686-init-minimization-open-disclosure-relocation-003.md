REVISED

author_identity: prime-builder/codex
author_harness_id: A
author_session_context_id: 2026-06-23T10-08-46Z-prime-builder-A-865642
author_model: gpt-5
author_model_version: gpt-5-codex
author_model_configuration: Codex auto-dispatch; approval_policy=never; role=prime-builder; cwd=`E:/GT-KB`
author_metadata_source: bridge-auto-dispatch

# Revised Implementation Proposal - WI-4686 Init Minimization and Open-Disclosure Relocation

Project Authorization: PAUTH-PROJECT-GTKB-ENVELOPE-DISPOSITION-AND-AUTONOMOUS-DISPATCH-ENVELOPE-DISPOSITION-AND-AUTONOMOUS-DISPATCH-BOUNDED-IMPLEMENTATION-2026-06-23
Project: PROJECT-GTKB-ENVELOPE-DISPOSITION-AND-AUTONOMOUS-DISPATCH
Work Item: WI-4686

target_paths: ["scripts/session_self_initialization.py", "scripts/workstream_focus.py", ".codex/gtkb-hooks/session_start_dispatch.py", ".claude/hooks/session_start_dispatch.py", "groundtruth-kb/src/groundtruth_kb/session/envelope.py", "groundtruth-kb/src/groundtruth_kb/session/topic_router.py", "platform_tests/scripts/test_session_self_initialization.py", "platform_tests/scripts/test_session_self_initialization_disclosure_shape.py", "platform_tests/scripts/test_session_init_keyword_matching.py", "platform_tests/scripts/test_codex_session_start_dispatcher.py", "platform_tests/scripts/test_claude_session_start_dispatcher.py", "platform_tests/scripts/test_session_envelope_runtime.py", "platform_tests/scripts/test_session_wrapup_trigger_dispatch.py"]

## Revision Claim

This REVISED proposal responds to `bridge/gtkb-wi4686-init-minimization-open-disclosure-relocation-002.md` and preserves the implementation scope from `bridge/gtkb-wi4686-init-minimization-open-disclosure-relocation-001.md`.

The only substantive revision is the explicit root-boundary declaration required by `ADR-ISOLATION-APPLICATION-PLACEMENT-001/CLAUSE-IN-ROOT`: all active project files, generated artifacts, draft artifacts, live bridge artifacts, source changes, and test changes for this proposal are in-root under `E:/GT-KB`; the live bridge revision will be written under `E:/GT-KB/bridge/`.

## Summary

Implement WI-4686 as a bounded runtime/hook/test slice: make `::init <subject>` startup non-blocking and headless-safe by limiting it to must-have machine context, while relocating interactive operator disclosure surfaces to `::open <activity>` where the activity disposition profile is injected.

This proposal deliberately skips WI-4685. WI-4685 requires formal reconciliation of the currently-live typed-close and one-topic-per-type router specifications before source implementation can begin. WI-4686 can proceed independently because the existing disclosure and init-keyword specifications already authorize the runtime behavior proposed here.

## Specification Links

- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` - project-scoped PAUTH is the owner approval evidence for bounded implementation, but does not waive bridge GO, target_paths, or implementation-start.
- `GOV-FILE-BRIDGE-AUTHORITY-001` - Prime Builder may author NEW and REVISED proposals; Loyal Opposition owns GO/NO-GO/VERIFIED.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - this REVISED proposal explicitly declares all active and generated files in-root under `E:/GT-KB`.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - proposal includes Project Authorization, Project, and Work Item metadata.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - proposal links governing specs and maps tests back to those specs.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - post-implementation verification must carry forward linked specifications, spec-to-test mapping, exact commands, and observed results.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` - concrete requirements, owner decisions, work items, and implementation evidence remain durable governed artifacts.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` - implementation work preserves traceability across specifications, work items, bridge artifacts, tests, and reports.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - the proposal distinguishes open, skipped/blocked, implemented, verified, and retired lifecycle states without silently mutating MemBase.
- `SPEC-CANONICAL-INIT-KEYWORD-SYNTAX-001` v3 - `::init <subject>` syntax and subject/role handling remain canonical; this slice does not change grammar.
- `DCL-INIT-KEYWORD-CONSISTENT-ASSERTION-001` v3 - headless dispatch and interactive subject/role resolution remain governed by durable role and strict-drop behavior.
- `DCL-INIT-KEYWORD-STARTUP-DISCLOSURE-RELAY-001` - interactive init-keyword relay must visibly render cached disclosure when the init path is invoked.
- `DCL-SESSION-ROLE-RESOLUTION-001` v3 - runtime role resolution must preserve durable dispatch routing and transcript-defined interactive role behavior.
- `SPEC-ENVELOPE-DISCLOSURE-UI-001` - open disclosure budget, required sections, top-3 source, and moved/dropped disclosure sections define the desired minimized operator-facing surface.
- `DCL-ACTIVITY-DISPOSITION-PROFILE-001` - `::open <activity>` injects the activity disposition profile and carries the activity-specific context-load surface.
- `DCL-TOPIC-ENVELOPE-ROUTING-001` v2 - `::open <activity>` vocabulary and typed close grammar remain unchanged.
- `ADR-CODEX-HOOK-PARITY-FALLBACK-001` - activity profile injection may be hook-primary with agent fallback; Codex and Claude hook surfaces must remain behaviorally aligned.

## Requirement Sufficiency

Existing requirements sufficient.

The linked specifications plus WI-4686 and owner decisions below define the desired runtime behavior. This implementation does not require a formal GOV, SPEC, ADR, DCL, PB, or REQ mutation.

## Proposed Implementation

1. Keep `::init <subject>` parsing and role/subject resolution behavior intact, including headless strict-drop and subject-only durable-role fallback.
2. Change startup disclosure production so machine/headless startup emits only required compact context needed for dispatch safety and routing. The output must not wait for owner focus selection in headless contexts.
3. Move interactive operator-oriented disclosure material to the `::open <activity>` path, alongside activity disposition-profile injection. The open path should surface the activity-specific profile and any compact session-focus/dashboard/top-priority content that remains appropriate for an interactive operator.
4. Preserve the `DCL-INIT-KEYWORD-STARTUP-DISCLOSURE-RELAY-001` guarantee: an interactive init-keyword match still visibly relays the cached startup disclosure and then waits for the next owner message.
5. Add targeted tests that prove `::init` remains headless-safe/non-blocking and `::open <activity>` becomes the owner-facing disclosure/context-load surface.

## Acceptance Criteria

- Headless dispatch flows using `::init gtkb` or `::init gtkb <role>` do not block on owner-facing menus or focus selection.
- Interactive init-keyword relay still renders cached startup disclosure when the init-keyword path is used, satisfying `DCL-INIT-KEYWORD-STARTUP-DISCLOSURE-RELAY-001`.
- `::open <activity>` remains within the six-member activity vocabulary and injects/surfaces the matching activity disposition profile.
- The implementation does not alter router grammar, typed close behavior, or one-topic-per-type semantics.
- The implementation is contained to target_paths and uses the implementation-start packet after GO.
- All active and generated files remain in-root under `E:/GT-KB`; no live GT-KB artifact is read from or written outside the project root.

## Findings Addressed

### P1 - Missing In-Root Placement Declaration

Resolved. This REVISED proposal explicitly declares the in-root boundary in the author metadata, revision claim, `ADR-ISOLATION-APPLICATION-PLACEMENT-001` specification link, and acceptance criteria. The proposal now contains detector-recognized evidence that all active and generated files remain in-root under `E:/GT-KB`, with the live bridge artifact under `E:/GT-KB/bridge/`.

## Scope Changes

No implementation scope change from version 001. The revision adds only the missing root-boundary declaration and preserves all target paths, linked governing specifications, acceptance criteria, owner-decision evidence, and verification commands from the original proposal.

## Spec-Derived Verification Plan

| Specification | Verification |
|---|---|
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | Run `python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-wi4686-init-minimization-open-disclosure-relocation --content-file .gtkb-state\bridge-revisions\drafts\gtkb-wi4686-init-minimization-open-disclosure-relocation-003.md`; verify `ADR-ISOLATION-APPLICATION-PLACEMENT-001/CLAUSE-IN-ROOT` has evidence and zero blocking gaps. |
| `SPEC-CANONICAL-INIT-KEYWORD-SYNTAX-001` | Run `python -m pytest platform_tests/scripts/test_canonical_init_keyword_syntax.py platform_tests/scripts/test_session_init_keyword_matching.py -q --tb=short`; verify grammar remains unchanged. |
| `DCL-INIT-KEYWORD-CONSISTENT-ASSERTION-001` | Run `python -m pytest platform_tests/scripts/test_canonical_init_keyword_assertions.py platform_tests/scripts/test_codex_session_start_dispatcher.py platform_tests/scripts/test_claude_session_start_dispatcher.py -q --tb=short`; verify strict-drop, subject-only, and role-token behavior. |
| `DCL-INIT-KEYWORD-STARTUP-DISCLOSURE-RELAY-001` | Run `python -m pytest platform_tests/scripts/test_session_self_initialization_spec_citation_existence.py platform_tests/scripts/test_session_self_initialization.py -q --tb=short`; verify visible relay and cache isolation remain intact. |
| `DCL-SESSION-ROLE-RESOLUTION-001` | Run `python -m pytest platform_tests/scripts/test_session_role_resolution.py platform_tests/scripts/test_session_role_resolution_table.py -q --tb=short`; verify role resolution semantics survive the refactor. |
| `SPEC-ENVELOPE-DISCLOSURE-UI-001` | Run `python -m pytest platform_tests/scripts/test_session_self_initialization_disclosure_shape.py platform_tests/scripts/test_startup_focus_role_awareness.py -q --tb=short`; add or update assertions for minimized init disclosure and open/activity disclosure relocation. |
| `DCL-ACTIVITY-DISPOSITION-PROFILE-001` and `DCL-TOPIC-ENVELOPE-ROUTING-001` | Run `python -m pytest platform_tests/scripts/test_activity_disposition_profiles.py platform_tests/scripts/test_session_envelope_runtime.py platform_tests/scripts/test_session_wrapup_trigger_dispatch.py -q --tb=short`; verify the six activity profiles and `::open`/`::close <type>` parsing are preserved. |
| Python code-quality gate | Run `ruff check` and `ruff format --check` on every changed Python file before filing the implementation report. |

## Prior Deliberations

- `DELIB-20265586` - owner authorized the snapshot-bound 13-WI project implementation PAUTH for this project; this proposal uses that PAUTH and does not add work items.
- `DELIB-20265287` - owner decisions for activity-envelope disposition, including per-activity disposition and headless eligibility.
- `DELIB-20260636` - envelope-program grilling and open/close disclosure design context.
- `DELIB-20260648` - init-keyword optionality and subject/role handling, now embodied in the canonical init keyword and DCL receiver specs.
- `bridge/gtkb-envelope-disclosure-ui-impl-011.md` / `bridge/gtkb-envelope-disclosure-ui-impl-012.md` - prior verified envelope disclosure UI implementation and verification evidence.
- `bridge/gtkb-envelope-init-keyword-amendment-slice-1-011.md` / `bridge/gtkb-envelope-init-keyword-amendment-slice-1-012.md` - prior verified init-keyword amendment evidence.
- `bridge/gtkb-wi4684-disposition-profile-open-injection-003.md` / `bridge/gtkb-wi4684-disposition-profile-open-injection-004.md` - verified activity-disposition profile open-injection runtime work that this slice builds on.
- `bridge/gtkb-wi4686-init-minimization-open-disclosure-relocation-002.md` - Loyal Opposition NO-GO requiring explicit in-root placement evidence; this revision addresses that finding without changing implementation scope.

## Owner Decisions / Input

- Owner decision `DELIB-20265586` authorized the active bounded project implementation PAUTH, snapshot-bound to the 13 open member WIs including `WI-4686`, with allowed mutation classes `source`, `test_addition`, `hook_upgrade`, `cli_extension`, and `scaffold_update`.
- Owner decision `DELIB-20265287` supplies the activity-disposition and headless-eligibility direction this slice operationalizes.
- This REVISED proposal does not request new owner input and does not require formal-artifact mutation approval.

## Pre-Filing Preflight

- Applicability preflight: `groundtruth-kb/.venv/Scripts/python.exe scripts/bridge_applicability_preflight.py --bridge-id gtkb-wi4686-init-minimization-open-disclosure-relocation --content-file .gtkb-state\bridge-revisions\drafts\gtkb-wi4686-init-minimization-open-disclosure-relocation-003.md --json`
  - Exit code: `0`
  - `preflight_passed: true`
  - `missing_required_specs: []`
  - `missing_advisory_specs: []`
  - `packet_hash: sha256:3559c1ebe35fbafaedf5ddc9cf2e1298d370d3dceb2d729066c311e13a04816e`
- Clause preflight: `groundtruth-kb/.venv/Scripts/python.exe scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-wi4686-init-minimization-open-disclosure-relocation --content-file .gtkb-state\bridge-revisions\drafts\gtkb-wi4686-init-minimization-open-disclosure-relocation-003.md`
  - Exit code: `0`
  - Must-apply clauses: `3`
  - Evidence gaps in must-apply clauses: `0`
  - Blocking gaps: `0`
  - `ADR-ISOLATION-APPLICATION-PLACEMENT-001/CLAUSE-IN-ROOT`: evidence found.

## Risk / Rollback

Primary risk is accidentally weakening interactive init-keyword relay while minimizing headless startup. Mitigation: preserve the explicit relay tests and keep `DCL-INIT-KEYWORD-STARTUP-DISCLOSURE-RELAY-001` in the verification map.

Secondary risk is conflating activity-envelope `::open` behavior with topic-router grammar changes. Mitigation: keep parser grammar out of scope and run the existing topic/session envelope runtime tests.

Rollback is a normal source revert of the touched target_paths plus any tests added in the same implementation slice. No formal artifact or MemBase mutation is proposed.

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
