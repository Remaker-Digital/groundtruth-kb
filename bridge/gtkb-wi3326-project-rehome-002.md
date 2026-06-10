REVISED
author_identity: Prime Builder (Codex automation)
author_harness_id: A
author_session_context_id: keep-working-pb-20260606-wi3326-rehome-r2
author_model: GPT-5 Codex
author_model_version: claude-opus-4-7
author_model_configuration: Codex desktop automation, Prime Builder role
author_metadata_source: prime-builder session; bridge-author-metadata/current.json

bridge_kind: prime_proposal
Document: gtkb-wi3326-project-rehome
Version: 002
Responds to: bridge/gtkb-wi3326-project-rehome-001.md
Author: Prime Builder (Codex, harness A; automation Keep Working PB)
Date: 2026-06-06 UTC
Recommended commit type: chore
Project: PROJECT-GTKB-DETERMINISTIC-SERVICES-001
Project Authorization: PAUTH-PROJECT-GTKB-DETERMINISTIC-SERVICES-001-WI-3326-REHOME
Work Item: WI-4266
Owner Decision: DELIB-20260624

# WI-3326 project re-home after verified lifecycle CLI

## Revision Notes

This revision corrects `-001` by adding explicit INDEX-update evidence,
specification-derived verification wording, and Codex author metadata. The
substantive requested operation is unchanged.

## Summary

Execute the split-out WI-3326 re-home that was intentionally excluded from the
verified `gt projects remove-item` code/test slice. The code slice is already
VERIFIED at `bridge/gtkb-projects-remove-item-cli-slice-1-011.md`; this proposal
requests Loyal Opposition review before the live MemBase project relation move.

## Scope

Allowed mutation class: `project_membership_mutation` under
`PAUTH-PROJECT-GTKB-DETERMINISTIC-SERVICES-001-WI-3326-REHOME`.

Perform exactly these two operator commands after GO:

```powershell
gt projects remove-item PROJECT-GTKB-STARTUP-ENHANCEMENTS WI-3326 --change-reason "Detach active-on-retired residual per DELIB-20260624"
gt projects add-item PROJECT-GTKB-DETERMINISTIC-SERVICES-001 WI-3326 --change-reason "Re-home per DELIB-20260624"
```

No source, test, setting, specification, deployment, credential, or history
rewrite changes are in scope. The only intended state change is append-only
MemBase project relation state for WI-3326.

## Current Evidence

- `bridge/gtkb-projects-remove-item-cli-slice-1-011.md` VERIFIED the operator
  implementation and explicitly kept the WI-3326 live move as a separately
  authorized follow-up.
- `gt projects show PROJECT-GTKB-STARTUP-ENHANCEMENTS --json` currently shows
  active relation `PWM-PROJECT-GTKB-STARTUP-ENHANCEMENTS-WI-3326` even though
  that project is retired.
- `gt backlog show WI-3326 --json` shows WI-3326 remains open, created, and
  `project_name: null`.
- `gt projects show PROJECT-GTKB-DETERMINISTIC-SERVICES-001 --json` shows
  WI-4266 remains open and does not yet show WI-3326 as an active member.
- `PAUTH-PROJECT-GTKB-DETERMINISTIC-SERVICES-001-WI-3326-REHOME` is active and
  is limited to `project_membership_mutation` for WI-4266 and WI-3326.
- INDEX update evidence: this helper-mediated REVISED filing inserts
  `REVISED: bridge/gtkb-wi3326-project-rehome-002.md` in `bridge/INDEX.md`
  without deleting or rewriting prior versions.

## Specification Links

- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` - this proposal cites the
  active project authorization and keeps the live move inside its allowed
  mutation class.
- `DCL-PROJECT-AUTHORIZATION-ENVELOPE-001` - the PAUTH envelope names scope,
  allowed mutation, forbidden operations, included specs, and included work
  items.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - this proposal
  lists concrete governing specifications and their relevance.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - the verification plan maps
  the proposal scope to concrete pre/post command evidence.
- `GOV-FILE-BRIDGE-AUTHORITY-001` - the bridge INDEX remains the authoritative
  handoff surface; Prime Builder will not execute the move until LO returns GO.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - the active relation on a retired
  project is an artifact-lifecycle trigger requiring governed transition
  evidence.
- `GOV-STANDING-BACKLOG-001` - WI-4266 and WI-3326 remain the MemBase backlog
  source of truth.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` - the relation change is treated as a
  durable artifact lifecycle transition, not an informal database edit.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` - owner decision, PAUTH, bridge review,
  and post-report verification preserve the governance trail.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - all commands and artifacts stay
  inside `E:\GT-KB`.

## target_paths

- `groundtruth.db` - MemBase project relation rows only.

## Specification-Derived Verification

| Specification | Command or evidence | Expected result |
|---|---|---|
| `GOV-FILE-BRIDGE-AUTHORITY-001` | `bridge/INDEX.md` contains latest `REVISED: bridge/gtkb-wi3326-project-rehome-002.md`. | Latest bridge state is authoritative and prior versions remain intact. |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | `python scripts/bridge_applicability_preflight.py --bridge-id gtkb-wi3326-project-rehome`. | No missing required specs. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | Pre/post `gt projects show` and `gt backlog show` evidence; pytest is not part of this MemBase-only operation. | Relation state proves the requested transition. |
| `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` | Inspect active PAUTH `PAUTH-PROJECT-GTKB-DETERMINISTIC-SERVICES-001-WI-3326-REHOME`. | Scope and allowed mutation match the operation. |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | Before/after relation rows in `gt projects show` output. | Active-on-retired relation becomes non-active history and a new active deterministic-services relation exists. |

## Verification Plan

After GO and execution:

1. `gt projects show PROJECT-GTKB-STARTUP-ENHANCEMENTS --json` no longer lists
   WI-3326 with an active relation.
2. The old startup-project relation is preserved append-only with a non-active
   status.
3. `gt projects show PROJECT-GTKB-DETERMINISTIC-SERVICES-001 --json` lists
   WI-3326 as an active member.
4. `gt backlog show WI-4266 --json` is updated or resolved only if the relation
   evidence satisfies its acceptance summary.
5. File a post-implementation bridge report with before/after command evidence.

## Acceptance Criteria

- WI-3326 is absent from the retired startup project active list.
- WI-3326 is active under PROJECT-GTKB-DETERMINISTIC-SERVICES-001.
- The prior startup-project relation remains auditable as non-active history.
- No source/test/setting/spec/deploy/credential files are changed by this
  operation.

## Code Quality Baseline

| Rule ID | Applies? | Compliance plan | Verification | Waiver / N/A reason |
|---|---|---|---|---|
| CQ-SECRETS-001 | Yes | Proposal and follow-up commands do not expose credentials or secret-shaped values. | Bridge helper credential scan and post-report inspection. | |
| CQ-PATHS-001 | Yes | Operation targets in-root MemBase state through documented `gt` commands. | `target_paths` lists `groundtruth.db`; command evidence remains under `E:\GT-KB`. | |
| CQ-COMPLEXITY-001 | N/A | | | No source code or function body changes are proposed. |
| CQ-CONSTANTS-001 | N/A | | | No source constants or tuning values are proposed. |
| CQ-SECURITY-001 | Yes | Scope forbids credential, deployment, and history rewrite changes. | PAUTH forbidden-operations field plus bridge review. | |
| CQ-DOCS-001 | Yes | Proposal and post-implementation report provide durable operator evidence. | LO review and post-report verification. | |
| CQ-TESTS-001 | Yes | Relation-state checks replace source tests for this MemBase-only operation. | Pre/post `gt projects show` and `gt backlog show` evidence in the implementation report. | |
| CQ-LOGGING-001 | Yes | Both operator commands carry explicit change reasons. | Resulting MemBase rows expose `changed_by`, `changed_at`, and `change_reason`. | |
| CQ-VERIFICATION-001 | Yes | Verification plan lists exact before/after checks and post-report requirement. | LO GO before execution, then post-implementation VERIFIED review. | |

## Prior Deliberations

- `DELIB-20260624` - owner selected re-home WI-3326 to deterministic-services
  and continue WI-4266.
- `DELIB-2543` - prior orphan work-item membership discovery and cleanup context
  relevant to active-on-retired project relations.
- `DELIB-S312-DETERMINISTIC-SERVICES-PRINCIPLE` - deterministic operator
  services should replace repetitive manual database mutation.
