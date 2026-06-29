NEW

# GT-KB Bridge Implementation Report - gtkb-wi4924-daemon-recipient-state-migration-dedup-repair - 003

bridge_kind: implementation_report
Document: gtkb-wi4924-daemon-recipient-state-migration-dedup-repair
Version: 003 (NEW; post-implementation report)
Responds to GO: bridge/gtkb-wi4924-daemon-recipient-state-migration-dedup-repair-002.md
Approved proposal: bridge/gtkb-wi4924-daemon-recipient-state-migration-dedup-repair-001.md
Recommended commit type: fix:

author_identity: prime-builder/codex/A
author_harness_id: A
author_session_context_id: 019f09c9-2db0-7b00-a337-40f998b07e56
author_model: GPT-5 Codex
author_model_version: 2026-06
author_model_configuration: Codex Desktop, approval_policy=never, cwd=E:\GT-KB

## Implementation Claim

Implemented the daemon duplicate-spawn repair for WI-4924. The dispatcher
state-key migration now preserves explicit recipient-suffixed dispatch state
over unsuffixed role placeholders, so a newer `prime-builder`
`substrate_mismatch_inert` mirror cannot overwrite `prime-builder:A` and erase
`last_dispatched_signature`.

The repair also preserves meaningful retry evidence from compatibility
role-label mirrors, so fatal prior-launch markers still make a same-signature
batch retryable. This avoids fixing the daemon burst by regressing the existing
fatal-worker retry contract.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001`
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001`
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`
- `GOV-STANDING-BACKLOG-001`
- `ADR-DISPATCHER-ARCHITECTURE-001`
- `SPEC-CENTRALIZED-DISPATCH-SERVICE-001`
- `SPEC-DISPATCHER-CONTROL-SURFACE-001`
- `DCL-DISPATCH-ENVELOPE-RULES-001`
- `DCL-SINGLE-HARNESS-DISPATCHER-DESKTOP-TASK-001`
- `SPEC-DISPATCH-KILL-SWITCH-EMERGENCY-ONLY-001`

## Owner Decisions / Input

No new owner decision was required. The work stays inside
`PAUTH-PROJECT-GTKB-DISPATCHER-RELIABILITY-WI-4924-DAEMON-DEDUP-MIGRATION`.

## Prior Deliberations

- `bridge/gtkb-wi4924-daemon-recipient-state-migration-dedup-repair-001.md` - approved implementation proposal.
- `bridge/gtkb-wi4924-daemon-recipient-state-migration-dedup-repair-002.md` - Loyal Opposition GO verdict authorizing implementation.
- `bridge/gtkb-wi4905-codex-hook-no-window-parity-004.md` - VERIFIED no-window hook repair that made live daemon smoke safe to execute.

## Specification-Derived Verification Plan

| Spec / governing surface | Executed verification evidence |
| --- | --- |
| `GOV-FILE-BRIDGE-AUTHORITY-001`; `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` | `python scripts/implementation_authorization.py validate --target scripts/cross_harness_bridge_trigger.py --target platform_tests/scripts/test_gtkb_dispatcher_daemon.py --target platform_tests/scripts/test_cross_harness_bridge_trigger.py` -> authorized true. |
| `SPEC-CENTRALIZED-DISPATCH-SERVICE-001`; `DCL-DISPATCH-ENVELOPE-RULES-001` | Focused regression bundle with migration, retry, and daemon live-dedupe tests -> 5 passed. |
| `ADR-DISPATCHER-ARCHITECTURE-001`; `SPEC-DISPATCHER-CONTROL-SURFACE-001` | Two-file dispatcher/trigger focused suite -> 153 passed after WI-4905 no-window repair. |
| `DCL-SINGLE-HARNESS-DISPATCHER-DESKTOP-TASK-001` | WI-4905 no-window guard verified first; daemon smoke process list showed `pythonw.exe` daemon/worker wrappers and no console-subsystem command burst. |
| `SPEC-DISPATCH-KILL-SWITCH-EMERGENCY-ONLY-001` | Process cleanup remained bounded to dispatcher daemon tree during `gt bridge dispatch daemon stop`; no leftover worker PIDs matched dispatcher/worker patterns afterward. |
| Lint/format quality | `ruff check` and `ruff format --check` passed for the three authorized source/test files. |

## Commands Run

- `groundtruth-kb\.venv\Scripts\python.exe scripts\implementation_authorization.py validate --target scripts/cross_harness_bridge_trigger.py --target platform_tests/scripts/test_gtkb_dispatcher_daemon.py --target platform_tests/scripts/test_cross_harness_bridge_trigger.py`
- `groundtruth-kb\.venv\Scripts\python.exe -m pytest platform_tests\scripts\test_cross_harness_bridge_trigger.py::test_previous_fatal_worker_output_retries_same_signature platform_tests\scripts\test_cross_harness_bridge_trigger.py::test_unchanged_signature_with_previous_fatal_worker_log_retries platform_tests\scripts\test_cross_harness_bridge_trigger.py::test_migration_preserves_explicit_recipient_over_newer_unsuffixed_placeholder platform_tests\scripts\test_cross_harness_bridge_trigger.py::test_migration_still_promotes_unsuffixed_role_when_no_explicit_recipient platform_tests\scripts\test_gtkb_dispatcher_daemon.py::test_daemon_live_dedupe_survives_newer_unsuffixed_substrate_mismatch_state -q --tb=short`
- `groundtruth-kb\.venv\Scripts\python.exe -m ruff check scripts\cross_harness_bridge_trigger.py platform_tests\scripts\test_gtkb_dispatcher_daemon.py platform_tests\scripts\test_cross_harness_bridge_trigger.py`
- `groundtruth-kb\.venv\Scripts\python.exe -m ruff format --check scripts\cross_harness_bridge_trigger.py platform_tests\scripts\test_gtkb_dispatcher_daemon.py platform_tests\scripts\test_cross_harness_bridge_trigger.py`
- `groundtruth-kb\.venv\Scripts\python.exe -m pytest platform_tests\scripts\test_gtkb_dispatcher_daemon.py platform_tests\scripts\test_cross_harness_bridge_trigger.py -q --tb=short`
- `groundtruth-kb\.venv\Scripts\python.exe -m groundtruth_kb.cli bridge dispatch reset --soft --json`
- `groundtruth-kb\.venv\Scripts\python.exe -m groundtruth_kb.cli bridge dispatch daemon start`
- `groundtruth-kb\.venv\Scripts\python.exe -m groundtruth_kb.cli bridge dispatch daemon status --json`
- `Get-CimInstance Win32_Process | Where-Object { $_.CommandLine -match 'run_with_status.py|codex exec|openrouter_harness|ollama_harness|gtkb_dispatcher_daemon|cross_harness_bridge_trigger' }`
- `groundtruth-kb\.venv\Scripts\python.exe -m groundtruth_kb.cli bridge dispatch daemon stop`

## Observed Results

- Authorization validation returned `authorized: true`.
- Focused regression bundle returned `5 passed`.
- Ruff check returned `All checks passed`; format-check returned `3 files already formatted`.
- The broader dispatcher/trigger suite returned `153 passed`.
- Soft reset cleared 10 recipients and pruned 3 stale dispatch-run records.
- Daemon smoke launched a single Prime Builder worker sidecar:
  `2026-06-29T08-51-09Z-prime-builder-A-3601c7`.
- The next daemon tick recorded `prime-builder:A` with
  `last_result: unchanged`, `pending_count: 2`, and unchanged
  `last_dispatched_signature: b19716a2966d998f12801c0012a9843fc75a3adb81def03643f9048a092a0fa8`.
- No repeated same-signature worker burst appeared across the observation
  window.
- `gt bridge dispatch daemon stop` terminated the daemon tree; a post-stop
  process scan showed no remaining dispatcher worker, `codex exec`,
  OpenRouter, Ollama, or cross-harness trigger processes.

## Files Changed

- `scripts/cross_harness_bridge_trigger.py`
- `platform_tests/scripts/test_cross_harness_bridge_trigger.py`
- `platform_tests/scripts/test_gtkb_dispatcher_daemon.py`

## Acceptance Criteria Status

- [x] Explicit suffixed recipient state cannot be overwritten by a newer unsuffixed substrate-mismatch placeholder during migration.
- [x] Legacy unsuffixed state still migrates when no explicit suffixed recipient state exists.
- [x] Retry evidence from compatibility role mirrors remains effective for fatal prior worker logs.
- [x] The daemon live-spawn path returns `unchanged` and performs no repeated spawn for a same-signature batch under the reproduced mixed-state condition.
- [x] Focused pytest, Ruff check, and Ruff format check pass for the authorized target paths.
- [x] Runtime smoke after soft reset and daemon restart shows no repeated same-signature Prime Builder worker bursts across successive ticks.
- [x] No unrelated source, provider, credential, bridge-history, or release-merge files were intentionally changed by this WI-4924 implementation.

## Risk And Rollback

Residual risk: the live smoke intentionally stopped the worker after observing
daemon dedupe behavior, so it proves no repeated burst rather than full worker
completion. Full worker completion belongs to the broader release-readiness and
harness-parity smoke. Rollback is a single commit reverting the three files
listed above; bridge audit files remain append-only.

## Loyal Opposition Asks

1. Verify the migration preserves explicit recipient signatures while ignoring unsuffixed substrate-mismatch placeholders.
2. Verify the retry-evidence regression coverage remains valid.
3. Verify the daemon smoke evidence demonstrates the original repeated-spawn storm is fixed.
4. Return VERIFIED if the report and implementation satisfy WI-4924; otherwise return NO-GO with specific findings.
