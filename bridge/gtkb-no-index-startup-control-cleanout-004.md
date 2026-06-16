NEW

author_identity: prime-builder/codex
author_harness_id: A
author_session_context_id: 019ecc9e-ca08-7b40-8eb2-23994cc2029d
author_model: gpt-5-codex
author_model_configuration: Codex desktop

# Prime Builder Implementation Report - No-Index Startup And Control-Surface Cleanout

bridge_kind: implementation_report
Document: gtkb-no-index-startup-control-cleanout
Version: 004
Implemented GO: bridge/gtkb-no-index-startup-control-cleanout-003.md
Date: 2026-06-15 America/Los_Angeles

## Specification Links

- PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001
- GOV-FILE-BRIDGE-AUTHORITY-001
- DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001
- DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001
- DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001
- SPEC-CENTRALIZED-DISPATCH-SERVICE-001
- SPEC-DISPATCH-ENVELOPE-ELEMENT-001

## Implementation Summary

Removed active startup/control-surface instructions that made
`bridge/INDEX.md` look like live bridge authority. Updated `AGENTS.md`,
`config/agent-control/SESSION-STARTUP-INDEX.md`,
`config/agent-control/LOYAL-OPPOSITION-STARTUP-OVERLAY.md`,
`config/agent-control/system-interface-map.toml`,
`scripts/session_start_dispatch_core.py`, and
`scripts/session_self_initialization.py` to direct agents to
TAFE/dispatcher state plus status-bearing versioned bridge files under
`bridge/`.

`scripts/session_self_initialization.py` now derives bridge metrics from the
versioned bridge file chain first and only treats `bridge/INDEX.md` as an
absent/deprecated compatibility fallback. Startup freshness metadata now tracks
`bridge/*.md` rather than `bridge/INDEX.md`.

## Verification

- `Test-Path bridge\INDEX.md` -> `False`
- Targeted stale-reference sweep over startup/control surfaces:
  `rg -n "bridge/INDEX\.md|INDEX\.md|bridge index" AGENTS.md config/agent-control scripts\session_self_initialization.py scripts\session_start_dispatch_core.py scripts\cross_harness_bridge_trigger.py scripts\single_harness_bridge_dispatcher.py .claude\rules\bridge-essential.md .claude\skills\bridge .codex\skills\bridge .codex\hooks.json`
  shows remaining target-surface references are deprecated, historical,
  prohibited, alias-only, or implementation fallback paths.
- `python -m pytest platform_tests\scripts\test_session_self_initialization.py platform_tests\scripts\test_bridge_dispatch_config.py -q --tb=short` -> `74 passed`
- Combined focused verification:
  `python -m pytest platform_tests\scripts\test_dispatch_author_meets_reviewer.py platform_tests\scripts\test_cross_harness_bridge_trigger.py platform_tests\scripts\test_session_self_initialization.py platform_tests\scripts\test_bridge_dispatch_config.py platform_tests\scripts\test_single_harness_bridge_dispatcher.py platform_tests\scripts\test_single_harness_bridge_automation.py platform_tests\scripts\test_slice_3_hook_registrations.py -q --tb=short` -> `185 passed`
- `python -m ruff check ...` on touched startup/dispatcher/test files -> `All checks passed!`
- `python -m ruff format --check ...` on touched startup/dispatcher/test files -> `8 files already formatted`
- `python -m groundtruth_kb.cli bridge dispatch config --json` -> config exists, no errors
- `python -m groundtruth_kb.cli bridge dispatch health --json` -> `health_status: PASS`

## Residual Risk

Some broader repository files outside this packet still mention
`bridge/INDEX.md`; they require separate GO packets or are historical tooling.
This report only claims cleanup for the startup/control targets authorized by
this thread.
