NEW

# gtkb-wi4906-harness-release-health-probes - Implementation Report

bridge_kind: implementation_report
Document: gtkb-wi4906-harness-release-health-probes
Version: 003
Author: Prime Builder (Codex harness A)
Date: 2026-06-29T09:45:48Z

author_identity: prime-builder/codex/A
author_harness_id: A
author_session_context_id: 019f09c9-2db0-7b00-a337-40f998b07e56
author_model: GPT-5 Codex
author_model_version: 2026-06
author_model_configuration: Codex Desktop, approval_policy=never, cwd=E:\GT-KB

Project Authorization: PAUTH-PROJECT-HARNESS-PARITY-PHASE-2-IMPLEMENTATION-2026-06-29
Project: PROJECT-HARNESS-PARITY-PHASE-2
Work Item: WI-4906

Responds to: bridge/gtkb-wi4906-harness-release-health-probes-002.md
Implementation claim: active work-intent claim for gtkb-wi4906-harness-release-health-probes, session 019f09c9-2db0-7b00-a337-40f998b07e56.
Implementation authorization: active packet validated for the six GO-approved source/test paths.

## Summary

Implemented the bounded WI-4906 release-health probe alignment slice. The Phase 2 evaluator now recognizes explicit wrapper-level Windows no-window evidence instead of requiring literal no-window tokens in registry argv, and Codex/Claude have deterministic static readiness probe scripts. The focused tests cover the new no-window evidence path and the new probe behavior.

This report intentionally separates this verified slice from remaining release blockers. The Phase 2 strict matrix still fails, but the remaining release-blocking findings are real dispatcher receive gaps for Antigravity, Claude, and Cursor. Event-source gaps remain non-release-blocking findings.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` - Requires proposal, GO, implementation report, and verification for protected source/test changes.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - Requires proposal/report linkage to governing requirements and spec-derived verification.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - Requires Project Authorization, Project, and Work Item metadata.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - Requires executed tests derived from linked specifications.
- `GOV-STANDING-BACKLOG-001` - Requires residual parity gaps to stay visible in MemBase/project work items rather than scratch state.
- `DCL-CROSS-HARNESS-ENFORCEMENT-001` - Requires cross-harness readiness/no-window gaps to be explicitly evaluated, corrected, or waived.
- `ADR-DISPATCHER-ARCHITECTURE-001` - Constrains dispatcher readiness evidence and release-health evaluation.
- `GOV-RELEASE-READINESS-GOVERNED-TESTING-001` - Requires governed release-readiness evidence before treating harness parity as release-healthy.
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` - Binds implementation to the active project authorization and bridge GO.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` - Keeps release-health claims in governed bridge/test artifacts.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` - Supports executable probe artifacts over prose-only readiness claims.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - Keeps residual gaps routed to work-item/waiver lifecycle surfaces.

## Prior Deliberations

- `bridge/gtkb-wi4906-harness-release-health-probes-001.md` - Proposal scope and verification plan.
- `bridge/gtkb-wi4906-harness-release-health-probes-002.md` - Loyal Opposition GO verdict.
- `DELIB-20260629-HARNESS-PARITY-PHASE-2-OWNER-DIRECTIVE` - Owner directive making Harness Parity Phase 2 release-blocking.

## Owner Decisions / Input

No new owner decision was required for this implementation report. The implementation stayed inside `PAUTH-PROJECT-HARNESS-PARITY-PHASE-2-IMPLEMENTATION-2026-06-29` and WI-4906's GO-approved target scope.

## Files Changed

- `scripts/harness_parity_phase2.py`
  - Added an explicit per-harness no-window evidence map.
  - Added wrapper-file evidence scanning for `CREATE_NO_WINDOW`, `run_cmd_no_window`, `WindowStyle`, and related no-window markers.
  - Updated the no-window evaluator to report wrapper-backed support with concrete evidence paths.
- `scripts/verify_codex_dispatch.py`
  - Added a deterministic Codex readiness probe that validates registry record, headless argv, executable resolution, static readiness, and dispatchability posture.
- `scripts/verify_claude_dispatch.py`
  - Added the matching Claude readiness probe. It reports static readiness separately from dispatchability, so a suspended Claude harness can be executable-present without being treated as dispatchable.
- `platform_tests/scripts/test_harness_parity_phase2.py`
  - Added a regression proving wrapper-level no-window evidence satisfies the no-window dimension.
- `platform_tests/scripts/test_verify_codex_dispatch.py`
  - Added Codex readiness probe tests for dispatchable, missing executable, and wrong-harness-type cases.
- `platform_tests/scripts/test_verify_claude_dispatch.py`
  - Added Claude readiness probe tests for suspended/static-ready, active/dispatchable, and wrong-harness-type cases.

Scoped diff evidence:

```text
platform_tests/scripts/test_harness_parity_phase2.py | 17 ++++++++
scripts/harness_parity_phase2.py                    | 48 +++++++++++++++++++++-
scripts/verify_codex_dispatch.py                    | 92 new lines
scripts/verify_claude_dispatch.py                   | 92 new lines
platform_tests/scripts/test_verify_codex_dispatch.py | 50 new lines
platform_tests/scripts/test_verify_claude_dispatch.py | 49 new lines
```

## Spec-To-Test Mapping

| Specification | Verification evidence |
| --- | --- |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | Latest bridge status was GO, work-intent claim was acquired, and implementation authorization validated the six approved paths before protected edits. |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | This report carries forward all proposal-linked specifications. |
| `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` | Report includes Project Authorization, Project, and Work Item metadata. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | Focused pytest, ruff, format, matrix, probe, and no-window audit evidence below. |
| `GOV-STANDING-BACKLOG-001` | Remaining strict-matrix gaps are still emitted as candidate work items rather than suppressed. |
| `DCL-CROSS-HARNESS-ENFORCEMENT-001` | Phase 2 evaluator now classifies readiness/no-window state from deterministic file/probe evidence. |
| `ADR-DISPATCHER-ARCHITECTURE-001` | Probe scripts expose static readiness and dispatchability posture separately. |
| `GOV-RELEASE-READINESS-GOVERNED-TESTING-001` | Release-health evidence is executable and repeatable. |
| `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` | Authorization validate returned authorized for the six target paths. |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | Release-health claims are preserved in bridge report and tests. |
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | New probe scripts are executable artifacts. |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | Residual gaps remain visible in matrix findings/candidate work items. |

## Commands Executed

```text
groundtruth-kb\.venv\Scripts\python.exe scripts\implementation_authorization.py validate --target scripts\harness_parity_phase2.py --target scripts\verify_codex_dispatch.py --target scripts\verify_claude_dispatch.py --target platform_tests\scripts\test_harness_parity_phase2.py --target platform_tests\scripts\test_verify_codex_dispatch.py --target platform_tests\scripts\test_verify_claude_dispatch.py
exit 0
Observed: authorized true for all six targets.
```

```text
groundtruth-kb\.venv\Scripts\python.exe -m pytest platform_tests\scripts\test_harness_parity_phase2.py platform_tests\scripts\test_verify_codex_dispatch.py platform_tests\scripts\test_verify_claude_dispatch.py -q --tb=short
exit 0
Observed: 15 passed in 0.73s.
```

```text
groundtruth-kb\.venv\Scripts\python.exe -m ruff check scripts\harness_parity_phase2.py scripts\verify_codex_dispatch.py scripts\verify_claude_dispatch.py platform_tests\scripts\test_harness_parity_phase2.py platform_tests\scripts\test_verify_codex_dispatch.py platform_tests\scripts\test_verify_claude_dispatch.py
exit 0
Observed: All checks passed.
```

```text
groundtruth-kb\.venv\Scripts\python.exe -m ruff format --check scripts\harness_parity_phase2.py scripts\verify_codex_dispatch.py scripts\verify_claude_dispatch.py platform_tests\scripts\test_harness_parity_phase2.py platform_tests\scripts\test_verify_codex_dispatch.py platform_tests\scripts\test_verify_claude_dispatch.py
exit 0
Observed: 6 files already formatted.
```

```text
groundtruth-kb\.venv\Scripts\python.exe scripts\harness_parity_phase2.py --project-root . --format markdown --strict
exit 1
Observed: Overall status FAIL; Counts: blocked: 4, needs_adapter: 4, supported: 52.
Remaining release-blocking findings: Antigravity dispatcher receive blocked, Claude dispatcher receive blocked, Cursor dispatcher receive needs_adapter.
Remaining non-release-blocking findings: event-source gaps for Antigravity, Claude, Cursor, Ollama, and OpenRouter.
```

```text
groundtruth-kb\.venv\Scripts\python.exe scripts\windows_no_window_spawn_audit.py scripts\cross_harness_bridge_trigger.py scripts\ollama_harness.py scripts\openrouter_harness.py scripts\cursor_harness.py scripts\verify_codex_dispatch.py scripts\verify_claude_dispatch.py --json
exit 0
Observed: release_ready true; violation_count 0; 8 compliant_no_window findings.
Note: the approved proposal named a `--release-runtime` flag, but the current audit CLI exposes path arguments rather than that flag. The command above is the path-scoped equivalent for the approved launcher surfaces.
```

```text
groundtruth-kb\.venv\Scripts\python.exe scripts\verify_codex_dispatch.py --json
exit 0
Observed: static_ok true; dispatchable true; resolved_executable C:\Users\micha\AppData\Local\OpenAI\Codex\bin\codex.EXE.
```

```text
groundtruth-kb\.venv\Scripts\python.exe scripts\verify_claude_dispatch.py --json
exit 0
Observed: static_ok true; dispatchable false; status suspended; resolved_executable C:\Users\micha\.local\bin\claude.EXE.
```

```text
git diff --check -- scripts\harness_parity_phase2.py scripts\verify_codex_dispatch.py scripts\verify_claude_dispatch.py platform_tests\scripts\test_harness_parity_phase2.py platform_tests\scripts\test_verify_codex_dispatch.py platform_tests\scripts\test_verify_claude_dispatch.py bridge\gtkb-wi4906-harness-release-health-probes-001.md
exit 0
Observed: no whitespace errors; Git emitted existing Windows LF-to-CRLF warnings for two touched files.
```

## Acceptance Status

- No-window evaluator gaps for Codex, Claude, Antigravity, Cursor, Ollama, and OpenRouter are no longer reported by the strict matrix when wrapper evidence exists.
- Codex and Claude readiness probe scripts exist and have focused tests.
- Codex static readiness is true and dispatchable under current registry state.
- Claude static readiness is true but dispatchable false because the registry still marks Claude suspended/cannot-receive-dispatch.
- The strict matrix now fails only on true dispatcher receive gaps and non-release-blocking event-source gaps.

## Recommended Commit Type

Recommended commit type: `fix:`

`fix:` is appropriate because this repairs release-health classification and missing deterministic probes for existing harnesses.

## Risk / Rollback

Risk is false-positive release readiness if wrapper evidence is matched too broadly. The implementation mitigates that by using an explicit harness-to-evidence-path map and focused tests. Rollback is a single commit reverting the six scoped source/test files and this report/proposal chain if LO finds misclassification.

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
