NEW

Document: gtkb-startup-relay-pretooluse-read-exemption

Project Authorization: PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING
Project: PROJECT-GTKB-RELIABILITY-FIXES
Work Item: WI-3323
target_paths: ["scripts/workstream_focus.py", "platform_tests/hooks/test_workstream_focus.py"]

# Implementation Report - Startup Relay PreToolUse Read Exemption

Status: NEW
Author: Prime Builder (Codex / harness A)
Date: 2026-05-19 UTC
Responds to: `bridge/gtkb-startup-relay-pretooluse-read-exemption-003.md`

## Summary

This implementation fixes the startup relay gate defect where
`startup_response_pending` blocked every tool call, including the one read-only
cache read required to relay the owner-visible startup disclosure for
`::init gtkb lo`.

`guard_tool_use()` now permits only an exact startup relay cache read while the
startup response is pending. The exception is scoped to the active harness
startup cache files and accepts only `Get-Content -Raw -LiteralPath <cache.md>`
for the default, Prime Builder, or Loyal Opposition startup disclosure cache.
The gate continues to block non-cache reads, chained commands, redirect/control
operators, and mutation commands while `startup_response_pending` remains true.

## Specification Links

- DCL-INIT-KEYWORD-STARTUP-DISCLOSURE-RELAY-001 - requires the init-keyword path
  to relay the cached startup disclosure instead of substituting a short
  acknowledgement.
- SPEC-CANONICAL-INIT-KEYWORD-SYNTAX-001 - `::init gtkb lo` activates the
  canonical LO startup receiver path.
- DCL-INIT-KEYWORD-CONSISTENT-ASSERTION-001 - the receiver-side relay must stay
  tied to the asserted harness and role mode.
- GOV-SESSION-SELF-INITIALIZATION-001 - requires fresh-session startup
  disclosure delivery.
- PB-SESSION-STARTUP-GOVERNANCE-DISCLOSURE-001 - treats the startup governance
  disclosure as first-class owner-visible content.
- DCL-SESSION-STARTUP-TOKEN-BUDGET-001 - supports the bounded pointer relay
  pattern rather than inlining the full disclosure into hook context.
- ADR-CODEX-HOOK-PARITY-FALLBACK-001 - startup relay behavior must remain
  explicit and parity-safe across harness hook implementations.
- GOV-RELIABILITY-FAST-LANE-001 - WI-3323 is a reliability fix under the
  standing fast-lane authorization.
- GOV-FILE-BRIDGE-AUTHORITY-001 - bridge protocol authority for this report.
- DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001 - this report cites
  the governing specifications.
- DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001 - verification below maps
  requirements to executed tests.
- GOV-ARTIFACT-ORIENTED-GOVERNANCE-001, ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001,
  and DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001 - preserve the defect, fix, and review
  evidence through governed bridge state.

## Changes Made

- `scripts/workstream_focus.py`
  - Added an exact startup-cache-read recognizer for the pending startup gate.
  - Allows only harness-scoped startup disclosure cache files:
    `last-user-visible-startup.md`, `last-user-visible-startup-pb.md`, and
    `last-user-visible-startup-lo.md`.
  - Rejects shell control operators and any command shape other than the
    read-only `Get-Content ... -LiteralPath ...` cache read.
  - Preserves `_clear_startup_response_pending_for_followup()` behavior; the
    allowed cache read does not clear `startup_response_pending`.

- `platform_tests/hooks/test_workstream_focus.py`
  - Added positive regression coverage for the exact LO startup cache read.
  - Added negative coverage proving non-cache reads, chained cache reads, and
    cache mutations remain blocked while startup response is pending.

## Spec-Derived Test Mapping

| Requirement / constraint | Verification |
|---|---|
| Startup relay must be able to read the cached owner-visible disclosure | `test_startup_response_pending_allows_exact_startup_cache_read` |
| Startup pending gate must continue blocking ordinary tool use | `test_startup_response_pending_blocks_tool_use_until_next_owner_prompt` |
| Exception must be exact-path and harness-cache scoped | `test_startup_response_pending_rejects_non_cache_read` |
| Exception must reject shell chaining and additional paths | `test_startup_response_pending_rejects_chained_cache_read` |
| Exception must reject mutation commands | `test_startup_response_pending_rejects_cache_mutation` |
| Follow-up clearing behavior remains separate from the cache read | `test_startup_response_pending_allows_exact_startup_cache_read` asserts pending state remains true |

## Verification Commands

```text
python -m pytest platform_tests/hooks/test_workstream_focus.py -q --tb=short
```

Observed result: `56 passed, 3 skipped, 2 xfailed`.

```text
python -m ruff check scripts/workstream_focus.py platform_tests/hooks/test_workstream_focus.py
```

Observed result: `All checks passed!`.

```text
python -m ruff format --check scripts/workstream_focus.py platform_tests/hooks/test_workstream_focus.py
```

Observed result: `2 files already formatted`.

## Governance Preflights

```text
python scripts/bridge_applicability_preflight.py --bridge-id gtkb-startup-relay-pretooluse-read-exemption
```

Observed result: `preflight_passed: true`; missing required specs: `[]`;
missing advisory specs: `[]`.

```text
python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-startup-relay-pretooluse-read-exemption
```

Observed result: blocking gaps: `0`.

## Decision Needed From Owner

None.

File bridge scan: 0 entries processed for this implementation report filing.
