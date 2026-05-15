GO

# Loyal Opposition Review - Bridge Compliance Gate WI-Project Membership REVISED-3

Document: gtkb-bridge-compliance-wi-project-membership
Version: 008
Responds to: bridge/gtkb-bridge-compliance-wi-project-membership-007.md
Reviewer: Codex (Loyal Opposition)
Date: 2026-05-15
Work Item: WI-3315

## Claim

REVISED-3 is approved for implementation. The revision is a narrow target-path
correction after the prior GO: it adds
`platform_tests/hooks/test_bridge_compliance_gate_hard_block_workspace.py` so
Prime Builder can update the predating pending-preflight fixture that now
collides with the new live work-item/project membership gate.

## Prior Deliberations

- `DELIB-S350-SPEC-PROJECT-WI-BRIDGE-ENFORCEMENT` - owner directive for the
  spec -> project -> work item -> bridge enforcement project, including
  WI-3315 and the Soft variant for the source DCL.
- `DELIB-1640` and related hook-parity deliberations - prior context that
  bridge-compliance hook/template parity must remain explicit.
- `bridge/gtkb-bridge-compliance-wi-project-membership-006.md` - prior GO on
  REVISED-2; this revision corrects a target-path gap surfaced while satisfying
  that GO's regression command.
- `bridge/gtkb-bridge-compliance-project-metadata-007.md` - sibling precedent
  for a small target-path correction on the same hard-block workspace helper.

No prior deliberation found that waives the live membership gate, hook/template
parity, or executable regression evidence.

## Applicability Preflight

Command:

```text
python scripts/bridge_applicability_preflight.py --bridge-id gtkb-bridge-compliance-wi-project-membership
```

Observed result:

```text
packet_hash: sha256:62bce4381860f80974554a1a99e7b55e9cd6e0eab6c400777a31c7b0c3452cec
operative_file: bridge/gtkb-bridge-compliance-wi-project-membership-007.md
preflight_passed: true
missing_required_specs: []
missing_advisory_specs: ["ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001", "DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001", "GOV-ARTIFACT-ORIENTED-GOVERNANCE-001"]
```

The missing advisory specs are non-blocking for this GO. Required governance
coverage is present.

## Clause Applicability

Command:

```text
python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-bridge-compliance-wi-project-membership
```

Observed result:

```text
operative_file: bridge\gtkb-bridge-compliance-wi-project-membership-007.md
clauses_evaluated: 5
must_apply: 5
may_apply: 0
evidence_gaps: 0
blocking_gaps: 0
```

No blocking clause gaps were reported.

## Findings

No blocking findings.

Positive evidence:

- The revision keeps the substantive five-condition membership/authorization
  gate unchanged from the previously approved REVISED-2.
- The added target path is in-root and exists:
  `platform_tests/hooks/test_bridge_compliance_gate_hard_block_workspace.py`.
- Current checkout inspection confirms the pending-preflight helper still uses
  placeholder metadata (`PROJECT-TEST-PENDING-PREFLIGHT`, `WI-0000`) without the
  proposed `bridge_kind: spec_intake` exemption, so the proposed one-file helper
  edit is necessary to make the existing preflight tests reach the behavior they
  are meant to exercise.
- The required verification command covers the new membership suite, the
  hard-block workspace regression suite, and the Codex hook regression suite.
- Both source DCLs remain `specified` at proposal time.

## GO Conditions

1. Keep the REVISED-3 delta limited to the approved target paths:
   `.claude/hooks/bridge-compliance-gate.py`,
   `groundtruth-kb/templates/hooks/bridge-compliance-gate.py`,
   `platform_tests/hooks/test_bridge_compliance_gate_wi_project_membership.py`,
   and `platform_tests/hooks/test_bridge_compliance_gate_hard_block_workspace.py`.
2. Apply the hook behavior byte-identically to the active hook and packaged
   template hook.
3. Update `_pending_preflight_content()` so the fixture is exempt through
   `bridge_kind: spec_intake` or an equivalent existing non-implementation
   bridge kind; do not weaken the production membership gate.
4. Run and report:

   ```text
   python -m pytest platform_tests/hooks/test_bridge_compliance_gate_wi_project_membership.py platform_tests/hooks/test_bridge_compliance_gate_hard_block_workspace.py platform_tests/scripts/test_codex_bridge_compliance_gate.py -v
   ```

5. Keep `DCL-WORK-ITEM-MUST-BELONG-TO-APPROVED-PROJECT-001` and
   `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` at `specified` until
   post-implementation verification.
6. The post-implementation report must state the current WI-3314 baseline,
   including that live `bridge/INDEX.md` has WI-3314 latest `NO-GO` at
   `bridge/gtkb-bridge-compliance-project-metadata-012.md` unless that changes
   before filing.

## Decision

GO.
