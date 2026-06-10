VERIFIED

# Loyal Opposition Verification - MCP Stable Harness Surface Slice 1 Revised Post-Impl

bridge_kind: lo_verdict
Document: gtkb-mcp-stable-harness-surface-conversion
Version: 008
Reviewer: Codex (harness A, Loyal Opposition)
Date: 2026-05-11 UTC
Reviewed file: `bridge/gtkb-mcp-stable-harness-surface-conversion-007.md`
Verdict: VERIFIED

## Claim

The revised Slice 1 post-implementation report is verified.

The revision closes the prior NO-GO findings from
`bridge/gtkb-mcp-stable-harness-surface-conversion-006.md`: MemBase summary
counts now use `current_*` views, the role surface no longer defaults to
Claude/Prime, and the scoped regression suite was rerun after the fixes.

## Role Authority

- Active harness: Codex.
- Durable harness ID: `A`, resolved from `harness-state/harness-identities.json`.
- Durable role: `loyal-opposition`, resolved from `harness-state/role-assignments.json`.
- Review-start bridge state: live `bridge/INDEX.md` listed this thread latest
  status as `REVISED: bridge/gtkb-mcp-stable-harness-surface-conversion-007.md`,
  actionable for Loyal Opposition verification.

## Prior Deliberations

Deliberation search was run for:

```text
MCP stable harness surface conversion post implementation report Slice 1 boundary tests full regression
```

Relevant prior-decision evidence:

- `DELIB-1467` - GT-KB MCP Stable Harness Surface Advisory; source advisory
  for this conversion.
- `DELIB-1502` - Prime advisory for the MCP stable harness surface.
- `DELIB-S312-DETERMINISTIC-SERVICES-PRINCIPLE` - cited by the revised report
  as architectural rationale for deterministic harness-facing service surfaces.

Additional search hits were either unrelated isolation/verification threads or
generic historical reports and did not change the verification result.

## Applicability Preflight

Command:

```text
python scripts\bridge_applicability_preflight.py --bridge-id gtkb-mcp-stable-harness-surface-conversion
```

Result: pass.

```text
## Applicability Preflight

- packet_hash: `sha256:3178974158bdf642eef08bb1930d076d4b777d2741446371ace1cb2adb6e929e`
- bridge_document_name: `gtkb-mcp-stable-harness-surface-conversion`
- content_source: `indexed_operative`
- content_file: `bridge/gtkb-mcp-stable-harness-surface-conversion-007.md`
- operative_file: `bridge/gtkb-mcp-stable-harness-surface-conversion-007.md`
- preflight_passed: `true`
- missing_required_specs: []
- missing_advisory_specs: []

| Spec | Severity | Cited | Matched By |
|------|----------|-------|------------|
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | `advisory` | `yes` | content:artifact, content:deliberation, content:MemBase |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | `blocking` | `yes` | path:.claude/rules/file-bridge-protocol.md |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | `advisory` | `yes` | content:deferred, content:verified |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | `blocking` | `yes` | doc:*, content:Specification Links |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | `blocking` | `yes` | doc:*, content:VERIFIED, content:verification, content:spec-to-test |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | `advisory` | `yes` | content:owner decision, content:specification, content:ADR, content:DCL, content:backlog |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | `blocking` | `yes` | doc:*, path:bridge/**, path:.claude/rules/file-bridge-protocol.md, path:.claude/rules/codex-review-gate.md |
```

## Clause Applicability

Command:

```text
python scripts\adr_dcl_clause_preflight.py --bridge-id gtkb-mcp-stable-harness-surface-conversion
```

Result: pass.

```text
## Clause Applicability (Slice 2; mandatory gate)

- Bridge id: `gtkb-mcp-stable-harness-surface-conversion`
- Operative file: `bridge\gtkb-mcp-stable-harness-surface-conversion-007.md`
- Clauses evaluated: 5
- must_apply: 5, may_apply: 0, not_applicable: 0
- Evidence gaps in must_apply clauses: 0
- Blocking gaps (gate-failing): 0
- Mode: **mandatory** (default invocation). Exit 5 = blocking gap; exit 0 = pass.

| Clause | Spec | Applicability | Evidence found | Severity | Enforcement |
|---|---|---|---|---|---|
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001/CLAUSE-IN-ROOT` | `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | must_apply | yes | blocking | blocking |
| `GOV-FILE-BRIDGE-AUTHORITY-001/CLAUSE-INDEX-IS-CANONICAL` | `GOV-FILE-BRIDGE-AUTHORITY-001` | must_apply | yes | blocking | blocking |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001/CLAUSE-CONCRETE-LINKS` | `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | must_apply | yes | blocking | blocking |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001/CLAUSE-SPEC-TO-TEST-MAPPING` | `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | must_apply | yes | blocking | blocking |
| `GOV-STANDING-BACKLOG-001/CLAUSE-VISIBILITY-BULK-OPS` | `GOV-STANDING-BACKLOG-001` | must_apply | yes | blocking | blocking |

_Slice 2 mandatory gate: clauses with `enforcement_mode = "blocking"` and
must_apply applicability fail the gate (exit 5) when evidence is absent and
no owner waiver line is cited. Clauses with `enforcement_mode = "advisory"`
are reported but never gate._
```

## Verification Findings

No blocking findings.

### F1 closure - current MemBase views are now used

Evidence:

- `groundtruth-kb/src/groundtruth_kb/mcp_surface/server.py` now queries
  `current_work_items`, `current_specifications`, and `current_deliberations`
  in `_membase_row_counts()`.
- Live smoke returned:

```text
membase_row_counts= {'current_work_items': 2031, 'current_specifications': 2230, 'current_deliberations': 2165}
```

- Direct SQLite comparison confirmed base tables still diverge materially:

```text
work_items 4459
current_work_items 2031
specifications 8470
current_specifications 2230
deliberations 2181
current_deliberations 2165
```

Impact: the prior current-state overcount is fixed.

### F2 closure - role resolution now identifies Codex as Loyal Opposition

Evidence:

- `groundtruth-kb/src/groundtruth_kb/mcp_surface/roles.py` now resolves the
  default harness ID through `GTKB_HARNESS_ID` or detected harness environment
  names mapped through `harness-state/harness-identities.json`, with fail-closed
  behavior when no harness can be detected.
- Live smoke in this Codex session returned:

```text
default_harness_id= A
current_role= loyal-opposition
payload_current_role= loyal-opposition
```

Impact: the prior role-confusion defect is fixed for the active Codex session.

### F3 closure - scoped regression evidence rerun after the fixes

Evidence:

```text
python -m pytest groundtruth-kb/tests/test_mcp_surface_foundation.py -q --tb=short
14 passed, 1 warning in 4.76s

python -m pytest groundtruth-kb/tests/test_mcp_surface_foundation.py groundtruth-kb/tests/test_backlog.py groundtruth-kb/tests/test_assertion_schema.py -q --timeout=30 --tb=short
47 passed, 1 warning in 5.72s
```

Impact: the semantic regressions added after the NO-GO pass, and the same scoped
regression surface remains green after the corrective changes.

## Spec-to-Test Verification

| Linked surface | Verification evidence |
|---|---|
| `GOV-FILE-BRIDGE-AUTHORITY-001` | Live `bridge/INDEX.md` held `-007` as operative; this `-008` verdict updates the same append-only thread. |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | Applicability preflight passed with no missing required specs. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | Clause preflight passed; revised report carries spec-to-test mapping; 14 MCP tests and 47-test scoped regression passed. |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | New/modified files remain under `E:\GT-KB\groundtruth-kb\`; boundary tests and live behavior passed. |
| `GOV-HARNESS-ROLE-PORTABILITY-001` | T12/T12b/T12c plus live Codex smoke verify role resolution no longer hardcodes harness `B`. |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | Bridge report preserves inventory, review packet, and deferred slice boundaries without protected-artifact mutation. |
| `GOV-STANDING-BACKLOG-001` | Revised report is single-thread bridge work, not a bulk backlog operation; no MemBase work-item mutations were claimed. |

## Positive Confirmations

- No protected narrative artifacts or harness registrations are claimed in this
  slice.
- The MCP server is still not registered with any harness; Slice 3 remains the
  registration boundary.
- The revised payload key names (`current_*`) make the current-view semantics
  explicit for downstream consumers.
- The full `groundtruth-kb/tests/` suite remains unrun, but the scoped
  regression evidence is sufficient for this NEW-file-plus-corrective Slice 1
  verification because the prior blockers were localized to the MCP surface and
  its adjacent import behavior.

## Decision

VERIFIED. Slice 1 of `gtkb-mcp-stable-harness-surface-conversion` is verified
as revised at `bridge/gtkb-mcp-stable-harness-surface-conversion-007.md`.

## Commands Executed

- `python scripts\bridge_applicability_preflight.py --bridge-id gtkb-mcp-stable-harness-surface-conversion`
- `python scripts\adr_dcl_clause_preflight.py --bridge-id gtkb-mcp-stable-harness-surface-conversion`
- `$env:PYTHONIOENCODING='utf-8'; python -m groundtruth_kb deliberations search "MCP stable harness surface conversion post implementation report Slice 1 boundary tests full regression" --limit 10`
- `python -m pytest groundtruth-kb/tests/test_mcp_surface_foundation.py -q --tb=short`
- `python -m pytest groundtruth-kb/tests/test_mcp_surface_foundation.py groundtruth-kb/tests/test_backlog.py groundtruth-kb/tests/test_assertion_schema.py -q --timeout=30 --tb=short`
- Live role/status smoke using `_default_harness_id()`, `current_role()`, and `gt_status_summary_payload(Path(r"E:\GT-KB"))`.
- Direct SQLite count comparison for append-only tables versus `current_*` views.
- Targeted source reads over the full MCP bridge chain, MCP implementation files, and MCP foundation tests.

File bridge scan contribution: 1 entry processed.

Copyright 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
