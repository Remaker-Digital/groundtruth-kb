NEW

# GT-KB Bridge Implementation Report - WI-4943 - 011

bridge_kind: implementation_report
Document: gtkb-wi4943-release-branch-dispatcher-substrate-reconciliation
Version: 011
Author: Prime Builder (Codex)
Date: 2026-07-01 UTC
Status: NEW

author_identity: Prime Builder / Codex
author_harness_id: A
author_session_context_id: 2026-07-01T11-49-39Z-prime-builder-A-4f392c
author_model: GPT-5 Codex
author_model_version: 2026-07-01 runtime
author_model_configuration: Codex auto-dispatch, Prime Builder role, approval_policy=never, cwd=E:\GT-KB

Responds to GO: bridge/gtkb-wi4943-release-branch-dispatcher-substrate-reconciliation-010.md
Approved proposal: bridge/gtkb-wi4943-release-branch-dispatcher-substrate-reconciliation-009.md
Prior NO-GO: bridge/gtkb-wi4943-release-branch-dispatcher-substrate-reconciliation-008.md
Project: PROJECT-GTKB-AD-HOC-RELEASE-20260701
Work Item: WI-4943
Project Authorization: PAUTH-PROJECT-GTKB-AD-HOC-RELEASE-20260701-WI-4943-DISPATCHER-SUBSTRATE
Recommended commit type: fix(dispatch)

---

## Implementation Claim

WI-4943 is not complete and this report does not request `VERIFIED`.

Prime Builder resumed from the live latest `GO` at `bridge/gtkb-wi4943-release-branch-dispatcher-substrate-reconciliation-010.md`, obtained the required implementation-start packet, and worked only in the in-root release worktree:

```text
E:\GT-KB\.gtkb-state\release-main-20260630
branch: codex/dispatcher-release-chain-main-20260701
```

The two v009/v010 dependency-envelope additions were applied from the current `research` source into the release worktree:

- `scripts/bridge_work_intent_registry.py`
- `scripts/ops/harness_storm_watchdog.ps1`

Those two paths are authorized by the active implementation packet. The release worktree's Git administrative directory is not writable from this sandbox, so `git restore --source research --worktree --staged -- ...` failed before changing content:

```text
fatal: Unable to create 'E:/GT-KB/.git/worktrees/release-main-20260630/index.lock': Permission denied
```

Prime Builder therefore applied the two approved file contents mechanically to the release worktree but could not stage them. No release commit was created.

Focused verification then exposed a third dispatcher-runtime dependency outside the approved target envelope:

- `scripts/windows_subprocess.py`

That file exists in `research`, is absent from the release worktree, and is denied by the active implementation authorization packet. Prime Builder therefore failed closed instead of expanding scope directly.

## First-Line Role Eligibility And Work-Intent Claim

Durable role resolution was performed through the required canonical reader:

```text
groundtruth-kb/.venv/Scripts/gt.exe harness roles
```

Harness `A` (`codex`) resolves to `prime-builder`.

Work-intent claim evidence:

```json
{
  "rowid": 28455,
  "session_id": "2026-07-01T11-49-39Z-prime-builder-A-4f392c",
  "acting_role": "prime-builder",
  "claim_kind": "go_implementation",
  "latest_bridge_status": "GO",
  "expired": false
}
```

Implementation-start packet evidence:

```text
groundtruth-kb/.venv/Scripts/python.exe scripts/implementation_authorization.py begin --bridge-id gtkb-wi4943-release-branch-dispatcher-substrate-reconciliation
packet_hash: sha256:67c8a46969e5bf7b23f04ce5cf12d24b9ea2cd964a8e24d19da4a9c3688cb3be
latest_status: GO
go_file: bridge/gtkb-wi4943-release-branch-dispatcher-substrate-reconciliation-010.md
proposal_file: bridge/gtkb-wi4943-release-branch-dispatcher-substrate-reconciliation-009.md
PAUTH status: active
PAUTH expires_at: 2026-07-02T00:00:00Z
```

Representative path validation:

| Target | Result |
| --- | --- |
| `scripts/bridge_work_intent_registry.py` | authorized |
| `scripts/ops/harness_storm_watchdog.ps1` | authorized |
| `scripts/windows_subprocess.py` | denied: outside implementation authorization scope |

## Release Worktree State

Current release worktree status after applying the two authorized dependency files:

```text
## codex/dispatcher-release-chain-main-20260701...origin/codex/dispatcher-release-chain-main-20260701
A  bridge/gtkb-wi4937-dispatcher-supervisor-governance-001.md
A  bridge/gtkb-wi4937-dispatcher-supervisor-governance-002.md
A  bridge/gtkb-wi4937-dispatcher-supervisor-governance-003.md
A  bridge/gtkb-wi4937-dispatcher-supervisor-governance-004.md
A  bridge/gtkb-wi4937-dispatcher-supervisor-governance-005.md
A  bridge/gtkb-wi4937-dispatcher-supervisor-governance-006.md
M  config/dispatcher/rules.toml
A  groundtruth-kb/src/groundtruth_kb/bridge/role_state.py
M  groundtruth-kb/src/groundtruth_kb/bridge_dispatch_config.py
M  groundtruth-kb/src/groundtruth_kb/bridge_dispatch_reset.py
M  groundtruth-kb/src/groundtruth_kb/cli.py
A  groundtruth-kb/src/groundtruth_kb/dispatcher_supervisor.py
M  groundtruth-kb/src/groundtruth_kb/project/doctor.py
M  harness-state/harness-registry.json
M  platform_tests/groundtruth_kb/cli/test_bridge_config_cli.py
A  platform_tests/groundtruth_kb/cli/test_bridge_dispatch_daemon_supervisor.py
A  platform_tests/scripts/test_dispatcher_daemon_supervision.py
A  platform_tests/scripts/test_dispatcher_runtime.py
A  platform_tests/scripts/test_gtkb_dispatcher_daemon.py
 M scripts/bridge_work_intent_registry.py
A  scripts/dispatcher_runtime.py
A  scripts/ensure_dispatcher_daemon.py
A  scripts/gtkb_dispatcher_daemon.py
A  scripts/install_dispatcher_daemon_task.ps1
A  scripts/ops/harness_storm_watchdog_launcher.py
?? .tmp-pytest-wi4943/
?? scripts/ops/harness_storm_watchdog.ps1
```

The two unstaged source-path entries are authorized by the v009/v010 packet. They remain unstaged because the Git index lock path is not writable in this sandbox.

## Specification Links

- `SPEC-DISPATCHER-CONTROL-SURFACE-001` - dispatcher health/status/drain/config commands must agree and expose release-operable dispatcher state from the release branch.
- `SPEC-CENTRALIZED-DISPATCH-SERVICE-001` - bridge dispatch must remain daemon-owned, bounded, and operational without restoring retired trigger or poller paths.
- `ADR-DISPATCHER-ARCHITECTURE-001` - the dispatcher daemon remains the active automation substrate; this report does not restore retired pollers or hook-driven automation.
- `DCL-SINGLE-HARNESS-DISPATCHER-DESKTOP-TASK-001` - Windows dispatcher persistence must remain headless/no-window safe.
- `GOV-FILE-BRIDGE-AUTHORITY-001` - this implementation report is the next numbered Prime Builder response to the live latest `GO`.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - the report carries forward the approved proposal's governing specifications.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - Project Authorization, Project, Work Item, and target-path evidence are preserved.
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` - PAUTH is active but does not broaden bridge `target_paths`.
- `DCL-PROJECT-AUTHORIZATION-ENVELOPE-001` - implementation must stay inside the active envelope and fail closed on `scripts/windows_subprocess.py`.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - this blocker report maps linked requirements to executed evidence and explicitly does not request `VERIFIED`.
- `GOV-STANDING-BACKLOG-001` - WI-4943 remains open in MemBase.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` - the new scope blocker is preserved as a bridge artifact.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` - the implementation state is carried through the artifact graph rather than informal scratch state.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - unresolved work remains bounded by the PAUTH expiry and bridge state.
- `SPEC-AUQ-POLICY-ENGINE-001` - owner authorization remains `DELIB-20260701-ADHOC-RELEASE-DISPATCHER-SUBSTRATE-AUTH`.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - all live work stayed under `E:\GT-KB`; the release worktree is in-root under `.gtkb-state\release-main-20260630`.
- `ADR-CODEX-HOOK-PARITY-FALLBACK-001` - Codex used explicit helper-mediated bridge filing and implementation-start checks.

## Owner Decisions / Input

No new owner decision was captured or requested in this non-interactive auto-dispatch.

The carried-forward owner evidence remains:

- `DELIB-20260701-ADHOC-RELEASE-DISPATCHER-SUBSTRATE-AUTH`
- `PAUTH-PROJECT-GTKB-AD-HOC-RELEASE-20260701-WI-4943-DISPATCHER-SUBSTRATE`

This worker cannot ask the owner interactively. The practical next path is another governed revision that either adds `scripts/windows_subprocess.py` to the WI-4943 target envelope or narrows the approved acceptance criteria so the staged runtime no longer depends on it.

## Prior Deliberations

- `bridge/gtkb-wi4943-release-branch-dispatcher-substrate-reconciliation-009.md` - approved revised implementation proposal carried forward.
- `bridge/gtkb-wi4943-release-branch-dispatcher-substrate-reconciliation-010.md` - Loyal Opposition GO verdict authorizing this implementation attempt.
- `bridge/gtkb-wi4943-release-branch-dispatcher-substrate-reconciliation-007.md` - prior blocker report for dependency-envelope gaps.
- `bridge/gtkb-wi4943-release-branch-dispatcher-substrate-reconciliation-008.md` - Loyal Opposition NO-GO confirming the two v009 dependency additions.
- `DELIB-20260701-ADHOC-RELEASE-DISPATCHER-SUBSTRATE-AUTH` - owner authorized the scoped WI/PAUTH for release-branch dispatcher substrate reconciliation.

## Specification-Derived Verification / Spec-To-Test Mapping

| Specification / governing surface | Executed evidence | Observed result |
| --- | --- | --- |
| `SPEC-DISPATCHER-CONTROL-SURFACE-001` | `gt bridge dispatch health --json` from release worktree with release `PYTHONPATH` | PASS; `health_status: PASS`; selected PB `A,E`; selected LO `D,F,C,B`. |
| `SPEC-DISPATCHER-CONTROL-SURFACE-001` | `gt bridge dispatch status --json` from release worktree with release `PYTHONPATH` | PASS; `health_status: PASS`; no health findings. |
| `SPEC-DISPATCHER-CONTROL-SURFACE-001` | `gt bridge dispatch drain --timeout 1 --dry-run --json` from release worktree with release `PYTHONPATH` | PASS-like dry run; no markers written, drained PIDs, or terminated PIDs. |
| `SPEC-CENTRALIZED-DISPATCH-SERVICE-001` | `gt bridge dispatch daemon status --json` from release worktree with release `PYTHONPATH` | Command succeeds; reports `running: true`, `mode: shadow`, no missing-file exception. |
| `DCL-SINGLE-HARNESS-DISPATCHER-DESKTOP-TASK-001` | `pytest platform_tests/scripts/test_dispatcher_daemon_supervision.py platform_tests/groundtruth_kb/cli/test_bridge_dispatch_daemon_supervisor.py platform_tests/groundtruth_kb/cli/test_bridge_config_cli.py -q --tb=short` | PASS: 31 passed, 1 warning. |
| `SPEC-CENTRALIZED-DISPATCH-SERVICE-001` / `ADR-DISPATCHER-ARCHITECTURE-001` | `pytest platform_tests/scripts/test_gtkb_dispatcher_daemon.py platform_tests/scripts/test_dispatcher_runtime.py platform_tests/scripts/test_dispatcher_daemon_supervision.py platform_tests/groundtruth_kb/cli/test_bridge_dispatch_daemon_supervisor.py platform_tests/groundtruth_kb/cli/test_bridge_config_cli.py -q --tb=short` | FAIL: 159 failed, 47 passed. Primary failure class is `ModuleNotFoundError: No module named 'windows_subprocess'` from `scripts/dispatcher_runtime.py`. |
| `SPEC-CENTRALIZED-DISPATCH-SERVICE-001` | `pytest platform_tests/scripts/test_dispatcher_runtime.py::test_runtime_inflight_lock_blocks_concurrent_hook_invocations -q --tb=short` | FAIL: `ModuleNotFoundError: No module named 'windows_subprocess'`. |
| `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` / `DCL-PROJECT-AUTHORIZATION-ENVELOPE-001` | `implementation_authorization.py validate --target scripts/windows_subprocess.py` | FAIL-closed: target path outside implementation authorization scope. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | This table and commands below | Satisfied as a blocker report; not a verification request. |
| `GOV-STANDING-BACKLOG-001` | `gt backlog show WI-4943 --json` | WI-4943 exists and remains `resolution_status: open`. |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | Path review and release worktree location | All live edits and report files stayed under `E:\GT-KB`. |

## Blocking Evidence

The newly exposed dependency is concrete and outside the approved envelope:

```text
Test-Path E:\GT-KB\scripts\windows_subprocess.py
True

Test-Path E:\GT-KB\.gtkb-state\release-main-20260630\scripts\windows_subprocess.py
False

rg -n "windows_subprocess|no_window_subprocess_kwargs|prefer_pythonw_executable" scripts platform_tests
scripts\dispatcher_runtime.py:149:from windows_subprocess import no_window_subprocess_kwargs, prefer_pythonw_executable
```

Focused failing test:

```text
platform_tests/scripts/test_dispatcher_runtime.py::test_runtime_inflight_lock_blocks_concurrent_hook_invocations
E   ModuleNotFoundError: No module named 'windows_subprocess'
```

Authorization denial:

```text
groundtruth-kb/.venv/Scripts/python.exe scripts/implementation_authorization.py validate --target scripts/windows_subprocess.py
{
  "authorized": false,
  "error": "Target path outside implementation authorization scope: scripts/windows_subprocess.py"
}
```

## Commands Run

```text
groundtruth-kb/.venv/Scripts/gt.exe harness roles
groundtruth-kb/.venv/Scripts/python.exe .codex/skills/bridge/helpers/scan_bridge.py --role prime-builder --compact --format json
groundtruth-kb/.venv/Scripts/python.exe .codex/skills/bridge/helpers/show_thread_bridge.py gtkb-wi4943-release-branch-dispatcher-substrate-reconciliation --format json --preview-lines 2000
groundtruth-kb/.venv/Scripts/python.exe scripts/implementation_authorization.py begin --bridge-id gtkb-wi4943-release-branch-dispatcher-substrate-reconciliation
groundtruth-kb/.venv/Scripts/python.exe scripts/implementation_authorization.py validate --target scripts/bridge_work_intent_registry.py
groundtruth-kb/.venv/Scripts/python.exe scripts/implementation_authorization.py validate --target scripts/ops/harness_storm_watchdog.ps1
groundtruth-kb/.venv/Scripts/python.exe scripts/implementation_authorization.py validate --target scripts/windows_subprocess.py
```

Release-worktree commands used `E:\GT-KB\groundtruth-kb\.venv\Scripts\python.exe` / `gt.exe` with `PYTHONPATH` pointed at `E:\GT-KB\.gtkb-state\release-main-20260630\groundtruth-kb\src`:

```text
gt bridge dispatch health --json
gt bridge dispatch status --json
gt bridge dispatch daemon status --json
gt bridge dispatch drain --timeout 1 --dry-run --json
python -m pytest platform_tests/scripts/test_gtkb_dispatcher_daemon.py platform_tests/scripts/test_dispatcher_runtime.py platform_tests/scripts/test_dispatcher_daemon_supervision.py platform_tests/groundtruth_kb/cli/test_bridge_dispatch_daemon_supervisor.py platform_tests/groundtruth_kb/cli/test_bridge_config_cli.py -q --tb=short
python -m pytest platform_tests/scripts/test_dispatcher_daemon_supervision.py platform_tests/groundtruth_kb/cli/test_bridge_dispatch_daemon_supervisor.py platform_tests/groundtruth_kb/cli/test_bridge_config_cli.py -q --tb=short
python -m pytest platform_tests/scripts/test_dispatcher_runtime.py::test_runtime_inflight_lock_blocks_concurrent_hook_invocations -q --tb=short
python -m ruff check --no-cache <16 changed Python paths>
python -m ruff format --check --no-cache <16 changed Python paths>
```

## Code Quality Evidence

The first Ruff invocation failed because `.ruff_cache` in the linked release worktree is not writable from this sandbox. The check was rerun with caching disabled:

```text
python -m ruff check --no-cache <16 changed Python paths>
All checks passed!

python -m ruff format --check --no-cache <16 changed Python paths>
16 files already formatted
```

## Recommended Commit Type

- Recommended commit type: `fix(dispatch)`
- Justification: the intended eventual commit remains a release-blocking dispatcher substrate repair, but no commit was created in this implementation attempt.

## Acceptance Criteria Status

- [x] Clean release branch `gt bridge dispatch health --json` returns `PASS`.
- [x] Clean release branch `gt bridge dispatch daemon status --json` succeeds without the missing `gtkb_dispatcher_daemon.py` exception.
- [x] Dispatcher topology on the release branch selects Prime Builder A/E and Loyal Opposition D/F/C/B.
- [ ] Focused dispatcher daemon/runtime tests pass.
- [ ] Release worktree changes are stageable and committable from the local environment.
- [ ] No additional out-of-envelope dependency paths remain.

## Risk And Rollback

Risk is now a third dependency-envelope gap: adding `scripts/windows_subprocess.py` is likely required for the staged runtime and tests, but it is outside the current GO. Expanding scope directly would violate `DCL-PROJECT-AUTHORIZATION-ENVELOPE-001`.

Rollback remains append-only bridge correction plus either reverting the release worktree changes or revising the proposal to include the missing helper. No published release commit was created by this worker.

## Loyal Opposition Asks

1. Issue `NO-GO` for this implementation report because `scripts/windows_subprocess.py` is a required dependency outside the current target envelope.
2. Confirm that the next Prime Builder step should be a revised proposal adding `scripts/windows_subprocess.py`, or a scoped alternative that removes the dependency from `scripts/dispatcher_runtime.py`.
