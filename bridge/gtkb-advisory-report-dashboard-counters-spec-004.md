GO

# Loyal Opposition Review - Advisory Report Dashboard Counters Spec REVISED-1

bridge_kind: loyal_opposition_verdict
Document: gtkb-advisory-report-dashboard-counters-spec
Version: 004
Reviewer: Codex (harness A, Loyal Opposition)
Date: 2026-05-11 UTC
Reviewed file: `bridge/gtkb-advisory-report-dashboard-counters-spec-003.md`
Verdict: GO

## Claim

`bridge/gtkb-advisory-report-dashboard-counters-spec-003.md` is approved for
implementation. REVISED-1 closes the prior NO-GO findings from `-002`:

1. `actionable_count_for_prime` now covers only latest `GO` and `NO-GO`.
   Latest `VERIFIED` is explicitly terminal and excluded. Latest `ADVISORY`
   is split into `advisory_disposition_count`.
2. The MemBase row and formal-artifact-approval packet now use the live
   taxonomy value `requirement`, not the unsupported value `specification`.
3. The proposal adds the missing actionability surfaces and strengthens the
   regression test plan to assert the semantics that caused the prior NO-GO.

## Role Authority

- Active harness: Codex.
- Durable harness ID: `A`, resolved from `harness-state/harness-identities.json`.
- Durable role: `loyal-opposition`, resolved from `harness-state/role-assignments.json`.
- Review-start bridge state: live `bridge/INDEX.md` listed this thread latest
  status as `REVISED: bridge/gtkb-advisory-report-dashboard-counters-spec-003.md`,
  actionable for Loyal Opposition.

## Prior Deliberations

Deliberation search was run for:

```text
advisory dashboard counters ADVISORY NO-GO actionable_count_for_prime advisory_disposition_count
```

Relevant results:

- `DELIB-1468` - source Loyal Opposition advisory for the bridge advisory
  report message type.
- `DELIB-1500` - Loyal Opposition review of ADVISORY status/message type.
- `DELIB-1501` - Prime advisory bridge delivery for the same issue.
- `DELIB-1478` - peer-solution advisory loop context.

No result found in this search contradicts the REVISED-1 split between Prime
bridge-continuation work and advisory disposition work.

## Applicability Preflight

Command:

```text
python scripts/bridge_applicability_preflight.py --bridge-id gtkb-advisory-report-dashboard-counters-spec
```

Result: pass.

```text
## Applicability Preflight

- packet_hash: `sha256:c6263e356ce1ad0ee82a3048fccdc8b1c64f06d9b8936896233c13bdef90ad24`
- bridge_document_name: `gtkb-advisory-report-dashboard-counters-spec`
- content_source: `indexed_operative`
- content_file: `bridge/gtkb-advisory-report-dashboard-counters-spec-003.md`
- operative_file: `bridge/gtkb-advisory-report-dashboard-counters-spec-003.md`
- preflight_passed: `true`
- missing_required_specs: []
- missing_advisory_specs: []

| Spec | Severity | Cited | Matched By |
|------|----------|-------|------------|
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | `advisory` | `yes` | content:artifact, content:deliberation, content:MemBase |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | `blocking` | `yes` | path:.claude/rules/file-bridge-protocol.md |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | `advisory` | `yes` | content:deferred, content:verified |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | `blocking` | `yes` | doc:*, content:Specification Links, content:implementation proposal |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | `blocking` | `yes` | doc:*, content:VERIFIED, content:spec-to-test |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | `advisory` | `yes` | content:owner decision, content:requirement, content:specification, content:ADR, content:DCL, content:backlog |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | `blocking` | `yes` | doc:*, path:bridge/**, path:.claude/rules/file-bridge-protocol.md, path:.claude/rules/codex-review-gate.md |
```

## Clause Applicability

Command:

```text
python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-advisory-report-dashboard-counters-spec
```

Result: pass.

```text
## Clause Applicability (Slice 2; mandatory gate)

- Bridge id: `gtkb-advisory-report-dashboard-counters-spec`
- Operative file: `bridge\gtkb-advisory-report-dashboard-counters-spec-003.md`
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
no owner-waiver line is cited. Clauses with `enforcement_mode = "advisory"`
are reported but never gate._
```

## Findings

No blocking findings.

### C1 - P3 - Prime actionability semantics now align with live role rules

Observation:

REVISED-1 defines `actionable_count_for_prime` as latest `GO` or `NO-GO`
only, and explicitly excludes latest `VERIFIED` and latest `ADVISORY`
(`bridge/gtkb-advisory-report-dashboard-counters-spec-003.md:111`). It adds a
separate `advisory_disposition_count` for latest `ADVISORY` entries
(`bridge/gtkb-advisory-report-dashboard-counters-spec-003.md:113`).

This aligns with the live role contract: Prime Builder must never process
latest `NEW`, `REVISED`, or `VERIFIED` entries as actionable queue work, and
Prime handling is limited to latest `GO` or `NO-GO` entries (`AGENTS.md:195`;
`config/agent-control/system-interface-map.toml:182`). It also matches
`.claude/rules/bridge-essential.md:56`, which states latest `VERIFIED` is
terminal and not dispatched.

Deficiency rationale:

No deficiency remains for GO. The prior NO-GO concern was that dashboard
metrics could drive Prime back into terminal work or blur advisory disposition
with bridge continuation. REVISED-1 splits those concepts.

Proposed solution/enhancement:

Implement exactly the REVISED-1 counter split and carry the same wording into
the MemBase row so later dashboard implementation work has a crisp spec target.

Decision needed from owner: none for GO. A formal-artifact-approval packet is
still required during implementation before the MemBase insert.

### C2 - P3 - Live MemBase taxonomy issue is corrected

Observation:

REVISED-1 changes the proposed row to `type='requirement'` and the approval
packet to `artifact_type='requirement'`
(`bridge/gtkb-advisory-report-dashboard-counters-spec-003.md:106`,
`:122`). This matches the live formal-artifact gate's `VALID_ARTIFACT_TYPES`
set, which includes `requirement` and does not include `specification`
(`.claude/hooks/formal-artifact-approval-gate.py:75`). It also matches the
`KnowledgeDB.insert_spec()` default and documented type set
(`groundtruth-kb/src/groundtruth_kb/db.py:818`, `:830`).

Deficiency rationale:

No deficiency remains for GO. Prime should not expand the schema or approval
packet enum under this slice.

Proposed solution/enhancement:

Proceed with `type='requirement'` for `SPEC-ADVISORY-DASHBOARD-COUNTERS-001`.
If a first-class `specification` type is desired later, file a separate
schema/API expansion proposal.

Decision needed from owner: none.

### C3 - P3 - Test mapping now covers the semantics that matter

Observation:

REVISED-1 strengthens IP-3 to six tests: row structure, all six counter names,
NO-GO excluding ADVISORY, Prime actionability excluding latest `VERIFIED`,
`advisory_disposition_count` separate from `actionable_count_for_prime`, and
visual distinction (`bridge/gtkb-advisory-report-dashboard-counters-spec-003.md:126-131`).

Deficiency rationale:

No deficiency remains for GO. The revised tests now derive from the linked
role and bridge semantics rather than merely checking that counter names exist.

Proposed solution/enhancement:

In the implementation report, cite the observed T1-T6 results and include the
formal-artifact packet validation output from
`python scripts/validate_formal_artifact_packet.py "<packet_path>"`.

Decision needed from owner: none at review time.

### N1 - P4 - Revision-note wording says "five-test suite" while IP-3 defines six tests

Observation:

The Revision Notes say IP-3 is strengthened to a "five-test suite"
(`bridge/gtkb-advisory-report-dashboard-counters-spec-003.md:30`), but the
same notes list T1-T5 and later IP-3 defines T1-T6
(`bridge/gtkb-advisory-report-dashboard-counters-spec-003.md:126-131`).

Deficiency rationale:

This is editorial noise, not a GO blocker. The operative scope, test plan, and
acceptance criteria all require six tests.

Proposed solution/enhancement:

Prime may correct the wording opportunistically in the implementation report or
future revision text, but this does not require another proposal revision.

Decision needed from owner: none.

## Positive Confirmations

- Applicability and clause preflights pass on the operative `-003` proposal.
- The proposal includes substantive `Specification Links`, `Prior Deliberations`,
  `Owner Decisions / Input`, spec-to-test mapping, acceptance criteria, and
  risk/rollback sections.
- All live paths are inside `E:\GT-KB`.
- The proposal correctly defers dashboard counter code implementation to a
  future slice.

## Decision

GO. Prime Builder may proceed with
`bridge/gtkb-advisory-report-dashboard-counters-spec-003.md` and file the
post-implementation report for Loyal Opposition verification.

The future implementation report must include observed evidence for:

- formal-artifact-approval packet creation with `artifact_type='requirement'`;
- pre-insertion validation via `scripts/validate_formal_artifact_packet.py`;
- MemBase insert using `GTKB_FORMAL_APPROVAL_PACKET`;
- `python -m pytest platform_tests/groundtruth_kb/specs/test_spec_advisory_dashboard_counters.py -v --tb=short`;
- spec-to-test mapping for T1-T6.

## Commands Executed

- `python scripts/bridge_applicability_preflight.py --bridge-id gtkb-advisory-report-dashboard-counters-spec`
- `python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-advisory-report-dashboard-counters-spec`
- `python -m groundtruth_kb deliberations search "advisory dashboard counters ADVISORY NO-GO actionable_count_for_prime advisory_disposition_count" --limit 10`
- Targeted reads over `bridge/INDEX.md`, the full dashboard-counter bridge
  version chain `-001` through `-003`, `AGENTS.md`,
  `config/agent-control/system-interface-map.toml`,
  `.claude/rules/bridge-essential.md`,
  `.claude/rules/peer-solution-advisory-loop.md`,
  `.claude/hooks/formal-artifact-approval-gate.py`, and
  `groundtruth-kb/src/groundtruth_kb/db.py`.

File bridge scan contribution: 1 entry processed.

Copyright 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
