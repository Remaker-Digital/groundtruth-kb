NO-GO

bridge_kind: loyal_opposition_review
Document: gtkb-fab-14-gate-fp-feedback-loop
Version: 002
Author: loyal-opposition (Codex, harness A)
Date: 2026-06-11
Responds-To: bridge/gtkb-fab-14-gate-fp-feedback-loop-001.md

# Loyal Opposition Review - FAB-14 Gate FP Feedback Loop

## Review Scope

Reviewed the operative Prime Builder proposal `bridge/gtkb-fab-14-gate-fp-feedback-loop-001.md`
for WI-4426 / PROJECT-FABLE-INVESTIGATION, including live bridge state, mandatory
bridge preflights, owner-decision evidence, project authorization, backlog state, and
future-work dependency/precedence.

## Same-Session Guard

This Loyal Opposition session did not author the proposal under review. The proposal was
authored by Prime Builder, harness B, session `d2f32e6b-5441-45b3-b355-097a2507f5f7`.

## Dependency And Precedence Check

FAB-14 is allowed to proceed independently of the later shared-classifier-library follow-on, which
the owner explicitly deferred. It overlaps FAB-10 on `bridge-compliance-gate.py`; implementation
must coordinate that shared hook file if both GOs are active.

## Preflight Evidence

- `python scripts/bridge_applicability_preflight.py --bridge-id gtkb-fab-14-gate-fp-feedback-loop`
  failed with `missing_required_specs=["ADR-ISOLATION-APPLICATION-PLACEMENT-001"]`.
- `python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-fab-14-gate-fp-feedback-loop`
  passed with 4 `must_apply` clauses and 0 blocking gaps.
- `gt deliberations get DELIB-FAB14-REMEDIATION-20260610` confirms the owner selected the
  cheaper-containment FP program, Bash parser hotfix, Requirement Sufficiency parser fix, and
  packet auto-discovery for both approval gates.
- `gt projects authorizations PROJECT-FABLE-INVESTIGATION --json` confirms active
  `PAUTH-FAB14-20260610` for WI-4426, including formal spec amendment with packet authority
  and the prohibition on downgrading blocking gates to warn mode.
- `gt backlog list --json --id WI-4426` confirms WI-4426 is open/backlogged and linked to the
  Fable Investigation advisory and chartering deliberations.

## Blocking Findings

### F1 - Mandatory applicability preflight fails

The proposal includes an `Isolation Placement Compliance` section and references `applications/`,
but `ADR-ISOLATION-APPLICATION-PLACEMENT-001` is not included in the `## Specification Links` list.
The mandatory bridge applicability preflight therefore fails. Loyal Opposition cannot GO a proposal
that fails this required gate.

### F2 - Formal amendment packet artifacts are missing from target_paths

The proposal amends `DCL-ARTIFACT-APPROVAL-HOOK-001` through the formal-artifact-approval workflow.
The PAUTH also describes this as `formal_spec_amendment_with_packet`. However, `target_paths` omit
`.groundtruth/formal-artifact-approvals/*.json` or concrete packet file paths.

Because implementation-start authority is path-scoped, the revised proposal must include the packet
artifact path(s) required to amend the DCL.

### F3 - Denial telemetry output path is not in target_paths

The proposal adds runtime denial telemetry at `.gtkb-state/gate-denials.jsonl`, but the target set
does not include `.gtkb-state/**` or that concrete path. If implementation or tests create the file,
the bridge scope should name it explicitly.

## Required Revision

Submit a REVISED proposal that:

1. Adds `ADR-ISOLATION-APPLICATION-PLACEMENT-001` to `## Specification Links` or removes the content
   that makes it applicable.
2. Adds concrete formal approval packet path(s) under `.groundtruth/formal-artifact-approvals/` for
   the DCL amendment.
3. Adds `.gtkb-state/gate-denials.jsonl` or a bounded `.gtkb-state/**` telemetry path to `target_paths`,
   or makes clear that tests use an isolated temp path instead.
4. Preserves the owner constraints: gates stay blocking, no external Agent Red mutation, and the shared
   classifier library remains deferred.

## Verdict

NO-GO until the mandatory preflight passes and all implementation artifacts are in scope.
