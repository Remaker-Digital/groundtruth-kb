NEW

# GT-KB Bridge Implementation Report - gtkb-storm-watchdog-detect-noncodex-process-families - 003

bridge_kind: implementation_report
Document: gtkb-storm-watchdog-detect-noncodex-process-families
Version: 003 (NEW; post-implementation report)
Responds to GO: bridge/gtkb-storm-watchdog-detect-noncodex-process-families-002.md
Approved proposal: bridge/gtkb-storm-watchdog-detect-noncodex-process-families-001.md
Recommended commit type: fix:
author_identity: prime-builder/codex
author_harness_id: A
author_session_context_id: 2026-06-22T00-06-09Z-prime-builder-A-393f21
author_model: GPT-5 Codex
author_model_version: gpt-5-codex
author_model_configuration: Codex bridge auto-dispatch Prime Builder implementation

## First-Line Role Eligibility Check

Resolved session role: Prime Builder. Latest bridge status acted on: GO. Status authored here: NEW implementation report. Prime Builder is authorized to file a post-implementation NEW report after implementing a GO-scoped proposal.

## Implementation Authorization Evidence

- `groundtruth-kb\.venv\Scripts\gt.exe harness roles` resolved harness `A` (`codex`) as `prime-builder`.
- `groundtruth-kb\.venv\Scripts\python.exe scripts\implementation_authorization.py begin --bridge-id gtkb-storm-watchdog-detect-noncodex-process-families` returned latest status `GO`, proposal `bridge/gtkb-storm-watchdog-detect-noncodex-process-families-001.md`, GO file `bridge/gtkb-storm-watchdog-detect-noncodex-process-families-002.md`, active authorization `PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-NONFASTLANE-BATCH-2026-06-21`, work item `WI-4631`, and packet hash `sha256:e885fc17629b31a9abd24de3d5a47b34a4ec6622206dab59c39c53438403da04`.
- `groundtruth-kb\.venv\Scripts\python.exe scripts\bridge_claim_cli.py claim gtkb-storm-watchdog-detect-noncodex-process-families` acquired work-intent claim rowid `15545` for session `2026-06-22T00-06-09Z-prime-builder-A-393f21`.

## Implementation Claim

Implemented the GO-approved tracked artifacts:

- Added `scripts/ops/harness_storm_watchdog.ps1` as a tracked, stageable watchdog source. It preserves the prior codex-family process count, heartbeat, log-rotate, `GTKB_NO_CROSS_HARNESS_TRIGGER` kill-switch assertion, `node_repl` `OpenAI\Codex` image-path guard, and `SilentlyContinue` posture.
- Widened the watchdog to count non-Codex Python LO harness processes by reading `Win32_Process.CommandLine` through `Get-CimInstance`, matching only Python processes that invoke `scripts/ollama_harness.py` or `scripts/openrouter_harness.py` and are tied to the GT-KB project root or `groundtruth-kb\.venv\Scripts\python.exe`.
- Added `$NONCODEX_THRESHOLD = 15`; the watchdog trips when either codex count or noncodex harness count exceeds its threshold.
- Updated heartbeat/intervention audit lines to include `noncodex=<n>` and `noncodexThreshold=<n>`.
- Added `platform_tests/scripts/test_harness_storm_watchdog.py`, a static regression suite covering tracked placement, noncodex backend detection, threshold trip logic, registry drift, conservative kill guards, heartbeat, kill-switch, and log rotation.

Runtime repoint note: the GO verdict approves implementation "within the declared target paths only", and the implementation authorization packet lists only `scripts/ops/harness_storm_watchdog.ps1` and `platform_tests/scripts/test_harness_storm_watchdog.py`. I did not mutate the Windows scheduled task or git-ignored `.gtkb-state/ops/run_harness_storm_watchdog_hidden.vbs` wrapper in this headless auto-dispatch because those host/runtime targets are outside the authorized target path set. The proposed repoint command for a separately authorized runtime operation is:

```powershell
$action = New-ScheduledTaskAction -Execute 'powershell.exe' -Argument '-NoProfile -ExecutionPolicy Bypass -File "E:\GT-KB\scripts\ops\harness_storm_watchdog.ps1"'
Set-ScheduledTask -TaskName 'GTKB-HarnessStormWatchdog' -Action $action
```

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001`
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001`
- `SPEC-AUQ-POLICY-ENGINE-001`
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001`
- `GOV-STANDING-BACKLOG-001`
- `ADR-CODEX-HOOK-PARITY-FALLBACK-001`
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`

## Owner Decisions / Input

- `PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-NONFASTLANE-BATCH-2026-06-21` - active project authorization covering `PROJECT-GTKB-RELIABILITY-FIXES` / `WI-4631`.
- `DELIB-20265457` - owner AUQ authorizing the 2026-06-21 non-fast-lane PROJECT-GTKB-RELIABILITY-FIXES proposal batch.
- No new owner decision was collected or required for the two tracked target-path changes.

## Prior Deliberations

- `DELIB-20262481` - established the backend-agnostic global dispatch concurrency cap that currently catches D/F storms.
- `DELIB-20265232` - dispatch-storm incident review context.
- `DELIB-20265231` - terminal verification context for the dispatch-storm remediation thread.
- `DELIB-BRIDGE-DISPATCH-OVERHAUL-D6-20260612` - owner decision selecting event-driven dispatch with watchdog fallback.
- `DELIB-20265457` - owner authorization for the reliability-fixes batch containing WI-4631.
- `bridge/gtkb-storm-watchdog-detect-noncodex-process-families-001.md` - approved implementation proposal carried forward.
- `bridge/gtkb-storm-watchdog-detect-noncodex-process-families-002.md` - Loyal Opposition GO verdict authorizing the two target paths.

## Specification-Derived Verification Plan

| Spec / governing surface | Executed verification evidence |
| --- | --- |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | `test_watchdog_lands_on_tracked_path` verifies the watchdog exists under `scripts/ops/` and is not git-ignored, making it stageable for the VERIFIED commit-finalization transaction. |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | `test_watchdog_covers_registry_lowcost_backends` verifies registry-declared Python harness scripts are represented in the tracked watchdog. |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | This implementation report carries forward the approved proposal's linked specs and maps them to executed tests in this table. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | `pytest platform_tests/scripts/test_harness_storm_watchdog.py` executed the specification-derived static contract tests. |
| `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` | Implementation authorization command returned active `PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-NONFASTLANE-BATCH-2026-06-21`, project `PROJECT-GTKB-RELIABILITY-FIXES`, and work item `WI-4631`. |
| `SPEC-AUQ-POLICY-ENGINE-001` | No AUQ policy-engine surface changed; the diff is limited to the watchdog script and its test. |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | `git status --short -- scripts/ops/harness_storm_watchdog.ps1 platform_tests/scripts/test_harness_storm_watchdog.py` shows only GT-KB platform ops/test paths for this implementation. |
| `GOV-STANDING-BACKLOG-001` | Implementation authorization ties the change to `WI-4631` under the active reliability-fixes project authorization. |
| `ADR-CODEX-HOOK-PARITY-FALLBACK-001` | The tracked watchdog preserves the dispatch-storm fallback family and does not alter Codex hook parity or hook files. |
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | The watchdog behavior is now represented by tracked source and a regression test rather than only ignored runtime state. |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | Touching the ungoverned runtime watchdog behavior triggered promotion into tracked source plus a test surface. |

## Commands Run

- `groundtruth-kb\.venv\Scripts\python.exe -m pytest platform_tests\scripts\test_harness_storm_watchdog.py -q --tb=short`
- `groundtruth-kb\.venv\Scripts\python.exe -m ruff check platform_tests\scripts\test_harness_storm_watchdog.py`
- `groundtruth-kb\.venv\Scripts\python.exe -m ruff format --check platform_tests\scripts\test_harness_storm_watchdog.py`
- Parse-only PowerShell check, not watchdog execution:

```powershell
$script = Get-Content -Raw -LiteralPath 'scripts\ops\harness_storm_watchdog.ps1'
[void][scriptblock]::Create($script)
Write-Output 'parse-ok'
```

- `git diff --check -- scripts/ops/harness_storm_watchdog.ps1 platform_tests/scripts/test_harness_storm_watchdog.py`

## Observed Results

- `pytest`: `6 passed, 2 warnings in 0.68s`. Warnings were existing pytest configuration/cache warnings: unknown `asyncio_mode`, and a `.pytest_cache` write warning.
- `ruff check`: `All checks passed!`
- `ruff format --check`: `1 file already formatted`
- PowerShell parse-only check: `parse-ok`
- `git diff --check`: clean, no output.

## Files Changed

- `scripts/ops/harness_storm_watchdog.ps1`
- `platform_tests/scripts/test_harness_storm_watchdog.py`

Worktree isolation note: `git status --short` contains unrelated pre-existing modified/untracked files outside this bridge scope. This report claims only the two GO-authorized paths above.

## Recommended Commit Type

- Recommended commit type: `fix:`
- Justification: this repairs a defect in the watchdog detection set so it covers the non-Codex Python LO backends preferred by cost-optimized dispatch, without adding a new user-facing feature surface.

## Acceptance Criteria Status

1. Met for tracked source/test scope: `scripts/ops/harness_storm_watchdog.ps1` exists at the tracked ops path, is not git-ignored, and preserves heartbeat, kill-switch assertion, `claude` exclusion, `node_repl` image-path guard, and log rotation. It becomes git-tracked in the VERIFIED commit-finalization transaction.
2. Met: the watchdog detects `scripts/ollama_harness.py` and `scripts/openrouter_harness.py` Python processes guarded by the GT-KB root / project venv and trips the kill path when noncodex count exceeds `$NONCODEX_THRESHOLD`.
3. Met: `platform_tests/scripts/test_harness_storm_watchdog.py` passes and includes the registry drift guard for Python `*_harness.py` backends.
4. Met: ruff lint and format checks pass on the new Python test file.
5. Partially met / recorded blocker: the scheduled-task repoint command is documented above, but the live host scheduled task and git-ignored runtime wrapper were not mutated because they are outside the GO-authorized target path set for this auto-dispatch.

## Risk And Rollback

- Residual risk: the live scheduled task may still point to the existing git-ignored runtime copy until a separately authorized runtime repoint is performed.
- Process-safety mitigation: the Python kill path requires both a watched harness script name and GT-KB project-root / project-venv evidence before stopping a process.
- Rollback: remove `scripts/ops/harness_storm_watchdog.ps1` and `platform_tests/scripts/test_harness_storm_watchdog.py`; leave the current `.gtkb-state/ops/` runtime copy untouched. Bridge audit files remain append-only.

## Loyal Opposition Asks

1. Verify the tracked watchdog and regression test against the linked specs and observed command evidence.
2. Decide whether the unperformed scheduled-task repoint is a NO-GO blocker under the approved proposal, or whether the documented command plus target-path boundary is acceptable for this verification cycle.
