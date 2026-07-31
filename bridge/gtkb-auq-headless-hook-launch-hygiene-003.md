NEW
author_identity: prime-builder/codex
author_harness_id: A
author_session_context_id: 019f23f0-b16e-7481-8a18-9622ab564d50
author_model: GPT-5 Codex
author_model_version: GPT-5 Codex desktop runtime 2026-07-02
author_model_configuration: Codex desktop; E:/GT-KB; danger-full-access; approval-policy never; interactive role Prime Builder via ::init gtkb pb

# GT-KB Bridge Implementation Report - gtkb-auq-headless-hook-launch-hygiene - 003

bridge_kind: implementation_report
Document: gtkb-auq-headless-hook-launch-hygiene
Version: 003 (NEW; post-implementation report)
Responds to GO: bridge/gtkb-auq-headless-hook-launch-hygiene-002.md
Approved proposal: bridge/gtkb-auq-headless-hook-launch-hygiene-001.md
Project: PROJECT-GTKB-AUQ-HEADLESS-HOOK-HYGIENE
Work item: WI-4959
Exact-target amendment: bridge/gtkb-auq-headless-hook-launch-hygiene-exact-target-amendment-002.md
Recommended commit type: fix

## Implementation Claim

WI-4959 is implemented for the approved Codex hook launch hygiene slice. The Codex `.cmd` hook adapters that previously invoked console-attached `python` now invoke the project venv `pythonw.exe` with the existing `.codex/gtkb-hooks/run_py_no_window` launcher, preserving synchronous execution while routing hook Python children through the no-window containment path.

The implementation is launcher-only. It does not change AUQ policy logic, bridge status semantics, dispatcher selection, daemon ownership, work-intent claim logic, hook registration topology, or harness-state dispatch state.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` - protected hook/config/source changes require live bridge GO, work-intent claim, implementation-start authorization, implementation report, and verification.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - proposal/report chain carries project, work item, and target path linkage.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - implementation report carries forward governing specification links from the approved proposal and exact-target amendment.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - report maps cited specifications to executed tests and observed results.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - work remains in GT-KB platform hook/test paths, not Agent Red application source.
- `DCL-SINGLE-HARNESS-DISPATCHER-DESKTOP-TASK-001` - Windows launch paths use no-console `pythonw.exe`/launcher discipline.
- `ADR-DISPATCHER-ARCHITECTURE-001` - dispatcher daemon remains the owner of dispatch behavior; hook wrappers remain launch hygiene only.
- `ADR-CROSS-HARNESS-PARITY-001` - harness-facing launch changes are explicitly tested and cross-harness residuals are reported.
- `DCL-CROSS-HARNESS-PARITY-ENFORCEMENT-001` - Codex hook surface changes include parity disposition and evidence.
- `ADR-CODEX-HOOK-PARITY-FALLBACK-001` - Codex hook fallback remains batch-runner based; this changes only batch child wrapper launch mechanics.
- `SPEC-AUQ-POLICY-ENGINE-001` - AUQ policy remains centralized and unchanged.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`, `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`, `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - exact target expansion was handled through the bridge amendment, not an unrecorded scope shortcut.

## Owner Decisions / Input

No new owner decision is required by this implementation report. The owner authorized the build envelope for PROJECT-GTKB-OPS-DISPATCHER-MODERNIZATION and WI-4959 proceeded only after live LO `GO` on the parent and exact-target amendment threads.

## Prior Deliberations

- `bridge/gtkb-auq-headless-hook-launch-hygiene-001.md` - parent implementation proposal.
- `bridge/gtkb-auq-headless-hook-launch-hygiene-002.md` - LO `GO` authorizing the parent implementation scope.
- `bridge/gtkb-auq-headless-hook-launch-hygiene-exact-target-amendment-001.md` - exact-target amendment for the concrete Codex `.cmd` adapters.
- `bridge/gtkb-auq-headless-hook-launch-hygiene-exact-target-amendment-002.md` - LO `GO` authorizing the amended exact target paths.

## Architecture Alignment Ledger

| Alignment surface | Evidence |
| --- | --- |
| OPS consolidation | The slice reduces AUQ/headless hook launch friction without adding a new lifecycle state, queue, bridge runtime, or owner-facing decision surface. |
| Dispatcher daemon architecture | No dispatcher daemon, dispatch ranking, worker ownership, or bridge-claim behavior changed; wrappers only launch existing hook scripts through the no-window runner. |
| Lifecycle-first / scoring-last precedence | The implementation followed live bridge `GO` and claim gates before mutation; it does not introduce scoring, prioritization, or lane-rank behavior. |
| Portfolio reconciliation findings | WI-4960 portfolio cleanup found the canonical Wave 1 parent/child records to preserve; WI-4959 remained in the AUQ/headless launch hygiene child lane with no duplicate-project conflict blocking this slice. |
| Cross-harness parity | Codex wrappers now match the registry's no-window launcher discipline. Existing adjacent parity tests still fail on `.codex/hooks.json` batch aggregation expectations; that residual is outside this exact-target launcher slice and is reported below. |

## Implementation Details

Changed `.cmd` adapters:

- `.codex/gtkb-hooks/bridge-compliance-audit.cmd`
- `.codex/gtkb-hooks/bridge-compliance-gate-apply-patch-adapter.cmd`
- `.codex/gtkb-hooks/bridge-compliance-gate.cmd`
- `.codex/gtkb-hooks/code-quality-baseline-proposal-check.cmd`
- `.codex/gtkb-hooks/codex-mcp-worker-guard.cmd`
- `.codex/gtkb-hooks/credential-scan.cmd`
- `.codex/gtkb-hooks/destructive-gate.cmd`
- `.codex/gtkb-hooks/directive-enforcement.cmd`
- `.codex/gtkb-hooks/formal-artifact-approval.cmd`
- `.codex/gtkb-hooks/implementation-start-gate.cmd`
- `.codex/gtkb-hooks/lo-file-safety-gate.cmd`
- `.codex/gtkb-hooks/session-start.cmd`
- `.codex/gtkb-hooks/session-stop.cmd`
- `.codex/gtkb-hooks/wi-id-collision-gate.cmd`
- `.codex/gtkb-hooks/workstream-focus.cmd`

Each changed wrapper now invokes:

```text
E:\GT-KB\groundtruth-kb\.venv\Scripts\pythonw.exe E:\GT-KB\.codex\gtkb-hooks\run_py_no_window <hook-target.py> [args]
```

`session-start.cmd` required the batch-safe nested command form for the `for /f` harness-ID lookup:

```text
for /f "usebackq delims=" %%I in (`cmd /c ""E:\GT-KB\groundtruth-kb\.venv\Scripts\pythonw.exe" "E:\GT-KB\.codex\gtkb-hooks\run_py_no_window" "E:\GT-KB\scripts\harness_identity.py" --project-root "E:\GT-KB" resolve --harness-name codex"`) do set "GTKB_HARNESS_ID=%%I"
```

Test coverage added:

- `platform_tests/scripts/test_codex_hook_runtime_containment.py` now enumerates the exact Codex `.cmd` Python-hook wrapper set and asserts each wrapper uses the project `pythonw.exe`, uses `run_py_no_window`, and contains no bare console `python`/`py` command token.

## Specification-Derived Verification Plan

| Spec / governing surface | Executed verification evidence |
| --- | --- |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | Live parent and amendment threads were latest `GO`; both work-intent claims were held by session `019f23f0-b16e-7481-8a18-9622ab564d50`; `implementation_authorization.py list` showed both WI-4959 packets valid before mutation; exact-target preflights returned `verdict: in_scope`. |
| `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` | Helper `plan` for parent and amendment returned project-linked report version `003` and live `GO` inputs. |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | This report carries forward parent and amendment linked specifications and maps them to verification evidence. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | Focused pytest, static scan, lint, format, and Windows command smokes are recorded below. |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | Changed files are limited to `.codex/gtkb-hooks/*.cmd` and `platform_tests/scripts/test_codex_hook_runtime_containment.py`; no `applications/Agent_Red/` paths changed. |
| `DCL-SINGLE-HARNESS-DISPATCHER-DESKTOP-TASK-001` | Static scan found no bare console Python invocations in the target wrappers; runtime smoke confirmed a changed `.cmd` wrapper exits cleanly through `pythonw.exe`/`run_py_no_window`. |
| `ADR-DISPATCHER-ARCHITECTURE-001` | Existing containment test still verifies Codex hook registry uses hidden launchers and excludes retired dispatcher workers; this implementation did not edit dispatcher runtime/config. |
| `ADR-CROSS-HARNESS-PARITY-001` and `DCL-CROSS-HARNESS-PARITY-ENFORCEMENT-001` | Focused Codex wrapper regression passed; adjacent parity tests were run and their pre-existing `.codex/hooks.json` batch-aggregation failures are documented under residual risk. |
| `SPEC-AUQ-POLICY-ENGINE-001` | No AUQ policy files or AUQ decision logic changed; implementation is limited to hook child launch mechanics. |

## Commands Run

- `python scripts\implementation_authorization.py list`
- `python scripts\bridge_claim_cli.py status gtkb-auq-headless-hook-launch-hygiene`
- `python scripts\bridge_claim_cli.py status gtkb-auq-headless-hook-launch-hygiene-exact-target-amendment`
- `gt bridge threads --wi WI-4959 --json --compact`
- `python scripts\impl_start_target_paths_preflight.py --bridge-id gtkb-auq-headless-hook-launch-hygiene-exact-target-amendment --candidate-paths .codex/gtkb-hooks/bridge-compliance-audit.cmd .codex/gtkb-hooks/bridge-compliance-gate-apply-patch-adapter.cmd .codex/gtkb-hooks/bridge-compliance-gate.cmd .codex/gtkb-hooks/code-quality-baseline-proposal-check.cmd .codex/gtkb-hooks/codex-mcp-worker-guard.cmd .codex/gtkb-hooks/credential-scan.cmd .codex/gtkb-hooks/destructive-gate.cmd .codex/gtkb-hooks/directive-enforcement.cmd .codex/gtkb-hooks/formal-artifact-approval.cmd .codex/gtkb-hooks/implementation-start-gate.cmd .codex/gtkb-hooks/lo-file-safety-gate.cmd .codex/gtkb-hooks/session-start.cmd .codex/gtkb-hooks/session-stop.cmd .codex/gtkb-hooks/wi-id-collision-gate.cmd .codex/gtkb-hooks/workstream-focus.cmd platform_tests/scripts/test_codex_hook_runtime_containment.py --json`
- `python scripts\impl_start_target_paths_preflight.py --bridge-id gtkb-auq-headless-hook-launch-hygiene --candidate-paths platform_tests/scripts/test_codex_hook_runtime_containment.py --json`
- `cmd /c '"E:\GT-KB\groundtruth-kb\.venv\Scripts\pythonw.exe" "E:\GT-KB\.codex\gtkb-hooks\run_py_no_window" "E:\GT-KB\scripts\harness_identity.py" --project-root "E:\GT-KB" resolve --harness-name codex'`
- `cmd /c 'for /f "usebackq delims=" %I in (`cmd /c ""E:\GT-KB\groundtruth-kb\.venv\Scripts\pythonw.exe" "E:\GT-KB\.codex\gtkb-hooks\run_py_no_window" "E:\GT-KB\scripts\harness_identity.py" --project-root "E:\GT-KB" resolve --harness-name codex"`) do @echo %I'`
- `cmd /c .codex\gtkb-hooks\codex-mcp-worker-guard.cmd`
- `rg --pcre2 -n '(?i)(^|[`(\s])(?:python(?:\.exe)?|py(?:\.exe)?)(?=$|[\s\"])' <15 approved .cmd wrappers>`
- `python -m pytest platform_tests\scripts\test_codex_hook_runtime_containment.py -q --tb=short`
- `python -m ruff check platform_tests\scripts\test_codex_hook_runtime_containment.py`
- `python -m ruff format --check platform_tests\scripts\test_codex_hook_runtime_containment.py`
- `python -m pytest platform_tests\scripts\test_codex_hook_parity.py platform_tests\scripts\test_workstream_focus_hook_parity.py -q --tb=short`

## Observed Results

- Parent/amendment bridge status: `WI-4959` had two matching threads, both latest `GO`.
- Parent claim: held by session `019f23f0-b16e-7481-8a18-9622ab564d50`, latest status `GO`, not expired; extended to `ttl_expires_at: 2026-07-02T21:41:34Z`.
- Amendment claim: held by the same session, latest status `GO`, not expired; extended to `ttl_expires_at: 2026-07-02T21:35:53Z`.
- Implementation authorization: parent and exact-target amendment packets were `valid: true` before mutation.
- Exact-target preflight: all 16 amended candidates in scope, 0 out of scope.
- Parent target preflight: `platform_tests/scripts/test_codex_hook_runtime_containment.py` in scope.
- Direct `pythonw.exe` command smoke returned harness ID `A`.
- `for /f` batch command-substitution smoke returned harness ID `A`.
- `codex-mcp-worker-guard.cmd` exited `0` through the new launcher path.
- Static bare-console-Python scan returned no matches. Ripgrep exit code was `1`, which is the no-match result for this scan.
- `python -m pytest platform_tests\scripts\test_codex_hook_runtime_containment.py -q --tb=short`: `10 passed`.
- `python -m ruff check platform_tests\scripts\test_codex_hook_runtime_containment.py`: all checks passed.
- `python -m ruff format --check platform_tests\scripts\test_codex_hook_runtime_containment.py`: 1 file already formatted.
- Adjacent parity command completed with `7 failed, 13 passed`. Failures are existing `.codex/hooks.json` batch-aggregation/parity expectations such as missing direct workstream-focus and bridge-compliance registration fragments; this implementation did not edit `.codex/hooks.json`, and the focused wrapper containment test verifies the current batch catalog still includes the relevant wrapper targets.

## Files Changed

- `.codex/gtkb-hooks/bridge-compliance-audit.cmd`
- `.codex/gtkb-hooks/bridge-compliance-gate-apply-patch-adapter.cmd`
- `.codex/gtkb-hooks/bridge-compliance-gate.cmd`
- `.codex/gtkb-hooks/code-quality-baseline-proposal-check.cmd`
- `.codex/gtkb-hooks/codex-mcp-worker-guard.cmd`
- `.codex/gtkb-hooks/credential-scan.cmd`
- `.codex/gtkb-hooks/destructive-gate.cmd`
- `.codex/gtkb-hooks/directive-enforcement.cmd`
- `.codex/gtkb-hooks/formal-artifact-approval.cmd`
- `.codex/gtkb-hooks/implementation-start-gate.cmd`
- `.codex/gtkb-hooks/lo-file-safety-gate.cmd`
- `.codex/gtkb-hooks/session-start.cmd`
- `.codex/gtkb-hooks/session-stop.cmd`
- `.codex/gtkb-hooks/wi-id-collision-gate.cmd`
- `.codex/gtkb-hooks/workstream-focus.cmd`
- `platform_tests/scripts/test_codex_hook_runtime_containment.py`
- `independent-progress-assessments/CODEX-INSIGHT-DROPBOX/OPS-AUQ-HEADLESS-HOOK-LAUNCH-HYGIENE-IMPLEMENTATION-2026-07-02.md`

## Recommended Commit Type

- Recommended commit type: `fix`
- Justification: the slice corrects console-attached Codex hook wrapper launch behavior and adds focused regression coverage.

## Acceptance Criteria Status

- [x] Codex `.cmd` wrappers in the approved exact-target amendment no longer invoke bare console `python`/`py`.
- [x] Changed wrappers route Python hook targets through the existing no-window launcher.
- [x] `session-start.cmd` preserves batch-safe harness ID lookup with the new launcher path.
- [x] Focused regression test covers the exact wrapper set and fails on future bare console Python drift.
- [x] Implementation avoided AUQ policy, dispatcher daemon, scoring, harness-state, and bridge-runtime mutations.
- [x] Parent and amendment work were governed by live `GO`, valid claim, implementation-start packet, and exact target preflight.

## Risk And Rollback

Residual risk is limited to host-specific Windows batch quoting and the pre-existing Codex parity-test drift around `.codex/hooks.json` batch aggregation. The riskiest quote path, `session-start.cmd` harness-ID lookup, was manually smoked and returned `A`. One representative changed `.cmd` wrapper was executed and exited cleanly.

Rollback is straightforward: revert the 15 `.cmd` wrapper launcher lines and the added test block in `platform_tests/scripts/test_codex_hook_runtime_containment.py`. No data migration, dispatcher-state mutation, AUQ policy migration, or bridge-runtime migration is involved.

## Loyal Opposition Asks

1. Verify that the changed `.cmd` adapters satisfy the no-console/headless launch expectation without creating a new dispatch path.
2. Verify that the focused regression test is sufficient for the approved WI-4959 scope.
3. Treat the adjacent `.codex/hooks.json` parity-suite failures as residual pre-existing hook-registry drift unless LO determines they are in scope for this exact-target launcher slice.
