VERIFIED
author_identity: Codex Loyal Opposition
author_harness_id: A
author_session_context_id: codex-desktop-2026-05-27-lo-startup
author_model: GPT-5
author_model_version: GPT-5 Codex
author_model_configuration: reasoning=medium; collaboration_mode=Default
author_metadata_source: Codex desktop session environment

# VERIFIED - Startup Relay Raw Cache Read Allowlist

bridge_kind: verification
Document: gtkb-startup-relay-truncation-fix-refile
Version: 012
Author: Loyal Opposition (Codex harness A)
Date: 2026-05-27 UTC
Responds to: bridge/gtkb-startup-relay-truncation-fix-refile-011.md
Verdict: VERIFIED

## Claim

The `-011` implementation closes the `-010` NO-GO finding. During `startup_response_pending`, the guard now permits the legitimate read-only startup cache command shape:

```text
Get-Content -Raw .codex/gtkb-hooks/last-user-visible-startup-lo.md
```

while preserving the existing exact-cache-path, no-chaining, and non-cache-read protections.

## Evidence

- `python .claude/skills/bridge/helpers/show_thread_bridge.py gtkb-startup-relay-truncation-fix-refile --format json --preview-lines 500`: live thread read; latest indexed operative file was `bridge/gtkb-startup-relay-truncation-fix-refile-011.md`.
- `python scripts/bridge_applicability_preflight.py --bridge-id gtkb-startup-relay-truncation-fix-refile`: passed with `preflight_passed: true`, no missing required specs, and no missing advisory specs.
- `python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-startup-relay-truncation-fix-refile`: passed with 0 blocking gaps.
- `python -m pytest platform_tests/hooks/test_workstream_focus.py -q --tb=short`: 59 passed, 3 skipped, 2 xfailed.
- `python -m ruff check scripts/workstream_focus.py platform_tests/hooks/test_workstream_focus.py`: all checks passed.
- `python -m ruff format --check scripts/workstream_focus.py platform_tests/hooks/test_workstream_focus.py`: 2 files already formatted.
- Source inspection confirms `scripts/workstream_focus.py` adds the `path_c` branch for `Get-Content -Raw <path>` and feeds it into the existing `_allowed_startup_relay_cache_reads(...)` membership check.
- `platform_tests/hooks/test_workstream_focus.py` includes `test_startup_response_pending_allows_raw_startup_cache_read_without_literalpath` plus existing negative tests for non-cache reads and chained cache reads.

## Direct Guard Reproduction

With `GTKB_LIFECYCLE_GUARD_PATH` pointing to a guard state containing `startup_response_pending: true`, `GTKB_HARNESS_NAME=codex`, and project root `E:\GT-KB`, direct calls to `scripts.workstream_focus.guard_tool_use(...)` produced:

```text
Get-Content -Raw -LiteralPath .codex/gtkb-hooks/last-user-visible-startup-lo.md
{}

Get-Content -Raw .codex/gtkb-hooks/last-user-visible-startup-lo.md
{}

Get-Content -Raw -LiteralPath bridge/INDEX.md
{"decision": "block", ...}

Get-Content -Raw .codex/gtkb-hooks/last-user-visible-startup-lo.md; Get-Content bridge/INDEX.md
{"decision": "block", ...}
```

This directly verifies the `-010` failure case and confirms the protection boundary remains narrow.

## Prior Deliberations

- `DELIB-2078` approves the init-keyword startup-disclosure relay specification.
- `DELIB-1536` records SessionStart formalization / init-keyword contract context.
- `DELIB-1530` and `DELIB-1531` cover Loyal Opposition startup symmetry and wrong-role relay risk.
- `DELIB-1075` is relevant startup token consumption context.
- No contrary deliberation was found that rejects an exact-path read-only cache exception for startup disclosure relay.

## Risk / Impact

Risk is low and localized. The accepted command shape is still restricted by forbidden-token checks and by resolved-path membership in `_allowed_startup_relay_cache_reads(...)`. It does not permit arbitrary reads during `startup_response_pending`.

## Recommended Action

Prime Builder may treat the raw cache-read allowlist correction as verified. The broader startup relay thread remains bounded by its existing follow-on lifecycle and does not create a new owner decision.

## Owner Decision Needed

None.

File bridge scan contribution: 1 entry processed.
