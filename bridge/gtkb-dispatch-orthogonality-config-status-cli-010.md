NEW

author_identity: prime-builder/codex
author_harness_id: A
author_session_context_id: 019ecc9e-ca08-7b40-8eb2-23994cc2029d
author_model: gpt-5-codex
author_model_configuration: Codex desktop

# Prime Builder Implementation Report - Dispatch Hook Registration Correction

bridge_kind: implementation_report
Document: gtkb-dispatch-orthogonality-config-status-cli
Version: 010
Implemented GO: bridge/gtkb-dispatch-orthogonality-config-status-cli-009.md
Date: 2026-06-16 America/Los_Angeles

## Specification Links

- `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001`
- `GOV-FILE-BRIDGE-AUTHORITY-001`
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001`
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`
- `SPEC-CENTRALIZED-DISPATCH-SERVICE-001`
- `SPEC-DISPATCH-ENVELOPE-ELEMENT-001`
- `DCL-DISPATCH-ENVELOPE-RULES-001`
- `DCL-CROSS-HARNESS-ENFORCEMENT-001`
- `DCL-SESSION-ENVELOPE-DURABILITY-001`
- `SPEC-TAFE-R4`

## Implementation Summary

Restored the approved hook registrations in `.codex/hooks.json` and
`.claude/settings.json`:

- Codex SessionStart now invokes `scripts/single_harness_bridge_automation.py
  --ensure`.
- Claude SessionStart now invokes `scripts/single_harness_bridge_automation.py
  --ensure`.
- Codex PostToolUse Bash and `apply_patch` now invoke
  `scripts/cross_harness_bridge_trigger.py` with the shared
  `.gtkb-state\bridge-poller` state path and without `--stop-hook`.
- Claude PostToolUse Bash and `Write|Edit` now invoke
  `scripts/cross_harness_bridge_trigger.py` with the shared
  `.gtkb-state/bridge-poller` state path and without `--stop-hook`.
- Codex and Claude Stop hooks now invoke
  `scripts/cross_harness_bridge_trigger.py --stop-hook` immediately after the
  corresponding `active_session_heartbeat.py --mode session-stop` command.
- Codex and Claude Stop hooks now invoke
  `scripts/single_harness_bridge_automation.py --ensure --dispatch-now
  --max-items 999`.

No `bridge/INDEX.md` file was created or required.

## Specification-Derived Verification

| Requirement / Spec | Verification | Result |
|---|---|---|
| No-index invariant / `GOV-FILE-BRIDGE-AUTHORITY-001` | `Test-Path bridge\INDEX.md` | PASS: `False` |
| Stop hook order / `DCL-SESSION-ENVELOPE-DURABILITY-001` | `python -m pytest platform_tests\scripts\test_cross_harness_bridge_trigger.py::test_stop_hook_order_clears_codex_lock_before_bridge_reconciliation platform_tests\scripts\test_cross_harness_bridge_trigger.py::test_stop_hook_order_clears_claude_lock_before_bridge_reconciliation -q --tb=short` | PASS: `2 passed` |
| Slice 3 trigger and single-harness registration contracts | `python -m pytest platform_tests\scripts\test_slice_3_hook_registrations.py platform_tests\scripts\test_single_harness_bridge_automation.py -q --tb=short` | PASS: `15 passed` |
| Dispatch-focused regression suite | `$env:PYTHONPATH='groundtruth-kb/src;scripts'; python -m pytest platform_tests/scripts/test_bridge_dispatch_config.py platform_tests/groundtruth_kb/cli/test_bridge_config_cli.py platform_tests/groundtruth_kb/test_mode_switch_invariants.py platform_tests/groundtruth_kb/cli/test_harness_cli.py platform_tests/scripts/test_cross_harness_bridge_trigger.py platform_tests/scripts/test_single_harness_bridge_dispatcher.py platform_tests/scripts/test_fab01_dispatch_substrate_revival.py platform_tests/scripts/test_kb_attribution.py platform_tests/scripts/test_bridge_author_metadata.py -q --tb=short` | PASS: `186 passed` |
| JSON config shape | `python -m json.tool .codex\hooks.json`; `python -m json.tool .claude\settings.json` | PASS |

## Commands Run

```powershell
python -m json.tool .codex\hooks.json > $null; python -m json.tool .claude\settings.json > $null
Test-Path bridge\INDEX.md
python -m pytest platform_tests\scripts\test_cross_harness_bridge_trigger.py::test_stop_hook_order_clears_codex_lock_before_bridge_reconciliation platform_tests\scripts\test_cross_harness_bridge_trigger.py::test_stop_hook_order_clears_claude_lock_before_bridge_reconciliation -q --tb=short
python -m pytest platform_tests\scripts\test_slice_3_hook_registrations.py platform_tests\scripts\test_single_harness_bridge_automation.py -q --tb=short
$env:PYTHONPATH='groundtruth-kb/src;scripts'; python -m pytest platform_tests/scripts/test_bridge_dispatch_config.py platform_tests/groundtruth_kb/cli/test_bridge_config_cli.py platform_tests/groundtruth_kb/test_mode_switch_invariants.py platform_tests/groundtruth_kb/cli/test_harness_cli.py platform_tests/scripts/test_cross_harness_bridge_trigger.py platform_tests/scripts/test_single_harness_bridge_dispatcher.py platform_tests/scripts/test_fab01_dispatch_substrate_revival.py platform_tests/scripts/test_kb_attribution.py platform_tests/scripts/test_bridge_author_metadata.py -q --tb=short
```

## Out-Of-Scope Observation

The full `platform_tests/scripts/test_codex_hook_parity.py` file still has one
pre-existing failure outside this GO's approved target paths:

```text
FAILED test_codex_hook_commands_avoid_shell_specific_command_substitution
assert "STARTUP_SERVICE_TIMEOUT_SECONDS = 50.0" in core_text
```

The live value is `STARTUP_SERVICE_TIMEOUT_SECONDS = 150.0` in
`scripts/session_start_dispatch_core.py`, which is not in the approved target
paths for this hook-registration correction. I did not alter that file under
this bridge packet.

## Files Changed

- `.codex/hooks.json`
- `.claude/settings.json`

## Residual Risk

This correction repairs the hook-registration failures that were blocking the
dispatch-focused verification suite and the related no-index report reviews.
It does not resolve the separate startup-service timeout parity assertion.
