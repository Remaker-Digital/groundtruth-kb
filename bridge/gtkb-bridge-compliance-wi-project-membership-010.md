VERIFIED

# Loyal Opposition Verification - Bridge Compliance Gate WI-Project Membership Check

Reviewer: Codex (Loyal Opposition, harness A)
Date: 2026-05-15 UTC
Reviewed report: `bridge/gtkb-bridge-compliance-wi-project-membership-009.md`
Verdict: VERIFIED

## Claim

The WI-3315 implementation report is verified. The live MemBase
work-item/project membership and project-authorization check is implemented
within the reviewed scope: NEW/REVISED implementation bridge proposals are
hard-blocked when the cited Work Item is not an active member of the cited
Project, or when the cited Project Authorization is missing, inactive, expired,
project-mismatched, excludes the Work Item, or fails an include-list check.
Verdict files and declared non-implementation bridge kinds remain exempt.

## Review Scope

- Read live `bridge/INDEX.md`; latest status for
  `gtkb-bridge-compliance-wi-project-membership` was `NEW:
  bridge/gtkb-bridge-compliance-wi-project-membership-009.md`, actionable for
  Loyal Opposition.
- Read the full thread through `bridge/gtkb-bridge-compliance-wi-project-membership-009.md`
  with `.claude/skills/bridge/helpers/show_thread_bridge.py`.
- Read `.claude/rules/file-bridge-protocol.md`,
  `.claude/rules/codex-review-gate.md`,
  `.claude/rules/deliberation-protocol.md`,
  `.claude/rules/operating-model.md`,
  `.claude/rules/loyal-opposition.md`, and
  `.claude/rules/report-depth-prime-builder-context.md`.
- Ran the mandatory applicability and ADR/DCL clause preflights.
- Searched the Deliberation Archive before verification.
- Re-ran the report's verification command and inspected the implemented hook
  and tests.

## Prior Deliberations

Commands:

```text
$env:PYTHONPATH='groundtruth-kb/src'; $env:PYTHONIOENCODING='utf-8'; python -m groundtruth_kb deliberations search 'WI-3315 bridge compliance work item project membership post implementation verification CLAUSE-BRIDGE-WI-PROJECT-MEMBERSHIP DELIB-S350' --limit 10 --json
```

Relevant result:

- `DELIB-S350-SPEC-PROJECT-WI-BRIDGE-ENFORCEMENT` records the owner directive
  for mechanical enforcement of the spec -> project -> work item -> bridge
  chain, authorizes project
  `GTKB-SPEC-PROJECT-WI-BRIDGE-ENFORCEMENT-001`, includes `WI-3315`, and records
  the Soft variant for `DCL-WORK-ITEM-MUST-BELONG-TO-APPROVED-PROJECT-001`.

No prior deliberation found waives the mandatory verification gate or
contradicts verification of this report.

## Applicability Preflight

Command:

```text
python scripts\bridge_applicability_preflight.py --bridge-id gtkb-bridge-compliance-wi-project-membership
```

Observed:

```text
## Applicability Preflight

- packet_hash: `sha256:31d23e3dcd3ec14706c2588e80c69cb0e589e2b8b27ee4d2841f9f185b9e9786`
- bridge_document_name: `gtkb-bridge-compliance-wi-project-membership`
- content_source: `indexed_operative`
- content_file: `bridge/gtkb-bridge-compliance-wi-project-membership-009.md`
- operative_file: `bridge/gtkb-bridge-compliance-wi-project-membership-009.md`
- preflight_passed: `true`
- missing_required_specs: []
- missing_advisory_specs: ["ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001", "DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001", "GOV-ARTIFACT-ORIENTED-GOVERNANCE-001"]

| Spec | Severity | Cited | Matched By |
|------|----------|-------|------------|
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | `advisory` | `no` | content:artifact, content:deliberation, content:MemBase |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | `advisory` | `no` | content:blocked, content:verified |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | `blocking` | `yes` | doc:*, content:Specification Links, content:implementation proposal |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | `blocking` | `yes` | doc:*, content:VERIFIED, content:verification, content:spec-to-test, content:Specification-Derived Verification |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | `advisory` | `no` | content:owner decision, content:requirement, content:specification, content:ADR, content:DCL, content:work item, content:backlog |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | `blocking` | `yes` | doc:*, path:bridge/** |
```

The missing advisory specs are non-blocking for this verification.

## Clause Applicability

Command:

```text
python scripts\adr_dcl_clause_preflight.py --bridge-id gtkb-bridge-compliance-wi-project-membership
```

Observed:

```text
## Clause Applicability (Slice 2; mandatory gate)

- Bridge id: `gtkb-bridge-compliance-wi-project-membership`
- Operative file: `bridge\gtkb-bridge-compliance-wi-project-membership-009.md`
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

## Verification Commands

Command re-run:

```text
python -m pytest platform_tests/hooks/test_bridge_compliance_gate_wi_project_membership.py platform_tests/hooks/test_bridge_compliance_gate_hard_block_workspace.py platform_tests/scripts/test_codex_bridge_compliance_gate.py -q
```

Observed result:

- `platform_tests/hooks/test_bridge_compliance_gate_wi_project_membership.py`
  + `platform_tests/hooks/test_bridge_compliance_gate_hard_block_workspace.py`
  + `platform_tests/scripts/test_codex_bridge_compliance_gate.py`: 33 passed
  in 35.22s.

## Implementation Evidence

- Active hook and packaged template hook are byte-identical by SHA-256:
  `5FA2BA5AF2BCF79E26562473AD923C3BB3D24CF676E2E6AD385CD43A4A4B3D35` for
  `.claude/hooks/bridge-compliance-gate.py` and
  `groundtruth-kb/templates/hooks/bridge-compliance-gate.py`.
- The membership gate extracts project metadata and validates the live MemBase
  membership and authorization state at
  `.claude/hooks/bridge-compliance-gate.py:120`,
  `.claude/hooks/bridge-compliance-gate.py:283`, and
  `.claude/hooks/bridge-compliance-gate.py:309`.
- The validator checks active membership, authorization status, expiration,
  excluded work items, and include-list coverage at
  `.claude/hooks/bridge-compliance-gate.py:332`,
  `.claude/hooks/bridge-compliance-gate.py:339`,
  `.claude/hooks/bridge-compliance-gate.py:341`,
  `.claude/hooks/bridge-compliance-gate.py:350`,
  `.claude/hooks/bridge-compliance-gate.py:352`,
  `.claude/hooks/bridge-compliance-gate.py:354`, and
  `.claude/hooks/bridge-compliance-gate.py:356`.
- `_deny_reason_for_content` hard-blocks proposals with a specific membership
  gap token and echoes the cited WI, Project, and Project Authorization at
  `.claude/hooks/bridge-compliance-gate.py:595`.
- The membership tests cover no membership, inactive membership, missing
  authorization, inactive authorization, expired authorization, excluded WI,
  missing include-list coverage, active happy path, verdict-file bypass,
  cited-project mismatch, and diagnostic condition tokens at
  `platform_tests/hooks/test_bridge_compliance_gate_wi_project_membership.py:130`,
  `platform_tests/hooks/test_bridge_compliance_gate_wi_project_membership.py:136`,
  `platform_tests/hooks/test_bridge_compliance_gate_wi_project_membership.py:142`,
  `platform_tests/hooks/test_bridge_compliance_gate_wi_project_membership.py:149`,
  `platform_tests/hooks/test_bridge_compliance_gate_wi_project_membership.py:159`,
  `platform_tests/hooks/test_bridge_compliance_gate_wi_project_membership.py:169`,
  `platform_tests/hooks/test_bridge_compliance_gate_wi_project_membership.py:179`,
  `platform_tests/hooks/test_bridge_compliance_gate_wi_project_membership.py:191`,
  `platform_tests/hooks/test_bridge_compliance_gate_wi_project_membership.py:202`,
  `platform_tests/hooks/test_bridge_compliance_gate_wi_project_membership.py:211`,
  and `platform_tests/hooks/test_bridge_compliance_gate_wi_project_membership.py:222`.
- The GO condition for the hard-block workspace helper is satisfied:
  `_pending_preflight_content()` declares `bridge_kind: spec_intake` at
  `platform_tests/hooks/test_bridge_compliance_gate_hard_block_workspace.py:285`
  and `platform_tests/hooks/test_bridge_compliance_gate_hard_block_workspace.py:302`,
  allowing those tests to exercise pending preflight behavior without depending
  on live MemBase membership rows.

## Findings

No blocking findings.

The implementation report carries forward linked specifications, includes a
spec-to-test mapping, reports executed commands, and the exact claimed
verification command passes in the live checkout. Both source DCLs remain
`specified`, matching the report's lifecycle claim.

## Decision

VERIFIED.

