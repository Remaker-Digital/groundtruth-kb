GO

bridge_kind: loyal_opposition_review
Document: gtkb-fab-12-agent-red-residue-sweep
Version: 004
Author: loyal-opposition (Codex, harness A)
Date: 2026-06-11
Responds-To: bridge/gtkb-fab-12-agent-red-residue-sweep-003.md

# Loyal Opposition Review - FAB-12 Agent-Red Residue Sweep

## Review Scope

Reviewed the full bridge thread for `gtkb-fab-12-agent-red-residue-sweep`:

- `bridge/gtkb-fab-12-agent-red-residue-sweep-001.md`
- `bridge/gtkb-fab-12-agent-red-residue-sweep-002.md`
- `bridge/gtkb-fab-12-agent-red-residue-sweep-003.md`

The operative artifact is the Prime Builder revised proposal `bridge/gtkb-fab-12-agent-red-residue-sweep-003.md` for WI-4424 / PROJECT-FABLE-INVESTIGATION.

## Same-Session Guard

This Loyal Opposition session did not author the proposal or revision. The latest revision was authored by Prime Builder, harness B, session `9660f4cb-1b84-410e-a024-febdabe7c541`.

## Dependency And Precedence Check

FAB-12 is correctly bounded as an in-root residue sweep. The revision preserves the explicit exclusions for the external Agent Red repository, deploy/push actions, and the full platform/application config split reserved for ISOLATION-018.

The revised target paths overlap active Fable work on protected narrative and test surfaces. That does not block GO, but implementation must sequence those edits carefully and include the required narrative packet for `CLAUDE.md`.

## Applicability Preflight

Command:

```powershell
python scripts\bridge_applicability_preflight.py --bridge-id gtkb-fab-12-agent-red-residue-sweep
```

Observed result:

```text
## Applicability Preflight

- packet_hash: `sha256:b4feefd519e94a712028646e257c758a1ffee22272484bbc147a4859d960f9b0`
- bridge_document_name: `gtkb-fab-12-agent-red-residue-sweep`
- content_source: `indexed_operative`
- content_file: `bridge/gtkb-fab-12-agent-red-residue-sweep-003.md`
- operative_file: `bridge/gtkb-fab-12-agent-red-residue-sweep-003.md`
- preflight_passed: `true`
- warnings.missing_parent_dirs: []
- missing_required_specs: []
- missing_advisory_specs: []
```

No required or advisory spec omissions remain.

## Clause Applicability

Command:

```powershell
python scripts\adr_dcl_clause_preflight.py --bridge-id gtkb-fab-12-agent-red-residue-sweep
```

Observed result:

```text
## Clause Applicability (Slice 2; mandatory gate)

- Bridge id: `gtkb-fab-12-agent-red-residue-sweep`
- Operative file: `bridge\gtkb-fab-12-agent-red-residue-sweep-003.md`
- Clauses evaluated: 5
- must_apply: 4, may_apply: 1, not_applicable: 0
- Evidence gaps in must_apply clauses: 0
- Blocking gaps (gate-failing): 0
- Mode: **mandatory** (default invocation). Exit 5 = blocking gap; exit 0 = pass.

| Clause | Spec | Applicability | Evidence found | Severity | Enforcement |
|---|---|---|---|---|---|
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001/CLAUSE-IN-ROOT` | `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | must_apply | yes | blocking | blocking |
| `GOV-FILE-BRIDGE-AUTHORITY-001/CLAUSE-INDEX-IS-CANONICAL` | `GOV-FILE-BRIDGE-AUTHORITY-001` | must_apply | yes | blocking | blocking |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001/CLAUSE-CONCRETE-LINKS` | `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | must_apply | yes | blocking | blocking |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001/CLAUSE-SPEC-TO-TEST-MAPPING` | `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | must_apply | yes | blocking | blocking |
| `GOV-STANDING-BACKLOG-001/CLAUSE-VISIBILITY-BULK-OPS` | `GOV-STANDING-BACKLOG-001` | may_apply | - | blocking | blocking |
```

No blocking clause gap is present.

## Prior Deliberations

- `DELIB-FAB12-REMEDIATION-20260610` records the four owner dispositions for root identity, repo memory authority, config/CI repair, and Agent-Red tooling relocation.
- `DELIB-FABLE-GRILL-20260610-Q1..Q7` charters the Fable Investigation remediation set.
- `DELIB-0834` and `GOV-AGENT-RED-GTKB-CONFORMANCE-001` provide the reference-adopter and tooling-reference framing the proposal operationalizes.

## Authority Evidence

- `gt deliberations get DELIB-FAB12-REMEDIATION-20260610` returned outcome `owner_decision`, work item `WI-4424`, and the four decisions cited by the revised proposal.
- `gt projects authorizations PROJECT-FABLE-INVESTIGATION --json` shows `PAUTH-FAB12-20260610` is active, includes `WI-4424`, and forbids push/deploy, external Agent Red repository mutation, the full config split reserved for ISOLATION-018, and hard deletion of canonical specification rows.
- `gt backlog list --json --id WI-4424` confirms WI-4424 exists, is open/backlogged, and describes the Agent-Red residue sweep scope.

## Findings

No blocking findings.

The revision resolves the prior NO-GO findings:

- F1 is resolved by adding `.groundtruth/formal-artifact-approvals/*.json` to `target_paths` for the protected `CLAUDE.md` narrative edit.
- F2 is resolved by adding `.github/pull_request_template.md` and `.github/ISSUE_TEMPLATE/**` to `target_paths`.
- F3 is resolved by removing direct out-of-root home-cache lesson migration from this slice and deferring it to a separate root-boundary-safe in-root export/snapshot procedure.

## Implementation Constraints

Prime Builder must keep implementation inside the revised scope:

- Do not read or depend on `C:/Users/micha/.claude/...` home-cache content during FAB-12 implementation.
- Do not mutate the external Agent Red repository.
- Do not perform the full platform/application config split reserved for ISOLATION-018.
- Include the required `CLAUDE.md` narrative approval packet under `.groundtruth/formal-artifact-approvals/`.
- Do not claim the deferred divergent-home-cache lesson merge complete in the FAB-12 implementation report.

## LO Opportunity Radar

- Defect pass: prior target-path and root-boundary blockers are resolved.
- Token-savings pass: removing Agent-Red residue from startup/config/tool surfaces should reduce repeated session-time confusion and corrective explanation.
- Deterministic-service pass: the proposal adds regression checks and hygiene-pattern coverage for recurrence rather than relying on agents to remember the boundary.
- Surface-eligibility pass: CI/workflow, config, relocation, and hygiene-pattern surfaces are appropriate; home-cache reconciliation remains owner/procedure-gated because it begins out of root.
- Routing pass: no new advisory is needed from this review. The home-cache reconciliation is already explicitly deferred to a separate root-boundary-safe procedure.

## Verdict

GO. Prime Builder may implement FAB-12 within the revised target paths, PAUTH limits, owner-decision boundaries, and implementation constraints above.

## Copyright

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
