NEW
author_identity: prime-builder/codex/A
author_harness_id: A
author_session_context_id: 019eecf8-b8d2-7d53-a35a-41a1c4634889
author_model: gpt-5-codex
author_model_version: 2026-06-22
author_model_configuration: Codex desktop session; owner-declared ::init gtkb pb; approval_policy=never

# Implementation Authorization Retired-Project Reconciliation Fix

bridge_kind: prime_proposal
Document: gtkb-implementation-authorization-retired-project-reconciliation
Version: 001
Status: NEW
Author: Prime Builder (Codex)
Date: 2026-06-22 UTC
Recommended commit type: fix:

Project Authorization: PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING
Project: PROJECT-GTKB-RELIABILITY-FIXES
Work Item: WI-4747

target_paths: ["scripts/implementation_authorization.py", "platform_tests/scripts/test_implementation_authorization.py"]

implementation_scope: source_test_reliability_fix
requires_review: true
requires_verification: true
kb_mutation_in_scope: false
source_code_mutation_in_scope: true
test_addition_in_scope: true
spec_assertion_backfill_in_scope: false
spec_status_promotion_in_scope: false
production_deployment_in_scope: false
credential_lifecycle_change_in_scope: false

---

## Summary

This proposal repairs a narrow implementation-start authorization defect discovered while following
the containment GO on `bridge/gtkb-architecture-improvement-project-closure-006.md`.

`scripts/implementation_authorization.py validate_project_authorization_row()` currently rejects a
project-scoped PAUTH whenever the PAUTH project is not `active`. That is correct for ordinary source
and governance work, but it fail-closes the exact retired-project reconciliation case that the
project authorization model already names as a mutation class: a PAUTH that explicitly allows
`project_retirement_reconciliation` may need to authorize work against an already retired project.

The fix is intentionally small: keep the active-project requirement for ordinary PAUTHs and for all
non-retired statuses, but allow `current_projects.status == retired` only when the PAUTH's
`allowed_mutation_classes` includes `project_retirement_reconciliation`. Add focused regression
tests for the allowed and denied paths.

This proposal does not perform any `PROJECT-ARCHITECTURE-IMPROVEMENT` closure mutation. It only
repairs the source/test gate needed before that closure thread can be regularized.

## Defect Evidence

- Closure thread `bridge/gtkb-architecture-improvement-project-closure-003.md` records the failing
  command: `python scripts/implementation_authorization.py begin --bridge-id gtkb-architecture-improvement-project-closure`
  returned `authorized: false` with `Project authorization PAUTH-PROJECT-ARCHITECTURE-IMPROVEMENT-CLOSURE is not attached to an active project`.
- `bridge/gtkb-architecture-improvement-project-closure-004.md` NO-GO rejected the proposed
  temporary-active pre-packet workaround because it would mutate protected project state before the
  implementation-start packet.
- `bridge/gtkb-architecture-improvement-project-closure-006.md` GO approved the containment path:
  file or continue a separate bridge-governed implementation-start-gate repair, then return to the
  closure thread only after that repair is VERIFIED.
- `WI-4747` captures this exact reliability defect as an active member of
  `PROJECT-GTKB-RELIABILITY-FIXES`.

## Specification Links

- `GOV-RELIABILITY-FAST-LANE-001` - authorizes small single-concern defect repairs under the
  reliability fast-lane when they stay inside source/test/hook mutation classes and add no new
  public behavior beyond removing the defect.
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` - governs PAUTH validation, including active
  project authorization envelopes and mutation-class scoping.
- `DCL-PROJECT-AUTHORIZATION-ENVELOPE-001` - project authorization metadata must bound the work
  item, project, mutation classes, and forbidden operations.
- `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001` - project authorization does not bypass bridge
  review, the live GO requirement, or the implementation-start packet.
- `GOV-FILE-BRIDGE-AUTHORITY-001` and `.claude/rules/file-bridge-protocol.md` - this proposal,
  review, implementation report, and verification must flow through the versioned bridge protocol.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - this proposal includes machine-readable
  `Project Authorization`, `Project`, and `Work Item` lines.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - this proposal cites the governing
  specifications before implementation.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - verification must be derived from the linked
  specifications and executed before VERIFIED.
- `GOV-STANDING-BACKLOG-001` - `WI-4747` is the captured backlog work item for this defect and is
  active in the reliability fixes project.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` - the defect was captured as a work item and routed
  through a bridge proposal instead of remaining in transient session memory.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` - the defect, proposal, tests, implementation report,
  and verification evidence are preserved as durable artifacts.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - the fix handles a lifecycle transition edge case
  (`active` project versus `retired` project) explicitly instead of normalizing it away.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - all target paths are inside `E:/GT-KB`; no Agent Red
  lifecycle-independent repository or out-of-root surface is in scope.

## Owner Decisions / Input

- `DELIB-S351-RELIABILITY-FAST-LANE-DIRECTION` authorized the standing reliability fast-lane,
  including `PROJECT-GTKB-RELIABILITY-FIXES` and
  `PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING`.
- The current owner automation directive for `PROJECT-ARCHITECTURE-IMPROVEMENT` closure instructs
  Prime Builder to file or continue a separate bridge-governed implementation-start-gate repair if
  the closure containment revision receives GO.

No new owner decision is required for this proposal because `WI-4747` is a single-concern defect
captured into the active reliability fixes project, and the requested mutation classes are limited
to `source` and `test_addition`.

## Requirement Sufficiency

Existing requirements sufficient.

The existing project authorization and bridge-gate specifications already require the behavior this
fix preserves: project-scoped authorization must fail closed by default, project authorization does
not bypass bridge review, and mutation classes define the allowed scope. The defect is that the
gate cannot distinguish an ordinary inactive project from an explicitly authorized retired-project
reconciliation. No new or revised GOV/SPEC/PB/ADR/DCL artifact is needed before implementation.

## Prior Deliberations

- `bridge/gtkb-architecture-improvement-project-closure-004.md` - NO-GO requiring an implementation
  authorization path that does not mutate project state before the packet.
- `bridge/gtkb-architecture-improvement-project-closure-006.md` - GO for the containment path,
  requiring a separate bridge-governed retired-project gate repair before closure regularization.
- `bridge/gtkb-reliability-fast-lane-006.md` - VERIFIED standing fast-lane implementation; confirms
  `PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING` covers fast-lane source/test fixes by active
  project membership.
- `bridge/gtkb-wrapup-clear-impl-start-packet-at-verified-003.md` through `-006.md` - adjacent
  precedent for repairing `scripts/implementation_authorization.py` under the same standing
  reliability fast-lane, after narrowing the proposal to source/test behavior with no new CLI
  surface.
- `WI-3350` - adjacent future work for parent-project PAUTH coverage in the same validator; this
  proposal does not implement parent-chain semantics.
- `WI-3510` - adjacent future work for included-work-item semantics divergence; this proposal does
  not alter included-work-item semantics.

## Fast-Lane Eligibility

1. Origin defect or regression - met. `WI-4747` is a defect captured from a live gate failure.
2. No new public API, CLI, schema, or behavior beyond removing the defect - met. The proposed change
   is internal PAUTH validation behavior plus regression tests. No CLI subcommand, packet schema, or
   bridge state behavior changes.
3. Existing requirements sufficient - met. The proposal preserves the existing fail-closed gate and
   narrows the retired-project allowance to a named mutation class.
4. Small single-concern scope - met. One source module and one focused test module.

## Implementation Plan

1. In `scripts/implementation_authorization.py`, replace the boolean-only active-project check with
   a status read helper or equivalent local logic.
2. In `validate_project_authorization_row()`, preserve the existing pass path for `active` projects.
3. Add a single narrow pass path for `retired` projects only when the PAUTH's parsed
   `allowed_mutation_classes` contains `project_retirement_reconciliation`.
4. Keep the existing authorization error for retired projects without that mutation class and for
   all other non-active statuses.
5. In `platform_tests/scripts/test_implementation_authorization.py`, add focused tests proving:
   - a retired project PAUTH with `project_retirement_reconciliation` can create a packet when the
     rest of the proposal is valid;
   - a retired project PAUTH without that mutation class still fails with the active-project error;
   - ordinary active-project PAUTH behavior is unchanged.

## Files Expected To Change

- `scripts/implementation_authorization.py`
- `platform_tests/scripts/test_implementation_authorization.py`

## Spec-To-Test Mapping

| Governing surface | Verification |
| --- | --- |
| `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` | Focused tests cover the retired-project PAUTH allow and deny cases. |
| `DCL-PROJECT-AUTHORIZATION-ENVELOPE-001` | Tests assert the allowance depends on the PAUTH's `allowed_mutation_classes`; ordinary retired PAUTHs remain denied. |
| `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001` | Implementation report will include the live GO, implementation-start packet, and validation commands before any source edit. |
| `GOV-RELIABILITY-FAST-LANE-001` | Diff inspection confirms only source/test files changed and no public CLI/schema/formal artifact behavior was added. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | Post-implementation report will carry exact pytest, ruff check, and ruff format-check results. |

Implementation verification will run:

```text
python -m pytest platform_tests/scripts/test_implementation_authorization.py -q -k "retired"
python -m pytest platform_tests/scripts/test_implementation_authorization.py -q
python -m ruff check scripts/implementation_authorization.py platform_tests/scripts/test_implementation_authorization.py
python -m ruff format --check scripts/implementation_authorization.py platform_tests/scripts/test_implementation_authorization.py
python scripts/bridge_applicability_preflight.py --bridge-id gtkb-implementation-authorization-retired-project-reconciliation
python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-implementation-authorization-retired-project-reconciliation
```

## Acceptance Criteria

- Loyal Opposition records GO on this proposal before implementation starts.
- `python scripts/implementation_authorization.py begin --bridge-id gtkb-implementation-authorization-retired-project-reconciliation` succeeds after GO and before source/test edits.
- The retired-project allowance is limited to PAUTHs whose allowed mutation classes include
  `project_retirement_reconciliation`.
- Retired-project PAUTHs without that mutation class still fail closed.
- Ordinary active-project PAUTH behavior and work-item membership validation are unchanged.
- The implementation report maps every linked specification to executed evidence.
- Loyal Opposition records VERIFIED before the repair is treated as complete.

## Out Of Scope

- Any mutation to `PROJECT-ARCHITECTURE-IMPROVEMENT`, its member work items, or its closure bridge
  report before this repair is VERIFIED.
- Any new public CLI subcommand, packet schema, bridge state semantics, or PAUTH storage schema.
- Parent-project / sub-project PAUTH inheritance (`WI-3350`).
- Included-work-item additive-versus-restrictive semantics (`WI-3510`).
- Formal GOV/ADR/DCL/SPEC mutation.
- Production deployment, credential lifecycle work, git force-push, or destructive cleanup.

## Risk And Rollback

Risk is low because the allowance is narrower than "inactive projects are okay": it applies only
when the project is specifically `retired` and the PAUTH explicitly allows
`project_retirement_reconciliation`.

Rollback is to revert the two changed files. Existing PAUTH rows, project rows, bridge files, and
implementation-start packet schema are not migrated.

## Pre-Filing Preflight Evidence

Commands run against this draft before live filing:

```text
python scripts/bridge_applicability_preflight.py --bridge-id gtkb-implementation-authorization-retired-project-reconciliation --content-file .gtkb-state/bridge-propose-drafts/gtkb-implementation-authorization-retired-project-reconciliation-001.md
python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-implementation-authorization-retired-project-reconciliation --content-file .gtkb-state/bridge-propose-drafts/gtkb-implementation-authorization-retired-project-reconciliation-001.md
```

Observed result before the advisory citation update:

```text
Applicability preflight: preflight_passed: true; missing_required_specs: [];
missing_advisory_specs: ["GOV-ARTIFACT-ORIENTED-GOVERNANCE-001"].
Clause preflight: exit_code 0; blocking gaps 0.
```

The advisory omission was corrected in this draft by adding
`GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` to Specification Links. Prime Builder will rerun both
preflights after this correction and before live filing.

Observed result after correction:

```text
Applicability preflight: preflight_passed: true; missing_required_specs: [];
missing_advisory_specs: [].
Clause preflight: exit_code 0; evidence gaps in must_apply clauses 0; blocking gaps 0.
```
