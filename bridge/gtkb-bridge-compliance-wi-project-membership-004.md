NO-GO

# Loyal Opposition Review - Bridge Compliance Gate WI-Project Membership Check REVISED-1

Reviewed: 2026-05-15 UTC
Reviewer: Codex Loyal Opposition (harness A)
Reviewed document: `bridge/gtkb-bridge-compliance-wi-project-membership-003.md`
Verdict: NO-GO

## Claim

The revised membership and authorization semantics close the prior active-membership
gap. The proposal is still not ready for GO because it authorizes edits to the
active bridge-compliance hook while omitting the packaged template hook that the
existing parity regression test requires to remain byte-identical.

## Prior Deliberations

Command:

```powershell
$env:PYTHONPATH='groundtruth-kb/src'; python -m groundtruth_kb deliberations search "DCL-WORK-ITEM-MUST-BELONG-TO-APPROVED-PROJECT-001 WI-3315 bridge-compliance work item project membership revised" --limit 8
```

Relevant result:

- `DELIB-S350-SPEC-PROJECT-WI-BRIDGE-ENFORCEMENT` records the owner directive
  for mechanical enforcement of the specification -> project -> work item ->
  bridge chain, including the Soft variant for
  `DCL-WORK-ITEM-MUST-BELONG-TO-APPROVED-PROJECT-001`.

No prior deliberation found that waives hook-template parity.

## Applicability Preflight

Command:

```powershell
python scripts/bridge_applicability_preflight.py --bridge-id gtkb-bridge-compliance-wi-project-membership
```

Observed:

```text
## Applicability Preflight

- packet_hash: `sha256:c208b09a9d885078466ae7796dd255b08f539e51f45832de2211e66e3b0a9343`
- bridge_document_name: `gtkb-bridge-compliance-wi-project-membership`
- content_source: `indexed_operative`
- content_file: `bridge/gtkb-bridge-compliance-wi-project-membership-003.md`
- operative_file: `bridge/gtkb-bridge-compliance-wi-project-membership-003.md`
- preflight_passed: `true`
- missing_required_specs: []
- missing_advisory_specs: ["ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001", "DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001", "GOV-ARTIFACT-ORIENTED-GOVERNANCE-001"]

| Spec | Severity | Cited | Matched By |
|------|----------|-------|------------|
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | `advisory` | `no` | content:artifact, content:deliberation, content:MemBase |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | `advisory` | `no` | content:deferred, content:blocked, content:verified |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | `blocking` | `yes` | doc:*, content:Specification Links, content:implementation proposal, content:bridge proposal |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | `blocking` | `yes` | doc:*, content:VERIFIED, content:verification, content:spec-to-test, content:Specification-Derived Verification |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | `advisory` | `no` | content:owner decision, content:requirement, content:specification, content:ADR, content:DCL, content:work item, content:backlog |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | `blocking` | `yes` | doc:*, path:bridge/** |
```

## Clause Applicability

Command:

```powershell
python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-bridge-compliance-wi-project-membership
```

Observed:

```text
## Clause Applicability (Slice 2; mandatory gate)

- Bridge id: `gtkb-bridge-compliance-wi-project-membership`
- Operative file: `bridge\gtkb-bridge-compliance-wi-project-membership-003.md`
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

### F1 - The hook template is omitted from authorized scope

Severity: P1

Evidence:

- The revised proposal authorizes only `.claude/hooks/bridge-compliance-gate.py`
  and the new membership test file in `target_paths`
  (`bridge/gtkb-bridge-compliance-wi-project-membership-003.md:18`).
- The implementation scope lands new behavior in `.claude/hooks/bridge-compliance-gate.py`
  (`bridge/gtkb-bridge-compliance-wi-project-membership-003.md:75`).
- Existing parity coverage defines both the active hook and the packaged
  template hook:
  `platform_tests/hooks/test_bridge_compliance_gate_hard_block_workspace.py:24`
  and `platform_tests/hooks/test_bridge_compliance_gate_hard_block_workspace.py:25`.
- That test hashes both files and asserts byte-for-byte equality at
  `platform_tests/hooks/test_bridge_compliance_gate_hard_block_workspace.py:56`
  through `platform_tests/hooks/test_bridge_compliance_gate_hard_block_workspace.py:61`.

Deficiency rationale:

If Prime edits only `.claude/hooks/bridge-compliance-gate.py`, the existing
hard-block workspace parity test will fail. If Prime also edits
`groundtruth-kb/templates/hooks/bridge-compliance-gate.py`, that edit would be
outside this proposal's current `target_paths`. Either route leaves the GO
packet internally inconsistent.

Impact:

The implementation would either regress the package-template parity contract or
require an implementation edit not authorized by the proposal. Because this is a
hook-level governance gate, that is a blocking review issue.

Recommended action:

Revise `target_paths` to include
`groundtruth-kb/templates/hooks/bridge-compliance-gate.py`, require the active
hook and template hook to receive the same behavior change, and include the
existing parity regression test in the required verification command.

### F2 - Existing regression tests are acceptance criteria but not execution criteria

Severity: P2

Evidence:

- The proposal says there must be no regression in
  `test_bridge_compliance_gate_hard_block_workspace.py` and
  `test_codex_bridge_compliance_gate.py`
  (`bridge/gtkb-bridge-compliance-wi-project-membership-003.md:151`).
- The verification plan executes only
  `platform_tests/hooks/test_bridge_compliance_gate_wi_project_membership.py`
  (`bridge/gtkb-bridge-compliance-wi-project-membership-003.md:144`).

Deficiency rationale:

The proposal correctly names the existing regression surfaces, but the proposed
execution command omits them. That leaves the post-implementation report an easy
path to report the new tests as passing while not actually proving the stated
no-regression criteria.

Impact:

Template parity, Codex hook invocation behavior, or existing workspace
hard-block behavior could drift without being covered by the implementation
report.

Recommended action:

Make the verification command include at least:

```powershell
python -m pytest platform_tests/hooks/test_bridge_compliance_gate_wi_project_membership.py platform_tests/hooks/test_bridge_compliance_gate_hard_block_workspace.py platform_tests/scripts/test_codex_bridge_compliance_gate.py -v
```

## Positive Evidence

- The revised SQL and Python checks address the prior active-membership gap.
- The proposal keeps both cited DCLs at `specified` until post-implementation
  verification.
- The proposal cites the governing S350 owner-decision deliberation.
- Bridge applicability preflight passes with no missing required specs.
- Mandatory clause preflight exits successfully with zero blocking gaps.

## Required Revision

File a revised proposal that:

1. Adds `groundtruth-kb/templates/hooks/bridge-compliance-gate.py` to
   `target_paths`.
2. Requires active/template hook parity for the new membership behavior.
3. Expands the required verification command to execute the existing parity and
   Codex hook regression tests along with the new membership tests.
4. Updates the WI-3314 dependency text to reference the latest state instead of
   the stale `bridge/gtkb-bridge-compliance-project-metadata-003.md` revision,
   or explains why the stale reference is intentionally historical.

File bridge scan: 1 entry processed.
