WITHDRAWN

bridge_kind: operational_state_change
Document: gtkb-wi5121-formalize-root-boundary-exception-carriers
Version: 003
Date: 2026-07-09 UTC
Responds to: bridge/gtkb-wi5121-formalize-root-boundary-exception-carriers-002.md

Project: PROJECT-GTKB-CANONICAL-AUTHORITY-DRIFT-REMEDIATION
Work Item: WI-5121

# Scope Withdrawal - WI-5121 Root-Boundary Exception Carriers

## Owner Decision

`DELIB-202665933` directs retirement and replacement of WI-5121. The matching
owner-approved packet is
`.groundtruth/formal-artifact-approvals/2026-07-09-WI-5121-retirement.json`.

## Rationale

The approved proposal is not implementable as written: it requires canonical
carrier creation but omits `groundtruth.db` from `target_paths` and declares
`kb_mutation_in_scope: false`. The live implementation-start gate does not
allow project authorization to broaden a GO'd proposal's target scope.

## Disposition

No implementation was performed under this GO. This withdrawal terminalizes
the obsolete bridge thread. A successor work item and NEW proposal will cover
the canonical MemBase carriers, narrative and template changes, formal
approval, and specification-derived verification.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` - preserves role-correct, append-only bridge authority.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` - routes the scope defect to a governed successor.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - prevents a GO from omitting required mutation targets.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - preserves verification obligations for the successor.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - requires fresh project/work linkage for the successor.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - governs retirement and replacement lifecycle capture.
- `SPEC-INTAKE-bb25be` - requires canonical carriers rather than DELIB-only authority.
- `GOV-ENV-LOCAL-AUTHORITY-001` - remains relevant to the root-boundary exception set.

## Prior Deliberations

- `DELIB-202665929` - diagnosis establishing the root-boundary carrier gap.
- `DELIB-202665930` - initial project authorization.
- `DELIB-202665933` - owner decision to retire and replace this insufficiently scoped work.

## Owner Decisions / Input

- `DELIB-202665933` - owner-approved withdrawal and successor path.

## Specification-Derived Verification

| Spec | Verification |
| --- | --- |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | Confirm the withdrawn proposal omitted `groundtruth.db` while requiring canonical carrier creation. |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | Confirm this entry is terminal `WITHDRAWN` and WI-5121 is retired with an owner-approved packet. |
| `SPEC-INTAKE-bb25be` | Confirm the successor proposal covers every carrier, narrative, and template mutation. |
