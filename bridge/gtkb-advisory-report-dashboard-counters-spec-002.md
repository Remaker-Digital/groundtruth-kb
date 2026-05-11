NO-GO

# Loyal Opposition Review - Advisory Report Dashboard Counters Spec NEW

bridge_kind: loyal_opposition_verdict
Document: gtkb-advisory-report-dashboard-counters-spec
Version: 002
Reviewer: Codex (harness A, Loyal Opposition)
Date: 2026-05-11 UTC
Reviewed file: `bridge/gtkb-advisory-report-dashboard-counters-spec-001.md`
Verdict: NO-GO

## Claim

`bridge/gtkb-advisory-report-dashboard-counters-spec-001.md` is not ready for
GO.

The proposal is right that ADVISORY entries need first-class dashboard counter
semantics and must not be conflated with NO-GO entries. It still needs revision
because its Prime-actionability definition conflicts with the live bridge role
contract, its proposed MemBase type is not in the live specification taxonomy,
and its tests do not prove the declared counter semantics.

## Role Authority

- Active harness: Codex.
- Durable harness ID: `A`, resolved from `harness-state/harness-identities.json`.
- Durable role: `loyal-opposition`, resolved from `harness-state/role-assignments.json`.
- Review-start bridge state: live `bridge/INDEX.md` listed this thread latest
  status as `NEW: bridge/gtkb-advisory-report-dashboard-counters-spec-001.md`,
  actionable for Loyal Opposition review.

## Prior Deliberations

Deliberation search was run for:

```text
advisory dashboard counters Prime actionable VERIFIED ADVISORY no_go_count
```

Relevant results:

- `DELIB-1468` - source Loyal Opposition advisory for the bridge advisory
  report message type.
- `DELIB-1501` - Prime advisory bridge delivery for the same issue.
- `DELIB-1500` - Loyal Opposition review of ADVISORY status/message type.
- `DELIB-0697` and `DELIB-0647` - prior dashboard/lifecycle metrics review
  context.

No result found in this search waives the live Prime Builder actionability
contract or authorizes treating latest `VERIFIED` entries as Prime-actionable
bridge work.

## Applicability Preflight

Command:

```text
python scripts\bridge_applicability_preflight.py --bridge-id gtkb-advisory-report-dashboard-counters-spec
```

Result: pass.

```text
## Applicability Preflight

- packet_hash: `sha256:40db3aff6885471b4fc19afaff4da5821724dcd84502b874236f416a1487cad9`
- bridge_document_name: `gtkb-advisory-report-dashboard-counters-spec`
- content_source: `indexed_operative`
- content_file: `bridge/gtkb-advisory-report-dashboard-counters-spec-001.md`
- operative_file: `bridge/gtkb-advisory-report-dashboard-counters-spec-001.md`
- preflight_passed: `true`
- missing_required_specs: []
- missing_advisory_specs: []

| Spec | Severity | Cited | Matched By |
|------|----------|-------|------------|
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | `advisory` | `yes` | content:artifact, content:deliberation, content:MemBase |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | `blocking` | `yes` | path:.claude/rules/file-bridge-protocol.md |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | `advisory` | `yes` | content:deferred, content:verified |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | `blocking` | `yes` | doc:*, content:Specification Links |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | `blocking` | `yes` | doc:*, content:VERIFIED, content:spec-to-test |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | `advisory` | `yes` | content:owner decision, content:requirement, content:specification, content:ADR, content:DCL, content:backlog |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | `blocking` | `yes` | doc:*, path:bridge/**, path:.claude/rules/file-bridge-protocol.md, path:.claude/rules/codex-review-gate.md |
```

## Clause Applicability

Command:

```text
python scripts\adr_dcl_clause_preflight.py --bridge-id gtkb-advisory-report-dashboard-counters-spec
```

Result: pass.

```text
## Clause Applicability (Slice 2; mandatory gate)

- Bridge id: `gtkb-advisory-report-dashboard-counters-spec`
- Operative file: `bridge\gtkb-advisory-report-dashboard-counters-spec-001.md`
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

### F1 (P1) - `actionable_count_for_prime` conflicts with live bridge actionability rules

Observation:

The proposal defines `actionable_count_for_prime` as entries whose latest status
is `GO`, `NO-GO`, `VERIFIED`, or `ADVISORY`
(`bridge/gtkb-advisory-report-dashboard-counters-spec-001.md:61`).

The live startup/role contract says Prime Builder continuation work includes
latest `GO` or `NO-GO`, and Prime Builder must never process latest
`VERIFIED` entries as actionable queue work (`AGENTS.md:178`,
`AGENTS.md:182`). The system-interface map preserves the same constraint:
"Prime Builder ignores latest NEW/REVISED/VERIFIED as actionable; Loyal
Opposition ignores latest GO/NO-GO as review queue"
(`config/agent-control/system-interface-map.toml:182`).

Deficiency rationale:

Dashboard counter semantics are not neutral labels. If a dashboard reports
latest `VERIFIED` entries as Prime-actionable, it directly contradicts the
role-actionability contract and can drive Prime back into terminal work. If it
places ADVISORY in the same Prime-actionable count, it also blurs an advisory
disposition target with the existing bridge continuation queue.

Impact:

Startup and dashboard surfaces could overstate Prime work, re-open terminal
threads, and undo the protocol distinction this slice is trying to add for
ADVISORY.

Recommended action:

Revise the proposal so `actionable_count_for_prime` covers only latest `GO` and
`NO-GO` entries, or rename/split the metric. Keep `advisory_count` as a
first-class separate metric. If Prime needs an advisory-disposition metric,
define it separately, for example `advisory_disposition_count`, and do not
include latest `VERIFIED`.

Decision needed from owner: none.

### F2 (P1) - Proposed `type='specification'` is outside the live MemBase artifact taxonomy

Observation:

The proposal says `SPEC-ADVISORY-DASHBOARD-COUNTERS-001` will be inserted as a
MemBase row with `type='specification'` and tests that exact value
(`bridge/gtkb-advisory-report-dashboard-counters-spec-001.md:56`,
`:72`). The live `KnowledgeDB.insert_spec()` API defaults `type` to
`requirement`, auto-detects GOV/PB/ADR/DCL prefixes, and documents valid types
as `requirement`, `governance`, `protected_behavior`,
`architecture_decision`, or `design_constraint`
(`groundtruth-kb/src/groundtruth_kb/db.py:818`, `:830`). The formal approval
hook likewise lists valid packet artifact types and does not include
`specification` (`.claude/hooks/formal-artifact-approval-gate.py:75`).

Deficiency rationale:

`SPEC-*` is an identifier family, not a live `type` enum value in the current
MemBase insert API or packet gate. A proposal that requires `type='specification'`
would either fail, require an unscoped enum expansion, or produce approval
packets whose `artifact_type` is ambiguous.

Impact:

Prime could implement tests and packets that cannot pass the live schema/gate,
or create ad hoc handling outside the approved artifact model.

Recommended action:

Revise the proposal to use the current taxonomy, most likely
`type='requirement'` for this `SPEC-*` row and `artifact_type='requirement'` in
the approval packet. If a first-class `specification` type is desired, file a
separate schema/API expansion proposal with tests and packet-gate changes.

Decision needed from owner: none.

### F3 (P2) - The linked surfaces and tests are too weak for dashboard/startup counter semantics

Observation:

The proposal governs dashboard and startup bridge-state counters but does not
cite `config/agent-control/system-interface-map.toml` or
`.claude/rules/bridge-essential.md` in `Specification Links`. Its regression
test asserts that the row exists, enumerates the five counter names, and
mentions display distinction (`bridge/gtkb-advisory-report-dashboard-counters-spec-001.md:70`,
`:73`, `:74`).

Deficiency rationale:

The file bridge protocol requires proposals to cite every relevant governing
surface and says applicability preflight is only a floor, not a ceiling
(`.claude/rules/file-bridge-protocol.md:22`,
`:116`). For this proposal, the live system-interface map and bridge-essential
rule directly constrain actionability, terminal VERIFIED handling, and
cross-harness dispatch semantics.

Impact:

An implementation could pass the proposed MemBase row test while still
miscounting `VERIFIED`, conflating ADVISORY with Prime continuation work, or
omitting a dashboard/startup surface that already reports bridge state.

Recommended action:

Add the missing governing surfaces and strengthen the test plan to prove:
`advisory_count` is distinct from `no_go_count`; latest `VERIFIED` is excluded
from Prime-actionable work; ADVISORY is either a separate disposition metric or
documented non-continuation count; and stale reports missing `advisory_count`
are detectable.

Decision needed from owner: none.

## Positive Confirmations

- Applicability and clause preflights pass on the operative proposal.
- The need for a distinct `advisory_count` is supported by the parent Slice-0
  thread and prior ADVISORY deliberations.
- The proposal correctly states that ADVISORY entries must not be included in
  `no_go_count`.

## Decision

NO-GO. Prime Builder should revise the dashboard counter specification to
remove latest `VERIFIED` from Prime actionability, keep ADVISORY as a separate
metric or explicitly named disposition metric, use the live MemBase artifact
taxonomy, and add governing dashboard/startup surfaces plus stronger
spec-derived tests.

## Commands Executed

- `python scripts\bridge_applicability_preflight.py --bridge-id gtkb-advisory-report-dashboard-counters-spec`
- `python scripts\adr_dcl_clause_preflight.py --bridge-id gtkb-advisory-report-dashboard-counters-spec`
- `python -m groundtruth_kb deliberations search "advisory dashboard counters Prime actionable VERIFIED ADVISORY no_go_count" --limit 8`
- Targeted reads over `bridge/INDEX.md`,
  `bridge/gtkb-advisory-report-dashboard-counters-spec-001.md`,
  `AGENTS.md`, `config/agent-control/system-interface-map.toml`,
  `.claude/rules/file-bridge-protocol.md`,
  `.claude/rules/bridge-essential.md`,
  `.claude/hooks/formal-artifact-approval-gate.py`, and
  `groundtruth-kb/src/groundtruth_kb/db.py`.

File bridge scan contribution: 1 entry processed.

Copyright 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
