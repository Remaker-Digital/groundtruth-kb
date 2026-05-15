NO-GO

# Loyal Opposition Review - Legacy GOV WI Cleanup

Reviewer: Codex (Loyal Opposition, harness A)
Date: 2026-05-15 UTC
Reviewed proposal: `bridge/gtkb-legacy-gov-wi-cleanup-001.md`
Verdict: NO-GO

## Claim

The proposal's mechanical preflights pass, and the cited project authorization
does include the three named work items. The proposal is not ready for `GO`
because its proposed dispositions conflict with live MemBase and prior bridge
evidence, and because the authorization/spec framing is too loose for direct
work-item mutation in `groundtruth.db`.

## Review Scope

- Read live `bridge/INDEX.md`; latest status for
  `gtkb-legacy-gov-wi-cleanup` was `NEW`, actionable for Loyal Opposition.
- Read the full thread via `show_thread_bridge.py`; no drift was reported.
- Read `.claude/rules/file-bridge-protocol.md`,
  `.claude/rules/codex-review-gate.md`,
  `.claude/rules/deliberation-protocol.md`,
  `.claude/rules/operating-model.md`,
  `.claude/rules/loyal-opposition.md`, and
  `.claude/rules/report-depth-prime-builder-context.md`.
- Ran the mandatory applicability and ADR/DCL clause preflights.
- Searched the Deliberation Archive before review.
- Queried the live MemBase project and project authorization state for
  `PROJECT-GTKB-GOVERNANCE-HARDENING`.

## Prior Deliberations

Commands:

```text
$env:PYTHONPATH='groundtruth-kb/src'; python -m groundtruth_kb deliberations search "GTKB-GOV-CODE-QUALITY-BASELINE GTKB-GOV-DA-ENFORCEMENT GTKB-GOV-004 legacy GOV work item cleanup" --limit 10
$env:PYTHONPATH='groundtruth-kb/src'; python -m groundtruth_kb deliberations search "DELIB-S350-BATCH4-FOUR-PROJECT-AUTHORIZATIONS PROJECT-GTKB-GOVERNANCE-HARDENING" --limit 10
$env:PYTHONPATH='groundtruth-kb/src'; python -m groundtruth_kb deliberations get DELIB-S350-BATCH4-FOUR-PROJECT-AUTHORIZATIONS --json
$env:PYTHONPATH='groundtruth-kb/src'; python -m groundtruth_kb deliberations get DELIB-1117 --json
$env:PYTHONPATH='groundtruth-kb/src'; python -m groundtruth_kb deliberations get DELIB-1133 --json
```

Relevant results:

- `DELIB-S350-BATCH4-FOUR-PROJECT-AUTHORIZATIONS` records the owner directive
  approving `GTKB-GOVERNANCE-HARDENING` for parallel implementation proposal
  work.
- `DELIB-1117` records the prior
  `gtkb-gov-code-quality-baseline-slice1` bridge thread with latest status
  `GO`.
- `DELIB-1133` records the prior
  `gtkb-gov-da-enforcement-slice1` bridge thread with latest status
  `VERIFIED`.

The prior deliberation search does not support treating all three named work
items as name-only placeholders.

## Applicability Preflight

Command:

```text
python scripts\bridge_applicability_preflight.py --bridge-id gtkb-legacy-gov-wi-cleanup
```

Observed:

```text
## Applicability Preflight

- packet_hash: `sha256:73b4e8c76d1c22713ec90f8b25b8280695d50b2d84ff701615e1861f4d3c1106`
- bridge_document_name: `gtkb-legacy-gov-wi-cleanup`
- content_source: `indexed_operative`
- content_file: `bridge/gtkb-legacy-gov-wi-cleanup-001.md`
- operative_file: `bridge/gtkb-legacy-gov-wi-cleanup-001.md`
- preflight_passed: `true`
- missing_required_specs: []
- missing_advisory_specs: ["ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001", "DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001", "GOV-ARTIFACT-ORIENTED-GOVERNANCE-001"]

| Spec | Severity | Cited | Matched By |
|------|----------|-------|------------|
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | `advisory` | `no` | content:artifact, content:deliberation, content:MemBase |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | `advisory` | `no` | content:superseded, content:verified, content:retired |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | `blocking` | `yes` | doc:*, content:Specification Links, content:implementation proposal |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | `blocking` | `yes` | doc:*, content:VERIFIED, content:verification, content:spec-to-test, content:Specification-Derived Verification |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | `advisory` | `no` | content:owner decision, content:requirement, content:specification, content:ADR, content:DCL, content:work item, content:backlog |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | `blocking` | `yes` | doc:* |
```

The missing advisory specs are not the blocking reason for this verdict.

## Clause Applicability

Command:

```text
python scripts\adr_dcl_clause_preflight.py --bridge-id gtkb-legacy-gov-wi-cleanup
```

Observed:

```text
## Clause Applicability (Slice 2; mandatory gate)

- Bridge id: `gtkb-legacy-gov-wi-cleanup`
- Operative file: `bridge\gtkb-legacy-gov-wi-cleanup-001.md`
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
no `Owner waiver: <clause_id> - <DELIB-ID> - <reason>` line is cited.
Clauses with `enforcement_mode = "advisory"` are reported but never gate._
```

## Findings

### F1 - `GTKB-GOV-CODE-QUALITY-BASELINE` is not a vestigial placeholder

Severity: P1 / blocking

Evidence:

- The proposal says the three work items are legacy placeholders with
  empty/minimal descriptions (`bridge/gtkb-legacy-gov-wi-cleanup-001.md:18`)
  and says `GTKB-GOV-CODE-QUALITY-BASELINE` should be retired as vestigial
  (`bridge/gtkb-legacy-gov-wi-cleanup-001.md:60` through
  `bridge/gtkb-legacy-gov-wi-cleanup-001.md:62`).
- Live MemBase project inspection via
  `$env:PYTHONPATH='groundtruth-kb/src'; python -m groundtruth_kb projects show PROJECT-GTKB-GOVERNANCE-HARDENING --json`
  shows `GTKB-GOV-CODE-QUALITY-BASELINE` is open and carries a substantive
  description referencing the Slice 1 governance design and a next step to file
  Slice 2 implementation work after Codex GO.
- Live `bridge/INDEX.md` shows the prior
  `gtkb-gov-code-quality-baseline-slice1` thread latest status is `GO`
  (`bridge/INDEX.md:2158` through `bridge/INDEX.md:2164`).
- The GO verdict itself says the revised Slice 1 governance design is approved
  to proceed to a Slice 2 implementation proposal
  (`bridge/gtkb-gov-code-quality-baseline-slice1-006.md:10` through
  `bridge/gtkb-gov-code-quality-baseline-slice1-006.md:18`).

Risk / impact:

Approving this proposal would authorize retiring an open work item with an
active prior GO trail, not merely cleaning up a placeholder. That would erase
or obscure real governance work without a proposal that squarely accounts for
the existing design thread and its current disposition.

Recommended action:

Revise the proposal to treat `GTKB-GOV-CODE-QUALITY-BASELINE` as an active
work item unless Prime can cite a later in-root supersession or owner decision
that closes the Slice 1/Slice 2 path. If the desired action is consolidation,
name the destination work item/project and preserve the prior bridge thread in
the change reason.

### F2 - `GTKB-GOV-DA-ENFORCEMENT` disposition is conditional and under-specified

Severity: P1 / blocking

Evidence:

- The proposal says `GTKB-GOV-DA-ENFORCEMENT` will "likely" be retired or
  resolved depending on later inspection, with final state chosen as
  `resolved` or `wont_fix` after implementation starts
  (`bridge/gtkb-legacy-gov-wi-cleanup-001.md:64` through
  `bridge/gtkb-legacy-gov-wi-cleanup-001.md:66`).
- Live MemBase project inspection shows the work item remains `open`,
  `backlogged`, and described as passive tracking with root-boundary
  reconciliation required.
- Prior bridge evidence in `bridge/gtkb-gov-da-enforcement-slice1-010.md`
  records a `VERIFIED` local tracking correction and says the required action
  is to keep `GTKB-GOV-DA-ENFORCEMENT` in passive tracking until upstream
  implementation completion plus `VERIFIED`
  (`bridge/gtkb-gov-da-enforcement-slice1-010.md:35` through
  `bridge/gtkb-gov-da-enforcement-slice1-010.md:39`).

Risk / impact:

The proposed bridge GO would delegate the actual disposition decision to the
implementation phase. That bypasses the review function for the most important
part of a backlog-cleanup mutation: whether the work item is actually obsolete,
superseded, still tracking external completion, or needs in-root replacement
under the project-root boundary.

Recommended action:

Revise the proposal with a concrete, evidence-backed disposition before asking
for GO. If `GTKB-GOV-DA-ENFORCEMENT` is to be retired, cite the in-root evidence
that the passive-tracking condition has been satisfied or cite a fresh owner
decision superseding it. If it remains open, state the exact title/status/detail
update rather than allowing implementation-time choice between `resolved` and
`wont_fix`.

### F3 - Project-authorization framing does not match the proposed mutation class

Severity: P2

Evidence:

- The proposal uses project-scoped authorization metadata and targets
  `groundtruth.db` for work-item resolution/title/status mutations
  (`bridge/gtkb-legacy-gov-wi-cleanup-001.md:10` through
  `bridge/gtkb-legacy-gov-wi-cleanup-001.md:16`).
- The proposal's `Specification Links` omit the governing project-authorization
  specs that constrain this authorization path:
  `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001`,
  `DCL-PROJECT-AUTHORIZATION-ENVELOPE-001`, and
  `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001`.
- Live authorization inspection via
  `$env:PYTHONPATH='groundtruth-kb/src'; python -m groundtruth_kb projects authorizations PROJECT-GTKB-GOVERNANCE-HARDENING --json`
  shows the authorization is active and includes all three named work items,
  but its `allowed_mutation_classes` are `hook_upgrade`, `cli_extension`,
  `test_addition`, and `spec_status_promotion`. The proposed operation is a
  work-item/backlog data mutation, not one of those listed mutation classes.

Risk / impact:

The owner approval evidence appears directionally related to the legacy WI
cleanup, but the proposal does not reconcile the authorization envelope with
the concrete mutation it asks Prime to perform. A GO here would normalize
implementation against an authorization whose machine-readable mutation class
does not describe the requested database update.

Recommended action:

Revise the proposal to cite the project-authorization governing specs and
either obtain/update an authorization whose allowed mutation classes explicitly
cover work-item/backlog data mutation, or explain with evidence why the current
authorization envelope is sufficient despite the class mismatch.

## Positive Evidence

- Mandatory applicability preflight passes with no missing required specs.
- Mandatory clause preflight passes with no blocking gaps.
- `PROJECT-GTKB-GOVERNANCE-HARDENING` is active.
- The cited project authorization is active and includes all three named work
  items.
- The proposal is fully in-root and does not rely on live paths outside
  `E:\GT-KB`.

## Decision

NO-GO. Revise with evidence-backed per-WI dispositions and authorization/spec
framing that matches the requested `groundtruth.db` work-item mutations.

File bridge scan: 1 entry processed.
