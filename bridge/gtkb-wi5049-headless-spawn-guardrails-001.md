NEW

# gtkb-wi5049-headless-spawn-guardrails - Direct script and MCP no-window guardrails

bridge_kind: prime_proposal
Document: gtkb-wi5049-headless-spawn-guardrails
Version: 001
Author: Prime Builder (Codex A)
Date: 2026-07-07T17:10:00Z

author_identity: prime-builder/codex
author_harness_id: A
author_session_context_id: 019f337a-009a-7f51-8dce-b6c3f1d91b1c
author_model: GPT-5 Codex
author_model_version: gpt-5
author_model_configuration: Codex desktop interactive Prime Builder session; reasoning=xhigh; approval_policy=never

Project Authorization: PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-WI5049-HEADLESS-SPAWN-20260707
Project: PROJECT-GTKB-RELIABILITY-FIXES
Work Item: WI-5049

target_paths: ["scripts/windows_no_window_spawn_audit.py", "platform_tests/scripts/test_windows_no_window_spawn_audit.py", "scripts/codex_mcp_worker_guard.py", "platform_tests/scripts/test_codex_mcp_worker_guard.py", "groundtruth-kb/src/groundtruth_kb/enforcement/__init__.py", "groundtruth-kb/tests/framework/test_bash_enforcement_parser.py", "platform_tests/scripts/test_fab14_directive_hook_coverage.py"]

implementation_scope: source
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

---

## Summary

Owner-observed process evidence on 2026-07-07 isolated a recurring Windows
headless-spawn defect into two linked surfaces. First, a visible Cursor root
process existed with command line
`Cursor.exe E:\GT-KB\.claude\skills\verify\helpers\write_verdict.py`, which is
consistent with a GT-KB helper script being launched directly through Windows
file association instead of through Python or the governed no-window wrappers.
Second, after the owner's 09:53 local cutoff, no new root `Cursor.exe` process
appeared, but the already-open Cursor process launched `cmd.exe /c npx` child
chains for `@upstash/context7-mcp` and `@playwright/mcp@latest` at 09:55:57 and
09:56:02, producing the same short-lived console-prone `cmd`/`conhost` pattern.

This proposal authorizes a focused repair to GT-KB-owned guardrails: prevent
direct Python script file-association launches from bypassing the direct
harness-invocation boundary, tighten the Windows no-window spawn audit so
hook-invoked support scripts are not mislabeled as harmless interactive tooling,
and make the Codex MCP worker guard's own subprocess probes use the shared
no-window helper. It does not mutate external Cursor/user-profile MCP
configuration; the durable GT-KB fix is to stop accidentally opening Cursor and
to ensure GT-KB hook/audit subprocesses do not flash console windows.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` - Requires this protected source/hook/test repair to be proposed through the bridge and receive Loyal Opposition GO before implementation.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - Requires this proposal to cite the concrete governing requirements, PAUTH, work item, and target paths before review.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - Requires the `Project Authorization`, `Project`, and `Work Item` metadata above.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - Requires the eventual implementation report and verification verdict to map these requirements to executed tests and runtime evidence.
- `GOV-STANDING-BACKLOG-001` - Supports promoting the owner-observed recurring window-spawn defect into governed backlog/bridge work.
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` - Requires the bounded PAUTH used by this proposal to remain project-scoped and owner-backed.
- `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001` - Confirms the PAUTH does not authorize source edits without later bridge GO and implementation-start evidence.
- `DCL-SINGLE-HARNESS-DISPATCHER-DESKTOP-TASK-001` - Establishes the Windows no-visible-console expectation for scheduled/background GT-KB dispatch surfaces, including CREATE_NO_WINDOW style launch discipline.
- `SPEC-INTAKE-21c5b3` - Prohibits direct harness-to-harness invocation and requires mechanical enforcement; direct `.py` file association to Cursor is a bypass class of that same boundary.
- `ADR-CROSS-HARNESS-PARITY-001` - Requires equivalent harness-observable behavior where the direct-invocation and hook no-window guardrails apply across Codex/Claude surfaces.
- `DCL-CROSS-HARNESS-PARITY-ENFORCEMENT-001` - Requires proposals touching harness-surface files to declare cross-harness disposition rather than silently changing one harness.

## Prior Deliberations

- `DELIB-202665869` - Owner authorized the WI-5049 durable headless-spawn repair after the 2026-07-07 Cursor/write_verdict.py and post-09:53 MCP child-process evidence.
- `DELIB-20260702-AUQ-ADJACENT-CONSOLE-WINDOWS-HEADLESS-REQUIREMENT` - Earlier owner decision requiring AUQ-adjacent hook and decision-capture launches to be headless on Windows.
- `DELIB-20260707-WI5037-IMPLEMENTATION-APPROVAL` - Adjacent owner authorization for WI-5037, the direct-invocation false-positive correction; this proposal must coordinate with that pending thread because both touch direct-invocation enforcement.
- `DELIB-S382-PROPOSAL-STANDARDS-COMPLETION-SCOPE` - Proposal scaffold and structural compliance expectations for bridge proposals.

## Owner Decisions / Input

Owner approval is `DELIB-202665869`, captured from the active session after
Mike reported that a Cursor window had opened on
`E:\GT-KB\.claude\skills\verify\helpers\write_verdict.py`, authorized Codex to
risk further spawns while fixing the issue, and then set the concrete
2026-07-07 09:53 local cutoff for diagnosis. The bounded PAUTH is
`PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-WI5049-HEADLESS-SPAWN-20260707`.

## Requirement Sufficiency

Existing requirements are sufficient. `DELIB-20260702-AUQ-ADJACENT-CONSOLE-WINDOWS-HEADLESS-REQUIREMENT`
requires Windows hook/helper launches to be headless, `DCL-SINGLE-HARNESS-DISPATCHER-DESKTOP-TASK-001`
establishes no-visible-console launch discipline for GT-KB background surfaces,
and `SPEC-INTAKE-21c5b3` requires mechanical enforcement against direct
harness-to-harness invocation. The new evidence identifies unclosed
implementation gaps in those existing requirements rather than a need for new
policy.

## Cross-Harness Disposition

Applicable harness surfaces: Codex and Claude PreToolUse direct-invocation
enforcement, Codex hook/runtime no-window audit surfaces, and Cursor as the
accidentally opened external GUI target. Cursor user-profile MCP configuration
is explicitly out of scope; this proposal controls GT-KB-owned launch and audit
behavior only.

Coordination note: `WI-5037` is already pending Loyal Opposition review for a
narrow correction to direct-invocation-ban false positives. This `WI-5049`
proposal adds the missing deny class surfaced by live evidence: executing a
GT-KB `.py` helper directly as a command head can route through Windows file
association and launch Cursor. If `WI-5037` receives GO first, implementation
must coordinate the shared enforcement tests/source with that GO rather than
landing duplicate or contradictory changes.

## Spec-Derived Verification Plan

Implementation must map each linked specification to focused tests and observed
runtime evidence. Use the repo venv interpreter for reproducible evidence:

```text
groundtruth-kb/.venv/Scripts/python.exe -m pytest platform_tests/scripts/test_windows_no_window_spawn_audit.py platform_tests/scripts/test_codex_mcp_worker_guard.py groundtruth-kb/tests/framework/test_bash_enforcement_parser.py platform_tests/scripts/test_fab14_directive_hook_coverage.py -q --no-header
groundtruth-kb/.venv/Scripts/python.exe scripts/windows_no_window_spawn_audit.py --json
```

Expected results:

- `SPEC-INTAKE-21c5b3`: direct harness launch denials still fire, and a command
  that executes `.claude/.codex/.cursor` Python helper files directly as the
  command head is denied or otherwise forced through `pythonw`/no-window
  wrappers instead of Windows file association.
- `DCL-SINGLE-HARNESS-DISPATCHER-DESKTOP-TASK-001` and
  `DELIB-20260702-AUQ-ADJACENT-CONSOLE-WINDOWS-HEADLESS-REQUIREMENT`:
  `scripts/codex_mcp_worker_guard.py` uses shared Windows no-window subprocess
  kwargs for its PowerShell/process-management children, and the audit treats
  hook-invoked support scripts as release-runtime surfaces when they are wired
  into `.codex/gtkb-hooks`.
- `GOV-FILE-BRIDGE-AUTHORITY-001`, `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001`,
  and `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001`: the implementation report
  cites this proposal, the PAUTH, the GO verdict, and the implementation-start
  packet before source/test changes are considered complete.
- `ADR-CROSS-HARNESS-PARITY-001` and `DCL-CROSS-HARNESS-PARITY-ENFORCEMENT-001`:
  Codex and Claude direct-invocation behavior remain equivalent for the covered
  deny/allow cases, with any intentional non-equivalence declared.

## Risk / Rollback

The main risk is over-blocking legitimate governed commands that mention or
inspect helper paths, especially while `WI-5037` is narrowing false positives in
the same enforcement family. The counter-risk is under-blocking direct helper
execution and allowing Windows file association to launch Cursor again. The MCP
worker guard change risks breaking stale-worker reporting if PowerShell process
collection is not exercised in tests.

Rollback is a single-commit revert of the implementation commit after
verification. No external Cursor settings, user-profile MCP config, credential
state, deployment, destructive cleanup, or git-history rewrite is in scope.

## Pre-Filing Checks

- Applicability preflight: `python scripts/bridge_applicability_preflight.py --bridge-id gtkb-wi5049-headless-spawn-guardrails --content-file .gtkb-state/propose-drafts/gtkb-wi5049-headless-spawn-guardrails-001.md --json` returned `preflight_passed: true`, `missing_required_specs: []`.
- Clause preflight: `python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-wi5049-headless-spawn-guardrails --content-file .gtkb-state/propose-drafts/gtkb-wi5049-headless-spawn-guardrails-001.md` exited 0 with blocking gaps `0`.
- Phantom-spec sweep: all cited `GOV`, `DCL`, `ADR`, `PB`, and `SPEC-INTAKE-21c5b3` ids resolved through `gt spec show`.
- `target_paths` parse check: inline JSON parsed to the seven intended protected source/test paths.
- Draft-marker scan: no scaffold markers remain.

## Bridge Filing

This proposal is filed under `bridge/` as the next status-bearing numbered
bridge file for `gtkb-wi5049-headless-spawn-guardrails`; no prior version is deleted or rewritten
(append-only). Dispatcher/TAFE state plus the numbered file chain are the live
workflow state per `GOV-FILE-BRIDGE-AUTHORITY-001`.

## Recommended Commit Type

fix(hooks) - repair Windows headless-spawn and direct-invocation guardrails.

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
