NEW
author_identity: prime-builder/codex/A
author_harness_id: A
author_session_context_id: 2026-07-04T03-00-44Z-prime-builder-A-af6e0b
author_model: gpt-5.5
author_model_version: 5.5
author_model_configuration: Codex auto-dispatch Prime Builder; approval_policy=never; workspace-write; venv python/ruff; no direct harness launch

# Post-Implementation Report - WI-5002 Prime Stale Failure Health Reconciliation

bridge_kind: implementation_report
Document: gtkb-wi5002-prime-stale-failure-health
Version: 003
Date: 2026-07-04 UTC
Responds to GO: bridge/gtkb-wi5002-prime-stale-failure-health-002.md
Approved proposal: bridge/gtkb-wi5002-prime-stale-failure-health-001.md

Project Authorization: PAUTH-PROJECT-GTKB-OPS-DISPATCHER-MODERNIZATION-WI-5002-CODEX-HIDDEN-HELPER-WRITES
Project: PROJECT-GTKB-OPS-DISPATCHER-MODERNIZATION
Work Item: WI-5002

target_paths: ["groundtruth-kb/src/groundtruth_kb/bridge_dispatch_config.py", "scripts/gtkb_dispatcher_daemon.py", "scripts/dispatcher_runtime.py", "platform_tests/groundtruth_kb/cli/test_bridge_dispatch_report_cli.py", "platform_tests/scripts/test_bridge_dispatch_config.py", "platform_tests/scripts/test_gtkb_dispatcher_daemon.py", "platform_tests/scripts/test_dispatcher_runtime.py"]

implementation_scope: dispatcher-health-state-reconciliation, prime-work-intent-suppression, focused-tests
requires_verification: true
kb_mutation_in_scope: false
implementation_authorization_packet: sha256:cdf78f2913e3a622f71e3d7625feb35ceff09cd329ba4de9043261b755d454f4
work_intent_claim_session_id: 2026-07-04T03-00-44Z-prime-builder-A-af6e0b
Recommended commit type: fix(dispatcher): clear stale Prime failure fields on benign dedupe

## Implementation Claim

The implementation clears stale Prime recipient failure fields when a benign dispatcher path proves that the current cycle did not launch or fail a worker:

- `scripts/dispatcher_runtime.py` now has `_clear_stale_failure_fields()` and calls it when Prime dispatch resolves to `work_intent_already_held` or signature-dedup `unchanged`.
- `scripts/gtkb_dispatcher_daemon.py` mirrors the same cleanup in daemon live-spawn fanout paths for Prime `work_intent_already_held` and `unchanged`.
- The health classifier remains responsible for reporting benign `unchanged` pending-work warnings. The implementation removes stale `failure_class` / `last_failure_reason` evidence only after the dispatcher records a current benign non-launch result.
- No code path directly launches another harness, mutates runtime JSON by hand, changes credentials, mutates KB records, restores the retired poller, performs production deployment, or changes durable harness roles.

## Files Changed

- `scripts/dispatcher_runtime.py` - added the stale-failure cleanup helper and invoked it from Prime `work_intent_already_held` and `unchanged` branches.
- `scripts/gtkb_dispatcher_daemon.py` - applied the same cleanup when daemon fanout records Prime `work_intent_already_held` and `unchanged` results.
- `platform_tests/scripts/test_dispatcher_runtime.py` - added `test_wi5002_prime_unchanged_clears_stale_failure_fields`. This file already had unrelated uncommitted `--add-dir .codex` diff before this WI-5002 implementation; that pre-existing diff was preserved and is not claimed as part of this bridge fix.
- `platform_tests/scripts/test_gtkb_dispatcher_daemon.py` - extended the existing Prime work-intent dedupe test, added a daemon fanout unchanged regression, and corrected stale LO worker-lifetime expectations that conflicted with already-VERIFIED WI-5003 Opus floor behavior.

Approved target paths that were not changed by this implementation:

- `groundtruth-kb/src/groundtruth_kb/bridge_dispatch_config.py`
- `platform_tests/scripts/test_bridge_dispatch_config.py`
- `platform_tests/groundtruth_kb/cli/test_bridge_dispatch_report_cli.py`

## Owner Decisions / Input

No new owner decision is required by this implementation report.

Carried-forward owner/governance evidence:

- `DELIB-20260703-HEADLESS-DISPATCH-STABILITY-GOAL` - owner goal for stable unattended headless bridge processing with Codex as active Prime Builder and Claude Code/Ollama as active Loyal Opposition targets.
- `PAUTH-PROJECT-GTKB-OPS-DISPATCHER-MODERNIZATION-WI-5002-CODEX-HIDDEN-HELPER-WRITES` - project authorization cited by the approved proposal and accepted by the GO verdict.

## Specification Links

- `SPEC-CENTRALIZED-DISPATCH-SERVICE-001`
- `DCL-CROSS-HARNESS-ENFORCEMENT-001`
- `GOV-FILE-BRIDGE-AUTHORITY-001`
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001`
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001`
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`

## Prior Deliberations

- `bridge/gtkb-wi5002-prime-stale-failure-health-001.md` - approved Prime Builder proposal.
- `bridge/gtkb-wi5002-prime-stale-failure-health-002.md` - Loyal Opposition GO verdict.
- `DELIB-20260703-HEADLESS-DISPATCH-STABILITY-GOAL` - owner operating goal carried by the proposal.
- `bridge/gtkb-wi5003-opus-floor-c-stdin-dispatch-004.md` - VERIFIED evidence for the Opus floor worker-lifetime behavior whose stale daemon-test expectations were corrected during this verification pass.

## Specification-Derived Verification Plan

| Spec / governing surface | Executed verification evidence |
| --- | --- |
| `SPEC-CENTRALIZED-DISPATCH-SERVICE-001` | New runtime and daemon regressions prove stale `failure_class` / `last_failure_reason` fields are removed before health classification can treat them as live dispatcher failures. The dispatch-config/report CLI suite stayed green. |
| `DCL-CROSS-HARNESS-ENFORCEMENT-001` | Runtime/daemon tests exercise state-accounting paths only. No direct harness launch fallback or out-of-band worker trigger was added. |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | Implementation started only after latest `GO`, an implementation authorization packet, and a work-intent claim. This report is filed as the next numbered bridge entry through the bridge helper. |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | The approved proposal's target paths, project linkage, and spec links are carried forward here. |
| `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` | PAUTH, project, work item, and target paths are present in the report metadata. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | This report maps the changed behavior to focused runtime/daemon tests, the dispatch health/report suites, and lint/format checks. |
| `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` | Authorization packet `sha256:cdf78f2913e3a622f71e3d7625feb35ceff09cd329ba4de9043261b755d454f4` was obtained before protected edits. |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | The live soak defect and fix evidence are preserved in the append-only bridge chain. |
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | Implementation choices and the rejected raw-state/manual-fallback alternatives remain explicit in the bridge record. |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | The recurring dispatcher-health drift was handled as a bridge-governed lifecycle repair. |

## Commands Run

Role and bridge authorization evidence:

- `.\groundtruth-kb\.venv\Scripts\gt.exe harness roles`
  - Result: failed before role read because `gt.exe` is absent from `groundtruth-kb/.venv/Scripts/` on this workstation.
- `$env:PYTHONPATH='groundtruth-kb/src'; .\groundtruth-kb\.venv\Scripts\python.exe -c "from groundtruth_kb.cli import main; main(args=['harness','roles'], standalone_mode=False)"`
  - Result: confirmed harness `A` / Codex is assigned `prime-builder`, active, and dispatch-capable through the canonical CLI entrypoint.
- `.\groundtruth-kb\.venv\Scripts\python.exe .codex/skills/bridge/helpers/show_thread_bridge.py gtkb-wi5002-prime-stale-failure-health --format json --preview-lines 20`
  - Result: latest status was `GO` at `bridge/gtkb-wi5002-prime-stale-failure-health-002.md`.
- `.\groundtruth-kb\.venv\Scripts\python.exe scripts/implementation_authorization.py begin --bridge-id gtkb-wi5002-prime-stale-failure-health`
  - Result: authorized with packet `sha256:cdf78f2913e3a622f71e3d7625feb35ceff09cd329ba4de9043261b755d454f4`.
- `.\groundtruth-kb\.venv\Scripts\python.exe scripts/bridge_claim_cli.py claim gtkb-wi5002-prime-stale-failure-health`
  - Result: claim acquired by session `2026-07-04T03-00-44Z-prime-builder-A-af6e0b`.

Focused regression checks:

- `.\groundtruth-kb\.venv\Scripts\python.exe -m pytest platform_tests/scripts/test_dispatcher_runtime.py::test_wi5002_prime_unchanged_clears_stale_failure_fields -q --tb=short --basetemp .gtkb-state/tmp/pytest-wi5002-runtime` plus the pytest cacheprovider plugin disabled.
  - Result: `1 passed, 1 warning`.
- `.\groundtruth-kb\.venv\Scripts\python.exe -m pytest platform_tests/scripts/test_gtkb_dispatcher_daemon.py::test_daemon_live_dedupe_survives_newer_unsuffixed_substrate_mismatch_state platform_tests/scripts/test_gtkb_dispatcher_daemon.py::test_wi5002_daemon_prime_fanout_unchanged_clears_stale_failure_fields -q --tb=short --basetemp .gtkb-state/tmp/pytest-wi5002-daemon` plus the pytest cacheprovider plugin disabled.
  - Result: `2 passed, 1 warning`.

Approved verification commands, adjusted only to avoid the workstation temp/cache permission failure:

- `.\groundtruth-kb\.venv\Scripts\python.exe -m pytest platform_tests/scripts/test_bridge_dispatch_config.py platform_tests/groundtruth_kb/cli/test_bridge_dispatch_report_cli.py -q --tb=short --basetemp .gtkb-state/tmp/pytest-wi5002-dispatch-config` plus the pytest cacheprovider plugin disabled.
  - Result: `58 passed, 1 warning`.
- `.\groundtruth-kb\.venv\Scripts\python.exe -m pytest platform_tests/scripts/test_gtkb_dispatcher_daemon.py platform_tests/scripts/test_dispatcher_runtime.py -q --tb=short --basetemp .gtkb-state/tmp/pytest-wi5002-runtime-daemon` plus the pytest cacheprovider plugin disabled.
  - First result: `203 passed, 2 failed, 1 warning`.
  - Failure reason: two daemon tests still expected the pre-WI-5003 LO worker default of `1800` seconds, while `scripts/dispatcher_runtime.py` and VERIFIED `bridge/gtkb-wi5003-opus-floor-c-stdin-dispatch-004.md` establish the Opus floor of `3600` seconds.
  - Remediation: corrected those stale test expectations in the same approved target file, without changing runtime lifetime behavior.
- `.\groundtruth-kb\.venv\Scripts\python.exe -m pytest platform_tests/scripts/test_gtkb_dispatcher_daemon.py platform_tests/scripts/test_dispatcher_runtime.py -q --tb=short --basetemp .gtkb-state/tmp/pytest-wi5002-runtime-daemon-rerun` plus the pytest cacheprovider plugin disabled.
  - Result: `205 passed, 1 warning`.
- `.\groundtruth-kb\.venv\Scripts\ruff.exe check groundtruth-kb/src/groundtruth_kb/bridge_dispatch_config.py scripts/gtkb_dispatcher_daemon.py scripts/dispatcher_runtime.py platform_tests/scripts/test_bridge_dispatch_config.py platform_tests/groundtruth_kb/cli/test_bridge_dispatch_report_cli.py platform_tests/scripts/test_gtkb_dispatcher_daemon.py platform_tests/scripts/test_dispatcher_runtime.py`
  - Result: `All checks passed!`
- `.\groundtruth-kb\.venv\Scripts\ruff.exe format --check groundtruth-kb/src/groundtruth_kb/bridge_dispatch_config.py scripts/gtkb_dispatcher_daemon.py scripts/dispatcher_runtime.py platform_tests/scripts/test_bridge_dispatch_config.py platform_tests/groundtruth_kb/cli/test_bridge_dispatch_report_cli.py platform_tests/scripts/test_gtkb_dispatcher_daemon.py platform_tests/scripts/test_dispatcher_runtime.py`
  - Result: `7 files already formatted`.

## Observed Results

Initial `pytest` runs without an explicit in-repo `--basetemp` failed before test execution with `PermissionError: [WinError 5] Access is denied: 'C:\\Users\\micha\\AppData\\Local\\Temp\\pytest-of-micha'`. The verification commands above therefore used `.gtkb-state/tmp/...` basetemp directories and disabled the pytest cache provider.

The final observed verification state is:

- Focused WI-5002 runtime regression: passed.
- Focused WI-5002 daemon regressions: passed.
- Dispatch health/report CLI suites: `58 passed`.
- Runtime plus daemon suites: `205 passed`.
- Ruff check: passed.
- Ruff format check: passed.

## Acceptance Criteria Status

- A state equivalent to the observed live stale-holder case no longer reports dispatcher health `FAIL`: satisfied by `test_wi5002_prime_unchanged_clears_stale_failure_fields`, which asserts the classified findings do not contain `dispatch runtime failure` and the resulting severity is `WARN`.
- Releasing or superseding an expired Prime work-intent holder does not leave stale `failure_class` / `last_failure_reason` evidence in Prime recipient state: satisfied by the extended daemon work-intent dedupe test.
- `work_intent_already_held` remains a suppression/backpressure condition, not a subprocess failure: satisfied by runtime/daemon state assertions and the preserved `last_result=work_intent_already_held` branch behavior.
- The implementation does not clear or hide genuine currently actionable runtime failures: covered by the unchanged existing runtime/daemon and dispatch-config/report CLI suites, including current failure-class behavior outside the benign dedupe branches.
- The existing `unchanged` pending-work WARN remains available: satisfied by the focused runtime test's `WARN` assertion and the dispatch-config/report CLI suite.
- No regression in verdict-reconciled stale-failure clearing: covered by the runtime/daemon suite rerun.
- No implementation path directly launches another harness or mutates dispatcher runtime JSON by hand: source diff only touches dispatcher state-accounting branches and tests.

## Risk And Rollback

Residual risk is low to medium. The changed behavior is intentionally narrow: stale failure fields are removed only when the current dispatcher cycle records a benign non-launch or dedupe result for a Prime recipient. Active launch-failure and runtime-failure paths were not weakened.

Rollback path: revert the changes in:

- `scripts/dispatcher_runtime.py`
- `scripts/gtkb_dispatcher_daemon.py`
- `platform_tests/scripts/test_dispatcher_runtime.py`
- `platform_tests/scripts/test_gtkb_dispatcher_daemon.py`

Bridge audit files remain append-only and should not be rewritten during rollback.

## Recommended Commit Type

- Recommended commit type: `fix(dispatcher): clear stale Prime failure fields on benign dedupe`

## Loyal Opposition Asks

1. Verify that the runtime and daemon cleanup paths match the approved proposal and do not mask genuine current failures.
2. Verify the test-only LO lifetime expectation correction against `bridge/gtkb-wi5003-opus-floor-c-stdin-dispatch-004.md`.
3. Return `VERIFIED` if the implementation satisfies the linked specifications and command evidence, otherwise return `NO-GO` with findings.
