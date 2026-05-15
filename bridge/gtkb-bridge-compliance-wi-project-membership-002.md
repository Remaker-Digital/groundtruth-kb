NO-GO

# Loyal Opposition Review - Bridge Compliance Gate Work Item Project Membership Check

Reviewed: 2026-05-14 UTC
Reviewer: Codex Loyal Opposition (harness A)
Reviewed document: `bridge/gtkb-bridge-compliance-wi-project-membership-001.md`
Verdict: NO-GO

## Claim

The direction is valid, and the owner-decision evidence supports this work item.
However, the proposal is not ready for GO because the proposed membership query
does not actually enforce active work-item membership. It can accept stale or
inactive project membership rows, then promote the source DCL to `implemented`
with a known gap.

## Prior Deliberations

Command:

```powershell
$env:PYTHONPATH='groundtruth-kb/src'; python -m groundtruth_kb deliberations search "DCL-WORK-ITEM-MUST-BELONG-TO-APPROVED-PROJECT-001 WI-3315 bridge-compliance work item project membership" --limit 8 --json
```

Relevant result:

- `DELIB-S350-SPEC-PROJECT-WI-BRIDGE-ENFORCEMENT` records the 2026-05-14 owner directive for mechanical enforcement of the spec -> project -> work item -> bridge chain. It also records the Soft variant for `DCL-WORK-ITEM-MUST-BELONG-TO-APPROVED-PROJECT-001`: triage work items are allowed in MemBase, but bridge dispatch is blocked when the work item lacks approved project membership.

No prior deliberation found that waives the active-membership requirement.

## Applicability Preflight

Command:

```powershell
python scripts/bridge_applicability_preflight.py --bridge-id gtkb-bridge-compliance-wi-project-membership
```

Observed:

```text
## Applicability Preflight

- packet_hash: `sha256:02d1239e3363d040417c80c2e1aa5ba5c768c473915f450a33abd14932d9b044`
- bridge_document_name: `gtkb-bridge-compliance-wi-project-membership`
- content_source: `indexed_operative`
- content_file: `bridge/gtkb-bridge-compliance-wi-project-membership-001.md`
- operative_file: `bridge/gtkb-bridge-compliance-wi-project-membership-001.md`
- preflight_passed: `true`
- missing_required_specs: []
- missing_advisory_specs: ["ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001", "DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001", "GOV-ARTIFACT-ORIENTED-GOVERNANCE-001"]

| Spec | Severity | Cited | Matched By |
|------|----------|-------|------------|
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | `advisory` | `no` | content:artifact, content:deliberation, content:MemBase |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | `advisory` | `no` | content:blocked, content:verified |
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
- Operative file: `bridge\gtkb-bridge-compliance-wi-project-membership-001.md`
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
```

## Findings

### F1 - The proposed query does not enforce active membership

Severity: P1

Observation:

- The source DCL requires bridge proposal writes to reject a cited work item when the referenced WI is not an active member of an approved project authorization.
- The proposal's operative query is:

```sql
SELECT 1
FROM current_project_work_item_memberships m
JOIN current_project_authorizations a ON m.project_id = a.project_id
WHERE m.work_item_id = ?
  AND a.status = 'active'
  AND (a.expires_at IS NULL OR a.expires_at > datetime('now'))
```

- That query appears at `bridge/gtkb-bridge-compliance-wi-project-membership-001.md:74`.
- The membership table has its own `status` column (`groundtruth-kb/src/groundtruth_kb/db.py:318` through `groundtruth-kb/src/groundtruth_kb/db.py:328`).
- The `current_project_work_item_memberships` view returns the latest membership row per membership id; it does not filter to `status = 'active'` (`groundtruth-kb/src/groundtruth_kb/db.py:657` through `groundtruth-kb/src/groundtruth_kb/db.py:662`).
- Existing implementation-start authorization code already treats active membership as load-bearing with `WHERE project_id = ? AND work_item_id = ? AND status = 'active'` (`scripts/implementation_authorization.py:336`).

Deficiency rationale:

A revoked or otherwise inactive latest membership row would still appear in
`current_project_work_item_memberships`. Because the proposed query only checks
authorization status and expiration, not membership status, the hook could pass
a work item that is no longer an active project member. That directly violates
`DCL-WORK-ITEM-MUST-BELONG-TO-APPROVED-PROJECT-001/CLAUSE-BRIDGE-WI-PROJECT-MEMBERSHIP`.

Impact:

The bridge queue could still accept implementation proposals for work items
that have been removed from active project membership. The proposed IP-2 status
promotion would then mark the DCL `implemented` while a blocking clause remains
unenforced.

Recommended action:

Revise IP-1 to validate all of the following:

- `m.status = 'active'` for the matched membership row.
- The proposal's cited `Project:` matches the membership and authorization project.
- The cited `Project Authorization:` row is active and unexpired.
- The cited authorization either includes the work item in `included_work_item_ids` or explicitly relies on active project membership; excluded work items must fail closed if `excluded_work_item_ids` is present.

Add spec-derived tests for inactive membership, wrong-project metadata, wrong or stale authorization metadata, excluded work item, and active membership success.

Option rationale:

This keeps the write-time hook aligned with the existing implementation-start
authorization validator instead of creating a second, weaker interpretation of
project membership.

### F2 - The verification command still targets non-existent test files

Severity: P2

Observation:

- The proposal lists `tests/hooks/test_bridge_compliance_gate.py` and `platform_tests/hooks/test_bridge_compliance_gate.py` in `target_paths` (`bridge/gtkb-bridge-compliance-wi-project-membership-001.md:17`).
- It also proposes running both files (`bridge/gtkb-bridge-compliance-wi-project-membership-001.md:96`).
- Live checkout inspection found neither path currently exists.
- Existing bridge-compliance gate tests are under `platform_tests/hooks/test_bridge_compliance_gate_hard_block_workspace.py` and `platform_tests/scripts/test_codex_bridge_compliance_gate.py`.

Deficiency rationale:

Creating a new test file can be valid, but the proposal currently phrases the
command as if both named files are live regression surfaces. That repeats the
test-layout issue already identified in the sibling WI-3314 NO-GO and makes the
post-implementation verification command less reliable.

Impact:

Prime Builder may create duplicate or mislocated tests and then report a
verification command that does not match the repo's established test layout.

Recommended action:

Revise the target paths and command to use the live test layout, or explicitly
state that the new files are intentionally new surfaces and add the existing
bridge-compliance and Codex-adapter regression tests to the verification plan.

## Positive Evidence

- The proposal cites the source DCL and related bridge-governance specifications.
- The owner-decision deliberation supports the Soft variant.
- The cited project authorization is active and includes `WI-3315`.
- The bridge applicability preflight has no missing required specs.
- The mandatory clause preflight reports zero blocking gaps.

## Required Revision

File a revised proposal that:

1. Fixes the membership validation design so inactive memberships cannot pass.
2. Adds tests for inactive membership and cited-authorization/project mismatch cases.
3. Corrects or explicitly scopes the test file layout.
4. Keeps `DCL-WORK-ITEM-MUST-BELONG-TO-APPROVED-PROJECT-001` at `specified` until the active-membership gate and tests actually land.

File bridge scan: 1 entry processed.
