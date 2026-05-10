NO-GO

# Loyal Opposition Review - Cross-Harness Trigger Windows Rename Race + Liveness Diagnostics

Reviewer: Loyal Opposition (Codex, harness A)
Date: 2026-05-10 UTC
Reviewed proposal: `bridge/gtkb-cross-harness-trigger-windows-rename-race-001-001.md`
Verdict: NO-GO

## Claim

The proposal correctly identifies a real bridge-dispatch state-write race in
`scripts/cross_harness_bridge_trigger.py`, and the mandatory preflights pass.
However, the proposed fix is too narrow for the observed failure modes. The
current writer uses one shared temp file path,
`.gtkb-state/bridge-poller/dispatch-state.json.tmp`, for every concurrent
trigger invocation. The local failure log shows failures not limited to
`WinError 32` target-file contention; it also includes `WinError 2` missing
temp-file failures and temp-write permission failures. A retry loop only around
`src.replace(dst)` with a shared `src` path can still lose races before or
during the replace step.

## Prior Deliberations

Deliberation searches executed:

```text
python -m groundtruth_kb deliberations search "cross harness trigger dispatch state rename race WinError 32 dispatch-failures" --limit 8
python -m groundtruth_kb deliberations search "smart poller retirement cross harness event driven trigger dispatch" --limit 8
python -m groundtruth_kb deliberations search "Codex hooks Windows retest cross harness trigger" --limit 8
python -m groundtruth_kb deliberations search "active session suppression counterpart active session trigger 120 seconds" --limit 8
```

Relevant results:

- `DELIB-S337-SMART-POLLER-RETIREMENT-2026-05-09` - owner decision authorizing retirement of the smart poller in favor of the cross-harness event-driven trigger.
- `DELIB-S337-CODEX-HOOKS-WINDOWS-RETEST-2026-05-08` - empirical basis for treating Codex hooks as live on Windows.
- `DELIB-S337-CODEX-HOOK-PARITY-STANCE-REFRESH-2026-05-08` - owner decision refreshing the stale Codex hook parity stance.
- `DELIB-S319-SMART-POLLER-POLICY-CLARIFICATION` - prior smart-poller policy context surfaced by search.
- No matching Deliberation Archive row was found for the exact active-session-suppression owner directive query, but the bridge thread `gtkb-cross-harness-trigger-active-session-suppression-001` carries that review/verification evidence.

## Applicability Preflight

- packet_hash: `sha256:845e14d8d32499fd41f252a0e11619626cc9c018303eafb8c02c138e8ed272ca`
- bridge_document_name: `gtkb-cross-harness-trigger-windows-rename-race-001`
- content_source: `indexed_operative`
- content_file: `bridge/gtkb-cross-harness-trigger-windows-rename-race-001-001.md`
- operative_file: `bridge/gtkb-cross-harness-trigger-windows-rename-race-001-001.md`
- preflight_passed: `true`
- missing_required_specs: []
- missing_advisory_specs: []

| Spec | Severity | Cited | Matched By |
|------|----------|-------|------------|
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | `advisory` | `yes` | content:artifact, content:traceability, content:deliberation |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | `blocking` | `yes` | path:.claude/rules/file-bridge-protocol.md, content:applications/ |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | `advisory` | `yes` | content:candidate, content:deferred, content:verified, content:retired |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | `blocking` | `yes` | doc:*, content:Specification Links, content:implementation proposal |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | `blocking` | `yes` | doc:*, content:VERIFIED, content:verification, content:spec-to-test |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | `advisory` | `yes` | content:owner decision, content:specification, content:ADR, content:DCL |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | `blocking` | `yes` | doc:*, path:.claude/rules/file-bridge-protocol.md, path:.claude/rules/codex-review-gate.md |

## Clause Applicability

- Bridge id: `gtkb-cross-harness-trigger-windows-rename-race-001`
- Operative file: `bridge\gtkb-cross-harness-trigger-windows-rename-race-001-001.md`
- Clauses evaluated: 5
- must_apply: 3, may_apply: 2, not_applicable: 0
- Evidence gaps in must_apply clauses: 0
- Blocking gaps (gate-failing): 0
- Mode: **mandatory** (default invocation). Exit 5 = blocking gap; exit 0 = pass.

| Clause | Spec | Applicability | Evidence found | Severity | Enforcement |
|---|---|---|---|---|---|
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001/CLAUSE-IN-ROOT` | `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | must_apply | yes | blocking | blocking |
| `GOV-FILE-BRIDGE-AUTHORITY-001/CLAUSE-INDEX-IS-CANONICAL` | `GOV-FILE-BRIDGE-AUTHORITY-001` | may_apply | — | blocking | blocking |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001/CLAUSE-CONCRETE-LINKS` | `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | must_apply | yes | blocking | blocking |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001/CLAUSE-SPEC-TO-TEST-MAPPING` | `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | must_apply | yes | blocking | blocking |
| `GOV-STANDING-BACKLOG-001/CLAUSE-VISIBILITY-BULK-OPS` | `GOV-STANDING-BACKLOG-001` | may_apply | — | blocking | blocking |

_Slice 2 mandatory gate: clauses with `enforcement_mode = "blocking"` and
must_apply applicability fail the gate (exit 5) when evidence is absent and
no `Owner waiver: <clause_id> — <DELIB-ID> — <reason>` line is cited.
Clauses with `enforcement_mode = "advisory"` are reported but never gate._

## Findings

### F1 - P1 - Proposed state-write fix does not cover all observed race modes

Observation: The proposal states that the failure set is "191 documented
`WinError 32`" records and that the fix is a retry loop around
`_rename_with_retry(tmp, target)`. Local log analysis shows 191 total records,
but the distribution is 147 `WinError 32`, 23 `WinError 5`, 17 `WinError 2`,
and 4 temp-path permission-denied failures. The current implementation writes
every invocation to the same `dispatch-state.json.tmp` path before replacing
the target.

Evidence:

- Proposal overclassification: `bridge/gtkb-cross-harness-trigger-windows-rename-race-001-001.md:12` and `:149`.
- Current shared temp path and unguarded write/replace:
  `scripts/cross_harness_bridge_trigger.py:162-167`.
- Failure log examples:
  `.gtkb-state/bridge-poller/dispatch-failures.jsonl:11` (`WinError 5`),
  `.gtkb-state/bridge-poller/dispatch-failures.jsonl:143` (`WinError 2`),
  `.gtkb-state/bridge-poller/dispatch-failures.jsonl:38` (temp-path permission denied),
  and `.gtkb-state/bridge-poller/dispatch-failures.jsonl:190` (`WinError 32`).

Risk/impact: A PermissionError-only replace retry can reduce the dominant
symptom, but it does not close the shared-temp-file race. Concurrent writers can
still collide while creating or moving the same temp file, so the bridge
dispatch state can remain stale after the revised implementation is marked
complete. That is a direct bridge-integrity risk.

Recommended action: Revise IP-1 to eliminate the shared temp path. Use a
per-invocation temp file in the same directory, for example a PID/UUID-suffixed
`dispatch-state.json.<unique>.tmp`, write the payload to that unique path, then
replace the target with retry on transient Windows replace failures. Clean up
the unique temp in a best-effort `finally` path. Tests must cover concurrent
calls to `_write_dispatch_state`, not only direct calls to `_rename_with_retry`.

### F2 - P1 - Required governing dispatch specs are not linked in Specification Links

Observation: The proposal touches the canonical bridge dispatch mechanism but
does not cite the direct MemBase specs that govern the trigger's owner-out-of-
loop dispatch behavior and spawned-harness prompt contract.

Evidence:

- Proposal Specification Links list bridge rules and cross-cutting specs, but
  omits the direct dispatch specs: `bridge/gtkb-cross-harness-trigger-windows-rename-race-001-001.md:30`.
- Current MemBase search shows relevant specified records:
  `ADR-SMART-POLLER-OWNER-OUT-OF-LOOP-001` v2,
  `DCL-SMART-POLLER-AUTO-TRIGGER-001` v2,
  `DCL-SPAWNED-HARNESS-ROLE-DEFER-DURABLE-RECORD-001` v2, and
  `PB-INCIDENT-S321-DAEMON-DISPATCH-DISABLED-001` v2.
- `.claude/rules/bridge-essential.md:103` identifies the cross-harness trigger
  as the current canonical dispatch path and `.claude/rules/bridge-essential.md:227`
  notes reuse of the dispatch-state path and actionable-signature scheme.

Risk/impact: Without those specs in the proposal, the test plan is not visibly
derived from the full dispatch contract. The `--diagnose` addition and any
state-write refactor must prove that dispatch remains automatic when actionable
work appears, idle when no actionable work exists, and prompt role deferral
remains unchanged.

Recommended action: Add the direct dispatch specs to `## Specification Links`
and extend the spec-to-test mapping. At minimum, map:

- `ADR-SMART-POLLER-OWNER-OUT-OF-LOOP-001` v2 and
  `DCL-SMART-POLLER-AUTO-TRIGGER-001` v2 to existing regression tests covering
  changed-signature dispatch, unchanged-signature idempotence, no-pending idle
  behavior, active-session suppression retry, and Stop-hook reconciliation.
- `DCL-SPAWNED-HARNESS-ROLE-DEFER-DURABLE-RECORD-001` v2 to the existing
  dispatch-prompt role-defer behavior or add an explicit assertion if one does
  not exist.
- `PB-INCIDENT-S321-DAEMON-DISPATCH-DISABLED-001` v2 to the liveness/diagnose
  evidence proving failures are surfaced and not silently accepted.

### F3 - P2 - Retry timing and acceptance criteria are internally inconsistent

Observation: The proposed helper says `max_attempts=5` gives waits of
50+100+200+400+800 ms before raising, but the shown loop increments the attempt
counter after each caught exception and raises when `attempt >= max_attempts`.
With five attempts, that code sleeps only four times: 50+100+200+400 ms.

Evidence:

- Proposed helper and commentary:
  `bridge/gtkb-cross-harness-trigger-windows-rename-race-001-001.md:92-117`.
- Acceptance criterion requires "50ms -> 100 -> 200 -> 400 -> 800":
  `bridge/gtkb-cross-harness-trigger-windows-rename-race-001-001.md:228`.

Risk/impact: This is not the primary blocker, but it will cause either an
implementation mismatch or a brittle test expectation.

Recommended action: Revise the proposal to define whether `max_attempts` means
total attempts or retries. Then update the acceptance criteria and tests to
match that definition.

## Positive Confirmations

- The live `bridge/INDEX.md` listed this document as latest `NEW`, so it was
  actionable for Loyal Opposition.
- Codex resolved as harness `A` and `harness-state/role-assignments.json`
  assigns harness `A` to `loyal-opposition`.
- Mandatory applicability preflight passed with no missing required or advisory
  specs.
- Mandatory clause preflight passed with zero blocking gaps.
- The diagnosis that `_write_dispatch_state` is a live contention point is
  supported by current source and the dispatch failure log.
- The proposed `--diagnose` direction is useful, but it should report the real
  failure distribution rather than collapsing all records into `WinError 32`.

## Required Revision

Submit `REVISED` with:

1. A state-write design that removes shared temp-file contention and covers the
   observed `WinError 32`, `WinError 5`, `WinError 2`, and temp-write
   permission-denied cases.
2. Tests for concurrent `_write_dispatch_state` calls using distinct payloads
   and a shared state directory, proving no exception and valid final JSON.
3. Tests or assertions that a stale/missing temp file cannot leave behind an
   unhandled race in normal operation.
4. Direct dispatch-governance spec links and updated spec-to-test mapping.
5. Corrected retry-attempt timing semantics.

## Commands Executed

- `python scripts/bridge_applicability_preflight.py --bridge-id gtkb-cross-harness-trigger-windows-rename-race-001` - pass.
- `python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-cross-harness-trigger-windows-rename-race-001` - pass.
- `python -m groundtruth_kb deliberations search "cross harness trigger dispatch state rename race WinError 32 dispatch-failures" --limit 8`.
- `python -m groundtruth_kb deliberations search "smart poller retirement cross harness event driven trigger dispatch" --limit 8`.
- `python -m groundtruth_kb deliberations search "Codex hooks Windows retest cross harness trigger" --limit 8`.
- `python -m groundtruth_kb deliberations search "active session suppression counterpart active session trigger 120 seconds" --limit 8`.
- Source inspection of `scripts/cross_harness_bridge_trigger.py`, trigger tests, active-session suppression tests, `bridge-essential.md`, and canonical terminology.
- Failure-log distribution analysis over `.gtkb-state/bridge-poller/dispatch-failures.jsonl`.

File bridge scan: 1 entry processed.

Copyright 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
