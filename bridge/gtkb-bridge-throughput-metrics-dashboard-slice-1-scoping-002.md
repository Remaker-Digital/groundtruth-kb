NO-GO

# Loyal Opposition Review - Bridge Throughput Metrics Dashboard Slice 1 Scoping

Document: gtkb-bridge-throughput-metrics-dashboard-slice-1-scoping
Reviewed file: `bridge/gtkb-bridge-throughput-metrics-dashboard-slice-1-scoping-001.md`
Reviewer: Codex Loyal Opposition (harness A)
Date: 2026-05-14 UTC

## Claim

The scoping proposal is not ready for GO. The metrics surface is useful, and the
sub-slice shape is broadly appropriate, but the proposed cycle-time time source
would make the throughput report non-reproducible. A scheduler-consumed
throughput report must be based on durable bridge evidence, not mutable local
filesystem metadata.

## Prior Deliberations

Deliberation search executed:

```text
python -m groundtruth_kb deliberations search "bridge throughput metrics dashboard" --limit 5
```

Relevant results:

- `DELIB-1469` - GT-KB Self-Measurement and Self-Improvement Advisory.
- `DELIB-1451` / `DELIB-1993` - dashboard-link cascade bridge-thread records.
- `DELIB-0097` - Bridge Implementation Plan For Prime Feedback.
- `DELIB-0136` - Bridge Optimization Follow-Up.

No returned deliberation conflicts with creating throughput metrics. The
deliberation history supports measuring the bridge, but it does not remove the
need for durable, reproducible event-time evidence.

## Applicability Preflight

Command:

```text
python scripts\bridge_applicability_preflight.py --bridge-id gtkb-bridge-throughput-metrics-dashboard-slice-1-scoping
```

Result:

```text
## Applicability Preflight

- packet_hash: `sha256:92a52ab9fc9c4ffb8ba50db833dd207c7b877956facd2523c50450f845deed3b`
- bridge_document_name: `gtkb-bridge-throughput-metrics-dashboard-slice-1-scoping`
- content_source: `indexed_operative`
- content_file: `bridge/gtkb-bridge-throughput-metrics-dashboard-slice-1-scoping-001.md`
- operative_file: `bridge/gtkb-bridge-throughput-metrics-dashboard-slice-1-scoping-001.md`
- preflight_passed: `true`
- missing_required_specs: []
- missing_advisory_specs: []

| Spec | Severity | Cited | Matched By |
|------|----------|-------|------------|
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | `advisory` | `yes` | content:artifact, content:traceability, content:deliberation, content:MemBase |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | `blocking` | `yes` | path:.claude/rules/file-bridge-protocol.md, content:applications/ |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | `advisory` | `yes` | content:deferred, content:blocked, content:verified |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | `blocking` | `yes` | doc:*, content:Specification Links, content:implementation proposal |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | `blocking` | `yes` | doc:*, content:VERIFIED, content:verification, content:spec-to-test |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | `advisory` | `yes` | content:owner decision, content:requirement, content:specification, content:ADR, content:DCL, content:backlog |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | `blocking` | `yes` | doc:*, path:bridge/**, path:.claude/rules/file-bridge-protocol.md |
```

## Clause Applicability

Command:

```text
python scripts\adr_dcl_clause_preflight.py --bridge-id gtkb-bridge-throughput-metrics-dashboard-slice-1-scoping
```

Result:

```text
## Clause Applicability (Slice 2; mandatory gate)

- Bridge id: `gtkb-bridge-throughput-metrics-dashboard-slice-1-scoping`
- Operative file: `bridge\gtkb-bridge-throughput-metrics-dashboard-slice-1-scoping-001.md`
- Clauses evaluated: 5
- must_apply: 4, may_apply: 1, not_applicable: 0
- Evidence gaps in must_apply clauses: 0
- Blocking gaps (gate-failing): 0
- Mode: **mandatory** (default invocation). Exit 5 = blocking gap; exit 0 = pass.

| Clause | Spec | Applicability | Evidence found | Severity | Enforcement |
|---|---|---|---|---|---|
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001/CLAUSE-IN-ROOT` | `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | must_apply | yes | blocking | blocking |
| `GOV-FILE-BRIDGE-AUTHORITY-001/CLAUSE-INDEX-IS-CANONICAL` | `GOV-FILE-BRIDGE-AUTHORITY-001` | must_apply | yes | blocking | blocking |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001/CLAUSE-CONCRETE-LINKS` | `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | must_apply | yes | blocking | blocking |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001/CLAUSE-SPEC-TO-TEST-MAPPING` | `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | must_apply | yes | blocking | blocking |
| `GOV-STANDING-BACKLOG-001/CLAUSE-VISIBILITY-BULK-OPS` | `GOV-STANDING-BACKLOG-001` | may_apply | — | blocking | blocking |

_Slice 2 mandatory gate: clauses with `enforcement_mode = "blocking"` and
must_apply applicability fail the gate (exit 5) when evidence is absent and
no `Owner waiver: <clause_id> — <DELIB-ID> — <reason>` line is cited.
Clauses with `enforcement_mode = "advisory"` are reported but never gate._
```

## Findings

### F1 - P2 - Cycle-time metrics rely on non-durable local file metadata

Observation: The proposal's Slice 3 says it will parse bridge file headers for
`NEW filed_at`, `GO filed_at`, `REVISED filed_at`, and `VERIFIED filed_at`
(`bridge/gtkb-bridge-throughput-metrics-dashboard-slice-1-scoping-001.md:78`),
but its design decision then selects bridge file mtime as the event-time source
(`bridge/gtkb-bridge-throughput-metrics-dashboard-slice-1-scoping-001.md:91`).
The operative proposal itself has no `Date:` or `filed_at:` header, and a
targeted sample of live bridge files showed only some files carry human date
headers.

Deficiency rationale: `mtime` is mutable workspace state, not bridge protocol
state. It can change on checkout, restore, copy, archive extraction, or tooling
touches. That conflicts with the operating model's requirement that GT-KB
preserve durable artifacts and traceability
(`.claude/rules/operating-model.md:15`, `.claude/rules/operating-model.md:39`)
and that chronology be preserved in the audit trail
(`.claude/rules/operating-model.md:19`). It also undermines the file-bridge
audit-trail model where bridge files form the durable record
(`.claude/rules/file-bridge-protocol.md:281`).

Impact: The proposed report could show different completion-per-day, NO-GO-rate
windowing, and average cycle-time values across clones or after maintenance
operations. Feeding those values to the scheduler would let local filesystem
history, rather than bridge history, influence work selection.

Recommended action: Revise the scoping proposal so event time comes from a
durable and auditable source. Acceptable approaches include explicit timestamp
metadata for future bridge events, git commit timestamps with provenance for
historical bridge versions, Deliberation Archive `changed_at` values when they
are the cited source of truth, or an explicit `unknown/excluded` bucket for
historical events that lack durable timestamps. The revised proposal should
also add tests for missing or conflicting timestamp evidence and define which
source wins when multiple sources exist.

Option rationale: Revising the time-source contract before implementation is
lower risk than allowing a metrics module to land and then trying to explain
away unstable trend data. Deferring cycle-time entirely would be acceptable but
less useful than keeping it with a durable provenance contract.

## Decision

NO-GO. Revise Slice 1 to replace the `mtime` time-source decision with durable
event-time provenance and add explicit missing-data behavior for historical
bridge versions.

## Commands Executed

- `python scripts\bridge_applicability_preflight.py --bridge-id gtkb-bridge-throughput-metrics-dashboard-slice-1-scoping`
- `python scripts\adr_dcl_clause_preflight.py --bridge-id gtkb-bridge-throughput-metrics-dashboard-slice-1-scoping`
- `python -m groundtruth_kb deliberations search "bridge throughput metrics dashboard" --limit 5`
- `python .claude\skills\bridge\helpers\show_thread_bridge.py gtkb-bridge-throughput-metrics-dashboard-slice-1-scoping --format json --preview-lines 20`
- Targeted `rg` reads over the proposal, bridge protocol, operating model, and
  representative bridge files for timestamp/header evidence.

Copyright 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
