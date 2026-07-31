NEW
author_identity: Prime Builder/Codex
author_harness_id: A
author_session_context_id: 019f337a-009a-7f51-8dce-b6c3f1d91b1c
author_model: GPT-5 Codex
author_model_version: GPT-5
author_model_configuration: Codex Desktop interactive session; reasoning default
author_metadata_source: explicit Codex runtime metadata plus CODEX_THREAD_ID

bridge_kind: prime_proposal
Document: gtkb-wi5058-advisory-intake-profile-surfacing
Version: 001
Date: 2026-07-07 UTC

Project Authorization: PAUTH-PROJECT-GTKB-ADVISORY-PROPOSAL-INTAKE-WORKFLOW-WI5058-ACTIVITY-PROFILE-20260707
Project: PROJECT-GTKB-ADVISORY-PROPOSAL-INTAKE-WORKFLOW
Work Item: WI-5058
target_paths: ["config/agent-control/activity-disposition-profiles.toml", "config/agent-control/harness-capability-registry.toml", ".claude/skills/advisory-proposal/SKILL.md", ".claude/skills/advisory-intake/SKILL.md", ".codex/skills/advisory-proposal/SKILL.md", ".codex/skills/advisory-intake/SKILL.md", ".codex/skills/MANIFEST.json", "platform_tests/skills/test_advisory_intake_profile_surfacing.py", "bridge/gtkb-wi5058-advisory-intake-profile-surfacing-*.md", "groundtruth.db"]
implementation_scope: Wire the advisory-proposal and advisory-intake skills into the intended activity/profile discovery surfaces while keeping them absent from unrelated contexts.
requires_review: true
requires_verification: true

# Implementation Proposal - Advisory Intake Activity Profile Surfacing

## Summary
Wire the advisory-proposal and advisory-intake skills into the intended activity/profile discovery surfaces while keeping them absent from unrelated contexts.

This filing is one child proposal under the verified parent advisory-intake workflow thread. It does not authorize protected implementation until Loyal Opposition returns GO and Prime Builder records implementation-start evidence.

## Source Advisory / Parent Thread
- Parent thread: bridge/gtkb-advisory-proposal-intake-workflow-001.md through bridge/gtkb-advisory-proposal-intake-workflow-005.md.
- Parent result: VERIFIED at bridge/gtkb-advisory-proposal-intake-workflow-005.md.
- Source workflow: advisory proposal intake for live ADVISORY entries that require owner-grilling and explicit project/work-item approval before implementation.
- Linked manual test: TEST-11296.

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

The parent proposal and child work items already encode the operative requirement: ADVISORY material can seed scoped proposals only after owner-grilling and explicit project/work-item approval, and advisory capture itself must not become implementation approval. The linked manual test TEST-11296 provides the acceptance anchor for this child item.

## Proposed Scope
- Update activity disposition profiles, skill catalog surfaces, and harness capability registry entries for advisory-proposal and advisory-intake discovery.
- Preserve role separation between advisory authoring and Prime Builder intake.
- Add tests proving intended-context discovery and absence from unrelated contexts.

## Out Of Scope
- No new skill behavior beyond discovery and profile surfacing is included.
- No direct implementation from ADVISORY entries is authorized by profile visibility.

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
- `python -m pytest platform_tests/skills/test_advisory_intake_profile_surfacing.py -q --tb=short` passes and maps to TEST-11296.
- Manual catalog/profile/adapter review confirms advisory-proposal and advisory-intake are discoverable in intended contexts and absent elsewhere.
- `python scripts/bridge_applicability_preflight.py --bridge-id gtkb-wi5058-advisory-intake-profile-surfacing --json` returns no blocking applicability findings for the final bridge thread.

## Acceptance Criteria
- Skill surfacing is precise enough to avoid confusing ordinary bridge proposal or implementation flows with advisory intake.
- TEST-11296 is satisfied by test output and implementation-report evidence.

## Risks / Rollback
- Risk: advisory intake could be mistaken for implementation approval. Mitigation: keep owner-grilling, PAUTH, bridge GO, implementation-start, and verification as separate evidence gates.
- Risk: child proposal overlap could duplicate another child item. Mitigation: use WI-5054 boundary findings and keep this proposal constrained to its listed target paths and acceptance criteria.
- Rollback: revert this child change set and clear the work-item bridge linkage; the verified parent thread and other child proposals remain valid if their target paths are independent.

## Recommended Commit Type
- Recommended commit type: feat.
