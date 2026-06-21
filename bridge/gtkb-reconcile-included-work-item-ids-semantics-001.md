NEW
author_identity: prime-builder/claude
author_harness_id: B
author_session_context_id: 96b4ab64-e440-47b7-8c81-cd55bc7a5c1e
author_model: claude-opus-4-8
author_model_version: 4.8
author_model_configuration: default

# Implementation Proposal - Reconcile divergent included_work_item_ids semantics between Write-time bridge-compliance gate and impl-start authorization gate

bridge_kind: prime_proposal
Document: gtkb-reconcile-included-work-item-ids-semantics
Version: 001 (DRAFT; non-dispatchable)
Date: 2026-06-21 UTC

Project Authorization: PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-NONFASTLANE-BATCH-2026-06-21
Project: PROJECT-GTKB-RELIABILITY-FIXES
Work Item: WI-3510

target_paths: [".claude/hooks/bridge-compliance-gate.py", "scripts/implementation_authorization.py", "platform_tests/hooks/test_bridge_compliance_gate_wi_project_membership.py", "platform_tests/scripts/test_project_authorization.py"]

Implementation proposal for a bounded code or platform change.

## Claim

Two gates guarding project-authorization coverage assign opposite semantics to a PAUTH `included_work_item_ids` field, producing inconsistent authorization scope at the two boundaries of the same protocol.

- Write-time gate (`.claude/hooks/bridge-compliance-gate.py`, `_wi_project_membership_gap`, currently lines 1021-1023): a NON-EMPTY `included_work_item_ids` acts as a RESTRICTIVE allowlist. A work item that is an active project member but is absent from the list yields `wi-not-included-by-authorization` and the proposal Write is hard-blocked.
- Impl-start gate (`scripts/implementation_authorization.py`, `validate_project_authorization_row`, currently line 821): inclusion is ADDITIVE. A work item passes when it is in `included_work_item_ids` OR is an active project member; a non-empty list never restricts an active member.

The same field therefore narrows scope at file-Write time but never narrows scope at implementation-start time. The divergence is a self-diagnostic defect (S379): a PAUTH that populates a non-empty allowlist (38/41 active PAUTHs do) blocks the proposal Write of an active-but-unlisted member, yet that same member would pass the impl-start authorization check post-GO. Per the owner disposition recorded on WI-3510 ("Reduce friction, keep gates"), the canonical meaning of `included_work_item_ids` is ADDITIVE (an additional grant of scope on top of active membership), not a restrictive allowlist; both gates remain present and active, and the reconciliation removes the friction by aligning the Write-time gate to the additive semantics rather than tightening the impl-start gate (which would widen no scope but would add friction the owner directed against).

## Requirement Sufficiency

New or revised requirement required before implementation. `included_work_item_ids` has no single governing specification that fixes its semantics as additive vs restrictive; the two existing enforcement clauses (`DCL-WORK-ITEM-MUST-BELONG-TO-APPROVED-PROJECT-001` for the Write-time gate and `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` for the impl-start gate) are silent on the field's directionality, which is the root cause of the drift. The owner disposition on WI-3510 ("Reduce friction, keep gates") sets the policy direction (additive), but a durable, machine-checkable specification of the canonical `included_work_item_ids` semantics does not yet exist. A new design constraint -- proposed id `DCL-PAUTH-INCLUDED-WORK-ITEM-IDS-ADDITIVE-001` -- should be created to state: "A non-empty `included_work_item_ids` is an ADDITIVE scope grant; a work item is in authorization scope when it is listed in `included_work_item_ids` OR is an active member of the authorized project, and is out of scope only when listed in `excluded_work_item_ids`. The Write-time bridge-compliance gate and the implementation-start authorization gate MUST apply this semantics identically." This proposal does NOT create that spec; it captures the requirement here per the spec-first correction cycle (GOV-06). The spec must be authored and owner-approved through the governed formal-artifact-approval path before the code reconciliation is implemented, so the reconciled gates have a durable spec to derive tests from. (See Risks / Rollback for the alternative restrictive direction, which the owner disposition does not select.)

## In-Root Placement Evidence

All target paths are inside `E:\GT-KB`: `.claude/hooks/bridge-compliance-gate.py`, `scripts/implementation_authorization.py`, `platform_tests/hooks/test_bridge_compliance_gate_wi_project_membership.py`, `platform_tests/scripts/test_project_authorization.py`.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` - both gates enforce the bridge/project-authorization model; the divergent `included_work_item_ids` semantics is an inconsistency in that enforcement surface, and this proposal is itself a bridge proposal subject to the file-bridge authority.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` - the reconciliation preserves the PAUTH as a durable, consistently-interpreted authorization artifact rather than leaving two gates that read the same field two ways.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - this proposal cites every relevant governing specification (mandatory linkage).
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - the verification plan derives tests from the cited specs / the new design constraint (mandatory).
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - the proposal carries Project Authorization / Project / Work Item linkage lines (mandatory), and the membership/authorization linkage is precisely the subject of this fix.
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` - governs the impl-start authorization gate (`validate_project_authorization_row`); it states backlog membership alone is not implementation authorization, and is the spec whose additive `included_work_item_ids` reading the Write-time gate must be aligned to (with the new DCL fixing the field directionality).
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - present by the applicability floor; the change is confined to the GT-KB platform control surfaces (`.claude/hooks/...`, `scripts/...`) and platform tests, crosses no application-placement boundary, and touches no adopter/`applications/` surface.
- `GOV-STANDING-BACKLOG-001` - WI-3510 is a standing-backlog work item (origin=hygiene, P2) under PROJECT-GTKB-RELIABILITY-FIXES.
- `ADR-CODEX-HOOK-PARITY-FALLBACK-001` - present by the applicability floor for hook-touching work; the Write-time gate is a Claude-side `PreToolUse` hook, and this change does not alter the Codex hook-parity posture (no Codex hook surface is added or removed).
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` - the authorization-scope decision stays artifact-backed (the new DCL plus the PAUTH row) rather than encoded divergently in two gate implementations.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - touching the previously-divergent `included_work_item_ids` enforcement triggers specification creation (the new DCL) per specify-on-contact, which this proposal records in Requirement Sufficiency.

## Prior Deliberations

- `DELIB-2547` - S379 disposition: reduce authorization friction without relaxing the gates; this is the owner direction that selects the additive canonical meaning and the "keep both gates" constraint for this reconciliation.
- `DELIB-20265457` - Owner decision (2026-06-21 AUQ) authorizing the PROJECT-GTKB-RELIABILITY-FIXES non-fast-lane proposal batch; WI-3510 is in scope for that batch.

## Owner Decisions / Input

- `PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-NONFASTLANE-BATCH-2026-06-21` - the non-fast-lane batch project authorization that covers WI-3510 (origin=hygiene, P2) through active project membership; it authorizes authoring this proposal and the bounded code reconciliation, but does NOT by itself authorize creation of the new design constraint (see Requirement Sufficiency) -- that spec requires its own formal-artifact-approval packet.
- `DELIB-20265457` - owner AUQ (2026-06-21) directing authoring of NEW proposals for the open PROJECT-GTKB-RELIABILITY-FIXES work items in this batch; WI-3510 is one of them. The S379 disposition recorded on WI-3510 ("Reduce friction, keep gates") supplies the policy direction (additive `included_work_item_ids`); any final adoption of the additive-vs-restrictive canonical meaning is captured durably via the new DCL's owner-approval packet before code lands.

## Proposed Scope

This is a contract-reconciliation defect fix. Implementation is sequenced AFTER the new design constraint (`DCL-PAUTH-INCLUDED-WORK-ITEM-IDS-ADDITIVE-001`, see Requirement Sufficiency) is authored and owner-approved, so the reconciled gates have a durable spec to test against.

1. Adopt the ADDITIVE canonical semantics for `included_work_item_ids` (per the S379 owner disposition) and align the Write-time gate to it. In `.claude/hooks/bridge-compliance-gate.py`, `_wi_project_membership_gap`, remove the restrictive-allowlist condition (currently lines 1021-1023):
   - Delete the `included = _parse_json_id_list(auth["included_work_item_ids"])` / `if included and work_item_id not in included: return "wi-not-included-by-authorization"` block, so a non-empty `included_work_item_ids` no longer blocks an active-but-unlisted member.
   - Retain ALL other conditions unchanged: `wi-not-found-in-project`, `wi-membership-inactive`, `authorization-not-found`, `authorization-inactive`, `authorization-expired`, and `wi-excluded-from-authorization`. The exclusion path stays restrictive (a listed exclusion still blocks). The gate is NOT removed -- it remains active; only the directionality of `included_work_item_ids` changes from restrictive to additive, matching impl-start.
   - The `wi-not-included-by-authorization` condition token is retired; remove it from the docstring condition list at the top of `_wi_project_membership_gap` to keep the documented token set accurate.
2. Confirm the impl-start gate already encodes the canonical additive semantics. In `scripts/implementation_authorization.py`, `validate_project_authorization_row` (line 821) already passes a work item that is `in included_items` OR `_work_item_in_project(...)` (active member). No behavior change is required there; add an explanatory comment citing `DCL-PAUTH-INCLUDED-WORK-ITEM-IDS-ADDITIVE-001` so the now-canonical semantics is documented at the surface that already implements it (keeping the two gates' intent legible and preventing future re-divergence).
3. Update the Write-time gate regression tests in `platform_tests/hooks/test_bridge_compliance_gate_wi_project_membership.py`:
   - Convert `test_wi_not_in_included_list_blocked` (currently asserts an active member absent from a non-empty `included_work_item_ids` is BLOCKED) into a passing-case test asserting that same proposal now PASSES (additive: active membership grants scope; the non-empty list does not restrict). Rename to reflect the new contract (e.g., `test_active_member_not_in_included_list_passes`).
   - Keep `test_excluded_wi_blocked` and `test_active_membership_active_auth_passes` unchanged (exclusion stays restrictive; the existing passing case is unaffected).
   - Add a guard test asserting a work item that is BOTH an active member AND listed in `included_work_item_ids` still passes (the additive contract's listed-and-member case).
4. Add an impl-start regression test in `platform_tests/scripts/test_project_authorization.py` asserting the additive semantics at that gate: a work item NOT in a non-empty `included_work_item_ids` but an active member PASSES `validate_project_authorization_row`, and a work item in `excluded_work_item_ids` is rejected (pinning that the impl-start gate's additive reading is the canonical one both gates now share).

This is the defect-removal path that aligns both gates on the owner-selected additive meaning. The alternative direction (tighten impl-start to a restrictive allowlist) is rejected by the S379 disposition and is described in Risks / Rollback.

## Specification-Derived Verification Plan

| Spec clause | Derived test | Assertion |
|---|---|---|
| `DCL-PAUTH-INCLUDED-WORK-ITEM-IDS-ADDITIVE-001` (additive at Write-time) | `test_active_member_not_in_included_list_passes` (in `test_bridge_compliance_gate_wi_project_membership.py`, converted from `test_wi_not_in_included_list_blocked`) | A NEW proposal whose WI is an active member but absent from a non-empty `included_work_item_ids` is NOT denied by `_deny_reason_for_content` (reason is None). |
| `DCL-PAUTH-INCLUDED-WORK-ITEM-IDS-ADDITIVE-001` (listed-and-member still passes) | `test_active_member_and_in_included_list_passes` (in `test_bridge_compliance_gate_wi_project_membership.py`) | A NEW proposal whose WI is an active member AND in `included_work_item_ids` is not denied (reason is None). |
| `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` / `DCL-PAUTH-INCLUDED-WORK-ITEM-IDS-ADDITIVE-001` (additive at impl-start; canonical reading) | `test_validate_authorization_active_member_not_in_included_list_passes` (in `test_project_authorization.py`) | `validate_project_authorization_row` does not raise for an active member absent from a non-empty `included_work_item_ids`. |
| `DCL-PAUTH-INCLUDED-WORK-ITEM-IDS-ADDITIVE-001` (exclusion stays restrictive at both gates) | `test_excluded_wi_blocked` (existing, unchanged) + `test_validate_authorization_excluded_wi_rejected` (in `test_project_authorization.py`) | An excluded WI is blocked at Write-time (`wi-excluded-from-authorization`) and raises `AuthorizationError` at impl-start. |
| `GOV-FILE-BRIDGE-AUTHORITY-001` (gate not removed; other conditions intact) | existing `test_bridge_compliance_gate_wi_project_membership.py` suite (membership/auth conditions) | `wi-not-found-in-project`, `wi-membership-inactive`, `authorization-not-found`, `authorization-inactive`, `authorization-expired` all still block (no regression to the retained conditions). |

Execution commands:
- `python -m pytest platform_tests/hooks/test_bridge_compliance_gate_wi_project_membership.py platform_tests/scripts/test_project_authorization.py -q --tb=short`
- `python -m ruff check .claude/hooks/bridge-compliance-gate.py scripts/implementation_authorization.py platform_tests/hooks/test_bridge_compliance_gate_wi_project_membership.py platform_tests/scripts/test_project_authorization.py`
- `python -m ruff format --check .claude/hooks/bridge-compliance-gate.py scripts/implementation_authorization.py platform_tests/hooks/test_bridge_compliance_gate_wi_project_membership.py platform_tests/scripts/test_project_authorization.py`

## Acceptance Criteria

1. `DCL-PAUTH-INCLUDED-WORK-ITEM-IDS-ADDITIVE-001` exists in MemBase with owner-approval-packet evidence, stating the additive canonical semantics and the both-gates-identical requirement (authored under its own formal-artifact-approval, prerequisite to the code change).
2. The Write-time gate (`_wi_project_membership_gap`) no longer returns `wi-not-included-by-authorization`; an active-but-unlisted member is not blocked by a non-empty `included_work_item_ids`, while `wi-excluded-from-authorization` and all other retained conditions still block.
3. The impl-start gate (`validate_project_authorization_row`) behavior is unchanged and is documented as the canonical additive implementation; both gates now interpret `included_work_item_ids` identically.
4. The converted/added tests pass; existing retained-condition tests still pass; `ruff check` and `ruff format --check` are clean on all four changed files.

## Risks / Rollback

- Risk: relaxing the Write-time restrictive allowlist widens which active members can have proposals written for a project. Mitigation/justification: this is the explicit S379 owner direction ("Reduce friction, keep gates"); active project membership is already the authorization basis the impl-start gate accepts, so the Write-time gate is being aligned to the existing post-GO contract, not loosened beyond it. The exclusion path (`excluded_work_item_ids`) remains the restrictive lever for scoping a specific member out.
- Risk (rejected alternative): the opposite reconciliation -- making impl-start restrictive to match the old Write-time allowlist -- would NARROW authorization scope and add friction (a member would need to be explicitly listed even when an active member), directly contradicting the S379 disposition. It is therefore rejected; it is recorded here so the decision is not silently revisited.
- Risk: a PAUTH author may have relied on the allowlist to scope a single WI. Mitigation: that intent is preserved by `excluded_work_item_ids`; no existing PAUTH loses its exclusion semantics.
- Rollback: revert the single condition deletion in `bridge-compliance-gate.py` and the comment/test changes; the change is one removed guard plus comment + test edits, fully reversible with no schema migration and no data change.

## Files Expected To Change

- `.claude/hooks/bridge-compliance-gate.py`
- `scripts/implementation_authorization.py`
- `platform_tests/hooks/test_bridge_compliance_gate_wi_project_membership.py`
- `platform_tests/scripts/test_project_authorization.py`

## Recommended Commit Type

`fix`
