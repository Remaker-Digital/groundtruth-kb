NEW

# GT-KB Bridge Implementation Report - WI-4943 - 007

bridge_kind: implementation_report
Document: gtkb-wi4943-release-branch-dispatcher-substrate-reconciliation
Version: 007
Author: Prime Builder (Codex)
Date: 2026-07-01 UTC
author_identity: Prime Builder / Codex
author_harness_id: A
author_session_context_id: 2026-07-01T10-30-33Z-prime-builder-A-194b67
author_model: GPT-5 Codex
author_model_version: 2026-07-01 runtime
author_model_configuration: Codex auto-dispatch, Prime Builder role, approval_policy=never, cwd=E:\GT-KB

Responds to GO: bridge/gtkb-wi4943-release-branch-dispatcher-substrate-reconciliation-006.md
Approved proposal: bridge/gtkb-wi4943-release-branch-dispatcher-substrate-reconciliation-005.md
Prior NO-GO: bridge/gtkb-wi4943-release-branch-dispatcher-substrate-reconciliation-004.md
Project: PROJECT-GTKB-AD-HOC-RELEASE-20260701
Work Item: WI-4943
Project Authorization: PAUTH-PROJECT-GTKB-AD-HOC-RELEASE-20260701-WI-4943-DISPATCHER-SUBSTRATE
Recommended commit type: fix(dispatch)

target_paths: ["scripts/gtkb_dispatcher_daemon.py", "scripts/dispatcher_runtime.py", "scripts/ensure_dispatcher_daemon.py", "scripts/install_dispatcher_daemon_task.ps1", "scripts/cursor_harness.py", "groundtruth-kb/src/groundtruth_kb/cli.py", "groundtruth-kb/src/groundtruth_kb/bridge_dispatch_config.py", "groundtruth-kb/src/groundtruth_kb/bridge_dispatch_reset.py", "groundtruth-kb/src/groundtruth_kb/dispatcher_supervisor.py", "groundtruth-kb/src/groundtruth_kb/project/doctor.py", "groundtruth-kb/src/groundtruth_kb/bridge/role_state.py", "scripts/ops/harness_storm_watchdog_launcher.py", "config/dispatcher/rules.toml", "harness-state/harness-registry.json", "platform_tests/scripts/test_gtkb_dispatcher_daemon.py", "platform_tests/scripts/test_dispatcher_daemon_supervision.py", "platform_tests/scripts/test_dispatcher_runtime.py", "platform_tests/scripts/test_cursor_harness.py", "platform_tests/groundtruth_kb/cli/test_bridge_config_cli.py", "platform_tests/groundtruth_kb/cli/test_bridge_dispatch_daemon_supervisor.py", "groundtruth-kb/docs/method/12-file-bridge-automation.md", "docs/gtkb-dashboard/grafana/README.md", "groundtruth-kb/docs/wiki/release-health.md", "README.md", "bridge/gtkb-wi4933-*.md", "bridge/gtkb-wi4937-dispatcher-supervisor-governance-*.md", "bridge/gtkb-wi4942-dispatch-drain-live-worker-parity-*.md", "bridge/gtkb-wi4943-release-branch-dispatcher-substrate-reconciliation-*.md"]

---

## Implementation Claim

This report does not request `VERIFIED`. The WI-4943 release worktree now has dispatcher topology sufficient for `gt bridge dispatch health --json` to pass, and the v005-added support files were applied. Focused tests expose two additional release-branch dependency gaps outside the current approved target envelope:

1. `scripts/bridge_work_intent_registry.py` is older than the staged dispatcher runtime and lacks `MalformedBridgeStatusError` and related dispatch-batch surfaces.
2. `scripts/ops/harness_storm_watchdog.ps1` is absent while the newly added `scripts/ops/harness_storm_watchdog_launcher.py` and its test require it.

Because those two paths are not in the v005/v006 target_paths envelope, Prime Builder did not modify them in this auto-dispatch. No release commit was created.

## First-Line Role Eligibility And Work-Intent Claim

Prime Builder role was resolved through the canonical reader:

```text
groundtruth-kb/.venv/Scripts/gt.exe harness roles
```

The role map reports harness `A` (`codex`) as `prime-builder`. The live bridge scan reported latest status `GO` at `bridge/gtkb-wi4943-release-branch-dispatcher-substrate-reconciliation-006.md`, so Prime Builder was authorized to work inside the approved WI-4943 target envelope.

Work-intent claim evidence:

```json
{
  "rowid": 28200,
  "session_id": "2026-07-01T10-30-33Z-prime-builder-A-194b67",
  "acting_role": "prime-builder",
  "claim_kind": "go_implementation",
  "latest_bridge_status": "GO",
  "expired": false
}
```

Implementation-start packet evidence:

```text
groundtruth-kb/.venv/Scripts/python.exe scripts/implementation_authorization.py begin --bridge-id gtkb-wi4943-release-branch-dispatcher-substrate-reconciliation
packet_hash: sha256:eb601cb52e500fdbde1a7fa88fba1e606bdc0377599dc2307125205630b1d8d6
latest_status: GO
go_file: bridge/gtkb-wi4943-release-branch-dispatcher-substrate-reconciliation-006.md
```

## Release Worktree Actions

Worktree inspected:

```text
E:\GT-KB\.gtkb-state\release-main-20260630
branch: codex/dispatcher-release-chain-main-20260701
starting HEAD: 174e8c5f1 docs: VERIFIED WI-4942 dispatcher drain live-worker parity (bridge -006)
```

Before this dispatch, the release worktree already contained staged dispatcher substrate changes and an unstaged `groundtruth-kb/src/groundtruth_kb/cli.py` edit. Prime Builder preserved that work and added only the missing paths from the v005 corrected envelope:

- copied current dispatcher topology into `config/dispatcher/rules.toml`;
- copied current harness projection into `harness-state/harness-registry.json`;
- copied `groundtruth-kb/src/groundtruth_kb/bridge/role_state.py`;
- copied `scripts/ops/harness_storm_watchdog_launcher.py`;
- staged the v005-added paths plus the existing unstaged `cli.py` edit.

Final release staged set:

```text
A       bridge/gtkb-wi4937-dispatcher-supervisor-governance-001.md
A       bridge/gtkb-wi4937-dispatcher-supervisor-governance-002.md
A       bridge/gtkb-wi4937-dispatcher-supervisor-governance-003.md
A       bridge/gtkb-wi4937-dispatcher-supervisor-governance-004.md
A       bridge/gtkb-wi4937-dispatcher-supervisor-governance-005.md
A       bridge/gtkb-wi4937-dispatcher-supervisor-governance-006.md
M       config/dispatcher/rules.toml
A       groundtruth-kb/src/groundtruth_kb/bridge/role_state.py
M       groundtruth-kb/src/groundtruth_kb/bridge_dispatch_config.py
M       groundtruth-kb/src/groundtruth_kb/bridge_dispatch_reset.py
M       groundtruth-kb/src/groundtruth_kb/cli.py
A       groundtruth-kb/src/groundtruth_kb/dispatcher_supervisor.py
M       groundtruth-kb/src/groundtruth_kb/project/doctor.py
M       harness-state/harness-registry.json
M       platform_tests/groundtruth_kb/cli/test_bridge_config_cli.py
A       platform_tests/groundtruth_kb/cli/test_bridge_dispatch_daemon_supervisor.py
A       platform_tests/scripts/test_dispatcher_daemon_supervision.py
A       platform_tests/scripts/test_dispatcher_runtime.py
A       platform_tests/scripts/test_gtkb_dispatcher_daemon.py
A       scripts/dispatcher_runtime.py
A       scripts/ensure_dispatcher_daemon.py
A       scripts/gtkb_dispatcher_daemon.py
A       scripts/install_dispatcher_daemon_task.ps1
A       scripts/ops/harness_storm_watchdog_launcher.py
```

`git diff --name-status` reported no remaining unstaged diff after staging.

## Passing Release Evidence

Dispatcher health now passes from the release worktree:

```text
E:\GT-KB\groundtruth-kb\.venv\Scripts\python.exe -m groundtruth_kb.cli bridge dispatch health --json
health_status: PASS
findings: []
selected_by_role.prime-builder: A, E
selected_by_role.loyal-opposition: D, F, C, B
```

Dispatcher status also passes and reports the same selected topology:

```text
E:\GT-KB\groundtruth-kb\.venv\Scripts\python.exe -m groundtruth_kb.cli bridge dispatch status --json
health_status: PASS
health_findings: []
```

Daemon status succeeds without the original missing-file exception:

```text
E:\GT-KB\groundtruth-kb\.venv\Scripts\python.exe -m groundtruth_kb.cli bridge dispatch daemon status --json
{
  "active_substrate": "cross_harness_trigger",
  "mode": "shadow",
  "pid_provenance_verified": false,
  "running": true
}
```

Dry-run drain succeeds:

```text
E:\GT-KB\groundtruth-kb\.venv\Scripts\python.exe -m groundtruth_kb.cli bridge dispatch drain --timeout 1 --dry-run --json
{
  "drain_markers_written": 0,
  "drained_pids": [],
  "dry_run": true,
  "terminated_pids": []
}
```

Code-quality gates pass for the changed Python paths:

```text
E:\GT-KB\groundtruth-kb\.venv\Scripts\python.exe -m ruff check <15 changed Python paths>
All checks passed!

E:\GT-KB\groundtruth-kb\.venv\Scripts\python.exe -m ruff format --check <15 changed Python paths>
15 files already formatted
```

## Blocking Test Evidence

Focused pytest command:

```text
$env:PYTHONPATH = E:\GT-KB\.gtkb-state\release-main-20260630\groundtruth-kb\src
$env:TEMP = E:\GT-KB\.gtkb-state\release-main-20260630\.tmp-pytest-wi4943\envtmp
$env:TMP = E:\GT-KB\.gtkb-state\release-main-20260630\.tmp-pytest-wi4943\envtmp
E:\GT-KB\groundtruth-kb\.venv\Scripts\python.exe -m pytest platform_tests/groundtruth_kb/cli/test_bridge_config_cli.py platform_tests/groundtruth_kb/cli/test_bridge_dispatch_daemon_supervisor.py platform_tests/scripts/test_gtkb_dispatcher_daemon.py platform_tests/scripts/test_dispatcher_runtime.py platform_tests/scripts/test_dispatcher_daemon_supervision.py -q --tb=short --no-header --basetemp E:\GT-KB\.gtkb-state\release-main-20260630\.tmp-pytest-wi4943\basetemp-run1 -o cache_dir=.tmp-pytest-wi4943\cache-run1
206 collected
160 failed, 46 passed in 80.30s
```

Primary failure class:

```text
ImportError: cannot import name 'MalformedBridgeStatusError' from 'bridge_work_intent_registry'
(E:\GT-KB\.gtkb-state\release-main-20260630\scripts\bridge_work_intent_registry.py)
```

The staged `scripts/dispatcher_runtime.py` expects newer work-intent registry symbols, but `scripts/bridge_work_intent_registry.py` is not in the approved v005 target paths.

Second clear missing-file failure:

```text
test_storm_watchdog_launcher_runs_powershell_headless_on_windows
storm watchdog script missing:
E:\GT-KB\.gtkb-state\release-main-20260630\scripts\ops\harness_storm_watchdog.ps1
```

The v005 target envelope includes `scripts/ops/harness_storm_watchdog_launcher.py` but not the PowerShell script that launcher invokes.

## Out-Of-Envelope Dependency Evidence

Both blocker paths exist in `research` commit `c45b5a28d`, but the release worktree differs from that commit:

```text
git -C .gtkb-state/release-main-20260630 diff --name-status c45b5a28d -- scripts/bridge_work_intent_registry.py scripts/ops/harness_storm_watchdog.ps1
M       scripts/bridge_work_intent_registry.py
D       scripts/ops/harness_storm_watchdog.ps1

git ls-tree -r --name-only c45b5a28d -- scripts/bridge_work_intent_registry.py scripts/ops/harness_storm_watchdog.ps1
scripts/bridge_work_intent_registry.py
scripts/ops/harness_storm_watchdog.ps1
```

The current approved target_paths in `bridge/gtkb-wi4943-release-branch-dispatcher-substrate-reconciliation-005.md` do not include either path. Prime Builder therefore treated this as a target-envelope blocker instead of silently expanding the implementation.

## Specification Links

- `SPEC-DISPATCHER-CONTROL-SURFACE-001` - health/status/drain now pass at the command level, but focused tests show the release control surface is not yet test-clean.
- `SPEC-CENTRALIZED-DISPATCH-SERVICE-001` - staged daemon/runtime work requires the matching work-intent registry dependency before it can be considered operational.
- `ADR-DISPATCHER-ARCHITECTURE-001` - no retired poller or alternate queue was restored.
- `DCL-SINGLE-HARNESS-DISPATCHER-DESKTOP-TASK-001` - the headless watchdog launcher requires its PowerShell script dependency before the no-window supervisor path can be verified.
- `GOV-FILE-BRIDGE-AUTHORITY-001` - this `NEW` implementation report records the blocker and returns the thread to Loyal Opposition rather than expanding scope directly.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - the report maps failing verification back to the proposal's linked dispatcher requirements.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - this report carries Project Authorization, Project, Work Item, and target-path metadata.
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` - Prime Builder stayed inside the active PAUTH and approved bridge target envelope.
- `DCL-PROJECT-AUTHORIZATION-ENVELOPE-001` - the blocker is specifically that two required dependencies are outside the approved envelope.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - `VERIFIED` is not requested because focused pytest fails.
- `GOV-STANDING-BACKLOG-001` - WI-4943 remains the backlog authority for this release-integration defect.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` - the partial implementation and blocker are preserved as bridge evidence.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` - the release defect remains represented through DELIB, WI, PAUTH, proposal, report, and test evidence.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - unresolved work remains bounded by the PAUTH expiry.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - all inspected and modified paths are under `E:\GT-KB`, including the in-root release worktree.

## Owner Decisions / Input

Existing owner authorization remains `DELIB-20260701-ADHOC-RELEASE-DISPATCHER-SUBSTRATE-AUTH` and `PAUTH-PROJECT-GTKB-AD-HOC-RELEASE-20260701-WI-4943-DISPATCHER-SUBSTRATE`, expiring `2026-07-02T00:00:00Z` unless renewed or replaced.

No new owner decision was requested or available to this non-interactive auto-dispatch worker. The blocker can be resolved through a revised bridge envelope that adds the two required dependency paths, or through an explicit Loyal Opposition determination that the existing envelope already covers them indirectly. Prime Builder did not assume either outcome.

## Prior Deliberations

- `DELIB-20260701-ADHOC-RELEASE-DISPATCHER-SUBSTRATE-AUTH` - owner authorized the scoped WI/PAUTH for release-branch dispatcher substrate reconciliation.
- `DELIB-20266138` - owner selected minimum-viable black-box dispatcher activation and autonomous drive of the critical dispatcher path.
- `DELIB-20266667` - GO for WI-4942 drain/report live-worker parity.
- `bridge/gtkb-wi4937-dispatcher-supervisor-governance-006.md` - terminal VERIFIED supervisor governance evidence.
- `bridge/gtkb-wi4942-dispatch-drain-live-worker-parity-*.md` - prior drain/live-worker parity bridge evidence.
- `bridge/gtkb-wi4943-release-branch-dispatcher-substrate-reconciliation-005.md` - corrected target envelope.
- `bridge/gtkb-wi4943-release-branch-dispatcher-substrate-reconciliation-006.md` - latest Loyal Opposition GO.

## Acceptance Status

- Clean release branch dispatcher health: PASS after topology reconciliation.
- Clean release branch daemon status: PASS for command execution; reports `active_substrate=cross_harness_trigger`, `mode=shadow`, `running=true`.
- Dispatcher topology A/E and D/F/C/B: PASS.
- Dry-run drain: PASS.
- Ruff lint and format: PASS.
- Focused pytest: FAIL (`160 failed, 46 passed`).
- Release commit: NOT CREATED.
- Verification request: NOT MADE.

## Required Follow-Up

File a revised proposal or equivalent Loyal Opposition-approved scope clarification before modifying:

- `scripts/bridge_work_intent_registry.py`
- `scripts/ops/harness_storm_watchdog.ps1`

After those dependencies are authorized and reconciled, rerun the focused pytest slice, create a release commit only if tests pass, and file a new implementation report with commit hash and clean evidence.

## Risk And Rollback

Risk is a partially staged release worktree. The staged set remains inside the WI-4943 target envelope except for no out-of-envelope modifications; the two missing dependencies were not edited. If the owner or Loyal Opposition decides not to proceed, rollback is to reset the in-root release worktree to `174e8c5f1` or a later approved release commit through the normal governed release-branch cleanup path. This auto-dispatch did not push or deploy anything.

---

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
