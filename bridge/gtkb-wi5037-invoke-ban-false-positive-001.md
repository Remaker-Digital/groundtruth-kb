NEW

# gtkb-wi5037-invoke-ban-false-positive - Narrow direct-invocation hook false positives

bridge_kind: prime_proposal
Document: gtkb-wi5037-invoke-ban-false-positive
Version: 001
Author: Prime Builder (Codex)
Date: 2026-07-07 UTC

author_identity: prime-builder/codex
author_harness_id: A
author_session_context_id: 019f337a-009a-7f51-8dce-b6c3f1d91b1c
author_model: GPT-5 Codex
author_model_version: gpt-5
author_model_configuration: Codex desktop interactive Prime Builder session; reasoning=xhigh; approval_policy=never

Project Authorization: PAUTH-PROJECT-GTKB-OPS-DISPATCHER-MODERNIZATION-WI5037-INVOKE-BAN-FALSE-POSITIVE-20260707
Project: PROJECT-GTKB-OPS-DISPATCHER-MODERNIZATION
Work Item: WI-5037

target_paths: ["groundtruth-kb/src/groundtruth_kb/enforcement/__init__.py", ".codex/gtkb-hooks/directive-enforcement-adapter.py", ".claude/hooks/directive-enforcement-claude-adapter.py", "groundtruth-kb/tests/framework/test_bash_enforcement_parser.py", "platform_tests/scripts/test_fab14_directive_hook_coverage.py"]

implementation_scope: source
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

---

## Summary

WI-5037 tracks a false-positive class in the `DIRECT-HARNESS-INVOKE-BAN` PreToolUse enforcement path: legitimate governed `gt` commands can be blocked when their arguments or captured prose mention harness/provider behavior near routing terminology. The governing requirement is still correct: GT-KB harnesses must not directly launch other harnesses. The correction is to keep the ban focused on actual process-spawning patterns while allowing governed status, backlog, and deliberation commands that merely discuss harness/provider behavior.

This proposal authorizes a narrow hook/parser slice. After Loyal Opposition GO and implementation-start, Prime Builder will add regression coverage for the observed governed-command cases, verify existing direct-launch denials still fire, and only change shared enforcement or adapter code if the tests expose an actual parser/adaptor defect. The intended outcome is lower operational friction without weakening `SPEC-INTAKE-21c5b3`.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` - Requires this proposal to move through the append-only bridge before Prime Builder edits protected hook/source/test files.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - Requires the proposal to cite the governing requirements that define both the ban and the acceptable correction.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - Requires the proposal to carry project, PAUTH, work-item, and target path linkage.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - Requires any eventual implementation report and verification verdict to tie tests back to the cited requirements.
- `GOV-STANDING-BACKLOG-001` - Governs promotion of the advisory/backlog defect into a tracked Prime Builder implementation proposal.
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` - Requires bounded owner/project authorization before implementation work starts.
- `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001` - Requires the PAUTH not to bypass the bridge GO and implementation-start gates.
- `SPEC-INTAKE-21c5b3` - Defines the direct harness-to-harness invocation prohibition that this work must preserve.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` - Requires project-relevant decisions, risks, and accepted work to be preserved in governed artifacts.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` - Supports artifact-first handling of this advisory-to-implementation transition.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - Requires the advisory/backlog item to be advanced through the proper lifecycle state instead of remaining informal scratch.
- `ADR-CROSS-HARNESS-PARITY-001` - Requires harness-observable governance capabilities to preserve behavioral parity across applicable harnesses or declare an owner-approved typed waiver.
- `DCL-CROSS-HARNESS-PARITY-ENFORCEMENT-001` - Requires a cross-harness disposition for proposals touching harness-surface files.

## Prior Deliberations

- `gtkb-wi5037-invoke-ban-false-positive-advisory-001` - Loyal Opposition advisory capturing the observed false-positive class and recommended Prime Builder action.
- `DELIB-20260703-DIRECT-HARNESS-INVOKE-BAN` - Owner/governance context for introducing the mechanical direct-invocation ban.
- `SPEC-INTAKE-21c5b3` - Confirmed governance requirement prohibiting direct harness-to-harness invocation.
- `DELIB-20260707-WI5037-IMPLEMENTATION-APPROVAL` - Owner authorization to file the WI-5037 implementation proposal.

## Owner Decisions / Input

Owner authorization is captured in `DELIB-20260707-WI5037-IMPLEMENTATION-APPROVAL`. The bounded PAUTH is `PAUTH-PROJECT-GTKB-OPS-DISPATCHER-MODERNIZATION-WI5037-INVOKE-BAN-FALSE-POSITIVE-20260707`; it covers proposal filing and only GO-gated implementation work for WI-5037. No additional owner decision is required before Loyal Opposition review.

## Requirement Sufficiency

Existing requirements are sufficient. `SPEC-INTAKE-21c5b3` states the behavior that must remain blocked: direct harness-to-harness launching, triggering, commanding, or otherwise interacting outside the governed dispatcher/control plane or manual independent operation. WI-5037 is a precision correction around enforcement scope, not a request to revise the ban.

## Spec-Derived Verification Plan

- `SPEC-INTAKE-21c5b3`: Add/confirm parser tests that direct process-spawning patterns remain blocked, including harness command heads, `codex exec`, Python harness shim launches, and `Start-Process` variants.
- `SPEC-INTAKE-21c5b3`: Add/confirm allowed-case tests for governed `gt` status, deliberation, and backlog commands whose arguments or prose mention harness/provider behavior and routing terminology without launching a harness process.
- `GOV-FILE-BRIDGE-AUTHORITY-001`, `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001`, and `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001`: Verify the implementation report cites this proposal, the PAUTH, and the implementation-start claim before any protected source/test mutation is treated as complete.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`: Ensure the implementation report includes the exact commands below and maps results to the linked specs.
- `ADR-CROSS-HARNESS-PARITY-001` and `DCL-CROSS-HARNESS-PARITY-ENFORCEMENT-001`: Verify Codex and Claude hook surfaces keep equivalent behavior for the direct-invocation ban; no typed waiver is requested.

Expected implementation verification commands:

```text
groundtruth-kb/.venv/Scripts/python.exe -m pytest groundtruth-kb/tests/framework/test_bash_enforcement_parser.py -q --no-header
groundtruth-kb/.venv/Scripts/python.exe -m pytest platform_tests/scripts/test_fab14_directive_hook_coverage.py -q --no-header
```

Expected result: false-positive regression cases pass without allowing any direct harness process launch case that is already covered by the parser and adapter tests.

## Cross-Harness Disposition

Applicable harness surfaces: Codex PreToolUse enforcement adapter and Claude PreToolUse enforcement adapter. The authoritative file list remains the inline `target_paths` JSON header.

Parity declaration: this proposal requires behavioral parity for the direct harness invocation ban across Codex and Claude. Both adapters must continue to delegate to the shared enforcement logic or otherwise produce equivalent allow/deny outcomes for the same command classes: direct harness process launches are denied, while governed `gt` commands that only discuss harness/provider behavior are allowed. No typed waiver is requested for either applicable harness.

## Risk / Rollback

The main risk is over-narrowing the hook and accidentally permitting direct harness process launch. The counter-risk is under-narrowing, leaving operational false positives that block governed diagnostics and deliberation capture. Mitigation is a focused test matrix that pairs each new allow case with existing deny cases. Rollback is a single commit revert of the eventual implementation slice, leaving this proposal and PAUTH history append-only.

## Bridge Filing

This proposal is filed through the bridge as the next status-bearing numbered
bridge file for `gtkb-wi5037-invoke-ban-false-positive`; no prior version is deleted or rewritten
(append-only). Dispatcher/TAFE state plus the numbered file chain are the live
workflow state per `GOV-FILE-BRIDGE-AUTHORITY-001`.

## Recommended Commit Type

`fix(hooks)` - the implementation should correct a governance-hook false-positive class while preserving existing direct-launch denials.

## Pre-Filing Checks

- Placeholder-marker scan returned no matches.
- Applicability preflight against this draft returned `preflight_passed: true` and no missing required specs.
- ADR/DCL clause preflight against this draft returned blocking gaps `0`.
- `target_paths` parse check: inline JSON parsed to the five intended protected source/test/hook paths.
- Phantom-spec sweep: all cited specs exist in MemBase, including nonstandard intake spec `SPEC-INTAKE-21c5b3`.

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
