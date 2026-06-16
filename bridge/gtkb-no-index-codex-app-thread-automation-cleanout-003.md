NEW

author_identity: prime-builder/codex
author_harness_id: A
author_session_context_id: 019ecc9e-ca08-7b40-8eb2-23994cc2029d
author_model: gpt-5-codex
author_model_configuration: Codex desktop

# Prime Builder Implementation Report - No-Index Codex App-Thread Automation Cleanout

bridge_kind: implementation_report
Document: gtkb-no-index-codex-app-thread-automation-cleanout
Version: 003
Implemented GO: bridge/gtkb-no-index-codex-app-thread-automation-cleanout-002.md
Date: 2026-06-15 America/Los_Angeles

## Specification Links

- PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001
- GOV-FILE-BRIDGE-AUTHORITY-001
- ADR-ISOLATION-APPLICATION-PLACEMENT-001
- E:\GT-KB
- DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001
- DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001
- DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001
- SPEC-CENTRALIZED-DISPATCH-SERVICE-001
- SPEC-DISPATCH-ENVELOPE-ELEMENT-001
- DCL-CROSS-HARNESS-ENFORCEMENT-001

## Implementation Summary

Updated in-repo authority surfaces so Codex app-thread automation memory is not
presented as GT-KB bridge authority. `config/agent-control/system-interface-map.toml`
now marks Codex app-thread automation entries as historical/deprecated and
states that they must not read or recreate `bridge/INDEX.md` or route live
GT-KB bridge work.

Updated `.claude/rules/bridge-essential.md` to remove the stale instruction
that agents must not remove/rename the deprecated compatibility view. The rule
now states that `bridge/INDEX.md` is deprecated/removed, must not be recreated
as live bridge state, and that TAFE/dispatcher state plus versioned bridge
files are authoritative.

The startup generator and cross-harness trigger changes from the adjacent
authorized packets also support this cleanup by ensuring in-repo startup and
dispatch prompts point at TAFE/dispatcher state rather than external app-thread
automation memory or the retired index.

## Verification

- `Test-Path bridge\INDEX.md` -> `False`
- `rg -n "bridge/INDEX\.md|INDEX\.md|bridge index" AGENTS.md config/agent-control scripts\session_self_initialization.py scripts\session_start_dispatch_core.py scripts\cross_harness_bridge_trigger.py scripts\single_harness_bridge_dispatcher.py .claude\rules\bridge-essential.md .claude\skills\bridge .codex\skills\bridge .codex\hooks.json` -> remaining target-surface references are deprecated, historical, prohibited, alias-only, or implementation fallback paths
- `python -m pytest platform_tests\scripts\test_session_self_initialization.py platform_tests\scripts\test_bridge_dispatch_config.py -q --tb=short` -> `74 passed`
- Combined focused verification:
  `python -m pytest platform_tests\scripts\test_dispatch_author_meets_reviewer.py platform_tests\scripts\test_cross_harness_bridge_trigger.py platform_tests\scripts\test_session_self_initialization.py platform_tests\scripts\test_bridge_dispatch_config.py platform_tests\scripts\test_single_harness_bridge_dispatcher.py platform_tests\scripts\test_single_harness_bridge_automation.py platform_tests\scripts\test_slice_3_hook_registrations.py -q --tb=short` -> `185 passed`
- `python -m ruff check ...` on touched dispatcher/startup/test files -> `All checks passed!`
- `python -m ruff format --check ...` on touched dispatcher/startup/test files -> `8 files already formatted`
- `python -m groundtruth_kb.cli bridge dispatch config --json` -> config exists, no errors
- `python -m groundtruth_kb.cli bridge dispatch health --json` -> `health_status: PASS`

## Residual Risk

This implementation does not read or mutate external `$CODEX_HOME` automation
memory. Any external Codex app automation disposition remains out of scope for
this in-repo report and requires a separate owner-controlled path if still
needed.
