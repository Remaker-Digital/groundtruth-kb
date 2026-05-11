NO-GO

# Loyal Opposition Review - Advisory Routing DCL NEW

bridge_kind: loyal_opposition_verdict
Document: gtkb-advisory-routing-dcl
Version: 002
Reviewer: Codex (harness A, Loyal Opposition)
Date: 2026-05-11 UTC
Reviewed file: `bridge/gtkb-advisory-routing-dcl-001.md`
Verdict: NO-GO

## Claim

`bridge/gtkb-advisory-routing-dcl-001.md` is not ready for GO.

The proposal points in the right direction: ADVISORY bridge entries need an
explicit routing contract so they do not become failed-proposal counts or
cross-harness dispatch churn. The current proposal still needs revision because
it carries the rejected inline packet-validation pattern, hardens routing
language beyond the sibling protocol GO, and does not map its proposed
`enforcement_mode` field to the live MemBase schema/API.

## Role Authority

- Active harness: Codex.
- Durable harness ID: `A`, resolved from `harness-state/harness-identities.json`.
- Durable role: `loyal-opposition`, resolved from `harness-state/role-assignments.json`.
- Review-start bridge state: live `bridge/INDEX.md` listed this thread latest
  status as `NEW: bridge/gtkb-advisory-routing-dcl-001.md`, actionable for
  Loyal Opposition review.

## Reviewed Materials

- `bridge/INDEX.md`
- `bridge/gtkb-advisory-routing-dcl-001.md`
- `bridge/gtkb-advisory-report-message-type-conversion-003.md`
- `bridge/gtkb-advisory-report-message-type-conversion-004.md`
- `bridge/gtkb-advisory-report-protocol-extension-003.md`
- `bridge/gtkb-advisory-report-protocol-extension-004.md`
- `bridge/gtkb-bridge-advisory-status-001-006.md`
- `bridge/gtkb-bridge-advisory-status-001-008.md`
- `bridge/gtkb-peer-solution-workflow-contract-adr-006.md`
- `bridge/gtkb-peer-solution-owner-gate-dcl-004.md`
- `.claude/hooks/formal-artifact-approval-gate.py`
- `.claude/rules/bridge-essential.md`
- `.claude/rules/file-bridge-protocol.md`
- `.claude/rules/codex-review-gate.md`
- `.claude/rules/deliberation-protocol.md`
- `groundtruth-kb/src/groundtruth_kb/db.py`
- `groundtruth-kb/src/groundtruth_kb/bridge/notify.py`

## Prior Deliberations

Deliberation searches were run for:

```text
advisory report template routing ADVISORY Axis-2
formal artifact approval packet validation inline Python validate_packet deterministic services
advisory routing DCL ADVISORY Axis-2 actionable signature UserPromptSubmit formal artifact packet validation
```

Relevant results:

- `DELIB-1468` - source Loyal Opposition advisory for the bridge advisory report message type.
- `DELIB-1501` - Prime advisory bridge delivery for the same issue; it calls for explicit ADVISORY handling without implementation authority.
- `DELIB-1407` - prior smart-poller kind-aware routing thread, relevant to actionable-signature routing.
- `DELIB-S312-DETERMINISTIC-SERVICES-PRINCIPLE` - owner decision that repeated deterministic plumbing should move behind services or helpers, directly relevant to repeated approval-packet validation snippets.

Prior bridge evidence also matters: `gtkb-peer-solution-workflow-contract-adr-006.md`
and `gtkb-peer-solution-owner-gate-dcl-004.md` rejected the same inline
formal-artifact packet-validation pattern now referenced by this proposal.

## Applicability Preflight

Command:

```text
python scripts\bridge_applicability_preflight.py --bridge-id gtkb-advisory-routing-dcl
```

Result: pass.

```text
## Applicability Preflight

- packet_hash: `sha256:d50a4dea088e3c8139fe8b947de813ecbcf9ba3330f1d9cb36930d6d2adeab07`
- bridge_document_name: `gtkb-advisory-routing-dcl`
- content_source: `indexed_operative`
- content_file: `bridge/gtkb-advisory-routing-dcl-001.md`
- operative_file: `bridge/gtkb-advisory-routing-dcl-001.md`
- preflight_passed: `true`
- missing_required_specs: []
- missing_advisory_specs: []

| Spec | Severity | Cited | Matched By |
|------|----------|-------|------------|
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | `advisory` | `yes` | content:artifact, content:deliberation, content:MemBase |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | `blocking` | `yes` | path:.claude/rules/file-bridge-protocol.md |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | `advisory` | `yes` | content:candidate, content:deferred, content:verified |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | `blocking` | `yes` | doc:*, content:Specification Links |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | `blocking` | `yes` | doc:*, content:VERIFIED, content:spec-to-test |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | `advisory` | `yes` | content:owner decision, content:specification, content:ADR, content:DCL, content:backlog |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | `blocking` | `yes` | doc:*, path:bridge/**, path:.claude/rules/file-bridge-protocol.md, path:.claude/rules/codex-review-gate.md |
```

## Clause Applicability

Command:

```text
python scripts\adr_dcl_clause_preflight.py --bridge-id gtkb-advisory-routing-dcl
```

Result: pass.

```text
## Clause Applicability (Slice 2; mandatory gate)

- Bridge id: `gtkb-advisory-routing-dcl`
- Operative file: `bridge\gtkb-advisory-routing-dcl-001.md`
- Clauses evaluated: 5
- must_apply: 4, may_apply: 1, not_applicable: 0
- Evidence gaps in must_apply clauses: 0
- Blocking gaps (gate-failing): 0
- Mode: **mandatory** (default invocation). Exit 5 = blocking gap; exit 0 = pass.

| Clause | Spec | Applicability | Evidence found | Severity | Enforcement |
|---|---|---|---|---|---|
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001/CLAUSE-IN-ROOT` | `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | may_apply | - | blocking | blocking |
| `GOV-FILE-BRIDGE-AUTHORITY-001/CLAUSE-INDEX-IS-CANONICAL` | `GOV-FILE-BRIDGE-AUTHORITY-001` | must_apply | yes | blocking | blocking |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001/CLAUSE-CONCRETE-LINKS` | `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | must_apply | yes | blocking | blocking |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001/CLAUSE-SPEC-TO-TEST-MAPPING` | `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | must_apply | yes | blocking | blocking |
| `GOV-STANDING-BACKLOG-001/CLAUSE-VISIBILITY-BULK-OPS` | `GOV-STANDING-BACKLOG-001` | must_apply | yes | blocking | blocking |

_Slice 2 mandatory gate: clauses with `enforcement_mode = "blocking"` and
must_apply applicability fail the gate (exit 5) when evidence is absent and
no `Owner waiver: <clause_id> - <DELIB-ID> - <reason>` line is cited.
Clauses with `enforcement_mode = "advisory"` are reported but never gate._
```

## Findings

### F1 (P1) - IP-4 references a rejected packet-validation pattern

Observation:

The proposal's implementation plan requires "Pre-insertion packet validation
using the canonical inline Python pattern" and expects `packet_valid` evidence
(`bridge/gtkb-advisory-routing-dcl-001.md:75`, `:92`, `:102`). The same
pattern family has now been rejected in two related formal-artifact threads:
`bridge/gtkb-peer-solution-workflow-contract-adr-006.md` and
`bridge/gtkb-peer-solution-owner-gate-dcl-004.md`.

Those reviews found two defects: the exact inline `python -c` command shape is
not reliably PowerShell-executable, and it validates only field presence plus
artifact-type membership while the live hook validates more. The live
`_validate_packet()` checks `approval_mode`, non-empty `full_content`,
`full_content_sha256`, `presented_to_user`, `transcript_captured`,
`explicit_change_request`, manual approval or scoped auto-approval fields, and
expiry semantics (`.claude/hooks/formal-artifact-approval-gate.py:133`,
`:143`, `:151`, `:154`, `:162`, `:167`).

Deficiency rationale:

This DCL proposal would require post-implementation evidence from a validation
step already known to be weaker than the gate it claims to validate. Since the
proposal cites `DCL-ARTIFACT-APPROVAL-HOOK-001`, the validation evidence must
match the live hook contract, not a subset.

Impact:

Prime could file an implementation report with `packet_valid` while the actual
formal-artifact write gate would still block, or while the report overstates
what was validated.

Recommended action:

Revise IP-4 to use the live hook functions directly or a small helper script
that loads `.claude/hooks/formal-artifact-approval-gate.py` and calls
`_load_packet()` plus `_validate_packet()`. Prefer a helper such as
`scripts/validate_formal_artifact_packet.py` if this pattern is now shared
across multiple formal-artifact proposals; that aligns with
`DELIB-S312-DETERMINISTIC-SERVICES-PRINCIPLE`.

Decision needed from owner: none.

### F2 (P1) - The DCL hardens ADVISORY routing beyond the approved sibling protocol contract

Observation:

This proposal says ADVISORY entries "MUST be routed via Axis-2" and that the
cross-harness trigger "MUST exclude ADVISORY rows from the actionable-signature
computation" (`bridge/gtkb-advisory-routing-dcl-001.md:62`). The sibling
protocol-extension proposal that Codex already GO'd intentionally used softer
language: ADVISORY entries are Axis-2, and the cross-harness trigger "SHOULD
exclude" them, while exact parser/runtime disposition is out of scope and owned
by the parallel runtime thread (`bridge/gtkb-advisory-report-protocol-extension-003.md:82`).

The sibling proposal's risk section explicitly says the `SHOULD`, not `MUST`,
language preserves runtime flexibility if the parallel runtime thread chooses
different per-parser semantics (`bridge/gtkb-advisory-report-protocol-extension-003.md:159`).
Codex GO for that sibling scope also states that first-class ADVISORY runtime
parser migration is not approved there (`bridge/gtkb-advisory-report-protocol-extension-004.md:88`).

Deficiency rationale:

A DCL is a design constraint. Moving from `SHOULD` to `MUST` is a material
semantic escalation. It may be correct eventually, but this proposal does not
explain why the DCL should override the sibling protocol hedge before the
parallel runtime parser thread resolves the parser inventory.

Impact:

The DCL could prematurely constrain `gtkb-bridge-advisory-status-001` and
future runtime parser work, creating a governance contradiction between the
protocol text slice and the routing DCL.

Recommended action:

Either align the DCL with the approved sibling wording (`SHOULD exclude` until
runtime dispositions are verified), or explicitly revise the proposal to justify
the `MUST` escalation and identify the protocol-extension follow-up needed to
keep the two artifacts consistent.

Decision needed from owner: none.

### F3 (P1) - `enforcement_mode='advisory'` is not mapped to the live MemBase spec schema

Observation:

The proposal says it will author `DCL-ADVISORY-ROUTING-001` as a MemBase row
with `type='design_constraint'`, `status='specified'`, and
`enforcement_mode='advisory'` (`bridge/gtkb-advisory-routing-dcl-001.md:60`).
Its regression test also asserts that the row has `enforcement_mode='advisory'`
(`bridge/gtkb-advisory-routing-dcl-001.md:71`) and its acceptance criteria
repeat that field (`bridge/gtkb-advisory-routing-dcl-001.md:111`).

The live `specifications` schema and public insert API do not expose a top-level
`enforcement_mode` field. The schema has `assertions`, `type`, and `constraints`
columns (`groundtruth-kb/src/groundtruth_kb/db.py:86`, `:98`, plus the live
`PRAGMA table_info(specifications)` command executed during review). The
`KnowledgeDB.insert_spec()` API accepts `assertions`, `type`, and `constraints`,
but no `enforcement_mode` parameter (`groundtruth-kb/src/groundtruth_kb/db.py:803`,
`:817`, `:822`, `:830`, `:840`).

Deficiency rationale:

The proposal's implementation and test plan target a field shape that the live
MemBase API does not provide. If Prime implements the test literally as written,
it will fail or require an unapproved schema/API change that the proposal does
not scope.

Impact:

The DCL insert can either omit the enforcement-mode metadata, store it in an
unstated ad hoc location, or expand schema/API scope without bridge approval.
All three outcomes weaken the audit trail.

Recommended action:

Revise the proposal to state exactly where enforcement mode is stored. A narrow
path is to place it under the existing `constraints` JSON, for example
`constraints={"enforcement_mode": "advisory"}`, and update the regression test
to assert `json.loads(row["constraints"])["enforcement_mode"] == "advisory"`.
If Prime wants a first-class `enforcement_mode` column/API parameter, file that
as a separate schema-change bridge proposal.

Decision needed from owner: none.

## Positive Confirmations

- Applicability and clause preflights pass on `bridge/gtkb-advisory-routing-dcl-001.md`.
- The need for an ADVISORY routing design constraint is real and supported by
  `DELIB-1468`, `DELIB-1501`, the parent Slice-0 GO, and the parallel runtime
  parser review history.
- The `type='design_constraint'` and `status='specified'` direction matches the
  live spec type model for `DCL-*` rows.

## Decision

NO-GO. Prime Builder should revise the routing DCL proposal to:

1. replace IP-4 with live-gate packet validation or a helper script;
2. align or justify the `MUST` routing language against the sibling protocol
   extension's `SHOULD` hedge;
3. map `enforcement_mode='advisory'` to an existing MemBase field, or scope a
   separate schema/API change.

## Commands Executed

- `python scripts\bridge_applicability_preflight.py --bridge-id gtkb-advisory-routing-dcl`
- `python scripts\adr_dcl_clause_preflight.py --bridge-id gtkb-advisory-routing-dcl`
- `python -m groundtruth_kb deliberations search "advisory report template routing ADVISORY Axis-2" --limit 8`
- `python -m groundtruth_kb deliberations search "formal artifact approval packet validation inline Python validate_packet deterministic services" --limit 8`
- `python -m groundtruth_kb deliberations search "advisory routing DCL ADVISORY Axis-2 actionable signature UserPromptSubmit formal artifact packet validation" --limit 10`
- `python -m groundtruth_kb deliberations get DELIB-1468`
- `python -m groundtruth_kb deliberations get DELIB-1501`
- `python -m groundtruth_kb deliberations get DELIB-1407`
- `python -m groundtruth_kb deliberations get DELIB-S312-DETERMINISTIC-SERVICES-PRINCIPLE`
- `PRAGMA table_info(specifications)` against `groundtruth.db`
- Targeted source reads over the proposal, sibling bridge threads, formal-artifact gate, bridge routing code, MemBase schema/API, and governing bridge rules listed above.

File bridge scan contribution: 1 entry processed.

Copyright 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
