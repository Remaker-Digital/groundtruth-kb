NEW

# gtkb-wi3350-parent-project-pauth-covers-subproject — accept a parent-project PAUTH for a sub-project proposal (WI-3350)

bridge_kind: prime_proposal
author_identity: prime-builder/claude
author_harness_id: B
author_session_context_id: f95c6f19-b1a8-4602-8d22-43886dcdf659
author_model: claude-opus-4-8
author_model_version: opus-4.8
author_model_configuration: Claude Code interactive Prime Builder (::init gtkb pb)
Document: gtkb-wi3350-parent-project-pauth-covers-subproject
Version: 001

Project Authorization: PAUTH-PROJECT-GTKB-IMPLEMENTATION-START-GATE-HARDENING-001-IMPLEMENTATION-START-GATE-HARDENING-001-BOUNDED-IMPLEMENTATION-2026-06-23
Project: PROJECT-GTKB-IMPLEMENTATION-START-GATE-HARDENING-001
Work Item: WI-3350

target_paths: ["scripts/implementation_authorization.py", "platform_tests/scripts/test_implementation_authorization.py"]

implementation_scope: source
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

## Summary

WI-3350 (defect): `validate_project_authorization_row`
(`scripts/implementation_authorization.py:896`) validates a project authorization
(PAUTH) against a proposal using **exact** project-id matching. When a proposal cites a
**sub-project** but the covering PAUTH is attached to that sub-project's **parent
project**, validation fails even though the sub-project is, by the taxonomy
(backlog → projects → sub-projects → work items), inside the authorized project's scope.
This proposal relaxes the two exact-project checks to also accept a sub-project proposal
under a parent-project PAUTH, by walking the first-class `projects.parent_project_id`
hierarchy. The restrictive `included_work_item_ids` semantics (DELIB-20266083) are
preserved unchanged.

## Problem detail (for LO review)

Two reject-points in `validate_project_authorization_row` enforce exact project identity:

- `scripts/implementation_authorization.py:914` —
  `if proposal_project_id and proposal_project_id != project_id:` raises
  `AuthorizationError(... is for {project_id}, not proposal project {proposal_project_id})`.
  A proposal citing a sub-project is rejected against the parent's PAUTH here.
- `scripts/implementation_authorization.py:938` — in the `included_work_item_ids`-**empty**
  branch only, `elif not _work_item_in_project(project_root, project_id, work_item_id):`
  requires the work item to be an active member of the PAUTH's project (the parent). A WI
  that belongs to the sub-project (not directly the parent) is rejected.

The data model already supports the hierarchy: the `projects` table carries a first-class
`parent_project_id TEXT` column with `idx_projects_parent` (`groundtruth-kb/src/groundtruth_kb/db.py`),
so a sub-project is a project row whose `parent_project_id` points to its parent.

The restrictive-included-list path (`scripts/implementation_authorization.py:932-937`),
governed by the owner decision in DELIB-20266083 (a non-empty `included_work_item_ids` list
is authoritative), is **out of scope** and must remain unchanged: when the PAUTH lists
explicit work items, that list — not project membership — is the gate.

## Proposed change

1. `scripts/implementation_authorization.py` — add two read-only helpers near the existing
   `_work_item_in_project` (line 883):

   - `_is_descendant_project(project_root, candidate_project_id, ancestor_project_id, *, max_depth=32) -> bool`:
     returns True when `candidate_project_id == ancestor_project_id` OR when walking
     `current_projects.parent_project_id` upward from `candidate_project_id` reaches
     `ancestor_project_id`. Bounded by `max_depth` with a visited-set cycle guard
     (fail-closed: returns False on cycle / missing row / depth exceeded).
   - `_work_item_in_project_or_descendant(project_root, project_id, work_item_id) -> bool`:
     True when the WI is an active member of `project_id` OR of any project whose
     ancestor chain reaches `project_id`.

2. Relax the two reject-points to honor the hierarchy:

   - Line 914: reject only when `proposal_project_id != project_id` **and not**
     `_is_descendant_project(project_root, proposal_project_id, project_id)`.
   - Line 938: replace `_work_item_in_project(...)` with
     `_work_item_in_project_or_descendant(...)`.

   No change to the active/expired/excluded/included/spec-exclusion checks. The
   `included_work_item_ids` restrictive branch (932-937) is untouched.

3. `platform_tests/scripts/test_implementation_authorization.py` — add focused tests using
   synthetic parent+sub-project fixtures (the gate-hardening project has no sub-projects
   today, so the capability is exercised with seeded rows).

## Specification Links

- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` — project-scoped implementation authorization; a sub-project proposal falling inside an authorized parent project is within that authorization's intent. This fix closes the validator gap that rejects it.
- `DCL-PROJECT-AUTHORIZATION-ENVELOPE-001` — project authorization envelope fields are explicit and append-only; this change reads the envelope and the project hierarchy, mutating neither.
- `GOV-PROJECT-REQUIRES-LINKED-SPECIFICATIONS-001` — project authorization requires linked specifications; unaffected (spec-link checks unchanged).
- `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001` — project authorization does not bypass bridge controls; preserved: this fix only governs PAUTH↔proposal project matching, never the bridge GO / implementation-start packet requirement.
- `GOV-FILE-BRIDGE-AUTHORITY-001` — filed as the next numbered bridge file in the append-only versioned chain.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` — satisfied: cites all governing specs.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — satisfied: spec-to-test mapping below.
- `GOV-STANDING-BACKLOG-001` — WI-3350 is the governing backlog item.

Cross-cutting artifact-governance specs (advisory):

- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` — durable artifact-network framing; the project/sub-project hierarchy is a durable artifact relationship the validator should honor.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` — artifact-oriented development decision.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` — artifact lifecycle triggers (this is a reliability fix to an existing validator, not a new artifact-lifecycle surface).

## Prior Deliberations

- `DELIB-20266083` — owner decision: PAUTH `included_work_item_ids` restrictive semantics (a non-empty included list is authoritative). This fix deliberately does NOT touch the included-list branch (932-937); it relaxes only the exact-project checks (914) and the included-empty membership branch (938), preserving the restrictive semantics.
- `DELIB-20265586` — the owner decision authorizing PROJECT-GTKB-IMPLEMENTATION-START-GATE-HARDENING-001 implementation (the PAUTH's `owner_decision_deliberation_id`).
- Deliberation search ("parent project authorization covers sub-project proposal validator") found no on-point precedent deciding the parent-PAUTH-covers-sub-project mechanism itself; the closest is DELIB-20266083 (included-list semantics), respected above.

## Owner Decisions / Input

This proposal is authorized for implementation by an existing active project authorization;
no new owner decision is required:

- `PAUTH-PROJECT-GTKB-IMPLEMENTATION-START-GATE-HARDENING-001-...-BOUNDED-IMPLEMENTATION-2026-06-23`
  (owner decision `DELIB-20265586`) lists `WI-3350` in `included_work_item_ids` and grants
  `allowed_mutation_classes` including `source` and `test_addition` — exactly the change
  classes in this proposal (validator source edit + test additions). The work stays within
  the bounded project scope.

Implementation remains gated behind Loyal Opposition `GO` and an implementation-start packet
(`PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001`); this proposal requests review only.

## Requirement Sufficiency

Existing requirements sufficient. `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` +
`DCL-PROJECT-AUTHORIZATION-ENVELOPE-001` already define project-scoped authorization over a
project and its sub-projects; the validator simply does not yet honor the sub-project
hierarchy. No new or revised requirement is needed before implementation.

## Spec-Derived Verification Plan

| Spec / clause | Test (new, synthetic fixtures) | Assertion |
|---|---|---|
| `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` (parent PAUTH covers sub-project proposal) | `test_validate_accepts_subproject_proposal_under_parent_pauth` | A PAUTH on parent `P` validates a proposal whose `proposal_project_id` is sub-project `P.child` (`parent_project_id=P`); no `AuthorizationError`. |
| same (work-item membership in sub-project) | `test_validate_accepts_work_item_in_subproject_under_parent_pauth` | With `included_work_item_ids` empty, a WI that is an active member of sub-project `P.child` validates under parent `P`'s PAUTH. |
| Negative — unrelated project still rejected | `test_validate_rejects_unrelated_project_proposal` | A proposal citing a project that is NOT `P` and NOT a descendant of `P` still raises `AuthorizationError` (no over-acceptance). |
| Restrictive included-list preserved (DELIB-20266083) | `test_validate_included_list_still_authoritative_for_subproject` | With a non-empty `included_work_item_ids`, a WI NOT in the list is rejected even when it belongs to a descendant sub-project (included-list branch unchanged). |
| Cycle / depth guard | `test_is_descendant_project_handles_cycle` | A malformed `parent_project_id` cycle returns False (fail-closed), does not hang. |
| No regression | existing `test_implementation_authorization.py` suite | green |

Commands (run pre-report): `groundtruth-kb/.venv/Scripts/python.exe -m pytest platform_tests/scripts/test_implementation_authorization.py -q --tb=short`; `ruff check` then `ruff format --check` on the two changed files.

## Acceptance Criteria

1. A proposal citing a sub-project is accepted under a PAUTH attached to an ancestor project (exact-match and membership checks honor `parent_project_id`).
2. The `included_work_item_ids` restrictive semantics (DELIB-20266083) are unchanged: a non-empty included list remains authoritative.
3. Unrelated (non-descendant) project proposals are still rejected (no over-acceptance); the ancestor walk is cycle- and depth-guarded (fail-closed).
4. No change to active/expired/excluded/spec-exclusion checks, the bridge-GO requirement, or the implementation-start packet.
5. `ruff check` and `ruff format --check` pass on both changed files; the existing test suite stays green.

## Risk / Rollback

- Risk: over-acceptance (a parent PAUTH wrongly authorizing an unrelated project). Mitigation: acceptance requires a concrete `parent_project_id` ancestry link to the PAUTH's project; the negative test (criterion 3) locks rejection of non-descendants; the walk is bounded + cycle-guarded.
- Risk: weakening the restrictive included-list gate. Mitigation: the included-list branch (932-937) is explicitly untouched; criterion 2 + its test lock this.
- Rollback: revert the two helper additions and the two relaxed conditionals; prior exact-match behavior returns. No schema change; append-only KB untouched; read-only hierarchy queries only.

## Recommended Commit Type

`fix:` — repairs the project-auth validator to honor the project/sub-project hierarchy for PAUTH↔proposal matching. No new capability surface beyond closing the hierarchy gap; no change to bridge controls or owner-facing behavior.
