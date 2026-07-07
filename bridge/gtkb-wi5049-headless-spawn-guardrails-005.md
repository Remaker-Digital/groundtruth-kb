NEW
author_identity: prime-builder/codex
author_harness_id: A
author_session_context_id: 019f3170-d706-77d3-b3e1-be39d47f3eda
author_model: GPT-5 Codex
author_model_version: gpt-5
author_model_configuration: interactive Prime Builder session; Codex desktop execution

# GT-KB Bridge Implementation Report - gtkb-wi5049-headless-spawn-guardrails - 003

bridge_kind: implementation_report
Document: gtkb-wi5049-headless-spawn-guardrails
Version: 003 (NEW; post-implementation report)
Responds to GO: bridge/gtkb-wi5049-headless-spawn-guardrails-002.md
Approved proposal: bridge/gtkb-wi5049-headless-spawn-guardrails-001.md
Project Authorization: PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-WI5049-HEADLESS-SPAWN-20260707
Project: PROJECT-GTKB-RELIABILITY-FIXES
Work Item: WI-5049
Recommended commit type: fix:

## Implementation Claim

WI-5049 is implemented for the approved target paths. The repair closes the two remaining spawn-guardrail gaps from the GO verdict:

- `scripts/codex_mcp_worker_guard.py` now runs its Windows PowerShell process listing, POSIX `ps`, and Windows `taskkill.exe` subprocesses through `no_window_subprocess_kwargs()`, so the MCP worker guard does not create visible console windows when launched as background/runtime tooling.
- `scripts/windows_no_window_spawn_audit.py` now classifies `scripts/codex_mcp_worker_guard.py` as release runtime, so future missing `CREATE_NO_WINDOW` regressions in that guard fail the release readiness audit instead of being treated as non-runtime tooling.
- `groundtruth-kb/src/groundtruth_kb/enforcement/__init__.py` now blocks direct `.py` helper-script command heads and `Start-Process` targets under GT-KB harness helper locations while preserving explicit `python helper.py` invocation. This closes the direct file-association route that can launch helper scripts through the OS or Cursor instead of the governed interpreter path.
- Focused tests cover the release-runtime audit classification, MCP worker guard no-window kwargs, direct helper-script denial, explicit-python allowance, and Codex/Claude hook coverage for the direct-helper block.

## In-Root Placement Evidence

- Project root: `E:\GT-KB`
- All edited implementation/test files are under `E:\GT-KB`.
- Bridge report filing uses the governed bridge helper and writes the next numbered file under `E:\GT-KB\bridge\`.
- Implementation authorization packet was opened with `python scripts/implementation_authorization.py begin --bridge-id gtkb-wi5049-headless-spawn-guardrails --expires-minutes 120`.
- The active claim for `gtkb-wi5049-headless-spawn-guardrails` was acquired by Prime Builder session `019f3170-d706-77d3-b3e1-be39d47f3eda` and extended through `2026-07-07T19:21:22Z`.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` - Protected source/test edits require live bridge authority and the numbered bridge chain remains canonical.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - The approved proposal cites concrete governing specs, target paths, PAUTH, project, and work item metadata.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - The proposal/report retain `Project Authorization`, `Project`, and `Work Item` linkage.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - This report maps linked specifications to executed test and audit evidence.
- `GOV-STANDING-BACKLOG-001` - WI-5049 remains tied to the governed backlog and reliability project.
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` - The bounded PAUTH is project/work-item scoped and paired with bridge GO plus implementation-start evidence.
- `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001` - Implementation occurred only after bridge GO, claim, and implementation-start authorization.
- `DCL-SINGLE-HARNESS-DISPATCHER-DESKTOP-TASK-001` - Background/scheduled Windows GT-KB surfaces must avoid visible console windows.
- `SPEC-INTAKE-21c5b3` - Direct harness-to-harness invocation and bypass launch paths require mechanical enforcement.
- `ADR-CROSS-HARNESS-PARITY-001` - Equivalent harness-observable guardrail behavior is maintained across Codex and Claude hook surfaces.
- `DCL-CROSS-HARNESS-PARITY-ENFORCEMENT-001` - Harness-surface changes include parity coverage rather than silently changing one harness.

## Owner Decisions / Input

No new owner decision is required by this implementation report.

## Prior Deliberations

- `bridge/gtkb-wi5049-headless-spawn-guardrails-001.md` - Approved Prime Builder implementation proposal.
- `bridge/gtkb-wi5049-headless-spawn-guardrails-002.md` - Loyal Opposition GO verdict authorizing implementation.

## Specification-Derived Verification Plan

| Spec / governing surface | Executed verification evidence |
| --- | --- |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | `python scripts/bridge_claim_cli.py status gtkb-wi5049-headless-spawn-guardrails`; `python scripts/bridge_applicability_preflight.py --bridge-id gtkb-wi5049-headless-spawn-guardrails --json`; `python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-wi5049-headless-spawn-guardrails` |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | Bridge applicability preflight returned `preflight_passed: true` and `missing_required_specs: []`. |
| `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` | Report metadata carries PAUTH, project, and work item from the approved proposal. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | Focused pytest, ruff, format, audit, and preflight commands below were executed and mapped to the linked requirements. |
| `GOV-STANDING-BACKLOG-001` | This implementation remains scoped to `PROJECT-GTKB-RELIABILITY-FIXES` / `WI-5049`. |
| `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` | `python scripts/implementation_authorization.py begin --bridge-id gtkb-wi5049-headless-spawn-guardrails --expires-minutes 120` succeeded, and target validation was run for each approved target before edits. |
| `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001` | Edits were made only after the live GO, claim, applicability preflight, clause preflight, and implementation-start packet were present. |
| `DCL-SINGLE-HARNESS-DISPATCHER-DESKTOP-TASK-001` | `platform_tests/scripts/test_windows_no_window_spawn_audit.py` and `platform_tests/scripts/test_codex_mcp_worker_guard.py` verify no-window subprocess handling and release-runtime audit coverage. |
| `SPEC-INTAKE-21c5b3` | `groundtruth-kb/tests/framework/test_bash_enforcement_parser.py` verifies direct helper `.py` launch blocking and explicit Python invocation allowance. |
| `ADR-CROSS-HARNESS-PARITY-001` | `platform_tests/scripts/test_fab14_directive_hook_coverage.py` verifies the direct-helper block through Codex Bash and Claude PowerShell hook paths. |
| `DCL-CROSS-HARNESS-PARITY-ENFORCEMENT-001` | Cross-harness Codex/Claude hook coverage was added for the enforcement path touched by this repair. |

## Commands Run

- `python scripts/bridge_applicability_preflight.py --bridge-id gtkb-wi5049-headless-spawn-guardrails --json`
- `python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-wi5049-headless-spawn-guardrails`
- `python scripts/implementation_authorization.py begin --bridge-id gtkb-wi5049-headless-spawn-guardrails --expires-minutes 120`
- `python scripts/implementation_authorization.py validate --bridge-id gtkb-wi5049-headless-spawn-guardrails --target <each of the seven approved source/test targets>`
- `python -m pytest platform_tests/scripts/test_windows_no_window_spawn_audit.py platform_tests/scripts/test_codex_mcp_worker_guard.py groundtruth-kb/tests/framework/test_bash_enforcement_parser.py platform_tests/scripts/test_fab14_directive_hook_coverage.py -q --tb=short`
- `python -m ruff check scripts/windows_no_window_spawn_audit.py platform_tests/scripts/test_windows_no_window_spawn_audit.py scripts/codex_mcp_worker_guard.py platform_tests/scripts/test_codex_mcp_worker_guard.py groundtruth-kb/src/groundtruth_kb/enforcement/__init__.py groundtruth-kb/tests/framework/test_bash_enforcement_parser.py platform_tests/scripts/test_fab14_directive_hook_coverage.py`
- `python -m ruff format --check scripts/windows_no_window_spawn_audit.py platform_tests/scripts/test_windows_no_window_spawn_audit.py scripts/codex_mcp_worker_guard.py platform_tests/scripts/test_codex_mcp_worker_guard.py groundtruth-kb/src/groundtruth_kb/enforcement/__init__.py groundtruth-kb/tests/framework/test_bash_enforcement_parser.py platform_tests/scripts/test_fab14_directive_hook_coverage.py`
- `python scripts/windows_no_window_spawn_audit.py --json`

## Observed Results

- Bridge applicability preflight: `preflight_passed: true`; `missing_required_specs: []`.
- ADR/DCL clause preflight: 5 clauses evaluated; `must_apply: 3`; blocking gaps: 0; exit 0.
- Implementation authorization: begin packet created and each approved target validated before edits.
- Focused pytest: 35 passed.
- Ruff check: all checks passed.
- Ruff format check: 7 files already formatted after applying ruff formatting to the edited enforcement file.
- Windows no-window spawn audit: `release_ready: true`; `violation_count: 0`; 71 compliant no-window findings, 120 interactive allowlist findings, 480 non-release-runtime findings.

## Files Changed

- `scripts/windows_no_window_spawn_audit.py`
- `platform_tests/scripts/test_windows_no_window_spawn_audit.py`
- `scripts/codex_mcp_worker_guard.py`
- `platform_tests/scripts/test_codex_mcp_worker_guard.py`
- `groundtruth-kb/src/groundtruth_kb/enforcement/__init__.py`
- `groundtruth-kb/tests/framework/test_bash_enforcement_parser.py`
- `platform_tests/scripts/test_fab14_directive_hook_coverage.py`

## Worktree Scope Note

The repository has unrelated pre-existing dirty worktree changes. This report is intentionally scoped to the seven WI-5049 approved target paths above and excludes unrelated files listed by the initial scaffold.

## Acceptance Criteria Status

- [x] Release runtime no-window audit covers `scripts/codex_mcp_worker_guard.py`.
- [x] MCP worker guard subprocess calls use no-window kwargs.
- [x] Direct `.py` helper-script file association launches are blocked for governed harness helper paths.
- [x] Explicit interpreter-based helper invocation remains allowed.
- [x] Codex and Claude hook surfaces have parity coverage for the direct-helper block.
- [x] Focused tests, lint, formatting check, bridge preflights, and no-window audit passed.

## Risk And Rollback

Residual risk is low and localized to command parsing around direct helper-script tokens. The implementation intentionally blocks only direct `.py` helper script command heads and `Start-Process` targets under known GT-KB harness helper directories, while allowing explicit `python` invocation.

Rollback is straightforward: revert the seven changed files listed above and keep the append-only bridge history intact.

## Loyal Opposition Asks

1. Verify the implementation against the approved proposal, linked specifications, and executed command evidence.
2. Return `VERIFIED` if the changes satisfy WI-5049, otherwise return `NO-GO` with concrete findings.
