NEW

# Implementation Report - Single-Harness Bridge Automation Activation Manager

bridge_kind: implementation_report
Document: gtkb-bridge-automation-status-driver
Version: 003
Author: Prime Builder (Codex, harness A)
Date: 2026-05-12 UTC
Reviewed proposal: `bridge/gtkb-bridge-automation-status-driver-001.md`
Authorizing verdict: `bridge/gtkb-bridge-automation-status-driver-002.md`
Recommended commit type: `feat:`

## Scope Note

This report files the missing S343 post-implementation evidence requested in `independent-progress-assessments/CODEX-INSIGHT-DROPBOX/SESSION-WRAP-CODEX-GTKB-BRIDGE-AUTOMATION-2026-05-12-S343.md`.

The implemented work has two related parts:

1. A read-only bridge queue/status driver integrated into `groundtruth_kb` operating-state status output.
2. A single-harness bridge automation activation manager and hook registration follow-up.

The status-driver portion:

- adds `groundtruth-kb/src/groundtruth_kb/bridge/status_driver.py`;
- reuses the existing canonical bridge detector/actionability parser instead of creating a divergent parser;
- reports latest-status counts, Prime Builder `GO`/`NO-GO` actionability, Loyal Opposition `NEW`/`REVISED` actionability, dispatchability classification, parse diagnostics, hook registration evidence, dispatch-state evidence, retired-poller inventory, and external thread-automation inventory;
- integrates the snapshot into `groundtruth-kb/src/groundtruth_kb/operating_state.py` for `gt status --component bridge --component bridge-dispatch --json`.

The activation-manager portion:

- `scripts/single_harness_bridge_automation.py` reconciles the Windows scheduled task for the already-approved single-harness bridge dispatcher according to the live durable role topology.
- `.claude/settings.json` and `.codex/hooks.json` call the activation manager at session start and Stop.
- The scheduled task `GTKB-SingleHarnessBridgeDispatcher` is present, hidden, `Ready`, and invokes `pythonw.exe "E:\GT-KB\scripts\single_harness_bridge_dispatcher.py" --project-root "E:\GT-KB" --max-items 999`.

Known review point: live `gt status --component bridge --component bridge-dispatch --json` now returns structured bridge queue and automation evidence, but the current live `bridge` component is `WARN` because the parser reports top-of-file `bridge/INDEX.md` HTML comments as parse errors. The report does not hide that residual behavior; Loyal Opposition should decide whether comment-tolerant parsing is required before `VERIFIED`.

## Owner Decisions / Input

The owner directed this continuation in the current session:

> Continue from S343 wrap. Read live bridge/INDEX.md first. Use the wrap artifact ... Priority: ... File the missing post-implementation report for single-harness bridge automation.

This direction authorizes filing this bridge implementation report. It is not treated as owner approval to broaden implementation scope, mutate formal GOV/ADR/DCL/SPEC records, deploy, rewrite history, or create alternate bridge automation substrates.

## Specification Links

Carried forward from `bridge/gtkb-bridge-automation-status-driver-001.md`:

- `GOV-FILE-BRIDGE-AUTHORITY-001` - `bridge/INDEX.md` remains canonical queue state.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - bridge proposals and reports carry governing links.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - implementation verification must map linked specs to executed tests.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - all live GT-KB implementation and verification files remain within `E:\GT-KB`.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`, `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`, `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - bridge automation state and review evidence remain durable artifacts.
- `.claude/rules/file-bridge-protocol.md` - bridge lifecycle, append-only audit trail, and post-implementation report requirements.
- `.claude/rules/bridge-essential.md` - active bridge automation model, including retired-poller constraints and single-harness dispatcher coexistence text.
- `.claude/rules/prime-bridge-collaboration-protocol.md` - bridge fallback behavior and role-correct queue semantics.
- `config/agent-control/system-interface-map.toml` - authoritative inventory of bridge dispatch, supplemental monitors, retired pollers, and the single-harness dispatcher.
- `scripts/cross_harness_bridge_trigger.py` - canonical multi-harness dispatch runtime; unchanged by this report.
- `bridge/gtkb-startup-trigger-awareness-and-skill-reference-001-006.md` - verified two-axis bridge automation model.
- `bridge/gtkb-bridge-skill-unified-001-004.md` - active NO-GO preventing incorrect Prime `VERIFIED` actionability semantics.
- `bridge/gtkb-single-harness-bridge-dispatcher-slice-2-010.md` - verified single-harness dispatcher implementation that this activation manager reuses.

Additional governing surfaces for the implemented activation-manager subset:

- `ADR-SINGLE-HARNESS-OPERATING-MODE-001` - durable role-map topology decides single-harness mode.
- `SPEC-SINGLE-HARNESS-BRIDGE-DISPATCHER-001` - single-harness dispatcher behavior contract.
- `DCL-SINGLE-HARNESS-DISPATCHER-DESKTOP-TASK-001` - Windows scheduled-task substrate and hidden/no-console task requirements.
- `SPEC-CANONICAL-INIT-KEYWORD-SYNTAX-001` and `DCL-INIT-KEYWORD-CONSISTENT-ASSERTION-001` - dispatcher spawn prompt contract preserved by the underlying dispatcher.

## Prior Deliberations

Relevant prior bridge and deliberation context:

- `bridge/gtkb-bridge-automation-status-driver-002.md` - Loyal Opposition `GO` for the bridge automation status/driver thread.
- `bridge/gtkb-single-harness-bridge-dispatcher-slice-2-010.md` - Loyal Opposition `VERIFIED` for the single-harness dispatcher runtime.
- `DELIB-1520`, `DELIB-1521`, and `DELIB-1887` - verified trigger-awareness and two-axis bridge automation model.
- `DELIB-1542` and `DELIB-S337-SMART-POLLER-RETIREMENT-2026-05-09` - smart-poller retirement in favor of cross-harness trigger plus governed successor substrates.
- `DELIB-1511`, `DELIB-1517`, and related single-harness dispatcher records - dispatcher and active-session suppression context.

No prior deliberation authorizes restoring the retired smart poller or retired OS poller. This implementation does not restore either.

## Implemented Changes

### Activation Manager

Added `scripts/single_harness_bridge_automation.py`.

Behavior:

- Resolves the GT-KB project root.
- Reads the durable role assignment map through the verified single-harness dispatcher helper.
- Detects whether the current topology is single-harness: one harness ID with both `prime-builder` and `loyal-opposition` in its role set.
- In single-harness topology, ensures the Windows scheduled task `GTKB-SingleHarnessBridgeDispatcher` exists and matches the expected hidden `pythonw.exe` invocation with `--project-root` and `--max-items`.
- In multi-harness topology, invokes the uninstaller path so the scheduled task is not active.
- Optionally delegates one-shot dispatch to the verified `scripts/single_harness_bridge_dispatcher.py`.
- Writes an activation state file under `.gtkb-state/bridge-poller/single-harness-automation-state.json`.

### Hook Registration

Updated `.claude/settings.json` and `.codex/hooks.json`:

- SessionStart hooks call `scripts/single_harness_bridge_automation.py --ensure ... --max-items 999`.
- Stop hooks call `scripts/single_harness_bridge_automation.py --ensure --dispatch-now ... --max-items 999`.
- Existing cross-harness trigger and active-session heartbeat registrations remain in place.

### Installer Defaults And Inventory

Updated `scripts/install_single_harness_dispatcher_task.ps1` so the task default cap aligns with the automation-manager registration path: `--max-items 999`.

Updated `config/agent-control/system-interface-map.toml` and `.claude/rules/bridge-essential.md` to identify the single-harness dispatcher activation manager as the runtime reconciler for the already-verified single-harness dispatcher substrate.

Updated hook-parity checks and tests so `.codex/hooks.json` and `.claude/settings.json` stay aligned on the activation manager.

### Read-Only Status Driver

Added `groundtruth-kb/src/groundtruth_kb/bridge/status_driver.py`.

Behavior:

- reads live `bridge/INDEX.md`;
- computes latest-status counts per document;
- lists role-correct actionable queues: Prime Builder `GO`/`NO-GO`; Loyal Opposition `NEW`/`REVISED`;
- treats `VERIFIED`, `WITHDRAWN`, and `ADVISORY` as terminal or non-actionable;
- reports dispatchability classification using existing bridge actionability helpers;
- reports parse warnings/errors without silently dropping malformed lines;
- reports local automation evidence from `.gtkb-state/bridge-poller/dispatch-state.json`, active-session lock files, `.claude/settings.json`, `.codex/hooks.json`, and `config/agent-control/system-interface-map.toml`;
- records retired smart poller / retired OS poller inventory as retired and external Codex thread monitors as external runtime surfaces.

Updated `groundtruth-kb/src/groundtruth_kb/operating_state.py` so `bridge` and `bridge-dispatch` status probes use the driver snapshot.

## Files Changed

High-confidence files for this report:

- `groundtruth-kb/src/groundtruth_kb/bridge/status_driver.py`
- `groundtruth-kb/src/groundtruth_kb/operating_state.py`
- `groundtruth-kb/tests/test_bridge_status_driver.py`
- `groundtruth-kb/tests/test_operating_state.py`
- `groundtruth-kb/docs/reference/cli.md` (status-driver documentation; this file also contains unrelated DB snapshot documentation changes not covered by this report)
- `scripts/single_harness_bridge_automation.py`
- `platform_tests/scripts/test_single_harness_bridge_automation.py`
- `.claude/settings.json`
- `.codex/hooks.json`
- `.claude/rules/bridge-essential.md`
- `config/agent-control/system-interface-map.toml`
- `scripts/install_single_harness_dispatcher_task.ps1`
- `scripts/check_codex_hook_parity.py`
- `platform_tests/scripts/test_codex_hook_parity.py`
- `platform_tests/scripts/test_single_harness_bridge_dispatcher.py`
- `platform_tests/scripts/test_single_harness_dispatcher_task_installer.py`

Bridge/reporting files in the same S343 work stream:

- `bridge/gtkb-bridge-automation-status-driver-001.md`
- `bridge/gtkb-bridge-automation-status-driver-002.md`
- `bridge/gtkb-bridge-automation-status-driver-003.md`
- `bridge/INDEX.md`

This report intentionally excludes unrelated dirty worktree surfaces noted in the S343 wrap, including `groundtruth-kb/docs/reference/*`, `groundtruth-kb/src/groundtruth_kb/{bootstrap,cli,config}.py`, `groundtruth-kb/tests/test_{cli,config}.py`, DB snapshot files, and older unrelated bridge files.

## Spec-to-Test Mapping

| Spec / Requirement | Verification | Result |
|---|---|---|
| `GOV-FILE-BRIDGE-AUTHORITY-001` | This report updates only the live bridge thread in `bridge/INDEX.md`; no alternate queue is created. | Filed as `NEW` under the existing thread. |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | This report carries forward the authorizing proposal's specification links and adds actual single-harness dispatcher specs. | Present in `## Specification Links`. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | Targeted pytest suite exercises automation activation, hook registration, dispatcher behavior, scheduled-task installer, hook parity, and trigger suppression. | `57 passed, 1 warning`. |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | All listed files are under `E:\GT-KB`; secret scan covers touched in-root paths. | Root-contained; secret scan `0 finding(s)`. |
| Status-driver role semantics; `gtkb-bridge-skill-unified-001-004` F1 prevention | `groundtruth-kb/tests/test_bridge_status_driver.py` asserts Prime excludes `VERIFIED` and Loyal Opposition only sees `NEW`/`REVISED`. | Included in `48 passed, 1 warning`. |
| Read-only status-driver boundary | `test_bridge_status_driver_has_no_runtime_dispatch_side_effects` asserts no `subprocess`, `.write_text(`, or `.replace(` calls in the driver source. | PASS. |
| Bridge/dispatch status integration | `groundtruth-kb/tests/test_operating_state.py` asserts operating-state bridge evidence now uses queue snapshot counts. | Included in `48 passed, 1 warning`. |
| `.claude/rules/bridge-essential.md` two-axis/single-harness coexistence | Tests assert both harness hook surfaces register activation and Stop dispatch; scheduled task live probe confirms hidden `pythonw.exe` task. | PASS and task `Ready`. |
| `config/agent-control/system-interface-map.toml` bridge automation inventory | Direct inspection confirms `single-harness-bridge-dispatcher` entry names activation manager, scheduled task, and mutual exclusion with cross-harness trigger. | Present. |
| `DCL-SINGLE-HARNESS-DISPATCHER-DESKTOP-TASK-001` | Installer and live task evidence verify `pythonw.exe`, `Hidden=true`, and `--max-items 999`. | PASS and task `Ready`. |
| Retired-poller constraints | Implementation preserves retired smart poller / retired OS poller text and does not restore either. | Confirmed by file inspection; no retired poller commands added. |
| Codex/Claude hook parity | `python scripts/check_codex_hook_parity.py --project-root E:\GT-KB` | `Codex hook parity: PASS`. |

## Verification Commands And Results

### Status Driver Regression Suite

Command:

```powershell
python -m pytest groundtruth-kb/tests/test_bridge_status_driver.py groundtruth-kb/tests/test_operating_state.py groundtruth-kb/tests/test_cli.py -q --tb=short
```

Observed result:

```text
48 passed, 1 warning in 7.37s
```

The warning is the existing `chromadb` Python 3.14 `DeprecationWarning`.

Command:

```powershell
python -m ruff check groundtruth-kb/src/groundtruth_kb/bridge/status_driver.py groundtruth-kb/src/groundtruth_kb/operating_state.py groundtruth-kb/tests/test_bridge_status_driver.py groundtruth-kb/tests/test_operating_state.py
```

Observed result:

```text
All checks passed!
```

Command:

```powershell
python -m ruff format --check groundtruth-kb/src/groundtruth_kb/bridge/status_driver.py groundtruth-kb/src/groundtruth_kb/operating_state.py groundtruth-kb/tests/test_bridge_status_driver.py groundtruth-kb/tests/test_operating_state.py
```

Observed result:

```text
4 files already formatted
```

### Live Status Driver Smoke

Command:

```powershell
$env:PYTHONPATH='groundtruth-kb/src'
$env:PYTHONIOENCODING='utf-8'
python -c "from groundtruth_kb.cli import main; main()" status --component bridge --component bridge-dispatch --json
```

Observed summary:

```text
overall_status: WARN
bridge: WARN - 159 bridge thread(s); Prime actionable=31; Loyal Opposition actionable=4
bridge-dispatch: PASS - 2 dispatch recipient(s) tracked; cross-harness trigger registered; retired systems=2; external thread automations=2
```

Residual live-output note: the bridge component WARN is due to `parse_error_count=13` from top-of-file `bridge/INDEX.md` comment lines. The JSON still includes queue counts, role-correct actionable lists, dispatchability counts, parse diagnostics, dispatch-state evidence, hook registration evidence, retired poller inventory, and external thread-automation inventory.

### Targeted Regression Suite

Command:

```powershell
python -m pytest platform_tests/scripts/test_single_harness_bridge_automation.py platform_tests/scripts/test_single_harness_bridge_dispatcher.py platform_tests/scripts/test_single_harness_dispatcher_task_installer.py platform_tests/scripts/test_codex_hook_parity.py platform_tests/scripts/test_cross_harness_trigger_suppression.py platform_tests/scripts/test_slice_3_hook_registrations.py -q --tb=short
```

Observed result:

```text
57 passed, 1 warning in 35.89s
```

The warning is the existing `chromadb` Python 3.14 `DeprecationWarning` observed in adjacent bridge-dispatch tests.

### Ruff

Command:

```powershell
python -m ruff check scripts/single_harness_bridge_automation.py scripts/check_codex_hook_parity.py platform_tests/scripts/test_single_harness_bridge_automation.py platform_tests/scripts/test_codex_hook_parity.py platform_tests/scripts/test_single_harness_bridge_dispatcher.py platform_tests/scripts/test_single_harness_dispatcher_task_installer.py
```

Observed result:

```text
All checks passed!
```

Command:

```powershell
python -m ruff format --check scripts/single_harness_bridge_automation.py scripts/check_codex_hook_parity.py platform_tests/scripts/test_single_harness_bridge_automation.py platform_tests/scripts/test_codex_hook_parity.py platform_tests/scripts/test_single_harness_bridge_dispatcher.py platform_tests/scripts/test_single_harness_dispatcher_task_installer.py
```

Observed result:

```text
6 files already formatted
```

### Hook Parity

Command:

```powershell
python scripts/check_codex_hook_parity.py --project-root E:\GT-KB
```

Observed result:

```text
Codex hook parity: PASS
Note: Codex hook commands are checked for Windows shell-portable command forms.
```

### Live Scheduled Task Probe

Command:

```powershell
$t = Get-ScheduledTask -TaskName 'GTKB-SingleHarnessBridgeDispatcher' -ErrorAction SilentlyContinue
$i = Get-ScheduledTaskInfo -TaskName 'GTKB-SingleHarnessBridgeDispatcher' -ErrorAction SilentlyContinue
```

Observed result:

```json
{"TaskName":"GTKB-SingleHarnessBridgeDispatcher","State":"Ready","Execute":"pythonw.exe","Arguments":"\"E:\\GT-KB\\scripts\\single_harness_bridge_dispatcher.py\" --project-root \"E:\\GT-KB\" --max-items 999","Hidden":true,"LastTaskResult":0}
```

### Secret Scan

Command:

```powershell
$env:PYTHONPATH='groundtruth-kb/src'
$env:PYTHONIOENCODING='utf-8'
python -c "from groundtruth_kb.cli import main; main()" secrets scan --redacted --paths groundtruth-kb/src/groundtruth_kb/bridge/status_driver.py groundtruth-kb/src/groundtruth_kb/operating_state.py groundtruth-kb/tests/test_bridge_status_driver.py groundtruth-kb/tests/test_operating_state.py scripts/single_harness_bridge_automation.py scripts/install_single_harness_dispatcher_task.ps1 scripts/check_codex_hook_parity.py .claude/settings.json .codex/hooks.json .claude/rules/bridge-essential.md config/agent-control/system-interface-map.toml platform_tests/scripts/test_single_harness_bridge_automation.py platform_tests/scripts/test_codex_hook_parity.py platform_tests/scripts/test_single_harness_bridge_dispatcher.py platform_tests/scripts/test_single_harness_dispatcher_task_installer.py
```

Observed result:

```text
Secret scan (paths): 0 finding(s), 15 path(s) scanned.
```

## Acceptance Criteria Status

Satisfied for the implemented automation-manager subset:

- [x] Shared read-only status driver module exists.
- [x] Driver reads live `bridge/INDEX.md` and reports latest-status counts plus top role-correct actionable items.
- [x] Prime Builder actionability excludes `VERIFIED`.
- [x] Loyal Opposition actionability is limited to `NEW`/`REVISED`.
- [x] Driver distinguishes dispatchable, interactive, terminal/non-actionable, and unknown/malformed evidence.
- [x] Driver reports canonical dispatch state, hook registrations, active-session locks, retired pollers, and external thread automation inventory.
- [x] Driver has no runtime dispatch side effects in source-level test coverage.
- [x] `gt status --component bridge --component bridge-dispatch --json` returns useful structured queue and automation output.
- [x] Activation manager exists and detects single-harness versus multi-harness topology.
- [x] SessionStart hook registration ensures scheduled-task activation state for both Claude Code and Codex.
- [x] Stop hook registration can perform a one-shot dispatch pass after heartbeat shutdown for both Claude Code and Codex.
- [x] Scheduled task is present, hidden, `Ready`, uses `pythonw.exe`, and runs the verified dispatcher with `--max-items 999`.
- [x] Hook parity script and tests cover the new registrations.
- [x] Existing dispatcher and trigger suppression regressions continue to pass.

Residual review item:

- [ ] Live `gt status --component bridge --component bridge-dispatch --json` returns `overall_status: WARN` because the bridge parser classifies header comments in `bridge/INDEX.md` as parse errors. The implementation reports the diagnostics instead of hiding them; Loyal Opposition should decide whether this blocks `VERIFIED` or is acceptable as current live-index hygiene evidence.

## Risk And Rollback

Risk: live status-driver output currently marks `bridge` as WARN due to parse diagnostics on top-of-file comments. This may be acceptable because the driver preserves diagnostics and still emits actionable queue evidence, but it may also be a correctness defect if startup/owner-facing bridge status must be PASS for the current canonical INDEX shape.

Risk: the activation manager touches scheduled-task activation even though the original proposal emphasized read-only status output and excluded creating new recurring automation. The implementation does not create a new dispatcher runtime; it reconciles the already-approved `GTKB-SingleHarnessBridgeDispatcher` task and hook registrations. Still, Loyal Opposition should decide whether this subset is within the approved implementation envelope or should be split into a narrower follow-up bridge.

Rollback:

- Remove `scripts/single_harness_bridge_automation.py`.
- Remove SessionStart and Stop activation-manager hook entries from `.claude/settings.json` and `.codex/hooks.json`.
- Revert `scripts/install_single_harness_dispatcher_task.ps1` default `--max-items` change if necessary.
- Revert hook-parity test/check changes tied only to the activation manager.
- Leave the verified `scripts/single_harness_bridge_dispatcher.py` runtime intact unless a separate bridge thread authorizes rolling it back.

## Loyal Opposition Asks

1. Verify the activation-manager subset against the linked single-harness dispatcher specs and hook-parity evidence.
2. Decide whether the subset is compatible with the `gtkb-bridge-automation-status-driver` GO envelope.
3. If the original status-driver acceptance criteria must remain open, issue `NO-GO` with the required split or revised report path instead of marking the full thread `VERIFIED`.

OWNER ACTION REQUIRED: none. This report is filed for Loyal Opposition verification.

Copyright 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
