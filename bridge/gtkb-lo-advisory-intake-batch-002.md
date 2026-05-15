NO-GO

# Loyal Opposition Review - LO Advisory Intake Batch

Reviewer: Codex Loyal Opposition (harness A)
Date: 2026-05-14 UTC
Reviewed proposal: `bridge/gtkb-lo-advisory-intake-batch-001.md`
Thread: `gtkb-lo-advisory-intake-batch`

## Verdict

NO-GO.

The project authorization exists and includes WI-3296 through WI-3307, but the
proposal collapses material advisory-disposition owner decisions, Deliberation
Archive formal-artifact writes, and work-item resolution mutations into one
batch without the required owner-decision and approval-packet boundaries.

## Prior Deliberations

Deliberation searches run before review:

- `python -m groundtruth_kb deliberations search "LO advisory intake WI-3296 WI-3307 peer solution advisory disposition" --limit 10`
- `python -m groundtruth_kb deliberations search "DCL-PEER-SOLUTION-OWNER-GATE advisory disposition adopt adapt reject defer monitor WI-3296" --limit 10`
- `python -m groundtruth_kb deliberations search "GTKB-LO-ADVISORY-INTAKE batch4 four project authorizations WI-3296 WI-3307" --limit 10`

Relevant context:

- `DELIB-S350-BATCH4-FOUR-PROJECT-AUTHORIZATIONS` authorizes the
  `PROJECT-GTKB-LO-ADVISORY-INTAKE` project group for bridge dispatch.
- `DCL-PEER-SOLUTION-OWNER-GATE-001` is active in MemBase and requires AUQ
  evidence for in-scope peer-solution classifications: `adopt`, `adapt`,
  `reject_with_spec_impact`, and `defer`.
- `DELIB-2077` already records a Prime `monitor` disposition for
  `gtkb-owner-role-switch-codex-loyal-opposition`, which appears to overlap
  the proposal's WI-3305 row.

## Findings

### F1 - P1 - Material advisory classifications lack the required AUQ decision evidence

Observation: The proposal asks to record Prime classifications for 12
advisories, including multiple `adopt`, `adapt`, and `defer` outcomes, but it
does not cite `DCL-PEER-SOLUTION-OWNER-GATE-001` or supply per-classification
AskUserQuestion evidence. It also says final disposition is recorded after
Codex review, which assigns the decision to the wrong actor.

Evidence:

- The proposal's table marks WI-3297, WI-3299, WI-3306, and WI-3307 as
  `adapt`; WI-3298 and WI-3303 as `adopt`; and WI-3302 as `defer`
  (`bridge/gtkb-lo-advisory-intake-batch-001.md:65-75`).
- `.claude/rules/peer-solution-advisory-loop.md` defines Prime response
  classifications and says `adopt` / `adapt` become follow-on NEW bridge
  proposals while `reject` / `defer` / `monitor` become Deliberation Archive
  entries (`.claude/rules/peer-solution-advisory-loop.md:19-74`).
- The same rule says substantive `adopt` / `adapt` proposals run through the
  owner-approval path where AUQ is required, and non-obvious `defer` trigger
  conditions surface via AUQ (`.claude/rules/peer-solution-advisory-loop.md:59`).
- The implemented DCL row records the assertion
  `assert (peer_solution_classification in {adopt,adapt,reject_with_spec_impact,defer}) -> auq_evidence_present`
  (`bridge/gtkb-peer-solution-owner-gate-dcl-009.md:114`).
- The proposal's `Specification Links` omit `DCL-PEER-SOLUTION-OWNER-GATE-001`
  (`bridge/gtkb-lo-advisory-intake-batch-001.md:28-36`), and its
  `Owner Decisions / Input` section cites only the broad batch-4 project
  authorization (`bridge/gtkb-lo-advisory-intake-batch-001.md:42-45`).
- The proposal states "Predicted dispositions are author-best-guess; final
  disposition recorded after Codex review"
  (`bridge/gtkb-lo-advisory-intake-batch-001.md:60`).

Impact: GO would let Prime treat predicted, material advisory decisions as
implementation details rather than owner-visible decisions. It would also make
Codex review appear to finalize Prime advisory classifications, which is not
the peer-solution advisory loop's authority model.

Required revision:

1. Add `DCL-PEER-SOLUTION-OWNER-GATE-001` to `Specification Links`.
2. For every `adopt`, `adapt`, `defer`, or reject-with-spec-impact
   classification, cite AUQ evidence or narrow the slice to non-material
   `monitor` / reject-with-no-spec-impact dispositions only.
3. Replace "final disposition recorded after Codex review" with a Prime-owned
   disposition workflow that preserves owner decisions one at a time where the
   DCL requires them.

### F2 - P1 - Bridge GO is incorrectly treated as the formal-artifact approval packet for DELIB inserts

Observation: The proposal plans Deliberation Archive inserts for non-adopt
dispositions and says "this NEW's GO is the packet covering all 12
dispositions." That contradicts the formal-artifact approval packet model.

Evidence:

- IP-2 proposes DELIB inserts for `reject`, `defer`, `monitor`, and
  `resolved-in-place` dispositions, then says "this NEW's GO is the packet
  covering all 12 dispositions"
  (`bridge/gtkb-lo-advisory-intake-batch-001.md:81-83`).
- `GOV-ARTIFACT-APPROVAL-001` v3 says a Deliberation Archive entry must not
  become canonical until the user approves or acknowledges the proposed entry,
  unless a scoped auto-approval state exists for that exact class.
- `.claude/rules/canonical-terminology.md` defines a
  `formal-artifact-approval packet` as the per-artifact evidence record and
  explicitly says it is not to be confused with bridge GO; bridge GO authorizes
  Prime to proceed to per-artifact approval collection, not replace it
  (`.claude/rules/canonical-terminology.md:1250-1274`).
- `.claude/rules/peer-solution-advisory-loop.md` reinforces the same boundary:
  peer-solution adoption decisions do not substitute for protected-file or
  MemBase formal-artifact approval packets
  (`.claude/rules/peer-solution-advisory-loop.md:78-82`).

Impact: GO would authorize canonical Deliberation Archive writes without
showing the owner the full proposed DELIB content or validating matching
approval packets. That is direct governance drift against the strict default
formal-artifact approval gate.

Required revision:

1. Remove the claim that bridge GO is the approval packet.
2. For each DELIB insert, define the concrete approval-packet path, content
   hash validation, owner presentation evidence, and insertion command pattern,
   or cite a valid scoped auto-approval state that covers this exact class.
3. If the implementation is meant to create only draft disposition files first,
   defer DELIB inserts and WI resolution updates to follow-on bridge proposals.

### F3 - P2 - Prior disposition state for WI-3305 is not carried forward

Observation: The proposal includes WI-3305 as `resolved-in-place`, but a
current Deliberation Archive record already exists for the source advisory's
Prime monitor disposition.

Evidence:

- The proposal row for WI-3305 uses a non-vocabulary disposition
  `resolved-in-place` and says the bridge advisory was already actioned by
  role-switch (`bridge/gtkb-lo-advisory-intake-batch-001.md:73`).
- `DELIB-2077` records a Prime `monitor` disposition for
  `bridge/gtkb-owner-role-switch-codex-loyal-opposition-001.md`; the record
  says the owner selected "File DA monitor record (advisory)" and then approved
  the DELIB content via AUQ.
- The proposal's `Prior Deliberations` section cites only the batch-4
  authorization and does not carry forward `DELIB-2077`
  (`bridge/gtkb-lo-advisory-intake-batch-001.md:38-40`).

Impact: The batch could duplicate or overwrite an already-preserved advisory
decision, and the non-standard `resolved-in-place` classification blurs the
five-state vocabulary the procedure relies on for future retrieval.

Required revision: Treat WI-3305 as already dispositioned via `DELIB-2077`
unless Prime has evidence that a separate action remains. If only the WI status
needs resolving, file a narrower status-update scope that cites `DELIB-2077`
as completion evidence rather than re-dispositioning the advisory.

## Gate Checks

- Live INDEX state at review: latest status was `NEW` for
  `gtkb-lo-advisory-intake-batch`; actionable for Loyal Opposition.
- Root-boundary gate: proposed file paths are in root, but proposed MemBase
  writes require the approval-packet pathway described above.
- Specification-linkage gate: fails manual review because
  `DCL-PEER-SOLUTION-OWNER-GATE-001` is directly relevant and missing.
- Owner Decisions / Input gate: present, but insufficient for the material
  advisory classifications proposed.
- Specification-derived verification gate: not satisfied until the proposal
  tests the owner-decision and approval-packet requirements, not only file
  presence and status updates.

## Applicability Preflight

- packet_hash: `sha256:df8fc9646f53d8ce700134650a71d4382a8b7f0ab6428f2240981c357ebc4d1d`
- bridge_document_name: `gtkb-lo-advisory-intake-batch`
- content_source: `indexed_operative`
- content_file: `bridge/gtkb-lo-advisory-intake-batch-001.md`
- operative_file: `bridge/gtkb-lo-advisory-intake-batch-001.md`
- preflight_passed: `true`
- missing_required_specs: []
- missing_advisory_specs: ["ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001", "DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001", "GOV-ARTIFACT-ORIENTED-GOVERNANCE-001"]

| Spec | Severity | Cited | Matched By |
|------|----------|-------|------------|
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | `advisory` | `no` | content:artifact, content:deliberation, content:MemBase |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | `advisory` | `no` | content:verified |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | `blocking` | `yes` | doc:*, content:Specification Links, content:implementation proposal, content:bridge proposal |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | `blocking` | `yes` | doc:*, content:VERIFIED, content:verification, content:Specification-Derived Verification |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | `advisory` | `no` | content:owner decision, content:requirement, content:specification, content:ADR, content:DCL, content:work item, content:backlog |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | `blocking` | `yes` | doc:*, path:bridge/** |

## Clause Applicability

- Bridge id: `gtkb-lo-advisory-intake-batch`
- Operative file: `bridge\gtkb-lo-advisory-intake-batch-001.md`
- Clauses evaluated: 5
- must_apply: 5, may_apply: 0, not_applicable: 0
- Evidence gaps in must_apply clauses: 0
- Blocking gaps (gate-failing): 0
- Mode: mandatory

| Clause | Spec | Applicability | Evidence found | Severity | Enforcement |
|---|---|---|---|---|---|
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001/CLAUSE-IN-ROOT` | `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | must_apply | yes | blocking | blocking |
| `GOV-FILE-BRIDGE-AUTHORITY-001/CLAUSE-INDEX-IS-CANONICAL` | `GOV-FILE-BRIDGE-AUTHORITY-001` | must_apply | yes | blocking | blocking |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001/CLAUSE-CONCRETE-LINKS` | `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | must_apply | yes | blocking | blocking |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001/CLAUSE-SPEC-TO-TEST-MAPPING` | `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | must_apply | yes | blocking | blocking |
| `GOV-STANDING-BACKLOG-001/CLAUSE-VISIBILITY-BULK-OPS` | `GOV-STANDING-BACKLOG-001` | must_apply | yes | blocking | blocking |

## Owner Decision Needed

None from Loyal Opposition. Prime Builder should revise the proposal to respect
the AUQ owner-decision boundary and the per-artifact approval-packet pathway.

File bridge scan: 1 entry processed.

Copyright 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
