GO
::init gtkb lo
::open test
author_identity: loyal-opposition/cursor
author_harness_id: E
author_session_context_id: abec7766-bd82-4efb-9b1c-752e6a43aedc
author_model: composer
author_model_version: composer
author_model_configuration: reasoning_effort=default; thread_source=cursor-ide
author_metadata_source: cursor-conversation-metadata

bridge_kind: lo_verdict
Document: gtkb-wi5761-project-reactivation-invariant
Version: 002
Author: Loyal Opposition (cursor, harness E)
Date: 2026-07-30 UTC
Reviewer: Loyal Opposition
Responds to: bridge/gtkb-wi5761-project-reactivation-invariant-001.md

# Loyal Opposition Review — WI-5761 Project Reactivation Invariant

## Verdict

GO for INV-1/INV-2/INV-3 as proposed (fail-closed evaluation + write gate; owner-evidenced reactivation path; audit-only historical census). Recommended default accepted: WARN-only evaluation is correctly rejected. Historical Authority Foundations v3 repair remains out of scope pending that recovery thread's owner decision.

## First-Line Role Eligibility And Review Independence

- Role: loyal-opposition (`::init gtkb lo`).
- Proposal author session `08ab8a9d-bc19-4278-b81f-a8b3a488700c` differs from reviewer `abec7766-bd82-4efb-9b1c-752e6a43aedc`.

## Applicability Preflight

- packet_hash: `sha256:e184ef33ef4cc0e24390bb6c30ab01046f4c5ae80362f509d76bb33cbf7418ed`
- candidate_evidence_hash: `sha256:17fa6d33d7aa7414ced8edcf9c06bbe7156cde458204b38bb6dea004c6972d6b`
- bridge_document_name: `gtkb-wi5761-project-reactivation-invariant`
- content_file: `bridge/gtkb-wi5761-project-reactivation-invariant-001.md`
- operative_file: `bridge/gtkb-wi5761-project-reactivation-invariant-001.md`
- preflight_passed: `true`
- missing_required_specs: []
- missing_advisory_specs: []
- blocking_errors: []

## Clause Applicability

- Mandatory clause preflight: PASS (zero blocking gaps) against v001.

## Prior Deliberations

- Source advisory `gtkb-lo-active-project-completion-state-enforcement-advisory-001` and WI-5761 disposition under `DELIB-202667531`.
- Completion/PAUTH precedents: `DELIB-20265559`, `DELIB-20264662`, `DELIB-S357-WI-3353-PAUTH-COMPLETION`.
- No prior deliberation selects the reactivation invariant; design-point framing with recommended default is appropriate.

## Positive Confirmations

- Evaluation defect verified: `_project_status` selects only `status`; `_project_is_active` is status-only (`scripts/implementation_authorization.py` ~1176–1186).
- Write-side carry-forward of `completed_at` and CLI `None`-filter blocking clear are accurately scoped (`lifecycle.update_project`, `cli.projects_update`).
- Two-layer enforcement (evaluation + lifecycle write) matches GOV-CROSS-CUTTING defense-in-depth; retirement-reconciliation carve-out preserved.
- Spec links, T1–T5, migration stance (audit never auto-mutates), and seven in-root target_paths are sufficient.

## Findings

_No blocking findings._ Design-point recommendation (fail-closed INV) accepted without owner AUQ escalation.

## Owner Action Required

None to accept this GO. Authority Foundations v3 scar repair remains gated on the separate recovery thread's pending owner decision (explicitly out of this proposal's mutation scope).

---

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
