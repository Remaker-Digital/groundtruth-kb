NEW

# gtkb-wi4893-lo-dispatch-readiness-gate - Implementation Report

bridge_kind: implementation_report
Document: gtkb-wi4893-lo-dispatch-readiness-gate
Version: 003
Author: Prime Builder (Codex harness A)
Date: 2026-06-28 UTC

author_identity: prime-builder/codex
author_harness_id: A
author_session_context_id: 019f09c9-2db0-7b00-a337-40f998b07e56
author_model: GPT-5
author_model_version: gpt-5
author_model_configuration: Codex Desktop default; reasoning effort not exposed

Project Authorization: PAUTH-PROJECT-GTKB-DISPATCHER-RELIABILITY-WI-4893-RELEASE-READINESS-HARDENING
Project: PROJECT-GTKB-DISPATCHER-RELIABILITY
Work Item: WI-4893

Responds to: bridge/gtkb-wi4893-lo-dispatch-readiness-gate-002.md
Implementation-start packet: sha256:d514ef953785b0d27a41080987f92f3ac04f2a18f4d71f052760a515a9bf05a5

---

## Summary

Implemented the LO dispatch readiness health hardening approved at `bridge/gtkb-wi4893-lo-dispatch-readiness-gate-002.md`.

The dispatcher health surface now detects recent selected LO worker run failures from dispatch-run sidecars and bounded stderr marker parsing even when recipient runtime state has compacted back to `last_result=launched`. The three observed release-blocking failure classes are now surfaced as WARN findings instead of a false PASS:

- Ollama/D: `max_turn_exhaustion`
- Cursor/E: GUI/Electron launcher path classified as `cursor_headless_cli_unavailable`, including exit-0 warning-only runs
- OpenRouter/F: missing key classified as `provider_configuration_failure`

The implementation also keeps Cursor fail-closed on GUI launcher fallback and adds safe in-root release-worktree `.env.local` fallback so OpenRouter dispatch can consume the owner-maintained primary `.env.local` without copying or printing secrets.

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
- `SPEC-DISPATCH-KILL-SWITCH-EMERGENCY-ONLY-001`
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`

## Files Changed

Scoped WI-4893 readiness paths:

- `groundtruth-kb/src/groundtruth_kb/bridge_dispatch_config.py`
- `groundtruth-kb/src/groundtruth_kb/bridge_dispatch_report.py`
- `platform_tests/groundtruth_kb/cli/test_bridge_dispatch_report_cli.py`
- `platform_tests/scripts/test_bridge_dispatch_config.py`
- `platform_tests/scripts/test_cross_harness_bridge_trigger.py`
- `platform_tests/scripts/test_cursor_harness.py`
- `platform_tests/scripts/test_openrouter_harness.py`
- `scripts/_env.py`
- `scripts/cross_harness_bridge_trigger.py`
- `scripts/cursor_harness.py`
- `scripts/openrouter_harness.py`

Other dirty worktree paths pre-existed or belong to sibling WI-4893 / WI-3459 work and are not claimed by this report.

## Implementation Details

- Added recent-run health evaluation in `bridge_dispatch_config.py`. It scans selected recipient dispatch-run sidecars, reads bounded stderr text, and classifies the latest run per selected recipient. The classification covers max-turn exhaustion, missing OpenRouter key, Cursor GUI/Electron warning output, generic nonzero exits, and preserves WI-4789 semantics by reporting recoverable runtime failures as overall `WARN` when dispatchable recipients still exist.
- Added `cursor_headless_cli_unavailable` to runtime failure classes.
- Preserved existing report history behavior while relying on the status collector so `report --json` now reports `runtime_failure_count > 0` for the compact-state false-green case.
- Added `.env.local` fallback in `scripts/_env.py` for release worktrees under `E:\GT-KB\.tmp\<worktree>` when the worktree omits `.env.local`; it resolves only to the primary in-root checkout's `.env.local` and does not copy or log credential values.
- Confirmed `scripts/cross_harness_bridge_trigger.py` forwards `OPENROUTER_API_KEY` from the allowlisted env set, and has fatal-output markers for the OpenRouter missing-key and Cursor GUI/headless failure classes.
- Confirmed `scripts/cursor_harness.py` rejects `cursor`, `cursor.cmd`, and `cursor.exe` GUI launcher paths instead of appending `agent` or accepting GUI fallback.
- Confirmed D/F root-escaping Glob/Grep behavior remains covered in the harness tests.

## Spec-To-Test Mapping

| Spec / governing surface | Verification evidence |
| --- | --- |
| `GOV-FILE-BRIDGE-AUTHORITY-001` / `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` | Implementation-start packet succeeded: `sha256:d514ef953785b0d27a41080987f92f3ac04f2a18f4d71f052760a515a9bf05a5`; target set matched the GO proposal. |
| `DCL-DISPATCH-ENVELOPE-RULES-001` | `python -m pytest platform_tests/scripts/test_cross_harness_bridge_trigger.py -q --tb=short` passed; includes OpenRouter env allowlist forwarding coverage. |
| `SPEC-DISPATCHER-CONTROL-SURFACE-001` / `ADR-DISPATCHER-ARCHITECTURE-001` | `python -m pytest platform_tests/scripts/test_bridge_dispatch_config.py platform_tests/groundtruth_kb/cli/test_bridge_dispatch_report_cli.py -q --tb=short` passed; compact recipient state plus recent run sidecars now produce WARN findings. |
| `SPEC-CENTRALIZED-DISPATCH-SERVICE-001` | Synthetic D/E/F recent-run fixtures prove selected LO targets with no verdict-producing completion are visible as release-blocking runtime findings. |
| Cursor headless dispatch readiness | `python -m pytest platform_tests/scripts/test_cursor_harness.py -q --tb=short` passed; GUI launcher fallback is rejected. |
| OpenRouter dispatch readiness | `python -m pytest platform_tests/scripts/test_openrouter_harness.py -q --tb=short` passed; release-worktree `.env.local` fallback and root-escaping path behavior are covered. |
| Code quality | `python -m ruff check ...` passed and `python -m ruff format --check ...` passed on the approved changed files. |
| Live readiness smoke | With local worktree source on `PYTHONPATH`, `python -m groundtruth_kb.cli bridge dispatch health|status|report --json` reported `WARN`, not false PASS, with three runtime findings for D/E/F. |

## Commands Executed

```text
python scripts/implementation_authorization.py begin --bridge-id gtkb-wi4893-lo-dispatch-readiness-gate --session-id 019f09c9-2db0-7b00-a337-40f998b07e56 --expires-minutes 120
python -m pytest platform_tests/scripts/test_bridge_dispatch_config.py platform_tests/groundtruth_kb/cli/test_bridge_dispatch_report_cli.py -q --tb=short
python -m pytest platform_tests/scripts/test_openrouter_harness.py platform_tests/scripts/test_cursor_harness.py -q --tb=short
python -m pytest platform_tests/scripts/test_cross_harness_bridge_trigger.py -q --tb=short
python -m ruff check scripts/cross_harness_bridge_trigger.py scripts/cursor_harness.py scripts/openrouter_harness.py scripts/_env.py groundtruth-kb/src/groundtruth_kb/bridge_dispatch_config.py groundtruth-kb/src/groundtruth_kb/bridge_dispatch_report.py platform_tests/scripts/test_cross_harness_bridge_trigger.py platform_tests/scripts/test_cursor_harness.py platform_tests/scripts/test_openrouter_harness.py platform_tests/scripts/test_bridge_dispatch_config.py platform_tests/groundtruth_kb/cli/test_bridge_dispatch_report_cli.py
python -m ruff format --check scripts/cross_harness_bridge_trigger.py scripts/cursor_harness.py scripts/openrouter_harness.py scripts/_env.py groundtruth-kb/src/groundtruth_kb/bridge_dispatch_config.py groundtruth-kb/src/groundtruth_kb/bridge_dispatch_report.py platform_tests/scripts/test_cross_harness_bridge_trigger.py platform_tests/scripts/test_cursor_harness.py platform_tests/scripts/test_openrouter_harness.py platform_tests/scripts/test_bridge_dispatch_config.py platform_tests/groundtruth_kb/cli/test_bridge_dispatch_report_cli.py
python -m pytest platform_tests/scripts/test_bridge_dispatch_config.py platform_tests/groundtruth_kb/cli/test_bridge_dispatch_report_cli.py platform_tests/scripts/test_openrouter_harness.py platform_tests/scripts/test_cursor_harness.py -q --tb=short
$env:PYTHONPATH = (Resolve-Path groundtruth-kb\src).Path; python -m groundtruth_kb.cli bridge dispatch health --json
$env:PYTHONPATH = (Resolve-Path groundtruth-kb\src).Path; python -m groundtruth_kb.cli bridge dispatch status --json
$env:PYTHONPATH = (Resolve-Path groundtruth-kb\src).Path; python -m groundtruth_kb.cli bridge dispatch report --json
python -c "from scripts._env import load_env_local; values = load_env_local(check_only=True); val = values.get('OPENROUTER_API_KEY',''); print({'has_OPENROUTER_API_KEY': bool(val), 'OPENROUTER_API_KEY_length': len(val)})"
```

Observed results:

- `platform_tests/scripts/test_bridge_dispatch_config.py platform_tests/groundtruth_kb/cli/test_bridge_dispatch_report_cli.py`: 41 passed in 24.69s.
- `platform_tests/scripts/test_openrouter_harness.py platform_tests/scripts/test_cursor_harness.py`: 27 passed in 4.19s.
- `platform_tests/scripts/test_cross_harness_bridge_trigger.py`: 106 passed in 55.51s.
- Combined post-format focused run: 68 passed in 9.54s.
- Ruff check: all checks passed.
- Ruff format check: 11 files already formatted.
- Local-source live smoke: health/status/report all reported `WARN`, with runtime findings for D max-turn exhaustion, E Cursor headless unavailable / GUI warning path, and F provider configuration failure.
- Env fallback smoke: `has_OPENROUTER_API_KEY=True`, value length 73; no secret value printed.

## Runtime / Release Caveats

During verification, the owner reported Windows console windows spawning repeatedly. Process inspection showed the storm was rooted in the primary checkout `E:\GT-KB`, not this release worktree: multiple nested `pythonw.exe` daemon processes were running `E:\GT-KB\scripts\gtkb_dispatcher_daemon.py`, alongside repeated `cross_harness_bridge_trigger.py` console processes and OpenRouter worker chains. I stopped only dispatcher-owned command lines, the queued `gt bridge dispatch daemon stop` then completed, and a 10-second quiet-period process check found zero matching daemon/trigger/worker processes.

The daemon multi-instance / monitoring loop is not fixed by this report because `scripts/gtkb_dispatcher_daemon.py` is outside the approved target paths for `gtkb-wi4893-lo-dispatch-readiness-gate`. The dispatcher daemon remains intentionally stopped. Release should remain blocked until a separate governed daemon-loop repair covers the daemon script and any hook launcher behavior required to prevent visible console storms.

The bare `gt` executable in this worktree still imports the previously installed package, so bare `gt bridge dispatch health|status|report --json` can still show the old false PASS before the package is reinstalled from this source tree. The verified local-source smoke uses `PYTHONPATH=groundtruth-kb/src`, matching the patched source that will ship in the release build.

## Acceptance Status

Accepted for this bounded thread: the approved false-green health/reporting and OpenRouter/Cursor readiness surfacing work is implemented and tested.

Not accepted as release-ready overall: dispatcher daemon spawning remains a separate release blocker outside this GO scope.

## Recommended Commit Type

Recommended commit type: fix

fix: this repairs release-blocking dispatcher readiness and health-reporting defects without adding a new user-facing capability surface.

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
