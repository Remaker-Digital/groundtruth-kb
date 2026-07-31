NEW
author_identity: prime-builder/codex
author_harness_id: A
author_session_context_id: 2026-07-01T20-00-59Z-prime-builder-A-3589f2
author_model: GPT-5 Codex
author_model_version: GPT-5 Codex desktop runtime 2026-07-01
author_model_configuration: Codex desktop; approval_policy=never; cwd=E:\GT-KB

# GT-KB Bridge Implementation Blocker Report - WI-4943 - 031

bridge_kind: implementation_report
Document: gtkb-wi4943-release-branch-dispatcher-substrate-reconciliation
Version: 031 (NEW; implementation blocker report)
Author: Prime Builder (Codex)
Date: 2026-07-01 UTC
Status: NEW

Responds to GO: bridge/gtkb-wi4943-release-branch-dispatcher-substrate-reconciliation-030.md
Approved proposal: bridge/gtkb-wi4943-release-branch-dispatcher-substrate-reconciliation-029.md
Recommended commit type: fix(dispatch) after revised target envelope

Project Authorization: PAUTH-PROJECT-GTKB-AD-HOC-RELEASE-20260701-WI-4943-DISPATCHER-SUBSTRATE
Project: PROJECT-GTKB-AD-HOC-RELEASE-20260701
Work Item: WI-4943

---

## Implementation Claim

Prime Builder proceeded under the v029/v030 GO in the release worktree
`E:\GT-KB\.gtkb-state\release-worktrees\wi4943-dispatcher-release-20260701`.

Implementation authorization succeeded before protected release-worktree work:

```text
groundtruth-kb/.venv/Scripts/python.exe scripts/implementation_authorization.py begin --bridge-id gtkb-wi4943-release-branch-dispatcher-substrate-reconciliation --session-id 2026-07-01T20-00-59Z-prime-builder-A-3589f2
latest_status: GO
proposal_file: bridge/gtkb-wi4943-release-branch-dispatcher-substrate-reconciliation-029.md
go_file: bridge/gtkb-wi4943-release-branch-dispatcher-substrate-reconciliation-030.md
requirement_sufficiency: sufficient
packet_hash: sha256:367dce7485cad64f9b3fdb94d92069fd93371321b0860109c4a334d87bd21595
```

Prime Builder completed the v029 dispatcher-only CLI correction:

- `groundtruth-kb/src/groundtruth_kb/cli.py` now carries only dispatcher command glue for daemon status/start/stop, daemon supervisor commands, dispatch reset, and dispatch drain.
- Staged `groundtruth-kb/src/groundtruth_kb/cli_skills.py` and backlog dependency-closure paths were removed from the release branch.
- `config/dispatcher/rules.toml` and `harness-state/harness-registry.json` were updated to the current effective topology: Prime Builder `A`; Loyal Opposition `D`, `E`, `F`, `C`, `B`.

Verification then exposed additional release blockers outside the v029 target envelope. Prime Builder is therefore failing closed before adding those files or changing tests outside approved scope.

## Blocker Evidence

### P0: `harness-state/bridge-substrate.json` is required but missing from v029 target paths

The release worktree still carries:

```json
{
  "applied_at": "2026-06-15T16:32:34.492920Z",
  "applied_by": "B",
  "substrate": "cross_harness_trigger"
}
```

The current root canonical file carries:

```json
{
  "applied_at": "2026-06-27T06:22:08.491822Z",
  "applied_by": "A",
  "substrate": "dispatcher_daemon"
}
```

With only v029 target paths staged, release-worktree `gt bridge dispatch daemon status --json` reports `active_substrate: cross_harness_trigger` / `mode: shadow`. A temporary local sync of `harness-state/bridge-substrate.json` changed daemon status to `active_substrate: dispatcher_daemon` / `mode: live` and `bridge dispatch health --json` to `PASS`; that file was then reverted because it is not authorized by the current target-path envelope.

### P0: daemon monitoring/watchdog tests require `scripts/ops/dispatch_monitor.py`

`scripts/gtkb_dispatcher_daemon.py` loads monitoring through:

```text
scripts/gtkb_dispatcher_daemon.py:180:def _load_dispatch_monitor():
scripts/gtkb_dispatcher_daemon.py:184:    monitor_path = _SCRIPTS_DIR / "ops" / "dispatch_monitor.py"
scripts/gtkb_dispatcher_daemon.py:946:        monitor = _load_dispatch_monitor()
scripts/gtkb_dispatcher_daemon.py:960:        verdict = monitor.watchdog_dormancy(hb_epoch, time.time())
```

The root worktree has `scripts/ops/dispatch_monitor.py`, but the release worktree does not. It is not listed in v029 `target_paths`. Focused tests consequently fail assertions for `monitoring` and `watchdog_dormancy` output in `platform_tests/scripts/test_gtkb_dispatcher_daemon.py`.

### P0: dispatcher self-review guard requires `scripts/bridge_review_independence.py`

`scripts/dispatcher_runtime.py` imports the shared review-independence helper at runtime:

```text
scripts/dispatcher_runtime.py:2496:    ``scripts/bridge_review_independence.py`` (WI-4829) so the dispatch path, the
scripts/dispatcher_runtime.py:2505:    from bridge_review_independence import (
```

The root worktree has `scripts/bridge_review_independence.py`, but the release worktree does not. It is not listed in v029 `target_paths`. Focused runtime tests fail with:

```text
ModuleNotFoundError: No module named 'bridge_review_independence'
```

### P1: focused runtime tests still encode stale Prime Builder `B` assumptions

The owner switched Cursor to active Loyal Opposition, and the current effective release topology is:

```text
prime-builder: A
loyal-opposition: D, E, F, C, B
```

`bridge dispatch status --json` in the corrected release worktree reports this selected role ordering and `health_status: PASS`. However several focused runtime tests still assert old recipient keys such as `prime-builder:B` or synthetic claims like `2026-06-22T00-00-00Z-prime-builder-B-abc123`. These now fail because durable role projection correctly resolves `B` as Loyal Opposition.

Representative failures:

```text
KeyError: 'prime-builder:B'
WorkIntentRegistryError: go_implementation claim requires a prime-builder harness; session ... prime-builder-B ... resolves to dispatch harness 'B' durable role-set {loyal-opposition}
```

### P1: one focused runtime test audits `.codex` hook files outside v029 target paths

`platform_tests/scripts/test_dispatcher_runtime.py::test_codex_hook_commands_do_not_use_foreground_console_launchers` scans `.codex/config.toml` and `.codex/hooks.json`. In the release worktree it reported 42 foreground-console command offenders.

Those `.codex` files are not listed in v029 `target_paths`. Prime Builder cannot fix them under the current GO without widening scope. Loyal Opposition should decide whether this test belongs in the WI-4943 focused verification bundle or whether the next proposal must add the Codex hook configuration paths.

## Verification Evidence

Commands run from the release worktree:

```text
git diff --cached --name-status -- groundtruth-kb/src/groundtruth_kb/cli.py groundtruth-kb/src/groundtruth_kb/cli_skills.py groundtruth-kb/src/groundtruth_kb/backlog.py groundtruth-kb/src/groundtruth_kb/backlog/__init__.py groundtruth-kb/src/groundtruth_kb/backlog/approval_state.py groundtruth-kb/src/groundtruth_kb/backlog/query.py
```

Observed:

```text
M       groundtruth-kb/src/groundtruth_kb/cli.py
```

Import smoke passed after dispatcher-only CLI correction:

```text
$env:PYTHONPATH='E:/GT-KB/.gtkb-state/release-worktrees/wi4943-dispatcher-release-20260701/groundtruth-kb/src'
E:/GT-KB/groundtruth-kb/.venv/Scripts/python.exe -c "import groundtruth_kb.cli; print('cli-import-ok')"
cli-import-ok
```

Focused test bundle result after `psutil` was present in the verification venv:

```text
python -m pytest platform_tests/groundtruth_kb/cli/test_bridge_config_cli.py platform_tests/groundtruth_kb/cli/test_bridge_dispatch_daemon_supervisor.py platform_tests/scripts/test_gtkb_dispatcher_daemon.py platform_tests/scripts/test_dispatcher_runtime.py platform_tests/scripts/test_dispatcher_daemon_supervision.py platform_tests/scripts/test_cursor_harness.py -q --tb=short --no-header
68 failed, 164 passed, 1 warning in 62.20s
```

The failures cluster around the four blockers above rather than the narrowed `groundtruth_kb.cli` import.

## Specification Links

- `SPEC-DISPATCHER-CONTROL-SURFACE-001` - dispatcher CLI import and command glue are narrowed and importable, but release verification cannot complete until substrate and transitive helper scope are corrected.
- `SPEC-CENTRALIZED-DISPATCH-SERVICE-001` - daemon/runtime tests expose missing dispatcher monitoring and review-independence helpers.
- `ADR-DISPATCHER-ARCHITECTURE-001` - the release branch must use dispatcher-daemon substrate and must not restore the retired cross-harness trigger.
- `DCL-SINGLE-HARNESS-DISPATCHER-DESKTOP-TASK-001` - daemon/supervisor verification remains in scope; no-window hook findings need explicit target-path authority if retained.
- `GOV-FILE-BRIDGE-AUTHORITY-001` - this is the next numbered Prime Builder implementation blocker report after latest GO v030.
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` and `DCL-PROJECT-AUTHORIZATION-ENVELOPE-001` - Prime Builder is failing closed on additional paths outside v029 `target_paths`.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - focused verification remains blocked until the test plan and target paths are aligned.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`, `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`, and `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - this blocker is preserved as append-only bridge evidence.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - all additional candidate paths remain under `E:\GT-KB`.

## Owner Decisions / Input

No new owner decision is requested. The blockers are implementation-envelope and test-fixture alignment issues inside the already authorized WI-4943 dispatcher release lane.

PAUTH remains active until `2026-07-02T00:00:00Z`.

## Prior Deliberations

- `DELIB-20260701-ADHOC-RELEASE-DISPATCHER-SUBSTRATE-AUTH` - owner authorization for WI-4943 release-dispatcher lane.
- `bridge/gtkb-wi4943-release-branch-dispatcher-substrate-reconciliation-027.md` - prior Prime Builder blocker report for broad `cli.py` dependency accretion.
- `bridge/gtkb-wi4943-release-branch-dispatcher-substrate-reconciliation-028.md` - LO NO-GO directing dispatcher-only CLI strategy.
- `bridge/gtkb-wi4943-release-branch-dispatcher-substrate-reconciliation-029.md` - REVISED proposal for dispatcher-only CLI strategy.
- `bridge/gtkb-wi4943-release-branch-dispatcher-substrate-reconciliation-030.md` - LO GO on v029, with explicit fail-closed instruction for additional transitive imports outside target paths.

## Recommended Next Scope

Prime Builder recommends LO return `NO-GO` on this blocker report and authorize a corrected `REVISED` proposal that:

1. Adds `harness-state/bridge-substrate.json` to the release target paths so the release branch can carry `dispatcher_daemon` instead of retired `cross_harness_trigger`.
2. Adds `scripts/ops/dispatch_monitor.py` and `scripts/bridge_review_independence.py` to the target paths, or directs removal of the daemon monitoring/review-independence test expectations from this release bundle.
3. Authorizes updating focused dispatcher tests and fixtures from stale `prime-builder:B` assumptions to the current owner-directed topology.
4. Either adds `.codex/config.toml` and `.codex/hooks.json` to the target paths for the no-window hook command test, or removes that hook-surface test from the WI-4943 verification bundle because hook configuration is outside this release lane.

## Acceptance Criteria Status

- [x] Implementation authorization succeeded against v029/v030.
- [x] Dispatcher-only `cli.py` strategy replaced the broad research-era `cli.py` import surface.
- [x] `cli_skills.py` and backlog dependency-closure paths were removed from the staged release set.
- [x] `import groundtruth_kb.cli` passes from the release worktree.
- [x] Current topology was identified and projected into `config/dispatcher/rules.toml` / `harness-state/harness-registry.json`.
- [x] Out-of-envelope `harness-state/bridge-substrate.json` correction was reverted pending LO approval.
- [x] Focused tests were run and produced a concrete blocker set.
- [ ] LO returns `NO-GO` and approves the next corrected target envelope.
- [ ] Prime Builder files a scoped `REVISED` proposal and receives GO.
- [ ] Prime Builder reruns implementation authorization and completes verification under the corrected envelope.

## Risk And Rollback

Risk is that adding the missing helpers becomes another broad dependency accretion loop. Mitigation is a narrow v032 target-envelope correction limited to the two helper scripts, the bridge-substrate control file, and explicit test-fixture/hook-surface handling. Rollback remains release-worktree local: restore any newly authorized paths to `origin/main` and keep the bridge blocker evidence append-only.

## Loyal Opposition Asks

1. Return `NO-GO` on this blocker report because v029/v030 cannot produce a verified release branch as written.
2. Confirm whether the next Prime Builder action should be a `REVISED` proposal adding the recommended next scope above.
3. If `.codex` hook files should not be included, explicitly direct that the hook foreground-console test be removed from the WI-4943 focused verification bundle.
