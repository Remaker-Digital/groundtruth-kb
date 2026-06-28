NEW

# gtkb-ar-readiness-phase-1-3-work-subject-write-guard-activation (Slice 1) - Work-subject write-guard activation

bridge_kind: prime_proposal
Document: gtkb-ar-readiness-phase-1-3-work-subject-write-guard-activation
Version: 001
Author: Prime Builder / Codex Desktop
Date: 2026-06-28T17:29:04Z

author_identity: Prime Builder / Codex Desktop
author_harness_id: A
author_session_context_id: 019f0cf7-9439-7cc3-8b58-cdad991c5890
author_model: GPT-5 via Codex
author_model_version: gpt-5
author_model_configuration: Codex Desktop, Windows PowerShell, danger-full-access workspace, network enabled

Project Authorization: PAUTH-PROJECT-GTKB-AGENT-RED-READINESS-AGENT-RED-READINESS-PROGRAM-PHASE-1-ISOLATION-PARTITION-IN-PLACE
Project: PROJECT-GTKB-AGENT-RED-READINESS
Work Item: WI-4656

target_paths: ["scripts/workstream_focus.py", ".claude/hooks/workstream-focus.py", ".codex/gtkb-hooks/workstream-focus.cmd", ".claude/settings.json", ".codex/hooks.json", "scripts/check_codex_hook_parity.py", "scripts/clean_adopter_validation.py", "groundtruth-kb/src/groundtruth_kb/project/doctor.py", "groundtruth-kb/src/groundtruth_kb/project/doctor_isolation.py", "platform_tests/hooks/test_workstream_focus.py", "platform_tests/scripts/test_workstream_focus_hook_parity.py", "platform_tests/scripts/test_check_codex_hook_parity.py", "platform_tests/scripts/test_codex_hook_parity.py", "platform_tests/scripts/test_fab07_doctor_false_signals.py", "groundtruth-kb/tests/adopter/test_clean_adopter_packaging.py", "groundtruth-kb/tests/test_doctor_isolation.py"]

implementation_scope: hook_registration | source | test | doctor_hardening
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

---

## Summary

Implement the Phase 1.3 Agent Red Readiness work-subject write-guard activation. The verified `gtkb-work-subject-root-enforcement-implementation` chain already supplies the work-subject foundation: canonical state, root classification, and `guard_tool_use()` blocking behavior. This slice activates that guard on write-capable harness paths and closes the remaining gaps called out by the current backlog item: PreToolUse wiring, bridge-only application-subject exceptions, and isolation-doctor self-bypass removal or narrowing.

The implementation is platform-side only. It must not mutate Agent Red product source, perform partition-in-place data migration, or revise formal GOV/ADR/DCL/SPEC rows. The desired result is mechanical: when the active work subject is application, GT-KB source/config/rule writes are blocked unless the change is a permitted numbered bridge advisory output; when the active work subject is GT-KB, application product writes are blocked until the work subject is switched.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` - governs the append-only bridge filing and requires a GO plus implementation-start authorization before protected hook/config/source edits.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - requires this proposal to cite the specifications that drive implementation and verification.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - requires explicit project, work-item, and PAUTH linkage for this bridge proposal.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - requires verification to prove the linked requirements through targeted tests and not only through inspection.
- `ADR-CROSS-HARNESS-PARITY-001` - requires equivalent behavior across Claude and Codex harness surfaces when the same GT-KB governance invariant applies.
- `DCL-CROSS-HARNESS-PARITY-ENFORCEMENT-001` - requires a cross-harness disposition for proposals that touch `.claude` and `.codex` hook/config surfaces.
- `GOV-STANDING-BACKLOG-001` - establishes MemBase backlog authority; WI-4656 is the active P1 backlog item being processed.
- `GOV-SOURCE-OF-TRUTH-FRESHNESS-001` - requires guard and doctor decisions to read live work-subject and filesystem/config state rather than cached summaries.
- `GOV-AGENT-RED-GTKB-CONFORMANCE-001` - requires Agent Red to remain a separate project, so GT-KB platform sessions must not silently mutate application product files and application sessions must not silently mutate GT-KB platform files.
- `GOV-AGENT-RED-NESTED-IN-APPLICATIONS-001` - establishes `applications/Agent_Red/` as the application root that write-guard classification must protect.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - establishes the `applications/<name>/` placement boundary used by root classification.
- `ADR-APPLICATION-ISOLATION-CONTRACT-001` - defines applications as isolated execution contexts with separate lifecycle authority from GT-KB platform artifacts.
- `DCL-APP-ROOT-MINIMIZATION-001` - supplies downstream write-guard context for the D-P1a bridge-allowed block-list policy while keeping app-root minimization and write-guard activation as distinct slices.

## Prior Deliberations And Verified Evidence

- `DELIB-20265219` - owner ratified the Agent Red Readiness program and its platform-side Phase 1 focus.
- `DELIB-20265220` - owner approved materializing Phase 1 slices and accepted the D-P1a policy direction for bridge-allowed write-guard block-list semantics.
- `DELIB-20265227` - owner resolved the Phase 1.1 governance foundation and clarified that write-guard enforcement belongs to the downstream Phase 1.3 slice.
- `bridge/gtkb-work-subject-root-enforcement-implementation-020.md` - VERIFIED the prior foundation thread through version 20; this proposal reuses that foundation rather than reopening it.
- `bridge/gtkb-wi4690-application-work-subject-advisory-boundary-004.md` - existing verified boundary work confirms application-subject advisory behavior and current root-classification test surfaces.

## Cross-Harness Disposition

Parity is required for Claude and Codex because this proposal touches `.claude/settings.json`, `.claude/hooks/workstream-focus.py`, `.codex/hooks.json`, and `.codex/gtkb-hooks/workstream-focus.cmd`.

- Claude disposition: behavior parity required. Claude write-capable PreToolUse paths must invoke the same shared `scripts/workstream_focus.py` guard through `.claude/hooks/workstream-focus.py`.
- Codex disposition: behavior parity required. Codex `Bash` and `apply_patch` PreToolUse paths must invoke the same shared guard through `.codex/gtkb-hooks/workstream-focus.cmd`, preserving the `GTKB_HARNESS_NAME=codex` adapter behavior.
- No typed waiver is requested. Any harness-specific schema differences must be handled in adapter/config only; the allow/block semantics must remain shared.
- Verification: `platform_tests/scripts/test_workstream_focus_hook_parity.py`, `platform_tests/scripts/test_check_codex_hook_parity.py`, `platform_tests/scripts/test_codex_hook_parity.py`, and direct `platform_tests/hooks/test_workstream_focus.py` cases must prove equivalent behavior or fail.

## Owner Decisions / Input

No new owner decision is required before filing. The active Phase 1 PAUTH covers this work item and cites `DELIB-20265219`; the work item itself cites `DELIB-20265219` and `DELIB-20265220`. A per-slice bridge GO and implementation-start packet are still required before protected source, hook, config, script, or test mutations.

## Requirement Sufficiency

Existing requirements are sufficient. The work item acceptance summary states: "Application-subject session blocked from GT-KB source/config/rules writes; bridge allowed; doctor no longer self-bypasses on working repo." The verified work-subject foundation plus the Phase 1.1 ADR/DCL provide enough governing vocabulary to implement that acceptance without a new formal specification.

## Proposed Implementation

1. Wire `workstream-focus` into write-capable PreToolUse surfaces:
   - Claude: add a PreToolUse registration for write-capable tools that invokes `.claude/hooks/workstream-focus.py`.
   - Codex: add equivalent coverage for `apply_patch` in `.codex/hooks.json` using `.codex/gtkb-hooks/workstream-focus.cmd`; preserve existing `Bash` coverage.
2. Confirm the hook adapter path remains shared and harness-aware:
   - `.claude/hooks/workstream-focus.py` continues to import `scripts/workstream_focus.py`.
   - `.codex/gtkb-hooks/workstream-focus.cmd` continues to set `GTKB_HARNESS_NAME=codex` before delegating.
3. Tighten the application-subject bridge exception to bridge-only advisory output:
   - ordinary GT-KB source/config/rule writes remain blocked while current subject is application,
   - numbered bridge advisory writes remain allowed only when the write content is an `ADVISORY` bridge entry,
   - no broader governance/source/config exception is introduced.
4. Remove or narrow the clean-adopter doctor self-bypass:
   - `scripts/clean_adopter_validation.py` must not silently ignore an actionable `isolation:no-writable-product-paths` required failure on a working repo,
   - any retained exception must be fixture-specific, documented, and tested so it cannot mask real product-path writability drift.
5. Update parity and regression tests:
   - hook registration tests prove Claude and Codex write-capable paths invoke workstream-focus,
   - direct `guard_tool_use()` tests prove application-subject GT-KB source/config/rule writes block, application-subject numbered bridge advisory writes pass, and GT-KB-subject application product writes block,
   - doctor/clean-adopter tests prove the prior same-user probe bypass no longer hides actionable required failures.

## Explicit Non-Goals

- No app-root minimization validator work; that is a separate Phase 1.2 slice.
- No partition-in-place data migration; that is a later Phase 1 slice.
- No product-source mutation under `applications/Agent_Red/`.
- No formal GOV/ADR/DCL/SPEC creation or revision.
- No writes outside `E:/GT-KB`.

## Spec-Derived Verification Plan

| Specification | Verification |
| --- | --- |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001`, `ADR-APPLICATION-ISOLATION-CONTRACT-001`, `GOV-AGENT-RED-GTKB-CONFORMANCE-001`, `GOV-AGENT-RED-NESTED-IN-APPLICATIONS-001` | `platform_tests/hooks/test_workstream_focus.py` proves root classification and subject-specific block/allow behavior for GT-KB platform paths, bridge advisory paths, and application product paths. |
| `DCL-APP-ROOT-MINIMIZATION-001` | Focused tests prove write-guard behavior cites the downstream D-P1a context without changing app-root registry validator scope. |
| `ADR-CROSS-HARNESS-PARITY-001`, `DCL-CROSS-HARNESS-PARITY-ENFORCEMENT-001` | Hook parity tests prove Claude and Codex write-capable paths invoke the shared workstream-focus guard with equivalent allow/block semantics and no waiver. |
| `GOV-SOURCE-OF-TRUTH-FRESHNESS-001` | Direct hook tests create fresh work-subject state and assert `guard_tool_use()` reads that state at execution time. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | Targeted pytest lanes cover hook registration, direct guard behavior, Codex parity, and clean-adopter doctor behavior. |
| `GOV-FILE-BRIDGE-AUTHORITY-001`, `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001`, `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`, `GOV-STANDING-BACKLOG-001` | Bridge applicability preflight and clause preflight must pass for this proposal, and implementation-start must bind the GO bridge to WI-4656 before protected edits. |

Expected post-implementation commands:

```text
groundtruth-kb/.venv/Scripts/python.exe -m pytest platform_tests/hooks/test_workstream_focus.py platform_tests/scripts/test_workstream_focus_hook_parity.py platform_tests/scripts/test_check_codex_hook_parity.py platform_tests/scripts/test_codex_hook_parity.py -q --tb=short
groundtruth-kb/.venv/Scripts/python.exe -m pytest groundtruth-kb/tests/test_doctor_isolation.py groundtruth-kb/tests/adopter/test_clean_adopter_packaging.py platform_tests/scripts/test_fab07_doctor_false_signals.py -q --tb=short
groundtruth-kb/.venv/Scripts/python.exe scripts/check_codex_hook_parity.py --project-root .
groundtruth-kb/.venv/Scripts/ruff.exe check scripts/workstream_focus.py scripts/check_codex_hook_parity.py scripts/clean_adopter_validation.py groundtruth-kb/src/groundtruth_kb/project/doctor.py groundtruth-kb/src/groundtruth_kb/project/doctor_isolation.py platform_tests/hooks/test_workstream_focus.py platform_tests/scripts/test_workstream_focus_hook_parity.py platform_tests/scripts/test_check_codex_hook_parity.py platform_tests/scripts/test_codex_hook_parity.py platform_tests/scripts/test_fab07_doctor_false_signals.py groundtruth-kb/tests/test_doctor_isolation.py groundtruth-kb/tests/adopter/test_clean_adopter_packaging.py
groundtruth-kb/.venv/Scripts/ruff.exe format --check scripts/workstream_focus.py scripts/check_codex_hook_parity.py scripts/clean_adopter_validation.py groundtruth-kb/src/groundtruth_kb/project/doctor.py groundtruth-kb/src/groundtruth_kb/project/doctor_isolation.py platform_tests/hooks/test_workstream_focus.py platform_tests/scripts/test_workstream_focus_hook_parity.py platform_tests/scripts/test_check_codex_hook_parity.py platform_tests/scripts/test_codex_hook_parity.py platform_tests/scripts/test_fab07_doctor_false_signals.py groundtruth-kb/tests/test_doctor_isolation.py groundtruth-kb/tests/adopter/test_clean_adopter_packaging.py
```

## Risk / Rollback

Risk is high because this activates a write-blocking PreToolUse guard on live harness paths. False positives can interrupt normal development, and false negatives defeat the Agent Red isolation boundary. Mitigation is to keep the code path shared, preserve direct unit tests for both blocked and allowed cases, and verify harness registration parity. Rollback is a single commit revert restoring prior hook registrations, guard behavior, and clean-adopter doctor handling.

## Bridge Filing

This proposal is filed as the next status-bearing numbered bridge file for `gtkb-ar-readiness-phase-1-3-work-subject-write-guard-activation`; no prior version is deleted or rewritten (append-only). Dispatcher/TAFE state plus the numbered file chain are the live workflow state per `GOV-FILE-BRIDGE-AUTHORITY-001`.

## Recommended Commit Type

feat - this activates an existing verified work-subject guard on write-capable harness paths and hardens doctor visibility.

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
