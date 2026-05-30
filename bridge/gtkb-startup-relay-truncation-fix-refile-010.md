NO-GO

bridge_kind: verification_verdict
Document: gtkb-startup-relay-truncation-fix-refile
Version: 010
Author: Loyal Opposition (Codex, harness A)
Date: 2026-05-27 UTC
Reviewer: Loyal Opposition
Responds to: bridge/gtkb-startup-relay-truncation-fix-refile-009.md

# Loyal Opposition Verification - Startup Relay Truncation Fix Refile

## Verdict Summary

NO-GO.

The `-009` stale-cache correction is directionally useful, and the mandatory
applicability and clause preflights pass. However, live session evidence from
2026-05-27 exposed a remaining startup relay defect in the same receiver guard:
the startup input gate instructs the assistant to perform one read-only
filesystem read of the named cache file, but `guard_tool_use(...)` only permits
a narrower `Get-Content ... -LiteralPath ...` spelling. A legitimate single-file
read, `Get-Content -Raw .codex/gtkb-hooks/last-user-visible-startup-lo.md`, is
blocked even though it targets the exact approved cache file and contains no
chaining, redirection, mutation, interpolation, or extra path access.

This means the startup relay can still fail during the owner-visible init
keyword path, producing the bad outcome this thread family is meant to prevent:
the assistant reports that the disclosure relay was blocked instead of relaying
the cached startup disclosure.

## Applicability Preflight

```text
python scripts/bridge_applicability_preflight.py --bridge-id gtkb-startup-relay-truncation-fix-refile
```

Observed result: PASS; `missing_required_specs: []`,
`missing_advisory_specs: []`; operative file
`bridge/gtkb-startup-relay-truncation-fix-refile-009.md`.

## Clause Applicability

```text
python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-startup-relay-truncation-fix-refile
```

Observed result: PASS; `Blocking gaps (gate-failing): 0`.

## Prior Deliberations

Deliberation search:

```text
python -m groundtruth_kb deliberations search "startup relay cache read Get-Content Raw LiteralPath WI-3323" --limit 8
```

Relevant context:

- `DELIB-1075` - startup token consumption review context.
- No contrary deliberation was found that rejects an exact-path read-only cache
  exception for the startup disclosure relay.

## Specifications Carried Forward

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

## Spec-to-Test Mapping

| Specification | Test or Verification Command | Executed | Result |
|---|---|---:|---|
| `DCL-INIT-KEYWORD-STARTUP-DISCLOSURE-RELAY-001` | Synthetic `guard_tool_use(...)` reproduction for both allowed and blocked startup cache read forms | yes | FAIL: literal-path form allowed; non-`-LiteralPath` read-only form blocked |
| `DCL-INIT-KEYWORD-CONSISTENT-ASSERTION-001` | Target path uses role-scoped LO cache `.codex/gtkb-hooks/last-user-visible-startup-lo.md` | yes | FAIL: exact LO cache target is still blocked under the common PowerShell form |
| `DCL-SESSION-STARTUP-TOKEN-BUDGET-001` | Inspection of `_startup_gate_response(...)` pointer design in `scripts/workstream_focus.py` | yes | PASS: disclosure remains a bounded pointer, but receiver cannot always read it |
| `ADR-CODEX-HOOK-PARITY-FALLBACK-001` | Source inspection of shared `scripts/workstream_focus.py` hook guard | yes | FAIL: Codex relay path remains brittle to allowed read syntax |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | This table plus executed reproduction | yes | PASS for mapping discipline; implementation result is NO-GO |

## Positive Confirmations

- `bridge/gtkb-startup-relay-truncation-fix-refile-009.md` passes the mandatory
  applicability preflight and clause preflight.
- The existing exact-path exception still allows
  `Get-Content -Raw -LiteralPath .codex/gtkb-hooks/last-user-visible-startup-lo.md`.
- The prior verified tests continue to cover non-cache reads, chained reads,
  and mutation commands as blocked cases.

## Findings

### F1 - P1 - Startup relay cache read allowlist is too narrow for the relay instruction

Observation: `scripts/workstream_focus.py:1108` defines
`_STARTUP_CACHE_READ_COMMAND_RE` with only `-LiteralPath` read forms, and
`scripts/workstream_focus.py:1185` extracts only `path_a` / `path_b`. The test
coverage at `platform_tests/hooks/test_workstream_focus.py:1084` verifies only
`Get-Content -Raw -LiteralPath ...`.

Live reproduction:

```text
Get-Content -Raw -LiteralPath .codex/gtkb-hooks/last-user-visible-startup-lo.md
{}

Get-Content -Raw .codex/gtkb-hooks/last-user-visible-startup-lo.md
{"decision": "block", "reason": "BLOCKED (GTKB-STARTUP-INPUT-GATE): startup disclosure has been emitted; awaiting owner's next message before tool use. The init-keyword contract relays the disclosure on match (init gtkb / init gtkb advisory / etc.) and passes through on no-match (per ADR-SESSION-START-INIT-KEYWORD-CONTRACT-001)."}
```

Deficiency rationale: the UserPromptSubmit startup relay payload says to read
the named cache file once. It does not require the assistant to choose the
specific `-LiteralPath` option. A read-only `Get-Content -Raw <approved-cache>`
command is semantically equivalent for this relative in-root cache path and
does not weaken the exact target-path, no-chaining, no-redirection, and
no-mutation protections.

Proposed solution: extend `_STARTUP_CACHE_READ_COMMAND_RE` and
`_is_startup_relay_cache_read(...)` to accept `Get-Content -Raw <path>` for the
same already approved cache paths. Add a regression test proving this form is
allowed while the existing rejection tests for non-cache reads, chained reads,
redirection/interpolation tokens, and mutation commands remain intact.

Prime Builder implementation context: a narrow patch is sufficient:

- Add a third capture group for `-Raw <path>` in
  `scripts/workstream_focus.py`.
- Include that capture group in the `raw_path` selection.
- Add a focused test next to
  `test_startup_response_pending_allows_exact_startup_cache_read(...)`.
- Run `python -m pytest platform_tests/hooks/test_workstream_focus.py -q --tb=short`.
- Run `python -m ruff check scripts/workstream_focus.py platform_tests/hooks/test_workstream_focus.py`.
- Run `python -m ruff format --check scripts/workstream_focus.py platform_tests/hooks/test_workstream_focus.py`.

## Required Revisions

- Revise the startup relay guard so `Get-Content -Raw <approved-startup-cache>`
  is permitted during `startup_response_pending` when the path resolves to one
  of `_allowed_startup_relay_cache_reads(...)`.
- Add regression coverage for that exact command shape.
- Preserve all existing negative tests for ordinary tool use, non-cache reads,
  chained reads, and cache mutation.

## Commands Executed

```text
python scripts/bridge_applicability_preflight.py --bridge-id gtkb-startup-relay-truncation-fix-refile
```

PASS.

```text
python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-startup-relay-truncation-fix-refile
```

PASS.

```text
python -m groundtruth_kb deliberations search "startup relay cache read Get-Content Raw LiteralPath WI-3323" --limit 8
```

Returned eight results; `DELIB-1075` was relevant startup context; no contrary
decision was found.

```text
<synthetic Python call into scripts/workstream_focus.py::guard_tool_use>
```

Observed result: `Get-Content -Raw -LiteralPath ...` allowed, while
`Get-Content -Raw ...` against the same approved LO cache file was blocked.

## Owner Action Required

None.

Copyright 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
