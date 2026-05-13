NEW

# Implementation Report - Single-Harness Bridge Activation Manager Audit Split

bridge_kind: post_implementation_report
Document: gtkb-single-harness-bridge-activation-manager
Version: 003
Author: Prime Builder (Codex, harness A)
Date: 2026-05-13 UTC
Implements: bridge/gtkb-single-harness-bridge-activation-manager-001.md
GO verdict: bridge/gtkb-single-harness-bridge-activation-manager-002.md
Recommended commit type: feat:

## Claim

The single-harness bridge activation-manager subset is implemented and ready
for Loyal Opposition verification.

The implementation keeps `scripts/single_harness_bridge_dispatcher.py` as the
dispatcher runtime. The activation manager reconciles scheduled-task activation
for the single-harness topology, preserves cross-harness trigger and heartbeat
registrations, and deactivates the scheduled task in non-single-harness
topologies. It does not restore the retired smart poller or retired OS poller
and does not create a third bridge queue or runtime.

During verification, the first targeted test run exposed that a non-positive
`GTKB_ACTIVE_SESSION_SANITY_TTL_SECONDS` environment value made fresh
active-session locks appear stale. Prime Builder fixed that fail-open risk by
treating non-positive TTL values as invalid and falling back to the documented
120-second default in both dispatch substrates.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` - bridge/INDEX.md is the authoritative queue and audit-trail surface.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - this implementation report carries concrete governing links.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - this report maps linked specs to executed verification.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - all live GT-KB files remain under `E:\GT-KB`.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`, `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`, `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - this split preserves durable traceability for the activation-manager lifecycle.
- `.claude/rules/file-bridge-protocol.md` - bridge lifecycle and append-only version-chain authority.
- `.claude/rules/bridge-essential.md` - active bridge-function contract, retired-poller prohibition, and single-harness dispatcher coexistence text.
- `ADR-SINGLE-HARNESS-OPERATING-MODE-001` - single-harness topology is one harness ID with both Prime Builder and Loyal Opposition role membership.
- `SPEC-SINGLE-HARNESS-BRIDGE-DISPATCHER-001` - dispatcher behavior contract that the activation manager reconciles.
- `DCL-SINGLE-HARNESS-DISPATCHER-DESKTOP-TASK-001` - Windows scheduled-task substrate for the single-harness dispatcher.
- `SPEC-CANONICAL-INIT-KEYWORD-SYNTAX-001` and `DCL-INIT-KEYWORD-CONSISTENT-ASSERTION-001` - dispatcher prompt syntax remains delegated to the verified dispatcher.
- `PB-INCIDENT-S321-DAEMON-DISPATCH-DISABLED-001` - dispatch failures leave audit evidence instead of silently dropping work.
- `bridge/gtkb-single-harness-bridge-dispatcher-slice-2-010.md` - VERIFIED dispatcher runtime and scheduled-task evidence.
- `bridge/gtkb-bridge-automation-status-driver-004.md` - source NO-GO requiring this split.

## Prior Deliberations

- `bridge/gtkb-bridge-automation-status-driver-004.md` required the activation-manager subset to be split from the read-only status-driver thread.
- `bridge/gtkb-single-harness-bridge-dispatcher-slice-2-010.md` VERIFIED the underlying dispatcher and scheduled-task end-to-end path.
- `DELIB-1511`, `DELIB-1516`, `DELIB-1517`, `DELIB-1549`, `DELIB-1550`, `DELIB-1568`, and `DELIB-1887` remain the relevant dispatcher, smart-poller retirement, and bridge automation context cited by the GO verdict.

## Owner Decisions / Input

No new owner decision was required during this implementation report. This
report stays within the `GO` scope in `bridge/gtkb-single-harness-bridge-activation-manager-002.md`.

## Files Changed / Accounted

This report accounts for the activation-manager subset already present in the
dirty working tree before this `GO`, plus the TTL hardening added during this
dispatch after the first verification run failed:

- `scripts/single_harness_bridge_automation.py` - activation manager that reconciles the `GTKB-SingleHarnessBridgeDispatcher` scheduled task and can delegate one-shot dispatch.
- `.claude/settings.json` - Claude SessionStart/Stop activation-manager registrations.
- `.codex/hooks.json` - Codex SessionStart/Stop activation-manager registrations.
- `scripts/install_single_harness_dispatcher_task.ps1` - scheduled-task installer default cap alignment.
- `scripts/check_codex_hook_parity.py` - parity checks for the activation-manager hook registrations.
- `config/agent-control/system-interface-map.toml` - inventory entry for the activation-manager surface.
- `.claude/rules/bridge-essential.md` - rule text for the single-harness dispatcher coexistence and retired-poller boundary.
- `platform_tests/scripts/test_single_harness_bridge_automation.py` - activation-manager topology and hook-registration tests.
- `platform_tests/scripts/test_single_harness_bridge_dispatcher.py` - dispatcher suppression and signature tests.
- `platform_tests/scripts/test_single_harness_dispatcher_task_installer.py` - scheduled-task installer shape tests.
- `platform_tests/scripts/test_codex_hook_parity.py` - hook parity regression tests.
- `scripts/cross_harness_bridge_trigger.py` - non-positive active-session TTL fallback to the documented 120-second default.
- `scripts/single_harness_bridge_dispatcher.py` - non-positive active-session TTL fallback to the documented 120-second default.

## Spec-to-Test Mapping

| Requirement | Verification |
|---|---|
| `ADR-SINGLE-HARNESS-OPERATING-MODE-001` | `platform_tests/scripts/test_single_harness_bridge_automation.py` proves activation applies only when one harness role set contains both Prime Builder and Loyal Opposition. |
| `DCL-SINGLE-HARNESS-DISPATCHER-DESKTOP-TASK-001` | `platform_tests/scripts/test_single_harness_dispatcher_task_installer.py` and the live dry-run probe prove hidden `pythonw.exe`, project-root, and `--max-items 999` task shape. |
| `SPEC-SINGLE-HARNESS-BRIDGE-DISPATCHER-001` | `platform_tests/scripts/test_single_harness_bridge_dispatcher.py` and `platform_tests/scripts/test_cross_harness_trigger_suppression.py` prove single-harness dispatch, signature dedupe, and active-session suppression behavior. |
| Cross-harness hook parity | `platform_tests/scripts/test_codex_hook_parity.py`, `platform_tests/scripts/test_slice_3_hook_registrations.py`, and `python scripts/check_codex_hook_parity.py --project-root E:\GT-KB` prove registrations remain aligned. |
| Retired-poller prohibition in `.claude/rules/bridge-essential.md` | Tests and file inspection confirm the activation manager calls the verified dispatcher and does not restore archived smart-poller or OS-poller substrates. |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | This report is filed as `bridge/gtkb-single-harness-bridge-activation-manager-003.md` and the matching `NEW` line is inserted in live `bridge/INDEX.md`. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | This section maps every linked implementation requirement to executed verification and observed results. |

## Commands Executed

Initial targeted test run:

```text
python -m pytest platform_tests/scripts/test_single_harness_bridge_automation.py platform_tests/scripts/test_single_harness_bridge_dispatcher.py platform_tests/scripts/test_single_harness_dispatcher_task_installer.py platform_tests/scripts/test_codex_hook_parity.py platform_tests/scripts/test_cross_harness_trigger_suppression.py platform_tests/scripts/test_slice_3_hook_registrations.py -q --tb=short
```

Observed result: failed with 7 active-session suppression failures. Root cause:
the inherited environment had `GTKB_ACTIVE_SESSION_SANITY_TTL_SECONDS=-1`,
which made fresh lock files stale under the old parser. The implementation was
revised so non-positive TTL values fall back to 120 seconds.

Final targeted test run:

```text
python -m pytest platform_tests/scripts/test_single_harness_bridge_automation.py platform_tests/scripts/test_single_harness_bridge_dispatcher.py platform_tests/scripts/test_single_harness_dispatcher_task_installer.py platform_tests/scripts/test_codex_hook_parity.py platform_tests/scripts/test_cross_harness_trigger_suppression.py platform_tests/scripts/test_slice_3_hook_registrations.py -q --tb=short
```

Observed result: `57 passed, 1 warning in 52.38s`. The warning was a third-party
ChromaDB deprecation warning for `asyncio.iscoroutinefunction`.

Lint:

```text
python -m ruff check scripts/single_harness_bridge_automation.py scripts/check_codex_hook_parity.py scripts/cross_harness_bridge_trigger.py scripts/single_harness_bridge_dispatcher.py platform_tests/scripts/test_single_harness_bridge_automation.py platform_tests/scripts/test_codex_hook_parity.py platform_tests/scripts/test_single_harness_bridge_dispatcher.py platform_tests/scripts/test_single_harness_dispatcher_task_installer.py
```

Observed result: `All checks passed!`

Format:

```text
python -m ruff format --check scripts/single_harness_bridge_automation.py scripts/check_codex_hook_parity.py scripts/cross_harness_bridge_trigger.py scripts/single_harness_bridge_dispatcher.py platform_tests/scripts/test_single_harness_bridge_automation.py platform_tests/scripts/test_codex_hook_parity.py platform_tests/scripts/test_single_harness_bridge_dispatcher.py platform_tests/scripts/test_single_harness_dispatcher_task_installer.py
```

Observed result: `8 files already formatted`.

Hook parity:

```text
python scripts/check_codex_hook_parity.py --project-root E:\GT-KB
```

Observed result: `Codex hook parity: PASS`; the command also noted that Codex
hook commands are checked for Windows shell-portable command forms.

Live scheduled-task evidence:

```text
python scripts/single_harness_bridge_automation.py --project-root E:\GT-KB --ensure --dry-run --verbose
```

Observed result:

- `single_harness_applicable: true`
- `harness_id: A`
- `command_handle: codex`
- `activated: true`
- `action: already_active`
- `task_before.exists: true`
- `task_before.state: Ready`
- `task_before.execute: pythonw.exe`
- `task_before.hidden: true`
- `task_before.arguments: "E:\GT-KB\scripts\single_harness_bridge_dispatcher.py" --project-root "E:\GT-KB" --max-items 999`
- `task_before.lastTaskResult: 0`

Post-filing preflight:

```text
python scripts/bridge_applicability_preflight.py --bridge-id gtkb-single-harness-bridge-activation-manager
python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-single-harness-bridge-activation-manager
```

Observed result after filing this report: applicability preflight passed with
`missing_required_specs: []`, `missing_advisory_specs: []`, and packet hash
`sha256:83afcfa4374cd9517e65ee63e1e28f165a668e15cbc010c41e1829dc65674e31`;
clause preflight passed with `Blocking gaps (gate-failing): 0`.

Secret scan:

```text
python -m groundtruth_kb secrets scan --paths bridge/gtkb-single-harness-bridge-activation-manager-003.md scripts/cross_harness_bridge_trigger.py scripts/single_harness_bridge_dispatcher.py --redacted --fail-on verified-provider
```

Observed result: `Secret scan (paths): 0 finding(s), 3 path(s) scanned.`

## Risk / Rollback

Rollback is `git revert <implementation-commit-sha>` for the implementation
commit after this bridge thread is verified and committed. No production
deployment, release tag, history rewrite, Agent Red source mutation, retired
poller restoration, or alternate bridge runtime is included in this report.

## Verification Request

Loyal Opposition should verify that the activation manager remains a
topology-gated reconciler for the already verified dispatcher, that hook
registrations preserve bridge dispatch and heartbeat behavior, and that the
non-positive TTL fallback closes the fail-open active-session suppression risk
without weakening documented override behavior for positive TTL values.

Copyright 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
