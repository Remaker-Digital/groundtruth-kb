NEW
author_identity: prime-builder/codex-automation
author_harness_id: A
author_session_context_id: 2026-06-29T20-42-31Z-prime-builder-A-4d6c23
author_model: GPT-5
author_model_version: codex-desktop
author_model_configuration: Codex desktop automation session; approval_policy=never; autonomous Prime Builder bridge dispatch

# WI-4885 Dispatcher-Only Purge Target Scope Repair Implementation Report

bridge_kind: implementation_report
Document: gtkb-wi4885-dispatcher-only-purge-target-scope-repair
Version: 003 (NEW; post-implementation report)
Responds to GO: bridge/gtkb-wi4885-dispatcher-only-purge-target-scope-repair-002.md
Approved proposal: bridge/gtkb-wi4885-dispatcher-only-purge-target-scope-repair-001.md
Recommended commit type: fix:

## Implementation Claim

Prime Builder continued from the current WI-4885 worktree state under the corrected implementation-start packet for direct script and direct test targets. The dispatcher-only purge is implemented for the scoped load-bearing surfaces:

- `scripts/dispatcher_runtime.py` is the dispatcher-owned runtime helper replacing the retired cross-harness trigger module name.
- `scripts/gtkb_dispatcher_daemon.py` remains the automated dispatch entrypoint and daemon owner.
- Retired direct worker/trigger entrypoints are removed from the scoped operational surface:
  - `scripts/cross_harness_bridge_trigger.py`
  - `scripts/single_harness_bridge_automation.py`
  - `scripts/single_harness_bridge_dispatcher.py`
  - `.codex/gtkb-hooks/bridge-dispatch-trigger.cmd`
  - retired single-harness task install/uninstall scripts.
- Load-bearing startup/rule/config/source/test surfaces now describe dispatcher daemon automation as the only automated success path and manual owner assignment as the fallback.
- Focused dispatcher daemon, substrate, hook-registration, and no-active-smart-poller tests pass under a workspace-local pytest temp directory.
- A load-bearing static scan for the retired trigger-family terms returns no matches across the scoped operational surfaces.

No owner decision was needed in this auto-dispatched worker. This report does not claim unrelated dirty-worktree files or untracked draft tests outside the focused verification set.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001`
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001`
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`
- `SPEC-CENTRALIZED-DISPATCH-SERVICE-001`
- `SPEC-DISPATCHER-CONTROL-SURFACE-001`
- `ADR-DISPATCHER-ARCHITECTURE-001`
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001`
- `GOV-RELEASE-READINESS-GOVERNED-TESTING-001`
- `GOV-AUTOMATION-VALUE-VS-COST-001`
- `DCL-DISPATCH-ENVELOPE-RULES-001`
- `DCL-CROSS-HARNESS-PARITY-ENFORCEMENT-001`
- `ADR-CROSS-HARNESS-PARITY-001`
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`

## Owner Decisions / Input

- `DELIB-20266276` authorizes the daemon-resilience program implementation scope.
- 2026-06-29 owner directive, carried forward from the proposal: the retired cross-harness trigger must be purged from load-bearing regular GT-KB operation; it is not a fallback option. Manual owner assignment is the only fallback. The dispatcher daemon is the only automated success path.
- 2026-06-29 owner directive, carried forward from the proposal: release remains blocked until dispatcher health and harness dispatchability are release-ready.

No new owner input was required for this implementation report.

## Prior Deliberations

- `DELIB-20266276` - daemon-resilience program scope-lock and full-topology release-readiness authority.
- `DELIB-20260628-DISPATCHER-RELEASE-READINESS` - release-health directive for dispatcher readiness.
- `bridge/gtkb-wi4885-dispatcher-only-cross-harness-trigger-purge-001.md` and `bridge/gtkb-wi4885-dispatcher-only-cross-harness-trigger-purge-002.md` - original WI-4885 purge proposal and GO.
- `bridge/gtkb-wi4885-dispatcher-only-purge-target-scope-repair-001.md` - corrected target-scope proposal.
- `bridge/gtkb-wi4885-dispatcher-only-purge-target-scope-repair-002.md` - GO verdict authorizing implementation under the corrected target path list.

## Spec-Derived Verification Evidence

| Spec / governing surface | Executed verification evidence | Result |
| --- | --- | --- |
| `GOV-FILE-BRIDGE-AUTHORITY-001`, `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` | `python scripts/implementation_authorization.py begin --bridge-id gtkb-wi4885-dispatcher-only-purge-target-scope-repair`; `python scripts/implementation_authorization.py validate --target scripts/dispatcher_runtime.py`; `python scripts/bridge_claim_cli.py claim gtkb-wi4885-dispatcher-only-purge-target-scope-repair`. | Packet created from live latest `GO`; representative direct script target authorized; work-intent claim acquired. |
| `SPEC-CENTRALIZED-DISPATCH-SERVICE-001`, `SPEC-DISPATCHER-CONTROL-SURFACE-001`, `ADR-DISPATCHER-ARCHITECTURE-001` | `gt bridge dispatch health --json`; `gt bridge dispatch status --json`; focused daemon/substrate pytest suite. | Dispatcher health/status report `PASS`; daemon/substrate tests pass. |
| `GOV-RELEASE-READINESS-GOVERNED-TESTING-001`, `GOV-AUTOMATION-VALUE-VS-COST-001`, `DCL-DISPATCH-ENVELOPE-RULES-001` | Load-bearing `rg` scan for retired trigger-family terms over startup/rule/config/hook/source/script/test surfaces. | No matches in scoped operational surfaces. |
| `DCL-CROSS-HARNESS-PARITY-ENFORCEMENT-001`, `ADR-CROSS-HARNESS-PARITY-001` | Hook registration tests and static hook-surface scan include `.claude/settings.json`, `.codex/hooks.json`, and `.cursor/hooks.json`. | No load-bearing retired trigger references remain; `test_slice_3_hook_registrations.py` passes as part of the focused suite. |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | Touched-path review and focused platform tests stayed within `E:\GT-KB`; no Agent Red/adopter application source was modified as part of this report. | Root and platform/application boundaries preserved for this scope. |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`, `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | This report carries forward linked specs, maps each spec family to executed command evidence, and records observed results. | Verification-ready report filed for Loyal Opposition review. |
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`, `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`, `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | Bridge report records the implementation evidence, known residual risks, non-gating exploratory failures, and verification handoff state. | Artifact graph preserved without treating draft/untracked tests as verified truth. |

## Commands Run

```text
python scripts/bridge_claim_cli.py claim gtkb-wi4885-dispatcher-only-purge-target-scope-repair
python scripts/implementation_authorization.py begin --bridge-id gtkb-wi4885-dispatcher-only-purge-target-scope-repair
python scripts/implementation_authorization.py validate --target scripts/dispatcher_runtime.py
python -m py_compile scripts/dispatcher_runtime.py scripts/gtkb_dispatcher_daemon.py scripts/ops/dispatch_parity.py scripts/verify_antigravity_dispatch.py scripts/verify_cursor_dispatch.py scripts/session_self_initialization.py scripts/session_start_dispatch_core.py scripts/harness_parity_phase2.py scripts/check_codex_hook_parity.py scripts/auto_finalize_sweep.py scripts/implementation_start_gate.py groundtruth-kb/src/groundtruth_kb/bridge_dispatch_reset.py groundtruth-kb/src/groundtruth_kb/mode_switch/validation.py groundtruth-kb/src/groundtruth_kb/project/doctor.py groundtruth-kb/src/groundtruth_kb/bridge/status_driver.py groundtruth-kb/src/groundtruth_kb/operating_state.py
python -m pytest platform_tests/scripts/test_gtkb_dispatcher_daemon.py platform_tests/groundtruth_kb/test_doctor_dispatcher_substrate.py platform_tests/groundtruth_kb/test_mode_switch_bridge_substrate.py platform_tests/groundtruth_kb/test_mode_switch_bridge_substrate_validation.py platform_tests/groundtruth_kb/test_mode_switch_bridge_substrate_pending.py platform_tests/scripts/test_slice_3_hook_registrations.py platform_tests/scripts/test_session_start_dispatch_drains_bridge_substrate_pending.py platform_tests/test_no_active_smart_poller_wording.py -q --tb=short --basetemp=.tmp/pytest-gtkb-wi4885
python -m ruff check scripts/dispatcher_runtime.py scripts/gtkb_dispatcher_daemon.py scripts/ops/dispatch_parity.py scripts/verify_antigravity_dispatch.py scripts/verify_cursor_dispatch.py scripts/session_self_initialization.py scripts/session_start_dispatch_core.py scripts/harness_parity_phase2.py scripts/check_codex_hook_parity.py scripts/auto_finalize_sweep.py scripts/implementation_start_gate.py groundtruth-kb/src/groundtruth_kb/bridge_dispatch_reset.py groundtruth-kb/src/groundtruth_kb/mode_switch/validation.py groundtruth-kb/src/groundtruth_kb/project/doctor.py groundtruth-kb/src/groundtruth_kb/bridge/status_driver.py groundtruth-kb/src/groundtruth_kb/operating_state.py platform_tests/scripts/test_gtkb_dispatcher_daemon.py platform_tests/groundtruth_kb/test_doctor_dispatcher_substrate.py platform_tests/groundtruth_kb/test_mode_switch_bridge_substrate.py platform_tests/groundtruth_kb/test_mode_switch_bridge_substrate_validation.py platform_tests/groundtruth_kb/test_mode_switch_bridge_substrate_pending.py platform_tests/scripts/test_slice_3_hook_registrations.py platform_tests/scripts/test_session_start_dispatch_drains_bridge_substrate_pending.py platform_tests/test_no_active_smart_poller_wording.py
python -m ruff format scripts/auto_finalize_sweep.py scripts/harness_parity_phase2.py scripts/implementation_start_gate.py scripts/ops/dispatch_parity.py scripts/session_self_initialization.py scripts/session_start_dispatch_core.py scripts/verify_antigravity_dispatch.py scripts/verify_cursor_dispatch.py
python -m ruff format --check scripts/dispatcher_runtime.py scripts/gtkb_dispatcher_daemon.py scripts/ops/dispatch_parity.py scripts/verify_antigravity_dispatch.py scripts/verify_cursor_dispatch.py scripts/session_self_initialization.py scripts/session_start_dispatch_core.py scripts/harness_parity_phase2.py scripts/check_codex_hook_parity.py scripts/auto_finalize_sweep.py scripts/implementation_start_gate.py groundtruth-kb/src/groundtruth_kb/bridge_dispatch_reset.py groundtruth-kb/src/groundtruth_kb/mode_switch/validation.py groundtruth-kb/src/groundtruth_kb/project/doctor.py groundtruth-kb/src/groundtruth_kb/bridge/status_driver.py groundtruth-kb/src/groundtruth_kb/operating_state.py platform_tests/scripts/test_gtkb_dispatcher_daemon.py platform_tests/groundtruth_kb/test_doctor_dispatcher_substrate.py platform_tests/groundtruth_kb/test_mode_switch_bridge_substrate.py platform_tests/groundtruth_kb/test_mode_switch_bridge_substrate_validation.py platform_tests/groundtruth_kb/test_mode_switch_bridge_substrate_pending.py platform_tests/scripts/test_slice_3_hook_registrations.py platform_tests/scripts/test_session_start_dispatch_drains_bridge_substrate_pending.py platform_tests/test_no_active_smart_poller_wording.py
rg -n "cross_harness_bridge_trigger|single_harness_bridge_automation|cross_harness_trigger|cross-harness event-driven trigger|bridge-dispatch-trigger" AGENTS.md CLAUDE.md .claude/rules .claude/settings.json .codex/hooks.json .cursor/hooks.json config docs/gtkb-dashboard groundtruth-kb/docs groundtruth-kb/src scripts platform_tests -g "!.claude/worktrees/**" -g "!.gtkb-state/**"
gt bridge dispatch health --json
gt bridge dispatch status --json
python scripts/bridge_applicability_preflight.py --bridge-id gtkb-wi4885-dispatcher-only-purge-target-scope-repair --content-file .gtkb-state/bridge-impl-reports/drafts/gtkb-wi4885-dispatcher-only-purge-target-scope-repair-003.completed.md --json
python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-wi4885-dispatcher-only-purge-target-scope-repair --content-file .gtkb-state/bridge-impl-reports/drafts/gtkb-wi4885-dispatcher-only-purge-target-scope-repair-003.completed.md
```

Commands were run through `groundtruth-kb/.venv/Scripts/python.exe` and `groundtruth-kb/.venv/Scripts/gt.exe` where applicable.

## Observed Results

- Work-intent claim: acquired for `gtkb-wi4885-dispatcher-only-purge-target-scope-repair`, claim kind `go_implementation`, session `2026-06-29T20-42-31Z-prime-builder-A-4d6c23`.
- Implementation authorization: packet hash `sha256:2381b3ae01f3880ea174c39184e18a0ea92bda4014dca5c32540bca7d035d545`; latest status `GO`; `scripts/dispatcher_runtime.py` authorized.
- Py compile: exit `0`.
- Focused pytest: `71 passed, 1 warning in 23.86s`.
- Narrowed Ruff check: `All checks passed!`
- Initial narrowed Ruff format check found eight touched scripts needing formatting; after `ruff format`, the final narrowed format check reported `24 files already formatted`.
- Load-bearing retired-trigger scan: no matches.
- Dispatcher health: `PASS`; findings `[]`.
- Dispatcher status: `PASS`; no health findings.
- Broad `python -m ruff check scripts groundtruth-kb/src platform_tests` was run as exploratory context and reported `740` pre-existing lint findings across broad legacy surfaces, many outside this bridge slice. It was not used as this report's pass gate.
- Broader retired-trigger scan including all `docs` found two historical design-document references under `docs/design/...`; these paths are outside the corrected target path set and outside regular load-bearing operation.
- Candidate applicability preflight: `preflight_passed: true`; `missing_required_specs: []`; `missing_advisory_specs: []`; observed candidate packet hash before this evidence line was updated: `sha256:adb198f7deb4c2ec918e3907b4c458c6f9e1aaba50c992f7bc5912ab4f98166b`.
- Candidate clause preflight: exit `0`; clauses evaluated `5`; must_apply `4`; evidence gaps in must_apply clauses `0`; blocking gaps `0`.

## Non-Gating Exploratory Result

I also ran untracked dispatcher-runtime draft tests that are present in the worktree but not part of the approved verification command set:

```text
python -m pytest platform_tests/scripts/test_dispatch_load_harness.py platform_tests/scripts/test_dispatcher_only_no_retired_worker_refs.py platform_tests/scripts/test_dispatcher_runtime.py platform_tests/scripts/test_dispatcher_runtime_concurrent_writes.py platform_tests/scripts/test_dispatcher_runtime_diagnose.py platform_tests/scripts/test_dispatcher_runtime_drains_pending_before_recipient_resolution.py platform_tests/scripts/test_dispatcher_runtime_durable_keyed_regression.py platform_tests/scripts/test_dispatcher_runtime_import_repair.py platform_tests/scripts/test_dispatcher_runtime_rename_retry.py platform_tests/scripts/test_dispatcher_runtime_work_intent.py platform_tests/scripts/test_dispatcher_runtime_worker_delivery.py -q --tb=short --basetemp=.tmp/pytest-gtkb-wi4885-dispatcher-runtime
```

Observed: `97 passed`, `63 failed`, `1 skipped`. The failures are concentrated in untracked draft tests that still expect retired trigger names and APIs such as `run_trigger`, `_try_acquire_trigger_inflight_lock`, and `TRIGGER_INFLIGHT_LOCK_FILENAME`. They are not included in the implementation claim for this report. If these draft tests are intended to become authoritative, they need a separate cleanup or adoption thread before inclusion in release-gate evidence.

## Files Changed

Scoped implementation surfaces covered by this report include:

- Runtime and dispatch source:
  - `scripts/dispatcher_runtime.py`
  - `scripts/gtkb_dispatcher_daemon.py`
  - `scripts/ops/dispatch_parity.py`
  - `scripts/verify_antigravity_dispatch.py`
  - `scripts/verify_cursor_dispatch.py`
  - `scripts/session_self_initialization.py`
  - `scripts/session_start_dispatch_core.py`
  - `scripts/harness_parity_phase2.py`
  - `scripts/check_codex_hook_parity.py`
  - `scripts/auto_finalize_sweep.py`
  - `scripts/implementation_start_gate.py`
  - `groundtruth-kb/src/groundtruth_kb/bridge/status_driver.py`
  - `groundtruth-kb/src/groundtruth_kb/bridge_dispatch_reset.py`
  - `groundtruth-kb/src/groundtruth_kb/mode_switch/validation.py`
  - `groundtruth-kb/src/groundtruth_kb/project/doctor.py`
  - `groundtruth-kb/src/groundtruth_kb/operating_state.py`
- Configuration, startup, and hook surfaces:
  - `AGENTS.md`
  - `CLAUDE.md`
  - `.claude/settings.json`
  - `.codex/hooks.json`
  - `.cursor/hooks.json` (scanned for parity; not part of implementation-start target validation)
  - `config/dispatcher/rules.toml`
  - `harness-state/bridge-substrate.json`
  - `harness-state/harness-registry.json`
- Focused tests:
  - `platform_tests/scripts/test_gtkb_dispatcher_daemon.py`
  - `platform_tests/groundtruth_kb/test_doctor_dispatcher_substrate.py`
  - `platform_tests/groundtruth_kb/test_mode_switch_bridge_substrate.py`
  - `platform_tests/groundtruth_kb/test_mode_switch_bridge_substrate_validation.py`
  - `platform_tests/groundtruth_kb/test_mode_switch_bridge_substrate_pending.py`
  - `platform_tests/scripts/test_slice_3_hook_registrations.py`
  - `platform_tests/scripts/test_session_start_dispatch_drains_bridge_substrate_pending.py`
  - `platform_tests/test_no_active_smart_poller_wording.py`

Retired operational files removed by the current worktree state include:

- `.codex/gtkb-hooks/bridge-dispatch-trigger.cmd`
- `scripts/cross_harness_bridge_trigger.py` (renamed/replaced by `scripts/dispatcher_runtime.py`)
- `scripts/single_harness_bridge_automation.py`
- `scripts/single_harness_bridge_dispatcher.py`
- `scripts/install_single_harness_dispatcher_task.ps1`
- `scripts/uninstall_single_harness_dispatcher_task.ps1`
- old cross-harness/single-harness trigger platform tests.

The helper plan reported many additional dirty files in the shared worktree, including bridge artifacts, memory/session-state files, generated adapter surfaces, and untracked draft tests. Those are not claimed as verified implementation surfaces by this report.

## Recommended Commit Type

- Recommended commit type: `fix:`
- Diff-stat justification: this repairs a release-blocking dispatcher automation path by removing retired trigger entrypoints from regular operation and making dispatcher-daemon automation the sole automated success path.

```text
 .cursor/hooks.json                                 |    22 -
 AGENTS.md                                          |   667 +-
 CLAUDE.md                                          |     5 +-
 .../src/groundtruth_kb/bridge/status_driver.py     |   790 +-
 .../src/groundtruth_kb/bridge_dispatch_reset.py    |    22 +-
 .../src/groundtruth_kb/operating_state.py          |   899 +-
 .../test_mode_switch_bridge_substrate.py           |   107 +-
 .../test_mode_switch_bridge_substrate_pending.py   |    33 +-
 ...test_mode_switch_bridge_substrate_validation.py |   200 +-
 .../scripts/test_gtkb_dispatcher_daemon.py         |   175 +-
 .../scripts/test_slice_3_hook_registrations.py     |     8 +-
 scripts/auto_finalize_sweep.py                     |     2 +-
 scripts/check_codex_hook_parity.py                 |  2738 +++--
 scripts/dispatcher_runtime.py                      | 11496 ++++++++++---------
 scripts/harness_parity_phase2.py                   |     6 +-
 scripts/implementation_start_gate.py               |     3 +-
 scripts/ops/dispatch_parity.py                     |     6 +-
 scripts/session_self_initialization.py             |    18 +-
 scripts/session_start_dispatch_core.py             |    10 +-
 scripts/verify_antigravity_dispatch.py             |   247 +-
 scripts/verify_cursor_dispatch.py                  |    65 +-
 21 files changed, 8828 insertions(+), 8691 deletions(-)
```

## Acceptance Criteria Status

- [x] New implementation-start packet authorizes direct script and direct test targets.
- [x] Representative direct target `scripts/dispatcher_runtime.py` validates as authorized.
- [x] Dispatcher daemon is the only automated success path in scoped operational surfaces.
- [x] Retired trigger-family terms are absent from scoped load-bearing startup/rule/config/hook/source/script/test surfaces.
- [x] Focused dispatcher daemon/substrate/hook tests pass.
- [x] Dispatcher health and status report `PASS`.
- [ ] Untracked draft dispatcher-runtime tests are not adopted into this report and still need cleanup if they are meant to become authoritative.

## Risk And Rollback

Primary risk is scope confusion in the dirty shared worktree. The verified claim is intentionally limited to the scoped dispatcher-only purge surfaces and commands above. Historical bridge/evidence files and draft/untracked tests remain outside this report.

Rollback for the claimed implementation is path-local: revert the dispatcher-only purge source/config/test changes from the eventual implementation commit. Do not restore hook-triggered or single-harness trigger automation as a fallback; rollback may only return to manual owner assignment plus dispatcher-disabled containment until a corrected daemon path is available.

## Loyal Opposition Asks

1. Verify the dispatcher-only purge against the focused command evidence and scoped file list.
2. Treat the untracked dispatcher-runtime draft tests as out of scope for this report unless the reviewer decides they are load-bearing; if so, return `NO-GO` with a finding requiring a separate adoption/cleanup path.
3. Return `VERIFIED` only if the scoped dispatcher-only operational surfaces satisfy the approved proposal despite the broader dirty worktree context.
