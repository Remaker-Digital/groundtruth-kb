ADVISORY

author_identity: loyal-opposition/codex
author_harness_id: A
author_session_context_id: 019fac54-c55c-75c0-8332-d7fdaf03b20a
author_model: gpt-5.6-sol
author_model_version: gpt-5.6-sol
author_model_configuration: Codex desktop interactive; transcript-resolved Loyal Opposition role; test activity
author_metadata_source: session envelope (worker_role_provenance)

# Advisory — Active Project Rows Must Not Bypass Inherited Completion State

bridge_kind: governance_advisory
Document: gtkb-lo-active-project-completion-state-enforcement-advisory
Version: 001
Author: Loyal Opposition (Codex, harness A)
Date: 2026-07-29 UTC

## Source

Independent review of
`bridge/gtkb-authority-foundations-project-authorization-chain-recovery-003.md`
and the review-only GO at `-004.md`, plus live project and operation-time gate
inspection on 2026-07-29. This is outside that recovery-routing item's
no-source/no-MemBase scope.

## Claim

Operation-time project-authorization evaluation treats `project.status ==
"active"` as sufficient even if the active project row retains a non-null
`completed_at` timestamp from a prior retirement. A prose quarantine in a
bridge review is not executable state, so a lifecycle-scarred active row can
be accepted for implementation authorization without a machine-checkable
reactivation/owner-evidence invariant.

## Evidence

- Live `current_projects` returns Authority Foundations v3 with `status:
  active` and `completed_at: 2026-07-29T06:08:54Z`; it was changed at
  `2026-07-29T10:03:20+00:00` by `prime-builder/codex/A` after v2 retirement.
  The reason cites sixteen active work items, but it does not establish a
  governed reactivation lifecycle or clear the completion field.
- `scripts/implementation_authorization.py:1176-1186` selects only `status`
  from `current_projects`; `_project_is_active` is exactly `status ==
  "active"`. The operation-time PAUTH evaluator at `:1295-1300` likewise
  permits an active project without inspecting `completed_at` or reactivation
  evidence.
- The recovery GO deliberately approves only fail-closed routing, not the v3
  row or a PAUTH. Its specified owner decision is pending, while the current
  active row remains mechanically eligible to the implementation-start gate.
- Duplicate search found the historical WI-5012 report
  `gtkb-dispatch-selection-binding-sot-consolidation-009.md` disclosing the
  same scar, but it is terminal evidence rather than a current advisory or
  remediation work item. No current work item description matched
  `completed_at`.

## Impact

An unauthorized or incompletely authorized reactivation can become operative
simply by changing `status` to `active`. That can permit later source/test work
under an active PAUTH while completion provenance remains contradictory,
undermining project-lifecycle auditability and the owner-decision boundary.

## Recommended Prime Action

Route this advisory through backlog/specification disposition. First define
the authoritative reactivation invariant (for example, active implies null
`completed_at`, or active-with-completion requires a durable, owner-evidenced
reactivation record). Then propose a narrowly scoped source/test change that
enforces the invariant in project lifecycle writes and operation-time
authorization checks, with migration/audit coverage for historical rows. Until
then, treat active-plus-completed project rows as a visible lifecycle risk; do
not silently normalize, delete history, or bypass the project/PAUTH protocol.

## Prior Deliberations

- `DELIB-202667524` CF-10 requires leader-only MemBase mutation serialization
  until WI-5675 and WI-5714 land.
- `DELIB-20260715-FLEET-HARNESS-DEFECT-REPAIR-AUTHORIZATION` and
  `DELIB-202666274` preserve the complete lifecycle and later mechanical gates;
  neither approves a status-only reactivation shortcut.
- `DELIB-20266119` is unrelated no-index history context and was considered
  only to ensure this advisory does not revive retired aggregate authority.

## Owner Decision Needed

No owner decision is requested to capture this advisory. Prime Builder must
obtain the normal owner/governance decision when selecting the reactivation
invariant and any historical-record disposition.

## Classification Slot

- Classification: `adapt`.
- Implementation implied: yes, after governed backlog/specification and bridge
  proposal intake; no current work item or implementation authorization is
  created by this advisory.

## Non-Approval Statement

This ADVISORY is not implementation approval. It does not validate the v3
Authority Foundations project row, authorize a PAUTH or project mutation,
permit source/configuration changes, activate the dispatcher, or bypass a
future Prime proposal, independent LO GO, implementation-start, and
verification lifecycle.
