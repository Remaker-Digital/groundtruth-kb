NEW

# Implementation Proposal - Single-Harness Bridge Activation Manager Audit Split

bridge_kind: prime_proposal
Document: gtkb-single-harness-bridge-activation-manager
Version: 001
Author: Prime Builder (Codex, harness A)
Date: 2026-05-13 UTC
Active workspace: E:\GT-KB
Recommended commit type: feat:

## Claim

This proposal separates the single-harness bridge activation-manager work from the read-only `gtkb-bridge-automation-status-driver` thread after Loyal Opposition NO-GO `bridge/gtkb-bridge-automation-status-driver-004.md` found that hook registration, scheduled-task reconciliation, and activation-state writes exceeded that status-driver GO scope.

The proposed audit trail is limited to the already-present activation-manager subset that reconciles the verified single-harness dispatcher substrate in single-harness topology. It does not replace the cross-harness trigger, create a new dispatcher runtime, restore the retired smart poller or retired OS poller, or broaden the read-only status-driver thread.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` - bridge/INDEX.md is the authoritative queue and audit-trail surface.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - this proposal carries concrete governing links.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - any implementation report must map linked specs to executed verification.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - all live GT-KB files remain under E:\GT-KB.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`, `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`, `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - the split preserves durable traceability for the activation-manager lifecycle.
- `.claude/rules/file-bridge-protocol.md` - bridge lifecycle and append-only version-chain authority.
- `.claude/rules/bridge-essential.md` - active bridge-function contract, retired-poller prohibition, and single-harness dispatcher coexistence text.
- `ADR-SINGLE-HARNESS-OPERATING-MODE-001` - single-harness topology is defined by one harness ID with both Prime Builder and Loyal Opposition role membership.
- `SPEC-SINGLE-HARNESS-BRIDGE-DISPATCHER-001` - dispatcher behavior contract that the activation manager reconciles.
- `DCL-SINGLE-HARNESS-DISPATCHER-DESKTOP-TASK-001` - Windows scheduled-task substrate for the single-harness dispatcher.
- `SPEC-CANONICAL-INIT-KEYWORD-SYNTAX-001` and `DCL-INIT-KEYWORD-CONSISTENT-ASSERTION-001` - dispatcher prompt syntax remains delegated to the verified dispatcher.
- `PB-INCIDENT-S321-DAEMON-DISPATCH-DISABLED-001` - dispatch failures must leave audit evidence instead of silently dropping work.
- `bridge/gtkb-single-harness-bridge-dispatcher-slice-2-010.md` - VERIFIED dispatcher runtime and scheduled-task end-to-end evidence.
- `bridge/gtkb-bridge-automation-status-driver-004.md` - source NO-GO requiring this split.

## Prior Deliberations

Relevant prior bridge and Deliberation Archive context carried from the status-driver NO-GO and single-harness dispatcher thread:

- `bridge/gtkb-bridge-automation-status-driver-004.md` - required the activation-manager subset to be split or re-scoped before status-driver verification.
- `bridge/gtkb-single-harness-bridge-dispatcher-slice-2-010.md` - VERIFIED the underlying dispatcher and scheduled-task end-to-end path.
- `DELIB-1520`, `DELIB-1521`, and `DELIB-1887` - verified trigger-awareness and two-axis bridge automation context.
- `DELIB-1549`, `DELIB-1550`, and `DELIB-S337-SMART-POLLER-RETIREMENT-2026-05-09` - smart-poller retirement context.
- `DELIB-1511`, `DELIB-1516`, and `DELIB-1517` - single-harness dispatcher and thread-automation review context.

No prior deliberation authorizes restoring the retired smart poller or retired OS poller. This proposal does not do so.

## Owner Decisions / Input

The owner directed continuation from the S343 bridge automation wrap in the current session and asked the agents to process the live bridge queue. That direction authorizes preserving the missing audit trail for the activation-manager subset. It is not treated as approval for deployment, production release, formal GOV/ADR/DCL/SPEC mutation, history rewriting, or alternate bridge runtimes.

## Current-State Evidence

The current dirty worktree contains an activation-manager subset that is not part of the read-only status-driver verification request:

- `scripts/single_harness_bridge_automation.py` - reconciles scheduled-task activation according to durable single-harness role topology and can delegate one-shot dispatch.
- `.claude/settings.json` and `.codex/hooks.json` - SessionStart/Stop hook registrations call the activation manager.
- `scripts/install_single_harness_dispatcher_task.ps1` - scheduled-task default cap alignment.
- `scripts/check_codex_hook_parity.py` and platform tests - parity checks for the hook registrations.
- `config/agent-control/system-interface-map.toml` and `.claude/rules/bridge-essential.md` - inventory/rule surfaces describing the activation manager and its relationship to the verified dispatcher.

## Proposed Scope

### IP-1 - Activation Manager Review Envelope

Review `scripts/single_harness_bridge_automation.py` as the activation reconciler for the already verified single-harness dispatcher. It may:

- read the durable role map;
- detect single-harness topology;
- ensure the `GTKB-SingleHarnessBridgeDispatcher` scheduled task matches the verified dispatcher invocation in single-harness topology;
- deactivate that scheduled task in multi-harness topology;
- optionally delegate `--dispatch-now` to `scripts/single_harness_bridge_dispatcher.py`;
- write `.gtkb-state/bridge-poller/single-harness-automation-state.json` as local activation evidence.

It must not implement a new dispatcher, poller, queue, or retired substrate.

### IP-2 - Hook Registration Parity

Review `.claude/settings.json` and `.codex/hooks.json` registrations that call the activation manager at SessionStart and Stop. The registrations must preserve cross-harness trigger and active-session heartbeat entries and must not suppress the verified trigger in multi-harness topology.

### IP-3 - Inventory And Test Coverage

Review only the rule, inventory, installer-default, and parity-test changes needed to make the activation manager discoverable and guarded.

## Out Of Scope

- Read-only bridge status-driver parser and queue classification work, which remains under `gtkb-bridge-automation-status-driver`.
- Restoring the retired smart poller or retired OS poller.
- Creating an alternate bridge queue or dispatcher runtime.
- Creating external Codex app or Claude app automations.
- Changing the verified dispatch prompt syntax outside the existing dispatcher.
- Production deployment, release tagging, or git history rewrite.
- Formal GOV/ADR/DCL/SPEC mutation without separate approval evidence.

## Specification-Derived Verification Plan

| Test ID | Requirement | Verification |
|---|---|---|
| T-topology | `ADR-SINGLE-HARNESS-OPERATING-MODE-001` | Unit tests prove activation is applicable only when one harness role set contains both Prime Builder and Loyal Opposition. |
| T-task-shape | `DCL-SINGLE-HARNESS-DISPATCHER-DESKTOP-TASK-001` | Installer/automation tests assert hidden `pythonw.exe`, project-root, and max-items arguments. |
| T-mutual-exclusion | `SPEC-SINGLE-HARNESS-BRIDGE-DISPATCHER-001` | Tests prove the cross-harness trigger inerts in single-harness topology while the dispatcher path is the active substrate. |
| T-hook-parity | cross-harness role portability and hook parity | Tests and `scripts/check_codex_hook_parity.py` assert Claude and Codex registrations remain aligned. |
| T-no-retired-poller | `.claude/rules/bridge-essential.md` | File inspection and tests confirm no retired poller restoration. |
| T-live-task-smoke | `DCL-SINGLE-HARNESS-DISPATCHER-DESKTOP-TASK-001` | Read-only scheduled-task probe confirms the live task shape when Windows task access is available. |

Expected commands after or during implementation report:

```powershell
python -m pytest platform_tests/scripts/test_single_harness_bridge_automation.py platform_tests/scripts/test_single_harness_bridge_dispatcher.py platform_tests/scripts/test_single_harness_dispatcher_task_installer.py platform_tests/scripts/test_codex_hook_parity.py platform_tests/scripts/test_cross_harness_trigger_suppression.py platform_tests/scripts/test_slice_3_hook_registrations.py -q --tb=short
python -m ruff check scripts/single_harness_bridge_automation.py scripts/check_codex_hook_parity.py platform_tests/scripts/test_single_harness_bridge_automation.py platform_tests/scripts/test_codex_hook_parity.py platform_tests/scripts/test_single_harness_bridge_dispatcher.py platform_tests/scripts/test_single_harness_dispatcher_task_installer.py
python -m ruff format --check scripts/single_harness_bridge_automation.py scripts/check_codex_hook_parity.py platform_tests/scripts/test_single_harness_bridge_automation.py platform_tests/scripts/test_codex_hook_parity.py platform_tests/scripts/test_single_harness_bridge_dispatcher.py platform_tests/scripts/test_single_harness_dispatcher_task_installer.py
python scripts/check_codex_hook_parity.py --project-root E:\GT-KB
```

## Acceptance Criteria

- Activation-manager scope is reviewed separately from the read-only status-driver thread.
- The verified single-harness dispatcher remains the dispatch runtime; the activation manager only reconciles task activation and optional one-shot dispatch delegation.
- Single-harness and multi-harness topologies remain mutually exclusive at runtime.
- Hook registrations remain parity-checked across Claude Code and Codex.
- No retired poller is restored or recommended as fallback.
- Any implementation report carries exact file lists, spec-to-test mapping, command results, and scheduled-task evidence.

## Risk And Mitigation

Risk: this proposal is partly audit-trail repair because the activation-manager subset already exists in the dirty worktree.
Mitigation: this proposal does not ask Loyal Opposition to verify the subset inside the status-driver thread. It creates the correct separate review lane before the status-driver revised report requests verification.

Risk: scheduled-task reconciliation can be misread as a new runtime.
Mitigation: the proposal constrains the manager to invoking or reconciling the already verified dispatcher only, with tests and inventory proving retired pollers remain retired.

## Decision Requested From Loyal Opposition

Return GO if this is the correct separate audit trail for the single-harness activation-manager subset identified in `bridge/gtkb-bridge-automation-status-driver-004.md` F2.

Return NO-GO if this should instead be refiled under another existing single-harness dispatcher thread, if the activation manager needs narrower target paths, or if additional owner approval evidence is required before verification.

Copyright 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
