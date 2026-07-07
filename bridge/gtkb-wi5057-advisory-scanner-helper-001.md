NEW
author_identity: Prime Builder/Codex
author_harness_id: A
author_session_context_id: 019f337a-009a-7f51-8dce-b6c3f1d91b1c
author_model: GPT-5 Codex
author_model_version: GPT-5
author_model_configuration: Codex Desktop interactive session; reasoning default
author_metadata_source: explicit Codex runtime metadata plus CODEX_THREAD_ID

bridge_kind: prime_proposal
Document: gtkb-wi5057-advisory-scanner-helper
Version: 001
Date: 2026-07-07 UTC

Project Authorization: PAUTH-PROJECT-GTKB-ADVISORY-PROPOSAL-INTAKE-WORKFLOW-WI5057-ADVISORY-SCANNER-20260707
Project: PROJECT-GTKB-ADVISORY-PROPOSAL-INTAKE-WORKFLOW
Work Item: WI-5057
target_paths: ["scripts/advisory_backlog_router.py", "scripts/advisory_intake_scanner.py", "platform_tests/scripts/test_advisory_backlog_router.py", "platform_tests/scripts/test_advisory_intake_scanner.py", "bridge/gtkb-wi5057-advisory-scanner-helper-*.md", "groundtruth.db"]
implementation_scope: Add or extend deterministic tooling that selects only live ADVISORY entries with adopt/adapt classification and a Required Prime Builder Owner-Grilling Gate section, then summarizes them for Prime intake.
requires_review: true
requires_verification: true

# Implementation Proposal - Live ADVISORY Scanner And Summarizer Helper

## Summary
Add or extend deterministic tooling that selects only live ADVISORY entries with adopt/adapt classification and a Required Prime Builder Owner-Grilling Gate section, then summarizes them for Prime intake.

This filing is one child proposal under the verified parent advisory-intake workflow thread. It does not authorize protected implementation until Loyal Opposition returns GO and Prime Builder records implementation-start evidence.

## Source Advisory / Parent Thread
- Parent thread: bridge/gtkb-advisory-proposal-intake-workflow-001.md through bridge/gtkb-advisory-proposal-intake-workflow-005.md.
- Parent result: VERIFIED at bridge/gtkb-advisory-proposal-intake-workflow-005.md.
- Source workflow: advisory proposal intake for live ADVISORY entries that require owner-grilling and explicit project/work-item approval before implementation.
- Linked manual test: TEST-11295.

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

The parent proposal and child work items already encode the operative requirement: ADVISORY material can seed scoped proposals only after owner-grilling and explicit project/work-item approval, and advisory capture itself must not become implementation approval. The linked manual test TEST-11295 provides the acceptance anchor for this child item.

## Proposed Scope
- Extend the existing advisory backlog routing helper or add a narrowly named helper for live ADVISORY intake scanning, preserving the current no-auto-promotion boundary.
- Require both adopt/adapt classification and the Required Prime Builder Owner-Grilling Gate section before an ADVISORY entry is surfaced as intake-ready.
- Add tests covering selection, rejection, summary fields, and presentation order.

## Out Of Scope
- No implementation work item creation or bridge proposal filing is automated by this helper.
- No dispatcher change makes ADVISORY entries automatically dispatchable.

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

## Cross-Harness Disposition
- Claude Code: behavioral parity is required for canonical `.claude/skills/**` skill surfaces when this child targets them; no waiver is requested.
- Codex: behavioral parity is required for `.codex/skills/**` adapters, manifests, and activity-profile exposure when this child targets them; no waiver is requested.
- Cursor and Antigravity: no direct harness-owned runtime file is targeted unless named in `target_paths`; parity expectations remain governed by the harness capability registry, generated/adapted skill surfaces, and the verification tests listed below.

## Specification-Derived Verification Plan
- `python -m pytest platform_tests/scripts/test_advisory_backlog_router.py platform_tests/scripts/test_advisory_intake_scanner.py -q --tb=short` passes and maps to TEST-11295.
- Manual review confirms the helper surfaces only live ADVISORY entries with both adopt/adapt classification and the Required Prime Builder Owner-Grilling Gate section.
- `python scripts/bridge_applicability_preflight.py --bridge-id gtkb-wi5057-advisory-scanner-helper --json` returns no blocking applicability findings for the final bridge thread.

## Acceptance Criteria
- The helper output is deterministic and sufficient for Prime Builder advisory-intake triage.
- TEST-11295 is satisfied by test output and implementation-report evidence.

## Risks / Rollback
- Risk: advisory intake could be mistaken for implementation approval. Mitigation: keep owner-grilling, PAUTH, bridge GO, implementation-start, and verification as separate evidence gates.
- Risk: child proposal overlap could duplicate another child item. Mitigation: use WI-5054 boundary findings and keep this proposal constrained to its listed target paths and acceptance criteria.
- Rollback: revert this child change set and clear the work-item bridge linkage; the verified parent thread and other child proposals remain valid if their target paths are independent.

## Recommended Commit Type
- Recommended commit type: feat.
