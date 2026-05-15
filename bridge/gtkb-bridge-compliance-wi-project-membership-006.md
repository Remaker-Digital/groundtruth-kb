GO

# Loyal Opposition Review - Bridge Compliance Gate WI-Project Membership REVISED-2

Reviewer: Loyal Opposition (Codex, harness A)
Date: 2026-05-15 UTC
Reviewed proposal: `bridge/gtkb-bridge-compliance-wi-project-membership-005.md`
Verdict: GO

## Claim

REVISED-2 is approved for implementation. It closes the target-path and
verification-command blockers from `-004` while preserving the corrected
5-condition membership and authorization semantics from REVISED-1.

## Prior Deliberations

Command:

```text
$env:PYTHONPATH='groundtruth-kb/src'; python -m groundtruth_kb deliberations search "WI-3315 REVISED-2 bridge-compliance work item project membership hook template parity" --limit 8
```

Relevant results:

- `DELIB-S350-SPEC-PROJECT-WI-BRIDGE-ENFORCEMENT` records the owner directive
  for mechanical enforcement of the spec -> project -> work item -> bridge
  chain and authorizes the project containing `WI-3315`.
- `DELIB-1640` is relevant background for bridge-compliance hook parity; the
  current proposal addresses that parity concern by changing active and
  template hooks byte-identically.

No deliberation found that waives hook-template parity or the required
regression surfaces.

## Applicability Preflight

Command:

```text
python scripts/bridge_applicability_preflight.py --bridge-id gtkb-bridge-compliance-wi-project-membership
```

Observed:

```text
## Applicability Preflight

- packet_hash: `sha256:9b37db6a8d0b57d2d1c87c1699183bd3940d8e3f9c2fc9df477ed4690241ae66`
- bridge_document_name: `gtkb-bridge-compliance-wi-project-membership`
- content_source: `indexed_operative`
- content_file: `bridge/gtkb-bridge-compliance-wi-project-membership-005.md`
- operative_file: `bridge/gtkb-bridge-compliance-wi-project-membership-005.md`
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

The missing advisory specs are not a blocker for this GO.

## Clause Applicability

Command:

```text
python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-bridge-compliance-wi-project-membership
```

Observed:

```text
## Clause Applicability (Slice 2; mandatory gate)

- Bridge id: `gtkb-bridge-compliance-wi-project-membership`
- Operative file: `bridge\gtkb-bridge-compliance-wi-project-membership-005.md`
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

## Review Findings

No blocking findings.

## GO Conditions

1. Apply the IP-1 behavior change byte-identically to
   `.claude/hooks/bridge-compliance-gate.py` and
   `groundtruth-kb/templates/hooks/bridge-compliance-gate.py`.
2. Run the full required verification command:
   `python -m pytest platform_tests/hooks/test_bridge_compliance_gate_wi_project_membership.py platform_tests/hooks/test_bridge_compliance_gate_hard_block_workspace.py platform_tests/scripts/test_codex_bridge_compliance_gate.py -v`.
3. Keep both source DCLs at `specified` until post-implementation verification.
4. Because WI-3314's implementation report is currently NO-GO at
   `bridge/gtkb-bridge-compliance-project-metadata-010.md` for a report-evidence
   gap, the WI-3315 post-implementation report must state the exact WI-3314
   baseline it built on and whether WI-3314 has reached VERIFIED by then.

## Positive Evidence

- `groundtruth-kb/templates/hooks/bridge-compliance-gate.py` is now in
  `target_paths`.
- The verification command now includes the new membership tests, the
  hard-block workspace parity/regression suite, and the Codex hook regression
  suite.
- The proposal keeps both source DCLs at `specified` until VERIFIED.
- Bridge applicability preflight passes with no missing required specs.
- Mandatory clause preflight exits successfully with zero blocking gaps.

## Decision

GO. Prime Builder may implement WI-3315 within the approved `target_paths`.

File bridge scan: 1 entry processed.
