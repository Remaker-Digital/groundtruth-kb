NEW

bridge_kind: implementation_report
Document: gtkb-startup-relay-truncation-fix-refile
Version: 011
Author: Loyal Opposition acting under owner-requested correction (Codex, harness A)
Date: 2026-05-27 UTC
Responds to: bridge/gtkb-startup-relay-truncation-fix-refile-010.md
Approved proposal: bridge/gtkb-startup-relay-truncation-fix-refile-003.md
Approved GO: bridge/gtkb-startup-relay-truncation-fix-refile-004.md
Project Authorization: PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING
Project: PROJECT-GTKB-RELIABILITY-FIXES
Work Item: WI-3323
target_paths: ["scripts/workstream_focus.py", "platform_tests/hooks/test_workstream_focus.py"]

# Implementation Report - Startup Relay Raw Cache Read Allowlist

## Claim

Implemented the narrow `-010` NO-GO correction. The startup input gate now
allows the read-only PowerShell form that failed in the live session:

```text
Get-Content -Raw .codex/gtkb-hooks/last-user-visible-startup-lo.md
```

The existing exact-path protections remain active: only the active harness
startup relay cache paths are allowed during `startup_response_pending`, and
ordinary non-cache reads remain blocked.

## Specification Links

- `DCL-INIT-KEYWORD-STARTUP-DISCLOSURE-RELAY-001`
- `DCL-INIT-KEYWORD-CONSISTENT-ASSERTION-001`
- `GOV-SESSION-SELF-INITIALIZATION-001`
- `PB-SESSION-STARTUP-GOVERNANCE-DISCLOSURE-001`
- `DCL-SESSION-STARTUP-TOKEN-BUDGET-001`
- `SPEC-CANONICAL-INIT-KEYWORD-SYNTAX-001`
- `ADR-CODEX-HOOK-PARITY-FALLBACK-001`
- `GOV-RELIABILITY-FAST-LANE-001`
- `GOV-FILE-BRIDGE-AUTHORITY-001`
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`

## Changes

- `scripts/workstream_focus.py`
  - Extended `_STARTUP_CACHE_READ_COMMAND_RE` with a third capture group for
    `Get-Content -Raw <path>`.
  - Included that capture group in the candidate path selection before the
    existing allowed-cache-path check.
- `platform_tests/hooks/test_workstream_focus.py`
  - Added
    `test_startup_response_pending_allows_raw_startup_cache_read_without_literalpath`.

## Spec-Derived Verification

| Requirement / constraint | Verification | Result |
|---|---|---|
| Startup relay can perform the named read-only cache read | Direct guard reproduction with `Get-Content -Raw .codex/gtkb-hooks/last-user-visible-startup-lo.md` | PASS |
| Existing `-LiteralPath` cache read remains allowed | Direct guard reproduction with `Get-Content -Raw -LiteralPath .codex/gtkb-hooks/last-user-visible-startup-lo.md` | PASS |
| Non-cache reads remain blocked during pending startup relay | Direct guard reproduction with `Get-Content -Raw -LiteralPath bridge/INDEX.md` | PASS |
| Regression suite covers startup relay guard behavior | `python -m pytest platform_tests/hooks/test_workstream_focus.py -q --tb=short` | PASS |
| Formatting and lint are clean | Ruff check and format-check on touched files | PASS |

## Verification Commands

```text
python -m pytest platform_tests/hooks/test_workstream_focus.py -q --tb=short
```

Observed result: `59 passed, 3 skipped, 2 xfailed`.

```text
python -m ruff check scripts/workstream_focus.py platform_tests/hooks/test_workstream_focus.py
```

Observed result: `All checks passed!`.

```text
python -m ruff format --check scripts/workstream_focus.py platform_tests/hooks/test_workstream_focus.py
```

Observed result: `2 files already formatted`.

```text
<synthetic Python call into scripts/workstream_focus.py::guard_tool_use>
```

Observed result:

```text
Get-Content -Raw -LiteralPath .codex/gtkb-hooks/last-user-visible-startup-lo.md
{}
Get-Content -Raw .codex/gtkb-hooks/last-user-visible-startup-lo.md
{}
Get-Content -Raw -LiteralPath bridge/INDEX.md
{"decision": "block", ...}
```

## Risk And Rollback

Risk is low and localized to the startup relay cache-read allowlist. The new
accepted command shape still flows through the same forbidden-token check and
the same resolved-path membership check against `_allowed_startup_relay_cache_reads(...)`.
Rollback is to remove the `path_c` regex branch and the new regression test.

## Owner Action Required

None.

Copyright 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
