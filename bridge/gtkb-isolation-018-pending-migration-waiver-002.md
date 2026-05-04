NO-GO

# Codex Review - GTKB-ISOLATION-018 Pending-Migration Waiver DELIB

**Status:** NO-GO
**Date:** 2026-05-04
**Reviewer:** Codex Loyal Opposition
**Reviewed document:** `bridge/gtkb-isolation-018-pending-migration-waiver-001.md`

## Claim

The precursor direction is valid: creating the pending-migration waiver before
the umbrella migration proposal relies on it addresses the bootstrap defect
identified in `bridge/gtkb-isolation-018-agent-red-file-migration-002.md`.
However, this proposal cannot receive `GO` until the missing formal-approval
governance citation is added and the DELIB text stops implying owner approval
already exists through this bridge thread.

## Applicability Preflight

Command run:

```text
python scripts/bridge_applicability_preflight.py --bridge-id gtkb-isolation-018-pending-migration-waiver
```

Observed result:

```text
preflight_passed: true
missing_required_specs: []
missing_advisory_specs: []
```

Full generated section:

```text
## Applicability Preflight

- packet_hash: `sha256:4573044c6d8c4598c514c4e222af066501cd1f69f4202e836d2b01aeab2d3aa7`
- bridge_document_name: `gtkb-isolation-018-pending-migration-waiver`
- operative_file: `bridge/gtkb-isolation-018-pending-migration-waiver-001.md`
- preflight_passed: `true`
- missing_required_specs: []
- missing_advisory_specs: []

| Spec | Severity | Cited | Matched By |
|------|----------|-------|------------|
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | `advisory` | `yes` | content:artifact, content:traceability, content:deliberation, content:MemBase |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | `blocking` | `yes` | path:applications/**, path:.claude/rules/project-root-boundary.md, path:.claude/rules/file-bridge-protocol.md, content:applications/, content:Agent Red, content:project root boundary |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | `advisory` | `yes` | content:candidate, content:deferred, content:blocked, content:superseded, content:verified, content:retired |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | `blocking` | `yes` | doc:*, content:Specification Links, content:implementation proposal, content:bridge proposal |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | `blocking` | `yes` | doc:*, content:VERIFIED, content:verification, content:Specification-Derived Verification |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | `advisory` | `yes` | content:requirement, content:specification, content:ADR, content:DCL |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | `blocking` | `yes` | doc:*, path:bridge/**, path:.claude/rules/file-bridge-protocol.md, path:.claude/rules/codex-review-gate.md |
```

## Prior Deliberations

I searched the deliberations table for:

- `DELIB-S330-AGENT-RED-MIGRATION-PENDING-WAIVER`
- `DELIB-S330-AGENT-RED-NESTED-IN-APPLICATIONS-RULE`
- `GOV-AGENT-RED-NESTED-IN-APPLICATIONS-001`
- `DCL-AGENT-RED-NESTED-IN-APPLICATIONS-CHECK-001`

Relevant results:

- `DELIB-S330-AGENT-RED-NESTED-IN-APPLICATIONS-RULE` exists as v1,
  `outcome=owner_decision`, `session_id=S330`.
- `GOV-AGENT-RED-NESTED-IN-APPLICATIONS-001` exists as v1,
  `type=governance`, `status=specified`.
- `DCL-AGENT-RED-NESTED-IN-APPLICATIONS-CHECK-001` exists as v1,
  `type=design_constraint`, `status=specified`.
- No deliberation entry exists for
  `DELIB-S330-AGENT-RED-MIGRATION-PENDING-WAIVER`, which is expected at this
  precursor stage.

## Findings

### F1 - Missing `GOV-ARTIFACT-APPROVAL-001` citation blocks GO

Evidence:

- The proposal says the DELIB will be inserted through a formal-approval packet
  at
  `.groundtruth/formal-artifact-approvals/2026-05-04-delib-s330-agent-red-migration-pending-waiver.json`
  (`bridge/gtkb-isolation-018-pending-migration-waiver-001.md` lines 93 and
  142).
- The proposal's own test plan maps `T-packet-1` to the
  "formal-artifact-approval gate (per `GOV-ARTIFACT-APPROVAL-001`)" and its
  Specifications-Tests Mapping lists `GOV-ARTIFACT-APPROVAL-001` as directly
  covered (`bridge/gtkb-isolation-018-pending-migration-waiver-001.md` lines
  162 and 179).
- The `Specification Links` section does not cite
  `GOV-ARTIFACT-APPROVAL-001`; it cites formal-approval packet files and
  conventions, but not the governing specification
  (`bridge/gtkb-isolation-018-pending-migration-waiver-001.md` lines 27-55).
- The MemBase query confirms `GOV-ARTIFACT-APPROVAL-001` exists and is
  relevant: latest version v2, `type=governance`, `status=verified`.

Risk / impact:

The proposal's implementation path is a formal artifact mutation. If the
approval gate is only tested but not listed as a governing spec, the bridge
record violates the mandatory spec-linkage rule's requirement to cite every
relevant governing specification.

Recommended action:

Revise the `Specification Links` section to cite `GOV-ARTIFACT-APPROVAL-001`
and explicitly state how the proposed packet fields and owner-approval flow
satisfy it. Keep `T-packet-1` mapped to that spec.

### F2 - Proposed DELIB text implies owner approval through the bridge before it exists

Evidence:

- The proposed `source_ref` includes
  `S331-2026-05-04-bridge-gtkb-isolation-018-pending-migration-waiver-001.md`
  (`bridge/gtkb-isolation-018-pending-migration-waiver-001.md` line 89).
- The proposed DELIB body says it is authorized by "S331 explicit confirmation
  via this bridge thread" (`bridge/gtkb-isolation-018-pending-migration-waiver-001.md`
  line 98).
- The acceptance criteria correctly require an owner-approved formal-approval
  packet before verification
  (`bridge/gtkb-isolation-018-pending-migration-waiver-001.md` lines 187-197).

Risk / impact:

Codex `GO` is not owner approval. Leaving the proposed body as written would
allow the eventual DELIB text to blur the distinction between review approval
and owner approval, which is especially risky because this artifact is itself a
waiver authorizing temporary exception behavior.

Recommended action:

Revise the proposed DELIB text so authorization points only to owner-approved
records: S330 for the source rule and the future formal-approval packet for the
waiver body. For example, replace "S331 explicit confirmation via this bridge
thread" with wording that the waiver becomes active only after owner approval
is captured in the formal-approval packet, and ensure `source_ref` references
the owner-approval evidence rather than implying the bridge review is that
evidence.

## Positive Evidence

- The mechanical applicability preflight passes with no missing required or
  advisory specs.
- The proposal correctly addresses the bootstrap defect from
  `bridge/gtkb-isolation-018-agent-red-file-migration-002.md` by placing the
  waiver DELIB before any migration sub-slice relies on it.
- The proposed DELIB includes the required waiver elements: scope, expiry, and
  residual risk.

## Decision

NO-GO.

Revise the proposal to cite `GOV-ARTIFACT-APPROVAL-001` in `Specification
Links`, carry that citation into the spec-to-test mapping, and adjust the
proposed DELIB authorization/source text so owner approval is not implied until
the formal-approval packet actually exists.
