GO

Document: gtkb-startup-relay-pretooluse-read-exemption
Reviewed-File: bridge/gtkb-startup-relay-pretooluse-read-exemption-002.md
Reviewer: Codex Loyal Opposition, harness A
Date: 2026-05-16 UTC

# Loyal Opposition Review - Startup Relay PreToolUse Read Exemption

## Verdict Summary

GO.

The revised proposal resolves the initial filing's clause-evidence gap. Live
applicability and clause preflights pass against
`bridge/gtkb-startup-relay-pretooluse-read-exemption-002.md`, and the requested
implementation is bounded to the receiver-side guard plus targeted regression
tests.

The current code confirms the defect: `guard_tool_use()` returns the
`GTKB-STARTUP-INPUT-GATE` block immediately when
`startup_response_pending` is true, before inspecting the tool payload, so it
cannot allow the one read-only startup disclosure cache read that the relay
contract asks the assistant to perform.

## Prior Deliberations

Deliberation CLI search was attempted but could not run in this sandbox because
the local CLI import failed on missing dependency `click`. I therefore used the
proposal's cited deliberation evidence and repository-local text search over
bridge/rule/memory surfaces.

Relevant cited deliberations:

- `DELIB-2078` - owner approval for the init-keyword startup disclosure relay
  specification.
- `DELIB-1536` - review of SessionStart formalization and the init-keyword
  contract.
- `DELIB-1530` / `DELIB-1531` - startup symmetry reviews.
- `DELIB-1075` / `DELIB-1083` - prior startup token consumption and premature
  wrap-up feedback.

No contrary prior decision was found in the searched local surfaces.

## Applicability Preflight

- packet_hash: `sha256:6be4ad9d8db6c674aab2a79575e6fb79089c15d359834aef6403e44ca37b59f9`
- bridge_document_name: `gtkb-startup-relay-pretooluse-read-exemption`
- content_source: `indexed_operative`
- content_file: `bridge/gtkb-startup-relay-pretooluse-read-exemption-002.md`
- operative_file: `bridge/gtkb-startup-relay-pretooluse-read-exemption-002.md`
- preflight_passed: `true`
- missing_required_specs: []
- missing_advisory_specs: []

| Spec | Severity | Cited | Matched By |
|------|----------|-------|------------|
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | `advisory` | `yes` | content:artifact, content:deliberation |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | `advisory` | `yes` | content:blocked, content:verified |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | `blocking` | `yes` | doc:*, content:Specification Links, content:implementation proposal |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | `blocking` | `yes` | doc:*, content:VERIFIED, content:verification |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | `advisory` | `yes` | content:owner decision, content:requirement, content:specification, content:ADR, content:DCL, content:work item, content:backlog |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | `blocking` | `yes` | doc:*, path:bridge/** |

## Clause Applicability

- Bridge id: `gtkb-startup-relay-pretooluse-read-exemption`
- Operative file: `bridge\gtkb-startup-relay-pretooluse-read-exemption-002.md`
- Clauses evaluated: 5
- must_apply: 4, may_apply: 1, not_applicable: 0
- Evidence gaps in must_apply clauses: 0
- Blocking gaps (gate-failing): 0
- Mode: mandatory

| Clause | Spec | Applicability | Evidence found | Severity | Enforcement |
|---|---|---|---|---|---|
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001/CLAUSE-IN-ROOT` | `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | may_apply | - | blocking | blocking |
| `GOV-FILE-BRIDGE-AUTHORITY-001/CLAUSE-INDEX-IS-CANONICAL` | `GOV-FILE-BRIDGE-AUTHORITY-001` | must_apply | yes | blocking | blocking |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001/CLAUSE-CONCRETE-LINKS` | `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | must_apply | yes | blocking | blocking |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001/CLAUSE-SPEC-TO-TEST-MAPPING` | `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | must_apply | yes | blocking | blocking |
| `GOV-STANDING-BACKLOG-001/CLAUSE-VISIBILITY-BULK-OPS` | `GOV-STANDING-BACKLOG-001` | must_apply | yes | blocking | blocking |

## Findings

No blocking findings.

## Implementation Conditions

- Keep implementation confined to `scripts/workstream_focus.py` and
  `platform_tests/hooks/test_workstream_focus.py`.
- The exception must be exact-path, read-only, and harness-cache scoped. It must
  reject shell chaining, mutation verbs, additional paths, and non-cache reads
  while `startup_response_pending` remains true.
- Preserve the follow-up clearing behavior in
  `_clear_startup_response_pending_for_followup()`.
- The implementation report must include targeted pytest and ruff evidence and
  explicit negative tests proving non-cache or mutating tool use remains blocked.

File bridge scan: 1 entry processed.

---

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
