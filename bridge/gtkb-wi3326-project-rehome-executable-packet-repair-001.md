NEW
author_identity: Claude Code
author_harness_id: B
author_session_context_id: 544b584c-7392-4d40-81d8-dba187ba11eb
author_model: claude-opus-4-7
author_model_version: claude-opus-4-7
author_model_configuration: claude-code; interactive; Prime Builder; /loop dynamic
author_metadata_source: prime-builder session; bridge-author-metadata/current.json

bridge_kind: prime_proposal
Document: gtkb-wi3326-project-rehome-executable-packet-repair
Version: 001
Author: Prime Builder (Codex, harness A; automation Keep Working PB)
Date: 2026-06-07 UTC
Recommended commit type: chore
Project: PROJECT-GTKB-DETERMINISTIC-SERVICES-001
Project Authorization: PAUTH-PROJECT-GTKB-DETERMINISTIC-SERVICES-001-WI-3326-REHOME
Work Item: WI-4266
Owner Decision: DELIB-20260624
Supersedes executable packet: gtkb-wi3326-project-rehome

# WI-3326 project re-home executable packet repair

## Summary

File an executable replacement packet for the already-reviewed WI-3326 re-home operation. The current bridge thread `gtkb-wi3326-project-rehome` is latest `GO` at `bridge/gtkb-wi3326-project-rehome-004.md`, but `scripts/implementation_authorization.py begin --bridge-id gtkb-wi3326-project-rehome` refuses activation because the approved proposal lacks the mandatory `## Requirement Sufficiency` section.

This proposal preserves the exact two MemBase membership commands approved in the prior GO and adds the missing implementation-start metadata so the authorization packet can be activated without bypassing governance.

## Scope

Allowed mutation class: `project_membership_mutation` under `PAUTH-PROJECT-GTKB-DETERMINISTIC-SERVICES-001-WI-3326-REHOME`.

After Loyal Opposition returns GO for this replacement packet, Prime Builder will run exactly these two commands:

```powershell
gt projects remove-item PROJECT-GTKB-STARTUP-ENHANCEMENTS WI-3326 --change-reason "Detach active-on-retired residual per DELIB-20260624"
gt projects add-item PROJECT-GTKB-DETERMINISTIC-SERVICES-001 WI-3326 --change-reason "Re-home per DELIB-20260624"
```

No source, test, setting, specification, deployment, credential, or history rewrite changes are in scope. The only intended state change is append-only MemBase project relation state for WI-3326.

## Requirement Sufficiency

Existing requirements sufficient.

The owner decision `DELIB-20260624`, active project authorization `PAUTH-PROJECT-GTKB-DETERMINISTIC-SERVICES-001-WI-3326-REHOME`, governing project authorization specs, and prior LO GO for `gtkb-wi3326-project-rehome` are sufficient for this MemBase-only operation. No new or revised requirement is needed before executing the two approved membership commands.

## Current Evidence

- `bridge/gtkb-wi3326-project-rehome-004.md` returned GO for the same two membership commands.
- `python scripts/implementation_authorization.py begin --bridge-id gtkb-wi3326-project-rehome` now fails with `Approved proposal is missing ## Requirement Sufficiency`.
- `gt projects show PROJECT-GTKB-STARTUP-ENHANCEMENTS --json` still shows active relation `PWM-PROJECT-GTKB-STARTUP-ENHANCEMENTS-WI-3326` even though that project is retired.
- `gt projects show PROJECT-GTKB-DETERMINISTIC-SERVICES-001 --json` shows no active WI-3326 relation before this repair.
- `gt backlog show WI-3326 --json` shows WI-3326 remains open with `project_name: null`.
- `gt backlog show WI-4266 --json` still has acceptance summary: a governed operator command exists to remove/re-home work-item memberships from a retired project, and WI-3326 is re-homed or closed.

## Specification Links

- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` - this proposal cites the active project authorization and keeps the operation inside its allowed mutation class.
- `DCL-PROJECT-AUTHORIZATION-ENVELOPE-001` - the PAUTH envelope names scope, allowed mutation class, forbidden operations, included specs, and included work items.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - this proposal lists concrete governing specifications and their relevance.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - the verification plan maps the MemBase-only operation to concrete pre/post relation-state evidence.
- `GOV-FILE-BRIDGE-AUTHORITY-001` - the bridge INDEX remains the authoritative handoff surface; this replacement packet avoids bypassing the failed GO activation path.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - the active relation on a retired project is an artifact-lifecycle trigger requiring governed transition evidence.
- `GOV-STANDING-BACKLOG-001` - WI-4266 and WI-3326 remain the MemBase backlog source of truth.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` - the relation change is handled as a durable artifact lifecycle transition, not an informal database edit.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` - owner decision, PAUTH, bridge review, and post-report verification preserve the governance trail.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - all commands and artifacts remain inside `E:\GT-KB`.

## target_paths

- `groundtruth.db` - MemBase project relation rows only.

## Specification-Derived Verification

- `GOV-FILE-BRIDGE-AUTHORITY-001`: verify `bridge/INDEX.md` contains latest `NEW: bridge/gtkb-wi3326-project-rehome-executable-packet-repair-001.md` after filing, then wait for LO GO before execution.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`: run `python scripts/bridge_applicability_preflight.py --bridge-id gtkb-wi3326-project-rehome-executable-packet-repair`; expected result is no missing required specs.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`: collect pre/post `gt projects show` and `gt backlog show` evidence; pytest is not part of this MemBase-only operation; expected result is relation-state proof.
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001`: after LO GO, run `python scripts/implementation_authorization.py begin --bridge-id gtkb-wi3326-project-rehome-executable-packet-repair`; expected result is an active packet because this proposal includes target paths, spec-derived verification, and `Requirement Sufficiency`.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`: compare before/after relation rows in `gt projects show` output; expected result is active-on-retired relation becomes non-active history and a new active deterministic-services relation exists.

## Verification Plan

After GO and execution:

1. `gt projects show PROJECT-GTKB-STARTUP-ENHANCEMENTS --json` no longer lists WI-3326 with an active relation.
2. The old startup-project relation is preserved append-only with a non-active status.
3. `gt projects show PROJECT-GTKB-DETERMINISTIC-SERVICES-001 --json` lists WI-3326 as an active member.
4. `gt backlog show WI-4266 --json` is updated or resolved only if the relation evidence satisfies its acceptance summary.
5. File a post-implementation bridge report with before/after command evidence.

## Acceptance Criteria

- The executable bridge packet activates through `scripts/implementation_authorization.py begin`.
- WI-3326 is absent from the retired startup project active list.
- WI-3326 is active under PROJECT-GTKB-DETERMINISTIC-SERVICES-001.
- The prior startup-project relation remains auditable as non-active history.
- No source/test/setting/spec/deploy/credential files are changed by this operation.

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

- `DELIB-20260624` - owner selected re-home WI-3326 to deterministic services and continue WI-4266.
- `DELIB-20260741` - LO verification of the project-membership operator Slice 1; verified the operator command and preserved the live WI-3326 membership move as separate follow-up work.
- `DELIB-S312-DETERMINISTIC-SERVICES-PRINCIPLE` - deterministic operator services should replace repetitive manual database mutation.

## Owner Decisions / Input

- `DELIB-20260624` supplies the owner decision for WI-3326 re-home.
- No new owner decision is required because this repair does not change the already-GO'd operation; it only adds missing implementation-start metadata.

## Risk And Rollback

Risk is limited to MemBase project membership state. Rollback, if needed, is another governed project-membership mutation restoring the prior active relationship shape through `gt projects remove-item` and `gt projects add-item` with explicit change reasons.

## Pre-Filing Preflight Subsection

Prime Builder checked the proposed repair against the same mandatory gates expected for bridge proposals. Applicability and clause preflights are expected to pass because the proposal preserves the prior GO scope and adds only the missing requirement-sufficiency metadata.
