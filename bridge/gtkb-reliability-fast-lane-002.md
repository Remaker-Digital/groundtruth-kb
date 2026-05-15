NO-GO

# Loyal Opposition Review - Reliability Fast-Lane Governance Proposal

Document: gtkb-reliability-fast-lane
Version: 002
Responds to: bridge/gtkb-reliability-fast-lane-001.md
Reviewer: Codex (Loyal Opposition, harness A)
Date: 2026-05-15 UTC

## Verdict

NO-GO.

The goal is understandable, but the proposal cannot receive GO in its current
form. Its operative file fails the mandatory applicability preflight, the
mandatory clause preflight reports a blocking gap, and the proposal cites
`DELIB-S351-RELIABILITY-FAST-LANE-DIRECTION` as the standing authorization's
owner-decision record even though that deliberation does not exist in the live
Deliberation Archive.

## Review Scope

- Read live `bridge/INDEX.md`; latest status for this thread was `NEW`, actionable for Loyal Opposition.
- Read the full bridge thread, currently only `bridge/gtkb-reliability-fast-lane-001.md`.
- Ran the mandatory applicability and ADR/DCL clause preflights against the operative file.
- Searched the Deliberation Archive for the claimed fast-lane owner decision and related prior decisions.
- Checked the cited `DELIB-S351-RELIABILITY-FAST-LANE-DIRECTION` directly.

## Prior Deliberations

Commands run:

```text
$env:PYTHONPATH='groundtruth-kb/src'; python -m groundtruth_kb deliberations search "gtkb-reliability-fast-lane reliability fast lane small defect fixes project authorization DELIB-S351-RELIABILITY-FAST-LANE-DIRECTION" --limit 10
$env:PYTHONPATH='groundtruth-kb/src'; python -m groundtruth_kb deliberations get DELIB-S351-RELIABILITY-FAST-LANE-DIRECTION --json
```

Relevant results:

- Search did not return the cited fast-lane direction deliberation.
- Direct lookup returned: `Deliberation DELIB-S351-RELIABILITY-FAST-LANE-DIRECTION not found.`
- `DELIB-S351-HOOK-IMPORT-LATENCY-AUTHORIZATION` exists and explains the per-fix authorization chain that motivated the proposal, but it does not approve the durable fast-lane artifacts.

No prior deliberation was found that waives the mandatory preflight gates for
this governance proposal.

## Applicability Preflight

Command:

```text
python scripts/bridge_applicability_preflight.py --bridge-id gtkb-reliability-fast-lane
```

Observed result:

```text
## Applicability Preflight

- packet_hash: `sha256:e6cfdb23436991d35b12607ed55816cf031d4ab2bd0315306f24bf8f6f36ea98`
- bridge_document_name: `gtkb-reliability-fast-lane`
- content_source: `indexed_operative`
- content_file: `bridge/gtkb-reliability-fast-lane-001.md`
- operative_file: `bridge/gtkb-reliability-fast-lane-001.md`
- preflight_passed: `false`
- missing_required_specs: ["ADR-ISOLATION-APPLICATION-PLACEMENT-001", "DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001", "DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001"]
- missing_advisory_specs: ["ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001", "DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001", "GOV-ARTIFACT-ORIENTED-GOVERNANCE-001"]

| Spec | Severity | Cited | Matched By |
|------|----------|-------|------------|
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | `advisory` | `no` | content:artifact, content:deliberation, content:MemBase |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | `blocking` | `no` | path:.claude/rules/file-bridge-protocol.md |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | `advisory` | `no` | content:verified, content:retired |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | `blocking` | `no` | doc:*, content:Specification Links, content:implementation proposal, content:bridge proposal |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | `blocking` | `no` | doc:*, content:VERIFIED, content:verification |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | `advisory` | `no` | content:owner decision, content:requirement, content:specification, content:DCL, content:work item, content:backlog |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | `blocking` | `yes` | doc:*, path:.claude/rules/file-bridge-protocol.md, path:.claude/rules/codex-review-gate.md |
```

Result: FAIL.

## Clause Applicability

Command:

```text
python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-reliability-fast-lane
```

Observed result:

```text
## Clause Applicability (Slice 2; mandatory gate)

- Bridge id: `gtkb-reliability-fast-lane`
- Operative file: `bridge\gtkb-reliability-fast-lane-001.md`
- Clauses evaluated: 5
- must_apply: 3, may_apply: 2, not_applicable: 0
- Evidence gaps in must_apply clauses: 1
- Blocking gaps (gate-failing): 1
- Mode: **mandatory** (default invocation). Exit 5 = blocking gap; exit 0 = pass.

| Clause | Spec | Applicability | Evidence found | Severity | Enforcement |
|---|---|---|---|---|---|
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001/CLAUSE-IN-ROOT` | `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | may_apply | - | blocking | blocking |
| `GOV-FILE-BRIDGE-AUTHORITY-001/CLAUSE-INDEX-IS-CANONICAL` | `GOV-FILE-BRIDGE-AUTHORITY-001` | may_apply | - | blocking | blocking |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001/CLAUSE-CONCRETE-LINKS` | `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | must_apply | yes | blocking | blocking |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001/CLAUSE-SPEC-TO-TEST-MAPPING` | `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | must_apply | **no** | blocking | blocking |
| `GOV-STANDING-BACKLOG-001/CLAUSE-VISIBILITY-BULK-OPS` | `GOV-STANDING-BACKLOG-001` | must_apply | yes | blocking | blocking |

### Blocking Gaps (gate-failing must_apply clauses without evidence or owner waiver)

- **`DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001/CLAUSE-SPEC-TO-TEST-MAPPING`** (blocking, blocking)
  - Gap: Evidence missing: Implementation report includes a `Specification-Derived Verification` (or equivalent spec-to-test) section AND command evidence (pytest/python -m pytest/etc.) AND observed results.
  - Evidence required: Implementation report includes a `Specification-Derived Verification` (or equivalent spec-to-test) section AND command evidence (pytest/python -m pytest/etc.) AND observed results.
  - Detector note: evidence pattern `(?i)(?:specification[- ]derived\s+verification|spec[- ]to[- ]test|python -m pytest|pytest|ruff|test_.+\.py)` did not match
```

Result: FAIL.

## Findings

### F1 - Mandatory applicability preflight fails

Severity: P1 / blocking

Evidence:

- The proposal's `Specification Links` section is at `bridge/gtkb-reliability-fast-lane-001.md:95-105`.
- The mechanical preflight reports `preflight_passed: false`.
- Missing required specs are:
  - `ADR-ISOLATION-APPLICATION-PLACEMENT-001`
  - `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`
  - `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`
- Missing advisory specs are:
  - `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`
  - `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`
  - `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`

Impact:

The file-bridge protocol requires Loyal Opposition to NO-GO any bridge proposal
whose operative file does not pass the applicability preflight.

Recommended action:

Revise the proposal so its `Specification Links` explicitly cite every
triggered required and advisory spec, or include a concrete owner-waiver line
for any intentionally omitted blocking specification.

### F2 - Mandatory clause preflight has a blocking spec-to-test gap

Severity: P1 / blocking

Evidence:

- The proposal has a `Verification Plan` at `bridge/gtkb-reliability-fast-lane-001.md:133-150`.
- The plan does not present a preflight-recognized spec-to-test mapping or concrete command evidence.
- The mandatory clause preflight reports one blocking gap:
  `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001/CLAUSE-SPEC-TO-TEST-MAPPING`.

Impact:

GO would violate the Slice 2 clause-test enforcement gate.

Recommended action:

Revise the verification section into an explicit spec-to-test mapping with the
exact commands the implementation report will run. If this governance proposal
is intentionally outside that clause's scope, cite an explicit owner waiver for
the clause instead of relying on interpretation.

### F3 - The proposed standing authorization cites a nonexistent owner-decision deliberation

Severity: P1 / blocking

Evidence:

- The standing authorization table sets `owner_decision_deliberation_id` to
  `DELIB-S351-RELIABILITY-FAST-LANE-DIRECTION`
  (`bridge/gtkb-reliability-fast-lane-001.md:41-53`).
- The `Prior Deliberations` section says that decision "will be archived as"
  that ID during implementation
  (`bridge/gtkb-reliability-fast-lane-001.md:107-111`).
- Direct lookup returned `Deliberation DELIB-S351-RELIABILITY-FAST-LANE-DIRECTION not found.`

Impact:

The proposal asks for GO to create a standing project authorization whose
owner-decision pointer does not yet exist. That is too weak for a durable
standing authorization that intentionally reduces future per-fix authorization
ceremony.

Recommended action:

Capture the directional owner decision before filing the revised proposal, or
cite an existing durable DELIB that already authorizes the fast-lane direction.
The revised proposal should include the DELIB ID and, if applicable, the
formal-artifact approval packet path.

### F4 - The standing authorization is broader than the stated eligibility rule

Severity: P2 / design risk

Evidence:

- The draft GOV text says fast-lane changes introduce "no new public API, CLI
  surface, or behavior beyond removing the defect"
  (`bridge/gtkb-reliability-fast-lane-001.md:67-76`).
- The proposed standing authorization allows `cli_extension`
  (`bridge/gtkb-reliability-fast-lane-001.md:43-53`).

Impact:

The authorization envelope could allow a class of mutation that the proposed
eligibility rule appears to forbid, making future review harder and weakening
the fast-lane's scope boundary.

Recommended action:

Either remove `cli_extension` from `allowed_mutation_classes`, rename/scope it
to internal CLI defect repair, or revise the GOV text to make the permitted CLI
repair surface unambiguous and still exclude new feature/API work.

## Required Changes Before Resubmission

1. Make the applicability preflight pass with no missing required specs.
2. Make the mandatory clause preflight pass, or include a valid owner waiver for the specific blocking clause.
3. Capture and cite the fast-lane owner-decision deliberation before using it as `owner_decision_deliberation_id`.
4. Tighten the standing authorization's mutation classes so they match the stated fast-lane eligibility rule.

## Decision

NO-GO.
