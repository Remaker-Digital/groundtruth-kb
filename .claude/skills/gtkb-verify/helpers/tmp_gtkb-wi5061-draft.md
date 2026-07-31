GO

# gtkb-wi5061-cursor-harness-no-gui-launcher-probe — Loyal Opposition review

bridge_kind: lo_verdict
Document: gtkb-wi5061-cursor-harness-no-gui-launcher-probe
Version: 002
Author: Loyal Opposition (Ollama, harness D)
Date: 2026-07-06 UTC

author_identity: loyal-opposition/ollama
author_harness_id: D
author_session_context_id: 2026-07-06T20-55-14Z-loyal-opposition-D-945c6c
author_model: kimi-k2.7-code:cloud
author_model_version: cloud
author_model_configuration: Ollama harness shim; route kimi-k2-7-code-cloud; skill bridge-review; guarded tools Read, Write, Edit, Grep, Glob, Bash

## Status

GO

## Applicability Preflight

- `scripts/bridge_applicability_preflight.py --bridge-id gtkb-wi5061-cursor-harness-no-gui-launcher-probe`
  - `preflight_passed: true`
  - All blocking and advisory specifications cited.
- `scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-wi5061-cursor-harness-no-gui-launcher-probe`
  - Mandatory gate passed; 0 blocking gaps.

## Deliberation

The Prime Proposal correctly identifies that `scripts/cursor_harness.py`
`_cursor_supports_agent_subcommand` may invoke the Cursor GUI launcher
(`cursor`/`cursor.cmd`/`cursor.exe`) with `agent --help`, causing the desktop IDE
to open on Windows because `CREATE_NO_WINDOW` only suppresses console windows,
not GUI windows. The proposal's trigger-agnostic fix is limited to two files
(`scripts/cursor_harness.py` and `platform_tests/scripts/test_cursor_harness.py`),
fits the reliability fast lane, and does not mutate KB content.

The implementation in the proposal has already been applied to the worktree:

- `_cursor_supports_agent_subcommand` now refuses GUI-launcher names by checking
  the executable basename against `_CURSOR_GUI_LAUNCHER_NAMES` before running
  the `agent --help` probe.
- `_resolve_agent_command` no longer falls back to `cursor`/`cursor.cmd`/
  `cursor.exe`; missing standalone agents raise `CursorHarnessError` with
  guidance to set `CURSOR_AGENT_BIN`.
- `CURSOR_AGENT_BIN` pointing at a GUI launcher is rejected unless the launcher
  also passes the (now launcher-refusing) capability check.
- New and updated tests cover:
  - rejecting `CURSOR_AGENT_BIN` when it points at a GUI launcher that does not
    expose a headless `agent --help`;
  - falling back to a standalone `cursor-agent` path only when `_cursor_supports_agent_subcommand`
    is mocked as passing;
  - failing closed when no standalone agent is available.

## Spec-Derived Verification Results

- `groundtruth-kb/.venv/Scripts/python.exe -m pytest platform_tests/scripts/test_cursor_harness.py -q --no-header`
  - **25 passed, 1 warning** (unknown `asyncio_mode` config option is advisory).
- `groundtruth-kb/.venv/Scripts/python.exe -m pytest platform_tests/scripts/test_verify_cursor_dispatch.py -q --no-header`
  - **6 passed, 1 warning** (same advisory config warning).
- `ruff check scripts/cursor_harness.py platform_tests/scripts/test_cursor_harness.py`
  - All checks passed.
- `ruff format --check scripts/cursor_harness.py platform_tests/scripts/test_cursor_harness.py`
  - 2 files already formatted.

## Concerns / Blockers

None. The change is low-risk, scoped, and the verification plan executes cleanly.

## Recommended Next Step

Prime Builder may proceed. This review artifact is the next numbered bridge file
for `gtkb-wi5061-cursor-harness-no-gui-launcher-probe` (version 002).
