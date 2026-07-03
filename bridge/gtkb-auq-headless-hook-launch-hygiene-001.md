NEW
author_identity: Codex Prime Builder
author_harness_id: A
author_session_context_id: codex-20260702-ops-dispatcher-synthesis
author_model: GPT-5
author_model_version: 2026-07-02
author_model_configuration: Codex desktop; E:/GT-KB; danger-full-access; approval-policy never; interactive role Prime Builder via ::init gtkb pb

# AUQ Headless Hook Launch Hygiene

bridge_kind: prime_proposal
Document: gtkb-auq-headless-hook-launch-hygiene
Version: 001
Date: 2026-07-02 UTC

Project Authorization: PAUTH-PROJECT-GTKB-AUQ-HEADLESS-HOOK-HYGIENE-WI-4959
Project: PROJECT-GTKB-AUQ-HEADLESS-HOOK-HYGIENE
Work Item: WI-4959

target_paths: [".codex/hooks.json", ".codex/gtkb-hooks", ".claude/hooks", ".cursor", "scripts/windows_subprocess.py", "scripts/check_codex_hook_parity.py", "platform_tests/scripts/test_codex_hook_runtime_containment.py", "platform_tests/scripts/test_codex_hook_parity.py", "platform_tests/scripts/test_cursor_hook_headless_parity.py", "platform_tests/scripts/test_workstream_focus_hook_parity.py", "platform_tests/scripts/test_windows_subprocess.py"]

implementation_scope: source+harness-config+tests
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

## Summary

Mike observed that after each AUQ/owner-answer flow, two Windows console windows spawn and disappear quickly. This proposal fixes AUQ-adjacent hook and owner-decision launch paths so short-lived child helpers run headlessly on Windows.

This Wave 1 child is intentionally small and prioritized for first implementation if it receives a quick GO. It does not change dispatcher topology, lane scoring, OPS lifecycle semantics, or production deployment behavior.

## Claim

Prime Builder proposes to eliminate visible Windows console flashes in AUQ-adjacent UserPromptSubmit, owner-decision, and hook child process paths by routing child helpers through `pythonw.exe`, `CREATE_NO_WINDOW`, `Start-Process -WindowStyle Hidden`, or existing no-window wrappers, and by adding static and Windows-oriented regression coverage.

## Requirement Sufficiency

Existing requirements sufficient.

Existing Windows no-console and dispatcher architecture constraints are sufficient for this bounded defect fix. No new requirement is needed before implementation because the owner observation is a concrete runtime defect against existing headless/background-launch expectations.

## In-Root Placement Evidence

All implementation outputs, hook updates, tests, generated diagnostics, and bridge artifacts for this proposal remain under the GT-KB project root `E:/GT-KB`. The status-bearing bridge proposal is filed under `E:/GT-KB/bridge/gtkb-auq-headless-hook-launch-hygiene-001.md`. No Agent Red application source or external archive path is in scope.

## OPS Consolidation Integration

This proposal is a Wave 1 operational hygiene child under the same OPS dispatcher modernization parent. It does not implement OPS lifecycle state or lane-scoring schema, but it keeps the owner-decision/AUQ path usable while those larger dispatcher changes move through review.

The fix also supports the OPS model's artifact-centric workflow: owner decisions and AUQ processing should not spawn visible interactive console windows as a side effect of governed artifact creation or dispatch preparation.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` - requires protected hook/config/source changes to proceed through bridge proposal, GO, implementation report, and verification.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - requires project authorization, project, work item, and target path metadata.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - requires concrete governing specification links.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - requires verification mapped to cited specifications.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - keeps this platform work inside GT-KB and out of Agent Red application source.
- `DCL-SINGLE-HARNESS-DISPATCHER-DESKTOP-TASK-001` - establishes Windows non-interactive no-console launch discipline for dispatcher wake paths.
- `ADR-DISPATCHER-ARCHITECTURE-001` - dispatcher and hook helpers must preserve daemon-owned dispatch semantics and avoid harness-side control-plane behavior.
- `ADR-CROSS-HARNESS-PARITY-001` - hook/harness launch changes must consider parity across Codex, Claude, Cursor, and other relevant harness surfaces.
- `DCL-CROSS-HARNESS-PARITY-ENFORCEMENT-001` - requires explicit cross-harness disposition when harness-specific hook/config paths are touched.

## Prior Deliberations

- `DELIB-20260702-AUQ-ADJACENT-CONSOLE-WINDOWS-HEADLESS-REQUIREMENT` - owner observed two short-lived console windows after each AUQ and directed headless behavior.
- `DELIB-20260702-DISPATCH-OPS-WAVE1-FILE-ALL-PRIORITIZE-AUQ-HEADLESS` - owner selected filing all three Wave 1 proposals together and prioritizing AUQ/headless hygiene first if GO-approved.
- `DELIB-20260702-DISPATCH-OPS-WAVE1-THREE-CHILD-PROPOSALS` - Wave 1 uses three child implementation proposals.
- `DELIB-20260702-DISPATCH-OPS-CREATE-ACTUAL-PROJECT-WIS-BRIDGE-PROPOSALS` - owner selected actual governed project/work-item/bridge proposal creation.
- `DELIB-20260702-DISPATCH-OPS-FOUNDATION-FIRST-IMPLEMENTATION-WAVE` - Wave 1 includes OPS foundation, lane-scoring foundation, and AUQ/headless hygiene.
- `DELIB-20260702-DISPATCH-LANE-SCORING-EXTENDS-OPS-LIFECYCLE-CONSOLIDATION` - current program folds into OPS lifecycle consolidation.
- `DELIB-20266297` - prior owner directive and authorization for WI-4896 console-window suppression.

## Owner Decisions / Input

- `DELIB-20260702-AUQ-ADJACENT-CONSOLE-WINDOWS-HEADLESS-REQUIREMENT` - owner reported the AUQ-adjacent two-console-window symptom and requested headless behavior.
- `DELIB-20260702-DISPATCH-OPS-CREATE-ACTUAL-PROJECT-WIS-BRIDGE-PROPOSALS` - owner selected actual project, WI, and bridge proposal creation.
- `PAUTH-PROJECT-GTKB-AUQ-HEADLESS-HOOK-HYGIENE-WI-4959` - active child-project authorization for this work item.

## Proposed Scope

- Audit AUQ-adjacent UserPromptSubmit, owner-decision, workstream-focus, session-start/stop, and hook batch child launch surfaces for visible Windows console allocation.
- Replace bare `python`, visible `cmd.exe`, visible `powershell.exe`, or unhidden `.cmd` child launches with `pythonw.exe`, `CREATE_NO_WINDOW`, `Start-Process -WindowStyle Hidden`, or the existing no-window wrappers.
- Update Codex hook batches and `.cmd` adapters so the wrapper being launched by `pythonw.exe` does not spawn console-attached child Python processes.
- Review Claude and Cursor hook surfaces for equivalent AUQ/UserPromptSubmit owner-decision paths and either fix them or document an explicit no-equivalent/no-change parity disposition.
- Add static tests that detect bare console-attached Python/shell usage in hook adapters participating in AUQ/UserPromptSubmit and owner-decision flows.
- Add or document a Windows smoke check that demonstrates no short-lived console windows appear after an AUQ answer.

## Cross-Harness Disposition

- Codex harness A: in scope. `.codex/hooks.json` and `.codex/gtkb-hooks` are the primary observed surfaces; static scan found `.cmd` adapters invoking bare `python` under a `run_py_no_window` batch.
- Claude Code harness B: in scope for audit and parity disposition. `.claude/hooks` owner-decision/AUQ-adjacent paths must be checked and fixed if they spawn visible Windows consoles.
- Cursor harness E: in scope for audit and parity disposition. `.cursor` hook configuration and existing cursor headless parity tests must be checked for equivalent launch behavior.
- OpenRouter/Ollama provider harnesses: no direct local hook config is expected, but shared dispatcher/hook helper changes must not regress provider-harness launch behavior.
- Retired Antigravity C: no new parity work unless active repo-managed hook surfaces still reference it.

## Out Of Scope

- Dispatcher topology changes.
- OPS lifecycle/protocol implementation; that is `WI-4957`.
- Lane-scoring registry/projection schema; that is `WI-4958`.
- Credential lifecycle changes or production deployment.
- Agent Red application source mutation.

## Specification-Derived Verification Plan

| Spec | Verification |
| --- | --- |
| `DCL-SINGLE-HARNESS-DISPATCHER-DESKTOP-TASK-001` | Static and Windows-oriented tests prove AUQ-adjacent hook child processes use no-window launch mechanisms and do not allocate visible console windows. |
| `ADR-DISPATCHER-ARCHITECTURE-001` | Tests and source review prove the fix is launcher hygiene only and does not reintroduce harness-triggered dispatch or dispatcher topology changes. |
| `ADR-CROSS-HARNESS-PARITY-001` | Cross-harness parity tests or documented dispositions cover Codex, Claude, Cursor, provider harnesses, and retired Antigravity. |
| `DCL-CROSS-HARNESS-PARITY-ENFORCEMENT-001` | Implementation report includes a non-empty cross-harness disposition because harness-specific hook/config paths are in target scope. |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | Target-path and preflight checks prove all mutations are in GT-KB platform paths and no Agent Red application source is changed. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | Implementation report maps each hook/launcher behavior change to targeted tests and, where possible, a Windows smoke check. |

Required focused checks include `platform_tests/scripts/test_codex_hook_runtime_containment.py`, `platform_tests/scripts/test_codex_hook_parity.py`, `platform_tests/scripts/test_cursor_hook_headless_parity.py`, `platform_tests/scripts/test_workstream_focus_hook_parity.py`, and `platform_tests/scripts/test_windows_subprocess.py`, plus any new AUQ-specific static test added by the implementation.

## Acceptance Criteria

- AUQ-adjacent Codex hook child adapters do not invoke bare console-attached `python` or visible shell windows on Windows.
- Owner-decision/UserPromptSubmit hook batches use no-window launch wrappers end to end, including child `.cmd` adapters.
- Claude and Cursor equivalent surfaces are fixed or explicitly documented as no-equivalent/no-change with evidence.
- Regression tests fail if AUQ/UserPromptSubmit/owner-decision hook adapters reintroduce visible console-attached child launches.
- Windows smoke evidence or a justified equivalent proves the two short-lived console windows no longer appear after an AUQ answer.
- No dispatcher topology, lane-scoring, production deployment, or Agent Red source behavior changes are included.

## Risks / Rollback

Risk is low to moderate. The main risk is hiding diagnostic output that hooks previously inherited from visible child consoles. Mitigation: preserve captured stdout/stderr where needed and write diagnostics to existing hook output files.

Rollback is a normal source/config/test revert for hook wrappers and parity tests. Bridge files and project authorization records remain append-only audit history.

## Files Expected To Change

- `.codex/hooks.json`
- `.codex/gtkb-hooks/`
- `.claude/hooks/`
- `.cursor/`
- `scripts/windows_subprocess.py`
- `scripts/check_codex_hook_parity.py`
- `platform_tests/scripts/test_codex_hook_runtime_containment.py`
- `platform_tests/scripts/test_codex_hook_parity.py`
- `platform_tests/scripts/test_cursor_hook_headless_parity.py`
- `platform_tests/scripts/test_workstream_focus_hook_parity.py`
- `platform_tests/scripts/test_windows_subprocess.py`

## Recommended Commit Type

`fix`
