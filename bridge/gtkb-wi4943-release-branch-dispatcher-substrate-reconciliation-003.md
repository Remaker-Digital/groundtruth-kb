NEW

# Implementation Report Blocker - WI-4943 release-branch dispatcher substrate reconciliation

bridge_kind: implementation_report
Document: gtkb-wi4943-release-branch-dispatcher-substrate-reconciliation
Version: 003
Author: Codex Prime Builder, harness A
Date: 2026-07-01 UTC
Responds to GO: bridge/gtkb-wi4943-release-branch-dispatcher-substrate-reconciliation-002.md
Approved proposal: bridge/gtkb-wi4943-release-branch-dispatcher-substrate-reconciliation-001.md

author_identity: prime-builder/codex
author_harness_id: A
author_session_context_id: 2026-07-01T09-07-57Z-prime-builder-A-a2bf6c
author_model: GPT-5 Codex
author_model_version: GPT-5
author_model_configuration: Codex auto-dispatch Prime Builder session; dispatcher id 2026-07-01T09-07-57Z-prime-builder-A-a2bf6c

Project Authorization: PAUTH-PROJECT-GTKB-AD-HOC-RELEASE-20260701-WI-4943-DISPATCHER-SUBSTRATE
Project: PROJECT-GTKB-AD-HOC-RELEASE-20260701
Work Item: WI-4943

Recommended commit type: fix(dispatch)

---

## Implementation Claim

WI-4943 is not complete and this report does not request `VERIFIED`.

This worker obtained the live GO implementation authorization packet and inspected the clean release worktree at `E:\GT-KB\.gtkb-state\release-main-20260630`. That worktree already contained staged dispatcher substrate changes before this worker made any release-worktree edits. This worker did not change release-worktree source, test, config, harness-state, docs, or git history.

The selected GO cannot be completed under the current authorization envelope because release-health acceptance now requires files outside the approved `target_paths` list:

- `config/dispatcher/rules.toml` is needed to satisfy the approved A/E Prime Builder and D/F/C/B Loyal Opposition topology, but `implementation_authorization.py validate --target config/dispatcher/rules.toml` denies it.
- `harness-state/harness-registry.json` is needed to bring the release worktree role projection up to the approved topology, but the validator denies it.
- `groundtruth-kb/src/groundtruth_kb/bridge/role_state.py` is imported by the staged `scripts/dispatcher_runtime.py`, is present in the root checkout, is absent from the release worktree, and is denied by the validator.
- `scripts/ops/harness_storm_watchdog_launcher.py` is required by the staged supervisor tests, is absent from the release worktree, and is denied by the validator.

The report records the blocker and expected NO-GO evidence rather than widening scope or editing unapproved topology/support files.

## Specification Links

- `SPEC-DISPATCHER-CONTROL-SURFACE-001` - dispatcher health/status/drain/config commands must agree and expose release-operable dispatcher state from the release branch.
- `SPEC-CENTRALIZED-DISPATCH-SERVICE-001` - bridge dispatch must be daemon-owned, bounded, and operational without restoring retired trigger or poller paths.
- `ADR-DISPATCHER-ARCHITECTURE-001` - dispatcher daemon is the active automation substrate; release integration must preserve the dispatcher-only architecture.
- `DCL-SINGLE-HARNESS-DISPATCHER-DESKTOP-TASK-001` - Windows dispatcher persistence must be headless/no-window safe.
- `GOV-FILE-BRIDGE-AUTHORITY-001` - implementation requires a live GO, implementation-start authorization, post-implementation report, and LO verification.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - the report carries forward the proposal's governing specs.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - the report preserves Project Authorization, Project, Work Item, and target-path evidence.
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` - the PAUTH is active but does not broaden the bridge target envelope.
- `DCL-PROJECT-AUTHORIZATION-ENVELOPE-001` - implementation must stay inside the approved envelope and fail closed on scope drift.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - the report maps linked specs to executed evidence and records failures.
- `GOV-STANDING-BACKLOG-001` - WI-4943 remains the durable backlog authority and remains open.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` - the blocker is preserved as a bridge artifact rather than informal chat.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` - the release defect is advanced through durable artifacts.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - unresolved deferral remains bounded by the proposal expiry.
- `SPEC-AUQ-POLICY-ENGINE-001` - owner authorization is carried by `DELIB-20260701-ADHOC-RELEASE-DISPATCHER-SUBSTRATE-AUTH`.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - all reads and bridge writes stayed under `E:\GT-KB`.
- `ADR-CODEX-HOOK-PARITY-FALLBACK-001` - Codex used helper-mediated bridge filing and explicit checks.

## Owner Decisions / Input

No new owner decision was captured in this non-interactive auto-dispatch.

Owner/governance action is required before this GO can complete: file a revised bridge proposal or other governed authorization that includes the missing topology and support paths, or explicitly narrows the WI-4943 acceptance criteria so those paths are no longer required.

Carried-forward owner evidence:

- `DELIB-20260701-ADHOC-RELEASE-DISPATCHER-SUBSTRATE-AUTH` authorized WI-4943 and the PAUTH.
- `PAUTH-PROJECT-GTKB-AD-HOC-RELEASE-20260701-WI-4943-DISPATCHER-SUBSTRATE` is active until `2026-07-02T00:00:00Z`.

## Prior Deliberations

Deliberation search refreshed during this dispatch:

```text
groundtruth-kb/.venv/Scripts/gt.exe deliberations search "WI-4943 release branch dispatcher substrate reconciliation" --limit 8
```

Relevant results:

- `DELIB-20260701-ADHOC-RELEASE-DISPATCHER-SUBSTRATE-AUTH` - owner authorized this scoped release-branch reconciliation WI/PAUTH.
- `DELIB-20266138` - owner selected minimum-viable black-box dispatcher activation.
- `DELIB-20266667` - GO for WI-4942 drain/report live-worker parity.
- `bridge/gtkb-wi4937-dispatcher-supervisor-governance-006.md` - prior VERIFIED supervisor governance evidence.
- `bridge/gtkb-wi4942-dispatch-drain-live-worker-parity-006.md` - prior VERIFIED drain/live-worker parity evidence.
- `bridge/gtkb-wi4933-cursor-bridge-skill-route-repair-004.md` and sibling WI-4933 bridge records - prior VERIFIED dispatcher substrate evidence cited by the proposal.

## Implementation Authorization Evidence

```text
groundtruth-kb/.venv/Scripts/python.exe scripts/implementation_authorization.py begin --bridge-id gtkb-wi4943-release-branch-dispatcher-substrate-reconciliation
```

Observed result:

- `latest_status`: `GO`
- `go_file`: `bridge/gtkb-wi4943-release-branch-dispatcher-substrate-reconciliation-002.md`
- `packet_hash`: `sha256:cb6751cb011cb7a516711f1d510f83de6702053898698f94a902e2e95aab3cfa`
- PAUTH status: `active`

Representative path validation:

| Target | Result |
| --- | --- |
| `groundtruth-kb/src/groundtruth_kb/bridge_dispatch_config.py` | authorized |
| `platform_tests/groundtruth_kb/cli/test_bridge_config_cli.py` | authorized |
| `config/dispatcher/rules.toml` | denied: outside implementation authorization scope |
| `harness-state/harness-registry.json` | denied: outside implementation authorization scope |
| `groundtruth-kb/src/groundtruth_kb/bridge/role_state.py` | denied: outside implementation authorization scope |
| `scripts/ops/harness_storm_watchdog_launcher.py` | denied: outside implementation authorization scope |

## Release Worktree State

Worktree inspected:

```text
git -c safe.directory=E:/GT-KB/.gtkb-state/release-main-20260630 -C .gtkb-state/release-main-20260630 status --short --branch
```

Observed state before this report:

```text
## codex/dispatcher-release-chain-main-20260701...origin/codex/dispatcher-release-chain-main-20260701
A  bridge/gtkb-wi4937-dispatcher-supervisor-governance-001.md
A  bridge/gtkb-wi4937-dispatcher-supervisor-governance-002.md
A  bridge/gtkb-wi4937-dispatcher-supervisor-governance-003.md
A  bridge/gtkb-wi4937-dispatcher-supervisor-governance-004.md
A  bridge/gtkb-wi4937-dispatcher-supervisor-governance-005.md
A  bridge/gtkb-wi4937-dispatcher-supervisor-governance-006.md
M  groundtruth-kb/src/groundtruth_kb/bridge_dispatch_config.py
M  groundtruth-kb/src/groundtruth_kb/bridge_dispatch_reset.py
MM groundtruth-kb/src/groundtruth_kb/cli.py
A  groundtruth-kb/src/groundtruth_kb/dispatcher_supervisor.py
M  groundtruth-kb/src/groundtruth_kb/project/doctor.py
M  platform_tests/groundtruth_kb/cli/test_bridge_config_cli.py
A  platform_tests/groundtruth_kb/cli/test_bridge_dispatch_daemon_supervisor.py
A  platform_tests/scripts/test_dispatcher_daemon_supervision.py
A  platform_tests/scripts/test_dispatcher_runtime.py
A  platform_tests/scripts/test_gtkb_dispatcher_daemon.py
A  scripts/dispatcher_runtime.py
A  scripts/ensure_dispatcher_daemon.py
A  scripts/gtkb_dispatcher_daemon.py
A  scripts/install_dispatcher_daemon_task.ps1
```

`groundtruth-kb/src/groundtruth_kb/cli.py` has staged changes plus an unstaged deletion of unrelated CLI surfaces (`skills_group` and `hygiene supersession-scan`). This worker did not stage, unstage, revert, or modify that existing split.

## Specification-Derived Verification / Spec-to-Test Mapping

| Specification / governing surface | Executed evidence | Observed result |
| --- | --- | --- |
| `SPEC-DISPATCHER-CONTROL-SURFACE-001` | `PYTHONPATH=E:\GT-KB\.gtkb-state\release-main-20260630\groundtruth-kb\src E:\GT-KB\groundtruth-kb\.venv\Scripts\python.exe -m groundtruth_kb.cli bridge dispatch health --json` from the release worktree | FAIL: `no active dispatchable harness is eligible for role 'loyal-opposition'`; selected PB only `A`, selected LO empty. |
| `SPEC-DISPATCHER-CONTROL-SURFACE-001` | same Python path, `bridge dispatch status --json` | Config/status sees C/D/F as active LO, but selection admits none because release config qualities are below the source quality floor; B is still suspended prime-builder and E is absent from the release projection. |
| `SPEC-DISPATCHER-CONTROL-SURFACE-001` | same Python path, `bridge dispatch drain --timeout 1 --dry-run --json` | PASS-like dry-run result: `drain_markers_written=0`, `drained_pids=[]`, `terminated_pids=[]`. This does not overcome health failure. |
| `SPEC-CENTRALIZED-DISPATCH-SERVICE-001` | same Python path, `bridge dispatch daemon status --json` | Command succeeds, but reports `active_substrate: cross_harness_trigger`, `mode: shadow`, `pid_provenance_verified: false`, not the proposed dispatcher-daemon release posture. |
| `ADR-DISPATCHER-ARCHITECTURE-001` | daemon status above | Not satisfied: release state still reports `active_substrate: cross_harness_trigger`. |
| `DCL-SINGLE-HARNESS-DISPATCHER-DESKTOP-TASK-001` | `pytest platform_tests/groundtruth_kb/cli/test_bridge_config_cli.py platform_tests/groundtruth_kb/cli/test_bridge_dispatch_daemon_supervisor.py platform_tests/scripts/test_dispatcher_daemon_supervision.py platform_tests/scripts/test_dispatcher_runtime.py platform_tests/scripts/test_gtkb_dispatcher_daemon.py -q --tb=short` with release `PYTHONPATH` | FAIL: 161 failed, 45 passed. First failure: missing `scripts/ops/harness_storm_watchdog_launcher.py`. Many runtime failures: `groundtruth_kb.bridge.role_state` missing and staged `scripts/dispatcher_runtime.py` APIs absent to tests. |
| `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` / `DCL-PROJECT-AUTHORIZATION-ENVELOPE-001` | `implementation_authorization.py validate` on needed extra paths | FAIL-closed: topology/support paths listed above are outside the packet. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | This table and command evidence | Satisfied as a blocker report: every linked requirement has executed evidence, and the report explicitly does not request `VERIFIED`. |
| `GOV-STANDING-BACKLOG-001` | `groundtruth-kb/.venv/Scripts/gt.exe backlog show WI-4943 --json` | WI-4943 exists, status `open`, stage `backlogged`; acceptance summary matches the release-health goals. |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | Path review | All reads and report writes stayed under `E:\GT-KB`; release worktree is in-root at `.gtkb-state/release-main-20260630`. |

## Commands Run

```text
groundtruth-kb/.venv/Scripts/gt.exe harness roles
groundtruth-kb/.venv/Scripts/python.exe .codex/skills/bridge/helpers/show_thread_bridge.py gtkb-wi4943-release-branch-dispatcher-substrate-reconciliation --format json --preview-lines 500
groundtruth-kb/.venv/Scripts/python.exe scripts/implementation_authorization.py begin --bridge-id gtkb-wi4943-release-branch-dispatcher-substrate-reconciliation
groundtruth-kb/.venv/Scripts/python.exe scripts/implementation_authorization.py validate --target groundtruth-kb/src/groundtruth_kb/bridge_dispatch_config.py
groundtruth-kb/.venv/Scripts/python.exe scripts/implementation_authorization.py validate --target platform_tests/groundtruth_kb/cli/test_bridge_config_cli.py
groundtruth-kb/.venv/Scripts/python.exe scripts/implementation_authorization.py validate --target config/dispatcher/rules.toml
groundtruth-kb/.venv/Scripts/python.exe scripts/implementation_authorization.py validate --target harness-state/harness-registry.json
groundtruth-kb/.venv/Scripts/python.exe scripts/implementation_authorization.py validate --target groundtruth-kb/src/groundtruth_kb/bridge/role_state.py
groundtruth-kb/.venv/Scripts/python.exe scripts/implementation_authorization.py validate --target scripts/ops/harness_storm_watchdog_launcher.py
```

Release-worktree commands used the root venv Python with `PYTHONPATH` pointed at the release worktree source because the release worktree has no `groundtruth-kb/.venv`:

```text
$env:PYTHONPATH='E:\GT-KB\.gtkb-state\release-main-20260630\groundtruth-kb\src'
E:\GT-KB\groundtruth-kb\.venv\Scripts\python.exe -m groundtruth_kb.cli bridge dispatch health --json
E:\GT-KB\groundtruth-kb\.venv\Scripts\python.exe -m groundtruth_kb.cli bridge dispatch status --json
E:\GT-KB\groundtruth-kb\.venv\Scripts\python.exe -m groundtruth_kb.cli bridge dispatch daemon status --json
E:\GT-KB\groundtruth-kb\.venv\Scripts\python.exe -m groundtruth_kb.cli bridge dispatch drain --timeout 1 --dry-run --json
E:\GT-KB\groundtruth-kb\.venv\Scripts\python.exe -m pytest platform_tests/groundtruth_kb/cli/test_bridge_config_cli.py platform_tests/groundtruth_kb/cli/test_bridge_dispatch_daemon_supervisor.py platform_tests/scripts/test_dispatcher_daemon_supervision.py platform_tests/scripts/test_dispatcher_runtime.py platform_tests/scripts/test_gtkb_dispatcher_daemon.py -q --tb=short
```

Code-quality gates on the changed Python paths in the release worktree:

```text
E:\GT-KB\groundtruth-kb\.venv\Scripts\ruff.exe check --no-cache groundtruth-kb/src/groundtruth_kb/bridge_dispatch_config.py groundtruth-kb/src/groundtruth_kb/bridge_dispatch_reset.py groundtruth-kb/src/groundtruth_kb/cli.py groundtruth-kb/src/groundtruth_kb/dispatcher_supervisor.py groundtruth-kb/src/groundtruth_kb/project/doctor.py platform_tests/groundtruth_kb/cli/test_bridge_config_cli.py platform_tests/groundtruth_kb/cli/test_bridge_dispatch_daemon_supervisor.py platform_tests/scripts/test_dispatcher_daemon_supervision.py platform_tests/scripts/test_dispatcher_runtime.py platform_tests/scripts/test_gtkb_dispatcher_daemon.py scripts/dispatcher_runtime.py scripts/ensure_dispatcher_daemon.py scripts/gtkb_dispatcher_daemon.py
E:\GT-KB\groundtruth-kb\.venv\Scripts\ruff.exe format --check --no-cache groundtruth-kb/src/groundtruth_kb/bridge_dispatch_config.py groundtruth-kb/src/groundtruth_kb/bridge_dispatch_reset.py groundtruth-kb/src/groundtruth_kb/cli.py groundtruth-kb/src/groundtruth_kb/dispatcher_supervisor.py groundtruth-kb/src/groundtruth_kb/project/doctor.py platform_tests/groundtruth_kb/cli/test_bridge_config_cli.py platform_tests/groundtruth_kb/cli/test_bridge_dispatch_daemon_supervisor.py platform_tests/scripts/test_dispatcher_daemon_supervision.py platform_tests/scripts/test_dispatcher_runtime.py platform_tests/scripts/test_gtkb_dispatcher_daemon.py scripts/dispatcher_runtime.py scripts/ensure_dispatcher_daemon.py scripts/gtkb_dispatcher_daemon.py
```

## Observed Results

- Implementation authorization begin: passed, packet `sha256:cb6751cb011cb7a516711f1d510f83de6702053898698f94a902e2e95aab3cfa`.
- Release health: failed because no LO candidate is selected.
- Release daemon status: command no longer throws missing-script exception, but reports `active_substrate=cross_harness_trigger`, `mode=shadow`, `pid_provenance_verified=false`.
- Release drain dry-run: returned empty/no-op result.
- Ruff check with `--no-cache`: passed.
- Ruff format check with `--no-cache`: passed.
- Focused pytest: failed, 161 failed / 45 passed.
- Initial ruff runs without `--no-cache` failed because ruff could not create cache temp files under the release worktree; no-cache reruns are the authoritative code-quality evidence.

## Acceptance Criteria Status

- Clean release branch `gt bridge dispatch health --json` returns `PASS`: FAIL.
- Clean release branch `gt bridge dispatch daemon status --json` succeeds and reports daemon/supervisor state without missing-file exceptions: PARTIAL. It succeeds, but reports the wrong active substrate/posture.
- Dispatcher topology selects Prime Builder A/E and Loyal Opposition D/F/C/B through governed dispatcher config surfaces: FAIL. Release selected PB only A and LO none.
- At least one daemon-driven Loyal Opposition dispatch path is bounded and terminally classified: NOT VERIFIED. Health fails before LO dispatch can be trusted.
- Headless Windows supervisor operation is the release path: NOT VERIFIED. Supervisor tests fail on missing support file.
- README/wiki compare remains clean and dashboard release health remains provider-neutral: NOT TESTED in this blocker pass because earlier required dispatcher gates failed.
- No unrelated dirty root WIP/scratch included: NOT SATISFIED for final implementation. The shared root is dirty and the release worktree contains pre-existing staged/unstaged changes; this worker did not commit or push them.
- Deferred residue expires `2026-07-02T00:00:00Z`: carried forward from proposal/PAUTH.

## Files Changed By This Worker

- `bridge/gtkb-work-tree-hygiene-slice-d-governance-spec-032.md` - separate selected Slice D blocker response.
- `bridge/gtkb-wi4943-release-branch-dispatcher-substrate-reconciliation-003.md` - this implementation blocker report, if live filing succeeds.

This worker did not modify the release worktree files listed in the release-worktree status section.

## Risk And Rollback

Risk is low for this report because it is append-only bridge evidence. The release branch remains unreconciled and should not be treated as release-healthy.

Rollback for this report is another append-only bridge entry; do not edit or delete prior bridge versions. Rollback for the pre-existing release worktree staged changes is outside this worker's action because they predated this dispatch and were not committed here.

## Loyal Opposition Asks

Return `NO-GO` unless a revised proposal/authorization includes the missing topology and support paths, or unless the owner explicitly narrows WI-4943 acceptance criteria. This report intentionally does not request `VERIFIED`.
