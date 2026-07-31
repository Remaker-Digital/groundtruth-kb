NEW
author_identity: Prime Builder/Codex
author_harness_id: A
author_session_context_id: 019f337a-009a-7f51-8dce-b6c3f1d91b1c
author_model: GPT-5 Codex
author_model_version: GPT-5
author_model_configuration: Codex Desktop interactive session; reasoning default
author_metadata_source: explicit Codex runtime metadata plus CODEX_THREAD_ID

bridge_kind: prime_proposal
Document: gtkb-wi5054-advisory-intake-boundaries
Version: 001
Date: 2026-07-07 UTC

Project Authorization: PAUTH-PROJECT-GTKB-ADVISORY-PROPOSAL-INTAKE-WORKFLOW-WI5054-INVESTIGATION-20260707
Project: PROJECT-GTKB-ADVISORY-PROPOSAL-INTAKE-WORKFLOW
Work Item: WI-5054
target_paths: ["independent-progress-assessments/CODEX-INSIGHT-DROPBOX/INSIGHTS-2026-07-07-ADVISORY-INTAKE-BOUNDARIES.md", "bridge/gtkb-wi5054-advisory-intake-boundaries-*.md", "groundtruth.db"]
implementation_scope: Produce the scoping report that separates reusable WI-4840 advisory-routing behavior from genuinely new advisory-intake work, then records the implementation boundaries needed by the remaining child proposals.
requires_review: true
requires_verification: true

# Implementation Proposal - Advisory Intake Boundary Investigation

## Summary
Produce the scoping report that separates reusable WI-4840 advisory-routing behavior from genuinely new advisory-intake work, then records the implementation boundaries needed by the remaining child proposals.

This filing is one child proposal under the verified parent advisory-intake workflow thread. It does not authorize protected implementation until Loyal Opposition returns GO and Prime Builder records implementation-start evidence.

## Source Advisory / Parent Thread
- Parent thread: bridge/gtkb-advisory-proposal-intake-workflow-001.md through bridge/gtkb-advisory-proposal-intake-workflow-005.md.
- Parent result: VERIFIED at bridge/gtkb-advisory-proposal-intake-workflow-005.md.
- Source workflow: advisory proposal intake for live ADVISORY entries that require owner-grilling and explicit project/work-item approval before implementation.
- Linked manual test: TEST-11292.

## Owner Decisions / Input
- DELIB-202665870: Mike approved filing all six child proposals for WI-5054 through WI-5059 in response to the owner-gated AUQ. This approval is limited to proposal filing and does not bypass Loyal Opposition GO, implementation-start, or post-implementation verification.
- The child-item authorization deliberations DELIB-202665483 through DELIB-202665487 remain prior scoping evidence for the six-way breakdown.

## Prior Deliberations
- DELIB-202665870: owner approval to file all six child implementation proposals for WI-5054 through WI-5059; this is proposal authorization only and does not authorize protected implementation before GO and implementation-start.
- DELIB-202665483: owner authorized the investigation/scoping child item for advisory-intake boundaries.
- DELIB-202665484: owner authorized the deliberation-side advisory-proposal skill child item.
- DELIB-202665485: owner authorized the Prime Builder advisory-intake skill child item.
- DELIB-202665486: owner authorized the live ADVISORY scanner/summarizer helper child item.
- DELIB-202665487: owner authorized the activity-profile surfacing and parity-test child items.

## Requirement Sufficiency
Existing requirements sufficient.

The parent proposal and child work items already encode the operative requirement: ADVISORY material can seed scoped proposals only after owner-grilling and explicit project/work-item approval, and advisory capture itself must not become implementation approval. The linked manual test TEST-11292 provides the acceptance anchor for this child item.

## Proposed Scope
- Review the completed parent thread, existing advisory-disposition skill, advisory backlog router, owner-grilling gate lint, ADVISORY dispatch behavior, and peer-solution loop boundaries.
- Write a concise investigation report in the insight dropbox with reusable-dependency, new-work, exclusion, and sequencing sections.
- Update the work item with the filed bridge thread and investigation outcome evidence once the report is produced under GO.

## Out Of Scope
- No source-code implementation beyond the investigation artifact is included in this proposal.
- No automatic promotion of ADVISORY entries into implementation work items is authorized.

## Specification Links
- GOV-FILE-BRIDGE-AUTHORITY-001
- GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001
- PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001
- GOV-STANDING-BACKLOG-001
- GOV-ARTIFACT-ORIENTED-GOVERNANCE-001
- ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001
- DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001
- DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001
- DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001
- DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001
- GOV-LO-ADVISORY-OWNER-GRILLING-GATE-001
- DCL-LO-ADVISORY-OWNER-GRILLING-GATE-001
- ADR-ISOLATION-APPLICATION-PLACEMENT-001

## Specification-Derived Verification Plan
- Manual review of INSIGHTS-2026-07-07-ADVISORY-INTAKE-BOUNDARIES.md against TEST-11292 confirms it cites WI-4840, the owner-grilling gate, live ADVISORY routing, advisory-candidate tooling, peer-solution loop boundaries, and separates reusable dependencies from new implementation work.
- `python scripts/bridge_applicability_preflight.py --bridge-id gtkb-wi5054-advisory-intake-boundaries --json` returns no blocking applicability findings for the final bridge thread.

## Acceptance Criteria
- The report gives the next five child proposals enough boundary evidence to avoid duplicating WI-4840 or bypassing the advisory owner-grilling gate.
- TEST-11292 has explicit implementation-report evidence mapped to the report sections.

## Risks / Rollback
- Risk: advisory intake could be mistaken for implementation approval. Mitigation: keep owner-grilling, PAUTH, bridge GO, implementation-start, and verification as separate evidence gates.
- Risk: child proposal overlap could duplicate another child item. Mitigation: use WI-5054 boundary findings and keep this proposal constrained to its listed target paths and acceptance criteria.
- Rollback: revert this child change set and clear the work-item bridge linkage; the verified parent thread and other child proposals remain valid if their target paths are independent.

## Recommended Commit Type
- Recommended commit type: docs.
